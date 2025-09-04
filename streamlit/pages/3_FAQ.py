"""
FAQ 페이지 - Streamlit 앱
Car Me Sama 프로젝트의 자주 묻는 질문 페이지
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling

# =========================================
# 페이지 설정
# =========================================
st.set_page_config(page_title="FAQ - Car Me Sama", page_icon="🛞", layout="wide")

# =========================================
# 경로 설정
# =========================================
ROOT = Path(__file__).resolve().parents[2]
LOGO = ROOT / "image" / "logo2.png"
FAQ_IMG = ROOT / "image" / "faq.png"

# =========================================
# 환경변수 로드
# =========================================
def load_env_config():
    """환경변수 파일을 찾아서 로드하고 DB 설정을 반환합니다."""
    # .env 파일 우선순위: 레포 루트 > streamlit 하위 > 현재 디렉토리
    env_candidates = [ROOT / ".env", ROOT / "streamlit" / ".env", Path.cwd() / ".env"]
    
    for env_path in env_candidates:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            break
    else:
        load_dotenv()  # 기본 환경변수 로드

    def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
        """환경변수를 안전하게 가져옵니다."""
        value = os.getenv(name, default)
        return None if value is None or str(value).strip() == "" else str(value).strip()

    # DB 설정 추출
    config = {
        "host": get_env_var("DB_HOST", "127.0.0.1"),
        "port": int(get_env_var("DB_PORT", "3306")),
        "user": get_env_var("DB_USER"),
        "password": get_env_var("DB_PASSWORD"),
        "database": get_env_var("DB_NAME", "carmesamadb"),
        "charset": "utf8mb4",
    }

    # 필수 설정 검증
    required_fields = ["user", "password", "database"]
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        st.error(
            f"DB 접속 정보가 부족합니다. 누락된 필드: {', '.join(missing_fields)}\n\n"
            "레포 루트에 `.env` 파일을 생성해 주세요:\n\n"
          
        )
        st.stop()

    return config

# =========================================
# DB 연결 설정
# =========================================
DB_CONFIG = load_env_config()

# 연결 테스트 및 풀 생성
try:
    test_conn = mysql.connector.connect(**DB_CONFIG)
    test_conn.close()
    
    CONNECTION_POOL = pooling.MySQLConnectionPool(
        pool_name="faq_pool", pool_size=5, autocommit=True, **DB_CONFIG
    )
except Exception as e:
    st.error(f"데이터베이스 연결 실패: {e}")
    st.stop()

# =========================================
# 데이터 로딩
# =========================================
@st.cache_data(ttl=60)
def load_faq_data() -> pd.DataFrame:
    """데이터베이스에서 FAQ 데이터를 로드합니다."""
    conn = CONNECTION_POOL.get_connection()
    try:
        query = "SELECT FAQ_ID, CATEGORY, QUESTION, ANSWER FROM tbl_faq ORDER BY FAQ_ID"
        df = pd.read_sql(query, conn)
        
        # 텍스트 컬럼을 문자열로 변환
        for col in ["CATEGORY", "QUESTION", "ANSWER"]:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        return df
    finally:
        conn.close()

def filter_faq_data(df: pd.DataFrame, categories: List[str], search_query: str) -> pd.DataFrame:
    """카테고리와 검색어로 FAQ 데이터를 필터링합니다."""
    mask = pd.Series([True] * len(df))
    
    # 카테고리 필터링
    if categories:
        mask &= df["CATEGORY"].isin(categories)
    
    # 검색어 필터링 (질문과 답변에서 검색)
    if search_query:
        search_mask = (
            df["QUESTION"].str.contains(search_query, case=False, na=False) |
            df["ANSWER"].str.contains(search_query, case=False, na=False)
        )
        mask &= search_mask
    
    return df[mask].reset_index(drop=True)

# =========================================
# 스타일 적용
# =========================================
st.markdown("""
<style>
/* 메인 컨테이너 설정 */
.block-container { 
    padding-top: 1.2rem !important; 
    max-width: 1100px !important; 
}

/* FAQ 카드 스타일 (라이트/다크 테마 자동 대응) */
div[data-testid="stExpander"] {
    border: 1px solid var(--secondary-background-color);
    border-radius: 14px; 
    background: var(--background-color);
    box-shadow: 0 10px 30px rgba(17,24,39,.06); 
    margin-bottom: 10px;
}

.streamlit-expanderHeader {
    font-weight: 600 !important;
    background: var(--secondary-background-color) !important;
}

/* 필터 영역 스타일 */
.filter-bar {
    border: 1px solid var(--secondary-background-color);
    border-radius: 14px;
    padding: 12px 14px;
    box-shadow: 0 6px 20px rgba(17,24,39,.06);
    margin: 8px 0 18px 0;
    background: var(--background-color);
}

/* 구분선 및 여백 */
.hr-soft { 
    margin: 10px 0 12px 0; 
    opacity: .55; 
}

.shrink { 
    height: 6px; 
}

/* CSS 변수 설정 (라이트/다크 테마 대응) */
:root, [data-baseweb="baseweb"] {
    --background-color: transparent;
    --secondary-background-color: rgba(0,0,0,.06);
}

@media (prefers-color-scheme: dark) {
    :root, [data-baseweb="baseweb"] {
        --background-color: transparent;
        --secondary-background-color: rgba(255,255,255,.12);
    }
}

/* Streamlit 이미지 강제 중앙정렬 */
.stImage, div[data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
}

.stImage > div, div[data-testid="stImage"] > div {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
}

.stImage img, div[data-testid="stImage"] img {
    display: block !important;
    margin: 0 auto !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# 헤더 렌더링
# =========================================
st.markdown("<div class='shrink'></div>", unsafe_allow_html=True)

# 로고 표시
if LOGO.exists():
    st.image(str(LOGO), width=300)

# FAQ 배지 이미지 표시
if FAQ_IMG.exists():
    st.image(str(FAQ_IMG), width=100)

# 안내 메시지
st.markdown(
    '<div style="text-align: center; opacity: 0.8; font-size: 0.95rem; margin: 10px 0 20px 0;">'
    '아래에서 유형을 선택하고 검색해 주세요.</div>', 
    unsafe_allow_html=True
)

# =========================================
# 데이터 로드 및 검증
# =========================================
faq_df = load_faq_data()
if faq_df.empty:
    st.warning("FAQ 데이터가 비어 있습니다. (tbl_faq 테이블을 확인해 주세요)")
    st.stop()

# =========================================
# 필터 바
# =========================================
st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)

col_category, col_search = st.columns([2, 3], vertical_alignment="center")

# 카테고리 선택
with col_category:
    categories = sorted(faq_df["CATEGORY"].dropna().unique()) if "CATEGORY" in faq_df.columns else []
    selected_categories = st.multiselect(
        "카테고리",
        categories,
        default=categories,  # 기본값: 모든 카테고리 선택
        placeholder="카테고리를 선택하세요"
    )

# 검색어 입력
with col_search:
    search_query = st.text_input(
        "검색어 (질문/답변)",
        placeholder="예: 창업, 대출, 오픈 기간, 장착…"
    )

st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# 결과 표시
# =========================================
# 데이터 필터링
filtered_results = filter_faq_data(faq_df, selected_categories, search_query)

# 결과 개수 표시
st.markdown(f"**총 {len(filtered_results)}건** 표시 중")
st.markdown("<hr class='hr-soft'/>", unsafe_allow_html=True)

# FAQ 항목들을 확장 가능한 카드로 표시
for _, row in filtered_results.iterrows():
    question = str(row.get("QUESTION", "")).strip()
    answer = str(row.get("ANSWER", "")).strip()
    
    # 질문이 비어있는 경우 처리
    display_question = question if question else "(질문 없음)"
    display_answer = answer if answer else "내용 없음"
    
    with st.expander(f"❓ {display_question}"):
        st.write(display_answer)
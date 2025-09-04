"""
FAQ 페이지 - Streamlit 앱
Car Me Sama 프로젝트의 자주 묻는 질문 페이지
"""

import os
from pathlib import Path
from typing import List, Optional

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
# 환경변수 로드 (streamlit/.env 만 사용)
# =========================================
def load_env_config():
    """streamlit/.env에서 DB 설정을 로드하고 검증."""
    env_path = ROOT / "streamlit" / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        st.error("`streamlit/.env` 파일을 찾을 수 없습니다. (예: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)")
        st.stop()

    def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
        v = os.getenv(name, default)
        return None if v is None or str(v).strip() == "" else str(v).strip()

    cfg = {
        "host": get_env("DB_HOST", "127.0.0.1"),
        "port": int(get_env("DB_PORT", "3306")),
        "user": get_env("DB_USER"),
        "password": get_env("DB_PASSWORD"),
        "database": get_env("DB_NAME", "carmesamadb"),
        "charset": "utf8mb4",
    }

    missing = [k for k in ("user", "password", "database") if not cfg.get(k)]
    if missing:
        st.error(
            "DB 접속 정보가 부족합니다. 누락 필드: "
            + ", ".join(missing)
            + "\n\n`streamlit/.env` 에 아래 형식으로 작성해 주세요:\n"
            "DB_HOST=127.0.0.1\nDB_PORT=3306\nDB_USER=root\nDB_PASSWORD=zzzz\nDB_NAME=carmesamadb"
        )
        st.stop()

    return cfg

# =========================================
# DB 연결 설정
# =========================================
DB_CONFIG = load_env_config()

# 연결 테스트 & 커넥션 풀
try:
    _t = mysql.connector.connect(**DB_CONFIG)
    _t.close()
    POOL = pooling.MySQLConnectionPool(pool_name="faq_pool", pool_size=5, autocommit=True, **DB_CONFIG)
except Exception as e:
    st.error(f"데이터베이스 연결 실패: {e}")
    st.stop()

# =========================================
# 데이터 로딩
# =========================================
@st.cache_data(ttl=60)
def load_faq_data() -> pd.DataFrame:
    """DB에서 FAQ 데이터를 로드."""
    conn = POOL.get_connection()
    try:
        sql = "SELECT FAQ_ID, CATEGORY, QUESTION, ANSWER FROM tbl_faq ORDER BY FAQ_ID"
        df = pd.read_sql(sql, conn)
        for c in ("CATEGORY", "QUESTION", "ANSWER"):
            if c in df.columns:
                df[c] = df[c].astype(str)
        return df
    finally:
        conn.close()

def filter_faq_data(df: pd.DataFrame, categories: List[str], query: str) -> pd.DataFrame:
    """카테고리/검색어 필터."""
    mask = pd.Series([True] * len(df))
    if categories:
        mask &= df["CATEGORY"].isin(categories)
    if query:
        mask &= (
            df["QUESTION"].str.contains(query, case=False, na=False) |
            df["ANSWER"].str.contains(query, case=False, na=False)
        )
    return df[mask].reset_index(drop=True)

# =========================================
# 스타일
# =========================================
st.markdown(
    """
<style>
.block-container { padding-top: 1.2rem !important; max-width: 1100px !important; }

/* 카드(Expander) */
div[data-testid="stExpander"]{
  border: 1px solid var(--secondary-background-color);
  border-radius: 14px; background: var(--background-color);
  box-shadow: 0 10px 30px rgba(17,24,39,.06); margin-bottom: 10px;
}
.streamlit-expanderHeader{
  font-weight: 600 !important;
  background: var(--secondary-background-color) !important;
}

/* 필터 박스 */
.filter-bar{
  border: 1px solid var(--secondary-background-color);
  border-radius: 14px; padding: 12px 14px;
  box-shadow: 0 6px 20px rgba(17,24,39,.06);
  margin: 8px 0 18px 0; background: var(--background-color);
}

/* 구분선/여백 */
.hr-soft{ margin:10px 0 12px 0; opacity:.55; }
.shrink{ height:6px; }

/* 라이트/다크 변수 */
:root, [data-baseweb="baseweb"]{
  --background-color: transparent;
  --secondary-background-color: rgba(0,0,0,.06);
}
@media (prefers-color-scheme: dark){
  :root, [data-baseweb="baseweb"]{
    --background-color: transparent;
    --secondary-background-color: rgba(255,255,255,.12);
  }
}

/* 이미지 강제 중앙정렬 */
.stImage, div[data-testid="stImage"]{ display:flex!important; justify-content:center!important; }
.stImage img, div[data-testid="stImage"] img{ display:block!important; margin:0 auto!important; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================================
# 헤더
# =========================================
st.markdown("<div class='shrink'></div>", unsafe_allow_html=True)
if LOGO.exists():
    st.image(str(LOGO), width=300)
if FAQ_IMG.exists():
    st.image(str(FAQ_IMG), width=100)
st.markdown(
    "<div style='text-align:center; opacity:.8; font-size:.95rem; margin:10px 0 20px 0;'>"
    "아래에서 유형을 선택하고 검색해 주세요.</div>",
    unsafe_allow_html=True,
)

# =========================================
# 데이터 로드/검증
# =========================================
df = load_faq_data()
if df.empty:
    st.warning("FAQ 데이터가 비어 있습니다. (tbl_faq 테이블 확인)")
    st.stop()

# =========================================
# 필터 바
# =========================================
st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)
col_cat, col_q = st.columns([2, 3], vertical_alignment="center")

with col_cat:
    cats = sorted(df["CATEGORY"].dropna().unique()) if "CATEGORY" in df.columns else []
    selected = st.multiselect("카테고리", cats, default=cats, placeholder="카테고리를 선택하세요")

with col_q:
    q = st.text_input("검색어 (질문/답변)", placeholder="예: 창업, 대출, 오픈 기간, 장착…")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# 결과
# =========================================
res = filter_faq_data(df, selected, q)
st.markdown(f"**총 {len(res)}건** 표시 중")
st.markdown("<hr class='hr-soft'/>", unsafe_allow_html=True)

for _, row in res.iterrows():
    question = str(row.get("QUESTION", "")).strip() or "(질문 없음)"
    answer = str(row.get("ANSWER", "")).strip() or "내용 없음"
    with st.expander(f"❓ {question}"):
        st.write(answer)
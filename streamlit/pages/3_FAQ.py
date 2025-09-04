# streamlit/pages/3_FAQ.py
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling

# =========================================
# 페이지 설정
# =========================================
st.set_page_config(page_title="FAQ", page_icon="🛞", layout="wide")

ROOT = Path(__file__).resolve().parents[2]
LOGO = ROOT / "image" / "logo6.png"
FAQ_IMG = ROOT / "image" / "faq.png"

# =========================================
# .env 로드 (레포 루트 / streamlit 하위 우선 탐색)
# =========================================
loaded_env_path = None
for cand in (ROOT / ".env", ROOT / "streamlit" / ".env", Path.cwd() / ".env"):
    if cand.exists():
        load_dotenv(dotenv_path=cand, override=True)
        loaded_env_path = str(cand)
        break
if loaded_env_path is None:
    load_dotenv()

# =========================================
# DB 설정 & 검증
# =========================================
def _get(name, default=None):
    v = os.getenv(name, default)
    return None if v is None or str(v).strip() == "" else str(v).strip()

raw_env = dict(
    host=_get("DB_HOST", "127.0.0.1"),
    port=_get("DB_PORT", "3306"),
    user=_get("DB_USER"),
    password=_get("DB_PASSWORD"),
    database=_get("DB_NAME", "carmesamadb"),
)

missing = [k for k in ("user", "password", "database") if not raw_env.get(k)]
if missing:
    st.error(
        "DB 접속 정보가 부족합니다. 레포 루트(또는 streamlit) 경로에 `.env` 파일을 만들어 주세요:\n\n"
        "```\nDB_HOST=127.0.0.1\nDB_PORT=3306\nDB_USER=root\nDB_PASSWORD=zzzz\nDB_NAME=carmesamadb\n```"
    )
    st.stop()

DB_CFG = dict(
    host=raw_env["host"],
    port=int(raw_env["port"]),
    user=raw_env["user"],
    password=raw_env["password"],
    database=raw_env["database"],
    charset="utf8mb4",
)

# 연결 테스트 & 풀 생성
try:
    _t = mysql.connector.connect(
        host=DB_CFG["host"], port=DB_CFG["port"],
        user=DB_CFG["user"], password=DB_CFG["password"],
        database=DB_CFG["database"], charset=DB_CFG["charset"],
    ); _t.close()
    POOL = pooling.MySQLConnectionPool(pool_name="faq_pool", pool_size=5, autocommit=True, **DB_CFG)
except Exception as e:
    st.error(f"DB 연결 실패: {e}")
    st.stop()

# =========================================
# 데이터 로딩 (캐시)
# =========================================
@st.cache_data(ttl=60)
def load_faq_df() -> pd.DataFrame:
    conn = POOL.get_connection()
    try:
        sql = """
            SELECT FAQ_ID, CATEGORY, QUESTION, ANSWER
            FROM tbl_faq
            ORDER BY FAQ_ID
        """
        df = pd.read_sql(sql, conn)
        for c in ("CATEGORY", "QUESTION", "ANSWER"):
            if c in df.columns:
                df[c] = df[c].astype(str)
        return df
    finally:
        conn.close()

# =========================================
# 스타일
# =========================================
st.markdown("""
<style>
.stApp { background: #f7f9fc; color: #1f2937; }
.block-container { padding-top: 1.2rem !important; max-width: 1100px !important; }

/* 헤더 중앙 정렬 */
.header-wrap {
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  gap:8px; margin:0 0 14px 0;
}
.header-wrap img { display:block; margin:0 auto; }
.header-sub { color:#6b7280; font-size:0.95rem; }

/* 필터 카드 */
.filter-bar {
  background:#fff; border:1px solid #e5e7eb; border-radius:14px;
  padding:12px 14px; box-shadow:0 6px 20px rgba(17,24,39,.06);
  margin:8px 0 18px 0;
}

/* Expander 카드 */
div[data-testid="stExpander"]{
  border:1px solid #e5e7eb; border-radius:14px; background:#fff;
  box-shadow:0 10px 30px rgba(17,24,39,.06); margin-bottom:10px;
}
.streamlit-expanderHeader{ font-weight:600 !important; color:#111827 !important; background:#f3f4f6 !important; }

/* 소프트 구분선 */
.hr-soft { margin:10px 0 12px 0; opacity:.55; }
.shrink { height:6px; }  /* 상단 여백 최소화 */
</style>
""", unsafe_allow_html=True)

# =========================================
# 헤더 (로고 + FAQ 배지 완전 중앙)
# =========================================
st.markdown("<div class='shrink'></div>", unsafe_allow_html=True)
st.markdown("<div class='header-wrap'>", unsafe_allow_html=True)
if LOGO.exists():
    st.image(str(LOGO), width=450)
if FAQ_IMG.exists():
    st.image(str(FAQ_IMG), width=100)
st.markdown("<div class='header-sub'>아래에서 유형을 선택하고 검색해 주세요.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# 필터 바
# =========================================
df = load_faq_df()
if df.empty:
    st.warning("FAQ 데이터가 비어 있습니다. (tbl_faq 확인)")
    st.stop()

st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)
col_cat, col_q = st.columns([2,3], vertical_alignment="center")
with col_cat:
    cats = sorted(df["CATEGORY"].dropna().unique()) if "CATEGORY" in df.columns else []
    selected = st.multiselect("카테고리", cats, default=cats, placeholder="카테고리를 선택하세요")
with col_q:
    query = st.text_input("검색어 (질문/답변)", placeholder="예: 창업, 대출, 오픈 기간, 장착…")
st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# 결과 리스트
# =========================================
mask = pd.Series([True]*len(df))
if selected:
    mask &= df["CATEGORY"].isin(selected)
if query:
    mask &= (df["QUESTION"].str.contains(query, case=False, na=False)
             | df["ANSWER"].str.contains(query, case=False, na=False))
results = df[mask].reset_index(drop=True)

st.markdown(f"**총 {len(results)}건** 표시 중")
st.markdown("<hr class='hr-soft'/>", unsafe_allow_html=True)


for _, row in results.iterrows():
    q = str(row.get("QUESTION", "")).strip()
    a = str(row.get("ANSWER", "")).strip()
    with st.expander(f"❓ {q if q else '(질문 없음)'}"):
        st.write(a if a else "내용 없음")

import os, re, math
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from urllib.parse import quote_plus

st.title("파트너 현황")

PAGE_SIZE = 10 


@st.cache_resource
def get_engine() -> Engine:
    try:
        cfg = st.secrets["db"]  
    except Exception:
        cfg = {
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", "05060112"),
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "database": os.getenv("DB_NAME", "carmesamadb"),
        }
    url = (
        f"mysql+pymysql://{cfg['user']}:{quote_plus(str(cfg['password']))}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['database']}?charset=utf8mb4&connect_timeout=5"
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=3600)

def normalize_phone(s: str) -> str:
    digits = re.sub(r"\D+", "", str(s))
    if digits.startswith("010") and len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    if digits.startswith("02") and len(digits) == 10:
        return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return s

def where_and_params(keyword: str):
    kw = (keyword or "").strip()
    if kw:
        return (
            "WHERE (VENDOR_NAME LIKE :kw OR ADDRESS LIKE :kw OR PHONE LIKE :kw)",
            {"kw": f"%{kw}%"},
        )
    return "", {}

@st.cache_data(ttl=60)
def total_count(keyword: str) -> int:
    where_sql, params = where_and_params(keyword)
    sql = text(f"SELECT COUNT(*) AS cnt FROM tbl_vendor {where_sql}")
    with get_engine().connect() as c:
        row = c.execute(sql, params).mappings().first()
    return int(row["cnt"] if row else 0)

@st.cache_data(ttl=60)
def fetch_page(keyword: str, page: int, page_size: int, order: str) -> pd.DataFrame:
    where_sql, params = where_and_params(keyword)
    order_map = {"이름순": "VENDOR_NAME ASC", "주소순": "ADDRESS ASC"}
    order_clause = order_map.get(order, "VENDOR_NAME ASC")
    offset = (page - 1) * page_size
    params.update({"limit": page_size, "offset": offset})

    sql = text(f"""
        SELECT VENDOR_NAME, ADDRESS, PHONE
        FROM tbl_vendor
        {where_sql}
        ORDER BY {order_clause}
        LIMIT :limit OFFSET :offset
    """)
    with get_engine().connect() as c:
        df = pd.read_sql(sql, c, params=params)
    if not df.empty:
        df["PHONE"] = df["PHONE"].map(normalize_phone)
    return df


if "partner_kw" not in st.session_state:      st.session_state.partner_kw = ""
if "partner_page" not in st.session_state:    st.session_state.partner_page = 1
if "partner_order" not in st.session_state:   st.session_state.partner_order = "이름순"

bar = st.container()
with bar:
    c1, c2, c3, c4 = st.columns([4, 2, 1, 1])
    kw = c1.text_input("검색어 (상호/주소/전화)", st.session_state.partner_kw, placeholder="예) 카미사마, 송파, 010-...")
    order = c2.selectbox(
        "정렬",
        ["이름순", "주소순"],
        index=0 if st.session_state.partner_order == "이름순" else 1,
    )
    search_clicked = c3.button("검색", use_container_width=True)
    reset_clicked  = c4.button("초기화", use_container_width=True)

    if search_clicked:
        if kw != st.session_state.partner_kw or order != st.session_state.partner_order:
            st.session_state.partner_page = 1
        st.session_state.partner_kw = kw
        st.session_state.partner_order = order

    if reset_clicked:
        st.session_state.partner_kw = ""
        st.session_state.partner_order = "이름순"
        st.session_state.partner_page = 1
        kw, order = "", "이름순"


try:
    tot = total_count(st.session_state.partner_kw)
except Exception as e:
    st.error("DB 연결/조회 오류 — secrets.toml을 만들거나 환경변수를 설정하세요.")
    st.exception(e)
    st.stop()

pages = max(1, math.ceil(tot / PAGE_SIZE))
if st.session_state.partner_page > pages:
    st.session_state.partner_page = pages

left, right = st.columns([3, 2])
with left:
    st.markdown(f"**총 {tot}건** · 페이지 **{st.session_state.partner_page} / {pages}** · 정렬: **{st.session_state.partner_order}**")
with right:
    b1, b2, b3, b4 = st.columns(4)
    if b1.button("⏮️ 처음"): st.session_state.partner_page = 1
    if b2.button("◀️ 이전") and st.session_state.partner_page > 1: st.session_state.partner_page -= 1
    if b3.button("다음 ▶️") and st.session_state.partner_page < pages: st.session_state.partner_page += 1
    if b4.button("마지막 ⏭️"): st.session_state.partner_page = pages

df = fetch_page(st.session_state.partner_kw, st.session_state.partner_page, PAGE_SIZE, st.session_state.partner_order)

if tot == 0:
    st.info("검색 결과가 없습니다.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

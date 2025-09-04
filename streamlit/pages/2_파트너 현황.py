import streamlit as st
import pandas as pd
import math
import os
from dotenv import load_dotenv
import mysql.connector

# --- 1. 환경 변수 및 페이지 설정 ---
load_dotenv()
st.title("파트너 현황")
st.set_page_config(page_title="파트너 현황", page_icon="🛞", layout="wide")

# --- 2. DB 연결 및 데이터 로직 ---
# mysql.connector는 커넥션 풀을 제공하지 않으므로, 연결/해제 로직을 직접 관리합니다.
@st.cache_data(ttl=300)
def fetch_data(keyword, page, order):
    """DB에서 데이터를 가져와 DataFrame으로 반환하는 함수"""
    connection = None
    try:
        # DB 연결 정보
        connect_info = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT")),
            "database": os.getenv("DB_NAME")
        }

        # 필수 환경 변수 누락 확인
        if not all(connect_info.values()):
            st.error("데이터베이스 환경 변수가 올바르게 설정되지 않았습니다.")
            st.stop()
        
        # DB 연결
        connection = mysql.connector.connect(**connect_info)
        cursor = connection.cursor(dictionary=True)
        
        # 쿼리 조건 및 매개변수 설정
        sql_where, params = "", []
        if keyword:
            sql_where = "WHERE (VENDOR_NAME LIKE %s OR ADDRESS LIKE %s OR PHONE LIKE %s)"
            kw_param = f"%{keyword}%"
            params = [kw_param, kw_param, kw_param]

        # 총 데이터 개수 계산
        count_sql = f"SELECT COUNT(*) AS cnt FROM tbl_vendor {sql_where}"
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()['cnt'] or 0

        # 정렬 순서 설정
        order_map = {"이름순": "VENDOR_NAME ASC", "주소순": "ADDRESS ASC"}
        order_by = order_map.get(order, "VENDOR_NAME ASC")
        
        # 페이지네이션 오프셋 설정
        offset = (page - 1) * PAGE_SIZE
        
        # 실제 데이터 조회
        query = f"""
            SELECT VENDOR_NAME, ADDRESS, PHONE
            FROM tbl_vendor
            {sql_where}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """
        # LIMIT와 OFFSET 매개변수는 별도로 추가
        params.extend([PAGE_SIZE, offset])
        cursor.execute(query, params)
        
        df = pd.DataFrame(cursor.fetchall())

        # 전화번호 정규화
        if not df.empty:
            df["PHONE"] = df["PHONE"].apply(normalize_phone)
        
        return df, total_count

    except mysql.connector.Error as err:
        st.error(f"데이터베이스 연결 오류 — `.env` 파일의 설정을 확인하세요.")
        st.exception(err)
        st.stop()
    finally:
        if connection and connection.is_connected():
            connection.close()
            
# --- 3. 전화번호 정규화 함수 ---
def normalize_phone(s: str):
    digits = "".join(filter(str.isdigit, str(s)))
    if len(digits) == 11 and digits.startswith("010"):
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10 and digits.startswith("02"):
        return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    return s

# --- 4. Streamlit UI ---
PAGE_SIZE = 10

# 세션 상태 변수 초기화
if 'page' not in st.session_state: st.session_state.page = 1
if 'keyword' not in st.session_state: st.session_state.keyword = ""
if 'order' not in st.session_state: st.session_state.order = "이름순"

# 검색 및 정렬 바
kw_input = st.text_input("검색어 (상호/주소/전화)", st.session_state.keyword, placeholder="예) 카미사마, 송파, 010-...")
order_select = st.selectbox("정렬", ["이름순", "주소순"], index=["이름순", "주소순"].index(st.session_state.order))

# 검색 및 초기화 버튼
c1, c2 = st.columns(2)
if c1.button("검색"):
    if kw_input != st.session_state.keyword or order_select != st.session_state.order:
        st.session_state.page = 1
    st.session_state.keyword = kw_input
    st.session_state.order = order_select
    st.rerun()

if c2.button("초기화"):
    st.session_state.keyword = ""
    st.session_state.order = "이름순"
    st.session_state.page = 1
    st.rerun()

# --- 5. 데이터 표시 및 페이징 ---
df, total_count = fetch_data(st.session_state.keyword, st.session_state.page, st.session_state.order)

if total_count == 0:
    st.info("검색 결과가 없습니다.")
else:
    total_pages = math.ceil(total_count / PAGE_SIZE)
    if st.session_state.page > total_pages:
        st.session_state.page = total_pages
        st.rerun()

    st.markdown(f"**총 {total_count}건** · 페이지 **{st.session_state.page} / {total_pages}**")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 페이징 버튼
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("⏮️ 처음"):
        st.session_state.page = 1
        st.rerun()
    if col2.button("◀️ 이전"):
        if st.session_state.page > 1:
            st.session_state.page -= 1
            st.rerun()
    if col3.button("다음 ▶️"):
        if st.session_state.page < total_pages:
            st.session_state.page += 1
            st.rerun()
    if col4.button("마지막 ⏭️"):
        st.session_state.page = total_pages
        st.rerun()
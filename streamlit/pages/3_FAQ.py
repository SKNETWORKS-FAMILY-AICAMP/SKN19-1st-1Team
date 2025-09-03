import streamlit as st

# 하위 페이지 모듈 불러오기 (각 모듈 안에 반드시 page() 함수가 있어야 합니다)
from carmesama.franchise_faq import franchise_faq
from carmesama.franchise_faq import AllTa_Crawling

st.title("FAQ")
st.write("아래에서 유형을 선택하세요.")

# 버튼 클릭 상태 보존
if "faq_tab" not in st.session_state:
    st.session_state.faq_tab = None

col1, col2 = st.columns(2)
with col1:
    if st.button("가맹 FAQ", use_container_width=True):
        st.session_state.faq_tab = "franchise"
with col2:
    if st.button("고객 FAQ", use_container_width=True):
        st.session_state.faq_tab = "customer"

# 선택에 따라 하위 페이지 렌더
if st.session_state.faq_tab == "franchise":
    franchise_faq.page()
elif st.session_state.faq_tab == "customer":
    # AllTa_Crawling.page()
    pass
else:
    st.caption("왼쪽 버튼 중 하나를 눌러주세요.")
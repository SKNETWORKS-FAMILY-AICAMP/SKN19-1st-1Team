import streamlit as st


from carmesama.franchise_faq import franchise_faq
from carmesama.franchise_faq import AllTa_Crawling

st.title("FAQ")
st.write("아래에서 유형을 선택하세요.")


if "faq_tab" not in st.session_state:
    st.session_state.faq_tab = None

col1, col2 = st.columns(2)
with col1:
    if st.button("가맹 FAQ", use_container_width=True):
        st.session_state.faq_tab = "franchise"
with col2:
    if st.button("고객 FAQ", use_container_width=True):
        st.session_state.faq_tab = "customer"

if st.session_state.faq_tab == "franchise":
    franchise_faq.page()
elif st.session_state.faq_tab == "customer":

    pass
else:
    st.caption("왼쪽 버튼 중 하나를 눌러주세요.")
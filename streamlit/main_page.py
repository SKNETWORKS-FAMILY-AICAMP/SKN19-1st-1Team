import streamlit as st

# 페이지 세팅
st.set_page_config(page_title="Car Me Sama", page_icon="🛞", layout="wide")
st.image("image/logo2.png", width=300)
st.header('Car Me Sama 대리점 개설, 저희가 도와드릴게요 !')
st.badge(
    "전국 자동차 등록 현황과 타이어 매장 분석 데이터를 기반으로, "
    "가장 유리한 입지 선택과 매출 성장 전략까지 한눈에 확인!",
    icon=":material/check:", 
    color="blue"
)

st.divider()

st.subheader('왜 이 플랫폼이 필요할까요?')
st.text('1. 자동차 수 증가와 함께 타이어 수요는 꾸준히 상승 중')
st.text('2. 매장 위치에 따라 매출 차이가 크므로, 전략적 입지 선정 필수')
st.text('3. 업계 경험이 없는 예비 창업자도 데이터 기반으로 빠르게 의사결정 가능')
st.divider()

st.subheader('플랫폼으로 할 수 있는 것')
st.text('1. 지역별 자동차 등록 현황과 매장 등록 현황을 한눈에 확인')
st.text('2. 인구 대비 차량 보유 분석으로 최적 상권 판단')
st.text('3. 창업 관련 FAQ와 가맹 정보 제공으로 초기 고민 최소화')
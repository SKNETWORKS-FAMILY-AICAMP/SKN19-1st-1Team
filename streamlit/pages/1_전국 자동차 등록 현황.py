import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

# ------------------------------------------------------------
# 페이지 초기화
# ------------------------------------------------------------

st.title("막대 1개와 선 2개 그래프 겹쳐 그리기")

# ------------------------------------------------------------
# DB 연결
# ------------------------------------------------------------

# 커넥션 정보
connect_info = {
        "host": os.getenv("CONNECTION_HOST"),           # 연결주소
        "user": os.getenv("CONNECTION_USER"),           # userid
        "password": os.getenv("CONNECTION_PASSWORD"),   # 패스워드
        "database": os.getenv("CONNECTION_DB")          # default 스키마
    }


def get_infos(reg_id):


    # 커넥션 연결
    connection = mysql.connector.connect(**connect_info)
    cursor = connection.cursor(dictionary=True)

    sql1 ="""
    SELECT
    SUM(CASE WHEN YEAR=2020 THEN 1 ELSE 0 END) AS `SUP_2020`,
    SUM(CASE WHEN YEAR=2021 THEN 1 ELSE 0 END) AS `SUP_2021`,
    SUM(CASE WHEN YEAR=2022 THEN 1 ELSE 0 END) AS `SUP_2022`,
    SUM(CASE WHEN YEAR=2023 THEN 1 ELSE 0 END) AS `SUP_2023`,
    SUM(CASE WHEN YEAR=2024 THEN 1 ELSE 0 END) AS `SUP_2024`
    FROM tbl_supplier s
    WHERE %s IS NULL OR REG_ID = %s;
    """

    cursor.execute(sql1, (reg_id, reg_id))

    dict = cursor.fetchall()

    sql2 ="""
    SELECT
    SUM(CASE WHEN YEAR=2020 THEN POPULATION ELSE 0 END) AS `POP_2020`,
    SUM(CASE WHEN YEAR=2021 THEN POPULATION ELSE 0 END) AS `POP_2021`,
    SUM(CASE WHEN YEAR=2022 THEN POPULATION ELSE 0 END) AS `POP_2022`,
    SUM(CASE WHEN YEAR=2023 THEN POPULATION ELSE 0 END) AS `POP_2023`,
    SUM(CASE WHEN YEAR=2024 THEN POPULATION ELSE 0 END) AS `POP_2024`
    FROM tbl_population c
    WHERE %s IS NULL OR REG_ID = %s;
    """

    cursor.execute(sql2, (reg_id, reg_id))

    dict2 = cursor.fetchall()


    sql3 ="""
    SELECT
    SUM(CASE WHEN YEAR=2020 THEN CAR ELSE 0 END) AS `CAR_2020`,
    SUM(CASE WHEN YEAR=2021 THEN CAR ELSE 0 END) AS `CAR_2021`,
    SUM(CASE WHEN YEAR=2022 THEN CAR ELSE 0 END) AS `CAR_2022`,
    SUM(CASE WHEN YEAR=2023 THEN CAR ELSE 0 END) AS `CAR_2023`,
    SUM(CASE WHEN YEAR=2024 THEN CAR ELSE 0 END) AS `CAR_2024`
    FROM tbl_car c
    WHERE %s IS NULL OR REG_ID = %s;
    """

    cursor.execute(sql3, (reg_id, reg_id))
    dict3 = cursor.fetchall()

    supplier_total = [int(value) for value in dict[0].values()]
    population_total = [int(value) for value in dict2[0].values()]
    car_total = [int(value) for value in dict3[0].values()]

    # 커서 닫기
    cursor.close()
    # 커넥션 닫기
    connection.close()

    return supplier_total, population_total, car_total



def make_chart(years:list, suppliers:list, populations:list, cars:list):
    # 1인당 차량 대수를 저장할 리스트
    cars_per_person = []

    def get_per_list_a(list_a, list_b):
        per_list_a = []
        # 각 연도별로 계산 수행
        for i in range(len(list_a)):
            
            #print(f"{list_b[i]} / {list_a[i]}")
            ratio = list_b[i] / list_a[i]
            per_list_a.append(ratio)
        return per_list_a

    # 폰트 설정 (Windows)
    font_name = font_manager.FontProperties(fname="C:/Windows/Fonts/malgun.ttf").get_name()
    rc('font', family=font_name)
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

    list_a = get_per_list_a(cars, suppliers)

    #print(list_a)

    # 데이터프레임 생성
    df = pd.DataFrame({
        '연도': years,
        '차량당 공급업체': list_a,
        #'인구': population_total,
        #'차량대수': car_total,
        '1인당 차량 대수': get_per_list_a(populations, cars)
    })

    # 폰트 설정 (Windows용, 한글 깨짐 방지)
    font_name = font_manager.FontProperties(fname="C:/Windows/Fonts/malgun.ttf").get_name()
    rc('font', family=font_name)
    plt.rcParams['axes.unicode_minus'] = False 

    st.title("연도별 통계 데이터")

    # 두 개의 Y축을 갖는 figure 생성
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # 첫 번째 Y축 (ax1): 막대 그래프 (1인당 차량 대수)
    color1 = 'skyblue'
    ax1.set_xlabel('연도')
    ax1.set_ylabel('1인당 차량 대수', color=color1)
    ax1.bar(df['연도'], df['1인당 차량 대수'], color=color1, alpha=0.6, label='1인당 차량 대수')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xticks(df['연도'])
    ax1.set_ylim(0, 2)

    # 두 번째 Y축 (ax2): 선 그래프 (공급업체 수)
    ax2 = ax1.twinx()
    color2 = 'orangered'
    ax2.set_ylabel('차량당 공급업체', color=color2)
    ax2.plot(df['연도'], df['차량당 공급업체'], color=color2, marker='o', label='차량당 공급업체')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0.00001, 0.0002)

    # 범례 통합
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    # 제목 및 레이아웃 설정
    fig.suptitle('연도별 1인당 차량 대수 및 차량당 공급업체 수 비교', fontsize=16)
    fig.tight_layout()

    return fig


# 지역정보 조회
connection = mysql.connector.connect(**connect_info)
cursor = connection.cursor(dictionary=True)

sql_region = "SELECT DISTINCT REGION,SUBREGION, REG_ID FROM TBL_REGION;"

cursor.execute(sql_region)
region_raw = cursor.fetchall()

cursor.close()
connection.close()

# 시도 초기화
sido_sigungu_data = {
    '전체': ['전체']
}

# 주소 REG_ID 데이터
addr_reg_id = {

}

# SELECT 노출용 데이터 준비
for r in region_raw:
    # 조회용
    addr_reg_id[r['REGION'] + " " + r['SUBREGION']] = r['REG_ID']
    if not r['REGION'] in sido_sigungu_data:
        sido_sigungu_data[r['REGION']] = []

    if not r['SUBREGION'] in sido_sigungu_data[r['REGION']]:
        sido_sigungu_data[r['REGION']].append(r['SUBREGION'])


# st.title("동적 셀렉트 박스 예제")

# 2. 첫 번째 셀렉트 박스 (시도) 생성
# st.selectbox는 사용자가 선택한 값을 반환합니다.
selected_sido = st.selectbox(
    "시/도를 선택하세요:",
    list(sido_sigungu_data.keys()) # 딕셔너리의 키(시도)를 옵션으로 사용
)

# 3. 두 번째 셀렉트 박스 (시군구) 생성
# 첫 번째 셀렉트 박스의 선택값에 따라 두 번째 셀렉트 박스의 옵션이 동적으로 결정됩니다.
sigungu_options = sido_sigungu_data[selected_sido]
selected_sigungu = st.selectbox(
    "시/군/구를 선택하세요:",
    sigungu_options # 첫 번째 선택값에 해당하는 시군구 리스트를 옵션으로 사용
)

# 4. 결과 출력
st.write(f"선택된 시/도: **{selected_sido}**")
st.write(f"선택된 시/군/구: **{selected_sigungu}**")

reg_id = None

if not (selected_sido == '전체' or selected_sigungu == '전체'):
    reg_id = addr_reg_id[selected_sido + " " + selected_sigungu]

print(reg_id)

supplier_total, population_total, car_total = get_infos(reg_id)
years = ['2020','2021','2022','2023','2024']

fig = make_chart(years, supplier_total, population_total, car_total)





# Streamlit에 그래프 표시
st.pyplot(fig)
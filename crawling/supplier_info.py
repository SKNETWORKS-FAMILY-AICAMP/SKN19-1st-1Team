# ------------------------------------------------------------
# import
# ------------------------------------------------------------
import requests, os, json
from dotenv import load_dotenv
import mysql.connector

# ------------------------------------------------------------
# 환경설정 로드

load_dotenv()

# ------------------------------------------------------------
# API KEY 설정

DATA_GO_KR_AUTH = os.getenv("DATA_GO_KR_AUTH")


# ------------------------------------------------------------
# URL, 쿼리스트링 설정

def get_suburl(year):
    return os.getenv(f"SUB_URL_{year}")

year_list = [2024,2023,2022,2021,2020]
# year_list = [2024]

headers = {
    'Authorization': 'Infuser ' + DATA_GO_KR_AUTH
}


sql = "INSERT INTO tbl_supplier_temp(REGION_ORI, SUBREGION_ORI, YEAR, SUPPLIER, ADDRESS) VALUES(%s, %s, %s, %s, %s)"


connect_info = {
    "host":os.getenv("DB_HOST"),         # 연결주소
    "user": os.getenv("DB_USER"),      # userid
    "password": os.getenv("DB_PASSWORD"),  # 패스워드
    "database": os.getenv("DB_NAME")        # default 스키마
}
# 커넥션 연결
connection = mysql.connector.connect(**connect_info)
cursor = connection.cursor()


cursor.execute("TRUNCATE tbl_supplier_temp;")

for year in year_list:
    suburl = get_suburl(year)

    # perPage 기본값이 500 이여서, 전체 카운트 체크하는 로직 추가
    url_check = f"https://api.odcloud.kr/api{suburl}?page=1&perPage=1"
    response_check = requests.get(url_check, headers=headers)
    json_check = json.loads(response_check.text)
    totalCount = json_check["totalCount"]
    #totalCount = 10000
    # 본 로직
    url = f"https://api.odcloud.kr/api{suburl}?page=1&perPage={totalCount}"
    response = requests.get(url, headers=headers)
    json_body = json.loads(response.text)
    # print(json_body)
    data_list = json_body["data"]
    cnt = 0
    for idx, row in enumerate(data_list):
        try:
            print(row)
            region = str(row["지역"]).split(" ")
            region_1 = ""
            region_2 = ""
            if 2 <= len(region):
                region_1 = region[0]
                for ir, r in enumerate(region):
                    if ir == 0:
                        continue
                    region_2 += r
            else:
                region_1 = region[0]
            values = (region_1, region_2, year, row["업체명"], row["주소"])
            cursor.execute(sql, values)
            cnt += cursor.rowcount
        except:
            print("오류발생:", idx, row)

print(f"{cnt}행이 등록되었습니다.")

# commit 처리
connection.commit()
# 커서 닫기
cursor.close()
# 커넥션 연결 해제
connection.close()


# print(response.status_code)
# print(response.text)
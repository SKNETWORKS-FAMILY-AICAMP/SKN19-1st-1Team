import pandas as pd
from sqlalchemy import create_engine, text

CSV_PATH = "partners_carmesama.csv"

USER = "root"
PASSWORD = "05060112"
HOST = "127.0.0.1"
PORT = 3306
DB = "carmesamadb"


engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}?charset=utf8mb4"
)

# CSV 읽기
df = pd.read_csv(CSV_PATH)
df = df.rename(columns={
    "매장명": "VENDOR_NAME",
    "주소": "ADDRESS",
    "전화번호": "PHONE"
})

df = df[["VENDOR_NAME", "ADDRESS", "PHONE"]].drop_duplicates().fillna("")

sql = text("""
    INSERT INTO tbl_vendor (VENDOR_NAME, ADDRESS, PHONE)
    VALUES (:VENDOR_NAME, :ADDRESS, :PHONE)
    ON DUPLICATE KEY UPDATE
        ADDRESS = VALUES(ADDRESS),
        PHONE = VALUES(PHONE)
""")

# DB 반영
with engine.begin() as conn:
    conn.execute(sql, df.to_dict(orient="records"))

print(df)

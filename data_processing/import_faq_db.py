# import_faq_db 입니다.

import pandas as pd
import mysql.connector

# DB 연결
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="zzzz",          # 김성욱 비번
    database="carmesamadb"
)
cur = conn.cursor()

# CSV 두 개 로드
csv1 = pd.read_csv("/Users/souluk/SKN_19/19-1team/data/faq_carme_swaptext.csv", encoding="utf-8-sig")
csv2 = pd.read_csv("/Users/souluk/SKN_19/19-1team/data/faq_allta.csv", encoding="utf-8-sig")

# 합치기
df = pd.concat([csv1, csv2], ignore_index=True)

# INSERT
for _, row in df.iterrows():
    category = "가맹점 FAQ"
    question = str(row["question"])[:50]  # 50자 제한
    answer   = str(row["answer"])[:1000] # 제한 안둬도 될 것 같은데 일단 1000자로 했습니다.
    cur.execute(
        "INSERT INTO tbl_faq (CATEGORY, QUESTION, ANSWER) VALUES (%s, %s, %s)",
        (category, question, answer)
    )

conn.commit()
cur.close()
conn.close()

print("✅ 두 CSV → tbl_faq 적재 완료")
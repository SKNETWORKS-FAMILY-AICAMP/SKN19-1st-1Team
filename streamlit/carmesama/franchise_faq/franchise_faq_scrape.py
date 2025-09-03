# 프랭크버거 FAQ 크롤링
# franchise_faq_scrape.py
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os

# 저장 경로 (없으면 자동 생성)
SAVE_DIR = "/Users/souluk/SKN_19/19-5team/data"
os.makedirs(SAVE_DIR, exist_ok=True)

URL = "https://frankburger.co.kr/board/index.php?board=faq_01"  # 프랭크버거 FAQ

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://frankburger.co.kr/",
}

res = requests.get(URL, headers=headers, timeout=15)
res.raise_for_status()
soup = BeautifulSoup(res.text, "html.parser")

rows = []        # 치환본
rows_raw = []    # 원본
rows_both = []   # 원본+치환 합본

for li in soup.select("ul.board_list > li.faq_list"):
    q_tag = li.select_one("dt > a.ellipsis")
    a_tag = li.select_one("dd")
    if not q_tag or not a_tag:
        continue

    # 텍스트 추출 (줄바꿈 보존)
    question = q_tag.get_text(strip=True)
    answer = a_tag.get_text("\n", strip=True)

    # ---- 원본 보관 ----
    original_question = question
    original_answer = answer

    # ---- 치환 ----
    question = question.replace("프랭크버거", "카미사마")
    question = question.replace("외식", "창업")
    answer = answer.replace("프랭크버거", "카미사마")
    answer = answer.replace("식자재", "부품 및 소모품")
    answer = answer.replace("반제품", "표준화된 제품")
    answer = answer.replace("메뉴조리", "장착 및 기본 정비 작업")
    answer = answer.replace("주방장", "정비사")
    answer = answer.replace("외식업", "정비업")
    answer = answer.replace("조리교육", "장착 교육")
    answer = answer.replace("매장관리 시스템", "점포운영 시스템")

    # 여러 단어를 '전문설비'로 치환
    for word in ["의탁자, 주방기기, 기자재, 집기"]:
        question = question.replace(word, "전문설비")
        answer = answer.replace(word, "전문설비")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---- 치환본 rows ----
    rows.append({
        "brand": "CarMeSama-Franchise",
        "category": "가맹점 FAQ",
        "question": question,
        "answer": answer,
        "source_url": URL,
        "scraped_at": now_str,
    })

    # ---- 원본 rows_raw ----
    rows_raw.append({
        "brand": "FrankBurger",
        "category": "가맹점 FAQ",
        "question": original_question,
        "answer": original_answer,
        "source_url": URL,
        "scraped_at": now_str,
    })

    # ---- 합본 rows_both (원본+치환 나란히 저장용) ----
    rows_both.append((rows_raw[-1], rows[-1]))

# 확인 출력 (치환본 기준)
for r in rows:
    print("Q:", r["question"])
    print("A:", r["answer"])
    print("-"*60)

# ---- CSV 저장 ----
if rows:
    # (1) 치환본
    path_cm = os.path.join(SAVE_DIR, "faq_carme_swaptext.csv")
    with open(path_cm, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"치환본 저장: {len(rows)}건 -> {path_cm}")

    # (2) 원본
    path_raw = os.path.join(SAVE_DIR, "faq_frank_raw.csv")
    with open(path_raw, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows_raw[0].keys())
        w.writeheader()
        w.writerows(rows_raw)
    print(f"원본 저장: {len(rows_raw)}건 -> {path_raw}")

    # (3) 합본 (원본+치환, 한 쌍씩 저장)
    path_both = os.path.join(SAVE_DIR, "faq_frank_carme_both.csv")
    with open(path_both, "w", newline="", encoding="utf-8-sig") as f:
        cols = ["brand", "category", "question", "answer", "source_url", "scraped_at"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for raw, cm in rows_both:
            w.writerow(raw)   # 원본
            w.writerow(cm)    # 치환본
    print(f"합본 저장: {len(rows_both)*2}건 -> {path_both}")

else:
    print("수집된 행이 없습니다.")
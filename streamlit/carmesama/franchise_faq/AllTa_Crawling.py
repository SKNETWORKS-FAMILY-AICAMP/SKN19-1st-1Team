# 올타_FAQ_크롤링


import requests
from bs4 import BeautifulSoup
import csv
import re
from pathlib import Path

def clean_text(text):
    text = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "1234-1234", text)  # 전화번호를 1234-1234로
    text = re.sub(r"[★]", "", text)  # ★ 제거
    text = re.sub(r"CONTACT-1:1", "", text, flags=re.IGNORECASE)  # CONTACT 제거
    text = re.sub(r"\s+", " ", text)  # 불필요한 공백 제거
    text = text.replace("올타이어", "카미사마")  # 카미사마로 치환
    return text.strip()


# 크롤링 URL
url = "http://alltire.koweb.co.kr/program.html?program_id=koweb_faq"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
response.raise_for_status()

# BeautifulSoup으로 파싱
soup = BeautifulSoup(response.text, "html.parser")
dl = soup.select_one("#content > div > dl")
questions = dl.find_all("dt")
answers = dl.find_all("dd")

# 데이터 리스트 생성
faq_list = []
for q, a in zip(questions, answers):
    question_text = clean_text(q.get_text(strip=True))
    answer_text = clean_text(a.get_text("\n"))
    faq_list.append({
        "question": question_text,
        "answer": answer_text
    })

# --- CSV 저장 (data 폴더 안) ---
ROOT = Path(__file__).resolve().parents[2]  # 19-5TEAM/
OUT_DIR = ROOT / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

out_path = OUT_DIR / "faq_allta.csv"

with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["question", "answer"], quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(faq_list)

print(f"✅ FAQ 크롤링 완료! {out_path} 에 저장됨")

import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "http://xn--3k5bm7q.com/contents/02_business/board.html"  # ← http (중요)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}

def get_page_rows(start: int):
    params = {
        "board_id": "board_partner",
        "start": start,     
        "category": "",
        "keyword": "",
        "search_key": ""
    }
    r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
    r.encoding = r.apparent_encoding or "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    content_div = soup.select_one("#content > div")
    if not content_div:
        return []

    rows = []
  
    for tr in content_div.select("table tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        name  = tds[1].get_text(strip=True).replace("올타이어", "카미사마")
        addr  = tds[2].get_text(strip=True).replace("올타이어", "카미사마")
        phone = tds[3].get_text(strip=True)
        rows.append([name, addr, phone])
    return rows

def crawl_all(max_pages=100, sleep_sec=0.4):
    all_rows = []
    start = 0
    for _ in range(max_pages):
        page_rows = get_page_rows(start)
        if not page_rows:
            break
        all_rows.extend(page_rows)
      
        start += len(page_rows)
        time.sleep(sleep_sec)
    return all_rows

if __name__ == "__main__":
    data = crawl_all()
    df = pd.DataFrame(data, columns=["매장명", "주소", "전화번호"]).drop_duplicates()
    df.to_csv("partners_carmesama.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 저장 완료: {len(df)}건 → partners_carmesama.csv")

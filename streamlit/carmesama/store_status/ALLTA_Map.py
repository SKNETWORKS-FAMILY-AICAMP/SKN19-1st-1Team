import requests
from bs4 import BeautifulSoup
import csv

all_partners = []

for page in range(1, 22):  
    url = f"http://alltire.koweb.co.kr/contents/02_business/board.html?board_id=board_partner&page={page}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    table_rows = soup.select("#content table tbody tr")
    
    for tr in table_rows:
        tds = tr.find_all("td")
        name = tds[0].get_text(strip=True)
        address = tds[1].get_text(strip=True)
        
        all_partners.append({
            "name": name,
            "address": address
        })


with open("partners.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["name", "address"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_partners)

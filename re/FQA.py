import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "https://www.ikfa.or.kr/bbs/faq.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/118.0.0.0 Safari/537.36"
}


def squash_hard_wrapped_lines(s: str) -> str:
    """하드랩(줄바꿈으로 쪼개진 문장)들을 문장단위로 재랩."""
    lines = [ln.strip() for ln in s.splitlines()]
    cleaned = []
    for ln in lines:
 
        if not ln:
            cleaned.append("")
            continue

        if ln in {"-", "—", "·", "•", "*", "※"}:
            continue
        if ln in {"<", ">", '""', '"'}:
            continue
   
        if re.fullmatch(r"<\s*참고\s*>", ln):
            ln = "참고:"
        cleaned.append(ln)

    out = []
    buf = ""
    sentence_end = tuple("。．.!?…」』)”]›＞＞")
    for ln in cleaned:
        if ln == "":  
            if buf:
                out.append(buf.strip())
                buf = ""
            out.append("")
            continue
        if not buf:
            buf = ln
        else:
           
            if buf.endswith(sentence_end) or re.search(r"[.!?]$", buf):
                out.append(buf.strip())
                buf = ln
            else:
                buf += " " + ln
    if buf:
        out.append(buf.strip())
    return "\n".join(out)

def fix_spacing(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\xa0", " ")
    s = re.sub(r"[\u200b\u200c\u200d\uFEFF]", "", s)  
    s = s.replace('""', '"')

    
    s = re.sub(r"(닫기\s*)+$", "", s, flags=re.IGNORECASE)

  
    s = re.sub(r"(\d+)\s*\n\s*([가-힣%])", r"\1\2", s)
    s = re.sub(r"(\d+)\s+([가-힣%])", r"\1\2", s)

  
    s = re.sub(r"([가-힣0-9])\s*\n\s*(\()", r"\1\2", s)
    s = re.sub(r"([가-힣0-9])\s+(\()", r"\1\2", s)

   
    s = re.sub(r"\s+([,.:;?!])", r"\1", s)
   
    s = re.sub(r"([(\[])\s+", r"\1", s)
    s = re.sub(r"\s+([)\]])", r"\1", s)

  
    s = re.sub(r"\n{3,}", "\n\n", s)

    
    return s.strip()

def clean_text(s: str) -> str:
    return fix_spacing(squash_hard_wrapped_lines(s))


def get_soup(page: int) -> BeautifulSoup | None:
    try:
        r = requests.get(BASE_URL, params={"fm_id": 2, "page": page}, headers=HEADERS, timeout=15)
        r.encoding = r.apparent_encoding or "utf-8"
        return BeautifulSoup(r.text, "html.parser")
    except requests.RequestException:
        return None

def get_li_list(soup: BeautifulSoup):
    ul = soup.select_one("#faq_con > ul")
    return ul.find_all("li", recursive=False) if ul else []

def extract_q_a_from_li(li) -> tuple[str, str]:
  
    q_el = li.select_one("h3 > a > p")
    q_raw = q_el.get_text(" ", strip=True) if q_el else ""

   
    raw_all = li.get_text("\n", strip=True).replace("\xa0", " ")
    if q_raw and raw_all.startswith(q_raw):
        a_raw = raw_all[len(q_raw):].strip()
    else:
        a_raw = raw_all.replace(q_raw, "", 1).strip()

    return clean_text(q_raw), clean_text(a_raw)

def fetch_specific_items(page_to_indices: dict[int, list[int]]) -> pd.DataFrame:
    rows = []
    for page, indices in page_to_indices.items():
        soup = get_soup(page)
        if not soup:
            continue
        li_list = get_li_list(soup)
        for idx in indices:
            i = idx - 1
            if 0 <= i < len(li_list):
                q, a = extract_q_a_from_li(li_list[i])
                if q or a:
                    rows.append({"질문": q, "답변": a})
    return pd.DataFrame(rows, columns=["질문", "답변"])



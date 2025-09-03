# FAQ 화면뼈대
# carmesama/franchise_faq/franchise_faq.py
import streamlit as st
import pandas as pd
from pathlib import Path

# 프로젝트 루트 (…/19-5TEAM)
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

# 👉 가맹 FAQ 소스 CSV들 (있으면 읽고, 없으면 건너뜀)
CSV_FR1 = DATA_DIR / "faq_carme_swaptext.csv"  # 프랭크→카미사마 치환본
CSV_FR2 = DATA_DIR / "faq_allta.csv"           # 올타 가맹 FAQ (파일명은 그대로 사용)

LOGO = ROOT / "image" / "logo6.png"


def _safe_load(path: Path) -> pd.DataFrame:
    """question/answer/scraped_at 컬럼으로 로드(없으면 빈 DF)."""
    if not path.exists():
        return pd.DataFrame(columns=["question", "answer", "scraped_at"])

    df = pd.read_csv(path)

    # 컬럼 이름 보정
    q_col = next((c for c in df.columns if c.lower() == "question"), None)
    a_col = next((c for c in df.columns if c.lower() == "answer"), None)

    out = pd.DataFrame({
        "question": df[q_col].astype(str) if q_col else "",
        "answer":   df[a_col].astype(str) if a_col else "",
    })
    out["scraped_at"] = (
        df["scraped_at"].astype(str) if "scraped_at" in df.columns else ""
    )
    return out


def page():
    # ===== 헤더 / 로고 =====
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if LOGO.exists():
            st.image(str(LOGO), width=500)
    st.markdown("<h1 style='text-align:center;'>CarMeSama 가맹점 FAQ</h1>", unsafe_allow_html=True)

    # ===== 데이터 로드 (두 소스 합치기, 출처 구분/선택 UI 없음) =====
    fr1 = _safe_load(CSV_FR1)
    fr2 = _safe_load(CSV_FR2)
    df = pd.concat([fr1, fr2], ignore_index=True)

    # 비어있으면 안내
    if df.empty:
        st.error(
            "표시할 가맹 FAQ가 없습니다. 먼저 수집 스크립트를 실행해 CSV를 만들어주세요.\n"
            f"- {CSV_FR1}\n- {CSV_FR2}"
        )
        return

    # 결측/중복 정리
    df = df.dropna(subset=["question", "answer"])
    df = df.drop_duplicates(subset=["question", "answer"]).reset_index(drop=True)

    # ===== 검색 =====
    query = st.text_input("검색어를 입력하세요 (예: 창업, 대출, 오픈, 장착 등)")
    if query:
        results = df[
            df["question"].str.contains(query, case=False, na=False)
            | df["answer"].str.contains(query, case=False, na=False)
        ]
    else:
        results = df

    # ===== 출력 (동일 페이지의 질문처럼 깔끔히) =====
    st.write(f"총 {len(results)}건 가맹 FAQ 표시 중")
    for _, row in results.iterrows():
        with st.expander("❓ " + str(row["question"])):
            st.write(str(row["answer"]))
            st.caption(
                f"상담 문의 : https://www.carmesama.co.kr/franchise/faq | 업데이트 : {row['scraped_at']}"
            )
            
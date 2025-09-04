USER = "root"
PASSWORD = "05060112"
HOST = "127.0.0.1"
PORT = 3306
DB = "carmesamadb"

ENGINE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}?charset=utf8mb4"
engine = create_engine(ENGINE_URL, pool_pre_ping=True)

DDL = """
CREATE TABLE IF NOT EXISTS tbl_faq
(
    FAQ_ID   INT NOT NULL AUTO_INCREMENT COMMENT 'FAQ번호',
    CATEGORY VARCHAR(50) NOT NULL COMMENT '카테고리',
    QUESTION VARCHAR(50) NOT NULL COMMENT '질문',
    ANSWER   VARCHAR(50) NOT NULL COMMENT '답변',
    CONSTRAINT pk_faq PRIMARY KEY (FAQ_ID)
) ENGINE=INNODB COMMENT 'FAQ';
"""

def normalize_1line(s: str) -> str:
    s = (s or "").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s

def truncate(s: str, limit: int) -> str:
    s = (s or "").strip()
    return s[:limit]

def ensure_table_exists():
    with engine.begin() as conn:
        conn.execute(text(DDL))

def prepare_df_for_db(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    
    df = df.copy()
    df["QUESTION"] = df["질문"].map(normalize_1line).map(lambda x: truncate(x, 50))
    df["ANSWER"]   = df["답변"].map(normalize_1line).map(lambda x: truncate(x, 50))

    df = df[(df["QUESTION"].str.len() > 0) & (df["ANSWER"].str.len() > 0)]

    df = df.drop_duplicates(subset=["QUESTION", "ANSWER"]).reset_index(drop=True)
    return df[["QUESTION", "ANSWER"]]

def insert_faq_rows(df: pd.DataFrame, category: str = "KFA") -> int:
    """tbl_faq에 벌크 insert. 반환값: 삽입 건수"""
    if df.empty:
        return 0
    rows = [{"cat": category, "q": r["QUESTION"], "a": r["ANSWER"]} for _, r in df.iterrows()]
    sql = text("INSERT INTO tbl_faq (CATEGORY, QUESTION, ANSWER) VALUES (:cat, :q, :a)")
    with engine.begin() as conn:
        conn.execute(sql, rows)
    return len(rows)


if __name__ == "__main__":

    ensure_table_exists()

    
    page_to_indices = {
        1: list(range(1, 21)),
        2: list(range(1, 21)),
    }
    raw_df = fetch_specific_items(page_to_indices)


    ready_df = prepare_df_for_db(raw_df)


    inserted = insert_faq_rows(ready_df, category="KFA")
    print(f"Inserted rows: {inserted}")
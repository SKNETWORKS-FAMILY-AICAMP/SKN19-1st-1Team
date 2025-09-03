# 작업 내역 (성욱)

## 1. FAQ DB 작업
- `db/` 폴더 새로 생성  
- `import_faq_db.py` 작성 → `data/faq_allta.csv`, `data/faq_carme_swaptext.csv` 를 MySQL `tbl_faq` 테이블에 적재  
- `tbl_faq` 테이블의 `VARCHAR(50)` 컬럼 숫자 (1000)으로 변경 (답변 길이 잘림 방지)

## 2. FAQ 페이지 구현
- `streamlit/pages/3_FAQ.py` 생성  
- MySQL DB에서 불러온 FAQ 데이터에 카테고리 필터 + 검색 기능 제공  
- UI 스타일 개선 (헤더 로고/FAQ 이미지 추가, 카드형 Expander)

## 3. 이미지 리소스 추가
- `/image/faq.png` 추가 (FAQ 배지)

## 4. 환경 변수 설정
- 보안을 위해 `.env`, `.env.example` 파일 생성  
- `.env.example`는 템플릿 파일 → 팀원들은 복사 후 `.env`로 이름 바꿔서 사용  

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=zzzz  # 각자 로컬 환경에 맞게 수정
DB_NAME=carmesamadb
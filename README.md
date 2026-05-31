# 상표 프리체크 MVP

브랜드명과 사용 분야를 입력하면 검색 변형어를 만들고, KIPRIS 상표 API 결과를 정규화해 예비 위험도와 HTML 리포트를 생성하는 로컬 Streamlit MVP입니다.

## 실행 방법

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 환경변수

`.env.example`을 복사해 `.env`를 만들고 값을 채웁니다. API 연결 전에도 Streamlit의 `Mock mode`를 켜면 전체 흐름을 테스트할 수 있습니다.

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
KIPRIS_API_KEY=
KIPRIS_TRADEMARK_ENDPOINT=
KIPRIS_KEY_PARAM=ServiceKey
KIPRIS_SEARCH_PARAM=searchString
KIPRIS_PAGE_PARAM=pageNo
KIPRIS_ROWS_PARAM=numOfRows
APP_ENV=local
SAVE_RAW_RESPONSES=true
```

KIPRIS Plus의 실제 endpoint와 파라미터명은 발급받은 명세서에 따라 `.env`에서 수정하세요.

## 테스트

```bash
python -m pytest
```

## 주의

본 앱은 예비 검토 자료를 생성하는 MVP입니다. 리포트는 상표 등록 가능성, 침해 여부, 분쟁 가능성을 단정하지 않으며 실제 출원 또는 상업적 사용 전에는 변리사 등 전문가 검토가 필요합니다.

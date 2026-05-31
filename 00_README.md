# 상표 프리체크 MVP 개발 문서

## 프로젝트 개요

사용자가 브랜드명, 서비스명, 앱 이름, 제품명을 입력하면 KIPRIS 상표 API와 OpenAI API를 활용하여 상표 프리체크 리포트를 생성하는 MVP입니다.

핵심 흐름은 다음과 같습니다.

```txt
브랜드명 입력
→ OpenAI로 변형어 생성
→ KIPRIS 상표 API 호출
→ 검색 결과 정규화
→ 상품류/지정상품 파싱
→ 상태값 정리
→ 유사도 계산
→ 위험도 산출
→ RAG 기반 근거 리포트 생성
```

## MVP 목표

KIPRIS에 직접 이름을 넣어보는 수준을 넘어서, 일반인이 이해할 수 있는 “상표 사용 전 예비 판단 리포트”를 제공합니다.

확인할 내용:

- 동일 또는 유사 상표 후보가 있는가?
- 사용하려는 업종과 기존 상표의 지정상품/서비스업이 겹칠 가능성이 있는가?
- 등록/출원/소멸/거절 상태를 어떻게 이해해야 하는가?
- 현재 이름을 그대로 쓸지, 수정할지, 추가 검토할지 판단할 수 있는가?

## 권장 기술 스택

빠른 MVP 기준:

- Python 3.11+
- Streamlit
- OpenAI API
- KIPRIS Plus 상표 API
- SQLite
- pandas
- requests
- python-dotenv
- rapidfuzz
- jinja2

## 환경변수

`.env` 파일에 아래 값을 설정합니다.

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
KIPRIS_API_KEY=your_kipris_api_key
KIPRIS_TRADEMARK_ENDPOINT=your_kipris_trademark_endpoint
APP_ENV=local
SAVE_RAW_RESPONSES=true
```

## 실행 목표

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 중요 주의 문구

모든 리포트에는 아래 문구를 포함합니다.

> 본 리포트는 KIPRIS 검색 결과와 AI 분석을 기반으로 한 예비 검토 자료입니다. 상표 등록 가능성, 침해 여부, 분쟁 가능성에 대한 최종 판단은 변리사 등 전문가 검토가 필요합니다.

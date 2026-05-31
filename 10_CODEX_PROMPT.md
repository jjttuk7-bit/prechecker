# Codex 실행 프롬프트

너는 Python/Streamlit 기반 MVP를 구현하는 시니어 개발자다.

## 목표

KIPRIS 상표 API와 OpenAI API를 연결하여 상표 프리체크 리포트를 생성하는 MVP를 구현한다.

## 반드시 먼저 읽을 문서

1. 00_README.md
2. 01_PRD.md
3. 02_ARCHITECTURE.md
4. 03_API_INTEGRATION.md
5. 05_RAG_DESIGN.md
6. 07_IMPLEMENTATION_TASKS.md

## 구현 원칙

- `.env`에서 API 키를 읽어라.
- API 키를 코드에 직접 넣지 마라.
- KIPRIS endpoint와 파라미터명은 환경변수/설정값으로 쉽게 바꿀 수 있게 하라.
- KIPRIS 응답이 XML/JSON 둘 다 가능하도록 방어적으로 파싱하라.
- OpenAI 응답은 JSON 구조로 받도록 구현하라.
- 법률 판단처럼 단정하는 문구를 리포트에 넣지 마라.
- 리포트에는 반드시 예비 검토 및 전문가 검토 필요 문구를 포함하라.
- 우선 Streamlit 로컬 MVP로 구현하라.
- 테스트 가능한 mock 데이터를 포함하라.

## 1차 구현 범위

1. 프로젝트 폴더 구조 생성
2. Streamlit 입력 화면
3. OpenAI 변형어 생성
4. KIPRIS 상표 API 호출 함수
5. 검색 결과 정규화
6. rapidfuzz 기반 유사도 계산
7. 위험도 산출
8. HTML 리포트 생성
9. 기본 테스트 작성
10. README 실행 방법 작성

## 완료 기준

- `streamlit run app.py`로 실행된다.
- 브랜드명과 사용 분야를 입력하면 분석 흐름이 동작한다.
- KIPRIS API가 아직 정확히 연결되지 않아도 mock mode로 테스트 가능하다.
- 실제 endpoint와 파라미터명을 `.env`에서 수정하면 연결 가능하도록 되어 있다.

# Codex 개발 작업 지시서

## 목표

상표 프리체크 MVP를 Python + Streamlit 기반으로 구현한다.

## 작업 원칙

- 한 번에 거대한 기능을 만들지 말고, 작은 단위로 구현하고 테스트한다.
- API 키는 `.env`에서 읽는다.
- KIPRIS API endpoint와 파라미터명은 `.env`와 설정 파일에서 바꿀 수 있게 한다.
- KIPRIS 응답 구조가 다를 수 있으므로 parser는 방어적으로 작성한다.
- 법률 판단처럼 보이는 문구를 리포트에서 피한다.

## Phase 0. 프로젝트 초기화

아래 구조를 만든다.

```txt
trademark-precheck-mvp/
├─ app.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ README.md
├─ src/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ openai_client.py
│  ├─ query_expander.py
│  ├─ kipris_client.py
│  ├─ trademark_normalizer.py
│  ├─ similarity_scorer.py
│  ├─ risk_analyzer.py
│  ├─ report_generator.py
│  └─ storage.py
├─ prompts/
│  ├─ query_expansion.md
│  ├─ class_mapping.md
│  ├─ risk_analysis.md
│  └─ report_writer.md
├─ templates/
│  └─ report.html
├─ data/
│  ├─ raw/
│  └─ reports/
└─ tests/
   ├─ test_similarity_scorer.py
   └─ test_normalizer.py
```

## Phase 1. 기본 UI 구현

- Streamlit 입력 화면
- 브랜드명 입력
- 사용 분야 입력
- 분석 실행 버튼
- 검색 변형어 표시
- KIPRIS 검색 결과 테이블 표시
- 위험 후보 TOP 3 표시
- 리포트 출력

## Phase 2. OpenAI 변형어 생성

`src/openai_client.py`

- 환경변수에서 API 키 로드
- model 이름 로드
- JSON 응답 요청 함수 작성
- 오류 처리

`src/query_expander.py`

```python
def generate_query_variants(brand_name: str, business_description: str) -> dict:
    ...
```

## Phase 3. KIPRIS API 연결

`src/kipris_client.py`

```python
def search_trademark(keyword: str, page: int = 1, rows: int = 20) -> list[dict]:
    ...
```

요구사항:

- 실제 endpoint는 `.env`에서 읽는다.
- 실제 파라미터명은 상수로 분리한다.
- 응답이 XML이면 XML 파싱
- 응답이 JSON이면 JSON 파싱
- 실패 시 빈 리스트와 오류 메시지 반환
- mock mode 지원

## Phase 4. 정규화

`src/trademark_normalizer.py`

```python
def normalize_items(raw_items: list[dict]) -> list[dict]:
    ...
```

KIPRIS 응답 필드명이 다를 수 있으므로 후보 키를 여러 개 지원한다.

## Phase 5. 유사도 계산

`src/similarity_scorer.py`

```python
def calc_name_similarity(input_name: str, candidate_name: str) -> float:
    ...
```

```python
def calc_class_similarity(likely_classes: list[str], candidate_classes: list[str]) -> float:
    ...
```

```python
def calc_status_risk(status: str | None) -> float:
    ...
```

## Phase 6. 위험도 분석

`src/risk_analyzer.py`

```python
def analyze_risk(scored_candidates: list[dict]) -> dict:
    ...
```

반환:

```python
{
  "overall_risk": "low|medium|high",
  "top_candidates": [...],
  "summary": "..."
}
```

## Phase 7. 리포트 생성

`templates/report.html`

포함:

- 제목
- 한 줄 결론
- 입력 정보
- 검색 확장어
- 유사 후보 테이블
- 위험 후보 TOP 3
- 대체 이름 후보
- 다음 행동
- 주의 문구

## Phase 8. 테스트

최소 테스트:

- 유사도 계산 테스트
- 상태 위험도 테스트
- 정규화 테스트
- mock KIPRIS 응답 기반 end-to-end 테스트

## 완료 기준

- `streamlit run app.py`로 실행된다.
- 브랜드명과 사용 분야를 입력하면 mock mode에서 리포트가 생성된다.
- 실제 KIPRIS endpoint와 파라미터명을 `.env`에서 수정하면 실 API 연결 가능하다.

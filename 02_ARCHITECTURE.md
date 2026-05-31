# 시스템 아키텍처

## 1. 전체 구조

```txt
사용자 입력
  ↓
Streamlit UI
  ↓
Query Expansion Agent
  ↓
KIPRIS Trademark Client
  ↓
Normalizer
  ↓
Similarity Scorer
  ↓
Risk Analyzer
  ↓
RAG Report Generator
  ↓
HTML/PDF 리포트
```

## 2. 주요 모듈

### app.py

Streamlit UI를 담당합니다.

- 브랜드명 입력
- 사용 분야 입력
- 분석 버튼
- 진행 상태 표시
- 리포트 출력
- 다운로드 버튼

### src/openai_client.py

OpenAI API 호출 공통 모듈입니다.

- 모델명 관리
- JSON 응답 요청
- 오류 처리
- 재시도

### src/query_expander.py

브랜드명 변형어를 생성합니다.

- 한글 변형
- 영문 변형
- 발음 유사어
- 의미 유사어
- 업종 관련 결합어

### src/kipris_client.py

KIPRIS 상표 API를 호출합니다.

- API 키 로딩
- 변형어별 API 요청
- 응답 XML/JSON 수신
- 호출 오류 처리
- 원본 응답 저장

### src/trademark_normalizer.py

KIPRIS 응답을 내부 표준 형식으로 변환합니다.

- 상표명 추출
- 출원번호 추출
- 등록번호 추출
- 상태값 추출
- 상품류/지정상품 추출
- 날짜 정규화

### src/similarity_scorer.py

입력 브랜드명과 검색 결과 간 유사도를 계산합니다.

- 문자 유사도
- 발음 유사도
- 의미 유사도
- 상품류 유사도
- 상태 위험도

### src/risk_analyzer.py

최종 위험도를 산출합니다.

- 후보별 점수 계산
- 위험 후보 TOP 3 선정
- 전체 위험도 낮음/중간/높음 결정
- 위험 이유 생성

### src/report_generator.py

리포트를 생성합니다.

- 분석 결과를 HTML 템플릿에 삽입
- 일반인 친화적 설명 생성
- 주의 문구 삽입
- PDF 저장 옵션 제공

## 3. RAG 구조

이 MVP의 RAG는 일반적인 문서 검색형 RAG가 아니라 구조화 데이터 기반 RAG입니다.

```txt
Retrieval:
  KIPRIS 상표 API 결과 수집

Augmentation:
  상표명, 상품류, 지정상품, 상태값, 유사도 점수, 업종 매핑 정보를 문맥으로 구성

Generation:
  OpenAI가 근거 기반 리포트 생성
```

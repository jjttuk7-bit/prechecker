# RAG 고도화 설계

## 1. 이 프로젝트에서 RAG의 의미

이 MVP의 RAG는 일반적인 “문서 검색 후 답변”이 아닙니다.

상표 프리체크에서 RAG는 다음 구조입니다.

```txt
Retrieval:
  KIPRIS 상표 API에서 후보 상표를 가져온다.

Augmentation:
  후보 상표의 표장, 상태, 상품류, 지정상품, 유사도 점수, 검색 변형어, 사용 분야 정보를 분석 문맥으로 구성한다.

Generation:
  OpenAI가 근거 기반으로 예비 위험도와 리포트를 생성한다.
```

즉, RAG의 역할은 검색 결과를 단순 나열하는 것이 아니라, 검색 결과를 근거로 사용자가 이해할 수 있는 판단 리포트를 만드는 것입니다.

## 2. RAG 레이어 구조

### Layer 1. Query Expansion RAG

입력 브랜드명 하나를 여러 검색 후보로 확장합니다.

목적:

- 동일명 검색 누락 방지
- 발음 유사 검색
- 영문 변형 검색
- 의미 유사 검색
- 업종 결합어 검색

### Layer 2. KIPRIS Retrieval

각 변형어로 KIPRIS 상표 API를 호출합니다.

수집 대상:

- 상표명
- 출원번호
- 등록번호
- 출원인
- 권리자
- 상태
- 상품류
- 지정상품
- 출원일
- 등록일

### Layer 3. Normalization

KIPRIS 응답을 내부 데이터 모델로 정규화합니다.

### Layer 4. Similarity Scoring

후보별로 점수를 계산합니다.

점수 종류:

1. Name Similarity
2. Phonetic Similarity
3. Semantic Similarity
4. Class Similarity
5. Status Risk

### Layer 5. Evidence Mapping

위험 판단에 근거를 연결합니다.

예시:

```txt
위험 후보:
- 상표명: 프리체크
- 상태: 등록
- 상품류: 제42류
- 지정상품: 소프트웨어 개발업

위험 이유:
입력 브랜드명과 의미가 유사하고, 사용 예정 분야인 AI 웹서비스와 상품류가 겹칠 가능성이 있습니다.
```

### Layer 6. Report Generation

OpenAI가 최종 리포트를 작성합니다.

중요 조건:

- 법률 판단처럼 단정하지 않음
- 근거 후보를 명시
- 일반인이 이해할 수 있는 문장 사용
- 다음 행동을 제안

## 3. 최종 위험도 계산

초기 MVP 공식:

```txt
total_score =
name_similarity * 0.30
+ phonetic_similarity * 0.20
+ semantic_similarity * 0.20
+ class_similarity * 0.20
+ status_risk * 0.10
```

위험도:

```txt
0.75 이상: 높음
0.45 이상: 중간
0.45 미만: 낮음
```

주의:

이 점수는 법적 판단이 아니라 AI 기반 예비 검토 점수입니다.

## 4. 후속 고도화

### 1단계

- 검색 결과 축적
- 중복 제거 개선
- 상태값 정규화 개선

### 2단계

- 자체 상표명 벡터 인덱스 구축
- embedding 기반 의미 유사도 도입
- 한글 발음 유사도 개선

### 3단계

- 도형상표 이미지 유사도
- 로고 이미지 업로드
- 상표 이미지 검색

### 4단계

- 특허/실용신안 RAG 모듈 결합
- 통합 IP 프리체크 리포트

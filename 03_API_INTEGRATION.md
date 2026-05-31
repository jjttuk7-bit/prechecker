# API 연동 문서

## 1. API 키 관리

API 키는 절대 코드에 직접 작성하지 않습니다.

`.env` 파일:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
KIPRIS_API_KEY=your_kipris_api_key
KIPRIS_TRADEMARK_ENDPOINT=your_kipris_trademark_endpoint
```

`.gitignore`:

```txt
.env
__pycache__/
data/raw/
data/reports/
*.sqlite3
```

## 2. OpenAI API 사용 위치

OpenAI API는 다음 네 곳에서 사용합니다.

1. 변형어 생성
2. 상품류/서비스류 후보 추정
3. 위험도 해석
4. 리포트 생성

## 3. 변형어 생성 출력 예시

```json
{
  "original": "먼저체크",
  "korean_variants": ["먼저체크", "먼저 첵", "먼저체커"],
  "english_variants": ["PreCheck", "FirstCheck", "MeonjeoCheck"],
  "phonetic_variants": ["먼저첵", "먼저채크"],
  "semantic_variants": ["상표체크", "권리체크", "IP체크"],
  "recommended_search_terms": ["먼저체크", "PreCheck", "FirstCheck", "상표체크", "IP체크"]
}
```

## 4. 상품류 후보 출력 예시

```json
{
  "likely_service_categories": [
    "소프트웨어 서비스",
    "온라인 정보 제공업",
    "데이터 분석 서비스",
    "지식재산 관련 정보 제공",
    "교육 서비스"
  ],
  "possible_nice_classes": ["42", "45", "41", "35"],
  "reason": "AI 기반 웹서비스, 정보 제공, 교육/컨설팅 가능성이 있어 해당 분류를 예비 후보로 봅니다."
}
```

## 5. KIPRIS 상표 API 사용

KIPRIS Plus의 실제 상표 API endpoint와 파라미터명은 발급받은 API 명세서 기준으로 작성해야 합니다.

예상 파라미터 구조 예시:

```python
params = {
    "ServiceKey": KIPRIS_API_KEY,
    "searchString": keyword,
    "pageNo": 1,
    "numOfRows": 20
}
```

주의:

- 실제 인증키 파라미터명이 다를 수 있습니다.
- 실제 검색어 파라미터명이 API별로 다를 수 있습니다.
- 응답이 XML일 수도 있고 JSON일 수도 있습니다.
- 반드시 KIPRIS Plus API 명세서를 확인하고 `kipris_client.py`의 값을 수정해야 합니다.

## 6. KIPRIS Client 의사코드

```python
def search_trademark(keyword: str, page: int = 1, rows: int = 20) -> list[dict]:
    endpoint = os.getenv("KIPRIS_TRADEMARK_ENDPOINT")
    key = os.getenv("KIPRIS_API_KEY")

    params = {
        "ServiceKey": key,
        "searchString": keyword,
        "pageNo": page,
        "numOfRows": rows
    }

    response = requests.get(endpoint, params=params, timeout=20)
    response.raise_for_status()

    return parse_response(response.text)
```

# 데이터 모델

## 1. SearchSession

사용자 한 번의 분석 요청입니다.

```json
{
  "id": "uuid",
  "brand_name": "먼저체크",
  "business_description": "AI 기반 특허·상표 프리체크 웹서비스",
  "created_at": "2026-05-31T10:00:00",
  "status": "completed"
}
```

## 2. QueryVariant

OpenAI가 생성한 검색 변형어입니다.

```json
{
  "session_id": "uuid",
  "term": "PreCheck",
  "variant_type": "english",
  "priority": 2
}
```

variant_type 후보:

- original
- korean
- english
- phonetic
- semantic
- industry_related

## 3. NormalizedTrademark

정규화된 상표 후보입니다.

```json
{
  "mark_name": "프리체크",
  "application_number": "4020xxxxxxxxx",
  "registration_number": "4019xxxxxxxxx",
  "applicant": "홍길동",
  "owner": "홍길동",
  "status": "등록",
  "nice_classes": ["42"],
  "designated_goods": ["소프트웨어 개발업", "온라인 정보 제공업"],
  "application_date": "2024-01-01",
  "registration_date": "2025-01-01",
  "source": "KIPRIS"
}
```

## 4. ScoredTrademark

유사도와 위험도 점수가 추가된 상표 후보입니다.

```json
{
  "name_similarity": 0.82,
  "phonetic_similarity": 0.75,
  "semantic_similarity": 0.62,
  "class_similarity": 0.80,
  "status_risk": 0.90,
  "total_risk_score": 0.78,
  "risk_level": "medium",
  "risk_reason": "명칭이 일부 유사하고 사용 분야가 소프트웨어 서비스와 겹칠 가능성이 있습니다."
}
```

## 5. 상태값 위험도

```python
STATUS_RISK_MAP = {
    "등록": 1.0,
    "출원": 0.8,
    "공고": 0.8,
    "심사중": 0.7,
    "거절": 0.3,
    "취하": 0.2,
    "포기": 0.2,
    "소멸": 0.2,
    "무효": 0.2,
    "알수없음": 0.5
}
```

## 6. 위험도 레벨

```python
if total_score >= 0.75:
    risk_level = "high"
elif total_score >= 0.45:
    risk_level = "medium"
else:
    risk_level = "low"
```

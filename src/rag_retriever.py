from __future__ import annotations

from rapidfuzz import fuzz


KNOWLEDGE_BASE = [
    {
        "id": "nice-35",
        "category": "상품류 근거",
        "title": "제35류: 광고·판매·사업관리 관련 서비스",
        "source": "local_nice_class_guide",
        "tags": ["35", "광고", "판매", "쇼핑", "마케팅", "커머스"],
        "text": "제35류는 광고, 마케팅, 판매 대행, 온라인 쇼핑몰, 사업관리 성격의 서비스와 관련될 수 있습니다.",
    },
    {
        "id": "nice-41",
        "category": "상품류 근거",
        "title": "제41류: 교육·콘텐츠 제공 관련 서비스",
        "source": "local_nice_class_guide",
        "tags": ["41", "교육", "강의", "콘텐츠", "출판", "커뮤니티"],
        "text": "제41류는 교육, 강의, 콘텐츠 제작·제공, 출판, 문화 활동 서비스와 관련될 수 있습니다.",
    },
    {
        "id": "nice-42",
        "category": "상품류 근거",
        "title": "제42류: 소프트웨어·기술 서비스",
        "source": "local_nice_class_guide",
        "tags": ["42", "소프트웨어", "앱", "웹", "ai", "플랫폼", "데이터"],
        "text": "제42류는 소프트웨어 개발, SaaS, 데이터 분석, 플랫폼 개발 등 기술 서비스와 관련될 수 있습니다.",
    },
    {
        "id": "nice-43",
        "category": "상품류 근거",
        "title": "제43류: 카페·음식점·숙박 서비스",
        "source": "local_nice_class_guide",
        "tags": ["43", "카페", "음식점", "식당", "베이커리", "숙박"],
        "text": "제43류는 카페업, 음식점업, 식음료 제공, 숙박 제공 서비스와 관련될 수 있습니다.",
    },
    {
        "id": "nice-45",
        "category": "상품류 근거",
        "title": "제45류: 법률·지식재산·보안 관련 서비스",
        "source": "local_nice_class_guide",
        "tags": ["45", "법률", "상표", "지식재산", "권리", "보안"],
        "text": "제45류는 법률 서비스, 지식재산 관련 정보 제공, 권리 관리, 보안 서비스와 관련될 수 있습니다.",
    },
    {
        "id": "status-registered",
        "category": "상태값 근거",
        "title": "등록 상태: 현재 권리 존재 가능성 우선 확인",
        "source": "local_status_guide",
        "tags": ["등록", "존속", "유효"],
        "text": "등록 또는 존속으로 표시된 후보는 권리가 유지 중일 가능성이 있어 지정상품과 권리 범위를 우선 확인하는 것이 좋습니다.",
    },
    {
        "id": "status-applied",
        "category": "상태값 근거",
        "title": "출원 상태: 심사 진행 중 후보",
        "source": "local_status_guide",
        "tags": ["출원", "공고", "심사"],
        "text": "출원 또는 심사 중인 후보는 아직 최종 등록 상태가 아닐 수 있으나, 향후 권리화 가능성이 있어 경과 확인이 필요합니다.",
    },
    {
        "id": "status-expired",
        "category": "상태값 근거",
        "title": "소멸 상태: 과거 권리와 재출원 가능성 확인",
        "source": "local_status_guide",
        "tags": ["소멸", "만료", "말소"],
        "text": "소멸 또는 만료로 표시된 후보는 현재 권리 유지 여부가 낮을 수 있으나, 과거 사용 이력과 재출원 가능성은 별도로 확인하는 것이 좋습니다.",
    },
    {
        "id": "similarity-guide",
        "category": "유사 판단 근거",
        "title": "유사 판단: 표장과 상품류를 함께 봐야 함",
        "source": "local_similarity_guide",
        "tags": ["유사", "상표명", "상품류", "지정상품", "혼동"],
        "text": "상표 예비 검토에서는 표장의 문자·발음·관념 유사성과 함께 지정상품 또는 서비스업의 관련성을 함께 살펴야 합니다.",
    },
]


def _candidate_terms(top_candidates: list[dict]) -> list[str]:
    terms: list[str] = []
    for candidate in top_candidates:
        terms.extend(candidate.get("nice_classes", []))
        terms.append(str(candidate.get("status", "")))
        terms.extend(candidate.get("designated_goods", []))
    return [term for term in terms if term]


def _score_doc(doc: dict, query_terms: list[str]) -> float:
    haystack = " ".join([doc["title"], doc["text"], " ".join(doc["tags"])]).lower()
    score = 0.0
    for term in query_terms:
        clean = str(term).lower().strip()
        if not clean:
            continue
        if clean in doc["tags"] or clean in haystack:
            score += 1.0
        else:
            score += fuzz.partial_ratio(clean, haystack) / 200
    return score


def retrieve_evidence(
    business_description: str,
    likely_classes: list[str],
    top_candidates: list[dict],
    limit: int = 5,
) -> list[dict]:
    query_terms = [business_description, *likely_classes, *_candidate_terms(top_candidates)]
    scored = []
    for doc in KNOWLEDGE_BASE:
        score = _score_doc(doc, query_terms)
        if score > 0:
            item = dict(doc)
            item["score"] = round(score, 3)
            scored.append(item)
    return _dedupe_by_id(sorted(scored, key=lambda item: item["score"], reverse=True))[:limit]


def related_evidence_for_candidate(candidate: dict, evidence: list[dict], limit: int = 2) -> list[dict]:
    query_terms = [
        str(candidate.get("status", "")),
        *candidate.get("nice_classes", []),
        *candidate.get("designated_goods", []),
        "유사",
    ]
    scored = []
    for item in evidence:
        score = _score_doc(item, query_terms)
        if score > 0:
            related = dict(item)
            related["candidate_match_score"] = round(score, 3)
            scored.append(related)
    return _dedupe_by_id(sorted(scored, key=lambda item: item["candidate_match_score"], reverse=True))[:limit]


def group_evidence_by_category(evidence: list[dict], per_category_limit: int = 2) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for item in _dedupe_by_id(evidence):
        category = item.get("category", "기타 근거")
        grouped.setdefault(category, [])
        if len(grouped[category]) < per_category_limit:
            grouped[category].append(item)
    return grouped


def _dedupe_by_id(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped: list[dict] = []
    for item in items:
        item_id = str(item.get("id") or item.get("title") or "")
        if item_id and item_id not in seen:
            seen.add(item_id)
            deduped.append(item)
    return deduped

from __future__ import annotations

from .openai_client import OpenAIJsonClient


def fallback_query_variants(brand_name: str, business_description: str) -> dict:
    compact = brand_name.replace(" ", "")
    spaced = " ".join(list(compact)) if len(compact) <= 6 else brand_name
    lower_hint = business_description.lower()
    semantic = ["브랜드체크", "상표체크", "권리체크"]
    if any(word in lower_hint for word in ["ai", "소프트웨어", "웹", "앱", "서비스"]):
        semantic.extend(["AI체크", "서비스체크"])

    terms = []
    for term in [brand_name, compact, spaced, f"{compact}AI", f"{compact}서비스", *semantic]:
        if term and term not in terms:
            terms.append(term)

    return {
        "original": brand_name,
        "korean_variants": [brand_name, compact, spaced],
        "english_variants": [compact, f"{compact}Check", f"{compact}Service"],
        "phonetic_variants": [compact.replace("체크", "첵"), compact.replace("크", "ㅋ")],
        "semantic_variants": semantic,
        "recommended_search_terms": terms[:8],
        "source": "fallback",
    }


def generate_query_variants(brand_name: str, business_description: str, mock_mode: bool = False) -> dict:
    if mock_mode:
        return fallback_query_variants(brand_name, business_description)

    system_prompt = (
        "상표 검색용 브랜드명 변형어를 생성한다. 반드시 JSON 객체만 반환한다. "
        "키는 original, korean_variants, english_variants, phonetic_variants, "
        "semantic_variants, recommended_search_terms를 사용한다."
    )
    user_prompt = f"브랜드명: {brand_name}\n사용 분야: {business_description}\n검색어는 5개 이상 10개 이하로 제안해줘."

    try:
        data = OpenAIJsonClient().generate_json(system_prompt, user_prompt)
    except Exception:
        data = fallback_query_variants(brand_name, business_description)

    if not data.get("recommended_search_terms"):
        data = fallback_query_variants(brand_name, business_description)
    return data


def infer_likely_classes(business_description: str) -> list[str]:
    text = business_description.lower()
    classes: list[str] = []
    keyword_map = {
        "42": ["ai", "소프트웨어", "웹", "앱", "플랫폼", "saas", "데이터", "개발"],
        "35": ["쇼핑", "광고", "마케팅", "커머스", "판매", "중개"],
        "41": ["교육", "강의", "콘텐츠", "커뮤니티", "출판"],
        "45": ["법률", "상표", "지식재산", "컨설팅", "정보 제공"],
        "43": ["카페", "식당", "음식", "베이커리"],
    }
    for nice_class, keywords in keyword_map.items():
        if any(keyword in text for keyword in keywords):
            classes.append(nice_class)
    return classes or ["35", "42"]

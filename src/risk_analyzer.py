from __future__ import annotations


LABELS = {"low": "낮음", "medium": "중간", "high": "높음"}


def _risk_from_score(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _reason(candidate: dict) -> str:
    name_similarity = candidate.get("name_similarity", 0)
    class_similarity = candidate.get("class_similarity", 0)
    status_risk = candidate.get("status_risk", 0)
    status = candidate.get("status") or "미상"

    if name_similarity >= 0.9 and class_similarity > 0 and status_risk >= 0.8:
        return (
            f"입력명과 표장이 거의 동일하게 검색되었고, 상품류가 겹칠 가능성이 있으며 "
            f"상태가 {status}로 표시되어 전문가 검토를 권장합니다."
        )
    if name_similarity >= 0.9 and status_risk >= 0.8:
        return f"입력명과 표장이 거의 동일하게 검색되었고, 상태가 {status}로 표시되어 추가 확인이 필요합니다."
    if name_similarity >= 0.75 and class_similarity > 0:
        return "표장 유사도가 높고 사용 예정 분야와 상품류/서비스류가 겹칠 가능성이 있어 추가 검토가 필요합니다."
    if class_similarity > 0:
        return "표장 자체의 유사도와 별개로, 사용 예정 분야와 상품류/서비스류가 겹칠 가능성이 있습니다."
    if status_risk >= 0.8:
        return f"상태가 {status}로 표시되어 현재 권리 상태와 지정상품을 함께 확인하는 것이 좋습니다."
    if name_similarity >= 0.75:
        return "표장이 입력명과 유사하게 검색되어 동일·유사 표장 여부를 추가 확인하는 것이 좋습니다."
    return "검색 결과의 표장, 상태, 지정상품을 기준으로 추가 확인이 필요한 후보입니다."


def analyze_risk(scored_candidates: list[dict]) -> dict:
    top_candidates = sorted(
        scored_candidates,
        key=lambda item: (
            item.get("class_similarity", 0) > 0,
            item.get("total_score", 0),
            item.get("status_risk", 0),
        ),
        reverse=True,
    )[:3]
    max_score = top_candidates[0]["total_score"] if top_candidates else 0.0
    overall_risk = _risk_from_score(max_score)
    enriched = []
    for candidate in top_candidates:
        item = dict(candidate)
        item["risk_reason"] = _reason(candidate)
        enriched.append(item)
    return {
        "overall_risk": overall_risk,
        "overall_risk_label": LABELS[overall_risk],
        "top_candidates": enriched,
        "summary": f"예비 위험도는 {LABELS[overall_risk]}으로 산출되었습니다. 결과는 추가 확인이 필요합니다.",
    }

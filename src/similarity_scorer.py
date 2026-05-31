from __future__ import annotations

from rapidfuzz import fuzz


def _clean(text: str | None) -> str:
    return "".join(str(text or "").lower().split())


def calc_name_similarity(input_name: str, candidate_name: str) -> float:
    source = _clean(input_name)
    target = _clean(candidate_name)
    if not source or not target:
        return 0.0
    return max(
        fuzz.ratio(source, target),
        fuzz.partial_ratio(source, target),
        fuzz.token_sort_ratio(source, target),
    ) / 100


def calc_phonetic_similarity(input_name: str, candidate_name: str) -> float:
    source = _clean(input_name).replace("체크", "첵").replace("크", "ㅋ")
    target = _clean(candidate_name).replace("체크", "첵").replace("크", "ㅋ")
    return fuzz.ratio(source, target) / 100 if source and target else 0.0


def calc_semantic_similarity(input_name: str, candidate_name: str) -> float:
    source = set(_clean(input_name))
    target = set(_clean(candidate_name))
    if not source or not target:
        return 0.0
    return len(source & target) / len(source | target)


def calc_class_similarity(likely_classes: list[str], candidate_classes: list[str]) -> float:
    source = {str(item).zfill(2) for item in likely_classes if item}
    target = {str(item).zfill(2) for item in candidate_classes if item}
    if not source or not target:
        return 0.0
    return len(source & target) / len(source)


def calc_status_risk(status: str | None) -> float:
    text = str(status or "")
    if any(token in text for token in ["등록", "존속", "유효"]):
        return 1.0
    if any(token in text for token in ["출원", "공고", "심사"]):
        return 0.8
    if any(token in text for token in ["미상", "불명"]):
        return 0.45
    if any(token in text for token in ["거절", "취하", "포기"]):
        return 0.25
    if any(token in text for token in ["소멸", "만료", "말소"]):
        return 0.15
    return 0.4


def risk_level_from_score(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def score_candidate(input_name: str, likely_classes: list[str], candidate: dict) -> dict:
    name_similarity = calc_name_similarity(input_name, candidate.get("trademark_name", ""))
    phonetic_similarity = calc_phonetic_similarity(input_name, candidate.get("trademark_name", ""))
    semantic_similarity = calc_semantic_similarity(input_name, candidate.get("trademark_name", ""))
    class_similarity = calc_class_similarity(likely_classes, candidate.get("nice_classes", []))
    status_risk = calc_status_risk(candidate.get("status"))
    total_score = (
        name_similarity * 0.30
        + phonetic_similarity * 0.20
        + semantic_similarity * 0.15
        + class_similarity * 0.25
        + status_risk * 0.10
    )
    if likely_classes and candidate.get("nice_classes") and class_similarity == 0:
        total_score *= 0.82
    scored = dict(candidate)
    scored.update(
        {
            "name_similarity": round(name_similarity, 3),
            "phonetic_similarity": round(phonetic_similarity, 3),
            "semantic_similarity": round(semantic_similarity, 3),
            "class_similarity": round(class_similarity, 3),
            "status_risk": round(status_risk, 3),
            "total_score": round(total_score, 3),
            "risk_level": risk_level_from_score(total_score),
        }
    )
    return scored


def score_candidates(input_name: str, likely_classes: list[str], candidates: list[dict]) -> list[dict]:
    return sorted(
        [score_candidate(input_name, likely_classes, candidate) for candidate in candidates],
        key=lambda item: item["total_score"],
        reverse=True,
    )

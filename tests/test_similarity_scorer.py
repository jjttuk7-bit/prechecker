from src.similarity_scorer import (
    calc_class_similarity,
    calc_name_similarity,
    calc_status_risk,
    score_candidate,
)


def test_name_similarity_is_high_for_close_names():
    assert calc_name_similarity("먼저체크", "먼저 첵") >= 0.7


def test_class_similarity_uses_overlap_ratio():
    assert calc_class_similarity(["42", "45"], ["42"]) == 0.5
    assert calc_class_similarity(["42"], []) == 0.0


def test_status_risk_maps_active_status_higher_than_dead_status():
    assert calc_status_risk("등록") > calc_status_risk("소멸")
    assert calc_status_risk("출원") > calc_status_risk("거절")


def test_score_candidate_returns_total_score_and_risk_level():
    candidate = {
        "trademark_name": "먼저체크",
        "status": "등록",
        "nice_classes": ["42"],
        "designated_goods": ["소프트웨어 개발업"],
    }

    scored = score_candidate("먼저체크", ["42"], candidate)

    assert scored["total_score"] >= 0.75
    assert scored["risk_level"] == "high"

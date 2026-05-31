from src.pipeline import run_precheck


def test_mock_pipeline_generates_report_and_top_candidates():
    result = run_precheck("먼저체크", "AI 기반 상표 검색 웹서비스", mock_mode=True)

    assert "먼저체크" in result["variants"]["recommended_search_terms"]
    assert len(result["candidates"]) >= 1
    assert len(result["risk"]["top_candidates"]) <= 3
    assert len(result["evidence"]) >= 1
    assert "전문가 검토" in result["risk"]["top_candidates"][0]["risk_reason"]
    assert "근거 지식" in result["report_html"]
    assert "본 리포트는 KIPRIS 검색 결과와 AI 분석을 기반으로 한 예비 검토 자료입니다" in result["report_html"]


def test_mock_pipeline_prioritizes_matching_business_class_in_top_candidates():
    result = run_precheck("모닝썬", "카페", mock_mode=True)

    top_candidate = result["risk"]["top_candidates"][0]

    assert "43" in top_candidate["nice_classes"]
    assert top_candidate["class_similarity"] > 0

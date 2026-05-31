from src.rag_retriever import group_evidence_by_category, related_evidence_for_candidate, retrieve_evidence


def test_retrieve_evidence_returns_class_and_status_context():
    evidence = retrieve_evidence(
        business_description="카페",
        likely_classes=["43"],
        top_candidates=[
            {
                "status": "등록",
                "nice_classes": ["43"],
                "designated_goods": ["카페업", "음식점업"],
            }
        ],
    )

    titles = [item["title"] for item in evidence]

    assert any("제43류" in title for title in titles)
    assert any("등록 상태" in title for title in titles)
    assert all("source" in item for item in evidence)
    assert all("category" in item for item in evidence)


def test_related_evidence_for_candidate_prioritizes_matching_class_and_status():
    evidence = retrieve_evidence(
        business_description="카페",
        likely_classes=["43"],
        top_candidates=[
            {
                "status": "등록",
                "nice_classes": ["43"],
                "designated_goods": ["카페업", "음식점업"],
            }
        ],
    )

    related = related_evidence_for_candidate(
        {
            "status": "등록",
            "nice_classes": ["43"],
            "designated_goods": ["카페업"],
        },
        evidence,
    )

    assert len(related) >= 1
    assert related[0]["category"] in {"상품류 근거", "상태값 근거"}


def test_retrieve_evidence_deduplicates_by_id_and_grouping_limits_categories():
    evidence = retrieve_evidence(
        business_description="카페 음식점 카페업",
        likely_classes=["43", "43"],
        top_candidates=[
            {"status": "등록", "nice_classes": ["43"], "designated_goods": ["카페업"]},
            {"status": "등록", "nice_classes": ["43"], "designated_goods": ["음식점업"]},
        ],
        limit=8,
    )

    ids = [item["id"] for item in evidence]
    grouped = group_evidence_by_category(evidence, per_category_limit=1)

    assert len(ids) == len(set(ids))
    assert all(len(items) <= 1 for items in grouped.values())
    assert "상품류 근거" in grouped

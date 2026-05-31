from app import candidate_table_rows


def test_candidate_table_rows_marks_missing_designated_goods_as_detail_needed():
    rows = candidate_table_rows(
        [
            {
                "trademark_name": "카페브레리",
                "status": "등록",
                "nice_classes": ["43"],
                "designated_goods": [],
                "name_similarity": 1,
                "class_similarity": 1,
                "status_risk": 1,
                "total_score": 0.9,
                "risk_level": "high",
            }
        ]
    )

    assert rows[0]["지정상품"] == "상세 조회 필요"

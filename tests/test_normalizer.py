from src.kipris_client import parse_kipris_response
from src.trademark_normalizer import normalize_items


def test_normalize_items_supports_varied_kipris_keys():
    raw_items = [
        {
            "applicationNumber": "40-2024-000001",
            "registrationNumber": "40-1234567",
            "title": "먼저체크",
            "applicationStatus": "등록",
            "viennaCode": "",
            "classificationCode": "42, 45",
            "designatedGoods": "소프트웨어 개발업; 법률 정보 제공업",
            "applicantName": "홍길동",
        }
    ]

    normalized = normalize_items(raw_items)

    assert normalized[0]["trademark_name"] == "먼저체크"
    assert normalized[0]["application_number"] == "40-2024-000001"
    assert normalized[0]["nice_classes"] == ["42", "45"]
    assert "소프트웨어 개발업" in normalized[0]["designated_goods"]


def test_parse_kipris_response_accepts_json_and_xml():
    json_items = parse_kipris_response('{"body":{"items":[{"title":"A"}]}}')
    xml_items = parse_kipris_response(
        "<response><body><items><item><title>B</title></item></items></body></response>"
    )

    assert json_items == [{"title": "A"}]
    assert xml_items == [{"title": "B"}]


def test_normalize_items_supports_kipris_designation_goods_hangeul_name():
    raw_items = [
        {
            "Title": "카페브레리",
            "ApplicationStatus": "등록",
            "ClassificationCode": "43",
            "DesignationGoodsHangeulName": "카페업; 음식점업",
        }
    ]

    normalized = normalize_items(raw_items)

    assert normalized[0]["nice_classes"] == ["43"]
    assert normalized[0]["designated_goods"] == ["카페업", "음식점업"]

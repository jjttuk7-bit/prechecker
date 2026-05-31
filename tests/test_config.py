from src.config import parse_extra_params


def test_parse_extra_params_supports_query_string_format():
    assert parse_extra_params("searchRecentYear=0&foo=bar") == {
        "searchRecentYear": "0",
        "foo": "bar",
    }


def test_parse_extra_params_returns_empty_dict_for_blank_value():
    assert parse_extra_params("") == {}

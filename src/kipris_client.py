from __future__ import annotations

import json
from pathlib import Path
import time
import xml.etree.ElementTree as ET
from typing import Any

import requests

from .config import BASE_DIR, ensure_data_dirs, get_settings


def _flatten_xml(element: ET.Element) -> dict[str, Any]:
    children = list(element)
    if not children:
        return {element.tag.split("}")[-1]: (element.text or "").strip()}
    data: dict[str, Any] = {}
    for child in children:
        child_data = _flatten_xml(child)
        for key, value in child_data.items():
            if key in data:
                if not isinstance(data[key], list):
                    data[key] = [data[key]]
                data[key].append(value)
            else:
                data[key] = value
    return data


def _extract_items_from_json(data: Any) -> list[dict]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []
    for key in ("items", "item", "trademarks", "results", "result", "data"):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = _extract_items_from_json(value)
            if nested:
                return nested
            return [value]
    for value in data.values():
        nested = _extract_items_from_json(value)
        if nested:
            return nested
    return []


def parse_kipris_response(text: str) -> list[dict]:
    clean = (text or "").strip()
    if not clean:
        return []
    try:
        return _extract_items_from_json(json.loads(clean))
    except json.JSONDecodeError:
        pass

    try:
        root = ET.fromstring(clean)
    except ET.ParseError:
        return []

    item_elements = [el for el in root.iter() if el.tag.split("}")[-1].lower() == "item"]
    if item_elements:
        return [_flatten_xml(item) for item in item_elements]
    flattened = _flatten_xml(root)
    return _extract_items_from_json(flattened) or [flattened]


def mock_trademark_results(keyword: str) -> list[dict]:
    return [
        {
            "title": keyword,
            "applicationNumber": "40-2024-000001",
            "registrationNumber": "40-1234567",
            "applicationStatus": "등록",
            "classificationCode": "42",
            "designatedGoods": "소프트웨어 개발업; 온라인 정보 제공업; 플랫폼 서비스업",
            "applicantName": "모의권리자",
            "search_keyword": keyword,
        },
        {
            "title": f"{keyword}랩",
            "applicationNumber": "40-2023-000002",
            "registrationNumber": "",
            "applicationStatus": "출원",
            "classificationCode": "35, 41",
            "designatedGoods": "광고업; 교육 서비스업; 콘텐츠 제공업",
            "applicantName": "테스트출원인",
            "search_keyword": keyword,
        },
        {
            "title": f"{keyword}클럽",
            "applicationNumber": "40-2018-000003",
            "registrationNumber": "40-7654321",
            "applicationStatus": "소멸",
            "classificationCode": "43",
            "designatedGoods": "카페업; 음식점업",
            "applicantName": "과거권리자",
            "search_keyword": keyword,
        },
    ]


def search_trademark(keyword: str, page: int = 1, rows: int = 20, mock_mode: bool = False) -> tuple[list[dict], str | None]:
    if mock_mode:
        return mock_trademark_results(keyword), None

    settings = get_settings()
    if not settings.kipris_endpoint or not settings.kipris_api_key:
        return [], "KIPRIS endpoint or API key is not configured."

    params = {
        settings.kipris_key_param: settings.kipris_api_key,
        settings.kipris_search_param: keyword,
        settings.kipris_page_param: page,
        settings.kipris_rows_param: rows,
    }
    try:
        response = requests.get(settings.kipris_endpoint, params=params, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        return [], str(exc)

    if settings.save_raw_responses:
        ensure_data_dirs()
        safe_keyword = "".join(ch for ch in keyword if ch.isalnum() or ch in ("-", "_"))[:40] or "keyword"
        raw_path = Path(BASE_DIR / "data" / "raw" / f"{int(time.time())}_{safe_keyword}.txt")
        raw_path.write_text(response.text, encoding="utf-8")

    return parse_kipris_response(response.text), None

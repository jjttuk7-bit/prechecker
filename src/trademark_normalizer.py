from __future__ import annotations

import re
from typing import Any


FIELD_ALIASES = {
    "trademark_name": ["trademarkName", "trademark_name", "title", "markName", "name", "brandName"],
    "application_number": ["applicationNumber", "appNo", "application_no", "applNo"],
    "registration_number": ["registrationNumber", "regNo", "registration_no"],
    "status": ["applicationStatus", "status", "regStatus", "rightStatus", "finalStatus"],
    "nice_classes": ["classificationCode", "niceClass", "nice_classes", "classNo", "goodsClass"],
    "designated_goods": [
        "designatedGoods",
        "designationGoods",
        "designatedGood",
        "DesignationGoodsHangeulName",
        "designationGoodsHangeulName",
        "designationGoodsName",
        "goods",
        "goodsName",
        "goodsNameKor",
        "productName",
        "productNameHangul",
        "serviceList",
    ],
    "applicant": ["applicantName", "applicant", "ownerName", "rightHolder"],
    "application_date": ["applicationDate", "appDate", "filingDate"],
    "registration_date": ["registrationDate", "regDate"],
    "search_keyword": ["search_keyword", "keyword"],
}


def _get_any(item: dict[str, Any], keys: list[str]) -> Any:
    lowered = {str(key).lower(): value for key, value in item.items()}
    for key in keys:
        if key in item and item[key] not in (None, ""):
            return item[key]
        value = lowered.get(key.lower())
        if value not in (None, ""):
            return value
    return None


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                nested = _get_any(item, FIELD_ALIASES["designated_goods"])
                parts.extend(_as_list(nested) if nested else [])
            else:
                parts.append(item)
    elif isinstance(value, dict):
        nested = _get_any(value, FIELD_ALIASES["designated_goods"])
        parts = _as_list(nested) if nested else list(value.values())
    else:
        parts = re.split(r"[,;/|·\n]+", str(value))
    return [str(part).strip() for part in parts if str(part).strip()]


def _classes(value: Any) -> list[str]:
    classes: list[str] = []
    for part in _as_list(value):
        found = re.findall(r"\d{1,2}", part)
        if found:
            classes.extend(found)
    unique: list[str] = []
    for item in classes:
        normalized = item.zfill(2) if len(item) == 1 else item
        if normalized not in unique:
            unique.append(normalized)
    return unique


def normalize_status(status: Any) -> str:
    text = str(status or "미상").strip()
    if any(token in text for token in ["등록", "존속", "유효"]):
        return "등록"
    if any(token in text for token in ["출원", "공고", "심사", "대기"]):
        return "출원"
    if any(token in text for token in ["거절", "무효", "포기", "취하"]):
        return "거절/취하"
    if any(token in text for token in ["소멸", "만료", "말소"]):
        return "소멸"
    return text or "미상"


def normalize_items(raw_items: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        record = {
            "trademark_name": str(_get_any(item, FIELD_ALIASES["trademark_name"]) or "").strip(),
            "application_number": str(_get_any(item, FIELD_ALIASES["application_number"]) or "").strip(),
            "registration_number": str(_get_any(item, FIELD_ALIASES["registration_number"]) or "").strip(),
            "status": normalize_status(_get_any(item, FIELD_ALIASES["status"])),
            "nice_classes": _classes(_get_any(item, FIELD_ALIASES["nice_classes"])),
            "designated_goods": _as_list(_get_any(item, FIELD_ALIASES["designated_goods"])),
            "applicant": str(_get_any(item, FIELD_ALIASES["applicant"]) or "").strip(),
            "application_date": str(_get_any(item, FIELD_ALIASES["application_date"]) or "").strip(),
            "registration_date": str(_get_any(item, FIELD_ALIASES["registration_date"]) or "").strip(),
            "search_keyword": str(_get_any(item, FIELD_ALIASES["search_keyword"]) or "").strip(),
        }
        key = (record["trademark_name"], record["application_number"], record["registration_number"])
        if record["trademark_name"] and key not in seen:
            seen.add(key)
            normalized.append(record)
    return normalized

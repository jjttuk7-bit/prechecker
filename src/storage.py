from __future__ import annotations

from pathlib import Path
import re
import time

from .config import BASE_DIR, ensure_data_dirs


def save_report_html(brand_name: str, html: str) -> Path:
    ensure_data_dirs()
    safe_name = re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", brand_name).strip("_") or "report"
    path = BASE_DIR / "data" / "reports" / f"{int(time.time())}_{safe_name}.html"
    path.write_text(html, encoding="utf-8")
    return path

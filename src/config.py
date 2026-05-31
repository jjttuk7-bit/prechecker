from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    kipris_api_key: str = os.getenv("KIPRIS_API_KEY", "")
    kipris_endpoint: str = os.getenv("KIPRIS_TRADEMARK_ENDPOINT", "")
    kipris_key_param: str = os.getenv("KIPRIS_KEY_PARAM", "ServiceKey")
    kipris_search_param: str = os.getenv("KIPRIS_SEARCH_PARAM", "searchString")
    kipris_page_param: str = os.getenv("KIPRIS_PAGE_PARAM", "pageNo")
    kipris_rows_param: str = os.getenv("KIPRIS_ROWS_PARAM", "numOfRows")
    app_env: str = os.getenv("APP_ENV", "local")
    save_raw_responses: bool = os.getenv("SAVE_RAW_RESPONSES", "true").lower() == "true"


def get_settings() -> Settings:
    return Settings()


def ensure_data_dirs() -> None:
    (BASE_DIR / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "data" / "reports").mkdir(parents=True, exist_ok=True)

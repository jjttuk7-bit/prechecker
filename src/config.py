from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
from urllib.parse import parse_qsl

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


def _secret_value(name: str, default: str = "") -> str:
    env_value = os.getenv(name)
    if env_value not in (None, ""):
        return env_value
    try:
        import streamlit as st

        value = st.secrets.get(name, default)
        return str(value) if value not in (None, "") else default
    except Exception:
        return default


def _secret_bool(name: str, default: bool = False) -> bool:
    value = _secret_value(name, str(default).lower())
    return value.lower() in {"1", "true", "yes", "y", "on"}


def parse_extra_params(raw: str) -> dict[str, str]:
    if not raw:
        return {}
    return {key: value for key, value in parse_qsl(raw, keep_blank_values=True)}


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = field(default_factory=lambda: _secret_value("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: _secret_value("OPENAI_MODEL", "gpt-4.1-mini"))
    kipris_api_key: str = field(default_factory=lambda: _secret_value("KIPRIS_API_KEY"))
    kipris_endpoint: str = field(default_factory=lambda: _secret_value("KIPRIS_TRADEMARK_ENDPOINT"))
    kipris_key_param: str = field(default_factory=lambda: _secret_value("KIPRIS_KEY_PARAM", "ServiceKey"))
    kipris_search_param: str = field(default_factory=lambda: _secret_value("KIPRIS_SEARCH_PARAM", "searchString"))
    kipris_page_param: str = field(default_factory=lambda: _secret_value("KIPRIS_PAGE_PARAM", "pageNo"))
    kipris_rows_param: str = field(default_factory=lambda: _secret_value("KIPRIS_ROWS_PARAM", "numOfRows"))
    kipris_extra_params: dict[str, str] | None = None
    app_env: str = field(default_factory=lambda: _secret_value("APP_ENV", "local"))
    save_raw_responses: bool = field(default_factory=lambda: _secret_bool("SAVE_RAW_RESPONSES", True))

    def __post_init__(self) -> None:
        if self.kipris_extra_params is None:
            object.__setattr__(
                self,
                "kipris_extra_params",
                parse_extra_params(_secret_value("KIPRIS_EXTRA_PARAMS", "")),
            )


def get_settings() -> Settings:
    return Settings()


def ensure_data_dirs() -> None:
    (BASE_DIR / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "data" / "reports").mkdir(parents=True, exist_ok=True)

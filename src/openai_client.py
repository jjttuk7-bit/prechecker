from __future__ import annotations

import json
from typing import Any

from .config import get_settings


class OpenAIJsonClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    @property
    def available(self) -> bool:
        return bool(self.settings.openai_api_key)

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self.available:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        client = self._get_client()
        response = client.responses.create(
            model=self.settings.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text={"format": {"type": "json_object"}},
        )
        text = getattr(response, "output_text", "")
        if not text:
            raise RuntimeError("OpenAI response did not include output_text.")
        return json.loads(text)

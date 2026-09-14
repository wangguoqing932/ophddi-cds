"""LLM client for ophthalmic-ddi-cds — OpenAI-compatible (DeepSeek)."""
from __future__ import annotations

import os
from dataclasses import dataclass

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


@dataclass
class LLMResponse:
    text: str
    degraded: bool = False


class LLMClient:
    def __init__(self, provider: str = "deepseek", temperature: float = 0.0, max_tokens: int = 256):
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None

    def _ensure_client(self):
        if self._client is not None:
            return
        try:
            from openai import OpenAI
            key = os.getenv("DEEPSEEK_API_KEY", "")
            base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            if not key:
                raise RuntimeError("DEEPSEEK_API_KEY not set")
            self._client = OpenAI(api_key=key, base_url=base)
        except Exception:
            self._client = False  # mark as unavailable

    def complete(self, prompt: str, system: str | None = None) -> LLMResponse:
        self._ensure_client()
        if self._client is False:
            return LLMResponse(text="unknown", degraded=True)
        try:
            msgs = []
            if system:
                msgs.append({"role": "system", "content": system})
            msgs.append({"role": "user", "content": prompt})
            resp = self._client.chat.completions.create(
                model=os.getenv("LLM_CHAT_MODEL", "deepseek-chat"),
                messages=msgs,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return LLMResponse(text=resp.choices[0].message.content or "", degraded=False)
        except Exception:
            return LLMResponse(text="unknown", degraded=True)

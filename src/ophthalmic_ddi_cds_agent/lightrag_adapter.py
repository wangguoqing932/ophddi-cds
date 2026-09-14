"""LightRAG query adapter using real doubao embedding matching the build."""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Set env vars BEFORE LightRAG imports (LightRAG reads OPENAI_API_BASE for fallback base_url)
load_dotenv(PROJECT_ROOT / ".env")
os.environ.setdefault("OPENAI_API_KEY", os.getenv("DEEPSEEK_API_KEY", ""))
os.environ.setdefault("OPENAI_BASE_URL", os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
os.environ.setdefault("OPENAI_API_BASE", os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
os.environ.setdefault("LLM_MODEL", "deepseek-chat")

from .embeddings import EmbeddingSettings, doubao_embed


class LightRAGAdapter:
    def __init__(self, working_dir: str | None = None):
        self.working_dir = Path(working_dir or PROJECT_ROOT / "data" / "processed" / "lightrag_index")
        self._rag = None

    async def _ensure_rag(self):
        if self._rag is not None:
            return

        from lightrag import LightRAG
        from lightrag.llm.openai import openai_complete as oai
        from lightrag.utils import EmbeddingFunc
        from functools import wraps

        settings = EmbeddingSettings.from_env()

        @wraps(oai)
        async def llm(prompt, system_prompt=None, **kw):
            for dup in ("model", "timeout", "api_key", "base_url"):
                kw.pop(dup, None)
            return await oai(prompt, system_prompt=system_prompt, **kw)

        self._rag = LightRAG(
            working_dir=str(self.working_dir),
            llm_model_func=llm,
            embedding_func=EmbeddingFunc(
                embedding_dim=settings.dimension,
                max_token_size=8192,
                func=lambda texts: doubao_embed(texts, settings),
            ),
            llm_model_name="deepseek-chat",
        )
        await self._rag.initialize_storages()

    async def query(self, prompt: str, mode: str = "naive") -> str:
        from lightrag.base import QueryParam
        await self._ensure_rag()
        result = await self._rag.aquery(prompt, param=QueryParam(mode=mode))
        return str(result)

    async def close(self):
        self._rag = None

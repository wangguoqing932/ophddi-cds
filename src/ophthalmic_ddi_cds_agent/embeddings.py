"""Shared Ark/Doubao embedding configuration for LightRAG build and query."""
from __future__ import annotations
import os
from dataclasses import dataclass
import httpx
import numpy as np

@dataclass(frozen=True)
class EmbeddingSettings:
    api_key:str; endpoint_id:str; base_url:str; dimension:int
    @classmethod
    def from_env(cls)->'EmbeddingSettings':
        key=os.getenv('HUANYU_EMBED_API_KEY') or os.getenv('ARK_DOUBAO_API_KEY','')
        endpoint=os.getenv('HUANYU_EMBED_ENDPOINT_ID') or os.getenv('DOUBAO_ENDPOINT_ID','')
        base=os.getenv('HUANYU_EMBED_BASE_URL') or os.getenv('ARK_DOUBAO_BASE_URL','https://ark.cn-beijing.volces.com/api/v3')
        dimension=int(os.getenv('HUANYU_EMBED_DIMENSION','2048'))
        if not key or not endpoint:raise RuntimeError('Ark/Doubao embedding configuration is missing')
        return cls(key,endpoint,base.rstrip('/'),dimension)

async def doubao_embed(texts:list[str],settings:EmbeddingSettings|None=None)->np.ndarray:
    """Embed texts via doubao multimodal API. API returns one vector per call,
    so we call once per text with a concurrency limit."""
    settings=settings or EmbeddingSettings.from_env()
    import asyncio
    sem = asyncio.Semaphore(8)
    async def _one(text:str, client:httpx.AsyncClient) -> np.ndarray:
        async with sem:
            payload={'model':settings.endpoint_id,'input':[{'type':'text','text':text}]}
            resp = await client.post(
                f'{settings.base_url}/embeddings/multimodal',
                headers={'Authorization':f'Bearer {settings.api_key}','Content-Type':'application/json'},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            emb = data.get('data',{}).get('embedding')
            if emb is None:
                raise RuntimeError(f'No embedding in response: {list(data.keys())}')
            return np.asarray(emb, dtype=np.float32)
    async with httpx.AsyncClient(timeout=60) as client:
        tasks = [_one(t, client) for t in texts]
        results = await asyncio.gather(*tasks)
    result = np.stack(results)
    if result.ndim!=2 or result.shape[1]!=settings.dimension:
        raise RuntimeError(f'embedding dimension mismatch: expected {settings.dimension}, got {result.shape}')
    return result

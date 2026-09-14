"""Canonical OpenAI-compatible LLM configuration shared by LightRAG paths."""
from __future__ import annotations
import os
from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass(frozen=True)
class LLMSettings:
    provider:str; api_key:str; base_url:str; model:str
    @classmethod
    def from_env(cls)->'LLMSettings':
        candidates=(
            ('huanyu_bulk',os.getenv('HUANYU_BULK_API_KEY',''),os.getenv('HUANYU_BULK_BASE_URL',''),os.getenv('HUANYU_BULK_MODEL','')),
            ('deepseek',os.getenv('DEEPSEEK_API_KEY',''),os.getenv('DEEPSEEK_BASE_URL',''),os.getenv('LLM_CHAT_MODEL','')),
            ('huanyu_legacy',os.getenv('HUANYU_LLM_API_KEY',''),os.getenv('HUANYU_LLM_BASE_URL',''),os.getenv('HUANYU_LLM_MODEL','')),
        )
        key=os.getenv('LLM_MODEL','')
        for provider,api_key,base_url,model in candidates:
            if api_key and base_url:
                return cls(provider,api_key,base_url.rstrip('/'),key or model or 'deepseek-v4-flash')
        raise RuntimeError('No configured OpenAI-compatible extraction LLM provider')
    def apply(self)->None:
        os.environ['OPENAI_API_KEY']=self.api_key
        os.environ['OPENAI_BASE_URL']=self.base_url
        os.environ['OPENAI_API_BASE']=self.base_url
    def sanitized(self)->dict[str,str]:
        return {'provider':self.provider,'model':self.model,'host':urlparse(self.base_url).netloc}

"""Cached public-source acquisition for Phase 2 evidence."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

import requests

PARSER_VERSION = "phase2-evidence-sources-v1"
USER_AGENT = "ophthalmic-ddi-cds/0.1 (mailto:registry@example.invalid)"


@dataclass(frozen=True)
class EvidenceSource:
    provider: str
    source_id: str
    url: str
    retrieved_at: str
    cache_path: str
    content_sha256: str
    content_type: str
    query: str = ""
    license_note: str = "public-source"

    def as_dict(self) -> dict[str, str]:
        return self.__dict__.copy()


class EvidenceSourceClient:
    def __init__(self, root: Path, mode: str = "online", *, email: str = "registry@example.invalid") -> None:
        if mode not in {"online", "cache-only"}:
            raise ValueError("mode must be online or cache-only")
        self.root, self.mode, self.email = root, mode, email
        self.cache_root = root / "data" / "raw" / "evidence"

    def _path(self, provider: str, key: str, suffix: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_root / provider / f"{digest}{suffix}"

    def get(self, provider: str, source_id: str, url: str, *, query: str = "", suffix: str = ".bin", content_type: str = "application/octet-stream") -> tuple[bytes, EvidenceSource]:
        path = self._path(provider, f"{source_id}|{url}", suffix)
        if path.exists():
            content = path.read_bytes()
            return content, EvidenceSource(provider, source_id, url, "cached", str(path.relative_to(self.root)), hashlib.sha256(content).hexdigest(), content_type, query)
        if self.mode == "cache-only":
            raise FileNotFoundError(f"missing cache: {provider}:{source_id}")
        response = requests.get(url, timeout=45, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        content = response.content
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return content, EvidenceSource(provider, source_id, response.url, datetime.now(UTC).isoformat(), str(path.relative_to(self.root)), hashlib.sha256(content).hexdigest(), response.headers.get("content-type", content_type), query)

    def dailymed_label(self, setid: str) -> tuple[bytes, EvidenceSource]:
        url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}.xml"
        return self.get("dailymed", setid, url, suffix=".xml", content_type="application/xml")

    def pubmed_search(self, query: str, max_results: int) -> tuple[dict, EvidenceSource]:
        params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json", "tool": "ophthalmic_ddi_cds", "email": self.email}
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urlencode(params)
        content, source = self.get("pubmed_search", hashlib.sha256(query.encode()).hexdigest(), url, query=query, suffix=".json", content_type="application/json")
        return json.loads(content), source

    def pubmed_fetch(self, pmids: list[str]) -> tuple[bytes, EvidenceSource]:
        joined = ",".join(pmids)
        params = {"db": "pubmed", "id": joined, "retmode": "xml", "tool": "ophthalmic_ddi_cds", "email": self.email}
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urlencode(params)
        return self.get("pubmed", joined, url, query=joined, suffix=".xml", content_type="application/xml")

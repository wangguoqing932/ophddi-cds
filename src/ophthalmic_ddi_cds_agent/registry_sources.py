"""Public-source registry enrichment with hashed local response caching."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

PARSER_VERSION = "phase1-registry-sources-v1"


@dataclass(frozen=True)
class SourceLookup:
    provider: str
    source_id: str
    url: str
    payload: dict[str, Any]
    cache_path: str
    response_sha256: str
    retrieved_at: str


class RegistrySourceClient:
    def __init__(self, cache_dir: Path, mode: str = "online", session: requests.Session | None = None) -> None:
        if mode not in {"online", "cache-only"}:
            raise ValueError("mode must be online or cache-only")
        self.cache_dir, self.mode, self.session = cache_dir, mode, session or requests.Session()

    def _cache_file(self, provider: str, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / provider / f"{digest}.json"

    def _request_json(self, provider: str, url: str, key: str) -> SourceLookup:
        path = self._cache_file(provider, key)
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            raw = path.read_bytes()
            return SourceLookup(provider, str(payload.get("source_id", key)), url, payload, str(path), hashlib.sha256(raw).hexdigest(), payload.get("retrieved_at", "cached"))
        if self.mode == "cache-only":
            raise FileNotFoundError(f"No cached {provider} response for {key}")
        response = self.session.get(url, timeout=30, headers={"Accept": "application/json", "User-Agent": "ophthalmic-ddi-cds/0.1"})
        response.raise_for_status()
        payload = response.json()
        envelope = {"source_id": key, "retrieved_at": datetime.now(UTC).isoformat(), "payload": payload}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(envelope, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        raw = path.read_bytes()
        return SourceLookup(provider, key, url, envelope, str(path), hashlib.sha256(raw).hexdigest(), envelope["retrieved_at"])

    def rxnorm(self, name: str) -> SourceLookup:
        return self._request_json("rxnorm", f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={quote(name)}&search=2", name)

    def pubchem(self, name: str) -> SourceLookup:
        return self._request_json("pubchem", f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{quote(name)}/property/Title/JSON", name)

    def dailymed(self, name: str) -> SourceLookup:
        return self._request_json("dailymed", f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={quote(name)}&pagesize=1", name)


def unwrap(lookup: SourceLookup) -> dict[str, Any]:
    return lookup.payload.get("payload", lookup.payload)


def extract_rxcui(lookup: SourceLookup) -> str:
    data = unwrap(lookup)
    return str(data.get("idGroup", {}).get("rxnormId", [""])[0])


def extract_pubchem_cid(lookup: SourceLookup) -> str:
    data = unwrap(lookup)
    props = data.get("PropertyTable", {}).get("Properties", [])
    return str(props[0].get("CID", "")) if props else ""

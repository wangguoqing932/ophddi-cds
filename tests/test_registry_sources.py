import json
from pathlib import Path

from ophthalmic_ddi_cds_agent.registry_sources import RegistrySourceClient, extract_pubchem_cid, extract_rxcui


def test_cache_only_replays_rxnorm_response(tmp_path: Path) -> None:
    client = RegistrySourceClient(tmp_path, "online")
    cache = client._cache_file("rxnorm", "Timolol")
    cache.parent.mkdir(parents=True)
    cache.write_text(json.dumps({"source_id": "Timolol", "retrieved_at": "2026-01-01T00:00:00Z", "payload": {"idGroup": {"rxnormId": ["10600"]}}}), encoding="utf-8")
    cached = RegistrySourceClient(tmp_path, "cache-only").rxnorm("Timolol")
    assert extract_rxcui(cached) == "10600"
    assert len(cached.response_sha256) == 64


def test_extract_pubchem_cid() -> None:
    class Lookup:
        payload = {"payload": {"PropertyTable": {"Properties": [{"CID": 5487}]}}}
    assert extract_pubchem_cid(Lookup()) == "5487"

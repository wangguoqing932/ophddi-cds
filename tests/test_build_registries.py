from pathlib import Path

import yaml

from ophthalmic_ddi_cds_agent.registry_builder import build
from ophthalmic_ddi_cds_agent.registry_sources import SourceLookup


def test_build_uses_fixture_enrichment(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path
    (root / "data/curation").mkdir(parents=True)
    (root / "configs").mkdir()
    (root / "data/curation/entity_a_candidates.yaml").write_text(yaml.safe_dump({"entities": [{"entity_a_id": "a1", "primary_name": "Timolol", "aliases": [], "category": "glaucoma", "active_mechanisms": [], "flags": ["beta_blocker"], "evidence_sources": [], "dosage_form": "drops", "ophthalmic_administration": "topical"}]}), encoding="utf-8")
    (root / "configs/flag_catalog.yaml").write_text(yaml.safe_dump({"flags": {"beta_blocker": {"sides": ["A"]}}, "derived_flags": {}}), encoding="utf-8")
    cache = root / "data/raw/test.json"; cache.parent.mkdir(parents=True); cache.write_text("{}", encoding="utf-8")
    def fake_enrich(record, client, project_root):
        from ophthalmic_ddi_cds_agent.schemas import SourceRecord
        source = SourceRecord(provider="fixture", source_id="1", url="https://example.test/1", retrieved_at="2026-01-01T00:00:00Z", response_sha256="a" * 64, cache_path="data/raw/test.json", parser_version="test", purpose="canonicalization")
        result = dict(record, canonical_name=record["primary_name"], provenance=[source], curation_status="source_enriched")
        return result, [source], []
    monkeypatch.setattr("ophthalmic_ddi_cds_agent.registry_builder.enrich", fake_enrich)
    output = root / "out"
    result = build(root, "A", "cache-only", root / "data/raw", output)
    assert result["entity_count"] == 1
    assert (output / "entities_a.csv").exists()

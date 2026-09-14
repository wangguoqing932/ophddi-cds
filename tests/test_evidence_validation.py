import hashlib
from pathlib import Path

from ophthalmic_ddi_cds_agent.evidence_validation import validate_evidence
from ophthalmic_ddi_cds_agent.schemas import EvidenceChunk


def record(root: Path, **overrides: object) -> EvidenceChunk:
    cache = root / "data/raw/evidence/test/source.txt"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text("source text", encoding="utf-8")
    data = {
        "evidence_id": "ev_test", "title": "Test", "source": "DailyMed", "source_type": "regulatory_label", "evidence_level": "A",
        "source_id": "label-1", "source_locator": "Warnings / excerpt 1", "verification_status": "approved_release",
        "retrieved_at": "2026-01-01T00:00:00Z", "cache_path": "data/raw/evidence/test/source.txt", "content_sha256": hashlib.sha256(cache.read_bytes()).hexdigest(),
        "parser_version": "test", "entities_a": ["a1"], "entities_b": ["b1"], "claim_text": "Source-located claim", "text": "Source-located claim", "url": "https://example.test/label",
    }
    data.update(overrides)
    return EvidenceChunk.model_validate(data)


def test_rejects_release_record_without_locator(tmp_path: Path) -> None:
    item = record(tmp_path, source_locator="")
    errors = validate_evidence([item], tmp_path, {"a1"}, {"b1"}, thresholds=False)
    assert any(error.startswith("missing source_locator") for error in errors)


def test_rejects_unknown_entity_and_bad_hash(tmp_path: Path) -> None:
    item = record(tmp_path, entities_a=["unknown"], content_sha256="x" * 64)
    errors = validate_evidence([item], tmp_path, {"a1"}, {"b1"}, thresholds=False)
    assert any(error.startswith("unknown entity_a") for error in errors)
    assert any(error.startswith("hash mismatch") for error in errors)


def test_reports_each_missing_level_quota(tmp_path: Path) -> None:
    item = record(tmp_path)
    errors = validate_evidence([item], tmp_path, {"a1"}, {"b1"})
    assert "B threshold:0<20" in errors
    assert "C threshold:0<100" in errors
    assert "D threshold:0<50" in errors
    assert "E threshold:0<50" in errors

from ophthalmic_ddi_cds_agent.registry_qa import validate_records
from ophthalmic_ddi_cds_agent.schemas import EntityA, SourceRecord


def source() -> SourceRecord:
    return SourceRecord(provider="test", source_id="x", url="https://example.test/x", retrieved_at="2026-01-01T00:00:00Z", response_sha256="a" * 64, cache_path="data/raw/test/x.json", parser_version="test", purpose="test")


def test_qa_rejects_unknown_flags() -> None:
    record = EntityA(entity_a_id="a1", primary_name="Timolol", canonical_name="Timolol", category="x", active_mechanisms=[], flags=["unknown"], evidence_sources=[], provenance=[source()])
    findings = validate_records([record], "A", {"flags": {}})
    assert any(item.code == "unknown_flag" for item in findings)

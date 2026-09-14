import json
from pathlib import Path
from ophthalmic_ddi_cds_agent.evidence_store import EvidenceStore


def test_store_preserves_citation_metadata(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    path.write_text(json.dumps({"evidence_id":"ev1","title":"Title","source":"PubMed","source_type":"pubmed_abstract","evidence_level":"D","source_id":"PMID:1","source_locator":"Abstract","pmid":"1","verification_status":"approved_release","retrieved_at":"x","cache_path":"x","content_sha256":"x","parser_version":"x","entities_a":["a1"],"entities_b":["b1"],"rule_ids":["rule1"],"claim_text":"claim","text":"excerpt","url":"https://pubmed.ncbi.nlm.nih.gov/1/"}) + "\n", encoding="utf-8")
    store = EvidenceStore(path)
    result = store.search(entity_a="a1", rule_id="rule1")
    assert result[0].pmid == "1"
    assert store.summary()["D"] == 1

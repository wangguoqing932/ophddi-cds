"""Validated, citation-preserving evidence repository."""
from __future__ import annotations
import json
from pathlib import Path
from .schemas import EvidenceChunk

class EvidenceStore:
    def __init__(self, path: Path) -> None:
        self.records = [EvidenceChunk.model_validate(json.loads(line)) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

    def search(self, *, entity_a: str = '', entity_b: str = '', rule_id: str = '') -> list[EvidenceChunk]:
        results = [item for item in self.records if (not entity_a or entity_a in item.entities_a) and (not entity_b or entity_b in item.entities_b) and (not rule_id or rule_id in item.rule_ids)]
        if not results and entity_a:
            results = [item for item in self.records if self._text_matches(item, entity_a, entity_b)]
        return results

    def _text_matches(self, item: EvidenceChunk, entity_a: str, entity_b: str) -> bool:
        haystack = (item.text + ' ' + item.title).lower()
        return entity_a.lower() in haystack or entity_b.lower() in haystack

    def summary(self) -> dict[str, int]:
        result = {'total': len(self.records)}
        for level in 'ABCDE':
            result[level] = sum(item.evidence_level == level for item in self.records)
        return result

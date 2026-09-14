"""Fail-closed validation for release-countable evidence."""
from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Iterable


RELEASE_STATES = {"approved_release"}
LEVELS = {"A", "B", "C", "D", "E"}


def validate_evidence(
    records: Iterable[object],
    root: Path,
    entity_a_ids: set[str],
    entity_b_ids: set[str],
    *,
    thresholds: bool = True,
    required_rule_ids: set[str] | None = None,
) -> list[str]:
    records = list(records)
    errors: list[str] = []
    seen_ids, seen_locator_text = set(), set()
    approved = []
    for record in records:
        if record.evidence_id in seen_ids: errors.append(f"duplicate evidence_id:{record.evidence_id}")
        seen_ids.add(record.evidence_id)
        if record.evidence_level not in LEVELS: errors.append(f"invalid level:{record.evidence_id}")
        if record.verification_status in RELEASE_STATES:
            approved.append(record)
            required = ("source_id", "url", "source_locator", "retrieved_at", "cache_path", "content_sha256", "parser_version", "claim_text")
            for field in required:
                if not getattr(record, field, ""): errors.append(f"missing {field}:{record.evidence_id}")
            cache = root / record.cache_path
            if not cache.exists(): errors.append(f"missing cache:{record.evidence_id}")
            elif hashlib.sha256(cache.read_bytes()).hexdigest() != record.content_sha256: errors.append(f"hash mismatch:{record.evidence_id}")
            key = (record.source_id, record.source_locator, " ".join(record.text.split()).casefold())
            if key in seen_locator_text: errors.append(f"duplicate locator/text:{record.evidence_id}")
            seen_locator_text.add(key)
            if record.evidence_level == "A" and record.source_type not in {"regulatory_label", "regulatory_communication"}: errors.append(f"invalid Level A source:{record.evidence_id}")
            if record.evidence_level == "B" and record.source_type not in {"authoritative_monograph", "pubmed_abstract", "pmc_fulltext"}: errors.append(f"invalid Level B source:{record.evidence_id}")
            if record.evidence_level in {"C", "D", "E"} and record.source_type not in {"pubmed_abstract", "pmc_fulltext"}: errors.append(f"invalid literature source:{record.evidence_id}")
            if record.evidence_level in {"C", "D", "E"} and not record.pmid: errors.append(f"missing pmid:{record.evidence_id}")
            if record.source_type == "drugbank_authorized" and not record.authorized_source: errors.append(f"unauthorized DrugBank:{record.evidence_id}")
        if not set(record.entities_a) <= entity_a_ids: errors.append(f"unknown entity_a:{record.evidence_id}")
        if not set(record.entities_b) <= entity_b_ids: errors.append(f"unknown entity_b:{record.evidence_id}")
    if required_rule_ids:
        supported = {rule_id for item in approved for rule_id in item.rule_ids}
        missing = sorted(required_rule_ids - supported)
        errors.extend(f"missing approved rule evidence:{rule_id}" for rule_id in missing)
    if thresholds:
        levels = Counter(item.evidence_level for item in approved)
        quotas = {"A": 30, "B": 20, "C": 100, "D": 50, "E": 50}
        for level, minimum in quotas.items():
            if levels[level] < minimum: errors.append(f"{level} threshold:{levels[level]}<{minimum}")
        if len(approved) < 250: errors.append(f"approved threshold:{len(approved)}<250")
    return errors

"""Shared deterministic implementation for Phase 1 registry builders."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .registry_qa import load_catalog, write_report
from .registry_sources import PARSER_VERSION, RegistrySourceClient, extract_pubchem_cid, extract_rxcui
from .schemas import EntityA, EntityB, SourceRecord


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def derived_flags(record: dict[str, Any], catalog: dict) -> list[str]:
    flags = set(record["flags"])
    name, drug_class = record.get("primary_name", record.get("generic_name", "")), record.get("drug_class", "")
    for flag, conditions in catalog.get("derived_flags", {}).items():
        for condition in conditions:
            field, expected = condition.split(":", 1)
            value = {"canonical_name": name, "drug_class": drug_class, "flags": flags}.get(field, "")
            if (field == "flags" and expected in flags) or (field != "flags" and ((expected.endswith("*") and str(value).startswith(expected[:-1])) or value == expected)):
                flags.add(flag)
    return sorted(flags)


def source_record(lookup, purpose: str, project_root: Path) -> SourceRecord:
    path = Path(lookup.cache_path)
    try:
        relative = str(path.relative_to(project_root))
    except ValueError:
        relative = str(path)
    return SourceRecord(provider=lookup.provider, source_id=lookup.source_id, url=lookup.url, retrieved_at=lookup.retrieved_at, response_sha256=lookup.response_sha256, cache_path=relative, parser_version=PARSER_VERSION, purpose=purpose)


def enrich(record: dict[str, Any], client: RegistrySourceClient, project_root: Path) -> tuple[dict[str, Any], list[SourceRecord], list[dict[str, str]]]:
    name = record.get("primary_name", record.get("generic_name", ""))
    result, provenance, warnings = dict(record), [], []
    for provider, extractor, field, purpose in (
        ("rxnorm", extract_rxcui, "rxcui", "canonicalization"),
        ("pubchem", extract_pubchem_cid, "pubchem_cid", "canonicalization"),
        ("dailymed", None, "", "route_formulation"),
    ):
        try:
            lookup = getattr(client, provider)(name)
            value = extractor(lookup) if extractor else ""
            provenance.append(source_record(lookup, purpose, project_root))
            if value:
                result[field] = value
        except Exception as exc:
            warnings.append({"entity": record.get("entity_a_id", record.get("entity_b_id", "")), "provider": provider, "message": str(exc)})
    source_status = {item.provider: item for item in provenance}
    result["canonical_name"] = name
    result["provenance"] = provenance
    result["curation_status"] = "source_enriched" if {"rxnorm", "pubchem"} <= set(source_status) else "source_partial"
    return result, provenance, warnings


def _write_csv(path: Path, records: list[dict[str, Any]], side: str) -> None:
    if side == "A":
        fields = ["topical_ophthalmic_medications_id", "primary_name", "canonical_name", "aliases", "category", "active_mechanisms", "flags", "route", "dosage_form", "ophthalmic_administration", "rxcui", "pubchem_cid", "components", "evidence_sources", "curation_status"]
    else:
        fields = ["entity_b_id", "generic_name", "canonical_name", "aliases", "drug_class", "flags", "metabolic_pathways", "transporter_substrates", "therapeutic_index_tier", "narrow_therapeutic_index", "route", "dosage_form", "rxcui", "pubchem_cid", "label_source", "curation_status"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in records:
            row = dict(item)
            if side == "A": row["topical_ophthalmic_medications_id"] = row["entity_a_id"]
            for key, value in row.items():
                if isinstance(value, list) and all(isinstance(element, str) for element in value):
                    row[key] = "|".join(value)
            writer.writerow({key: row.get(key, "") for key in fields})
        temporary = Path(handle.name)
    os.replace(temporary, path)


def build(project_root: Path, side: str, source_mode: str, cache_dir: Path, output_dir: Path) -> dict[str, Any]:
    candidate_path = project_root / "data" / "curation" / f"entity_{side.lower()}_candidates.yaml"
    candidate_data = yaml.safe_load(candidate_path.read_text(encoding="utf-8"))
    catalog = load_catalog(project_root / "configs" / "flag_catalog.yaml")
    client = RegistrySourceClient(cache_dir, source_mode)
    raw_records, models, provenance, warnings = [], [], [], []
    seen_names: set[str] = set()
    for candidate in candidate_data["entities"]:
        name = candidate.get("primary_name", candidate.get("generic_name"))
        if name.casefold() in seen_names:
            warnings.append({"entity": candidate.get("entity_a_id", candidate.get("entity_b_id", "")), "provider": "curation", "message": f"duplicate candidate name skipped: {name}"})
            continue
        seen_names.add(name.casefold())
        enriched, source_rows, source_warnings = enrich(candidate, client, project_root)
        enriched["flags"] = derived_flags(enriched, catalog)
        model = EntityA.model_validate(enriched) if side == "A" else EntityB.model_validate(enriched)
        models.append(model)
        raw_records.append(model.model_dump(mode="json"))
        provenance.extend(source_rows)
        warnings.extend(source_warnings)
    report = write_report(project_root / "outputs" / f"registry_reconciliation_report_entity_{side.lower()}.json", models if side == "A" else [], models if side == "B" else [], catalog)
    if report["status"] != "pass":
        raise ValueError(f"registry QA failed: {report['findings']}")
    destination = output_dir / ("entities_a.csv" if side == "A" else "entities_b.csv")
    _write_csv(destination, raw_records, side)
    manifest_path = project_root / "data" / "manifest" / f"source_manifest_entity_{side.lower()}.jsonl"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        for item in provenance:
            handle.write(json.dumps(item.model_dump(), ensure_ascii=False, sort_keys=True) + "\n")
    build_manifest = {"schema_version": 1, "generated_at": datetime.now(UTC).isoformat(), "source_mode": source_mode, "candidate_input": str(candidate_path.relative_to(project_root)), "candidate_sha256": sha256(candidate_path), "output": str(destination.relative_to(project_root)), "output_sha256": sha256(destination), "entity_count": len(models), "source_record_count": len(provenance), "warning_count": len(warnings), "warnings": warnings, "qa_status": report["status"]}
    build_path = project_root / "data" / "manifest" / f"build_manifest_entity_{side.lower()}.json"
    build_path.write_text(json.dumps(build_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return build_manifest

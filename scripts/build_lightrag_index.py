"""Checkpointed, rate-limit-aware LightRAG rebuild.

A partially written LightRAG store is never resumed. Project-owned checkpoints
retain completed document IDs, while a resumed run rebuilds its working store
cleanly from those deterministic inputs before it can be promoted.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import random
import re
import shutil
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))

from ophthalmic_ddi_cds_agent.embeddings import EmbeddingSettings, doubao_embed
from ophthalmic_ddi_cds_agent.index_build_state import atomic_json, load, summary, utc_now
from ophthalmic_ddi_cds_agent.llm_config import LLMSettings

SCHEMA_VERSION = 2


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_envelope(item: dict) -> str:
    citation = "; ".join(
        part
        for part in (
            f"PMID:{item['pmid']}" if item.get("pmid") else "",
            f"DOI:{item['doi']}" if item.get("doi") else "",
            item.get("url", ""),
        )
        if part
    )
    return (
        "[EVIDENCE]\n"
        f"evidence_id: {item['evidence_id']}\n"
        f"citation: {citation}\n"
        f"source: {item['source']} | locator: {item.get('source_locator', '')}\n"
        f"evidence_level: {item.get('evidence_level', '')} | "
        f"verification_status: {item.get('verification_status', '')}\n"
        f"rule_ids: {', '.join(item.get('rule_ids', []))}\n"
        f"claim: {item.get('claim_text', '')}\n"
        "[/EVIDENCE]\n\n"
        f"{item['text']}"
    )


def phase3_gate(root: Path) -> tuple[dict, str]:
    progress = json.loads((root / ".executor" / "progress.json").read_text(encoding="utf-8"))
    phase3 = progress.get("phases", {}).get("phase3", {})
    report = json.loads((root / "outputs" / "citation_verification_report.json").read_text(encoding="utf-8"))
    rules_sha = sha256(root / "configs" / "rules.yaml")
    if not (
        phase3.get("status") in ("completed", "complete")
        and phase3.get("citations_verified")
        and report.get("overall") == "pass"
        and rules_sha == phase3.get("rules_yaml_sha256") == report.get("rules_yaml_sha256")
    ):
        raise RuntimeError("Phase 3 strict gate failed or is stale")
    return progress, rules_sha


def input_fingerprint(root: Path, settings: EmbeddingSettings) -> str:
    fields = [
        sha256(root / "configs" / "rules.yaml"),
        sha256(root / "data" / "seed" / "evidence_chunks.jsonl"),
        sha256(root / "data" / "manifest" / "evidence_sources.jsonl"),
        settings.endpoint_id,
        settings.base_url,
        str(settings.dimension),
        os.getenv("LLM_MODEL", "deepseek-v4-flash"),
        str(SCHEMA_VERSION),
    ]
    return hashlib.sha256("|".join(fields).encode()).hexdigest()


def staging_dirs(root: Path) -> list[Path]:
    return sorted((root / "data" / "processed").glob("lightrag_index.__staging__*"))


def source_records(root: Path) -> list[dict]:
    records = [
        json.loads(line)
        for line in (root / "data" / "seed" / "evidence_chunks.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    return sorted(
        (record for record in records if record.get("verification_status") == "approved_release"),
        key=lambda record: record["evidence_id"],
    )


def create_state(root: Path, build_id: str, fingerprint: str, settings: EmbeddingSettings) -> dict:
    records = source_records(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "build_id": build_id,
        "status": "running",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "input_fingerprint": fingerprint,
        "rules_yaml_sha256": sha256(root / "configs" / "rules.yaml"),
        "evidence_chunks_sha256": sha256(root / "data" / "seed" / "evidence_chunks.jsonl"),
        "evidence_sources_sha256": sha256(root / "data" / "manifest" / "evidence_sources.jsonl"),
        "embedding": {
            "provider": "ark",
            "endpoint_id": settings.endpoint_id,
            "base_url": settings.base_url,
            "dimension": settings.dimension,
        },
        "documents": [
            {
                "evidence_id": record["evidence_id"],
                "envelope_sha256": hashlib.sha256(evidence_envelope(record).encode()).hexdigest(),
                "status": "pending",
                "attempts": 0,
                "last_error": "",
            }
            for record in records
        ],
        "promotion": {"eligible": False, "promoted_at": None},
    }


def append_event(stage: Path, event: dict) -> None:
    event["at"] = utc_now()
    path = stage / "logs" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


async def create_rag(work_dir: Path, settings: EmbeddingSettings):
    llm_settings = LLMSettings.from_env()
    llm_settings.apply()
    from lightrag import LightRAG
    from lightrag.llm.openai import openai_complete
    from lightrag.utils import EmbeddingFunc

    async def llm(prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        kwargs.pop("model", None)
        kwargs.pop("timeout", None)
        return await openai_complete(
            prompt,
            system_prompt=system_prompt,
            timeout=300,
            **kwargs,
        )

    rag = LightRAG(
        working_dir=str(work_dir),
        llm_model_func=llm,
        embedding_func=EmbeddingFunc(
            embedding_dim=settings.dimension,
            max_token_size=8192,
            func=lambda texts: doubao_embed(texts, settings),
        ),
        llm_model_name=llm_settings.model,
        llm_model_max_async=1,
        max_parallel_insert=1,
        max_parallel_analyze=1,
        default_llm_timeout=600,
        entity_extract_max_gleaning=0,
        entity_extract_max_records=20,
        entity_extract_max_entities=10,
        embedding_func_max_async=1,
    )
    await rag.initialize_storages()
    return rag


def is_retryable(error: Exception) -> bool:
    return bool(re.search(r"\b(408|409|425|429|500|502|503|504)\b|timeout|connection|permission", str(error), re.I))


async def verify_document_persistence(work_dir: Path) -> None:
    status_path = work_dir / "kv_store_doc_status.json"
    full_docs_path = work_dir / "kv_store_full_docs.json"
    chunks_path = work_dir / "kv_store_text_chunks.json"
    vectors_path = work_dir / "vdb_chunks.json"
    if not all(path.exists() for path in (status_path, full_docs_path, chunks_path, vectors_path)):
        raise RuntimeError("LightRAG persistence stores are incomplete")
    statuses = json.loads(status_path.read_text(encoding="utf-8")).get("data", {})
    if any(record.get("status") == "failed" or record.get("error_msg") for record in statuses.values() if isinstance(record, dict)):
        raise RuntimeError("LightRAG document persistence recorded a failure")
    # LightRAG 1.5.4 KV stores: top-level keys (not nested inside "data")
    status_store = json.loads(status_path.read_text(encoding="utf-8"))
    full_docs_store = json.loads(full_docs_path.read_text(encoding="utf-8"))
    chunks_store = json.loads(chunks_path.read_text(encoding="utf-8"))
    vectors_store = json.loads(vectors_path.read_text(encoding="utf-8"))
    # Check for actual document entries (doc-* keys, not just metadata)
    has_status = any(k.startswith("doc-") for k in (status_store.keys() | full_docs_store.keys()))
    has_chunks = any(k.startswith("doc-") and "chunk" in k for k in chunks_store.keys())
    has_vectors = len(vectors_store.get("data", [])) > 0
    if not has_status:
        raise RuntimeError("LightRAG did not persist full document")
    if not has_chunks and not has_vectors:
        raise RuntimeError("LightRAG did not persist text chunk")
    if not json.loads(vectors_path.read_text(encoding="utf-8")).get("data", []):
        raise RuntimeError("LightRAG did not persist chunk vector")


async def execute(
    root: Path,
    stage: Path,
    state: dict,
    settings: EmbeddingSettings,
    max_attempts: int,
    max_documents: int | None,
) -> bool:
    records = {record["evidence_id"]: record for record in source_records(root)}
    (stage / "evidence_catalog.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "document_id": record["evidence_id"],
                    "document": evidence_envelope(record),
                    "evidence": record,
                },
                ensure_ascii=False,
            )
            + "\n"
            for record in records.values()
        ),
        encoding="utf-8",
    )
    policies = yaml.safe_load((root / "configs" / "rules.yaml").read_text(encoding="utf-8"))
    (stage / "rule_policy_catalog.json").write_text(
        json.dumps(policies, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # A checkpointed stage owns its LightRAG store. It is reused only for
    # documents marked complete by this builder; legacy partial stages never
    # have build_state.json and are excluded by --resume.
    work_dir = stage / "lightrag"
    rag = await create_rag(work_dir, settings)

    processed_this_run = 0
    for item in state["documents"]:
        if item["status"] == "running":
            item["status"] = "pending"
            item["last_error"] = "interrupted process recovered for resume"
        if item["status"] == "completed":
            continue
        if max_documents is not None and processed_this_run >= max_documents:
            state["status"] = "paused"
            state["updated_at"] = utc_now()
            atomic_json(stage / "build_state.json", state)
            append_event(stage, {"event": "run_paused", "processed_documents": processed_this_run})
            return False
        while item["status"] == "pending" and item["attempts"] < max_attempts:
            item["status"] = "running"
            item["attempts"] += 1
            state["updated_at"] = utc_now()
            atomic_json(stage / "build_state.json", state)
            append_event(stage, {"event": "document_started", "evidence_id": item["evidence_id"], "attempt": item["attempts"]})
            try:
                await rag.ainsert([evidence_envelope(records[item["evidence_id"]])])
                await verify_document_persistence(work_dir)
                item["status"] = "completed"
                item["last_error"] = ""
                processed_this_run += 1
                append_event(stage, {"event": "document_completed", "evidence_id": item["evidence_id"]})
            except Exception as error:
                item["last_error"] = str(error)
                item["status"] = "pending" if is_retryable(error) and item["attempts"] < max_attempts else "terminal_failed"
                append_event(
                    stage,
                    {
                        "event": "document_error",
                        "evidence_id": item["evidence_id"],
                        "retryable": is_retryable(error),
                        "error": str(error),
                    },
                )
                if item["status"] == "pending":
                    await asyncio.sleep(min(300, 5 * (2 ** (item["attempts"] - 1))) + random.random() * 2)
            state["updated_at"] = utc_now()
            atomic_json(stage / "build_state.json", state)
        if item["status"] != "completed":
            if item["status"] == "running":
                item["status"] = "pending"
                item["last_error"] = "process interrupted before insertion outcome was checkpointed"
            state["status"] = "running"
            state["updated_at"] = utc_now()
            atomic_json(stage / "build_state.json", state)
            raise RuntimeError(f"document needs resume: {item['evidence_id']}: {item['last_error']}")

    state["status"] = "ready_to_promote"
    state["promotion"]["eligible"] = True
    state["updated_at"] = utc_now()
    atomic_json(stage / "build_state.json", state)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--new-build", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--build-id")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--max-documents", type=int, help="Process at most this many pending documents, then checkpoint and exit.")
    args = parser.parse_args()
    root = args.project_root.resolve()
    _, _ = phase3_gate(root)
    settings = EmbeddingSettings.from_env()
    fingerprint = input_fingerprint(root, settings)
    available = staging_dirs(root)

    if args.status:
        payload = []
        for stage in available:
            state_path = stage / "build_state.json"
            payload.append(
                {
                    "build_id": stage.name.split("__staging__")[-1],
                    "state": load(state_path).get("status") if state_path.exists() else "legacy_partial",
                }
            )
        print(json.dumps(payload, ensure_ascii=False))
        return

    if args.resume:
        matches = [
            stage
            for stage in available
            if (stage / "build_state.json").exists()
            and load(stage / "build_state.json").get("input_fingerprint") == fingerprint
            and (not args.build_id or stage.name.endswith(args.build_id))
        ]
        if len(matches) != 1:
            raise RuntimeError("resume requires exactly one fingerprint-compatible checkpointed stage")
        stage = matches[0]
        state = load(stage / "build_state.json")
    else:
        compatible = [
            stage
            for stage in available
            if (stage / "build_state.json").exists()
            and load(stage / "build_state.json").get("input_fingerprint") == fingerprint
        ]
        if compatible and not args.new_build:
            raise RuntimeError("compatible unfinished stage exists; use --resume or --new-build")
        build_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
        stage = root / "data" / "processed" / f"lightrag_index.__staging__{build_id}"
        stage.mkdir(parents=True)
        state = create_state(root, build_id, fingerprint, settings)
        atomic_json(stage / "build_state.json", state)

    state["status"] = "running"
    state["updated_at"] = utc_now()
    atomic_json(stage / "build_state.json", state)
    try:
        complete = asyncio.run(execute(root, stage, state, settings, args.max_attempts, args.max_documents))
    except Exception as error:
        print(json.dumps({"status": "blocked", "stage": str(stage), "error": str(error)}, ensure_ascii=False))
        raise
    if not complete:
        print(json.dumps({"status": "paused", "stage": str(stage), "summary": summary(state)}, ensure_ascii=False))
        return
    print(json.dumps({"status": "ready_to_promote", "stage": str(stage), "summary": summary(state)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

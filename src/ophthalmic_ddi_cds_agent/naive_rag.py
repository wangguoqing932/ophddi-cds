"""naive_rag — BM25 retrieval over the evidence corpus.

This is the retrieval component of the `naive_rag` baseline reported in the
manuscript. The implementation mirrors the constants used in the reported
evaluation; see `configs/prompts.yaml` for the prompt that consumes this context
and `scripts/run_multiseed_per_dataset.py` for the full evaluation harness.

Retrieval parameters (as reported): BM25Okapi with k1 = 1.5, b = 0.75, top-k = 3
passages, each truncated to 400 characters.
"""
from __future__ import annotations

import json
from pathlib import Path

from rank_bm25 import BM25Okapi

ROOT = Path(__file__).resolve().parents[2]

K1 = 1.5
B = 0.75
TOP_K = 3
PASSAGE_CHAR_CAP = 400
EMPTY_FALLBACK = "No evidence."


class NaiveRAG:
    """BM25 retrieval over the curated evidence chunks.

    The corpus is loaded once at construction. Query and corpus are both
    lowercased and whitespace-tokenised, matching the reported protocol.
    """

    def __init__(self, corpus_path: Path | None = None):
        path = corpus_path or (ROOT / "data" / "seed" / "evidence_chunks.jsonl")
        self.chunks: list[dict] = []
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    self.chunks.append(json.loads(line))
        self._texts = [c.get("text", c.get("content", "")) for c in self.chunks]
        tokenised = [t.lower().split() for t in self._texts]
        self._bm25 = BM25Okapi(tokenised, k1=K1, b=B)

    def __len__(self) -> int:
        return len(self.chunks)

    def retrieve(self, ophthalmic_drug: str, systemic_drug: str, k: int = TOP_K) -> list[dict]:
        """Return the top-k evidence chunks for a drug pair."""
        query = f"{ophthalmic_drug} {systemic_drug} ophthalmic interaction"
        scores = self._bm25.get_scores(query.lower().split())
        top = scores.argsort()[-k:][::-1]
        out = []
        for i in top:
            out.append({
                "doc_id": self.chunks[i].get("doc_id", i),
                "score": float(scores[i]),
                "text": self._texts[i][:PASSAGE_CHAR_CAP],
            })
        return out

    def context(self, ophthalmic_drug: str, systemic_drug: str, k: int = TOP_K) -> str:
        """Format retrieved passages as the prompt context block."""
        hits = self.retrieve(ophthalmic_drug, systemic_drug, k)
        if not hits:
            return EMPTY_FALLBACK
        return "\n\n".join(f"[{h['doc_id']}] {h['text']}" for h in hits)

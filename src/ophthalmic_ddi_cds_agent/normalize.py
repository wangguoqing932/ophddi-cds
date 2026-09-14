"""Deterministic, route-aware medication name normalization."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

_SALT_TERMS = {"acetate", "besylate", "fumarate", "hydrochloride", "hydrobromide", "maleate", "mesylate", "phosphate", "sodium", "succinate", "sulfate", "tartrate"}


def normalized_key(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    value = re.sub(r"[,_+/()\-]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value


def active_moiety_key(value: str) -> str:
    tokens = [part for part in normalized_key(value).split() if part not in _SALT_TERMS]
    return " ".join(tokens)


@dataclass(frozen=True)
class NormalizationResult:
    canonical_name: str | None
    candidates: tuple[str, ...] = ()
    ambiguous: bool = False


def normalize_medication(query: str, records: Iterable[object], *, route: str | None = None) -> NormalizationResult:
    """Resolve a name only when its approved aliases yield one route-compatible record."""
    query_keys = {normalized_key(query), active_moiety_key(query)}
    matches: list[object] = []
    for record in records:
        record_route = getattr(record, "route", "")
        if route and record_route != route:
            continue
        names = [getattr(record, "canonical_name", ""), getattr(record, "primary_name", ""), getattr(record, "generic_name", ""), *getattr(record, "aliases", [])]
        if query_keys & {normalized_key(name) for name in names if name} or query_keys & {active_moiety_key(name) for name in names if name}:
            matches.append(record)
    canonical = tuple(sorted({
        (getattr(item, "canonical_name", "") or getattr(item, "primary_name", "") or getattr(item, "generic_name", ""), getattr(item, "route", ""))
        for item in matches
    }))
    names = tuple(item[0] for item in canonical)
    if len(canonical) == 1:
        return NormalizationResult(canonical_name=names[0], candidates=names)
    return NormalizationResult(canonical_name=None, candidates=names, ambiguous=bool(canonical))

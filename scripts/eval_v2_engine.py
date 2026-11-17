#!/usr/bin/env python3
"""eval_v2_engine.py — Evaluate the architecture-v2 cascade engine on:
1. Main consensus set (84) — regression vs v1
2. Blind set 1 (20) — regression vs v1 (was 0.500)
3. Blind set 2 (20, frozen SHA df2890f6) — one-shot generalization
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG

kg = PreciseKG()


def metrics(pairs):
    tp = sum(1 for p in pairs if p['gold'] == 'high' and p['pred'] == 'high')
    fp = sum(1 for p in pairs if p['gold'] != 'high' and p['pred'] == 'high')
    fn = sum(1 for p in pairs if p['gold'] == 'high' and p['pred'] != 'high')
    tn = sum(1 for p in pairs if p['gold'] != 'high' and p['pred'] != 'high')
    sens = tp / (tp + fn) if tp + fn else 0
    spec = tn / (tn + fp) if tn + fp else 0
    acc = sum(1 for p in pairs if p['gold'] == p['pred']) / len(pairs)
    return sens, spec, acc, tp, fn, fp


def run(name, cases, gold_key):
    print(f'=== {name} ===')
    pairs = []
    for c in cases:
        lvl, _, info = kg.deterministic_level_v2(c['ophthalmic_drug'], c['systemic_drug'])
        pairs.append({'case': c['case_id'], 'gold': c[gold_key], 'pred': lvl, 'path': info.get('path')})
    sens, spec, acc, tp, fn, fp = metrics(pairs)
    print(f'Sens={sens:.3f} ({tp}/{tp + fn})  Spec={spec:.3f}  Acc4={acc:.3f}')
    for p in pairs:
        mark = 'OK' if p['gold'] == p['pred'] else 'XX'
        print(f'  {mark} {p["case"]}: gold={p["gold"]} pred={p["pred"]} [{p["path"]}]')
    print()
    return pairs


golds = [json.loads(l) for l in
         (ROOT / 'data' / 'datasets' / 'consensus_validation' / 'cases.jsonl').open(encoding='utf-8')]
blind1 = json.load((ROOT / 'outputs' / 'blind_test' / 'blind_set_v2.json').open(encoding='utf-8'))
blind2 = json.load((ROOT / 'outputs' / 'blind_test' / 'blind_set_v3.json').open(encoding='utf-8'))

run('1. MAIN SET REGRESSION (84) — v2 engine (v1 was 0.988 Acc4, 1 error)', golds, 'gold_risk_level')
run('2. BLIND SET 1 REGRESSION (20) — v2 engine (v1 was 0.500)', blind1, 'proposed_gold')
run('3. BLIND SET 2 ONE-SHOT (20, frozen SHA df2890f6) — v2 engine', blind2, 'proposed_gold')

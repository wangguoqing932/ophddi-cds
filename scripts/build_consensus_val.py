"""build_consensus_val.py — Multi-source consensus gold"""

import csv, json, yaml
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

# Load all
a_rows = {}
with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        a_rows[row["topical_ophthalmic_medications_id"]] = row
b_rows = {}
with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        b_rows[row["entity_b_id"]] = row
with open(ROOT / "configs" / "rules.yaml") as f:
    rules = yaml.safe_load(f)["rules"]

sev = {"high":3,"medium":2,"low":1}
def rule_level(aid, bid):
    af = set(a_rows[aid]["flags"].split("|"))
    bf = set(b_rows[bid]["flags"].split("|"))
    best = "low"; bv = 1
    matched = []
    for r in rules:
        a_f = set(r.get("entity_a_flags",[]))
        b_f = set(r.get("entity_b_flags",[]))
        if r.get("match") == "all":
            a_ok = a_f <= af if a_f else True
            b_ok = b_f <= bf if b_f else True
        else:
            a_ok = bool(a_f & af)
            b_ok = bool(b_f & bf)
        if a_ok and b_ok:
            sv = sev[r["severity"]]
            if sv > bv: best = r["severity"]; bv = sv
            matched.append(r["id"])
    return best, matched

seen = set()
cases = []
def add(cid, aid, bid, level, source, method, **extra):
    if (aid,bid) in seen: return
    seen.add((aid,bid))
    cases.append({
        "case_id": cid,
        "entity_a_id": aid, "entity_b_id": bid,
        "ophthalmic_drug": a_rows[aid]["primary_name"],
        "systemic_drug": b_rows[bid]["generic_name"],
        "ophthalmic_class": a_rows[aid]["category"],
        "systemic_class": b_rows[bid]["drug_class"],
        "gold_risk_level": level,
        "gold_source": source,
        "ground_truth_method": method,
        "patient_factors": [],
        "provenance": {"source": source, "method": method, **extra},
    })

# ═══ SOURCE 1: Expert (always trusted) ═══
with open(ROOT / "data" / "gold_mechanisms.json") as f:
    gold = json.load(f)
for g in gold:
    aid = next((eid for eid,r in a_rows.items() if r["primary_name"].lower()==g["ophthalmic"].lower()), None)
    bid = next((eid for eid,r in b_rows.items() if r["generic_name"].lower()==g["systemic"].lower()), None)
    if aid and bid:
        add(g["case_id"], aid, bid, g["ddinter_level"], "expert",
            "expert_adjudication", mechanisms=g.get("true_mechanisms",[]),
            evidence=g.get("evidence_source",""))
print(f"1. Expert: {len(cases)}")

# ═══ SOURCE 2: FDA label co-occurrence in same chunk ═══
chunks = []
with open(ROOT / "data" / "seed" / "evidence_chunks.jsonl") as f:
    for l in f:
        if l.strip(): chunks.append(json.loads(l))
fda_chunks = [c for c in chunks if c.get("evidence_level")=="A" and c.get("verification_status")=="approved_release"]
n2 = 0
for fc in fda_chunks:
    text = (fc.get("text","")+" "+fc.get("claim_text","")).lower()
    a_in = [aid for aid,ar in a_rows.items() if len(ar["primary_name"])>3 and ar["primary_name"].lower() in text]
    b_in = [bid for bid,br in b_rows.items() if len(br["generic_name"])>3 and br["generic_name"].lower() in text]
    for aid in a_in[:3]:
        for bid in b_in[:3]:
            rl, _ = rule_level(aid, bid)
            add(f"FDA-{n2:03d}", aid, bid, rl, "fda_label",
                "label_guideline", pmid=fc.get("pmid",""))
            n2 += 1
print(f"2. FDA label: +{n2} = {len(cases)}")

# ═══ SOURCE 3: DDInter ∩ Rule consensus ═══
dev = [json.loads(l) for l in open(ROOT/"data/datasets/dev-ddinter/cases.jsonl") if l.strip()]
intp = [json.loads(l) for l in open(ROOT/"data/datasets/int-pubmed/cases.jsonl") if l.strip()]
n3_agree = 0; n3_conflict = 0
for c in dev + intp:
    aid, bid = c.get("entity_a_id",""), c.get("entity_b_id","")
    ddi_level = c.get("gold_risk_level","?")
    rl, matched = rule_level(aid, bid)
    
    if ddi_level == rl:
        # Consensus!
        add(f"CONS-{c['case_id']}", aid, bid, ddi_level,
            f"DDInter={ddi_level} ∩ Rules={rl}", "consensus",
            ddi_level=ddi_level, rule_level=rl, matched_rules=matched)
        n3_agree += 1
    else:
        n3_conflict += 1
print(f"3. Consensus (DDInter ∩ Rules): +{n3_agree} agree, {n3_conflict} conflict excluded = {len(cases)}")

# ═══ SOURCE 4: Negative controls (both agree = low) ═══
n4 = 0
for aid, ar in a_rows.items():
    af = set(ar["flags"].split("|"))
    if "systemic_absorption_low" not in af: continue
    for bid, br in b_rows.items():
        bf = set(br["flags"].split("|"))
        if any(
            (set(r.get("entity_a_flags",[])) <= af if r.get("match")=="all" else bool(set(r.get("entity_a_flags",[])) & af))
            and (set(r.get("entity_b_flags",[])) <= bf if r.get("match")=="all" else bool(set(r.get("entity_b_flags",[])) & bf))
            for r in rules
        ):
            continue
        add(f"NEG-{n4:03d}", aid, bid, "low", "negative_control",
            "expert_adjudication")
        n4 += 1
        if n4 >= 25: break
    if n4 >= 25: break
print(f"4. Negative controls: +{n4} = {len(cases)}")

# ═══ Final stats ═══
dist = Counter(c["gold_risk_level"] for c in cases)
srcs = Counter(c["gold_source"] for c in cases)
print(f"\n{'='*55}")
print(f"  CONSENSUS GOLD: {len(cases)} cases")
print(f"  H={dist.get('high',0)} M={dist.get('medium',0)} L={dist.get('low',0)}")
print(f"  Sources: {dict(srcs)}")
print(f"  Excluded conflicts: {n3_conflict}")
print(f"{'='*55}")

# Save
out = ROOT / "data" / "datasets" / "consensus_validation"
out.mkdir(parents=True, exist_ok=True)
with open(out / "cases.jsonl", "w") as f:
    for c in cases: f.write(json.dumps(c, ensure_ascii=False)+"\n")
with open(out / "dataset.meta.json", "w") as f:
    json.dump({"dataset_id":"consensus_validation","n_cases":len(cases),
               "distribution":dict(dist),"sources":dict(srcs),
               "method":"Multi-source consensus: DDInter ∩ Rules, + Expert + FDA",
               "conflicts_excluded":n3_conflict}, f, indent=2)
print(f"\nSaved: {out}/cases.jsonl")

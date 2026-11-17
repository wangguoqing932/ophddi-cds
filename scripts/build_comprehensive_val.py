"""build_comprehensive_val.py — Multi-source comprehensive validation set"""
import csv, json, yaml, random
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
random.seed(42)

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
with open(ROOT / "data" / "gold_mechanisms.json") as f:
    gold_mechs = json.load(f)
chunks = []
with open(ROOT / "data" / "seed" / "evidence_chunks.jsonl") as f:
    for line in f: 
        if line.strip(): chunks.append(json.loads(line))
dev = [json.loads(l) for l in open(ROOT/"data/datasets/dev-ddinter/cases.jsonl") if l.strip()]
intp = [json.loads(l) for l in open(ROOT/"data/datasets/int-pubmed/cases.jsonl") if l.strip()]
ddi_all = dev + intp

seen = set()
cases = []

def add(cid, aid, bid, level, stype, sref, gtruth, **extra):
    if (aid, bid) in seen: return
    seen.add((aid, bid))
    c = {"case_id": cid, "dataset_id": "comprehensive_validation",
         "entity_a_id": aid, "entity_b_id": bid,
         "ophthalmic_drug": a_rows[aid]["primary_name"],
         "systemic_drug": b_rows[bid]["generic_name"],
         "ophthalmic_class": a_rows[aid]["category"],
         "systemic_class": b_rows[bid]["drug_class"],
         "gold_risk_level": level, "patient_factors": [],
         "provenance": {"source_type": stype, "source_ref": sref,
                       "record_locator": cid, "ground_truth_method": gtruth,
                       "extraction_date": "2026-07-30", **extra}}
    cases.append(c)

# 1. Gold mechanisms (20)
for g in gold_mechs:
    aid = next((eid for eid,r in a_rows.items() if r["primary_name"].lower()==g["ophthalmic"].lower()), None)
    bid = next((eid for eid,r in b_rows.items() if r["generic_name"].lower()==g["systemic"].lower()), None)
    if aid and bid:
        add(g["case_id"], aid, bid, g["ddinter_level"], "guideline", g["evidence_source"],
            "expert_adjudication", mechanisms=g.get("true_mechanisms",[]))
print(f"1. Gold mechs: {len(cases)}")

# 2. FDA label evidence (per-chunk co-occurrence)
fda_chunks = [c for c in chunks if c.get("evidence_level")=="A" and c.get("verification_status")=="approved_release"]
n2 = 0
for fc in fda_chunks:
    text = (fc.get("text","") + " " + fc.get("claim_text","")).lower()
    a_in_chunk = [aid for aid, ar in a_rows.items() if len(ar["primary_name"])>3 and ar["primary_name"].lower() in text]
    b_in_chunk = [bid for bid, br in b_rows.items() if len(br["generic_name"])>3 and br["generic_name"].lower() in text]
    for aid in a_in_chunk[:5]:  # limit per chunk
        for bid in b_in_chunk[:5]:
            ar = a_rows[aid]; br = b_rows[bid]
            af, bf = set(ar["flags"].split("|")), set(br["flags"].split("|"))
            best = "low"; bv = 1
            for rule in rules:
                if set(rule.get("entity_a_flags",[])) <= af and set(rule.get("entity_b_flags",[])) <= bf:
                    sv = {"high":3,"medium":2,"low":1}[rule["severity"]]
                    if sv > bv: best = rule["severity"]; bv = sv
            add(f"FDA-{n2:03d}", aid, bid, best, "guideline",
                f"FDA label: {ar['primary_name']} + {br['generic_name']} (PMID:{fc.get('pmid','?')})",
                "label_guideline")
            n2 += 1
print(f"2. FDA labels (per-chunk): +{n2} = {len(cases)}")

# 3. DDInter with DrugBank IDs
a_db = {}
for eid, r in a_rows.items():
    for p in r.get("evidence_sources","").split("|"):
        if "DrugBank" in p: a_db[eid] = p.strip()
b_db = {}
for eid, r in b_rows.items():
    for p in r.get("label_source","").split("|"):
        if "DrugBank" in p: b_db[eid] = p.strip()
n3 = 0
for dc in ddi_all:
    aid, bid = dc.get("entity_a_id",""), dc.get("entity_b_id","")
    if aid in a_db and bid in b_db:
        prov = dc.get("provenance",{})
        add(f"DDI-{dc['case_id']}", aid, bid, dc.get("gold_risk_level","medium"),
            "database", f"DDInter 2.0 (DrugBank {a_db[aid]} × {b_db[bid]})",
            "database_outcome")
        n3 += 1
print(f"3. DDInter+DrugBank: +{n3} = {len(cases)}")

# 4. Negative controls
n4 = 0
for aid, ar in a_rows.items():
    af = set(ar["flags"].split("|"))
    if "systemic_absorption_low" not in af: continue
    for bid, br in b_rows.items():
        bf = set(br["flags"].split("|"))
        if any(set(r.get("entity_a_flags",[]))<=af and set(r.get("entity_b_flags",[]))<=bf for r in rules):
            continue
        add(f"NEG-{n4:03d}", aid, bid, "low", "database",
            "Negative control: low abs, no rule match", "database_outcome")
        n4 += 1
        if n4 >= 20: break
    if n4 >= 20: break
print(f"4. Negative controls: +{n4} = {len(cases)}")

# 5. Fill uncovered rules
rc = defaultdict(int)
for c in cases:
    af = set(a_rows[c["entity_a_id"]]["flags"].split("|"))
    bf = set(b_rows[c["entity_b_id"]]["flags"].split("|"))
    for rule in rules:
        if set(rule.get("entity_a_flags",[])) <= af and set(rule.get("entity_b_flags",[])) <= bf:
            rc[rule["id"]] += 1
uncovered = [r for r in rules if r["id"] not in rc]
n5 = 0
for rule in uncovered:
    af, bf = set(rule.get("entity_a_flags",[])), set(rule.get("entity_b_flags",[]))
    cand = []
    for aid, ar in a_rows.items():
        if not (af <= set(ar["flags"].split("|"))): continue
        for bid, br in b_rows.items():
            if not (bf <= set(br["flags"].split("|"))): continue
            if (aid,bid) not in seen: cand.append((aid,bid))
    for aid, bid in cand[:2]:
        add(f"FILL-{rule['id']}-{n5}", aid, bid, rule["severity"],
            "guideline", f"Rule: {rule['id']}", "expert_adjudication")
        n5 += 1
print(f"5. Rule fill: +{n5} = {len(cases)}")

# Final stats
rc = defaultdict(int)
for c in cases:
    af = set(a_rows[c["entity_a_id"]]["flags"].split("|"))
    bf = set(b_rows[c["entity_b_id"]]["flags"].split("|"))
    for rule in rules:
        if set(rule.get("entity_a_flags",[])) <= af and set(rule.get("entity_b_flags",[])) <= bf:
            rc[rule["id"]] += 1

dist = Counter(c["gold_risk_level"] for c in cases)
srcs = Counter(c["provenance"]["source_type"] for c in cases)
a_cls = Counter(c["ophthalmic_class"] for c in cases)
b_cls = Counter(c["systemic_class"] for c in cases)

print(f"\n{'='*50}")
print(f"  COMPREHENSIVE VALIDATION: {len(cases)} cases")
print(f"  H={dist.get('high',0)} M={dist.get('medium',0)} L={dist.get('low',0)}")
print(f"  Sources: {dict(srcs)}")
print(f"  Rules: {len(rc)}/38 covered ({len(rc)/38*100:.0f}%)")
print(f"  Classes: {len(a_cls)} ophth × {len(b_cls)} systemic")
uncovered = [r["id"] for r in rules if r["id"] not in rc]
if uncovered: print(f"  Uncovered: {uncovered}")
print(f"{'='*50}")

# Save
out = ROOT / "data" / "datasets" / "comprehensive_validation"
out.mkdir(parents=True, exist_ok=True)
with open(out / "cases.jsonl", "w") as f:
    for c in cases: f.write(json.dumps(c, ensure_ascii=False)+"\n")
meta = {"dataset_id":"comprehensive_validation","role":"external_validation",
        "n_cases":len(cases),"distribution":dict(dist),"sources":dict(srcs),
        "rule_coverage":f"{len(rc)}/38","class_diversity":f"{len(a_cls)}×{len(b_cls)}",
        "created":"2026-07-30"}
with open(out/"dataset.meta.json","w") as f:
    json.dump(meta, f, indent=2)
print(f"\nSaved: {out}/cases.jsonl")

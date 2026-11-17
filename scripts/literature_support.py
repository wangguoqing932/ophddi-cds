"""literature_support.py — Compute Literature Support Index for system predictions"""
import csv, json, re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]

# ═══ Load ═══
with open(ROOT / "output" / "pubmed_evidence_types.json", encoding="utf-8") as f:
    pubmed_data = json.load(f)

a_rows = {}
with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        a_rows[row["topical_ophthalmic_medications_id"]] = row
b_rows = {}
with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        b_rows[row["entity_b_id"]] = row

# Load system predictions from ablation results
predictions = []
with open(ROOT / "output" / "ablation_classify.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            predictions.append(json.loads(line))

# ═══ Build literature index ═══
# For each drug pair, count how many PubMed articles mention BOTH drugs
pair_lit_count = defaultdict(int)
pair_article_details = defaultdict(list)

for art in pubmed_data["articles"]:
    text = (art.get("title","") + " " + art.get("abstract","")).lower()
    if len(text) < 50: continue
    
    # Find all mentioned drugs from our registries
    a_mentioned = set()
    for a_id, a_row in a_rows.items():
        name = a_row["primary_name"].lower()
        if len(name) > 4 and name in text:
            a_mentioned.add(a_id)
    b_mentioned = set()
    for b_id, b_row in b_rows.items():
        name = b_row["generic_name"].lower()
        if len(name) > 4 and name in text:
            b_mentioned.add(b_id)
    
    # Count co-mentions as "literature support"
    for a_id in a_mentioned:
        for b_id in b_mentioned:
            key = f"{a_id}|{b_id}"
            pair_lit_count[key] += 1
            pair_article_details[key].append({
                "pmid": art["pmid"],
                "title": art["title"][:120],
                "pubdate": art.get("pubdate",""),
                "pubtypes": art.get("pubtypes",[]),
            })

# ═══ Compute Literature Support Index by prediction level ═══
fs_preds = [p for p in predictions if p["method"] == "full_system"]

# Map entity IDs for predictions
# We need to match ophthalmic_drug name → entity_a_id
a_name_to_id = {}
for a_id, a_row in a_rows.items():
    a_name_to_id[a_row["primary_name"].lower()] = a_id
b_name_to_id = {}
for b_id, b_row in b_rows.items():
    b_name_to_id[b_row["generic_name"].lower()] = b_id

by_pred_level = defaultdict(list)
for p in fs_preds:
    a_id = a_name_to_id.get(p["ophthalmic"].lower(), "")
    b_id = b_name_to_id.get(p["systemic"].lower(), "")
    key = f"{a_id}|{b_id}"
    lit_count = pair_lit_count.get(key, 0)
    by_pred_level[p["predicted"]].append({
        "case_id": p["case_id"],
        "pair": f"{p['ophthalmic']} × {p['systemic']}",
        "gold": p["gold"],
        "pred": p["predicted"],
        "lit_count": lit_count,
        "articles": pair_article_details.get(key, [])[:3],
    })

# ═══ Report ═══
print("=" * 70)
print("  LITERATURE SUPPORT INDEX (LSI)")
print("=" * 70)
print("  PubMed articles (PK/clinical/review): 166")
print()

for level in ["high", "medium", "low"]:
    cases = by_pred_level[level]
    if not cases: continue
    avg_lit = sum(c["lit_count"] for c in cases) / len(cases)
    min_lit = min(c["lit_count"] for c in cases)
    max_lit = max(c["lit_count"] for c in cases)
    zero_lit = sum(1 for c in cases if c["lit_count"] == 0)
    
    print(f"  System predicts = {level.upper()} (n={len(cases)}):")
    print(f"    Mean PubMed mentions: {avg_lit:.1f}")
    print(f"    Range: {min_lit} – {max_lit}")
    print(f"    Zero literature: {zero_lit}/{len(cases)} ({zero_lit/len(cases)*100:.0f}%)")
    
    # Show top-3 most-supported pairs
    top = sorted(cases, key=lambda x: x["lit_count"], reverse=True)[:3]
    print(f"    Top-3 supported pairs:")
    for c in top:
        print(f"      {c['pair']}: {c['lit_count']} PubMed mentions")
        for a in c["articles"][:2]:
            print(f"        PMID:{a['pmid']} ({a['pubdate']}) {a['title'][:90]}")
    print()

# ═══ Gradient check ═══
high_avg = sum(c["lit_count"] for c in by_pred_level["high"]) / max(len(by_pred_level["high"]), 1)
med_avg = sum(c["lit_count"] for c in by_pred_level["medium"]) / max(len(by_pred_level["medium"]), 1)
low_avg = sum(c["lit_count"] for c in by_pred_level["low"]) / max(len(by_pred_level["low"]), 1)

print(f"  LSI Gradient: HIGH={high_avg:.1f} > MEDIUM={med_avg:.1f} > LOW={low_avg:.1f}")
print(f"  Gradient holds: {'✅' if high_avg > med_avg > low_avg else '❌'}")

# ═══ Compare with gold ═══
print(f"\n  Literature support by GOLD level:")
for level in ["high", "medium", "low"]:
    cases = [c for c in by_pred_level["high"] + by_pred_level["medium"] + by_pred_level["low"] if c["gold"] == level]
    if not cases: continue
    avg = sum(c["lit_count"] for c in cases) / len(cases)
    print(f"    Gold={level}: mean {avg:.1f} PubMed mentions (n={len(cases)})")

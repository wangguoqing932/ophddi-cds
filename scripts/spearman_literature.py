"""spearman_literature.py — Spearman correlation: system risk vs PubMed literature volume"""
import csv, json, time, urllib.request, urllib.parse
from pathlib import Path
from collections import defaultdict
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# ═══ Sample drug pairs from internal_validation ═══
a_rows = {}
with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        a_rows[row["topical_ophthalmic_medications_id"]] = row
b_rows = {}
with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        b_rows[row["entity_b_id"]] = row

# Load validation cases
cases = []
with open(ROOT / "data" / "datasets" / "consensus_validation" / "cases.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            cases.append(json.loads(line))

# Load system predictions
predictions = []
with open(ROOT / "output" / "ablation_classify.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            predictions.append(json.loads(line))

# Build prediction map
pred_map = {}
for p in predictions:
    if p["method"] == "full_system":
        key = (p["ophthalmic"].lower(), p["systemic"].lower())
        pred_map[key] = p["predicted"]

# ═══ PubMed search for each pair ═══
risk_levels = {"high": 3, "medium": 2, "low": 1, "unparseable": 0}
pairs_data = []
count = 0

# Take all unique pairs from internal validation
seen = set()
for c in cases:
    oph = (c.get("ophthalmic_drug") or c.get("ophthalmic", "")).lower()
    sys_d = (c.get("systemic_drug") or c.get("systemic", "")).lower()
    key = (oph, sys_d)
    if key in seen: continue
    seen.add(key)
    
    # Get system prediction
    pred = pred_map.get(key, "unknown")
    pred_val = risk_levels.get(pred, 0)
    
    # PubMed search: count articles mentioning both drugs
    query = f'("{oph}"[tiab] AND "{sys_d}"[tiab])'
    try:
        params = {"db": "pubmed", "term": query, "retmax": 1, "retmode": "json"}
        url = f"{BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url) as r:
            data = json.loads(r.read())
        pubmed_count = int(data["esearchresult"]["count"])
        time.sleep(0.25)
    except Exception as e:
        pubmed_count = 0
        print(f"  ERROR: {oph} x {sys_d} - {e}")
    
    pairs_data.append({
        "ophthalmic": oph,
        "systemic": sys_d,
        "system_risk": pred,
        "system_risk_val": pred_val,
        "pubmed_count": pubmed_count,
    })
    count += 1
    if count % 15 == 0:
        print(f"  {count}/{len(cases)} pairs queried...")

# ═══ Compute Spearman ═══
import numpy as np
try:
    from scipy.stats import spearmanr
    has_scipy = True
except ImportError:
    has_scipy = False

if has_scipy:
    risk_vals = [p["system_risk_val"] for p in pairs_data if p["system_risk_val"] > 0]
    lit_vals = [p["pubmed_count"] for p in pairs_data if p["system_risk_val"] > 0]
    
    rho, pval = spearmanr(risk_vals, lit_vals)
    
    print(f"\n{'='*60}")
    print(f"  SPEARMAN CORRELATION")
    print(f"{'='*60}")
    print(f"  N = {len(risk_vals)} drug pairs")
    print(f"  ρ = {rho:.4f}")
    print(f"  p = {pval:.4f}")
    print(f"  Significant (p<0.05): {'✅' if pval < 0.05 else '❌'}")
    
    # By risk level
    for level, val in [("high", 3), ("medium", 2), ("low", 1)]:
        subset = [p for p in pairs_data if p["system_risk_val"] == val]
        if subset:
            avg_lit = sum(p["pubmed_count"] for p in subset) / len(subset)
            print(f"  System={level}: mean {avg_lit:.1f} PubMed mentions (n={len(subset)})")
else:
    # Manual Spearman
    risk_vals = np.array([p["system_risk_val"] for p in pairs_data if p["system_risk_val"] > 0])
    lit_vals = np.array([p["pubmed_count"] for p in pairs_data if p["system_risk_val"] > 0])
    
    # Rank
    from scipy.stats import rankdata
    r_risk = rankdata(risk_vals)
    r_lit = rankdata(lit_vals)
    n = len(risk_vals)
    rho = 1 - 6 * np.sum((r_risk - r_lit)**2) / (n * (n**2 - 1))
    
    print(f"\n{'='*60}")
    print(f"  SPEARMAN CORRELATION (manual)")
    print(f"{'='*60}")
    print(f"  N = {n} drug pairs")
    print(f"  ρ = {rho:.4f}")
    print(f"  Positive correlation: {'✅' if rho > 0 else '❌'}")

# Save
out = ROOT / "output" / "spearman_results.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump({"n_pairs": len(pairs_data), "rho": float(rho), "p_value": float(pval) if has_scipy else None,
               "data": pairs_data}, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {out}")

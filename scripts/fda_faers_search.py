"""fda_faers_search.py — Query OpenFDA for ophthalmic drug adverse event reports"""
import json, time, urllib.request, urllib.parse
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://api.fda.gov/drug/event.json"

def faers_search(query, limit=100):
    """Search FDA FAERS adverse event database via OpenFDA API."""
    params = {"search": query, "limit": limit}
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

# ═══ Known ophthalmic drugs with systemic effects ═══
OPHTHALMIC_DRUGS = [
    "timolol", "brimonidine", "dorzolamide", "brinzolamide",
    "latanoprost", "travoprost", "bimatoprost",
    "phenylephrine", "atropine", "cyclopentolate", "tropicamide",
    "ketorolac", "bromfenac", "nepafenac", "diclofenac",
    "dexamethasone", "prednisolone", "fluorometholone", "loteprednol",
    "ciprofloxacin", "moxifloxacin", "ofloxacin", "tobramycin", "erythromycin",
    "cyclosporine", "tacrolimus",
]

print("Querying FDA FAERS (OpenFDA API)...")
print(f"Testing {len(OPHTHALMIC_DRUGS)} ophthalmic drugs\n")

results = {}
for drug in OPHTHALMIC_DRUGS:
    try:
        # Search for adverse events where this drug is mentioned
        query = f'patient.drug.medicinalproduct:"{drug}"'
        data = faers_search(query, limit=5)
        time.sleep(0.5)
        
        if "error" in data:
            results[drug] = {"status": "error", "error": data["error"]}
            print(f"  {drug}: API error - {data['error'][:80]}")
        else:
            meta = data.get("meta", {}).get("results", {})
            total = meta.get("total", 0)
            results[drug] = {"status": "ok", "total_reports": total}
            print(f"  {drug}: {total} FAERS reports")
    except Exception as e:
        results[drug] = {"status": "error", "error": str(e)[:80]}
        print(f"  {drug}: Exception - {str(e)[:80]}")

# ═══ For drugs with reports, search for specific adverse events ═══
print("\n\nDetailed AE searches for drugs with >0 reports:")
ae_terms = {
    "timolol": ["bradycardia", "syncope", "bronchospasm", "hypotension"],
    "brimonidine": ["coma", "apnea", "bradycardia", "hypotension", "CNS depression"],
    "phenylephrine": ["hypertension", "pulmonary edema", "tachycardia"],
    "atropine": ["delirium", "tachycardia", "fever", "hallucination"],
    "dorzolamide": ["metabolic acidosis", "hypokalemia", "aplastic anemia"],
    "brinzolamide": ["metabolic acidosis", "hypokalemia"],
}

for drug, aes in ae_terms.items():
    for ae in aes:
        try:
            query = f'patient.drug.medicinalproduct:"{drug}" AND patient.reaction.reactionmeddrapt:"{ae.upper()}"'
            data = faers_search(query, limit=1)
            time.sleep(0.35)
            if "error" not in data:
                total = data.get("meta", {}).get("results", {}).get("total", 0)
                if total > 0:
                    print(f"  {drug} + {ae}: {total} reports ✅")
        except:
            pass

# ═══ Save summary ═══
out = ROOT / "output" / "faers_summary.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump({"search_date": "2026-07-31", "drugs_searched": len(OPHTHALMIC_DRUGS),
               "results": {k: v for k, v in results.items() if v.get("status") == "ok"}},
              f, indent=2, ensure_ascii=False)
print(f"\nSaved: {out}")

#!/usr/bin/env python3
"""Batch verify all PMIDs in evidence_chunks.jsonl via PubMed E-utilities."""
import json, time, requests
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ZCodeProject\ophthalmic-ddi-cds")
EVIDENCE = ROOT / "data" / "seed" / "evidence_chunks.jsonl"
OUTPUT = ROOT / "outputs" / "pmid_verification_report.json"

chunks = [json.loads(line) for line in EVIDENCE.read_text(encoding="utf-8").splitlines() if line.strip()]

# Find all unique PMIDs
pmid_chunks = [(c["evidence_id"], c["pmid"], c.get("title", "")) for c in chunks if c.get("pmid")]
unique_pmids = list(set(p[1] for p in pmid_chunks))
print(f"Total PMIDs to verify: {len(unique_pmids)}")

verified = {}
failed = []
mismatched = []

for i, pmid in enumerate(unique_pmids):
    try:
        resp = requests.get(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={"db": "pubmed", "id": pmid, "rettype": "xml", "retmode": "xml"},
            timeout=30
        )
        if resp.status_code != 200:
            failed.append({"pmid": pmid, "error": f"HTTP {resp.status_code}"})
            continue
        
        # Extract title from XML
        import re
        title_match = re.search(r'<ArticleTitle>(.*?)</ArticleTitle>', resp.text)
        pubmed_title = title_match.group(1) if title_match else "(no title)"
        
        # Find chunks with this PMID
        chunk_titles = [(cid, title) for cid, pid, title in pmid_chunks if pid == pmid]
        
        verified[pmid] = {
            "pubmed_title": pubmed_title,
            "chunks": [{"evidence_id": cid, "chunk_title": t[:100]} for cid, t in chunk_titles],
            "status": "verified"
        }
        
        if i % 20 == 0:
            print(f"  {i}/{len(unique_pmids)} verified...")
        
        time.sleep(0.34)  # Respect NCBI rate limit: 3 req/s
        
    except Exception as e:
        failed.append({"pmid": pmid, "error": str(e)})

# Report
report = {
    "generated": datetime.now().isoformat(),
    "total_pmids": len(unique_pmids),
    "verified": len(verified),
    "failed": len(failed),
    "mismatched_titles": len(mismatched),
    "details": {
        "verified_sample": list(verified.values())[:5],
        "failed": failed,
    }
}

OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nDone: {len(verified)} verified, {len(failed)} failed")
print(f"Report: {OUTPUT}")

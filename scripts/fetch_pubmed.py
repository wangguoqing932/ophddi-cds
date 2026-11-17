"""Fetch and cache PubMed XML from the versioned evidence query manifest."""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from ophthalmic_ddi_cds_agent.evidence_sources import EvidenceSourceClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--source-mode", choices=("online", "cache-only"), default="online")
    parser.add_argument("--max-results", type=int, default=35)
    parser.add_argument("--email", default="registry@example.invalid")
    args = parser.parse_args(); root = args.project_root.resolve()
    config = yaml.safe_load((root / "data/curation/evidence_queries.yaml").read_text(encoding="utf-8"))
    client = EvidenceSourceClient(root, args.source_mode, email=args.email)
    index = []
    for item in config["pubmed_queries"]:
        response, search_source = client.pubmed_search(item["query"], item.get("max_results", args.max_results))
        pmids = response["esearchresult"].get("idlist", [])
        if pmids:
            _, fetch_source = client.pubmed_fetch(pmids)
            index.append({**item, "pmids": pmids, "search_source": search_source.as_dict(), "fetch_source": fetch_source.as_dict()})
        else:
            index.append({**item, "pmids": [], "search_source": search_source.as_dict()})
        print(f"{item['id']}: {len(pmids)} PubMed records")
        if args.source_mode == "online": time.sleep(0.4)
    output = root / "data/manifest/pubmed_query_index.json"
    output.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__": main()

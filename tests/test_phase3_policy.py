import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_policy_gate_replays_cached_sources() -> None:
    result = subprocess.run([sys.executable, 'scripts/verify_rule_citations.py', '--project-root', '.'], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((ROOT / 'outputs/citation_verification_report.json').read_text(encoding='utf-8'))
    assert report['overall'] == 'pass'
    assert report['policy_count'] == 43
    assert report['policy_errors'] == []
    assert all(item['status'] == 'verified' for item in report['items'])

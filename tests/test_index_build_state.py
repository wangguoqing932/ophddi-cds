import json
from pathlib import Path

from ophthalmic_ddi_cds_agent.index_build_state import atomic_json, load, summary


def test_atomic_checkpoint_round_trip(tmp_path: Path) -> None:
    path = tmp_path / 'build_state.json'
    state = {'status': 'running', 'documents': [{'status': 'pending'}, {'status': 'completed'}]}
    atomic_json(path, state)
    assert load(path) == state
    assert summary(state) == {'pending': 1, 'running': 0, 'completed': 1, 'terminal_failed': 0}


def test_checkpoint_overwrite_is_valid_json(tmp_path: Path) -> None:
    path = tmp_path / 'build_state.json'
    atomic_json(path, {'status': 'running', 'documents': []})
    atomic_json(path, {'status': 'blocked', 'documents': []})
    assert json.loads(path.read_text(encoding='utf-8'))['status'] == 'blocked'

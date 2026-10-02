from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_INDEX = REPO_ROOT / "skills_UIUX/knowledge/index.json"
EV_CANONICAL_REF = "records/ev-charging-ocpp-transaction-semantics.json"
HISTORICAL_PRE_EV_PROMOTION_TESTS = {
    "test_knowledge_usefulness_a50.py",
    "test_knowledge_expansion_proposal_a50.py",
    "test_knowledge_ready_candidate_drafts_a50.py",
    "test_knowledge_candidate_acceptance_trial_a50.py",
    "test_knowledge_edtech_revision_trial_a50.py",
    "test_knowledge_ev_controlled_index_trial_a50.py",
    "test_knowledge_edtech_controlled_index_trial_a50.py",
    "test_knowledge_ev_canonical_promotion_proposal_a50.py",
    "test_knowledge_ev_canonical_promotion_shadow_a50.py",
}


def _ev_is_canonical() -> bool:
    payload = json.loads(KNOWLEDGE_INDEX.read_text(encoding="utf-8"))
    return EV_CANONICAL_REF in payload.get("records", [])


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if not _ev_is_canonical():
        return
    marker = pytest.mark.skip(
        reason="historical pre-EV-promotion A50 evidence; frozen after A50.10C canonical apply"
    )
    for item in items:
        if Path(str(item.path)).name in HISTORICAL_PRE_EV_PROMOTION_TESTS:
            item.add_marker(marker)

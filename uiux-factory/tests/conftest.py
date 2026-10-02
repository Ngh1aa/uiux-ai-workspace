from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_INDEX = REPO_ROOT / "skills_UIUX/knowledge/index.json"
EV_CANONICAL_REF = "records/ev-charging-ocpp-transaction-semantics.json"
EDTECH_CANONICAL_REF = "records/edtech-lti-context-roles-services-v2.json"
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
HISTORICAL_PRE_EDTECH_PROMOTION_TESTS = {
    "test_knowledge_ev_canonical_apply_a50.py",
    "test_knowledge_edtech_canonical_promotion_proposal_a50.py",
    "test_knowledge_edtech_canonical_promotion_shadow_a50.py",
}


def _canonical_refs() -> set[str]:
    payload = json.loads(KNOWLEDGE_INDEX.read_text(encoding="utf-8"))
    return {str(ref) for ref in payload.get("records", [])}


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    refs = _canonical_refs()
    ev_is_canonical = EV_CANONICAL_REF in refs
    edtech_is_canonical = EDTECH_CANONICAL_REF in refs
    ev_marker = pytest.mark.skip(
        reason="historical pre-EV-promotion A50 evidence; frozen after A50.10C canonical apply"
    )
    edtech_marker = pytest.mark.skip(
        reason="historical pre-EdTech-promotion A50 evidence; frozen after A50.13 canonical apply"
    )
    for item in items:
        name = Path(str(item.path)).name
        if ev_is_canonical and name in HISTORICAL_PRE_EV_PROMOTION_TESTS:
            item.add_marker(ev_marker)
        if edtech_is_canonical and name in HISTORICAL_PRE_EDTECH_PROMOTION_TESTS:
            item.add_marker(edtech_marker)

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from core.benchmarks.lifecycle_parity_regression import evaluate_lifecycle_parity_corpus
from core.runtime.lifecycle_projection import (
    PHASES,
    project_factory_lifecycle,
    project_managed_lifecycle,
)


ROOT = Path(__file__).resolve().parents[1]


def test_a49_factory_projection_is_read_only_and_never_infers_release_from_completion() -> None:
    payload = {
        "status": "completed",
        "active_stage": None,
        "completed_stages": ["research", "design_system", "implementation", "visual_qa"],
        "artifacts": {"flow_plan": "/tmp/flow.json"},
    }
    before = deepcopy(payload)

    projection = project_factory_lifecycle(payload)

    assert payload == before
    assert [item.phase for item in projection.phases] == list(PHASES)
    assert projection.phase("RESEARCH").status == "completed"
    assert projection.phase("DESIGN").status == "completed"
    assert projection.phase("IMPLEMENT").status == "completed"
    assert projection.phase("QA").status == "completed"
    assert projection.phase("FINALIZE").status == "completed"
    assert projection.phase("RELEASE").status == "unavailable"
    assert projection.release_effect == "none"


def test_a49_managed_projection_never_infers_finalize_or_release_from_completed_state() -> None:
    payload = {
        "state": "COMPLETED",
        "active_stage": "qa",
        "completed_stages": ["research", "design", "implementation", "qa"],
        "replan_count": 0,
        "flow": {
            "stages": [
                {"id": "research", "agent": "research"},
                {"id": "design", "agent": "development"},
                {"id": "implementation", "agent": "implementation"},
                {"id": "qa", "agent": "qa"},
            ]
        },
    }

    projection = project_managed_lifecycle(payload)

    assert projection.phase("RESEARCH").status == "completed"
    assert projection.phase("DESIGN").status == "completed"
    assert projection.phase("IMPLEMENT").status == "completed"
    assert projection.phase("QA").status == "active"
    assert projection.phase("FINALIZE").status == "unknown"
    assert projection.phase("RELEASE").status == "unknown"
    assert projection.evidence_effect == "none"
    assert projection.release_effect == "none"


def test_a49_managed_projection_fails_safe_on_unknown_stage_role() -> None:
    payload = {
        "state": "RUNNING",
        "active_stage": "mystery",
        "completed_stages": [],
        "flow": {"stages": [{"id": "mystery", "agent": "custom"}]},
    }

    projection = project_managed_lifecycle(payload)

    assert projection.unmapped_native_stages == ("mystery",)
    assert all(
        projection.phase(phase).status != "active"
        for phase in ("RESEARCH", "DESIGN", "IMPLEMENT", "QA")
    )


def test_a49_replanned_managed_state_projects_replan_without_mutation() -> None:
    payload = {
        "state": "REPLANNED",
        "active_stage": "design",
        "completed_stages": ["research"],
        "replan_count": 1,
        "flow": {
            "stages": [
                {"id": "research", "agent": "research"},
                {"id": "design", "agent": "development"},
            ]
        },
    }
    before = deepcopy(payload)

    projection = project_managed_lifecycle(payload)

    assert payload == before
    assert projection.phase("REPLAN").status == "active"
    assert projection.phase("DESIGN").status == "active"


def test_a49_lifecycle_parity_corpus_passes_and_is_explicitly_not_execution_evidence() -> None:
    report = evaluate_lifecycle_parity_corpus(ROOT / "benchmarks/lifecycle-parity-v1.json")

    assert report.total >= 6
    assert report.passed == report.total
    assert report.scope == "projection_parity_not_execution_or_release_evidence"

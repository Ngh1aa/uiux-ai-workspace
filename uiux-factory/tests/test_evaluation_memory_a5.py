from __future__ import annotations

import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from core.evaluation.run_evaluator import RunEvaluation, RunEvaluator
from core.memory.evaluation_memory import EvaluationMemoryError, EvaluationMemoryStore
from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.evidence import EvidenceRecord
from core.runtime.flow_os.managed import ManagedFlowController


FACTORY = Path(__file__).resolve().parents[1]
SKILLS = FACTORY.parent / "skills_UIUX"


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir(parents=True)
    _git(root, "init")
    _git(root, "config", "user.email", "a5-memory@example.test")
    _git(root, "config", "user.name", "A5 Memory Test")
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root.resolve()


def _evidence(stage_id: str, status: str = "PASS", name: str = "validate-runtime") -> dict:
    return EvidenceRecord(
        id=f"{stage_id}-{status}-{name}",
        type="validator_result",
        stage_id=stage_id,
        tool="run_validator",
        status=status,
        summary=f"{name}: {status}",
        data={"name": name, "returncode": 0 if status == "PASS" else 1},
    ).to_dict()


def _memory_record(run_id: str, outcome: str = "passed", channel: str = "") -> RunEvaluation:
    suffix = sum(ord(char) for char in run_id) % 60
    return RunEvaluation(
        schema_version=1,
        run_id=run_id,
        flow_id="micro-ui-change",
        flow_revision=0,
        managed_state="COMPLETED" if outcome == "passed" else "FAILED",
        outcome=outcome,
        evaluated_at=f"2026-09-28T00:00:{suffix:02d}+00:00",
        signature={"change_surface": "MICRO"},
        effective_evidence_count=1,
        evidence_type_counts={"validator_result": 1},
        passing_evidence_types=["validator_result"] if outcome == "passed" else [],
        failing_channels=[channel] if channel else [],
        memory_eligible=True,
    )


def _complete_with_evidence(
    manager: ManagedFlowController,
    managed,
    *,
    repaired_first_stage: bool = False,
    secret_marker: str = "",
) -> None:
    for index, resolved in enumerate(list(managed.flow.stages)):
        stage_state = manager.start_stage(managed)
        records = list(stage_state.context.get("evidence_records", []))
        if repaired_first_stage and index == 0:
            records.append(_evidence(resolved.id, "FAIL"))
            records.append(_evidence(resolved.id, "PASS"))
        else:
            records.append(_evidence(resolved.id, "PASS"))
        stage_state.context["evidence_records"] = records
        if secret_marker:
            stage_state.context["provider_summary"] = f"untrusted provider prose {secret_marker}"
            stage_state.context["provider_evidence_claims"] = [
                {
                    "id": "claim-secret",
                    "type": "provider_claim",
                    "stage_id": resolved.id,
                    "tool": "provider",
                    "status": "CLAIMED",
                    "summary": secret_marker,
                    "data": {},
                    "origin": "provider",
                    "trusted": False,
                }
            ]
        stage_state.state = "COMPLETED"
        manager.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
        manager.complete_stage(managed)


def test_a5_terminal_run_is_evaluated_and_repaired_failure_is_superseded(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Fix button spacing on the current website",
        authority="branch_write",
        overrides={"change_surface": "MICRO"},
    )

    _complete_with_evidence(manager, managed, repaired_first_stage=True)

    checkpoint = harness.resume(managed.manager_run_id)
    evaluation = RunEvaluation.from_dict(checkpoint.context["run_evaluation"])
    assert managed.state == "COMPLETED"
    assert evaluation.outcome == "passed"
    assert evaluation.memory_eligible is True
    assert evaluation.failing_channels == []
    assert evaluation.effective_evidence_count == len(managed.flow.stages)
    assert checkpoint.context["evaluation_memory_recorded"] is True


def test_a5_terminal_failure_checkpoint_is_evaluated_and_learned(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Fix one broken button",
        authority="branch_write",
        overrides={"change_surface": "MICRO"},
    )
    stage_state = manager.start_stage(managed)
    stage_state.context["evidence_records"] = [_evidence(managed.active_stage, "FAIL")]
    stage_state.state = "FAILED"
    harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
    managed.state = "FAILED"
    manager._checkpoint_managed(managed)

    checkpoint = harness.resume(managed.manager_run_id)
    evaluation = RunEvaluation.from_dict(checkpoint.context["run_evaluation"])
    assert evaluation.outcome == "failed"
    assert evaluation.memory_eligible is True
    assert evaluation.failing_channels
    assert manager.evaluation_memory.load()[-1].run_id == managed.manager_run_id


def test_a5_memory_excludes_provider_prose_and_reuses_only_aggregate_insight(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)
    secret = "TOP_SECRET_PROVIDER_MARKER_92374"
    first = manager.start_from_goal(
        "Improve the current SaaS landing page button spacing",
        authority="branch_write",
        overrides={"change_surface": "MICRO", "business_domain": "saas"},
    )
    first_flow = first.flow.id
    _complete_with_evidence(manager, first, secret_marker=secret)

    memory_path = project / ".uiux-agent-runs" / "memory" / "evaluation-memory.json"
    raw = memory_path.read_text(encoding="utf-8")
    assert secret not in raw
    assert "provider_summary" not in raw
    assert "provider_claim" not in raw

    second = manager.start_from_goal(
        "Improve the current SaaS landing page button spacing",
        authority="branch_write",
        overrides={"change_surface": "MICRO", "business_domain": "saas"},
    )
    insight = second.task_context.get("prior_evaluation_insight")
    assert second.flow.id == first_flow
    assert second.authority == "branch_write"
    assert isinstance(insight, dict)
    assert insight["advisory_only"] is True
    assert insight["sample_size"] == 1
    assert insight["pass_rate"] == 1.0
    assert insight["authority_effect"] == "none"
    assert insight["gate_effect"] == "none"
    assert secret not in json.dumps(insight)


def test_a5_memory_is_bounded_and_deduplicates_run_ids(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    policy = {
        "evaluation_memory": {
            "enabled": True,
            "max_records": 2,
            "max_recall_records": 2,
            "min_signature_matches": 1,
        }
    }
    store = EvaluationMemoryStore(project, policy)

    assert store.record(_memory_record("run1", "failed", "qa:validator_result:run_validator:validate-runtime"))
    assert store.record(_memory_record("run2", "passed"))
    assert store.record(_memory_record("run3", "passed"))
    assert [row.run_id for row in store.load()] == ["run2", "run3"]

    updated = _memory_record("run3", "failed", "qa:browser_render:playwright:/")
    assert store.record(updated)
    loaded = store.load()
    assert [row.run_id for row in loaded] == ["run2", "run3"]
    assert loaded[-1].outcome == "failed"

    insight = store.insight(flow_id="micro-ui-change", signature={"change_surface": "MICRO"})
    assert insight is not None
    assert insight["sample_size"] == 2
    assert insight["failed_or_blocked_runs"] == 1
    assert insight["recurrent_failure_channels"][0]["channel"] == "qa:browser_render:playwright:/"


def test_a5_memory_serializes_concurrent_writers_without_lost_updates(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    policy = {
        "evaluation_memory": {
            "enabled": True,
            "max_records": 10,
            "max_recall_records": 10,
            "min_signature_matches": 1,
            "lock_timeout_seconds": 5,
            "lock_stale_seconds": 30,
        }
    }
    store = EvaluationMemoryStore(project, policy)
    records = [_memory_record(f"parallel-{index}") for index in range(6)]

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(store.record, records))

    assert results == [True] * 6
    assert {row.run_id for row in store.load()} == {row.run_id for row in records}


def test_a5_memory_refuses_symlinked_storage_path(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    runs = project / ".uiux-agent-runs"
    runs.mkdir()
    os.symlink(outside, runs / "memory", target_is_directory=True)
    store = EvaluationMemoryStore(project, {"evaluation_memory": {"enabled": True}})

    with pytest.raises(EvaluationMemoryError, match="symlink"):
        store.load()


def test_a5_nonterminal_or_evidenceless_evaluation_is_not_learned(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Fix one button",
        authority="branch_write",
        overrides={"change_surface": "MICRO"},
    )
    evaluation = RunEvaluator().evaluate(managed, harness)
    assert evaluation.outcome == "incomplete"
    assert evaluation.memory_eligible is False
    assert manager.evaluation_memory.record(evaluation) is False

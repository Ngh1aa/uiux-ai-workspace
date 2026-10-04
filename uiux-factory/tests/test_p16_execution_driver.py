from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.execution_driver import (
    ArtifactRegistry,
    CommandRunnerAdapter,
    ExecutionDriver,
    JsonCheckpointStore,
    RunnerResult,
    RunnerContractError,
)
from core.runtime.flow_os.flow import AmbiguousRoutingError


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS = WORKSPACE / "skills_UIUX"
FIXTURE_RUNNER = Path(__file__).resolve().parent / "fixtures" / "p16_segment_runner.py"
GOAL = "Audit the landing page, redesign checkout, implement it, and QA it."


def _build_driver(tmp_path: Path, *, fail_qa_once: bool = False, goal: str = GOAL, max_repair_attempts: int = 2):
    factory = ProfessionalWebsiteFlow(SKILLS)
    target = tmp_path / "target"
    target.mkdir()
    exchange = tmp_path / "exchange"
    runner = CommandRunnerAdapter(
        [sys.executable, str(FIXTURE_RUNNER)],
        work_dir=WORKSPACE,
        exchange_dir=exchange,
        extra_env={
            "P16_WORKSPACE": str(target),
            "P16_FAIL_QA_ONCE": "1" if fail_qa_once else "0",
        },
    )
    profile, driver = factory.resolve_execution_driver(
        goal,
        runner,
        workspace_root=target,
        checkpoint_path=tmp_path / "checkpoint.json",
        max_repair_attempts=max_repair_attempts,
    )
    return factory, profile, driver, runner, target, exchange


def _request_docs(exchange: Path) -> list[dict[str, object]]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(exchange.glob("*-request.json"))
    ]


def test_p16_real_subprocess_runner_drives_plan_to_completion(tmp_path: Path) -> None:
    _factory, profile, driver, runner, _target, _exchange = _build_driver(tmp_path)
    assert profile.routing_status == "resolved"
    assert driver.run_until_blocked() == "completed"
    assert runner.invocations == 4
    assert [node.status for node in driver.execution_plan.nodes] == ["passed"] * 4
    assert all(record.accepted_for_handoff for record in driver.registry.records.values())


def test_p16_request_routes_exact_active_stage_agent_skills_and_gates(tmp_path: Path) -> None:
    _factory, _profile, driver, _runner, _target, exchange = _build_driver(tmp_path)
    event = driver.run_next()
    request = _request_docs(exchange)[0]
    resolved = driver.work_plan.segments[0]
    stage = next(stage for stage in resolved.flow.stages if stage.id in resolved.active_stage_ids)

    assert event is not None and event["status"] == "passed"
    assert request["segment_id"] == resolved.id
    assert request["active_stage_id"] == stage.id
    assert request["agent"] == stage.agent
    assert request["skills"] == stage.skills
    assert request["mandatory_skills"] == stage.mandatory_skills
    assert request["gates"] == stage.gates
    assert request["expected_output_kinds"] == ["audit-findings"]


def test_p16_artifact_handoff_is_injected_into_next_runner_request(tmp_path: Path) -> None:
    _factory, _profile, driver, _runner, _target, exchange = _build_driver(tmp_path)
    driver.run_next()
    driver.run_next()
    requests = _request_docs(exchange)
    design_request = requests[1]
    assert len(design_request["input_artifacts"]) == 1
    assert design_request["input_artifacts"][0]["kind"] == "audit-findings"
    assert design_request["input_artifacts"][0]["digest"].startswith("sha256:")


def test_p16_registry_covers_file_report_screenshot_commit_and_evidence(tmp_path: Path) -> None:
    goal = "Audit the landing page, redesign checkout, implement it, and QA it; keep animation unchanged."
    _factory, _profile, driver, _runner, _target, _exchange = _build_driver(tmp_path, goal=goal)
    assert driver.run_until_blocked() == "completed"
    classes = {record.artifact_class for record in driver.registry.records.values()}
    assert {"file", "report", "screenshot", "commit", "evidence"}.issubset(classes)
    local = [record for record in driver.registry.records.values() if record.uri.startswith("file://")]
    assert local and all(record.digest and record.digest.startswith("sha256:") for record in local)


def test_p16_checkpoint_resume_continues_from_first_unfinished_segment(tmp_path: Path) -> None:
    _factory, _profile, driver, _runner, target, exchange = _build_driver(tmp_path)
    driver.run_next()
    driver.run_next()
    checkpoint = JsonCheckpointStore(tmp_path / "checkpoint.json")
    resumed_runner = CommandRunnerAdapter(
        [sys.executable, str(FIXTURE_RUNNER)],
        work_dir=WORKSPACE,
        exchange_dir=exchange,
        extra_env={"P16_WORKSPACE": str(target), "P16_FAIL_QA_ONCE": "0"},
    )
    resumed = ExecutionDriver.resume(
        driver.work_plan,
        resumed_runner,
        workspace_root=target,
        checkpoint_store=checkpoint,
    )
    assert [node.status for node in resumed.execution_plan.nodes[:2]] == ["passed", "passed"]
    assert resumed.execution_plan.runnable_segment_ids() == ["work-3"]
    assert resumed.run_until_blocked() == "completed"
    assert resumed_runner.invocations == 2


def test_p16_qa_failure_auto_routes_to_nearest_implementation_repair_owner(tmp_path: Path) -> None:
    _factory, _profile, driver, runner, _target, exchange = _build_driver(tmp_path, fail_qa_once=True)
    assert driver.run_until_blocked(max_steps=10) == "completed"
    assert runner.invocations == 6
    nodes = {node.segment_id: node for node in driver.execution_plan.nodes}
    assert nodes["work-1"].attempts == 1
    assert nodes["work-2"].attempts == 1
    assert nodes["work-3"].attempts == 2
    assert nodes["work-4"].attempts == 2

    failure = next(event for event in driver.history if event.get("failure_class") == "PRODUCT_QA_FAILED")
    assert failure["repair_owner_segment_id"] == "work-3"
    assert failure["superseded_artifact_ids"]
    repair = next(event for event in driver.history if event["segment_id"] == "work-3" and event["runner_mode"] == "repair")
    assert repair["status"] == "passed"
    requests = _request_docs(exchange)
    repair_request = next(item for item in requests if item["segment_id"] == "work-3" and item["runner_mode"] == "repair")
    assert repair_request["repair_of_segment_id"] == "work-4"
    assert repair_request["repair_failure_artifact_ids"]
    assert "web-ui-code-review" in repair_request["required_capabilities"]

    implementation_records = [
        record for record in driver.registry.records.values() if record.producer_segment_id == "work-3"
    ]
    assert len(implementation_records) == 2
    superseded = [record for record in implementation_records if record.metadata.get("superseded") == "true"]
    active = [record for record in implementation_records if record.accepted_for_handoff]
    assert len(superseded) == 1
    assert superseded[0].accepted_for_handoff is False
    assert len(active) == 1
    assert active[0].metadata.get("mode") == "repair"


def test_p16_failed_qa_evidence_is_retained_but_never_promoted_to_handoff(tmp_path: Path) -> None:
    _factory, _profile, driver, _runner, _target, _exchange = _build_driver(tmp_path, fail_qa_once=True)
    assert driver.run_until_blocked(max_steps=10) == "completed"
    failed = [record for record in driver.registry.records.values() if record.kind == "qa-failure-evidence"]
    assert len(failed) == 1
    assert failed[0].accepted_for_handoff is False
    assert failed[0].artifact_class == "report"
    assert failed[0].metadata.get("superseded") is None


def test_p16_runner_pass_without_expected_outputs_fails_gate_and_keeps_downstream_locked(tmp_path: Path) -> None:
    factory = ProfessionalWebsiteFlow(SKILLS)
    _profile, work_plan = factory.resolve_work_plan(GOAL)
    execution = factory.resolve_execution_plan(GOAL)[1]
    target = tmp_path / "target"
    target.mkdir()

    class EmptyPassRunner:
        def run(self, _request):
            return RunnerResult(schema_version="1.0", status="passed", artifacts=[])

    driver = ExecutionDriver(work_plan, execution, EmptyPassRunner(), ArtifactRegistry(target))
    event = driver.run_next()
    assert event is not None
    assert event["status"] == "failed"
    assert event["failure_class"] == "RUNNER_OUTPUT_GATE_FAILED"
    assert driver.execution_plan._node("work-1").status == "failed"
    assert driver.execution_plan._node("work-2").status == "blocked"


def test_p16_resume_rejects_checkpoint_for_different_resolved_plan(tmp_path: Path) -> None:
    factory, _profile, driver, _runner, target, _exchange = _build_driver(tmp_path)
    driver.run_next()
    _profile2, different_plan = factory.resolve_work_plan(
        "Audit the homepage, redesign the whole product, implement it, and QA it."
    )
    with pytest.raises(RunnerContractError, match="fingerprint"):
        ExecutionDriver.resume(
            different_plan,
            driver.runner,
            workspace_root=target,
            checkpoint_store=JsonCheckpointStore(tmp_path / "checkpoint.json"),
        )


def test_p16_factory_entrypoint_preserves_p13_ambiguity_fail_closed(tmp_path: Path) -> None:
    factory = ProfessionalWebsiteFlow(SKILLS)
    target = tmp_path / "target"
    target.mkdir()
    runner = CommandRunnerAdapter(
        [sys.executable, str(FIXTURE_RUNNER)],
        work_dir=WORKSPACE,
        exchange_dir=tmp_path / "exchange",
        extra_env={"P16_WORKSPACE": str(target)},
    )
    goal = "Audit an AI workspace for fintech treasury, redesign its dashboard, implement it, and QA it."
    with pytest.raises(AmbiguousRoutingError):
        factory.resolve_execution_driver(goal, runner, workspace_root=target)


def test_p16_checkpoint_contains_history_registry_and_execution_state(tmp_path: Path) -> None:
    _factory, _profile, driver, _runner, _target, _exchange = _build_driver(tmp_path)
    driver.run_next()
    payload = json.loads((tmp_path / "checkpoint.json").read_text(encoding="utf-8"))
    assert payload["plan_fingerprint"].startswith("sha256:")
    assert payload["history"][0]["segment_id"] == "work-1"
    assert payload["execution_plan"]["nodes"][0]["status"] == "passed"
    assert payload["artifact_registry"]["artifacts"][0]["accepted_for_handoff"] is True


def _b12_pending_repair_checkpoint(tmp_path: Path):
    _factory, _profile, driver, runner, target, _exchange = _build_driver(
        tmp_path, fail_qa_once=True, max_repair_attempts=1,
    )
    for _ in range(4):
        driver.run_next()
    checkpoint = JsonCheckpointStore(tmp_path / "checkpoint.json")
    payload = checkpoint.load()
    assert payload["repair_counts"] == {"work-3": 1}
    assert payload["repair_context"]["work-3"]["qa_segment_id"] == "work-4"
    assert len(payload["history"]) == 4
    return driver, runner, target, checkpoint, payload


@pytest.mark.parametrize("interrupt_at", [1, 2])
def test_b12_resume_preserves_checkpoint_when_writes_are_interrupted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, interrupt_at: int,
) -> None:
    driver, runner, target, checkpoint, payload = _b12_pending_repair_checkpoint(tmp_path)
    before = checkpoint.path.read_bytes()
    save = checkpoint.save
    writes = []

    def interrupted_save(value):
        writes.append(value)
        if len(writes) == interrupt_at:
            raise OSError("B12 interrupted checkpoint save")
        save(value)

    monkeypatch.setattr(checkpoint, "save", interrupted_save)
    try:
        resumed = ExecutionDriver.resume(
            driver.work_plan, runner, workspace_root=target,
            checkpoint_store=checkpoint, max_repair_attempts=1,
        )
    finally:
        assert checkpoint.path.read_bytes() == before
    assert writes == []
    assert resumed.checkpoint_payload() == payload
    assert resumed.checkpoint_store is checkpoint
    assert runner.invocations == 4


@pytest.mark.parametrize(("field", "invalid"), [
    ("repair_counts", {"work-3": "invalid-count"}),
    ("repair_context", {"work-3": None}),
    ("history", [None]),
    ("execution_plan", {"nodes": [None]}),
    ("artifact_registry", {"artifacts": [None]}),
    ("plan_fingerprint", "sha256:different"),
])
def test_b12_invalid_resume_payload_never_overwrites_checkpoint(
    tmp_path: Path, field: str, invalid,
) -> None:
    driver, runner, target, checkpoint, payload = _b12_pending_repair_checkpoint(tmp_path)
    checkpoint.save({**payload, field: invalid})
    before = checkpoint.path.read_bytes()
    with pytest.raises((RunnerContractError, TypeError, ValueError, KeyError)):
        ExecutionDriver.resume(
            driver.work_plan, runner, workspace_root=target, checkpoint_store=checkpoint,
        )
    assert checkpoint.path.read_bytes() == before
    assert runner.invocations == 4


def test_b12_resume_keeps_repair_budget_and_passed_stages(tmp_path: Path) -> None:
    driver, runner, target, checkpoint, payload = _b12_pending_repair_checkpoint(tmp_path)
    resumed = ExecutionDriver.resume(
        driver.work_plan, runner, workspace_root=target,
        checkpoint_store=checkpoint, max_repair_attempts=1,
    )
    assert resumed.checkpoint_payload() == payload
    assert resumed.execution_plan.runnable_segment_ids() == ["work-3"]
    repair = resumed.run_next()
    assert repair["runner_mode"] == "repair"
    assert repair["status"] == "passed"
    # A second independent QA failure must not receive a fresh repair budget.
    (target / ".qa-failed-once").unlink()
    failure = resumed.run_next()
    assert failure["failure_class"] == "PRODUCT_QA_FAILED"
    assert "repair_attempt" not in failure
    assert resumed.repair_counts == {"work-3": 1}
    assert resumed.execution_plan.runnable_segment_ids() == []
    assert [node.attempts for node in resumed.execution_plan.nodes] == [1, 1, 2, 2]
    assert [node.status for node in resumed.execution_plan.nodes] == ["passed", "passed", "passed", "failed"]
    assert resumed.history[:4] == payload["history"]
    assert runner.invocations == 6
    assert checkpoint.load() == resumed.checkpoint_payload()


def test_b12_atomic_checkpoint_preserves_old_file_at_every_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    checkpoint = JsonCheckpointStore(tmp_path / "checkpoint.json")
    old = {"repair_counts": {"work-3": 1}, "history": [{"status": "failed"}]}
    new = {**old, "history": [*old["history"], {"status": "passed", "reason": "Phục hồi đầy đủ"}]}
    checkpoint.save(old)
    before = checkpoint.path.read_bytes()
    encoder = json.JSONEncoder(ensure_ascii=False, indent=2, sort_keys=True)
    write_boundaries = len(list(encoder.iterencode(new))) + 1
    create_temp = tempfile.NamedTemporaryFile

    for interrupt_at in range(1, write_boundaries + 1):
        calls = []

        class InterruptedFile:
            def __init__(self, handle):
                self.handle = handle

            def __enter__(self):
                self.handle.__enter__()
                return self

            def __exit__(self, *args):
                return self.handle.__exit__(*args)

            @property
            def name(self):
                return self.handle.name

            def write(self, text):
                calls.append(text)
                if len(calls) == interrupt_at:
                    self.handle.write(text[:max(1, len(text) // 2)])
                    raise OSError("B12 interrupted partial write")
                return self.handle.write(text)

        with monkeypatch.context() as fault:
            fault.setattr(tempfile, "NamedTemporaryFile", lambda *args, **kwargs: InterruptedFile(create_temp(*args, **kwargs)))
            with pytest.raises(OSError, match="interrupted partial write"):
                checkpoint.save(new)
        assert len(calls) == interrupt_at
        assert checkpoint.path.read_bytes() == before
        assert checkpoint.load() == old


@pytest.mark.parametrize("boundary", ["temp-create", "replace"])
def test_b12_atomic_checkpoint_keeps_old_file_when_commit_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, boundary: str,
) -> None:
    checkpoint = JsonCheckpointStore(tmp_path / "checkpoint.json")
    checkpoint.save({"repair_counts": {"work-3": 1}, "history": [{"status": "failed"}]})
    before = checkpoint.path.read_bytes()

    def interrupted(*_args, **_kwargs):
        raise OSError("B12 interrupted atomic commit")

    with monkeypatch.context() as fault:
        if boundary == "temp-create":
            fault.setattr(tempfile, "NamedTemporaryFile", interrupted)
        else:
            fault.setattr(Path, "replace", interrupted)
        with pytest.raises(OSError, match="interrupted atomic commit"):
            checkpoint.save({"repair_counts": {}, "history": []})
    assert checkpoint.path.read_bytes() == before

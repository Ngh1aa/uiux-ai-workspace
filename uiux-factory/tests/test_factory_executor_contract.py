"""Executor 2.0 regressions; subprocesses use only the existing temporary fixture."""
from dataclasses import replace

import pytest

from core.runtime.flow_os.execution_driver import ExecutionGrant, ExecutionDriver, JsonCheckpointStore, RunnerContractError, RunnerResult
from test_p16_execution_driver import GOAL, _build_driver


def test_read_only_goal_blocks_host_runner_before_dispatch(tmp_path):
    _, profile, driver, runner, target, _ = _build_driver(tmp_path, goal=GOAL + " Read-only.")
    assert profile.authority == "read_only"
    event = driver.run_next()
    assert event["status"] == "failed", "read_only must fail before a mutating host runner executes"
    assert runner.invocations == 0
    assert list(target.iterdir()) == []


def test_dispatch_request_has_explicit_caller_control_contract(tmp_path):
    _, _, driver, _, _, _ = _build_driver(tmp_path)
    request = driver._request("work-2").to_dict()
    assert request["schema_version"] == "2.0"
    assert request["authority"] == "branch_write"
    assert request["approval_status"] == "UNREVIEWED"
    assert request["plan_fingerprint"] == driver.plan_fingerprint


@pytest.mark.parametrize("version", ["1.0", "", None])
def test_result_contract_rejects_missing_or_legacy_version(version):
    with pytest.raises(RunnerContractError, match="version"):
        RunnerResult.from_dict({"schema_version": version, "status": "passed", "artifacts": []})


def test_direct_command_adapter_rejects_legacy_request_before_writing_exchange(tmp_path):
    _, _, driver, runner, _, exchange = _build_driver(tmp_path)
    request = replace(driver._request("work-1"), schema_version="1.0")
    with pytest.raises(RunnerContractError, match="version"):
        runner.run(request)
    assert runner.invocations == 0
    assert list(exchange.iterdir()) == []


@pytest.mark.parametrize("authority", [None, "read_only"])
def test_missing_or_insufficient_caller_grant_never_dispatches(tmp_path, authority):
    _, _, driver, runner, target, _ = _build_driver(tmp_path)
    driver.grant = ExecutionGrant(authority) if authority else None
    assert driver.run_next()["status"] == "failed"
    assert runner.invocations == 0
    assert list(target.iterdir()) == []


@pytest.mark.parametrize("authority", ["", "unspecified", "admin"])
def test_invalid_caller_grant_rejected(authority):
    with pytest.raises(RunnerContractError, match="authority"):
        ExecutionGrant(authority)


@pytest.mark.parametrize("field,value", [("authority", ""), ("approval_status", ""),
                                        ("approval_status", "AWAITING_APPROVAL"),
                                        ("workspace_root", "relative"), ("plan_fingerprint", "sha256:stale")])
def test_direct_adapter_rejects_missing_wrong_or_stale_controls(tmp_path, field, value):
    _, _, driver, runner, _, exchange = _build_driver(tmp_path)
    with pytest.raises(RunnerContractError):
        runner.run(replace(driver._request("work-1"), **{field: value}))
    assert runner.invocations == 0
    assert list(exchange.iterdir()) == []


def test_manual_stage_approval_is_bound_to_current_plan_and_precedes_dispatch(tmp_path):
    _, _, driver, runner, _, _ = _build_driver(tmp_path)
    driver.grant = ExecutionGrant("branch_write", "manual")
    assert driver.run_next()["status"] == "passed"  # audit requires no human execution approval
    assert driver.run_until_blocked() == "AWAITING_APPROVAL"
    assert runner.invocations == 1
    with pytest.raises(RunnerContractError, match="stale"):
        driver.approve_stage("work-2", plan_fingerprint="sha256:" + "0" * 64)
    driver.approve_stage("work-2", plan_fingerprint=driver.plan_fingerprint)
    assert driver.run_next()["status"] == "passed"
    assert runner.invocations == 2


def test_resume_requires_same_explicit_caller_grant(tmp_path):
    _, _, driver, runner, target, _ = _build_driver(tmp_path)
    driver.run_next()
    with pytest.raises(RunnerContractError, match="caller grant"):
        ExecutionDriver.resume(driver.work_plan, runner, workspace_root=target,
                               checkpoint_store=JsonCheckpointStore(tmp_path / "checkpoint.json"),
                               grant=ExecutionGrant("release"))
    assert runner.invocations == 1

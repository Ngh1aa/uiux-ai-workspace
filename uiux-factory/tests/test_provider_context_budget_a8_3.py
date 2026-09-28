from __future__ import annotations

from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.provider import ScriptedProvider
from core.runtime.flow_os.provider_runner import ProviderContextBudgetError, ProviderManagedRunner


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"


def _research_run(tmp_path: Path, *, source_text: str | None = None):
    project = tmp_path / "project"
    project.mkdir()
    explicit_sources: list[str] = []
    if source_text is not None:
        (project / "source.md").write_text(source_text, encoding="utf-8")
        explicit_sources = ["source.md"]

    harness = ProviderNeutralAgentHarness(SKILLS_ROOT, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Build a modern ecommerce website with search and forms",
        authority="branch_write",
        overrides={
            "website_type": "ecommerce",
            "mode": "interactive-prototype",
            "features": ["search", "forms"],
        },
    )
    stage_state = manager.start_stage(managed, explicit_sources=explicit_sources)
    runner = ProviderManagedRunner(manager, ScriptedProvider([]))
    return harness, manager, managed, stage_state, runner


def _skill_item(stage_state, skill: str) -> dict:
    return next(
        item
        for item in stage_state.context["items"]
        if item.get("kind") == "skill" and Path(str(item["path"])).parent.name == skill
    )


def test_a8_3_request_exposes_shared_document_budget_metadata(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("UIUX_PROVIDER_CONTEXT_CHARS", raising=False)
    _harness, _manager, managed, stage_state, runner = _research_run(
        tmp_path,
        source_text="project truth\n" * 20,
    )

    request = runner._request(managed, stage_state, [])
    budget = request.task_context["provider_context_budget"]
    measured = sum(len(item["content"]) for item in request.skill_context + request.source_context)

    assert budget["loaded_document_chars"] == measured
    assert budget["skill_document_chars"] == sum(len(item["content"]) for item in request.skill_context)
    assert budget["source_document_chars"] == sum(len(item["content"]) for item in request.source_context)
    assert budget["remaining_document_chars"] == budget["max_document_chars_per_request"] - measured
    assert budget["source"] == "runtime_policy"
    assert budget["authority_effect"] == "none"
    assert budget["gate_effect"] == "none"
    assert budget["evidence_effect"] == "none"


def test_a8_3_skill_and_source_documents_share_one_budget(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("UIUX_PROVIDER_CONTEXT_CHARS", raising=False)
    harness, _manager, managed, stage_state, runner = _research_run(
        tmp_path,
        source_text="S" * 12000,
    )

    initial = runner._request(managed, stage_state, [])
    metadata = initial.task_context["provider_context_budget"]
    skill_chars = metadata["skill_document_chars"]
    source_chars = metadata["source_document_chars"]
    assert skill_chars > 0
    assert source_chars > 0
    assert skill_chars + source_chars > max(skill_chars, source_chars)

    # This ceiling is deliberately large enough for each category independently,
    # but too small for their combined request. Pre-A8.3 separate loaders would pass.
    shared_ceiling = max(skill_chars, source_chars) + 1
    harness.policy_doc["provider_context"]["max_document_chars_per_request"] = shared_ceiling

    with pytest.raises(ProviderContextBudgetError, match="shared provider context document budget exceeded"):
        runner._request(managed, stage_state, [])


def test_a8_3_jit_activation_preflight_is_atomic_on_budget_rejection(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("UIUX_PROVIDER_CONTEXT_CHARS", raising=False)
    harness, _manager, managed, stage_state, runner = _research_run(tmp_path)

    baseline = runner._request(managed, stage_state, [])
    baseline_chars = baseline.task_context["provider_context_budget"]["loaded_document_chars"]
    candidate = _skill_item(stage_state, "ecommerce-website")
    candidate_chars = len(Path(str(candidate["path"])).read_text(encoding="utf-8"))
    assert candidate_chars > 1

    harness.policy_doc["provider_context"]["max_document_chars_per_request"] = (
        baseline_chars + candidate_chars - 1
    )
    assert runner._request(managed, stage_state, []).task_context["provider_context_budget"][
        "loaded_document_chars"
    ] == baseline_chars

    result = runner._execute_one(
        managed,
        stage_state,
        "activate_skill_context",
        {"skill": "ecommerce-website"},
    )

    assert result["accepted"] is False
    assert result["activated"] is None
    assert result["requested"] == "ecommerce-website"
    assert result["available_next_turn"] is False
    assert "budget exceeded" in result["reason"]
    assert stage_state.context.get("jit_active_skills", []) == []

    resumed = harness.resume(stage_state.run_id)
    assert resumed.context.get("jit_active_skills", []) == []
    next_request = runner._request(managed, stage_state, [])
    assert "ecommerce-website" in next_request.task_context["jit_skill_context"]["available_jit_skills"]


def test_a8_3_successful_activation_reports_post_activation_budget(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("UIUX_PROVIDER_CONTEXT_CHARS", raising=False)
    _harness, _manager, managed, stage_state, runner = _research_run(tmp_path)

    result = runner._execute_one(
        managed,
        stage_state,
        "activate_skill_context",
        {"skill": "ecommerce-website"},
    )

    assert result["accepted"] is True
    assert result["activated"] == "ecommerce-website"
    assert result["document_chars_after_activation"] > 0
    assert result["document_char_limit"] >= result["document_chars_after_activation"]
    assert result["remaining_document_chars"] == (
        result["document_char_limit"] - result["document_chars_after_activation"]
    )


def test_a8_3_initial_context_overflow_blocks_before_provider_call(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("UIUX_PROVIDER_CONTEXT_CHARS", raising=False)
    project = tmp_path / "project"
    project.mkdir()
    harness = ProviderNeutralAgentHarness(SKILLS_ROOT, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Build a modern ecommerce website with search and forms",
        authority="branch_write",
        overrides={
            "website_type": "ecommerce",
            "mode": "interactive-prototype",
            "features": ["search", "forms"],
        },
    )
    harness.policy_doc["provider_context"]["max_document_chars_per_request"] = 1
    provider = ScriptedProvider([])
    runner = ProviderManagedRunner(manager, provider)

    result = runner.run_active_stage(managed, max_turns=1, auto_replan=False)

    assert result.state == "BLOCKED"
    assert managed.state == "BLOCKED"
    assert provider.requests == []
    stage_run_id = managed.stage_runs["research"][-1]
    resumed = harness.resume(stage_run_id)
    assert resumed.state == "BLOCKED"
    assert any("provider context budget exceeded" in item for item in resumed.limitations)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("180000", "provider_context.max_document_chars_per_request must be an integer"),
        (True, "provider_context.max_document_chars_per_request must be an integer"),
        (0, "provider_context.max_document_chars_per_request must be between 1 and 2000000"),
    ],
)
def test_a8_3_provider_context_policy_is_strict(
    tmp_path: Path,
    monkeypatch,
    value: object,
    message: str,
) -> None:
    monkeypatch.delenv("UIUX_PROVIDER_CONTEXT_CHARS", raising=False)
    harness, _manager, managed, stage_state, runner = _research_run(tmp_path)
    harness.policy_doc["provider_context"]["max_document_chars_per_request"] = value

    with pytest.raises(ValueError, match=message):
        runner._request(managed, stage_state, [])


def test_a8_3_env_context_limit_can_only_lower_policy_ceiling(tmp_path: Path, monkeypatch) -> None:
    harness, _manager, managed, stage_state, runner = _research_run(tmp_path)
    harness.policy_doc["provider_context"]["max_document_chars_per_request"] = 180000

    monkeypatch.setenv("UIUX_PROVIDER_CONTEXT_CHARS", "170000")
    lowered = runner._request(managed, stage_state, []).task_context["provider_context_budget"]
    assert lowered["max_document_chars_per_request"] == 170000
    assert lowered["source"] == "runtime_policy+env_ceiling"

    monkeypatch.setenv("UIUX_PROVIDER_CONTEXT_CHARS", "190000")
    capped = runner._request(managed, stage_state, []).task_context["provider_context_budget"]
    assert capped["max_document_chars_per_request"] == 180000
    assert capped["source"] == "runtime_policy"

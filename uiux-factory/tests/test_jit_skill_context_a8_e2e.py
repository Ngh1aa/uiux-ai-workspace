from __future__ import annotations

from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.provider import ScriptedProvider
from core.runtime.flow_os.provider_runner import ProviderManagedRunner


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"


def _managed_research_run(tmp_path: Path):
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
    return harness, manager, managed


def _skill_names(request) -> set[str]:
    return {Path(item["path"]).parent.name for item in request.skill_context}


def test_a8_multiturn_provider_activation_reloads_skill_context(tmp_path: Path) -> None:
    harness, manager, managed = _managed_research_run(tmp_path)
    provider = ScriptedProvider(
        [
            {
                "status": "CONTINUE",
                "actions": [
                    {
                        "tool": "activate_skill_context",
                        "args": {"skill": "ecommerce-website"},
                    }
                ],
                "summary": "Activate the routed ecommerce skill before continuing.",
                "evidence": [],
                "replan_signal": None,
            },
            {
                "status": "BLOCKED",
                "actions": [],
                "summary": "Stop after verifying the next provider turn received the activated skill.",
                "evidence": [],
                "replan_signal": "BLOCKED",
            },
        ]
    )
    runner = ProviderManagedRunner(manager, provider)

    result = runner.run_active_stage(
        managed,
        max_turns=2,
        auto_replan=False,
    )

    assert result.state == "BLOCKED"
    assert result.cycles == 2
    assert len(provider.requests) == 2

    first, second = provider.requests
    assert "ecommerce-website" not in _skill_names(first)
    assert "ecommerce-website" in first.task_context["jit_skill_context"]["available_jit_skills"]

    assert "ecommerce-website" in _skill_names(second)
    assert second.task_context["jit_skill_context"]["active_jit_skills"] == ["ecommerce-website"]
    assert "ecommerce-website" not in second.task_context["jit_skill_context"]["available_jit_skills"]
    assert second.observations[-1]["tool"] == "activate_skill_context"
    assert second.observations[-1]["result"]["activated"] == "ecommerce-website"

    stage_run_id = managed.stage_runs["research"][-1]
    resumed = harness.resume(stage_run_id)
    assert resumed.context["jit_active_skills"] == ["ecommerce-website"]
    assert resumed.context["provider_observations"][-1]["tool"] == "activate_skill_context"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("enabled", "false", "jit_skill_context.enabled must be a boolean"),
        ("max_active_per_stage", "6", "jit_skill_context.max_active_per_stage must be an integer"),
        ("max_active_per_stage", True, "jit_skill_context.max_active_per_stage must be an integer"),
    ],
)
def test_a8_jit_policy_types_are_strict(
    tmp_path: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    harness, manager, managed = _managed_research_run(tmp_path)
    harness.policy_doc["jit_skill_context"][field] = value
    stage_state = manager.start_stage(managed)
    runner = ProviderManagedRunner(manager, ScriptedProvider([]))

    with pytest.raises(ValueError, match=message):
        runner._request(managed, stage_state, [])

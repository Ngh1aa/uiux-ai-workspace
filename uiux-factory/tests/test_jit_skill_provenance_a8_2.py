from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.flow import (
    ReplanDecision,
    ReplanningEngine,
    ResolvedFlow,
    ResolvedStage,
    SkillResolver,
)
from core.runtime.flow_os.managed import ManagedFlowController, ManagedWebsiteRun
from core.runtime.flow_os.provider import ScriptedProvider
from core.runtime.flow_os.provider_runner import ProviderManagedRunner


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS_ROOT / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def test_optional_skills_are_real_jit_capabilities_with_provenance() -> None:
    resolver = SkillResolver(SKILLS_ROOT, POLICY)
    stage = {
        "id": "research",
        "agent": "research",
        "purpose": "fixture",
        "required_skills": ["website-audit-and-redesign"],
        "optional_skills": ["ecommerce-website"],
        "conditional_skills": [
            {
                "when": {"features": ["search"]},
                "skills": ["site-search-and-findability"],
            }
        ],
    }

    resolved = resolver.resolve_stage(
        stage,
        {"features": ["search"]},
        additional_skills=["conversion-and-content"],
    )

    assert "ecommerce-website" in resolved.skills
    assert "ecommerce-website" not in resolved.mandatory_skills
    assert resolved.jit_skills == [
        "ecommerce-website",
        "site-search-and-findability",
        "conversion-and-content",
    ]
    assert resolved.jit_skill_sources == {
        "ecommerce-website": "optional",
        "site-search-and-findability": "conditional",
        "conversion-and-content": "additional",
    }


def test_optional_skill_missing_from_library_fails_closed() -> None:
    resolver = SkillResolver(SKILLS_ROOT, POLICY)
    stage = {
        "id": "research",
        "agent": "research",
        "purpose": "fixture",
        "required_skills": [],
        "optional_skills": ["definitely-not-a-real-skill"],
    }

    with pytest.raises(ValueError, match="references missing skills"):
        resolver.resolve_stage(stage, {})


def test_old_a8_checkpoint_stage_infers_legacy_jit_pool() -> None:
    payload = {
        "manager_run_id": "manager_fixture",
        "flow": {
            "id": "fixture-flow",
            "source": "flows/fixture.json",
            "score": 1,
            "stages": [
                {
                    "id": "research",
                    "agent": "research",
                    "purpose": "fixture",
                    "skills": ["project-context", "ecommerce-website"],
                    "mandatory_skills": ["project-context"],
                    "gates": [],
                }
            ],
            "replanning": {},
            "revision": 0,
            "replan_history": [],
        },
        "task_context": {},
        "authority": "read_only",
        "active_stage": "research",
    }

    resumed = ManagedWebsiteRun.from_dict(payload)
    stage = resumed.flow.stages[0]

    assert stage.jit_skills == ["ecommerce-website"]
    assert stage.jit_skill_sources == {"ecommerce-website": "legacy_inferred"}


def test_explicit_empty_jit_pool_is_not_treated_as_legacy_missing_metadata() -> None:
    stage = ResolvedStage(
        id="research",
        agent="research",
        purpose="fixture",
        skills=["project-context", "ecommerce-website"],
        mandatory_skills=["project-context"],
        jit_skills=[],
        jit_skill_sources={},
    )

    assert stage.jit_skills == []
    assert stage.jit_skill_sources == {}


def test_resolved_stage_rejects_invalid_jit_provenance() -> None:
    with pytest.raises(ValueError, match="invalid JIT source"):
        ResolvedStage(
            id="research",
            agent="research",
            purpose="fixture",
            skills=["project-context", "ecommerce-website"],
            mandatory_skills=["project-context"],
            jit_skills=["ecommerce-website"],
            jit_skill_sources={"ecommerce-website": "provider_invented"},
        )

    with pytest.raises(ValueError, match="provenance for non-JIT skills"):
        ResolvedStage(
            id="research",
            agent="research",
            purpose="fixture",
            skills=["project-context", "ecommerce-website"],
            mandatory_skills=["project-context"],
            jit_skills=["ecommerce-website"],
            jit_skill_sources={
                "ecommerce-website": "optional",
                "project-context": "optional",
            },
        )


def test_replan_add_drop_updates_jit_pool_and_provenance() -> None:
    stage = ResolvedStage(
        id="implementation",
        agent="implementation",
        purpose="fixture",
        skills=["ai-agent-coding-guardrails", "conversion-and-content"],
        mandatory_skills=["ai-agent-coding-guardrails"],
        jit_skills=["conversion-and-content"],
        jit_skill_sources={"conversion-and-content": "conditional"},
    )
    flow = ResolvedFlow(
        id="fixture",
        source="flows/fixture.json",
        score=1,
        stages=[stage],
        replanning={},
    )
    decision = ReplanDecision(
        accepted=True,
        signal="GATE_FAIL",
        reason="fixture",
        target_stage="implementation",
        add_skills=["site-search-and-findability"],
        drop_skills=["conversion-and-content"],
    )

    updated = ReplanningEngine().apply(flow, decision)
    next_stage = updated.stages[0]

    assert "conversion-and-content" not in next_stage.skills
    assert "conversion-and-content" not in next_stage.jit_skills
    assert next_stage.jit_skills == ["site-search-and-findability"]
    assert next_stage.jit_skill_sources == {"site-search-and-findability": "replan"}


def test_provider_runner_uses_explicit_jit_pool_not_nonmandatory_difference(tmp_path: Path) -> None:
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

    stages = []
    for stage in managed.flow.stages:
        if stage.id != "research":
            stages.append(stage)
            continue
        assert "ecommerce-website" in stage.skills
        assert "conversion-and-content" in stage.skills
        stages.append(
            replace(
                stage,
                jit_skills=["ecommerce-website"],
                jit_skill_sources={"ecommerce-website": "optional"},
            )
        )
    managed.flow = replace(managed.flow, stages=stages)

    stage_state = manager.start_stage(managed)
    runner = ProviderManagedRunner(manager, ScriptedProvider([]))
    request = runner._request(managed, stage_state, [])
    jit = request.task_context["jit_skill_context"]

    assert jit["available_jit_skills"] == ["ecommerce-website"]
    assert jit["jit_skill_sources"] == {"ecommerce-website": "optional"}
    assert "conversion-and-content" not in jit["available_jit_skills"]

    activation = runner._execute_one(
        managed,
        stage_state,
        "activate_skill_context",
        {"skill": "ecommerce-website"},
    )
    assert activation["source"] == "optional"

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness, ToolRegistry
from core.runtime.flow_os.evidence import evidence_from_tool, gate_evidence_errors
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.provider import ScriptedProvider
from core.runtime.flow_os.provider_runner import ProviderManagedRunner
from core.runtime.flow_os.safe_read import SafeReadError, SafeReader
from core.runtime.flow_os.skill_sections import (
    SkillSectionError,
    build_skill_section_registry,
    read_skill_section,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS_ROOT / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _first_capability(index_path: Path, *, skill: str | None = None) -> str:
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    for row in payload["routed_skills"]:
        if skill is not None and row["skill"] != skill:
            continue
        if row["sections"]:
            return str(row["sections"][0]["capability"])
    raise AssertionError("no section capability found")


def test_a8_5_registry_indexes_only_routed_skills_and_retrieves_exact_section(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    summary = build_skill_section_registry(
        project,
        SKILLS_ROOT,
        "stagefixture",
        ["ecommerce-website"],
        POLICY,
    )
    assert summary is not None
    index_path = Path(summary["path"])
    public = json.loads(index_path.read_text(encoding="utf-8"))

    assert [item["skill"] for item in public["routed_skills"]] == ["ecommerce-website"]
    assert public["advisory_only"] is True
    capability = _first_capability(index_path)

    result = read_skill_section(project, SKILLS_ROOT, capability, POLICY)
    assert result["skill"] == "ecommerce-website"
    assert result["content"]
    assert len(result["sha256"]) == 64
    assert result["authority_effect"] == "none"
    assert result["gate_effect"] == "none"
    assert result["evidence_effect"] == "none"

    registry = json.loads(
        (project / ".uiux-agent-runs" / "stagefixture" / "skill-section-registry.json").read_text(
            encoding="utf-8"
        )
    )
    assert registry["usage"]["retrievals"] == 1
    assert registry["ledger"][0]["sha256"] == result["sha256"]


def test_a8_5_unknown_capability_fails_closed(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    build_skill_section_registry(project, SKILLS_ROOT, "stagefixture", ["ecommerce-website"], POLICY)

    with pytest.raises(SkillSectionError, match="unknown or not routed"):
        read_skill_section(project, SKILLS_ROOT, "stagefixture:not-a-real-token", POLICY)


def test_a8_5_retrieval_budget_is_stage_bounded(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    policy = json.loads(json.dumps(POLICY))
    policy["jit_skill_sections"]["max_retrievals_per_stage"] = 1
    summary = build_skill_section_registry(
        project,
        SKILLS_ROOT,
        "stagefixture",
        ["ecommerce-website"],
        policy,
    )
    assert summary is not None
    capability = _first_capability(Path(summary["path"]))
    read_skill_section(project, SKILLS_ROOT, capability, policy)

    with pytest.raises(SkillSectionError, match="count budget exhausted"):
        read_skill_section(project, SKILLS_ROOT, capability, policy)


def test_a8_5_safe_read_allows_only_public_index_not_private_registry(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    summary = build_skill_section_registry(
        project,
        SKILLS_ROOT,
        "stagefixture",
        ["ecommerce-website"],
        POLICY,
    )
    assert summary is not None
    reader = SafeReader(project)

    public = reader.read_text(".uiux-agent-runs/stagefixture/skill-section-index.json")
    assert "routed_skills" in public.content
    with pytest.raises(SafeReadError, match="blocked directory"):
        reader.read_text(".uiux-agent-runs/stagefixture/skill-section-registry.json")
    with pytest.raises(SafeReadError, match="blocked directory"):
        reader.read_text(".uiux-agent-runs/stagefixture/checkpoint.json")


def test_a8_5_skill_section_read_is_advisory_not_gate_evidence() -> None:
    record = evidence_from_tool(
        "research",
        "read_skill_section",
        {
            "skill": "ecommerce-website",
            "section_id": "overview",
            "content": "secret-to-evidence-channel",
            "sha256": "a" * 64,
            "chars": 10,
        },
    )
    payload = record.to_dict()

    assert payload["trusted"] is False
    assert payload["type"] == "skill_section_read"
    assert "content" not in payload["data"]
    errors = gate_evidence_errors(
        [{"id": "research-proof", "require": "runtime evidence"}],
        "research",
        [payload],
        agent="research",
    )
    assert errors


def test_a8_5_managed_provider_receives_public_index_and_section_tool(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    harness = ProviderNeutralAgentHarness(SKILLS_ROOT, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Build a modern ecommerce website with search",
        authority="branch_write",
        overrides={
            "website_type": "ecommerce",
            "mode": "interactive-prototype",
            "features": ["search"],
        },
    )
    stage_state = manager.start_stage(managed)
    runner = ProviderManagedRunner(manager, ScriptedProvider([]))
    request = runner._request(managed, stage_state, [])

    assert "read_skill_section" in {tool["name"] for tool in request.tools}
    indexes = []
    for item in request.source_context:
        try:
            payload = json.loads(item["content"])
        except (KeyError, TypeError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and "routed_skills" in payload:
            indexes.append(payload)
    assert len(indexes) == 1

    routed = {row["skill"] for row in indexes[0]["routed_skills"]}
    stage = next(item for item in managed.flow.stages if item.id == managed.active_stage)
    assert routed == set(stage.skills)

    capability = next(
        section["capability"]
        for row in indexes[0]["routed_skills"]
        if row["skill"] == "ecommerce-website"
        for section in row["sections"]
    )
    result = runner._execute_one(
        managed,
        stage_state,
        "read_skill_section",
        {"capability": capability},
    )
    assert result["skill"] == "ecommerce-website"


def test_a8_5_tool_registry_rejects_cross_run_capability(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    summary = build_skill_section_registry(
        project,
        SKILLS_ROOT,
        "runone",
        ["ecommerce-website"],
        POLICY,
    )
    assert summary is not None
    capability = _first_capability(Path(summary["path"]))
    token = capability.split(":", 1)[1]
    registry = ToolRegistry(SKILLS_ROOT, project)

    with pytest.raises(SkillSectionError):
        registry.execute("read_skill_section", {"capability": f"runtwo:{token}"})

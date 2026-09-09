import json
from pathlib import Path

from core.orchestration.reference_intelligence import ReferenceIntelligencePlanner
from core.orchestration.skill_governance import FlowReplanner, SkillGovernanceSnapshot


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def test_reference_intelligence_preserves_user_reference_priority() -> None:
    planner = ReferenceIntelligencePlanner()
    user = ["https://example.com/"]
    plan = planner.plan(
        goal="Tạo website SaaS hiện đại có dashboard",
        user_urls=user,
        auto_enabled=True,
        target_reference_count=2,
    )

    assert plan.website_type == "saas"
    assert plan.final_reference_urls[0] == user[0]
    assert len(plan.final_reference_urls) == 2
    assert len(plan.selected) == 1
    assert plan.selected[0].provenance == "curated-public-production-site"
    assert "Do not copy" in plan.selected[0].transfer_policy


def test_reference_intelligence_can_be_disabled() -> None:
    planner = ReferenceIntelligencePlanner()
    plan = planner.plan(
        goal="Build an ecommerce store",
        user_urls=[],
        auto_enabled=False,
        target_reference_count=2,
    )

    assert plan.final_reference_urls == []
    assert plan.selected == []


def test_skills_flow_replans_failed_qa_to_implementation() -> None:
    flow = json.loads(
        (SKILLS / "flows" / "professional-website-redesign.json").read_text(encoding="utf-8")
    )
    replanner = FlowReplanner(flow)
    decision = replanner.decide(
        signal="GATE_FAIL",
        current_stage="qa",
        task_context={
            "intent": "build",
            "website_type": "saas",
            "mode": "interactive-prototype",
            "risk": "standard",
            "features": ["dashboard"],
        },
        replan_count=0,
    )

    assert decision.accepted is True
    assert decision.target_stage == "implementation"
    assert "ui-improvement" in decision.add_skills
    assert "web-ui-code-review" in decision.add_skills


def test_replan_budget_is_enforced() -> None:
    flow = json.loads(
        (SKILLS / "flows" / "professional-website-redesign.json").read_text(encoding="utf-8")
    )
    replanner = FlowReplanner(flow)
    max_replans = int(flow["replanning"]["max_replans"])
    decision = replanner.decide(
        signal="GATE_FAIL",
        current_stage="qa",
        task_context={"risk": "standard", "features": []},
        replan_count=max_replans,
    )

    assert decision.accepted is False
    assert "budget exhausted" in decision.reason


def test_governance_snapshot_locks_cross_phase_skill_documents() -> None:
    snapshot = SkillGovernanceSnapshot(SKILLS).build()
    names = {item["path"] for item in snapshot["policy_files"]}

    assert "FLOW-AGENT-OS.md" in names
    assert "PHASE-AWARE-GATING.md" in names
    assert "FINAL-UIUX-VISUAL-CONTENT-QA-REMEDIATION-V3.2.md" in names
    assert all(len(item["sha256"]) == 64 for item in snapshot["policy_files"])
    assert "PENDING_FUTURE_PHASE" in snapshot["requirement_states"]

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.brain_os.adapters.flow_selection import (
    EscalationTrigger,
    FlowEscalationProposal,
    SurfaceSource,
    propose_bounded_escalation,
    select_after_bounded_escalation,
    select_canonical_flow,
)
from core.runtime.flow_os.flow import FlowPlanner


FACTORY = Path(__file__).resolve().parents[1]
WORKSPACE = FACTORY.parent
SKILLS = WORKSPACE / "skills_UIUX"


def _planner() -> FlowPlanner:
    policy = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))
    return FlowPlanner(SKILLS, policy)


def _context(**updates: object) -> dict[str, object]:
    base: dict[str, object] = {
        "intent": "improve",
        "website_type": "generic",
        "domain": "generic",
        "product_archetype": "generic",
        "validation_lane": "prototype",
        "mode": "interactive-prototype",
        "risk": "normal",
        "features": [],
        "scope": [],
    }
    base.update(updates)
    return base


@pytest.mark.parametrize(
    ("goal", "context", "expected_surface", "expected_flow"),
    [
        (
            "Fix the spacing on one card",
            _context(intent="fix", scope=["card", "spacing"]),
            "MICRO",
            "micro-ui-change",
        ),
        (
            "Improve the pricing section",
            _context(intent="improve", scope=["pricing"]),
            "FOCUSED",
            "existing-ui-improvement",
        ),
        (
            "Build one landing page",
            _context(intent="build", website_type="landing", scope=["landing-page"]),
            "PAGE",
            "page-ui-work",
        ),
        (
            "Redesign the whole website",
            _context(intent="redesign", website_type="corporate"),
            "REDESIGN",
            "professional-website-redesign",
        ),
        (
            "Build a SaaS web app platform",
            _context(intent="build", website_type="saas"),
            "PRODUCT",
            "professional-website-redesign",
        ),
        (
            "Redesign the whole website portfolio",
            _context(intent="redesign", website_type="portfolio"),
            "REDESIGN",
            "portfolio-career-system",
        ),
    ],
)
def test_a43_smallest_surface_routes_through_canonical_planner(
    goal: str,
    context: dict[str, object],
    expected_surface: str,
    expected_flow: str,
) -> None:
    selection = select_canonical_flow(_planner(), context=context, goal=goal)

    assert selection.change_surface == expected_surface
    assert selection.flow_id == expected_flow
    assert selection.surface_source is SurfaceSource.CANONICAL_CLASSIFIER
    assert selection.canonical_owner == "core.runtime.flow_os.flow.FlowPlanner"
    assert selection.classifier_owner == "core.runtime.flow_os.adaptive_surface.classify_change_surface"


def test_a43_existing_task_contract_surface_is_preserved_over_goal_text() -> None:
    selection = select_canonical_flow(
        _planner(),
        context=_context(
            intent="fix",
            change_surface="PAGE",
            website_type="landing",
            scope=["button"],
        ),
        goal="Fix one button",
    )

    assert selection.change_surface == "PAGE"
    assert selection.flow_id == "page-ui-work"
    assert selection.surface_source is SurfaceSource.TASK_CONTRACT


def test_a43_bounded_escalation_moves_only_one_surface_and_replans_canonically() -> None:
    planner = _planner()
    context = _context(intent="fix", change_surface="MICRO", scope=["card"])
    initial = select_canonical_flow(planner, context=context, goal="Fix one card")
    proposal = propose_bounded_escalation(
        current_surface="MICRO",
        trigger=EscalationTrigger.SCOPE_INSUFFICIENT,
        reason="Rendered evidence shows the issue spans the whole card cluster.",
    )
    widened = select_after_bounded_escalation(planner, context=context, proposal=proposal)

    assert initial.flow_id == "micro-ui-change"
    assert proposal.from_surface == "MICRO"
    assert proposal.to_surface == "FOCUSED"
    assert widened.change_surface == "FOCUSED"
    assert widened.flow_id == "existing-ui-improvement"
    assert widened.surface_source is SurfaceSource.BOUNDED_ESCALATION


def test_a43_escalation_contract_rejects_skipping_surface_levels() -> None:
    with pytest.raises(ValueError, match="one surface at a time"):
        FlowEscalationProposal(
            from_surface="MICRO",
            to_surface="PAGE",
            trigger=EscalationTrigger.SCOPE_INSUFFICIENT,
            reason="Invalid jump",
        )


def test_a43_product_surface_cannot_escalate_further() -> None:
    with pytest.raises(ValueError, match="widest change surface"):
        propose_bounded_escalation(
            current_surface="PRODUCT",
            trigger=EscalationTrigger.SCOPE_INSUFFICIENT,
            reason="No wider surface exists.",
        )


def test_a43_evidence_driven_escalation_requires_evidence_reference() -> None:
    with pytest.raises(ValueError, match="requires at least one evidence reference"):
        propose_bounded_escalation(
            current_surface="FOCUSED",
            trigger=EscalationTrigger.EVIDENCE_REVEALED_BROADER_SCOPE,
            reason="A rendered issue appears on multiple page regions.",
        )

    proposal = propose_bounded_escalation(
        current_surface="FOCUSED",
        trigger=EscalationTrigger.EVIDENCE_REVEALED_BROADER_SCOPE,
        reason="Browser evidence shows the defect spans the full route.",
        evidence_refs=["ev_browser_001", "ev_browser_001"],
    )
    assert proposal.to_surface == "PAGE"
    assert proposal.evidence_refs == ["ev_browser_001"]


def test_a43_escalation_source_must_match_current_context() -> None:
    proposal = propose_bounded_escalation(
        current_surface="MICRO",
        trigger=EscalationTrigger.REQUIRED_STAGE_MISSING,
        reason="The current lane lacks the research stage required by new scope.",
    )

    with pytest.raises(ValueError, match="source mismatch"):
        select_after_bounded_escalation(
            _planner(),
            context=_context(intent="improve", change_surface="PAGE"),
            proposal=proposal,
        )

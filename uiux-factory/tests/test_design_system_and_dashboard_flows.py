"""Routing for work whose object is a design system or a product dashboard."""
import json
from pathlib import Path

import pytest

from core.runtime.flow_os.external_task import build_external_task_manifest
from core.runtime.flow_os.task_context import GoalInterpreter

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime/runtime-policy.json").read_text(encoding="utf-8"))


def _packet(goal: str, authority: str = "branch_write") -> dict:
    return build_external_task_manifest(SKILLS, POLICY, goal, "example/product", authority=authority).to_dict()


def _skills(packet: dict, stage_id: str | None = None) -> set[str]:
    return {skill for stage in packet["stages"] if stage_id in (None, stage["id"]) for skill in stage["skills"]}


@pytest.mark.parametrize("goal", [
    "Build a design system for our fintech product",
    "Nâng cấp design system: thêm dark mode và component mới",
    "Add dark mode tokens to the design system",
    "Refactor the component library and document every state",
    "Tạo hệ thống thiết kế cho sản phẩm",
])
def test_design_system_as_work_object_routes_to_design_system_work(goal):
    packet = _packet(goal)
    assert packet["resolved_flow"]["id"] == "design-system-work"
    assert [stage["id"] for stage in packet["stages"]] == ["research", "design", "implementation", "qa"]
    skills = _skills(packet)
    assert {"design-system-and-components", "design-system-governance-and-adoption", "visual-regression-and-design-drift"} <= skills


def test_mobile_design_system_adds_platform_handoff_skills():
    packet = _packet("Tạo hệ thống thiết kế cho app iOS và Android")
    assert packet["resolved_flow"]["id"] == "design-system-work"
    research = _skills(packet, "research")
    assert {"mobile-design-system-and-handoff", "ios-app-design", "android-app-design"} <= research


@pytest.mark.parametrize("goal", [
    "Audit our design system for consistency",
    "Review only the design system tokens; do not change code",
])
def test_design_system_review_is_read_only(goal):
    packet = _packet(goal)
    assert packet["resolved_flow"]["id"] == "design-system-audit"
    assert packet["authority"] == "read_only"
    assert all(stage["agent"] != "implementation" for stage in packet["stages"])


@pytest.mark.parametrize("goal", [
    "Build a landing page using our design system",
    "Redesign homepage, keep design system",
    "Redesign the dashboard with the existing design system",
    "Fix the button; do not change the design system",
    "Sửa trang chủ theo design system hiện có",
])
def test_consuming_a_design_system_is_not_design_system_work(goal):
    assert not _packet(goal)["resolved_flow"]["id"].startswith("design-system")


@pytest.mark.parametrize("goal", [
    "Improve dashboard screen",
    "Build an admin console for fraud case review",
    "Thiết kế lại trang quản trị đơn hàng",
    "Redesign the analytics dashboard and the settings page",
])
def test_product_dashboards_route_to_web_app_dashboard(goal):
    packet = _packet(goal)
    assert packet["resolved_flow"]["id"] == "web-app-dashboard"
    assert {"data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux", "state-feedback-and-error-recovery"} <= _skills(packet, "design")
    assert "information-architecture" in _skills(packet, "research")


@pytest.mark.parametrize("goal,expected", [
    ("Redesign our SaaS marketing website with analytics", "professional-website-redesign"),
    ("Build a SaaS software platform with dashboard", "professional-website-redesign"),
    ("Fix the dashboard button color", "micro-ui-change"),
    ("Audit the dashboard", "audit-review"),
])
def test_dashboard_mentions_that_are_not_the_work_object_keep_their_lane(goal, expected):
    assert _packet(goal)["resolved_flow"]["id"] == expected


def test_financial_dashboard_keeps_specialist_composition():
    packet = _packet("Build a fintech fraud case review dashboard with a transaction table.")
    assert packet["resolved_flow"]["id"] == "web-app-dashboard"
    assert "security-and-privacy" in _skills(packet)


def test_features_are_reported_in_the_task_contract():
    assert "design-system" in GoalInterpreter().interpret("Build a design system").features
    dashboard = GoalInterpreter().interpret("Improve dashboard screen").features
    assert {"dashboard", "app-dashboard"} <= set(dashboard)
    assert "app-dashboard" not in GoalInterpreter().interpret("Build a SaaS platform with dashboard").features

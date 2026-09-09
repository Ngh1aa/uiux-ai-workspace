from core.contracts.browser_qa_schema import (
    BrowserQAGate,
    BrowserQAResult,
    RouteViewportEvidence,
    ViewportSpec,
)


def test_advanced_browser_qa_evidence_fields_round_trip() -> None:
    viewport = ViewportSpec(name="mobile-390", width=390, height=844)
    evidence = RouteViewportEvidence(
        route="/",
        viewport=viewport,
        screenshot="/tmp/home.png",
        status="failed",
        missing_alt_count=1,
        unlabeled_control_count=2,
        small_control_target_count=3,
        focus_obscured_count=1,
        catastrophic_contrast_count=1,
    )

    result = BrowserQAResult(
        status="partial",
        project_slug="demo",
        project_dir="/tmp/demo",
        base_url="http://127.0.0.1:1234",
        routes=["/"],
        viewports=[viewport],
        evidence=[evidence],
        gates=BrowserQAGate(
            routes_discovered=True,
            screenshots_created=True,
            no_page_errors=True,
            no_console_errors=True,
            no_horizontal_overflow=True,
            internal_links_valid=True,
            semantic_smoke_passed=True,
            image_alt_smoke_passed=False,
            accessible_name_smoke_passed=False,
            control_target_smoke_passed=False,
            focus_visibility_smoke_passed=False,
            elementary_visual_sanity_passed=False,
            ready_for_visual_critic=False,
        ),
        summary={"missing_alt_count": 1},
    )

    restored = BrowserQAResult.model_validate_json(result.model_dump_json())
    assert restored.schema_version == "0.2.0"
    assert restored.evidence[0].missing_alt_count == 1
    assert restored.evidence[0].small_control_target_count == 3
    assert restored.gates.ready_for_visual_critic is False


def test_accessibility_smoke_defaults_do_not_fake_a_pass() -> None:
    gates = BrowserQAGate()
    assert gates.image_alt_smoke_passed is False
    assert gates.accessible_name_smoke_passed is False
    assert gates.control_target_smoke_passed is False
    assert gates.focus_visibility_smoke_passed is False
    assert gates.elementary_visual_sanity_passed is False

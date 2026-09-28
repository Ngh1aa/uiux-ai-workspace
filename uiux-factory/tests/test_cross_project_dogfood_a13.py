from __future__ import annotations

from core.dogfood.cross_project import (
    PROJECT_PROFILES,
    compile_task_contract,
    evaluate_cross_project_contract,
    project_profile,
    resolve_source_truth,
)


LUMEN_PATHS = {
    "AGENTS.md",
    "PROJECT-CONTEXT.md",
    "docs/COMPOSITION-PROOFS.md",
    "docs/CULTURAL-EXPERIENCE.md",
    "docs/DESIGN-DIRECTION.md",
    "docs/DISCOVERY-MODES.md",
    "docs/IA-AND-FLOWS.md",
    "docs/VERIFICATION-PLAN.md",
}

CENNEXT_PATHS = {
    "README.md",
    "BRIEF_COMPLIANCE.md",
    "DESIGN_REFERENCES.md",
    "sitemap.html",
    "design-system.html",
    "component-states.html",
    "index.html",
    "motion-system.css",
}


def test_a13_lumen_visual_art_direction_stays_product_boundary_without_nova_leakage() -> None:
    profile = project_profile("lumen")
    report = evaluate_cross_project_contract(
        profile,
        available_paths=LUMEN_PATHS,
        task_description=(
            "Refine the visual and art direction only. Preserve the cultural experience and "
            "do not reopen product strategy."
        ),
        change_boundary="PRODUCT",
    )

    assert report["passed"] is True
    assert report["contract"]["change_boundary"] == "PRODUCT"
    assert report["contract"]["change_surface"] == "FOCUSED"
    assert report["routing_intent"] == "visual-art-direction"
    assert report["evidence_model"] == "composition-cultural-experience"
    assert report["source_truth"] == "PROJECT-CONTEXT.md"
    assert report["missing_evidence"] == []
    assert report["nova_domain_leaks"] == []


def test_a13_cennext_enterprise_ia_stays_product_boundary_without_fintech_assumptions() -> None:
    profile = project_profile("cennext")
    report = evaluate_cross_project_contract(
        profile,
        available_paths=CENNEXT_PATHS,
        task_description=(
            "Improve enterprise information architecture and workflow clarity while preserving "
            "brief and compliance constraints."
        ),
        change_boundary="PRODUCT",
    )

    assert report["passed"] is True
    assert report["contract"]["change_boundary"] == "PRODUCT"
    assert report["contract"]["change_surface"] == "FOCUSED"
    assert report["routing_intent"] == "enterprise-ia-workflow"
    assert report["evidence_model"] == "ia-workflow-compliance"
    assert report["source_truth"] == "README.md"
    assert report["missing_evidence"] == []
    assert report["nova_domain_leaks"] == []


def test_a13_execution_boundary_is_domain_invariant_without_overwriting_ui_surface() -> None:
    for project_id in ("nova", "lumen", "cennext"):
        profile = project_profile(project_id)
        product = compile_task_contract(profile, change_boundary="PRODUCT")
        factory = compile_task_contract(profile, change_boundary="FACTORY")

        assert product["change_boundary"] == "PRODUCT"
        assert factory["change_boundary"] == "FACTORY"
        assert product["change_surface"] == factory["change_surface"]
        assert product["dogfood_profile"]["project_id"] == project_id
        assert factory["dogfood_profile"]["project_id"] == project_id


def test_a13_source_truth_resolution_supports_hyphenated_and_legacy_underscore_names() -> None:
    lumen = project_profile("lumen")

    assert resolve_source_truth(lumen, {"PROJECT-CONTEXT.md"}) == "PROJECT-CONTEXT.md"
    assert resolve_source_truth(lumen, {"PROJECT_CONTEXT.md"}) == "PROJECT_CONTEXT.md"
    assert resolve_source_truth(lumen, {"AGENTS.md"}) == "AGENTS.md"


def test_a14_path_normalization_preserves_dotfiles_and_removes_only_real_prefixes() -> None:
    report = evaluate_cross_project_contract(
        project_profile("nova"),
        available_paths={"./PROJECT-CONTEXT.md", "./.uiux-profile.json", "/app.html"},
        change_boundary="PRODUCT",
    )

    assert report["missing_evidence"] == []
    assert report["checks"]["profile_evidence_grounded"] is True
    assert report["source_truth"] == "PROJECT-CONTEXT.md"


def test_a13_cross_project_profiles_do_not_share_one_generic_evidence_model() -> None:
    profiles = [PROJECT_PROFILES[key] for key in ("nova", "lumen", "cennext")]

    assert len({profile.archetype for profile in profiles}) == 3
    assert len({profile.routing_intent for profile in profiles}) == 3
    assert len({profile.evidence_model for profile in profiles}) == 3
    assert all(profile.expected_change_boundary == "PRODUCT" for profile in profiles)


def test_a13_missing_project_specific_evidence_fails_closed() -> None:
    report = evaluate_cross_project_contract(
        project_profile("cennext"),
        available_paths={"README.md", "index.html"},
        change_boundary="PRODUCT",
    )

    assert report["passed"] is False
    assert report["checks"]["profile_evidence_grounded"] is False
    assert "BRIEF_COMPLIANCE.md" in report["missing_evidence"]
    assert "sitemap.html" in report["missing_evidence"]

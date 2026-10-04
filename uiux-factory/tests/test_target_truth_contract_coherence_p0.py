from __future__ import annotations

import json
from pathlib import Path

from core.runtime.flow_os.external_task import build_external_task_manifest


FACTORY_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = FACTORY_ROOT.parent
SKILLS = WORKSPACE_ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _write_profile(root: Path, payload: dict[str, object]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / ".uiux-profile.json").write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_batch1_deployment_prohibition_preserves_real_project_risk(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _write_profile(target, {"mode": "production", "features": ["auth"]})
    manifest = build_external_task_manifest(
        SKILLS, POLICY, "Fix button spacing only; do not deploy production",
        "owner/product", target_root=target, authority="release",
    ).to_dict()
    contract = manifest["task_contract"]
    assert manifest["authority"] == "branch_write"
    assert contract["mode"] == "production"
    assert contract["risk"] == "production"
    assert contract["features"] == ["auth"]
    assert contract["validation_lane"] == "production-learning"
    assert contract["forbidden"] == ["deploy production"]
    assert manifest["execution_advice"]["overall_profile"]["recommended_capability"] == "advanced"


def test_p0_structured_mode_recomputes_default_validation_lane(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _write_profile(target, {"mode": "production_candidate"})

    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Improve the existing interface.",
        "owner/product",
        target_root=target,
    ).to_dict()
    contract = manifest["task_contract"]

    assert contract["mode"] == "production-candidate"
    assert contract["validation_lane"] == "production-learning"
    assert contract["routing_provenance"]["field_sources"]["mode"] == "target_project_truth"
    assert contract["routing_provenance"]["field_sources"]["validation_lane"] == "derived_from_final_contract"
    assert contract["routing_provenance"]["derived_fields"]["validation_lane"] == "mode+risk+features"


def test_p0_structured_production_mode_recomputes_default_risk_and_lane(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _write_profile(target, {"mode": "production"})

    contract = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Improve the existing interface.",
        "owner/product",
        target_root=target,
    ).to_dict()["task_contract"]

    assert contract["mode"] == "production"
    assert contract["risk"] == "production"
    assert contract["validation_lane"] == "production-learning"
    assert contract["routing_provenance"]["derived_fields"]["risk"] == "website_type+mode"


def test_p0_non_default_task_lifecycle_signal_is_not_erased_by_project_default(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _write_profile(
        target,
        {
            "mode": "visual_prototype",
            "risk": "standard",
            "validation_lane": "prototype",
        },
    )

    contract = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Improve the product for production and go live with outcome metrics.",
        "owner/product",
        target_root=target,
    ).to_dict()["task_contract"]

    assert contract["mode"] == "production"
    assert contract["risk"] == "production"
    assert contract["validation_lane"] == "production-learning"
    diagnostics = contract["routing_provenance"]["merge_diagnostics"]
    assert "structured_default_not_applied:mode:task_inference_is_non_default" in diagnostics


def test_p0_truth_features_are_additive_and_raise_validation_rigor(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _write_profile(target, {"features": ["user-validation"]})

    contract = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Improve the existing interface with motion.",
        "owner/product",
        target_root=target,
    ).to_dict()["task_contract"]

    assert contract["features"] == ["motion", "user-validation"]
    assert contract["validation_lane"] == "evidence-led"
    assert contract["routing_provenance"]["field_sources"]["features"] == "goal_inference+target_project_truth"


def test_p0_readme_fallback_only_fills_generic_identity_gaps(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "README.md").write_text(
        "Fintech banking payments platform with settlement workflows.\n",
        encoding="utf-8",
    )

    contract = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Improve the cultural museum artwork discovery experience.",
        "owner/museum",
        target_root=target,
    ).to_dict()["task_contract"]

    assert contract["domain"] == "art-culture"
    assert contract["routing_provenance"]["field_sources"]["domain"] == "goal_inference"
    assert "fallback_not_applied:domain:goal_inference_is_specific" in contract["routing_provenance"]["merge_diagnostics"]


def test_p0_domain_truth_resets_stale_goal_inferred_archetype(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _write_profile(target, {"domain": "art_culture"})

    contract = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Improve the existing fintech settlement and payment rails product.",
        "owner/product",
        target_root=target,
    ).to_dict()["task_contract"]

    assert contract["domain"] == "art-culture"
    assert contract["product_archetype"] == "generic"
    assert contract["routing_provenance"]["field_sources"]["product_archetype"] == "derived_from_final_contract"
    assert "product_archetype_reset_after_domain_change" in contract["routing_provenance"]["merge_diagnostics"]


def test_p0_explicit_lifecycle_override_remains_highest_priority(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _write_profile(target, {"mode": "production_candidate", "validation_lane": "production_learning"})

    contract = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Improve the existing interface.",
        "owner/product",
        target_root=target,
        overrides={"mode": "visual-prototype", "validation_lane": "prototype"},
    ).to_dict()["task_contract"]

    assert contract["mode"] == "visual-prototype"
    assert contract["validation_lane"] == "prototype"
    assert contract["routing_provenance"]["field_sources"]["mode"] == "explicit_override"
    assert contract["routing_provenance"]["field_sources"]["validation_lane"] == "explicit_override"

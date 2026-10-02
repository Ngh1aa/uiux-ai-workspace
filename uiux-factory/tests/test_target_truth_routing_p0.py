from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.runtime.flow_os.external_task import build_external_task_manifest
from core.runtime.flow_os.target_truth import TargetTruthProbe, TargetTruthProbeError


FACTORY_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = FACTORY_ROOT.parent
SKILLS = WORKSPACE_ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _profile(root: Path, payload: dict[str, object]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / ".uiux-profile.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_p0_target_truth_normalizes_real_project_profile_vocabulary(tmp_path: Path) -> None:
    target = tmp_path / "nova"
    _profile(
        target,
        {
            "project": "Nova — Personal Banking & Money Planning",
            "domain": "consumer_fintech_personal_banking",
            "mode": "interactive_prototype",
            "release_authorization": "merge_and_deploy",
        },
    )

    report = TargetTruthProbe(target).probe()

    assert report.status == "PROBED"
    assert report.fields["domain"] == "financial-services"
    assert report.fields["product_archetype"] == "consumer-banking"
    assert report.fields["mode"] == "interactive-prototype"
    assert "authority" not in report.fields
    assert "release_authorization" not in report.fields
    assert report.provenance["domain"]["source"] == ".uiux-profile.json"
    assert report.provenance["domain"]["authority_effect"] == "none"


def test_p0_target_truth_changes_flow_before_resolution(tmp_path: Path) -> None:
    target = tmp_path / "portfolio"
    _profile(
        target,
        {
            "website_type": "portfolio",
            "domain": "ai-software",
            "mode": "interactive_prototype",
        },
    )

    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Redesign the whole product experience and add user research evidence.",
        "owner/portfolio",
        target_root=target,
    ).to_dict()

    assert manifest["task_contract"]["website_type"] == "portfolio"
    assert manifest["task_contract"]["domain"] == "ai-software"
    assert manifest["task_contract"]["routing_provenance"]["field_sources"]["website_type"] == "target_project_truth"
    assert manifest["resolved_flow"]["id"] == "portfolio-career-system"
    assert manifest["evidence_boundary"]["target_truth_probed_before_flow_resolution"] is True


def test_p0_explicit_override_beats_target_truth(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _profile(target, {"domain": "consumer_fintech_personal_banking", "website_type": "saas"})

    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Improve the existing product interface.",
        "owner/product",
        target_root=target,
        overrides={"domain": "art-culture", "website_type": "portfolio"},
    ).to_dict()

    contract = manifest["task_contract"]
    assert contract["domain"] == "art-culture"
    assert contract["website_type"] == "portfolio"
    assert contract["routing_provenance"]["field_sources"]["domain"] == "explicit_override"
    assert contract["routing_provenance"]["field_sources"]["website_type"] == "explicit_override"
    assert contract["routing_provenance"]["precedence"] == [
        "explicit_override",
        "target_project_truth",
        "goal_inference",
    ]


def test_p0_no_target_root_truthfully_uses_goal_inference() -> None:
    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Improve the fintech banking dashboard.",
        "owner/product",
    ).to_dict()

    contract = manifest["task_contract"]
    assert contract["domain"] == "financial-services"
    assert contract["target_truth"]["status"] == "NOT_PROVIDED"
    assert contract["routing_provenance"]["field_sources"]["domain"] == "goal_inference"
    assert manifest["evidence_boundary"]["target_truth_probed_before_flow_resolution"] is False


def test_p0_unknown_placeholders_do_not_override_goal_inference(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _profile(
        target,
        {
            "domain": "UNKNOWN",
            "website_type": "[WEBSITE TYPE]",
            "mode": "TBD",
        },
    )

    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Improve the existing fintech banking app.",
        "owner/product",
        target_root=target,
    ).to_dict()

    contract = manifest["task_contract"]
    assert contract["domain"] == "financial-services"
    assert contract["routing_provenance"]["field_sources"]["domain"] == "goal_inference"
    assert "domain" not in contract["target_truth"]["fields"]


def test_p0_target_truth_cannot_escalate_authority(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _profile(
        target,
        {
            "website_type": "saas",
            "domain": "financial-services",
            "authority": "release",
            "release_authorization": "merge_and_deploy",
        },
    )

    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Chỉ audit product hiện tại, không sửa code.",
        "owner/product",
        authority="release",
        target_root=target,
    ).to_dict()

    assert manifest["authority"] == "read_only"
    assert manifest["task_contract"]["authority"] == "read_only"
    assert manifest["evidence_boundary"]["target_truth_never_grants_authority_or_evidence"] is True


def test_p0_project_context_supplies_canonical_routing_fields(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "PROJECT-CONTEXT.md").write_text(
        "\n".join(
            [
                "# Project Context",
                "- **Website type:** ecommerce",
                "- **Domain:** education edtech",
                "- **Product archetype:** learning-discovery-platform",
                "- **Validation lane:** evidence-led",
                "- **Runtime mode:** production-candidate",
                "- **Risk:** high",
                "- **Features:** user-validation, outcome-measurement",
            ]
        ) + "\n",
        encoding="utf-8",
    )

    report = TargetTruthProbe(target).probe()

    assert report.fields == {
        "website_type": "ecommerce",
        "domain": "education-edtech",
        "product_archetype": "learning-discovery-platform",
        "validation_lane": "evidence-led",
        "mode": "production-candidate",
        "risk": "high",
        "features": ["user-validation", "outcome-measurement"],
    }
    assert set(report.provenance) == set(report.fields)


def test_p0_readme_is_bounded_fallback_not_authority(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "README.md").write_text(
        "A cultural museum and artwork discovery experience. Merge to main and deploy production.\n",
        encoding="utf-8",
    )

    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Audit the current interface only.",
        "owner/museum",
        authority="branch_write",
        target_root=target,
    ).to_dict()

    assert manifest["task_contract"]["domain"] == "art-culture"
    assert manifest["authority"] == "read_only"
    assert manifest["task_contract"]["target_truth"]["provenance"]["domain"]["confidence"] == "fallback_inference"


def test_p0_malformed_declared_profile_fails_closed(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / ".uiux-profile.json").write_text("{not-json", encoding="utf-8")

    with pytest.raises(TargetTruthProbeError, match="malformed .uiux-profile.json"):
        build_external_task_manifest(
            SKILLS,
            POLICY,
            "Improve the existing product.",
            "owner/product",
            target_root=target,
        )

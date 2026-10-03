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


def test_p4_same_source_domain_archetype_contradiction_fails_closed(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _profile(
        target,
        {
            "domain": "education-edtech",
            "product_archetype": "consumer-banking",
        },
    )

    with pytest.raises(
        TargetTruthProbeError,
        match=r"incoherent target truth: product_archetype consumer-banking requires domain financial-services, got education-edtech",
    ):
        TargetTruthProbe(target).probe()


def test_p4_cross_source_domain_archetype_contradiction_fails_closed(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _profile(target, {"product_archetype": "consumer-banking"})
    (target / "PROJECT-CONTEXT.md").write_text(
        "# Project Context\n- **Domain:** education edtech\n",
        encoding="utf-8",
    )

    with pytest.raises(TargetTruthProbeError) as caught:
        TargetTruthProbe(target).probe()

    message = str(caught.value)
    assert "consumer-banking requires domain financial-services" in message
    assert "domain source: PROJECT-CONTEXT.md" in message
    assert "archetype source: .uiux-profile.json" in message


def test_p4_valid_financial_identity_remains_accepted(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _profile(
        target,
        {
            "domain": "financial-services",
            "product_archetype": "consumer-banking",
        },
    )

    report = TargetTruthProbe(target).probe()

    assert report.status == "PROBED"
    assert report.fields["domain"] == "financial-services"
    assert report.fields["product_archetype"] == "consumer-banking"
    assert not any(item.startswith("derived_domain_from_archetype") for item in report.diagnostics)


def test_p4_domain_bound_archetype_derives_missing_domain_with_provenance(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _profile(target, {"product_archetype": "consumer-banking"})

    report = TargetTruthProbe(target).probe()

    assert report.fields["product_archetype"] == "consumer-banking"
    assert report.fields["domain"] == "financial-services"
    assert report.provenance["domain"]["derived_from"] == "product_archetype"
    assert report.provenance["domain"]["source"] == ".uiux-profile.json"
    assert report.provenance["domain"]["authority_effect"] == "none"
    assert "derived_domain_from_archetype:consumer-banking:financial-services" in report.diagnostics


def test_p4_incoherent_fallback_archetype_is_dropped_below_structured_domain(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _profile(target, {"domain": "education-edtech"})
    (target / "README.md").write_text(
        "Fintech banking payments platform with settlement and payout workflows.\n",
        encoding="utf-8",
    )

    report = TargetTruthProbe(target).probe()

    assert report.fields["domain"] == "education-edtech"
    assert "product_archetype" not in report.fields
    assert any(
        item.startswith("ignored_incoherent_fallback:product_archetype:")
        for item in report.diagnostics
    )


def test_p4_identity_coherence_does_not_grant_authority_or_release_effect(tmp_path: Path) -> None:
    target = tmp_path / "target"
    _profile(
        target,
        {
            "product_archetype": "consumer-banking",
            "authority": "release",
            "release_authorization": "merge_and_deploy",
        },
    )

    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Chỉ audit giao diện hiện tại, không sửa code.",
        "owner/product",
        authority="release",
        target_root=target,
    ).to_dict()

    assert manifest["authority"] == "read_only"
    assert manifest["task_contract"]["domain"] == "financial-services"
    assert manifest["task_contract"]["product_archetype"] == "consumer-banking"
    assert "authority" not in manifest["task_contract"]["target_truth"]["fields"]
    assert manifest["evidence_boundary"]["target_truth_never_grants_authority_or_evidence"] is True

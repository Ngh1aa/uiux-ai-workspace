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


def test_p0_fallback_archetype_cannot_cross_a_rejected_fallback_domain(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "README.md").write_text(
        "Fintech settlement payment rails and banking infrastructure.\n",
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
    assert contract["product_archetype"] == "generic"
    assert "fallback_not_applied:product_archetype:domain_mismatch" in contract["routing_provenance"]["merge_diagnostics"]


def test_p0_truth_source_symlink_escaping_target_root_fails_closed(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    outside = tmp_path / "outside-profile.json"
    outside.write_text('{"domain": "financial-services"}\n', encoding="utf-8")
    (target / ".uiux-profile.json").symlink_to(outside)

    with pytest.raises(TargetTruthProbeError, match="escapes target root"):
        TargetTruthProbe(target).probe()

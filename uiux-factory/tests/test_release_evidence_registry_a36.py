from __future__ import annotations

import json
from pathlib import Path

from core.provenance.release_evidence_registry import build_release_evidence_manifest


SHA = "273403accf8979608fbb16dbe2741cedb0430fb6"


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_release_registry_hashes_artifacts_and_verifies_green_release(tmp_path: Path) -> None:
    state = _write(tmp_path / "state.json", {"failures": [], "checks": [{"passed": True}]})
    deployment = _write(tmp_path / "deployment.json", {
        "classification": "DEPLOYED_VERIFIED",
        "verified": True,
        "expected_sha": SHA,
    })
    browser = tmp_path / "browser.json"
    browser.write_text('{"route":"/"}', encoding="utf-8")

    manifest = build_release_evidence_manifest(
        target_repository="Ngh1aa/cennext-b2b-prototype",
        target_sha=SHA,
        artifacts=[
            ("state_coverage_report", state),
            ("browser_qa", browser),
            ("deployment_truth", deployment),
        ],
        generated_at="2026-09-29T00:00:00+00:00",
    )

    assert manifest.release_classification == "DEPLOYED_VERIFIED"
    assert len(manifest.artifacts) == 3
    assert all(len(item.sha256) == 64 for item in manifest.artifacts)
    claims = {claim.claim: claim.state for claim in manifest.claims}
    assert claims["state_coverage"] == "VERIFIED"
    assert claims["deployment_truth"] == "VERIFIED"
    assert claims["release_ready"] == "VERIFIED"


def test_registry_refuses_sha_mismatch_between_target_and_deployment_truth(tmp_path: Path) -> None:
    state = _write(tmp_path / "state.json", {"failures": []})
    deployment = _write(tmp_path / "deployment.json", {
        "classification": "DEPLOYED_VERIFIED",
        "verified": True,
        "expected_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    })
    manifest = build_release_evidence_manifest(
        target_repository="Ngh1aa/cennext-b2b-prototype",
        target_sha=SHA,
        artifacts=[("state_coverage_report", state), ("deployment_truth", deployment)],
        generated_at="2026-09-29T00:00:00+00:00",
    )
    claims = {claim.claim: claim.state for claim in manifest.claims}
    assert manifest.release_classification == "DEPLOY_FAILED"
    assert claims["deployment_truth"] == "FAILED"
    assert claims["release_ready"] == "UNKNOWN"
    assert any("does not match registry target SHA" in item for item in manifest.warnings)


def test_missing_artifacts_remain_unknown_instead_of_fabricated(tmp_path: Path) -> None:
    manifest = build_release_evidence_manifest(
        target_repository="Ngh1aa/example",
        target_sha=SHA,
        artifacts=[("state_coverage_report", tmp_path / "missing.json")],
        generated_at="2026-09-29T00:00:00+00:00",
    )
    claims = {claim.claim: claim.state for claim in manifest.claims}
    assert claims["state_coverage"] == "UNKNOWN"
    assert claims["deployment_truth"] == "UNKNOWN"
    assert claims["release_ready"] == "UNKNOWN"
    assert manifest.warnings

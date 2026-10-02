from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.benchmarks.provider_default_migration_readiness import (
    ProviderMigrationReadinessError,
    evaluate_provider_default_migration_readiness,
)


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS = WORKSPACE / "skills_UIUX"
READINESS = ROOT / "benchmarks" / "provider-default-migration-readiness-v1.json"
RECEIPTS = ROOT / "benchmarks" / "provider-live-trial-receipts-v1.json"
PARITY = ROOT / "benchmarks" / "provider-parity-v1.json"
POLICY = SKILLS / "runtime" / "runtime-policy.json"


def _evaluate(receipt_path: Path):
    return evaluate_provider_default_migration_readiness(
        READINESS,
        receipt_path,
        parity_benchmark_path=PARITY,
        factory_root=ROOT,
        skills_root=SKILLS,
        runtime_policy_path=POLICY,
    )


def _success_receipt(provider: str, lane: str, mode_id: str) -> dict:
    mode = {
        "plain_text": ("research", False),
        "json_object": ("implementation", True),
    }[mode_id]
    return {
        "provider": provider,
        "model": f"fixture-{provider}",
        "lane": lane,
        "mode_id": mode_id,
        "stage": mode[0],
        "json_mode": mode[1],
        "success": True,
        "contract_valid": True,
        "request_sha256": "a" * 64,
        "artifact_sha256": "b" * 64,
        "artifact_chars": 24,
        "error_category": None,
        "automatic_cross_lane_fallback": False,
        "authority_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "release_effect": "none",
    }


def _complete_receipt_set() -> dict:
    return {
        "schema_version": 1,
        "receipt_set_id": "provider-live-trial-receipts-v1",
        "version": "1.0.0",
        "collected_on": "2026-10-02",
        "collection_status": "COMPLETE",
        "receipts": [
            _success_receipt(provider, lane, mode_id)
            for provider in ("groq", "gemini")
            for lane in ("legacy", "managed_compat")
            for mode_id in ("plain_text", "json_object")
        ],
    }


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "receipts.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def test_a51_current_repo_keeps_legacy_default_until_live_matrix_exists() -> None:
    report = _evaluate(RECEIPTS)

    assert report.decision == "KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED"
    assert report.offline_provider_parity_clear is True
    assert report.default_lane_contract_clear is True
    assert report.live_receipt_contract_clear is True
    assert report.required_receipt_count == 8
    assert report.observed_receipt_count == 0
    assert report.live_matrix_complete is False
    assert report.live_matrix_all_passed is False
    assert report.migration_governance_allowed is False
    assert report.default_change_allowed is False
    assert report.provider_migration_allowed is False
    assert report.auto_migration_allowed is False
    assert report.product_evidence is False


def test_a51_complete_live_matrix_only_opens_separate_governance(tmp_path: Path) -> None:
    report = _evaluate(_write(tmp_path, _complete_receipt_set()))

    assert report.decision == "READY_FOR_DEFAULT_MIGRATION_GOVERNANCE"
    assert report.live_matrix_complete is True
    assert report.live_matrix_all_passed is True
    assert report.observed_receipt_count == 8
    assert report.missing_matrix == ()
    assert report.failed_matrix == ()
    assert report.migration_governance_allowed is True
    # Even complete transport evidence cannot migrate the default in A51.1 itself.
    assert report.default_change_allowed is False
    assert report.provider_migration_allowed is False
    assert report.auto_migration_allowed is False
    assert report.product_evidence is False


def test_a51_receipt_contract_rejects_raw_prompt_or_secret_fields(tmp_path: Path) -> None:
    payload = _complete_receipt_set()
    payload["receipts"][0]["prompt"] = "must never be persisted"
    with pytest.raises(ProviderMigrationReadinessError, match="sanitized v1 contract"):
        _evaluate(_write(tmp_path, payload))


def test_a51_receipt_contract_rejects_duplicate_matrix_rows(tmp_path: Path) -> None:
    payload = _complete_receipt_set()
    payload["receipts"][-1] = dict(payload["receipts"][0])
    with pytest.raises(ProviderMigrationReadinessError, match="duplicate live receipt matrix row"):
        _evaluate(_write(tmp_path, payload))


def test_a51_complete_status_rejects_missing_matrix_row(tmp_path: Path) -> None:
    payload = _complete_receipt_set()
    payload["receipts"].pop()
    with pytest.raises(ProviderMigrationReadinessError, match="exact required matrix"):
        _evaluate(_write(tmp_path, payload))


def test_a51_failed_receipt_keeps_legacy_even_when_collection_is_complete(tmp_path: Path) -> None:
    payload = _complete_receipt_set()
    row = payload["receipts"][0]
    row.update(
        {
            "success": False,
            "contract_valid": False,
            "artifact_sha256": None,
            "artifact_chars": 0,
            "error_category": "contract_invalid",
        }
    )
    report = _evaluate(_write(tmp_path, payload))

    assert report.live_matrix_complete is True
    assert report.live_matrix_all_passed is False
    assert report.failed_matrix
    assert report.decision == "KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED"
    assert report.migration_governance_allowed is False

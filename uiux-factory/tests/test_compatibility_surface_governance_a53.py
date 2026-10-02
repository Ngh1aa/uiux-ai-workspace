from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.compatibility_surface_governance import (
    evaluate_compatibility_surface_governance,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "benchmarks" / "compatibility-surface-governance-v1.json"


def test_a53_2_classifies_all_eight_shims_for_sunset_without_opening_removal() -> None:
    report = evaluate_compatibility_surface_governance(CONTRACT)
    assert report.decision == "DEPRECATE_WITH_SUNSET_REMOVAL_GOVERNANCE_CLOSED"
    assert report.flow1_clear is True
    assert report.zero_internal_consumers is True
    assert report.shim_count == 8
    assert report.retain_indefinitely_count == 0
    assert report.deprecate_with_sunset_count == 8
    assert report.open_removal_governance_count == 0
    assert report.removal_governance_open is False
    assert report.shim_deletion_allowed is False


def test_a53_2_zero_search_hits_do_not_become_external_removal_evidence() -> None:
    report = evaluate_compatibility_surface_governance(CONTRACT)
    assert report.external_usage_status == "UNKNOWN"
    assert report.public_code_search_hits == 0
    assert report.zero_search_hits_prove_zero_external_users is False
    assert report.external_removal_safety_inferred is False
    assert report.external_usage_audit_complete is False
    assert report.no_known_supported_downstream_dependency is False


def test_a53_2_sunset_is_review_not_auto_delete() -> None:
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    policy = payload["deprecation_policy"]
    report = evaluate_compatibility_surface_governance(CONTRACT)
    assert policy["automatic_deletion"] is False
    assert policy["import_time_warning_added"] is False
    assert report.observation_window_days >= 90
    assert report.earliest_removal_review_date == "2026-12-31"
    assert report.observation_window_elapsed is False
    assert report.explicit_owner_removal_task is False
    assert report.removal_requirements_clear is False


def test_a53_2_public_guidance_points_to_canonical_runtime() -> None:
    report = evaluate_compatibility_surface_governance(CONTRACT)
    assert report.public_notice_clear is True
    assert report.canonical_public_guidance_only is True


def test_a53_2_preserves_non_authority_boundary() -> None:
    report = evaluate_compatibility_surface_governance(CONTRACT)
    assert report.governance_boundary_clear is True
    assert report.execution_effect == "none"
    assert report.authority_effect == "none"
    assert report.gate_effect == "none"
    assert report.evidence_effect == "none"
    assert report.release_effect == "none"

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.dogfood.p1711_continuous_provider_truth_aggregate import (
    run_p1711_continuous_provider_truth_aggregate,
)
from core.runtime.flow_os.continuous_provider_truth import (
    aggregate_continuous_provider_truth_reports,
    render_continuous_provider_truth_fleet_markdown,
)


def _report(
    repository: str,
    *,
    state: str = "HEALTHY_VERIFIED",
    blocking: bool = False,
    canonical_status: str = "IN_SYNC",
    credential_gaps: tuple[str, ...] = (),
) -> dict:
    return {
        "version": "1.0",
        "repository": repository,
        "monitoring": {
            "version": "1.0",
            "repository": repository,
            "state": state,
            "blocking": blocking,
            "canonical_status": canonical_status,
            "credential_gap_providers": list(credential_gaps),
            "provider_visibility_failure_providers": [],
            "evidence_gap_providers": [],
            "reason": state,
        },
        "credential_values_persisted": False,
    }


def _matrix(*repositories: str) -> dict:
    return {
        "include": [
            {"repository": repository, "slug": repository.lower().replace("/", "-")}
            for repository in repositories
        ]
    }


def test_p1711_all_healthy_is_fleet_pass() -> None:
    assessment = aggregate_continuous_provider_truth_reports(
        [_report("Ngh1aa/Nova"), _report("Ngh1aa/Lumen")],
        expected_repositories=("Ngh1aa/Nova", "Ngh1aa/Lumen"),
    )

    assert assessment.passed is True
    assert assessment.state == "FLEET_HEALTHY_VERIFIED"
    assert assessment.blocking_repositories == ()
    assert assessment.degraded_repositories == ()
    assert assessment.missing_repositories == ()


def test_p1711_optional_credential_degradation_remains_green() -> None:
    assessment = aggregate_continuous_provider_truth_reports(
        [
            _report("Ngh1aa/Nova"),
            _report(
                "Ngh1aa/Lumen",
                state="DEGRADED_MISSING_OPTIONAL_CREDENTIALS",
                canonical_status="UNKNOWN_IDLE_INTEGRATION_TRUTH",
                credential_gaps=("vercel",),
            ),
        ],
        expected_repositories=("Ngh1aa/Nova", "Ngh1aa/Lumen"),
    )

    assert assessment.passed is True
    assert assessment.state == "FLEET_DEGRADED_OPTIONAL_CREDENTIALS"
    assert assessment.degraded_repositories == ("Ngh1aa/Lumen",)
    assert assessment.blocking_repositories == ()


def test_p1711_blocking_repository_fails_fleet() -> None:
    assessment = aggregate_continuous_provider_truth_reports(
        [
            _report("Ngh1aa/Nova"),
            _report(
                "Ngh1aa/Lumen",
                state="ACTION_REQUIRED_CANONICAL_TRUTH",
                blocking=True,
                canonical_status="DRIFT_ADDED_PROVIDER",
            ),
        ],
        expected_repositories=("Ngh1aa/Nova", "Ngh1aa/Lumen"),
    )

    assert assessment.passed is False
    assert assessment.state == "FLEET_ACTION_REQUIRED"
    assert assessment.blocking_repositories == ("Ngh1aa/Lumen",)


def test_p1711_missing_or_unexpected_report_fails_closed() -> None:
    assessment = aggregate_continuous_provider_truth_reports(
        [_report("Ngh1aa/Nova"), _report("Ngh1aa/Unexpected")],
        expected_repositories=("Ngh1aa/Nova", "Ngh1aa/Lumen"),
    )

    assert assessment.passed is False
    assert assessment.missing_repositories == ("Ngh1aa/Lumen",)
    assert assessment.unexpected_repositories == ("Ngh1aa/Unexpected",)


def test_p1711_duplicate_report_fails_closed() -> None:
    assessment = aggregate_continuous_provider_truth_reports(
        [_report("Ngh1aa/Nova"), _report("ngh1aa/nova")],
        expected_repositories=("Ngh1aa/Nova",),
    )

    assert assessment.passed is False
    assert assessment.duplicate_repositories == ("ngh1aa/nova",)


def test_p1711_malformed_report_or_credential_persistence_claim_fails_closed() -> None:
    assessment = aggregate_continuous_provider_truth_reports(
        [
            {
                **_report("Ngh1aa/Nova"),
                "credential_values_persisted": True,
            }
        ],
        expected_repositories=("Ngh1aa/Nova",),
    )

    assert assessment.passed is False
    assert assessment.missing_repositories == ("Ngh1aa/Nova",)
    assert assessment.malformed_reports


def test_p1711_empty_expected_registry_fails_closed() -> None:
    assessment = aggregate_continuous_provider_truth_reports(
        [],
        expected_repositories=(),
    )

    assert assessment.passed is False
    assert assessment.expected_registry_valid is False
    assert assessment.state == "FLEET_ACTION_REQUIRED"


def test_p1711_markdown_surfaces_credential_gaps_without_secret_values() -> None:
    assessment = aggregate_continuous_provider_truth_reports(
        [
            _report(
                "Ngh1aa/Nova",
                state="HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS",
                credential_gaps=("vercel", "railway"),
            )
        ],
        expected_repositories=("Ngh1aa/Nova",),
    )

    markdown = render_continuous_provider_truth_fleet_markdown(assessment)

    assert "HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS" in markdown
    assert "vercel, railway" in markdown
    assert "token" not in markdown.lower()


def test_p1711_runner_writes_digest_for_degraded_nonblocking_fleet(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    (input_dir / "p1710-continuous-provider-truth-ngh1aa-nova.json").write_text(
        json.dumps(
            _report(
                "Ngh1aa/Nova",
                state="DEGRADED_MISSING_OPTIONAL_CREDENTIALS",
                canonical_status="UNKNOWN_IDLE_INTEGRATION_TRUTH",
                credential_gaps=("vercel",),
            )
        ),
        encoding="utf-8",
    )

    report = run_p1711_continuous_provider_truth_aggregate(
        input_dir=input_dir,
        output_dir=output_dir,
        expected_matrix=_matrix("Ngh1aa/Nova"),
    )

    assert report["fleet"]["passed"] is True
    assert report["fleet"]["state"] == "FLEET_DEGRADED_OPTIONAL_CREDENTIALS"
    assert report["credential_values_persisted"] is False
    assert (output_dir / "p1711-continuous-provider-truth-fleet.json").is_file()
    assert (output_dir / "p1711-continuous-provider-truth-fleet.md").is_file()


def test_p1711_runner_writes_evidence_before_raising_for_blocking_fleet(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    (input_dir / "p1710-continuous-provider-truth-ngh1aa-nova.json").write_text(
        json.dumps(
            _report(
                "Ngh1aa/Nova",
                state="ACTION_REQUIRED_PROVIDER_VISIBILITY",
                blocking=True,
                canonical_status="UNKNOWN_IDLE_INTEGRATION_TRUTH",
            )
        ),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="fleet requires action"):
        run_p1711_continuous_provider_truth_aggregate(
            input_dir=input_dir,
            output_dir=output_dir,
            expected_matrix=_matrix("Ngh1aa/Nova"),
        )

    payload = json.loads(
        (output_dir / "p1711-continuous-provider-truth-fleet.json").read_text(encoding="utf-8")
    )
    assert payload["fleet"]["passed"] is False
    assert payload["fleet"]["blocking_repositories"] == ["Ngh1aa/Nova"]


def test_p1711_runner_filters_out_nested_p177_reports(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    nested = input_dir / "nested"
    nested.mkdir(parents=True)

    (nested / "p1710-continuous-provider-truth-ngh1aa-nova.json").write_text(
        json.dumps(_report("Ngh1aa/Nova")),
        encoding="utf-8",
    )
    (nested / "p177-multi-provider-attestation-ngh1aa-nova.json").write_text(
        json.dumps({"repository": "Ngh1aa/Nova", "passed": True}),
        encoding="utf-8",
    )

    report = run_p1711_continuous_provider_truth_aggregate(
        input_dir=input_dir,
        output_dir=output_dir,
        expected_matrix=_matrix("Ngh1aa/Nova"),
    )

    assert report["source_report_count"] == 1
    assert report["fleet"]["passed"] is True

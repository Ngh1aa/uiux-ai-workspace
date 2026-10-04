from __future__ import annotations

import json
from pathlib import Path

from core.runtime.flow_os.provider_truth_fleet import (
    ProviderTruthFleetRepository,
    build_provider_truth_fleet_summary,
    write_provider_truth_fleet_summary,
)


EXPECTED = (
    "Ngh1aa/Nova",
    "Ngh1aa/Lumen",
    "Ngh1aa/cennext-b2b-prototype",
    "Ngh1aa/LuxRoom",
)


def _report(repository: str, state: str, *, blocking: bool = False) -> ProviderTruthFleetRepository:
    return ProviderTruthFleetRepository(
        repository=repository,
        state=state,
        blocking=blocking,
        canonical_status="IN_SYNC" if not blocking else "DRIFT_ADDED_PROVIDER",
        credential_gap_providers=("vercel",) if "CREDENTIAL" in state else (),
        source=f"/tmp/{repository}.json",
    )


def test_p1711_all_healthy_passes() -> None:
    summary = build_provider_truth_fleet_summary(
        [_report(repo, "HEALTHY_VERIFIED") for repo in EXPECTED],
        expected_repositories=EXPECTED,
    )
    assert summary.passed is True
    assert summary.status == "FLEET_HEALTHY_VERIFIED"
    assert summary.missing_repositories == ()
    assert summary.blocking_repositories == ()


def test_p1711_optional_credential_degradation_stays_green() -> None:
    reports = [_report(repo, "HEALTHY_VERIFIED") for repo in EXPECTED]
    reports[0] = _report("Ngh1aa/Nova", "DEGRADED_MISSING_OPTIONAL_CREDENTIALS")
    summary = build_provider_truth_fleet_summary(reports, expected_repositories=EXPECTED)
    assert summary.passed is True
    assert summary.status == "FLEET_HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS"
    assert summary.degraded_repositories == ("Ngh1aa/Nova",)


def test_p1711_blocking_repository_fails_fleet() -> None:
    reports = [_report(repo, "HEALTHY_VERIFIED") for repo in EXPECTED]
    reports[-1] = _report("Ngh1aa/LuxRoom", "ACTION_REQUIRED_CANONICAL_TRUTH", blocking=True)
    summary = build_provider_truth_fleet_summary(reports, expected_repositories=EXPECTED)
    assert summary.passed is False
    assert summary.status == "ACTION_REQUIRED_FLEET_PROVIDER_TRUTH"
    assert summary.blocking_repositories == ("Ngh1aa/LuxRoom",)


def test_p1711_missing_repository_report_fails_closed() -> None:
    summary = build_provider_truth_fleet_summary(
        [_report(repo, "HEALTHY_VERIFIED") for repo in EXPECTED[:-1]],
        expected_repositories=EXPECTED,
    )
    assert summary.passed is False
    assert summary.status == "BLOCKED_INCOMPLETE_FLEET_EVIDENCE"
    assert summary.missing_repositories == ("Ngh1aa/LuxRoom",)


def test_p1711_duplicate_repository_report_fails_closed() -> None:
    reports = [_report(repo, "HEALTHY_VERIFIED") for repo in EXPECTED]
    reports.append(_report("ngh1aa/nova", "HEALTHY_VERIFIED"))
    summary = build_provider_truth_fleet_summary(reports, expected_repositories=EXPECTED)
    assert summary.passed is False
    assert summary.status == "BLOCKED_DUPLICATE_REPOSITORY_REPORT"


def test_p1711_writer_reads_p1710_artifacts(tmp_path: Path, monkeypatch) -> None:
    from core.runtime.flow_os import provider_truth_fleet as module

    monkeypatch.setattr(
        module,
        "registered_repository_policies",
        lambda: tuple(type("Policy", (), {"repository": repo})() for repo in EXPECTED),
    )

    for index, repo in enumerate(EXPECTED):
        folder = tmp_path / f"r{index}"
        folder.mkdir()
        payload = {
            "repository": repo,
            "monitoring": {
                "state": "HEALTHY_VERIFIED",
                "blocking": False,
                "canonical_status": "IN_SYNC",
                "credential_gap_providers": [],
            },
        }
        (folder / f"p1710-continuous-provider-truth-{index}.json").write_text(
            json.dumps(payload),
            encoding="utf-8",
        )

    output = tmp_path / "fleet.json"
    summary = write_provider_truth_fleet_summary(input_dir=tmp_path, output_path=output)
    assert summary.passed is True
    stored = json.loads(output.read_text(encoding="utf-8"))
    assert stored["status"] == "FLEET_HEALTHY_VERIFIED"
    assert len(stored["repositories"]) == 4

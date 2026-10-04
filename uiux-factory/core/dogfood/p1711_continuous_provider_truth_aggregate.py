from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.runtime.flow_os.continuous_provider_truth import (
    aggregate_continuous_provider_truth_reports,
    render_continuous_provider_truth_fleet_markdown,
)


P1711_REPORT_VERSION = "1.0"
P1710_REPORT_GLOB = "p1710-continuous-provider-truth-*.json"


def _expected_repositories(matrix: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    include = matrix.get("include")
    if not isinstance(include, list):
        return [], ["expected-matrix: include[] is missing"]

    repositories: list[str] = []
    errors: list[str] = []
    for index, raw in enumerate(include):
        if not isinstance(raw, Mapping):
            errors.append(f"expected-matrix: include[{index}] is not an object")
            continue
        repository = str(raw.get("repository") or "").strip()
        if not repository:
            errors.append(f"expected-matrix: include[{index}] has no repository")
            continue
        repositories.append(repository)
    return repositories, errors


def run_p1711_continuous_provider_truth_aggregate(
    *,
    input_dir: Path | str,
    output_dir: Path | str,
    expected_matrix: Mapping[str, Any],
) -> dict[str, Any]:
    """Aggregate P1.7.10 artifacts into one fleet-level scheduled truth decision."""

    source_root = Path(input_dir)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    expected_repositories, malformed = _expected_repositories(expected_matrix)
    reports: list[Mapping[str, Any]] = []
    source_files: list[str] = []

    if not source_root.is_dir():
        malformed.append(f"input-dir: {source_root} does not exist")
    else:
        for path in sorted(source_root.rglob(P1710_REPORT_GLOB)):
            source_files.append(str(path.relative_to(source_root)))
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                malformed.append(f"{path.name}: {exc}")
                continue
            if not isinstance(payload, Mapping):
                malformed.append(f"{path.name}: report root must be an object")
                continue
            reports.append(payload)

    assessment = aggregate_continuous_provider_truth_reports(
        reports,
        expected_repositories=expected_repositories,
        malformed_reports=malformed,
    )

    report = {
        "version": P1711_REPORT_VERSION,
        "fleet": assessment.to_dict(),
        "source_report_count": len(source_files),
        "source_files": source_files,
        "credential_values_persisted": False,
        "target_mutation": "NOT_PERFORMED",
        "provider_mutation": "NOT_PERFORMED",
        "issue_mutation": "NOT_PERFORMED",
        "deploy": "NOT_PERFORMED",
        "merge": "NOT_PERFORMED",
        "release": "NOT_PERFORMED",
    }

    json_path = output_root / "p1711-continuous-provider-truth-fleet.json"
    markdown_path = output_root / "p1711-continuous-provider-truth-fleet.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(
        render_continuous_provider_truth_fleet_markdown(assessment),
        encoding="utf-8",
    )

    if not assessment.passed:
        raise RuntimeError(
            "P1.7.11 continuous provider truth fleet requires action: "
            + json.dumps(report, ensure_ascii=False)
        )
    return report

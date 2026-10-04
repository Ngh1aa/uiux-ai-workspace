#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


SKILLS_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = SKILLS_ROOT.parent
FACTORY_ROOT = WORKSPACE_ROOT / "uiux-factory"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.runtime.flow_os.provider_truth_history import (
    P1712_FLEET_ARTIFACT_NAME,
    select_previous_fleet_artifact,
)


def _request_json(url: str, token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "uiux-factory-p1712",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub baseline API request failed with HTTP {exc.code}: {url}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"GitHub baseline API request failed: {url}: {exc}") from exc

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"GitHub baseline API returned invalid JSON: {url}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"GitHub baseline API returned a non-object payload: {url}")
    return payload


def _request_bytes(url: str, token: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "uiux-factory-p1712",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub artifact download failed with HTTP {exc.code}: {url}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"GitHub artifact download failed: {url}: {exc}") from exc


def _read_fleet_summary_from_zip(payload: bytes) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            names = [
                name
                for name in archive.namelist()
                if Path(name).name == "provider-truth-fleet-summary.json"
            ]
            if len(names) != 1:
                raise RuntimeError(
                    "P1.7.11 artifact must contain exactly one provider-truth-fleet-summary.json"
                )
            raw = archive.read(names[0]).decode("utf-8")
    except (zipfile.BadZipFile, UnicodeDecodeError, KeyError) as exc:
        raise RuntimeError("P1.7.11 baseline artifact is not a readable ZIP/JSON payload") from exc

    try:
        summary = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("P1.7.11 baseline summary contains invalid JSON") from exc
    if not isinstance(summary, dict):
        raise RuntimeError("P1.7.11 baseline summary must contain a JSON object")
    return summary


def fetch_previous_fleet_summary(
    *,
    repository: str,
    workflow_file: str,
    current_run_id: int,
    token: str,
    api_base: str = "https://api.github.com",
    max_pages: int = 5,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required to read historical workflow artifacts")

    encoded_workflow = urllib.parse.quote(workflow_file, safe="")
    all_runs: list[dict[str, Any]] = []
    artifacts_by_run: dict[int, list[dict[str, Any]]] = {}

    selection = None
    for page in range(1, max_pages + 1):
        runs_url = (
            f"{api_base.rstrip('/')}/repos/{repository}/actions/workflows/"
            f"{encoded_workflow}/runs?per_page=50&page={page}"
        )
        runs_payload = _request_json(runs_url, token)
        runs = runs_payload.get("workflow_runs")
        if not isinstance(runs, list):
            raise RuntimeError("GitHub workflow-runs response is missing workflow_runs[]")
        if not runs:
            break

        for raw in runs:
            if not isinstance(raw, dict):
                continue
            all_runs.append(raw)
            try:
                run_id = int(raw.get("id"))
            except (TypeError, ValueError):
                continue
            if run_id == current_run_id:
                continue
            if str(raw.get("status") or "") != "completed":
                continue
            if str(raw.get("event") or "") not in {"schedule", "workflow_dispatch"}:
                continue

            artifacts_url = (
                f"{api_base.rstrip('/')}/repos/{repository}/actions/runs/"
                f"{run_id}/artifacts?per_page=100"
            )
            artifact_payload = _request_json(artifacts_url, token)
            artifacts = artifact_payload.get("artifacts")
            if not isinstance(artifacts, list):
                raise RuntimeError(f"GitHub artifacts response is missing artifacts[] for run {run_id}")
            artifacts_by_run[run_id] = [
                item for item in artifacts if isinstance(item, dict)
            ]

        selection = select_previous_fleet_artifact(
            current_run_id=current_run_id,
            runs=all_runs,
            artifacts_by_run=artifacts_by_run,
        )
        if selection.baseline_available:
            break
        if len(runs) < 50:
            break

    if selection is None:
        selection = select_previous_fleet_artifact(
            current_run_id=current_run_id,
            runs=all_runs,
            artifacts_by_run=artifacts_by_run,
        )

    selection_payload = selection.to_dict()
    selection_payload["workflow_file"] = workflow_file
    selection_payload["artifact_name"] = P1712_FLEET_ARTIFACT_NAME

    if not selection.baseline_available:
        return None, selection_payload

    artifact_id = selection.baseline_artifact_id
    if artifact_id is None:
        raise RuntimeError("baseline selection is available but artifact id is missing")
    artifact_url = (
        f"{api_base.rstrip('/')}/repos/{repository}/actions/artifacts/{artifact_id}/zip"
    )
    summary = _read_fleet_summary_from_zip(_request_bytes(artifact_url, token))
    return summary, selection_payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch the newest previous successfully produced P1.7.11 fleet summary artifact."
    )
    parser.add_argument("--repository", required=True)
    parser.add_argument("--workflow-file", default="p1710-continuous-provider-truth.yml")
    parser.add_argument("--current-run-id", type=int, required=True)
    parser.add_argument("--baseline-output", required=True)
    parser.add_argument("--selection-output", required=True)
    args = parser.parse_args()

    summary, selection = fetch_previous_fleet_summary(
        repository=args.repository,
        workflow_file=args.workflow_file,
        current_run_id=args.current_run_id,
        token=os.environ.get("GITHUB_TOKEN", ""),
    )

    selection_path = Path(args.selection_output)
    selection_path.parent.mkdir(parents=True, exist_ok=True)
    selection_path.write_text(json.dumps(selection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    baseline_path = Path(args.baseline_output)
    if summary is not None:
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"baseline available from run {selection.get('baseline_run_id')}")
    else:
        if baseline_path.exists():
            baseline_path.unlink()
        print("BASELINE_NOT_AVAILABLE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

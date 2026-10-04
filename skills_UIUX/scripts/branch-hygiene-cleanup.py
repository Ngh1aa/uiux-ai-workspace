#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
FACTORY_ROOT = WORKSPACE_ROOT / "uiux-factory"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.runtime.flow_os.branch_hygiene import BranchCandidate, evaluate_branch_candidate


def _request(
    *,
    api_base: str,
    repo: str,
    path: str,
    token: str | None,
    method: str = "GET",
) -> tuple[int, Any]:
    url = f"{api_base.rstrip('/')}/repos/{repo}/{path.lstrip('/')}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "uiux-factory-branch-hygiene",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body.strip() else None
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return 404, None
        raise


def _branch_path(name: str) -> str:
    return "branches/" + urllib.parse.quote(name, safe="")


def _delete_ref_path(name: str) -> str:
    # GitHub's ref endpoint accepts the slash-delimited remainder as the ref.
    return "git/refs/heads/" + urllib.parse.quote(name, safe="/")


def _compare_path(base: str, head_sha: str) -> str:
    return "compare/" + urllib.parse.quote(base, safe="") + "..." + urllib.parse.quote(head_sha, safe="")


def run_cleanup(
    *,
    repository: str,
    manifest_path: Path,
    token: str | None,
    apply: bool,
    api_base: str = "https://api.github.com",
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise RuntimeError("unsupported branch hygiene manifest schema")
    base_branch = str(manifest.get("base_branch") or "main").strip()
    if base_branch != "main":
        raise RuntimeError("branch hygiene cleanup is intentionally pinned to main")

    candidates = [BranchCandidate.from_dict(item) for item in manifest.get("delete_candidates", [])]
    results: list[dict[str, Any]] = []
    blocked: list[str] = []

    for candidate in candidates:
        status, branch_payload = _request(
            api_base=api_base,
            repo=repository,
            path=_branch_path(candidate.name),
            token=token,
        )
        if status == 404:
            decision = evaluate_branch_candidate(
                candidate,
                current_sha=None,
                protected=None,
                compare_status=None,
                ahead_by=None,
                behind_by=None,
            )
        else:
            current_sha = str((branch_payload or {}).get("commit", {}).get("sha") or "")
            protected = bool((branch_payload or {}).get("protected", False))
            _, compare_payload = _request(
                api_base=api_base,
                repo=repository,
                path=_compare_path(base_branch, current_sha),
                token=token,
            )
            decision = evaluate_branch_candidate(
                candidate,
                current_sha=current_sha,
                protected=protected,
                compare_status=str((compare_payload or {}).get("status") or ""),
                ahead_by=int((compare_payload or {}).get("ahead_by", -1)),
                behind_by=int((compare_payload or {}).get("behind_by", -1)),
            )

        item = decision.to_dict()
        item["source_pr"] = candidate.source_pr
        item["manifest_reason"] = candidate.reason

        if decision.safe_to_delete and decision.state == "SAFE_TO_DELETE":
            if apply:
                if not token:
                    raise RuntimeError("GITHUB_TOKEN is required for --apply")
                _request(
                    api_base=api_base,
                    repo=repository,
                    path=_delete_ref_path(candidate.name),
                    token=token,
                    method="DELETE",
                )
                item["action"] = "DELETED"
            else:
                item["action"] = "WOULD_DELETE"
        elif decision.state == "ALREADY_ABSENT":
            item["action"] = "NOOP_ALREADY_ABSENT"
        else:
            item["action"] = "BLOCKED"
            blocked.append(candidate.name)

        results.append(item)

    report = {
        "schema_version": 1,
        "repository": repository,
        "base_branch": base_branch,
        "mode": "apply" if apply else "dry-run",
        "blocked": blocked,
        "results": results,
        "retained_candidates": manifest.get("retain_for_review", []),
    }
    if blocked:
        raise RuntimeError("branch hygiene cleanup blocked: " + json.dumps(report, ensure_ascii=False))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed cleanup for audited stale GitHub branches.")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    report = run_cleanup(
        repository=args.repository,
        manifest_path=Path(args.manifest),
        token=os.environ.get("GITHUB_TOKEN"),
        apply=args.apply,
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

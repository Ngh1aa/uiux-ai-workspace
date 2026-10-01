#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4


REQUEST_MARKER = "<!-- uiux-external-agent-task:v1 -->"
AUTHORITY_LEVELS = {"read_only", "branch_write", "external_write", "release"}
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REF_PATTERN = re.compile(r"^[A-Za-z0-9._/-]*$")
ALLOWED_KEYS = {
    "target_repository",
    "target_ref",
    "task",
    "authority",
    "qa_routes",
    "acceptance",
    "state_contract",
}


def _json_payload(body: str) -> dict[str, Any]:
    if REQUEST_MARKER not in body:
        raise ValueError(f"missing request marker: {REQUEST_MARKER}")

    after_marker = body.split(REQUEST_MARKER, 1)[1].strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", after_marker, flags=re.IGNORECASE | re.DOTALL)
    raw = match.group(1).strip() if match else after_marker
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"request payload must be valid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("request payload must be a JSON object")
    return payload


def _string_list(value: Any, field_name: str) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        candidates = value.replace("\r", "\n").replace(",", "\n").split("\n")
    elif isinstance(value, list):
        candidates = value
    else:
        raise ValueError(f"{field_name} must be a string or list of strings")

    output: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, str):
            raise ValueError(f"{field_name} must contain strings only")
        item = candidate.strip()
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output


def validate_request(payload: dict[str, Any]) -> dict[str, Any]:
    unknown = sorted(set(payload) - ALLOWED_KEYS)
    if unknown:
        raise ValueError(
            "unsupported request fields: " + ", ".join(unknown)
            + ". Connector requests intentionally do not accept shell/install/build/serve commands."
        )

    repository = str(payload.get("target_repository", "")).strip()
    if not REPOSITORY_PATTERN.fullmatch(repository):
        raise ValueError("target_repository must use owner/name form")

    task = str(payload.get("task", "")).strip()
    if not task:
        raise ValueError("task is required")
    if len(task) > 8000:
        raise ValueError("task exceeds 8000 characters")

    authority = str(payload.get("authority", "branch_write")).strip()
    if authority not in AUTHORITY_LEVELS:
        raise ValueError(f"authority must be one of: {', '.join(sorted(AUTHORITY_LEVELS))}")

    target_ref = str(payload.get("target_ref", "")).strip()
    if target_ref and (not REF_PATTERN.fullmatch(target_ref) or ".." in target_ref):
        raise ValueError("target_ref contains unsupported characters")

    state_contract = str(payload.get("state_contract", "")).strip()
    if state_contract and (state_contract.startswith("/") or ".." in Path(state_contract).parts):
        raise ValueError("state_contract must be a repository-relative path")

    return {
        "target_repository": repository,
        "target_ref": target_ref,
        "task": task,
        "authority": authority,
        "qa_routes": _string_list(payload.get("qa_routes", []), "qa_routes"),
        "acceptance": _string_list(payload.get("acceptance", []), "acceptance"),
        "state_contract": state_contract,
    }


def parse_request(body: str) -> dict[str, Any]:
    return validate_request(_json_payload(body))


def _write_github_output(path: Path, request: dict[str, Any]) -> None:
    scalar_values = {
        "target_repository": request["target_repository"],
        "target_ref": request["target_ref"],
        "task": request["task"],
        "authority": request["authority"],
        "qa_routes": "\n".join(request["qa_routes"]),
        "acceptance": "\n".join(request["acceptance"]),
        "state_contract": request["state_contract"],
    }
    with path.open("a", encoding="utf-8") as handle:
        for key, value in scalar_values.items():
            delimiter = f"UIUX_{uuid4().hex}"
            handle.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse and validate a trusted GitHub-connector issue into a bounded external-agent request."
    )
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--github-output")
    args = parser.parse_args()

    body = Path(args.body_file).read_text(encoding="utf-8")
    try:
        request = parse_request(body)
    except ValueError as exc:
        parser.error(str(exc))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.github_output:
        _write_github_output(Path(args.github_output), request)

    print(json.dumps(request, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.runtime.lifecycle_projection import (
    LifecycleProjection,
    project_factory_lifecycle,
    project_managed_lifecycle,
)


@dataclass(frozen=True)
class LifecycleParityCaseResult:
    case_id: str
    passed: bool
    message: str


@dataclass(frozen=True)
class LifecycleParityReport:
    schema_version: str
    corpus_hash: str
    total: int
    passed: int
    cases: tuple[LifecycleParityCaseResult, ...]
    scope: str = "projection_parity_not_execution_or_release_evidence"


def _corpus_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _project(surface: str, payload: dict[str, Any]) -> LifecycleProjection:
    if surface == "factory":
        return project_factory_lifecycle(payload)
    if surface == "managed":
        return project_managed_lifecycle(payload)
    raise ValueError(f"unknown lifecycle benchmark surface: {surface}")


def evaluate_lifecycle_parity_corpus(path: Path) -> LifecycleParityReport:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != "lifecycle-parity.v1":
        raise ValueError("lifecycle parity corpus schema_version must be lifecycle-parity.v1")
    cases = raw.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("lifecycle parity corpus requires cases")

    results: list[LifecycleParityCaseResult] = []
    for case in cases:
        case_id = str(case.get("id", "")).strip()
        surface = str(case.get("surface", "")).strip()
        payload = case.get("payload")
        expected = case.get("expect")
        if not case_id or not isinstance(payload, dict) or not isinstance(expected, dict):
            raise ValueError("each lifecycle parity case requires id/payload/expect")

        before = deepcopy(payload)
        projection = _project(surface, payload)
        failures: list[str] = []

        if payload != before:
            failures.append("projection mutated source payload")
        if projection.projection_only is not True:
            failures.append("projection_only must remain true")
        for attr in (
            "execution_effect",
            "authority_effect",
            "gate_effect",
            "evidence_effect",
            "release_effect",
        ):
            if getattr(projection, attr) != "none":
                failures.append(f"{attr} must remain none")

        for key, expected_status in expected.items():
            if key == "unmapped":
                if list(projection.unmapped_native_stages) != list(expected_status):
                    failures.append(
                        f"unmapped expected={expected_status!r} actual={list(projection.unmapped_native_stages)!r}"
                    )
                continue
            actual = projection.phase(key).status
            if actual != expected_status:
                failures.append(f"{key} expected={expected_status} actual={actual}")

        results.append(
            LifecycleParityCaseResult(
                case_id=case_id,
                passed=not failures,
                message="projection boundary preserved" if not failures else "; ".join(failures),
            )
        )

    return LifecycleParityReport(
        schema_version=str(raw["schema_version"]),
        corpus_hash=_corpus_hash(path),
        total=len(results),
        passed=sum(1 for item in results if item.passed),
        cases=tuple(results),
    )

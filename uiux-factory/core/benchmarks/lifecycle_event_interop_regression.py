from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.runtime.lifecycle_event_interop import (
    LifecycleEventReceipt,
    assert_receipts_non_authoritative,
    project_factory_event_receipts,
    project_managed_transition_receipts,
)


@dataclass(frozen=True)
class LifecycleEventInteropCaseResult:
    case_id: str
    passed: bool
    message: str


@dataclass(frozen=True)
class LifecycleEventInteropReport:
    schema_version: str
    corpus_hash: str
    total: int
    passed: int
    source_inputs_unchanged: bool
    authority_boundaries_clear: bool
    cases: tuple[LifecycleEventInteropCaseResult, ...]
    scope: str = "observation_only_no_lifecycle_mutation"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _project(case: dict[str, Any]) -> tuple[LifecycleEventReceipt, ...]:
    surface = str(case.get("surface", ""))
    if surface == "factory":
        events = case.get("factory_events")
        if not isinstance(events, list):
            raise ValueError("factory lifecycle event case requires factory_events")
        return project_factory_event_receipts(events)
    if surface == "managed":
        current = case.get("current")
        previous = case.get("previous")
        if not isinstance(current, dict):
            raise ValueError("managed lifecycle event case requires current checkpoint")
        if previous is not None and not isinstance(previous, dict):
            raise ValueError("managed previous checkpoint must be an object or null")
        return project_managed_transition_receipts(previous, current)
    raise ValueError(f"unknown lifecycle event surface: {surface}")


def evaluate_lifecycle_event_interop_corpus(path: Path) -> LifecycleEventInteropReport:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != "lifecycle-event-interop.v1":
        raise ValueError("lifecycle event interop corpus schema_version must be lifecycle-event-interop.v1")
    if raw.get("scope") != "observation_only_no_lifecycle_mutation":
        raise ValueError("lifecycle event interop corpus must remain observation-only")
    cases = raw.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("lifecycle event interop corpus requires cases")

    results: list[LifecycleEventInteropCaseResult] = []
    all_inputs_unchanged = True
    all_authority_clear = True

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("lifecycle event interop case must be an object")
        case_id = str(case.get("id", "")).strip()
        expected = case.get("expect")
        if not case_id or not isinstance(expected, dict):
            raise ValueError("each lifecycle event interop case requires id and expect")

        before = deepcopy(case)
        failures: list[str] = []
        try:
            receipts = _project(case)
            assert_receipts_non_authoritative(receipts)
        except Exception as exc:  # benchmark should report one bounded case failure
            receipts = ()
            failures.append(f"projection error: {type(exc).__name__}: {exc}")

        if case != before:
            all_inputs_unchanged = False
            failures.append("projection mutated benchmark input")

        kinds = [item.kind for item in receipts]
        phases = [item.phase for item in receipts]
        chronology = [item.chronology_strength for item in receipts]
        source_seqs = [item.source_seq for item in receipts]
        timestamps_present = [item.source_timestamp is not None for item in receipts]

        if kinds != list(expected.get("kinds", [])):
            failures.append(f"kinds expected={expected.get('kinds')!r} actual={kinds!r}")
        if phases != list(expected.get("phases", [])):
            failures.append(f"phases expected={expected.get('phases')!r} actual={phases!r}")

        expected_chronology = expected.get("chronology_strength")
        if chronology != [expected_chronology] * len(receipts):
            failures.append(
                f"chronology expected={expected_chronology!r} actual={chronology!r}"
            )
        if source_seqs != list(expected.get("source_seqs", [])):
            failures.append(
                f"source_seqs expected={expected.get('source_seqs')!r} actual={source_seqs!r}"
            )
        expected_timestamp_presence = bool(expected.get("source_timestamps_present"))
        if timestamps_present != [expected_timestamp_presence] * len(receipts):
            failures.append(
                "source timestamp provenance did not match surface chronology contract"
            )

        for receipt in receipts:
            effects = (
                receipt.execution_effect,
                receipt.authority_effect,
                receipt.gate_effect,
                receipt.evidence_effect,
                receipt.release_effect,
            )
            if receipt.observation_only is not True or effects != ("none",) * 5:
                all_authority_clear = False
                failures.append("receipt acquired runtime/evidence/release authority")
            if receipt.surface_id == "managed_flow":
                if receipt.source_seq is not None or receipt.source_timestamp is not None:
                    all_authority_clear = False
                    failures.append("managed checkpoint receipt fabricated native chronology")
                if not receipt.checkpoint_hash:
                    failures.append("managed checkpoint receipt requires current checkpoint hash")
            if receipt.surface_id == "factory_product":
                if receipt.previous_checkpoint_hash is not None or receipt.checkpoint_hash is not None:
                    failures.append("factory native event receipt must not fabricate checkpoint hashes")

        results.append(
            LifecycleEventInteropCaseResult(
                case_id=case_id,
                passed=not failures,
                message="interoperability boundary preserved" if not failures else "; ".join(failures),
            )
        )

    return LifecycleEventInteropReport(
        schema_version=str(raw["schema_version"]),
        corpus_hash=_hash(path),
        total=len(results),
        passed=sum(1 for item in results if item.passed),
        source_inputs_unchanged=all_inputs_unchanged,
        authority_boundaries_clear=all_authority_clear,
        cases=tuple(results),
    )

from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from core.brain_os.adapters.flow_selection import FlowSelectionDecision, SurfaceSource
from core.brain_os.adapters.memory_context import attach_memory_after_flow_selection
from core.brain_os.contracts import Decision, Hypothesis, Reversibility
from core.brain_os.memory_contracts import (
    decision_memory,
    hypothesis_memory,
    rationale_memory,
)
from core.memory.brain_memory import BrainMemoryError, BrainMemoryStore


SCHEMA_VERSION = 1
Operation = Literal["recall", "cross_project_write_rejected"]


class MemoryBoundaryBenchmarkError(ValueError):
    """Raised when the memory-boundary regression corpus is malformed."""


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class MemoryRecordSpec:
    kind: str
    source_run_id: str
    source_ref: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class MemoryBoundaryCase:
    id: str
    operation: Operation
    current_run_id: str
    records: tuple[MemoryRecordSpec, ...]
    filters: dict[str, Any]
    expected_source_refs: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "MemoryBoundaryCase":
        allowed = {
            "id",
            "operation",
            "current_run_id",
            "records",
            "filters",
            "expected_source_refs",
        }
        unknown = sorted(set(raw).difference(allowed))
        missing = sorted(allowed.difference(raw))
        if unknown:
            raise MemoryBoundaryBenchmarkError("memory case has unknown keys: " + ", ".join(unknown))
        if missing:
            raise MemoryBoundaryBenchmarkError("memory case missing keys: " + ", ".join(missing))

        case_id = str(raw["id"]).strip()
        operation = str(raw["operation"]).strip()
        run_id = str(raw["current_run_id"]).strip()
        if not case_id or operation not in {"recall", "cross_project_write_rejected"} or not run_id:
            raise MemoryBoundaryBenchmarkError("id/current_run_id/operation are invalid")
        raw_records = raw["records"]
        if not isinstance(raw_records, list):
            raise MemoryBoundaryBenchmarkError("records must be an array")
        records: list[MemoryRecordSpec] = []
        for item in raw_records:
            if not isinstance(item, dict) or set(item) != {"kind", "source_run_id", "source_ref", "tags"}:
                raise MemoryBoundaryBenchmarkError("each record must contain kind/source_run_id/source_ref/tags")
            kind = str(item["kind"]).strip()
            source_run_id = str(item["source_run_id"]).strip()
            source_ref = str(item["source_ref"]).strip()
            tags = item["tags"]
            if kind not in {"rationale", "hypothesis", "decision"}:
                raise MemoryBoundaryBenchmarkError(f"unsupported memory kind: {kind}")
            if not source_run_id or not source_ref or not isinstance(tags, list):
                raise MemoryBoundaryBenchmarkError("memory record provenance/tags are invalid")
            if any(not isinstance(tag, str) or not tag.strip() for tag in tags):
                raise MemoryBoundaryBenchmarkError("memory tags must be non-empty strings")
            records.append(
                MemoryRecordSpec(
                    kind=kind,
                    source_run_id=source_run_id,
                    source_ref=source_ref,
                    tags=tuple(tag.strip() for tag in tags),
                )
            )
        filters = raw["filters"]
        if not isinstance(filters, dict):
            raise MemoryBoundaryBenchmarkError("filters must be an object")
        allowed_filters = {"kinds", "tags", "source_refs", "limit"}
        if set(filters).difference(allowed_filters):
            raise MemoryBoundaryBenchmarkError("filters contain unsupported keys")
        expected = raw["expected_source_refs"]
        if not isinstance(expected, list) or any(not isinstance(item, str) for item in expected):
            raise MemoryBoundaryBenchmarkError("expected_source_refs must be a string array")
        return cls(
            id=case_id,
            operation=operation,  # type: ignore[arg-type]
            current_run_id=run_id,
            records=tuple(records),
            filters=dict(filters),
            expected_source_refs=tuple(str(item).strip() for item in expected),
        )


@dataclass(frozen=True)
class MemoryBoundaryCorpus:
    benchmark_id: str
    version: str
    cases: tuple[MemoryBoundaryCase, ...]
    content_hash: str

    @classmethod
    def load(cls, path: Path) -> "MemoryBoundaryCorpus":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise MemoryBoundaryBenchmarkError("memory benchmark must be an object")
        allowed = {"schema_version", "benchmark_id", "version", "description", "cases"}
        unknown = sorted(set(payload).difference(allowed))
        if unknown:
            raise MemoryBoundaryBenchmarkError("benchmark has unknown keys: " + ", ".join(unknown))
        if payload.get("schema_version") != SCHEMA_VERSION:
            raise MemoryBoundaryBenchmarkError(f"schema_version must be {SCHEMA_VERSION}")
        benchmark_id = str(payload.get("benchmark_id", "")).strip()
        version = str(payload.get("version", "")).strip()
        raw_cases = payload.get("cases")
        if not benchmark_id or not version or not isinstance(raw_cases, list) or not raw_cases:
            raise MemoryBoundaryBenchmarkError("benchmark_id/version/cases are required")
        cases = tuple(MemoryBoundaryCase.from_dict(item) for item in raw_cases)
        ids = [case.id for case in cases]
        if len(ids) != len(set(ids)):
            raise MemoryBoundaryBenchmarkError("memory benchmark case ids must be unique")
        normalized = {
            "schema_version": SCHEMA_VERSION,
            "benchmark_id": benchmark_id,
            "version": version,
            "cases": raw_cases,
        }
        return cls(benchmark_id, version, cases, _stable_hash(normalized))


def _flow() -> FlowSelectionDecision:
    return FlowSelectionDecision(
        change_surface="PAGE",
        surface_source=SurfaceSource.TASK_CONTRACT,
        flow_id="page-ui-work",
        flow_source="skills_UIUX/flows/page-ui-work.json",
        score=100,
        rationale="Canonical FlowPlanner already selected the flow before memory recall.",
    )


def _record(spec: MemoryRecordSpec, *, project_scope: str, index: int):
    created_at = f"2026-10-02T00:00:{index:02d}Z"
    tags = list(spec.tags)
    if spec.kind == "rationale":
        return rationale_memory(
            source_ref=spec.source_ref,
            subject=f"Rationale {spec.source_ref}",
            rationale=f"Historical rationale for {spec.source_ref}",
            project_scope=project_scope,
            source_run_id=spec.source_run_id,
            created_at=created_at,
            tags=tags,
        )
    if spec.kind == "hypothesis":
        hypothesis = Hypothesis(
            id=spec.source_ref,
            statement=f"Historical hypothesis {spec.source_ref}",
            risk="normal",
            confidence=0.5,
            validation_method="Historical usability test",
        )
        return hypothesis_memory(
            hypothesis,
            project_scope=project_scope,
            source_run_id=spec.source_run_id,
            created_at=created_at,
            tags=tags,
        )
    decision = Decision(
        id=spec.source_ref,
        question=f"Historical decision {spec.source_ref}?",
        chosen="Preserve the historical choice as context only",
        alternatives=["Alternative"],
        evidence_refs=[],
        tradeoff="Historical context may be stale and must not become current truth.",
        reversibility=Reversibility.REVERSIBLE,
        confidence=0.5,
    )
    return decision_memory(
        decision,
        project_scope=project_scope,
        source_run_id=spec.source_run_id,
        created_at=created_at,
        tags=tags,
    )


def evaluate_memory_boundary_case(case: MemoryBoundaryCase) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="uiux-memory-benchmark-") as temporary:
        root = Path(temporary).resolve()
        store = BrainMemoryStore(
            root,
            {"brain_memory": {"max_records": 50, "max_recall_records": 10}},
        )

        if case.operation == "cross_project_write_rejected":
            record = rationale_memory(
                source_ref="cross-project",
                subject="Cross-project record",
                rationale="This record must not be accepted into another project store.",
                project_scope=str((root / "different-project").resolve()),
                source_run_id="run-old",
                created_at="2026-10-02T00:00:00Z",
            )
            rejected = False
            try:
                store.record(record)
            except BrainMemoryError:
                rejected = True
            checks = {
                "cross_project_rejected": rejected,
                "store_remains_empty": store.load() == [],
            }
            return {
                "case_id": case.id,
                "operation": case.operation,
                "checks": checks,
                "passed": all(checks.values()),
                "actual_source_refs": [],
                "flow_id": None,
            }

        scope = str(root)
        for index, spec in enumerate(case.records):
            store.record(_record(spec, project_scope=scope, index=index))

        flow = _flow()
        before = flow.model_dump(mode="json")
        context = attach_memory_after_flow_selection(
            store=store,
            flow_selection=flow,
            current_run_id=case.current_run_id,
            kinds=case.filters.get("kinds", []),
            tags=case.filters.get("tags", []),
            source_refs=case.filters.get("source_refs", []),
            limit=case.filters.get("limit"),
        )
        actual_refs = [item.source_ref for item in context.memories]
        checks = {
            "expected_recall": tuple(actual_refs) == case.expected_source_refs,
            "current_run_excluded": all(
                item.source_run_id != case.current_run_id for item in context.memories
            ),
            "post_routing": context.attached_after_flow_selection is True,
            "flow_unchanged": flow.model_dump(mode="json") == before and context.flow_selection == flow,
            "flow_effect_none": context.flow_effect == "none",
            "authority_effect_none": context.authority_effect == "none",
            "gate_effect_none": context.gate_effect == "none",
            "evidence_effect_none": context.evidence_effect == "none",
            "not_current_evidence": all(
                item.current_run_evidence is False for item in context.memories
            ),
        }
        return {
            "case_id": case.id,
            "operation": case.operation,
            "checks": checks,
            "passed": all(checks.values()),
            "actual_source_refs": actual_refs,
            "flow_id": context.flow_selection.flow_id,
        }


def run_memory_boundary_benchmark(corpus: MemoryBoundaryCorpus) -> dict[str, Any]:
    rows = [evaluate_memory_boundary_case(case) for case in corpus.cases]
    return {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": corpus.benchmark_id,
        "version": corpus.version,
        "content_hash": corpus.content_hash,
        "case_count": len(rows),
        "pass_count": sum(1 for row in rows if row["passed"]),
        "passed": all(row["passed"] for row in rows),
        "cases": rows,
    }

from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


SCHEMA_VERSION = 1


class KnowledgeRetrievalBenchmarkError(ValueError):
    """Raised when the deterministic knowledge-retrieval corpus is malformed."""


@dataclass(frozen=True)
class KnowledgeRetrievalCaseResult:
    case_id: str
    passed: bool
    message: str
    actual_ids: tuple[str, ...]
    exclusion_reasons: tuple[str, ...]


@dataclass(frozen=True)
class KnowledgeRetrievalBenchmarkReport:
    schema_version: int
    benchmark_id: str
    version: str
    scope: str
    corpus_hash: str
    cases: tuple[KnowledgeRetrievalCaseResult, ...]

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def passed(self) -> int:
        return sum(1 for case in self.cases if case.passed)


def _content(record: dict[str, Any]) -> str:
    if "content" in record:
        value = str(record["content"])
        if not value:
            raise KnowledgeRetrievalBenchmarkError("record content cannot be empty")
        return value
    repeat = record.get("content_repeat")
    if not isinstance(repeat, dict) or set(repeat) != {"char", "count"}:
        raise KnowledgeRetrievalBenchmarkError("record requires content or content_repeat")
    char = str(repeat["char"])
    count = repeat["count"]
    if len(char) != 1 or isinstance(count, bool) or not isinstance(count, int) or count < 1 or count > 20_000:
        raise KnowledgeRetrievalBenchmarkError("content_repeat char/count are invalid")
    return char * count


def _write_case_workspace(root: Path, raw_records: list[dict[str, Any]]) -> Path:
    knowledge = root / "skills_UIUX/knowledge"
    records_dir = knowledge / "records"
    content_dir = knowledge / "content"
    records_dir.mkdir(parents=True)
    content_dir.mkdir(parents=True)
    refs: list[str] = []

    allowed = {
        "id",
        "category",
        "domains",
        "stages",
        "tags",
        "freshness",
        "updated_at",
        "confidence",
        "content",
        "content_repeat",
    }
    for item in raw_records:
        if not isinstance(item, dict):
            raise KnowledgeRetrievalBenchmarkError("records must contain objects")
        unknown = set(item).difference(allowed)
        required = {"id", "category", "domains", "stages", "tags", "freshness", "updated_at", "confidence"}
        missing = required.difference(item)
        if unknown or missing:
            raise KnowledgeRetrievalBenchmarkError(
                f"record keys invalid; unknown={sorted(unknown)}, missing={sorted(missing)}"
            )
        record_id = str(item["id"]).strip()
        if not record_id:
            raise KnowledgeRetrievalBenchmarkError("record id is required")
        slug = record_id.replace(".", "-")
        body = _content(item)
        content_path = content_dir / f"{slug}.md"
        content_path.write_text(body, encoding="utf-8")
        ref = f"records/{slug}.json"
        payload = {
            "schema_version": "knowledge-record.v1",
            "id": record_id,
            "title": record_id,
            "category": item["category"],
            "topic": record_id.split(".")[-1],
            "summary": f"Benchmark summary for {record_id}",
            "content_ref": f"skills_UIUX/knowledge/content/{slug}.md",
            "source_ref": f"https://example.invalid/benchmark/{slug}",
            "source_kind": "external_reference",
            "version": "benchmark-v1",
            "updated_at": item["updated_at"],
            "freshness": item["freshness"],
            "confidence": item["confidence"],
            "applicable_domains": item["domains"],
            "applicable_stages": item["stages"],
            "tags": item["tags"],
            "advisory_only": True,
            "current_run_evidence": False,
            "authority_effect": "none",
            "gate_effect": "none",
            "evidence_effect": "none",
            "release_effect": "none",
        }
        (knowledge / ref).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        refs.append(ref)

    (knowledge / "index.json").write_text(
        json.dumps({"schema_version": "knowledge-index.v1", "records": refs}, indent=2),
        encoding="utf-8",
    )
    return knowledge


def _validate_case(raw: dict[str, Any]) -> None:
    allowed = {
        "id",
        "query",
        "records",
        "expected_ids",
        "expected_excluded_reasons",
        "expected_delivered_chars",
    }
    unknown = set(raw).difference(allowed)
    required = {"id", "query", "records", "expected_ids", "expected_excluded_reasons"}
    missing = required.difference(raw)
    if unknown or missing:
        raise KnowledgeRetrievalBenchmarkError(
            f"case keys invalid; unknown={sorted(unknown)}, missing={sorted(missing)}"
        )
    if not str(raw["id"]).strip() or not isinstance(raw["query"], dict) or not isinstance(raw["records"], list):
        raise KnowledgeRetrievalBenchmarkError("case id/query/records are invalid")
    for key in ("expected_ids", "expected_excluded_reasons"):
        if not isinstance(raw[key], list) or any(not isinstance(item, str) for item in raw[key]):
            raise KnowledgeRetrievalBenchmarkError(f"{key} must be a string array")
    delivered = raw.get("expected_delivered_chars")
    if delivered is not None and (
        not isinstance(delivered, list)
        or any(isinstance(item, bool) or not isinstance(item, int) or item < 1 for item in delivered)
    ):
        raise KnowledgeRetrievalBenchmarkError("expected_delivered_chars must be a positive integer array")


def evaluate_knowledge_retrieval_corpus(path: Path) -> KnowledgeRetrievalBenchmarkReport:
    raw_bytes = Path(path).read_bytes()
    payload = json.loads(raw_bytes.decode("utf-8"))
    if not isinstance(payload, dict):
        raise KnowledgeRetrievalBenchmarkError("benchmark must be an object")
    allowed = {"schema_version", "benchmark_id", "version", "scope", "cases"}
    if set(payload) != allowed:
        raise KnowledgeRetrievalBenchmarkError("benchmark keys do not match the v1 contract")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise KnowledgeRetrievalBenchmarkError(f"schema_version must be {SCHEMA_VERSION}")
    benchmark_id = str(payload["benchmark_id"]).strip()
    version = str(payload["version"]).strip()
    scope = str(payload["scope"]).strip()
    raw_cases = payload["cases"]
    if not benchmark_id or not version or not scope or not isinstance(raw_cases, list) or not raw_cases:
        raise KnowledgeRetrievalBenchmarkError("benchmark_id/version/scope/cases are required")

    ids: set[str] = set()
    results: list[KnowledgeRetrievalCaseResult] = []
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            raise KnowledgeRetrievalBenchmarkError("cases must contain objects")
        _validate_case(raw_case)
        case_id = str(raw_case["id"]).strip()
        if case_id in ids:
            raise KnowledgeRetrievalBenchmarkError(f"duplicate case id: {case_id}")
        ids.add(case_id)

        with tempfile.TemporaryDirectory(prefix="uiux-knowledge-benchmark-") as temporary:
            workspace = Path(temporary).resolve()
            knowledge = _write_case_workspace(workspace, raw_case["records"])
            query = KnowledgeQuery.model_validate(raw_case["query"])
            result = KnowledgeRetriever(KnowledgeIndex(knowledge)).retrieve(query)

        actual_ids = tuple(hit.record.id for hit in result.hits)
        reasons = tuple(item.reason for item in result.exclusions)
        expected_ids = tuple(raw_case["expected_ids"])
        expected_reasons = tuple(raw_case["expected_excluded_reasons"])
        checks = {
            "ids": actual_ids == expected_ids,
            "exclusions": sorted(reasons) == sorted(expected_reasons),
            "metadata_first": result.deterministic_metadata_first is True,
            "no_vector": result.vector_search_used is False,
            "not_evidence": result.current_run_evidence is False,
            "flow_effect": result.flow_effect == "none",
            "skill_effect": result.skill_activation_effect == "none",
            "gate_effect": result.gate_effect == "none",
            "release_effect": result.release_effect == "none",
            "index_hash": len(result.index_sha256) == 64,
        }
        expected_chars = raw_case.get("expected_delivered_chars")
        if expected_chars is not None:
            checks["delivered_chars"] = [hit.delivered_content_chars for hit in result.hits] == expected_chars
        passed = all(checks.values())
        failed = [name for name, ok in checks.items() if not ok]
        results.append(
            KnowledgeRetrievalCaseResult(
                case_id=case_id,
                passed=passed,
                message="knowledge retrieval boundary preserved" if passed else "failed: " + ", ".join(failed),
                actual_ids=actual_ids,
                exclusion_reasons=reasons,
            )
        )

    return KnowledgeRetrievalBenchmarkReport(
        schema_version=SCHEMA_VERSION,
        benchmark_id=benchmark_id,
        version=version,
        scope=scope,
        corpus_hash=hashlib.sha256(raw_bytes).hexdigest()[:16],
        cases=tuple(results),
    )

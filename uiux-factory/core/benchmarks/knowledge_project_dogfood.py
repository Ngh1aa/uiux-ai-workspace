from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


SCHEMA_VERSION = 1


class KnowledgeProjectDogfoodError(ValueError):
    pass


@dataclass(frozen=True)
class KnowledgeProjectDogfoodResult:
    case_id: str
    repository: str
    passed: bool
    expected_ids: tuple[str, ...]
    actual_ids: tuple[str, ...]
    message: str


@dataclass(frozen=True)
class KnowledgeProjectDogfoodReport:
    benchmark_id: str
    version: str
    scope: str
    corpus_hash: str
    index_hash: str
    cases: tuple[KnowledgeProjectDogfoodResult, ...]

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def passed(self) -> int:
        return sum(1 for case in self.cases if case.passed)


def _case(raw: dict[str, Any]) -> dict[str, Any]:
    required = {"id", "repository", "goal", "domain", "stage", "terms", "expected_ids"}
    if set(raw) != required:
        raise KnowledgeProjectDogfoodError("dogfood case keys do not match v1 contract")
    if not all(str(raw[key]).strip() for key in ("id", "repository", "goal", "domain", "stage")):
        raise KnowledgeProjectDogfoodError("dogfood case string fields are required")
    if not isinstance(raw["terms"], list) or any(not isinstance(item, str) for item in raw["terms"]):
        raise KnowledgeProjectDogfoodError("dogfood terms must be a string array")
    if not isinstance(raw["expected_ids"], list) or not raw["expected_ids"]:
        raise KnowledgeProjectDogfoodError("dogfood expected_ids must be a non-empty array")
    return raw


def evaluate_knowledge_project_dogfood(
    corpus_path: Path,
    *,
    knowledge_root: Path,
) -> KnowledgeProjectDogfoodReport:
    raw_bytes = Path(corpus_path).read_bytes()
    payload = json.loads(raw_bytes.decode("utf-8"))
    if not isinstance(payload, dict):
        raise KnowledgeProjectDogfoodError("dogfood benchmark must be an object")
    if set(payload) != {"schema_version", "benchmark_id", "version", "scope", "cases"}:
        raise KnowledgeProjectDogfoodError("dogfood benchmark keys do not match v1 contract")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise KnowledgeProjectDogfoodError(f"schema_version must be {SCHEMA_VERSION}")
    raw_cases = payload["cases"]
    if not isinstance(raw_cases, list) or not raw_cases:
        raise KnowledgeProjectDogfoodError("dogfood cases are required")

    index = KnowledgeIndex(knowledge_root)
    indexed, index_hash = index.load()
    if len(indexed) != 4:
        raise KnowledgeProjectDogfoodError(
            f"A50.10C canonical corpus must contain exactly 4 records, got {len(indexed)}"
        )
    retriever = KnowledgeRetriever(index)
    results: list[KnowledgeProjectDogfoodResult] = []
    seen_ids: set[str] = set()

    for raw in raw_cases:
        case = _case(raw)
        case_id = str(case["id"])
        if case_id in seen_ids:
            raise KnowledgeProjectDogfoodError(f"duplicate dogfood case id: {case_id}")
        seen_ids.add(case_id)
        retrieval = retriever.retrieve(
            KnowledgeQuery(
                as_of="2026-10-02",
                domains=[str(case["domain"])],
                stages=[str(case["stage"])],
                terms=[str(item) for item in case["terms"]],
                limit=3,
                max_item_chars=4_000,
                max_total_chars=8_000,
            )
        )
        actual = tuple(hit.record.id for hit in retrieval.hits)
        expected = tuple(str(item) for item in case["expected_ids"])
        checks = {
            "expected_only": actual == expected,
            "cross_domain_excluded": sum(
                1 for item in retrieval.exclusions if item.reason == "domain_mismatch"
            ) == 3,
            "four_record_corpus": retrieval.indexed_record_count == 4,
            "no_vector": retrieval.vector_search_used is False,
            "not_evidence": retrieval.current_run_evidence is False,
            "flow_effect_none": retrieval.flow_effect == "none",
            "skill_effect_none": retrieval.skill_activation_effect == "none",
            "gate_effect_none": retrieval.gate_effect == "none",
            "release_effect_none": retrieval.release_effect == "none",
        }
        failed = [name for name, passed in checks.items() if not passed]
        results.append(
            KnowledgeProjectDogfoodResult(
                case_id=case_id,
                repository=str(case["repository"]),
                passed=not failed,
                expected_ids=expected,
                actual_ids=actual,
                message="curated retrieval isolated correctly" if not failed else "failed: " + ", ".join(failed),
            )
        )

    return KnowledgeProjectDogfoodReport(
        benchmark_id=str(payload["benchmark_id"]),
        version=str(payload["version"]),
        scope=str(payload["scope"]),
        corpus_hash=hashlib.sha256(raw_bytes).hexdigest()[:16],
        index_hash=index_hash,
        cases=tuple(results),
    )

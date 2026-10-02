from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


SCHEMA_VERSION = 1
ALLOWED_DECISIONS = {"KEEP", "REVISE", "REMOVE"}


class KnowledgeUsefulnessError(ValueError):
    pass


@dataclass(frozen=True)
class KnowledgeUsefulnessCaseResult:
    case_id: str
    record_id: str
    decision: str
    passed: bool
    actionable_delta: bool
    domain_specificity: bool
    skill_duplication_clear: bool
    retrieval_noise_clear: bool
    provenance_clear: bool
    context_chars: int
    message: str


@dataclass(frozen=True)
class KnowledgeUsefulnessReport:
    benchmark_id: str
    version: str
    scope: str
    corpus_hash: str
    index_hash: str
    expand_allowed: bool
    expand_blocker: str
    cases: tuple[KnowledgeUsefulnessCaseResult, ...]

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def passed(self) -> int:
        return sum(1 for case in self.cases if case.passed)


def _normalized_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _substantive_lines(text: str) -> set[str]:
    output: set[str] = set()
    for raw in text.splitlines():
        line = re.sub(r"^[#>*\-\d.\s]+", "", raw).strip()
        normalized = _normalized_text(line)
        if len(normalized) >= 60:
            output.add(normalized)
    return output


def _validate_case(raw: dict[str, Any]) -> dict[str, Any]:
    required = {
        "id",
        "repository",
        "domain",
        "stage",
        "terms",
        "record_id",
        "required_actionable_concepts",
        "related_skill_paths",
        "expected_decision",
    }
    if set(raw) != required:
        raise KnowledgeUsefulnessError("usefulness case keys do not match v1 contract")
    for key in ("id", "repository", "domain", "stage", "record_id", "expected_decision"):
        if not str(raw[key]).strip():
            raise KnowledgeUsefulnessError(f"{key} is required")
    for key in ("terms", "required_actionable_concepts", "related_skill_paths"):
        if not isinstance(raw[key], list) or not raw[key] or any(not isinstance(item, str) or not item.strip() for item in raw[key]):
            raise KnowledgeUsefulnessError(f"{key} must be a non-empty string array")
    if raw["expected_decision"] not in ALLOWED_DECISIONS:
        raise KnowledgeUsefulnessError("expected_decision is invalid")
    return raw


def evaluate_knowledge_usefulness(
    corpus_path: Path,
    *,
    workspace_root: Path,
    knowledge_root: Path,
) -> KnowledgeUsefulnessReport:
    raw_bytes = Path(corpus_path).read_bytes()
    payload = json.loads(raw_bytes.decode("utf-8"))
    if not isinstance(payload, dict):
        raise KnowledgeUsefulnessError("usefulness benchmark must be an object")
    if set(payload) != {"schema_version", "benchmark_id", "version", "scope", "cases", "governance"}:
        raise KnowledgeUsefulnessError("usefulness benchmark keys do not match v1 contract")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise KnowledgeUsefulnessError(f"schema_version must be {SCHEMA_VERSION}")
    raw_cases = payload["cases"]
    if not isinstance(raw_cases, list) or not raw_cases:
        raise KnowledgeUsefulnessError("usefulness cases are required")
    governance = payload["governance"]
    if not isinstance(governance, dict) or set(governance) != {"allowed_decisions", "expand_allowed", "expand_blocker"}:
        raise KnowledgeUsefulnessError("governance keys do not match v1 contract")
    if set(governance["allowed_decisions"]) != ALLOWED_DECISIONS:
        raise KnowledgeUsefulnessError("governance decision set drifted")
    if governance["expand_allowed"] is not False or not str(governance["expand_blocker"]).strip():
        raise KnowledgeUsefulnessError("A50.4 must keep corpus expansion blocked with a reason")

    index = KnowledgeIndex(knowledge_root)
    indexed, index_hash = index.load()
    records = {item.record.id: item for item in indexed}
    if len(records) != 3:
        raise KnowledgeUsefulnessError(f"A50.4 evaluates the three-record A50.3 seed; got {len(records)}")
    retriever = KnowledgeRetriever(index)
    results: list[KnowledgeUsefulnessCaseResult] = []
    seen: set[str] = set()

    for raw_case in raw_cases:
        case = _validate_case(raw_case)
        case_id = str(case["id"])
        if case_id in seen:
            raise KnowledgeUsefulnessError(f"duplicate usefulness case id: {case_id}")
        seen.add(case_id)
        record_id = str(case["record_id"])
        item = records.get(record_id)
        if item is None:
            raise KnowledgeUsefulnessError(f"unknown canonical seed record: {record_id}")

        retrieval = retriever.retrieve(
            KnowledgeQuery(
                as_of="2026-10-02",
                domains=[str(case["domain"])],
                stages=[str(case["stage"])],
                terms=[str(value) for value in case["terms"]],
                limit=3,
                max_item_chars=4_000,
                max_total_chars=8_000,
            )
        )
        actual_ids = [hit.record.id for hit in retrieval.hits]
        hit = next((value for value in retrieval.hits if value.record.id == record_id), None)
        content = hit.content if hit else ""
        content_normalized = _normalized_text(content)
        actionable_delta = bool(hit) and all(
            _normalized_text(str(concept)) in content_normalized
            for concept in case["required_actionable_concepts"]
        )
        domain_specificity = (
            bool(hit)
            and item.record.applicable_domains == [str(case["domain"])]
            and actual_ids == [record_id]
        )
        retrieval_noise_clear = (
            actual_ids == [record_id]
            and sum(exclusion.reason == "domain_mismatch" for exclusion in retrieval.exclusions) == 2
        )

        knowledge_lines = _substantive_lines(content)
        duplicated_lines: set[str] = set()
        for relative in case["related_skill_paths"]:
            skill_path = (workspace_root / str(relative)).resolve()
            if not skill_path.is_relative_to(workspace_root.resolve()) or not skill_path.is_file():
                raise KnowledgeUsefulnessError(f"related skill path is invalid: {relative}")
            skill_lines = _substantive_lines(skill_path.read_text(encoding="utf-8"))
            duplicated_lines.update(knowledge_lines.intersection(skill_lines))
        skill_duplication_clear = not duplicated_lines

        parsed_source = urlparse(item.record.source_ref)
        provenance_clear = (
            parsed_source.scheme == "https"
            and bool(parsed_source.hostname)
            and bool(item.record.version.strip())
            and bool(item.record.updated_at.strip())
            and item.record.current_run_evidence is False
            and item.record.authority_effect == "none"
            and item.record.gate_effect == "none"
            and item.record.release_effect == "none"
        )
        context_chars = hit.delivered_content_chars if hit else 0
        context_budget_clear = 250 <= context_chars <= 4_000

        checks = {
            "actionable_delta": actionable_delta,
            "domain_specificity": domain_specificity,
            "skill_duplication_clear": skill_duplication_clear,
            "retrieval_noise_clear": retrieval_noise_clear,
            "provenance_clear": provenance_clear,
            "context_budget_clear": context_budget_clear,
        }
        decision = "KEEP" if all(checks.values()) else "REVISE"
        passed = decision == case["expected_decision"] and all(checks.values())
        failed = [name for name, ok in checks.items() if not ok]
        results.append(
            KnowledgeUsefulnessCaseResult(
                case_id=case_id,
                record_id=record_id,
                decision=decision,
                passed=passed,
                actionable_delta=actionable_delta,
                domain_specificity=domain_specificity,
                skill_duplication_clear=skill_duplication_clear,
                retrieval_noise_clear=retrieval_noise_clear,
                provenance_clear=provenance_clear,
                context_chars=context_chars,
                message=(
                    "KEEP proxy boundaries satisfied; expansion still blocked"
                    if passed
                    else "failed: " + ", ".join(failed or ["decision_mismatch"])
                ),
            )
        )

    return KnowledgeUsefulnessReport(
        benchmark_id=str(payload["benchmark_id"]),
        version=str(payload["version"]),
        scope=str(payload["scope"]),
        corpus_hash=hashlib.sha256(raw_bytes).hexdigest()[:16],
        index_hash=index_hash,
        expand_allowed=False,
        expand_blocker=str(governance["expand_blocker"]),
        cases=tuple(results),
    )

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.brain_os.adapters.repair_lineage import project_repair_lineage
from core.brain_os.critique_contracts import CritiqueIssue, CritiqueSeverity
from core.brain_os.reasoning.evidence_graph import EvidenceRelation
from core.brain_os.repair_orchestrator import CritiqueRepairOrchestrator


SCHEMA_VERSION = 1
EXPECTED_RELATIONS = [
    EvidenceRelation.CAUSED_BY,
    EvidenceRelation.REPAIRED_BY,
    EvidenceRelation.REQUIRES_RETEST,
]


class RepairProposalBenchmarkError(ValueError):
    """Raised when the deterministic repair proposal benchmark is malformed."""


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class RepairProposalCase:
    id: str
    critic: str
    severity: CritiqueSeverity
    expected_target_stage: str
    expected_evidence_types: tuple[str, ...]
    expected_human_approval: bool

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RepairProposalCase":
        allowed = {
            "id",
            "critic",
            "severity",
            "expected_target_stage",
            "expected_evidence_types",
            "expected_human_approval",
        }
        unknown = sorted(set(raw).difference(allowed))
        missing = sorted(allowed.difference(raw))
        if unknown:
            raise RepairProposalBenchmarkError("repair proposal case has unknown keys: " + ", ".join(unknown))
        if missing:
            raise RepairProposalBenchmarkError("repair proposal case missing keys: " + ", ".join(missing))

        case_id = str(raw["id"]).strip()
        critic = str(raw["critic"]).strip()
        target = str(raw["expected_target_stage"]).strip()
        if not case_id or not critic or not target:
            raise RepairProposalBenchmarkError("id/critic/expected_target_stage must be non-empty")
        try:
            severity = CritiqueSeverity(str(raw["severity"]))
        except ValueError as exc:
            raise RepairProposalBenchmarkError("severity must be P0, P1 or P2") from exc
        evidence = raw["expected_evidence_types"]
        if (
            not isinstance(evidence, list)
            or not evidence
            or any(not isinstance(item, str) or not item.strip() for item in evidence)
        ):
            raise RepairProposalBenchmarkError("expected_evidence_types must be a non-empty string array")
        human = raw["expected_human_approval"]
        if not isinstance(human, bool):
            raise RepairProposalBenchmarkError("expected_human_approval must be boolean")
        return cls(
            id=case_id,
            critic=critic,
            severity=severity,
            expected_target_stage=target,
            expected_evidence_types=tuple(str(item).strip() for item in evidence),
            expected_human_approval=human,
        )


@dataclass(frozen=True)
class RepairProposalCorpus:
    benchmark_id: str
    version: str
    cases: tuple[RepairProposalCase, ...]
    content_hash: str

    @classmethod
    def load(cls, path: Path) -> "RepairProposalCorpus":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RepairProposalBenchmarkError("repair proposal benchmark must be an object")
        allowed = {"schema_version", "benchmark_id", "version", "description", "cases"}
        unknown = sorted(set(payload).difference(allowed))
        if unknown:
            raise RepairProposalBenchmarkError("benchmark has unknown keys: " + ", ".join(unknown))
        if payload.get("schema_version") != SCHEMA_VERSION:
            raise RepairProposalBenchmarkError(f"schema_version must be {SCHEMA_VERSION}")
        benchmark_id = str(payload.get("benchmark_id", "")).strip()
        version = str(payload.get("version", "")).strip()
        raw_cases = payload.get("cases")
        if not benchmark_id or not version or not isinstance(raw_cases, list) or not raw_cases:
            raise RepairProposalBenchmarkError("benchmark_id/version/cases are required")
        cases = tuple(RepairProposalCase.from_dict(item) for item in raw_cases)
        ids = [case.id for case in cases]
        if len(ids) != len(set(ids)):
            raise RepairProposalBenchmarkError("repair proposal case ids must be unique")
        hash_payload = {
            "schema_version": SCHEMA_VERSION,
            "benchmark_id": benchmark_id,
            "version": version,
            "cases": [
                {
                    "id": case.id,
                    "critic": case.critic,
                    "severity": case.severity.value,
                    "expected_target_stage": case.expected_target_stage,
                    "expected_evidence_types": list(case.expected_evidence_types),
                    "expected_human_approval": case.expected_human_approval,
                }
                for case in cases
            ],
        }
        return cls(
            benchmark_id=benchmark_id,
            version=version,
            cases=cases,
            content_hash=_stable_hash(hash_payload),
        )


def evaluate_repair_proposal_case(case: RepairProposalCase) -> dict[str, Any]:
    issue = CritiqueIssue(
        id=f"CR-{case.id}",
        critic=case.critic,
        category=f"benchmark.{case.id}",
        severity=case.severity,
        summary=f"Benchmark issue {case.id}",
        rationale="Deterministic repair proposal benchmark input.",
        affected_artifacts=["benchmark"],
    )
    bundle = CritiqueRepairOrchestrator().propose(issue)
    fragment = project_repair_lineage(issue=issue, bundle=bundle)

    relations = [edge.relation for edge in fragment.edges]
    checks = {
        "target_stage": bundle.directive.target_stage == case.expected_target_stage,
        "evidence_types": tuple(bundle.retest.evidence_types) == case.expected_evidence_types,
        "human_approval": bundle.directive.requires_human_approval is case.expected_human_approval,
        "root_proposed": bundle.root_cause.status.value == "PROPOSED",
        "directive_proposed": bundle.directive.status.value == "PROPOSED",
        "retest_pending": bundle.retest.status.value == "PENDING",
        "no_retest_evidence": bundle.retest.evidence_refs == [],
        "proposal_relations": relations == EXPECTED_RELATIONS,
        "no_verified_by": EvidenceRelation.VERIFIED_BY not in relations,
        "no_retested_by": EvidenceRelation.RETESTED_BY not in relations,
        "no_trusted_flag": all(node.canonical_trusted_flag is None for node in fragment.nodes),
        "no_execution_claim": fragment.execution_claim is False,
        "no_verification_claim": fragment.verification_claim is False,
        "no_authority_effect": (
            bundle.execution_effect == "none"
            and bundle.acceptance_effect == "none"
            and bundle.resolution_effect == "none"
            and bundle.gate_effect == "none"
            and bundle.evidence_effect == "none"
        ),
    }
    return {
        "case_id": case.id,
        "critic": case.critic,
        "severity": case.severity.value,
        "checks": checks,
        "passed": all(checks.values()),
        "actual_target_stage": bundle.directive.target_stage,
        "actual_evidence_types": list(bundle.retest.evidence_types),
        "actual_human_approval": bundle.directive.requires_human_approval,
        "relations": [relation.value for relation in relations],
    }


def run_repair_proposal_benchmark(corpus: RepairProposalCorpus) -> dict[str, Any]:
    rows = [evaluate_repair_proposal_case(case) for case in corpus.cases]
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

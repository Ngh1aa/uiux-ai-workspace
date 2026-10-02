from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from core.benchmarks.compatibility_surface_governance import (
    evaluate_compatibility_surface_governance,
)
from core.benchmarks.lifecycle_mutation_convergence_readiness import (
    evaluate_lifecycle_mutation_convergence_readiness,
)
from core.benchmarks.provider_default_migration_readiness import (
    evaluate_provider_default_migration_readiness,
)
from core.benchmarks.runtime_compatibility_convergence import (
    evaluate_runtime_compatibility_convergence,
)
from core.brain_os.knowledge_retrieval import KnowledgeRetrievalResult
from core.brain_os.scorecard import (
    CANONICAL_RUNTIME_EVALUATION_OWNER,
    build_brain_scorecard,
)
from core.evaluation.run_evaluator import RunEvaluation, RunEvaluator
from core.runtime.flow_os.evidence import EvidenceRecord, provider_claim_records
from core.runtime.provider_compat_contract import resolve_factory_provider_lane


CLASSIFICATIONS = {"CLOSED", "INTENTIONAL_HOLD", "NEW_ACTIONABLE_DEBT"}
EXPECTED_AREA_IDS = (
    "runtime_flow_os_single_owner",
    "provider_default_migration",
    "lifecycle_mutation_convergence",
    "brain_os_authority_boundary",
    "knowledge_os_canonical_corpus",
    "genai_nist_expansion",
    "vector_semantic_retrieval",
    "evidence_and_terminal_evaluation",
    "compatibility_surface_removal",
)
EXPECTED_CLASSIFICATIONS = {
    "runtime_flow_os_single_owner": "CLOSED",
    "provider_default_migration": "INTENTIONAL_HOLD",
    "lifecycle_mutation_convergence": "INTENTIONAL_HOLD",
    "brain_os_authority_boundary": "CLOSED",
    "knowledge_os_canonical_corpus": "CLOSED",
    "genai_nist_expansion": "INTENTIONAL_HOLD",
    "vector_semantic_retrieval": "INTENTIONAL_HOLD",
    "evidence_and_terminal_evaluation": "CLOSED",
    "compatibility_surface_removal": "INTENTIONAL_HOLD",
}
EXPECTED_LIFECYCLE_BLOCKERS = (
    "distinct_state_models",
    "factory_append_only_chronology",
    "managed_checkpoint_and_stage_lineage",
    "managed_human_gate_semantics",
    "replan_invalidation_semantics_non_parity",
    "finalize_release_semantics_non_parity",
)


class ArchitectureDebtClosureAuditError(RuntimeError):
    pass


@dataclass(frozen=True)
class DebtAreaResult:
    id: str
    classification: str
    evidence_clear: bool
    upgrade_blocker: bool
    trigger: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArchitectureDebtClosureAuditReport:
    schema_version: str
    decision: str
    scope: str
    source_contract_clear: bool
    area_contract_clear: bool
    governance_boundary_clear: bool
    closed_count: int
    intentional_hold_count: int
    actionable_debt_count: int
    areas: tuple[DebtAreaResult, ...]
    flow4_allowed: bool
    runtime_mutation_allowed: bool
    provider_default_change_allowed: bool
    lifecycle_state_owner_change_allowed: bool
    routing_change_allowed: bool
    knowledge_index_mutation_allowed: bool
    vector_search_change_allowed: bool
    compatibility_shim_deletion_allowed: bool
    evidence_authority_change_allowed: bool
    gate_authority_change_allowed: bool
    release_authority_change_allowed: bool
    product_evidence: bool
    execution_effect: str
    authority_effect: str
    gate_effect: str
    evidence_effect: str
    release_effect: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["areas"] = [item.to_dict() for item in self.areas]
        return payload


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ArchitectureDebtClosureAuditError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ArchitectureDebtClosureAuditError(f"expected JSON object at {path}")
    return payload


def _validate_contract(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    required = {
        "schema_version",
        "audit_id",
        "version",
        "phase",
        "checked_on",
        "scope",
        "classification_values",
        "source_contracts",
        "areas",
        "decision_policy",
        "governance",
        "successor",
    }
    if set(contract) != required:
        raise ArchitectureDebtClosureAuditError("Flow 3 root keys do not match v1 contract")
    if contract["schema_version"] != 1:
        raise ArchitectureDebtClosureAuditError("Flow 3 schema_version must be 1")
    if contract["scope"] != "architecture_debt_closure_audit_only_no_runtime_mutation":
        raise ArchitectureDebtClosureAuditError("Flow 3 scope drifted from audit-only")
    if set(contract["classification_values"]) != CLASSIFICATIONS:
        raise ArchitectureDebtClosureAuditError("Flow 3 classification vocabulary drifted")

    raw_areas = contract["areas"]
    if not isinstance(raw_areas, list) or len(raw_areas) != len(EXPECTED_AREA_IDS):
        raise ArchitectureDebtClosureAuditError("Flow 3 must audit exactly nine architecture areas")
    by_id: dict[str, dict[str, Any]] = {}
    for raw in raw_areas:
        if not isinstance(raw, dict):
            raise ArchitectureDebtClosureAuditError("Flow 3 area entries must be objects")
        area_id = str(raw.get("id", ""))
        classification = str(raw.get("classification", ""))
        if area_id in by_id:
            raise ArchitectureDebtClosureAuditError(f"duplicate Flow 3 area: {area_id}")
        if area_id not in EXPECTED_AREA_IDS:
            raise ArchitectureDebtClosureAuditError(f"unknown Flow 3 area: {area_id}")
        if classification not in CLASSIFICATIONS:
            raise ArchitectureDebtClosureAuditError(f"unknown classification for {area_id}")
        if classification != EXPECTED_CLASSIFICATIONS[area_id]:
            raise ArchitectureDebtClosureAuditError(
                f"{area_id} classification drifted from current evidence-backed contract"
            )
        if classification == "INTENTIONAL_HOLD":
            if raw.get("upgrade_blocker") is not False or not str(raw.get("hold_trigger", "")).strip():
                raise ArchitectureDebtClosureAuditError(
                    f"intentional hold {area_id} requires a non-blocking explicit trigger"
                )
        if classification == "CLOSED" and not str(raw.get("closure_basis", "")).strip():
            raise ArchitectureDebtClosureAuditError(f"closed area {area_id} requires a closure basis")
        by_id[area_id] = raw
    if tuple(item["id"] for item in raw_areas) != EXPECTED_AREA_IDS:
        raise ArchitectureDebtClosureAuditError("Flow 3 area order drifted")

    expected_policy = {
        "source_or_boundary_regression": "HOLD_ARCHITECTURE_DEBT_AUDIT_REGRESSION",
        "new_actionable_debt_present": "NEW_ACTIONABLE_DEBT_REQUIRES_BOUNDED_TASK",
        "closed_and_intentional_holds_only": "ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE",
    }
    if contract["decision_policy"] != expected_policy:
        raise ArchitectureDebtClosureAuditError("Flow 3 decision policy drifted")
    successor = contract["successor"]
    if successor != {
        "when_ledger_closed": "Flow 4 — Final Regression & Cross-project Dogfood",
        "when_actionable_debt_present": "Open one bounded task per evidenced NEW_ACTIONABLE_DEBT before Flow 4",
    }:
        raise ArchitectureDebtClosureAuditError("Flow 3 successor policy drifted")
    return by_id


def _provider_area_clear(repo_root: Path, sources: dict[str, str]) -> bool:
    report = evaluate_provider_default_migration_readiness(
        repo_root / sources["provider_readiness"],
        repo_root / sources["provider_live_receipts"],
        parity_benchmark_path=repo_root / "uiux-factory/benchmarks/provider-parity-v1.json",
        factory_root=repo_root / "uiux-factory",
        skills_root=repo_root / "skills_UIUX",
        runtime_policy_path=repo_root / sources["runtime_policy"],
    )
    return all(
        (
            resolve_factory_provider_lane({}) == ("legacy", "default"),
            report.decision == "KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED",
            report.required_receipt_count == 8,
            report.observed_receipt_count == 0,
            report.default_change_allowed is False,
            report.provider_migration_allowed is False,
            report.auto_migration_allowed is False,
            report.migration_governance_allowed is False,
            report.product_evidence is False,
        )
    )


def _brain_area_clear(repo_root: Path, sources: dict[str, str]) -> bool:
    runtime_evaluation = RunEvaluation(
        schema_version=1,
        run_id="flow3-audit",
        flow_id="audit",
        flow_revision=1,
        managed_state="COMPLETED",
        outcome="insufficient_evidence",
        evaluated_at="2026-10-02T00:00:00+00:00",
        effective_evidence_count=0,
    )
    scorecard = build_brain_scorecard(
        runtime_evaluation=runtime_evaluation,
        runtime_source_ref="audit://runtime-evaluation",
    )
    policy = _read_json(repo_root / sources["runtime_policy"])
    required_rule = (
        "Release authority must come from explicit user/project authorization and is never delegated to provider roles."
    )
    return all(
        (
            scorecard.runtime_outcome == runtime_evaluation.outcome,
            scorecard.canonical_runtime_outcome_owner == CANONICAL_RUNTIME_EVALUATION_OWNER,
            scorecard.advisory_only is True,
            scorecard.authority_effect == "none",
            scorecard.gate_effect == "none",
            scorecard.evidence_effect == "none",
            scorecard.release_effect == "none",
            required_rule in list(policy.get("rules") or []),
        )
    )


def _knowledge_area_clear(repo_root: Path, sources: dict[str, str]) -> bool:
    state = _read_json(repo_root / sources["knowledge_canonical_state"])
    index = _read_json(repo_root / sources["knowledge_index"])
    expected_refs = [str(item["ref"]) for item in state.get("expected_records", [])]
    governance = dict(state.get("governance") or {})
    fields = KnowledgeRetrievalResult.model_fields
    return all(
        (
            len(expected_refs) == 5,
            index.get("schema_version") == "knowledge-index.v1",
            list(index.get("records") or []) == expected_refs,
            governance.get("canonical_record_count") == 5,
            governance.get("vector_search_change_allowed") is False,
            governance.get("product_evidence") is False,
            governance.get("genai_candidate_status") == "HOLD_FRESHNESS_REVIEW",
            fields["deterministic_metadata_first"].default is True,
            fields["vector_search_used"].default is False,
            fields["advisory_only"].default is True,
            fields["current_run_evidence"].default is False,
        )
    )


def _genai_area_clear(repo_root: Path, sources: dict[str, str]) -> bool:
    review = _read_json(repo_root / sources["genai_freshness"])
    governance = dict(review.get("governance") or {})
    trigger = dict(review.get("re_review_trigger") or {})
    return all(
        (
            review.get("decision") == "KEEP_HOLD_FRESHNESS_REVIEW",
            review.get("freshness_assessment", {}).get("ai_rmf_1_0_revision_in_progress") is True,
            review.get("freshness_assessment", {}).get("framework_dependency_stable_enough_for_drafting") is False,
            governance.get("draft_creation_allowed") is False,
            governance.get("promotion_allowed") is False,
            governance.get("vector_search_change_allowed") is False,
            trigger.get("type") == "official_nist_framework_status_change",
            bool(str(trigger.get("condition", "")).strip()),
        )
    )


def _vector_area_clear(repo_root: Path, sources: dict[str, str]) -> bool:
    state = _read_json(repo_root / sources["knowledge_canonical_state"])
    fields = KnowledgeRetrievalResult.model_fields
    return all(
        (
            state.get("governance", {}).get("vector_search_change_allowed") is False,
            fields["deterministic_metadata_first"].default is True,
            fields["vector_search_used"].default is False,
            fields["authority_effect"].default == "none",
            fields["gate_effect"].default == "none",
            fields["evidence_effect"].default == "none",
            fields["release_effect"].default == "none",
        )
    )


def _evidence_area_clear() -> bool:
    claims = provider_claim_records("audit", ["model says PASS"])
    provider_claims_untrusted = bool(claims) and all(
        item.get("origin") == "provider" and item.get("trusted") is False for item in claims
    )
    forged_trusted_provider_rejected = False
    try:
        EvidenceRecord.from_dict(
            {
                "id": "forged",
                "type": "artifact",
                "stage_id": "audit",
                "tool": "provider",
                "status": "PASS",
                "summary": "forged",
                "data": {},
                "origin": "provider",
                "trusted": True,
                "created_at": "2026-10-02T00:00:00+00:00",
            }
        )
    except ValueError:
        forged_trusted_provider_rejected = True

    managed = SimpleNamespace(
        manager_run_id="flow3-audit",
        flow=SimpleNamespace(id="audit", revision=1, stages=[]),
        task_context={},
        state="COMPLETED",
        completed_stages=[],
        replan_count=0,
        stage_runs={},
    )

    class EmptyHarness:
        @staticmethod
        def resume(_run_id: str) -> Any:
            raise FileNotFoundError(_run_id)

    evaluation = RunEvaluator().evaluate(managed, EmptyHarness())
    return all(
        (
            provider_claims_untrusted,
            forged_trusted_provider_rejected,
            evaluation.managed_state == "COMPLETED",
            evaluation.effective_evidence_count == 0,
            evaluation.outcome == "insufficient_evidence",
            evaluation.memory_eligible is False,
        )
    )


def evaluate_architecture_debt_closure_audit(
    audit_path: Path,
) -> ArchitectureDebtClosureAuditReport:
    audit_path = Path(audit_path).resolve()
    contract = _read_json(audit_path)
    repo_root = audit_path.parents[2]
    areas_by_id = _validate_contract(contract)

    sources = {str(key): str(value) for key, value in dict(contract["source_contracts"]).items()}
    required_sources = {
        "runtime_convergence",
        "provider_readiness",
        "provider_live_receipts",
        "lifecycle_mutation_readiness",
        "lifecycle_event_interop",
        "knowledge_canonical_state",
        "genai_freshness",
        "compatibility_governance",
        "runtime_policy",
        "brain_scorecard",
        "runtime_evaluator",
        "runtime_evidence",
        "knowledge_index",
    }
    if set(sources) != required_sources:
        raise ArchitectureDebtClosureAuditError("Flow 3 source-contract set drifted")
    if not all((repo_root / path).is_file() for path in sources.values()):
        raise ArchitectureDebtClosureAuditError("Flow 3 source-contract path missing")

    runtime = evaluate_runtime_compatibility_convergence(repo_root / sources["runtime_convergence"])
    runtime_clear = all(
        (
            runtime.decision == "FIRST_PARTY_RUNTIME_COMPAT_CONVERGENCE_PASS",
            runtime.internal_consumer_file_count == 0,
            runtime.internal_consumer_import_count == 0,
            runtime.shim_count == 8,
            runtime.shim_contract_clear,
            runtime.identity_checks_clear,
            runtime.shim_deletion_allowed is False,
            runtime.external_removal_safety_inferred is False,
        )
    )

    provider_clear = _provider_area_clear(repo_root, sources)

    lifecycle = evaluate_lifecycle_mutation_convergence_readiness(
        repo_root / sources["lifecycle_mutation_readiness"],
        lifecycle_parity_path=repo_root / "uiux-factory/benchmarks/lifecycle-parity-v1.json",
    )
    interop = _read_json(repo_root / sources["lifecycle_event_interop"])
    lifecycle_clear = all(
        (
            lifecycle.decision == "KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED",
            lifecycle.semantic_blockers == EXPECTED_LIFECYCLE_BLOCKERS,
            lifecycle.semantic_blockers_match_contract,
            lifecycle.source_contract_clear,
            lifecycle.reconciliation_read_only,
            lifecycle.runtime_transition_change_allowed is False,
            lifecycle.state_owner_replacement_allowed is False,
            lifecycle.shared_mutable_state_allowed is False,
            interop.get("scope") == "observation_only_no_lifecycle_mutation",
        )
    )

    brain_clear = _brain_area_clear(repo_root, sources)
    knowledge_clear = _knowledge_area_clear(repo_root, sources)
    genai_clear = _genai_area_clear(repo_root, sources)
    vector_clear = _vector_area_clear(repo_root, sources)
    evidence_clear = _evidence_area_clear()

    compatibility = evaluate_compatibility_surface_governance(
        repo_root / sources["compatibility_governance"]
    )
    compatibility_clear = all(
        (
            compatibility.decision == "DEPRECATE_WITH_SUNSET_REMOVAL_GOVERNANCE_CLOSED",
            compatibility.deprecate_with_sunset_count == 8,
            compatibility.open_removal_governance_count == 0,
            compatibility.external_usage_status == "UNKNOWN",
            compatibility.earliest_removal_review_date == "2026-12-31",
            compatibility.removal_governance_open is False,
            compatibility.shim_deletion_allowed is False,
            compatibility.external_removal_safety_inferred is False,
        )
    )

    evidence_by_area = {
        "runtime_flow_os_single_owner": runtime_clear,
        "provider_default_migration": provider_clear,
        "lifecycle_mutation_convergence": lifecycle_clear,
        "brain_os_authority_boundary": brain_clear,
        "knowledge_os_canonical_corpus": knowledge_clear,
        "genai_nist_expansion": genai_clear,
        "vector_semantic_retrieval": vector_clear,
        "evidence_and_terminal_evaluation": evidence_clear,
        "compatibility_surface_removal": compatibility_clear,
    }

    area_results: list[DebtAreaResult] = []
    for area_id in EXPECTED_AREA_IDS:
        raw = areas_by_id[area_id]
        classification = str(raw["classification"])
        trigger = str(raw.get("hold_trigger", "")) if classification == "INTENTIONAL_HOLD" else ""
        area_results.append(
            DebtAreaResult(
                id=area_id,
                classification=classification,
                evidence_clear=bool(evidence_by_area[area_id]),
                upgrade_blocker=bool(raw.get("upgrade_blocker", False)),
                trigger=trigger,
            )
        )

    governance = dict(contract["governance"])
    false_keys = (
        "new_feature_implementation_allowed",
        "runtime_mutation_allowed",
        "provider_default_change_allowed",
        "lifecycle_state_owner_change_allowed",
        "routing_change_allowed",
        "knowledge_index_mutation_allowed",
        "vector_search_change_allowed",
        "compatibility_shim_deletion_allowed",
        "evidence_authority_change_allowed",
        "gate_authority_change_allowed",
        "release_authority_change_allowed",
        "product_evidence",
    )
    effect_keys = (
        "execution_effect",
        "authority_effect",
        "gate_effect",
        "evidence_effect",
        "release_effect",
    )
    governance_boundary_clear = all(governance.get(key) is False for key in false_keys) and all(
        governance.get(key) == "none" for key in effect_keys
    )
    if governance.get("final_owner_review_status") != "DEFERRED_UNTIL_UPGRADE_COMPLETE":
        governance_boundary_clear = False

    closed_count = sum(item.classification == "CLOSED" for item in area_results)
    hold_count = sum(item.classification == "INTENTIONAL_HOLD" for item in area_results)
    actionable_count = sum(item.classification == "NEW_ACTIONABLE_DEBT" for item in area_results)
    source_contract_clear = all(item.evidence_clear for item in area_results)
    area_contract_clear = (
        closed_count == 4
        and hold_count == 5
        and actionable_count == 0
        and all(not item.upgrade_blocker for item in area_results if item.classification == "INTENTIONAL_HOLD")
    )

    policy = dict(contract["decision_policy"])
    if not source_contract_clear or not area_contract_clear or not governance_boundary_clear:
        decision = policy["source_or_boundary_regression"]
    elif actionable_count:
        decision = policy["new_actionable_debt_present"]
    else:
        decision = policy["closed_and_intentional_holds_only"]

    flow4_allowed = decision == "ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE"

    return ArchitectureDebtClosureAuditReport(
        schema_version="architecture-debt-closure-audit.v1",
        decision=decision,
        scope=str(contract["scope"]),
        source_contract_clear=source_contract_clear,
        area_contract_clear=area_contract_clear,
        governance_boundary_clear=governance_boundary_clear,
        closed_count=closed_count,
        intentional_hold_count=hold_count,
        actionable_debt_count=actionable_count,
        areas=tuple(area_results),
        flow4_allowed=flow4_allowed,
        runtime_mutation_allowed=bool(governance.get("runtime_mutation_allowed")),
        provider_default_change_allowed=bool(governance.get("provider_default_change_allowed")),
        lifecycle_state_owner_change_allowed=bool(governance.get("lifecycle_state_owner_change_allowed")),
        routing_change_allowed=bool(governance.get("routing_change_allowed")),
        knowledge_index_mutation_allowed=bool(governance.get("knowledge_index_mutation_allowed")),
        vector_search_change_allowed=bool(governance.get("vector_search_change_allowed")),
        compatibility_shim_deletion_allowed=bool(governance.get("compatibility_shim_deletion_allowed")),
        evidence_authority_change_allowed=bool(governance.get("evidence_authority_change_allowed")),
        gate_authority_change_allowed=bool(governance.get("gate_authority_change_allowed")),
        release_authority_change_allowed=bool(governance.get("release_authority_change_allowed")),
        product_evidence=bool(governance.get("product_evidence")),
        execution_effect=str(governance.get("execution_effect", "")),
        authority_effect=str(governance.get("authority_effect", "")),
        gate_effect=str(governance.get("gate_effect", "")),
        evidence_effect=str(governance.get("evidence_effect", "")),
        release_effect=str(governance.get("release_effect", "")),
    )

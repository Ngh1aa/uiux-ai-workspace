from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from core.benchmarks.knowledge_value_trial import evaluate_knowledge_value_trial


SCHEMA_VERSION = 1
EXPECTED_SCOPE = "proposal_only_no_index_or_record_mutation"
ALLOWED_STATUSES = {"READY_FOR_CONTENT_DRAFT", "HOLD_FRESHNESS_REVIEW", "REJECT"}
ALLOWED_RISKS = {"LOW", "MEDIUM", "HIGH"}
ALLOWED_FRESHNESS = {"evergreen", "versioned", "time_sensitive"}
NO_EFFECT = "none"


class KnowledgeExpansionProposalError(ValueError):
    pass


@dataclass(frozen=True)
class ExpansionCandidateResult:
    candidate_id: str
    proposed_record_id: str
    domain: str
    status: str
    source_host: str
    freshness: str
    duplication_risk: str
    freshness_risk: str


@dataclass(frozen=True)
class KnowledgeExpansionProposalReport:
    proposal_id: str
    version: str
    proposal_hash: str
    current_index_count: int
    candidate_count: int
    ready_count: int
    hold_count: int
    reject_count: int
    trigger_recommendation: str
    index_mutation_allowed: bool
    record_creation_allowed: bool
    vector_search_change_allowed: bool
    candidates: tuple[ExpansionCandidateResult, ...]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise KnowledgeExpansionProposalError(f"expected object: {path}")
    return payload


def _nonempty_strings(value: Any, *, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise KnowledgeExpansionProposalError(f"{field} must be a non-empty string array")
    output: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise KnowledgeExpansionProposalError(f"{field} must be a non-empty string array")
        output.append(item.strip())
    if len(set(output)) != len(output):
        raise KnowledgeExpansionProposalError(f"{field} must not contain duplicates")
    return output


def _canonical_records(knowledge_root: Path) -> tuple[set[str], set[str], int]:
    index = _load_json(knowledge_root / "index.json")
    records = index.get("records")
    if not isinstance(records, list) or len(records) != 3:
        raise KnowledgeExpansionProposalError(
            f"A50.6 proposal must not mutate the three-record canonical index; got {len(records) if isinstance(records, list) else 'invalid'}"
        )
    ids: set[str] = set()
    domains: set[str] = set()
    for relative in records:
        if not isinstance(relative, str) or not relative.strip():
            raise KnowledgeExpansionProposalError("canonical index contains invalid record path")
        record_path = (knowledge_root / relative).resolve()
        if not record_path.is_relative_to(knowledge_root.resolve()) or not record_path.is_file():
            raise KnowledgeExpansionProposalError(f"canonical index record path is invalid: {relative}")
        record = _load_json(record_path)
        record_id = str(record.get("id", "")).strip()
        if not record_id:
            raise KnowledgeExpansionProposalError(f"canonical record missing id: {relative}")
        ids.add(record_id)
        for domain in record.get("applicable_domains") or []:
            if isinstance(domain, str) and domain.strip():
                domains.add(domain.strip())
    if len(ids) != 3:
        raise KnowledgeExpansionProposalError("canonical seed must contain three unique record ids")
    return ids, domains, len(records)


def evaluate_knowledge_expansion_proposal(
    *,
    proposal_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
    benchmarks_root: Path,
) -> KnowledgeExpansionProposalReport:
    raw = proposal_path.read_bytes()
    proposal = json.loads(raw.decode("utf-8"))
    if not isinstance(proposal, dict):
        raise KnowledgeExpansionProposalError("proposal must be an object")

    required_top = {
        "schema_version",
        "proposal_id",
        "version",
        "checked_on",
        "scope",
        "trigger",
        "governance",
        "candidates",
    }
    if set(proposal) != required_top:
        raise KnowledgeExpansionProposalError("proposal top-level keys do not match v1 contract")
    if proposal["schema_version"] != SCHEMA_VERSION:
        raise KnowledgeExpansionProposalError(f"schema_version must be {SCHEMA_VERSION}")
    if proposal["scope"] != EXPECTED_SCOPE:
        raise KnowledgeExpansionProposalError("A50.6 must remain proposal-only")

    trigger = proposal["trigger"]
    expected_trigger_keys = {
        "trial_id",
        "required_recommendation",
        "required_knowledge_preferred_count",
        "required_joint_usefulness_win_count",
        "required_material_regression_count",
    }
    if not isinstance(trigger, dict) or set(trigger) != expected_trigger_keys:
        raise KnowledgeExpansionProposalError("trigger keys do not match v1 contract")
    if trigger["trial_id"] != "knowledge-value-trial-v2":
        raise KnowledgeExpansionProposalError("A50.6 trigger must be the completed round-two trial")

    trial_result = evaluate_knowledge_value_trial(
        trial_path=benchmarks_root / "knowledge-value-trial-v2.json",
        mapping_path=benchmarks_root / "knowledge-value-trial-mapping-v2.json",
        reviews_path=benchmarks_root / "knowledge-value-human-reviews-v2.json",
    )
    if trial_result.expansion_recommendation != trigger["required_recommendation"]:
        raise KnowledgeExpansionProposalError("proposal trigger recommendation does not match canonical v2 evaluator")
    if trial_result.expansion_recommendation != "CONSIDER_EXPANSION":
        raise KnowledgeExpansionProposalError("A50.6 requires canonical CONSIDER_EXPANSION")
    if trial_result.knowledge_preferred_count != trigger["required_knowledge_preferred_count"]:
        raise KnowledgeExpansionProposalError("proposal knowledge-preference trigger drifted")
    if trial_result.joint_usefulness_win_count != trigger["required_joint_usefulness_win_count"]:
        raise KnowledgeExpansionProposalError("proposal joint-usefulness trigger drifted")
    if trial_result.material_regression_count != trigger["required_material_regression_count"]:
        raise KnowledgeExpansionProposalError("proposal regression trigger drifted")

    governance = proposal["governance"]
    expected_governance_keys = {
        "index_mutation_allowed",
        "record_creation_allowed",
        "vector_search_change_allowed",
        "current_run_evidence",
        "product_evidence",
        "authority_effect",
        "gate_effect",
        "release_effect",
        "next_action",
    }
    if not isinstance(governance, dict) or set(governance) != expected_governance_keys:
        raise KnowledgeExpansionProposalError("governance keys do not match v1 contract")
    for field in (
        "index_mutation_allowed",
        "record_creation_allowed",
        "vector_search_change_allowed",
        "current_run_evidence",
        "product_evidence",
    ):
        if governance[field] is not False:
            raise KnowledgeExpansionProposalError(f"A50.6 proposal must keep {field}=false")
    for field in ("authority_effect", "gate_effect", "release_effect"):
        if governance[field] != NO_EFFECT:
            raise KnowledgeExpansionProposalError(f"A50.6 proposal must keep {field}=none")
    if governance["next_action"] != "candidate_review_only":
        raise KnowledgeExpansionProposalError("A50.6 next action must remain candidate_review_only")

    current_ids, current_domains, index_count = _canonical_records(knowledge_root)
    candidates = proposal["candidates"]
    if not isinstance(candidates, list) or len(candidates) != 3:
        raise KnowledgeExpansionProposalError("A50.6 v1 must stay bounded to exactly three candidates")

    required_candidate_keys = {
        "candidate_id",
        "proposed_record_id",
        "title",
        "category",
        "domain",
        "topic",
        "source_ref",
        "source_kind",
        "source_version",
        "source_checked_on",
        "freshness",
        "target_stages",
        "knowledge_scope",
        "excluded_methodology",
        "related_skill_paths",
        "duplication_risk",
        "freshness_risk",
        "expected_retrieval_value",
        "proposal_status",
        "authority_effect",
        "gate_effect",
        "evidence_effect",
        "release_effect",
    }
    seen_candidate_ids: set[str] = set()
    seen_record_ids: set[str] = set()
    seen_domains: set[str] = set()
    results: list[ExpansionCandidateResult] = []

    for candidate in candidates:
        if not isinstance(candidate, dict) or set(candidate) != required_candidate_keys:
            raise KnowledgeExpansionProposalError("candidate keys do not match v1 contract")
        candidate_id = str(candidate["candidate_id"]).strip()
        record_id = str(candidate["proposed_record_id"]).strip()
        domain = str(candidate["domain"]).strip()
        if not candidate_id or not record_id or not domain:
            raise KnowledgeExpansionProposalError("candidate id, proposed record id and domain are required")
        if candidate_id in seen_candidate_ids or record_id in seen_record_ids or domain in seen_domains:
            raise KnowledgeExpansionProposalError("candidate ids, proposed record ids and domains must be unique")
        seen_candidate_ids.add(candidate_id)
        seen_record_ids.add(record_id)
        seen_domains.add(domain)
        if record_id in current_ids:
            raise KnowledgeExpansionProposalError(f"candidate already exists in canonical index: {record_id}")
        if domain in current_domains:
            raise KnowledgeExpansionProposalError(f"A50.6 v1 candidate duplicates an existing seed domain: {domain}")
        if candidate["category"] != "domain":
            raise KnowledgeExpansionProposalError("A50.6 v1 candidates must remain domain knowledge")

        source = urlparse(str(candidate["source_ref"]))
        if source.scheme != "https" or not source.hostname:
            raise KnowledgeExpansionProposalError(f"{candidate_id}: source_ref must be an HTTPS source")
        if not str(candidate["source_version"]).strip() or not str(candidate["source_checked_on"]).strip():
            raise KnowledgeExpansionProposalError(f"{candidate_id}: source version/check date are required")
        if candidate["source_checked_on"] != proposal["checked_on"]:
            raise KnowledgeExpansionProposalError(f"{candidate_id}: source check date must match proposal check date")

        freshness = candidate["freshness"]
        if freshness not in ALLOWED_FRESHNESS:
            raise KnowledgeExpansionProposalError(f"{candidate_id}: invalid freshness")
        duplication_risk = candidate["duplication_risk"]
        freshness_risk = candidate["freshness_risk"]
        if duplication_risk not in ALLOWED_RISKS or freshness_risk not in ALLOWED_RISKS:
            raise KnowledgeExpansionProposalError(f"{candidate_id}: invalid risk level")
        status = candidate["proposal_status"]
        if status not in ALLOWED_STATUSES:
            raise KnowledgeExpansionProposalError(f"{candidate_id}: invalid proposal status")
        if freshness == "time_sensitive" and status != "HOLD_FRESHNESS_REVIEW":
            raise KnowledgeExpansionProposalError(f"{candidate_id}: time-sensitive candidate must HOLD for freshness review")
        if status == "READY_FOR_CONTENT_DRAFT" and (duplication_risk == "HIGH" or freshness_risk == "HIGH"):
            raise KnowledgeExpansionProposalError(f"{candidate_id}: high-risk candidate cannot be READY")

        _nonempty_strings(candidate["target_stages"], field=f"{candidate_id}.target_stages")
        _nonempty_strings(candidate["knowledge_scope"], field=f"{candidate_id}.knowledge_scope")
        _nonempty_strings(candidate["excluded_methodology"], field=f"{candidate_id}.excluded_methodology")
        skill_paths = _nonempty_strings(candidate["related_skill_paths"], field=f"{candidate_id}.related_skill_paths")
        if not str(candidate["expected_retrieval_value"]).strip():
            raise KnowledgeExpansionProposalError(f"{candidate_id}: expected retrieval value is required")
        for relative in skill_paths:
            path = (workspace_root / relative).resolve()
            if not path.is_relative_to(workspace_root.resolve()) or not path.is_file():
                raise KnowledgeExpansionProposalError(f"{candidate_id}: related skill path is invalid: {relative}")
        for field in ("authority_effect", "gate_effect", "evidence_effect", "release_effect"):
            if candidate[field] != NO_EFFECT:
                raise KnowledgeExpansionProposalError(f"{candidate_id}: {field} must remain none")

        results.append(
            ExpansionCandidateResult(
                candidate_id=candidate_id,
                proposed_record_id=record_id,
                domain=domain,
                status=status,
                source_host=source.hostname,
                freshness=freshness,
                duplication_risk=duplication_risk,
                freshness_risk=freshness_risk,
            )
        )

    return KnowledgeExpansionProposalReport(
        proposal_id=str(proposal["proposal_id"]),
        version=str(proposal["version"]),
        proposal_hash=hashlib.sha256(raw).hexdigest()[:16],
        current_index_count=index_count,
        candidate_count=len(results),
        ready_count=sum(item.status == "READY_FOR_CONTENT_DRAFT" for item in results),
        hold_count=sum(item.status == "HOLD_FRESHNESS_REVIEW" for item in results),
        reject_count=sum(item.status == "REJECT" for item in results),
        trigger_recommendation=trial_result.expansion_recommendation,
        index_mutation_allowed=False,
        record_creation_allowed=False,
        vector_search_change_allowed=False,
        candidates=tuple(results),
    )

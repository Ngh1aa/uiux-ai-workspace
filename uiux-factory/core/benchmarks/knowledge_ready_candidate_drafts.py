from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from urllib.parse import urlparse

from core.benchmarks.knowledge_expansion_proposal import evaluate_knowledge_expansion_proposal
from core.brain_os.knowledge_contracts import KnowledgeRecord
from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


SCHEMA_VERSION = 1
EXPECTED_SCOPE = "draft_validation_shadow_index_not_canonical_acceptance"
KEEP_DRAFT = "KEEP_DRAFT"
REVISE_DRAFT = "REVISE_DRAFT"


class KnowledgeReadyCandidateDraftError(ValueError):
    pass


@dataclass(frozen=True)
class DraftCaseResult:
    case_id: str
    candidate_id: str
    record_id: str
    decision: str
    passed: bool
    actionable_delta: bool
    proposal_alignment_clear: bool
    canonical_unindexed: bool
    domain_specificity: bool
    skill_duplication_clear: bool
    retrieval_noise_clear: bool
    provenance_clear: bool
    context_budget_clear: bool
    context_chars: int
    message: str


@dataclass(frozen=True)
class KnowledgeReadyCandidateDraftReport:
    benchmark_id: str
    version: str
    corpus_hash: str
    canonical_index_count: int
    draft_record_count: int
    shadow_index_count: int
    keep_draft_count: int
    revise_draft_count: int
    genai_hold_preserved: bool
    index_mutation_allowed: bool
    canonical_acceptance_allowed: bool
    vector_search_change_allowed: bool
    human_usefulness_claimed: bool
    cases: tuple[DraftCaseResult, ...]

    @property
    def passed(self) -> int:
        return sum(1 for case in self.cases if case.passed)

    @property
    def total(self) -> int:
        return len(self.cases)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeReadyCandidateDraftError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeReadyCandidateDraftError(f"expected object: {path}")
    return payload


def _safe_workspace_path(workspace_root: Path, relative: str, *, purpose: str) -> Path:
    value = str(relative).strip()
    if not value:
        raise KnowledgeReadyCandidateDraftError(f"{purpose} path is required")
    candidate = Path(value)
    if candidate.is_absolute():
        raise KnowledgeReadyCandidateDraftError(f"{purpose} path must be workspace-relative: {value}")
    resolved = (workspace_root / candidate).resolve()
    if not resolved.is_relative_to(workspace_root.resolve()):
        raise KnowledgeReadyCandidateDraftError(f"{purpose} path escapes workspace: {value}")
    return resolved


def _normalized_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).lower()).strip()


def _substantive_lines(text: str) -> set[str]:
    output: set[str] = set()
    for raw in text.splitlines():
        line = re.sub(r"^[#>*\-\d.\s]+", "", raw).strip()
        normalized = _normalized_text(line)
        if len(normalized) >= 60:
            output.add(normalized)
    return output


def _validate_governance(raw: Any) -> dict[str, Any]:
    expected = {
        "canonical_index_expected_count",
        "draft_record_expected_count",
        "shadow_index_expected_count",
        "index_mutation_allowed",
        "canonical_acceptance_allowed",
        "vector_search_change_allowed",
        "human_usefulness_claim_allowed",
        "genai_candidate_status",
        "next_action",
    }
    if not isinstance(raw, dict) or set(raw) != expected:
        raise KnowledgeReadyCandidateDraftError("A50.7 governance keys do not match v1 contract")
    if raw["canonical_index_expected_count"] != 3:
        raise KnowledgeReadyCandidateDraftError("A50.7 canonical index expectation must remain 3")
    if raw["draft_record_expected_count"] != 2 or raw["shadow_index_expected_count"] != 5:
        raise KnowledgeReadyCandidateDraftError("A50.7 must remain bounded to two drafts / five-record shadow index")
    for field in (
        "index_mutation_allowed",
        "canonical_acceptance_allowed",
        "vector_search_change_allowed",
        "human_usefulness_claim_allowed",
    ):
        if raw[field] is not False:
            raise KnowledgeReadyCandidateDraftError(f"A50.7 must keep {field}=false")
    if raw["genai_candidate_status"] != "HOLD_FRESHNESS_REVIEW":
        raise KnowledgeReadyCandidateDraftError("GenAI/NIST must remain HOLD in A50.7")
    if raw["next_action"] != "draft_review_only":
        raise KnowledgeReadyCandidateDraftError("A50.7 next action must remain draft_review_only")
    return raw


def _validate_case(raw: Any) -> dict[str, Any]:
    expected = {
        "id",
        "candidate_id",
        "draft_record_path",
        "draft_content_path",
        "expected_record_id",
        "expected_source_host",
        "domain",
        "stage",
        "terms",
        "required_actionable_concepts",
        "related_skill_paths",
        "expected_proxy_decision",
    }
    if not isinstance(raw, dict) or set(raw) != expected:
        raise KnowledgeReadyCandidateDraftError("A50.7 case keys do not match v1 contract")
    for field in (
        "id",
        "candidate_id",
        "draft_record_path",
        "draft_content_path",
        "expected_record_id",
        "expected_source_host",
        "domain",
        "stage",
    ):
        if not str(raw[field]).strip():
            raise KnowledgeReadyCandidateDraftError(f"{field} is required")
    for field in ("terms", "required_actionable_concepts", "related_skill_paths"):
        values = raw[field]
        if not isinstance(values, list) or not values or any(not isinstance(item, str) or not item.strip() for item in values):
            raise KnowledgeReadyCandidateDraftError(f"{field} must be a non-empty string array")
        if len(values) != len(set(values)):
            raise KnowledgeReadyCandidateDraftError(f"{field} must not contain duplicates")
    if raw["expected_proxy_decision"] != KEEP_DRAFT:
        raise KnowledgeReadyCandidateDraftError("A50.7 v1 expects KEEP_DRAFT for READY candidates")
    return raw


def _canonical_index(knowledge_root: Path) -> tuple[list[str], set[str], set[str]]:
    payload = _load_json(knowledge_root / "index.json")
    if set(payload) != {"schema_version", "records"} or payload.get("schema_version") != "knowledge-index.v1":
        raise KnowledgeReadyCandidateDraftError("canonical knowledge index contract drifted")
    refs = payload.get("records")
    if not isinstance(refs, list) or len(refs) != 3:
        raise KnowledgeReadyCandidateDraftError("A50.7 must not mutate the three-record canonical index")
    ids: set[str] = set()
    domains: set[str] = set()
    for relative in refs:
        if not isinstance(relative, str) or not relative.strip() or relative.startswith("drafts/"):
            raise KnowledgeReadyCandidateDraftError("canonical index must not reference draft records")
        record_path = (knowledge_root / relative).resolve()
        if not record_path.is_relative_to(knowledge_root.resolve()) or not record_path.is_file():
            raise KnowledgeReadyCandidateDraftError(f"invalid canonical record path: {relative}")
        record = KnowledgeRecord.model_validate(_load_json(record_path))
        ids.add(record.id)
        domains.update(record.applicable_domains)
    if len(ids) != 3:
        raise KnowledgeReadyCandidateDraftError("canonical seed must contain three unique record ids")
    return [str(value) for value in refs], ids, domains


def _shadow_retriever(
    *,
    knowledge_root: Path,
    canonical_refs: list[str],
    draft_record_paths: list[Path],
) -> tuple[KnowledgeRetriever, int]:
    with TemporaryDirectory(prefix="a50-7-shadow-") as temp_dir:
        temp_workspace = Path(temp_dir)
        shadow_root = temp_workspace / "skills_UIUX/knowledge"
        shutil.copytree(knowledge_root, shadow_root)
        draft_refs = [
            str(path.resolve().relative_to(knowledge_root.resolve())).replace("\\", "/")
            for path in draft_record_paths
        ]
        shadow_refs = [*canonical_refs, *draft_refs]
        (shadow_root / "shadow-index.json").write_text(
            json.dumps(
                {"schema_version": "knowledge-index.v1", "records": shadow_refs},
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        index = KnowledgeIndex(shadow_root, manifest_name="shadow-index.json")
        indexed, _digest = index.load()
        # The retriever must be consumed while the temporary workspace exists, so return
        # the index data through a small closure-like materialization instead of the object.
        # This helper is intentionally unused directly; evaluation builds queries below.
        raise AssertionError("_shadow_retriever should not be called directly")


def evaluate_knowledge_ready_candidate_drafts(
    corpus_path: Path,
    *,
    proposal_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
    benchmarks_root: Path,
) -> KnowledgeReadyCandidateDraftReport:
    raw_bytes = Path(corpus_path).read_bytes()
    try:
        payload = json.loads(raw_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise KnowledgeReadyCandidateDraftError(f"cannot parse A50.7 corpus: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeReadyCandidateDraftError("A50.7 corpus must be an object")
    expected_top = {"schema_version", "benchmark_id", "version", "checked_on", "scope", "governance", "cases"}
    if set(payload) != expected_top:
        raise KnowledgeReadyCandidateDraftError("A50.7 top-level keys do not match v1 contract")
    if payload["schema_version"] != SCHEMA_VERSION or payload["scope"] != EXPECTED_SCOPE:
        raise KnowledgeReadyCandidateDraftError("A50.7 schema/scope drifted")
    governance = _validate_governance(payload["governance"])

    proposal_report = evaluate_knowledge_expansion_proposal(
        proposal_path=proposal_path,
        workspace_root=workspace_root,
        knowledge_root=knowledge_root,
        benchmarks_root=benchmarks_root,
    )
    if (proposal_report.ready_count, proposal_report.hold_count, proposal_report.reject_count) != (2, 1, 0):
        raise KnowledgeReadyCandidateDraftError("A50.6 proposal must still be 2 READY / 1 HOLD / 0 REJECT")

    proposal = _load_json(proposal_path)
    proposal_candidates = {str(item["candidate_id"]): item for item in proposal.get("candidates", [])}
    genai = proposal_candidates.get("a50-6-genai-nist")
    genai_hold_preserved = bool(genai and genai.get("proposal_status") == governance["genai_candidate_status"])
    if not genai_hold_preserved:
        raise KnowledgeReadyCandidateDraftError("GenAI/NIST HOLD boundary drifted")

    canonical_refs, canonical_ids, canonical_domains = _canonical_index(knowledge_root)
    raw_cases = payload["cases"]
    if not isinstance(raw_cases, list) or len(raw_cases) != governance["draft_record_expected_count"]:
        raise KnowledgeReadyCandidateDraftError("A50.7 must contain exactly two draft cases")
    cases = [_validate_case(case) for case in raw_cases]
    if len({case["id"] for case in cases}) != len(cases):
        raise KnowledgeReadyCandidateDraftError("duplicate A50.7 case id")

    draft_dir = knowledge_root / "drafts/records"
    actual_draft_files = sorted(draft_dir.glob("*.json")) if draft_dir.is_dir() else []
    if len(actual_draft_files) != governance["draft_record_expected_count"]:
        raise KnowledgeReadyCandidateDraftError("A50.7 drafts directory must contain exactly the two READY record drafts")

    draft_records: dict[str, KnowledgeRecord] = {}
    draft_paths: dict[str, Path] = {}
    content_by_record: dict[str, str] = {}
    case_by_record: dict[str, dict[str, Any]] = {}
    for case in cases:
        record_path = _safe_workspace_path(workspace_root, str(case["draft_record_path"]), purpose="draft record")
        content_path = _safe_workspace_path(workspace_root, str(case["draft_content_path"]), purpose="draft content")
        if not record_path.is_file() or not content_path.is_file():
            raise KnowledgeReadyCandidateDraftError(f"draft files missing for {case['id']}")
        if not record_path.is_relative_to((knowledge_root / "drafts/records").resolve()):
            raise KnowledgeReadyCandidateDraftError("draft record must stay under skills_UIUX/knowledge/drafts/records")
        if not content_path.is_relative_to((knowledge_root / "drafts/content").resolve()):
            raise KnowledgeReadyCandidateDraftError("draft content must stay under skills_UIUX/knowledge/drafts/content")
        record = KnowledgeRecord.model_validate(_load_json(record_path))
        if record.id != case["expected_record_id"]:
            raise KnowledgeReadyCandidateDraftError(f"record id mismatch for {case['id']}")
        if record.id in canonical_ids or str(record_path.relative_to(knowledge_root)).replace("\\", "/") in canonical_refs:
            raise KnowledgeReadyCandidateDraftError(f"draft leaked into canonical index: {record.id}")
        if record.id in draft_records:
            raise KnowledgeReadyCandidateDraftError(f"duplicate draft record id: {record.id}")
        if record.applicable_domains != [case["domain"]] or case["domain"] in canonical_domains:
            raise KnowledgeReadyCandidateDraftError(f"draft domain is not isolated: {record.id}")
        if case["stage"] not in record.applicable_stages:
            raise KnowledgeReadyCandidateDraftError(f"draft stage mismatch: {record.id}")
        if record.content_ref != case["draft_content_path"]:
            raise KnowledgeReadyCandidateDraftError(f"content_ref mismatch: {record.id}")
        parsed = urlparse(record.source_ref)
        if parsed.scheme != "https" or parsed.hostname != case["expected_source_host"]:
            raise KnowledgeReadyCandidateDraftError(f"unexpected source host: {record.id}")
        if record.updated_at != payload["checked_on"] or record.freshness.value != "versioned":
            raise KnowledgeReadyCandidateDraftError(f"draft freshness metadata drifted: {record.id}")
        for field in ("advisory_only", "current_run_evidence", "authority_effect", "gate_effect", "evidence_effect", "release_effect"):
            expected = True if field == "advisory_only" else False if field == "current_run_evidence" else "none"
            if getattr(record, field) != expected:
                raise KnowledgeReadyCandidateDraftError(f"draft authority boundary drifted: {record.id}.{field}")

        candidate = proposal_candidates.get(str(case["candidate_id"]))
        if not candidate or candidate.get("proposal_status") != "READY_FOR_CONTENT_DRAFT":
            raise KnowledgeReadyCandidateDraftError(f"case does not map to READY A50.6 candidate: {case['id']}")
        if candidate.get("proposed_record_id") != record.id:
            raise KnowledgeReadyCandidateDraftError(f"proposal record id mismatch: {record.id}")
        if candidate.get("source_ref") != record.source_ref or candidate.get("source_version") != record.version:
            raise KnowledgeReadyCandidateDraftError(f"proposal provenance mismatch: {record.id}")
        if candidate.get("domain") != case["domain"]:
            raise KnowledgeReadyCandidateDraftError(f"proposal domain mismatch: {record.id}")

        content = content_path.read_text(encoding="utf-8").strip()
        if not content:
            raise KnowledgeReadyCandidateDraftError(f"draft content is empty: {record.id}")
        draft_records[record.id] = record
        draft_paths[record.id] = record_path
        content_by_record[record.id] = content
        case_by_record[record.id] = case

    ready_ids = {
        str(item["proposed_record_id"])
        for item in proposal.get("candidates", [])
        if item.get("proposal_status") == "READY_FOR_CONTENT_DRAFT"
    }
    if set(draft_records) != ready_ids:
        raise KnowledgeReadyCandidateDraftError("A50.7 drafts must cover exactly the two READY A50.6 candidates")
    if str(genai.get("proposed_record_id")) in draft_records:
        raise KnowledgeReadyCandidateDraftError("GenAI/NIST HOLD candidate must not have an A50.7 draft")

    results: list[DraftCaseResult] = []
    with TemporaryDirectory(prefix="a50-7-shadow-") as temp_dir:
        temp_workspace = Path(temp_dir)
        shadow_root = temp_workspace / "skills_UIUX/knowledge"
        shutil.copytree(knowledge_root, shadow_root)
        draft_refs = [
            str(draft_paths[record_id].resolve().relative_to(knowledge_root.resolve())).replace("\\", "/")
            for record_id in sorted(draft_paths)
        ]
        shadow_refs = [*canonical_refs, *draft_refs]
        (shadow_root / "shadow-index.json").write_text(
            json.dumps({"schema_version": "knowledge-index.v1", "records": shadow_refs}, indent=2) + "\n",
            encoding="utf-8",
        )
        shadow_index = KnowledgeIndex(shadow_root, manifest_name="shadow-index.json")
        shadow_records, _shadow_hash = shadow_index.load()
        if len(shadow_records) != governance["shadow_index_expected_count"]:
            raise KnowledgeReadyCandidateDraftError("shadow index must contain three canonical + two draft records")
        retriever = KnowledgeRetriever(shadow_index)

        for record_id in sorted(draft_records):
            case = case_by_record[record_id]
            record = draft_records[record_id]
            content = content_by_record[record_id]
            content_normalized = _normalized_text(content)
            actionable_delta = all(
                _normalized_text(str(concept)) in content_normalized
                for concept in case["required_actionable_concepts"]
            )

            knowledge_lines = _substantive_lines(content)
            duplicated_lines: set[str] = set()
            for relative in case["related_skill_paths"]:
                skill_path = _safe_workspace_path(workspace_root, str(relative), purpose="related skill")
                if not skill_path.is_file():
                    raise KnowledgeReadyCandidateDraftError(f"related skill path is invalid: {relative}")
                duplicated_lines.update(knowledge_lines.intersection(_substantive_lines(skill_path.read_text(encoding="utf-8"))))
            skill_duplication_clear = not duplicated_lines

            candidate = proposal_candidates[str(case["candidate_id"])]
            proposal_alignment_clear = (
                candidate["proposal_status"] == "READY_FOR_CONTENT_DRAFT"
                and candidate["proposed_record_id"] == record.id
                and candidate["domain"] == case["domain"]
                and candidate["source_ref"] == record.source_ref
                and candidate["source_version"] == record.version
            )
            canonical_unindexed = record.id not in canonical_ids and all(
                not ref.startswith("drafts/") for ref in canonical_refs
            )

            retrieval = retriever.retrieve(
                KnowledgeQuery(
                    as_of=payload["checked_on"],
                    domains=[case["domain"]],
                    stages=[case["stage"]],
                    terms=[str(value) for value in case["terms"]],
                    limit=5,
                    max_item_chars=4_000,
                    max_total_chars=8_000,
                )
            )
            actual_ids = [hit.record.id for hit in retrieval.hits]
            hit = next((item for item in retrieval.hits if item.record.id == record.id), None)
            domain_specificity = record.applicable_domains == [case["domain"]] and actual_ids == [record.id]
            retrieval_noise_clear = (
                actual_ids == [record.id]
                and sum(item.reason == "domain_mismatch" for item in retrieval.exclusions) == 4
                and retrieval.vector_search_used is False
            )
            parsed = urlparse(record.source_ref)
            provenance_clear = (
                parsed.scheme == "https"
                and parsed.hostname == case["expected_source_host"]
                and bool(record.version.strip())
                and record.updated_at == payload["checked_on"]
                and record.current_run_evidence is False
                and record.authority_effect == "none"
                and record.gate_effect == "none"
                and record.evidence_effect == "none"
                and record.release_effect == "none"
            )
            context_chars = hit.delivered_content_chars if hit else 0
            context_budget_clear = 250 <= context_chars <= 4_000

            checks = {
                "actionable_delta": actionable_delta,
                "proposal_alignment_clear": proposal_alignment_clear,
                "canonical_unindexed": canonical_unindexed,
                "domain_specificity": domain_specificity,
                "skill_duplication_clear": skill_duplication_clear,
                "retrieval_noise_clear": retrieval_noise_clear,
                "provenance_clear": provenance_clear,
                "context_budget_clear": context_budget_clear,
            }
            decision = KEEP_DRAFT if all(checks.values()) else REVISE_DRAFT
            passed = decision == case["expected_proxy_decision"] and all(checks.values())
            failed = [name for name, ok in checks.items() if not ok]
            results.append(
                DraftCaseResult(
                    case_id=str(case["id"]),
                    candidate_id=str(case["candidate_id"]),
                    record_id=record.id,
                    decision=decision,
                    passed=passed,
                    actionable_delta=actionable_delta,
                    proposal_alignment_clear=proposal_alignment_clear,
                    canonical_unindexed=canonical_unindexed,
                    domain_specificity=domain_specificity,
                    skill_duplication_clear=skill_duplication_clear,
                    retrieval_noise_clear=retrieval_noise_clear,
                    provenance_clear=provenance_clear,
                    context_budget_clear=context_budget_clear,
                    context_chars=context_chars,
                    message=(
                        "draft proxy boundaries satisfied; canonical acceptance remains blocked"
                        if passed
                        else "failed: " + ", ".join(failed or ["decision_mismatch"])
                    ),
                )
            )

    return KnowledgeReadyCandidateDraftReport(
        benchmark_id=str(payload["benchmark_id"]),
        version=str(payload["version"]),
        corpus_hash=hashlib.sha256(raw_bytes).hexdigest()[:16],
        canonical_index_count=len(canonical_refs),
        draft_record_count=len(draft_records),
        shadow_index_count=len(canonical_refs) + len(draft_records),
        keep_draft_count=sum(item.decision == KEEP_DRAFT for item in results),
        revise_draft_count=sum(item.decision == REVISE_DRAFT for item in results),
        genai_hold_preserved=genai_hold_preserved,
        index_mutation_allowed=False,
        canonical_acceptance_allowed=False,
        vector_search_change_allowed=False,
        human_usefulness_claimed=False,
        cases=tuple(results),
    )

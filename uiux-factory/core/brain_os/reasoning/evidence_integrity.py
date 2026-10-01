from __future__ import annotations

from collections.abc import Iterable, Mapping
from enum import Enum

from pydantic import Field, model_validator

from core.brain_os.contracts import BrainContractModel
from core.brain_os.critique_contracts import (
    CritiqueIssue,
    CritiqueIssueStatus,
    RepairDirective,
    RepairLink,
    RetestRequirement,
    RetestStatus,
    RootCause,
)
from core.brain_os.reasoning.evidence_graph import (
    EvidenceGraph,
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceNodeKind,
    EvidenceRelation,
)


EVIDENCE_NODE_KINDS = {
    EvidenceNodeKind.RUNTIME_EVIDENCE,
    EvidenceNodeKind.PROVENANCE_EVIDENCE,
    EvidenceNodeKind.RELEASE_EVIDENCE,
}


class IntegritySeverity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


class IntegrityCode(str, Enum):
    CANONICAL_REF_MISSING = "CANONICAL_REF_MISSING"
    CANONICAL_EVIDENCE_MISSING = "CANONICAL_EVIDENCE_MISSING"
    CANONICAL_PROJECTION_MISMATCH = "CANONICAL_PROJECTION_MISMATCH"
    DUPLICATE_CANONICAL_REF = "DUPLICATE_CANONICAL_REF"
    BRAIN_TRUST_CLAIM = "BRAIN_TRUST_CLAIM"
    NON_RUNTIME_TRUST_OVERRIDE = "NON_RUNTIME_TRUST_OVERRIDE"
    VERIFIED_BY_NON_EVIDENCE = "VERIFIED_BY_NON_EVIDENCE"
    UNTRUSTED_RUNTIME_VERIFICATION = "UNTRUSTED_RUNTIME_VERIFICATION"
    LINEAGE_OBJECT_MISSING = "LINEAGE_OBJECT_MISSING"
    LINEAGE_NODE_MISSING = "LINEAGE_NODE_MISSING"
    LINEAGE_EDGE_MISSING = "LINEAGE_EDGE_MISSING"
    LINEAGE_REFERENCE_MISMATCH = "LINEAGE_REFERENCE_MISMATCH"
    EVIDENCE_REF_UNRESOLVED = "EVIDENCE_REF_UNRESOLVED"
    RETEST_UNTRUSTED_EVIDENCE = "RETEST_UNTRUSTED_EVIDENCE"
    LINEAGE_INCOMPLETE = "LINEAGE_INCOMPLETE"


class EvidenceIntegrityFinding(BrainContractModel):
    code: IntegrityCode
    severity: IntegritySeverity
    subject_ref: str = Field(min_length=1, max_length=512)
    detail: str = Field(min_length=1, max_length=4000)


class EvidenceIntegrityReport(BrainContractModel):
    """Advisory integrity result; never a runtime or release gate result."""

    schema_version: str = "brain-evidence-integrity.v1"
    graph_id: str = Field(min_length=1, max_length=256)
    integrity_valid: bool
    lineage_complete: bool
    findings: list[EvidenceIntegrityFinding] = Field(default_factory=list, max_length=1000)

    @model_validator(mode="after")
    def _validate_flags(self) -> "EvidenceIntegrityReport":
        has_error = any(item.severity is IntegritySeverity.ERROR for item in self.findings)
        if self.integrity_valid == has_error:
            raise ValueError("integrity_valid must be false exactly when ERROR findings exist")
        return self


def _finding(
    code: IntegrityCode,
    subject_ref: str,
    detail: str,
    *,
    severity: IntegritySeverity = IntegritySeverity.ERROR,
) -> EvidenceIntegrityFinding:
    return EvidenceIntegrityFinding(
        code=code,
        severity=severity,
        subject_ref=subject_ref,
        detail=detail,
    )


def _report(graph: EvidenceGraph, findings: list[EvidenceIntegrityFinding], *, lineage_complete: bool) -> EvidenceIntegrityReport:
    has_error = any(item.severity is IntegritySeverity.ERROR for item in findings)
    return EvidenceIntegrityReport(
        graph_id=graph.graph_id,
        integrity_valid=not has_error,
        lineage_complete=lineage_complete and not has_error,
        findings=findings,
    )


def _node_map(graph: EvidenceGraph) -> dict[str, EvidenceGraphNode]:
    return {node.node_id: node for node in graph.nodes}


def _edge_keys(graph: EvidenceGraph) -> set[tuple[str, EvidenceRelation, str]]:
    return {(edge.source_node_id, edge.relation, edge.target_node_id) for edge in graph.edges}


def _evidence_by_canonical_ref(graph: EvidenceGraph) -> tuple[dict[str, EvidenceGraphNode], list[EvidenceIntegrityFinding]]:
    output: dict[str, EvidenceGraphNode] = {}
    findings: list[EvidenceIntegrityFinding] = []
    for node in graph.nodes:
        if node.kind not in EVIDENCE_NODE_KINDS or not node.canonical_ref:
            continue
        previous = output.get(node.canonical_ref)
        if previous is not None and previous.node_id != node.node_id:
            findings.append(_finding(
                IntegrityCode.DUPLICATE_CANONICAL_REF,
                node.canonical_ref,
                f"canonical evidence ref is represented by multiple graph nodes: {previous.node_id}, {node.node_id}",
            ))
            continue
        output[node.canonical_ref] = node
    return output, findings


def validate_evidence_integrity(
    graph: EvidenceGraph,
    canonical_index: Mapping[str, EvidenceGraphNode],
) -> EvidenceIntegrityReport:
    """Validate graph projections against adapter-produced canonical evidence nodes.

    `canonical_index` must be produced from the existing evidence owners through
    `core.brain_os.adapters.evidence.canonical_evidence_index`. This validator only
    compares identity/metadata and relationship safety. It cannot create trust, satisfy
    a runtime gate or determine release readiness.
    """

    findings: list[EvidenceIntegrityFinding] = []
    nodes = _node_map(graph)
    _, duplicate_findings = _evidence_by_canonical_ref(graph)
    findings.extend(duplicate_findings)

    for node in graph.nodes:
        if node.kind in EVIDENCE_NODE_KINDS:
            if not node.canonical_ref:
                findings.append(_finding(
                    IntegrityCode.CANONICAL_REF_MISSING,
                    node.node_id,
                    "canonical evidence nodes must preserve the canonical evidence reference",
                ))
                continue

            expected = canonical_index.get(node.node_id)
            if expected is None:
                findings.append(_finding(
                    IntegrityCode.CANONICAL_EVIDENCE_MISSING,
                    node.node_id,
                    "graph evidence node has no matching adapter projection from canonical evidence owners",
                ))
                continue

            if node != expected:
                findings.append(_finding(
                    IntegrityCode.CANONICAL_PROJECTION_MISMATCH,
                    node.node_id,
                    "graph evidence metadata differs from the canonical adapter projection",
                ))

            if node.kind is not EvidenceNodeKind.RUNTIME_EVIDENCE and node.canonical_trusted_flag is not None:
                findings.append(_finding(
                    IntegrityCode.NON_RUNTIME_TRUST_OVERRIDE,
                    node.node_id,
                    "only runtime EvidenceRecord projections may carry the canonical trusted flag; provenance/release nodes do not gain Brain-owned trust",
                ))
        elif node.canonical_trusted_flag is not None:
            findings.append(_finding(
                IntegrityCode.BRAIN_TRUST_CLAIM,
                node.node_id,
                "reasoning/control nodes cannot carry a canonical trusted-evidence flag",
            ))

    for edge in graph.edges:
        if edge.relation is not EvidenceRelation.VERIFIED_BY:
            continue
        target = nodes[edge.target_node_id]
        if target.kind not in EVIDENCE_NODE_KINDS:
            findings.append(_finding(
                IntegrityCode.VERIFIED_BY_NON_EVIDENCE,
                edge.edge_id,
                f"VERIFIED_BY target {target.node_id} is not a canonical evidence node",
            ))
            continue
        if target.kind is EvidenceNodeKind.RUNTIME_EVIDENCE and target.canonical_trusted_flag is not True:
            findings.append(_finding(
                IntegrityCode.UNTRUSTED_RUNTIME_VERIFICATION,
                edge.edge_id,
                f"runtime evidence {target.canonical_ref or target.node_id} is untrusted and cannot be represented as verification",
            ))

    return _report(graph, findings, lineage_complete=True)


def _require_graph_node(
    node_id: str,
    kind: EvidenceNodeKind,
    nodes: Mapping[str, EvidenceGraphNode],
    findings: list[EvidenceIntegrityFinding],
) -> bool:
    node = nodes.get(node_id)
    if node is None:
        findings.append(_finding(
            IntegrityCode.LINEAGE_NODE_MISSING,
            node_id,
            f"required lineage node is missing; expected kind {kind.value}",
        ))
        return False
    if node.kind is not kind:
        findings.append(_finding(
            IntegrityCode.LINEAGE_REFERENCE_MISMATCH,
            node_id,
            f"lineage node kind is {node.kind.value}; expected {kind.value}",
        ))
        return False
    return True


def _require_edge(
    source: str,
    relation: EvidenceRelation,
    target: str,
    edge_keys: set[tuple[str, EvidenceRelation, str]],
    findings: list[EvidenceIntegrityFinding],
) -> None:
    if (source, relation, target) not in edge_keys:
        findings.append(_finding(
            IntegrityCode.LINEAGE_EDGE_MISSING,
            f"{source}->{target}",
            f"required {relation.value} relationship is missing",
        ))


def _resolve_evidence_refs(
    refs: Iterable[str],
    evidence_by_ref: Mapping[str, EvidenceGraphNode],
    findings: list[EvidenceIntegrityFinding],
    *,
    subject_ref: str,
    terminal_retest: bool = False,
) -> list[EvidenceGraphNode]:
    resolved: list[EvidenceGraphNode] = []
    for ref in refs:
        node = evidence_by_ref.get(ref)
        if node is None:
            findings.append(_finding(
                IntegrityCode.EVIDENCE_REF_UNRESOLVED,
                subject_ref,
                f"evidence reference does not resolve to a canonical evidence node: {ref}",
            ))
            continue
        resolved.append(node)
        if terminal_retest and node.kind is EvidenceNodeKind.RUNTIME_EVIDENCE and node.canonical_trusted_flag is not True:
            findings.append(_finding(
                IntegrityCode.RETEST_UNTRUSTED_EVIDENCE,
                subject_ref,
                f"terminal retest references untrusted runtime evidence: {ref}",
            ))
    return resolved


def validate_repair_lineage_integrity(
    graph: EvidenceGraph,
    repair_link: RepairLink,
    *,
    issues: Iterable[CritiqueIssue],
    root_causes: Iterable[RootCause],
    directives: Iterable[RepairDirective],
    retests: Iterable[RetestRequirement],
) -> EvidenceIntegrityReport:
    """Validate one repair chain against graph relationships and evidence references.

    This checks traceability only. A complete, valid lineage does not mean a product
    gate passed, a repair executed, a user outcome improved or a release is ready.
    """

    findings: list[EvidenceIntegrityFinding] = []
    nodes = _node_map(graph)
    edge_keys = _edge_keys(graph)
    evidence_by_ref, duplicate_findings = _evidence_by_canonical_ref(graph)
    findings.extend(duplicate_findings)

    issue_map = {item.id: item for item in issues}
    cause_map = {item.id: item for item in root_causes}
    directive_map = {item.id: item for item in directives}
    retest_map = {item.id: item for item in retests}

    expected_sets = (
        (repair_link.issue_ids, issue_map, "critique issue"),
        (repair_link.root_cause_ids, cause_map, "root cause"),
        (repair_link.repair_directive_ids, directive_map, "repair directive"),
        (repair_link.retest_requirement_ids, retest_map, "retest requirement"),
    )
    for refs, object_map, label in expected_sets:
        for ref in refs:
            if ref not in object_map:
                findings.append(_finding(
                    IntegrityCode.LINEAGE_OBJECT_MISSING,
                    ref,
                    f"RepairLink references a missing {label} object",
                ))

    for issue_id in repair_link.issue_ids:
        _require_graph_node(f"critique:{issue_id}", EvidenceNodeKind.CRITIQUE_ISSUE, nodes, findings)
    for cause_id in repair_link.root_cause_ids:
        _require_graph_node(f"root:{cause_id}", EvidenceNodeKind.ROOT_CAUSE, nodes, findings)
    for directive_id in repair_link.repair_directive_ids:
        _require_graph_node(f"repair:{directive_id}", EvidenceNodeKind.REPAIR_DIRECTIVE, nodes, findings)
    for retest_id in repair_link.retest_requirement_ids:
        _require_graph_node(f"retest:{retest_id}", EvidenceNodeKind.RETEST_REQUIREMENT, nodes, findings)

    for cause_id in repair_link.root_cause_ids:
        cause = cause_map.get(cause_id)
        if cause is None:
            continue
        for issue_id in cause.issue_ids:
            if issue_id not in repair_link.issue_ids:
                findings.append(_finding(
                    IntegrityCode.LINEAGE_REFERENCE_MISMATCH,
                    cause_id,
                    f"root cause references issue {issue_id} outside RepairLink",
                ))
                continue
            _require_edge(
                f"critique:{issue_id}",
                EvidenceRelation.CAUSED_BY,
                f"root:{cause_id}",
                edge_keys,
                findings,
            )

    for directive_id in repair_link.repair_directive_ids:
        directive = directive_map.get(directive_id)
        if directive is None:
            continue
        for issue_id in directive.issue_ids:
            if issue_id not in repair_link.issue_ids:
                findings.append(_finding(
                    IntegrityCode.LINEAGE_REFERENCE_MISMATCH,
                    directive_id,
                    f"repair directive references issue {issue_id} outside RepairLink",
                ))
        for cause_id in directive.root_cause_ids:
            if cause_id not in repair_link.root_cause_ids:
                findings.append(_finding(
                    IntegrityCode.LINEAGE_REFERENCE_MISMATCH,
                    directive_id,
                    f"repair directive references root cause {cause_id} outside RepairLink",
                ))
                continue
            _require_edge(
                f"root:{cause_id}",
                EvidenceRelation.REPAIRED_BY,
                f"repair:{directive_id}",
                edge_keys,
                findings,
            )

    lineage_complete = True
    for retest_id in repair_link.retest_requirement_ids:
        retest = retest_map.get(retest_id)
        if retest is None:
            lineage_complete = False
            continue
        if retest.repair_directive_id not in repair_link.repair_directive_ids:
            findings.append(_finding(
                IntegrityCode.LINEAGE_REFERENCE_MISMATCH,
                retest_id,
                f"retest references repair directive {retest.repair_directive_id} outside RepairLink",
            ))
            lineage_complete = False
            continue

        _require_edge(
            f"repair:{retest.repair_directive_id}",
            EvidenceRelation.REQUIRES_RETEST,
            f"retest:{retest_id}",
            edge_keys,
            findings,
        )

        if retest.status is RetestStatus.PENDING:
            findings.append(_finding(
                IntegrityCode.LINEAGE_INCOMPLETE,
                retest_id,
                "retest is still pending; end-to-end repair lineage is not complete",
                severity=IntegritySeverity.WARNING,
            ))
            lineage_complete = False
        elif retest.status is RetestStatus.BLOCKED:
            findings.append(_finding(
                IntegrityCode.LINEAGE_INCOMPLETE,
                retest_id,
                "retest is blocked; end-to-end repair lineage is not complete",
                severity=IntegritySeverity.WARNING,
            ))
            lineage_complete = False
        elif retest.status in {RetestStatus.PASSED, RetestStatus.FAILED}:
            evidence_nodes = _resolve_evidence_refs(
                retest.evidence_refs,
                evidence_by_ref,
                findings,
                subject_ref=retest_id,
                terminal_retest=True,
            )
            if not evidence_nodes:
                lineage_complete = False
            for evidence_node in evidence_nodes:
                _require_edge(
                    f"retest:{retest_id}",
                    EvidenceRelation.VERIFIED_BY,
                    evidence_node.node_id,
                    edge_keys,
                    findings,
                )

    for issue_id in repair_link.issue_ids:
        issue = issue_map.get(issue_id)
        if issue is None:
            continue
        if issue.status in {CritiqueIssueStatus.CONFIRMED, CritiqueIssueStatus.RESOLVED}:
            _resolve_evidence_refs(
                issue.evidence_refs,
                evidence_by_ref,
                findings,
                subject_ref=issue_id,
            )
        if issue.status is CritiqueIssueStatus.RESOLVED:
            for retest_ref in issue.retest_refs:
                if retest_ref not in repair_link.retest_requirement_ids:
                    findings.append(_finding(
                        IntegrityCode.LINEAGE_REFERENCE_MISMATCH,
                        issue_id,
                        f"resolved critique references retest {retest_ref} outside RepairLink",
                    ))
                    lineage_complete = False

    return _report(graph, findings, lineage_complete=lineage_complete)

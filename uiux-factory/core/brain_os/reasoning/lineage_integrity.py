from __future__ import annotations

from core.brain_os.reasoning.evidence_graph import (
    EvidenceGraph,
    EvidenceGraphNode,
    EvidenceNodeKind,
    EvidenceRelation,
)
from core.brain_os.reasoning.evidence_integrity import (
    EVIDENCE_NODE_KINDS,
    EvidenceIntegrityFinding,
    EvidenceIntegrityReport,
    IntegrityCode,
    IntegritySeverity,
)


LINEAGE_STEPS: tuple[tuple[EvidenceNodeKind, frozenset[EvidenceRelation], EvidenceNodeKind | None], ...] = (
    (EvidenceNodeKind.TASK, frozenset({EvidenceRelation.JUSTIFIES}), EvidenceNodeKind.HYPOTHESIS),
    (
        EvidenceNodeKind.HYPOTHESIS,
        frozenset({EvidenceRelation.SUPPORTS, EvidenceRelation.CONTRADICTS}),
        EvidenceNodeKind.DECISION,
    ),
    (EvidenceNodeKind.DECISION, frozenset({EvidenceRelation.REFERENCES}), EvidenceNodeKind.CRITIQUE_ISSUE),
    (EvidenceNodeKind.CRITIQUE_ISSUE, frozenset({EvidenceRelation.CAUSED_BY}), EvidenceNodeKind.ROOT_CAUSE),
    (EvidenceNodeKind.ROOT_CAUSE, frozenset({EvidenceRelation.REPAIRED_BY}), EvidenceNodeKind.REPAIR_DIRECTIVE),
    (
        EvidenceNodeKind.REPAIR_DIRECTIVE,
        frozenset({EvidenceRelation.REQUIRES_RETEST}),
        EvidenceNodeKind.RETEST_REQUIREMENT,
    ),
    (EvidenceNodeKind.RETEST_REQUIREMENT, frozenset({EvidenceRelation.VERIFIED_BY}), None),
)


def _error(code: IntegrityCode, subject_ref: str, detail: str) -> EvidenceIntegrityFinding:
    return EvidenceIntegrityFinding(
        code=code,
        severity=IntegritySeverity.ERROR,
        subject_ref=subject_ref,
        detail=detail,
    )


def _warning(code: IntegrityCode, subject_ref: str, detail: str) -> EvidenceIntegrityFinding:
    return EvidenceIntegrityFinding(
        code=code,
        severity=IntegritySeverity.WARNING,
        subject_ref=subject_ref,
        detail=detail,
    )


def validate_end_to_end_lineage(graph: EvidenceGraph) -> EvidenceIntegrityReport:
    """Require at least one complete typed path from task framing to canonical evidence.

    This proves relationship completeness only. It does not prove the design is correct,
    the repair executed, the retest passed a runtime gate or the release is ready.
    """

    nodes = {node.node_id: node for node in graph.nodes}
    findings: list[EvidenceIntegrityFinding] = []
    task = nodes.get(graph.task_ref)
    if task is None:
        findings.append(_error(
            IntegrityCode.LINEAGE_NODE_MISSING,
            graph.task_ref,
            "graph task_ref does not resolve to a graph node",
        ))
        return EvidenceIntegrityReport(
            graph_id=graph.graph_id,
            integrity_valid=False,
            lineage_complete=False,
            findings=findings,
        )
    if task.kind is not EvidenceNodeKind.TASK:
        findings.append(_error(
            IntegrityCode.LINEAGE_REFERENCE_MISMATCH,
            graph.task_ref,
            f"graph task_ref points to {task.kind.value}; expected TASK",
        ))
        return EvidenceIntegrityReport(
            graph_id=graph.graph_id,
            integrity_valid=False,
            lineage_complete=False,
            findings=findings,
        )

    outgoing: dict[str, list[tuple[EvidenceRelation, EvidenceGraphNode]]] = {}
    for edge in graph.edges:
        outgoing.setdefault(edge.source_node_id, []).append((edge.relation, nodes[edge.target_node_id]))

    frontier = [task]
    for source_kind, relations, target_kind in LINEAGE_STEPS:
        next_frontier: list[EvidenceGraphNode] = []
        for current in frontier:
            if current.kind is not source_kind:
                continue
            for relation, target in outgoing.get(current.node_id, []):
                if relation not in relations:
                    continue
                if target_kind is None:
                    if target.kind not in EVIDENCE_NODE_KINDS:
                        continue
                    if target.kind is EvidenceNodeKind.RUNTIME_EVIDENCE and target.canonical_trusted_flag is not True:
                        findings.append(_error(
                            IntegrityCode.UNTRUSTED_RUNTIME_VERIFICATION,
                            current.node_id,
                            f"end-to-end lineage terminates in untrusted runtime evidence {target.canonical_ref or target.node_id}",
                        ))
                        continue
                    next_frontier.append(target)
                elif target.kind is target_kind:
                    next_frontier.append(target)

        if not next_frontier:
            findings.append(_warning(
                IntegrityCode.LINEAGE_INCOMPLETE,
                source_kind.value,
                f"no complete {source_kind.value} relationship step reaches the expected next lineage kind",
            ))
            return EvidenceIntegrityReport(
                graph_id=graph.graph_id,
                integrity_valid=not any(item.severity is IntegritySeverity.ERROR for item in findings),
                lineage_complete=False,
                findings=findings,
            )
        frontier = next_frontier

    has_error = any(item.severity is IntegritySeverity.ERROR for item in findings)
    return EvidenceIntegrityReport(
        graph_id=graph.graph_id,
        integrity_valid=not has_error,
        lineage_complete=not has_error,
        findings=findings,
    )

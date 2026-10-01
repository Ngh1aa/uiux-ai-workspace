from __future__ import annotations

from core.brain_os.adapters.evidence import runtime_evidence_node
from core.brain_os.reasoning.evidence_graph import (
    EvidenceGraph,
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceNodeKind,
    EvidenceRelation,
)
from core.brain_os.reasoning.evidence_integrity import IntegrityCode
from core.brain_os.reasoning.lineage_integrity import validate_end_to_end_lineage
from core.runtime.flow_os.evidence import EvidenceRecord, provider_claim_records


def _node(node_id: str, kind: EvidenceNodeKind) -> EvidenceGraphNode:
    return EvidenceGraphNode(node_id=node_id, kind=kind, canonical_ref=node_id, label=node_id)


def _graph(evidence_node: EvidenceGraphNode, *, omit_edge: str | None = None) -> EvidenceGraph:
    nodes = [
        _node("task:T-1", EvidenceNodeKind.TASK),
        _node("hypothesis:H-1", EvidenceNodeKind.HYPOTHESIS),
        _node("decision:D-1", EvidenceNodeKind.DECISION),
        _node("critique:C-1", EvidenceNodeKind.CRITIQUE_ISSUE),
        _node("root:RC-1", EvidenceNodeKind.ROOT_CAUSE),
        _node("repair:RP-1", EvidenceNodeKind.REPAIR_DIRECTIVE),
        _node("retest:RT-1", EvidenceNodeKind.RETEST_REQUIREMENT),
        evidence_node,
    ]
    edges = [
        EvidenceGraphEdge(edge_id="e1", source_node_id="task:T-1", relation=EvidenceRelation.JUSTIFIES, target_node_id="hypothesis:H-1", rationale="task frames hypothesis"),
        EvidenceGraphEdge(edge_id="e2", source_node_id="hypothesis:H-1", relation=EvidenceRelation.SUPPORTS, target_node_id="decision:D-1", rationale="hypothesis informs decision"),
        EvidenceGraphEdge(edge_id="e3", source_node_id="decision:D-1", relation=EvidenceRelation.REFERENCES, target_node_id="critique:C-1", rationale="decision is reviewed"),
        EvidenceGraphEdge(edge_id="e4", source_node_id="critique:C-1", relation=EvidenceRelation.CAUSED_BY, target_node_id="root:RC-1", rationale="issue maps to root cause"),
        EvidenceGraphEdge(edge_id="e5", source_node_id="root:RC-1", relation=EvidenceRelation.REPAIRED_BY, target_node_id="repair:RP-1", rationale="root cause maps to repair"),
        EvidenceGraphEdge(edge_id="e6", source_node_id="repair:RP-1", relation=EvidenceRelation.REQUIRES_RETEST, target_node_id="retest:RT-1", rationale="repair requires retest"),
        EvidenceGraphEdge(edge_id="e7", source_node_id="retest:RT-1", relation=EvidenceRelation.VERIFIED_BY, target_node_id=evidence_node.node_id, rationale="retest links canonical evidence"),
    ]
    if omit_edge:
        edges = [edge for edge in edges if edge.edge_id != omit_edge]
    return EvidenceGraph(graph_id="g-end-to-end", task_ref="task:T-1", nodes=nodes, edges=edges)


def test_a42_full_task_to_trusted_evidence_lineage_is_complete() -> None:
    evidence = runtime_evidence_node(EvidenceRecord(
        id="ev_runtime_001",
        type="validator_result",
        stage_id="qa",
        tool="run_validator",
        status="PASS",
        summary="validator passed",
        data={"returncode": 0},
        origin="runtime",
        trusted=True,
    ))

    report = validate_end_to_end_lineage(_graph(evidence))

    assert report.integrity_valid is True
    assert report.lineage_complete is True
    assert report.findings == []


def test_a42_full_lineage_marks_missing_upstream_step_incomplete() -> None:
    evidence = runtime_evidence_node(EvidenceRecord(
        id="ev_runtime_001",
        type="validator_result",
        stage_id="qa",
        tool="run_validator",
        status="PASS",
        summary="validator passed",
        data={"returncode": 0},
        origin="runtime",
        trusted=True,
    ))

    report = validate_end_to_end_lineage(_graph(evidence, omit_edge="e2"))

    assert report.integrity_valid is True
    assert report.lineage_complete is False
    assert any(finding.code is IntegrityCode.LINEAGE_INCOMPLETE for finding in report.findings)


def test_a42_full_lineage_rejects_provider_claim_as_terminal_verification() -> None:
    claim = EvidenceRecord.from_dict(provider_claim_records("qa", ["Looks fixed."])[0])
    evidence = runtime_evidence_node(claim)

    report = validate_end_to_end_lineage(_graph(evidence))

    assert report.integrity_valid is False
    assert report.lineage_complete is False
    assert any(finding.code is IntegrityCode.UNTRUSTED_RUNTIME_VERIFICATION for finding in report.findings)

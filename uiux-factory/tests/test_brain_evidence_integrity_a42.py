from __future__ import annotations

from core.brain_os.adapters.evidence import canonical_evidence_index, runtime_evidence_node
from core.brain_os.critique_contracts import (
    CritiqueIssue,
    CritiqueIssueStatus,
    CritiqueSeverity,
    RepairDirective,
    RepairDirectiveStatus,
    RepairLink,
    RetestRequirement,
    RetestStatus,
    RootCause,
    RootCauseStatus,
)
from core.brain_os.reasoning.evidence_graph import (
    EvidenceGraph,
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceNodeKind,
    EvidenceRelation,
)
from core.brain_os.reasoning.evidence_integrity import (
    IntegrityCode,
    validate_evidence_integrity,
    validate_repair_lineage_integrity,
)
from core.runtime.flow_os.evidence import EvidenceRecord, provider_claim_records


def _brain_node(node_id: str, kind: EvidenceNodeKind) -> EvidenceGraphNode:
    return EvidenceGraphNode(node_id=node_id, kind=kind, canonical_ref=node_id, label=node_id)


def _runtime_record(evidence_id: str = "ev_retest_001") -> EvidenceRecord:
    return EvidenceRecord(
        id=evidence_id,
        type="validator_result",
        stage_id="qa",
        tool="run_validator",
        status="PASS",
        summary="validator passed",
        data={"returncode": 0, "name": "a42-lineage"},
        origin="runtime",
        trusted=True,
    )


def _objects(evidence_ref: str = "ev_retest_001") -> tuple[CritiqueIssue, RootCause, RepairDirective, RetestRequirement, RepairLink]:
    issue = CritiqueIssue(
        id="C-1",
        critic="runtime-critic",
        category="runtime",
        severity=CritiqueSeverity.P0,
        status=CritiqueIssueStatus.RESOLVED,
        summary="QA failure was repaired",
        rationale="The original validator failure no longer reproduces after the bounded repair.",
        evidence_refs=[evidence_ref],
        affected_artifacts=["src/app.tsx"],
        retest_refs=["RT-1"],
    )
    cause = RootCause(
        id="RC-1",
        issue_ids=["C-1"],
        statement="Component state was not wired to the existing error branch.",
        status=RootCauseStatus.SUPPORTED,
        confidence=0.9,
        evidence_refs=[evidence_ref],
    )
    directive = RepairDirective(
        id="RP-1",
        issue_ids=["C-1"],
        root_cause_ids=["RC-1"],
        target_stage="implementation",
        instruction="Wire the component state to the existing error branch without changing unrelated flow behavior.",
        rationale="The repair addresses the supported root cause.",
        expected_outcome="The validator observes the expected error state.",
        priority=CritiqueSeverity.P0,
        status=RepairDirectiveStatus.ACCEPTED,
        accepted_by="human:test",
    )
    retest = RetestRequirement(
        id="RT-1",
        repair_directive_id="RP-1",
        stage="qa",
        evidence_types=["validator_result"],
        acceptance_criteria=["validator exits successfully"],
        status=RetestStatus.PASSED,
        evidence_refs=[evidence_ref],
    )
    link = RepairLink(
        id="RL-1",
        issue_ids=["C-1"],
        root_cause_ids=["RC-1"],
        repair_directive_ids=["RP-1"],
        retest_requirement_ids=["RT-1"],
        rationale="Trace one repaired P0 issue through retest evidence.",
    )
    return issue, cause, directive, retest, link


def _graph(evidence_node: EvidenceGraphNode) -> EvidenceGraph:
    nodes = [
        _brain_node("task:T-1", EvidenceNodeKind.TASK),
        _brain_node("hypothesis:H-1", EvidenceNodeKind.HYPOTHESIS),
        _brain_node("decision:D-1", EvidenceNodeKind.DECISION),
        _brain_node("critique:C-1", EvidenceNodeKind.CRITIQUE_ISSUE),
        _brain_node("root:RC-1", EvidenceNodeKind.ROOT_CAUSE),
        _brain_node("repair:RP-1", EvidenceNodeKind.REPAIR_DIRECTIVE),
        _brain_node("retest:RT-1", EvidenceNodeKind.RETEST_REQUIREMENT),
        evidence_node,
    ]
    edges = [
        EvidenceGraphEdge(edge_id="e1", source_node_id="task:T-1", relation=EvidenceRelation.JUSTIFIES, target_node_id="hypothesis:H-1", rationale="task frames hypothesis"),
        EvidenceGraphEdge(edge_id="e2", source_node_id="hypothesis:H-1", relation=EvidenceRelation.SUPPORTS, target_node_id="decision:D-1", rationale="hypothesis informs decision"),
        EvidenceGraphEdge(edge_id="e3", source_node_id="decision:D-1", relation=EvidenceRelation.REFERENCES, target_node_id="critique:C-1", rationale="decision is reviewed"),
        EvidenceGraphEdge(edge_id="e4", source_node_id="critique:C-1", relation=EvidenceRelation.CAUSED_BY, target_node_id="root:RC-1", rationale="issue maps to root cause"),
        EvidenceGraphEdge(edge_id="e5", source_node_id="root:RC-1", relation=EvidenceRelation.REPAIRED_BY, target_node_id="repair:RP-1", rationale="root cause maps to repair"),
        EvidenceGraphEdge(edge_id="e6", source_node_id="repair:RP-1", relation=EvidenceRelation.REQUIRES_RETEST, target_node_id="retest:RT-1", rationale="repair requires retest"),
        EvidenceGraphEdge(edge_id="e7", source_node_id="retest:RT-1", relation=EvidenceRelation.VERIFIED_BY, target_node_id=evidence_node.node_id, rationale="canonical evidence records retest observation"),
    ]
    return EvidenceGraph(graph_id="g-a42-integrity", task_ref="task:T-1", nodes=nodes, edges=edges)


def test_a42_integrity_accepts_exact_adapter_projection_and_complete_repair_lineage() -> None:
    runtime = _runtime_record()
    canonical = canonical_evidence_index(runtime_records=[runtime])
    graph = _graph(runtime_evidence_node(runtime))

    evidence_report = validate_evidence_integrity(graph, canonical)
    issue, cause, directive, retest, link = _objects()
    lineage_report = validate_repair_lineage_integrity(
        graph,
        link,
        issues=[issue],
        root_causes=[cause],
        directives=[directive],
        retests=[retest],
    )

    assert evidence_report.integrity_valid is True
    assert evidence_report.lineage_complete is True
    assert evidence_report.findings == []
    assert lineage_report.integrity_valid is True
    assert lineage_report.lineage_complete is True
    assert lineage_report.findings == []


def test_a42_integrity_detects_tampered_trust_projection() -> None:
    runtime = _runtime_record()
    canonical = canonical_evidence_index(runtime_records=[runtime])
    canonical_node = runtime_evidence_node(runtime)
    tampered = canonical_node.model_copy(update={"canonical_trusted_flag": False})
    graph = _graph(tampered)

    report = validate_evidence_integrity(graph, canonical)
    codes = {finding.code for finding in report.findings}

    assert report.integrity_valid is False
    assert IntegrityCode.CANONICAL_PROJECTION_MISMATCH in codes
    assert IntegrityCode.UNTRUSTED_RUNTIME_VERIFICATION in codes


def test_a42_provider_claim_cannot_be_used_as_terminal_retest_proof() -> None:
    payload = provider_claim_records("qa", ["The retest passed visually."])[0]
    provider_claim = EvidenceRecord.from_dict(payload)
    canonical = canonical_evidence_index(runtime_records=[provider_claim])
    graph = _graph(runtime_evidence_node(provider_claim))

    evidence_report = validate_evidence_integrity(graph, canonical)
    issue, cause, directive, retest, link = _objects(evidence_ref=provider_claim.id)
    lineage_report = validate_repair_lineage_integrity(
        graph,
        link,
        issues=[issue],
        root_causes=[cause],
        directives=[directive],
        retests=[retest],
    )

    evidence_codes = {finding.code for finding in evidence_report.findings}
    lineage_codes = {finding.code for finding in lineage_report.findings}
    assert IntegrityCode.UNTRUSTED_RUNTIME_VERIFICATION in evidence_codes
    assert IntegrityCode.RETEST_UNTRUSTED_EVIDENCE in lineage_codes
    assert evidence_report.integrity_valid is False
    assert lineage_report.integrity_valid is False


def test_a42_integrity_rejects_brain_authored_trust_flag() -> None:
    fake_brain_node = EvidenceGraphNode(
        node_id="decision:D-1",
        kind=EvidenceNodeKind.DECISION,
        canonical_ref="D-1",
        label="decision",
        canonical_trusted_flag=True,
    )
    graph = EvidenceGraph(graph_id="g-brain-trust", task_ref="task:T-1", nodes=[fake_brain_node], edges=[])

    report = validate_evidence_integrity(graph, {})

    assert report.integrity_valid is False
    assert any(finding.code is IntegrityCode.BRAIN_TRUST_CLAIM for finding in report.findings)


def test_a42_lineage_detects_missing_edge_and_unresolved_evidence_ref() -> None:
    runtime = _runtime_record()
    evidence_node = runtime_evidence_node(runtime)
    graph = _graph(evidence_node)
    graph = EvidenceGraph(
        graph_id=graph.graph_id,
        task_ref=graph.task_ref,
        nodes=graph.nodes,
        edges=[edge for edge in graph.edges if edge.edge_id not in {"e5", "e7"}],
    )
    issue, cause, directive, retest, link = _objects(evidence_ref="missing-evidence")

    report = validate_repair_lineage_integrity(
        graph,
        link,
        issues=[issue],
        root_causes=[cause],
        directives=[directive],
        retests=[retest],
    )
    codes = {finding.code for finding in report.findings}

    assert report.integrity_valid is False
    assert report.lineage_complete is False
    assert IntegrityCode.LINEAGE_EDGE_MISSING in codes
    assert IntegrityCode.EVIDENCE_REF_UNRESOLVED in codes


def test_a42_pending_retest_is_valid_but_lineage_is_not_complete() -> None:
    runtime = _runtime_record()
    graph = _graph(runtime_evidence_node(runtime))
    issue, cause, directive, _, link = _objects()
    pending = RetestRequirement(
        id="RT-1",
        repair_directive_id="RP-1",
        stage="qa",
        evidence_types=["validator_result"],
        acceptance_criteria=["validator exits successfully"],
        status=RetestStatus.PENDING,
    )

    report = validate_repair_lineage_integrity(
        graph,
        link,
        issues=[issue.model_copy(update={"status": CritiqueIssueStatus.CONFIRMED, "retest_refs": []})],
        root_causes=[cause],
        directives=[directive],
        retests=[pending],
    )

    assert report.integrity_valid is True
    assert report.lineage_complete is False
    assert any(finding.code is IntegrityCode.LINEAGE_INCOMPLETE for finding in report.findings)

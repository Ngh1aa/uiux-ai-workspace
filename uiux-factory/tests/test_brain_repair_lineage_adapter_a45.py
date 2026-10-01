from __future__ import annotations

from pathlib import Path

import pytest

from core.brain_os.adapters.repair_lineage import (
    extend_graph_with_repair_proposal,
    project_repair_lineage,
)
from core.brain_os.critique_contracts import CritiqueIssue, CritiqueSeverity
from core.brain_os.reasoning.evidence_graph import (
    EvidenceGraph,
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceNodeKind,
    EvidenceRelation,
)
from core.brain_os.reasoning.lineage_integrity import validate_end_to_end_lineage
from core.brain_os.repair_orchestrator import CritiqueRepairOrchestrator


def _issue(issue_id: str = "CR-graph") -> CritiqueIssue:
    return CritiqueIssue(
        id=issue_id,
        critic="visual",
        category="visual.signature",
        severity=CritiqueSeverity.P1,
        summary="Visual signature is generic",
        rationale="The current composition lacks a project-specific signature.",
        affected_artifacts=["visual_composition"],
    )


def _graph(issue: CritiqueIssue) -> EvidenceGraph:
    nodes = [
        EvidenceGraphNode(
            node_id="task:t1",
            kind=EvidenceNodeKind.TASK,
            canonical_ref="t1",
            label="task",
        ),
        EvidenceGraphNode(
            node_id="hypothesis:h1",
            kind=EvidenceNodeKind.HYPOTHESIS,
            canonical_ref="h1",
            label="hypothesis",
        ),
        EvidenceGraphNode(
            node_id="decision:d1",
            kind=EvidenceNodeKind.DECISION,
            canonical_ref="d1",
            label="decision",
        ),
        EvidenceGraphNode(
            node_id=f"critique:{issue.id}",
            kind=EvidenceNodeKind.CRITIQUE_ISSUE,
            canonical_ref=issue.id,
            label=issue.summary,
            source_module="core.brain_os.critique_contracts",
            source_status=issue.status.value,
            source_origin="brain_critique",
            tags=[issue.critic, issue.category, issue.severity.value],
        ),
    ]
    edges = [
        EvidenceGraphEdge(
            edge_id="e1",
            source_node_id="task:t1",
            relation=EvidenceRelation.JUSTIFIES,
            target_node_id="hypothesis:h1",
            rationale="test",
        ),
        EvidenceGraphEdge(
            edge_id="e2",
            source_node_id="hypothesis:h1",
            relation=EvidenceRelation.SUPPORTS,
            target_node_id="decision:d1",
            rationale="test",
        ),
        EvidenceGraphEdge(
            edge_id="e3",
            source_node_id="decision:d1",
            relation=EvidenceRelation.REFERENCES,
            target_node_id=f"critique:{issue.id}",
            rationale="test",
        ),
    ]
    return EvidenceGraph(graph_id="g1", task_ref="task:t1", nodes=nodes, edges=edges)


def test_a45_repair_lineage_fragment_stops_before_verification() -> None:
    issue = _issue()
    bundle = CritiqueRepairOrchestrator().propose(issue)
    fragment = project_repair_lineage(issue=issue, bundle=bundle)

    assert [node.kind for node in fragment.nodes] == [
        EvidenceNodeKind.CRITIQUE_ISSUE,
        EvidenceNodeKind.ROOT_CAUSE,
        EvidenceNodeKind.REPAIR_DIRECTIVE,
        EvidenceNodeKind.RETEST_REQUIREMENT,
    ]
    assert [edge.relation for edge in fragment.edges] == [
        EvidenceRelation.CAUSED_BY,
        EvidenceRelation.REPAIRED_BY,
        EvidenceRelation.REQUIRES_RETEST,
    ]
    assert EvidenceRelation.VERIFIED_BY not in {edge.relation for edge in fragment.edges}
    assert EvidenceRelation.RETESTED_BY not in {edge.relation for edge in fragment.edges}
    assert all(node.canonical_trusted_flag is None for node in fragment.nodes)
    assert fragment.execution_claim is False
    assert fragment.verification_claim is False


def test_a45_extend_graph_is_immutable_and_idempotent() -> None:
    issue = _issue()
    bundle = CritiqueRepairOrchestrator().propose(issue)
    graph = _graph(issue)
    before = graph.model_dump()

    extended = extend_graph_with_repair_proposal(graph=graph, issue=issue, bundle=bundle)
    extended_again = extend_graph_with_repair_proposal(
        graph=extended,
        issue=issue,
        bundle=bundle,
    )

    assert graph.model_dump() == before
    assert extended_again == extended
    assert len(extended.nodes) == len(graph.nodes) + 3
    assert len(extended.edges) == len(graph.edges) + 3


def test_a45_projected_proposal_keeps_end_to_end_lineage_incomplete_until_real_evidence() -> None:
    issue = _issue()
    bundle = CritiqueRepairOrchestrator().propose(issue)
    graph = extend_graph_with_repair_proposal(
        graph=_graph(issue),
        issue=issue,
        bundle=bundle,
    )

    report = validate_end_to_end_lineage(graph)

    assert report.lineage_complete is False
    assert any("incomplete" in finding.code.value.lower() for finding in report.findings)
    assert not any(
        edge.relation is EvidenceRelation.VERIFIED_BY
        for edge in graph.edges
    )


def test_a45_fragment_rejects_mismatched_source_issue() -> None:
    issue = _issue("CR-one")
    other = _issue("CR-two")
    bundle = CritiqueRepairOrchestrator().propose(issue)

    with pytest.raises(ValueError, match="source_issue_id"):
        project_repair_lineage(issue=other, bundle=bundle)


def test_a45_graph_adapter_rejects_conflicting_existing_proposal_node() -> None:
    issue = _issue()
    bundle = CritiqueRepairOrchestrator().propose(issue)
    graph = _graph(issue)
    root_id = f"root:{bundle.root_cause.id}"
    conflicting = graph.model_copy(
        update={
            "nodes": [
                *graph.nodes,
                EvidenceGraphNode(
                    node_id=root_id,
                    kind=EvidenceNodeKind.ROOT_CAUSE,
                    canonical_ref=bundle.root_cause.id,
                    label="conflicting projection",
                ),
            ]
        }
    )

    with pytest.raises(ValueError, match="graph node collision"):
        extend_graph_with_repair_proposal(
            graph=conflicting,
            issue=issue,
            bundle=bundle,
        )


def test_a45_graph_adapter_has_no_runtime_gate_or_evidence_execution_owner() -> None:
    factory = Path(__file__).resolve().parents[1]
    source = (
        factory / "core" / "brain_os" / "adapters" / "repair_lineage.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "EvidenceRecord",
        "effective_evidence",
        "gate_evidence_errors",
        "ProviderManagedRunner",
        "ManagedFlowController",
        "run_target_command",
        "release_action",
        "ProductionReleaseController",
        "merge_pull_request",
    )
    for token in forbidden:
        assert token not in source

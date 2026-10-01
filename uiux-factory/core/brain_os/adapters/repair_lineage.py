from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import Field, model_validator

from core.brain_os.contracts import BrainContractModel
from core.brain_os.critique_contracts import CritiqueIssue
from core.brain_os.reasoning.evidence_graph import (
    EvidenceGraph,
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceNodeKind,
    EvidenceRelation,
)
from core.brain_os.repair_orchestrator import RepairProposalBundle


SOURCE_MODULE = "core.brain_os.critique_contracts"
PROPOSAL_MODULE = "core.brain_os.repair_orchestrator"


def _edge_id(source: str, relation: EvidenceRelation, target: str) -> str:
    raw = f"{source}\n{relation.value}\n{target}".encode("utf-8")
    return f"edge-{hashlib.sha256(raw).hexdigest()[:16]}"


class RepairLineageFragment(BrainContractModel):
    """Proposal-only EvidenceGraph fragment for one repair bundle."""

    schema_version: Literal["brain-repair-lineage-fragment.v1"] = "brain-repair-lineage-fragment.v1"
    source_issue_id: str = Field(min_length=1, max_length=128)
    nodes: list[EvidenceGraphNode] = Field(min_length=4, max_length=4)
    edges: list[EvidenceGraphEdge] = Field(min_length=3, max_length=3)
    advisory_only: Literal[True] = True
    execution_claim: Literal[False] = False
    verification_claim: Literal[False] = False
    evidence_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"

    @model_validator(mode="after")
    def _validate_fragment_shape(self) -> "RepairLineageFragment":
        kinds = [node.kind for node in self.nodes]
        expected = [
            EvidenceNodeKind.CRITIQUE_ISSUE,
            EvidenceNodeKind.ROOT_CAUSE,
            EvidenceNodeKind.REPAIR_DIRECTIVE,
            EvidenceNodeKind.RETEST_REQUIREMENT,
        ]
        if kinds != expected:
            raise ValueError("repair lineage fragment must preserve critique→root→repair→retest node order")
        relations = [edge.relation for edge in self.edges]
        if relations != [
            EvidenceRelation.CAUSED_BY,
            EvidenceRelation.REPAIRED_BY,
            EvidenceRelation.REQUIRES_RETEST,
        ]:
            raise ValueError("repair lineage fragment may only project proposal lineage relations")
        return self


def project_repair_lineage(
    *,
    issue: CritiqueIssue,
    bundle: RepairProposalBundle,
) -> RepairLineageFragment:
    """Project proposal objects into the existing EvidenceGraph vocabulary.

    The projection intentionally stops at the pending retest node. It never creates
    VERIFIED_BY/RETESTED_BY edges or canonical evidence nodes because no execution or
    retest evidence exists at proposal time.
    """

    if bundle.source_issue_id != issue.id:
        raise ValueError("repair proposal source_issue_id must match the critique issue")
    if bundle.root_cause.issue_ids != [issue.id]:
        raise ValueError("repair proposal root cause must reference exactly the source issue")
    if bundle.directive.issue_ids != [issue.id]:
        raise ValueError("repair proposal directive must reference exactly the source issue")
    if bundle.directive.root_cause_ids != [bundle.root_cause.id]:
        raise ValueError("repair proposal directive must reference its projected root cause")
    if bundle.retest.repair_directive_id != bundle.directive.id:
        raise ValueError("repair proposal retest must reference its projected directive")

    critique_node = EvidenceGraphNode(
        node_id=f"critique:{issue.id}",
        kind=EvidenceNodeKind.CRITIQUE_ISSUE,
        canonical_ref=issue.id,
        label=issue.summary,
        source_module=SOURCE_MODULE,
        source_status=issue.status.value,
        source_origin="brain_critique",
        canonical_trusted_flag=None,
        tags=[issue.critic, issue.category, issue.severity.value],
    )
    root_node = EvidenceGraphNode(
        node_id=f"root:{bundle.root_cause.id}",
        kind=EvidenceNodeKind.ROOT_CAUSE,
        canonical_ref=bundle.root_cause.id,
        label=bundle.root_cause.statement,
        source_module=PROPOSAL_MODULE,
        source_status=bundle.root_cause.status.value,
        source_origin="brain_repair_proposal",
        canonical_trusted_flag=None,
        tags=["proposal"],
    )
    repair_node = EvidenceGraphNode(
        node_id=f"repair:{bundle.directive.id}",
        kind=EvidenceNodeKind.REPAIR_DIRECTIVE,
        canonical_ref=bundle.directive.id,
        label=bundle.directive.instruction,
        source_module=PROPOSAL_MODULE,
        source_status=bundle.directive.status.value,
        source_origin="brain_repair_proposal",
        canonical_trusted_flag=None,
        tags=[bundle.directive.priority.value, bundle.directive.target_stage, "proposal"],
    )
    retest_node = EvidenceGraphNode(
        node_id=f"retest:{bundle.retest.id}",
        kind=EvidenceNodeKind.RETEST_REQUIREMENT,
        canonical_ref=bundle.retest.id,
        label="; ".join(bundle.retest.acceptance_criteria),
        source_module=PROPOSAL_MODULE,
        source_status=bundle.retest.status.value,
        source_origin="brain_repair_proposal",
        canonical_trusted_flag=None,
        tags=[bundle.retest.stage, *bundle.retest.evidence_types, "pending"],
    )

    edges = [
        EvidenceGraphEdge(
            edge_id=_edge_id(critique_node.node_id, EvidenceRelation.CAUSED_BY, root_node.node_id),
            source_node_id=critique_node.node_id,
            relation=EvidenceRelation.CAUSED_BY,
            target_node_id=root_node.node_id,
            rationale="Source critique issue is linked to a proposed root cause only.",
        ),
        EvidenceGraphEdge(
            edge_id=_edge_id(root_node.node_id, EvidenceRelation.REPAIRED_BY, repair_node.node_id),
            source_node_id=root_node.node_id,
            relation=EvidenceRelation.REPAIRED_BY,
            target_node_id=repair_node.node_id,
            rationale="Proposed root cause is linked to a proposed repair directive only.",
        ),
        EvidenceGraphEdge(
            edge_id=_edge_id(repair_node.node_id, EvidenceRelation.REQUIRES_RETEST, retest_node.node_id),
            source_node_id=repair_node.node_id,
            relation=EvidenceRelation.REQUIRES_RETEST,
            target_node_id=retest_node.node_id,
            rationale="Proposed repair requires a pending retest before any resolution claim.",
        ),
    ]

    return RepairLineageFragment(
        source_issue_id=issue.id,
        nodes=[critique_node, root_node, repair_node, retest_node],
        edges=edges,
    )


def extend_graph_with_repair_proposal(
    *,
    graph: EvidenceGraph,
    issue: CritiqueIssue,
    bundle: RepairProposalBundle,
) -> EvidenceGraph:
    """Return a new graph containing the proposal lineage; never mutate input graph."""

    fragment = project_repair_lineage(issue=issue, bundle=bundle)
    existing_nodes = {node.node_id: node for node in graph.nodes}
    existing_edges = {edge.edge_id: edge for edge in graph.edges}

    nodes = list(graph.nodes)
    for node in fragment.nodes:
        previous = existing_nodes.get(node.node_id)
        if previous is not None:
            if previous != node:
                raise ValueError(f"graph node collision for repair proposal: {node.node_id}")
            continue
        nodes.append(node)
        existing_nodes[node.node_id] = node

    edges = list(graph.edges)
    for edge in fragment.edges:
        previous = existing_edges.get(edge.edge_id)
        if previous is not None:
            if previous != edge:
                raise ValueError(f"graph edge collision for repair proposal: {edge.edge_id}")
            continue
        edges.append(edge)
        existing_edges[edge.edge_id] = edge

    return EvidenceGraph(
        schema_version=graph.schema_version,
        graph_id=graph.graph_id,
        task_ref=graph.task_ref,
        nodes=nodes,
        edges=edges,
        warnings=list(graph.warnings),
    )

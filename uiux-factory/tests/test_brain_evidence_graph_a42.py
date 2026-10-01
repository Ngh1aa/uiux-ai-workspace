from __future__ import annotations

from pathlib import Path

import pytest

from core.brain_os.adapters.evidence import (
    provenance_evidence_node,
    release_evidence_node,
    runtime_evidence_node,
)
from core.brain_os.reasoning.evidence_graph import (
    EvidenceGraph,
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceNodeKind,
    EvidenceRelation,
)
from core.contracts.evidence_provenance_schema import EvidenceProvenanceRecord
from core.contracts.release_evidence_schema import ReleaseEvidenceArtifact
from core.runtime.flow_os.evidence import EvidenceRecord, provider_claim_records


FACTORY = Path(__file__).resolve().parents[1]


def _brain_node(node_id: str, kind: EvidenceNodeKind) -> EvidenceGraphNode:
    return EvidenceGraphNode(node_id=node_id, kind=kind, canonical_ref=node_id, label=node_id)


def test_a42_runtime_adapter_preserves_canonical_identity_and_trust_flag() -> None:
    record = EvidenceRecord(
        id="ev_runtime_001",
        type="validator_result",
        stage_id="qa",
        tool="run_validator",
        status="PASS",
        summary="validator passed",
        data={"returncode": 0},
        origin="runtime",
        trusted=True,
    )

    node = runtime_evidence_node(record)

    assert node.node_id == "runtime:ev_runtime_001"
    assert node.canonical_ref == record.id
    assert node.kind is EvidenceNodeKind.RUNTIME_EVIDENCE
    assert node.source_status == record.status
    assert node.source_origin == record.origin
    assert node.canonical_trusted_flag is True


def test_a42_provider_claim_remains_untrusted_when_projected_into_graph() -> None:
    payload = provider_claim_records("qa", ["The UI passed visual QA."])[0]
    record = EvidenceRecord.from_dict(payload)

    node = runtime_evidence_node(record)

    assert record.trusted is False
    assert node.canonical_trusted_flag is False
    assert node.source_origin == "provider"
    assert "provider_claim" in node.tags


def test_a42_provenance_adapter_keeps_stable_evid_identity() -> None:
    record = EvidenceProvenanceRecord(
        evidence_id="EVID-0123456789abcdef",
        status="VERIFIED",
        kind="style",
        source_type="computed_style",
        source_url="https://example.com",
        source_artifact="reference-evidence.json",
        source_artifact_sha256="a" * 64,
        captured_at="2026-10-02T00:00:00Z",
        viewport="desktop:1440x900",
        selector=".hero",
        property_name="display",
        value="grid",
        locator="references[0].captures[0].computed_styles[0].properties.display",
    )

    node = provenance_evidence_node(record)

    assert node.node_id == "provenance:EVID-0123456789abcdef"
    assert node.canonical_ref == record.evidence_id
    assert node.kind is EvidenceNodeKind.PROVENANCE_EVIDENCE
    assert node.canonical_trusted_flag is None
    assert node.source_status == "VERIFIED"


def test_a42_release_adapter_keeps_rel_identity_without_claiming_gate_authority() -> None:
    record = ReleaseEvidenceArtifact(
        evidence_id="REL-0123456789abcdef",
        kind="browser_qa",
        path="artifacts/browser-qa.json",
        sha256="b" * 64,
        size_bytes=512,
        state="VERIFIED",
        claims=["browser_qa_artifacts"],
    )

    node = release_evidence_node(record)

    assert node.node_id == "release:REL-0123456789abcdef"
    assert node.canonical_ref == record.evidence_id
    assert node.kind is EvidenceNodeKind.RELEASE_EVIDENCE
    assert node.source_status == "VERIFIED"
    assert node.canonical_trusted_flag is None


def test_a42_graph_can_trace_reasoning_repair_and_retest_to_runtime_evidence() -> None:
    runtime = runtime_evidence_node(
        EvidenceRecord(
            id="ev_retest_001",
            type="validator_result",
            stage_id="qa",
            tool="run_validator",
            status="PASS",
            summary="retest passed",
            data={"returncode": 0},
        )
    )
    nodes = [
        _brain_node("task:T-1", EvidenceNodeKind.TASK),
        _brain_node("hypothesis:H-1", EvidenceNodeKind.HYPOTHESIS),
        _brain_node("decision:D-1", EvidenceNodeKind.DECISION),
        _brain_node("critique:C-1", EvidenceNodeKind.CRITIQUE_ISSUE),
        _brain_node("root:R-1", EvidenceNodeKind.ROOT_CAUSE),
        _brain_node("repair:RP-1", EvidenceNodeKind.REPAIR_DIRECTIVE),
        _brain_node("retest:RT-1", EvidenceNodeKind.RETEST_REQUIREMENT),
        runtime,
    ]
    edges = [
        EvidenceGraphEdge(edge_id="e1", source_node_id="task:T-1", relation=EvidenceRelation.JUSTIFIES, target_node_id="hypothesis:H-1", rationale="task frames hypothesis"),
        EvidenceGraphEdge(edge_id="e2", source_node_id="hypothesis:H-1", relation=EvidenceRelation.SUPPORTS, target_node_id="decision:D-1", rationale="hypothesis informs decision"),
        EvidenceGraphEdge(edge_id="e3", source_node_id="decision:D-1", relation=EvidenceRelation.REFERENCES, target_node_id="critique:C-1", rationale="decision is reviewed"),
        EvidenceGraphEdge(edge_id="e4", source_node_id="critique:C-1", relation=EvidenceRelation.CAUSED_BY, target_node_id="root:R-1", rationale="issue maps to root cause"),
        EvidenceGraphEdge(edge_id="e5", source_node_id="root:R-1", relation=EvidenceRelation.REPAIRED_BY, target_node_id="repair:RP-1", rationale="root cause maps to repair"),
        EvidenceGraphEdge(edge_id="e6", source_node_id="repair:RP-1", relation=EvidenceRelation.REQUIRES_RETEST, target_node_id="retest:RT-1", rationale="repair requires retest"),
        EvidenceGraphEdge(edge_id="e7", source_node_id="retest:RT-1", relation=EvidenceRelation.VERIFIED_BY, target_node_id=runtime.node_id, rationale="runtime validator is retest evidence"),
    ]

    graph = EvidenceGraph(graph_id="graph-001", task_ref="task:T-1", nodes=nodes, edges=edges)
    restored = EvidenceGraph.model_validate_json(graph.model_dump_json())

    assert restored == graph
    assert restored.edges[-1].target_node_id == "runtime:ev_retest_001"


def test_a42_graph_rejects_duplicate_nodes_dangling_edges_and_self_edges() -> None:
    node = _brain_node("task:T-1", EvidenceNodeKind.TASK)

    with pytest.raises(ValueError, match="node ids must be unique"):
        EvidenceGraph(graph_id="g-dup", task_ref="task:T-1", nodes=[node, node], edges=[])

    with pytest.raises(ValueError, match="dangling edge endpoint"):
        EvidenceGraph(
            graph_id="g-dangling",
            task_ref="task:T-1",
            nodes=[node],
            edges=[
                EvidenceGraphEdge(
                    edge_id="e1",
                    source_node_id="task:T-1",
                    relation=EvidenceRelation.SUPPORTS,
                    target_node_id="missing:D-1",
                    rationale="invalid dangling edge",
                )
            ],
        )

    with pytest.raises(ValueError, match="cannot link a node to itself"):
        EvidenceGraphEdge(
            edge_id="e-self",
            source_node_id="task:T-1",
            relation=EvidenceRelation.REFERENCES,
            target_node_id="task:T-1",
            rationale="self edge",
        )


def test_a42_evidence_graph_foundation_has_no_brain_owned_evidence_store_or_policy() -> None:
    brain_root = FACTORY / "core" / "brain_os"
    forbidden_names = {
        "evidence_store.py",
        "evidence_registry.py",
        "runtime-policy.json",
        "provider-policy.json",
        "release-policy.json",
    }
    found = [path for path in brain_root.rglob("*") if path.is_file() and path.name in forbidden_names]
    assert not found

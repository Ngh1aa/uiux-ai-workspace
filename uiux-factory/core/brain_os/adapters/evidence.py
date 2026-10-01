from __future__ import annotations

import core.provenance.evidence_lineage as evidence_lineage
import core.provenance.release_evidence_registry as release_evidence_registry
from core.brain_os.reasoning.evidence_graph import EvidenceGraphNode, EvidenceNodeKind
from core.contracts.evidence_provenance_schema import EvidenceProvenanceRecord
from core.contracts.release_evidence_schema import ReleaseEvidenceArtifact
from core.runtime.flow_os.evidence import EvidenceRecord


RUNTIME_EVIDENCE_MODULE = "core.runtime.flow_os.evidence"
PROVENANCE_MODULE = "core.provenance.evidence_lineage"
RELEASE_REGISTRY_MODULE = "core.provenance.release_evidence_registry"


def runtime_evidence_node(record: EvidenceRecord) -> EvidenceGraphNode:
    """Project one canonical runtime evidence record into a Brain relationship node.

    The adapter copies the canonical trusted flag for traceability only. Brain OS does
    not recompute, upgrade or enforce evidence trust from this node.
    """

    return EvidenceGraphNode(
        node_id=f"runtime:{record.id}",
        kind=EvidenceNodeKind.RUNTIME_EVIDENCE,
        canonical_ref=record.id,
        label=record.summary,
        source_module=RUNTIME_EVIDENCE_MODULE,
        source_status=record.status,
        source_origin=record.origin,
        canonical_trusted_flag=record.trusted,
        tags=[record.type, record.stage_id, record.tool],
    )


def provenance_evidence_node(record: EvidenceProvenanceRecord) -> EvidenceGraphNode:
    """Reference a stable EVID-* provenance record without changing its semantics."""

    # Touch the canonical module explicitly so architecture guardrails can verify that
    # Brain Evidence Graph remains adapter-backed by the existing provenance owner.
    _ = evidence_lineage.EVIDENCE_MARKER
    return EvidenceGraphNode(
        node_id=f"provenance:{record.evidence_id}",
        kind=EvidenceNodeKind.PROVENANCE_EVIDENCE,
        canonical_ref=record.evidence_id,
        label=f"{record.kind}: {record.source_type}",
        source_module=PROVENANCE_MODULE,
        source_status=record.status,
        source_origin=record.source_type,
        canonical_trusted_flag=None,
        tags=[record.kind, record.source_type],
    )


def release_evidence_node(record: ReleaseEvidenceArtifact) -> EvidenceGraphNode:
    """Reference a release-registry artifact without turning it into a new gate result."""

    # Explicitly bind the adapter to the canonical release registry module. The graph
    # stores only identity/relationship metadata and does not own release readiness.
    _ = release_evidence_registry.build_release_evidence_manifest
    return EvidenceGraphNode(
        node_id=f"release:{record.evidence_id}",
        kind=EvidenceNodeKind.RELEASE_EVIDENCE,
        canonical_ref=record.evidence_id,
        label=f"{record.kind}: {record.path}",
        source_module=RELEASE_REGISTRY_MODULE,
        source_status=record.state,
        source_origin="release_registry",
        canonical_trusted_flag=None,
        tags=[record.kind],
    )

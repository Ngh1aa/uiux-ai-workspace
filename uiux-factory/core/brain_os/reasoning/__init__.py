"""Reasoning-layer data structures for UIUX Brain OS.

This package does not own execution, provider, gate, evidence-trust, merge or release authority.
"""

from core.brain_os.reasoning.evidence_graph import (
    EvidenceGraph,
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceNodeKind,
    EvidenceRelation,
)
from core.brain_os.reasoning.evidence_integrity import (
    EvidenceIntegrityFinding,
    EvidenceIntegrityReport,
    IntegrityCode,
    IntegritySeverity,
    validate_evidence_integrity,
    validate_repair_lineage_integrity,
)

__all__ = [
    "EvidenceGraph",
    "EvidenceGraphEdge",
    "EvidenceGraphNode",
    "EvidenceIntegrityFinding",
    "EvidenceIntegrityReport",
    "EvidenceNodeKind",
    "EvidenceRelation",
    "IntegrityCode",
    "IntegritySeverity",
    "validate_evidence_integrity",
    "validate_repair_lineage_integrity",
]

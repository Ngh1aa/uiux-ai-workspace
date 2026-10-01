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
from core.brain_os.reasoning.lineage_integrity import validate_end_to_end_lineage

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
    "validate_end_to_end_lineage",
    "validate_evidence_integrity",
    "validate_repair_lineage_integrity",
]

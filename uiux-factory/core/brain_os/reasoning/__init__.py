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

__all__ = [
    "EvidenceGraph",
    "EvidenceGraphEdge",
    "EvidenceGraphNode",
    "EvidenceNodeKind",
    "EvidenceRelation",
]

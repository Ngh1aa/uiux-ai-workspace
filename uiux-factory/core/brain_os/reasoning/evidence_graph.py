from __future__ import annotations

from enum import Enum

from pydantic import Field, field_validator, model_validator

from core.brain_os.contracts import BrainContractModel


class EvidenceNodeKind(str, Enum):
    TASK = "TASK"
    HYPOTHESIS = "HYPOTHESIS"
    DECISION = "DECISION"
    CRITIQUE_ISSUE = "CRITIQUE_ISSUE"
    ROOT_CAUSE = "ROOT_CAUSE"
    REPAIR_DIRECTIVE = "REPAIR_DIRECTIVE"
    RETEST_REQUIREMENT = "RETEST_REQUIREMENT"
    RUNTIME_EVIDENCE = "RUNTIME_EVIDENCE"
    PROVENANCE_EVIDENCE = "PROVENANCE_EVIDENCE"
    RELEASE_EVIDENCE = "RELEASE_EVIDENCE"
    ARTIFACT = "ARTIFACT"


class EvidenceRelation(str, Enum):
    REFERENCES = "REFERENCES"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    OBSERVES = "OBSERVES"
    JUSTIFIES = "JUSTIFIES"
    IDENTIFIES = "IDENTIFIES"
    CAUSED_BY = "CAUSED_BY"
    REPAIRED_BY = "REPAIRED_BY"
    REQUIRES_RETEST = "REQUIRES_RETEST"
    RETESTED_BY = "RETESTED_BY"
    VERIFIED_BY = "VERIFIED_BY"
    SUPERSEDES = "SUPERSEDES"
    PRODUCED = "PRODUCED"


def _clean_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


class EvidenceGraphNode(BrainContractModel):
    """A lightweight relationship node that references canonical data by ID.

    This node is not evidence authority. It carries identity and minimal source metadata
    only so Brain reasoning can connect hypotheses/decisions/critique/repair state to
    the evidence systems that already own trust and provenance semantics.
    """

    node_id: str = Field(min_length=1, max_length=256)
    kind: EvidenceNodeKind
    canonical_ref: str | None = Field(default=None, max_length=256)
    label: str = Field(default="", max_length=1000)
    source_module: str = Field(default="", max_length=500)
    source_status: str = Field(default="", max_length=128)
    source_origin: str = Field(default="", max_length=128)
    canonical_trusted_flag: bool | None = None
    tags: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("canonical_ref", mode="before")
    @classmethod
    def _normalize_optional_ref(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @field_validator("tags")
    @classmethod
    def _normalize_tags(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)


class EvidenceGraphEdge(BrainContractModel):
    edge_id: str = Field(min_length=1, max_length=256)
    source_node_id: str = Field(min_length=1, max_length=256)
    relation: EvidenceRelation
    target_node_id: str = Field(min_length=1, max_length=256)
    rationale: str = Field(min_length=1, max_length=4000)

    @model_validator(mode="after")
    def _prevent_self_edges(self) -> "EvidenceGraphEdge":
        if self.source_node_id == self.target_node_id:
            raise ValueError("EvidenceGraphEdge cannot link a node to itself")
        return self


class EvidenceGraph(BrainContractModel):
    """Immutable in-memory relationship view over canonical evidence references.

    It deliberately has no persistence, gate evaluation, PASS/FAIL aggregation,
    release decision or trust-upgrade behavior. Those responsibilities remain with
    existing runtime/provenance/evaluation owners.
    """

    schema_version: str = "brain-evidence-graph.v1"
    graph_id: str = Field(min_length=1, max_length=256)
    task_ref: str = Field(min_length=1, max_length=256)
    nodes: list[EvidenceGraphNode] = Field(default_factory=list, max_length=5000)
    edges: list[EvidenceGraphEdge] = Field(default_factory=list, max_length=10000)
    warnings: list[str] = Field(default_factory=list, max_length=200)

    @field_validator("warnings")
    @classmethod
    def _normalize_warnings(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @model_validator(mode="after")
    def _validate_graph_integrity(self) -> "EvidenceGraph":
        node_ids = [node.node_id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("EvidenceGraph node ids must be unique")

        edge_ids = [edge.edge_id for edge in self.edges]
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("EvidenceGraph edge ids must be unique")

        known_nodes = set(node_ids)
        dangling: list[str] = []
        for edge in self.edges:
            if edge.source_node_id not in known_nodes:
                dangling.append(f"{edge.edge_id}:source={edge.source_node_id}")
            if edge.target_node_id not in known_nodes:
                dangling.append(f"{edge.edge_id}:target={edge.target_node_id}")
        if dangling:
            raise ValueError("EvidenceGraph contains dangling edge endpoint(s): " + ", ".join(dangling))
        return self

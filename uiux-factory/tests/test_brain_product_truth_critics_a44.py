from __future__ import annotations

from core.brain_os.adapters.evidence import canonical_evidence_index, runtime_evidence_node
from core.brain_os.contracts import (
    BrainTaskFrame,
    Decision,
    DecisionStatus,
    Hypothesis,
    HypothesisStatus,
    Reversibility,
    Uncertainty,
    UncertaintyState,
)
from core.brain_os.critics.product_truth import (
    EvidenceTruthCritic,
    ProductCritic,
    RuntimeCritic,
)
from core.brain_os.critique_contracts import CritiqueIssueStatus, CritiqueSeverity
from core.brain_os.reasoning.evidence_graph import (
    EvidenceGraph,
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceNodeKind,
    EvidenceRelation,
)
from core.runtime.flow_os.evidence import EvidenceRecord


def _frame(*, healthy: bool) -> BrainTaskFrame:
    return BrainTaskFrame(
        frame_id="frame-1",
        goal="Improve the product",
        intent="redesign",
        domain="generic",
        product_archetype="saas",
        change_surface="PRODUCT",
        validation_lane="prototype",
        authority="branch_write",
        risk="normal",
        constraints=[],
        preserve=[],
        forbidden=[],
        success_criteria=(
            ["Primary task completion is measurable and critical states are covered"]
            if healthy
            else []
        ),
        evidence_refs=[],
        uncertainties=(
            [
                Uncertainty(
                    id="u1",
                    subject="target user role",
                    state=UncertaintyState.KNOWN,
                    rationale="Explicitly supplied",
                    confidence=1.0,
                )
            ]
            if healthy
            else [
                Uncertainty(
                    id="u1",
                    subject="primary workflow ownership",
                    state=UncertaintyState.CONFLICTED,
                    rationale="Two sources disagree",
                    confidence=0.2,
                )
            ]
        ),
        source_task_contract_version="1.0",
        source_confidence=0.95 if healthy else 0.35,
        source_inference_evidence=[],
    )


def _healthy_hypothesis() -> Hypothesis:
    return Hypothesis(
        id="h1",
        statement="A clearer task hierarchy reduces user hesitation",
        risk="normal",
        confidence=0.8,
        validation_method="Usability test",
        status=HypothesisStatus.VALIDATED,
        evidence_refs=["ev_ok"],
    )


def _healthy_decision() -> Decision:
    return Decision(
        id="d1",
        question="Which task hierarchy should lead the product?",
        chosen="Primary workflow first",
        alternatives=["Feature-first navigation"],
        evidence_refs=["ev_ok"],
        tradeoff="Reduces secondary-feature prominence",
        reversibility=Reversibility.REVERSIBLE,
        confidence=0.85,
        status=DecisionStatus.SELECTED,
        owner="human",
        selected_by="product-owner",
    )


def _runtime_record(*, record_id: str, status: str, returncode: int) -> dict[str, object]:
    return EvidenceRecord(
        id=record_id,
        type="validator_result",
        stage_id="qa",
        tool="run_validator",
        status=status,
        summary=f"validator {'passed' if returncode == 0 else 'failed'}",
        data={"name": "smoke", "returncode": returncode},
        origin="runtime",
        trusted=True,
        created_at=f"2026-10-02T00:00:0{returncode}Z",
    ).to_dict()


def _full_graph(*, trusted: bool) -> tuple[EvidenceGraph, dict[str, EvidenceGraphNode]]:
    runtime = EvidenceRecord(
        id="ev_runtime",
        type="validator_result",
        stage_id="qa",
        tool="run_validator",
        status="PASS",
        summary="qa validator passed",
        data={"name": "qa", "returncode": 0},
        origin="runtime",
        trusted=trusted,
        created_at="2026-10-02T00:00:00Z",
    )
    runtime_node = runtime_evidence_node(runtime)
    nodes = [
        EvidenceGraphNode(node_id="task:t1", kind=EvidenceNodeKind.TASK, label="task"),
        EvidenceGraphNode(node_id="hypothesis:h1", kind=EvidenceNodeKind.HYPOTHESIS, label="hypothesis"),
        EvidenceGraphNode(node_id="decision:d1", kind=EvidenceNodeKind.DECISION, label="decision"),
        EvidenceGraphNode(node_id="critique:c1", kind=EvidenceNodeKind.CRITIQUE_ISSUE, label="critique"),
        EvidenceGraphNode(node_id="root:r1", kind=EvidenceNodeKind.ROOT_CAUSE, label="root"),
        EvidenceGraphNode(node_id="repair:p1", kind=EvidenceNodeKind.REPAIR_DIRECTIVE, label="repair"),
        EvidenceGraphNode(node_id="retest:rt1", kind=EvidenceNodeKind.RETEST_REQUIREMENT, label="retest"),
        runtime_node,
    ]
    chain = [
        ("e1", "task:t1", EvidenceRelation.JUSTIFIES, "hypothesis:h1"),
        ("e2", "hypothesis:h1", EvidenceRelation.SUPPORTS, "decision:d1"),
        ("e3", "decision:d1", EvidenceRelation.REFERENCES, "critique:c1"),
        ("e4", "critique:c1", EvidenceRelation.CAUSED_BY, "root:r1"),
        ("e5", "root:r1", EvidenceRelation.REPAIRED_BY, "repair:p1"),
        ("e6", "repair:p1", EvidenceRelation.REQUIRES_RETEST, "retest:rt1"),
        ("e7", "retest:rt1", EvidenceRelation.VERIFIED_BY, runtime_node.node_id),
    ]
    graph = EvidenceGraph(
        graph_id="g1",
        task_ref="task:t1",
        nodes=nodes,
        edges=[
            EvidenceGraphEdge(
                edge_id=edge_id,
                source_node_id=source,
                relation=relation,
                target_node_id=target,
                rationale="test lineage",
            )
            for edge_id, source, relation, target in chain
        ],
    )
    return graph, canonical_evidence_index(runtime_records=[runtime])


def test_a44_product_critic_surfaces_broad_reasoning_and_governance_gaps() -> None:
    decision = Decision(
        id="d-risky",
        question="Should we replace the core workflow?",
        chosen="Replace it",
        alternatives=["Incremental migration"],
        tradeoff="High migration cost",
        reversibility=Reversibility.COSTLY,
        confidence=0.55,
        status=DecisionStatus.SELECTED,
        owner="brain_advisory",
        selected_by="brain",
    )
    hypothesis = Hypothesis(
        id="h-risky",
        statement="Users will understand the replacement workflow",
        risk="high",
        confidence=0.4,
        validation_method="Usability test",
        status=HypothesisStatus.PROPOSED,
    )

    report = ProductCritic().review(
        frame=_frame(healthy=False),
        hypotheses=[hypothesis],
        decisions=[decision],
    )
    categories = {item.category for item in report.issues}

    assert "product.success_criteria_missing" in categories
    assert "product.low_source_confidence" in categories
    assert "product.blocking_uncertainty" in categories
    assert "product.high_risk_hypothesis_unverified" in categories
    assert "product.selected_decision_without_evidence" in categories
    assert "product.high_cost_brain_owned_selection" in categories
    assert any(item.severity is CritiqueSeverity.P0 for item in report.issues)
    assert all(item.status is CritiqueIssueStatus.OBSERVED for item in report.issues)
    assert report.gate_effect == report.evidence_effect == report.authority_effect == "none"


def test_a44_healthy_product_reasoning_can_have_no_findings_without_implying_pass() -> None:
    report = ProductCritic().review(
        frame=_frame(healthy=True),
        hypotheses=[_healthy_hypothesis()],
        decisions=[_healthy_decision()],
    )

    assert report.issues == []
    assert report.advisory_only is True
    assert not hasattr(report, "passed")


def test_a44_runtime_critic_uses_effective_latest_channel_not_historical_failure() -> None:
    records = [
        _runtime_record(record_id="ev_old_fail", status="FAIL", returncode=1),
        _runtime_record(record_id="ev_new_pass", status="PASS", returncode=0),
    ]
    report = RuntimeCritic().review(
        records=records,
        expected_stage_ids=["qa"],
        required_evidence_types_by_stage={"qa": ["validator_result"]},
    )

    assert report.issues == []
    assert report.effective_evidence_refs == ["ev_new_pass"]
    assert not hasattr(report, "passed")


def test_a44_runtime_critic_reports_effective_failure_and_missing_expected_evidence() -> None:
    report = RuntimeCritic().review(
        records=[_runtime_record(record_id="ev_fail", status="FAIL", returncode=1)],
        expected_stage_ids=["qa", "implementation"],
        required_evidence_types_by_stage={"qa": ["validator_result", "browser_render"]},
    )
    categories = {item.category for item in report.issues}

    assert "runtime.effective_failure" in categories
    assert "runtime.stage_evidence_missing" in categories
    assert "runtime.expected_evidence_type_missing" in categories
    failed = next(item for item in report.issues if item.category == "runtime.effective_failure")
    assert failed.evidence_refs == ["ev_fail"]
    assert failed.status is CritiqueIssueStatus.OBSERVED
    assert report.gate_effect == "none"


def test_a44_truth_critic_reuses_a42_integrity_and_lineage_without_upgrading_trust() -> None:
    graph, canonical = _full_graph(trusted=False)
    report = EvidenceTruthCritic().review(graph=graph, canonical_index=canonical)

    assert report.integrity_valid is False
    assert report.lineage_complete is False
    assert report.issues
    assert all(item.status is CritiqueIssueStatus.OBSERVED for item in report.issues)
    assert all(item.evidence_refs == [] for item in report.issues)
    assert any("untrusted_runtime_verification" in item.category for item in report.issues)
    assert report.evidence_effect == "none"


def test_a44_truth_critic_complete_trusted_lineage_can_be_issue_free_without_gate_pass() -> None:
    graph, canonical = _full_graph(trusted=True)
    report = EvidenceTruthCritic().review(graph=graph, canonical_index=canonical)

    assert report.integrity_valid is True
    assert report.lineage_complete is True
    assert report.issues == []
    assert report.advisory_only is True
    assert not hasattr(report, "passed")


def test_a44_product_truth_critics_do_not_import_or_call_gate_release_execution_owners() -> None:
    from pathlib import Path

    factory = Path(__file__).resolve().parents[1]
    source = (factory / "core" / "brain_os" / "critics" / "product_truth.py").read_text(encoding="utf-8")
    forbidden = (
        "gate_evidence_errors",
        "ProductionReleaseController",
        "ProviderManagedRunner",
        "ManagedFlowController",
        "release_action",
        "run_target_command",
        "merge_pull_request",
    )
    for token in forbidden:
        assert token not in source

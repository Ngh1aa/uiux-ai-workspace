from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.brain_os import (
    BRAIN_CONTRACT_VERSION,
    BrainTaskFrame,
    Decision,
    DecisionStatus,
    Hypothesis,
    HypothesisStatus,
    Reversibility,
    Uncertainty,
    UncertaintyState,
)
from core.runtime.flow_os.task_context import TASK_CONTRACT_VERSION, GoalInterpreter


def _known_uncertainty() -> Uncertainty:
    return Uncertainty(
        id="U-001",
        subject="Current hero animation must be preserved",
        state=UncertaintyState.KNOWN,
        rationale="The task explicitly declares a preserve constraint.",
        confidence=1.0,
    )


def test_a41_brain_task_frame_is_compatible_with_canonical_task_contract() -> None:
    profile = GoalInterpreter().interpret("Fix button padding on the current fintech dashboard")
    context = profile.to_context()

    frame = BrainTaskFrame(
        frame_id="FRAME-001",
        goal="Fix button padding on the current fintech dashboard",
        intent=profile.intent,
        domain=profile.domain,
        product_archetype=profile.product_archetype,
        change_surface=profile.change_surface,
        validation_lane=profile.validation_lane,
        authority="branch_write",
        risk=profile.risk,
        constraints=["Do not change product behavior"],
        success_criteria=["Button spacing is corrected without layout regression"],
        uncertainties=[_known_uncertainty()],
        source_task_contract_version=profile.task_contract_version,
        source_confidence=profile.confidence,
        source_inference_evidence=profile.evidence,
    )

    assert frame.schema_version == BRAIN_CONTRACT_VERSION
    assert frame.source_task_contract_version == TASK_CONTRACT_VERSION
    assert frame.change_surface == context["change_surface"]
    assert frame.domain == context["domain"]
    assert frame.authority == "branch_write"

    restored = BrainTaskFrame.model_validate_json(frame.model_dump_json())
    assert restored == frame


def test_a41_brain_contracts_are_strict_and_immutable() -> None:
    uncertainty = _known_uncertainty()
    with pytest.raises(ValidationError):
        Uncertainty(
            id="U-002",
            subject="Unknown",
            state=UncertaintyState.INFERRED,
            rationale="Inference",
            confidence=0.5,
            invented_field="not allowed",
        )

    with pytest.raises(ValidationError):
        uncertainty.confidence = 0.1


def test_a41_uncertainty_state_semantics_require_proof_or_blocker() -> None:
    with pytest.raises(ValidationError, match="VALIDATED uncertainty requires"):
        Uncertainty(
            id="U-VAL",
            subject="Users can recover from payment failure",
            state=UncertaintyState.VALIDATED,
            rationale="This cannot be called validated without linked evidence.",
            confidence=0.9,
        )

    validated = Uncertainty(
        id="U-VAL",
        subject="Users can recover from payment failure",
        state=UncertaintyState.VALIDATED,
        rationale="Observed in a traceable usability session.",
        confidence=0.9,
        evidence_refs=["research:session:07"],
    )
    assert validated.evidence_refs == ["research:session:07"]

    with pytest.raises(ValidationError, match="BLOCKED uncertainty requires"):
        Uncertainty(
            id="U-BLOCK",
            subject="Production conversion impact",
            state=UncertaintyState.BLOCKED,
            rationale="Analytics are unavailable.",
            confidence=0.0,
        )


def test_a41_hypothesis_cannot_claim_validation_without_evidence() -> None:
    base = {
        "id": "H-001",
        "statement": "Making recovery actions visible will reduce abandoned payment attempts.",
        "risk": "medium",
        "confidence": 0.6,
        "validation_method": "Prototype usability test with payment-error scenarios",
    }
    proposed = Hypothesis(**base)
    assert proposed.status is HypothesisStatus.PROPOSED

    with pytest.raises(ValidationError, match="VALIDATED hypothesis requires"):
        Hypothesis(**base, status=HypothesisStatus.VALIDATED)

    validated = Hypothesis(
        **base,
        status=HypothesisStatus.VALIDATED,
        evidence_refs=["evidence:usability:H-001"],
    )
    assert validated.status is HypothesisStatus.VALIDATED


def test_a41_decision_records_tradeoff_reversibility_and_selection_provenance() -> None:
    base = {
        "id": "D-001",
        "question": "How should payment failure recovery be exposed?",
        "chosen": "Keep recovery inline with the failed payment rather than sending users to a generic error page.",
        "alternatives": ["Generic error page", "Support-only recovery"],
        "evidence_refs": ["evidence:browser:payment-failure", "H-001"],
        "tradeoff": "Adds local state complexity but keeps context and recovery actions visible.",
        "reversibility": Reversibility.REVERSIBLE,
        "confidence": 0.82,
    }
    decision = Decision(**base)
    assert decision.owner == "brain_advisory"
    assert decision.status is DecisionStatus.PROPOSED

    with pytest.raises(ValidationError, match="SELECTED decision requires selected_by"):
        Decision(**base, status=DecisionStatus.SELECTED)

    selected = Decision(
        **base,
        status=DecisionStatus.SELECTED,
        selected_by="human:design-owner",
        owner="human",
    )
    assert selected.selected_by == "human:design-owner"


def test_a41_brain_task_frame_rejects_invalid_authority_surface_and_duplicate_uncertainties() -> None:
    common = {
        "frame_id": "FRAME-002",
        "goal": "Improve checkout recovery",
        "intent": "improve",
        "domain": "financial-services",
        "product_archetype": "payments-infrastructure",
        "change_surface": "FOCUSED",
        "validation_lane": "browser-plus-review",
        "risk": "medium",
        "source_task_contract_version": TASK_CONTRACT_VERSION,
    }

    with pytest.raises(ValidationError):
        BrainTaskFrame(**common, authority="root_admin")

    repeated = _known_uncertainty()
    with pytest.raises(ValidationError, match="uncertainty ids must be unique"):
        BrainTaskFrame(
            **common,
            uncertainties=[repeated, repeated],
        )

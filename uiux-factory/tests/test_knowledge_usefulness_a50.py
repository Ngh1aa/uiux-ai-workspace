from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.knowledge_usefulness_regression import evaluate_knowledge_usefulness


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
CORPUS = ROOT / "benchmarks/knowledge-usefulness-v1.json"
KNOWLEDGE_ROOT = WORKSPACE / "skills_UIUX/knowledge"


def test_a50_seed_records_are_keep_but_expansion_remains_blocked() -> None:
    report = evaluate_knowledge_usefulness(
        CORPUS,
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE_ROOT,
    )

    assert report.total == 3
    assert report.passed == 3
    assert {case.decision for case in report.cases} == {"KEEP"}
    assert all(case.actionable_delta for case in report.cases)
    assert all(case.domain_specificity for case in report.cases)
    assert all(case.skill_duplication_clear for case in report.cases)
    assert all(case.retrieval_noise_clear for case in report.cases)
    assert all(case.provenance_clear for case in report.cases)
    assert report.expand_allowed is False
    assert "human/model-assisted usefulness trial" in report.expand_blocker


def test_a50_governance_contract_has_no_expand_decision() -> None:
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    governance = payload["governance"]

    assert governance["allowed_decisions"] == ["KEEP", "REVISE", "REMOVE"]
    assert governance["expand_allowed"] is False
    assert payload["scope"] == "deterministic_context_usefulness_proxy_not_model_reasoning_or_product_evidence"

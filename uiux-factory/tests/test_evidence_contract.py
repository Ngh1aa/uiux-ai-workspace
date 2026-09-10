from __future__ import annotations

import json
from pathlib import Path

from core.contracts.evidence_contract_schema import EvidenceOutcome
from core.verification.evidence_contract import EvidenceContractEvaluator, RequirementRegistry


def test_registry_has_exactly_56_unique_requirements():
    registry = RequirementRegistry()
    ids = [rule.id for rule in registry.rules]
    assert len(ids) == 56
    assert len(set(ids)) == 56
    assert any(rule.verification_mode.value == "manual" for rule in registry.rules)
    assert all(rule.expectations for rule in registry.rules)
    assert all(rule.required_evidence for rule in registry.rules)


def test_missing_evidence_never_becomes_false_pass(tmp_path: Path):
    run_dir = tmp_path / "run"
    project_dir = tmp_path / "project"
    run_dir.mkdir()
    project_dir.mkdir()
    (project_dir / "index.html").write_text("<main><h1>Test</h1></main>", encoding="utf-8")

    report = EvidenceContractEvaluator().evaluate(
        run_id="test-run",
        run_dir=run_dir,
        project_dir=project_dir,
    )

    assert report.summary.total == 56
    assert report.machine_status == "blocked"
    assert report.final_status == "blocked"
    assert report.summary.passed == 0
    assert report.summary.untested > 0
    assert report.summary.cant_tell > 0


def test_project_digest_changes_when_output_changes(tmp_path: Path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    page = project_dir / "index.html"
    page.write_text("alpha", encoding="utf-8")
    evaluator = EvidenceContractEvaluator()
    first = evaluator.project_digest(project_dir)
    page.write_text("beta", encoding="utf-8")
    second = evaluator.project_digest(project_dir)
    assert first != second


def test_human_review_requires_reviewer_and_explicit_approval(tmp_path: Path):
    run_dir = tmp_path / "run"
    project_dir = tmp_path / "project"
    run_dir.mkdir()
    project_dir.mkdir()
    (project_dir / "index.html").write_text("<main></main>", encoding="utf-8")
    evaluator = EvidenceContractEvaluator()
    rule = next(rule for rule in evaluator.registry.rules if rule.id == "CRITIQUE-008")

    pending = evaluator._human_review_result(
        rule,
        run_dir,
        run_id="human-test",
        project_digest=evaluator.project_digest(project_dir),
    )
    assert pending.outcome == EvidenceOutcome.CANT_TELL

    (run_dir / "human-review.json").write_text(
        json.dumps({"reviewer": "Independent reviewer", "approved": True, "feedback": "Reviewed representative flow."}),
        encoding="utf-8",
    )
    approved = evaluator._human_review_result(
        rule,
        run_dir,
        run_id="human-test",
        project_digest=evaluator.project_digest(project_dir),
    )
    assert approved.outcome == EvidenceOutcome.PASSED

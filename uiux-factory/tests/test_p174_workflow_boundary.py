from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "p174-policy-drift-detection.yml"


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_p174_workflow_is_scheduled_and_registry_driven() -> None:
    text = _workflow_text()
    assert "schedule:" in text
    assert "workflow_dispatch:" in text
    assert "run-p174-policy-drift.py --matrix" in text
    assert "fromJSON(needs.registry.outputs.matrix)" in text
    assert "Ngh1aa/Nova" not in text
    assert "Ngh1aa/Lumen" not in text
    assert "Ngh1aa/cennext-b2b-prototype" not in text
    assert "Ngh1aa/LuxRoom" not in text


def test_target_checkout_is_read_only_and_no_target_mutation_command_exists() -> None:
    text = _workflow_text().lower()
    assert "persist-credentials: false" in text
    assert "target_branch_create_or_push" not in text
    assert "git push" not in text
    assert "gh pr create" not in text
    assert "merge_pull_request" not in text
    assert "vercel --prod" not in text
    assert "netlify deploy" not in text


def test_drift_report_uploads_before_failure_is_enforced() -> None:
    text = _workflow_text()
    drift_index = text.index("id: drift")
    upload_index = text.index("Upload P1.7.4 evidence")
    enforce_index = text.index("Enforce drift gate")
    assert drift_index < upload_index < enforce_index
    assert "continue-on-error: true" in text


def test_issue_mutation_is_scoped_to_factory_alerting_not_target_repositories() -> None:
    text = _workflow_text()
    assert "issues: write" in text
    assert "github.rest.issues.create" in text
    assert "github.rest.issues.update" in text
    assert "context.repo.owner" in text
    assert "context.repo.repo" in text

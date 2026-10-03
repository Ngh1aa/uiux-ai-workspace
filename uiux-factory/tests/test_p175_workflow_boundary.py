from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "p175-external-integration-discovery.yml"


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_p175_is_scheduled_registry_driven_and_can_read_deployments() -> None:
    text = _workflow_text()
    assert "schedule:" in text
    assert "workflow_dispatch:" in text
    assert "deployments: read" in text
    assert "run-p175-external-integration-discovery.py --matrix" in text
    assert "fromJSON(needs.registry.outputs.matrix)" in text
    assert "Ngh1aa/Nova" not in text
    assert "Ngh1aa/Lumen" not in text
    assert "Ngh1aa/cennext-b2b-prototype" not in text
    assert "Ngh1aa/LuxRoom" not in text


def test_target_repositories_remain_read_only() -> None:
    text = _workflow_text().lower()
    assert "persist-credentials: false" in text
    assert "git push" not in text
    assert "gh pr create" not in text
    assert "merge_pull_request" not in text
    assert "vercel --prod" not in text
    assert "netlify deploy" not in text


def test_external_discovery_receives_read_token_and_uploads_evidence_before_gate() -> None:
    text = _workflow_text()
    assert 'P175_GITHUB_TOKEN: ${{ github.token }}' in text
    discovery_index = text.index("id: discovery")
    upload_index = text.index("Upload P1.7.5 evidence")
    enforce_index = text.index("Enforce external drift gate")
    assert discovery_index < upload_index < enforce_index
    assert "continue-on-error: true" in text


def test_alert_mutation_is_factory_only() -> None:
    text = _workflow_text()
    assert "issues: write" in text
    assert "context.repo.owner" in text
    assert "context.repo.repo" in text
    assert "github.rest.issues.create" in text
    assert "github.rest.issues.update" in text


def test_p175_gate_runs_prior_governance_regressions() -> None:
    text = _workflow_text()
    assert "test_p175_external_integration_discovery.py" in text
    assert "test_p174_policy_drift.py" in text
    assert "test_p173_repository_policy_registry.py" in text
    assert "test_p172_external_side_effect_governance.py" in text
    assert "test_p171_authenticated_real_runner.py" in text

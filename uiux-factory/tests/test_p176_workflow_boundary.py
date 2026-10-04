from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "p176-provider-attestation.yml"
SCRIPT = ROOT / "skills_UIUX" / "scripts" / "run-p176-provider-attestation-truth.py"


def test_p176_workflow_is_controlled_read_only_provider_attestation() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in text
    assert "pull_request:" in text
    assert "schedule:" not in text
    assert "permissions:\n  contents: read" in text
    assert "persist-credentials: false" in text
    assert "P176_VERCEL_TOKEN: ${{ secrets.P176_VERCEL_TOKEN }}" in text
    assert "P176_VERCEL_TEAM_ID: ${{ secrets.P176_VERCEL_TEAM_ID }}" in text
    assert "continue-on-error: true" in text
    assert "Enforce fail-closed canonical truth" in text

    forbidden = [
        "git push",
        "gh pr merge",
        "merge_pull_request",
        "vercel deploy",
        "npm run deploy",
        "actions/create-github-app-token",
    ]
    assert not any(token in text for token in forbidden)


def test_p176_cli_has_no_mutation_or_release_switches() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert "P176_VERCEL_TOKEN" in text
    assert "P176_VERCEL_TEAM_ID" in text
    assert "--allow-deploy" not in text
    assert "--merge" not in text
    assert "--release" not in text
    assert "--write" not in text

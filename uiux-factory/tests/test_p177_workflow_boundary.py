from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "p177-multi-provider-attestation.yml"
SCRIPT = ROOT / "skills_UIUX" / "scripts" / "run-p177-multi-provider-attestation-truth.py"


def test_p177_workflow_is_read_only_and_manual_for_live_provider_calls() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in text
    assert "pull_request:" in text
    assert "schedule:" not in text
    assert "permissions:\n  contents: read" in text
    assert "persist-credentials: false" in text
    for secret in (
        "P177_VERCEL_TOKEN",
        "P177_NETLIFY_TOKEN",
        "P177_RENDER_TOKEN",
        "P177_CLOUDFLARE_API_TOKEN",
        "P177_CLOUDFLARE_ACCOUNT_ID",
        "P179_RAILWAY_TOKEN",
        "P179_RAILWAY_WORKSPACE_ID",
    ):
        assert secret in text

    forbidden = [
        "git push",
        "gh pr merge",
        "vercel deploy",
        "netlify deploy",
        "render deploy",
        "wrangler pages deploy",
        "npm run deploy",
    ]
    assert not any(token in text for token in forbidden)


def test_p177_cli_exposes_no_mutation_release_switches() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    for name in (
        "P177_VERCEL_TOKEN",
        "P177_NETLIFY_TOKEN",
        "P177_RENDER_TOKEN",
        "P177_CLOUDFLARE_API_TOKEN",
        "P177_CLOUDFLARE_ACCOUNT_ID",
    ):
        assert name in text
    assert "--allow-deploy" not in text
    assert "--merge" not in text
    assert "--release" not in text
    assert "--write" not in text

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "p1710-continuous-provider-truth.yml"
SCRIPT = ROOT / "skills_UIUX" / "scripts" / "run-p1710-continuous-provider-truth.py"


def test_p1710_workflow_is_scheduled_manual_and_read_only() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "schedule:" in text
    assert 'cron: "17 1 * * *"' in text
    assert "workflow_dispatch:" in text
    assert "permissions:\n  contents: read" in text
    assert "persist-credentials: false" in text
    assert "continue-on-error: true" not in text


def test_p1710_schedule_consumes_optional_provider_secrets_without_requiring_them() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")

    for name in (
        "P177_VERCEL_TOKEN",
        "P177_VERCEL_TEAM_ID",
        "P177_NETLIFY_TOKEN",
        "P177_RENDER_TOKEN",
        "P177_CLOUDFLARE_API_TOKEN",
        "P177_CLOUDFLARE_ACCOUNT_ID",
        "P179_RAILWAY_TOKEN",
        "P179_RAILWAY_WORKSPACE_ID",
    ):
        assert name in workflow
        assert name in script

    assert "Missing opt-in provider credentials are degraded coverage, not workflow failure." in script


def test_p1710_surfaces_have_no_mutation_release_commands() -> None:
    text = "\n".join(
        [
            WORKFLOW.read_text(encoding="utf-8"),
            SCRIPT.read_text(encoding="utf-8"),
        ]
    ).lower()

    forbidden = [
        "git push",
        "gh pr merge",
        "vercel deploy",
        "netlify deploy",
        "render deploy",
        "railway up",
        "railway deploy",
        "wrangler pages deploy",
        "firebase deploy",
        "npm run deploy",
        "--merge",
        "--release",
        "--write",
    ]
    assert not any(token in text for token in forbidden)


def test_p1710_monitor_runs_only_on_schedule_or_explicit_dispatch() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    condition = "if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'"
    assert text.count(condition) == 2

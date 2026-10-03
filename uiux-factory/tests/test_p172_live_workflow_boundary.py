from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
LIVE_WORKFLOW = WORKSPACE / ".github" / "workflows" / "p172-external-side-effect-live-dogfood.yml"
LIVE_SCRIPT = WORKSPACE / "skills_UIUX" / "scripts" / "run-p172-external-side-effect-governance.py"
DOGFOOD = ROOT / "core" / "dogfood" / "p172_external_side_effect_governance.py"


def test_p172_live_lane_is_read_only_and_has_no_transaction_runner() -> None:
    text = "\n".join(
        [
            LIVE_WORKFLOW.read_text(encoding="utf-8"),
            LIVE_SCRIPT.read_text(encoding="utf-8"),
            DOGFOOD.read_text(encoding="utf-8"),
        ]
    )
    forbidden = (
        "GitHubProductionRunner",
        "git push",
        "gh pr create",
        "gh pr merge",
        "merge_pull_request",
        "create_pull_request",
        "vercel deploy",
        "netlify deploy",
        "npm run deploy",
        "actions/deploy-pages",
    )
    assert not any(token in text for token in forbidden)


def test_p172_live_lane_uses_existing_pr_evidence_and_secret_read_boundary() -> None:
    text = LIVE_WORKFLOW.read_text(encoding="utf-8")
    assert "secrets.UIUX_TARGET_REPO_TOKEN" in text
    assert "repos/Ngh1aa/LuxRoom/pulls/24" in text
    assert "--pr-number 24" in text
    assert "target mutation, merge, or deployment" in text.lower()
    assert "getCollaboratorPermissionLevel" in text


def test_p172_live_dogfood_requires_main_unchanged() -> None:
    text = DOGFOOD.read_text(encoding="utf-8")
    assert "base_sha_before == base_sha_after" in text
    assert '"target_mutation": "NOT_PERFORMED"' in text
    assert '"merge": "NOT_PERFORMED"' in text

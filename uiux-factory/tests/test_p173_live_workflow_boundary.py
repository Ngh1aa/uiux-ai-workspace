from __future__ import annotations

from pathlib import Path

from core.dogfood.p173_repository_policy_registry import DOGFOOD_TARGETS


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
LIVE_WORKFLOW = WORKSPACE / ".github" / "workflows" / "p173-repository-policy-live-dogfood.yml"
LIVE_SCRIPT = WORKSPACE / "skills_UIUX" / "scripts" / "run-p173-repository-policy-registry.py"
DOGFOOD = ROOT / "core" / "dogfood" / "p173_repository_policy_registry.py"


def test_p173_live_lane_is_read_only_and_has_no_transaction_runner() -> None:
    text = "\n".join(
        [
            LIVE_WORKFLOW.read_text(encoding="utf-8"),
            LIVE_SCRIPT.read_text(encoding="utf-8"),
            DOGFOOD.read_text(encoding="utf-8"),
        ]
    )
    forbidden = (
        "GitHubProductionRunner",
        "GitHubTransactionConfig",
        "git push",
        "gh pr create",
        "gh pr edit",
        "gh pr merge",
        "merge_pull_request",
        "create_pull_request",
        "update_pull_request",
        "vercel deploy",
        "netlify deploy",
        "npm run deploy",
        "actions/deploy-pages",
    )
    assert not any(token in text for token in forbidden)


def test_p173_live_lane_checks_out_all_four_targets_without_persisted_credentials() -> None:
    text = LIVE_WORKFLOW.read_text(encoding="utf-8")
    for repository in (
        "Ngh1aa/Nova",
        "Ngh1aa/Lumen",
        "Ngh1aa/cennext-b2b-prototype",
        "Ngh1aa/LuxRoom",
    ):
        assert f"repository: {repository}" in text
    assert text.count("persist-credentials: false") >= 5
    assert "secrets.UIUX_TARGET_REPO_TOKEN" in text


def test_p173_live_lane_uses_pinned_existing_pr_evidence() -> None:
    text = LIVE_WORKFLOW.read_text(encoding="utf-8")
    assert "repos/Ngh1aa/Nova/pulls/73" in text
    assert "repos/Ngh1aa/cennext-b2b-prototype/pulls/8" in text
    assert "repos/Ngh1aa/LuxRoom/pulls/24" in text
    matrix = {target.repository: target.evidence_pr_number for target in DOGFOOD_TARGETS}
    assert matrix == {
        "Ngh1aa/Nova": 73,
        "Ngh1aa/Lumen": None,
        "Ngh1aa/cennext-b2b-prototype": 8,
        "Ngh1aa/LuxRoom": 24,
    }


def test_p173_live_lane_installs_dependencies_before_policy_evaluation() -> None:
    text = LIVE_WORKFLOW.read_text(encoding="utf-8")
    install_index = text.index("Install Factory runtime dependencies")
    evaluate_index = text.index("Evaluate repository policies against four real targets")
    assert install_index < evaluate_index
    assert '"pydantic>=2.5.3,<3"' in text
    assert '"python-dotenv>=1,<2"' in text


def test_p173_live_dogfood_requires_all_main_branches_unchanged() -> None:
    text = DOGFOOD.read_text(encoding="utf-8")
    assert "base_sha_before == base_sha_after" in text
    assert '"target_mutation": "NOT_PERFORMED"' in text
    assert '"target_branch_create_or_push": "NOT_PERFORMED"' in text
    assert '"target_pr_create_or_update": "NOT_PERFORMED"' in text
    assert '"merge": "NOT_PERFORMED"' in text

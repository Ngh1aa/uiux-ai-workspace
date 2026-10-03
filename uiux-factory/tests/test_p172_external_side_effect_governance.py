from __future__ import annotations

from pathlib import Path

import pytest

from core.dogfood.p171_authenticated_real_runner import DOGFOOD_PROFILES
from core.runtime.flow_os.external_side_effects import (
    ExternalSideEffectBlocked,
    ExternalSideEffectEvidence,
    GitHubExternalSideEffectObserver,
    PreviewPolicy,
    assess_external_side_effects,
    detect_static_integrations,
)


def _vercel_observed() -> ExternalSideEffectEvidence:
    return ExternalSideEffectEvidence(
        provider="vercel",
        effect="pr-preview",
        source="github-pr-comment",
        state="observed",
        url="https://github.com/Ngh1aa/LuxRoom/pull/24#issuecomment-test",
        detail="Vercel preview observed.",
    )


def test_preview_allowed_records_observed_side_effect_without_blocking() -> None:
    assessment = assess_external_side_effects(
        "Ngh1aa/LuxRoom",
        PreviewPolicy.PR_PREVIEW_ALLOWED,
        [_vercel_observed()],
        inspection_complete=True,
    )
    assert assessment.status == "PREVIEW_OBSERVED"
    assert assessment.mutation_allowed is True
    assert assessment.evidence[0].provider == "vercel"
    assessment.require_mutation_allowed()


def test_zero_deploy_strict_blocks_observed_preview_before_mutation() -> None:
    assessment = assess_external_side_effects(
        "Ngh1aa/LuxRoom",
        PreviewPolicy.ZERO_DEPLOY_STRICT,
        [_vercel_observed()],
        inspection_complete=True,
    )
    assert assessment.status == "BLOCKED_EXTERNAL_SIDE_EFFECT"
    assert assessment.mutation_allowed is False
    with pytest.raises(ExternalSideEffectBlocked, match="zero-deploy-strict"):
        assessment.require_mutation_allowed()


def test_zero_deploy_strict_fails_closed_when_integration_visibility_is_unknown() -> None:
    assessment = assess_external_side_effects(
        "Ngh1aa/Unknown",
        PreviewPolicy.ZERO_DEPLOY_STRICT,
        [],
        inspection_complete=False,
    )
    assert assessment.status == "UNKNOWN_EXTERNAL_SIDE_EFFECT"
    assert assessment.mutation_allowed is False


def test_preview_allowed_may_proceed_with_explicit_unknown_evidence_state() -> None:
    assessment = assess_external_side_effects(
        "Ngh1aa/Unknown",
        PreviewPolicy.PR_PREVIEW_ALLOWED,
        [],
        inspection_complete=False,
    )
    assert assessment.status == "UNKNOWN_EXTERNAL_SIDE_EFFECT"
    assert assessment.mutation_allowed is True


def test_completed_clean_inspection_is_not_misreported_as_unknown() -> None:
    assessment = assess_external_side_effects(
        "Ngh1aa/Clean",
        PreviewPolicy.ZERO_DEPLOY_STRICT,
        [],
        inspection_complete=True,
    )
    assert assessment.status == "NONE_DETECTED"
    assert assessment.mutation_allowed is True


def test_static_detector_finds_vercel_netlify_and_github_pages(tmp_path: Path) -> None:
    (tmp_path / "vercel.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "netlify.toml").write_text("[build]\n", encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "pages.yml").write_text("uses: actions/deploy-pages@v4\n", encoding="utf-8")
    evidence = detect_static_integrations(tmp_path)
    assert {item.provider for item in evidence} == {"vercel", "netlify", "github-pages"}
    assert all(item.state == "configured" for item in evidence)


def test_static_detector_does_not_invent_absence_evidence(tmp_path: Path) -> None:
    assert detect_static_integrations(tmp_path) == ()


def test_vercel_bot_comment_is_provider_evidence() -> None:
    evidence = GitHubExternalSideEffectObserver._comment_evidence(
        {
            "user": {"login": "vercel[bot]"},
            "body": "Deployment Ready — Preview",
            "html_url": "https://github.com/Ngh1aa/LuxRoom/pull/24#issuecomment-1",
        },
        pr_url="https://github.com/Ngh1aa/LuxRoom/pull/24",
    )
    assert evidence is not None
    assert evidence.provider == "vercel"
    assert evidence.effect == "pr-preview"
    assert evidence.state == "observed"


def test_netlify_and_pages_bot_evidence_are_distinct() -> None:
    observer = GitHubExternalSideEffectObserver
    netlify = observer._comment_evidence(
        {"user": {"login": "netlify[bot]"}, "body": "Deploy Preview ready"},
        pr_url="https://github.com/example/repo/pull/1",
    )
    pages = observer._comment_evidence(
        {"user": {"login": "github-actions[bot]"}, "body": "GitHub Pages deployment ready"},
        pr_url="https://github.com/example/repo/pull/2",
    )
    assert netlify is not None and netlify.provider == "netlify"
    assert pages is not None and pages.provider == "github-pages"


def test_p171_luxroom_profile_explicitly_opts_into_pr_preview() -> None:
    profile = DOGFOOD_PROFILES["luxroom-cart-total-live-region"]
    assert profile.preview_policy == PreviewPolicy.PR_PREVIEW_ALLOWED.value
    assert "external PR preview side effects are allowed" in profile.pr_body
    assert "no production deploy/release" in profile.pr_body


def test_assessment_serialization_keeps_policy_status_and_evidence() -> None:
    payload = assess_external_side_effects(
        "Ngh1aa/LuxRoom",
        PreviewPolicy.PR_PREVIEW_ALLOWED,
        [_vercel_observed()],
        inspection_complete=True,
    ).to_dict()
    assert payload["version"] == "1.0"
    assert payload["policy"] == "pr-preview-allowed"
    assert payload["status"] == "PREVIEW_OBSERVED"
    assert payload["evidence"][0]["provider"] == "vercel"

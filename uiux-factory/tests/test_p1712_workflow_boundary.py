from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "p1710-continuous-provider-truth.yml"
FETCHER = ROOT / "skills_UIUX" / "scripts" / "fetch-p1712-provider-truth-baseline.py"
TRANSITION = ROOT / "skills_UIUX" / "scripts" / "run-p1712-provider-truth-transition.py"


def test_p1712_workflow_has_read_only_historical_actions_access() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "permissions:\n  contents: read\n  actions: read" in text
    assert "provider-truth-transition:" in text
    assert "needs: [fleet-summary]" in text
    assert "if: always() && (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')" in text


def test_p1712_workflow_reads_current_and_previous_summary_then_uploads_transition() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "name: p1711-provider-truth-fleet-summary" in text
    assert "fetch-p1712-provider-truth-baseline.py" in text
    assert "run-p1712-provider-truth-transition.py" in text
    assert "name: p1712-provider-truth-transition" in text
    assert "baseline-selection.json" in text


def test_p1712_baseline_absence_is_not_encoded_as_workflow_failure() -> None:
    fetcher = FETCHER.read_text(encoding="utf-8")
    transition = TRANSITION.read_text(encoding="utf-8")

    assert 'print("BASELINE_NOT_AVAILABLE")' in fetcher
    assert "return 0" in fetcher
    assert "return 0" in transition
    assert "workflow_blocking" not in transition.lower()


def test_p1712_surfaces_have_no_alert_or_mutation_authority() -> None:
    text = "\n".join(
        [
            WORKFLOW.read_text(encoding="utf-8"),
            FETCHER.read_text(encoding="utf-8"),
            TRANSITION.read_text(encoding="utf-8"),
        ]
    ).lower()

    forbidden = (
        "gh issue create",
        "gh pr create",
        "gh pr merge",
        "git push",
        "vercel deploy",
        "netlify deploy",
        "railway deploy",
        "firebase deploy",
        "curl -x post",
        "slack webhook",
    )
    assert not any(token in text for token in forbidden)

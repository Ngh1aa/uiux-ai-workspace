from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "p1710-continuous-provider-truth.yml"
SCRIPT = ROOT / "skills_UIUX" / "scripts" / "run-p1711-continuous-provider-truth-aggregate.py"


def test_p1711_aggregate_runs_after_monitor_even_when_matrix_has_failures() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "aggregate:" in text
    assert "needs: [matrix, monitor]" in text
    assert "always() && (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')" in text
    assert "actions/download-artifact@v8" in text
    assert "pattern: p1710-continuous-provider-truth-*" in text
    assert "merge-multiple: true" in text


def test_p1711_aggregate_uses_exact_expected_registry_matrix_and_publishes_summary() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")

    assert "P1711_EXPECTED_MATRIX: ${{ needs.matrix.outputs.repositories }}" in workflow
    assert "run-p1711-continuous-provider-truth-aggregate.py" in workflow
    assert "p1711-continuous-provider-truth-fleet.md" in workflow
    assert "$GITHUB_STEP_SUMMARY" in workflow
    assert "P1711_EXPECTED_MATRIX" in script


def test_p1711_preserves_read_only_authority() -> None:
    text = "\n".join(
        [
            WORKFLOW.read_text(encoding="utf-8"),
            SCRIPT.read_text(encoding="utf-8"),
        ]
    ).lower()

    assert "permissions:\n  contents: read" in WORKFLOW.read_text(encoding="utf-8")
    forbidden = [
        "issues: write",
        "contents: write",
        "git push",
        "gh pr",
        "gh issue",
        "vercel deploy",
        "netlify deploy",
        "render deploy",
        "railway up",
        "wrangler pages deploy",
        "firebase deploy",
        "--merge",
        "--release",
    ]
    assert not any(token in text for token in forbidden)


def test_p1711_aggregate_is_not_executed_on_pull_request_or_push() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    aggregate_condition = "if: always() && (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')"
    assert text.count(aggregate_condition) == 1

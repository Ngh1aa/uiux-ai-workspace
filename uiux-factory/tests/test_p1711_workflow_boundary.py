from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "p1710-continuous-provider-truth.yml"
SCRIPT = ROOT / "skills_UIUX" / "scripts" / "run-p1711-provider-truth-fleet-summary.py"


def test_p1711_aggregate_runs_after_monitor_even_if_matrix_has_failures() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "fleet-summary:" in text
    assert "needs: [matrix, monitor]" in text
    assert "if: always() && (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')" in text
    assert "pattern: p1710-continuous-provider-truth-*" in text


def test_p1711_is_read_only_and_has_no_alert_mutation_authority() -> None:
    text = (WORKFLOW.read_text(encoding="utf-8") + "\n" + SCRIPT.read_text(encoding="utf-8")).lower()
    for forbidden in ("gh issue create", "git push", "gh pr", "deploy", "--write-repo"):
        assert forbidden not in text

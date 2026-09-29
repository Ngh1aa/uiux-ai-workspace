from pathlib import Path


def test_reusable_external_agent_checks_out_factory_explicitly() -> None:
    root = Path(__file__).resolve().parents[2]
    workflow = (root / ".github" / "workflows" / "external-agent-runner.yml").read_text(encoding="utf-8")

    assert workflow.count("- name: Checkout Factory") == 2
    assert workflow.count("repository: Ngh1aa/uiux-ai-workspace") == 2
    assert workflow.count("ref: main") >= 2
    assert "python -B skills_UIUX/scripts/github-external-agent-runner.py" in workflow
    assert "working-directory: uiux-factory/qa" in workflow

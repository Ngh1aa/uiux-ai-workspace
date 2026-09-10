from pathlib import Path

import pytest

from core.contracts.prototype_acceptance_schema import AcceptanceSummary, PrototypeAcceptanceReport
from core.contracts.quality_loop_schema import QualityLoopResult
from core.runtime.run_context import RunContext


class FakeAcceptanceEvaluator:
    def __init__(self, report: PrototypeAcceptanceReport):
        self.report = report

    def evaluate(self, **_kwargs) -> PrototypeAcceptanceReport:
        return self.report


def quality_artifact(context: RunContext) -> Path:
    browser = context.run_dir / "browser-report.json"
    critic = context.run_dir / "visual-critic.json"
    browser.write_text("{}", encoding="utf-8")
    critic.write_text("{}", encoding="utf-8")
    quality = QualityLoopResult(
        status="passed",
        project_slug="demo",
        project_dir=str(context.run_dir),
        max_iterations=1,
        iterations=[],
        final_score=95,
        stop_reason="visual_critic_passed",
        browser_report_path=str(browser),
        visual_critic_path=str(critic),
    )
    path = context.run_dir / "quality-loop.json"
    path.write_text(quality.model_dump_json(indent=2), encoding="utf-8")
    context.add_artifact("quality_loop", path)
    return path


def report(context: RunContext, machine_status: str) -> PrototypeAcceptanceReport:
    return PrototypeAcceptanceReport(
        run_id=context.run_id,
        project_dir=str(context.run_dir),
        project_digest="a" * 64,
        browser_report_path=str(context.run_dir / "browser-report.json"),
        visual_critic_path=str(context.run_dir / "visual-critic.json"),
        requirements=[],
        results=[],
        summary=AcceptanceSummary(total=56, passed=8, untested=46, cantTell=2, implemented=8, planned=46, manual=2),
        machine_status=machine_status,
        final_status="blocked",
        blocking_requirement_ids=[] if machine_status == "passed" else ["P1-03"],
        human_review_requirement_ids=["P7-02", "P7-08"],
    )


def test_complete_registers_acceptance_artifact_before_run_completed(tmp_path: Path, monkeypatch) -> None:
    context = RunContext(root=tmp_path, goal="prototype", run_id="accept-pass")
    context.initialize()
    quality_artifact(context)
    fake = FakeAcceptanceEvaluator(report(context, "passed"))
    monkeypatch.setattr(
        "core.verification.prototype_acceptance.PrototypeAcceptanceEvaluator",
        lambda: fake,
    )

    context.complete()

    acceptance = Path(context.artifacts["prototype_acceptance"])
    assert acceptance.is_file()
    assert context.status == "completed"
    assert '"final_status": "blocked"' in acceptance.read_text(encoding="utf-8")


def test_complete_blocks_when_machine_requirement_is_unresolved(tmp_path: Path, monkeypatch) -> None:
    context = RunContext(root=tmp_path, goal="prototype", run_id="accept-block")
    context.initialize()
    quality_artifact(context)
    fake = FakeAcceptanceEvaluator(report(context, "blocked"))
    monkeypatch.setattr(
        "core.verification.prototype_acceptance.PrototypeAcceptanceEvaluator",
        lambda: fake,
    )

    with pytest.raises(RuntimeError, match="P1-03"):
        context.complete()

    assert Path(context.artifacts["prototype_acceptance"]).is_file()
    assert context.status == "running"

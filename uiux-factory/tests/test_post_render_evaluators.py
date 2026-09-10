import json
import sys
import types
from pathlib import Path

# Foundation CI intentionally does not install the full MetaGPT runtime. The
# post-render module only needs Action as an import-time base class through the
# existing StaticServer module, so stub that boundary for pure evaluator tests.
if "metagpt.actions" not in sys.modules:
    metagpt = types.ModuleType("metagpt")
    actions = types.ModuleType("metagpt.actions")
    actions.Action = object
    metagpt.actions = actions
    sys.modules.setdefault("metagpt", metagpt)
    sys.modules.setdefault("metagpt.actions", actions)

from core.contracts.evidence_contract_schema import EvidenceOutcome
from core.verification.evidence_contract import EvidenceContractEvaluator, RequirementRegistry
from core.verification.post_render_evaluators import PostRenderEvaluatorSuite


def test_timing_parser_and_token_overlap_are_conservative():
    assert PostRenderEvaluatorSuite._parse_ms_list("150ms, 0.2s") == [150.0, 200.0]
    assert PostRenderEvaluatorSuite._parse_ms_list("0s, garbage") == [0.0]
    assert PostRenderEvaluatorSuite._token_overlap("luxury fragrance ecommerce", "luxury fragrance store") >= 0.5
    assert PostRenderEvaluatorSuite._token_overlap("", "anything") == 0.0


def test_dedicated_report_is_bound_to_current_project_digest(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "index.html").write_text("<main>Hello</main>", encoding="utf-8")
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    evaluator = EvidenceContractEvaluator()
    digest = evaluator.project_digest(project)
    report = {
        "schema_version": 1,
        "evaluator": "preferred-touch-targets",
        "evaluator_version": "1.0.0",
        "project_digest": digest,
        "requirements": {
            "RESPONSIVE-003": {
                "outcome": "passed",
                "applicable": True,
                "rationale": "all targets large enough",
                "test_targets": [],
                "evidence_files": [],
            }
        },
    }
    (run_dir / "touch-target-metrics.json").write_text(json.dumps(report), encoding="utf-8")
    rule = next(rule for rule in RequirementRegistry().rules if rule.id == "RESPONSIVE-003")

    result = evaluator._dedicated_report_result(
        rule,
        run_dir,
        run_id="run-1",
        project_digest=digest,
    )
    assert result.outcome == EvidenceOutcome.PASSED

    (project / "index.html").write_text("<main>Changed</main>", encoding="utf-8")
    changed_digest = evaluator.project_digest(project)
    stale = evaluator._dedicated_report_result(
        rule,
        run_dir,
        run_id="run-1",
        project_digest=changed_digest,
    )
    assert stale.outcome == EvidenceOutcome.UNTESTED
    assert "stale" in stale.rationale.lower()


def test_missing_requirement_row_never_auto_passes(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "index.html").write_text("<main>Hello</main>", encoding="utf-8")
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    evaluator = EvidenceContractEvaluator()
    digest = evaluator.project_digest(project)
    (run_dir / "squint-review.json").write_text(
        json.dumps({"project_digest": digest, "requirements": {}}),
        encoding="utf-8",
    )
    rule = next(rule for rule in RequirementRegistry().rules if rule.id == "VISUAL-010")
    result = evaluator._dedicated_report_result(
        rule,
        run_dir,
        run_id="run-2",
        project_digest=digest,
    )
    assert result.outcome == EvidenceOutcome.UNTESTED


def test_blind_comparison_requires_real_overlap():
    assert PostRenderEvaluatorSuite._token_overlap(
        "luxury fragrance ecommerce",
        "developer dashboard analytics",
    ) == 0.0


def test_requested_evaluator_families_are_wired_to_dedicated_reports():
    expected = {
        "interaction_trace",
        "interaction_timing",
        "state_crawler",
        "preferred_touch_targets",
        "content_stress",
        "squint_critic",
        "blind_five_second",
    }
    assert expected.issubset(EvidenceContractEvaluator.DEDICATED_REPORTS)

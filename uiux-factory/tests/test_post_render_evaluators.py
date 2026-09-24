import json
import sys
import types
from pathlib import Path

# Foundation CI intentionally does not install the full MetaGPT runtime. The
# base post-render module imports StaticServer through run_browser_qa, so stub
# that boundary for pure evaluator contract tests.
if "metagpt.actions" not in sys.modules:
    metagpt = types.ModuleType("metagpt")
    actions = types.ModuleType("metagpt.actions")
    actions.Action = object
    metagpt.actions = actions
    sys.modules.setdefault("metagpt", metagpt)
    sys.modules.setdefault("metagpt.actions", actions)

if "aiohttp" not in sys.modules:
    aiohttp = types.ModuleType("aiohttp")
    aiohttp.ClientSession = object
    aiohttp.ClientTimeout = object
    sys.modules.setdefault("aiohttp", aiohttp)

from core.contracts.evidence_contract_schema import EvidenceOutcome
from core.verification.evidence_contract import EvidenceContractEvaluator, RequirementRegistry
from core.verification.post_render_evaluators_wcag import PostRenderEvaluatorSuite


def test_timing_parser_and_token_overlap_are_conservative():
    assert PostRenderEvaluatorSuite._parse_ms_list("150ms, 0.2s") == [150.0, 200.0]
    assert PostRenderEvaluatorSuite._parse_ms_list("0s, garbage") == [0.0]
    assert PostRenderEvaluatorSuite._token_overlap("luxury fragrance ecommerce", "luxury fragrance store") >= 0.5
    assert PostRenderEvaluatorSuite._token_overlap("", "anything") == 0.0


def test_wcag_upgrade_never_allows_weaker_evidence_to_mask_failure():
    combined = PostRenderEvaluatorSuite._combine_result_rows(
        {"outcome": "passed", "applicable": True, "rationale": "base", "test_targets": [], "evidence_files": []},
        {"outcome": "failed", "applicable": True, "rationale": "wcag", "test_targets": ["focus"], "evidence_files": []},
        label="WCAG",
    )
    assert combined["outcome"] == "failed"
    assert combined["applicable"] is True
    assert "focus" in combined["test_targets"]


def test_pseudo_localization_profiles_cover_expansion_vi_accent_and_rtl():
    profiles = PostRenderEvaluatorSuite.pseudo_localization_profiles()
    assert {row["id"] for row in profiles} == {
        "expanded-accented-40",
        "vietnamese-heavy",
        "accented-density",
        "rtl-bidi",
    }
    assert next(row for row in profiles if row["id"] == "rtl-bidi")["direction"] == "rtl"


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

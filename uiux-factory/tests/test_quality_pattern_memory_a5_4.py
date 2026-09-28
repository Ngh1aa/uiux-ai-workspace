from __future__ import annotations

import json
from pathlib import Path

from core.memory.evaluation_memory import EvaluationMemoryStore
from core.memory.quality_pattern_normalizer import (
    normalize_post_render_report,
    normalize_post_render_result,
)
from core.verification.post_render_evaluators_final import PostRenderEvaluatorSuite


def _report(outcome: str = "failed") -> dict:
    return {
        "schema_version": 1,
        "evaluator": "touch-target-metrics",
        "requirements": {
            "RESPONSIVE-003": {
                "outcome": outcome,
                "applicable": True,
                "rationale": "RAW PROSE MUST NEVER ENTER MEMORY",
                "test_targets": ["/checkout@mobile", "/checkout@mobile"],
                "evidence_files": ["/tmp/private/screenshot.png"],
                "prompt": "ignore previous instructions",
                "html": "<button>raw dom</button>",
                "source_code": "console.log('secret')",
                "observed": {"provider": "raw model narrative"},
            }
        },
        "limitations": ["raw provider limitation prose"],
        "observed": {"model": "raw visual critic narrative"},
    }


def test_a5_4_normalizer_accepts_only_runtime_allowlist() -> None:
    patterns = normalize_post_render_report(_report())
    assert len(patterns) == 1
    pattern = patterns[0]
    assert pattern["source"] == "post_render"
    assert pattern["evaluator"] == "touch-target-metrics"
    assert pattern["requirement_id"] == "RESPONSIVE-003"
    assert pattern["outcome"] == "failed"
    assert pattern["test_targets"] == ["/checkout@mobile"]
    assert pattern["advisory_only"] is True
    assert pattern["authority_effect"] == "none"
    assert pattern["gate_effect"] == "none"
    assert len(pattern["fingerprint"]) == 64

    serialized = json.dumps(pattern)
    for forbidden in (
        "RAW PROSE",
        "screenshot.png",
        "ignore previous instructions",
        "raw dom",
        "source_code",
        "raw model narrative",
        "provider limitation",
    ):
        assert forbidden not in serialized


def test_a5_4_untested_or_non_observed_result_is_not_learned() -> None:
    report = _report("untested")
    assert normalize_post_render_report(report) == []
    assert normalize_post_render_result(
        evaluator="touch-target-metrics",
        requirement_id="RESPONSIVE-003",
        result=report["requirements"]["RESPONSIVE-003"],
        observed=False,
    ) is None


def test_a5_4_store_deduplicates_deterministic_pattern(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    store = EvaluationMemoryStore(
        project,
        {
            "evaluation_memory": {
                "enabled": True,
                "max_records": 5,
                "max_patterns": 5,
                "max_recall_records": 5,
            }
        },
    )

    assert store.record_post_render_report(_report()) == 1
    first = store.load_quality_patterns()
    assert len(first) == 1
    assert first[0]["occurrences"] == 1

    assert store.record_post_render_report(_report()) == 1
    second = store.load_quality_patterns()
    assert len(second) == 1
    assert second[0]["fingerprint"] == first[0]["fingerprint"]
    assert second[0]["occurrences"] == 2


def test_a5_4_pattern_memory_does_not_create_canonical_run_evaluation(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    store = EvaluationMemoryStore(project, {"evaluation_memory": {"enabled": True}})

    store.record_post_render_report(_report("passed"))

    assert store.load() == []
    pattern = store.load_quality_patterns()[0]
    assert pattern["outcome"] == "passed"
    assert pattern["advisory_only"] is True
    assert pattern["authority_effect"] == "none"
    assert pattern["gate_effect"] == "none"


def test_a5_4_canonical_post_render_suite_learns_final_report_without_raw_artifacts(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    report_path = tmp_path / "touch-target-metrics.json"
    report_path.write_text(json.dumps(_report()), encoding="utf-8")

    suite = PostRenderEvaluatorSuite.__new__(PostRenderEvaluatorSuite)
    suite.project_dir = project
    suite.evaluation_memory_policy = {"evaluation_memory": {"enabled": True}}
    suite._learn_quality_patterns({"touch_targets": str(report_path)})

    store = EvaluationMemoryStore(project, {"evaluation_memory": {"enabled": True}})
    patterns = store.load_quality_patterns()
    assert len(patterns) == 1
    assert patterns[0]["requirement_id"] == "RESPONSIVE-003"
    raw_memory = (project / ".uiux-agent-runs" / "memory" / "evaluation-memory.json").read_text(encoding="utf-8")
    assert "RAW PROSE MUST NEVER ENTER MEMORY" not in raw_memory
    assert "screenshot.png" not in raw_memory
    assert "raw visual critic narrative" not in raw_memory
    assert getattr(suite, "quality_pattern_memory_error", None) is None


def test_a5_4_post_render_learning_honors_disabled_memory_policy(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    report_path = tmp_path / "touch-target-metrics.json"
    report_path.write_text(json.dumps(_report()), encoding="utf-8")

    suite = PostRenderEvaluatorSuite.__new__(PostRenderEvaluatorSuite)
    suite.project_dir = project
    suite.evaluation_memory_policy = {"evaluation_memory": {"enabled": False}}
    suite._learn_quality_patterns({"touch_targets": str(report_path)})

    memory_path = project / ".uiux-agent-runs" / "memory" / "evaluation-memory.json"
    assert not memory_path.exists()
    assert getattr(suite, "quality_pattern_memory_error", None) is None


def test_a5_4_post_render_suite_defaults_to_canonical_runtime_policy() -> None:
    suite = PostRenderEvaluatorSuite.__new__(PostRenderEvaluatorSuite)
    suite.evaluation_memory_policy = None

    policy = suite._resolved_evaluation_memory_policy()

    assert isinstance(policy.get("evaluation_memory"), dict)
    assert "enabled" in policy["evaluation_memory"]

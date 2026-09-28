from __future__ import annotations

from core.runtime.flow_os.provider import ProviderStageRequest, render_provider_prompt


def _evaluation_insight() -> dict:
    return {
        "schema_version": 1,
        "advisory_only": True,
        "flow_id": "professional-website-redesign",
        "sample_size": 4,
        "passed_runs": 2,
        "failed_or_blocked_runs": 2,
        "pass_rate": 0.5,
        "average_replans": 1.25,
        "recurrent_failure_channels": [
            {"channel": "qa:browser:/pricing", "count": 3, "raw_stdout": "MUST NOT LEAK"}
        ],
        "observed_evidence_types": ["browser", "validator"],
        "matched_signature": {"website_type": "saas"},
        "authority_effect": "none",
        "gate_effect": "none",
        "prompt": "RAW EVALUATION PROMPT MUST NOT LEAK",
        "provider_summary": "RAW PROVIDER SUMMARY MUST NOT LEAK",
    }


def _quality_insight() -> dict:
    return {
        "schema_version": 1,
        "source": "post_render_quality_memory",
        "advisory_only": True,
        "scope": "project_scoped_history",
        "relevance": "historical_only_not_current_evidence",
        "observed_pattern_count": 2,
        "observed_occurrences": 7,
        "outcome_occurrences": {"passed": 2, "failed": 4, "cantTell": 1},
        "recurrent_attention_patterns": [
            {
                "evaluator": "touch-target-metrics",
                "requirement_id": "RESPONSIVE-003",
                "outcome": "failed",
                "applicable": True,
                "occurrences": 4,
                "rationale": "RAW QUALITY RATIONALE MUST NOT LEAK",
                "test_targets": ["/@mobile"],
                "screenshot": "/tmp/private.png",
            }
        ],
        "recurrent_pass_patterns": [
            {
                "evaluator": "visual-hierarchy",
                "requirement_id": "VISUAL-001",
                "outcome": "passed",
                "applicable": True,
                "occurrences": 2,
                "html": "<main>PRIVATE DOM</main>",
            }
        ],
        "authority_effect": "none",
        "flow_effect": "none",
        "replan_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "merge_effect": "none",
        "release_effect": "none",
        "source_code": "console.log('private')",
    }


def _request(agent: str, task_context: dict) -> ProviderStageRequest:
    return ProviderStageRequest(
        goal="Improve the current product UI",
        project_root="/tmp/project",
        flow_id="professional-website-redesign",
        flow_revision=1,
        stage_id="qa" if agent == "qa" else "stage",
        agent=agent,
        purpose="test",
        gates=[],
        task_context=task_context,
        authority="read_only",
        tools=[],
        skill_context=[],
        source_context=[],
        observations=[],
    )


def test_a5_7_research_provider_cannot_receive_quality_memory() -> None:
    request = _request(
        "research",
        {
            "website_type": "saas",
            "prior_evaluation_insight": _evaluation_insight(),
            "prior_quality_insight": _quality_insight(),
        },
    )

    assert request.task_context["website_type"] == "saas"
    assert "prior_evaluation_insight" in request.task_context
    assert "prior_quality_insight" not in request.task_context


def test_a5_7_implementation_provider_receives_only_allowlisted_advisory_fields() -> None:
    request = _request(
        "implementation",
        {
            "website_type": "saas",
            "prior_evaluation_insight": _evaluation_insight(),
            "prior_quality_insight": _quality_insight(),
        },
    )

    evaluation = request.task_context["prior_evaluation_insight"]
    quality = request.task_context["prior_quality_insight"]

    assert set(evaluation) == {
        "schema_version",
        "advisory_only",
        "flow_id",
        "sample_size",
        "passed_runs",
        "failed_or_blocked_runs",
        "pass_rate",
        "average_replans",
        "recurrent_failure_channels",
        "observed_evidence_types",
        "matched_signature",
        "authority_effect",
        "gate_effect",
        "rule",
    }
    assert set(evaluation["recurrent_failure_channels"][0]) == {"channel", "count"}

    assert set(quality["recurrent_attention_patterns"][0]) == {
        "evaluator",
        "requirement_id",
        "outcome",
        "applicable",
        "occurrences",
    }
    assert set(quality["recurrent_pass_patterns"][0]) == {
        "evaluator",
        "requirement_id",
        "outcome",
        "applicable",
        "occurrences",
    }

    prompt = render_provider_prompt(request)
    for forbidden in (
        "RAW EVALUATION PROMPT",
        "RAW PROVIDER SUMMARY",
        "MUST NOT LEAK",
        "RAW QUALITY RATIONALE",
        "test_targets",
        "private.png",
        "PRIVATE DOM",
        "source_code",
        "console.log('private')",
    ):
        assert forbidden not in prompt


def test_a5_7_invalid_authority_effect_drops_poisoned_memory_payload() -> None:
    evaluation = _evaluation_insight()
    evaluation["authority_effect"] = "raise_to_production"
    quality = _quality_insight()
    quality["release_effect"] = "auto_release"

    request = _request(
        "qa",
        {
            "intent": "improve",
            "prior_evaluation_insight": evaluation,
            "prior_quality_insight": quality,
        },
    )

    assert request.task_context == {"intent": "improve"}


def test_a5_7_malformed_memory_is_removed_without_touching_current_task_context() -> None:
    request = _request(
        "implementation",
        {
            "intent": "fix",
            "features": ["motion"],
            "prior_evaluation_insight": "not-a-dict",
            "prior_quality_insight": ["not-a-dict"],
        },
    )

    assert request.task_context == {"intent": "fix", "features": ["motion"]}


def test_a5_7_provider_request_detaches_top_level_task_context() -> None:
    original = {
        "intent": "fix",
        "prior_quality_insight": _quality_insight(),
    }
    request = _request("implementation", original)
    original["intent"] = "poison-after-request"
    original["prior_quality_insight"]["authority_effect"] = "poison-after-request"

    assert request.task_context["intent"] == "fix"
    assert request.task_context["prior_quality_insight"]["authority_effect"] == "none"

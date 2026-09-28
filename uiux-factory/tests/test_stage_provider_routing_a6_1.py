import pytest

from core.runtime.flow_os.provider_routing import StageProviderRouter


def test_a6_1_disabled_policy_preserves_caller_provider_and_budget() -> None:
    router = StageProviderRouter({"provider_routing": {"enabled": False}})

    selection = router.resolve(
        stage_id="research_truth",
        agent="research",
        default_provider="auto",
        default_model=None,
        requested_max_turns=12,
    )

    assert selection.provider == "auto"
    assert selection.model is None
    assert selection.max_turns == 12
    assert selection.source == "caller_default"


def test_a6_1_agent_route_can_select_explicit_provider_model_and_lower_budget() -> None:
    router = StageProviderRouter(
        {
            "provider_routing": {
                "enabled": True,
                "allow_provider_switch": True,
                "by_agent": {
                    "research": {
                        "provider": "anthropic",
                        "model": "claude-test-research",
                        "max_turns": 5,
                    }
                },
            }
        }
    )

    selection = router.resolve(
        stage_id="research_truth",
        agent="research",
        default_provider="openai",
        default_model="gpt-test-default",
        requested_max_turns=12,
    )

    assert selection.provider == "anthropic"
    assert selection.model == "claude-test-research"
    assert selection.max_turns == 5
    assert selection.source == "by_agent:research"


def test_a6_1_stage_route_wins_over_agent_route() -> None:
    router = StageProviderRouter(
        {
            "provider_routing": {
                "enabled": True,
                "allow_provider_switch": True,
                "by_agent": {
                    "implementation": {
                        "provider": "anthropic",
                        "model": "agent-model",
                        "max_turns": 8,
                    }
                },
                "by_stage": {
                    "implementation": {
                        "provider": "openai",
                        "model": "stage-model",
                        "max_turns": 4,
                    }
                },
            }
        }
    )

    selection = router.resolve(
        stage_id="implementation",
        agent="implementation",
        default_provider="openai",
        default_model="default-model",
        requested_max_turns=10,
    )

    assert selection.provider == "openai"
    assert selection.model == "stage-model"
    assert selection.max_turns == 4
    assert selection.source == "by_stage:implementation"


def test_a6_1_routed_turn_budget_cannot_raise_caller_ceiling() -> None:
    router = StageProviderRouter(
        {
            "provider_routing": {
                "enabled": True,
                "default": {"provider": "openai", "max_turns": 32},
            }
        }
    )

    selection = router.resolve(
        stage_id="qa",
        agent="qa",
        default_provider="openai",
        default_model=None,
        requested_max_turns=7,
    )

    assert selection.max_turns == 7


def test_a6_1_provider_switch_is_fail_closed_without_explicit_permission() -> None:
    router = StageProviderRouter(
        {
            "provider_routing": {
                "enabled": True,
                "allow_provider_switch": False,
                "by_agent": {"qa": {"provider": "anthropic"}},
            }
        }
    )

    with pytest.raises(ValueError, match="allow_provider_switch is false"):
        router.resolve(
            stage_id="qa",
            agent="qa",
            default_provider="openai",
            default_model=None,
            requested_max_turns=12,
        )


def test_a6_1_routed_auto_provider_is_forbidden() -> None:
    router = StageProviderRouter(
        {
            "provider_routing": {
                "enabled": True,
                "default": {"provider": "auto"},
            }
        }
    )

    with pytest.raises(ValueError, match="may not use provider=auto"):
        router.resolve(
            stage_id="research_truth",
            agent="research",
            default_provider="openai",
            default_model=None,
            requested_max_turns=12,
        )


@pytest.mark.parametrize("value", [0, -1, 65, "bad"])
def test_a6_1_invalid_route_turn_budget_is_rejected(value) -> None:
    router = StageProviderRouter(
        {
            "provider_routing": {
                "enabled": True,
                "default": {"provider": "openai", "max_turns": value},
            }
        }
    )

    with pytest.raises(ValueError, match="max_turns"):
        router.resolve(
            stage_id="implementation",
            agent="implementation",
            default_provider="openai",
            default_model=None,
            requested_max_turns=12,
        )

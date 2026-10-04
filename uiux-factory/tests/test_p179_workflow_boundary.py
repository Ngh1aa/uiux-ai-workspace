from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_WORKFLOW = ROOT / ".github" / "workflows" / "p179-railway-provider-attestation.yml"
LIVE_WORKFLOW = ROOT / ".github" / "workflows" / "p177-multi-provider-attestation.yml"
CLI = ROOT / "skills_UIUX" / "scripts" / "run-p177-multi-provider-attestation-truth.py"
RUNTIME = ROOT / "uiux-factory" / "core" / "runtime" / "flow_os" / "provider_attestation.py"


def test_p179_contract_workflow_is_read_only() -> None:
    text = CONTRACT_WORKFLOW.read_text(encoding="utf-8")

    assert "permissions:\n  contents: read" in text
    assert "persist-credentials: false" in text
    assert "workflow_dispatch:" not in text


def test_p179_live_credentials_remain_manual_opt_in_through_p177_lane() -> None:
    workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    cli = CLI.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    for name in ("P179_RAILWAY_TOKEN", "P179_RAILWAY_WORKSPACE_ID"):
        assert name in workflow
        assert name in cli


def test_p179_surfaces_expose_no_railway_mutation_commands() -> None:
    text = "\n".join(
        [
            LIVE_WORKFLOW.read_text(encoding="utf-8"),
            CLI.read_text(encoding="utf-8"),
            RUNTIME.read_text(encoding="utf-8"),
        ]
    ).lower()

    forbidden = [
        "railway up",
        "railway deploy",
        "serviceconnect(",
        "servicedisconnect(",
        "serviceinstancedeploy",
        "projectcreate(",
        "projectdelete(",
    ]
    assert not any(token in text for token in forbidden)

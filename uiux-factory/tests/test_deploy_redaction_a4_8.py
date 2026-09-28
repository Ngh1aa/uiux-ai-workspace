from __future__ import annotations

from core.runtime.flow_os.release import CommandDeployAdapter, DeploymentResult


def test_a4_8_known_deploy_secret_values_are_redacted_from_output() -> None:
    environment = {"VERCEL_TOKEN": "super-secret-token"}
    text = "deploy started token=super-secret-token deploy complete"
    assert CommandDeployAdapter._redact_known_secrets(
        text,
        environment,
        ["VERCEL_TOKEN"],
    ) == "deploy started token=[REDACTED] deploy complete"


def test_a4_8_deployment_checkpoint_metadata_excludes_command_output() -> None:
    result = DeploymentResult(
        adapter="command",
        returncode=0,
        stdout="potentially sensitive stdout",
        stderr="potentially sensitive stderr",
        deployed=True,
    )
    checkpoint = result.checkpoint_dict()
    assert checkpoint == {"adapter": "command", "returncode": 0, "deployed": True}
    assert "stdout" not in checkpoint
    assert "stderr" not in checkpoint

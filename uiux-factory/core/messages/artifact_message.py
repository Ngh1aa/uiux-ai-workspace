from __future__ import annotations

from typing import Any

from metagpt.schema import Message

from core.skills.execution_context import SkillExecutionContext


def make_stage_message(
    *,
    content: str,
    role_name: str,
    stage: str,
    run_id: str,
    skill_context: SkillExecutionContext,
    extra_metadata: dict[str, Any] | None = None,
) -> Message:
    metadata = {
        "uiux_factory": True,
        "run_id": run_id,
        "stage": stage,
        **skill_context.metadata(),
    }

    if extra_metadata:
        metadata.update(extra_metadata)

    return Message(
        content=content,
        role="user",
        send_to={role_name},
        metadata=metadata,
    )

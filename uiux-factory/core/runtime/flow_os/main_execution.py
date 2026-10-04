from __future__ import annotations

import hashlib
from pathlib import Path

from core.runtime.flow_os.work_execution import ArtifactRef, WorkExecutionPlan


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def advance_execution_phase(
    plan: WorkExecutionPlan,
    phase: str,
    output_sources: dict[str, tuple[str, Path]],
    *,
    source: str = "factory-main-entrypoint",
) -> list[str]:
    """Advance consecutive runnable nodes for one lifecycle phase using real artifacts.

    This is a deterministic adapter over WorkExecutionPlan. It owns no routing,
    provider loop, authority, gate policy, or release behavior.
    """

    completed: list[str] = []
    while True:
        runnable = plan.runnable_segment_ids()
        if not runnable:
            break
        node = plan._node(runnable[0])
        if node.phase != phase:
            break

        artifacts: list[ArtifactRef] = []
        for kind in node.expected_output_kinds:
            resolved = output_sources.get(kind)
            if resolved is None:
                raise RuntimeError(
                    f"No main-entrypoint artifact mapping for execution output kind: {kind}"
                )
            source_key, raw_path = resolved
            path = Path(raw_path).resolve()
            if not path.is_file():
                raise RuntimeError(f"Execution source artifact missing: {path}")
            artifacts.append(
                ArtifactRef(
                    id=f"{node.segment_id}-{kind}-main-entrypoint",
                    kind=kind,
                    producer_segment_id=node.segment_id,
                    uri=path.as_uri(),
                    digest=_sha256(path),
                    metadata={
                        "source": source,
                        "source_artifact_key": source_key,
                        "phase": phase,
                        "scope": ",".join(node.scope),
                    },
                )
            )

        plan.start(node.segment_id)
        plan.pass_segment(node.segment_id, artifacts)
        completed.append(node.segment_id)

    return completed


def fail_execution_phase(
    plan: WorkExecutionPlan,
    phase: str,
    reason: str,
) -> str | None:
    """Fail the first runnable node only when it belongs to the active lifecycle phase."""

    runnable = plan.runnable_segment_ids()
    if not runnable:
        return None
    node = plan._node(runnable[0])
    if node.phase != phase:
        return None
    plan.start(node.segment_id)
    plan.fail_segment(node.segment_id, str(reason).strip() or "main_entrypoint_failed")
    return node.segment_id

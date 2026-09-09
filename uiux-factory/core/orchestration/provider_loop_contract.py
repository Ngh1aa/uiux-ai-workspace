from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


PROVIDER_STATUSES = {"CONTINUE", "PASS", "FAIL", "BLOCKED"}
READ_ONLY_TOOLS = {"read_artifact", "read_skill_source", "list_artifacts"}
REPLAN_SIGNALS = {
    "GATE_FAIL",
    "BLOCKED",
    "NEW_RISK",
    "INVALID_ASSUMPTION",
    "TOOL_FAILURE",
    "CONTEXT_DRIFT",
}


@dataclass(frozen=True)
class ProviderObservationRequest:
    tool: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderLoopResponse:
    status: str
    requests: tuple[ProviderObservationRequest, ...] = field(default_factory=tuple)
    summary: str = ""
    evidence: tuple[str, ...] = field(default_factory=tuple)
    artifact: str | None = None
    replan_signal: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProviderLoopResponse":
        status = str(payload.get("status", "")).upper()
        if status not in PROVIDER_STATUSES:
            raise ValueError(f"invalid provider loop status: {status or '(missing)'}")

        raw_requests = payload.get("requests", [])
        if not isinstance(raw_requests, list) or len(raw_requests) > 6:
            raise ValueError("provider requests must be an array with at most 6 items")

        requests: list[ProviderObservationRequest] = []
        for index, item in enumerate(raw_requests):
            if not isinstance(item, dict):
                raise ValueError(f"provider request {index} must be an object")
            tool = str(item.get("tool", ""))
            args = item.get("args", {})
            if tool not in READ_ONLY_TOOLS:
                raise ValueError(f"provider request {index} uses unsupported read-only tool: {tool}")
            if not isinstance(args, dict):
                raise ValueError(f"provider request {index}.args must be an object")
            requests.append(ProviderObservationRequest(tool=tool, args=dict(args)))

        evidence = payload.get("evidence", [])
        if not isinstance(evidence, list) or any(not isinstance(item, str) for item in evidence):
            raise ValueError("provider evidence must be an array of strings")

        artifact = payload.get("artifact")
        if artifact is not None and not isinstance(artifact, str):
            raise ValueError("provider artifact must be a string or null")

        signal = payload.get("replan_signal")
        if signal is not None:
            signal = str(signal)
            if signal not in REPLAN_SIGNALS:
                raise ValueError(f"unknown provider replan signal: {signal}")

        if status == "CONTINUE" and not requests:
            raise ValueError("CONTINUE requires at least one read-only observation request")
        if status == "PASS":
            if not evidence:
                raise ValueError("PASS requires concrete evidence")
            if not artifact or not artifact.strip():
                raise ValueError("PASS requires the complete refined artifact")
        if status in {"FAIL", "BLOCKED"} and signal is None:
            signal = "GATE_FAIL" if status == "FAIL" else "BLOCKED"

        return cls(
            status=status,
            requests=tuple(requests),
            summary=str(payload.get("summary", "")),
            evidence=tuple(evidence),
            artifact=artifact,
            replan_signal=signal,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["requests"] = [asdict(item) for item in self.requests]
        payload["evidence"] = list(self.evidence)
        return payload


def response_contract_text() -> str:
    return (
        "Return ONLY JSON with keys status, requests, summary, evidence, artifact, replan_signal. "
        "status is CONTINUE|PASS|FAIL|BLOCKED. requests may use only read_artifact, "
        "read_skill_source, list_artifacts. Use CONTINUE when more evidence is needed. "
        "PASS requires concrete evidence and the complete refined artifact. "
        "FAIL/BLOCKED must identify a replan signal when appropriate."
    )

from __future__ import annotations

import json
import os
import shlex
import subprocess
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

from runtime.flow import REPLAN_SIGNALS

PROVIDER_STATUSES = {"CONTINUE", "PASS", "FAIL", "BLOCKED"}
DEFAULT_OPENAI_MODEL = "gpt-5.6-sol"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"


@dataclass(frozen=True)
class ProviderStageRequest:
    goal: str
    project_root: str
    flow_id: str
    flow_revision: int
    stage_id: str
    agent: str
    purpose: str
    gates: list[dict[str, Any]]
    task_context: dict[str, Any]
    authority: str
    tools: list[dict[str, Any]]
    skill_context: list[dict[str, str]]
    source_context: list[dict[str, str]]
    observations: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderStageResponse:
    status: str
    actions: list[dict[str, Any]]
    summary: str = ""
    evidence: list[str] = field(default_factory=list)
    replan_signal: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProviderStageResponse":
        status = str(payload.get("status", "")).upper()
        if status not in PROVIDER_STATUSES:
            raise ValueError(f"invalid provider status: {status or '(missing)'}")
        raw_actions = payload.get("actions", [])
        if not isinstance(raw_actions, list) or len(raw_actions) > 24:
            raise ValueError("provider actions must be an array with at most 24 items")
        actions: list[dict[str, Any]] = []
        for index, item in enumerate(raw_actions):
            if not isinstance(item, dict):
                raise ValueError(f"provider action {index} must be an object")
            if "handoff" in item:
                raise ValueError("provider responses cannot hand off agents; Flow owns stage routing")
            tool = item.get("tool")
            args = item.get("args", {})
            if not isinstance(tool, str) or not tool:
                raise ValueError(f"provider action {index} requires a tool name")
            if not isinstance(args, dict):
                raise ValueError(f"provider action {index}.args must be an object")
            actions.append({"tool": tool, "args": dict(args)})

        evidence = payload.get("evidence", [])
        if not isinstance(evidence, list) or any(not isinstance(item, str) for item in evidence):
            raise ValueError("provider evidence must be an array of strings")
        signal = payload.get("replan_signal")
        if signal is not None and str(signal) not in REPLAN_SIGNALS:
            raise ValueError(f"unknown provider replan signal: {signal}")
        if status == "PASS" and not evidence:
            raise ValueError("provider PASS requires concrete gate evidence")
        if status in {"FAIL", "BLOCKED"} and not signal:
            signal = "GATE_FAIL" if status == "FAIL" else "BLOCKED"
        return cls(
            status=status,
            actions=actions,
            summary=str(payload.get("summary", "")),
            evidence=list(evidence),
            replan_signal=str(signal) if signal is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ModelProvider(Protocol):
    name: str
    model: str

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        ...


def provider_response_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["status", "actions", "summary", "evidence", "replan_signal"],
        "properties": {
            "status": {"type": "string", "enum": ["CONTINUE", "PASS", "FAIL", "BLOCKED"]},
            "actions": {
                "type": "array",
                "maxItems": 24,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["tool", "args"],
                    "properties": {
                        "tool": {"type": "string"},
                        "args": {"type": "object", "additionalProperties": True},
                    },
                },
            },
            "summary": {"type": "string"},
            "evidence": {"type": "array", "items": {"type": "string"}},
            "replan_signal": {
                "anyOf": [
                    {"type": "null"},
                    {"type": "string", "enum": sorted(REPLAN_SIGNALS)},
                ]
            },
        },
    }


def _system_prompt() -> str:
    return (
        "You are a specialist execution agent inside skills_UIUX Flow Agent OS. "
        "The Development Manager and declarative Flow own orchestration, stage order, skill routing, approvals and replanning. "
        "You must never invent a handoff or bypass gates. Use only the provided tools. "
        "Work iteratively: inspect project evidence with tools, make the smallest justified changes, verify them, then return PASS only with concrete evidence. "
        "A model claim is not evidence. If evidence is insufficient, use CONTINUE with tool actions. "
        "If the active gate materially fails, return FAIL with an appropriate replan_signal instead of retrying blindly. "
        "If blocked by missing truth or authority, return BLOCKED. Never expose secrets or request hidden credentials."
    )


def render_provider_prompt(request: ProviderStageRequest) -> str:
    payload = request.to_dict()
    return (
        "Execute the active Flow Agent OS stage. Return only data matching the required response schema.\n\n"
        "ACTIVE STAGE REQUEST:\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\nRULES:\n"
        "- Flow owns agent/stage routing; do not output handoffs.\n"
        "- Use CONTINUE when more tool observations are needed.\n"
        "- PASS requires evidence that addresses the declared gates.\n"
        "- Prefer project truth and routed skills over generic model assumptions.\n"
        "- Do not write outside the project or bypass tool permissions.\n"
    )


def _http_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[-4000:]
        raise RuntimeError(f"provider HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"provider network error: {exc.reason}") from exc
    decoded = json.loads(data)
    if not isinstance(decoded, dict):
        raise RuntimeError("provider response must be a JSON object")
    return decoded


class OpenAIResponsesProvider:
    name = "openai"

    def __init__(self, model: str | None = None, api_key: str | None = None, timeout: int = 180) -> None:
        self.model = model or os.environ.get("UIUX_OPENAI_MODEL") or DEFAULT_OPENAI_MODEL
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for provider=openai")

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        schema = provider_response_schema()
        payload = {
            "model": self.model,
            "store": False,
            "instructions": _system_prompt(),
            "input": render_provider_prompt(request),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "uiux_stage_response",
                    "strict": False,
                    "schema": schema,
                }
            },
        }
        data = _http_json(
            "https://api.openai.com/v1/responses",
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            payload,
            self.timeout,
        )
        texts: list[str] = []
        for item in data.get("output", []):
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if isinstance(content, dict) and content.get("type") == "output_text":
                    texts.append(str(content.get("text", "")))
        if not texts:
            raise RuntimeError("OpenAI response contained no output_text")
        decoded = json.loads("".join(texts))
        if not isinstance(decoded, dict):
            raise RuntimeError("OpenAI structured output was not an object")
        return ProviderStageResponse.from_dict(decoded)


class AnthropicMessagesProvider:
    name = "anthropic"

    def __init__(self, model: str | None = None, api_key: str | None = None, timeout: int = 180) -> None:
        self.model = model or os.environ.get("UIUX_ANTHROPIC_MODEL") or DEFAULT_ANTHROPIC_MODEL
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for provider=anthropic")

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        schema = provider_response_schema()
        payload = {
            "model": self.model,
            "max_tokens": int(os.environ.get("UIUX_ANTHROPIC_MAX_TOKENS", "8192")),
            "system": _system_prompt(),
            "messages": [{"role": "user", "content": render_provider_prompt(request)}],
            "tools": [
                {
                    "name": "submit_stage_response",
                    "description": "Submit the next bounded stage action batch or final gate outcome.",
                    "input_schema": schema,
                }
            ],
            "tool_choice": {"type": "tool", "name": "submit_stage_response"},
        }
        data = _http_json(
            "https://api.anthropic.com/v1/messages",
            {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            payload,
            self.timeout,
        )
        for item in data.get("content", []):
            if isinstance(item, dict) and item.get("type") == "tool_use" and item.get("name") == "submit_stage_response":
                value = item.get("input")
                if not isinstance(value, dict):
                    raise RuntimeError("Anthropic tool response input was not an object")
                return ProviderStageResponse.from_dict(value)
        raise RuntimeError("Anthropic response did not call submit_stage_response")


class CommandProvider:
    name = "command"

    def __init__(self, command: str, model: str | None = None, timeout: int = 300) -> None:
        if not command.strip():
            raise ValueError("provider=command requires --provider-command or UIUX_PROVIDER_COMMAND")
        self.command = command
        self.model = model or "external-command"
        self.timeout = timeout

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        envelope = {
            "system": _system_prompt(),
            "request": request.to_dict(),
            "response_schema": provider_response_schema(),
        }
        result = subprocess.run(
            shlex.split(self.command),
            input=json.dumps(envelope, ensure_ascii=False),
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(f"provider command failed ({result.returncode}): {result.stderr[-4000:]}")
        decoded = json.loads(result.stdout)
        if not isinstance(decoded, dict):
            raise RuntimeError("provider command stdout must be a JSON object")
        return ProviderStageResponse.from_dict(decoded)


class ScriptedProvider:
    """Deterministic provider used by runtime smoke tests; never selected from CLI automatically."""

    name = "scripted"
    model = "scripted-test"

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = list(responses)
        self.requests: list[ProviderStageRequest] = []

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        self.requests.append(request)
        if not self.responses:
            raise RuntimeError("scripted provider has no remaining responses")
        return ProviderStageResponse.from_dict(self.responses.pop(0))


def create_provider(
    name: str,
    model: str | None = None,
    command: str | None = None,
) -> ModelProvider:
    normalized = name.strip().lower()
    if normalized == "auto":
        configured = os.environ.get("UIUX_PROVIDER", "").strip().lower()
        if configured:
            normalized = configured
        elif os.environ.get("OPENAI_API_KEY"):
            normalized = "openai"
        elif os.environ.get("ANTHROPIC_API_KEY"):
            normalized = "anthropic"
        elif os.environ.get("UIUX_PROVIDER_COMMAND"):
            normalized = "command"
        else:
            raise ValueError(
                "provider=auto found no provider configuration; set OPENAI_API_KEY, "
                "ANTHROPIC_API_KEY, UIUX_PROVIDER_COMMAND, or UIUX_PROVIDER"
            )
    if normalized == "openai":
        return OpenAIResponsesProvider(model=model)
    if normalized == "anthropic":
        return AnthropicMessagesProvider(model=model)
    if normalized == "command":
        return CommandProvider(command or os.environ.get("UIUX_PROVIDER_COMMAND", ""), model=model)
    raise ValueError(f"unknown provider: {name}")


def load_context_documents(
    items: list[dict[str, Any]],
    kinds: set[str],
    max_chars: int | None = None,
) -> list[dict[str, str]]:
    budget = max_chars or int(os.environ.get("UIUX_PROVIDER_CONTEXT_CHARS", "180000"))
    result: list[dict[str, str]] = []
    used = 0
    for item in items:
        if str(item.get("kind", "")) not in kinds:
            continue
        path = Path(str(item.get("path", "")))
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if used + len(text) > budget:
            raise ValueError(
                f"provider context budget exceeded ({budget} chars) while loading {path}; "
                "route fewer skills/sources or raise UIUX_PROVIDER_CONTEXT_CHARS deliberately"
            )
        result.append({"path": str(path), "content": text})
        used += len(text)
    return result

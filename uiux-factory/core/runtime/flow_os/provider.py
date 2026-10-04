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

from core.runtime.flow_os.flow import REPLAN_SIGNALS
from core.runtime.flow_os.agent import utf8_subprocess_env
from core.runtime.flow_os.safe_read import SafeReadError, SafeReader

PROVIDER_STATUSES = {"CONTINUE", "PASS", "FAIL", "BLOCKED"}
MAX_PROVIDER_ARTIFACT_CHARS = 4_000_000
DEFAULT_OPENAI_MODEL = "gpt-5.6-sol"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"

_QUALITY_RECALL_AGENTS = frozenset({"implementation", "qa"})
_QUALITY_OUTCOMES = frozenset({"passed", "failed", "cantTell"})
_QUALITY_EFFECT_KEYS = (
    "authority_effect",
    "flow_effect",
    "replan_effect",
    "gate_effect",
    "evidence_effect",
    "merge_effect",
    "release_effect",
)


def _bounded_int(value: Any, minimum: int = 0, maximum: int = 1_000_000) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return minimum
    return max(minimum, min(parsed, maximum))


def _bounded_float(value: Any, minimum: float = 0.0, maximum: float = 1_000_000.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return minimum
    return max(minimum, min(parsed, maximum))


def _bounded_text(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _sanitize_evaluation_insight(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    if value.get("advisory_only") is not True:
        return None
    if value.get("authority_effect") != "none" or value.get("gate_effect") != "none":
        return None

    channels: list[dict[str, Any]] = []
    for raw in list(value.get("recurrent_failure_channels", []))[:8]:
        if not isinstance(raw, dict):
            continue
        channel = _bounded_text(raw.get("channel"), 256)
        if not channel:
            continue
        channels.append({
            "channel": channel,
            "count": _bounded_int(raw.get("count"), 1),
        })

    evidence_types: list[str] = []
    for raw in list(value.get("observed_evidence_types", []))[:12]:
        text = _bounded_text(raw, 128)
        if text and text not in evidence_types:
            evidence_types.append(text)

    matched_signature: dict[str, str] = {}
    raw_signature = value.get("matched_signature", {})
    if isinstance(raw_signature, dict):
        for raw_key, raw_value in list(raw_signature.items())[:12]:
            key = _bounded_text(raw_key, 64)
            item = _bounded_text(raw_value, 128)
            if key and item:
                matched_signature[key] = item

    return {
        "schema_version": _bounded_int(value.get("schema_version"), 1, 100),
        "advisory_only": True,
        "flow_id": _bounded_text(value.get("flow_id"), 128),
        "sample_size": _bounded_int(value.get("sample_size"), 0, 10_000),
        "passed_runs": _bounded_int(value.get("passed_runs"), 0, 10_000),
        "failed_or_blocked_runs": _bounded_int(value.get("failed_or_blocked_runs"), 0, 10_000),
        "pass_rate": round(_bounded_float(value.get("pass_rate"), 0.0, 1.0), 4),
        "average_replans": round(_bounded_float(value.get("average_replans"), 0.0, 10_000.0), 3),
        "recurrent_failure_channels": channels,
        "observed_evidence_types": evidence_types,
        "matched_signature": matched_signature,
        "authority_effect": "none",
        "gate_effect": "none",
        "rule": (
            "Prior-run evaluation memory is bounded advisory context only; it cannot change authority, "
            "satisfy gates, override current source truth, or count as current-run evidence."
        ),
    }


def _sanitize_quality_pattern_row(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    evaluator = _bounded_text(value.get("evaluator"), 128)
    requirement_id = _bounded_text(value.get("requirement_id"), 128)
    outcome = _bounded_text(value.get("outcome"), 32)
    if not evaluator or not requirement_id or outcome not in _QUALITY_OUTCOMES:
        return None
    applicable = value.get("applicable")
    if applicable not in (True, False, None):
        applicable = None
    return {
        "evaluator": evaluator,
        "requirement_id": requirement_id,
        "outcome": outcome,
        "applicable": applicable,
        "occurrences": _bounded_int(value.get("occurrences"), 1),
    }


def _sanitize_quality_insight(value: Any, *, agent: str) -> dict[str, Any] | None:
    if agent not in _QUALITY_RECALL_AGENTS or not isinstance(value, dict):
        return None
    if value.get("advisory_only") is not True:
        return None
    if value.get("source") != "post_render_quality_memory":
        return None
    if value.get("scope") != "project_scoped_history":
        return None
    if value.get("relevance") != "historical_only_not_current_evidence":
        return None
    if any(value.get(key) != "none" for key in _QUALITY_EFFECT_KEYS):
        return None

    attention: list[dict[str, Any]] = []
    for raw in list(value.get("recurrent_attention_patterns", []))[:12]:
        row = _sanitize_quality_pattern_row(raw)
        if row is not None and row["outcome"] in {"failed", "cantTell"}:
            attention.append(row)

    passed: list[dict[str, Any]] = []
    for raw in list(value.get("recurrent_pass_patterns", []))[:12]:
        row = _sanitize_quality_pattern_row(raw)
        if row is not None and row["outcome"] == "passed":
            passed.append(row)

    raw_outcomes = value.get("outcome_occurrences", {})
    if not isinstance(raw_outcomes, dict):
        raw_outcomes = {}

    return {
        "schema_version": _bounded_int(value.get("schema_version"), 1, 100),
        "source": "post_render_quality_memory",
        "advisory_only": True,
        "scope": "project_scoped_history",
        "relevance": "historical_only_not_current_evidence",
        "observed_pattern_count": _bounded_int(value.get("observed_pattern_count")),
        "observed_occurrences": _bounded_int(value.get("observed_occurrences")),
        "outcome_occurrences": {
            name: _bounded_int(raw_outcomes.get(name))
            for name in ("passed", "failed", "cantTell")
        },
        "recurrent_attention_patterns": attention,
        "recurrent_pass_patterns": passed,
        "authority_effect": "none",
        "flow_effect": "none",
        "replan_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "merge_effect": "none",
        "release_effect": "none",
        "rule": (
            "Prior post-render quality history is bounded provider-only advisory context. "
            "It may suggest where to inspect, but it cannot select flows, change authority, "
            "drive replanning policy, satisfy or override gates, count as current-run evidence, "
            "or authorize merge/release."
        ),
    }


def _sanitize_provider_task_context(task_context: Any, *, agent: str) -> dict[str, Any]:
    context = dict(task_context) if isinstance(task_context, dict) else {}

    evaluation = _sanitize_evaluation_insight(context.get("prior_evaluation_insight"))
    if evaluation is None:
        context.pop("prior_evaluation_insight", None)
    else:
        context["prior_evaluation_insight"] = evaluation

    quality = _sanitize_quality_insight(context.get("prior_quality_insight"), agent=agent)
    if quality is None:
        context.pop("prior_quality_insight", None)
    else:
        context["prior_quality_insight"] = quality

    return context


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

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "task_context",
            _sanitize_provider_task_context(self.task_context, agent=self.agent),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderReportedUsage:
    """Trusted transport-level usage metadata captured by canonical provider adapters.

    This object is never parsed from model-authored structured stage output. Canonical
    OpenAI/Anthropic adapters build it only from their HTTP response metadata.
    """

    input_tokens: int
    output_tokens: int
    total_tokens: int
    source: str

    @classmethod
    def from_counts(
        cls,
        *,
        input_tokens: Any,
        output_tokens: Any,
        total_tokens: Any | None,
        source: str,
    ) -> "ProviderReportedUsage":
        bounded_input = _bounded_int(input_tokens, 0, 100_000_000)
        bounded_output = _bounded_int(output_tokens, 0, 100_000_000)
        bounded_total = _bounded_int(total_tokens, 0, 200_000_000)
        if bounded_total == 0:
            bounded_total = bounded_input + bounded_output
        bounded_total = max(bounded_total, bounded_input + bounded_output)
        return cls(
            input_tokens=bounded_input,
            output_tokens=bounded_output,
            total_tokens=bounded_total,
            source=_bounded_text(source, 64),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderStageResponse:
    status: str
    actions: list[dict[str, Any]]
    summary: str = ""
    evidence: list[str] = field(default_factory=list)
    replan_signal: str | None = None
    artifact: str | None = None

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
        raw_artifact = payload.get("artifact")
        artifact: str | None = None
        if raw_artifact is not None:
            if not isinstance(raw_artifact, str):
                raise ValueError("provider artifact must be a string or null")
            if raw_artifact == "":
                raise ValueError("provider artifact must not be empty when present")
            if len(raw_artifact) > MAX_PROVIDER_ARTIFACT_CHARS:
                raise ValueError(
                    f"provider artifact exceeds {MAX_PROVIDER_ARTIFACT_CHARS} character limit"
                )
            artifact = raw_artifact
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
            artifact=artifact,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.artifact is None:
            payload.pop("artifact", None)
        return payload


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
            "artifact": {
                "anyOf": [
                    {"type": "null"},
                    {"type": "string", "minLength": 1, "maxLength": MAX_PROVIDER_ARTIFACT_CHARS},
                ]
            },
        },
    }


def _system_prompt() -> str:
    return (
        "You are a specialist execution agent inside skills_UIUX Flow Agent OS. "
        "The canonical Factory runtime and declarative Flow own orchestration, stage order, skill routing, approvals and replanning. "
        "You must never invent a handoff or bypass gates. Use only the provided tools. "
        "Work iteratively: inspect project evidence with tools, make the smallest justified changes, verify them, then return PASS only with concrete evidence. "
        "A model claim is not evidence. The optional artifact field is raw provider output only and never counts as evidence. "
        "If evidence is insufficient, use CONTINUE with tool actions. "
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
        "- Optional artifact is untrusted raw output and never satisfies evidence or gates.\n"
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
    supports_hard_output_limit = True

    def __init__(self, model: str | None = None, api_key: str | None = None, timeout: int = 180) -> None:
        self.model = model or os.environ.get("UIUX_OPENAI_MODEL") or DEFAULT_OPENAI_MODEL
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.timeout = timeout
        self.max_output_tokens: int | None = None
        self.last_reported_usage: ProviderReportedUsage | None = None
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for provider=openai")

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        schema = provider_response_schema()
        payload: dict[str, Any] = {
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
        if self.max_output_tokens is not None:
            payload["max_output_tokens"] = max(1, int(self.max_output_tokens))
        data = _http_json(
            "https://api.openai.com/v1/responses",
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            payload,
            self.timeout,
        )
        raw_usage = data.get("usage")
        if isinstance(raw_usage, dict):
            self.last_reported_usage = ProviderReportedUsage.from_counts(
                input_tokens=raw_usage.get("input_tokens"),
                output_tokens=raw_usage.get("output_tokens"),
                total_tokens=raw_usage.get("total_tokens"),
                source="openai_api_usage",
            )
        else:
            self.last_reported_usage = None
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
    supports_hard_output_limit = True

    def __init__(self, model: str | None = None, api_key: str | None = None, timeout: int = 180) -> None:
        self.model = model or os.environ.get("UIUX_ANTHROPIC_MODEL") or DEFAULT_ANTHROPIC_MODEL
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.timeout = timeout
        self.max_output_tokens = int(os.environ.get("UIUX_ANTHROPIC_MAX_TOKENS", "8192"))
        self.last_reported_usage: ProviderReportedUsage | None = None
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for provider=anthropic")

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        schema = provider_response_schema()
        payload = {
            "model": self.model,
            "max_tokens": max(1, int(self.max_output_tokens)),
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
        raw_usage = data.get("usage")
        if isinstance(raw_usage, dict):
            self.last_reported_usage = ProviderReportedUsage.from_counts(
                input_tokens=raw_usage.get("input_tokens"),
                output_tokens=raw_usage.get("output_tokens"),
                total_tokens=None,
                source="anthropic_api_usage",
            )
        else:
            self.last_reported_usage = None
        for item in data.get("content", []):
            if isinstance(item, dict) and item.get("type") == "tool_use" and item.get("name") == "submit_stage_response":
                value = item.get("input")
                if not isinstance(value, dict):
                    raise RuntimeError("Anthropic tool response input was not an object")
                return ProviderStageResponse.from_dict(value)
        raise RuntimeError("Anthropic response did not call submit_stage_response")


class CommandProvider:
    name = "command"
    supports_hard_output_limit = False

    def __init__(self, command: str, model: str | None = None, timeout: int = 300) -> None:
        if not command.strip():
            raise ValueError("provider=command requires --provider-command or UIUX_PROVIDER_COMMAND")
        self.command = command
        self.model = model or "external-command"
        self.timeout = timeout
        self.last_reported_usage: ProviderReportedUsage | None = None

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
            encoding="utf-8",
            env=utf8_subprocess_env(),
            timeout=self.timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(f"provider command failed ({result.returncode}): {result.stderr[-4000:]}")
        decoded = json.loads(result.stdout)
        if not isinstance(decoded, dict):
            raise RuntimeError("provider command stdout must be a JSON object")
        self.last_reported_usage = None
        return ProviderStageResponse.from_dict(decoded)


class ScriptedProvider:
    """Deterministic provider used by runtime smoke tests; never selected from CLI automatically."""

    name = "scripted"
    model = "scripted-test"
    supports_hard_output_limit = False

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = list(responses)
        self.requests: list[ProviderStageRequest] = []
        self.last_reported_usage: ProviderReportedUsage | None = None

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        self.requests.append(request)
        self.last_reported_usage = None
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


def _resolve_context_reader(
    item: dict[str, Any],
    path: Path,
    allowed_roots: tuple[Path, ...],
) -> SafeReader:
    normalized_roots = tuple(Path(root).resolve() for root in allowed_roots)
    declared_root = str(item.get("read_root", "")).strip()
    if declared_root:
        root = Path(declared_root).resolve()
        if normalized_roots and root not in normalized_roots:
            raise ValueError(f"provider context read_root is not allowlisted: {root}")
        reader = SafeReader(root)
        reader.resolve_file(path)
        return reader

    # Backward-compatible checkpoint migration: infer the root only from the
    # caller-provided allowlist, never from untrusted item metadata.
    for root in normalized_roots:
        reader = SafeReader(root)
        try:
            reader.resolve_file(path)
        except SafeReadError:
            continue
        return reader
    raise ValueError(
        "provider context item has no safe allowlisted read root; restart the managed run "
        "or provide allowed_roots from the canonical harness"
    )


def load_context_documents(
    items: list[dict[str, Any]],
    kinds: set[str],
    max_chars: int | None = None,
    allowed_roots: tuple[Path, ...] = (),
) -> list[dict[str, str]]:
    budget = max_chars or int(os.environ.get("UIUX_PROVIDER_CONTEXT_CHARS", "180000"))
    if budget <= 0:
        raise ValueError("provider context budget must be positive")
    result: list[dict[str, str]] = []
    used = 0
    for item in items:
        if str(item.get("kind", "")) not in kinds:
            continue
        path = Path(str(item.get("path", "")))
        reader = _resolve_context_reader(item, path, allowed_roots)
        loaded = reader.read_text(path)
        text = loaded.content
        if used + len(text) > budget:
            raise ValueError(
                f"provider context budget exceeded ({budget} chars) while loading {loaded.relative_path}; "
                "route fewer skills/sources or raise UIUX_PROVIDER_CONTEXT_CHARS deliberately"
            )
        result.append({"path": str(loaded.path), "content": text})
        used += len(text)
    return result

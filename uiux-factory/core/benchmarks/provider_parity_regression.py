from __future__ import annotations

import ast
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.brain_os.adapters.flow_selection import select_canonical_flow
from core.dogfood.cross_project import compile_task_contract, project_profile
from core.runtime.flow_os.factory_provider_adapter import ManagedArtifactCompletionAdapter
from core.runtime.flow_os.flow import FlowPlanner
from core.runtime.flow_os.provider import ProviderStageResponse
from core.runtime.provider_compat_contract import ProviderError


@dataclass(frozen=True)
class ProviderParityResult:
    case_id: str
    passed: bool
    detail: str
    kind: str


class DeterministicManagedProvider:
    def __init__(self, name: str, responses: list[ProviderStageResponse | BaseException]) -> None:
        self.name = name
        self.model = f"benchmark-{name}"
        self.responses = list(responses)
        self.requests = []
        self.max_output_tokens: int | None = 8192
        self.timeout = 120

    def run_stage(self, request):
        self.requests.append(request)
        if not self.responses:
            raise RuntimeError("benchmark provider response queue exhausted")
        value = self.responses.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value


def load_provider_parity_benchmark(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("provider parity benchmark must be an object")
    if not str(payload.get("version", "")).strip():
        raise ValueError("provider parity benchmark version is required")
    if payload.get("scope") != "offline_contract_parity_not_live_provider_or_product_evidence":
        raise ValueError("provider parity benchmark must declare its non-product-evidence scope")
    if not isinstance(payload.get("cases"), list) or not payload["cases"]:
        raise ValueError("provider parity benchmark cases are required")
    if not isinstance(payload.get("project_smokes"), list) or not payload["project_smokes"]:
        raise ValueError("provider parity project_smokes are required")
    ids = [str(item.get("id", "")) for item in payload["cases"] + payload["project_smokes"]]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        raise ValueError("provider parity case ids must be non-empty and unique")
    return payload


def validate_legacy_complete_contract(factory_root: Path) -> ProviderParityResult:
    """Validate the legacy caller contract without importing aiohttp transport code."""

    source_path = factory_root / "core/runtime/free_provider.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    provider_class = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "FreeProvider"
        ),
        None,
    )
    if provider_class is None:
        return ProviderParityResult("legacy-complete-contract", False, "FreeProvider class missing", "contract")
    complete = next(
        (
            node
            for node in provider_class.body
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "complete"
        ),
        None,
    )
    if complete is None:
        return ProviderParityResult("legacy-complete-contract", False, "async complete() missing", "contract")
    positional = [arg.arg for arg in complete.args.args]
    kwonly = [arg.arg for arg in complete.args.kwonlyargs]
    if positional != ["self", "stage", "system", "prompt"] or kwonly != ["json_mode"]:
        return ProviderParityResult(
            "legacy-complete-contract",
            False,
            f"legacy complete signature drifted: positional={positional} kwonly={kwonly}",
            "contract",
        )
    source = source_path.read_text(encoding="utf-8")
    shared_markers = (
        "PROVIDER_CONTEXT_CHAR_LIMIT",
        "PROVIDER_MAX_CALLS_PER_RUN",
        "PROVIDER_STAGE_MAX_TOKENS",
        "PROVIDER_STAGE_TIMEOUT",
    )
    missing = [marker for marker in shared_markers if marker not in source]
    if missing:
        return ProviderParityResult(
            "legacy-complete-contract",
            False,
            "legacy provider no longer consumes shared compatibility contract: " + ", ".join(missing),
            "contract",
        )
    return ProviderParityResult(
        "legacy-complete-contract",
        True,
        "async complete(stage, system, prompt, *, json_mode) and shared limits preserved",
        "contract",
    )


def _carrier(artifact: str, *, status: str = "CONTINUE", evidence: list[str] | None = None) -> ProviderStageResponse:
    return ProviderStageResponse(
        status=status,
        actions=[],
        summary="provider parity fixture",
        evidence=list(evidence or []),
        replan_signal=None,
        artifact=artifact,
    )


async def _no_sleep(_seconds: float) -> None:
    return None


def evaluate_provider_case(case: dict[str, Any], *, factory_root: Path) -> ProviderParityResult:
    case_id = str(case.get("id", "")).strip()
    stage = str(case.get("stage", "research"))
    artifact = str(case.get("artifact", ""))
    mode = str(case.get("mode", "success"))
    json_mode = bool(case.get("json_mode", False))
    expected_error = str(case.get("expected_error", ""))

    env: dict[str, str] = {}
    preferred = str(case.get("preferred_provider", "")).strip()
    if preferred:
        env[f"UIUX_PROVIDER_{stage.upper()}"] = preferred

    if mode == "transient_fallback":
        providers = [
            DeterministicManagedProvider(
                "groq",
                [RuntimeError("free-tier provider HTTP 503"), RuntimeError("free-tier provider HTTP 503")],
            ),
            DeterministicManagedProvider("gemini", [_carrier(artifact)]),
        ]
    elif mode == "lifecycle_pass":
        providers = [DeterministicManagedProvider("groq", [_carrier(artifact, status="PASS", evidence=["claim"])])]
    elif mode == "evidence_carrier":
        providers = [DeterministicManagedProvider("groq", [_carrier(artifact, evidence=["claim"])])]
    else:
        first_name = preferred or "groq"
        providers = [DeterministicManagedProvider(first_name, [_carrier(artifact)])]
        if preferred == "gemini":
            providers.insert(0, DeterministicManagedProvider("groq", [_carrier("wrong provider")]))

    adapter = ManagedArtifactCompletionAdapter(providers, env=env, project_root=factory_root)
    try:
        with patch("core.runtime.flow_os.factory_provider_adapter.asyncio.sleep", new=_no_sleep):
            result = asyncio.run(
                adapter.complete(
                    stage=stage,
                    system=f"benchmark system {case_id}",
                    prompt=f"benchmark prompt {case_id}",
                    json_mode=json_mode,
                )
            )
    except ProviderError as exc:
        if expected_error and expected_error in str(exc):
            return ProviderParityResult(case_id, True, f"rejected as expected: {expected_error}", "provider_contract")
        return ProviderParityResult(case_id, False, f"unexpected provider rejection: {exc}", "provider_contract")

    if expected_error:
        return ProviderParityResult(case_id, False, "expected rejection but adapter returned output", "provider_contract")
    if result != artifact:
        return ProviderParityResult(case_id, False, "artifact changed across compatibility adapter", "provider_contract")
    expected_calls = int(case.get("expected_calls", 1))
    if adapter.calls != expected_calls:
        return ProviderParityResult(
            case_id,
            False,
            f"call count mismatch: expected={expected_calls} actual={adapter.calls}",
            "provider_contract",
        )
    expected_provider = str(case.get("expected_provider", "")).strip()
    completed = next((row for row in adapter.history if row.get("status") == "completed"), None)
    if expected_provider and (not completed or completed.get("provider") != expected_provider):
        return ProviderParityResult(
            case_id,
            False,
            f"provider order mismatch: expected completion from {expected_provider}; history={adapter.history}",
            "provider_contract",
        )
    if any(row.get("compatibility_mode") != "managed_artifact_carrier" for row in adapter.history):
        return ProviderParityResult(case_id, False, "history lost compatibility provenance", "provider_contract")
    return ProviderParityResult(case_id, True, "offline completion contract parity preserved", "provider_contract")


def evaluate_project_smoke(
    case: dict[str, Any],
    *,
    factory_root: Path,
    planner: FlowPlanner,
) -> ProviderParityResult:
    case_id = str(case.get("id", "")).strip()
    project_id = str(case.get("project_id", "")).strip()
    profile = project_profile(project_id)
    context = compile_task_contract(profile)
    selection = select_canonical_flow(
        planner,
        context=context,
        goal=profile.default_task,
        scope=context.get("scope", []),
    )
    expected_surface = str(case.get("expected_surface", ""))
    expected_flow = str(case.get("expected_flow", ""))
    if str(context.get("change_surface")) != expected_surface or selection.flow_id != expected_flow:
        return ProviderParityResult(
            case_id,
            False,
            f"canonical routing drifted before provider smoke: surface={context.get('change_surface')} flow={selection.flow_id}",
            "project_profile_smoke",
        )

    artifact = json.dumps(
        {
            "project_id": project_id,
            "change_surface": context.get("change_surface"),
            "flow_id": selection.flow_id,
            "scope": "offline_provider_compatibility_smoke",
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    provider = DeterministicManagedProvider("groq", [_carrier(artifact)])
    adapter = ManagedArtifactCompletionAdapter([provider], project_root=factory_root)
    result = asyncio.run(
        adapter.complete(
            stage="implementation",
            system="Offline compatibility smoke only; do not claim product evidence.",
            prompt=json.dumps(context, ensure_ascii=False, sort_keys=True),
            json_mode=True,
        )
    )
    decoded = json.loads(result)
    if decoded.get("project_id") != project_id or decoded.get("flow_id") != expected_flow:
        return ProviderParityResult(case_id, False, "project identity/flow was not preserved through adapter smoke", "project_profile_smoke")
    if adapter.calls != 1 or len(provider.requests) != 1:
        return ProviderParityResult(case_id, False, "project smoke used unexpected provider call count", "project_profile_smoke")
    return ProviderParityResult(
        case_id,
        True,
        "offline adapter smoke preserved canonical project/routing context; not product evidence",
        "project_profile_smoke",
    )


def evaluate_provider_parity_benchmark(
    path: Path,
    *,
    factory_root: Path,
    planner: FlowPlanner,
) -> list[ProviderParityResult]:
    payload = load_provider_parity_benchmark(path)
    results = [validate_legacy_complete_contract(factory_root)]
    results.extend(evaluate_provider_case(dict(case), factory_root=factory_root) for case in payload["cases"])
    results.extend(
        evaluate_project_smoke(dict(case), factory_root=factory_root, planner=planner)
        for case in payload["project_smokes"]
    )
    return results

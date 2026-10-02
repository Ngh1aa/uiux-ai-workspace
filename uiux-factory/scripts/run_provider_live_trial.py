from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.runtime.flow_os.factory_provider_adapter import ManagedArtifactCompletionAdapter
from core.runtime.flow_os.free_tier_provider import OpenAICompatibleFreeTierProvider
from core.runtime.free_provider import FreeProvider, ProviderConfig
from core.runtime.provider_compat_contract import ProviderError


SUPPORTED_PROVIDERS = ("groq", "gemini")
LANES = ("legacy", "managed_compat")
TRIALS = (
    {
        "mode_id": "plain_text",
        "stage": "research",
        "json_mode": False,
        "marker": "A51-LIVE-PLAIN",
        "system": (
            "A51 provider transport compatibility live trial. Follow the user request exactly. "
            "Do not include secrets, account data, explanations, evidence claims or release claims."
        ),
        "prompt": "Return exactly this plain-text marker and nothing else: A51-LIVE-PLAIN",
    },
    {
        "mode_id": "json_object",
        "stage": "implementation",
        "json_mode": True,
        "marker": "A51-LIVE-JSON",
        "system": (
            "A51 provider transport compatibility live trial. Follow the user request exactly. "
            "Return only the requested JSON object and no secrets/account data."
        ),
        "prompt": (
            "Return a JSON object with exactly two keys: trial_marker with value "
            "\"A51-LIVE-JSON\" and ok with boolean value true."
        ),
    },
)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _request_digest(trial: dict[str, Any]) -> str:
    payload = {
        "mode_id": trial["mode_id"],
        "stage": trial["stage"],
        "json_mode": trial["json_mode"],
        "system": trial["system"],
        "prompt": trial["prompt"],
    }
    return _sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _contract_valid(artifact: str, trial: dict[str, Any]) -> bool:
    if trial["json_mode"]:
        try:
            decoded = json.loads(artifact)
        except json.JSONDecodeError:
            return False
        return decoded == {"trial_marker": trial["marker"], "ok": True}
    return artifact.strip() == trial["marker"]


def _error_category(error: BaseException) -> str:
    if isinstance(error, (asyncio.TimeoutError, TimeoutError)):
        return "network_or_timeout"
    text = str(error).lower()
    if any(marker in text for marker in ("timeout", "network", "connection", "http 429", "http 502", "http 503", "http 504")):
        return "network_or_timeout"
    if any(marker in text for marker in ("contract", "json", "artifact", "continue", "evidence", "action")):
        return "contract_invalid"
    if isinstance(error, ProviderError):
        return "provider_error"
    return "unexpected_error"


def _success_receipt(
    *,
    config: ProviderConfig,
    lane: str,
    trial: dict[str, Any],
    artifact: str,
) -> dict[str, Any]:
    return {
        "provider": config.name,
        "model": config.model,
        "lane": lane,
        "mode_id": trial["mode_id"],
        "stage": trial["stage"],
        "json_mode": bool(trial["json_mode"]),
        "success": True,
        "contract_valid": True,
        "request_sha256": _request_digest(trial),
        "artifact_sha256": _sha256_text(artifact),
        "artifact_chars": len(artifact),
        "error_category": None,
        "automatic_cross_lane_fallback": False,
        "authority_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "release_effect": "none",
    }


def _failure_receipt(
    *,
    config: ProviderConfig,
    lane: str,
    trial: dict[str, Any],
    error_category: str,
) -> dict[str, Any]:
    return {
        "provider": config.name,
        "model": config.model,
        "lane": lane,
        "mode_id": trial["mode_id"],
        "stage": trial["stage"],
        "json_mode": bool(trial["json_mode"]),
        "success": False,
        "contract_valid": False,
        "request_sha256": _request_digest(trial),
        "artifact_sha256": None,
        "artifact_chars": 0,
        "error_category": error_category,
        "automatic_cross_lane_fallback": False,
        "authority_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "release_effect": "none",
    }


def _legacy_provider(config: ProviderConfig, env: dict[str, str]) -> FreeProvider:
    return FreeProvider([config], env=dict(env))


def _managed_provider(config: ProviderConfig, env: dict[str, str]) -> ManagedArtifactCompletionAdapter:
    provider = OpenAICompatibleFreeTierProvider(
        config.name,
        model=config.model,
        api_key=config.key,
        env=dict(env),
    )
    return ManagedArtifactCompletionAdapter([provider], env=dict(env), project_root=ROOT)


async def _run_one(
    *,
    config: ProviderConfig,
    lane: str,
    trial: dict[str, Any],
    env: dict[str, str],
) -> dict[str, Any]:
    try:
        provider = _legacy_provider(config, env) if lane == "legacy" else _managed_provider(config, env)
        artifact = await provider.complete(
            trial["stage"],
            trial["system"],
            trial["prompt"],
            json_mode=bool(trial["json_mode"]),
        )
        if not _contract_valid(artifact, trial):
            return _failure_receipt(
                config=config,
                lane=lane,
                trial=trial,
                error_category="contract_invalid",
            )
        return _success_receipt(config=config, lane=lane, trial=trial, artifact=artifact)
    except (ProviderError, RuntimeError, ValueError, asyncio.TimeoutError, TimeoutError) as error:
        return _failure_receipt(
            config=config,
            lane=lane,
            trial=trial,
            error_category=_error_category(error),
        )


async def _collect(root: Path) -> dict[str, Any]:
    if os.environ.get("UIUX_PROVIDER_LIVE_TRIAL_CONFIRMED") != "1":
        raise ProviderError(
            "Live provider trial is disabled. Set UIUX_PROVIDER_LIVE_TRIAL_CONFIRMED=1 only after "
            "confirming the configured accounts/models may be used for this bounded trial."
        )

    configured = FreeProvider.from_env(root)
    by_name = {config.name: config for config in configured.configs}
    receipts: list[dict[str, Any]] = []
    for provider_name in SUPPORTED_PROVIDERS:
        config = by_name.get(provider_name)
        if config is None:
            continue
        for lane in LANES:
            for trial in TRIALS:
                receipts.append(
                    await _run_one(
                        config=config,
                        lane=lane,
                        trial=dict(trial),
                        env=dict(configured.env),
                    )
                )

    required_count = len(SUPPORTED_PROVIDERS) * len(LANES) * len(TRIALS)
    if not receipts:
        status = "NOT_RUN"
        collected_on = None
    elif len(receipts) == required_count:
        status = "COMPLETE"
        collected_on = datetime.now(timezone.utc).date().isoformat()
    else:
        status = "PARTIAL"
        collected_on = datetime.now(timezone.utc).date().isoformat()

    return {
        "schema_version": 1,
        "receipt_set_id": "provider-live-trial-receipts-v1",
        "version": "1.0.0",
        "collected_on": collected_on,
        "collection_status": status,
        "receipts": receipts,
    }


def _trial_exit_code(payload: dict[str, Any]) -> int:
    receipts = payload.get("receipts")
    if not isinstance(receipts, list):
        return 1
    required_count = len(SUPPORTED_PROVIDERS) * len(LANES) * len(TRIALS)
    if payload.get("collection_status") != "COMPLETE" or len(receipts) != required_count:
        return 1
    return 0 if all(row.get("success") is True and row.get("contract_valid") is True for row in receipts) else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run explicit A51.1 live provider transport trials and write sanitized receipts"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help=(
            "Destination for the sanitized receipt JSON. The script never updates the canonical "
            "benchmark ledger or provider default automatically."
        ),
    )
    args = parser.parse_args()

    try:
        payload = asyncio.run(_collect(ROOT))
    except ProviderError as exc:
        print(f"A51.1 live provider trial BLOCKED: {exc}")
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    passed = sum(1 for row in payload["receipts"] if row["success"] and row["contract_valid"])
    total = len(payload["receipts"])
    print(
        f"A51.1 live provider trial collected: status={payload['collection_status']} "
        f"contract_pass={passed}/{total} output={args.output}"
    )
    print(
        "Receipt contains provider/model/lane/mode, hashes, lengths and bounded status only; "
        "prompt bodies, response bodies and credentials are not persisted."
    )
    print("No provider default, governance decision, merge/release authority or product evidence was changed.")
    return _trial_exit_code(payload)


if __name__ == "__main__":
    raise SystemExit(main())

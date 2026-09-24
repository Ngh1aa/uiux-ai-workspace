"""Explicit free-tier cloud routing. No automatic billing, model or account upgrade."""

from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import aiohttp
from dotenv import dotenv_values


ENDPOINTS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
}
KEY_NAMES = {"groq": "GROQ_API_KEY", "gemini": "GEMINI_API_KEY"}


class ProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    model: str
    key: str = field(repr=False)


class FreeProvider:
    """Only configured providers; one attempt each on transient failures, bounded per run."""

    def __init__(self, configs: list[ProviderConfig], env: dict[str, str] | None = None):
        if not configs:
            raise ProviderError("Chưa cấu hình AI cloud. Xem docs/FREE_BRAIN.md; không có API trả phí dự phòng.")
        self.configs = configs
        self.env = env or {}
        self.calls = 0
        self.history: list[dict] = []

    @classmethod
    def from_env(cls, root: Path) -> "FreeProvider":
        # Local configuration stays out of Git, browser state and run artifacts.
        env = {key: value for key, value in {**dotenv_values(root / ".env.local"), **os.environ}.items() if value is not None}
        if env.get("UIUX_FREE_TIER_CONFIRMED") != "1":
            raise ProviderError("AI cloud chưa bật. Chỉ bật UIUX_FREE_TIER_CONFIRMED=1 cho tài khoản free tier đã kiểm tra billing.")
        names = list(dict.fromkeys(x.strip() for x in env.get("UIUX_CLOUD_PROVIDERS", "").split(",") if x.strip()))
        configs = []
        for name in names:
            if name not in ENDPOINTS:
                raise ProviderError(f"Provider không được hỗ trợ: {name}")
            key = env.get(KEY_NAMES[name], "")
            model = env.get(f"UIUX_{name.upper()}_MODEL", "")
            if not key or not model:
                raise ProviderError(f"Thiếu key hoặc model cho {name}; xem docs/FREE_BRAIN.md.")
            if not re.fullmatch(r"[A-Za-z0-9._:/-]{1,120}", model):
                raise ProviderError(f"Model ID không hợp lệ cho {name}.")
            configs.append(ProviderConfig(name, model, key))
        return cls(configs, env)

    # Stage-specific max_tokens: heavy generation stages get more room.
    STAGE_MAX_TOKENS: dict[str, int] = {
        "implementation": 12000,
        "repair": 12000,
        "visual_composition": 8000,
        "art_direction": 8000,
    }
    # Heavy stages need longer timeouts.
    STAGE_TIMEOUT: dict[str, int] = {
        "implementation": 180,
        "repair": 180,
        "visual_composition": 120,
    }
    MAX_CALLS_PER_RUN = 20

    async def complete(self, stage: str, system: str, prompt: str, *, json_mode: bool = False) -> str:
        if len(system) + len(prompt) > 80000:
            raise ProviderError("Context vượt giới hạn 80.000 ký tự; hãy rút gọn brief/context.")
        preferred = self.env.get(f"UIUX_PROVIDER_{stage.upper()}")
        configs = list(self.configs)
        if preferred:
            if preferred not in {config.name for config in configs}:
                raise ProviderError(f"Provider cho stage {stage} chưa được bật.")
            configs.sort(key=lambda config: config.name != preferred)
        max_tokens = self.STAGE_MAX_TOKENS.get(stage, 8000)
        timeout_sec = self.STAGE_TIMEOUT.get(stage, 120)
        failures = []
        for config in configs:
            # Retry once on transient failures with backoff.
            for retry in range(2):
                if self.calls >= self.MAX_CALLS_PER_RUN:
                    raise ProviderError(f"Đã đạt giới hạn {self.MAX_CALLS_PER_RUN} yêu cầu AI cho run này.")
                self.calls += 1
                payload = {"model": config.model, "messages": [
                    {"role": "system", "content": system}, {"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "stream": False}
                if json_mode:
                    payload["response_format"] = {"type": "json_object"}
                record = {"stage": stage, "provider": config.name, "model": config.model, "attempt": self.calls}
                self.history.append(record)
                try:
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_sec), trust_env=False) as session:
                        async with session.post(ENDPOINTS[config.name], json=payload,
                                                headers={"Authorization": f"Bearer {config.key}"}, allow_redirects=False) as response:
                            record["http_status"] = response.status
                            if response.status in {429, 502, 503, 504}:
                                failures.append(f"{config.name}: HTTP {response.status}")
                                if retry == 0:
                                    await asyncio.sleep(2 + retry * 3)
                                    continue
                                break
                            if response.status != 200:
                                # Provider error bodies can echo prompts or credentials; never persist them.
                                raise ProviderError(f"{config.name}: HTTP {response.status}; kiểm tra key, model và tài khoản.")
                            raw = bytearray()
                            async for chunk in response.content.iter_chunked(65536):
                                raw.extend(chunk)
                                if len(raw) > 4_000_000:
                                    raise ProviderError("AI response vượt giới hạn 4 MB.")
                            data = json.loads(raw)
                            choice = data["choices"][0]
                            if choice.get("finish_reason") != "stop":
                                raise ProviderError("AI response chưa hoàn chỉnh hoặc bị từ chối; không ghi code bị cắt.")
                            content = choice["message"]["content"]
                            if not isinstance(content, str) or not content.strip():
                                raise ProviderError("AI trả về nội dung rỗng.")
                            record["status"] = "completed"
                            return content
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    record["status"] = "connection_failed"
                    failures.append(f"{config.name}: connection/timeout")
                    if retry == 0:
                        await asyncio.sleep(2)
                        continue
                except (KeyError, IndexError, TypeError, ValueError):
                    raise ProviderError("AI trả về response không đúng contract.") from None
                break
        raise ProviderError("Không có provider khả dụng trong danh sách đã bật: " + "; ".join(failures))

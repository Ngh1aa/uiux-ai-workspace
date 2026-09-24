from __future__ import annotations

import asyncio
import base64
from io import BytesIO
import json
from pathlib import Path

import aiohttp

from core.runtime.free_provider import ENDPOINTS, FreeProvider, ProviderError


class FreeVisionProvider(FreeProvider):
    """Multimodal extension of FreeProvider for bounded screenshot critique.

    It preserves the existing free-tier opt-in, provider allow-list and call budget.
    Screenshot bytes are encoded only in-memory for the request and are never stored
    in provider history or run artifacts.
    """

    MAX_IMAGES = 8
    MAX_EDGE = 1280
    JPEG_QUALITY = 78

    @classmethod
    def _image_data_url(cls, path: Path) -> str:
        try:
            from PIL import Image
        except ImportError as exc:
            raise ProviderError("Pillow is required for semantic visual QA.") from exc

        path = Path(path).resolve()
        if not path.is_file():
            raise ProviderError(f"Visual QA screenshot is missing: {path}")

        with Image.open(path).convert("RGB") as image:
            width, height = image.size
            longest = max(width, height)
            if longest > cls.MAX_EDGE:
                scale = cls.MAX_EDGE / longest
                image = image.resize((max(1, int(width * scale)), max(1, int(height * scale))))
            output = BytesIO()
            image.save(output, format="JPEG", quality=cls.JPEG_QUALITY, optimize=True)

        encoded = base64.b64encode(output.getvalue()).decode("ascii")
        return "data:image/jpeg;base64," + encoded

    async def complete_vision(
        self,
        *,
        stage: str,
        system: str,
        prompt: str,
        images: list[tuple[str, Path]],
    ) -> str:
        if not images:
            raise ProviderError("Semantic visual QA requires at least one screenshot.")
        if len(images) > self.MAX_IMAGES:
            images = images[: self.MAX_IMAGES]

        preferred = self.env.get(f"UIUX_PROVIDER_{stage.upper()}")
        configs = list(self.configs)
        if preferred:
            if preferred not in {config.name for config in configs}:
                raise ProviderError(f"Provider cho stage {stage} chưa được bật.")
            configs.sort(key=lambda config: config.name != preferred)

        content: list[dict] = [{"type": "text", "text": prompt}]
        for label, image_path in images:
            content.append({"type": "text", "text": f"Screenshot: {label}"})
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": self._image_data_url(image_path)},
                }
            )

        failures: list[str] = []
        timeout_sec = self.STAGE_TIMEOUT.get(stage, 150)
        max_tokens = min(6000, self.STAGE_MAX_TOKENS.get(stage, 8000))

        for config in configs:
            if self.calls >= self.MAX_CALLS_PER_RUN:
                raise ProviderError(f"Đã đạt giới hạn {self.MAX_CALLS_PER_RUN} yêu cầu AI cho run này.")
            self.calls += 1
            record = {
                "stage": stage,
                "provider": config.name,
                "model": config.model,
                "attempt": self.calls,
                "modality": "vision",
                "image_count": len(images),
            }
            self.history.append(record)
            payload = {
                "model": config.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": content},
                ],
                "max_tokens": max_tokens,
                "stream": False,
            }

            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=timeout_sec),
                    trust_env=False,
                ) as session:
                    async with session.post(
                        ENDPOINTS[config.name],
                        json=payload,
                        headers={"Authorization": f"Bearer {config.key}"},
                        allow_redirects=False,
                    ) as response:
                        record["http_status"] = response.status
                        if response.status != 200:
                            # A text-only configured model can reject image_url input.
                            # Never persist the response body because providers may echo prompts.
                            record["status"] = "vision_rejected"
                            failures.append(f"{config.name}: HTTP {response.status}")
                            continue

                        raw = bytearray()
                        async for chunk in response.content.iter_chunked(65536):
                            raw.extend(chunk)
                            if len(raw) > 4_000_000:
                                raise ProviderError("AI response vượt giới hạn 4 MB.")
                        data = json.loads(raw)
                        choice = data["choices"][0]
                        content_text = choice["message"]["content"]
                        if not isinstance(content_text, str) or not content_text.strip():
                            raise ProviderError("Vision provider returned empty content.")
                        record["status"] = "completed"
                        return content_text
            except (aiohttp.ClientError, asyncio.TimeoutError):
                record["status"] = "connection_failed"
                failures.append(f"{config.name}: connection/timeout")
            except (KeyError, IndexError, TypeError, ValueError):
                record["status"] = "invalid_response"
                failures.append(f"{config.name}: invalid response")

        raise ProviderError(
            "No configured free-tier provider accepted semantic screenshot review: "
            + "; ".join(failures)
        )

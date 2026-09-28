from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any

from core.runtime.flow_os.browser_evidence import BrowserEvidenceError, PlaywrightBrowserEvidenceAdapter


class BrowserObservationError(RuntimeError):
    """Raised when model-readable browser observations are unsafe or unavailable."""


def _bounded_text(value: Any, limit: int) -> str:
    return str(value or "")[:limit]


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class PlaywrightBrowserObservationAdapter:
    """Expose bounded read-only browser facts without granting acceptance authority.

    The adapter reuses the canonical Playwright browser-evidence capture path and then
    sanitizes its JSON into provider-readable observations. It never evaluates model
    JavaScript, never returns screenshot bytes, and never upgrades its output to trusted
    gate evidence. Deterministic BrowserQA remains the acceptance owner.
    """

    def __init__(self, qa_root: Path, policy: dict[str, Any]) -> None:
        self.qa_root = Path(qa_root).resolve()
        self.policy = dict(policy)
        raw = self.policy.get("browser_observation", {})
        if not isinstance(raw, dict):
            raise BrowserObservationError("runtime-policy browser_observation must be an object")
        enabled = raw.get("enabled", True)
        if not isinstance(enabled, bool):
            raise BrowserObservationError("browser_observation.enabled must be a boolean")
        self.enabled = enabled

        def bounded_int(name: str, default: int, low: int, high: int) -> int:
            value = raw.get(name, default)
            if isinstance(value, bool) or not isinstance(value, int):
                raise BrowserObservationError(f"browser_observation.{name} must be an integer")
            if value < low or value > high:
                raise BrowserObservationError(
                    f"browser_observation.{name} must be between {low} and {high}"
                )
            return value

        self.max_dom_chars = bounded_int("max_dom_chars", 12000, 256, 100000)
        self.max_aria_chars = bounded_int("max_aria_chars", 12000, 256, 100000)
        self.max_console_items = bounded_int("max_console_items", 40, 1, 200)
        self.max_network_items = bounded_int("max_network_items", 40, 1, 200)
        self.max_elements = bounded_int("max_elements", 24, 1, 100)
        self.evidence = PlaywrightBrowserEvidenceAdapter(self.qa_root, self.policy)

    def _sanitize_elements(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        result: list[dict[str, Any]] = []
        for raw in value[: self.max_elements]:
            if not isinstance(raw, dict):
                continue
            box = raw.get("box")
            result.append(
                {
                    "tag": _bounded_text(raw.get("tag"), 32),
                    "role": _bounded_text(raw.get("role"), 64),
                    "text": _bounded_text(raw.get("text"), 300),
                    "aria_label": _bounded_text(raw.get("ariaLabel"), 300),
                    "name": _bounded_text(raw.get("name"), 160),
                    "type": _bounded_text(raw.get("type"), 80),
                    "disabled": bool(raw.get("disabled", False)),
                    "checked": raw.get("checked") if isinstance(raw.get("checked"), bool) else None,
                    "expanded": raw.get("expanded") if isinstance(raw.get("expanded"), bool) else None,
                    "box": dict(box) if isinstance(box, dict) else None,
                    "style": {
                        key: _bounded_text(value, 120)
                        for key, value in dict(raw.get("style", {})).items()
                        if key in {
                            "display",
                            "position",
                            "color",
                            "backgroundColor",
                            "fontFamily",
                            "fontSize",
                            "fontWeight",
                            "lineHeight",
                            "width",
                            "height",
                            "overflow",
                        }
                    },
                    "image": {
                        key: raw.get("image", {}).get(key)
                        for key in (
                            "src",
                            "naturalWidth",
                            "naturalHeight",
                            "renderedWidth",
                            "renderedHeight",
                        )
                        if isinstance(raw.get("image"), dict) and key in raw["image"]
                    }
                    if isinstance(raw.get("image"), dict)
                    else None,
                }
            )
        return result

    def observe(self, artifacts_dir: Path, route: str | None = None) -> dict[str, Any]:
        if not self.enabled:
            raise BrowserObservationError("browser observation is disabled by runtime policy")
        try:
            records = self.evidence.collect(artifacts_dir, stage_id="browser_observation")
            root = self.evidence._artifact_root(artifacts_dir)
        except BrowserEvidenceError as exc:
            raise BrowserObservationError(str(exc)) from exc

        selected = None
        if route is None and len(records) == 1:
            selected = records[0]
        else:
            for record in records:
                if str(record.data.get("route", "")) == str(route or ""):
                    selected = record
                    break
        if selected is None:
            available = ", ".join(str(item.data.get("route", "")) for item in records)
            raise BrowserObservationError(
                f"browser observation route not found: {route!r}; available: {available or '(none)'}"
            )

        evidence_json = root / str(selected.data["evidence_json"])
        payload = json.loads(evidence_json.read_text(encoding="utf-8"))
        dom = _bounded_text(payload.get("dom"), self.max_dom_chars)
        aria = _bounded_text(payload.get("ariaSnapshot"), self.max_aria_chars)
        console = []
        for raw in list(payload.get("consoleMessages", []))[: self.max_console_items]:
            if isinstance(raw, dict):
                console.append(
                    {
                        "type": _bounded_text(raw.get("type"), 32),
                        "text": _bounded_text(raw.get("text"), 1000),
                    }
                )
        failed = [
            _bounded_text(item, 1000)
            for item in list(payload.get("failedRequests", []))[: self.max_network_items]
        ]
        blocked = [
            _bounded_text(item, 1000)
            for item in list(payload.get("blockedRequests", []))[: self.max_network_items]
        ]
        page_errors = [
            _bounded_text(item, 1000)
            for item in list(payload.get("pageErrors", []))[: self.max_console_items]
        ]
        computed = payload.get("computedStyle", {})
        if not isinstance(computed, dict):
            computed = {}

        return {
            "observation_id": f"browser_obs_{uuid.uuid4().hex[:16]}",
            "route": str(selected.data.get("route", "")),
            "url": str(selected.data.get("url", "")),
            "title": str(selected.data.get("title", ""))[:500],
            "viewport": dict(selected.data.get("viewport", {})),
            "box": selected.data.get("box"),
            "computed_style": {
                str(key)[:80]: _bounded_text(value, 160)
                for key, value in computed.items()
            },
            "dom_excerpt": dom,
            "dom_excerpt_sha256": _sha256_text(dom),
            "aria_snapshot": aria,
            "aria_snapshot_sha256": _sha256_text(aria),
            "elements": self._sanitize_elements(payload.get("elements", [])),
            "console_messages": console,
            "console_errors": [item for item in console if item["type"] == "error"],
            "page_errors": page_errors,
            "failed_requests": failed,
            "blocked_requests": blocked,
            "screenshot": str(selected.data.get("screenshot", "")),
            "screenshot_sha256": str(selected.data.get("screenshot_sha256", "")),
            "browser_evidence_status": selected.status,
            "advisory_only": True,
            "trusted": False,
            "authority_effect": "none",
            "gate_effect": "none",
            "evidence_effect": "none",
            "rule": (
                "This is bounded model-readable browser context only. Deterministic BrowserQA/browser_render "
                "evidence remains the acceptance owner."
            ),
        }

    def capture_and_observe(self, base_url: str, route: str) -> dict[str, Any]:
        if not self.enabled:
            raise BrowserObservationError("browser observation is disabled by runtime policy")
        observation_dir = self.qa_root / "artifacts" / f"model-observation-{uuid.uuid4().hex[:16]}"
        try:
            self.evidence.capture(base_url, [route], artifacts_dir=observation_dir)
        except BrowserEvidenceError as exc:
            raise BrowserObservationError(str(exc)) from exc
        return self.observe(observation_dir, route=route)

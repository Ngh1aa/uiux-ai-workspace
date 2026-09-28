from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.runtime.flow_os.browser_evidence import BrowserEvidenceError, PlaywrightBrowserEvidenceAdapter


def _policy() -> dict:
    return {
        "browser_evidence": {
            "allow_remote": False,
            "max_routes": 4,
            "max_artifact_bytes": 1024 * 1024,
            "timeout_seconds": 30,
        }
    }


def test_a4_9_routes_must_stay_same_origin_relative(tmp_path: Path) -> None:
    qa = tmp_path / "qa"
    qa.mkdir()
    adapter = PlaywrightBrowserEvidenceAdapter(qa, _policy())

    assert adapter._validate_routes(["/", "/dashboard?tab=1#summary"]) == [
        "/",
        "/dashboard?tab=1#summary",
    ]
    for unsafe in ["https://example.com/", "//example.com/", "dashboard", "http://127.0.0.1:9999/"]:
        with pytest.raises(BrowserEvidenceError, match="same-origin relative paths"):
            adapter._validate_routes([unsafe])


def _write_artifact(artifacts: Path, *, url: str, blocked_requests: list[str]) -> None:
    screenshot = artifacts / "home-render.png"
    screenshot.write_bytes(b"\x89PNG\r\n\x1a\nfixture-png-bytes")
    payload = {
        "route": "/",
        "url": url,
        "title": "Home",
        "viewport": {"width": 1440, "height": 900},
        "box": {"x": 0, "y": 0, "width": 100, "height": 30},
        "screenshot": screenshot.name,
        "ariaSnapshot": "- heading Home",
        "consoleMessages": [],
        "pageErrors": [],
        "blockedRequests": blocked_requests,
    }
    (artifacts / "browser-evidence-home.json").write_text(json.dumps(payload), encoding="utf-8")


def test_a4_9_ingested_cross_origin_network_evidence_is_failed(tmp_path: Path) -> None:
    qa = tmp_path / "qa"
    artifacts = qa / "artifacts"
    artifacts.mkdir(parents=True)
    adapter = PlaywrightBrowserEvidenceAdapter(qa, _policy())

    _write_artifact(
        artifacts,
        url="http://127.0.0.1:4173/",
        blocked_requests=["https://example.com/tracker.js"],
    )
    blocked = adapter.collect(artifacts)
    assert blocked[0].status == "FAIL"
    assert blocked[0].data["blocked_requests"] == ["https://example.com/tracker.js"]

    _write_artifact(
        artifacts,
        url="https://example.com/redirected",
        blocked_requests=[],
    )
    redirected = adapter.collect(artifacts)
    assert redirected[0].status == "FAIL"
    assert redirected[0].data["remote_final_url"] is True

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ToolRegistry
from core.runtime.flow_os.browser_evidence import PlaywrightBrowserEvidenceAdapter
from core.runtime.flow_os.browser_observation import (
    BrowserObservationError,
    PlaywrightBrowserObservationAdapter,
)
from core.runtime.flow_os.evidence import evidence_from_tool, gate_evidence_errors


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS_ROOT / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))
PNG = b"\x89PNG\r\n\x1a\n" + b"fixture-png-payload"


def _write_artifacts(
    qa_root: Path,
    *,
    route: str = "/",
    failed_requests: list[str] | None = None,
    dom: str | None = None,
    aria: str | None = None,
) -> Path:
    artifacts = qa_root / "artifacts" / "fixture"
    artifacts.mkdir(parents=True)
    (artifacts / "root-render.png").write_bytes(PNG)
    payload = {
        "route": route,
        "url": "http://127.0.0.1:4173/",
        "title": "Fixture",
        "viewport": {"width": 1440, "height": 900},
        "hasMain": True,
        "dom": dom if dom is not None else "<main>" + ("D" * 500) + "</main>",
        "ariaSnapshot": aria if aria is not None else "ARIA" * 200,
        "box": {"x": 10, "y": 20, "width": 200, "height": 40},
        "computedStyle": {"fontSize": "16px", "color": "rgb(0, 0, 0)"},
        "elements": [
            {
                "tag": "button",
                "role": "button",
                "text": "Continue",
                "ariaLabel": "Continue",
                "name": "",
                "type": "button",
                "disabled": False,
                "checked": None,
                "expanded": None,
                "box": {"x": 10, "y": 20, "width": 200, "height": 40},
                "style": {"display": "block", "fontSize": "16px"},
                "image": None,
            }
        ],
        "screenshot": "root-render.png",
        "consoleMessages": [{"type": "log", "text": "loaded"}],
        "pageErrors": [],
        "blockedRequests": [],
        "failedRequests": list(failed_requests or []),
    }
    (artifacts / "browser-evidence-root.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    return artifacts


def test_a9_observation_is_bounded_and_contains_useful_browser_facts(tmp_path: Path) -> None:
    qa_root = tmp_path / "qa"
    qa_root.mkdir()
    artifacts = _write_artifacts(qa_root, dom="X" * 1000, aria="Y" * 1000)
    policy = json.loads(json.dumps(POLICY))
    policy["browser_observation"] = {
        "enabled": True,
        "max_dom_chars": 256,
        "max_aria_chars": 300,
        "max_console_items": 10,
        "max_network_items": 10,
        "max_elements": 5,
    }

    observed = PlaywrightBrowserObservationAdapter(qa_root, policy).observe(artifacts, route="/")

    assert observed["route"] == "/"
    assert observed["title"] == "Fixture"
    assert len(observed["dom_excerpt"]) == 256
    assert len(observed["aria_snapshot"]) == 300
    assert len(observed["dom_excerpt_sha256"]) == 64
    assert observed["elements"][0]["role"] == "button"
    assert observed["screenshot"] == "root-render.png"
    assert len(observed["screenshot_sha256"]) == 64
    assert observed["advisory_only"] is True
    assert observed["trusted"] is False
    assert observed["gate_effect"] == "none"


def test_a9_failed_network_request_fails_trusted_browser_render(tmp_path: Path) -> None:
    qa_root = tmp_path / "qa"
    qa_root.mkdir()
    artifacts = _write_artifacts(
        qa_root,
        failed_requests=["GET http://127.0.0.1:4173/missing.png :: net::ERR_FAILED"],
    )

    records = PlaywrightBrowserEvidenceAdapter(qa_root, POLICY).collect(artifacts)
    assert records[0].status == "FAIL"
    assert records[0].data["failed_requests"]


def test_a9_browser_observation_checkpoint_record_strips_large_content_and_cannot_gate() -> None:
    record = evidence_from_tool(
        "qa",
        "browser_observe",
        {
            "route": "/",
            "url": "http://127.0.0.1:4173/",
            "title": "Fixture",
            "viewport": {"width": 1440, "height": 900},
            "dom_excerpt": "SECRET DOM" * 1000,
            "dom_excerpt_sha256": "a" * 64,
            "aria_snapshot": "SECRET ARIA" * 1000,
            "aria_snapshot_sha256": "b" * 64,
            "elements": [{"text": "hidden state"}],
            "console_messages": [{"type": "log", "text": "hello"}],
            "console_errors": [],
            "page_errors": [],
            "failed_requests": [],
            "blocked_requests": [],
            "screenshot": "root-render.png",
            "screenshot_sha256": "c" * 64,
            "browser_evidence_status": "PASS",
        },
    )
    payload = record.to_dict()

    assert payload["type"] == "browser_observation"
    assert payload["trusted"] is False
    assert "dom_excerpt" not in payload["data"]
    assert "aria_snapshot" not in payload["data"]
    assert "elements" not in payload["data"]
    errors = gate_evidence_errors(
        [{"id": "render", "require": "browser proof", "evidence_types": ["browser_render"]}],
        "qa",
        [payload],
        agent="qa",
    )
    assert errors == ["gate render missing typed evidence: browser_render"]


def test_a9_tool_registry_exposes_browser_observe_as_read_only() -> None:
    registry = ToolRegistry(SKILLS_ROOT, REPO_ROOT)
    spec = registry.specs["browser_observe"]

    assert spec.risk == "READ"
    assert spec.required_authority == "read_only"
    assert spec.side_effect is False


def test_a9_policy_types_fail_closed(tmp_path: Path) -> None:
    qa_root = tmp_path / "qa"
    qa_root.mkdir()
    policy = json.loads(json.dumps(POLICY))
    policy["browser_observation"] = {"enabled": "yes"}

    with pytest.raises(BrowserObservationError, match="enabled must be a boolean"):
        PlaywrightBrowserObservationAdapter(qa_root, policy)


def test_a9_missing_route_fails_closed(tmp_path: Path) -> None:
    qa_root = tmp_path / "qa"
    qa_root.mkdir()
    artifacts = _write_artifacts(qa_root, route="/")

    with pytest.raises(BrowserObservationError, match="route not found"):
        PlaywrightBrowserObservationAdapter(qa_root, POLICY).observe(artifacts, route="/other")

from __future__ import annotations

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

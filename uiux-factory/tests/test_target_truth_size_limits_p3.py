from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.runtime.flow_os.target_truth import TargetTruthProbe, TargetTruthProbeError


def test_p3_oversized_declared_profile_fails_with_explicit_size_error(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    payload = {
        "domain": "financial-services",
        "mode": "interactive-prototype",
        "padding": "x" * 256,
    }
    (target / ".uiux-profile.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(TargetTruthProbeError) as caught:
        TargetTruthProbe(target, max_source_chars=96).probe()

    message = str(caught.value)
    assert "exceeds size limit (96 chars)" in message
    assert ".uiux-profile.json" in message
    assert "malformed" not in message


def test_p3_in_limit_malformed_profile_still_fails_as_malformed(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / ".uiux-profile.json").write_text('{"domain": "financial-services"', encoding="utf-8")

    with pytest.raises(TargetTruthProbeError, match=r"malformed \.uiux-profile\.json"):
        TargetTruthProbe(target, max_source_chars=256).probe()


def test_p3_oversized_optional_package_metadata_is_ignored_not_misparsed(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    package = {
        "name": "large-package",
        "description": "fintech banking " + ("x" * 256),
    }
    (target / "package.json").write_text(json.dumps(package), encoding="utf-8")

    report = TargetTruthProbe(target, max_source_chars=80).probe()

    assert report.status == "NO_USABLE_TRUTH"
    assert "package.json" not in report.sources
    assert "ignored_oversized_fallback:package.json" in report.diagnostics
    assert not any(item.startswith("ignored_malformed_fallback:package.json") for item in report.diagnostics)


def test_p3_unstructured_readme_remains_bounded_and_usable(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "README.md").write_text(
        "Museum artwork gallery cultural collection discovery experience. " + ("x" * 512),
        encoding="utf-8",
    )

    report = TargetTruthProbe(target, max_source_chars=96).probe()

    assert "README.md" in report.sources
    assert report.fields.get("domain") == "art-culture"
    assert report.status == "PROBED"

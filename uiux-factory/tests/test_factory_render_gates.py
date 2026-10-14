"""Rendered-evidence gate contracts; PNGs are synthetic fixtures, not live renders."""
import copy
import hashlib
import json
import struct
import zlib
from pathlib import Path

import pytest

from core.runtime.flow_os.browser_evidence import PlaywrightBrowserEvidenceAdapter
from core.runtime.flow_os.evidence import evidence_from_tool, gate_evidence_errors


GATES = [{"id": name} for name in ("rendered-qa", "prototype-experience-qa", "truthful-completion")]


def _png(width=320, height=240):
    def chunk(kind, value):
        return struct.pack(">I", len(value)) + kind + value + struct.pack(">I", zlib.crc32(kind + value))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress((b"\0" + b"\xff\xff\xff" * width) * height))
            + chunk(b"IEND", b""))


@pytest.fixture
def rendered(tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    image = artifacts / "home.png"
    image.write_bytes(_png())
    observation = {
        "route": "/", "url": "http://127.0.0.1:4173/", "title": "Home",
        "viewport": {"width": 320, "height": 240}, "screenshot": "home.png",
        "box": {"x": 0, "y": 0, "width": 320, "height": 240},
        "pageErrors": [], "consoleMessages": [], "blockedRequests": [], "failedRequests": [],
        "keyboardFocus": {"status": "PASS", "total": 0, "checked": []},  # synthetic blank image
    }
    (artifacts / "browser-evidence-home.json").write_text(json.dumps(observation), encoding="utf-8")
    record = PlaywrightBrowserEvidenceAdapter(tmp_path, {}).collect(artifacts)[0].to_dict()
    return record, image


def test_file_read_cannot_pass_any_website_qa_gate():
    record = evidence_from_tool("qa", "read_text", {"path": "index.html", "bytes": 100}).to_dict()
    errors = gate_evidence_errors(GATES, "qa", [record], agent="qa")
    assert len(errors) >= 3


@pytest.mark.parametrize('row_filter', [0, 1, 2, 3, 4, 5, 255])
def test_png_gate_checks_scanline_filters_not_only_hash_and_size(row_filter):
    from core.runtime.flow_os.evidence import _valid_png
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))
    raw = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(bytes([row_filter, 0, 0, 0])))
           + chunk(b'IEND', b''))
    assert _valid_png(raw) is (row_filter <= 4)


@pytest.mark.parametrize("case", ["missing_image", "missing_route", "wrong_route", "missing_viewport",
                                 "wrong_viewport", "wrong_hash", "stale", "corrupt_png", "empty", "bad_url"])
def test_render_gate_rejects_invalid_evidence(rendered, case):
    record, image = rendered
    record = copy.deepcopy(record)
    data = record["data"]
    records = [record]
    if case == "missing_image":
        image.unlink()
    elif case == "missing_route":
        data.pop("route")
    elif case == "wrong_route":
        data["route"] = "/wrong-route"
    elif case == "bad_url":
        data["url"] = "http://[bad"
    elif case == "missing_viewport":
        data.pop("viewport")
    elif case == "wrong_viewport":
        data["viewport"] = {"width": 321, "height": 240}
    elif case == "wrong_hash":
        data["screenshot_sha256"] = "0" * 64
    elif case == "stale":
        image.write_bytes(image.read_bytes() + b"changed after capture")
    elif case == "corrupt_png":
        image.write_bytes(b"\x89PNG\r\n\x1a\nnot-a-real-image")
        data["screenshot_sha256"] = hashlib.sha256(image.read_bytes()).hexdigest()
    else:
        records = []
    assert gate_evidence_errors(GATES, "qa", records, agent="qa")


def test_valid_adapter_render_passes_gate(rendered):
    record, _ = rendered
    assert gate_evidence_errors(GATES, "qa", [record], agent="qa") == []


@pytest.mark.parametrize('case', ['missing', 'failed', 'review', 'incomplete', 'hidden'])
def test_keyboard_focus_cannot_be_replaced_by_css_or_partial_report(rendered, case):
    record, image = rendered
    report = {'status': 'PASS', 'total': 1, 'checked': [{'status': 'PASS', 'focused': True, 'hidden': False}]}
    if case == 'missing': report = None
    elif case == 'failed': report['status'] = 'FAIL'
    elif case == 'review': report['status'] = 'NEEDS_REVIEW'
    elif case == 'incomplete': report['checked'] = []
    else: report['checked'][0]['hidden'] = True
    observation = image.parent / record['data']['evidence_json']
    payload = json.loads(observation.read_text())
    payload['keyboardFocus'] = report
    observation.write_text(json.dumps(payload), encoding='utf-8')
    record['data']['keyboard_focus'] = report
    record['data']['evidence_sha256'] = hashlib.sha256(observation.read_bytes()).hexdigest()
    assert gate_evidence_errors([{'id':'keyboard-focus'}], 'qa', [record], 'qa')


def test_explicit_browser_type_also_requires_image(rendered):
    record, image = rendered
    image.unlink()
    assert gate_evidence_errors([{"id": "custom", "evidence_types": ["browser_render"]}],
                                "qa", [record], agent="qa")


@pytest.mark.parametrize("case", ["changed_observation", "bad_compressed_pixels", "provider_origin"])
def test_render_gate_rechecks_provenance_and_encoded_pixels(rendered, case):
    record, image = rendered
    if case == "changed_observation":
        (image.parent / record["data"]["evidence_json"]).write_text("{}", encoding="utf-8")
    elif case == "bad_compressed_pixels":
        raw = _png()
        offset = raw.index(b"IDAT") - 4
        size = struct.unpack(">I", raw[offset:offset + 4])[0]
        payload = b"not-compressed-pixels"
        replacement = struct.pack(">I", len(payload)) + b"IDAT" + payload + struct.pack(">I", zlib.crc32(b"IDAT" + payload))
        image.write_bytes(raw[:offset] + replacement + raw[offset + size + 12:])
        record["data"]["screenshot_sha256"] = hashlib.sha256(image.read_bytes()).hexdigest()
    else:
        record["origin"] = "provider"
    assert gate_evidence_errors(GATES, "qa", [record], agent="qa")


def test_nested_full_page_capture_is_accepted(tmp_path):
    artifacts = tmp_path / "artifacts"
    (artifacts / "screens").mkdir(parents=True)
    (artifacts / "screens" / "home.png").write_bytes(_png(height=480))
    observation = {
        "route": "/?state=open", "url": "http://localhost:4173/?state=open",
        "viewport": {"width": 320, "height": 240}, "screenshot": "screens/home.png",
        "box": {"width": 320, "height": 480},
    }
    (artifacts / "browser-evidence-home.json").write_text(json.dumps(observation), encoding="utf-8")
    record = PlaywrightBrowserEvidenceAdapter(tmp_path, {}).collect(artifacts)[0].to_dict()
    assert gate_evidence_errors(GATES, "qa", [record], agent="qa") == []

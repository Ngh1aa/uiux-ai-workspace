"""Explicit synthetic render fixtures through the shipped capture ingestion adapter."""
import hashlib
import json
import sys
from pathlib import Path

FACTORY = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(FACTORY), str(FACTORY / 'tests')]
from core.runtime.flow_os.browser_evidence import PlaywrightBrowserEvidenceAdapter
from core.runtime.flow_os.evidence import evidence_from_tool
from test_factory_render_gates import _png


def file_proof(stage, tool, path, result=None):
    path = Path(path).resolve()
    raw = path.read_bytes()
    return evidence_from_tool(stage, tool, {**(result or {}), 'path': str(path),
                             'artifact_path': str(path),
                             'artifact_sha256': 'sha256:' + hashlib.sha256(raw).hexdigest()}).to_dict()


def render_fixture(root, tag, stage='qa'):
    artifacts = Path(root) / ('synthetic-browser-' + tag)
    artifacts.mkdir(parents=True, exist_ok=True)
    image = artifacts / 'capture.png'
    image.write_bytes(_png())
    observation = {'route': '/', 'url': 'http://127.0.0.1:4173/', 'title': 'SYNTHETIC contract fixture',
                   'viewport': {'width': 320, 'height': 240}, 'screenshot': image.name,
                   'box': {'x': 0, 'y': 0, 'width': 320, 'height': 240},
                   'pageErrors': [], 'consoleMessages': [], 'blockedRequests': [], 'failedRequests': []}
    (artifacts / 'browser-evidence-capture.json').write_text(json.dumps(observation), encoding='utf-8')
    record = PlaywrightBrowserEvidenceAdapter(root, {}).collect(artifacts)[0].to_dict()
    record['stage_id'] = stage
    return record, image

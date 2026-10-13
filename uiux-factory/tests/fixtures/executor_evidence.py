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


def design_fixture(root, stage, tag='fixture'):
    """Run the canonical checker on explicit synthetic v2 data, never prose PASS.

    Separate immutable proof directories keep later QA/repair from making an
    already accepted design handoff stale. PNGs are integrity fixtures only.
    """
    from core.skills.design_decisions import check_design_file
    from test_design_direction_comparison import v2_fixture, rendered_fixture

    phase = 'rendered' if stage == 'qa' else 'design'
    artifacts = Path(root) / ('design-' + stage) / hashlib.sha256(tag.encode()).hexdigest()[:12]
    artifacts.mkdir(parents=True, exist_ok=True)
    payload = rendered_fixture(artifacts) if phase == 'rendered' else v2_fixture()
    path = artifacts / 'contract.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    result = check_design_file(artifacts, path.name, phase)
    if result['returncode']:
        raise ValueError('Synthetic design fixture failed canonical checker: ' + str(result['errors']))
    return file_proof(stage, 'check_design_decisions', path, result)


def attach_design_fixture(harness, state):
    """Prepare fixture data in the same isolated workspace as its stage."""
    if state.authority != 'read_only':
        harness._ensure_workspace(state)
    root = harness._active_project_root(state)
    state.context.setdefault('evidence_records', []).append(design_fixture(root, state.context['stage_id']))
    harness.checkpoints.save(state.run_id, state.to_dict())


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

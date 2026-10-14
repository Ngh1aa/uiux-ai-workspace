"""Lifecycle guidance must be bounded, honest and shared by both agent paths."""
import hashlib
import json
from pathlib import Path

import pytest

from core.skills.website_delivery import delivery_packet, check_delivery, delivery_template
from core.runtime.flow_os.external_task import build_external_task_manifest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / 'skills_UIUX'


def test_packet_routes_only_active_stage_and_keeps_future_release_separate():
    packet = delivery_packet(SKILLS, 'research', {'intent': 'redesign', 'mode': 'visual-prototype'})
    assert packet['active'] is True
    assert packet['stage'] == 'research'
    assert packet['baseline_rule'].startswith('Existing')
    assert packet['human_validation'] == 'UNKNOWN'
    assert all(item['id'].startswith('research.') for item in packet['deliverables'])
    assert 'release' not in packet['exit_checks']
    assert len(json.dumps(packet)) < 16000
    assert delivery_packet(SKILLS, 'research', {'intent': 'build'})['baseline_rule'].startswith('Confirm')


def test_external_manifest_reuses_lifecycle_owner():
    policy = json.loads((SKILLS / 'runtime/runtime-policy.json').read_text(encoding='utf-8'))
    manifest = build_external_task_manifest(SKILLS, policy, 'Redesign corporate website', 'test/site',
                                           overrides={'intent': 'redesign', 'change_surface': 'REDESIGN'})
    for stage in manifest.stages:
        assert stage['delivery_workflow'] == delivery_packet(SKILLS, stage['id'], manifest.task_contract)


def test_all_resources_resolve_and_unknown_stage_does_not_invent_pipeline():
    for stage in ['research', 'design', 'implementation', 'qa']:
        packet = delivery_packet(SKILLS, stage, {})
        for item in packet['deliverables']:
            for resource in item['resources']:
                assert (SKILLS / resource).is_file(), resource
    assert delivery_packet(SKILLS, 'surprise', {})['active'] is False
    assert delivery_packet(SKILLS, 'implementation', {'change_surface':'MICRO'})['active'] is False


def test_template_is_incomplete_and_cannot_be_mistaken_for_pass(tmp_path):
    report = delivery_template(SKILLS, 'design')
    result = check_delivery(SKILLS, tmp_path, report)
    assert result['status'] == 'BLOCKED'
    assert result['human_validation'] == 'UNKNOWN'
    assert result['aesthetic_quality'] == 'UNKNOWN'


def _filled(tmp_path):
    report = delivery_template(SKILLS, 'research')
    artifact = tmp_path / 'research.md'
    artifact.write_text('Synthetic fixture: a recorded decision and its limitations.', encoding='utf-8')
    for item in report['items']:
        item.update(status='RECORDED', evidence=[{'path': 'research.md',
                    'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}],
                    rationale='Synthetic fixture for file integrity only.')
    return report


def test_current_files_prove_only_record_integrity_not_design_quality(tmp_path):
    result = check_delivery(SKILLS, tmp_path, _filled(tmp_path))
    assert result['status'] == 'RECORDED_CURRENT'
    assert result['human_validation'] == 'UNKNOWN'
    assert result['aesthetic_quality'] == 'UNKNOWN'
    assert result['gate_effect'] == 'none'


@pytest.mark.parametrize('mutation', ['missing', 'stale', 'escape', 'empty', 'duplicate', 'unknown_status', 'invented_item'])
def test_lifecycle_records_fail_closed(tmp_path, mutation):
    report = _filled(tmp_path)
    if mutation == 'missing': report['items'].pop()
    if mutation == 'stale': (tmp_path / 'research.md').write_text('Changed', encoding='utf-8')
    if mutation == 'escape': report['items'][0]['evidence'][0]['path'] = '../research.md'
    if mutation == 'empty': report['items'][0]['evidence'] = []
    if mutation == 'duplicate': report['items'].append(report['items'][0])
    if mutation == 'unknown_status': report['items'][0]['status'] = 'PASS'
    if mutation == 'invented_item': report['items'][0]['id'] = 'research.fake'
    assert check_delivery(SKILLS, tmp_path, report)['status'] == 'BLOCKED'


def test_deferred_and_na_work_stays_visible_and_needs_reason(tmp_path):
    report = _filled(tmp_path)
    report['items'][0].update(status='DEFERRED', evidence=[], rationale='')
    assert check_delivery(SKILLS, tmp_path, report)['status'] == 'BLOCKED'
    report['items'][0].update(status='NA_JUSTIFIED', rationale='Prototype has no recruitment budget.')
    # The checker records this claim; only a reviewer may accept its relevance.
    assert check_delivery(SKILLS, tmp_path, report)['status'] == 'NEEDS_REVIEW'


def test_context_change_invalidates_record(tmp_path):
    report = _filled(tmp_path)
    report['context'] = {'goal': 'A completely different product'}
    assert check_delivery(SKILLS, tmp_path, report)['status'] == 'BLOCKED'


def test_managed_provider_receives_the_same_active_stage_card(tmp_path):
    from test_provider_context_budget_a8_3 import _research_run
    _, _, managed, state, runner = _research_run(tmp_path)
    request = runner._request(managed, state, [])
    assert request.task_context['delivery_workflow'] == delivery_packet(SKILLS, managed.active_stage, managed.task_context)
    assert request.task_context['delivery_workflow']['stage'] == 'research'

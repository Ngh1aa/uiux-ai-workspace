"""A browser presentation must never silently replace a requested native build."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.external_task import build_external_task_manifest
from core.runtime.flow_os.flow import validate_flow_document
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.task_context import GoalInterpreter
from core.skills.website_delivery import delivery_packet

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / 'skills_UIUX'
POLICY = json.loads((SKILLS / 'runtime/runtime-policy.json').read_text(encoding='utf-8'))


def manifest(goal, **kwargs):
    return build_external_task_manifest(SKILLS, POLICY, goal, 'example/app', **kwargs).to_dict()


@pytest.mark.parametrize('goal', [
    'Design mobile app iOS Android and build a browser prototype',
    'Thiết kế mobile app và tạo prototype chạy trên trình duyệt để khách bấm thử',
    'Thiết kế app iOS Android có link demo GitHub Pages',
    'Build a mobile app browser preview',
    'Design an Expo mobile app with an interactive browser prototype',
    'Thiết kế ứng dụng di động và prototype trên web',
])
def test_browser_request_routes_implementation_and_browser_qa_without_native_claim(goal):
    result = manifest(goal)
    assert result['task_contract']['platform_family'] == 'mobile_app'
    assert result['task_contract']['requested_output'] == 'browser-prototype'
    assert result['resolved_flow']['id'] == 'mobile-web-preview'
    assert [stage['id'] for stage in result['stages']] == ['research', 'design', 'implementation', 'qa']
    implementation, qa = result['stages'][2:]
    assert {'mobile-web-preview', 'frontend-implementation'}.issubset(implementation['skills'])
    assert 'web-quality-and-performance' in qa['skills']
    assert {'browser_render', 'validator_result'} == set(qa['gates'][0]['evidence_types'])
    assert result['stages'][1]['design_workflow']['active']
    assert result['stages'][1]['design_workflow']['required_check_phases'] == ['design']
    assert qa['design_workflow']['required_check_phases'] == ['rendered']
    assert result['authority'] == 'branch_write'
    assert result['evidence_boundary']['mobile_completion_scope'] == 'browser_prototype_and_client_handoff'
    assert result['evidence_boundary']['native_runtime_qa_available'] is False
    assert result['evidence_boundary']['native_implementation_available'] is False
    assert result['evidence_boundary']['publication_requires_separate_release_authority'] is True
    assert result['status'] == 'READY_FOR_EXTERNAL_COLLABORATOR'


@pytest.mark.parametrize('goal', [
    'Design only mobile app iOS Android; browser prototype later',
    'Design mobile app Figma prototype',
    'Design mobile app Figma prototype with a demo link',
    'Design mobile app; do not build a browser prototype',
    'Design mobile app, reference https://example.com/browser-prototype',
])
def test_design_only_negative_and_reference_requests_do_not_add_browser_implementation(goal):
    result = manifest(goal)
    assert result['resolved_flow']['id'] == 'mobile-app-design'
    assert result['task_contract']['requested_output'] == 'design'


@pytest.mark.parametrize('goal', [
    'Design and implement a native iOS app with a browser prototype',
    'Implement a SwiftUI app and create a browser prototype',
    'Build a native Android app and web preview',
    'Build APK for mobile app and a browser prototype',
    'Implement a mobile app and create a browser prototype',
])
def test_browser_preview_does_not_erase_a_native_implementation_requirement(goal):
    with pytest.raises(ValueError, match='no applicable flow'):
        manifest(goal)


def test_explicit_preview_output_keeps_target_stack_and_output_provenance(tmp_path):
    (tmp_path / '.uiux-profile.json').write_text(json.dumps({
        'platform_family': 'mobile_app', 'target_platforms': ['ios'],
        'implementation_stack': 'swiftui', 'requested_output': 'browser-prototype', 'authority': 'release',
    }), encoding='utf-8')
    design = manifest('Design the existing app', target_root=tmp_path)
    assert design['resolved_flow']['id'] == 'mobile-app-design'
    result = manifest('Design the existing app', target_root=tmp_path,
                      overrides={'requested_output': 'browser-prototype'})
    assert result['resolved_flow']['id'] == 'mobile-web-preview'
    assert result['task_contract']['implementation_stack'] == 'swiftui'
    assert result['task_contract']['routing_provenance']['field_sources']['requested_output'] == 'explicit_override'
    assert result['authority'] == 'branch_write'
    assert 'ios-app-design' in result['stages'][1]['skills']


def test_read_only_preview_planning_cannot_write_branch_scoped_artifacts(tmp_path):
    result = manifest('Design mobile app browser prototype', authority='read_only')
    assert result['resolved_flow']['id'] == 'mobile-web-preview'
    assert result['task_contract']['intent'] == 'build'
    assert result['authority'] == 'read_only'
    harness = ProviderNeutralAgentHarness(SKILLS, tmp_path)
    state = harness.create_run(result['task'], 'implementation', authority=result['authority'],
                          selected_skills=['mobile-web-preview'], platform_family='mobile_app')
    finished = harness.execute_plan(state, [{'tool': 'write_artifact', 'args': {
        'path': 'docs/uiux/preview-review.md', 'content': 'Must not be written'}}])
    assert finished.state == 'BLOCKED'
    assert not (tmp_path / 'docs/uiux/preview-review.md').exists()


def test_explicit_read_only_website_intent_cannot_be_overridden_into_implementation():
    result = manifest('Audit the corporate website, read-only', authority='release', overrides={'intent': 'fix'})
    assert result['resolved_flow']['id'] == 'audit-review'
    assert result['task_contract']['intent'] == 'audit'
    assert all(stage['agent'] != 'implementation' for stage in result['stages'])


def test_preview_work_cards_do_not_leak_into_design_or_website_lifecycle():
    context = GoalInterpreter().interpret('Design mobile app browser prototype').to_context()
    implementation = delivery_packet(SKILLS, 'implementation', context)
    qa = delivery_packet(SKILLS, 'qa', context)
    assert implementation['active'] and qa['active']
    assert implementation['owner'] == qa['owner'] == 'mobile-app-design'
    assert any(item['id'] == 'qa.mobile_client_handoff' for item in qa['deliverables'])
    assert not delivery_packet(SKILLS, 'implementation', {**context, 'requested_output': 'design'})['active']
    web = delivery_packet(SKILLS, 'implementation', {**context, 'platform_family': 'web'})
    assert web['owner'] == 'website-delivery-pipeline'
    for packet in [implementation, qa]:
        for item in packet['deliverables']:
            assert all((SKILLS / path).is_file() for path in item['resources'])


def test_managed_preview_and_external_preview_share_the_canonical_flow(tmp_path):
    goal = 'Design mobile app iOS browser prototype'
    harness = ProviderNeutralAgentHarness(SKILLS, tmp_path)
    managed = ManagedFlowController(harness).start_from_goal(goal, authority='branch_write')
    assert managed.flow.id == manifest(goal)['resolved_flow']['id'] == 'mobile-web-preview'
    manager = harness.resume(managed.manager_run_id)
    assert 'website-delivery-pipeline' not in manager.context['selected_skills']


def test_managed_read_only_preview_keeps_planning_intent_and_caller_grant(tmp_path):
    harness = ProviderNeutralAgentHarness(SKILLS, tmp_path)
    controller = ManagedFlowController(harness)
    goal = 'Design mobile app iOS browser prototype'
    context = GoalInterpreter().interpret(goal).to_context()
    managed = controller.start(goal, context, authority='read_only')
    assert managed.flow.id == 'mobile-web-preview'
    assert managed.task_context['intent'] == context['intent'] == 'build'
    assert managed.task_context['effective_authority'] == 'read_only'
    assert managed.authority == 'read_only'


def test_preview_cli_and_flow_json_schema_accept_the_new_output(tmp_path):
    output = tmp_path / 'packet.json'
    process = subprocess.run([
        sys.executable, '-B', str(SKILLS / 'scripts/prepare-external-task.py'),
        '--repository', 'example/app', '--task', 'Design mobile app iOS',
        '--platform-family', 'mobile_app', '--requested-output', 'browser-prototype',
        '--output', str(output),
    ], capture_output=True, text=True, encoding='utf-8')
    assert process.returncode == 0, process.stderr
    assert json.loads(output.read_text(encoding='utf-8'))['resolved_flow']['id'] == 'mobile-web-preview'
    flow = json.loads((SKILLS / 'flows/mobile-web-preview.json').read_text(encoding='utf-8'))
    assert not validate_flow_document(flow)
    schema = json.loads((SKILLS / 'schemas/flow.schema.json').read_text(encoding='utf-8'))
    assert 'browser-prototype' in schema['properties']['match']['properties']['requested_outputs']['items']['enum']


def test_actual_mobile_example_fits_the_project_profile_schema_and_routes_preview():
    target = SKILLS / 'examples/projects/mobile-appointment'
    profile = json.loads((target / '.uiux-profile.json').read_text(encoding='utf-8'))
    schema = json.loads((SKILLS / 'schemas/uiux-profile.schema.json').read_text(encoding='utf-8'))
    assert set(schema['required']).issubset(profile)
    assert set(profile).issubset(schema['properties'])
    assert profile['platform_family'] in schema['properties']['platform_family']['enum']
    assert profile['implementation_stack'] in schema['properties']['implementation_stack']['enum']
    assert all(item in schema['properties']['target_platforms']['items']['enum'] for item in profile['target_platforms'])
    result = manifest('Design current app', target_root=target, overrides={'requested_output': 'browser-prototype'})
    assert result['resolved_flow']['id'] == 'mobile-web-preview'
    assert result['task_contract']['target_truth']['status'] == 'PROBED'

"""Mobile knowledge/routing is additive; design records never prove a native app."""
import hashlib
import json
from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.external_task import build_external_task_manifest
from core.runtime.flow_os.flow import FlowPlanner, FlowResolver, validate_flow_document
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.target_truth import TargetTruthProbe, build_truth_aware_context
from core.runtime.flow_os.task_context import GoalInterpreter
from core.skills.website_delivery import check_delivery, delivery_packet, delivery_template

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / 'skills_UIUX'
POLICY = json.loads((SKILLS / 'runtime/runtime-policy.json').read_text(encoding='utf-8'))


def manifest(goal, **kwargs):
    return build_external_task_manifest(SKILLS, POLICY, goal, 'example/app', **kwargs).to_dict()


@pytest.mark.parametrize('goal,platforms,stack', [
    ('Thiết kế UI UX app mobile iOS Android; chỉ thiết kế', ['ios', 'android'], 'unknown'),
    ('Design a SwiftUI app prototype', ['ios'], 'swiftui'),
    ('Design a Jetpack Compose app prototype', ['android'], 'jetpack-compose'),
    ('Design an Expo mobile app for iOS and Android', ['ios', 'android'], 'expo'),
    ('Thiết kế giao diện cho iOS', ['ios'], 'unknown'),
    ('Design a Flutter app for Android', ['android'], 'flutter'),
])
def test_mobile_design_routes_only_platform_owners(goal, platforms, stack):
    result = manifest(goal)
    context = result['task_contract']
    assert context['platform_family'] == 'mobile_app'
    assert context['target_platforms'] == platforms
    assert context['implementation_stack'] == stack
    assert context['requested_output'] == 'design'
    assert result['resolved_flow']['id'] == 'mobile-app-design'
    assert [stage['id'] for stage in result['stages']] == ['research', 'design', 'qa']
    design = next(stage for stage in result['stages'] if stage['id'] == 'design')
    assert ('ios-app-design' in design['skills']) == ('ios' in platforms)
    assert ('android-app-design' in design['skills']) == ('android' in platforms)
    forbidden = {'website-delivery-pipeline', 'frontend-implementation', 'web-ui-code-review',
                 'responsive-and-device-strategy', 'web-quality-and-performance', 'corporate-website'}
    for stage in result['stages']:
        assert not forbidden.intersection(stage['skills'])
        assert stage['delivery_workflow'] == delivery_packet(SKILLS, stage['id'], context)
        assert not stage['design_workflow']['active']
    assert result['status'] == 'READY_FOR_EXTERNAL_COLLABORATOR'
    assert result['evidence_boundary']['native_implementation_available'] is False
    assert result['evidence_boundary']['native_runtime_qa_available'] is False


@pytest.mark.parametrize('goal,flow', [
    ('Fix the mobile navigation', 'existing-ui-improvement'),
    ('Redesign the whole corporate website', 'professional-website-redesign'),
    ('Create a landing page for a fintech platform', 'page-ui-work'),
    ('Thiết kế website responsive trên điện thoại', 'professional-website-redesign'),
    ('Design a responsive website for Android Chrome', 'professional-website-redesign'),
    ('Redesign portfolio website', 'portfolio-career-system'),
    ('Fix button padding', 'micro-ui-change'),
    ('Audit current website; do not design a mobile app', 'audit-review'),
])
def test_near_miss_web_requests_keep_existing_routing(goal, flow):
    result = manifest(goal)
    assert result['task_contract']['platform_family'] == 'web'
    assert result['resolved_flow']['id'] == flow
    assert all('mobile-app-design' not in stage['skills'] for stage in result['stages'])


def test_reference_url_does_not_choose_mobile_platform():
    result = manifest('Redesign corporate website; reference https://example.com/ios-app')
    assert result['task_contract']['platform_family'] == 'web'
    result = manifest('Redesign corporate website, reference a SwiftUI iOS app for typography')
    assert result['task_contract']['platform_family'] == 'web'


@pytest.mark.parametrize('goal', ['Implement a SwiftUI iOS app', 'Build app mobile Android',
                                 'Design and implement an Expo mobile app',
                                 'Build a mobile application', 'Design and build an Expo app'])
def test_native_implementation_cannot_fall_back_to_browser_or_design_flow(goal):
    with pytest.raises(ValueError, match='no applicable flow'):
        manifest(goal)


def test_native_review_is_read_only_even_with_larger_caller_grant():
    result = manifest('Chỉ audit app mobile iOS Android, không sửa code', authority='release')
    assert result['authority'] == 'read_only'
    assert result['resolved_flow']['id'] == 'mobile-app-audit'
    assert all(stage['agent'] != 'implementation' for stage in result['stages'])


def test_mobile_research_reuses_existing_evidence_owner_without_inventing_sessions():
    result = manifest('Design mobile app iOS with user research and user validation')
    research = result['stages'][0]
    assert 'research-evidence-pipeline' in research['skills']
    assert result['research_packet']['state'] == 'PLANNED_VALIDATION_UNTIL_REAL_EVIDENCE_EXISTS'


def test_structured_platform_truth_keeps_output_and_authority_with_caller(tmp_path):
    (tmp_path / '.uiux-profile.json').write_text(json.dumps({
        'platform_family': 'mobile_app', 'target_platforms': ['ios'], 'implementation_stack': 'swiftui',
        'requested_output': 'application', 'authority': 'release', 'mode': 'interactive-prototype',
    }), encoding='utf-8')
    result = manifest('Thiết kế UX hiện tại', target_root=tmp_path)
    assert result['resolved_flow']['id'] == 'mobile-app-design'
    assert result['task_contract']['requested_output'] == 'design'
    assert result['authority'] == 'branch_write'
    assert result['task_contract']['routing_provenance']['field_sources']['platform_family'] == 'target_project_truth'
    overridden = manifest('Thiết kế UX hiện tại', target_root=tmp_path,
                          overrides={'platform_family': 'web', 'target_platforms': ['android']})
    assert overridden['task_contract']['platform_family'] == 'web'
    assert overridden['resolved_flow']['id'] != 'mobile-app-design'


def test_react_native_dependency_probe_is_bounded_and_does_not_execute_scripts(tmp_path):
    (tmp_path / 'package.json').write_text(json.dumps({
        'dependencies': {'expo': '*', 'react-native': '*'},
        'scripts': {'postinstall': 'DO_NOT_EXECUTE'}, 'authority': 'release',
    }), encoding='utf-8')
    result = manifest('Thiết kế giao diện hiện tại', target_root=tmp_path)
    assert result['task_contract']['platform_family'] == 'mobile_app'
    assert result['task_contract']['implementation_stack'] == 'expo'
    assert result['authority'] == 'branch_write'
    assert result['resolved_flow']['id'] == 'mobile-app-design'


def test_declared_web_profile_beats_native_dependency_fallback(tmp_path):
    (tmp_path / '.uiux-profile.json').write_text('{"platform_family":"web"}', encoding='utf-8')
    (tmp_path / 'package.json').write_text('{"dependencies":{"react-native":"*"}}', encoding='utf-8')
    assert TargetTruthProbe(tmp_path).probe().fields['platform_family'] == 'web'


def test_invalid_dependency_marker_does_not_claim_native_identity(tmp_path):
    (tmp_path / 'package.json').write_text('{"dependencies":{"react-native":null}}', encoding='utf-8')
    assert 'platform_family' not in TargetTruthProbe(tmp_path).probe().fields


def test_platform_override_normalizes_duplicate_targets():
    result = manifest('Design mobile app', overrides={'target_platforms': ['ios', 'ios']})
    assert result['task_contract']['target_platforms'] == ['ios']


@pytest.mark.parametrize('override', [
    {'platform_family': 'native-ish'}, {'target_platforms': ['ios', 'windows']},
    {'implementation_stack': 'random-framework'}, {'requested_output': 'release'},
])
def test_unknown_mobile_overrides_fail_closed(override):
    with pytest.raises(ValueError):
        build_truth_aware_context('Design mobile app', target_root=None, overrides=override)


@pytest.mark.parametrize('key,value', [('platform_families', []), ('platform_families', ['arbitrary']),
                                      ('requested_outputs', ['release'])])
def test_flow_schema_and_runtime_reject_invalid_platform_matches(key, value):
    flow = json.loads((SKILLS / 'flows/mobile-app-design.json').read_text(encoding='utf-8'))
    flow['match'][key] = value
    assert validate_flow_document(flow)


def test_current_web_and_mobile_manifests_fit_portable_schema_surface():
    schema = json.loads((SKILLS / 'schemas/external-task-manifest.schema.json').read_text(encoding='utf-8'))
    for result in [manifest('Redesign corporate website'), manifest('Design mobile app iOS')]:
        assert result['schema_version'] in schema['properties']['schema_version']['enum']
        assert set(schema['required']).issubset(result)
        assert set(result).issubset(schema['properties'])


def test_mobile_lifecycle_hashes_record_files_not_runtime_quality(tmp_path):
    context = GoalInterpreter().interpret('Design mobile app iOS').to_context()
    report = delivery_template(SKILLS, 'design', context)
    assert check_delivery(SKILLS, tmp_path, report)['status'] == 'BLOCKED'
    artifact = tmp_path / 'design.md'
    artifact.write_text('SYNTHETIC file coverage fixture, not reviewed design or native runtime.', encoding='utf-8')
    for item in report['items']:
        item.update(status='RECORDED', evidence=[{'path': artifact.name,
                    'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}])
    result = check_delivery(SKILLS, tmp_path, report)
    assert result['status'] == 'RECORDED_CURRENT'
    assert result['gate_effect'] == 'none'
    assert result['human_validation'] == result['aesthetic_quality'] == 'UNKNOWN'
    artifact.write_text('Changed after receipt', encoding='utf-8')
    assert check_delivery(SKILLS, tmp_path, report)['status'] == 'BLOCKED'
    assert not delivery_packet(SKILLS, 'implementation', context)['active']


def test_mobile_resources_and_immutable_reference_rights_are_resolvable():
    registry = json.loads((SKILLS / 'mobile-app-design/data/sources.json').read_text(encoding='utf-8'))
    assert len({source['id'] for source in registry['sources']}) == len(registry['sources'])
    for source in registry['sources']:
        assert source['integration_mode'] in {'link-only', 'reference'}
        assert source['license'] and source['checked_at'] and source['verification']
        if source['integration_mode'] == 'reference':
            assert len(source['revision']) == 40 and source['license_url']
    for stage in ['research', 'design', 'qa']:
        packet = delivery_packet(SKILLS, stage, {'platform_family': 'mobile_app'})
        assert packet['owner'] == 'mobile-app-design'
        for item in packet['deliverables']:
            for resource in item['resources']:
                assert (SKILLS / resource).is_file()


def test_managed_and_external_share_mobile_flow_without_web_manager_default(tmp_path):
    goal = 'Review mobile app iOS Android'
    harness = ProviderNeutralAgentHarness(SKILLS, tmp_path)
    managed = ManagedFlowController(harness).start_from_goal(goal, authority='read_only')
    external = manifest(goal, authority='read_only')
    assert managed.flow.id == external['resolved_flow']['id'] == 'mobile-app-audit'
    manager = harness.resume(managed.manager_run_id)
    assert 'mobile-app-design' in manager.context['selected_skills']
    assert 'website-delivery-pipeline' not in manager.context['selected_skills']


def test_mobile_replanning_preserves_authority_and_mandatory_skills():
    context = GoalInterpreter().interpret('Design mobile app iOS').to_context()
    planner = FlowPlanner(SKILLS, POLICY)
    flow = planner.plan(context)
    decision = planner.replanner.decide(flow, 'GATE_FAIL', {**context, 'current_stage': 'qa'}, 0)
    revised = planner.apply_replan(flow, decision)
    assert revised.id == flow.id
    assert revised.revision == flow.revision + 1
    assert 'ios-app-design' in next(stage for stage in revised.stages if stage.id == 'design').skills

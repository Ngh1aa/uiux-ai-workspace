import json
from pathlib import Path

import pytest

from core.runtime.flow_os.external_task import build_external_task_manifest
from core.runtime.flow_os.task_context import GoalInterpreter
from core.skills.research_workflow import research_workflow_packet

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / 'skills_UIUX'
POLICY = json.loads((SKILLS / 'runtime/runtime-policy.json').read_text(encoding='utf-8'))


def packet(goal, **overrides):
    return build_external_task_manifest(
        SKILLS, POLICY, goal, 'example/test-project', authority='branch_write',
        overrides={'intent': 'research', 'website_type': 'saas', 'domain': 'enterprise-software',
                   'validation_lane': 'prototype', 'change_surface': 'FOCUSED', **overrides},
    ).to_dict()


@pytest.mark.parametrize('goal', [
    'Research buyers and compare website references before designing a SaaS marketing website.',
    'Nghiên cứu trước khi thiết kế website dịch vụ.',
    'Nghiên cứu người mua và reference giao diện.',
    'Research before design: dashboard operator decisions.',
    'Pre-design research for ecommerce product detail.',
])
def test_bilingual_research_routes_without_user_study_or_mutation(goal):
    result = packet(goal)
    assert result['schema_version'] == '1.3'
    assert result['resolved_flow']['id'] == 'audit-review'
    assert result['authority'] == 'read_only'
    assert [s['id'] for s in result['stages']] == ['research', 'qa']
    stage = result['stages'][0]
    assert {'product-discovery', 'design-reference-research-and-benchmark',
            'research-synthesis-and-insight-management'} <= set(stage['skills'])
    workflow = stage['research_workflow']
    assert workflow['active'] and len(workflow['resources']) == 3
    for path in workflow['resources'] + [workflow['evidence_schema']]:
        assert (ROOT / path).is_file()
    assert not result['research_packet']['required']
    assert workflow['human_validation'] == 'UNKNOWN'
    assert not result['stages'][1]['research_workflow']['active']


@pytest.mark.parametrize('goal', [
    'Research API reference documentation for a Python library.',
    'Audit the existing mobile navigation for keyboard bugs.',
    'Fix the button spacing, preserve the current style.',
    'Do not research buyers; audit the keyboard navigation only.',
    'Không nghiên cứu trước khi thiết kế; chỉ kiểm tra lỗi console.',
])
def test_technical_small_and_negated_tasks_do_not_trigger_design_research(goal):
    assert 'pre-design-research' not in GoalInterpreter().interpret(goal).features
    result = packet(goal)
    assert not result['stages'][0]['research_workflow']['active']
    assert 'design-reference-research-and-benchmark' not in result['stages'][0]['skills']


def test_explicit_feature_and_human_packet_are_independent():
    desk = packet('Inspect the current experience', features=['pre-design-research'])
    human = packet('Inspect the current experience', features=['pre-design-research', 'user-validation'])
    assert desk['stages'][0]['research_workflow']['active']
    assert not desk['research_packet']['required']
    assert human['research_packet']['required']
    assert human['research_packet']['state'] == 'PLANNED_VALIDATION_UNTIL_REAL_EVIDENCE_EXISTS'
    assert human['research_packet']['templates']
    assert human['authority'] == desk['authority'] == 'read_only'


def test_existing_redesign_research_activates_by_routed_owner_not_new_feature():
    result = packet('Redesign the corporate website', intent='redesign',
                    website_type='corporate', change_surface='REDESIGN')
    assert result['resolved_flow']['id'] == 'professional-website-redesign'
    assert result['stages'][0]['research_workflow']['active']
    assert all(not s['research_workflow']['active'] for s in result['stages'][1:])


def test_resource_loading_is_bounded_by_activated_owner():
    context = {'features': ['pre-design-research']}
    initial = research_workflow_packet(context, 'research', [])
    assert initial['active'] and initial['resources'] == []
    active = research_workflow_packet(context, 'research', ['product-discovery'])
    assert len(active['resources']) == 1
    assert not research_workflow_packet(context, 'implementation', ['product-discovery'])['active']


def test_ledger_retains_desk_class_without_requiring_fake_session():
    schema = json.loads((SKILLS / 'research-evidence-pipeline/templates/evidence-ledger.schema.json').read_text())
    record = {'evidence_id': 'E1', 'evidence_class': 'DESK_EVIDENCE',
              'observation': 'The fixture brief requires comparing service exclusions.',
              'decision_ids': ['D1'], 'limitations': 'Synthetic fixture, no human observation.',
              'source_ref': 'fixture://corporate/C0', 'observed_at': '2026-10-09'}
    assert set(schema['required']) <= record.keys() <= schema['properties'].keys()
    assert record['evidence_class'] in schema['properties']['evidence_class']['enum']
    assert 'session_id' not in schema['required']
    assert 'session_id' not in record


def test_managed_provider_gets_research_resources_and_shared_budget(tmp_path):
    from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
    from core.runtime.flow_os.managed import ManagedFlowController
    from core.runtime.flow_os.provider import ScriptedProvider
    from core.runtime.flow_os.provider_runner import ProviderManagedRunner, ProviderContextBudgetError
    project = tmp_path / 'project'
    project.mkdir()
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal('Research buyers and website references', authority='read_only',
                                      overrides={'intent': 'research', 'website_type': 'saas'})
    state = manager.start_stage(managed)
    runner = ProviderManagedRunner(manager, ScriptedProvider([]))
    first = runner._request(managed, state, [])
    assert first.task_context['research_workflow']['active']
    assert not any('reference-anatomy-method.md' in d['path'] for d in first.source_context)
    for skill in ['product-discovery', 'design-reference-research-and-benchmark', 'research-synthesis-and-insight-management']:
        if skill not in managed.flow.stages[0].mandatory_skills:
            assert runner._activate_skill_context(managed, state, skill=skill)['accepted']
    request = runner._request(managed, state, [])
    for path in request.task_context['research_workflow']['resources']:
        assert any(Path(d['path']).as_posix().endswith(path) for d in request.source_context)
    chars = sum(len(d['content']) for d in request.source_context + request.skill_context)
    assert chars == request.task_context['provider_context_budget']['loaded_document_chars']
    harness.policy_doc['provider_context']['max_document_chars_per_request'] = chars - 1
    with pytest.raises(ProviderContextBudgetError):
        runner._request(managed, state, [])

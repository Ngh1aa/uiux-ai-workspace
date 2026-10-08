import json
from pathlib import Path
import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.provider import ScriptedProvider
from core.runtime.flow_os.provider_runner import ProviderManagedRunner, ProviderContextBudgetError

SKILLS = Path(__file__).resolve().parents[2]/'skills_UIUX'


def runner_fixture(tmp_path):
    project = tmp_path/'project'; project.mkdir()
    harness = ProviderNeutralAgentHarness(SKILLS,project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal('Redesign the Home page',authority='branch_write',overrides={'intent':'redesign','change_surface':'PAGE','website_type':'corporate','domain':'industrial-services','product_archetype':'b2b-service-operations'})
    managed.active_stage = 'design'
    stage = manager.start_stage(managed)
    runner = ProviderManagedRunner(manager,ScriptedProvider([]))
    return harness,manager,managed,stage,runner


def test_provider_receives_bounded_actual_knowledge_not_only_a_skill_name(tmp_path):
    harness,manager,managed,stage,runner = runner_fixture(tmp_path)
    request = runner._request(managed,stage,[])
    assert request.task_context['design_workflow']['decision_contract_required'] is True
    knowledge = next(item for item in request.source_context if item['path'].endswith('design-knowledge.json'))
    data = json.loads(knowledge['content'])
    assert data['domain_profiles'][0]['id'] == 'industrial-service-operations'
    assert data['role_card'] is None
    assert len(data['available_roles']) == 6
    assert {'retrieve_design_knowledge','check_design_decisions','prepare_design_comparison','evaluate_design_comparison'} <= {tool['name'] for tool in request.tools}
    assert data['reference_anatomy']['cards'] == []
    assert request.task_context['design_workflow']['contract_version'] == '2.0'
    assert request.task_context['provider_context_budget']['loaded_document_chars'] == sum(len(item['content']) for item in request.skill_context+request.source_context)
    result = runner._execute_one(managed,stage,'retrieve_design_knowledge',{'page_role':'rfq'})
    assert result['page_role'] == 'conversion'
    assert result['adopted'] is False


def test_knowledge_cannot_escape_document_budget_or_override_identity(tmp_path):
    harness,manager,managed,stage,runner = runner_fixture(tmp_path)
    baseline = runner._request(managed,stage,[])
    harness.policy_doc['provider_context']['max_document_chars_per_request'] = baseline.task_context['provider_context_budget']['loaded_document_chars']-1
    with pytest.raises(ProviderContextBudgetError):
        runner._request(managed,stage,[])
    with pytest.raises(ValueError,match='routing-owned'):
        runner._execute_one(managed,stage,'retrieve_design_knowledge',{'page_role':'home','domain':'consumer-gardening'})


def test_research_does_not_eager_load_design_dataset_or_tools(tmp_path):
    harness,manager,managed,stage,runner = runner_fixture(tmp_path)
    managed.active_stage='research'
    state = manager.start_stage(managed)
    request = runner._request(managed,state,[])
    assert not request.task_context['design_workflow']['active']
    assert 'retrieve_design_knowledge' not in {tool['name'] for tool in request.tools}
    assert 'prepare_design_comparison' not in {tool['name'] for tool in request.tools}
    assert 'evaluate_design_comparison' not in {tool['name'] for tool in request.tools}
    assert not any(item['path'].endswith('design-knowledge.json') for item in request.source_context)
    with pytest.raises(ValueError,match='active routed'):
        runner._execute_one(managed,state,'retrieve_design_knowledge',{'page_role':'home'})
    with pytest.raises(ValueError,match='active routed'):
        runner._execute_one(managed,state,'prepare_design_comparison',{'route':'/'})


def test_provider_comparison_reads_contract_and_cannot_override_identity(tmp_path):
    from core.skills.design_comparison import digest
    from test_design_direction_comparison import v2_fixture
    harness,manager,managed,stage,runner = runner_fixture(tmp_path)
    payload = v2_fixture()
    harness.project_root.joinpath('direction.json').write_text(json.dumps(payload),encoding='utf-8')
    plan = runner._execute_one(managed,stage,'prepare_design_comparison',{'path':'direction.json','route':'/','seed':27})
    assert plan['status']=='PLANNED_VALIDATION'
    harness.project_root.joinpath('plan.json').write_text(json.dumps(plan),encoding='utf-8')
    harness.project_root.joinpath('observations.json').write_text(json.dumps({'schema_version':'1.0','plan_sha256':digest(plan),'reviews':[]}),encoding='utf-8')
    result = runner._execute_one(managed,stage,'evaluate_design_comparison',{'path':'direction.json','plan':'plan.json','observations':'observations.json'})
    assert result['status']=='PLANNED_VALIDATION' and result['human_preference']=='UNKNOWN'
    with pytest.raises(ValueError,match='unsupported'):
        runner._execute_one(managed,stage,'prepare_design_comparison',{'path':'direction.json','route':'/','domain':'industrial-services'})
    with pytest.raises(ValueError):
        runner._execute_one(managed,stage,'prepare_design_comparison',{'path':'../direction.json','route':'/'})

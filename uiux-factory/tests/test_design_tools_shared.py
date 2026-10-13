import json
from pathlib import Path
import subprocess
import sys
import pytest

from core.runtime.flow_os.external_task import build_external_task_manifest
from core.skills.design_knowledge import retrieve_design_knowledge

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / 'skills_UIUX'
QUERY = SKILLS / 'design-intelligence-retrieval/scripts/query.py'


def test_structured_industrial_query_returns_page_job_knowledge():
    result = subprocess.run([sys.executable, '-B', str(QUERY), 'plant electrical control engineering', '--design-system', '--json', '--website-type', 'corporate', '--project-domain', 'industrial-services', '--product-archetype', 'b2b-service-operations', '--page-role', 'service-detail'], capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    knowledge = payload['factory_design_knowledge']
    assert knowledge['domain_profiles'][0]['id'] == 'industrial-service-operations'
    assert knowledge['page_role'] == 'offering'
    assert len(knowledge['role_card']['compositions']) == 2
    assert knowledge['adopted'] is False
    assert knowledge['aesthetic_quality'] == 'UNKNOWN'
    assert payload['design_system']['source_identities']['product'] == 'Plant Care Tracker'
    assert payload['factory_retrieval_review']['context_fit'] == 'REQUIRES_REVIEW_AGAINST_STRUCTURED_IDENTITY'


def test_external_packet_has_active_design_workflow_only():
    policy = json.loads((SKILLS/'runtime/runtime-policy.json').read_text(encoding='utf-8'))
    packet = build_external_task_manifest(SKILLS, policy, 'Redesign a corporate website', 'owner/example', overrides={'intent':'redesign','change_surface':'REDESIGN','website_type':'corporate','domain':'industrial-services','product_archetype':'b2b-service-operations'})
    stages = packet.to_dict()['stages']
    design = next(stage for stage in stages if stage['id'] == 'design')
    assert design['design_workflow']['decision_contract_required'] is True
    assert design['design_workflow']['lookup_tool'] == 'retrieve_design_knowledge'
    research = next(stage for stage in stages if stage['id'] == 'research')
    assert research['design_workflow']['active'] is False
    assert 'design_contract_check' in {kind for gate in design['gates'] for kind in gate.get('evidence_types', [])}


def test_unknown_domain_does_not_inherit_an_industrial_preset():
    card = retrieve_design_knowledge(SKILLS, {'website_type':'corporate','domain':'marine-biology'}, 'home')
    assert card['domain_status'] == 'NO_CURATED_DOMAIN_PROFILE'
    assert card['domain_profiles'] == []
    assert card['role_card']['decision_object']
    assert card['numeric_status'] == 'PROFESSIONAL_HYPOTHESIS'


def test_enterprise_governance_selects_software_objects_not_hardware():
    context = {'website_type':'saas','domain':'enterprise-software','product_archetype':'b2b-service-operations'}
    card = retrieve_design_knowledge(SKILLS, context, 'home')
    assert card['domain_status'] == 'CONTEXT_MATCHED_CANDIDATE'
    assert [p['id'] for p in card['domain_profiles']] == ['enterprise-software-governance']
    assert 'provisioning result distinct from approval' in card['domain_profiles'][0]['objects']
    assert card['adopted'] is False
    assert card['aesthetic_quality'] == 'UNKNOWN'
    assert 'font_family' not in card['domain_profiles'][0]
    assert 'palette' not in card['domain_profiles'][0]


def test_conflicting_enterprise_context_does_not_select_software_profile():
    card = retrieve_design_knowledge(SKILLS, {'website_type':'ecommerce','domain':'enterprise-software'}, 'home')
    assert card['domain_status'] == 'IDENTITY_CONFLICT'
    assert card['domain_profiles'] == []


def test_conflicting_identity_is_visible_and_not_merged():
    card = retrieve_design_knowledge(SKILLS, {'website_type':'ecommerce','domain':'industrial-services'}, 'catalog')
    assert card['domain_status'] == 'IDENTITY_CONFLICT'
    assert card['domain_profiles'] == []


def test_page_role_changes_quantitative_choices_without_freezing_brand():
    context = {'website_type':'corporate','domain':'industrial-services'}
    orientation = retrieve_design_knowledge(SKILLS, context, 'home')['role_card']
    conversion = retrieve_design_knowledge(SKILLS, context, 'rfq')['role_card']
    assert orientation['type_px_candidates'] != conversion['type_px_candidates']
    assert orientation['spacing_px_candidates'] != conversion['spacing_px_candidates']
    assert 'font_family' not in json.dumps(orientation)
    assert 'palette' not in orientation


@pytest.mark.parametrize('context,expected', [
    ({'website_type':'corporate','domain':'industrial-services','product_archetype':'b2b-service-operations'},'industrial-service-operations'),
    ({'website_type':'ecommerce','domain':'retail','product_archetype':'physical-product-commerce'},'physical-product-commerce'),
    ({'website_type':'portfolio','domain':'career','product_archetype':'career-portfolio'},'career-portfolio'),
])
def test_shared_resource_selects_distinct_subject_matter(context,expected):
    result = retrieve_design_knowledge(SKILLS,context,'home')
    assert result['domain_profiles'][0]['id'] == expected
    assert result['fit_status'] == 'UNVALIDATED'


def test_invalid_role_fails_before_candidate_persistence(tmp_path):
    result = subprocess.run([sys.executable, '-B', str(QUERY), 'SaaS', '--design-system', '--page-role', 'unknown-role', '--persist', '--output-dir', str(tmp_path)],capture_output=True,text=True)
    assert result.returncode == 2
    assert list(tmp_path.rglob('MASTER.md')) == []


def test_all_three_design_flows_emit_semantic_check_gate():
    for name in ['page-ui-work','professional-website-redesign','portfolio-career-system']:
        flow = json.loads((SKILLS/f'flows/{name}.json').read_text(encoding='utf-8'))
        phases = {gate.get('design_phase') for stage in flow['stages'] for gate in stage['gates'] if 'design_contract_check' in gate.get('evidence_types',[])}
        assert phases == {'design','rendered'}
        assert all(gate.get('design_contract_version') == '2.0' for stage in flow['stages'] for gate in stage['gates'] if 'design_contract_check' in gate.get('evidence_types',[]))


def test_owned_skill_validation_does_not_treat_upstream_references_as_active_skills():
    result = subprocess.run([sys.executable,'-B',str(SKILLS/'scripts/validate-skills.py')],capture_output=True,text=True,encoding='utf-8')
    assert result.returncode == 0,result.stderr
    assert f"Validated {len(list(SKILLS.glob('*/SKILL.md')))} skills" in result.stdout


def test_skill_validator_still_rejects_invalid_owned_skill(tmp_path):
    import runpy
    module = runpy.run_path(str(SKILLS/'scripts/validate-skills.py'))
    validate = module['main']
    validate.__globals__['ROOT'] = tmp_path
    (tmp_path/'bad-owned').mkdir()
    (tmp_path/'bad-owned/SKILL.md').write_text('---\nname: bad-owned\ndescription: ""\n---\nBody',encoding='utf-8')
    (tmp_path/'upstream/deep').mkdir(parents=True)
    (tmp_path/'upstream/deep/SKILL.md').write_text('Invalid pinned source, tested separately',encoding='utf-8')
    assert validate() == 1


def test_executor_design_handoff_runs_canonical_design_checker(tmp_path):
    from test_p16_execution_driver import _build_driver
    _, _, driver, _, _, _ = _build_driver(tmp_path)
    assert driver.run_next()['status'] == 'passed'
    event = driver.run_next()
    assert event['status'] == 'passed', event.get('reason')
    records = driver.checkpoint_store.load()['stage_evidence']['work-2']
    proof = next(item for item in records if item['type'] == 'design_contract_check')
    assert proof['data']['phase'] == 'design'
    assert proof['data']['contract_version'] == '2.0'
    assert proof['data']['aesthetic_quality'] == 'UNKNOWN'
    assert proof['data']['human_preference'] == 'UNKNOWN'
    assert Path(proof['data']['artifact_path']).is_file()


def test_runtime_foundation_smoke_satisfies_canonical_design_gates():
    import runpy
    smoke = runpy.run_path(str(SKILLS/'scripts/validate-runtime-foundation.py'))
    errors = []
    smoke['_run_flow_os_smoke'](errors)
    assert errors == []


@pytest.mark.parametrize('case', ['empty', 'provider_origin', 'failed', 'wrong_phase', 'legacy', 'wrong_stage'])
def test_canonical_design_completion_rejects_invalid_proof(tmp_path, case):
    from fixtures.executor_evidence import design_fixture
    from test_factory_completion_gates import _fresh
    harness, manager, managed = _fresh(tmp_path)
    harness.execute_plan(manager.start_stage(managed), [{'tool': 'read_text', 'args': {'path': 'index.html'}}])
    manager.complete_stage(managed)
    state = harness.execute_plan(manager.start_stage(managed), [])
    proof = design_fixture(tmp_path, 'design')
    if case == 'provider_origin':
        proof['origin'] = 'provider'
    elif case == 'failed':
        proof['status'] = 'FAIL'
    elif case == 'wrong_phase':
        proof['data']['phase'] = 'rendered'
    elif case == 'legacy':
        proof['data']['contract_version'] = '1.0'
    elif case == 'wrong_stage':
        proof['stage_id'] = 'research'
    state.context['evidence_records'] = [] if case == 'empty' else [proof]
    harness.checkpoints.save(state.run_id, state.to_dict())
    with pytest.raises(ValueError, match='completion evidence failed'):
        manager.complete_stage(managed)
    assert managed.active_stage == 'design' and managed.state != 'COMPLETED'


def test_executor_resume_rechecks_current_design_proof(tmp_path):
    from core.runtime.flow_os.execution_driver import ExecutionDriver, RunnerContractError
    from test_p16_execution_driver import _build_driver
    _, _, driver, runner, target, _ = _build_driver(tmp_path)
    assert driver.run_next()['status'] == 'passed'
    assert driver.run_next()['status'] == 'passed'
    proof = next(item for item in driver.checkpoint_store.load()['stage_evidence']['work-2']
                 if item['type'] == 'design_contract_check')
    Path(proof['data']['artifact_path']).write_text('{}', encoding='utf-8')
    with pytest.raises(RunnerContractError):
        ExecutionDriver.resume(driver.work_plan, runner, workspace_root=target,
                               checkpoint_store=driver.checkpoint_store, grant=driver.grant)


def test_design_proof_cannot_replace_implementation_evidence(tmp_path):
    from fixtures.executor_evidence import design_fixture
    from core.runtime.flow_os.evidence import gate_evidence_errors
    proof = design_fixture(tmp_path, 'implementation')
    assert gate_evidence_errors([{'id': 'stage-completion-evidence'}], 'implementation',
                                [proof], agent='implementation')


@pytest.mark.parametrize('content', ['{}', 'not json'])
def test_runtime_smoke_never_attests_invalid_contract(tmp_path, content):
    import runpy
    from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
    from core.runtime.flow_os.managed import ManagedFlowController
    smoke = runpy.run_path(str(SKILLS/'scripts/validate-runtime-foundation.py'))
    source = tmp_path/'invalid-contract.json'
    source.write_text(content, encoding='utf-8')
    project = tmp_path/'project'
    smoke['_git_fixture'](project)
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal('Build a corporate website', authority='branch_write')
    managed.active_stage = 'design'  # Isolated smoke-fixture boundary.
    state = manager.start_stage(managed)
    record = smoke['_record_smoke_design_check']
    record.__globals__['DESIGN_SMOKE_CONTRACT'] = source
    with pytest.raises(ValueError):
        record(harness, state)
    assert not state.context.get('evidence_records')

"""Negative probes use temporary artifacts and explicit synthetic captures only."""
import asyncio
import hashlib
import sys
import copy
import types
from dataclasses import replace
from pathlib import Path

import pytest

FACTORY = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(FACTORY), str(FACTORY / 'tests')]
from test_factory_render_gates import _png, rendered
from test_factory_pipeline_gates import manager
from test_p16_execution_driver import _build_driver
from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.release import ProductionReleaseController
from core.runtime.flow_os.evidence import gate_evidence_errors, evidence_from_tool
from core.runtime.flow_os.execution_driver import ExecutionGrant, RunnerContractError, RunnerResult, validate_runner_evidence


def test_driver_rejects_file_only_qa(tmp_path):
    _, _, driver, runner, _, _ = _build_driver(tmp_path)
    runner.extra_env['P16_FILE_ONLY_QA'] = '1'
    driver.run_until_blocked()
    assert driver.execution_plan.nodes[-1].status != 'passed', 'text file labeled screenshot cannot prove rendered QA'


def test_driver_rechecks_handoff_before_dispatch(tmp_path):
    _, _, driver, runner, target, _ = _build_driver(tmp_path)
    assert driver.run_next()['status'] == 'passed'
    record = next(iter(driver.registry.records.values()))
    (target / record.metadata['workspace_path']).write_text('changed after acceptance', encoding='utf-8')
    assert driver.run_next()['status'] == 'failed', 'stale artifact must block the next runner'
    assert runner.invocations == 1


def test_release_rechecks_capture_hash(tmp_path, rendered):
    project = tmp_path / 'project'
    project.mkdir()
    harness = ProviderNeutralAgentHarness(FACTORY.parent / 'skills_UIUX', project)
    controller = ManagedFlowController(harness)
    managed = controller.start_from_goal('Build a corporate industrial automation website', authority='read_only')
    managed.active_stage = 'qa'  # Final boundary fixture, not a complete AI run.
    state = harness.execute_plan(controller.start_stage(managed), [{'tool': 'run_validator', 'args': {'name': 'validate-flows'}}])
    record, image = rendered
    state.context['evidence_records'].append(record)
    harness.checkpoints.save(state.run_id, state.to_dict())
    controller.complete_stage(managed)
    assert ProductionReleaseController(harness).validate_release_ready(managed) == []
    image.write_bytes(_png(width=321))
    assert ProductionReleaseController(harness).validate_release_ready(managed), 'release must reject stale capture'


@pytest.mark.parametrize('gate', ['rendered-check', 'micro-rendered-check', 'page-rendered-check', 'rendered-recruiter-path'])
def test_every_rendered_flow_gate_requires_capture(gate):
    record = evidence_from_tool('qa', 'run_validator', {'returncode': 0}).to_dict()
    assert gate_evidence_errors([{'id': gate}], 'qa', [record], agent='qa'), 'a validator alone cannot satisfy rendered inspection'


def test_native_quality_loop_checks_frozen_hash_before_repair_dispatch(manager, monkeypatch):
    from core.manager.development_manager import DevelopmentManager
    context = asyncio.run(manager.run('Build a calm editorial portfolio', engine='ai'))
    Path(context.artifacts['full_build_spec']).write_text('stale specification', encoding='utf-8')
    require = manager._require
    def checked_require(ctx, key):
        if key == 'implementation':
            raise AssertionError('QA attempted dispatch before verifying frozen spec')
        return require(ctx, key)
    monkeypatch.setattr(manager, '_require', checked_require)
    with pytest.raises(RuntimeError, match='Frozen specification'):
        asyncio.run(DevelopmentManager._run_quality_loop(manager, context))


@pytest.mark.parametrize('executor', ['ai-manager', 'template-manager', 'direct-builder', 'revision'])
@pytest.mark.parametrize('case', ['missing', 'read_only', 'manual_pending', 'manual_stale'])
def test_native_executors_require_caller_grant_before_write(manager, monkeypatch, executor, case):
    from core.manager.development_manager import DevelopmentManager
    from core.orchestration.ai_frontend_builder import AIFrontendBuilder
    context = asyncio.run(manager.run('Build a calm editorial portfolio', engine='ai'))
    context.execution_grant = (None if case == 'missing' else ExecutionGrant(
        'read_only' if case == 'read_only' else 'branch_write',
        'manual' if case.startswith('manual') else 'auto'))
    context.execution_approval = 'stale' if case == 'manual_stale' else None
    if executor == 'ai-manager':
        work = DevelopmentManager._run_ai_implementation(manager, context, object())
    elif executor == 'template-manager':
        work = DevelopmentManager._run_template_implementation(manager, context)
    elif executor == 'direct-builder':
        work = AIFrontendBuilder(context=context, provider=object(), team_runner=manager.team_runner).run()
    else:
        monkeypatch.setattr(manager, '_run_ai_implementation', types.MethodType(DevelopmentManager._run_ai_implementation, manager))
        work = manager._run_revision_stage(context, 'implementation', 'ai', object())
    with pytest.raises(RuntimeError, match='authority denied|AWAITING_APPROVAL'):
        asyncio.run(work)
    assert not (context.root / 'projects').exists()


def test_valid_native_grant_and_current_manual_approval_are_accepted(manager):
    from core.runtime.run_context import require_native_execution_grant
    context = asyncio.run(manager.run('Build a calm editorial portfolio', engine='ai'))
    context.execution_grant = ExecutionGrant('branch_write')
    require_native_execution_grant(context)
    context.execution_grant = ExecutionGrant('branch_write', 'manual')
    context.execution_approval = hashlib.sha256(Path(context.artifacts['full_build_spec']).read_bytes()).hexdigest()
    require_native_execution_grant(context)
    context.goal += ' Read-only.'
    with pytest.raises(RuntimeError, match='authority denied'):
        require_native_execution_grant(context)


@pytest.mark.parametrize('case', ['missing', 'foreign', 'untrusted', 'stale', 'wrong_route', 'wrong_viewport', 'empty'])
def test_driver_typed_evidence_negative_matrix(tmp_path, rendered, case):
    _, _, driver, _, _, _ = _build_driver(tmp_path)
    request = replace(driver._request('work-4'), workspace_root=str(tmp_path), agent='qa')
    record, image = rendered
    record = copy.deepcopy(record)
    records = [record]
    if case == 'missing':
        records = []
    elif case == 'foreign':
        record['stage_id'] = 'research'
    elif case == 'untrusted':
        record['trusted'] = False
    elif case == 'stale':
        image.write_bytes(_png(width=321))
    elif case == 'wrong_route':
        record['data']['route'] = '/wrong'
    elif case == 'wrong_viewport':
        record['data']['viewport']['width'] = 900
    else:
        image.write_bytes(b'')
    with pytest.raises(RunnerContractError, match='evidence'):
        validate_runner_evidence(request, RunnerResult('2.0', 'passed', [], evidence_records=records))


@pytest.mark.parametrize('case', ['valid', 'missing_hash', 'stale', 'missing_image', 'wrong_route', 'wrong_viewport', 'empty'])
def test_native_render_matrix_checks_actual_png_bytes(tmp_path, case):
    from core.runtime.flow_os.evidence import native_browser_evidence_errors
    image = tmp_path / 'native.png'
    image.write_bytes(_png())
    report = {'base_url': 'http://localhost:4173', 'routes': ['/'], 'viewports': [{'width': 320, 'height': 240}],
              'evidence': [{'route': '/', 'viewport': {'width': 320, 'height': 240}, 'screenshot': str(image),
                            'screenshot_sha256': hashlib.sha256(image.read_bytes()).hexdigest(), 'status': 'passed'}]}
    if case == 'missing_hash':
        report['evidence'][0].pop('screenshot_sha256')
    elif case == 'stale':
        image.write_bytes(_png(width=321))
    elif case == 'missing_image':
        image.unlink()
    elif case == 'wrong_route':
        report['evidence'][0]['route'] = '/unplanned'
    elif case == 'wrong_viewport':
        report['evidence'][0]['viewport']['width'] = 1000
    elif case == 'empty':
        image.write_bytes(b'')
    errors = native_browser_evidence_errors(report, tmp_path)
    assert bool(errors) == (case != 'valid')


@pytest.mark.parametrize('field,value', [('schema_version', '1.0'), ('authority', ''), ('authority', 'read_only'),
                                       ('approval_status', 'AWAITING_APPROVAL'), ('workspace_root', ''),
                                       ('plan_fingerprint', ''), ('plan_fingerprint', 'sha256:' + '0' * 64)])
def test_direct_github_broker_preflight_precedes_checkout_or_worker(tmp_path, monkeypatch, field, value):
    from core.runtime.flow_os.github_transaction import GitHubProductionRunner, GitHubTransactionConfig
    _, _, driver, _, _, _ = _build_driver(tmp_path)
    runner = GitHubProductionRunner(GitHubTransactionConfig(
        repository='example/fixture', remote_url=str(tmp_path / 'nonexistent.git'),
        workspace_root=tmp_path / 'broker', transaction_id='preflight', worker_command=['must-never-run']))
    runner.bind_plan(driver.plan_fingerprint)
    request = replace(driver._request('work-1'), authority='external_write', workspace_root=str(runner.artifact_root))
    request = replace(request, **{field: value})
    def forbidden_checkout():
        pytest.fail('broker attempted checkout before validating request controls')
    monkeypatch.setattr(runner, '_ensure_checkout_and_claim', forbidden_checkout)
    with pytest.raises(RunnerContractError):
        runner.run(request)
    assert runner.state.runner_invocations == 0
    assert not runner.repo_root.exists()


def test_github_source_only_qa_cannot_create_pr(tmp_path):
    from test_p17_github_production_transaction import _init_remote, _fake_github_api, _build_driver as github_driver
    remote, base = _init_remote(tmp_path)
    with _fake_github_api() as (api, state):
        _, _, driver, runner = github_driver(tmp_path, remote, api)
        runner.config.extra_env['P17_FILE_ONLY_QA'] = '1'
        assert driver.run_until_blocked() != 'completed'
        assert runner.state.pr_number is None
        assert state['create_count'] == 0
        assert driver.execution_plan.nodes[-1].status == 'failed'


@pytest.mark.parametrize('executor', ['managed', 'provider', 'release'])
@pytest.mark.parametrize('case', ['valid', 'missing', 'wrong_route', 'wrong_viewport', 'stale', 'empty'])
def test_shared_render_negatives_on_managed_provider_and_release(tmp_path, rendered, monkeypatch, executor, case):
    from core.runtime.flow_os.provider import ScriptedProvider
    from core.runtime.flow_os.provider_runner import ProviderManagedRunner
    record, image = rendered
    record = copy.deepcopy(record)
    project = tmp_path / 'shared-matrix'
    project.mkdir()
    harness = ProviderNeutralAgentHarness(FACTORY.parent / 'skills_UIUX', project)
    controller = ManagedFlowController(harness)
    managed = controller.start_from_goal('Build a corporate industrial automation website', authority='read_only')
    managed.active_stage = 'qa'  # Isolated QA boundary fixture; no claimed lifecycle/research completion.
    if executor != 'provider':
        state = harness.execute_plan(controller.start_stage(managed), [{'tool': 'run_validator', 'args': {'name': 'validate-flows'}}])
        state.context['evidence_records'].append(record)
        harness.checkpoints.save(state.run_id, state.to_dict())
        if executor == 'release':
            controller.complete_stage(managed)
    if case == 'wrong_route':
        record['data']['route'] = '/wrong'
    elif case == 'wrong_viewport':
        record['data']['viewport']['width'] = 900
    elif case == 'stale':
        image.write_bytes(_png(width=321))
    elif case == 'empty':
        image.write_bytes(b'')
    if executor == 'provider':
        provider = ScriptedProvider([{'status': 'PASS', 'actions': [{'tool': 'run_validator', 'args': {'name': 'validate-flows'}}],
                                      'summary': 'Synthetic boundary fixture',
                                      'evidence': ['SYNTHETIC provider claim; only runtime records may satisfy the gate']}])
        runner = ProviderManagedRunner(controller, provider)
        check = runner._typed_gate_errors
        def captured_evidence(run, stage):
            if case != 'missing':
                stage.context.setdefault('evidence_records', []).append(record)
            return check(run, stage)
        monkeypatch.setattr(runner, '_typed_gate_errors', captured_evidence)
        result = runner.run_active_stage(managed, auto_replan=False)
        assert (result.state == 'COMPLETED') == (case == 'valid')
    else:
        if case == 'missing':
            state.context['evidence_records'] = [item for item in state.context['evidence_records'] if item['type'] != 'browser_render']
        harness.checkpoints.save(state.run_id, state.to_dict())
        if executor == 'release':
            assert bool(ProductionReleaseController(harness).validate_release_ready(managed)) == (case != 'valid')
        elif case == 'valid':
            controller.complete_stage(managed)
            assert managed.state == 'COMPLETED'
        else:
            with pytest.raises(ValueError, match='completion evidence failed'):
                controller.complete_stage(managed)
            assert managed.state != 'COMPLETED'

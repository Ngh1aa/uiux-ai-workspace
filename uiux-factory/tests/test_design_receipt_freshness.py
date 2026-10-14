"""Synthetic boundary fixtures: current artifacts and approvals, never visual taste."""
import hashlib
import json
import struct
from types import SimpleNamespace

import pytest

from core.runtime.flow_os.evidence import evidence_from_tool, gate_evidence_errors
from core.runtime.flow_os.execution_driver import validate_runner_evidence, RunnerContractError
from core.skills.design_decisions import check_design_file, check_design_decisions
from fixtures.executor_evidence import design_fixture, render_fixture, file_proof
from test_design_direction_comparison import rendered_fixture, prepare_comparison, observations
from test_factory_completion_gates import _fresh


def design_stage(root, approval='auto'):
    harness, manager, managed = _fresh(root, approval)
    harness.execute_plan(manager.start_stage(managed), [{'tool':'read_text','args':{'path':'index.html'}}])
    manager.complete_stage(managed)
    state = harness.execute_plan(manager.start_stage(managed), [])
    state.context['evidence_records'] = [design_fixture(root, 'design')]
    harness.checkpoints.save(state.run_id, state.to_dict())
    return harness, manager, managed, state


@pytest.mark.parametrize('change', ['replan', 'contract', 'legacy'])
def test_manual_approval_is_bound_to_current_revision_and_design(tmp_path, change):
    harness, manager, managed, state = design_stage(tmp_path, 'manual')
    manager.approve_gate(managed, 'design-contract')
    if change == 'replan':
        assert manager.replan(managed, 'GATE_FAIL').accepted
        state = harness.execute_plan(manager.start_stage(managed), [])
        state.context['evidence_records'] = [design_fixture(tmp_path, 'design', 'revision')]
    elif change == 'contract':
        from pathlib import Path
        path = Path(state.context['evidence_records'][0]['data']['artifact_path'])
        payload = json.loads(path.read_text())
        payload['pages'][0]['cta'] = 'Buy a subscription'
        path.write_text(json.dumps(payload), encoding='utf-8')
        state.context['evidence_records'] = [file_proof('design', 'check_design_decisions', path,
            check_design_file(path.parent, path.name))]
    else:
        # Legacy gate IDs alone must not imply content-bound approval.
        managed.approval_bindings = {}
    harness.checkpoints.save(state.run_id, state.to_dict())
    with pytest.raises(ValueError, match='human approval required'):
        manager.complete_stage(managed)
    manager.approve_gate(managed, 'design-contract')
    assert manager.complete_stage(managed) == 'implementation'


@pytest.mark.parametrize('change', ['missing', 'stale', 'unbound'])
def test_managed_completion_rechecks_design_contract(tmp_path, change):
    from pathlib import Path
    harness, manager, managed, state = design_stage(tmp_path)
    proof = state.context['evidence_records'][0]
    path = Path(proof['data']['artifact_path'])
    if change == 'missing':
        path.unlink()
    elif change == 'stale':
        path.write_text('{}', encoding='utf-8')
    else:
        for key in ['artifact_path', 'artifact_sha256', 'project_root', 'contract_sha256']:
            proof['data'].pop(key, None)
        harness.checkpoints.save(state.run_id, state.to_dict())
    with pytest.raises(ValueError, match='evidence|contract'):
        manager.complete_stage(managed)
    assert managed.active_stage == 'design'


@pytest.mark.parametrize('dependency', ['capture', 'plan', 'observations'])
def test_executor_rechecks_nested_design_dependencies(tmp_path, dependency):
    from pathlib import Path
    proof = design_fixture(tmp_path, 'qa')
    path = Path(proof['data']['artifact_path'])
    payload = json.loads(path.read_text())
    target = (payload['captures'][0]['file'] if dependency == 'capture'
              else payload['pages'][0]['comparison_record'][dependency])
    (path.parent / target).unlink()
    render, _ = render_fixture(tmp_path, 'current')
    request = SimpleNamespace(workspace_root=str(tmp_path), active_stage_id='qa', agent='qa', gates=[
        {'id':'design-render-integrity','evidence_types':['design_contract_check'],
         'design_phase':'rendered','design_contract_version':'2.0'}, {'id':'rendered-qa'}])
    with pytest.raises(RunnerContractError, match='design|evidence'):
        validate_runner_evidence(request, SimpleNamespace(evidence_records=[proof, render]))


def test_design_checker_rejects_header_only_images(tmp_path):
    payload = rendered_fixture(tmp_path)
    for index, capture in enumerate(payload['captures']):
        raw = b'\x89PNG\r\n\x1a\n' + struct.pack('>I', 13) + b'IHDR'
        raw += struct.pack('>II', capture['width'], capture['viewport_height']) + bytes([index])*9
        (tmp_path/capture['file']).write_bytes(raw)
        capture['sha256'] = hashlib.sha256(raw).hexdigest()
    plan = prepare_comparison(payload, '/')
    (tmp_path/'plan.json').write_text(json.dumps(plan), encoding='utf-8')
    (tmp_path/'observations.json').write_text(json.dumps(observations(payload, plan)), encoding='utf-8')
    assert check_design_decisions(payload, phase='rendered', project_root=tmp_path)['status'] == 'FAIL'


def test_current_bound_receipt_and_manual_approval_pass(tmp_path):
    harness, manager, managed, state = design_stage(tmp_path, 'manual')
    manager.approve_gate(managed, 'design-contract')
    restored = manager.resume(managed.manager_run_id)
    assert manager.complete_stage(restored) == 'implementation'


def test_receipt_detects_changed_but_still_valid_nested_file(tmp_path):
    from pathlib import Path
    from core.skills.design_decisions import design_receipt_errors
    proof = design_fixture(tmp_path, 'qa')
    path = Path(proof['data']['artifact_path'])
    payload = json.loads(path.read_text())
    observations_path = path.parent / payload['pages'][0]['comparison_record']['observations']
    # Whitespace keeps the same valid JSON/semantics but invalidates the recorded file.
    observations_path.write_text(observations_path.read_text() + '\n', encoding='utf-8')
    assert check_design_file(path.parent, path.name, 'rendered')['status'] == 'PASS'
    assert any('dependency_hashes' in error for error in design_receipt_errors(proof['data'], tmp_path))


@pytest.mark.parametrize('change', ['missing', 'changed', 'replaced_receipt'])
def test_downstream_stage_cannot_start_with_invalidated_design(tmp_path, change):
    from pathlib import Path
    harness, manager, managed, state = design_stage(tmp_path, 'manual')
    manager.approve_gate(managed, 'design-contract')
    assert manager.complete_stage(managed) == 'implementation'
    proof = state.context['evidence_records'][0]
    path = Path(proof['data']['artifact_path'])
    if change == 'missing':
        path.unlink()
    else:
        payload = json.loads(path.read_text())
        payload['pages'][0]['cta'] = 'Changed after approval'
        path.write_text(json.dumps(payload), encoding='utf-8')
        if change == 'replaced_receipt':
            state.context['evidence_records'] = [file_proof('design', 'check_design_decisions', path,
                check_design_file(path.parent, path.name))]
            harness.checkpoints.save(state.run_id, state.to_dict())
    restored = manager.resume(managed.manager_run_id)
    with pytest.raises(ValueError, match='upstream design|human approval'):
        manager.start_stage(restored)
    assert not restored.stage_runs.get('implementation')


def test_downstream_stage_can_start_with_current_approved_design(tmp_path):
    _, manager, managed, _ = design_stage(tmp_path, 'manual')
    manager.approve_gate(managed, 'design-contract')
    manager.complete_stage(managed)
    assert manager.start_stage(managed).context['stage_id'] == 'implementation'

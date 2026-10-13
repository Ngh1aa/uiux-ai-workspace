from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys

import pytest

from core.skills.design_decisions import check_design_decisions, check_design_file
from core.runtime.flow_os.evidence import evidence_from_tool, gate_evidence_errors, provider_claim_records

ROOT = Path(__file__).resolve().parents[2]


def contract_fixture():
    types = {role:{'size_px':size,'line_height':1.5,'weight':400} for role,size in [('title',40),('section',28),('body',16),('ui',16),('meta',12)]}
    spacing = {'gutter_px':20,'section_gap_px':40,'group_gap_px':24,'component_padding_px':16}
    structure = {'regions':[{'role':'offer','layout':'stack','contains':['title','lead','actions']},{'role':'scope','layout':'labelled-register','contains':['need','deliverables']}], 'relationships':[['offer','introduces','scope']], 'mobile_layout':'labelled-records','mobile_grouping':[['need','deliverables']]}
    alternate = deepcopy(structure)
    alternate['regions'][1]['layout'] = 'annotated-object'
    alternate['relationships'] = [['offer','annotates','scope']]
    alternate['mobile_layout'] = 'linear-annotated-object'
    page = {'route':'/','page_role':'orientation','user_question':'Which scope fits?','cta':'Discuss the scope', 'decisions':[{'axis':axis,'source':{'kind':'hypothesis','ref':'Synthetic test fixture; not user research'},'value':f'Test {axis} choice','rejected_alternative':'Test rejected choice'} for axis in ['layout','font','typography','spacing','media','voice']], 'desktop_type':types,'mobile_type':deepcopy(types),'desktop_spacing':spacing,'mobile_spacing':deepcopy(spacing),'compositions':[{'id':'a','anchor':'register','structure':structure,'proof':'Fixture diagram','tradeoff':'Fixture tradeoff'},{'id':'b','anchor':'object','structure':alternate,'proof':'Fixture alternate diagram','tradeoff':'Fixture alternate tradeoff'}], 'selected_composition':'a'}
    page['desktop_layout'] = {'max_width_px':1200,'columns':3,'column_gap_px':32,'reading_width_ch':65,'density':'mixed'}
    page['mobile_layout'] = {'max_width_px':None,'columns':1,'column_gap_px':0,'reading_width_ch':32,'density':'productive'}
    return {'schema_version':'1.0','pages':[page],'captures':[]}


def test_concrete_distinct_contract_passes_integrity_only():
    result = check_design_decisions(contract_fixture())
    assert result['status'] == 'PASS'
    assert result['aesthetic_quality'] == 'UNKNOWN'
    assert result['human_preference'] == 'UNKNOWN'


def test_section_reorder_and_new_anchor_cannot_fake_two_compositions():
    payload = contract_fixture()
    first, second = payload['pages'][0]['compositions']
    second['structure'] = deepcopy(first['structure'])
    second['structure']['regions'].reverse()
    second['anchor'] = 'Renamed architecture-first'
    result = check_design_decisions(payload)
    assert result['status'] == 'FAIL'
    assert 'reordered unchanged blocks' in '\n'.join(result['errors'])


@pytest.mark.parametrize('field', ['desktop_type','mobile_type','decisions','desktop_spacing'])
def test_long_document_does_not_substitute_missing_design_decisions(field):
    payload = contract_fixture()
    payload['pages'][0].pop(field)
    payload['pages'][0]['compositions'][0]['proof'] = 'Long prose ' * 300
    assert check_design_decisions(payload)['status'] == 'FAIL'


def test_explicit_preserve_request_does_not_force_novel_layout():
    payload = contract_fixture()
    payload['pages'][0]['composition_constraint'] = {'kind':'user','ref':'User explicitly preserves existing composition'}
    payload['pages'][0]['compositions'] = payload['pages'][0]['compositions'][:1]
    assert check_design_decisions(payload)['status'] == 'PASS'
    payload['pages'][0]['composition_constraint']['kind'] = 'hypothesis'
    assert check_design_decisions(payload)['status'] == 'FAIL'


def test_rendered_phase_needs_actual_capture_references():
    assert check_design_decisions(contract_fixture(),phase='rendered',project_root=ROOT)['status'] == 'FAIL'


def test_rollout_page_inherits_representative_without_repeating_alternatives():
    payload = contract_fixture()
    rollout = deepcopy(payload['pages'][0])
    rollout.update(route='/services/second', comparison_required=False, inherited_from='/')
    rollout['compositions'] = rollout['compositions'][:1]
    payload['pages'].append(rollout)
    assert check_design_decisions(payload)['status'] == 'PASS'
    rollout['inherited_from'] = '/missing'
    assert check_design_decisions(payload)['status'] == 'FAIL'


def test_contract_cannot_disable_all_representative_comparisons():
    payload = contract_fixture()
    payload['pages'][0].update(comparison_required=False, inherited_from='/')
    assert check_design_decisions(payload)['status'] == 'FAIL'


def test_real_capture_digest_dimensions_and_critique_are_checked(tmp_path):
    # Existing local rendered captures exercise integrity. This synthetic contract
    # does not claim that those screenshots prove the fixture's design or preference.
    samples = ROOT.parents[1]/'outputs/composition-study/screenshots'
    if not samples.exists():
        pytest.skip('local rendered artifacts unavailable; portable negative cases still run')
    payload = contract_fixture()
    for composition in ['a','b']:
        for width in [1440,390]:
            source = samples/f'{composition}-{width}-viewport.png'
            target = tmp_path/source.name
            raw = source.read_bytes(); target.write_bytes(raw)
            payload['captures'].append({'route':'/','composition_id':composition,'file':target.name,'sha256':sha256(raw).hexdigest(),'width':width,'viewport_height':844 if width==390 else 1000,'inspected':True,'review_source':'agent-heuristic','critique':{key:'Synthetic integrity test; not a visual finding' for key in ['hierarchy','typography','spacing','media','distinctiveness']}})
    assert check_design_decisions(payload,phase='rendered',project_root=tmp_path)['status'] == 'PASS'
    payload['captures'][0]['sha256'] = '0'*64
    result = check_design_decisions(payload,phase='rendered',project_root=tmp_path)
    assert result['status'] == 'FAIL' and 'digest mismatch' in '\n'.join(result['errors'])
    payload['captures'][0]['file'] = '../outside.png'
    assert check_design_decisions(payload,phase='rendered',project_root=tmp_path)['status'] == 'FAIL'


def test_file_checker_refuses_escape_and_cli_rejects_prose(tmp_path):
    (tmp_path/'decision.json').write_text(json.dumps(contract_fixture()),encoding='utf-8')
    assert check_design_file(tmp_path,'decision.json')['status'] == 'PASS'
    with pytest.raises(ValueError):
        check_design_file(tmp_path,'../decision.json')
    (tmp_path/'prose.md').write_text('Complete Design Contract '*500,encoding='utf-8')
    result = subprocess.run([sys.executable,str(ROOT/'skills_UIUX/visual-design-direction/scripts/check-design-decisions.py'),'--root',str(tmp_path),'--contract','prose.md'],capture_output=True,text=True)
    assert result.returncode == 1
    assert json.loads(result.stdout)['aesthetic_quality'] == 'UNKNOWN'


def test_generic_validator_or_provider_pass_cannot_satisfy_design_gate():
    gates = [{'id':'design-decision-integrity','evidence_types':['design_contract_check'],'design_phase':'design'}]
    records = [evidence_from_tool('design','run_validator',{'returncode':0}).to_dict()]
    assert gate_evidence_errors(gates,'design',records,'implementation')
    records.append(evidence_from_tool('design','check_design_decisions',check_design_decisions(contract_fixture())).to_dict())
    assert gate_evidence_errors(gates,'design',records,'implementation') == []
    gates[0]['design_phase'] = 'rendered'
    assert gate_evidence_errors(gates,'design',records,'implementation')


def test_later_failed_check_blocks_stale_success():
    gate = [{'id':'design-decision-integrity','evidence_types':['design_contract_check'],'design_phase':'design'}]
    records = [evidence_from_tool('design','check_design_decisions',check_design_decisions(contract_fixture())).to_dict(), evidence_from_tool('design','check_design_decisions',{'returncode':1,'phase':'design','errors':['topology failure']}).to_dict()]
    assert gate_evidence_errors(gate,'design',records,'implementation')

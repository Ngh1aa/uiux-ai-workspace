"""Synthetic integrity fixtures; these tests do not grade aesthetic quality."""
from copy import deepcopy
from hashlib import sha256
import json
import struct
import subprocess
import sys
import zlib

import pytest

from core.skills.design_decisions import check_design_decisions
from core.skills.design_comparison import prepare_comparison, reviewer_order, evaluate_comparison, digest, read_comparison_json
from core.skills.design_knowledge import retrieve_design_knowledge
from core.runtime.flow_os.evidence import evidence_from_tool, gate_evidence_errors
from test_design_decision_integrity import contract_fixture, ROOT


def v2_fixture():
    value = contract_fixture()
    value['schema_version'] = '2.0'
    page = value['pages'][0]
    for index, composition in enumerate(page['compositions']):
        composition['direction'] = {
            'visual_object': {'kind': 'test-object', 'information_task': 'Locate scope and its boundary', 'anatomy': ['scope','boundary'] if not index else ['input','decision','result'], 'reality':'synthetic'},
        }
        for viewport in ('desktop','mobile'):
            typography = {'family':'Test Sans', 'title': deepcopy(page[viewport+'_type']['title']), 'body':deepcopy(page[viewport+'_type']['body']), 'title_tracking_em':0, 'reading_width_ch':page[viewport+'_layout']['reading_width_ch']}
            density = {'mode': page[viewport+'_layout']['density'], 'section_gap_px':40, 'group_gap_px':24, 'object_padding_px':16}
            if index:
                typography['title']['size_px'] = 54
                density.update(section_gap_px=64, group_gap_px=32, object_padding_px=24)
            composition['direction'][viewport+'_typography'] = typography
            composition['direction'][viewport+'_density'] = density
    page['reference_transfers'] = [{'reference_id':'synthetic-test-reference', 'source':{'kind':'hypothesis','ref':'Unit fixture; not first-party research'}, 'action':'ADAPT','property':'Scope-to-boundary relationship','reason':'Evaluate supplier fit','boundary':'No copied claims or beauty proof'}]
    page['comparison_protocol'] = {
        'buyer_task':'Find whether this scope fits the requirement',
        'held_constant': {key:'Same synthetic fixture input' for key in ['audience','content','claims','cta','state','assets','viewports']},
        'questions':[{'id':'fit','dimension':'comprehension','prompt':'Which scope fits and what is excluded?','criteria':['Names the scope','Names the boundary']},
                     {'id':'cue','dimension':'distinctiveness','prompt':'What signals this specific domain without its logo?','criteria':['Names an information relationship','Explains its buyer use']}],
    }
    return value


def png(width, height, tone):
    def chunk(kind, raw):
        return struct.pack('>I',len(raw))+kind+raw+struct.pack('>I',zlib.crc32(kind+raw))
    rows = (b'\x00'+bytes([tone,tone,tone])*width)*height
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')


def rendered_fixture(tmp_path):
    payload = v2_fixture()
    for index, composition in enumerate(['a','b']):
        for width, height in [(1440,1000),(390,844)]:
            raw=png(width,height,230-index)
            name=f'{composition}-{width}.png'
            (tmp_path/name).write_bytes(raw)
            payload['captures'].append({'route':'/','composition_id':composition,'file':name,'sha256':sha256(raw).hexdigest(),'width':width,'viewport_height':height,'inspected':True,'review_source':'agent-heuristic','critique':{key:'Synthetic test image, not visual preference evidence' for key in ['hierarchy','typography','spacing','media','distinctiveness']}})
    payload['pages'][0]['comparison_record'] = {'plan':'plan.json','observations':'observations.json'}
    plan = prepare_comparison(payload,'/')
    (tmp_path/'plan.json').write_text(json.dumps(plan),encoding='utf-8')
    (tmp_path/'observations.json').write_text(json.dumps(observations(payload,plan)),encoding='utf-8')
    return payload


def observations(payload, plan):
    answers=[]
    for label, composition in plan['facilitator']['labels'].items():
        capture=next(item for item in payload['captures'] if item['composition_id']==composition)
        for question in plan['facilitator']['protocol']['questions']:
            answers.append({'label':label,'question_id':question['id'],'response':'Synthetic reviewer answer','criteria_met':[True]*len(question['criteria']),'observed_element':'Synthetic fixture region','capture_sha256':capture['sha256']})
    return {'schema_version':'1.0','plan_sha256':digest(plan),'reviews':[{'reviewer_id':'synthetic-agent','role':'Test fixture','source':'agent-heuristic','independent':False,'presentation_order':reviewer_order(plan,'synthetic-agent'),'answers':answers,'preferred_label':None,'tradeoff':'Fixture demonstrates integrity only'}]}


def test_v2_has_material_axes_and_unknown_aesthetics():
    result=check_design_decisions(v2_fixture())
    assert result['status']=='PASS'
    assert result['direction_comparison']=='MULTI_AXIS_DECLARED'
    assert result['human_preference']==result['aesthetic_quality']=='UNKNOWN'


@pytest.mark.parametrize('axis', ['typography','density','visual_object'])
def test_unchanged_free_axis_blocks_v2(axis):
    payload=v2_fixture()
    a,b=payload['pages'][0]['compositions']
    keys=['visual_object'] if axis=='visual_object' else ['desktop_'+axis,'mobile_'+axis]
    for key in keys:
        b['direction'][key]=deepcopy(a['direction'][key])
    assert check_design_decisions(payload)['status']=='FAIL'


def test_minuscule_numeric_changes_and_renamed_object_do_not_count():
    payload=v2_fixture()
    a,b=payload['pages'][0]['compositions']
    b['direction']=deepcopy(a['direction'])
    b['direction']['desktop_typography']['title']['size_px']+=.1
    b['direction']['desktop_density']['section_gap_px']+=.1
    b['direction']['visual_object']['kind']='Renamed object'
    assert check_design_decisions(payload)['status']=='FAIL'


def test_user_constraint_preserves_axis_without_turning_suggestion_into_lock():
    payload=v2_fixture()
    page=payload['pages'][0]
    page['compositions'][1]['direction']['visual_object']=deepcopy(page['compositions'][0]['direction']['visual_object'])
    page['axis_constraints']=[{'axis':'visual_object','source':{'kind':'user','ref':'Explicit fixed visual object request'},'reason':'Keep the working product object'}]
    assert check_design_decisions(payload)['status']=='PASS'
    page['axis_constraints'][0]['source']['kind']='hypothesis'
    assert check_design_decisions(payload)['status']=='FAIL'


def test_locked_axis_cannot_change_and_selected_values_cannot_drift():
    payload=v2_fixture()
    page=payload['pages'][0]
    page['axis_constraints']=[{'axis':'visual_object','source':{'kind':'user','ref':'User preserve'},'reason':'Keep the actual object'}]
    assert check_design_decisions(payload)['status']=='FAIL'
    page['axis_constraints']=[]
    page['compositions'][0]['direction']['desktop_typography']['title']['size_px']=41
    assert check_design_decisions(payload)['status']=='FAIL'


@pytest.mark.parametrize('field',['reference_transfers','comparison_protocol'])
def test_v2_missing_transfer_or_evaluation_cannot_pass(field):
    payload=v2_fixture(); payload['pages'][0].pop(field)
    assert check_design_decisions(payload)['status']=='FAIL'


def test_new_gate_rejects_legacy_receipt_but_manual_v1_stays_readable():
    old=check_design_decisions(contract_fixture())
    assert old['status']=='PASS' and old['direction_comparison']=='LEGACY_LAYOUT_ONLY'
    gate=[{'id':'v2','evidence_types':['design_contract_check'],'design_phase':'design','design_contract_version':'2.0'}]
    record=evidence_from_tool('design','check_design_decisions',old).to_dict()
    assert gate_evidence_errors(gate,'design',[record],'implementation')
    record=evidence_from_tool('design','check_design_decisions',check_design_decisions(v2_fixture())).to_dict()
    assert gate_evidence_errors(gate,'design',[record],'implementation')==[]


@pytest.mark.parametrize('context,role,profile', [
    ({'website_type':'corporate','domain':'industrial-services'},'service-detail','industrial-service-operations'),
    ({'website_type':'saas','domain':'enterprise-software'},'home','enterprise-software-governance'),
    ({'website_type':'ecommerce','domain':'retail'},'offering','physical-product-commerce'),
    ({'website_type':'portfolio','domain':'career'},'evidence','career-portfolio'),
])
def test_reference_anatomy_is_domain_and_role_bounded(context,role,profile):
    knowledge=retrieve_design_knowledge(ROOT/'skills_UIUX',context,role)
    anatomy=knowledge['reference_anatomy']
    assert anatomy['status']=='CONTEXT_MATCHED_CANDIDATES'
    assert len(anatomy['cards'])==1
    assert anatomy['cards'][0]['profile_id']==profile
    assert anatomy['cards'][0]['why'] and len(anatomy['cards'][0]['visual_object_candidates'])==2
    assert anatomy['adopted'] is False
    assert all(source['pixel_geometry']=='UNKNOWN' for source in anatomy['sources'].values())


def test_reference_gaps_and_index_do_not_load_wrong_role_or_all_sources():
    context={'website_type':'portfolio','domain':'career'}
    assert retrieve_design_knowledge(ROOT/'skills_UIUX',context,'rfq')['reference_anatomy']['status']=='NO_CURATED_REFERENCE_ANATOMY'
    index=retrieve_design_knowledge(ROOT/'skills_UIUX',context)['reference_anatomy']
    assert index['cards']==[] and index['sources']=={}
    wrong=retrieve_design_knowledge(ROOT/'skills_UIUX',{'website_type':'ecommerce','domain':'industrial-services'},'home')['reference_anatomy']
    assert wrong['cards']==[]


def test_review_packet_omits_answer_criteria_and_candidate_mapping():
    plan=prepare_comparison(v2_fixture(),'/',27)
    reviewer=json.dumps(plan['reviewer'])
    assert 'criteria' not in reviewer.replace('answer criteria','answer key')
    assert 'compositions' not in reviewer
    assert plan['status']=='PLANNED_VALIDATION'
    orders={tuple(reviewer_order(plan,f'p{i}',i)) for i in range(20)}
    assert len(orders)==2
    assert reviewer_order(plan,'p0',0)[0]!=reviewer_order(plan,'p1',1)[0]


def test_empty_observations_remain_planned_and_agent_review_is_not_user_research(tmp_path):
    payload=rendered_fixture(tmp_path); plan=prepare_comparison(payload,'/')
    empty={'schema_version':'1.0','plan_sha256':digest(plan),'reviews':[]}
    assert evaluate_comparison(payload,plan,empty,tmp_path)['status']=='PLANNED_VALIDATION'
    result=evaluate_comparison(payload,plan,observations(payload,plan),tmp_path)
    assert result['status']=='HEURISTIC_ONLY' and result['human_review_count']==0
    assert result['aesthetic_quality']==result['human_preference']==result['causal_effect']=='UNKNOWN'


@pytest.mark.parametrize('failure',['stale','duplicate','missing','wrong_capture','wrong_order','fake_independence','tampered_plan'])
def test_invalid_observations_fail_closed(tmp_path,failure):
    payload=rendered_fixture(tmp_path); plan=prepare_comparison(payload,'/')
    records=observations(payload,plan); review=records['reviews'][0]
    if failure=='stale': payload['pages'][0]['cta']='Changed action'
    if failure=='duplicate': review['answers'].append(deepcopy(review['answers'][0]))
    if failure=='missing': review['answers'].pop()
    if failure=='wrong_capture': review['answers'][0]['capture_sha256']='0'*64
    if failure=='wrong_order': review['presentation_order'].reverse()
    if failure=='fake_independence': review['independent']=True
    if failure=='tampered_plan': plan['facilitator']['labels']={'A':'b','B':'b'}
    assert evaluate_comparison(payload,plan,records,tmp_path)['status']=='FAIL'


def test_comparison_reader_refuses_escaping_path(tmp_path):
    with pytest.raises(ValueError): read_comparison_json(tmp_path,'../outside.json')


def test_rendered_v2_requires_actual_paired_observations_not_only_plan(tmp_path):
    payload=rendered_fixture(tmp_path)
    assert check_design_decisions(payload,phase='rendered',project_root=tmp_path)['status']=='PASS'
    plan=prepare_comparison(payload,'/')
    (tmp_path/'observations.json').write_text(json.dumps({'schema_version':'1.0','plan_sha256':digest(plan),'reviews':[]}),encoding='utf-8')
    result=check_design_decisions(payload,phase='rendered',project_root=tmp_path)
    assert result['status']=='FAIL' and 'actual recorded review' in '\n'.join(result['errors'])


def test_comparison_cli_prepares_and_summarizes_without_provider(tmp_path):
    payload=rendered_fixture(tmp_path)
    (tmp_path/'contract.json').write_text(json.dumps(payload),encoding='utf-8')
    command=[sys.executable,'-B',str(ROOT/'skills_UIUX/visual-design-direction/scripts/evaluate-design-comparison.py'),'--root',str(tmp_path),'--contract','contract.json']
    result=subprocess.run(command+['--route','/'],capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,result.stderr
    plan=json.loads(result.stdout)
    (tmp_path/'plan.json').write_text(json.dumps(plan),encoding='utf-8')
    (tmp_path/'observations.json').write_text(json.dumps(observations(payload,plan)),encoding='utf-8')
    result=subprocess.run(command+['--plan','plan.json','--observations','observations.json'],capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,result.stderr
    assert json.loads(result.stdout)['status']=='HEURISTIC_ONLY'


def test_portable_rendered_specimen_receipt_and_comparison_are_current():
    evidence = ROOT/'docs/evidence/design-direction-study'
    payload = json.loads((evidence/'design-decisions.json').read_text(encoding='utf-8'))
    result = check_design_decisions(payload,phase='rendered',project_root=evidence)
    assert result['status']=='PASS',result['errors']
    assert len(payload['captures'])==12 and result['page_count']==2
    assert all(item['status']=='HEURISTIC_ONLY' and item['human_review_count']==0 for item in result['comparison_reviews'])
    assert result['human_preference']==result['aesthetic_quality']=='UNKNOWN'

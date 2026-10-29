"""Evidence is bound to the actual files; source-only PASS never certifies a flow."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import report


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run = Path(self.tmp.name)
        self.scores = {'protocol': {'independent_review': False}}
        self.checks = {'source': {}, 'briefs': {}}
        source = self.checks['source']
        source['repo_commit'] = 'a' * 40
        source['patch'] = self.file('provenance/local.patch', 'local patch')
        manifest = {'baseline_commit': 'a' * 40, 'patch_sha256': source['patch']['sha256'], 'files': {'FLOW.md': 'c' * 64}}
        source['manifest'] = self.file('provenance/manifest.json', json.dumps(manifest))
        source['checkers'] = {key: 'b' * 64 for key in ('render','static','flow')}
        source['browser_test_sha256'] = self.file('flow.browser.cjs', 'assertions')['sha256']
        sample = self.file('01-landing/index.html', '<h1>Sample</h1>')
        render = self.file('render.json', json.dumps({'errorCount': 0}))
        scenarios = [{'name':'root → result','status':'PASS'}]
        runtime = self.file('flow-results.json', json.dumps({'briefs': {'01-landing': {'status': 'PASS', 'scenarios':scenarios}}}))
        static = self.file('static.json', json.dumps({'errorCount':0}))
        self.entry = {'status': 'PASS', 'render': {'status':'PASS','evidence':render['path'],'sha256':render['sha256']},
            'flow': {'status':'PASS','static':{'status':'PASS','evidence':static['path'],'sha256':static['sha256']},'browser':{'status':'PASS','evidence':runtime['path'],'sha256':runtime['sha256'],'scenarios':scenarios}},
            'sample': {'source': 'original', 'files': {sample['path']: sample['sha256']}}}
        self.checks['briefs']['01-landing'] = self.entry

    def file(self, name, content):
        target = self.run / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf8')
        return {'path':name, 'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}

    def errors(self):
        return report.validate_evidence(self.run, self.scores, self.checks)

    def test_complete_evidence_binds_files(self):
        self.assertEqual(self.errors(), [])

    def test_changed_sample_is_rejected(self):
        (self.run / '01-landing/index.html').write_text('changed')
        self.assertTrue(self.errors())

    def test_missing_patch_and_manifest_rejected(self):
        (self.run / 'provenance/local.patch').unlink()
        self.assertTrue(self.errors())

    def test_source_pass_with_unknown_runtime_cannot_pass(self):
        self.entry['flow']['browser']['status'] = 'UNKNOWN'
        self.entry['flow']['status'] = 'UNKNOWN'
        self.assertTrue(self.errors())

    def test_empty_scenarios_do_not_certify_flow(self):
        self.entry['flow']['browser']['scenarios'] = []
        self.assertTrue(self.errors())

    def test_false_independent_flag_rejected(self):
        self.scores['protocol']['independent_review'] = True
        self.assertTrue(self.errors())

    def test_review_reference_cannot_escape_run(self):
        self.assertIsNone(report.checked_file(self.run, {'path':'../outside','sha256':'a'*64}))

    def test_native_browser_does_not_certify_native(self):
        self.checks['briefs'] = {'05-native': self.entry}
        self.entry['flow']['native_status'] = 'PASS'
        self.assertTrue(self.errors())

    def test_legacy_high_scores_without_flow_are_unknown(self):
        row = report.row('legacy','01-landing', {'size':'M','scores':{str(i):5 for i in range(1,11)},'hard_fails':[]}, {'status':'PASS','errors':0,'warnings':0}, {'kind':'legacy-unknown','independent_review':False})
        self.assertIn('| UNKNOWN |', row)
        self.assertNotIn('| Đạt |', row)

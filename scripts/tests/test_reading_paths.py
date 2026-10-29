"""Protect routing, read budget and lossless progressive disclosure."""
import importlib.util
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('reading_paths', ROOT / 'scripts/reading-paths.py')
reading = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reading)


class ReadingPathsTests(unittest.TestCase):
    def test_representative_m_paths_below_budget(self):
        for name, item in reading.build()['paths'].items():
            with self.subTest(path=name):
                self.assertLess(item['after']['total'], 8000)
                self.assertLess(item['after']['total'], item['before']['total'])

    def test_workflow_skill_routes_resolve_and_catalog_covers_skills(self):
        workflow = (ROOT / 'WORKFLOWS.md').read_text(encoding='utf8')
        paths = re.findall(r'\]\((skills_UIUX/[^)#]+/SKILL\.md)(?:#[^)]*)?\)', workflow)
        self.assertGreater(len(set(paths)), 10)
        for path in paths:
            self.assertTrue((ROOT / path).is_file(), path)
        catalog = (ROOT / 'skills_UIUX/SKILL-CATALOG.md').read_text(encoding='utf8')
        for path in (ROOT / 'skills_UIUX').glob('*/SKILL.md'):
            self.assertIn(f'`{path.parent.name}`', catalog)

    def test_deep_content_not_lost_in_compaction(self):
        for reference in (ROOT / 'skills_UIUX').glob('*/references/practice-detail.md'):
            original = reference.parent.parent / 'SKILL.md'
            rel = original.relative_to(ROOT).as_posix()
            baseline = subprocess.run(['git','-C',str(ROOT),'show',f'{reading.BASELINE}:{rel}'],capture_output=True,encoding='utf8',check=True).stdout
            body = baseline.split('---',2)[-1].lstrip()
            body = re.sub(r'\]\((?![a-z]+:|/|#)([^)]+)\)',lambda m:'](../'+m[1]+')',body)
            self.assertIn(body.rstrip(), reference.read_text(encoding='utf8'), rel)
            self.assertIn('references/practice-detail.md', original.read_text(encoding='utf8'), rel)

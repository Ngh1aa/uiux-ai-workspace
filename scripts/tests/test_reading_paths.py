"""Protect routing, read budget and lossless progressive disclosure."""
import importlib.util
import json
import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('reading_paths', ROOT / 'scripts/reading-paths.py')
reading = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reading)


_MERGED_DATA = json.loads((ROOT / 'skills_UIUX/merged-skills.json').read_text(encoding='utf8'))
MERGED = _MERGED_DATA['merged']
RENAMED_FILES = _MERGED_DATA['renamed_files']
FLATTENED = {'references', 'checklists', 'examples', 'assets', 'templates'}
MOVED_DIRS = {**{f"{v['host']}/references/{k}": v['dir'] for k, v in MERGED.items()}, **_MERGED_DATA['folded_dirs']}


def remap_merged(body, base):
    """Links into a skill that was later folded into a host skill point to its new home; text stays verbatim."""
    def fix(m):
        target, _, anchor = m[1].partition('#')
        if '://' in target or not target:
            return m[0]
        resolved = Path(os.path.normpath(base / target))
        try:
            parts = resolved.relative_to(ROOT / 'skills_UIUX').parts
        except ValueError:
            return m[0]
        new = list(parts)
        if new and new[0] in MERGED:
            rest = new[1:]
            if rest == ['SKILL.md']:
                rest = ['README.md']
            new = [MERGED[new[0]]['host'], 'references', new[0]] + rest
        if len(new) >= 3 and new[1] == 'references' and '/'.join(new[:3]) in MOVED_DIRS:
            rest = new[3:]
            if len(rest) == 2 and rest[0] in FLATTENED:
                rest = rest[1:]
            new = [new[0], 'references', MOVED_DIRS['/'.join(new[:3])]] + rest
        if new:
            new[-1] = RENAMED_FILES.get(new[-1], new[-1])
        if new == list(parts):
            return m[0]
        target = ROOT / 'skills_UIUX' / Path(*new)
        return '](' + os.path.relpath(target, base).replace(os.sep, '/') + ('#' + anchor if anchor else '') + ')'
    return re.sub(r'\]\(([^)\s]+)\)', fix, body)


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
            body = remap_merged(body, reference.parent)
            self.assertIn(body.rstrip(), reference.read_text(encoding='utf8'), rel)
            self.assertIn('references/practice-detail.md', original.read_text(encoding='utf8'), rel)

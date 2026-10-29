#!/usr/bin/env python3
"""Đếm đúng file thực mở, whitespace units, cùng thuật toán cho baseline và local."""
from pathlib import Path
import argparse
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'd7000758c2e2aa273785455ae91d255fe3be04e0'
CORE = ['START-HERE.md', 'AGENTS.md', 'TASTE.md', 'CRAFT.md', 'FLOW.md', 'WORKFLOWS.md']
SKILLS = ['ux-structure-and-flow-design', 'visual-design-direction', 'ui-craft-and-visual-qa', 'design-critique-and-rationale']
COMMON = CORE + [f'skills_UIUX/{name}/SKILL.md' for name in SKILLS]
PATHS = {
    'M-feature-existing-system': COMMON,
    'M-table-dashboard': COMMON + [f'skills_UIUX/{name}/SKILL.md' for name in ['data-tables-and-enterprise-ux', 'data-visualization-and-dashboard-ux']],
    'M-responsive-web': COMMON + ['skills_UIUX/responsive-and-device-strategy/SKILL.md'],
}


def measure(paths, ref=None):
    result = {}
    for name in paths:
        if ref:
            process = subprocess.run(['git', '-C', str(ROOT), 'show', f'{ref}:{name}'], capture_output=True, encoding='utf8')
            if process.returncode:
                if name == 'FLOW.md':
                    result[name] = {'units': 0, 'status': 'MISSING_AT_BASELINE'}
                    continue
                raise ValueError(f'Không đọc được baseline {name}')
            text = process.stdout
        else:
            text = (ROOT / name).read_text(encoding='utf8')
        result[name] = {'units': len(text.split()), 'status': 'READ'}
    return {'total': sum(item['units'] for item in result.values()), 'files': result}


def build():
    paths = {name: {'before': measure(files, BASELINE), 'after': measure(files)} for name, files in PATHS.items()}
    return {'baseline': BASELINE, 'unit': 'Unicode whitespace split; full file including code/frontmatter; no token estimate',
            'scope': 'Đường khởi đầu M phổ biến; reference mở theo quyết định chưa tính là đã đọc. Native/redesign lớn có đường đọc riêng, không gán mục tiêu M cho mọi tác vụ.',
            'paths': paths, 'status': 'PASS' if all(item['after']['total'] < 8000 for item in paths.values()) else 'FAIL'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text, encoding='utf8')
    for name, item in data['paths'].items():
        print(f"{name}: {item['before']['total']} → {item['after']['total']} đơn vị whitespace")
    raise SystemExit(0 if data['status'] == 'PASS' else 1)

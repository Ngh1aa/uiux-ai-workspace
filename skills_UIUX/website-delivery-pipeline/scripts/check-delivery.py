#!/usr/bin/env python3
"""Print a pending lifecycle template, or verify existing record files. No writes or LLM calls."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'uiux-factory'))
from core.runtime.flow_os.safe_read import SafeReader
from core.skills.website_delivery import check_delivery, delivery_template


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['research', 'design', 'implementation', 'qa'])
    parser.add_argument('--template', action='store_true')
    parser.add_argument('--goal', default='')
    parser.add_argument('--root', type=Path)
    parser.add_argument('--report', help='Path relative to --root; existing UTF-8 JSON')
    args = parser.parse_args()
    if args.template:
        if not args.stage:
            parser.error('--template requires --stage')
        result = delivery_template(ROOT / 'skills_UIUX', args.stage, {'goal': args.goal})
    else:
        if not args.root or not args.report:
            parser.error('checking requires --root and --report')
        try:
            report = json.loads(SafeReader(args.root).read_text(args.report).content)
            result = check_delivery(ROOT / 'skills_UIUX', args.root, report)
        except (OSError, ValueError, TypeError) as exc:
            result = {'status': 'BLOCKED', 'errors': [str(exc)], 'returncode': 1}
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result.get('returncode', 0)


if __name__ == '__main__':
    raise SystemExit(main())

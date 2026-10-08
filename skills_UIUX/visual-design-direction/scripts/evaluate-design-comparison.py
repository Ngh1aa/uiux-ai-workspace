#!/usr/bin/env python3
"""Prepare a labelled review or summarize real recorded direction observations."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'uiux-factory'))
from core.skills.design_comparison import prepare_comparison, evaluate_comparison, read_comparison_json


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--contract', default='docs/uiux/design-decisions.json')
    parser.add_argument('--route')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--plan', help='Project-relative prepared plan; requires --observations')
    parser.add_argument('--observations', help='Project-relative observation file; no provider calls')
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        payload = read_comparison_json(root, args.contract)
        if args.plan or args.observations:
            if not (args.plan and args.observations):
                parser.error('--plan and --observations must be supplied together')
            result = evaluate_comparison(payload, read_comparison_json(root, args.plan), read_comparison_json(root, args.observations), root)
        else:
            if not args.route:
                parser.error('--route is required to prepare a comparison')
            result = prepare_comparison(payload, args.route, args.seed)
    except (ValueError, OSError) as error:
        result = {'status': 'FAIL', 'returncode': 1, 'errors': [str(error)], 'human_preference': 'UNKNOWN'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result.get('returncode', 0)


if __name__ == '__main__':
    raise SystemExit(main())

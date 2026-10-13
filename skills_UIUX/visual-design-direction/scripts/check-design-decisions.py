#!/usr/bin/env python3
"""Check one project decision contract; exit status is integrity, never beauty."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'uiux-factory'))
from core.skills.design_decisions import DesignDecisions, check_design_file


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--contract', default='docs/uiux/design-decisions.json')
    parser.add_argument('--phase', choices=['design','rendered'], default='design')
    parser.add_argument('--schema', action='store_true')
    args = parser.parse_args()
    if args.schema:
        print(json.dumps(DesignDecisions.model_json_schema(), ensure_ascii=False, indent=2))
        return 0
    if args.root is None:
        parser.error('--root is required unless --schema is supplied')
    try:
        result = check_design_file(args.root, args.contract, args.phase)
    except (ValueError, OSError) as error:
        result = {'status':'FAIL','returncode':1,'errors':[str(error)],'aesthetic_quality':'UNKNOWN'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result['returncode']


if __name__ == '__main__':
    raise SystemExit(main())

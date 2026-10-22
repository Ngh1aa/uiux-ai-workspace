#!/usr/bin/env python3
"""Check a UX structure record (U1 to U6). Exit status is structural integrity, never usability."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'uiux-factory'))
from core.skills.ux_structure import UXStructure, check_ux_structure_file, export_page_ux  # noqa: E402


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, help='target project root')
    parser.add_argument('--contract', default='docs/ux/ux-structure.json')
    parser.add_argument('--schema', action='store_true', help='print the JSON schema and exit')
    parser.add_argument('--export-page-ux', metavar='EVIDENCE_REF',
                        help='print pages[].ux blocks for the visual decision contract (gate must PASS)')
    args = parser.parse_args()
    if args.schema:
        print(json.dumps(UXStructure.model_json_schema(), ensure_ascii=False, indent=2))
        return 0
    if args.root is None:
        parser.error('--root is required unless --schema is supplied')
    try:
        if args.export_page_ux:
            text = (args.root / args.contract).read_text(encoding='utf-8')
            print(json.dumps(export_page_ux(json.loads(text), args.export_page_ux), ensure_ascii=False, indent=2))
            return 0
        result = check_ux_structure_file(args.root, args.contract)
    except (ValueError, OSError) as error:
        result = {'status': 'FAIL', 'returncode': 1, 'verdict': 'UNKNOWN', 'errors': [str(error)], 'usability': 'UNKNOWN'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result['returncode']


if __name__ == '__main__':
    raise SystemExit(main())

"""Bounded lifecycle work cards and read-only record integrity. Never a quality gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.runtime.flow_os.safe_read import SafeReader

CATALOG = 'website-delivery-pipeline/data/lifecycle.json'
MOBILE_CATALOG = 'mobile-app-design/data/lifecycle.json'
CHECKER = 'skills_UIUX/website-delivery-pipeline/scripts/check-delivery.py'


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def delivery_packet(skills_root: Path, stage: str, context: dict[str, Any]) -> dict[str, Any]:
    if context.get('change_surface') in {'MICRO', 'FOCUSED'}:
        return {'active': False, 'stage': stage, 'reason': 'Bounded change: use the resolved Flow and existing project artifacts, not a whole-site deliverable set.'}
    catalog_path = MOBILE_CATALOG if context.get('platform_family') == 'mobile_app' else CATALOG
    catalog = json.loads(SafeReader(skills_root).read_text(catalog_path).content)
    if catalog.get('schema_version') != '1.0':
        raise ValueError('unsupported website lifecycle catalog')
    card = catalog['stages'].get(stage)
    if context.get('platform_family') == 'mobile_app' and context.get('requested_output') == 'browser-prototype':
        card = catalog.get('browser_preview_stages', {}).get(stage, card)
    if card is None:
        return {'active': False, 'stage': stage, 'reason': 'No lifecycle card for this Flow stage; use its routed skills.'}
    baseline = ('Existing project: inspect source and rendered UI; preserve explicit invariants and uncommitted work.'
                if context.get('intent') in {'redesign', 'rebuild', 'improve', 'fix', 'polish'}
                else 'Confirm whether a baseline exists; build does not imply greenfield. Record absent content/brand/data as UNKNOWN.')
    return {'active': True, 'stage': stage, 'owner': catalog['owner'],
            'source': 'skills_UIUX/' + catalog_path, 'catalog_sha256': _digest(catalog),
            'baseline_rule': baseline, 'mode': context.get('mode', 'unresolved'), **card,
            'checker': CHECKER, 'human_validation': 'UNKNOWN', 'aesthetic_quality': 'UNKNOWN',
            'gate_effect': 'none', 'authority_effect': 'none',
            'rule': 'Use the active card only. Reuse existing project artifacts; one file may serve several deliverables. '
                    'Load linked resources only for unresolved decisions. RECORDED_CURRENT proves file integrity, '
                    'not content quality, human validation, approval or stage completion. Existing Flow gates remain required.'}


def delivery_template(skills_root: Path, stage: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    packet = delivery_packet(skills_root, stage, context)
    if not packet['active']:
        raise ValueError(f'unsupported lifecycle stage: {stage}')
    return {'schema_version': '1.0', 'stage': stage, 'context': context,
            'context_sha256': _digest(context), 'catalog_sha256': packet['catalog_sha256'],
            'items': [{'id': item['id'], 'status': 'PENDING', 'rationale': '', 'evidence': []}
                      for item in packet['deliverables']]}


def check_delivery(skills_root: Path, project_root: Path, report: dict[str, Any]) -> dict[str, Any]:
    """File coverage only. Context hash detects edits, not authenticity/authority.

    Caller must compare context to the current task and inspect evidence content.
    A recorded artifact can still contain a bad decision or an untested hypothesis.
    """
    errors: list[str] = []
    review: list[str] = []
    try:
        if not isinstance(report, dict) or report.get('schema_version') != '1.0' or not isinstance(report.get('context'), dict):
            raise ValueError('invalid lifecycle report version/context')
        packet = delivery_packet(skills_root, report.get('stage', ''), report['context'])
        if not packet['active']:
            raise ValueError('unknown lifecycle stage')
        if report.get('context_sha256') != _digest(report['context']):
            errors.append('context changed; regenerate the record for the current task')
        if report.get('catalog_sha256') != packet['catalog_sha256']:
            errors.append('lifecycle catalog changed; review the current deliverables')
        expected = {item['id'] for item in packet['deliverables']}
        items = report.get('items')
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise ValueError('items must be a list of records')
        ids = [item.get('id') for item in items]
        if any(not isinstance(key, str) for key in ids) or set(ids) != expected or len(ids) != len(expected):
            raise ValueError('missing, duplicate or unknown deliverables')
        reader = SafeReader(project_root)
        for item in items:
            key, status = item['id'], item.get('status')
            if status in {'NA_JUSTIFIED', 'DEFERRED'}:
                if not isinstance(item.get('rationale'), str) or not item['rationale'].strip():
                    errors.append(f'{key}: rationale required')
                review.append(f'{key}: {status} requires operator review; not verified completion')
            elif status != 'RECORDED':
                errors.append(f'{key}: not recorded ({status})')
            else:
                refs = item.get('evidence')
                if not isinstance(refs, list) or not refs:
                    errors.append(f'{key}: current evidence files required')
                    continue
                for ref in refs:
                    if not isinstance(ref, dict) or not isinstance(ref.get('path'), str):
                        raise ValueError(f'{key}: malformed evidence reference')
                    path = Path(ref['path'])
                    if path.is_absolute() or '..' in path.parts:
                        raise ValueError(f'{key}: evidence must remain inside project root')
                    loaded = reader.read_text(ref['path'])
                    if not loaded.content.strip() or ref.get('sha256') != hashlib.sha256(loaded.path.read_bytes()).hexdigest():
                        errors.append(f'{key}: empty or stale evidence: {ref["path"]}')
    except (ValueError, TypeError, OSError, KeyError) as exc:
        errors.append(str(exc))
    return {'schema_version': '1.0', 'status': 'BLOCKED' if errors else 'NEEDS_REVIEW' if review else 'RECORDED_CURRENT',
            'errors': errors, 'review_required': review, 'human_validation': 'UNKNOWN',
            'aesthetic_quality': 'UNKNOWN', 'gate_effect': 'none', 'authority_effect': 'none',
            'boundary': 'File coverage and freshness only. Inspect content, current task context and runtime gates separately.',
            'returncode': 1 if errors else 2 if review else 0}

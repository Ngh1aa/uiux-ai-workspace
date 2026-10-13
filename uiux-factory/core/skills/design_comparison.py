"""Counterbalanced direction review. Recorded judgments are not causal evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import random
from typing import Literal

from pydantic import Field, ValidationError

from core.runtime.flow_os.safe_read import SafeReader
from core.skills.design_decisions import DesignDecisions, StrictModel, check_design_decisions


def digest(value: dict) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()


def prepare_comparison(payload: dict, route: str, seed: int = 0) -> dict:
    contract = DesignDecisions.model_validate(payload)
    if contract.schema_version != '2.0':
        raise ValueError('direction review requires v2; a legacy layout comparison is not multi-axis evidence')
    page = next((item for item in contract.pages if item.route == route), None)
    if page is None or page.comparison_protocol is None:
        raise ValueError('route must own a representative comparison protocol')
    ids = [item.id for item in page.compositions]
    random.Random(seed).shuffle(ids)
    labels = {chr(65 + index): value for index, value in enumerate(ids)}
    questions = page.comparison_protocol.questions
    return {
        'schema_version': '1.0', 'contract_sha256': digest(payload), 'route': route, 'seed': seed,
        'facilitator': {'labels': labels, 'protocol': page.comparison_protocol.model_dump(),
                        'captures': [item.model_dump() for item in contract.captures if item.route == route],
                        'ordering': 'Assign contiguous session_index from zero; rotate label order by seed + session index. This balances first exposure within one cohort.'},
        'reviewer': {'buyer_task': page.comparison_protocol.buyer_task,
                     'labels': list(labels),
                     'questions': [{'id': item.id, 'dimension': item.dimension, 'prompt': item.prompt} for item in questions],
                     'instruction': 'Show only this reviewer packet and anonymously labelled captures. Answer before seeing another candidate. Do not disclose answer criteria or author preference.'},
        'status': 'PLANNED_VALIDATION', 'human_preference': 'UNKNOWN', 'causal_effect': 'UNKNOWN',
        'boundary': 'Labels do not prove blinding. A facilitator who also authored or grades the candidates must report heuristic review. Human provenance remains a reviewer declaration.',
    }


def reviewer_order(plan: dict, reviewer_id: str, session_index: int = 0) -> list[str]:
    labels = list(plan['reviewer']['labels'])
    if not reviewer_id.strip() or session_index < 0:
        raise ValueError('reviewer id and nonnegative session index required')
    # Rotation is actually balanced for consecutive sessions; hashing reviewer ids
    # merely randomized order and could assign both participants the same first label.
    offset = (plan['seed'] + session_index) % len(labels)
    return labels[offset:] + labels[:offset]


class Answer(StrictModel):
    label: str = Field(min_length=1, max_length=1)
    question_id: str = Field(min_length=1, max_length=80)
    response: str = Field(min_length=1, max_length=3000)
    criteria_met: list[bool] = Field(min_length=1, max_length=8)
    observed_element: str = Field(min_length=1, max_length=1000)
    capture_sha256: str = Field(pattern=r'^[a-f0-9]{64}$')


class ReviewerObservation(StrictModel):
    reviewer_id: str = Field(min_length=1, max_length=80)
    role: str = Field(min_length=1, max_length=200)
    source: Literal['agent-heuristic', 'human']
    independent: bool
    session_index: int = Field(default=0, ge=0, le=1000)
    presentation_order: list[str] = Field(min_length=2, max_length=5)
    answers: list[Answer] = Field(min_length=4, max_length=50)
    preferred_label: str | None = None
    tradeoff: str = Field(min_length=1, max_length=3000)


class Observations(StrictModel):
    schema_version: Literal['1.0']
    plan_sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    reviews: list[ReviewerObservation] = Field(default_factory=list, max_length=100)


def evaluate_comparison(payload: dict, plan: dict, observations: dict, root: Path, *, _capture_integrity_verified: bool = False) -> dict:
    errors = []
    try:
        expected_plan = prepare_comparison(payload, plan['route'], plan['seed'])
        if plan != expected_plan:
            raise ValueError('plan does not match current contract; regenerate after a design/capture change')
        records = Observations.model_validate(observations)
        if records.plan_sha256 != digest(plan):
            raise ValueError('observations reference a different plan')
    except (ValueError, ValidationError, KeyError, TypeError) as error:
        return {'status': 'FAIL', 'returncode': 1, 'errors': [str(error)], 'human_preference': 'UNKNOWN', 'causal_effect': 'UNKNOWN'}
    if not records.reviews:
        return {'status': 'PLANNED_VALIDATION', 'returncode': 0, 'review_count': 0, 'errors': [], 'human_preference': 'UNKNOWN', 'causal_effect': 'UNKNOWN'}
    if not _capture_integrity_verified:
        rendered = check_design_decisions(payload, phase='rendered', project_root=root)
        errors.extend(rendered['errors'])
    labels = plan['facilitator']['labels']
    questions = {item['id']: item for item in plan['facilitator']['protocol']['questions']}
    expected_pairs = {(label, question) for label in labels for question in questions}
    ids = [item.reviewer_id for item in records.reviews]
    if len(ids) != len(set(ids)):
        errors.append('reviewer ids must be unique; repeated observations are not independent participants')
    if sorted(item.session_index for item in records.reviews) != list(range(len(records.reviews))):
        errors.append('session indices must be contiguous and unique for counterbalancing')
    # Separate human and heuristic totals; never blend synthetic reviewers into a user count.
    totals = {source: {label: {dimension: {'met': 0, 'total': 0} for dimension in ('comprehension', 'distinctiveness')}
                      for label in labels} for source in ('agent-heuristic', 'human')}
    for record in records.reviews:
        if record.source == 'agent-heuristic' and record.independent:
            errors.append('agent heuristic cannot claim independent human validation')
        if record.presentation_order != reviewer_order(plan, record.reviewer_id, record.session_index):
            errors.append(f'{record.reviewer_id}: presentation order disagrees with counterbalanced plan')
        pairs = [(item.label, item.question_id) for item in record.answers]
        if len(pairs) != len(set(pairs)) or set(pairs) != expected_pairs:
            errors.append(f'{record.reviewer_id}: provide exactly one answer per label/question')
        if record.preferred_label is not None and record.preferred_label not in labels:
            errors.append('preferred label must exist')
        for answer in record.answers:
            question = questions.get(answer.question_id)
            if question is None or answer.label not in labels:
                continue
            if len(answer.criteria_met) != len(question['criteria']):
                errors.append('criteria grading length disagrees with predeclared question')
                continue
            capture_matches = [item for item in plan['facilitator']['captures']
                               if item['composition_id'] == labels[answer.label] and item['sha256'] == answer.capture_sha256]
            if not capture_matches:
                errors.append('answer must point to an inspected capture of its labelled candidate')
            total = totals[record.source][answer.label][question['dimension']]
            total['met'] += sum(answer.criteria_met)
            total['total'] += len(answer.criteria_met)
    human_count = sum(item.source == 'human' for item in records.reviews)
    return {
        'status': 'FAIL' if errors else 'RECORDED_HUMAN_REVIEW' if human_count else 'HEURISTIC_ONLY',
        'returncode': 1 if errors else 0, 'errors': errors,
        'review_count': len(records.reviews), 'human_review_count': human_count,
        'heuristic_review_count': len(records.reviews) - human_count,
        'criterion_totals': totals if not errors else {},
        'preferences': [{'reviewer_id': item.reviewer_id, 'source': item.source, 'label': item.preferred_label, 'tradeoff': item.tradeoff} for item in records.reviews] if not errors else [],
        'human_preference': 'RECORDED_NOT_INDEPENDENTLY_AUTHENTICATED' if human_count and not errors else 'UNKNOWN',
        'aesthetic_quality': 'UNKNOWN', 'causal_effect': 'UNKNOWN',
        'interpretation': 'Criterion counts summarize recorded judgments, not a beauty score. Report comprehension regressions and domain cues separately; multi-axis direction selection cannot identify which axis caused an effect. No automatic winner or human research claim.',
    }


def read_comparison_json(root: Path, path: str) -> dict:
    text = SafeReader(root).read_text(path).content
    if len(text) > 512_000:
        raise ValueError('comparison JSON exceeds 512000 chars')
    return json.loads(text)

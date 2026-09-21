import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from taste_cache_common import validate_taste_factors

ROOT = Path('.')
CONTRACT = ROOT / 'config/progressive_pass1_contract.json'
STATE = ROOT / 'data/cache/progressive_pass1_state.json'
WORK = ROOT / 'data/production/pre_ai/progressive_pass1_work.json'
PROGRESSIVE_CONTEXT = ROOT / 'data/production/pre_ai/progressive_candidate_context.jsonl'
TASTE_QUEUE = ROOT / 'data/production/pre_ai/chatgpt_taste_queue.jsonl'
TASTE_PROJECTION = ROOT / 'data/production/pre_ai/taste_projection.json'

FIT_LEVELS = {'strong', 'moderate'}
CONFIDENCE = {'medium', 'high'}
NOT_FIT_BASES = {'completed_below_threshold', 'confirmed_personal_negative'}
INCOMPLETE_CODES = {
    'insufficient_evidence',
    'evidence_unavailable',
    'worker_failure',
    'invalid_semantic_result',
    'base_support_unresolved',
}
OUTCOMES = {'analyzed_fit', 'analyzed_not_fit', 'analysis_incomplete'}
IDENTITY_FIELDS = (
    'semantic_generation_id',
    'work_id',
    'family_id',
    'taste_subject_key',
    'appid',
    'taste_fingerprint',
    'candidate_context_sha256',
)
FORBIDDEN_COMMERCIAL_TEXT = (
    'price', 'discount', 'wishlist', 'steamdb', 'sale price', 'historical price',
    'rub', 'kzt', 'цена', 'скидк', 'вишлист', 'руб', 'тенге',
)


def load_json(path):
    path = Path(path)
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


def load_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding='utf-8').splitlines()
        if line.strip()
    ]


def canonical_sha256(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def load_contract(path=CONTRACT):
    contract = load_json(path)
    if contract.get('contract') != 'PROGRESSIVE-PASS1-V1':
        raise ValueError('progressive PASS 1 contract mismatch')
    if contract.get('status') != 'canonical' or contract.get('phase') != 'phase_b_pass1':
        raise ValueError('progressive PASS 1 contract is not canonical Phase B')
    if (contract.get('pass2') or {}).get('active') is not False:
        raise ValueError('PASS 2 must remain inactive')
    budget = contract.get('attempt_budget') or {}
    if budget.get('maximum_attempts_per_work_id') != 1 or budget.get('automatic_pass1_retry') is not False:
        raise ValueError('PASS 1 one-attempt budget mismatch')
    transport = contract.get('transport') or {}
    if transport.get('one_result_artifact_per_item') is not True or transport.get('batch_atomicity') is not False:
        raise ValueError('PASS 1 transport must be item-level')
    return contract


def load_state(path=None):
    path = STATE if path is None else path
    doc = load_json(path)
    if not doc:
        return {'schema_version': 1, 'contract': 'PROGRESSIVE-PASS1-STATE-V1', 'entries': {}}
    if doc.get('schema_version') != 1 or doc.get('contract') != 'PROGRESSIVE-PASS1-STATE-V1':
        raise ValueError('progressive PASS 1 state schema mismatch')
    if not isinstance(doc.get('entries'), dict):
        raise ValueError('progressive PASS 1 entries must be an object')
    return doc


def semantic_generation(projection_doc=None):
    projection_doc = projection_doc if projection_doc is not None else load_json(TASTE_PROJECTION)
    profile = projection_doc.get('current_profile') or {}
    binding = projection_doc.get('current_binding') or {}
    material = {
        'profile_blob_sha': profile.get('blob_sha'),
        'taste_model_version': binding.get('taste_model_version'),
        'taste_semantics_sha256': binding.get('taste_semantics_sha256'),
        'candidate_context_contract_blob_sha': binding.get('candidate_context_contract_blob_sha'),
    }
    missing = [key for key, value in material.items() if not isinstance(value, str) or not value]
    if missing:
        raise ValueError(f'missing PASS 1 semantic generation bindings: {missing}')
    return {
        'semantic_generation_id': canonical_sha256(material),
        'bindings': material,
    }


def _queue_indexes(queue_rows):
    by_family = {}
    by_taste = {}
    for row in queue_rows:
        family_id = str(row.get('family_id') or '')
        taste_key = str(row.get('taste_subject_key') or '')
        if not family_id or not taste_key:
            raise ValueError('PASS 1 semantic queue row missing family/taste identity')
        if family_id in by_family or taste_key in by_taste:
            raise ValueError('PASS 1 semantic queue contains duplicate family/taste identity')
        by_family[family_id] = row
        by_taste[taste_key] = row
    return by_family, by_taste


def current_bindings(context_rows=None, projection_doc=None, queue_rows=None):
    context_rows = context_rows if context_rows is not None else load_jsonl(PROGRESSIVE_CONTEXT)
    projection_doc = projection_doc if projection_doc is not None else load_json(TASTE_PROJECTION)
    queue_rows = queue_rows if queue_rows is not None else load_jsonl(TASTE_QUEUE)
    generation = semantic_generation(projection_doc)
    by_family, by_taste = _queue_indexes(queue_rows)
    bindings = {}
    queue_by_family = {}

    for context in context_rows:
        family_id = str(context.get('family_id') or '')
        taste_key = str(context.get('taste_subject_key') or '')
        if not family_id or not taste_key:
            raise ValueError('progressive candidate missing family/taste identity')
        queue_row = by_family.get(family_id) or by_taste.get(taste_key)
        if queue_row is None:
            continue
        if str(queue_row.get('family_id')) != family_id or str(queue_row.get('taste_subject_key')) != taste_key:
            raise ValueError(f'PASS 1 queue/context identity mismatch for {family_id}')
        item_material = {
            'semantic_generation_id': generation['semantic_generation_id'],
            'family_id': family_id,
            'taste_subject_key': taste_key,
            'appid': str(queue_row.get('appid') or ''),
            'taste_fingerprint': queue_row.get('taste_fingerprint'),
            'candidate_context_sha256': queue_row.get('candidate_context_sha256'),
        }
        missing = [key for key, value in item_material.items() if not isinstance(value, str) or not value]
        if missing:
            raise ValueError(f'PASS 1 work binding missing fields for {family_id}: {missing}')
        work_id = canonical_sha256(item_material)
        bindings[family_id] = {**item_material, 'work_id': work_id}
        queue_by_family[family_id] = queue_row

    return generation, bindings, queue_by_family


def matching_state_entry(binding, state_doc=None):
    if not binding:
        return None
    state_doc = state_doc if state_doc is not None else load_state()
    entry = (state_doc.get('entries') or {}).get(binding['family_id'])
    if not isinstance(entry, dict):
        return None
    if any(str(entry.get(field) or '') != str(binding.get(field) or '') for field in IDENTITY_FIELDS):
        return None
    if entry.get('pass1_attempted') is not True:
        return None
    return entry


def project_state(binding, state_doc=None):
    entry = matching_state_entry(binding, state_doc)
    if entry is None:
        return None
    outcome = entry.get('outcome')
    if outcome == 'analyzed_fit':
        return {
            'analysis_state': 'analyzed_fit',
            'analysis_tier': 1,
            'analysis_issue_code': None,
            'fit': entry.get('fit_level'),
            'evaluated_at_utc': entry.get('accepted_at_utc'),
            'analysis_semantic_source': 'progressive_pass1',
            'semantic_generation_id': entry.get('semantic_generation_id'),
            'pass1_attempted': True,
        }
    if outcome == 'analyzed_not_fit':
        return {
            'analysis_state': 'analyzed_not_fit',
            'analysis_tier': None,
            'analysis_issue_code': None,
            'fit': None,
            'evaluated_at_utc': entry.get('accepted_at_utc'),
            'analysis_semantic_source': 'progressive_pass1',
            'semantic_generation_id': entry.get('semantic_generation_id'),
            'pass1_attempted': True,
        }
    if outcome == 'analysis_incomplete':
        return {
            'analysis_state': 'analysis_incomplete',
            'analysis_tier': 2,
            'analysis_issue_code': entry.get('analysis_issue_code') or 'invalid_semantic_result',
            'fit': None,
            'evaluated_at_utc': entry.get('accepted_at_utc'),
            'analysis_semantic_source': 'progressive_pass1',
            'semantic_generation_id': entry.get('semantic_generation_id'),
            'pass1_attempted': True,
        }
    raise ValueError(f'unknown PASS 1 persisted outcome: {outcome!r}')


def semantic_taste_entry(entry):
    if not isinstance(entry, dict) or entry.get('outcome') != 'analyzed_fit':
        return {}
    return {
        'key': entry.get('taste_subject_key'),
        'appid': entry.get('appid'),
        'verdict': 'INCLUDE',
        'fit_level': entry.get('fit_level'),
        'reason_code': 'progressive_pass1_candidate_specific_fit',
        'taste_fingerprint': entry.get('taste_fingerprint'),
        'candidate_context_sha256': entry.get('candidate_context_sha256'),
        'positive_evidence': list(entry.get('positive_evidence') or []),
        'negative_analysis_status': 'incomplete_no_confirmed_negative',
        'negative_findings': [],
        'negative_evidence': [],
        'taste_factors': dict(entry.get('taste_factors') or {}),
        'fit_evidence_state': 'sufficient',
        'fit_evidence_confidence': entry.get('confidence') or 'medium',
        'fit_evidence_basis': ['candidate_specific_positive_match'],
        'historical_negative_context': None,
        'candidate_quality_findings': [],
        'evaluated_at_utc': entry.get('accepted_at_utc'),
        'semantic_source': 'progressive_pass1',
        'semantic_generation_id': entry.get('semantic_generation_id'),
    }


def current_fit_semantic_entries(context_rows=None, projection_doc=None, queue_rows=None, state_doc=None):
    context_rows = context_rows if context_rows is not None else load_jsonl(PROGRESSIVE_CONTEXT)
    projection_doc = projection_doc if projection_doc is not None else load_json(TASTE_PROJECTION)
    queue_rows = queue_rows if queue_rows is not None else load_jsonl(TASTE_QUEUE)
    state_doc = state_doc if state_doc is not None else load_state()
    _generation, bindings, _queue = current_bindings(context_rows, projection_doc, queue_rows)
    out = {}
    for family_id, binding in bindings.items():
        entry = matching_state_entry(binding, state_doc)
        if entry and entry.get('outcome') == 'analyzed_fit':
            out[binding['taste_subject_key']] = semantic_taste_entry(entry)
    return out


def _validate_text_list(name, values, *, require_nonempty):
    if not isinstance(values, list):
        raise ValueError(f'{name} must be an array')
    if require_nonempty and not values:
        raise ValueError(f'{name} must not be empty')
    normalized = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{name}[{index}] must be non-empty text')
        text = ' '.join(value.strip().split())
        folded = text.casefold()
        hit = next((fragment for fragment in FORBIDDEN_COMMERCIAL_TEXT if fragment in folded), None)
        if hit is not None:
            raise ValueError(f'{name}[{index}] contains forbidden commercial evidence fragment: {hit!r}')
        normalized.append(text)
    return normalized


def identity_matches_submission(doc, work_item):
    if not isinstance(doc, dict):
        return False
    if doc.get('schema_version') != 1 or doc.get('contract') != 'PROGRESSIVE-PASS1-RESULT-V1':
        return False
    return all(str(doc.get(field) or '') == str(work_item.get(field) or '') for field in IDENTITY_FIELDS)


def normalize_submission(doc, work_item, accepted_at_utc=None):
    if not identity_matches_submission(doc, work_item):
        raise ValueError('submission identity does not exactly match prepared PASS 1 work')
    outcome = doc.get('outcome')
    if outcome not in OUTCOMES:
        raise ValueError(f'unknown PASS 1 outcome: {outcome!r}')

    accepted_at_utc = accepted_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    base = {
        field: work_item[field]
        for field in IDENTITY_FIELDS
    }
    base.update({
        'pass1_attempted': True,
        'outcome': outcome,
        'analysis_issue_code': None,
        'accepted_at_utc': accepted_at_utc,
    })

    if outcome == 'analyzed_fit':
        fit_level = doc.get('fit_level')
        confidence = doc.get('confidence')
        if fit_level not in FIT_LEVELS:
            raise ValueError('analyzed_fit requires strong/moderate fit_level')
        if confidence not in CONFIDENCE:
            raise ValueError('analyzed_fit requires medium/high confidence')
        evidence = _validate_text_list('positive_evidence', doc.get('positive_evidence'), require_nonempty=True)
        factors = doc.get('taste_factors')
        validate_taste_factors(factors)
        requires_base = bool(((work_item.get('semantic_input') or {}).get('semantic_condition') or {}).get('requires_ai_base_support'))
        if requires_base and doc.get('base_support_compatible') is not True:
            raise ValueError('analyzed_fit addon requires explicit base_support_compatible=true')
        base.update({
            'fit_level': fit_level,
            'confidence': confidence,
            'positive_evidence': evidence,
            'taste_factors': deepcopy(factors),
            'base_support_compatible': True if requires_base else None,
        })
        return base

    if outcome == 'analyzed_not_fit':
        confidence = doc.get('confidence')
        basis = doc.get('not_fit_basis')
        if confidence not in CONFIDENCE:
            raise ValueError('analyzed_not_fit requires medium/high confidence')
        if basis not in NOT_FIT_BASES:
            raise ValueError('analyzed_not_fit requires a completed not-fit basis')
        if basis == 'confirmed_personal_negative' and confidence != 'high':
            raise ValueError('confirmed personal negative requires high confidence')
        evidence = _validate_text_list('not_fit_evidence', doc.get('not_fit_evidence'), require_nonempty=True)
        base.update({
            'confidence': confidence,
            'not_fit_basis': basis,
            'not_fit_evidence': evidence,
        })
        return base

    issue = doc.get('issue_code')
    if issue not in INCOMPLETE_CODES - {'invalid_semantic_result'}:
        raise ValueError('worker-returned analysis_incomplete has unsupported issue_code')
    base['analysis_issue_code'] = issue
    return base


def invalid_result_entry(work_item, accepted_at_utc=None):
    accepted_at_utc = accepted_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        **{field: work_item[field] for field in IDENTITY_FIELDS},
        'pass1_attempted': True,
        'outcome': 'analysis_incomplete',
        'analysis_issue_code': 'invalid_semantic_result',
        'accepted_at_utc': accepted_at_utc,
    }


def process_submission_documents(work_doc, state_doc, documents, accepted_at_utc=None):
    """Process independent item artifacts without sibling rollback.

    documents is an iterable of (artifact_name, parsed_doc_or_none, parse_error_or_none).
    Publishing the exact deterministic current item path consumes that item's one
    PASS 1 attempt even when the semantic payload is malformed. Artifacts outside
    current prepared paths are stale/unbound and never mutate current state.
    """
    state = deepcopy(state_doc)
    state.setdefault('entries', {})
    work_items = {
        item.get('work_id'): item
        for item in (work_doc.get('items') or [])
        if isinstance(item, dict) and item.get('work_id')
    }
    work_by_name = {
        Path(item.get('submission_path') or '').name: item
        for item in work_items.values()
        if item.get('submission_path')
    }
    receipts = []

    for artifact_name, doc, parse_error in documents:
        receipt = {'artifact': artifact_name}
        work_item = work_by_name.get(artifact_name)
        if work_item is None:
            work_id = doc.get('work_id') if isinstance(doc, dict) else None
            receipt.update({
                'status': 'rejected_stale_or_mismatched',
                'work_id': work_id,
                'reason': 'artifact_path_not_current',
            })
            receipts.append(receipt)
            continue

        existing = matching_state_entry(work_item, state)
        if existing is not None:
            receipt.update({
                'status': 'replay_ignored',
                'work_id': work_item['work_id'],
                'outcome': existing.get('outcome'),
            })
            receipts.append(receipt)
            continue

        if parse_error is not None or not isinstance(doc, dict):
            entry = invalid_result_entry(work_item, accepted_at_utc=accepted_at_utc)
            state['entries'][work_item['family_id']] = entry
            receipt.update({
                'status': 'accepted_as_incomplete_invalid_result',
                'work_id': work_item['work_id'],
                'family_id': work_item['family_id'],
                'outcome': entry['outcome'],
                'analysis_issue_code': entry['analysis_issue_code'],
                'validation_error': parse_error or 'malformed_json',
            })
            receipts.append(receipt)
            continue

        try:
            if not identity_matches_submission(doc, work_item):
                raise ValueError('submission identity does not exactly match prepared PASS 1 work')
            entry = normalize_submission(doc, work_item, accepted_at_utc=accepted_at_utc)
            status = 'accepted'
        except ValueError as exc:
            entry = invalid_result_entry(work_item, accepted_at_utc=accepted_at_utc)
            status = 'accepted_as_incomplete_invalid_result'
            receipt['validation_error'] = str(exc)

        state['entries'][work_item['family_id']] = entry
        receipt.update({
            'status': status,
            'work_id': work_item['work_id'],
            'family_id': work_item['family_id'],
            'outcome': entry['outcome'],
            'analysis_issue_code': entry.get('analysis_issue_code'),
        })
        receipts.append(receipt)

    return state, receipts

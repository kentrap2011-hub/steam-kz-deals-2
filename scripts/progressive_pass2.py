import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import progressive_pass1
from taste_cache_common import validate_taste_factors


ROOT = Path('.')
CONTRACT = ROOT / 'config/progressive_pass2_contract.json'
STATE = ROOT / 'data/cache/progressive_pass2_state.json'
WORK = ROOT / 'data/production/pre_ai/progressive_pass2_work.json'
DOSSIER_STORE = ROOT / 'data/cache/taste_steam_review_dossiers'
DOSSIER_WORKER_INDEX = ROOT / 'data/production/pre_ai/taste_steam_review_dossier_worker_index.json'
CANONICAL_EXECUTION_RECEIPTS = ROOT / 'data/cache/progressive_pass2_execution_receipts'

FIT_LEVELS = {'strong', 'moderate'}
CONFIDENCE = {'medium', 'high'}
NOT_FIT_BASES = {'completed_below_threshold', 'confirmed_personal_negative'}
INCOMPLETE_CODES = {
    'insufficient_evidence',
    'evidence_unavailable',
    'worker_failure',
    'base_support_unresolved',
    'terminal_execution_failure',
}
TERMINAL_REASONS = set(INCOMPLETE_CODES)
OUTCOMES = {'analyzed_fit', 'analyzed_not_fit', 'analysis_incomplete'}
PASS1_IDENTITY_FIELDS = progressive_pass1.IDENTITY_FIELDS
IMMUTABLE_RESULT_FIELDS = PASS1_IDENTITY_FIELDS + (
    'dossier_content_sha256',
    'authorization_id',
)


def load_json(path):
    path = Path(path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def canonical_sha256(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def parse_utc(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_contract(path=CONTRACT):
    contract = load_json(path)
    if contract.get('contract') != 'PROGRESSIVE-PASS2-V1':
        raise ValueError('progressive PASS 2 contract mismatch')
    if contract.get('implemented') is not True:
        raise ValueError('progressive PASS 2 core is not implemented')
    if contract.get('active') not in {True, False}:
        raise ValueError('progressive PASS 2 active flag must be boolean')
    budget = contract.get('attempt_budget') or {}
    if budget.get('maximum_automatic_attempts_per_semantic_generation_and_work_id') != 1:
        raise ValueError('progressive PASS 2 one-attempt budget mismatch')
    if budget.get('new_dossier_same_budget_key_resets_attempt') is not False:
        raise ValueError('new Dossier must not reset PASS 2 attempt budget')
    transport = contract.get('transport') or {}
    if transport.get('batch_atomicity') is not False or transport.get('maximal_contiguous_prefix') is not False:
        raise ValueError('progressive PASS 2 must remain independent item-level transport')
    return contract


def load_state(path=None):
    path = STATE if path is None else Path(path)
    doc = load_json(path)
    if not doc:
        return {'schema_version': 1, 'contract': 'PROGRESSIVE-PASS2-STATE-V1', 'entries': {}}
    if doc.get('schema_version') != 1 or doc.get('contract') != 'PROGRESSIVE-PASS2-STATE-V1':
        raise ValueError('progressive PASS 2 state schema mismatch')
    if not isinstance(doc.get('entries'), dict):
        raise ValueError('progressive PASS 2 entries must be an object')
    return doc


def current_dossier_binding(index_doc=None):
    index_doc = index_doc if index_doc is not None else load_json(DOSSIER_WORKER_INDEX)
    binding = index_doc.get('web_evidence_contract_binding') if isinstance(index_doc, dict) else None
    if not isinstance(binding, dict) or not binding:
        raise ValueError('current Dossier compatibility binding is missing')
    return deepcopy(binding)


def release_year_from_semantic_input(semantic_input):
    if not isinstance(semantic_input, dict):
        return None
    direct = semantic_input.get('release_year')
    if isinstance(direct, int) and 1900 <= direct <= 2200:
        return direct
    value = semantic_input.get('release_date')
    if not isinstance(value, str):
        return None
    match = re.search(r'\b(19\d{2}|20\d{2}|21\d{2})\b', value)
    return int(match.group(1)) if match else None


def matching_state_entry(binding, state_doc=None):
    if not isinstance(binding, dict):
        return None
    state_doc = state_doc if state_doc is not None else load_state()
    family_id = str(binding.get('family_id') or '')
    entry = (state_doc.get('entries') or {}).get(family_id)
    if not isinstance(entry, dict) or entry.get('pass2_attempted') is not True:
        return None
    for field in PASS1_IDENTITY_FIELDS:
        if str(entry.get(field) or '') != str(binding.get(field) or ''):
            return None
    return entry


def authorization_id(binding, dossier_content_sha256, dossier_compatibility_binding):
    material = {
        'semantic_generation_id': binding.get('semantic_generation_id'),
        'work_id': binding.get('work_id'),
        'appid': binding.get('appid'),
        'dossier_content_sha256': dossier_content_sha256,
        'dossier_compatibility_binding': dossier_compatibility_binding,
    }
    if any(not material.get(key) for key in ('semantic_generation_id', 'work_id', 'appid', 'dossier_content_sha256')):
        raise ValueError('PASS 2 authorization material is incomplete')
    if not isinstance(dossier_compatibility_binding, dict) or not dossier_compatibility_binding:
        raise ValueError('PASS 2 Dossier compatibility binding is missing')
    return canonical_sha256(material)


def _semantic_input(queue_row):
    return {
        'title': queue_row.get('title'),
        'short_description': queue_row.get('short_description'),
        'bundle_members': list(queue_row.get('bundle_members') or []),
        'fit_tags': list(queue_row.get('fit_tags') or []),
        'core_fit_count': int(queue_row.get('core_fit_count') or 0),
        'release_date': queue_row.get('release_date'),
        'release_year': queue_row.get('release_year'),
        'semantic_condition': dict(queue_row.get('semantic_condition') or {}),
    }


def canonical_dossier_loader(appid):
    path = DOSSIER_STORE / f'App_{appid}.json'
    if not path.exists():
        return None
    raw = path.read_bytes()
    try:
        doc = json.loads(raw.decode('utf-8'))
    except Exception:
        return None
    return {
        'path': str(path).replace('\\', '/'),
        'doc': doc,
        'content_sha256': hashlib.sha256(raw).hexdigest(),
    }


def dossier_is_eligible(
    *,
    binding,
    pass1_entry,
    semantic_input,
    dossier_record,
    current_binding,
    pass2_state_doc,
    now=None,
):
    now = now or datetime.now(timezone.utc)

    if not isinstance(pass1_entry, dict) or pass1_entry.get('outcome') != 'analysis_incomplete':
        return False, 'pass1_not_current_analysis_incomplete'
    for field in PASS1_IDENTITY_FIELDS:
        if str(pass1_entry.get(field) or '') != str(binding.get(field) or ''):
            return False, 'pass1_identity_mismatch'
    if matching_state_entry(binding, pass2_state_doc) is not None:
        return False, 'pass2_attempt_already_consumed'
    if not isinstance(dossier_record, dict):
        return False, 'no_canonically_accepted_dossier'

    dossier = dossier_record.get('doc')
    digest = dossier_record.get('content_sha256')
    path = dossier_record.get('path')
    if not isinstance(dossier, dict) or not isinstance(digest, str) or len(digest) != 64 or not path:
        return False, 'canonical_dossier_record_invalid'
    if str(dossier.get('appid') or '') != str(binding.get('appid') or ''):
        return False, 'dossier_wrong_appid'

    identity = dossier.get('game_identity')
    if not isinstance(identity, dict) or identity.get('resolution_status') != 'resolved':
        return False, 'dossier_identity_unresolved_or_ambiguous'
    title = semantic_input.get('title')
    if not isinstance(title, str) or identity.get('work_title') != title:
        return False, 'dossier_wrong_work_title'
    release_year = release_year_from_semantic_input(semantic_input)
    if release_year is not None and identity.get('release_year') != release_year:
        return False, 'dossier_wrong_release_year'

    binding_copy = dossier.get('web_evidence_contract_binding')
    if not isinstance(current_binding, dict) or binding_copy != current_binding:
        return False, 'dossier_compatibility_binding_mismatch'

    expires = parse_utc(dossier.get('expires_at_utc'))
    generated = parse_utc(dossier.get('generated_at_utc'))
    if expires is None or expires <= now:
        return False, 'dossier_expired_or_missing_expiry'
    if generated is None or generated > now:
        return False, 'dossier_generated_at_invalid'

    return True, 'eligible'


def make_work_item(binding, queue_row, dossier_record, current_binding):
    semantic_input = _semantic_input(queue_row)
    digest = dossier_record['content_sha256']
    dossier = dossier_record['doc']
    auth = authorization_id(binding, digest, current_binding)
    prefix = f"{binding['semantic_generation_id'][:16]}--{binding['work_id']}--{auth}"
    return {
        **binding,
        'semantic_input': semantic_input,
        'dossier_path': dossier_record['path'],
        'dossier_content_sha256': digest,
        'dossier_compatibility_binding': deepcopy(current_binding),
        'dossier_expires_at_utc': dossier['expires_at_utc'],
        'authorization_id': auth,
        'result_submission_path': f'data/ai_inbox/progressive_pass2/results/{prefix}.json',
        'terminal_execution_submission_path': (
            f'data/ai_inbox/progressive_pass2/execution_receipts/{prefix}.json'
        ),
    }


def recompute_eligibility(
    *,
    context_rows,
    projection_doc,
    queue_rows,
    pass1_state_doc,
    pass2_state_doc,
    current_binding,
    dossier_loader=canonical_dossier_loader,
    now=None,
):
    now = now or datetime.now(timezone.utc)
    generation, bindings, queue_by_family = progressive_pass1.current_bindings(
        context_rows,
        projection_doc,
        queue_rows,
    )
    items = []
    counts = {
        'current_analysis_incomplete_count': 0,
        'dossier_waiting_count': 0,
        'pass2_attempted_count': 0,
        'pass2_eligible_count': 0,
    }
    reasons = {}

    for context in context_rows:
        family_id = str(context.get('family_id') or '')
        binding = bindings.get(family_id)
        if binding is None:
            continue
        pass1_entry = progressive_pass1.matching_state_entry(binding, pass1_state_doc)
        if pass1_entry is None or pass1_entry.get('outcome') != 'analysis_incomplete':
            continue

        counts['current_analysis_incomplete_count'] += 1
        if matching_state_entry(binding, pass2_state_doc) is not None:
            counts['pass2_attempted_count'] += 1
            reasons[family_id] = 'pass2_attempt_already_consumed'
            continue

        queue_row = queue_by_family.get(family_id) or {}
        semantic_input = _semantic_input(queue_row)
        dossier_record = dossier_loader(binding['appid'])
        eligible, reason = dossier_is_eligible(
            binding=binding,
            pass1_entry=pass1_entry,
            semantic_input=semantic_input,
            dossier_record=dossier_record,
            current_binding=current_binding,
            pass2_state_doc=pass2_state_doc,
            now=now,
        )
        reasons[family_id] = reason
        if not eligible:
            counts['dossier_waiting_count'] += 1
            continue

        items.append(make_work_item(binding, queue_row, dossier_record, current_binding))

    counts['pass2_eligible_count'] = len(items)
    return {
        'semantic_generation_id': generation['semantic_generation_id'],
        'semantic_bindings': generation['bindings'],
        'items': items,
        'counts': counts,
        'reasons': reasons,
    }


def _identity_matches(doc, work_item, contract_name):
    if not isinstance(doc, dict):
        return False
    if doc.get('schema_version') != 1 or doc.get('contract') != contract_name:
        return False
    for field in IMMUTABLE_RESULT_FIELDS:
        if str(doc.get(field) or '') != str(work_item.get(field) or ''):
            return False
    return doc.get('dossier_compatibility_binding') == work_item.get('dossier_compatibility_binding')


def normalize_result(doc, work_item, accepted_at_utc=None):
    if not _identity_matches(doc, work_item, 'PROGRESSIVE-PASS2-RESULT-V1'):
        raise ValueError('PASS 2 result identity does not exactly match prepared work')
    outcome = doc.get('outcome')
    if outcome not in OUTCOMES:
        raise ValueError(f'unknown PASS 2 outcome: {outcome!r}')

    accepted_at_utc = accepted_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    base = {field: work_item[field] for field in PASS1_IDENTITY_FIELDS}
    base.update({
        'dossier_content_sha256': work_item['dossier_content_sha256'],
        'dossier_compatibility_binding': deepcopy(work_item['dossier_compatibility_binding']),
        'authorization_id': work_item['authorization_id'],
        'pass2_attempted': True,
        'outcome': outcome,
        'analysis_issue_code': None,
        'attempt_consumption_source': 'accepted_result',
        'accepted_at_utc': accepted_at_utc,
    })

    if outcome == 'analyzed_fit':
        fit_level = doc.get('fit_level')
        confidence = doc.get('confidence')
        if fit_level not in FIT_LEVELS:
            raise ValueError('PASS 2 analyzed_fit requires strong/moderate fit_level')
        if confidence not in CONFIDENCE:
            raise ValueError('PASS 2 analyzed_fit requires medium/high confidence')
        evidence = progressive_pass1._validate_text_list(
            'positive_evidence', doc.get('positive_evidence'), require_nonempty=True
        )
        factors = doc.get('taste_factors')
        validate_taste_factors(factors)
        requires_base = bool(
            ((work_item.get('semantic_input') or {}).get('semantic_condition') or {}).get(
                'requires_ai_base_support'
            )
        )
        if requires_base and doc.get('base_support_compatible') is not True:
            raise ValueError('PASS 2 analyzed_fit addon requires base_support_compatible=true')
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
            raise ValueError('PASS 2 analyzed_not_fit requires medium/high confidence')
        if basis not in NOT_FIT_BASES:
            raise ValueError('PASS 2 analyzed_not_fit requires completed not-fit basis')
        if basis == 'confirmed_personal_negative' and confidence != 'high':
            raise ValueError('confirmed personal negative requires high confidence')
        evidence = progressive_pass1._validate_text_list(
            'not_fit_evidence', doc.get('not_fit_evidence'), require_nonempty=True
        )
        base.update({
            'confidence': confidence,
            'not_fit_basis': basis,
            'not_fit_evidence': evidence,
        })
        return base

    issue = doc.get('issue_code')
    if issue not in INCOMPLETE_CODES:
        raise ValueError('PASS 2 analysis_incomplete has unsupported issue_code')
    base['analysis_issue_code'] = issue
    return base


def normalize_terminal_execution_receipt(doc, work_item, accepted_at_utc=None, source_sha256=None):
    if not _identity_matches(doc, work_item, 'PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1'):
        raise ValueError('PASS 2 execution receipt identity does not exactly match prepared work')
    if doc.get('execution_status') != 'executed_no_accepted_result':
        raise ValueError('PASS 2 execution receipt does not prove an executed terminal attempt')
    reason = doc.get('terminal_reason')
    if reason not in TERMINAL_REASONS:
        raise ValueError('PASS 2 execution receipt terminal_reason is unsupported')
    started = parse_utc(doc.get('execution_started_at_utc'))
    finished = parse_utc(doc.get('execution_finished_at_utc'))
    if started is None or finished is None or finished < started:
        raise ValueError('PASS 2 execution receipt timestamps are invalid')

    accepted_at_utc = accepted_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    state_entry = {field: work_item[field] for field in PASS1_IDENTITY_FIELDS}
    state_entry.update({
        'dossier_content_sha256': work_item['dossier_content_sha256'],
        'dossier_compatibility_binding': deepcopy(work_item['dossier_compatibility_binding']),
        'authorization_id': work_item['authorization_id'],
        'pass2_attempted': True,
        'outcome': 'analysis_incomplete',
        'analysis_issue_code': reason,
        'attempt_consumption_source': 'terminal_execution_receipt',
        'accepted_at_utc': accepted_at_utc,
    })
    canonical_receipt = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS2-CANONICAL-EXECUTION-RECEIPT-V1',
        **{field: work_item[field] for field in PASS1_IDENTITY_FIELDS},
        'dossier_content_sha256': work_item['dossier_content_sha256'],
        'dossier_compatibility_binding': deepcopy(work_item['dossier_compatibility_binding']),
        'authorization_id': work_item['authorization_id'],
        'execution_status': 'executed_no_accepted_result',
        'execution_started_at_utc': doc['execution_started_at_utc'],
        'execution_finished_at_utc': doc['execution_finished_at_utc'],
        'terminal_reason': reason,
        'source_transport_sha256': source_sha256,
        'accepted_at_utc': accepted_at_utc,
    }
    return state_entry, canonical_receipt


def _work_by_artifact_name(work_doc, path_field):
    return {
        Path(item.get(path_field) or '').name: item
        for item in (work_doc.get('items') or [])
        if isinstance(item, dict) and item.get(path_field)
    }


def process_result_documents(work_doc, state_doc, documents, accepted_at_utc=None):
    state = deepcopy(state_doc)
    state.setdefault('entries', {})
    work_by_name = _work_by_artifact_name(work_doc, 'result_submission_path')
    receipts = []

    for artifact_name, doc, parse_error in documents:
        receipt = {'artifact': artifact_name}
        work_item = work_by_name.get(artifact_name)
        if work_item is None:
            receipt.update({
                'status': 'rejected_stale_or_mismatched',
                'work_id': doc.get('work_id') if isinstance(doc, dict) else None,
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
            receipt.update({
                'status': 'rejected_invalid_result_no_attempt',
                'work_id': work_item['work_id'],
                'reason': parse_error or 'malformed_json',
            })
            receipts.append(receipt)
            continue
        try:
            entry = normalize_result(doc, work_item, accepted_at_utc=accepted_at_utc)
        except ValueError as exc:
            receipt.update({
                'status': 'rejected_invalid_result_no_attempt',
                'work_id': work_item['work_id'],
                'reason': str(exc),
            })
            receipts.append(receipt)
            continue

        state['entries'][work_item['family_id']] = entry
        receipt.update({
            'status': 'accepted',
            'work_id': work_item['work_id'],
            'family_id': work_item['family_id'],
            'outcome': entry['outcome'],
            'analysis_issue_code': entry.get('analysis_issue_code'),
        })
        receipts.append(receipt)

    return state, receipts


def process_terminal_execution_documents(
    work_doc,
    state_doc,
    documents,
    accepted_at_utc=None,
    source_sha256_by_name=None,
):
    state = deepcopy(state_doc)
    state.setdefault('entries', {})
    work_by_name = _work_by_artifact_name(work_doc, 'terminal_execution_submission_path')
    receipts = []
    canonical_receipts = {}
    source_sha256_by_name = source_sha256_by_name or {}

    for artifact_name, doc, parse_error in documents:
        receipt = {'artifact': artifact_name}
        work_item = work_by_name.get(artifact_name)
        if work_item is None:
            receipt.update({
                'status': 'rejected_stale_or_mismatched',
                'work_id': doc.get('work_id') if isinstance(doc, dict) else None,
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
            receipt.update({
                'status': 'rejected_invalid_execution_receipt_no_attempt',
                'work_id': work_item['work_id'],
                'reason': parse_error or 'malformed_json',
            })
            receipts.append(receipt)
            continue
        try:
            entry, canonical = normalize_terminal_execution_receipt(
                doc,
                work_item,
                accepted_at_utc=accepted_at_utc,
                source_sha256=source_sha256_by_name.get(artifact_name),
            )
        except ValueError as exc:
            receipt.update({
                'status': 'rejected_invalid_execution_receipt_no_attempt',
                'work_id': work_item['work_id'],
                'reason': str(exc),
            })
            receipts.append(receipt)
            continue

        state['entries'][work_item['family_id']] = entry
        canonical_path = (
            CANONICAL_EXECUTION_RECEIPTS
            / f"{work_item['semantic_generation_id']}--{work_item['work_id']}.json"
        )
        canonical_receipts[str(canonical_path).replace('\\', '/')] = canonical
        receipt.update({
            'status': 'accepted_terminal_execution_receipt',
            'work_id': work_item['work_id'],
            'family_id': work_item['family_id'],
            'outcome': 'analysis_incomplete',
            'analysis_issue_code': entry['analysis_issue_code'],
            'canonical_receipt_path': str(canonical_path).replace('\\', '/'),
        })
        receipts.append(receipt)

    return state, receipts, canonical_receipts


def project_state(binding, state_doc=None):
    entry = matching_state_entry(binding, state_doc)
    if entry is None:
        return None
    outcome = entry.get('outcome')
    base = {
        'analysis_state': outcome,
        'analysis_tier': 1 if outcome == 'analyzed_fit' else (2 if outcome == 'analysis_incomplete' else None),
        'analysis_issue_code': entry.get('analysis_issue_code'),
        'fit': entry.get('fit_level') if outcome == 'analyzed_fit' else None,
        'evaluated_at_utc': entry.get('accepted_at_utc'),
        'analysis_semantic_source': 'progressive_pass2',
        'analysis_resolution_pass': 'pass2',
        'semantic_generation_id': entry.get('semantic_generation_id'),
        'pass1_attempted': True,
        'pass2_attempted': True,
    }
    if outcome not in OUTCOMES:
        raise ValueError(f'unknown PASS 2 persisted outcome: {outcome!r}')
    return base


def semantic_taste_entry(entry):
    if not isinstance(entry, dict) or entry.get('outcome') != 'analyzed_fit':
        return {}
    return {
        'key': entry.get('taste_subject_key'),
        'appid': entry.get('appid'),
        'verdict': 'INCLUDE',
        'fit_level': entry.get('fit_level'),
        'reason_code': 'progressive_pass2_dossier_recovery_fit',
        'taste_fingerprint': entry.get('taste_fingerprint'),
        'candidate_context_sha256': entry.get('candidate_context_sha256'),
        'positive_evidence': list(entry.get('positive_evidence') or []),
        'negative_analysis_status': 'incomplete_no_confirmed_negative',
        'negative_findings': [],
        'negative_evidence': [],
        'taste_factors': dict(entry.get('taste_factors') or {}),
        'fit_evidence_state': 'sufficient',
        'fit_evidence_confidence': entry.get('confidence') or 'medium',
        'fit_evidence_basis': ['candidate_specific_positive_match', 'accepted_dossier_recovery'],
        'historical_negative_context': None,
        'candidate_quality_findings': [],
        'evaluated_at_utc': entry.get('accepted_at_utc'),
        'semantic_source': 'progressive_pass2',
        'semantic_generation_id': entry.get('semantic_generation_id'),
        'dossier_content_sha256': entry.get('dossier_content_sha256'),
    }


def current_fit_semantic_entries(context_rows=None, projection_doc=None, queue_rows=None, state_doc=None):
    context_rows = context_rows if context_rows is not None else progressive_pass1.load_jsonl(progressive_pass1.PROGRESSIVE_CONTEXT)
    projection_doc = projection_doc if projection_doc is not None else load_json(progressive_pass1.TASTE_PROJECTION)
    queue_rows = queue_rows if queue_rows is not None else progressive_pass1.load_jsonl(progressive_pass1.TASTE_QUEUE)
    state_doc = state_doc if state_doc is not None else load_state()
    _generation, bindings, _queue = progressive_pass1.current_bindings(
        context_rows, projection_doc, queue_rows
    )
    out = {}
    for binding in bindings.values():
        entry = matching_state_entry(binding, state_doc)
        if entry and entry.get('outcome') == 'analyzed_fit':
            out[binding['taste_subject_key']] = semantic_taste_entry(entry)
    return out

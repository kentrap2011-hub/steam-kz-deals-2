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
DOSSIER_WORK = ROOT / 'data/production/pre_ai/taste_steam_review_dossier_work.json'
CANONICAL_EXECUTION_RECEIPTS = ROOT / 'data/cache/progressive_pass2_execution_receipts'

STATE_SCHEMA_VERSION = 2
STATE_CONTRACT = 'PROGRESSIVE-PASS2-STATE-V2'
WORK_MODES = {'normal_first_pass', 'recovery'}
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
AUTHORITATIVE_OUTCOMES = {'analyzed_fit', 'analyzed_not_fit'}
RECOVERY_REASONS = {
    'materially_changed_canonically_accepted_dossier_or_evidence',
    'corrected_runtime_or_validation_defect_material_to_the_prior_failure',
    'explicit_canonical_github_recovery_action_with_recorded_reason',
}
PASS1_IDENTITY_FIELDS = progressive_pass1.IDENTITY_FIELDS
IMMUTABLE_RESULT_FIELDS = PASS1_IDENTITY_FIELDS + (
    'dossier_content_sha256',
    'authorization_id',
    'work_mode',
    'recovery_authorization_id',
    'recovery_reason',
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
    architecture = contract.get('runtime_architecture') or {}
    if architecture.get('target_architecture_runtime_adapted') is not True:
        raise ValueError('progressive Deep runtime is not adapted to FAST-DOSSIER-DEEP-V1')
    budget = contract.get('attempt_budget') or {}
    if budget.get('normal_first_pass_attempts_per_deep_identity') != 1:
        raise ValueError('progressive Deep normal first-pass budget mismatch')
    if budget.get('recovery_attempts_share_normal_first_pass_budget') is not False:
        raise ValueError('Deep recovery must remain separate from normal first-pass accounting')
    if budget.get('recovery_requires_fresh_github_authorization_each_attempt') is not True:
        raise ValueError('Deep recovery requires fresh GitHub authorization')
    if budget.get('recovery_has_hidden_fixed_quota') is not False:
        raise ValueError('Deep recovery must not introduce a hidden fixed quota')
    transport = contract.get('transport') or {}
    if transport.get('batch_atomicity') is not False or transport.get('maximal_contiguous_prefix') is not False:
        raise ValueError('progressive Deep must remain independent item-level transport')
    return contract


def empty_state():
    return {
        'schema_version': STATE_SCHEMA_VERSION,
        'contract': STATE_CONTRACT,
        'entries': {},
    }


def load_state(path=None):
    path = STATE if path is None else Path(path)
    doc = load_json(path)
    if not doc:
        return empty_state()
    # The only production migration authorized by this task is the known zero-entry
    # V1 state. Non-empty legacy state would require a separate explicit migration.
    if doc.get('schema_version') == 1 and doc.get('contract') == 'PROGRESSIVE-PASS2-STATE-V1':
        if doc.get('entries') == {}:
            return empty_state()
        raise ValueError('non-empty legacy PASS 2 state requires explicit migration')
    if doc.get('schema_version') != STATE_SCHEMA_VERSION or doc.get('contract') != STATE_CONTRACT:
        raise ValueError('progressive Deep state schema mismatch')
    if not isinstance(doc.get('entries'), dict):
        raise ValueError('progressive Deep entries must be an object')
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


def _identity_matches_binding(entry, binding):
    if not isinstance(entry, dict) or not isinstance(binding, dict):
        return False
    return all(
        str(entry.get(field) or '') == str(binding.get(field) or '')
        for field in PASS1_IDENTITY_FIELDS
    )


def matching_state_entry(binding, state_doc=None):
    if not isinstance(binding, dict):
        return None
    state_doc = state_doc if state_doc is not None else load_state()
    family_id = str(binding.get('family_id') or '')
    entry = (state_doc.get('entries') or {}).get(family_id)
    if not _identity_matches_binding(entry, binding):
        return None
    if entry.get('normal_first_pass_attempted') is not True:
        return None
    return entry


def authoritative_completion_entry(binding, state_doc=None):
    entry = matching_state_entry(binding, state_doc)
    if not isinstance(entry, dict):
        return None
    if entry.get('authoritative_completed') is not True:
        return None
    if entry.get('outcome') not in AUTHORITATIVE_OUTCOMES:
        return None
    return entry


def authorization_id(
    binding,
    dossier_content_sha256,
    dossier_compatibility_binding,
    *,
    work_mode='normal_first_pass',
    recovery_authorization_id=None,
):
    if work_mode not in WORK_MODES:
        raise ValueError('unknown Deep work mode')
    material = {
        'semantic_generation_id': binding.get('semantic_generation_id'),
        'work_id': binding.get('work_id'),
        'appid': binding.get('appid'),
        'dossier_content_sha256': dossier_content_sha256,
        'dossier_compatibility_binding': dossier_compatibility_binding,
        'work_mode': work_mode,
        'recovery_authorization_id': recovery_authorization_id,
    }
    if any(not material.get(key) for key in ('semantic_generation_id', 'work_id', 'appid', 'dossier_content_sha256')):
        raise ValueError('Deep authorization material is incomplete')
    if work_mode == 'recovery' and not recovery_authorization_id:
        raise ValueError('Deep recovery work requires recovery_authorization_id')
    if not isinstance(dossier_compatibility_binding, dict) or not dossier_compatibility_binding:
        raise ValueError('Deep Dossier compatibility binding is missing')
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
    semantic_input,
    dossier_record,
    current_binding,
    now=None,
    pass1_entry=None,
    pass2_state_doc=None,
):
    """Validate only the current Deep evidence gate.

    Fast/PASS 1 parameters remain accepted for call-site compatibility but are
    intentionally irrelevant to FAST-DOSSIER-DEEP-V1 eligibility.
    """
    del pass1_entry, pass2_state_doc
    now = now or datetime.now(timezone.utc)

    if not isinstance(binding, dict):
        return False, 'current_deep_identity_missing'
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


def _latest_attempt_dossier_sha(entry):
    attempts = list(entry.get('recovery_attempts') or [])
    if attempts:
        return attempts[-1].get('dossier_content_sha256')
    first = entry.get('normal_first_pass') or {}
    return first.get('dossier_content_sha256') or entry.get('dossier_content_sha256')


def _recovery_history_authorization_ids(entry):
    return {
        str(row.get('recovery_authorization_id'))
        for row in (entry.get('recovery_attempts') or [])
        if isinstance(row, dict) and row.get('recovery_authorization_id')
    }


def recovery_authorization_is_live(entry, dossier_record, current_binding):
    if not isinstance(entry, dict) or entry.get('recovery_owned') is not True:
        return False
    auth = entry.get('recovery_authorization')
    if not isinstance(auth, dict) or auth.get('status') != 'authorized':
        return False
    if not _identity_matches_binding(auth, entry):
        return False
    auth_id = auth.get('recovery_authorization_id')
    if not isinstance(auth_id, str) or len(auth_id) != 64:
        return False
    if auth_id in _recovery_history_authorization_ids(entry):
        return False
    if not isinstance(dossier_record, dict):
        return False
    if auth.get('dossier_content_sha256') != dossier_record.get('content_sha256'):
        return False
    if auth.get('dossier_compatibility_binding') != current_binding:
        return False
    if auth.get('recovery_reason') not in RECOVERY_REASONS:
        return False
    if not isinstance(auth.get('recovery_condition_binding'), dict) or not auth.get('recovery_condition_binding'):
        return False
    return True


def authorize_recovery(
    *,
    binding,
    state_doc,
    dossier_record,
    current_binding,
    recovery_reason,
    recovery_condition_binding,
    authorized_at_utc=None,
):
    if recovery_reason not in RECOVERY_REASONS:
        raise ValueError('unsupported Deep recovery reason')
    if not isinstance(recovery_condition_binding, dict) or not recovery_condition_binding:
        raise ValueError('Deep recovery requires a concrete recovery_condition_binding')

    state = deepcopy(state_doc)
    state.setdefault('entries', {})
    entry = matching_state_entry(binding, state)
    if entry is None:
        raise ValueError('Deep recovery authorization requires a consumed normal first pass')
    if entry.get('authoritative_completed') is True:
        raise ValueError('authoritative Deep completion cannot enter recovery')
    if entry.get('recovery_owned') is not True:
        raise ValueError('Deep identity is not recovery-owned')

    semantic_input = recovery_condition_binding.get('semantic_input')
    if not isinstance(semantic_input, dict):
        raise ValueError('recovery_condition_binding must include current semantic_input')
    eligible, reason = dossier_is_eligible(
        binding=binding,
        semantic_input=semantic_input,
        dossier_record=dossier_record,
        current_binding=current_binding,
    )
    if not eligible:
        raise ValueError(f'current Dossier cannot authorize Deep recovery: {reason}')

    digest = dossier_record['content_sha256']
    if (
        recovery_reason == 'materially_changed_canonically_accepted_dossier_or_evidence'
        and digest == _latest_attempt_dossier_sha(entry)
    ):
        raise ValueError('material Dossier/evidence recovery requires a changed canonical Dossier digest')

    material = {
        **{field: binding[field] for field in PASS1_IDENTITY_FIELDS},
        'dossier_content_sha256': digest,
        'dossier_compatibility_binding': deepcopy(current_binding),
        'recovery_reason': recovery_reason,
        'recovery_condition_binding': deepcopy(recovery_condition_binding),
    }
    recovery_authorization_id = canonical_sha256(material)
    if recovery_authorization_id in _recovery_history_authorization_ids(entry):
        raise ValueError('recovery authorization must be fresh and cannot replay a consumed authorization')

    existing_auth = entry.get('recovery_authorization')
    if isinstance(existing_auth, dict) and existing_auth.get('status') == 'authorized':
        if existing_auth.get('recovery_authorization_id') == recovery_authorization_id:
            return state, deepcopy(existing_auth)
        # A stale/unusable authorization may be superseded only by a different
        # concrete GitHub-owned condition binding. No attempt is consumed here.

    authorized_at_utc = authorized_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    auth = {
        **{field: binding[field] for field in PASS1_IDENTITY_FIELDS},
        'recovery_authorization_id': recovery_authorization_id,
        'status': 'authorized',
        'recovery_reason': recovery_reason,
        'recovery_condition_binding': deepcopy(recovery_condition_binding),
        'dossier_content_sha256': digest,
        'dossier_compatibility_binding': deepcopy(current_binding),
        'authorized_at_utc': authorized_at_utc,
    }
    state['entries'][binding['family_id']]['recovery_authorization'] = auth
    return state, deepcopy(auth)


def make_work_item(
    binding,
    queue_row,
    dossier_record,
    current_binding,
    *,
    work_mode='normal_first_pass',
    recovery_authorization=None,
):
    semantic_input = _semantic_input(queue_row)
    digest = dossier_record['content_sha256']
    dossier = dossier_record['doc']
    recovery_authorization = recovery_authorization if isinstance(recovery_authorization, dict) else None
    recovery_authorization_id = (
        recovery_authorization.get('recovery_authorization_id')
        if recovery_authorization else None
    )
    recovery_reason = recovery_authorization.get('recovery_reason') if recovery_authorization else None
    recovery_condition_binding = (
        deepcopy(recovery_authorization.get('recovery_condition_binding'))
        if recovery_authorization else None
    )
    auth = authorization_id(
        binding,
        digest,
        current_binding,
        work_mode=work_mode,
        recovery_authorization_id=recovery_authorization_id,
    )
    prefix = f"{binding['semantic_generation_id'][:16]}--{binding['work_id']}--{auth}"
    return {
        **binding,
        'work_mode': work_mode,
        'semantic_input': semantic_input,
        'dossier_path': dossier_record['path'],
        'dossier_content_sha256': digest,
        'dossier_compatibility_binding': deepcopy(current_binding),
        'dossier_expires_at_utc': dossier['expires_at_utc'],
        'recovery_authorization_id': recovery_authorization_id,
        'recovery_reason': recovery_reason,
        'recovery_condition_binding': recovery_condition_binding,
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
        'deep_total_current_coverage_target': 0,
        'deep_first_pass_attempted_count': 0,
        'deep_authoritative_completed_count': 0,
        'deep_completed_fit_count': 0,
        'deep_completed_not_fit_count': 0,
        'deep_incomplete_or_recovery_count': 0,
        'deep_waiting_for_dossier_count': 0,
        'deep_ready_or_pending_count': 0,
        'deep_normal_first_pass_remaining_count': 0,
        'deep_remaining_until_all_authoritative_count': 0,
        'deep_normal_first_pass_complete': False,
        'deep_all_current_authoritative_complete': False,
        'recovery_owned_count': 0,
        'recovery_eligible_count': 0,
        'recovery_pending_count': 0,
        # Compatibility counters retained for existing operational surfaces.
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
        counts['deep_total_current_coverage_target'] += 1
        pass1_entry = progressive_pass1.matching_state_entry(binding, pass1_state_doc)
        if pass1_entry is not None and pass1_entry.get('outcome') == 'analysis_incomplete':
            counts['current_analysis_incomplete_count'] += 1

        entry = matching_state_entry(binding, pass2_state_doc)
        if entry is not None:
            counts['deep_first_pass_attempted_count'] += 1
            counts['pass2_attempted_count'] += 1
            if entry.get('authoritative_completed') is True and entry.get('outcome') in AUTHORITATIVE_OUTCOMES:
                counts['deep_authoritative_completed_count'] += 1
                if entry.get('outcome') == 'analyzed_fit':
                    counts['deep_completed_fit_count'] += 1
                else:
                    counts['deep_completed_not_fit_count'] += 1
                reasons[family_id] = 'deep_authoritative_completed'
                continue
            counts['deep_incomplete_or_recovery_count'] += 1

        queue_row = queue_by_family.get(family_id) or {}
        semantic_input = _semantic_input(queue_row)
        dossier_record = dossier_loader(binding['appid'])
        dossier_ok, dossier_reason = dossier_is_eligible(
            binding=binding,
            semantic_input=semantic_input,
            dossier_record=dossier_record,
            current_binding=current_binding,
            now=now,
        )

        if entry is None:
            if not dossier_ok:
                counts['deep_waiting_for_dossier_count'] += 1
                reasons[family_id] = dossier_reason
                continue
            items.append(
                make_work_item(
                    binding,
                    queue_row,
                    dossier_record,
                    current_binding,
                    work_mode='normal_first_pass',
                )
            )
            counts['deep_ready_or_pending_count'] += 1
            reasons[family_id] = 'eligible_normal_first_pass'
            continue

        # Any unresolved consumed normal first pass is recovery-owned. It is never
        # silently re-emitted into normal work, regardless of Fast state or time.
        auth = entry.get('recovery_authorization')
        if not dossier_ok:
            counts['recovery_owned_count'] += 1
            reasons[family_id] = f'recovery_owned_{dossier_reason}'
            continue
        if not recovery_authorization_is_live(entry, dossier_record, current_binding):
            counts['recovery_owned_count'] += 1
            reasons[family_id] = 'recovery_owned_fresh_authorization_required'
            continue

        items.append(
            make_work_item(
                binding,
                queue_row,
                dossier_record,
                current_binding,
                work_mode='recovery',
                recovery_authorization=auth,
            )
        )
        counts['recovery_eligible_count'] += 1
        counts['recovery_pending_count'] += 1
        counts['deep_ready_or_pending_count'] += 1
        reasons[family_id] = 'eligible_recovery_authorization'

    counts['deep_normal_first_pass_remaining_count'] = (
        counts['deep_total_current_coverage_target'] - counts['deep_first_pass_attempted_count']
    )
    counts['deep_remaining_until_all_authoritative_count'] = (
        counts['deep_total_current_coverage_target'] - counts['deep_authoritative_completed_count']
    )
    counts['deep_normal_first_pass_complete'] = counts['deep_normal_first_pass_remaining_count'] == 0
    counts['deep_all_current_authoritative_complete'] = counts['deep_remaining_until_all_authoritative_count'] == 0
    counts['dossier_waiting_count'] = counts['deep_waiting_for_dossier_count']
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
    if doc.get('dossier_compatibility_binding') != work_item.get('dossier_compatibility_binding'):
        return False
    if doc.get('recovery_condition_binding') != work_item.get('recovery_condition_binding'):
        return False
    return True


def _attempt_base(work_item, outcome, accepted_at_utc, source):
    return {
        **{field: work_item[field] for field in PASS1_IDENTITY_FIELDS},
        'dossier_content_sha256': work_item['dossier_content_sha256'],
        'dossier_compatibility_binding': deepcopy(work_item['dossier_compatibility_binding']),
        'authorization_id': work_item['authorization_id'],
        'work_mode': work_item['work_mode'],
        'recovery_authorization_id': work_item.get('recovery_authorization_id'),
        'recovery_reason': work_item.get('recovery_reason'),
        'recovery_condition_binding': deepcopy(work_item.get('recovery_condition_binding')),
        'outcome': outcome,
        'analysis_issue_code': None,
        'attempt_consumption_source': source,
        'accepted_at_utc': accepted_at_utc,
    }


def normalize_result(doc, work_item, accepted_at_utc=None):
    if not _identity_matches(doc, work_item, 'PROGRESSIVE-PASS2-RESULT-V1'):
        raise ValueError('Deep result identity does not exactly match prepared work')
    outcome = doc.get('outcome')
    if outcome not in OUTCOMES:
        raise ValueError(f'unknown Deep outcome: {outcome!r}')

    accepted_at_utc = accepted_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    base = _attempt_base(work_item, outcome, accepted_at_utc, 'accepted_result')

    if outcome == 'analyzed_fit':
        fit_level = doc.get('fit_level')
        confidence = doc.get('confidence')
        if fit_level not in FIT_LEVELS:
            raise ValueError('Deep analyzed_fit requires strong/moderate fit_level')
        if confidence not in CONFIDENCE:
            raise ValueError('Deep analyzed_fit requires medium/high confidence')
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
            raise ValueError('Deep analyzed_fit addon requires base_support_compatible=true')
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
            raise ValueError('Deep analyzed_not_fit requires medium/high confidence')
        if basis not in NOT_FIT_BASES:
            raise ValueError('Deep analyzed_not_fit requires completed not-fit basis')
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
        raise ValueError('Deep analysis_incomplete has unsupported issue_code')
    base['analysis_issue_code'] = issue
    return base


def normalize_terminal_execution_receipt(doc, work_item, accepted_at_utc=None, source_sha256=None):
    if not _identity_matches(doc, work_item, 'PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1'):
        raise ValueError('Deep execution receipt identity does not exactly match prepared work')
    if doc.get('execution_status') != 'executed_no_accepted_result':
        raise ValueError('Deep execution receipt does not prove an executed terminal attempt')
    reason = doc.get('terminal_reason')
    if reason not in TERMINAL_REASONS:
        raise ValueError('Deep execution receipt terminal_reason is unsupported')
    started = parse_utc(doc.get('execution_started_at_utc'))
    finished = parse_utc(doc.get('execution_finished_at_utc'))
    if started is None or finished is None or finished < started:
        raise ValueError('Deep execution receipt timestamps are invalid')

    accepted_at_utc = accepted_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    attempt = _attempt_base(
        work_item,
        'analysis_incomplete',
        accepted_at_utc,
        'terminal_execution_receipt',
    )
    attempt['analysis_issue_code'] = reason
    canonical_receipt = {
        'schema_version': 2,
        'contract': 'PROGRESSIVE-PASS2-CANONICAL-EXECUTION-RECEIPT-V2',
        **{field: work_item[field] for field in PASS1_IDENTITY_FIELDS},
        'dossier_content_sha256': work_item['dossier_content_sha256'],
        'dossier_compatibility_binding': deepcopy(work_item['dossier_compatibility_binding']),
        'authorization_id': work_item['authorization_id'],
        'work_mode': work_item['work_mode'],
        'recovery_authorization_id': work_item.get('recovery_authorization_id'),
        'recovery_reason': work_item.get('recovery_reason'),
        'recovery_condition_binding': deepcopy(work_item.get('recovery_condition_binding')),
        'execution_status': 'executed_no_accepted_result',
        'execution_started_at_utc': doc['execution_started_at_utc'],
        'execution_finished_at_utc': doc['execution_finished_at_utc'],
        'terminal_reason': reason,
        'source_transport_sha256': source_sha256,
        'accepted_at_utc': accepted_at_utc,
    }
    return attempt, canonical_receipt


def _work_by_artifact_name(work_doc, path_field):
    return {
        Path(item.get(path_field) or '').name: item
        for item in (work_doc.get('items') or [])
        if isinstance(item, dict) and item.get(path_field)
    }


def _attempt_authorization_status(existing, work_item):
    mode = work_item.get('work_mode')
    if mode == 'normal_first_pass':
        return 'new' if existing is None else 'replay'
    if mode != 'recovery' or existing is None:
        return 'unauthorized'
    recovery_authorization_id = work_item.get('recovery_authorization_id')
    if recovery_authorization_id in _recovery_history_authorization_ids(existing):
        return 'replay'
    auth = existing.get('recovery_authorization')
    if not isinstance(auth, dict) or auth.get('status') != 'authorized':
        return 'unauthorized'
    if auth.get('recovery_authorization_id') != recovery_authorization_id:
        return 'unauthorized'
    if auth.get('recovery_reason') != work_item.get('recovery_reason'):
        return 'unauthorized'
    if auth.get('recovery_condition_binding') != work_item.get('recovery_condition_binding'):
        return 'unauthorized'
    if auth.get('dossier_content_sha256') != work_item.get('dossier_content_sha256'):
        return 'unauthorized'
    if auth.get('dossier_compatibility_binding') != work_item.get('dossier_compatibility_binding'):
        return 'unauthorized'
    return 'new'


def _apply_attempt(existing, work_item, attempt):
    authoritative = attempt.get('outcome') in AUTHORITATIVE_OUTCOMES
    if work_item.get('work_mode') == 'normal_first_pass':
        if existing is not None:
            raise ValueError('normal Deep first pass cannot overwrite existing current state')
        entry = {
            **{field: work_item[field] for field in PASS1_IDENTITY_FIELDS},
            'pass2_attempted': True,
            'normal_first_pass_attempted': True,
            'authoritative_completed': authoritative,
            'outcome': attempt['outcome'],
            'analysis_issue_code': attempt.get('analysis_issue_code'),
            'attempt_consumption_source': attempt.get('attempt_consumption_source'),
            'accepted_at_utc': attempt.get('accepted_at_utc'),
            'dossier_content_sha256': attempt.get('dossier_content_sha256'),
            'dossier_compatibility_binding': deepcopy(attempt.get('dossier_compatibility_binding')),
            'authorization_id': attempt.get('authorization_id'),
            'work_mode': 'normal_first_pass',
            'recovery_authorization_id': None,
            'recovery_reason': None,
            'recovery_condition_binding': None,
            'normal_first_pass': deepcopy(attempt),
            'recovery_attempts': [],
            'recovery_owned': not authoritative,
            'recovery_authorization': None,
        }
        for field in (
            'fit_level', 'confidence', 'positive_evidence', 'taste_factors',
            'base_support_compatible', 'not_fit_basis', 'not_fit_evidence',
        ):
            if field in attempt:
                entry[field] = deepcopy(attempt[field])
        return entry

    if work_item.get('work_mode') != 'recovery' or existing is None:
        raise ValueError('Deep recovery attempt lacks current recovery-owned state')
    entry = deepcopy(existing)
    entry.setdefault('recovery_attempts', []).append(deepcopy(attempt))
    entry['pass2_attempted'] = True
    entry['authoritative_completed'] = authoritative
    entry['outcome'] = attempt['outcome']
    entry['analysis_issue_code'] = attempt.get('analysis_issue_code')
    entry['attempt_consumption_source'] = attempt.get('attempt_consumption_source')
    entry['accepted_at_utc'] = attempt.get('accepted_at_utc')
    entry['dossier_content_sha256'] = attempt.get('dossier_content_sha256')
    entry['dossier_compatibility_binding'] = deepcopy(attempt.get('dossier_compatibility_binding'))
    entry['authorization_id'] = attempt.get('authorization_id')
    entry['work_mode'] = 'recovery'
    entry['recovery_authorization_id'] = attempt.get('recovery_authorization_id')
    entry['recovery_reason'] = attempt.get('recovery_reason')
    entry['recovery_condition_binding'] = deepcopy(attempt.get('recovery_condition_binding'))
    entry['recovery_owned'] = not authoritative
    entry['recovery_authorization'] = None
    for field in (
        'fit_level', 'confidence', 'positive_evidence', 'taste_factors',
        'base_support_compatible', 'not_fit_basis', 'not_fit_evidence',
    ):
        entry.pop(field, None)
        if field in attempt:
            entry[field] = deepcopy(attempt[field])
    return entry


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
        auth_status = _attempt_authorization_status(existing, work_item)
        if auth_status == 'replay':
            receipt.update({
                'status': 'replay_ignored',
                'work_id': work_item['work_id'],
                'work_mode': work_item.get('work_mode'),
                'outcome': existing.get('outcome') if existing else None,
            })
            receipts.append(receipt)
            continue
        if auth_status != 'new':
            receipt.update({
                'status': 'rejected_stale_or_mismatched',
                'work_id': work_item['work_id'],
                'reason': 'recovery_authorization_not_current',
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
            attempt = normalize_result(doc, work_item, accepted_at_utc=accepted_at_utc)
            entry = _apply_attempt(existing, work_item, attempt)
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
            'work_mode': work_item.get('work_mode'),
            'outcome': entry['outcome'],
            'analysis_issue_code': entry.get('analysis_issue_code'),
            'authoritative_completed': entry.get('authoritative_completed'),
            'recovery_owned': entry.get('recovery_owned'),
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
        auth_status = _attempt_authorization_status(existing, work_item)
        if auth_status == 'replay':
            receipt.update({
                'status': 'replay_ignored',
                'work_id': work_item['work_id'],
                'work_mode': work_item.get('work_mode'),
                'outcome': existing.get('outcome') if existing else None,
            })
            receipts.append(receipt)
            continue
        if auth_status != 'new':
            receipt.update({
                'status': 'rejected_stale_or_mismatched',
                'work_id': work_item['work_id'],
                'reason': 'recovery_authorization_not_current',
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
            attempt, canonical = normalize_terminal_execution_receipt(
                doc,
                work_item,
                accepted_at_utc=accepted_at_utc,
                source_sha256=source_sha256_by_name.get(artifact_name),
            )
            entry = _apply_attempt(existing, work_item, attempt)
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
            / f"{work_item['semantic_generation_id']}--{work_item['work_id']}--{work_item['authorization_id']}.json"
        )
        canonical_receipts[str(canonical_path).replace('\\', '/')] = canonical
        receipt.update({
            'status': 'accepted_terminal_execution_receipt',
            'work_id': work_item['work_id'],
            'family_id': work_item['family_id'],
            'work_mode': work_item.get('work_mode'),
            'outcome': 'analysis_incomplete',
            'analysis_issue_code': entry['analysis_issue_code'],
            'authoritative_completed': False,
            'recovery_owned': True,
            'canonical_receipt_path': str(canonical_path).replace('\\', '/'),
        })
        receipts.append(receipt)

    return state, receipts, canonical_receipts


def project_state(binding, state_doc=None):
    entry = matching_state_entry(binding, state_doc)
    if entry is None:
        return None
    outcome = entry.get('outcome')
    if outcome not in OUTCOMES:
        raise ValueError(f'unknown Deep persisted outcome: {outcome!r}')
    authoritative = entry.get('authoritative_completed') is True and outcome in AUTHORITATIVE_OUTCOMES
    return {
        'analysis_state': outcome if authoritative else 'analysis_incomplete',
        'analysis_tier': 1 if authoritative and outcome == 'analyzed_fit' else (
            None if authoritative and outcome == 'analyzed_not_fit' else 2
        ),
        'analysis_issue_code': None if authoritative else (
            entry.get('analysis_issue_code') or 'insufficient_evidence'
        ),
        'fit': entry.get('fit_level') if authoritative and outcome == 'analyzed_fit' else None,
        'evaluated_at_utc': entry.get('accepted_at_utc'),
        'analysis_semantic_source': 'progressive_pass2',
        'analysis_resolution_pass': 'pass2',
        'semantic_generation_id': entry.get('semantic_generation_id'),
        'pass1_attempted': False,
        'pass2_attempted': True,
    }


def semantic_taste_entry(entry):
    if (
        not isinstance(entry, dict)
        or entry.get('authoritative_completed') is not True
        or entry.get('outcome') != 'analyzed_fit'
    ):
        return {}
    return {
        'key': entry.get('taste_subject_key'),
        'appid': entry.get('appid'),
        'verdict': 'INCLUDE',
        'fit_level': entry.get('fit_level'),
        'reason_code': 'progressive_deep_authoritative_fit',
        'taste_fingerprint': entry.get('taste_fingerprint'),
        'candidate_context_sha256': entry.get('candidate_context_sha256'),
        'positive_evidence': list(entry.get('positive_evidence') or []),
        'negative_analysis_status': 'incomplete_no_confirmed_negative',
        'negative_findings': [],
        'negative_evidence': [],
        'taste_factors': dict(entry.get('taste_factors') or {}),
        'fit_evidence_state': 'sufficient',
        'fit_evidence_confidence': entry.get('confidence') or 'medium',
        'fit_evidence_basis': ['candidate_specific_positive_match', 'accepted_dossier_deep'],
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
        entry = authoritative_completion_entry(binding, state_doc)
        if entry and entry.get('outcome') == 'analyzed_fit':
            out[binding['taste_subject_key']] = semantic_taste_entry(entry)
    return out


def dossier_group_state_index(dossier_work_doc=None):
    dossier_work_doc = dossier_work_doc if dossier_work_doc is not None else load_json(DOSSIER_WORK)
    plan = (dossier_work_doc.get('submission_group_plan') or {}).get('groups') or []
    progress = (dossier_work_doc.get('group_progress') or {}).get('groups') or []
    progress_by_sequence = {
        int(row.get('sequence')): row.get('state')
        for row in progress
        if isinstance(row, dict) and row.get('sequence') is not None
    }
    out = {}
    for group in plan:
        if not isinstance(group, dict):
            continue
        state = progress_by_sequence.get(int(group.get('sequence') or 0), 'pending')
        for appid in group.get('appids') or []:
            out[str(appid)] = state
    return out


def dossier_stage_state(
    *,
    binding,
    semantic_input,
    current_binding,
    dossier_record=None,
    dossier_work_doc=None,
    now=None,
):
    dossier_record = dossier_record if dossier_record is not None else canonical_dossier_loader(binding.get('appid'))
    eligible, _reason = dossier_is_eligible(
        binding=binding,
        semantic_input=semantic_input,
        dossier_record=dossier_record,
        current_binding=current_binding,
        now=now,
    )
    if eligible:
        return 'accepted'
    group_state = dossier_group_state_index(dossier_work_doc).get(str(binding.get('appid') or ''))
    if group_state == 'failed_or_invalid_pending_recovery':
        return 'failed_or_recovery'
    return 'not_ready'


def deep_recovery_state(binding, state_doc=None, work_doc=None):
    entry = matching_state_entry(binding, state_doc)
    if entry is None or entry.get('authoritative_completed') is True or entry.get('recovery_owned') is not True:
        return 'none'
    work_doc = work_doc if work_doc is not None else load_json(WORK)
    for item in work_doc.get('items') or []:
        if (
            isinstance(item, dict)
            and item.get('family_id') == binding.get('family_id')
            and item.get('work_id') == binding.get('work_id')
            and item.get('work_mode') == 'recovery'
        ):
            return 'recovery_pending'
    auth = entry.get('recovery_authorization')
    if isinstance(auth, dict) and auth.get('status') == 'authorized':
        return 'recovery_eligible'
    return 'recovery_owned'

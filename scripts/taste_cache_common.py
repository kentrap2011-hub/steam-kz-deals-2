import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

from taste_negative_contract import validate_entry_negative_fields

ENTRY_CONTRACT = Path('config/taste_cache_entry_contract.json')
FINGERPRINT_CONTRACT = Path('config/taste_fingerprint_contract.json')
CANDIDATE_CONTEXT_CONTRACT = Path('config/taste_candidate_context_contract.json')
LEDGER_CONTRACT = Path('config/taste_ledger_contract.json')
POLICY = Path('config/mailing_policy.json')
LEGACY_LEDGER = Path('data/cache/taste_fit.ledger_validation.json')

TASTE_FACTOR_IDS = (
    'gameplay_mastery',
    'development_variety',
    'structure_pacing_direction',
    'identity_hooks',
    'breadth_of_match',
)


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def git_blob_sha_bytes(raw):
    return hashlib.sha1(f'blob {len(raw)}\0'.encode('ascii') + raw).hexdigest()


def git_blob_sha_path(path):
    raw = Path(path).read_bytes()
    return git_blob_sha_bytes(raw)


def git_blob_json(blob_sha):
    raw = subprocess.check_output(['git', 'cat-file', 'blob', blob_sha])
    return json.loads(raw.decode('utf-8'))


def taste_semantics_digest(policy_doc, entry_contract=None):
    contract = entry_contract or load_json(ENTRY_CONTRACT)
    fields = contract['taste_semantics_policy_fields']
    payload = {field: policy_doc.get(field) for field in fields}
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(',', ':'),
    ).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def current_taste_semantics_digest():
    return taste_semantics_digest(load_json(POLICY))


def legacy_v1_semantics_digest():
    ledger = load_json(LEGACY_LEDGER)
    policy_blob_sha = (ledger.get('bindings') or {}).get('policy_blob_sha')
    if not policy_blob_sha:
        raise RuntimeError('Legacy ledger lacks historical policy binding')
    historical_policy = git_blob_json(policy_blob_sha)
    return taste_semantics_digest(historical_policy)


def normalize_title(title):
    return unicodedata.normalize('NFKC', str(title)).lower()


def normalize_context_text(value):
    normalized = unicodedata.normalize('NFKC', str(value or '')).strip()
    return re.sub(r'\s+', ' ', normalized)


def normalize_bundle_member_name(value):
    return normalize_context_text(value).casefold()


def candidate_context_digest(taste_fingerprint_value, short_description, bundle_members):
    contract = load_json(CANDIDATE_CONTEXT_CONTRACT)
    if contract.get('contract') != 'TASTE-CANDIDATE-CONTEXT-V1':
        raise RuntimeError('Unexpected candidate context contract')

    projected_members = []
    for member in bundle_members or []:
        appid = str(member.get('appid') or '')
        if not appid.isdigit():
            raise ValueError(f'Invalid bundle member appid: {appid!r}')
        projected_members.append({
            'appid': appid,
            'normalized_name': normalize_bundle_member_name(member.get('name')),
        })
    projected_members.sort(key=lambda x: (int(x['appid']), x['normalized_name']))

    payload = {
        'taste_fingerprint': str(taste_fingerprint_value),
        'normalized_short_description': normalize_context_text(short_description),
        'sorted_bundle_members': projected_members,
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest(), payload


def taste_fingerprint(key, appid, title, fit_tags, core_fit_count, release_date):
    contract = load_json(FINGERPRINT_CONTRACT)
    if contract.get('contract') != 'TASTE-FINGERPRINT-V1':
        raise RuntimeError('Unexpected taste fingerprint contract')
    payload = {
        'key': key,
        'appid': str(appid),
        'normalized_title_for_taste': normalize_title(title),
        'sorted_fit_tags': sorted(fit_tags),
        'core_fit_count': int(core_fit_count),
        'release_date': release_date,
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def validate_verdict_shape(verdict, fit_level, reason_code):
    policy = load_json(POLICY)
    contract = load_json(LEDGER_CONTRACT)
    allowed = set(policy['decision_ledger']['allowed_decisions'])
    mapping = contract['cache_reason_code_semantics']
    spec = mapping.get(reason_code)
    if spec is None:
        raise ValueError(f'Unknown taste cache reason_code: {reason_code!r}')
    if verdict not in allowed or verdict != spec['decision']:
        raise ValueError(
            f'Verdict/reason mismatch: verdict={verdict!r} reason_code={reason_code!r}'
        )
    required_fit = spec.get('required_fit_level')
    if not fit_level or (required_fit is not None and fit_level != required_fit):
        raise ValueError(
            f'Fit/reason mismatch: fit_level={fit_level!r} reason_code={reason_code!r}'
        )
    return spec


def validate_taste_factors(factors):
    if not isinstance(factors, dict):
        raise ValueError('taste_factors must be an object')
    expected = set(TASTE_FACTOR_IDS)
    actual = set(factors)
    missing = expected - actual
    extra = actual - expected
    if missing or extra:
        raise ValueError(
            f'taste_factors must contain exactly {list(TASTE_FACTOR_IDS)!r}; '
            f'missing={sorted(missing)!r} extra={sorted(extra)!r}'
        )
    for factor_id in TASTE_FACTOR_IDS:
        value = factors[factor_id]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f'taste_factors.{factor_id} must be numeric')
        if not 0 <= float(value) <= 100:
            raise ValueError(f'taste_factors.{factor_id} must be within 0..100')
    return True


def schema_v2_entry_from_legacy(entry, legacy_semantics_sha):
    out = dict(entry)
    out['taste_semantics_sha256'] = legacy_semantics_sha
    return out


def validate_cache_entry(
    entry,
    map_key,
    required_fields,
    require_taste_factors=False,
    require_v4_negative_fields=False,
):
    if not isinstance(entry, dict):
        raise ValueError(f'Entry {map_key!r} must be an object')
    missing = [field for field in required_fields if field not in entry]
    if missing:
        raise ValueError(f'Entry {map_key!r} missing fields: {missing}')
    if entry['key'] != map_key:
        raise ValueError(f'Entry map key mismatch for {map_key!r}')
    if not str(entry['appid']).isdigit():
        raise ValueError(f'Entry {map_key!r} has invalid appid')
    if not isinstance(entry['positive_evidence'], list) or not isinstance(entry['negative_evidence'], list):
        raise ValueError(f'Entry {map_key!r} evidence fields must be arrays')
    validate_verdict_shape(entry['verdict'], entry['fit_level'], entry['reason_code'])
    if 'taste_factors' in entry:
        validate_taste_factors(entry['taste_factors'])
    elif require_taste_factors:
        raise ValueError(f'Entry {map_key!r} missing required taste_factors')
    validate_entry_negative_fields(entry, require_v4=require_v4_negative_fields)
    return True

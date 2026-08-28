import hashlib
import json
import subprocess
import time
import unicodedata
import urllib.request
from collections import Counter
from pathlib import Path

FAMILIES = Path('data/production/pre_ai/family_graph.json')
MAILING = Path('data/production/mailing/index.json')
POLICY = Path('config/mailing_policy.json')
FINGERPRINT_CONTRACT = Path('config/taste_fingerprint_contract.json')
TASTE_INDEX = Path('data/cache/taste_fit.index.json')
TASTE_CACHE = Path('data/cache/taste_fit.json')
LEDGER_VALIDATION = Path('data/cache/taste_fit.ledger_validation.json')
TASTE_VALIDATION = Path('data/cache/taste_fit.validation.json')
OUT = Path('data/production/pre_ai/taste_projection.json')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def git_blob_sha_bytes(raw):
    return hashlib.sha1(f'blob {len(raw)}\0'.encode('ascii') + raw).hexdigest()


def git_hash_object(path):
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def current_profile(policy):
    profile_cfg = policy['taste_profile']
    repo = profile_cfg['canonical_repository']
    path = profile_cfg['canonical_path']
    url = f'https://raw.githubusercontent.com/{repo}/main/{path}'
    req = urllib.request.Request(url, headers={'User-Agent': 'steam-kz-deals/1.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
    json.loads(raw.decode('utf-8'))
    return {
        'repository': repo,
        'path': path,
        'raw_url': url,
        'blob_sha': git_blob_sha_bytes(raw),
        'bytes': len(raw),
    }


def load_feed_fingerprints(index):
    cols = index['columns']
    ci = {name: i for i, name in enumerate(cols)}
    required = {'key', 'appid', 'title', 'fit_tags', 'core_fit_count', 'release_date'}
    if not required <= set(ci):
        raise SystemExit('Mailing feed lacks taste fingerprint fields')

    feed = {}
    for n in range(1, int(index['chunk_count']) + 1):
        p = Path(index['chunk_pattern'].replace('NNN', f'{n:03d}'))
        for line in p.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            cells = line.split('\t')
            if len(cells) != len(cols):
                raise SystemExit(f'Column mismatch in {p}')
            key = cells[ci['key']]
            payload = {
                'key': key,
                'appid': str(cells[ci['appid']]),
                'normalized_title_for_taste': unicodedata.normalize('NFKC', cells[ci['title']]).lower(),
                'sorted_fit_tags': sorted([] if cells[ci['fit_tags']] == '' else cells[ci['fit_tags']].split('|')),
                'core_fit_count': int(cells[ci['core_fit_count']]),
                'release_date': cells[ci['release_date']],
            }
            raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
            if key in feed:
                raise SystemExit(f'Duplicate mailing key: {key}')
            feed[key] = {
                'appid': payload['appid'],
                'title': cells[ci['title']],
                'fit_tags': payload['sorted_fit_tags'],
                'core_fit_count': payload['core_fit_count'],
                'release_date': payload['release_date'],
                'taste_fingerprint': hashlib.sha256(raw.encode('utf-8')).hexdigest(),
            }
    if len(feed) != int(index['item_count']):
        raise SystemExit('Mailing item_count mismatch')
    return feed


def policy_semantics_status(policy, ledger):
    bound_sha = (ledger.get('bindings') or {}).get('policy_blob_sha')
    semantic_keys = [
        'taste_profile',
        'taste_deal_separation',
        'personal_filter',
        'false_negative_audit',
        'taste_cache',
    ]
    if not bound_sha:
        return False, None, 'ledger_policy_binding_missing'
    try:
        raw = subprocess.check_output(['git', 'cat-file', 'blob', bound_sha])
        old = json.loads(raw.decode('utf-8'))
    except Exception:
        return False, bound_sha, 'ledger_bound_policy_blob_unavailable'
    equal = all(old.get(k) == policy.get(k) for k in semantic_keys)
    return equal, bound_sha, 'equal' if equal else 'taste_semantics_changed'


def main():
    started = time.monotonic()
    families_doc = load(FAMILIES)
    mailing = load(MAILING)
    policy = load(POLICY)
    fingerprint_contract = load(FINGERPRINT_CONTRACT)
    taste_index = load(TASTE_INDEX)
    taste_cache = load(TASTE_CACHE)
    ledger = load(LEDGER_VALIDATION)
    validation = load(TASTE_VALIDATION)

    if families_doc.get('status') != 'complete' or not families_doc.get('complete_coverage_of_nonexcluded_candidates'):
        raise SystemExit('Pre-AI family graph incomplete')
    if fingerprint_contract.get('contract') != 'TASTE-FINGERPRINT-V1':
        raise SystemExit('Unexpected taste fingerprint contract')

    canonical_fields = policy['taste_cache']['fingerprint_fields']
    contract_fields = fingerprint_contract['input_fields_in_serialization_order']
    if canonical_fields != contract_fields:
        raise SystemExit('Taste fingerprint contract differs from canonical policy')

    profile = current_profile(policy)
    feed = load_feed_fingerprints(mailing)
    families = families_doc.get('families') or []
    subjects = [family['taste_subject_key'] for family in families]
    if len(subjects) != int(families_doc.get('taste_subject_count') or -1):
        raise SystemExit('Taste subject count mismatch')
    if len(subjects) != len(set(subjects)):
        raise SystemExit('Duplicate taste subject key')
    if not set(subjects) <= set(feed):
        raise SystemExit('Taste subject missing from current mailing feed')

    current_model = policy['personal_filter']['structured_taste_evaluation']['taste_model_version']
    index_model = taste_index.get('taste_model_version')
    cache_profile_sha = taste_index.get('profile_blob_sha')
    profile_match = profile['blob_sha'] == cache_profile_sha
    model_match = current_model == index_model
    semantics_equal, bound_policy_sha, semantics_reason = policy_semantics_status(policy, ledger)

    index_entries = taste_index.get('entries') or {}
    index_count_ok = int(taste_index.get('index_entry_count') or -1) == len(index_entries)
    index_source = taste_index.get('source_cache') or {}
    source_cache_blob_ok = index_source.get('blob_sha') == git_hash_object(TASTE_CACHE)
    fingerprint_contract_blob_ok = (
        (validation.get('bindings') or {}).get('fingerprint_contract_blob_sha')
        == git_hash_object(FINGERPRINT_CONTRACT)
    )
    validation_complete = validation.get('status') == 'complete'
    ledger_complete = ledger.get('status') == 'complete' and bool(ledger.get('complete_ledger'))
    index_integrity_ok = all([
        index_count_ok,
        source_cache_blob_ok,
        fingerprint_contract_blob_ok,
        validation_complete,
        ledger_complete,
    ])

    global_reuse_allowed = all([
        index_integrity_ok,
        profile_match,
        model_match,
        semantics_equal,
    ])

    rows = {}
    status_counts = Counter()
    raw_overlap = 0
    fingerprint_matches = 0
    appid_matches = 0
    safe_hits = 0

    for family in families:
        key = family['taste_subject_key']
        current = feed[key]
        cached = index_entries.get(key)
        cache_presence = cached is not None
        if cache_presence:
            raw_overlap += 1
            cached_appid, cached_fp, verdict, fit_level, reason_code = cached
            appid_ok = str(cached_appid) == current['appid']
            fp_ok = cached_fp == current['taste_fingerprint']
            appid_matches += int(appid_ok)
            fingerprint_matches += int(fp_ok)
        else:
            appid_ok = False
            fp_ok = False
            verdict = fit_level = reason_code = None

        hit = bool(global_reuse_allowed and cache_presence and appid_ok and fp_ok)
        if hit:
            safe_hits += 1
            status = 'cache_hit'
            ai_reason = None
        else:
            status = 'ai_required'
            if not index_integrity_ok:
                ai_reason = 'taste_cache_integrity_not_current'
            elif not profile_match:
                ai_reason = 'canonical_profile_blob_changed'
            elif not model_match:
                ai_reason = 'taste_model_version_changed'
            elif not semantics_equal:
                ai_reason = 'taste_policy_semantics_changed_or_unverifiable'
            elif not cache_presence:
                ai_reason = 'taste_cache_key_missing'
            elif not appid_ok:
                ai_reason = 'taste_cache_appid_mismatch'
            else:
                ai_reason = 'taste_fingerprint_changed'
        status_counts[status] += 1

        row = {
            'family_id': family['family_id'],
            'taste_subject_key': key,
            'taste_subject_title': current['title'],
            'appid': current['appid'],
            'taste_fingerprint': current['taste_fingerprint'],
            'fit_tags': current['fit_tags'],
            'core_fit_count': current['core_fit_count'],
            'release_date': current['release_date'],
            'status': status,
            'ai_required_reason': ai_reason,
            'cache_entry_present': cache_presence,
            'cache_appid_matches': appid_ok if cache_presence else None,
            'cache_fingerprint_matches': fp_ok if cache_presence else None,
        }
        if hit:
            row['cached_taste'] = {
                'verdict': verdict,
                'fit_level': fit_level,
                'reason_code': reason_code,
            }
        rows[key] = row

    if len(rows) != len(subjects) or set(rows) != set(subjects):
        raise SystemExit('Taste projection coverage mismatch')

    out = {
        'schema_version': 1,
        'purpose': 'pre_ai_safe_taste_cache_projection_and_ai_work_queue',
        'status': 'complete',
        'source_mailing_updated_at_utc': mailing.get('source_updated_at_utc'),
        'taste_subject_count': len(subjects),
        'classified_count': len(rows),
        'complete_coverage': True,
        'current_profile': profile,
        'cache_binding': {
            'cache_profile_blob_sha': cache_profile_sha,
            'profile_binding_matches': profile_match,
            'cache_taste_model_version': index_model,
            'current_taste_model_version': current_model,
            'taste_model_matches': model_match,
            'ledger_bound_policy_blob_sha': bound_policy_sha,
            'current_policy_blob_sha': git_hash_object(POLICY),
            'taste_semantics_equal_to_ledger_policy': semantics_equal,
            'taste_semantics_check_reason': semantics_reason,
            'index_integrity_ok': index_integrity_ok,
            'index_entry_count_ok': index_count_ok,
            'index_source_cache_blob_matches': source_cache_blob_ok,
            'fingerprint_contract_blob_matches_validation': fingerprint_contract_blob_ok,
            'ledger_complete': ledger_complete,
            'taste_validation_complete': validation_complete,
            'global_cache_reuse_allowed': global_reuse_allowed,
        },
        'raw_cache_overlap_count': raw_overlap,
        'raw_cache_miss_count': len(subjects) - raw_overlap,
        'raw_appid_match_count': appid_matches,
        'raw_fingerprint_match_count': fingerprint_matches,
        'raw_fingerprint_stale_count': raw_overlap - fingerprint_matches,
        'safe_cache_hit_count': safe_hits,
        'ai_required_count': len(subjects) - safe_hits,
        'status_counts': dict(sorted(status_counts.items())),
        'external_calls': 1,
        'entries': rows,
        'elapsed_seconds': round(time.monotonic() - started, 3),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': out['status'],
        'taste_subject_count': out['taste_subject_count'],
        'complete_coverage': out['complete_coverage'],
        'current_profile_blob_sha': profile['blob_sha'],
        'cache_profile_blob_sha': cache_profile_sha,
        'profile_binding_matches': profile_match,
        'taste_model_matches': model_match,
        'taste_semantics_equal_to_ledger_policy': semantics_equal,
        'index_integrity_ok': index_integrity_ok,
        'raw_cache_overlap_count': raw_overlap,
        'raw_cache_miss_count': len(subjects) - raw_overlap,
        'raw_appid_match_count': appid_matches,
        'raw_fingerprint_match_count': fingerprint_matches,
        'raw_fingerprint_stale_count': raw_overlap - fingerprint_matches,
        'safe_cache_hit_count': safe_hits,
        'ai_required_count': len(subjects) - safe_hits,
        'external_calls': 1,
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

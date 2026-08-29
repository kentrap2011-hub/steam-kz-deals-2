import hashlib
import json
import subprocess
import time
import unicodedata
import urllib.request
from collections import Counter
from pathlib import Path

from taste_cache_common import (
    CANDIDATE_CONTEXT_CONTRACT,
    candidate_context_digest,
    current_taste_semantics_digest,
    legacy_v1_semantics_digest,
    validate_verdict_shape,
)

FAMILIES = Path('data/production/pre_ai/family_graph.json')
CONTENT_METADATA = Path('data/production/pre_ai/content_metadata.json')
MAILING = Path('data/production/mailing/index.json')
POLICY = Path('config/mailing_policy.json')
FINGERPRINT_CONTRACT = Path('config/taste_fingerprint_contract.json')
TASTE_INDEX = Path('data/cache/taste_fit.entry_index.json')
TASTE_CACHE = Path('data/cache/taste_fit.json')
TASTE_OVERLAY = Path('data/cache/taste_fit.entry_overlay.json')
OUT = Path('data/production/pre_ai/taste_projection.json')

V1_FIELDS = [
    'appid',
    'taste_fingerprint',
    'verdict',
    'fit_level',
    'reason_code',
]
V2_LEGACY_FIELDS = [
    'appid',
    'profile_blob_sha',
    'taste_model_version',
    'taste_semantics_sha256',
    'taste_fingerprint',
    'verdict',
    'fit_level',
    'reason_code',
]
V2_CONTEXT_FIELDS = [
    'appid',
    'profile_blob_sha',
    'taste_model_version',
    'taste_semantics_sha256',
    'candidate_context_sha256',
    'taste_fingerprint',
    'verdict',
    'fit_level',
    'reason_code',
]


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


def decode_index_entry(index, key, cached, legacy_semantics):
    schema = index.get('schema_version')
    fields = index.get('entry_fields')
    if schema == 1:
        if fields != V1_FIELDS:
            raise ValueError('Unexpected taste index v1 entry_fields')
        if not isinstance(cached, list) or len(cached) != len(V1_FIELDS):
            raise ValueError(f'Invalid taste index v1 shape for {key}')
        appid, fp, verdict, fit_level, reason_code = cached
        profile_sha = index.get('profile_blob_sha')
        model = index.get('taste_model_version')
        semantics = legacy_semantics
        context_sha = None
    elif schema == 2 and fields == V2_LEGACY_FIELDS:
        if index.get('profile_binding_mode') != 'per_entry_exact':
            raise ValueError('Taste index v2 is not per_entry_exact')
        if not isinstance(cached, list) or len(cached) != len(V2_LEGACY_FIELDS):
            raise ValueError(f'Invalid legacy taste index v2 shape for {key}')
        appid, profile_sha, model, semantics, fp, verdict, fit_level, reason_code = cached
        context_sha = None
    elif schema == 2 and fields == V2_CONTEXT_FIELDS:
        if index.get('profile_binding_mode') != 'per_entry_exact':
            raise ValueError('Taste index v2 is not per_entry_exact')
        if index.get('candidate_context_binding_mode') != 'per_entry_exact_nullable_for_legacy':
            raise ValueError('Taste index v2 candidate context binding mode is unexpected')
        if not isinstance(cached, list) or len(cached) != len(V2_CONTEXT_FIELDS):
            raise ValueError(f'Invalid context-aware taste index v2 shape for {key}')
        appid, profile_sha, model, semantics, context_sha, fp, verdict, fit_level, reason_code = cached
    else:
        raise ValueError(f'Unsupported taste index schema/fields: schema={schema!r} fields={fields!r}')

    validate_verdict_shape(verdict, fit_level, reason_code)
    if not profile_sha or not model or not semantics or not fp:
        raise ValueError(f'Incomplete taste cache binding for {key}')
    if context_sha is not None and (not isinstance(context_sha, str) or len(context_sha) != 64):
        raise ValueError(f'Invalid candidate context binding for {key}')
    return {
        'appid': str(appid),
        'profile_blob_sha': profile_sha,
        'taste_model_version': model,
        'taste_semantics_sha256': semantics,
        'candidate_context_sha256': context_sha,
        'taste_fingerprint': fp,
        'verdict': verdict,
        'fit_level': fit_level,
        'reason_code': reason_code,
    }


def main():
    started = time.monotonic()
    families_doc = load(FAMILIES)
    metadata_doc = load(CONTENT_METADATA)
    mailing = load(MAILING)
    policy = load(POLICY)
    fingerprint_contract = load(FINGERPRINT_CONTRACT)
    context_contract = load(CANDIDATE_CONTEXT_CONTRACT)
    taste_index = load(TASTE_INDEX)

    if families_doc.get('status') != 'complete' or not families_doc.get('complete_coverage_of_nonexcluded_candidates'):
        raise SystemExit('Pre-AI family graph incomplete')
    if metadata_doc.get('status') != 'complete' or not metadata_doc.get('complete_coverage'):
        raise SystemExit('Pre-AI content metadata incomplete')
    if metadata_doc.get('source_updated_at_utc') != mailing.get('source_updated_at_utc'):
        raise SystemExit('Content metadata stale versus current mailing feed')
    if fingerprint_contract.get('contract') != 'TASTE-FINGERPRINT-V1':
        raise SystemExit('Unexpected taste fingerprint contract')
    if context_contract.get('contract') != 'TASTE-CANDIDATE-CONTEXT-V1':
        raise SystemExit('Unexpected taste candidate context contract')
    if policy['taste_cache']['fingerprint_fields'] != fingerprint_contract['input_fields_in_serialization_order']:
        raise SystemExit('Taste fingerprint contract differs from canonical policy')

    profile = current_profile(policy)
    current_model = policy['personal_filter']['structured_taste_evaluation']['taste_model_version']
    current_semantics = current_taste_semantics_digest()
    feed = load_feed_fingerprints(mailing)
    metadata = metadata_doc.get('entries') or {}
    families = families_doc.get('families') or []
    subjects = [family['taste_subject_key'] for family in families]
    if len(subjects) != int(families_doc.get('taste_subject_count') or -1):
        raise SystemExit('Taste subject count mismatch')
    if len(subjects) != len(set(subjects)):
        raise SystemExit('Duplicate taste subject key')
    if not set(subjects) <= set(feed):
        raise SystemExit('Taste subject missing from current mailing feed')
    if not set(subjects) <= set(metadata):
        raise SystemExit('Taste subject missing from current content metadata')

    current_context = {}
    description_known_count = 0
    bundle_subject_count = 0
    for key in subjects:
        meta = metadata[key]
        short_description = meta.get('short_description') or ''
        bundle_members = meta.get('package_apps') or [] if meta.get('entity_kind') == 'sub' else []
        digest, projected = candidate_context_digest(
            feed[key]['taste_fingerprint'],
            short_description,
            bundle_members,
        )
        if projected['normalized_short_description']:
            description_known_count += 1
        if bundle_members:
            bundle_subject_count += 1
        current_context[key] = {
            'candidate_context_sha256': digest,
            'short_description': short_description or None,
            'bundle_members': bundle_members,
        }

    index_entries = taste_index.get('entries') or {}
    index_count_ok = int(taste_index.get('index_entry_count') or -1) == len(index_entries)
    index_source = taste_index.get('source_cache') or {}
    index_overlay = taste_index.get('source_overlay') or {}
    source_cache_blob_ok = index_source.get('blob_sha') == git_hash_object(TASTE_CACHE)
    source_overlay_blob_ok = index_overlay.get('blob_sha') == git_hash_object(TASTE_OVERLAY)
    source_attestation_ok = all([
        index_source.get('entry_count_matches_len_entries') is True,
        index_source.get('required_entry_fields_complete') is True,
        index_overlay.get('entry_count_matches_len_entries') is True,
        index_overlay.get('required_entry_fields_complete') is True,
        taste_index.get('merge_policy') == 'overlay_exact_key_wins',
    ])
    schema_supported = taste_index.get('schema_version') in {1, 2}
    legacy_semantics = legacy_v1_semantics_digest() if taste_index.get('schema_version') == 1 else None

    decoded_entries = {}
    semantic_shape_ok = True
    semantic_shape_error = None
    if index_count_ok and source_cache_blob_ok and source_overlay_blob_ok and source_attestation_ok and schema_supported:
        try:
            for key, cached in index_entries.items():
                decoded_entries[key] = decode_index_entry(taste_index, key, cached, legacy_semantics)
        except (ValueError, RuntimeError) as exc:
            semantic_shape_ok = False
            semantic_shape_error = str(exc)
    else:
        semantic_shape_ok = False

    index_integrity_ok = all([
        index_count_ok,
        source_cache_blob_ok,
        source_overlay_blob_ok,
        source_attestation_ok,
        schema_supported,
        semantic_shape_ok,
    ])

    rows = {}
    status_counts = Counter()
    raw_overlap = 0
    fingerprint_matches = 0
    context_matches = 0
    context_bound_entries = 0
    appid_matches = 0
    profile_matches = 0
    model_matches = 0
    semantics_matches = 0
    safe_hits = 0

    for family in families:
        key = family['taste_subject_key']
        current = feed[key]
        context = current_context[key]
        cached = decoded_entries.get(key) if index_integrity_ok else None
        cache_presence = cached is not None
        if cache_presence:
            raw_overlap += 1
            appid_ok = cached['appid'] == current['appid']
            fp_ok = cached['taste_fingerprint'] == current['taste_fingerprint']
            profile_ok = cached['profile_blob_sha'] == profile['blob_sha']
            model_ok = cached['taste_model_version'] == current_model
            semantics_ok = cached['taste_semantics_sha256'] == current_semantics
            cached_context = cached.get('candidate_context_sha256')
            context_bound = bool(cached_context)
            context_ok = context_bound and cached_context == context['candidate_context_sha256']
            appid_matches += int(appid_ok)
            fingerprint_matches += int(fp_ok)
            profile_matches += int(profile_ok)
            model_matches += int(model_ok)
            semantics_matches += int(semantics_ok)
            context_bound_entries += int(context_bound)
            context_matches += int(context_ok)
        else:
            appid_ok = fp_ok = profile_ok = model_ok = semantics_ok = context_bound = context_ok = False

        hit = bool(
            index_integrity_ok
            and cache_presence
            and appid_ok
            and profile_ok
            and model_ok
            and semantics_ok
            and fp_ok
            and context_ok
        )
        if hit:
            safe_hits += 1
            status = 'cache_hit'
            ai_reason = None
        else:
            status = 'ai_required'
            if not index_integrity_ok:
                ai_reason = 'taste_cache_index_integrity_invalid'
            elif not cache_presence:
                ai_reason = 'taste_cache_key_missing'
            elif not appid_ok:
                ai_reason = 'taste_cache_appid_mismatch'
            elif not profile_ok:
                ai_reason = 'canonical_profile_blob_changed_for_entry'
            elif not model_ok:
                ai_reason = 'taste_model_version_changed_for_entry'
            elif not semantics_ok:
                ai_reason = 'taste_policy_semantics_changed_for_entry'
            elif not fp_ok:
                ai_reason = 'taste_fingerprint_changed'
            elif not context_bound:
                ai_reason = 'candidate_context_binding_missing_for_entry'
            else:
                ai_reason = 'candidate_context_changed_for_entry'
        status_counts[status] += 1

        row = {
            'family_id': family['family_id'],
            'taste_subject_key': key,
            'taste_subject_title': current['title'],
            'appid': current['appid'],
            'taste_fingerprint': current['taste_fingerprint'],
            'candidate_context_sha256': context['candidate_context_sha256'],
            'short_description': context['short_description'],
            'bundle_members': context['bundle_members'],
            'fit_tags': current['fit_tags'],
            'core_fit_count': current['core_fit_count'],
            'release_date': current['release_date'],
            'status': status,
            'ai_required_reason': ai_reason,
            'cache_entry_present': cache_presence,
            'cache_appid_matches': appid_ok if cache_presence else None,
            'cache_profile_matches': profile_ok if cache_presence else None,
            'cache_model_matches': model_ok if cache_presence else None,
            'cache_semantics_matches': semantics_ok if cache_presence else None,
            'cache_fingerprint_matches': fp_ok if cache_presence else None,
            'cache_candidate_context_bound': context_bound if cache_presence else None,
            'cache_candidate_context_matches': context_ok if cache_presence else None,
        }
        if hit:
            row['cached_taste'] = {
                'verdict': cached['verdict'],
                'fit_level': cached['fit_level'],
                'reason_code': cached['reason_code'],
            }
        rows[key] = row

    if len(rows) != len(subjects) or set(rows) != set(subjects):
        raise SystemExit('Taste projection coverage mismatch')

    out = {
        'schema_version': 3,
        'purpose': 'pre_ai_safe_context_bound_per_entry_taste_cache_projection_and_ai_work_queue',
        'status': 'complete',
        'source_mailing_updated_at_utc': mailing.get('source_updated_at_utc'),
        'taste_subject_count': len(subjects),
        'classified_count': len(rows),
        'complete_coverage': True,
        'current_profile': profile,
        'current_binding': {
            'taste_model_version': current_model,
            'taste_semantics_sha256': current_semantics,
            'candidate_context_contract_blob_sha': git_hash_object(CANDIDATE_CONTEXT_CONTRACT),
            'content_metadata_blob_sha': git_hash_object(CONTENT_METADATA),
            'policy_blob_sha': git_hash_object(POLICY),
        },
        'candidate_context': {
            'binding_required_for_cache_hit': True,
            'description_known_count': description_known_count,
            'description_missing_count': len(subjects) - description_known_count,
            'description_coverage': round(description_known_count / len(subjects), 6) if subjects else 1.0,
            'bundle_subject_count': bundle_subject_count,
        },
        'cache_binding': {
            'index_schema_version': taste_index.get('schema_version'),
            'profile_binding_mode': 'legacy_global_projected_per_entry' if taste_index.get('schema_version') == 1 else taste_index.get('profile_binding_mode'),
            'candidate_context_binding_mode': taste_index.get('candidate_context_binding_mode'),
            'index_integrity_ok': index_integrity_ok,
            'index_entry_count_ok': index_count_ok,
            'index_source_cache_blob_matches': source_cache_blob_ok,
            'index_source_overlay_blob_matches': source_overlay_blob_ok,
            'index_source_attestation_ok': source_attestation_ok,
            'schema_supported': schema_supported,
            'semantic_shape_ok': semantic_shape_ok,
            'semantic_shape_error': semantic_shape_error,
            'cache_reuse_is_per_entry_exact': True,
        },
        'raw_cache_overlap_count': raw_overlap,
        'raw_cache_miss_count': len(subjects) - raw_overlap,
        'raw_appid_match_count': appid_matches,
        'raw_profile_match_count': profile_matches,
        'raw_model_match_count': model_matches,
        'raw_semantics_match_count': semantics_matches,
        'raw_fingerprint_match_count': fingerprint_matches,
        'raw_candidate_context_bound_count': context_bound_entries,
        'raw_candidate_context_match_count': context_matches,
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
        'index_schema_version': taste_index.get('schema_version'),
        'index_integrity_ok': index_integrity_ok,
        'description_known_count': description_known_count,
        'description_missing_count': len(subjects) - description_known_count,
        'current_profile_blob_sha': profile['blob_sha'],
        'current_taste_model_version': current_model,
        'current_taste_semantics_sha256': current_semantics,
        'raw_cache_overlap_count': raw_overlap,
        'raw_cache_miss_count': len(subjects) - raw_overlap,
        'raw_appid_match_count': appid_matches,
        'raw_profile_match_count': profile_matches,
        'raw_model_match_count': model_matches,
        'raw_semantics_match_count': semantics_matches,
        'raw_fingerprint_match_count': fingerprint_matches,
        'raw_candidate_context_bound_count': context_bound_entries,
        'raw_candidate_context_match_count': context_matches,
        'safe_cache_hit_count': safe_hits,
        'ai_required_count': len(subjects) - safe_hits,
        'external_calls': 1,
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

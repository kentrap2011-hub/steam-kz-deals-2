import hashlib
import json
from collections import Counter
from pathlib import Path

from taste_cache_common import (
    ENTRY_CONTRACT,
    git_blob_sha_path,
    legacy_v1_semantics_digest,
    load_json,
    schema_v2_entry_from_legacy,
    validate_cache_entry,
)

SOURCE = Path('data/cache/taste_fit.json')
OVERLAY = Path('data/cache/taste_fit.entry_overlay.json')
OUT = Path('data/cache/taste_fit.entry_index.json')


def compact_entry(entry):
    return [
        entry['appid'],
        entry['profile_blob_sha'],
        entry['taste_model_version'],
        entry['taste_semantics_sha256'],
        entry['taste_fingerprint'],
        entry['verdict'],
        entry['fit_level'],
        entry['reason_code'],
    ]


def main():
    contract = load_json(ENTRY_CONTRACT)
    if contract.get('contract') != 'TASTE-CACHE-ENTRY-BINDING-V2':
        raise SystemExit('Unexpected per-entry taste cache contract')
    required_v2 = contract['schema_v2_required_entry_fields']

    source_raw = SOURCE.read_bytes()
    cache = json.loads(source_raw.decode('utf-8'))
    source_schema = cache.get('schema_version')
    if source_schema not in {1, 2}:
        raise SystemExit(f'Unsupported taste cache schema_version: {source_schema!r}')
    source_entries = cache.get('entries')
    if not isinstance(source_entries, dict):
        raise SystemExit('taste_fit.json entries must be an object')
    if cache.get('entry_count') != len(source_entries):
        raise SystemExit('taste_fit.json entry_count mismatch')

    overlay_raw = OVERLAY.read_bytes()
    overlay = json.loads(overlay_raw.decode('utf-8'))
    if overlay.get('schema_version') != 1 or overlay.get('entry_schema_version') != 2:
        raise SystemExit('Unexpected taste overlay schema')
    overlay_entries = overlay.get('entries')
    if not isinstance(overlay_entries, dict):
        raise SystemExit('taste overlay entries must be an object')
    if overlay.get('entry_count') != len(overlay_entries):
        raise SystemExit('taste overlay entry_count mismatch')

    legacy_semantics = legacy_v1_semantics_digest() if source_schema == 1 else None
    merged_entries = {}
    for key, raw_entry in source_entries.items():
        if source_schema == 1:
            if raw_entry.get('profile_blob_sha') != cache.get('profile_blob_sha'):
                raise SystemExit(f'Legacy entry {key} profile differs from legacy generation')
            if raw_entry.get('taste_model_version') != cache.get('taste_model_version'):
                raise SystemExit(f'Legacy entry {key} model differs from legacy generation')
            entry = schema_v2_entry_from_legacy(raw_entry, legacy_semantics)
        else:
            entry = raw_entry
        try:
            validate_cache_entry(entry, key, required_v2)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        merged_entries[key] = entry

    overlay_replace_count = 0
    overlay_new_count = 0
    for key, entry in overlay_entries.items():
        try:
            validate_cache_entry(entry, key, required_v2)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        if key in merged_entries:
            overlay_replace_count += 1
        else:
            overlay_new_count += 1
        merged_entries[key] = entry

    compact = {}
    profile_counts = Counter()
    model_counts = Counter()
    semantics_counts = Counter()
    for key, entry in merged_entries.items():
        profile_counts[entry['profile_blob_sha']] += 1
        model_counts[entry['taste_model_version']] += 1
        semantics_counts[entry['taste_semantics_sha256']] += 1
        compact[key] = compact_entry(entry)

    canonical_compact = json.dumps(
        compact,
        ensure_ascii=False,
        sort_keys=True,
        separators=(',', ':'),
    ).encode('utf-8')

    out = {
        'schema_version': 2,
        'purpose': 'compact_verified_per_entry_projection_of_legacy_cache_plus_incremental_overlay',
        'profile_binding_mode': 'per_entry_exact',
        'source_cache': {
            'path': str(SOURCE),
            'blob_sha': git_blob_sha_path(SOURCE),
            'size_bytes': len(source_raw),
            'schema_version': source_schema,
            'entry_count_declared': cache.get('entry_count'),
            'entry_count_actual': len(source_entries),
            'entry_count_matches_len_entries': True,
            'required_entry_fields_complete': True,
            'legacy_schema_v1_semantics_binding_derived': source_schema == 1,
        },
        'source_overlay': {
            'path': str(OVERLAY),
            'blob_sha': git_blob_sha_path(OVERLAY),
            'size_bytes': len(overlay_raw),
            'schema_version': overlay.get('schema_version'),
            'entry_schema_version': overlay.get('entry_schema_version'),
            'entry_count_declared': overlay.get('entry_count'),
            'entry_count_actual': len(overlay_entries),
            'entry_count_matches_len_entries': True,
            'required_entry_fields_complete': True,
            'replace_existing_key_count': overlay_replace_count,
            'new_key_count': overlay_new_count,
        },
        'merge_policy': 'overlay_exact_key_wins',
        'entry_fields': [
            'appid',
            'profile_blob_sha',
            'taste_model_version',
            'taste_semantics_sha256',
            'taste_fingerprint',
            'verdict',
            'fit_level',
            'reason_code',
        ],
        'index_entry_count': len(compact),
        'entries_digest_sha256': hashlib.sha256(canonical_compact).hexdigest(),
        'profile_binding_counts': dict(sorted(profile_counts.items())),
        'taste_model_counts': dict(sorted(model_counts.items())),
        'taste_semantics_counts': dict(sorted(semantics_counts.items())),
        'source_updated_at_utc': cache.get('updated_at_utc'),
        'entries': compact,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': 'complete',
        'output': str(OUT),
        'source_cache_schema': source_schema,
        'legacy_entry_count': len(source_entries),
        'overlay_entry_count': len(overlay_entries),
        'overlay_replace_count': overlay_replace_count,
        'overlay_new_count': overlay_new_count,
        'merged_entry_count': len(compact),
        'profile_generation_count': len(profile_counts),
        'model_generation_count': len(model_counts),
        'semantics_generation_count': len(semantics_counts),
        'legacy_semantics_derived': source_schema == 1,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

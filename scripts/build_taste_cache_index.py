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
OUT = Path('data/cache/taste_fit.entry_index.json')


def main():
    contract = load_json(ENTRY_CONTRACT)
    if contract.get('contract') != 'TASTE-CACHE-ENTRY-BINDING-V2':
        raise SystemExit('Unexpected per-entry taste cache contract')

    source_raw = SOURCE.read_bytes()
    cache = json.loads(source_raw.decode('utf-8'))
    schema = cache.get('schema_version')
    if schema not in {1, 2}:
        raise SystemExit(f'Unsupported taste cache schema_version: {schema!r}')

    entries = cache.get('entries')
    if not isinstance(entries, dict):
        raise SystemExit('taste_fit.json entries must be an object')
    if cache.get('entry_count') != len(entries):
        raise SystemExit('taste_fit.json entry_count mismatch')

    required_v2 = contract['schema_v2_required_entry_fields']
    legacy_semantics = legacy_v1_semantics_digest() if schema == 1 else None
    compact = {}
    profile_counts = Counter()
    model_counts = Counter()
    semantics_counts = Counter()

    for key, raw_entry in entries.items():
        if schema == 1:
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

        profile = entry['profile_blob_sha']
        model = entry['taste_model_version']
        semantics = entry['taste_semantics_sha256']
        profile_counts[profile] += 1
        model_counts[model] += 1
        semantics_counts[semantics] += 1
        compact[key] = [
            entry['appid'],
            profile,
            model,
            semantics,
            entry['taste_fingerprint'],
            entry['verdict'],
            entry['fit_level'],
            entry['reason_code'],
        ]

    canonical_compact = json.dumps(
        compact,
        ensure_ascii=False,
        sort_keys=True,
        separators=(',', ':'),
    ).encode('utf-8')

    out = {
        'schema_version': 2,
        'purpose': 'compact_verified_per_entry_projection_of_taste_fit_cache',
        'profile_binding_mode': 'per_entry_exact',
        'source_cache': {
            'path': str(SOURCE),
            'blob_sha': git_blob_sha_path(SOURCE),
            'size_bytes': len(source_raw),
            'schema_version': schema,
            'entry_count_declared': cache.get('entry_count'),
            'entry_count_actual': len(entries),
            'entry_count_matches_len_entries': True,
            'required_entry_fields_complete': True,
            'legacy_schema_v1_semantics_binding_derived': schema == 1,
        },
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
        'source_cache_schema': schema,
        'entry_count': len(compact),
        'profile_generation_count': len(profile_counts),
        'model_generation_count': len(model_counts),
        'semantics_generation_count': len(semantics_counts),
        'legacy_semantics_derived': schema == 1,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

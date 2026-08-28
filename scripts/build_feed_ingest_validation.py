import json
import subprocess
from pathlib import Path

POLICY = Path('config/mailing_policy.json')
CONTRACT = Path('config/feed_integrity_contract.json')
MANIFEST = Path('data/production/manifest.json')
SOURCE_INDEX = Path('data/production/shortlist/index.json')
MAILING_INDEX = Path('data/production/mailing/index.json')
OUT = Path('data/cache/feed_ingest.validation.json')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def git_sha(path):
    return subprocess.check_output(['git', 'rev-parse', f'HEAD:{path}'], text=True).strip()


def line_count(path):
    with path.open('r', encoding='utf-8') as fh:
        return sum(1 for _ in fh)


policy = load(POLICY)
contract = load(CONTRACT)
manifest = load(MANIFEST)
source_index = load(SOURCE_INDEX)
mailing_index = load(MAILING_INDEX)

if policy.get('status') != 'canonical':
    raise SystemExit('Canonical policy not loaded/valid')
if contract.get('contract') != 'PRODUCTION-FEED-INTEGRITY-FAST-PATH' or contract.get('version') != '1.1':
    raise SystemExit('Unexpected feed integrity contract')

qa = policy['ingest_qa']
att = mailing_index.get('integrity_attestation') or {}
if att.get('proof_method') != 'content_addressed_producer_attestation':
    raise SystemExit('Producer integrity attestation absent')

# Canonical top-level QA.
checks = {
    'manifest_complete': manifest.get('complete') is True,
    'manifest_coverage': float(manifest.get('coverage_ratio') or 0) >= float(qa['minimum_coverage_ratio']),
    'manifest_needs_tuning': manifest.get('needs_tuning') is False,
    'source_complete': source_index.get('source_complete') is True,
    'source_coverage': float(source_index.get('source_coverage_ratio') or 0) >= float(qa['minimum_source_index_coverage_ratio']),
    'source_needs_tuning': source_index.get('needs_tuning') is False,
    'country_code_kz': source_index.get('country_code') == 'kz' and mailing_index.get('country_code') == 'kz',
    'mailing_has_no_header': mailing_index.get('has_header') is False,
    'review_selection_rule': manifest.get('review_selection_rule') == qa['required_review_selection_rule'] and source_index.get('review_selection_rule') == qa['required_review_selection_rule'],
    'review_count_basis': manifest.get('review_count_basis') == qa['required_review_count_basis'] and source_index.get('review_count_basis') == qa['required_review_count_basis'],
    'russian_review_count_cap': int(manifest.get('russian_review_count_cap') or -1) == int(qa['required_russian_review_count_cap']) and int(source_index.get('russian_review_count_cap') or -1) == int(qa['required_russian_review_count_cap']),
    'russian_rating_comparison': manifest.get('russian_rating_comparison') == qa['required_russian_rating_comparison'] and source_index.get('russian_rating_comparison') == qa['required_russian_rating_comparison'],
    'review_policy_regression_guard': manifest.get('review_policy_regression_guard') is qa['require_review_policy_regression_guard'] and source_index.get('review_policy_regression_guard') is qa['require_review_policy_regression_guard'],
    'optimized_item_count_matches_source': int(mailing_index.get('item_count') or -1) == int(source_index.get('item_count') or -2),
    'optimized_source_count_matches_source': int(mailing_index.get('source_item_count') or -1) == int(source_index.get('item_count') or -2),
    'optimized_updated_at_matches_source': mailing_index.get('source_updated_at_utc') == source_index.get('source_updated_at_utc'),
    'optimized_reports_all_source_chunks': len(mailing_index.get('source_files_verified') or []) == int(source_index.get('chunk_count') or -1),
}
if not all(checks.values()):
    raise SystemExit(f'Canonical feed QA failed: {[k for k,v in checks.items() if not v]}')

# Manifest/source-index exact blob and size identity against producer attestation.
for label, path, descriptor in [
    ('manifest', MANIFEST, att.get('source_manifest') or {}),
    ('source_index', SOURCE_INDEX, att.get('source_index') or {}),
]:
    if descriptor.get('path') != path.as_posix():
        raise SystemExit(f'{label} descriptor path mismatch')
    if descriptor.get('git_blob_sha') != git_sha(path.as_posix()):
        raise SystemExit(f'{label} descriptor blob mismatch')
    if int(descriptor.get('size_bytes') or -1) != path.stat().st_size:
        raise SystemExit(f'{label} descriptor size mismatch')


def validate_chunks(directory, descriptors, expected_count, expected_rows, label):
    paths = sorted(directory.glob('chunk_*.tsv'))
    descriptor_by_path = {d['path']: d for d in descriptors}
    actual_path_set = {p.as_posix() for p in paths}
    descriptor_path_set = set(descriptor_by_path)
    if actual_path_set != descriptor_path_set:
        raise SystemExit(f'{label} exact chunk path set mismatch')
    if len(paths) != int(expected_count):
        raise SystemExit(f'{label} actual chunk count mismatch')
    rows = 0
    for path in paths:
        desc = descriptor_by_path[path.as_posix()]
        blob = git_sha(path.as_posix())
        size = path.stat().st_size
        count = line_count(path)
        if blob != desc.get('git_blob_sha'):
            raise SystemExit(f'{label} blob mismatch: {path}')
        if size != int(desc.get('size_bytes') or -1):
            raise SystemExit(f'{label} size mismatch: {path}')
        if count != int(desc.get('row_count') or -1):
            raise SystemExit(f'{label} row count mismatch: {path}')
        rows += count
    if rows != int(expected_rows):
        raise SystemExit(f'{label} total rows mismatch: {rows} != {expected_rows}')
    return len(paths), rows


source_chunk_count, source_rows = validate_chunks(
    Path('data/production/shortlist'),
    att.get('source_chunks') or [],
    source_index['chunk_count'],
    source_index['item_count'],
    'source',
)
mailing_chunk_count, mailing_rows = validate_chunks(
    Path('data/production/mailing'),
    att.get('mailing_chunks') or [],
    mailing_index['chunk_count'],
    mailing_index['item_count'],
    'mailing',
)

attestation_checks = {
    'source_chunk_count_verified': int(att.get('source_chunk_count_verified') or -1) == source_chunk_count,
    'mailing_chunk_count_verified': int(att.get('mailing_chunk_count_verified') or -1) == mailing_chunk_count,
    'source_rows_verified': int(att.get('source_rows_verified') or -1) == source_rows,
    'mailing_rows_verified': int(att.get('mailing_rows_verified') or -1) == mailing_rows,
    'projection_lossless': att.get('source_to_mailing_row_projection_lossless') is True,
    'source_columns_validated': att.get('all_source_rows_column_validated') is True,
}
if not all(attestation_checks.values()):
    raise SystemExit(f'Producer attestation invariant failed: {[k for k,v in attestation_checks.items() if not v]}')

out = {
    'schema_version': 1,
    'purpose': 'compact_runtime_proof_of_canonical_feed_ingest_qa',
    'status': 'complete',
    'contract_version': contract['version'],
    'bindings': {
        'policy_blob_sha': git_sha('config/mailing_policy.json'),
        'feed_integrity_contract_blob_sha': git_sha('config/feed_integrity_contract.json'),
        'manifest_blob_sha': git_sha('data/production/manifest.json'),
        'source_index_blob_sha': git_sha('data/production/shortlist/index.json'),
        'mailing_index_blob_sha': git_sha('data/production/mailing/index.json'),
        'shortlist_tree_sha': git_sha('data/production/shortlist'),
        'mailing_tree_sha': git_sha('data/production/mailing'),
    },
    'country_code': 'kz',
    'item_count': int(mailing_index['item_count']),
    'source_item_count': int(source_index['item_count']),
    'source_chunk_count': source_chunk_count,
    'mailing_chunk_count': mailing_chunk_count,
    'source_rows_verified': source_rows,
    'mailing_rows_verified': mailing_rows,
    'manifest_complete': manifest.get('complete') is True,
    'manifest_coverage_ratio': manifest.get('coverage_ratio'),
    'manifest_needs_tuning': manifest.get('needs_tuning'),
    'source_complete': source_index.get('source_complete') is True,
    'source_coverage_ratio': source_index.get('source_coverage_ratio'),
    'needs_tuning': source_index.get('needs_tuning'),
    'source_to_mailing_row_projection_lossless': True,
    'all_source_rows_column_validated': True,
    'canonical_qa_checks': checks,
    'attestation_checks': attestation_checks,
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({
    'status': out['status'],
    'item_count': out['item_count'],
    'source_rows_verified': source_rows,
    'mailing_rows_verified': mailing_rows,
    'source_chunk_count': source_chunk_count,
    'mailing_chunk_count': mailing_chunk_count,
    'shortlist_tree_sha': out['bindings']['shortlist_tree_sha'],
    'mailing_tree_sha': out['bindings']['mailing_tree_sha'],
}, ensure_ascii=False, indent=2))

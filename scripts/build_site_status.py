#!/usr/bin/env python3
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import progressive_pass1
import progressive_pass2
import progressive_personalization
import site_publication_resilience

ROOT = Path('.')
OUT = ROOT / 'data/production/site/current_status.json'
CONTRACT_PATH = ROOT / 'config/site_publication_resilience_contract.json'

SOURCE_PATHS = {
    'progressive_candidate_context_blob_sha': progressive_personalization.PROGRESSIVE_CONTEXT,
    'progressive_pass1_work_blob_sha': progressive_pass1.WORK,
    'progressive_pass1_state_blob_sha': progressive_pass1.STATE,
    'progressive_pass2_work_blob_sha': progressive_pass2.WORK,
    'progressive_pass2_state_blob_sha': progressive_pass2.STATE,
    'dossier_work_blob_sha': progressive_pass2.DOSSIER_WORK,
    'russian_description_status_blob_sha': progressive_personalization.RUSSIAN_TRANSLATION_STATUS,
    'publication_quarantine_blob_sha': site_publication_resilience.QUARANTINE_PATH,
    'progressive_personalization_contract_blob_sha': progressive_personalization.CONTRACT,
    'site_publication_resilience_contract_blob_sha': CONTRACT_PATH,
}

FAST_SCOPE_FIELDS = (
    'fast_total_current_scope',
    'fast_attempted_count',
    'fast_completed_fit_count',
    'fast_completed_not_fit_count',
    'fast_incomplete_count',
    'fast_error_count',
    'fast_skipped_due_to_authoritative_deep_count',
    'fast_remaining_count',
)
DEEP_SCOPE_FIELDS = (
    'deep_total_current_coverage_target',
    'deep_first_pass_attempted_count',
    'deep_authoritative_completed_count',
    'deep_completed_fit_count',
    'deep_completed_not_fit_count',
    'deep_incomplete_or_recovery_count',
    'deep_waiting_for_dossier_count',
    'deep_ready_or_pending_count',
    'deep_normal_first_pass_remaining_count',
    'deep_remaining_until_all_authoritative_count',
    'deep_normal_first_pass_complete',
    'deep_all_current_authoritative_complete',
)


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def working_blob_sha(path):
    path = str(path)
    candidate = Path(path)
    if not candidate.is_file():
        raise RuntimeError(f'missing site-status source: {path}')
    return subprocess.check_output(['git', 'hash-object', path], text=True).strip()


def source_bindings():
    return {key: working_blob_sha(path) for key, path in SOURCE_PATHS.items()}


def _require_scope_match(processing_status, scope, fields, label):
    for field in fields:
        if field not in scope:
            raise RuntimeError(f'{label} source scope missing {field}')
        if processing_status.get(field) != scope.get(field):
            raise RuntimeError(
                f'{label} statistics mismatch for {field}: '
                f'status={processing_status.get(field)!r} source={scope.get(field)!r}'
            )


def build_document(generated_at_utc=None):
    contract = load_json(CONTRACT_PATH)
    if contract.get('contract') != 'SITE-PUBLICATION-RESILIENCE-V1' or contract.get('status') != 'canonical':
        raise RuntimeError('site publication resilience contract is not canonical')

    state_index = progressive_personalization.build_state_index()
    processing_status = progressive_personalization.build_processing_status(
        state_index,
        None,
        business_excluded_family_ids=None,
    )
    progressive_personalization.validate_processing_status(processing_status)

    pass1_scope = (load_json(progressive_pass1.WORK).get('scope') or {})
    pass2_scope = (load_json(progressive_pass2.WORK).get('scope') or {})
    _require_scope_match(processing_status, pass1_scope, FAST_SCOPE_FIELDS, 'Fast')
    _require_scope_match(processing_status, pass2_scope, DEEP_SCOPE_FIELDS, 'Deep')

    if processing_status.get('dossier_observability') != 'available':
        raise RuntimeError('Dossier statistics are not canonically observable')
    if processing_status.get('translation_observability') != 'available':
        raise RuntimeError('Russian translation statistics are not canonically observable')

    quarantine = site_publication_resilience.load_quarantine()
    qsummary = site_publication_resilience.active_summary(quarantine)
    generated_at = generated_at_utc or utc_now()
    processing_status = dict(processing_status)
    processing_status.update({
        'site_quarantine_pending_count': qsummary['pending_count'],
        'site_quarantine_category_counts': qsummary['category_counts'],
        'site_quarantine_last_change_at_utc': qsummary['last_change_at_utc'],
        'site_status_generated_at_utc': generated_at,
    })

    return {
        'schema_version': 1,
        'contract': 'SITE-CURRENT-STATUS-V1',
        'generated_at_utc': generated_at,
        'source_bindings': source_bindings(),
        'processing_status': processing_status,
        'publication_quarantine': {
            'pending_count': qsummary['pending_count'],
            'category_counts': qsummary['category_counts'],
            'last_change_at_utc': qsummary['last_change_at_utc'],
        },
    }


def validate_document(doc, *, require_current_bindings=False):
    if not isinstance(doc, dict):
        raise RuntimeError('site current status must be an object')
    if doc.get('schema_version') != 1 or doc.get('contract') != 'SITE-CURRENT-STATUS-V1':
        raise RuntimeError('site current status contract mismatch')
    if not doc.get('generated_at_utc'):
        raise RuntimeError('site current status generated_at_utc missing')

    status = doc.get('processing_status')
    if not isinstance(status, dict):
        raise RuntimeError('site current status processing_status missing')
    progressive_personalization.validate_processing_status(status)

    quarantine = doc.get('publication_quarantine')
    if not isinstance(quarantine, dict):
        raise RuntimeError('site current status quarantine summary missing')
    if int(quarantine.get('pending_count') or 0) != int(status.get('site_quarantine_pending_count') or 0):
        raise RuntimeError('site current status quarantine count mismatch')
    if (quarantine.get('category_counts') or {}) != (status.get('site_quarantine_category_counts') or {}):
        raise RuntimeError('site current status quarantine category mismatch')

    pass1_scope = (load_json(progressive_pass1.WORK).get('scope') or {})
    pass2_scope = (load_json(progressive_pass2.WORK).get('scope') or {})
    _require_scope_match(status, pass1_scope, FAST_SCOPE_FIELDS, 'Fast')
    _require_scope_match(status, pass2_scope, DEEP_SCOPE_FIELDS, 'Deep')

    if require_current_bindings:
        current = source_bindings()
        published = doc.get('source_bindings') or {}
        mismatches = {
            key: {'published': published.get(key), 'current': value}
            for key, value in current.items()
            if published.get(key) != value
        }
        if mismatches:
            raise RuntimeError(
                'site current status source binding mismatch: '
                + json.dumps(mismatches, ensure_ascii=False, separators=(',', ':'))
            )
        current_q = site_publication_resilience.active_summary()
        if int(quarantine.get('pending_count') or 0) != int(current_q.get('pending_count') or 0):
            raise RuntimeError('site current status quarantine summary is stale')
        if (quarantine.get('category_counts') or {}) != (current_q.get('category_counts') or {}):
            raise RuntimeError('site current status quarantine categories are stale')
    return doc


def write_current():
    doc = build_document()
    validate_document(doc, require_current_bindings=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(
        'SITE_STATUS=BUILT '
        f"generated={doc['generated_at_utc']} "
        f"deep_completed={doc['processing_status'].get('deep_authoritative_completed_count')} "
        f"quarantine={doc['publication_quarantine'].get('pending_count')}"
    )
    return doc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--validate-current', metavar='PATH')
    args = parser.parse_args()
    if args.validate_current:
        doc = load_json(args.validate_current)
        validate_document(doc, require_current_bindings=True)
        print(
            'SITE_STATUS=VALID_CURRENT '
            f"generated={doc.get('generated_at_utc')} "
            f"deep_completed={(doc.get('processing_status') or {}).get('deep_authoritative_completed_count')}"
        )
        return
    write_current()


if __name__ == '__main__':
    main()

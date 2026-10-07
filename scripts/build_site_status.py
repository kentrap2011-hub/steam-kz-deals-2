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
    'progressive_pass1_work_blob_sha': progressive_pass1.WORK,
    'progressive_pass1_state_blob_sha': progressive_pass1.STATE,
    'progressive_pass2_work_blob_sha': progressive_pass2.WORK,
    'progressive_pass2_state_blob_sha': progressive_pass2.STATE,
    'dossier_work_blob_sha': progressive_pass2.DOSSIER_WORK,
    'russian_description_status_blob_sha': progressive_personalization.RUSSIAN_TRANSLATION_STATUS,
    'publication_quarantine_blob_sha': site_publication_resilience.QUARANTINE_PATH,
    'progressive_personalization_contract_blob_sha': progressive_personalization.CONTRACT,
    'progressive_pass1_contract_blob_sha': progressive_pass1.CONTRACT,
    'progressive_pass2_contract_blob_sha': progressive_pass2.CONTRACT,
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


def _normalized_timestamp(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace('Z', '+00:00')
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _last_state_write(state_doc, generation_id):
    values = []
    for entry in (state_doc.get('entries') or {}).values():
        if not isinstance(entry, dict):
            continue
        if generation_id and entry.get('semantic_generation_id') != generation_id:
            continue
        accepted = _normalized_timestamp(entry.get('accepted_at_utc'))
        if accepted:
            values.append(accepted)
    return max(values) if values else None


def _copy_scope(scope, fields, label):
    result = {}
    for field in fields:
        if field not in scope:
            raise RuntimeError(f'{label} source scope missing {field}')
        result[field] = scope[field]
    return result


def validate_stage_status(status):
    required = {
        *FAST_SCOPE_FIELDS,
        *DEEP_SCOPE_FIELDS,
        'fast_last_write_at_utc',
        'dossier_observability',
        'dossier_last_write_at_utc',
        'dossier_total_current_scope',
        'dossier_accepted_count',
        'dossier_pending_count',
        'dossier_failed_or_recovery_count',
        'deep_last_write_at_utc',
        'translation_observability',
        'untranslated_game_count',
        'translation_diagnostic_count',
        'last_translation_attempt_at_utc',
        'last_successful_translation_at_utc',
        'site_quarantine_pending_count',
        'site_quarantine_category_counts',
        'site_status_generated_at_utc',
    }
    missing = sorted(required - set(status))
    if missing:
        raise RuntimeError(f'site status missing required fields: {missing}')

    fast_total = int(status['fast_total_current_scope'])
    fast_attempted = int(status['fast_attempted_count'])
    fast_skipped = int(status['fast_skipped_due_to_authoritative_deep_count'])
    fast_remaining = int(status['fast_remaining_count'])
    if fast_total != fast_attempted + fast_skipped + fast_remaining:
        raise RuntimeError('site status Fast current-scope arithmetic mismatch')
    if fast_attempted != (
        int(status['fast_completed_fit_count'])
        + int(status['fast_completed_not_fit_count'])
        + int(status['fast_incomplete_count'])
        + int(status['fast_error_count'])
    ):
        raise RuntimeError('site status Fast attempted-outcome arithmetic mismatch')

    dossier_total = int(status['dossier_total_current_scope'])
    if dossier_total != (
        int(status['dossier_accepted_count'])
        + int(status['dossier_pending_count'])
        + int(status['dossier_failed_or_recovery_count'])
    ):
        raise RuntimeError('site status Dossier arithmetic mismatch')

    deep_total = int(status['deep_total_current_coverage_target'])
    deep_first = int(status['deep_first_pass_attempted_count'])
    deep_authoritative = int(status['deep_authoritative_completed_count'])
    if deep_first + int(status['deep_normal_first_pass_remaining_count']) != deep_total:
        raise RuntimeError('site status Deep first-pass arithmetic mismatch')
    if deep_authoritative + int(status['deep_remaining_until_all_authoritative_count']) != deep_total:
        raise RuntimeError('site status Deep authoritative arithmetic mismatch')
    if deep_authoritative != (
        int(status['deep_completed_fit_count']) + int(status['deep_completed_not_fit_count'])
    ):
        raise RuntimeError('site status Deep completed-outcome arithmetic mismatch')
    if bool(status['deep_normal_first_pass_complete']) != (
        int(status['deep_normal_first_pass_remaining_count']) == 0
    ):
        raise RuntimeError('site status Deep first-pass completion mismatch')
    if bool(status['deep_all_current_authoritative_complete']) != (
        int(status['deep_remaining_until_all_authoritative_count']) == 0
    ):
        raise RuntimeError('site status Deep authoritative completion mismatch')

    if status.get('dossier_observability') != 'available':
        raise RuntimeError('Dossier statistics are not canonically observable')
    if status.get('translation_observability') != 'available':
        raise RuntimeError('Russian translation statistics are not canonically observable')
    untranslated = int(status['untranslated_game_count'])
    diagnostics = int(status['translation_diagnostic_count'])
    if untranslated < 0 or diagnostics < 0 or diagnostics > untranslated:
        raise RuntimeError('site status translation arithmetic mismatch')

    pending = int(status['site_quarantine_pending_count'])
    categories = status.get('site_quarantine_category_counts')
    if pending < 0 or not isinstance(categories, dict):
        raise RuntimeError('site status quarantine summary invalid')
    if sum(int(value) for value in categories.values()) != pending:
        raise RuntimeError('site status quarantine category arithmetic mismatch')

    for field in (
        'fast_last_write_at_utc',
        'dossier_last_write_at_utc',
        'deep_last_write_at_utc',
        'last_translation_attempt_at_utc',
        'last_successful_translation_at_utc',
        'site_quarantine_last_change_at_utc',
        'site_status_generated_at_utc',
    ):
        value = status.get(field)
        if value is not None and _normalized_timestamp(value) is None:
            raise RuntimeError(f'site status timestamp invalid: {field}')
    return status


def build_processing_status(generated_at):
    pass1_work = load_json(progressive_pass1.WORK)
    pass2_work = load_json(progressive_pass2.WORK)
    pass1_scope = pass1_work.get('scope') or {}
    pass2_scope = pass2_work.get('scope') or {}

    status = {}
    status.update(_copy_scope(pass1_scope, FAST_SCOPE_FIELDS, 'Fast'))
    status['fast_last_write_at_utc'] = _last_state_write(
        progressive_pass1.load_json(progressive_pass1.STATE),
        pass1_work.get('semantic_generation_id'),
    )

    dossier = progressive_personalization._dossier_processing_metrics()
    status.update(dossier)

    status.update(_copy_scope(pass2_scope, DEEP_SCOPE_FIELDS, 'Deep'))
    status['deep_last_write_at_utc'] = _last_state_write(
        progressive_pass2.load_state(),
        pass2_work.get('semantic_generation_id'),
    )
    status['deep_legacy_full_reanalysis'] = pass2_scope.get('legacy_full_reanalysis') or {}

    translation = progressive_personalization._translation_processing_metrics()
    status.update(translation)

    quarantine = site_publication_resilience.load_quarantine()
    qsummary = site_publication_resilience.active_summary(quarantine)
    status.update({
        'site_quarantine_pending_count': qsummary['pending_count'],
        'site_quarantine_category_counts': qsummary['category_counts'],
        'site_quarantine_last_change_at_utc': qsummary['last_change_at_utc'],
        'site_status_generated_at_utc': generated_at,
    })
    return validate_stage_status(status)


def build_document(generated_at_utc=None):
    contract = load_json(CONTRACT_PATH)
    if contract.get('contract') != 'SITE-PUBLICATION-RESILIENCE-V1' or contract.get('status') != 'canonical':
        raise RuntimeError('site publication resilience contract is not canonical')

    generated_at = generated_at_utc or utc_now()
    processing_status = build_processing_status(generated_at)
    return {
        'schema_version': 1,
        'contract': 'SITE-CURRENT-STATUS-V1',
        'generated_at_utc': generated_at,
        'source_bindings': source_bindings(),
        'processing_status': processing_status,
        'publication_quarantine': {
            'pending_count': processing_status['site_quarantine_pending_count'],
            'category_counts': processing_status['site_quarantine_category_counts'],
            'last_change_at_utc': processing_status['site_quarantine_last_change_at_utc'],
        },
    }


def _require_scope_match(status, scope, fields, label):
    for field in fields:
        if field not in scope:
            raise RuntimeError(f'{label} source scope missing {field}')
        if status.get(field) != scope.get(field):
            raise RuntimeError(
                f'{label} statistics mismatch for {field}: '
                f'status={status.get(field)!r} source={scope.get(field)!r}'
            )


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
    validate_stage_status(status)

    pass1_scope = (load_json(progressive_pass1.WORK).get('scope') or {})
    pass2_scope = (load_json(progressive_pass2.WORK).get('scope') or {})
    _require_scope_match(status, pass1_scope, FAST_SCOPE_FIELDS, 'Fast')
    _require_scope_match(status, pass2_scope, DEEP_SCOPE_FIELDS, 'Deep')

    quarantine = doc.get('publication_quarantine')
    if not isinstance(quarantine, dict):
        raise RuntimeError('site current status quarantine summary missing')
    if int(quarantine.get('pending_count') or 0) != int(status.get('site_quarantine_pending_count') or 0):
        raise RuntimeError('site current status quarantine count mismatch')
    if (quarantine.get('category_counts') or {}) != (status.get('site_quarantine_category_counts') or {}):
        raise RuntimeError('site current status quarantine category mismatch')

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

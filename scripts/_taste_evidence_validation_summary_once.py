import json
from pathlib import Path

manifest = json.loads(Path('data/production/pre_ai/chatgpt_payload.json').read_text(encoding='utf-8'))
taste = json.loads(Path('data/production/pre_ai/taste_projection.json').read_text(encoding='utf-8'))
contract = manifest.get('contract') or {}

assert manifest.get('complete_family_partition') is True
assert contract.get('negative_work_also_resolves_fit_evidence_state_v5') is True
assert contract.get('new_evidence_work_code_or_scheduler_created') is False
assert contract.get('confirmed_negative_cannot_be_rescued_by_paid_commercial_signals') is True

bio = (taste.get('entries') or {}).get('App_7670')
bio_state = None
if bio:
    cached = bio.get('cached_taste') or {}
    bio_state = {
        'status': bio.get('status'),
        'reason_code': cached.get('reason_code'),
        'fit_evidence_state': bio.get('fit_evidence_state'),
        'fit_evidence_confidence': bio.get('fit_evidence_confidence'),
        'fit_evidence_source': bio.get('fit_evidence_source'),
        'fit_evidence_backfill_required': bio.get('fit_evidence_backfill_required'),
    }
    if bio.get('status') == 'cache_hit' and cached.get('reason_code') == 'exclude_direct_conflict':
        assert bio.get('fit_evidence_backfill_required') is True

summary = {
    'complete_family_partition': True,
    'ai_queue_count': manifest.get('ai_queue_count'),
    'evidence_backfill_queue_count': (manifest.get('negative_analysis') or {}).get('evidence_backfill_queue_count'),
    'deterministically_excluded_without_ai_count': manifest.get('deterministically_excluded_without_ai_count'),
    'bioshock_current_control': bio_state,
    'fit_semantics_sha256': Path('/tmp/taste_fit_semantics_digest.txt').read_text(encoding='utf-8').strip(),
}
Path('/tmp/taste_validation_summary.json').write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8'
)
print(json.dumps(summary, ensure_ascii=False, indent=2))

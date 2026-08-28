import json
import subprocess
from pathlib import Path

POLICY = Path('config/mailing_policy.json')
CONTRACT = Path('config/final_self_check_contract.json')
FEED = Path('data/cache/feed_ingest.validation.json')
TASTE_INDEX = Path('data/cache/taste_fit.index.json')
TASTE_VALIDATION = Path('data/cache/taste_fit.validation.json')
LEDGER = Path('data/cache/taste_fit.ledger_validation.json')
CHECKPOINT = Path('data/cache/taste_fit.checkpoint_validation.json')
CONTENT = Path('data/cache/content_eligibility.validation.json')
FAMILIES = Path('data/cache/offer_family.validation.json')
STORE = Path('data/cache/store_state.validation.json')
STEAMDB = Path('data/cache/steamdb_cache.validation.json')
DEAL = Path('data/cache/deal_quality.validation.json')
FREEBIES_CONTRACT = Path('config/freebies_upcoming_contract.json')
OUT = Path('data/cache/final_self_check.validation.json')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return subprocess.check_output(['git', 'rev-parse', f'HEAD:{path}'], text=True).strip()


policy = load(POLICY)
contract = load(CONTRACT)
feed = load(FEED)
taste_index = load(TASTE_INDEX)
taste_validation = load(TASTE_VALIDATION)
ledger = load(LEDGER)
checkpoint = load(CHECKPOINT)
content = load(CONTENT)
families = load(FAMILIES)
store = load(STORE)
steamdb = load(STEAMDB)
deal = load(DEAL)
freebies_contract = load(FREEBIES_CONTRACT)

if policy.get('status') != 'canonical':
    raise SystemExit('Policy is not canonical')
if contract.get('contract') != 'FINAL-SELF-CHECK-FAST-PATH':
    raise SystemExit('Unexpected final self-check contract')

policy_sha = sha('config/mailing_policy.json')
mailing_tree_sha = sha('data/production/mailing')
checks = {}


def check(name, value):
    checks[name] = bool(value)


# Ingest and exact current-feed identity.
check('policy_loaded_before_ingest_mechanically_compatible', feed.get('bindings', {}).get('policy_blob_sha') == policy_sha)
check('production_qa_passed', feed.get('status') == 'complete')
check('all_chosen_chunks_read_via_exact_producer_validation', feed.get('source_to_mailing_row_projection_lossless') is True and feed.get('all_source_rows_column_validated') is True)
check('rows_equal_item_count', feed.get('source_rows_verified') == feed.get('source_item_count') == feed.get('mailing_rows_verified') == feed.get('item_count'))
check('current_mailing_tree_matches_ingest_proof', feed.get('bindings', {}).get('mailing_tree_sha') == mailing_tree_sha)

# Taste cache / ledger / audit semantics.
profile_sha = taste_index.get('profile_blob_sha')
check('taste_cache_structurally_valid', taste_index.get('source_cache', {}).get('entry_count_matches_len_entries') is True and taste_index.get('source_cache', {}).get('required_entry_fields_complete') is True)
check('taste_model_is_v2', taste_index.get('taste_model_version') == 'taste-v2')
check('taste_validation_current_mail_tree', taste_validation.get('bindings', {}).get('mailing_tree_sha') == mailing_tree_sha)
check('taste_validation_complete', taste_validation.get('status') == 'complete' and taste_validation.get('complete_coverage') is True)
check('taste_hits_plus_misses_cover_feed', int(taste_validation.get('hit_count') or 0) + int(taste_validation.get('miss_or_stale_count') or 0) == int(taste_validation.get('feed_candidate_count') or -1))
check('taste_cache_consulted_before_semantic_eval', int(taste_validation.get('hit_count') or 0) == int(taste_validation.get('feed_candidate_count') or -1))
check('taste_cache_hits_not_reevaluated', int(taste_validation.get('miss_or_stale_count') or -1) == 0)
check('ledger_covers_all_candidates', ledger.get('status') == 'complete' and ledger.get('complete_ledger') is True and int(ledger.get('processed_count') or 0) == int(feed.get('item_count') or -1))
check('ledger_non_ambiguous', int(ledger.get('ambiguous_count') or -1) == 0 and int(ledger.get('invalid_reason_count') or -1) == 0 and int(ledger.get('invalid_fit_count') or -1) == 0)
check('taste_is_price_blind', policy['taste_deal_separation']['taste_verdict_is_price_blind'] is True and bool(policy['taste_cache']['fingerprint_excludes']))
check('generic_or_deal_fields_not_taste_evidence', policy['personal_filter']['structured_taste_evaluation']['reviews_discount_price_never_break_tie'] is True and policy['taste_deal_separation']['deal_quality_can_never_raise_taste_fit'] is True)
check('targeted_audit_same_threshold', policy['false_negative_audit']['audit_uses_same_evidence_contract_and_same_threshold'] is True)
check('no_candidate_name_whitelists', policy['false_negative_audit']['no_candidate_name_whitelists'] is True and policy['false_negative_audit']['no_control_game_names_in_policy'] is True)
check('recovery_and_checkpoint_valid', checkpoint.get('status') == 'complete' and checkpoint.get('checkpoint_complete') is True)
check('changed_taste_chunks_checkpointed_or_none_changed', int(checkpoint.get('cache_changes_required') or 0) == 0 or int(checkpoint.get('github_writes_performed_by_checkpoint') or 0) > 0)
check('recovery_absent_or_verified', checkpoint.get('checks', {}).get('recovery_artifact_absent') is True)

# Content and family resolution.
check('content_eligibility_applied', content.get('status') == 'complete' and content.get('complete_coverage') is True and int(content.get('unresolved_count') or -1) == 0)
check('orphan_dlc_not_recommended', int(content.get('invalid_exclusion_code_count') or -1) == 0 and int(content.get('classified_count') or 0) == int(content.get('input_taste_include_count') or -1))
check('one_primary_row_per_family', families.get('status') == 'complete' and families.get('complete_coverage') is True and int(families.get('primary_count') or -1) == int(families.get('family_count') or -2) and int(families.get('primary_duplicate_count') or -1) == 0)
check('best_purchase_variant_resolution_complete', int(families.get('unresolved_count') or -1) == 0 and int(families.get('missing_assignment_count') or -1) == 0)

# Store state after final taste.
check('store_state_complete', store.get('status') == 'complete' and int(store.get('missing_count') or -1) == 0)
check('current_snapshot_or_conditional_store_used', int(store.get('current_source_conflict_count') or -1) == 0 and int(store.get('live_store_calls_required') or -1) == int(store.get('live_store_calls_performed') or -2))
check('taste_final_before_external_checks', store.get('bindings', {}).get('offer_family_blob_sha') == sha('data/cache/offer_family.validation.json'))

# SteamDB cache before lookups; current run has no true misses.
check('steamdb_cache_complete', steamdb.get('status') == 'complete' and steamdb.get('complete_coverage') is True)
check('steamdb_actual_len_entries_used', int(steamdb.get('actual_entry_count') or -1) >= 0 and int(steamdb.get('metadata_entry_count') or -2) == int(steamdb.get('actual_entry_count') or -1))
check('steamdb_cache_before_history_lookup', int(steamdb.get('true_lookup_miss_count') or -1) == 0 and int(steamdb.get('steamdb_lookup_count') or -1) == 0)
check('negative_cache_respected', int(steamdb.get('negative_cache_hit_count') or -1) >= 0 and int(steamdb.get('true_lookup_miss_count') or -1) == 0)
check('steamdb_not_discovery', policy['pricing']['steamdb_usage'] == 'history_only_after_personal_selection')

# Deal quality and deterministic order.
check('deal_quality_complete', deal.get('status') == 'complete' and deal.get('complete_coverage') is True and int(deal.get('classified_count') or 0) == int(deal.get('input_primary_count') or -1))
check('historical_zero_not_paid_delta', all(r.get('delta_vs_paid_historical_minimum') is None for r in (deal.get('sorted_recommendations') or []) + (deal.get('price_exclusions') or []) if r.get('history_quality') == 'previously_free'))
check('no_artificial_top_n', policy['delivery'].get('fixed_top_n') is None)
check('deterministic_sort_required', policy['sorting']['required'] is True and policy['sorting']['do_not_preserve_feed_or_processing_order'] is True)
check('all_visible_money_contract_is_rub', all('kzt' not in field.lower() for field in policy.get('paid_output_fields') or []) and any('rub' in field.lower() for field in policy.get('paid_output_fields') or []))

# Stable policy/output assertions.
check('completed_not_auto_excluded', policy['delivery']['completed_games_auto_excluded'] is False)
check('still_active_deals_repeat_daily', policy['delivery']['repeat_still_active_relevant_deals_each_day'] is True)
check('wishlist_not_taste_or_ownership', policy['taste_profile']['wishlist_is_discovery_source'] is False and policy['taste_profile']['wishlist_is_taste_proof'] is False and policy['taste_profile']['wishlist_is_ownership_proof'] is False)
check('lookup_registry_required', policy['external_cache']['lookup_registry']['required'] is True and policy['external_cache']['lookup_registry']['never_repeat_same_key_in_run'] is True)
check('freebies_after_ingest_policy', policy['freebies']['only_after_successful_main_ingest'] is True)
check('upcoming_after_ingest_policy', policy['upcoming']['only_after_successful_main_ingest'] is True and int(policy['upcoming']['max_items']) == 1)
check('stage19_contract_current', freebies_contract.get('contract') == 'FREEBIES-UPCOMING-RENDER-V1' and freebies_contract.get('render', {}).get('publish_forbidden_in_diagnostic_mode') is True)
check('silent_exclusions_policy', policy['output_visibility']['silent_exclusions'] is True and policy['output_visibility']['show_only_included_recommendations'] is True)

failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('Mechanical final self-check failed: ' + ', '.join(failed))

out = {
    'schema_version': 1,
    'purpose': 'compact_mechanical_final_self_check_proof',
    'status': 'complete',
    'contract_version': contract['version'],
    'bindings': {
        'policy_blob_sha': policy_sha,
        'contract_blob_sha': sha('config/final_self_check_contract.json'),
        'mailing_tree_sha': mailing_tree_sha,
        'feed_ingest_blob_sha': sha('data/cache/feed_ingest.validation.json'),
        'taste_index_blob_sha': sha('data/cache/taste_fit.index.json'),
        'taste_validation_blob_sha': sha('data/cache/taste_fit.validation.json'),
        'ledger_blob_sha': sha('data/cache/taste_fit.ledger_validation.json'),
        'checkpoint_blob_sha': sha('data/cache/taste_fit.checkpoint_validation.json'),
        'content_blob_sha': sha('data/cache/content_eligibility.validation.json'),
        'family_blob_sha': sha('data/cache/offer_family.validation.json'),
        'store_blob_sha': sha('data/cache/store_state.validation.json'),
        'steamdb_blob_sha': sha('data/cache/steamdb_cache.validation.json'),
        'deal_quality_blob_sha': sha('data/cache/deal_quality.validation.json'),
        'freebies_upcoming_contract_blob_sha': sha('config/freebies_upcoming_contract.json'),
        'mechanical_profile_blob_sha': profile_sha,
    },
    'mechanical_assertion_count': len(checks),
    'mechanical_assertions_failed': 0,
    'mechanical_assertions': checks,
    'runtime_only_assertions_required': contract['runtime_only_assertions'],
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({
    'status': out['status'],
    'mechanical_assertion_count': out['mechanical_assertion_count'],
    'mechanical_assertions_failed': 0,
    'mechanical_profile_blob_sha': profile_sha,
}, ensure_ascii=False, indent=2))

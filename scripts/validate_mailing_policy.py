import json
from pathlib import Path

from taste_cache_common import taste_semantics_digest

POLICY = Path('config/mailing_policy.json')
CACHE_ENTRY_CONTRACT = Path('config/taste_cache_entry_contract.json')
TASTE_PROJECTION_SCRIPT = Path('scripts/build_pre_ai_taste_projection.py')
EXPECTED_TASTE_SEMANTICS = '0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828'


def main():
    p = json.loads(POLICY.read_text(encoding='utf-8'))
    cache_contract = json.loads(CACHE_ENTRY_CONTRACT.read_text(encoding='utf-8'))
    projection_source = TASTE_PROJECTION_SCRIPT.read_text(encoding='utf-8')
    sep = p['taste_deal_separation']
    deal = p['deal_selection']
    pricing = p['pricing']
    verification = p['verification']
    sorting = p['sorting']
    pf = p['personal_filter']
    st = pf['structured_taste_evaluation']
    tc = p['taste_cache']
    cp = tc['checkpoint_strategy']
    ra = tc['recovery_artifact']
    sh = p['external_cache']['steamdb_history']
    reg = p['external_cache']['lookup_registry']
    rtc = p['review_threshold_calibration']

    expected_review_thresholds = {
        'affordable_quality': 75,
        'genre_fit': 75,
        'big_discount': 75,
        'popular_quality': 82,
        'very_high_rating': 90,
        'cheap_quality': 80,
        'niche_fit': 78,
        'recent_quality': 78,
        'mainstream_quality': 80,
        'strong_fit': 78,
        'strong_niche_fit': 78,
        'exceptional_discount': 75,
        'recent_fit': 78,
        'high_confidence_adjacent': 88,
        'substantive_content': 78,
    }

    cache_hit_requirements = set(cache_contract.get('cache_hit_requires_same_entry') or [])
    mixed_generation = cache_contract.get('mixed_generation_rules') or {}

    checks = {
        'contract': p.get('contract') == 'GAME-DEALS-MAILING',
        'canonical': p.get('status') == 'canonical',
        'version': p.get('version') == '1.21',
        'policy_first': p['policy_loading']['load_before_any_ingest'] is True,
        'fail_closed': p['policy_loading']['fail_closed_if_unavailable'] is True,
        'full_snapshot': p['delivery']['mode'] == 'full_daily_snapshot',
        'not_delta': p['delivery']['delta_only'] is False,
        'no_topn': p['delivery']['fixed_top_n'] is None,
        'repeat_active': p['delivery']['repeat_still_active_relevant_deals_each_day'] is True,
        'completed_not_excluded': p['delivery']['completed_games_auto_excluded'] is False,
        'wishlist_not_discovery': p['taste_profile']['wishlist_is_discovery_source'] is False,
        'wishlist_not_taste': p['taste_profile']['wishlist_is_taste_proof'] is False,
        'wishlist_not_ownership': p['taste_profile']['wishlist_is_ownership_proof'] is False,
        'production_primary': p['paid_discovery']['production_feed_is_primary_discovery_source'] is True,
        'steamdb_not_discovery': p['paid_discovery']['steamdb_for_discovery'] is False,
        'all_chunks': p['paid_discovery']['read_all_chunks'] is True,
        'qa_fail_closed': p['ingest_qa']['fail_closed'] is True,
        'max_age_18': p['ingest_qa']['maximum_snapshot_age_hours'] == 18,
        'review_threshold_profile': rtc['profile'] == 'personal-calibrated-v1',
        'review_thresholds': rtc['thresholds'] == expected_review_thresholds,
        'review_threshold_qa_binding': p['ingest_qa']['required_review_threshold_profile'] == rtc['profile'] and p['ingest_qa']['require_review_threshold_map_match'] is True,
        'price_blind': sep['taste_verdict_is_price_blind'] is True,
        'deal_never_raises_taste': sep['deal_quality_can_never_raise_taste_fit'] is True,
        'recall_not_evidence': sep['recall_flags_can_trigger_audit_but_are_not_taste_evidence'] is True,
        'core_not_evidence': sep['core_fit_count_is_recall_context_not_positive_taste_evidence'] is True,
        'taste_semantics_stable': taste_semantics_digest(p) == EXPECTED_TASTE_SEMANTICS,
        'taste_factor_semantics_v3': (p.get('taste_factor_semantics') or {}).get('contract') == 'TASTE-SEMANTIC-RESULT-V3',
        'taste_factor_ids_bound': (p.get('taste_factor_semantics') or {}).get('normalized_factor_ids') == list(__import__('taste_cache_common').TASTE_FACTOR_IDS),
        'taste_v3': st['taste_model_version'] == 'taste-v3',
        'audit_same_threshold': p['false_negative_audit']['audit_uses_same_evidence_contract_and_same_threshold'] is True,
        'no_whitelist': p['false_negative_audit']['no_candidate_name_whitelists'] is True,
        'deal_policy_canonical': deal['status'] == 'canonical',
        'taste_primary': deal['taste_is_primary_eligibility_filter'] is True,
        'discount_cannot_raise_taste': deal['discount_can_never_raise_taste_fit'] is True,
        'weak_taste_not_promoted': deal['below_moderate_taste_cannot_be_promoted_by_commercial_bridge'] is True,
        'weak_taste_exception_requires_v5_bridge': deal['below_moderate_commercial_eligibility_exception_requires_explicit_v5_bridge'] is True,
        'symbolic_discount_5': deal['symbolic_discount_max_percent_inclusive'] == 5,
        'target_500_deal': deal['normal_target_rub'] == 500,
        'strong_standard_650_deal': deal['strong_standard_overage_ceiling_rub'] == 650,
        'absolute_budget_750_deal': deal['strong_absolute_ceiling_rub'] == 750,
        'moderate_absolute_550_deal': deal['moderate_absolute_ceiling_rub'] == 550,
        'exceptional_discount_75_deal': deal['exceptional_discount_min_percent_for_high_overage'] == 75,
        'high_overage_strong_only_deal': deal['high_overage_requires_strong_taste'] is True,
        'budget_overrides_discount_deal': deal['price_above_750_excluded_regardless_of_taste_or_discount'] is True,
        'commercial_rules_outside_taste_semantics': deal['commercial_rules_are_excluded_from_taste_cache_semantics'] is True,
        'target_500': pricing['target_rub'] == 500,
        'target_soft': pricing['target_is_hard_cap'] is False,
        'symbolic_discount_5_pricing': pricing['symbolic_discount_max_percent_inclusive'] == 5,
        'absolute_budget_750': pricing['absolute_max_rub'] == 750,
        'strong_standard_650': pricing['strong_fit_standard_overage_ceiling_rub'] == 650,
        'moderate_absolute_550': pricing['moderate_fit_absolute_ceiling_rub'] == 550,
        'exceptional_discount_75': pricing['exceptional_discount_min_percent_for_high_overage'] == 75,
        'budget_overrides_discount': pricing['price_above_absolute_max_is_excluded_regardless_of_discount'] is True,
        'daily_commercial_refresh': verification['commercial_refresh_frequency'] == 'once_per_day_nightly',
        'no_morning_network_refresh': verification['no_network_refresh_for_morning_delivery'] is True,
        'local_expiry_guard': verification['known_sale_end_may_be_applied_locally_without_network'] is True,
        'known_end_runtime_guard': verification['known_sale_end_at_or_before_consumer_time_means_inactive'] is True,
        'no_offer_reuse_past_end': verification['current_offer_state_must_not_be_reused_past_known_sale_end'] is True,
        'taste_weight': sorting['conceptual_weight_taste'] == 0.6,
        'deal_weight': sorting['conceptual_weight_deal'] == 0.4,
        'budget_before_ranking': sorting['absolute_budget_ceiling_applied_before_ranking'] is True,
        'qualitative_ranking_method': sorting['ranking_method'] == 'explicit_qualitative_60_40_matrix_no_hidden_numeric_score',
        'qualitative_bucket_count': len(sorting['qualitative_priority_buckets']) == 6,
        'strong_standard_weak_deal_waits': deal['weak_non_symbolic_deal_within_standard_fit_band_remains_visible_as_wait_or_low_priority'] is True,
        'presentation_deferred': p['presentation_strategy']['status'] == 'deferred_until_data_optimization_complete',
        'wishlist_ranking_bonus_final_sort_only': p['final_ranking_context']['wishlist']['ranking_bonus_applies_only_during_final_sorting'] is True,
        'wishlist_bounded_eligibility_context': p['final_ranking_context']['wishlist']['may_be_used_as_bounded_commercial_eligibility_context'] is True,
        'wishlist_bridge_never_changes_taste': p['final_ranking_context']['wishlist']['bounded_eligibility_context_never_changes_taste_fit'] is True,
        'wishlist_not_inclusion': p['final_ranking_context']['wishlist']['never_causes_inclusion_by_itself'] is True,
        'wishlist_not_taste': p['final_ranking_context']['wishlist']['never_changes_taste_fit'] is True,
        'wishlist_budget_bounded': p['final_ranking_context']['wishlist']['cannot_override_budget_ceiling'] is True,
        'wishlist_symbolic_discount_bounded': p['final_ranking_context']['wishlist']['cannot_override_symbolic_discount_exclusion'] is True,
        'wishlist_no_invented_numeric_bonus': p['final_ranking_context']['wishlist']['numeric_bonus_must_not_be_invented_without_user_agreement'] is True,
        'cache_v3': tc['taste_model_version'] == 'taste-v3',
        'taste_cache_has_no_commercial_state': tc['commercial_state_not_stored_in_taste_cache'] is True,
        'sale_expiry_keeps_taste_verdict': tc['sale_expiry_does_not_invalidate_taste_verdict'] is True,
        'cache_contract_v5': cache_contract.get('contract') == 'TASTE-CACHE-ENTRY-BINDING-V5',
        'cache_requires_exact_profile_blob': 'exact_profile_blob_sha' in cache_hit_requirements,
        'old_profile_entries_not_hits': mixed_generation.get('old_generation_entries_are_preserved_but_are_not_cache_hits_for_a_new_binding') is True,
        'never_rebind_old_entry_without_ai': mixed_generation.get('never_upgrade_an_old_entry_fit_binding_or_add_factors_without_a_new_ai_verdict') is True,
        'projection_compares_exact_profile_blob': "profile_ok = cached['profile_blob_sha'] == profile['blob_sha']" in projection_source,
        'projection_requeues_profile_change': "canonical_profile_blob_changed_for_entry" in projection_source,
        'incremental_checkpoint': cp['mode'] == 'incremental_by_chosen_feed_chunk',
        'checkpoint_each_chunk': cp['checkpoint_after_each_chunk_final_post_audit_verdicts'] is True,
        'checkpoint_before_next_chunk': cp['checkpoint_before_advancing_to_next_chunk_when_cache_changed'] is True,
        'checkpoint_before_external': cp['checkpoint_before_content_family_store_steamdb_deal_quality_sorting'] is True,
        'checkpoint_stop_safe': cp['if_execution_budget_is_low_stop_after_successful_checkpoint_and_resume_next_run'] is True,
        'recovery_enabled': ra['enabled'] is True,
        'recovery_not_evidence': ra['artifact_is_not_user_evidence'] is True,
        'dlc_gate': p['content_eligibility']['dlc_is_not_independent_recommendation_by_default'] is True,
        'family_required': p['offer_family_resolution']['required'] is True,
        'one_row_family': p['offer_family_resolution']['one_primary_output_row_per_purchase_family'] is True,
        'zero_free': pricing['historical_zero']['zero_means_previously_free_not_paid_minimum'] is True,
        'steamdb_v2': sh['writer_schema_version'] == 2,
        'steamdb_legacy': sh['accept_legacy_schema_version_1'] is True,
        'negative_ttl': sh['negative_cache']['ttl_days'] == 14,
        'actual_count': sh['actual_runtime_entry_count_is_len_entries'] is True,
        'lookup_registry': reg['required'] is True and reg['never_repeat_same_key_in_run'] is True,
        'sort_required': sorting['required'] is True,
        'silent_exclusions': p['output_visibility']['silent_exclusions'] is True,
        'one_upcoming': p['upcoming']['max_items'] == 1,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit('Mailing policy invariant failure: ' + ', '.join(failed))
    print(f'OK: {len(checks)} mailing invariants validated; taste semantics={EXPECTED_TASTE_SEMANTICS}')


if __name__ == '__main__':
    main()

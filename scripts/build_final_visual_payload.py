import json
import os
from pathlib import Path

import apply_fixed_package_purchase_options as package_options
import build_daily_visual_payload as base_builder
import card_explanation_policy
import duration_enrichment
import giveaway_visual_handoff
import priority_ranking
import refine_visual_ranking as refiner
from semantic_runtime_completion import apply_visual_semantic_status

ROOT = Path('.')
OUT = ROOT / 'data/production/visual/current.json'
SEMANTIC_PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'
DURATION_CONTRACT = ROOT / 'config/duration_enrichment_contract.json'
DURATION_CACHE = ROOT / 'data/cache/duration_estimates.json'


def normalize_media_url(value):
    if isinstance(value, str) and value.startswith('https://shared.fastly.steamstatic.com/'):
        return 'https://shared.akamai.steamstatic.com/' + value[len('https://shared.fastly.steamstatic.com/'):]
    return value


def load_duration_entries():
    if not DURATION_CONTRACT.exists():
        return {}
    contract = duration_enrichment.load_json(DURATION_CONTRACT)
    cache = duration_enrichment.load_cache(DURATION_CACHE, contract)
    entries = cache.get('entries') or {}
    return entries if isinstance(entries, dict) else {}


def apply_duration_resolution(game, projection, duration_entries, preserve_existing_fallback=False):
    structured = duration_enrichment.structured_duration_for_game(game, duration_entries)
    if structured:
        resolved = structured
    elif preserve_existing_fallback and game.get('duration_estimate_source') != 'igdb_game_time_to_beats_normally':
        return False
    else:
        resolved = duration_enrichment.resolve_duration_for_game(
            game,
            projection,
            duration_entries,
            refiner.extract_duration_hours,
        )

    hours = resolved.get('hours')
    band, penalty = refiner.duration_band(hours)
    fields = {
        'estimated_duration_hours': hours,
        'duration_estimate_source': resolved.get('source'),
        'duration_estimate_provenance': resolved.get('provenance'),
        'duration_preference_band': band,
        'duration_tiebreak_penalty': penalty,
    }
    changed = False
    for key, value in fields.items():
        if game.get(key) != value:
            game[key] = value
            changed = True
    return changed


def duration_source_distribution(items):
    counts = {'structured_igdb': 0, 'legacy_text': 0, 'unknown': 0}
    for game in items or []:
        source = game.get('duration_estimate_source')
        if source == 'igdb_game_time_to_beats_normally':
            counts['structured_igdb'] += 1
        elif source == 'legacy_text_explicit_duration_phrase':
            counts['legacy_text'] += 1
        else:
            counts['unknown'] += 1
    return counts


def _set_if_changed(game, key, value):
    if game.get(key) == value:
        return False
    game[key] = value
    return True


def explanation_risk_candidates(taste_entry, projection, practical):
    risks = refiner.personal_taste_risks(taste_entry)
    for code, row in refiner.structural_risks(projection, practical).items():
        refiner.add_risk(
            risks,
            code,
            row['score'],
            row['text'],
            row.get('source') or 'derived',
        )
    return risks


def apply_card_explanation_policy(game, taste_entry, projection, update_scoring=True):
    """Apply the one canonical player-facing explanation policy.

    Ranking/scoring still receives the full existing risk candidate set. Only the
    player-facing negative block is fail-closed to grounded sources.
    """
    changed = False

    reasons, why_fit_provenance = card_explanation_policy.positive_reasons(
        taste_entry.get('positive_evidence') or []
    )
    changed |= _set_if_changed(game, 'why_fit', reasons)
    changed |= _set_if_changed(
        game,
        'why_fit_status',
        {
            'has_described_fit': bool(reasons),
            'grounding': 'grounded' if reasons else 'insufficient_evidence',
        },
    )
    changed |= _set_if_changed(game, 'why_fit_provenance', why_fit_provenance)

    risks = explanation_risk_candidates(taste_entry, projection, game.get('practical') or {})
    visible = card_explanation_policy.visible_risk_payload(risks)
    changed |= _set_if_changed(game, 'risks', visible['risks'])
    changed |= _set_if_changed(game, 'risk_codes', visible['risk_codes'])
    changed |= _set_if_changed(game, 'risk_status', visible['risk_status'])
    changed |= _set_if_changed(game, 'risk_provenance', visible['risk_provenance'])

    if update_scoring:
        # Preserve the existing ranking semantics: scoring sees all candidates,
        # including derived heuristics, while visibility requires grounding.
        _, _, risk_penalty, risk_level = refiner.risk_summary(risks)
        changed |= _set_if_changed(game, 'risk_penalty', risk_penalty)
        changed |= _set_if_changed(game, 'risk_level', risk_level)

    return changed, risks


def current_explanation_context():
    context_by_family = {
        str(row.get('family_id')): row
        for row in base_builder.load_jsonl(base_builder.PURCHASE_CONTEXT)
        if row.get('family_id')
    }
    taste_entries = refiner.effective_taste_entries()
    projections = (
        (refiner.load_json(refiner.TASTE_PROJECTION).get('entries') or {})
        if refiner.TASTE_PROJECTION.exists()
        else {}
    )
    return context_by_family, taste_entries, projections


def explanation_inputs_for_game(game, context_by_family, taste_entries, projections):
    context = context_by_family.get(str(game.get('id') or '')) or {}
    taste_key = context.get('taste_subject_key')
    taste_entry = taste_entries.get(taste_key) if taste_key else {}
    projection = projections.get(taste_key) if taste_key else {}
    return (
        taste_entry if isinstance(taste_entry, dict) else {},
        projection if isinstance(projection, dict) else {},
    )


def apply_deterministic_purchase_refresh(ready):
    """Reapply producer-owned purchase options and the one canonical ranking policy.

    This path is intentionally price/Taste independent: it operates on an already
    accepted visual snapshot and is safe while semantic Taste work is still queued.
    """
    package_stats = package_options.apply_current_artifacts_to_visual(ready)
    ranked, final_priority_order = priority_ranking.apply_final_priority_order(
        ready.get('items') or []
    )
    ready['items'] = ranked
    ready['item_count'] = len(ranked)

    contract = ready.setdefault('production_contract', {})
    contract.update({
        'ranking_helper_blob_sha': base_builder.git_sha('scripts/priority_ranking.py'),
        'ranking_policy_blob_sha': base_builder.git_sha('config/final_ranking_policy.json'),
        'fixed_package_helper_blob_sha': base_builder.git_sha('scripts/apply_fixed_package_purchase_options.py'),
        'fixed_package_options_blob_sha': package_options.git_blob_sha(package_options.PACKAGE_OPTIONS),
        'purchase_equivalence_blob_sha': package_options.git_blob_sha(package_options.PURCHASE_EQUIVALENCE),
        'duration_enrichment_helper_blob_sha': base_builder.git_sha('scripts/duration_enrichment.py'),
        'duration_enrichment_contract_blob_sha': base_builder.git_sha('config/duration_enrichment_contract.json'),
        'duration_cache_blob_sha': base_builder.git_sha('data/cache/duration_estimates.json'),
        'card_explanation_policy_blob_sha': base_builder.git_sha('scripts/card_explanation_policy.py'),
        'duration_source_precedence': [
            'validated_structured_igdb_normally',
            'legacy_text_explicit_duration_phrase',
            'unknown',
        ],
        'ranking_stage': 'single_canonical_sort_after_deterministic_purchase_option_refresh',
        'priority_factors': final_priority_order,
        'priority_ranking_contract': 'FINAL-PRIORITY-RANKING-V2',
        'card_explanation_rule': 'positive requires specific Taste evidence; visible negative requires grounded provenance; scoring/ranking semantics unchanged',
        'fixed_package_purchase_option_rule': (
            'fixed Sub only; >=2 visible base-game families by exact appid or explicit verified '
            'purchase equivalence; relevant package information may be displayed without strict '
            'savings; ranking boost remains fail-closed and requires the commercial package route '
            'to satisfy ranking policy; personalized bundles excluded'
        ),
        'fixed_package_qualifying_count': package_stats.get('qualifying_package_count'),
        'fixed_package_strict_savings_count': package_stats.get('strict_savings_package_count'),
        'fixed_package_verified_equivalence_count': package_stats.get('verified_equivalence_package_count'),
        'fixed_package_touched_game_count': package_stats.get('visible_game_count_with_better_package'),
    })
    return package_stats, final_priority_order


def refresh_existing_giveaways_only():
    """Update only the giveaway sibling on an already accepted visual payload.

    This bounded path exists so an auxiliary giveaway refresh never has to rewrite
    paid cards while an independent paid-card prerequisite is blocked. It preserves
    the canonical final visual producer and explicitly asserts that paid `items`
    remain byte-equivalent after JSON normalization.
    """
    if not OUT.exists():
        raise RuntimeError(f'missing canonical visual payload: {OUT}')

    before = OUT.read_text(encoding='utf-8')
    ready = json.loads(before)
    paid_before = json.dumps(ready.get('items') or [], ensure_ascii=False, separators=(',', ':'))

    giveaways = giveaway_visual_handoff.derive_from_path()
    ready['giveaways'] = giveaways
    contract = ready.setdefault('production_contract', {})
    contract['final_visual_producer_blob_sha'] = base_builder.git_sha('scripts/build_final_visual_payload.py')
    contract['giveaway_visual_handoff_blob_sha'] = base_builder.git_sha('scripts/giveaway_visual_handoff.py')
    contract['source_giveaway_snapshot_blob_sha'] = base_builder.git_sha('data/production/giveaways/v1/current.json')
    contract['giveaway_visual_schema_version'] = 1

    paid_after = json.dumps(ready.get('items') or [], ensure_ascii=False, separators=(',', ':'))
    if paid_after != paid_before:
        raise RuntimeError('giveaway-only refresh mutated paid items')

    after = json.dumps(ready, ensure_ascii=False, separators=(',', ':'))
    changed = after != before
    if changed:
        OUT.write_text(after, encoding='utf-8')

    return changed, giveaways.get('state'), giveaways.get('accepted_offer_count_at_build')


def refresh_existing_media():
    if not OUT.exists():
        return False, 0, 0, {}

    before = OUT.read_text(encoding='utf-8')
    ready = json.loads(before)
    semantic_payload = json.loads(SEMANTIC_PAYLOAD.read_text(encoding='utf-8')) if SEMANTIC_PAYLOAD.exists() else {}
    apply_visual_semantic_status(ready, semantic_payload)
    items = ready.get('items') or []
    duration_entries = load_duration_entries()
    context_by_family, taste_entries, projections = current_explanation_context()
    translation_cache = base_builder.visual_builder.load_translation_cache(
        base_builder.visual_builder.TRANSLATION_CACHE
    )
    wanted_appids = set()
    for game in items:
        for appid in game.get('base_appids') or []:
            appid = str(appid)
            if appid.isdigit():
                wanted_appids.add(appid)

    media = base_builder.visual_builder.storebrowse_media(wanted_appids) if wanted_appids else {}
    content_metadata_by_appid = base_builder.visual_builder.load_content_metadata_by_appid()
    touched = 0
    duration_touched = 0
    explanation_touched = 0
    for game in items:
        screenshots = []
        header = None
        for appid in game.get('base_appids') or []:
            m = media.get(str(appid)) or {}
            header = header or normalize_media_url(m.get('header_image'))
            for url in m.get('screenshots') or []:
                url = normalize_media_url(url)
                if url not in screenshots:
                    screenshots.append(url)

        changed = False
        if screenshots and screenshots != (game.get('screenshots') or []):
            game['screenshots'] = screenshots
            changed = True
        if header and header != game.get('header_image'):
            game['header_image'] = header
            changed = True
        description = base_builder.visual_builder.resolve_description_for_appids(
            game.get('base_appids') or [],
            media,
            content_metadata_by_appid,
            translation_cache,
        )
        description_fields = {
            'summary': description.get('summary'),
            'description_status': description.get('description_status'),
            'description_source_locale': description.get('description_source_locale'),
            'description_source_quality': description.get('description_source_quality'),
            'description_source_appid': description.get('description_source_appid'),
            'description_source_path': description.get('description_source_path'),
            'description_source_text': description.get('description_source_text'),
        }
        for key, value in description_fields.items():
            if game.get(key) != value:
                game[key] = value
                changed = True

        if apply_duration_resolution(game, {}, duration_entries, preserve_existing_fallback=True):
            duration_touched += 1
            changed = True

        taste_entry, projection = explanation_inputs_for_game(
            game,
            context_by_family,
            taste_entries,
            projections,
        )
        explanation_changed, _ = apply_card_explanation_policy(
            game,
            taste_entry,
            projection,
            update_scoring=True,
        )
        if explanation_changed:
            explanation_touched += 1
            changed = True

        if changed:
            touched += 1

    # Even when there is no new semantic Taste result, package/equivalence/price/duration
    # logic is deterministic and must be allowed to refresh the current visual snapshot.
    package_stats, _ = apply_deterministic_purchase_refresh(ready)
    items = ready.get('items') or []

    with_screenshots = sum(bool(game.get('screenshots')) for game in items)
    with_any_image = sum(bool(game.get('screenshots') or game.get('header_image')) for game in items)
    ready['media_coverage'] = {
        'visible_item_count': len(items),
        'with_screenshots': with_screenshots,
        'with_any_image': with_any_image,
        'without_any_image': len(items) - with_any_image,
        'coverage_percent': round((with_any_image / len(items)) * 100, 1) if items else 100.0,
    }
    ready['giveaways'] = giveaway_visual_handoff.derive_from_path()
    contract = ready.setdefault('production_contract', {})
    contract['visual_builder_blob_sha'] = base_builder.git_sha('scripts/build_visual_feed_v2.py')
    contract['final_visual_producer_blob_sha'] = base_builder.git_sha('scripts/build_final_visual_payload.py')
    contract['card_explanation_policy_blob_sha'] = base_builder.git_sha('scripts/card_explanation_policy.py')
    contract['card_explanation_rule'] = 'positive requires specific Taste evidence; visible negative requires grounded provenance; scoring/ranking semantics unchanged'
    contract['duration_source_distribution'] = duration_source_distribution(items)
    contract['duration_structured_refresh_touched_count'] = duration_touched
    contract['card_explanation_refresh_touched_count'] = explanation_touched
    contract['giveaway_visual_handoff_blob_sha'] = base_builder.git_sha('scripts/giveaway_visual_handoff.py')
    contract['source_giveaway_snapshot_blob_sha'] = base_builder.git_sha('data/production/giveaways/v1/current.json')
    contract['giveaway_visual_schema_version'] = 1

    after = json.dumps(ready, ensure_ascii=False, separators=(',', ':'))
    if after == before:
        return False, touched, len(media), package_stats

    OUT.write_text(after, encoding='utf-8')
    return True, touched, len(media), package_stats


def main():
    if os.environ.get('GIVEAWAY_VISUAL_REFRESH_ONLY') == '1':
        changed, state, offer_count = refresh_existing_giveaways_only()
        print(
            f'VISUAL_GIVEAWAY_REFRESH=BUILT changed={str(changed).lower()} '
            f'state={state} offers={offer_count}'
        )
        return

    source_key, payload = base_builder.current_production_readiness()
    if source_key is None:
        if os.environ.get('FORCE_VISUAL_BUILD') == '1':
            changed, refreshed, media_keys, package_stats = refresh_existing_media()
            if changed:
                print(
                    f'VISUAL_FINAL_BUILD=BUILT mode=deterministic_refresh '
                    f'items_refreshed={refreshed} media_keys={media_keys} '
                    f'package_qualifying={package_stats.get("qualifying_package_count")} '
                    f'package_strict={package_stats.get("strict_savings_package_count")} '
                    f'package_equivalence={package_stats.get("verified_equivalence_package_count")} '
                    f'package_touched={package_stats.get("visible_game_count_with_better_package")} '
                    f'ai_queue={payload.get("ai_queue_count")}'
                )
                return
        print(
            f'VISUAL_FINAL_BUILD=WAIT source={payload.get("source_mailing_updated_at_utc")} '
            f'ai_queue={payload.get("ai_queue_count")}'
        )
        return

    context_by_family = {
        str(row.get('family_id')): row
        for row in base_builder.load_jsonl(base_builder.PURCHASE_CONTEXT)
        if row.get('family_id')
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    base_builder.visual_builder.OUT = OUT
    base_builder.visual_builder.main()

    ready = base_builder.load_json(OUT)
    apply_visual_semantic_status(ready, payload)
    ready['items'] = base_builder.achievement_quality.enrich_visual_items(ready.get('items') or [])
    ready = base_builder.enrich_history_and_remove_expired(ready, context_by_family, payload)
    achievement_distribution = base_builder.achievement_quality_distribution(ready.get('items') or [])

    taste_entries = refiner.effective_taste_entries()
    projections = (
        (refiner.load_json(refiner.TASTE_PROJECTION).get('entries') or {})
        if refiner.TASTE_PROJECTION.exists()
        else {}
    )
    duration_entries = load_duration_entries()
    profile, profile_error = refiner.fetch_bound_profile(payload)
    direct_index = refiner.direct_profile_index(profile)

    fit_changes = 0
    removed = 0
    windows_labels_neutralized = 0
    refined = []

    for game in ready.get('items') or []:
        family_id = str(game.get('id') or '')
        context = context_by_family.get(family_id) or {}
        taste_key = context.get('taste_subject_key')
        taste_entry = taste_entries.get(taste_key) if taste_key else {}
        projection = projections.get(taste_key) if taste_key else {}
        taste_entry = taste_entry if isinstance(taste_entry, dict) else {}
        projection = projection if isinstance(projection, dict) else {}

        practical = game.setdefault('practical', {})
        old_windows = practical.get('windows_status')
        refiner.normalize_windows(practical)
        if old_windows in {'legacy', 'older_but_plausible'}:
            windows_labels_neutralized += 1

        _, risks = apply_card_explanation_policy(
            game,
            taste_entry,
            projection,
            update_scoring=True,
        )

        evidence = refiner.direct_evidence(game, direct_index)
        game['direct_user_evidence'] = evidence or {'level': 'none'}
        old_fit = game.get('fit')
        refiner.apply_fit_adjustment(game, evidence, risks, taste_entry, projection)
        if game.get('fit') != old_fit:
            fit_changes += 1

        apply_duration_resolution(game, projection, duration_entries)

        if not refiner.apply_commercial_branch(game, context):
            removed += 1
            continue
        refined.append(game)

    # Purchase-option enrichment belongs before the one canonical final ranking pass.
    # This lets the ranking compare the economics of buying the game alone with the
    # economics of a fixed multi-game package without inventing a second sort layer.
    ready['items'] = refined
    package_stats = package_options.apply_current_artifacts_to_visual(ready)
    refined = ready.get('items') or []

    # taste_rank is diagnostic only. It is deliberately not the source of priority_rank.
    taste_sorted = sorted(refined, key=refiner.taste_sort_key)
    for index, game in enumerate(taste_sorted, 1):
        game['taste_rank'] = index

    refined, final_priority_order = priority_ranking.apply_final_priority_order(refined)

    ready['items'] = refined
    ready['item_count'] = len(refined)
    with_screenshots = sum(bool(game.get('screenshots')) for game in refined)
    with_any_image = sum(bool(game.get('screenshots') or game.get('header_image')) for game in refined)
    ready['media_coverage'] = {
        'visible_item_count': len(refined),
        'with_screenshots': with_screenshots,
        'with_any_image': with_any_image,
        'without_any_image': len(refined) - with_any_image,
        'coverage_percent': round((with_any_image / len(refined)) * 100, 1) if refined else 100.0,
    }
    ready['giveaways'] = giveaway_visual_handoff.derive_from_path()
    duration_distribution = duration_source_distribution(refined)
    contract = ready.setdefault('production_contract', {})
    contract.clear()
    contract.update({
        'schema_version': 7,
        'mode': 'daily_precomputed_read_only_for_ui',
        'heavy_calculation_allowed_in_ui': False,
        'external_lookup_allowed_in_ui': False,
        'visual_builder_blob_sha': base_builder.git_sha('scripts/build_visual_feed_v2.py'),
        'final_visual_producer_blob_sha': base_builder.git_sha('scripts/build_final_visual_payload.py'),
        'card_explanation_policy_blob_sha': base_builder.git_sha('scripts/card_explanation_policy.py'),
        'achievement_quality_builder_blob_sha': base_builder.git_sha('scripts/achievement_quality.py'),
        'ranking_helper_blob_sha': base_builder.git_sha('scripts/priority_ranking.py'),
        'ranking_policy_blob_sha': base_builder.git_sha('config/final_ranking_policy.json'),
        'refinement_helper_blob_sha': base_builder.git_sha('scripts/refine_visual_ranking.py'),
        'duration_enrichment_helper_blob_sha': base_builder.git_sha('scripts/duration_enrichment.py'),
        'duration_enrichment_contract_blob_sha': base_builder.git_sha('config/duration_enrichment_contract.json'),
        'duration_cache_blob_sha': base_builder.git_sha('data/cache/duration_estimates.json'),
        'fixed_package_helper_blob_sha': base_builder.git_sha('scripts/apply_fixed_package_purchase_options.py'),
        'fixed_package_options_blob_sha': package_options.git_blob_sha(package_options.PACKAGE_OPTIONS),
        'purchase_equivalence_blob_sha': package_options.git_blob_sha(package_options.PURCHASE_EQUIVALENCE),
        'source_chatgpt_payload_blob_sha': base_builder.git_sha('data/production/pre_ai/chatgpt_payload.json'),
        'source_purchase_context_blob_sha': base_builder.git_sha('data/production/pre_ai/chatgpt_purchase_context.jsonl'),
        'source_taste_queue_blob_sha': base_builder.git_sha('data/production/pre_ai/chatgpt_taste_queue.jsonl'),
        'source_history_snapshot_blob_sha': base_builder.git_sha('data/production/pre_ai/history_snapshot.json'),
        'giveaway_visual_handoff_blob_sha': base_builder.git_sha('scripts/giveaway_visual_handoff.py'),
        'source_giveaway_snapshot_blob_sha': base_builder.git_sha('data/production/giveaways/v1/current.json'),
        'giveaway_visual_schema_version': 1,
        'source_family_count': payload.get('source_family_count'),
        'ready_family_count_before_expiry_filter': payload.get('ready_without_ai_count'),
        'visible_family_count': len(refined),
        'expired_family_count_removed_at_build': ready.get('expired_family_count_removed_at_build'),
        'ai_queue_count': payload.get('ai_queue_count'),
        'complete_family_partition': payload.get('complete_family_partition'),
        'canonical_profile_blob_sha': (payload.get('profile_binding') or {}).get('canonical_profile_blob_sha'),
        'taste_model_version': (payload.get('profile_binding') or {}).get('taste_model_version'),
        'ranking_stage': 'single_final_sort_after_all_refinement_and_purchase_option_enrichment',
        'priority_factors': final_priority_order,
        'priority_ranking_contract': 'FINAL-PRIORITY-RANKING-V2',
        'card_explanation_rule': 'positive requires specific Taste evidence; visible negative requires grounded provenance; scoring/ranking semantics unchanged',
        'fixed_package_purchase_option_rule': (
            'fixed Sub only; >=2 visible base-game families by exact appid or explicit verified '
            'purchase equivalence; relevant package information may be displayed without strict '
            'savings; ranking boost remains fail-closed and requires the commercial package route '
            'to satisfy ranking policy; personalized bundles excluded'
        ),
        'fixed_package_qualifying_count': package_stats.get('qualifying_package_count'),
        'fixed_package_strict_savings_count': package_stats.get('strict_savings_package_count'),
        'fixed_package_verified_equivalence_count': package_stats.get('verified_equivalence_package_count'),
        'fixed_package_touched_game_count': package_stats.get('visible_game_count_with_better_package'),
        'direct_user_evidence_rule': 'adjusts fit/bucket upstream; not a second final sort factor',
        'windows_rule': 'legacy Steam XP/7/8 requirement label alone is neutral; only confirmed modern-Windows friction may penalize',
        'ui_manual_end_rule': 'local explicit end-of-queue override is applied by UI after production priority_rank',
        'backtracking_rule': 'location reuse itself is neutral; penalize unchanged repetition without new gameplay value',
        'duration_rule': 'structured IGDB normally -> legacy explicit-text fallback -> unknown; ranking weights unchanged',
        'duration_source_precedence': [
            'validated_structured_igdb_normally',
            'legacy_text_explicit_duration_phrase',
            'unknown',
        ],
        'duration_source_distribution': duration_distribution,
        'achievement_profile_scale': {
            '5': 'new_play_styles_or_challenges',
            '4': 'deeper_mechanic_use',
            '3': 'meaningful_optional_goals_or_secrets',
            '2': 'mostly_grind_or_collectathon',
            '1': 'mostly_automatic_story_progression',
        },
        'achievement_quality_distribution': achievement_distribution,
        'refinement_stats': {
            'fit_changes': fit_changes,
            'removed_after_fit_change_and_commercial_recheck': removed,
            'legacy_windows_labels_neutralized': windows_labels_neutralized,
            'direct_profile_loaded': profile is not None,
            'direct_profile_error': profile_error,
        },
    })

    OUT.write_text(json.dumps(ready, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(
        f'VISUAL_FINAL_BUILD=BUILT source={source_key} items={len(refined)} '
        f'expired_removed={ready.get("expired_family_count_removed_at_build")} '
        f'fit_changes={fit_changes} removed={removed} '
        f'windows_labels_neutralized={windows_labels_neutralized} '
        f'duration_igdb={duration_distribution.get("structured_igdb")} '
        f'duration_text={duration_distribution.get("legacy_text")} '
        f'duration_unknown={duration_distribution.get("unknown")} '
        f'package_qualifying={package_stats.get("qualifying_package_count")} '
        f'package_strict={package_stats.get("strict_savings_package_count")} '
        f'package_equivalence={package_stats.get("verified_equivalence_package_count")} '
        f'package_touched={package_stats.get("visible_game_count_with_better_package")} '
        f'giveaways={ready.get("giveaways", {}).get("state")} '
        f'force={os.environ.get("FORCE_VISUAL_BUILD") == "1"}'
    )


if __name__ == '__main__':
    main()

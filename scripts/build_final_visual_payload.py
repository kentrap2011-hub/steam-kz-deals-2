import json
import os
from pathlib import Path

import apply_fixed_package_purchase_options as package_options
import build_daily_visual_payload as base_builder
import priority_ranking
import refine_visual_ranking as refiner

ROOT = Path('.')
OUT = ROOT / 'data/production/visual/current.json'


def normalize_media_url(value):
    if isinstance(value, str) and value.startswith('https://shared.fastly.steamstatic.com/'):
        return 'https://shared.akamai.steamstatic.com/' + value[len('https://shared.fastly.steamstatic.com/'):]
    return value


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
        'ranking_stage': 'single_canonical_sort_after_deterministic_purchase_option_refresh',
        'priority_factors': final_priority_order,
        'priority_ranking_contract': 'FINAL-PRIORITY-RANKING-V2',
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


def refresh_existing_media():
    if not OUT.exists():
        return False, 0, 0, {}

    before = OUT.read_text(encoding='utf-8')
    ready = json.loads(before)
    items = ready.get('items') or []
    wanted_appids = set()
    for game in items:
        for appid in game.get('base_appids') or []:
            appid = str(appid)
            if appid.isdigit():
                wanted_appids.add(appid)

    media = base_builder.visual_builder.storebrowse_media(wanted_appids) if wanted_appids else {}
    touched = 0
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
        if changed:
            touched += 1

    # Even when there is no new semantic Taste result, package/equivalence/price logic
    # is deterministic and must be allowed to refresh the current visual snapshot.
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
    contract = ready.setdefault('production_contract', {})
    contract['visual_builder_blob_sha'] = base_builder.git_sha('scripts/build_visual_feed_v2.py')
    contract['final_visual_producer_blob_sha'] = base_builder.git_sha('scripts/build_final_visual_payload.py')

    after = json.dumps(ready, ensure_ascii=False, separators=(',', ':'))
    if after == before:
        return False, touched, len(media), package_stats

    OUT.write_text(after, encoding='utf-8')
    return True, touched, len(media), package_stats


def main():
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
    ready['items'] = base_builder.achievement_quality.enrich_visual_items(ready.get('items') or [])
    ready = base_builder.enrich_history_and_remove_expired(ready, context_by_family, payload)
    achievement_distribution = base_builder.achievement_quality_distribution(ready.get('items') or [])

    taste_entries = refiner.effective_taste_entries()
    projections = (
        (refiner.load_json(refiner.TASTE_PROJECTION).get('entries') or {})
        if refiner.TASTE_PROJECTION.exists()
        else {}
    )
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

        risks = {}
        for ev in taste_entry.get('negative_evidence') or []:
            refiner.map_negative_evidence(ev, risks)
        for code, row in refiner.structural_risks(projection, practical).items():
            refiner.add_risk(
                risks,
                code,
                row['score'],
                row['text'],
                row.get('source') or 'derived',
            )

        risk_texts, risk_codes, risk_penalty, risk_level = refiner.risk_summary(risks)
        game['risks'] = risk_texts
        game['risk_codes'] = risk_codes
        game['risk_penalty'] = risk_penalty
        game['risk_level'] = risk_level

        evidence = refiner.direct_evidence(game, direct_index)
        game['direct_user_evidence'] = evidence or {'level': 'none'}
        old_fit = game.get('fit')
        refiner.apply_fit_adjustment(game, evidence, risks, taste_entry, projection)
        if game.get('fit') != old_fit:
            fit_changes += 1

        hours, duration_source = refiner.extract_duration_hours(projection, game)
        band, penalty = refiner.duration_band(hours)
        game['estimated_duration_hours'] = hours
        game['duration_estimate_source'] = duration_source
        game['duration_preference_band'] = band
        game['duration_tiebreak_penalty'] = penalty

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
    contract = ready.setdefault('production_contract', {})
    contract.clear()
    contract.update({
        'schema_version': 7,
        'mode': 'daily_precomputed_read_only_for_ui',
        'heavy_calculation_allowed_in_ui': False,
        'external_lookup_allowed_in_ui': False,
        'visual_builder_blob_sha': base_builder.git_sha('scripts/build_visual_feed_v2.py'),
        'final_visual_producer_blob_sha': base_builder.git_sha('scripts/build_final_visual_payload.py'),
        'achievement_quality_builder_blob_sha': base_builder.git_sha('scripts/achievement_quality.py'),
        'ranking_helper_blob_sha': base_builder.git_sha('scripts/priority_ranking.py'),
        'ranking_policy_blob_sha': base_builder.git_sha('config/final_ranking_policy.json'),
        'refinement_helper_blob_sha': base_builder.git_sha('scripts/refine_visual_ranking.py'),
        'fixed_package_helper_blob_sha': base_builder.git_sha('scripts/apply_fixed_package_purchase_options.py'),
        'fixed_package_options_blob_sha': package_options.git_blob_sha(package_options.PACKAGE_OPTIONS),
        'purchase_equivalence_blob_sha': package_options.git_blob_sha(package_options.PURCHASE_EQUIVALENCE),
        'source_chatgpt_payload_blob_sha': base_builder.git_sha('data/production/pre_ai/chatgpt_payload.json'),
        'source_purchase_context_blob_sha': base_builder.git_sha('data/production/pre_ai/chatgpt_purchase_context.jsonl'),
        'source_taste_queue_blob_sha': base_builder.git_sha('data/production/pre_ai/chatgpt_taste_queue.jsonl'),
        'source_history_snapshot_blob_sha': base_builder.git_sha('data/production/pre_ai/history_snapshot.json'),
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
        'duration_rule': 'very weak late tiebreak only',
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
        f'package_qualifying={package_stats.get("qualifying_package_count")} '
        f'package_strict={package_stats.get("strict_savings_package_count")} '
        f'package_equivalence={package_stats.get("verified_equivalence_package_count")} '
        f'package_touched={package_stats.get("visible_game_count_with_better_package")} '
        f'force={os.environ.get("FORCE_VISUAL_BUILD") == "1"}'
    )


if __name__ == '__main__':
    main()

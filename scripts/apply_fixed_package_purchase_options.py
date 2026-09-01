import json
import subprocess
from collections import defaultdict
from pathlib import Path

import refresh_visual_commercial_fields as commercial_refresh

PACKAGE_OPTIONS = Path('data/production/pre_ai/fixed_package_options.json')
FAMILY_GRAPH = Path('data/production/pre_ai/family_graph.json')
FX_SNAPSHOT = Path('data/production/pre_ai/fx_snapshot.json')
PURCHASE_EQUIVALENCE = Path('config/purchase_equivalence_overrides.json')
VISUAL = Path('data/production/visual/current.json')


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rub_display(kzt, kzt_per_rub):
    if kzt is None or not kzt_per_rub:
        return None
    return int(round(float(kzt) / float(kzt_per_rub)))


def load_purchase_equivalence(path=PURCHASE_EQUIVALENCE):
    if not Path(path).exists():
        return {}
    doc = load_json(Path(path))
    if doc.get('contract') != 'PURCHASE-EQUIVALENCE-OVERRIDES-V1':
        raise ValueError('Unsupported purchase equivalence contract')
    if doc.get('status') != 'canonical':
        raise ValueError('Purchase equivalence overrides are not canonical')
    rules = doc.get('rules') or {}
    if rules.get('affects_taste') is not False or rules.get('affects_family_graph') is not False:
        raise ValueError('Purchase equivalence must remain purchase-only')
    if rules.get('title_or_franchise_guessing_allowed') is not False:
        raise ValueError('Purchase equivalence title guessing must remain disabled')

    result = {}
    for visible_appid, entry in (doc.get('entries') or {}).items():
        if not str(visible_appid).isdigit() or not isinstance(entry, dict):
            raise ValueError(f'Invalid purchase equivalence entry: {visible_appid!r}')
        substitutes = {
            str(value)
            for value in (entry.get('package_substitute_appids') or [])
            if str(value).isdigit()
        }
        if not substitutes:
            raise ValueError(f'Purchase equivalence has no substitutes: {visible_appid}')
        result[str(visible_appid)] = {
            'package_substitute_appids': substitutes,
            'relationship': entry.get('relationship') or 'verified_purchase_substitute',
            'visible_title': entry.get('visible_title'),
            'package_substitute_titles': entry.get('package_substitute_titles') or [],
            'evidence_note': entry.get('evidence_note'),
        }
    return result


def family_rows(family_graph, visible_items):
    graph = {
        str(row.get('family_id')): row
        for row in (family_graph.get('families') or [])
        if row.get('family_id')
    }
    rows = {}
    for game in visible_items:
        fid = str(game.get('id') or '')
        family = graph.get(fid)
        if not family or family.get('family_type') != 'base_game':
            continue
        price = game.get('current_price_kzt')
        if price is None:
            price = family.get('primary_final_kzt')
        if price is None or float(price) <= 0:
            continue
        appids = {
            str(value)
            for value in (family.get('base_appids') or [])
            if str(value).isdigit()
        }
        if not appids:
            continue
        rows[fid] = {
            'family_id': fid,
            'title': game.get('title') or family.get('primary_title') or fid,
            'price_kzt': float(price),
            'base_appids': appids,
        }
    return rows


def visible_rows_without_price(visible_items):
    rows = {}
    for game in visible_items:
        fid = str(game.get('id') or '')
        if not fid:
            continue
        appids = {
            str(value)
            for value in (game.get('base_appids') or [])
            if str(value).isdigit()
        }
        if not appids:
            continue
        rows[fid] = {
            'family_id': fid,
            'title': game.get('title') or fid,
            'price_kzt': None,
            'base_appids': appids,
        }
    return rows


def build_coverage_index(visible, purchase_equivalence=None):
    purchase_equivalence = purchase_equivalence or {}
    appid_to_family = defaultdict(list)
    for fid, row in visible.items():
        for appid in sorted(row['base_appids']):
            appid_to_family[appid].append({
                'family_id': fid,
                'coverage_mode': 'exact_included_appid',
                'visible_appid': appid,
                'package_appid': appid,
                'relationship': 'exact',
            })
            override = purchase_equivalence.get(appid)
            if not override:
                continue
            for substitute in sorted(override['package_substitute_appids']):
                appid_to_family[substitute].append({
                    'family_id': fid,
                    'coverage_mode': 'verified_purchase_equivalence',
                    'visible_appid': appid,
                    'package_appid': substitute,
                    'relationship': override.get('relationship'),
                    'evidence_note': override.get('evidence_note'),
                })
    return appid_to_family


def eligible_fixed_package(package):
    if not isinstance(package, dict):
        return False
    if package.get('entity_kind') != 'sub':
        return False
    if package.get('fixed_price_semantics') is not True:
        return False
    if package.get('personalized_price') is not False:
        return False
    package_price = package.get('final_kzt')
    return package_price is not None and float(package_price) > 0


def coverage_for_package(package, visible, appid_to_family):
    coverage_by_family = defaultdict(list)
    for appid in package.get('included_appids') or []:
        package_appid = str(appid)
        for evidence in appid_to_family.get(package_appid, []):
            fid = evidence['family_id']
            if evidence not in coverage_by_family[fid]:
                coverage_by_family[fid].append(evidence)
    covered_ids = set(coverage_by_family)
    if len(covered_ids) < 2:
        return None, None
    covered = [visible[fid] for fid in sorted(covered_ids)]
    coverage_evidence = [
        {
            'family_id': row['family_id'],
            'visible_title': row['title'],
            'matches': coverage_by_family[row['family_id']],
        }
        for row in covered
    ]
    return covered, coverage_evidence


def package_base_record(package, covered, coverage_evidence, kzt_per_rub):
    package_price = float(package['final_kzt'])
    original_kzt = package.get('original_kzt')
    package_price_rub = rub_display(package_price, kzt_per_rub)
    count = len(covered)
    return {
        'package_key': package.get('key') or f"Sub_{package.get('packageid')}",
        'packageid': int(package.get('packageid') or 0),
        'package_title': package.get('title') or package.get('purchase_option_name') or 'Steam package',
        'package_price_kzt': round(package_price, 2),
        'package_price_rub': package_price_rub,
        'package_price_per_visible_game_rub': (
            round(float(package_price_rub) / count, 1)
            if package_price_rub is not None and count > 0
            else None
        ),
        'package_original_kzt': round(float(original_kzt), 2) if original_kzt is not None else None,
        'package_original_rub': rub_display(original_kzt, kzt_per_rub),
        'discount_percent': int(package.get('discount_percent') or 0),
        'discount_end_utc': package.get('discount_end_utc'),
        'covered_visible_game_ids': [row['family_id'] for row in covered],
        'covered_visible_titles': [row['title'] for row in covered],
        'covered_visible_game_count': count,
        'coverage_evidence': coverage_evidence,
        'uses_verified_purchase_equivalence': any(
            match.get('coverage_mode') == 'verified_purchase_equivalence'
            for family in coverage_evidence
            for match in family.get('matches') or []
        ),
        'requires_multi_game_intent': True,
        'unknown_extra_content_value_assumed_kzt': 0,
        'web_url': package.get('web_url'),
    }


def build_recommendations(package_artifact, family_graph, visible_items, kzt_per_rub, purchase_equivalence=None):
    visible = family_rows(family_graph, visible_items)
    appid_to_family = build_coverage_index(visible, purchase_equivalence)

    recommendations = []
    for package in (package_artifact.get('packages') or {}).values():
        if not eligible_fixed_package(package):
            continue
        covered, coverage_evidence = coverage_for_package(package, visible, appid_to_family)
        if not covered:
            continue

        standalone_total = sum(row['price_kzt'] for row in covered)
        package_price = float(package['final_kzt'])
        savings = standalone_total - package_price
        strict_savings = savings > 0.01
        package_price_rub = rub_display(package_price, kzt_per_rub)
        standalone_total_rub = rub_display(standalone_total, kzt_per_rub)
        savings_rub = rub_display(savings, kzt_per_rub)

        rec = package_base_record(package, covered, coverage_evidence, kzt_per_rub)
        rec.update({
            'standalone_total_kzt': round(standalone_total, 2),
            'standalone_total_rub': standalone_total_rub,
            'savings_kzt': round(savings, 2),
            'savings_rub': savings_rub,
            'savings_percent_vs_standalone': round((savings / standalone_total) * 100.0, 1),
            'strict_current_price_savings': strict_savings,
            'price_delta_vs_standalone_kzt': round(package_price - standalone_total, 2),
            'price_delta_vs_standalone_rub': (
                None
                if package_price_rub is None or standalone_total_rub is None
                else package_price_rub - standalone_total_rub
            ),
            'comparison_source_aligned': True,
            'ranking_comparison_unavailable_reason': None,
            'comparison_scope': 'currently_visible_base_game_families_covered_by_exact_or_verified_purchase_equivalence',
        })
        recommendations.append(rec)

    recommendations.sort(key=lambda row: (
        0 if row.get('strict_current_price_savings') else 1,
        -float(row['savings_kzt']),
        -int(row['covered_visible_game_count']),
        -float(row['savings_percent_vs_standalone']),
        float(row['package_price_kzt']),
        int(row['packageid']),
    ))

    best_by_family = {}
    for rec in recommendations:
        for fid in rec['covered_visible_game_ids']:
            best_by_family.setdefault(fid, rec)
    return recommendations, best_by_family


def build_display_only_recommendations(package_artifact, visible_items, kzt_per_rub, purchase_equivalence=None):
    visible = visible_rows_without_price(visible_items)
    appid_to_family = build_coverage_index(visible, purchase_equivalence)
    recommendations = []

    for package in (package_artifact.get('packages') or {}).values():
        if not eligible_fixed_package(package):
            continue
        covered, coverage_evidence = coverage_for_package(package, visible, appid_to_family)
        if not covered:
            continue
        rec = package_base_record(package, covered, coverage_evidence, kzt_per_rub)
        rec.update({
            'standalone_total_kzt': None,
            'standalone_total_rub': None,
            'savings_kzt': None,
            'savings_rub': None,
            'savings_percent_vs_standalone': None,
            'strict_current_price_savings': False,
            'price_delta_vs_standalone_kzt': None,
            'price_delta_vs_standalone_rub': None,
            'comparison_source_aligned': False,
            'ranking_comparison_unavailable_reason': 'visual_and_package_sources_differ',
            'comparison_scope': 'display_only_membership_coverage_until_visual_and_price_sources_align',
        })
        recommendations.append(rec)

    recommendations.sort(key=lambda row: (
        -int(row['covered_visible_game_count']),
        float(row['package_price_kzt']),
        int(row['packageid']),
    ))
    best_by_family = {}
    for rec in recommendations:
        for fid in rec['covered_visible_game_ids']:
            best_by_family.setdefault(fid, rec)
    return recommendations, best_by_family


def compact_titles(titles, max_items=4):
    titles = [str(value) for value in titles if value]
    if len(titles) <= max_items:
        return ', '.join(titles)
    return ', '.join(titles[:max_items]) + f' и ещё {len(titles) - max_items}'


def offer_from_recommendation(rec):
    titles = compact_titles(rec['covered_visible_titles'])
    savings_rub = rec.get('savings_rub')
    strict = rec.get('strict_current_price_savings') is True
    source_aligned = rec.get('comparison_source_aligned') is not False
    if strict:
        economics = f"экономия около {savings_rub} ₽" if savings_rub is not None else f"экономия {rec['savings_kzt']:.0f} KZT"
        prefix = 'Выгодный набор'
    elif not source_aligned:
        economics = 'сравнение выгоды обновится после синхронизации цен'
        prefix = 'Набор Steam'
    else:
        delta = rec.get('price_delta_vs_standalone_rub')
        economics = (
            f'примерно на {abs(int(delta))} ₽ дороже этих игр отдельно'
            if delta is not None and delta > 0
            else 'не дешевле этих игр отдельно'
        )
        prefix = 'Набор Steam'
    title = (
        f"{prefix}: {rec['package_title']} — "
        f"{rec['covered_visible_game_count']} игры из списка ({titles}), {economics}"
    )
    return {
        'key': rec['package_key'],
        'title': title,
        'offer_kind': 'fixed_multi_game_package',
        'current_price_rub': rec.get('package_price_rub'),
        'original_price_rub': rec.get('package_original_rub'),
        'discount_percent': rec.get('discount_percent'),
        'historical_minimum_rub': None,
        'history_quality': 'not_applicable_to_purchase_option_comparison',
        'previously_free': False,
        'sale_end_utc': rec.get('discount_end_utc'),
        'web_url': rec.get('web_url'),
        'steam_url': None,
        'package_comparison': rec,
    }


def source_binding_status(visual, packages, family_graph):
    semantic_source = visual.get('source_mailing_updated_at_utc')
    source = visual.get('commercial_source_mailing_updated_at_utc') or semantic_source
    package_source = packages.get('source_mailing_updated_at_utc')
    family_source = family_graph.get('source_updated_at_utc')
    return {
        'aligned': bool(source and package_source == source and family_source == source),
        'semantic_source': semantic_source,
        'visual_source': source,
        'package_source': package_source,
        'family_source': family_source,
    }


def apply_to_visual(visual, packages, family_graph, kzt_per_rub, purchase_equivalence=None):
    if kzt_per_rub is None or float(kzt_per_rub) <= 0:
        raise ValueError('Fixed package enrichment requires positive kzt_per_rub')

    items = visual.get('items') or []
    binding = source_binding_status(visual, packages, family_graph)
    if binding['aligned']:
        recommendations, best_by_family = build_recommendations(
            packages,
            family_graph,
            items,
            float(kzt_per_rub),
            purchase_equivalence=purchase_equivalence,
        )
    else:
        recommendations, best_by_family = build_display_only_recommendations(
            packages,
            items,
            float(kzt_per_rub),
            purchase_equivalence=purchase_equivalence,
        )

    touched = 0
    touched_ids = []
    for game in items:
        fid = str(game.get('id') or '')
        rec = best_by_family.get(fid)
        offers = [
            offer for offer in (game.get('offers') or [])
            if (offer.get('offer_kind') if isinstance(offer, dict) else None)
            != 'fixed_multi_game_package'
        ]
        if rec is None:
            game.pop('better_purchase_option', None)
            game['offers'] = offers
            continue

        game['better_purchase_option'] = rec
        package_key = rec['package_key']
        offers = [
            offer for offer in offers
            if not (isinstance(offer, dict) and offer.get('key') == package_key)
        ]
        offers.append(offer_from_recommendation(rec))
        game['offers'] = offers
        touched += 1
        touched_ids.append(fid)

    strict_count = sum(1 for row in recommendations if row.get('strict_current_price_savings') is True)
    equivalence_count = sum(1 for row in recommendations if row.get('uses_verified_purchase_equivalence') is True)
    stats = {
        'schema_version': 5,
        'fixed_sub_only': True,
        'dynamic_bundle_supported': False,
        'personalized_complete_the_set_supported': False,
        'source_binding_aligned': binding['aligned'],
        'display_only_due_source_mismatch': not binding['aligned'],
        'semantic_source_mailing_updated_at_utc': binding['semantic_source'],
        'commercial_source_mailing_updated_at_utc': binding['visual_source'],
        'package_source_mailing_updated_at_utc': binding['package_source'],
        'family_source_updated_at_utc': binding['family_source'],
        'qualifying_package_count': len(recommendations),
        'strict_savings_package_count': strict_count,
        'verified_equivalence_package_count': equivalence_count,
        'visible_game_count_with_better_package': touched,
        'visible_game_ids_with_better_package': touched_ids,
        'comparison_rule': (
            'refresh current commercial fields from the current GitHub-owned store/history/family source, '
            'then compare fixed Steam Sub packages across at least two visible base-game families by exact '
            'included appid or explicit verified purchase equivalence; Taste source remains independent'
        ),
        'ranking_stage_requirement': 'commercial refresh and package enrichment before the single final ranking pass',
    }
    visual['purchase_option_enrichment'] = stats
    return stats


def apply_current_artifacts_to_visual(visual):
    missing = [
        str(path)
        for path in (PACKAGE_OPTIONS, FAMILY_GRAPH, FX_SNAPSHOT, PURCHASE_EQUIVALENCE)
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(f'Fixed package enrichment missing required artifacts: {missing}')

    commercial_refresh.refresh_visual_commercial_fields(visual)

    packages = load_json(PACKAGE_OPTIONS)
    family_graph = load_json(FAMILY_GRAPH)
    fx = load_json(FX_SNAPSHOT)
    purchase_equivalence = load_purchase_equivalence(PURCHASE_EQUIVALENCE)
    rate = ((fx.get('fx') or {}).get('kzt_per_rub'))
    return apply_to_visual(
        visual,
        packages,
        family_graph,
        rate,
        purchase_equivalence=purchase_equivalence,
    )


def git_blob_sha(path):
    try:
        value = subprocess.check_output(
            ['git', 'rev-parse', f'HEAD:{path.as_posix()}'],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return value or None
    except Exception:
        return None


def attach_contract_fields(visual):
    contract = visual.setdefault('production_contract', {})
    contract['fixed_package_options_blob_sha'] = git_blob_sha(PACKAGE_OPTIONS)
    contract['purchase_equivalence_blob_sha'] = git_blob_sha(PURCHASE_EQUIVALENCE)
    contract['fixed_package_purchase_option_rule'] = (
        'refresh current commercial fields independently of Taste; fixed Sub only; >=2 visible game '
        'families by exact appid or explicit verified purchase equivalence; personalized bundles excluded; '
        'package enrichment before final ranking'
    )


def main():
    if not VISUAL.exists():
        raise SystemExit('Fixed package enrichment requires an existing visual payload')
    visual = load_json(VISUAL)
    stats = apply_current_artifacts_to_visual(visual)
    attach_contract_fields(visual)
    VISUAL.write_text(
        json.dumps(visual, ensure_ascii=False, separators=(',', ':')),
        encoding='utf-8',
    )
    print(
        'FIXED_PACKAGE_OPTIONS=APPLIED '
        f"qualifying_packages={stats['qualifying_package_count']} "
        f"strict_savings_packages={stats['strict_savings_package_count']} "
        f"verified_equivalence_packages={stats['verified_equivalence_package_count']} "
        f"touched_games={stats['visible_game_count_with_better_package']} "
        f"source_aligned={stats['source_binding_aligned']}"
    )


if __name__ == '__main__':
    main()

import json
import subprocess
from pathlib import Path

PACKAGE_OPTIONS = Path('data/production/pre_ai/fixed_package_options.json')
FAMILY_GRAPH = Path('data/production/pre_ai/family_graph.json')
FX_SNAPSHOT = Path('data/production/pre_ai/fx_snapshot.json')
VISUAL = Path('data/production/visual/current.json')


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rub_display(kzt, kzt_per_rub):
    if kzt is None or not kzt_per_rub:
        return None
    return int(round(float(kzt) / float(kzt_per_rub)))


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


def build_recommendations(package_artifact, family_graph, visible_items, kzt_per_rub):
    visible = family_rows(family_graph, visible_items)
    appid_to_family = {}
    for fid, row in visible.items():
        for appid in row['base_appids']:
            appid_to_family.setdefault(appid, set()).add(fid)

    recommendations = []
    for package in (package_artifact.get('packages') or {}).values():
        if not isinstance(package, dict):
            continue
        if package.get('entity_kind') != 'sub':
            continue
        if package.get('fixed_price_semantics') is not True:
            continue
        if package.get('personalized_price') is not False:
            continue
        package_price = package.get('final_kzt')
        if package_price is None or float(package_price) <= 0:
            continue

        covered_ids = set()
        for appid in package.get('included_appids') or []:
            covered_ids.update(appid_to_family.get(str(appid), set()))
        if len(covered_ids) < 2:
            continue

        covered = [visible[fid] for fid in sorted(covered_ids)]
        standalone_total = sum(row['price_kzt'] for row in covered)
        savings = standalone_total - float(package_price)
        if savings <= 0.01:
            continue

        covered_titles = [row['title'] for row in covered]
        original_kzt = package.get('original_kzt')
        package_price_rub = rub_display(package_price, kzt_per_rub)
        standalone_total_rub = rub_display(standalone_total, kzt_per_rub)
        savings_rub = rub_display(savings, kzt_per_rub)
        count = len(covered)
        rec = {
            'package_key': package.get('key') or f"Sub_{package.get('packageid')}",
            'packageid': int(package.get('packageid') or 0),
            'package_title': package.get('title') or package.get('purchase_option_name') or 'Steam package',
            'package_price_kzt': round(float(package_price), 2),
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
            'covered_visible_titles': covered_titles,
            'covered_visible_game_count': count,
            'standalone_total_kzt': round(standalone_total, 2),
            'standalone_total_rub': standalone_total_rub,
            'savings_kzt': round(savings, 2),
            'savings_rub': savings_rub,
            'savings_percent_vs_standalone': round((savings / standalone_total) * 100.0, 1),
            'requires_multi_game_intent': True,
            'comparison_scope': 'currently_visible_base_game_families_covered_by_package',
            'unknown_extra_content_value_assumed_kzt': 0,
            'web_url': package.get('web_url'),
        }
        recommendations.append(rec)

    recommendations.sort(key=lambda row: (
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


def compact_titles(titles, max_items=4):
    titles = [str(value) for value in titles if value]
    if len(titles) <= max_items:
        return ', '.join(titles)
    return ', '.join(titles[:max_items]) + f' и ещё {len(titles) - max_items}'


def offer_from_recommendation(rec):
    titles = compact_titles(rec['covered_visible_titles'])
    savings_rub = rec.get('savings_rub')
    savings_text = f'{savings_rub} ₽' if savings_rub is not None else f"{rec['savings_kzt']:.0f} KZT"
    title = (
        f"Выгодный набор: {rec['package_title']} — "
        f"{rec['covered_visible_game_count']} игры из списка ({titles}), "
        f"экономия около {savings_text}"
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


def validate_source_binding(visual, packages, family_graph):
    source = visual.get('source_mailing_updated_at_utc')
    package_source = packages.get('source_mailing_updated_at_utc')
    family_source = family_graph.get('source_updated_at_utc')
    if not source or package_source != source or family_source != source:
        raise ValueError(
            'Fixed package source mismatch: '
            f'visual={source} packages={package_source} family={family_source}'
        )


def apply_to_visual(visual, packages, family_graph, kzt_per_rub):
    validate_source_binding(visual, packages, family_graph)
    if kzt_per_rub is None or float(kzt_per_rub) <= 0:
        raise ValueError('Fixed package enrichment requires positive kzt_per_rub')

    items = visual.get('items') or []
    recommendations, best_by_family = build_recommendations(
        packages, family_graph, items, float(kzt_per_rub)
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

    stats = {
        'schema_version': 2,
        'fixed_sub_only': True,
        'dynamic_bundle_supported': False,
        'personalized_complete_the_set_supported': False,
        'qualifying_package_count': len(recommendations),
        'visible_game_count_with_better_package': touched,
        'visible_game_ids_with_better_package': touched_ids,
        'comparison_rule': (
            'recommend only a fixed Steam Sub package covering at least two currently visible '
            'base-game families when package price is strictly below the sum of those standalone '
            'family prices; unknown extra content contributes zero value'
        ),
        'ranking_stage_requirement': 'package enrichment must happen before the single final ranking pass',
    }
    visual['purchase_option_enrichment'] = stats
    return stats


def apply_current_artifacts_to_visual(visual):
    missing = [
        str(path)
        for path in (PACKAGE_OPTIONS, FAMILY_GRAPH, FX_SNAPSHOT)
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(f'Fixed package enrichment missing required artifacts: {missing}')
    packages = load_json(PACKAGE_OPTIONS)
    family_graph = load_json(FAMILY_GRAPH)
    fx = load_json(FX_SNAPSHOT)
    rate = ((fx.get('fx') or {}).get('kzt_per_rub'))
    return apply_to_visual(visual, packages, family_graph, rate)


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
    contract['fixed_package_purchase_option_rule'] = (
        'fixed Sub only; >=2 visible game families; strict current-price savings; '
        'unknown extra content value=0; personalized bundles excluded; package enrichment before final ranking'
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
        f"touched_games={stats['visible_game_count_with_better_package']}"
    )


if __name__ == '__main__':
    main()

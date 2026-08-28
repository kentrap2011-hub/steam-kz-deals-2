import json
import re
import time
import unicodedata
from collections import defaultdict
from pathlib import Path

MAILING = Path('data/production/mailing/index.json')
STORE = Path('data/production/pre_ai/store_snapshot.json')
META = Path('data/production/pre_ai/content_metadata.json')
RULES = Path('data/production/pre_ai/content_rules.json')
CONTRACT = Path('config/offer_family_contract.json')
OLD_CONTROL = Path('data/cache/offer_family.validation.json')
OUT = Path('data/production/pre_ai/family_graph.json')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_feed(index):
    cols = index['columns']
    ci = {name: i for i, name in enumerate(cols)}
    feed = {}
    for n in range(1, int(index['chunk_count']) + 1):
        p = Path(index['chunk_pattern'].replace('NNN', f'{n:03d}'))
        for line in p.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            cells = line.split('\t')
            if len(cells) != len(cols):
                raise SystemExit(f'Column mismatch in {p}')
            key = cells[ci['key']]
            feed[key] = {
                'key': key,
                'appid': cells[ci['appid']],
                'title': cells[ci['title']],
            }
    if len(feed) != int(index['item_count']):
        raise SystemExit('Mailing item_count mismatch')
    return feed


def normalize_builder(suffixes):
    marker_re = re.compile(
        '|'.join(re.escape(x) for x in sorted(suffixes, key=len, reverse=True)),
        re.I,
    )

    def normalized(title):
        value = unicodedata.normalize('NFKC', title or '').lower().replace('™', '').replace('®', '')
        had_marker = bool(marker_re.search(value))
        value = marker_re.sub('', value)
        value = re.sub(r'\b(edition|upgrade|pack)\b', '', value, flags=re.I)
        value = re.sub(r'[^a-z0-9]+', ' ', value)
        return ' '.join(value.split()), had_marker

    return normalized


def resolve(allowed_keys, feed, store, meta, rules, contract):
    allowed_keys = set(allowed_keys)
    game_keys = {
        key for key in allowed_keys
        if rules[key].get('mechanical_kind') == 'game'
    }
    dlc_keys = {
        key for key in allowed_keys
        if rules[key].get('mechanical_kind') == 'dlc'
    }
    package_keys = {
        key for key in allowed_keys
        if rules[key].get('mechanical_kind') == 'package'
    }

    game_appid_to_key = {
        str(feed[key]['appid']): key
        for key in game_keys
        if feed[key].get('appid')
    }
    game_appids = set(game_appid_to_key)

    families = {}
    family_of = {}
    for key in sorted(game_keys):
        appid = str(feed[key]['appid'])
        fid = f'game:{appid}'
        families[fid] = {
            'family_id': fid,
            'family_type': 'base_game',
            'members': [key],
            'relationship_evidence': [f'exact_game_appid:{appid}'],
            'base_appids': [appid],
            'requires_ai_base_support': False,
        }
        family_of[key] = fid

    # DLC with an on-sale candidate base joins that exact family. An addon whose base
    # is outside the candidate set remains its own conditional family instead of failing.
    for key in sorted(dlc_keys):
        base_appid = str(rules[key].get('base_appid') or '')
        base_key = game_appid_to_key.get(base_appid)
        if base_key and base_key in family_of:
            fid = family_of[base_key]
            families[fid]['members'].append(key)
            families[fid]['relationship_evidence'].append(f'exact_dlc_fullgame:{key}->{base_appid}')
            family_of[key] = fid
        else:
            fid = f'addon:{key}'
            families[fid] = {
                'family_id': fid,
                'family_type': 'external_base_addon',
                'members': [key],
                'relationship_evidence': [f'exact_dlc_external_base:{key}->{base_appid or "unknown"}'],
                'base_appids': [base_appid] if base_appid else [],
                'requires_ai_base_support': True,
            }
            family_of[key] = fid

    # Packages attach only by exact contained base-app relationships.
    for key in sorted(package_keys):
        package_appids = {str(x) for x in (rules[key].get('package_appids') or [])}
        included_base_appids = sorted(package_appids & game_appids)
        representative = str(rules[key].get('representative_appid') or '')
        if representative in game_appids and representative not in included_base_appids:
            included_base_appids.append(representative)
            included_base_appids = sorted(set(included_base_appids))

        if len(included_base_appids) == 1:
            base_key = game_appid_to_key[included_base_appids[0]]
            fid = family_of[base_key]
            families[fid]['members'].append(key)
            families[fid]['relationship_evidence'].append(
                f'exact_package_component:{key}->{included_base_appids[0]}'
            )
            family_of[key] = fid
        elif len(included_base_appids) > 1:
            fid = f'bundle:{key}'
            families[fid] = {
                'family_id': fid,
                'family_type': 'franchise_bundle',
                'members': [key],
                'relationship_evidence': [
                    'exact_package_multiple_candidate_bases:' + ','.join(included_base_appids)
                ],
                'base_appids': included_base_appids,
                'requires_ai_base_support': False,
            }
            family_of[key] = fid
        else:
            fid = f'package:{key}'
            families[fid] = {
                'family_id': fid,
                'family_type': 'package_without_candidate_base',
                'members': [key],
                'relationship_evidence': [
                    'exact_package_no_candidate_base:' + ','.join(sorted(package_appids))
                ],
                'base_appids': [],
                'package_appids': sorted(package_appids),
                'requires_ai_base_support': True,
            }
            family_of[key] = fid

    # Strict edition-title normalization, matching the old family contract.
    normalized = normalize_builder(contract['edition_suffixes'])
    norm_groups = defaultdict(list)
    for key in sorted(game_keys):
        norm, had_marker = normalized(meta[key].get('store_name') or feed[key]['title'])
        if norm:
            norm_groups[norm].append((key, had_marker))

    for norm, items in sorted(norm_groups.items()):
        fids = sorted({family_of[key] for key, _ in items})
        if len(fids) <= 1 or not any(had for _, had in items):
            continue
        target = fids[0]
        for other in fids[1:]:
            if other == target or other not in families:
                continue
            moved = list(families[other]['members'])
            families[target]['members'].extend(moved)
            families[target]['relationship_evidence'].append('exact_normalized_edition_title:' + norm)
            families[target]['base_appids'] = sorted(set(families[target].get('base_appids', [])) | set(families[other].get('base_appids', [])))
            families[target]['requires_ai_base_support'] = families[target].get('requires_ai_base_support', False) or families[other].get('requires_ai_base_support', False)
            for key in moved:
                family_of[key] = target
            del families[other]
        families[target]['family_type'] = 'edition_family'

    ratio = float(contract['primary_variant_selection']['small_increment_ratio'])
    rows = []
    assigned = []

    for fid in sorted(families):
        fam = families[fid]
        members = sorted(set(fam['members']))
        assigned.extend(members)
        addons = [key for key in members if rules[key].get('mechanical_kind') == 'dlc']
        base_candidates = [key for key in members if key not in addons]

        if fam['family_type'] == 'external_base_addon':
            primary = members[0]
            selection_reason = 'standalone_addon_purchase_family_requires_ai_base_support'
            taste_subject = primary
            ai_condition = 'addon_taste_include_and_base_support_required'
        elif fam['family_type'] in {'franchise_bundle', 'package_without_candidate_base'}:
            primary = members[0]
            selection_reason = 'bundle_or_external_package_is_own_family'
            taste_subject = primary
            ai_condition = 'bundle_or_package_taste_evaluation_required'
        else:
            if not base_candidates:
                raise SystemExit(f'Family has no base purchase candidate: {fid}')
            direct_games = [
                key for key in base_candidates
                if rules[key].get('mechanical_kind') == 'game'
            ]
            direct_games.sort(key=lambda key: (
                store[key]['final_kzt'],
                -store[key]['discount_percent'],
                key,
            ))
            baseline = direct_games[0] if direct_games else min(
                base_candidates,
                key=lambda key: (
                    store[key]['final_kzt'],
                    -store[key]['discount_percent'],
                    key,
                ),
            )
            primary = baseline
            selection_reason = 'cheapest_base_containing_variant'

            package_candidates = [
                key for key in base_candidates
                if rules[key].get('mechanical_kind') == 'package'
            ]
            for package_key in sorted(
                package_candidates,
                key=lambda key: (
                    store[key]['final_kzt'],
                    -store[key]['discount_percent'],
                    key,
                ),
            ):
                package_price = store[package_key]['final_kzt']
                base_price = store[baseline]['final_kzt']
                extra_count = max(0, len(rules[package_key].get('package_appids') or []) - 1)
                if package_price <= base_price:
                    primary = package_key
                    selection_reason = 'package_not_more_expensive_than_base'
                    break
                if base_price > 0 and (package_price - base_price) / base_price <= ratio and extra_count >= 1:
                    primary = package_key
                    selection_reason = 'small_increment_adds_package_content'
                    break

            if not package_candidates and len(base_candidates) > 1:
                primary = min(
                    base_candidates,
                    key=lambda key: (
                        store[key]['final_kzt'],
                        -store[key]['discount_percent'],
                        key,
                    ),
                )
                selection_reason = 'cheapest_local_edition_variant'

            taste_subject = direct_games[0] if direct_games else primary
            ai_condition = 'taste_subject_include_controls_purchase_family'

        alternatives = [key for key in base_candidates if key != primary]
        rows.append({
            'family_id': fid,
            'family_type': fam['family_type'],
            'taste_subject_key': taste_subject,
            'ai_condition': ai_condition,
            'requires_ai_base_support': fam.get('requires_ai_base_support', False),
            'base_appids': fam.get('base_appids', []),
            'primary_key': primary,
            'primary_title': feed[primary]['title'],
            'primary_final_kzt': store[primary]['final_kzt'],
            'primary_discount_percent': store[primary]['discount_percent'],
            'primary_discount_end_utc': store[primary]['discount_end_utc'],
            'primary_discount_end_europe_berlin': store[primary]['discount_end_europe_berlin'],
            'primary_selection_reason': selection_reason,
            'alternative_purchase_keys': alternatives,
            'addon_keys': addons,
            'all_member_keys': members,
            'relationship_evidence': fam['relationship_evidence'],
        })

    if len(assigned) != len(set(assigned)):
        raise SystemExit('Duplicate pre-AI family assignment')
    if set(assigned) != allowed_keys:
        raise SystemExit('Pre-AI family assignment does not cover exactly the allowed candidates')
    return rows


def compare_control(feed, store, meta, rules, contract):
    if not OLD_CONTROL.exists():
        return {'control_available': False}
    old = load(OLD_CONTROL)
    old_families = old.get('families') or []
    old_keys = {
        key
        for family in old_families
        for key in (family.get('all_member_keys') or [])
    }
    available = {
        key for key in old_keys
        if key in feed and key in rules and rules[key].get('mechanical_action') != 'exclude_before_ai_output'
    }
    complete_old = [
        family for family in old_families
        if set(family.get('all_member_keys') or []) <= available
    ]
    comparable_keys = {
        key for family in complete_old
        for key in (family.get('all_member_keys') or [])
    }
    projected = resolve(comparable_keys, feed, store, meta, rules, contract) if comparable_keys else []

    old_partition = sorted(
        [sorted(family.get('all_member_keys') or []) for family in complete_old]
    )
    new_partition = sorted(
        [sorted(family.get('all_member_keys') or []) for family in projected]
    )
    if old_partition != new_partition:
        raise SystemExit('Pre-AI family grouping differs from comparable validated control families')

    old_primary = {
        tuple(sorted(family.get('all_member_keys') or [])): family.get('primary_key')
        for family in complete_old
    }
    new_primary = {
        tuple(sorted(family.get('all_member_keys') or [])): family.get('primary_key')
        for family in projected
    }
    primary_changes = [
        {
            'members': list(members),
            'old_primary': old_primary[members],
            'current_primary': new_primary.get(members),
        }
        for members in old_primary
        if new_primary.get(members) != old_primary[members]
    ]
    return {
        'control_available': True,
        'control_family_count': len(old_families),
        'control_key_count': len(old_keys),
        'available_old_key_count': len(available),
        'comparable_complete_family_count': len(complete_old),
        'comparable_key_count': len(comparable_keys),
        'grouping_match_count': len(complete_old),
        'grouping_mismatch_count': 0,
        'grouping_match_ratio': 1.0 if complete_old else None,
        'primary_change_count_due_to_current_store_or_new_context': len(primary_changes),
        'primary_change_examples': primary_changes[:20],
    }


def main():
    started = time.monotonic()
    mailing = load(MAILING)
    store_doc = load(STORE)
    meta_doc = load(META)
    rules_doc = load(RULES)
    contract = load(CONTRACT)

    if store_doc.get('status') != 'complete' or meta_doc.get('status') != 'complete' or rules_doc.get('status') != 'complete':
        raise SystemExit('Pre-AI prerequisites incomplete')
    source_stamp = mailing.get('source_updated_at_utc')
    for label, doc in [('store', store_doc), ('metadata', meta_doc), ('rules', rules_doc)]:
        stamp = doc.get('discovery_source_updated_at_utc') if label == 'store' else doc.get('source_updated_at_utc')
        if stamp != source_stamp:
            raise SystemExit(f'{label} stale versus current mailing source')

    feed = load_feed(mailing)
    store = store_doc.get('entries') or {}
    meta = meta_doc.get('entries') or {}
    rules = rules_doc.get('rules') or {}
    if set(feed) != set(store) or set(feed) != set(meta) or set(feed) != set(rules):
        raise SystemExit('Pre-AI prerequisite keysets differ')

    allowed = {
        key for key, rule in rules.items()
        if rule.get('mechanical_action') in {'keep_for_ai', 'keep_for_ai_then_resolve_condition'}
    }
    excluded = set(feed) - allowed
    families = resolve(allowed, feed, store, meta, rules, contract)
    control = compare_control(feed, store, meta, rules, contract)
    assigned = {
        key for family in families
        for key in family['all_member_keys']
    }

    out = {
        'schema_version': 1,
        'purpose': 'pre_ai_purchase_family_graph',
        'status': 'complete',
        'source_path': 'data/production/mailing/index.json',
        'source_updated_at_utc': source_stamp,
        'source_item_count': len(feed),
        'mechanically_excluded_count': len(excluded),
        'family_candidate_item_count': len(allowed),
        'assigned_item_count': len(assigned),
        'family_count': len(families),
        'complete_coverage_of_nonexcluded_candidates': assigned == allowed,
        'taste_subject_count': len({family['taste_subject_key'] for family in families}),
        'family_type_counts': dict(sorted(__import__('collections').Counter(family['family_type'] for family in families).items())),
        'validated_control_comparison': control,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'families': families,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': out['status'],
        'source': out['source_item_count'],
        'mechanically_excluded': out['mechanically_excluded_count'],
        'family_candidates': out['family_candidate_item_count'],
        'families': out['family_count'],
        'taste_subjects': out['taste_subject_count'],
        'family_types': out['family_type_counts'],
        'control': out['validated_control_comparison'],
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

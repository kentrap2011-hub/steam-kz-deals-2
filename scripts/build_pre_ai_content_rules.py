import json
import re
import time
from collections import Counter
from pathlib import Path

POLICY = Path('config/mailing_policy.json')
CONTRACT = Path('config/content_eligibility_contract.json')
MAILING = Path('data/production/mailing/index.json')
METADATA = Path('data/production/pre_ai/content_metadata.json')
OLD_CONTROL = Path('data/cache/content_eligibility.validation.json')
OUT = Path('data/production/pre_ai/content_rules.json')


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


def compare_control(rules):
    if not OLD_CONTROL.exists():
        return {
            'control_available': False,
            'comparable_count': 0,
            'match_count': 0,
            'mismatch_count': 0,
            'match_ratio': None,
        }
    old = load(OLD_CONTROL)
    mismatches = []
    comparable = 0

    for row in old.get('eligible') or []:
        key = row.get('key')
        got = rules.get(key)
        if not key or not got:
            continue
        comparable += 1
        disposition = row.get('disposition')
        if disposition == 'game':
            ok = got.get('mechanical_kind') == 'game'
        elif disposition == 'addon_with_same_run_included_base':
            ok = (
                got.get('mechanical_kind') == 'dlc'
                and str(got.get('base_appid') or '') == str(row.get('base_appid') or '')
            )
        elif disposition == 'purchase_variant_for_included_family':
            related = {str(x) for x in (row.get('related_included_appids') or [])}
            package = {str(x) for x in (got.get('package_appids') or [])}
            ok = got.get('mechanical_kind') == 'package' and related <= package
        else:
            ok = False
        if not ok:
            mismatches.append({
                'key': key,
                'old_disposition': disposition,
                'new_rule': got,
            })

    for row in old.get('excluded') or []:
        key = row.get('key')
        got = rules.get(key)
        if not key or not got:
            continue
        comparable += 1
        if got.get('mechanical_action') != 'exclude_before_ai_output':
            mismatches.append({
                'key': key,
                'old_disposition': row.get('disposition'),
                'new_rule': got,
            })

    if mismatches:
        raise SystemExit(
            'Pre-AI content rules differ from validated control: '
            + json.dumps(mismatches[:20], ensure_ascii=False)
        )
    return {
        'control_available': True,
        'control_status': old.get('status'),
        'control_classified_count': old.get('classified_count'),
        'comparable_count': comparable,
        'match_count': comparable,
        'mismatch_count': 0,
        'match_ratio': 1.0 if comparable else None,
    }


def main():
    started = time.monotonic()
    policy = load(POLICY)
    contract = load(CONTRACT)
    mailing = load(MAILING)
    metadata = load(METADATA)

    if policy.get('status') != 'canonical':
        raise SystemExit('Policy not canonical')
    if contract.get('contract') != 'CONTENT-ELIGIBILITY-V1':
        raise SystemExit('Unexpected content contract')
    if metadata.get('status') != 'complete' or metadata.get('complete_coverage') is not True:
        raise SystemExit('Pre-AI content metadata incomplete')
    if metadata.get('source_updated_at_utc') != mailing.get('source_updated_at_utc'):
        raise SystemExit('Pre-AI metadata stale versus mailing source')

    feed = load_feed(mailing)
    meta = metadata.get('entries') or {}
    if set(meta) != set(feed):
        raise SystemExit('Pre-AI metadata does not cover exactly the mailing candidates')

    patterns = contract['obvious_non_game_title_patterns']
    obvious_extra_re = re.compile('|'.join(re.escape(p) for p in patterns), re.I)
    rules = {}
    counts = Counter()

    for key in sorted(feed):
        row = feed[key]
        m = meta[key]
        title = (m.get('store_name') or row['title'] or '').strip()
        entity_kind = m.get('entity_kind')
        app_type = m.get('app_type')

        common = {
            'key': key,
            'appid': row['appid'] or None,
            'title': title,
        }

        if obvious_extra_re.search(title):
            rule = {
                **common,
                'mechanical_kind': 'obvious_non_game_addon',
                'mechanical_action': 'exclude_before_ai_output',
                'canonical_reason_code': 'not_a_game_or_not_relevant_game_content',
                'ai_condition_after_self_taste_include': 'never_eligible',
            }
        elif entity_kind == 'sub':
            appids = sorted({
                str(app.get('appid'))
                for app in (m.get('package_apps') or [])
                if isinstance(app, dict) and app.get('appid') is not None
            })
            rule = {
                **common,
                'mechanical_kind': 'package',
                'mechanical_action': 'keep_for_ai_then_resolve_condition',
                'package_appids': appids,
                'representative_appid': row['appid'] or None,
                'ai_condition_after_self_taste_include': 'at_least_one_contained_or_representative_app_is_same_run_taste_include',
            }
        elif entity_kind == 'app' and app_type == 'game':
            rule = {
                **common,
                'mechanical_kind': 'game',
                'mechanical_action': 'keep_for_ai',
                'ai_condition_after_self_taste_include': 'eligible',
            }
        elif entity_kind == 'app' and app_type == 'dlc':
            rule = {
                **common,
                'mechanical_kind': 'dlc',
                'mechanical_action': 'keep_for_ai_then_resolve_condition',
                'base_appid': str(m.get('fullgame_appid') or '') or None,
                'ai_condition_after_self_taste_include': 'base_is_same_run_taste_include_or_profile_supports_base_or_content_is_proven_standalone_game_like',
            }
        elif entity_kind == 'app' and app_type in {'software', 'demo', 'mod', 'movie', 'guide', 'video', 'series', 'episode', 'hardware', 'music', 'beta', 'tool', 'advertising'}:
            rule = {
                **common,
                'mechanical_kind': app_type,
                'mechanical_action': 'exclude_before_ai_output',
                'canonical_reason_code': 'not_a_game_or_not_relevant_game_content',
                'ai_condition_after_self_taste_include': 'never_eligible',
            }
        else:
            rule = {
                **common,
                'mechanical_kind': 'unknown',
                'mechanical_action': 'fail_closed_unresolved',
                'entity_kind': entity_kind,
                'app_type': app_type,
                'ai_condition_after_self_taste_include': 'unresolved_type_requires_rule_update_not_freeform_guess',
            }

        rules[key] = rule
        counts[f"{rule['mechanical_action']}:{rule['mechanical_kind']}"] += 1

    unresolved = [k for k, r in rules.items() if r['mechanical_action'] == 'fail_closed_unresolved']
    if unresolved:
        raise SystemExit(f'Unresolved pre-AI content types: {unresolved[:20]}')

    control = compare_control(rules)
    out = {
        'schema_version': 1,
        'purpose': 'pre_ai_mechanical_content_rules_for_all_candidates',
        'status': 'complete',
        'source_path': 'data/production/mailing/index.json',
        'source_updated_at_utc': mailing.get('source_updated_at_utc'),
        'metadata_path': 'data/production/pre_ai/content_metadata.json',
        'source_item_count': len(feed),
        'rule_count': len(rules),
        'complete_coverage': len(rules) == len(feed),
        'unresolved_count': 0,
        'rule_counts': dict(sorted(counts.items())),
        'validated_control_comparison': control,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'rules': rules,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': out['status'],
        'source': out['source_item_count'],
        'rules': out['rule_count'],
        'unresolved': out['unresolved_count'],
        'rule_counts': out['rule_counts'],
        'control': out['validated_control_comparison'],
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

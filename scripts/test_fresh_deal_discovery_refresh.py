import tempfile
from datetime import date
from pathlib import Path

import build_pre_ai_store_snapshot as store_builder
from build_pre_ai_taste_projection import classify_cache_reuse
from steam_partial_publish_runner import load_core


PROBE_APPID = '1233570'
PROBE_KEY = f'App_{PROBE_APPID}'


def qualifying_probe(core, *, discount=90, price=450.0, review_count=50000):
    return {
        'key': PROBE_KEY,
        'appid': PROBE_APPID,
        'title': "Mirror's Edge Catalyst",
        'discount_percent': discount,
        'final_kzt': price,
        'tag_ids': [4106, 1697, 19, 21, 4182],
        'global_review_positive': 90.0,
        'global_review_count': review_count,
        'russian_review_positive': 90.0,
        'russian_review_count': 1000,
        'release_date': 'Jun 4, 2020',
    }


def selected_by_existing_rules(core, item):
    broad_reasons, fit_tags = core['broad_reasons'](item, date(2026, 10, 2))
    if not broad_reasons:
        return None
    broad = {
        **item,
        'fit_tags': fit_tags,
        'broad_reasons': broad_reasons,
    }
    refined_reasons, core_fit_count = core['refined_reasons'](broad)
    if not refined_reasons:
        return None
    return {
        'key': item['key'],
        'appid': item['appid'],
        'reasons': refined_reasons,
        'core_fit_count': core_fit_count,
    }


def test_01_fresh_catalog_can_introduce_game_absent_from_old_universe():
    core = load_core()
    old_catalog = {'App_1': {'key': 'App_1'}}
    fresh_catalog = dict(old_catalog)
    fresh_catalog[PROBE_KEY] = qualifying_probe(core)
    assert PROBE_KEY not in old_catalog
    assert selected_by_existing_rules(core, fresh_catalog[PROBE_KEY]) is not None


def test_02_price_only_refresh_cannot_discover_absent_identity():
    old_feed = {
        'App_1': {
            'key': 'App_1',
            'appid': '1',
            'title': 'Existing',
            'source_discount_percent': 50,
            'source_final_kzt': 1000.0,
        }
    }
    requested = store_builder.requested_ids(old_feed)
    assert all(str(spec.get('appid')) != PROBE_APPID for _, spec in requested)


def test_03_stale_price_only_store_shape_cannot_publish_current():
    import discovery_freshness
    legacy = {
        'status': 'complete',
        'observed_at_utc': '2026-10-01T18:15:33.903961+00:00',
        'discovery_source_updated_at_utc': '2026-09-23T23:12:47.031485+00:00',
    }
    try:
        discovery_freshness.require_store_snapshot_freshness(legacy)
    except ValueError:
        pass
    else:
        raise AssertionError('price-only legacy store snapshot must fail closed')


def test_04_new_game_still_must_pass_existing_shortlist_rules():
    core = load_core()
    weak = qualifying_probe(core, discount=5, price=450.0)
    assert selected_by_existing_rules(core, weak) is None


def test_05_no_active_discount_remains_excluded():
    row = {
        'key': PROBE_KEY,
        'appid': PROBE_APPID,
        'title': "Mirror's Edge Catalyst",
        'source_discount_percent': 90,
        'source_final_kzt': 450.0,
    }
    store_item = {
        'purchase_options': [{
            'packageid': 1,
            'purchase_option_name': 'Probe',
            'discount_pct': 0,
            'final_price_in_cents': 45000,
            'original_price_in_cents': 45000,
            'active_discounts': [],
        }]
    }
    option, reason = store_builder.choose_option(PROBE_KEY, row, store_item)
    assert option is None
    assert reason == 'no_active_discounted_purchase_option'


def exact_cache_entry():
    return {
        'appid': '1',
        'profile_blob_sha': 'profile',
        'taste_model_version': 'model',
        'taste_semantics_sha256': 'semantics',
        'candidate_context_sha256': 'context',
        'taste_fingerprint': 'fingerprint',
        'verdict': 'INCLUDE',
        'fit_level': 'strong',
        'reason_code': 'fit',
    }


def test_06_unchanged_candidate_preserves_exact_semantic_cache_binding():
    result = classify_cache_reuse(
        index_integrity_ok=True,
        cached=exact_cache_entry(),
        current={'appid': '1', 'taste_fingerprint': 'fingerprint'},
        candidate_context_sha256='context',
        profile_blob_sha='profile',
        taste_model_version='model',
        taste_semantics_sha256='semantics',
    )
    assert result['status'] == 'cache_hit'
    assert result['hit'] is True


def test_07_genuinely_new_candidate_is_pending_semantic_not_fabricated_fit():
    result = classify_cache_reuse(
        index_integrity_ok=True,
        cached=None,
        current={'appid': PROBE_APPID, 'taste_fingerprint': 'new-fingerprint'},
        candidate_context_sha256='new-context',
        profile_blob_sha='profile',
        taste_model_version='model',
        taste_semantics_sha256='semantics',
    )
    assert result['status'] == 'ai_required'
    assert result['ai_reason'] == 'taste_cache_key_missing'
    assert result['hit'] is False


def test_08_duplicate_candidate_identity_is_rejected_by_mailing_loader():
    original_index = store_builder.MAILING_INDEX
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            chunk = root / 'chunk_001.tsv'
            chunk.write_text(
                'App_1\t1\t50\t1000\tOne\n'
                'App_1\t1\t50\t1000\tOne duplicate\n',
                encoding='utf-8',
            )
            index = {
                'columns': ['key', 'appid', 'discount_percent', 'final_kzt', 'title'],
                'chunk_count': 1,
                'chunk_pattern': str(root / 'chunk_NNN.tsv'),
                'item_count': 2,
            }
            import json
            index_path = root / 'index.json'
            index_path.write_text(json.dumps(index), encoding='utf-8')
            store_builder.MAILING_INDEX = index_path
            try:
                store_builder.load_feed()
            except SystemExit as exc:
                assert 'Duplicate mailing key' in str(exc)
            else:
                raise AssertionError('duplicate identity must be rejected')
    finally:
        store_builder.MAILING_INDEX = original_index


def test_09_downstream_binding_uses_new_discovery_timestamp():
    import discovery_freshness
    source = '2026-10-02T20:20:00+00:00'
    manifest = {
        'updated_at_utc': source,
        'complete': True,
        'source_has_known_gaps': False,
        'shortlist_items': 2,
    }
    shortlist = {
        'source_updated_at_utc': source,
        'source_complete': True,
        'source_has_known_gaps': False,
        'item_count': 2,
    }
    mailing = {
        'source_updated_at_utc': source,
        'source_complete': True,
        'manifest_complete': True,
        'item_count': 2,
        'source_item_count': 2,
    }
    result = discovery_freshness.assess_discovery_freshness(
        manifest,
        shortlist,
        mailing,
        '2026-10-02T20:30:00+00:00',
    )
    assert result['fresh'] is True
    assert result['discovery_generated_at_utc'] == source
    assert result['source_binding']['source_chain_aligned'] is True


def test_10_probe_identity_is_not_special_cased_in_production_logic():
    production_paths = [
        Path('scripts/steam_production.py'),
        Path('scripts/steam_partial_publish_runner.py'),
        Path('scripts/build_pre_ai_store_snapshot.py'),
        Path('scripts/discovery_freshness.py'),
        Path('scripts/refresh_visual_commercial_fields.py'),
    ]
    for path in production_paths:
        text = path.read_text(encoding='utf-8')
        assert PROBE_APPID not in text
        assert "Mirror's Edge Catalyst" not in text



def test_11_canonical_search_is_bounded_to_supported_paid_content_types():
    core = load_core()
    params = core['search_params'](150, 'Name_ASC')
    assert params['specials'] == 1
    assert params['start'] == 150
    assert params['sort_by'] == 'Name_ASC'
    categories = set(str(params['category1']).split(','))
    assert categories == {'998', '21'}
    assert set(core['SEARCH_CATEGORY_TYPES']) == {'games', 'dlc'}
    assert '996' not in categories
    bundle_policy = core['PAID_DISCOVERY_POLICY']['bundle_package_discovery']
    assert bundle_policy['mode'] == 'embedded_in_games_partition'
    assert bundle_policy['standalone_category1_996_traversal'] is False



def test_12_publication_waits_for_current_cycle_mailing_and_pre_ai_state():
    steam_workflow = Path('.github/workflows/steam-test.yml').read_text(encoding='utf-8')
    mailing_workflow = Path('.github/workflows/build-mailing-feed.yml').read_text(encoding='utf-8')
    pre_ai_workflow = Path('.github/workflows/build-pre-ai-store-snapshot.yml').read_text(encoding='utf-8')
    visual_workflow = Path('.github/workflows/build-daily-visual-payload.yml').read_text(encoding='utf-8')

    # Steam discovery must not race visual publication before mailing has
    # rebuilt data/cache/store_state.json for the same discovery timestamp.
    assert 'gh workflow run build-daily-visual-payload.yml --ref main' not in steam_workflow
    assert '- "Steam KZ production shortlist"' in mailing_workflow
    assert '- "Build mailing-optimized feed"' in pre_ai_workflow
    assert '- "Build pre-AI deterministic payload"' in visual_workflow

def main():
    tests = [
        test_01_fresh_catalog_can_introduce_game_absent_from_old_universe,
        test_02_price_only_refresh_cannot_discover_absent_identity,
        test_03_stale_price_only_store_shape_cannot_publish_current,
        test_04_new_game_still_must_pass_existing_shortlist_rules,
        test_05_no_active_discount_remains_excluded,
        test_06_unchanged_candidate_preserves_exact_semantic_cache_binding,
        test_07_genuinely_new_candidate_is_pending_semantic_not_fabricated_fit,
        test_08_duplicate_candidate_identity_is_rejected_by_mailing_loader,
        test_09_downstream_binding_uses_new_discovery_timestamp,
        test_10_probe_identity_is_not_special_cased_in_production_logic,
        test_11_canonical_search_is_bounded_to_supported_paid_content_types,
        test_12_publication_waits_for_current_cycle_mailing_and_pre_ai_state,
    ]
    for test in tests:
        test()
        print(f'{test.__name__}: PASS')
    print(f'fresh deal discovery regressions: {len(tests)}/{len(tests)} PASS')


if __name__ == '__main__':
    main()

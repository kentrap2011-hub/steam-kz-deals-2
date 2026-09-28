import copy
import hashlib
import json
from datetime import timedelta
from pathlib import Path

import progressive_pass2


ROOT = Path('.')
CASES = [
    ('1170760', 'XIII - Classic', 2020, 2003),
    ('1237950', 'STAR WARS™ Battlefront™ II', 2020, 2017),
    ('1237970', 'Titanfall® 2', 2020, 2016),
    ('1237980', 'STAR WARS™ Battlefront', 2020, 2015),
    ('1238040', 'Dragon Age II: Ultimate Edition', 2020, 2011),
    ('1238060', 'Dead Space™ 3', 2020, 2013),
    ('1238820', 'Battlefield 3™', 2020, 2011),
    ('13500', 'Prince of Persia: Warrior Within™', 2009, 2004),
]


def load_current_record(appid):
    path = ROOT / f'data/cache/taste_steam_review_dossiers/App_{appid}.json'
    raw = path.read_bytes()
    return {
        'path': str(path).replace('\\', '/'),
        'content_sha256': hashlib.sha256(raw).hexdigest(),
        'doc': json.loads(raw.decode('utf-8')),
    }


def eligible(record, appid, title, store_year, *, current_binding=None, now=None):
    doc = record['doc']
    if current_binding is None:
        current_binding = doc['web_evidence_contract_binding']
    if now is None:
        generated = progressive_pass2.parse_utc(doc['generated_at_utc'])
        expires = progressive_pass2.parse_utc(doc['expires_at_utc'])
        candidate = generated + timedelta(days=1)
        now = candidate if candidate < expires else generated + timedelta(minutes=1)
    return progressive_pass2.dossier_is_eligible(
        binding={'appid': str(appid)},
        semantic_input={'title': title, 'release_year': store_year},
        dossier_record=record,
        current_binding=current_binding,
        now=now,
    )


def main():
    shared = json.loads((ROOT / 'config/dossier_deep_identity_compatibility_contract.json').read_text(encoding='utf-8'))
    dossier_contract = json.loads((ROOT / 'config/taste_steam_review_dossier_contract.json').read_text(encoding='utf-8'))
    pass2_contract = json.loads((ROOT / 'config/progressive_pass2_contract.json').read_text(encoding='utf-8'))
    assert shared['decision'] == 'PPD-011'
    assert shared['year_semantics']['dossier_game_identity_release_year']['canonical_meaning'] == 'original_or_work_release_year'
    assert shared['year_semantics']['progressive_semantic_input_release_year_or_release_date_year']['canonical_meaning'] == 'steam_storefront_release_date_year'
    assert shared['year_semantics']['cross_kind_exact_equality_required'] is False
    assert dossier_contract['cross_stage_identity_compatibility']['canonical_contract'] == 'config/dossier_deep_identity_compatibility_contract.json'
    assert pass2_contract['dossier_integration']['identity_compatibility']['canonical_contract'] == 'config/dossier_deep_identity_compatibility_contract.json'

    records = {}
    for appid, title, store_year, work_year in CASES:
        record = load_current_record(appid)
        records[appid] = record
        doc = record['doc']
        assert doc['appid'] == appid
        assert doc['title'] == title
        assert doc['game_identity']['work_title'] == title
        assert doc['game_identity']['release_year'] == work_year
        assert store_year != work_year
        ok, reason = eligible(record, appid, title, store_year)
        assert ok is True, (appid, reason)

    base = records['1170760']
    title = 'XIII - Classic'

    wrong_appid = copy.deepcopy(base)
    wrong_appid['doc']['appid'] = '999999'
    ok, reason = eligible(wrong_appid, '1170760', title, 2020)
    assert ok is False and reason == 'dossier_wrong_appid'

    wrong_title = copy.deepcopy(base)
    wrong_title['doc']['title'] = 'XIII Remastered'
    wrong_title['doc']['game_identity']['work_title'] = 'XIII Remastered'
    ok, reason = eligible(wrong_title, '1170760', title, 2020)
    assert ok is False and reason == 'dossier_wrong_work_title'

    unresolved = copy.deepcopy(base)
    unresolved['doc']['game_identity']['resolution_status'] = 'ambiguous'
    ok, reason = eligible(unresolved, '1170760', title, 2020)
    assert ok is False and reason == 'dossier_identity_unresolved_or_ambiguous'

    expired = copy.deepcopy(base)
    now = progressive_pass2.parse_utc(expired['doc']['expires_at_utc']) + timedelta(seconds=1)
    ok, reason = eligible(expired, '1170760', title, 2020, now=now)
    assert ok is False and reason == 'dossier_expired_or_missing_expiry'

    incompatible_binding = copy.deepcopy(base['doc']['web_evidence_contract_binding'])
    incompatible_binding['evidence_contract_sha256'] = '0' * 64
    ok, reason = eligible(base, '1170760', title, 2020, current_binding=incompatible_binding)
    assert ok is False and reason == 'dossier_compatibility_binding_mismatch'

    cross_product = records['1237950']
    ok, reason = eligible(cross_product, '1170760', title, 2020)
    assert ok is False and reason == 'dossier_wrong_appid'

    forged_corroborator = copy.deepcopy(base)
    forged_corroborator['doc']['game_identity']['corroborators'] = [
        {'kind': 'appid', 'value': '999999'}
    ]
    ok, reason = eligible(forged_corroborator, '1170760', title, 2020)
    assert ok is False and reason == 'dossier_identity_missing_exact_appid_corroborator'

    missing_identity_source = copy.deepcopy(base)
    missing_identity_source['doc']['game_identity']['identity_source_ids'] = ['source-999']
    ok, reason = eligible(missing_identity_source, '1170760', title, 2020)
    assert ok is False and reason == 'dossier_identity_evidence_missing_or_incompatible'

    print('DOSSIER_DEEP_RELEASE_YEAR_IDENTITY_COMPATIBILITY=PASS appids=' + ','.join(appid for appid, *_ in CASES))


if __name__ == '__main__':
    main()

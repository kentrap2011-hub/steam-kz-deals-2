"""Reconcile historical taste verdicts against exact current Steam mailing offers."""
def put_feed(feed, row):
    key = row.get('key')
    if not isinstance(key, str) or not (key.startswith('App_') or key.startswith('Sub_')):
        raise ValueError(f'Invalid offer key: {key!r}')
    if key in feed:
        raise ValueError(f'Duplicate offer key: {key}')
    appid = str(row.get('appid') or '')
    if not appid or (key.startswith('App_') and key[4:] != appid):
        raise ValueError(f'Offer/AppID mismatch: {key}')
    feed[key] = row

def current_includes(entries, feed):
    if not isinstance(entries, dict):
        raise ValueError('Taste entries malformed')
    all_includes = set()
    for key, entry in entries.items():
        if not isinstance(entry, list) or len(entry) != 5:
            raise ValueError(f'Invalid historical taste entry: {key}')
        if entry[2] != 'INCLUDE':
            continue
        all_includes.add(key)
        if key in feed and str(entry[0]) != str(feed[key]['appid']):
            raise ValueError(f'Taste/offer AppID mismatch: {key}')
    return sorted(all_includes & set(feed)), sorted(all_includes - set(feed))

def assert_family_inputs(elig, meta, feed, *, policy_sha, mailing_sha, metadata_sha):
    bindings = elig.get('bindings') or {}
    for key, expected in [('policy_blob_sha', policy_sha), ('mailing_tree_sha', mailing_sha),
                          ('content_metadata_blob_sha', metadata_sha)]:
        if not expected or bindings.get(key) != expected:
            raise ValueError(f'Stale eligibility source binding: {key}')
    if meta.get('mailing_tree_sha') != mailing_sha or meta.get('taste_index_blob_sha') != bindings.get('taste_index_blob_sha'):
        raise ValueError('Stale metadata source binding')
    if elig.get('status') != 'complete' or elig.get('complete_coverage') is not True or elig.get('unresolved_count') != 0:
        raise ValueError('Eligibility not complete')
    eligible, excluded = elig.get('eligible'), elig.get('excluded')
    if not isinstance(eligible, list) or not isinstance(excluded, list):
        raise ValueError('Eligibility rows malformed')
    rows = eligible + excluded
    keys = [r['key'] for r in rows]
    if len(set(keys)) != len(keys) or len(rows) != elig.get('input_taste_include_count') or len(rows) != elig.get('classified_count'):
        raise ValueError('Eligibility exact current-scope coverage mismatch')
    if len(eligible) != elig.get('eligible_count') or len(excluded) != elig.get('excluded_count'):
        raise ValueError('Eligibility section counts differ')
    meta_entries = meta.get('entries') or {}
    if (set(keys) != set(meta_entries) or meta.get('entry_count') != len(keys)
            or meta.get('required_include_count') != len(keys)):
        raise ValueError('Metadata exact current-scope coverage mismatch')
    missing = sorted(set(keys) - set(feed))
    if missing:
        raise ValueError(f'Current mailing feed missing eligible keys: {missing[:10]}')
    if any(str(r['appid']) != str(feed[r['key']]['appid']) for r in rows):
        raise ValueError('Eligibility/offer AppID mismatch')
    historical = elig.get('historical_taste_include_count')
    inactive = elig.get('out_of_current_feed_keys')
    if (not isinstance(inactive, list) or inactive != sorted(set(inactive)) or set(inactive) & set(keys)
        or historical != len(keys) + len(inactive) or elig.get('out_of_current_feed_count') != len(inactive)
        or meta.get('out_of_current_feed_keys') != inactive):
        raise ValueError('Historical/current offer-scope reconciliation missing or invalid')
    return set(r['key'] for r in eligible)

"""Git-attested Deep profile content dates: punctuation vs same-content commit."""
import hashlib
import json
from unittest.mock import patch

import progressive_profile_content_dates as dates

SRC = b'{"note":"hello."}'
OLD = b'{"note":"hello"}'
UPDATED_SHA = 'a' * 40
FIRST_CHANGE = 'b' * 40
PREVIOUS_SHA = 'c' * 40
IDENTICAL_LATER = 'd' * 40


def identity(commit=UPDATED_SHA, content=SRC):
    return {
        'repository': dates.REPOSITORY, 'path': dates.PATH,
        'resolved_commit_sha': commit,
        'blob_sha': dates._blob_sha(content),
        'content_sha256': hashlib.sha256(content).hexdigest(),
        'bytes': len(content),
    }


def fake_get(url):
    if '/commits?' in url:
        return json.dumps([{'sha': FIRST_CHANGE}]).encode()
    if '/commits/' + FIRST_CHANGE in url:
        return json.dumps({
            'sha': FIRST_CHANGE,
            'files': [{'filename': dates.PATH, 'sha': dates._blob_sha(SRC), 'status': 'modified'}],
            'parents': [{'sha': PREVIOUS_SHA}],
            'commit': {'committer': {'date': '2026-10-11T05:11:09Z'}},
        }).encode()
    if '/' + PREVIOUS_SHA + '/' in url:
        return OLD
    if '/' + UPDATED_SHA + '/' in url or '/' + IDENTICAL_LATER + '/' in url:
        return SRC
    raise AssertionError('unexpected Git URL: ' + url)


def main():
    assert dates._blob_sha(SRC) != dates._blob_sha(OLD)
    with patch.object(dates, '_get', side_effect=fake_get):
        dates._attested_date.cache_clear()
        expected = '2026-10-11T05:11:09Z'
        assert dates.profile_version_date(identity()) == expected
        # New commit changing wishlist only: SAME profile byte content.
        assert dates.profile_version_date(identity(IDENTICAL_LATER)) == expected
        # Punctuation is a different profile content version, not same bytes.
        punctuation_removed = identity(content=OLD)
        assert punctuation_removed['content_sha256'] != identity()['content_sha256']
        assert dates.profile_version_date(punctuation_removed) is None
        # Legacy without an exact pin cannot invent any timestamp.
        assert dates.historical_profile_date({'pin_sha256': 'pin-only'}) is None
        v = identity()
        historical = {'content_version_id': v['content_sha256'],
                      'content_sha256': v['content_sha256'],
                      'blob_sha': v['blob_sha'], 'source_commit_sha': v['resolved_commit_sha']}
        assert dates.historical_profile_date(historical) == expected
        # False attestation never falls back to commit/acceptance timestamps.
        mismatch = identity()
        mismatch['blob_sha'] = 'e' * 40
        assert dates.profile_version_date(mismatch) is None
        def broken(_url):
            raise OSError('offline')
        with patch.object(dates, '_get', side_effect=broken):
            dates._attested_date.cache_clear()
            assert dates.profile_version_date(identity()) is None
    print('Deep profile Git dates: source bytes/blob, commit-only churn, punctuation, null fallback: OK')


if __name__ == '__main__':
    main()

"""Fail-closed Git provenance for a pinned Taste profile content revision.

Source is READ-ONLY stopgame-ratings-data at an exact pinned Git commit.
A Git commit's time is NOT the last content-change time: use the most
recent path-changing ancestor and verify both that revision's blob and its
first parent's DIFFERENT blob.  Network, rate-limit or proof failures return
None; never replace unknown with publication or analysis timestamps.
"""
import hashlib
import json
import os
import re
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from datetime import datetime, timezone

REPOSITORY = 'kentrap2011-hub/stopgame-ratings-data'
PATH = 'gaming_taste_live.json'
HEX40 = re.compile(r'^[0-9a-f]{40}$')
HEX64 = re.compile(r'^[0-9a-f]{64}$')
MAX_RESPONSE = 2_000_000


def _get(url):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'steam-kz-deep-history-provenance'}
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    with urlopen(Request(url, headers=headers), timeout=5) as response:
        raw = response.read(MAX_RESPONSE + 1)
    if len(raw) > MAX_RESPONSE:
        raise ValueError('provenance source too large')
    return raw


def _blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\\0' + data).hexdigest()


def _source(commit):
    return ('https://raw.githubusercontent.com/' + REPOSITORY + '/'
            + quote(commit, safe='') + '/' + PATH)


def _api(path):
    return 'https://api.github.com/repos/' + REPOSITORY + '/' + path


@lru_cache(maxsize=64)
def _attested_date(commit, blob, digest, size):
    try:
        source = _get(_source(commit))
        if (hashlib.sha256(source).hexdigest() != digest or _blob_sha(source) != blob
                or (size is not None and len(source) != size)):
            return None
        url = _api('commits?sha=' + commit + '&path=' + PATH + '&per_page=1')
        changes = json.loads(_get(url))
        if not isinstance(changes, list) or not changes:
            return None
        revision_sha = changes[0].get('sha')
        if not isinstance(revision_sha, str) or not HEX40.fullmatch(revision_sha):
            return None
        revision = json.loads(_get(_api('commits/' + revision_sha)))
        if revision.get('sha') != revision_sha:
            return None
        affected = [f for f in revision.get('files') or []
                    if f.get('filename') == PATH and f.get('sha') == blob
                    and f.get('status') in ('added', 'modified')]
        if len(affected) != 1:
            return None
        parents = revision.get('parents') or []
        if parents:
            parent = parents[0].get('sha')
            if not isinstance(parent, str) or not HEX40.fullmatch(parent):
                return None
            try:
                previous = _get(_source(parent))
            except HTTPError as exc:
                if exc.code != 404:
                    raise
                previous = None
            if previous is not None and _blob_sha(previous) == blob:
                # No proven change at this commit, including a same-bytes touch.
                return None
        stamp = ((revision.get('commit') or {}).get('committer') or {}).get('date')
        if not isinstance(stamp, str):
            return None
        parsed = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    except (ValueError, TypeError, KeyError, TimeoutError, OSError, URLError,
            json.JSONDecodeError):
        return None


def profile_version_date(identity):
    """Only an exact pinned source triple (plus optional byte count) is eligible.

    Caller must supply the already canonical, pinned profile identity (not a
    historical guess derived from analysis/build time).
    """
    if not isinstance(identity, dict):
        return None
    if identity.get('repository') != REPOSITORY or identity.get('path') != PATH:
        return None
    commit = identity.get('resolved_commit_sha')
    blob = identity.get('blob_sha')
    digest = identity.get('content_sha256')
    if not all(isinstance(x, str) for x in (commit, blob, digest)):
        return None
    if not HEX40.fullmatch(commit) or not HEX40.fullmatch(blob) or not HEX64.fullmatch(digest):
        return None
    size = identity.get('bytes')
    if size is not None and (type(size) is not int or size < 1 or size > MAX_RESPONSE):
        return None
    return _attested_date(commit, blob, digest, size)


def historical_profile_date(version):
    """Legacy revisions without a V1 pin cannot acquire an invented date."""
    if not isinstance(version, dict) or not version.get('content_version_id'):
        return None
    return profile_version_date({
        'repository': REPOSITORY, 'path': PATH,
        'resolved_commit_sha': version.get('source_commit_sha'),
        'blob_sha': version.get('blob_sha'),
        'content_sha256': version.get('content_sha256'),
    })

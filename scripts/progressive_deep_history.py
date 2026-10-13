"""Immutable, per-game completed Deep history; never an authority for current scoring.

Only canonically accepted Deep completions are snapshots.  Older V2 root and
revision_history data are read without rewriting their original provenance.
A missing historic profile-content pin/date is recorded as unknown, never
guessed from the latest profile or a publication timestamp.
"""
import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone

HISTORY_CONTRACT = 'PROGRESSIVE-DEEP-COMPLETED-HISTORY-V1'
COMPLETE = {'analyzed_fit', 'analyzed_not_fit'}
SNAPSHOT_EXCLUDE = {
    'completed_versions', 'revision_history', 'history_contract',
}


def _sha(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def _instant(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(timezone.utc)


def content_profile_version(profile_pin, work_item):
    """Only an exact immutable profile pin is allowed to name a content version."""
    if not isinstance(profile_pin, dict) or not isinstance(work_item, dict):
        return None
    if profile_pin.get('contract') != 'PROGRESSIVE-PROFILE-PIN-V1':
        return None
    if profile_pin.get('pin_sha256') != work_item.get('profile_pin_sha256'):
        return None
    identity = profile_pin.get('profile_identity') or {}
    if identity.get('repository') != 'kentrap2011-hub/stopgame-ratings-data':
        return None
    if identity.get('path') != 'gaming_taste_live.json':
        return None
    if not isinstance(identity.get('content_sha256'), str) or len(identity['content_sha256']) != 64:
        return None
    if not isinstance(identity.get('blob_sha'), str) or len(identity['blob_sha']) != 40:
        return None
    if not isinstance(identity.get('resolved_commit_sha'), str) or len(identity['resolved_commit_sha']) != 40:
        return None
    # A Git commit date is NOT supplied by PROGRESSIVE-PROFILE-PIN-V1.
    # Do not substitute analysis or projection time for the profile-change date.
    return {
        'content_version_id': identity['content_sha256'],
        'content_sha256': identity['content_sha256'],
        'blob_sha': identity['blob_sha'],
        'source_commit_sha': identity['resolved_commit_sha'],
        'source_commit_at_utc': None,
        'pin_sha256': profile_pin['pin_sha256'],
    }


def _record(snapshot, profile=None):
    if not isinstance(snapshot, dict):
        return None
    if snapshot.get('authoritative_completed') is not True or snapshot.get('outcome') not in COMPLETE:
        return None
    accepted = snapshot.get('accepted_at_utc')
    if _instant(accepted) is None:
        # Without a real accepted timestamp there is no dateable success.
        return None
    exact = {k: deepcopy(v) for k, v in snapshot.items() if k not in SNAPSHOT_EXCLUDE}
    identity = {
        'family_id': exact.get('family_id'),
        'taste_subject_key': exact.get('taste_subject_key'),
        'appid': exact.get('appid'),
        'work_id': exact.get('work_id'),
        'authorization_id': exact.get('authorization_id'),
        'accepted_at_utc': accepted,
        'outcome': exact.get('outcome'),
    }
    return {
        'history_contract': HISTORY_CONTRACT,
        'revision_id': _sha(identity),
        'accepted_at_utc': accepted,
        'profile_version': deepcopy(profile) if isinstance(profile, dict) else {
            'content_version_id': None,
            'pin_sha256': exact.get('profile_pin_sha256'),
            'source_commit_at_utc': None,
            'provenance_status': 'legacy_profile_pin_not_attested',
        },
        'result': exact,
    }


def completed_versions(entry):
    """Read V1 history plus legacy V2 root/revision snapshots; stable dedup."""
    if not isinstance(entry, dict):
        return []
    versions = {}
    for row in entry.get('completed_versions') or []:
        if not isinstance(row, dict) or row.get('history_contract') != HISTORY_CONTRACT:
            raise ValueError('invalid Deep completed history contract')
        actual = _record(row.get('result'), row.get('profile_version'))
        if actual is None or actual['revision_id'] != row.get('revision_id'):
            raise ValueError('corrupt Deep completed history revision')
        versions[actual['revision_id']] = deepcopy(row)
    for revision in entry.get('revision_history') or []:
        if not isinstance(revision, dict):
            continue
        candidate = _record(revision.get('state'))
        if candidate is not None:
            versions.setdefault(candidate['revision_id'], candidate)
    active = _record(entry)
    if active is not None:
        versions.setdefault(active['revision_id'], active)
    return sorted(versions.values(), key=lambda v: (_instant(v['accepted_at_utc']), v['revision_id']))


def preserve_completion(previous, updated, work_item, attempt, profile_pin=None):
    """Attach all older successful revisions even across a semantic-generation reset."""
    versions = {v['revision_id']: v for v in completed_versions(previous)}
    # Migration may have appended a pre-migration snapshot on the updated root.
    for v in completed_versions(updated):
        versions.setdefault(v['revision_id'], v)
    if attempt.get('outcome') in COMPLETE:
        current = _record(updated, content_profile_version(profile_pin, work_item))
        if current is None:
            raise ValueError('accepted Deep completion needs a timestamp and canonical state')
        versions[current['revision_id']] = current
    updated['history_contract'] = HISTORY_CONTRACT
    updated['completed_versions'] = sorted(
        versions.values(), key=lambda v: (_instant(v['accepted_at_utc']), v['revision_id'])
    )
    return updated


def latest_completed(state_doc, family_id, binding=None):
    entry = ((state_doc or {}).get('entries') or {}).get(str(family_id))
    candidates = completed_versions(entry)
    if isinstance(binding, dict):
        candidates = [
            v for v in candidates
            if all(str(v['result'].get(k) or '') == str(binding.get(k) or '')
                   and str(binding.get(k) or '')
                   for k in ('family_id', 'taste_subject_key', 'appid'))
        ]
    return deepcopy(candidates[-1]) if candidates else None


def version_counts(state_doc, current_bindings, current_profile_content_sha256, current_authoritative_families=None):
    """Unique-game totals; migrations overlap by game and must not be added."""
    per_version = {}
    current = older_only = never = 0
    current_authoritative_families = set(current_authoritative_families or [])
    same_profile_historical = 0
    for family_id, binding in current_bindings.items():
        entry = ((state_doc or {}).get('entries') or {}).get(str(family_id))
        revisions = [
            v for v in completed_versions(entry)
            if all(str(v['result'].get(k) or '') == str(binding.get(k) or '')
                   and str(binding.get(k) or '')
                   for k in ('family_id', 'taste_subject_key', 'appid'))
        ]
        versions_for_game = set()
        for revision in revisions:
            profile = revision['profile_version']
            name = profile.get('content_version_id')
            if not name:
                # Legacy data has a real completion but no attested content SHA.
                name = 'legacy-unverified:' + str(profile.get('pin_sha256') or 'unknown')
            versions_for_game.add(name)
        for name in versions_for_game:
            per_version[name] = per_version.get(name, 0) + 1
        if current_profile_content_sha256 in versions_for_game:
            same_profile_historical += 1
        if family_id in current_authoritative_families:
            current += 1
        elif revisions:
            older_only += 1
        else:
            never += 1
    target = len(current_bindings)
    return {
        'deep_history_contract': HISTORY_CONTRACT,
        'deep_profile_version_unique_game_counts': dict(sorted(per_version.items())),
        'deep_current_profile_content_version_id': current_profile_content_sha256,
        'deep_current_version_target': target,
        'deep_current_version_completed_count': current,
        'deep_same_profile_historical_completed_count': same_profile_historical,
        'deep_historical_only_not_current_compatible_count': older_only,
        'deep_older_version_only_count': older_only,
        'deep_never_completed_count': never,
        'deep_current_version_remaining_count': target - current,
    }

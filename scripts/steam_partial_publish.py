from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
DEFAULT_FAILURE_PATH = Path('data/cache/steam_partial_publish_failures.json')


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def default_run_ref():
    run_id = os.environ.get('GITHUB_RUN_ID')
    run_attempt = os.environ.get('GITHUB_RUN_ATTEMPT')
    if run_id:
        return f'github:{run_id}:{run_attempt or "1"}'
    return f'local:{utc_now_iso()}'


def _error_text(error):
    text = str(error).strip() or error.__class__.__name__
    return text[:2000]


def _empty_state():
    return {
        'schema_version': SCHEMA_VERSION,
        'updated_at_utc': None,
        'unresolved_games': {},
        'unresolved_catalog_segments': {},
        'system_problems': [],
    }


def source_coverage_metadata(failed_segment_count):
    failed_segment_count = int(failed_segment_count or 0)
    has_gaps = failed_segment_count > 0
    return {
        'source_complete': not has_gaps,
        'source_has_known_gaps': has_gaps,
        'known_gap_count': failed_segment_count,
        'source_status': 'partial' if has_gaps else 'complete',
    }


class FailureQueue:
    def __init__(self, path=DEFAULT_FAILURE_PATH, run_ref=None, now_fn=utc_now_iso):
        self.path = Path(path)
        self.run_ref = run_ref or default_run_ref()
        self.now_fn = now_fn
        self.load_incident = None
        self.state = self._load()
        self.failed_game_keys_this_run = set()
        self.failed_segment_ids_this_run = set()

    def _validated_payload(self, payload):
        if not isinstance(payload, dict):
            raise ValueError('failure queue root is not an object')
        if payload.get('schema_version') != SCHEMA_VERSION:
            raise ValueError(
                'unsupported failure queue schema_version='
                f'{payload.get("schema_version")!r}'
            )
        if not isinstance(payload.get('unresolved_games'), dict):
            raise ValueError('unresolved_games is not an object')
        if not isinstance(payload.get('unresolved_catalog_segments'), dict):
            raise ValueError('unresolved_catalog_segments is not an object')
        system_problems = payload.get('system_problems')
        if system_problems is None:
            payload['system_problems'] = []
        elif not isinstance(system_problems, list):
            raise ValueError('system_problems is not an array')
        return payload

    def _quarantine_path(self):
        stamp = self.now_fn().replace(':', '-').replace('+', '_')
        quarantine_dir = self.path.parent / f'{self.path.stem}_quarantine'
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        candidate = quarantine_dir / f'{self.path.name}.corrupt.{stamp}'
        suffix = 1
        while candidate.exists():
            candidate = quarantine_dir / f'{self.path.name}.corrupt.{stamp}.{suffix}'
            suffix += 1
        return candidate

    def _recover_unreadable_state(self, error):
        original_path = str(self.path)
        quarantined_path = None
        if self.path.exists():
            target = self._quarantine_path()
            try:
                self.path.replace(target)
            except Exception as quarantine_error:
                raise RuntimeError(
                    'Failure queue is unreadable and could not be quarantined; '
                    'refusing to overwrite active path. '
                    f'load_error={_error_text(error)}; '
                    f'quarantine_error={_error_text(quarantine_error)}'
                ) from quarantine_error
            quarantined_path = str(target)

        now = self.now_fn()
        problem = {
            'problem_type': 'failure_queue_unreadable',
            'failed_stage': 'failure_queue_load',
            'root_error': _error_text(error),
            'original_path': original_path,
            'quarantined_path': quarantined_path,
            'run_ref': self.run_ref,
            'first_seen_at_utc': now,
            'last_seen_at_utc': now,
            'requires_manual_disposition': True,
        }
        state = _empty_state()
        state['system_problems'].append(problem)
        self.load_incident = problem
        return state

    def _load(self):
        try:
            text = self.path.read_text(encoding='utf-8')
        except FileNotFoundError:
            return _empty_state()
        except Exception as exc:
            return self._recover_unreadable_state(exc)

        try:
            payload = json.loads(text)
            return self._validated_payload(payload)
        except Exception as exc:
            return self._recover_unreadable_state(exc)

    def record_game(self, key, *, appid=None, name=None, stage, error, prior_site_data_exists=False):
        key = str(key or '').strip()
        if not key:
            return
        now = self.now_fn()
        games = self.state['unresolved_games']
        old = games.get(key) if isinstance(games.get(key), dict) else {}
        games[key] = {
            'key': key,
            'appid': str(appid) if appid not in (None, '') else old.get('appid'),
            'name': name or old.get('name'),
            'failed_stage': stage,
            'root_error': _error_text(error),
            'first_seen_at_utc': old.get('first_seen_at_utc') or now,
            'last_seen_at_utc': now,
            'first_run_ref': old.get('first_run_ref') or self.run_ref,
            'last_run_ref': self.run_ref,
            'attempts': int(old.get('attempts') or 0) + 1,
            'prior_site_data_exists': bool(prior_site_data_exists or old.get('prior_site_data_exists')),
        }
        self.failed_game_keys_this_run.add(key)

    def resolve_games(self, keys):
        games = self.state['unresolved_games']
        for key in set(map(str, keys)):
            if key not in self.failed_game_keys_this_run:
                games.pop(key, None)

    @staticmethod
    def segment_id(sort_by, start, count):
        return f'{sort_by}:start={int(start)}:count={int(count)}'

    def record_segment(self, *, sort_by, start, count, error):
        segment_id = self.segment_id(sort_by, start, count)
        now = self.now_fn()
        segments = self.state['unresolved_catalog_segments']
        old = segments.get(segment_id) if isinstance(segments.get(segment_id), dict) else {}
        segments[segment_id] = {
            'segment_id': segment_id,
            'request': {'sort_by': sort_by, 'start': int(start), 'count': int(count)},
            'failed_stage': 'catalog_segment_fetch',
            'root_error': _error_text(error),
            'first_seen_at_utc': old.get('first_seen_at_utc') or now,
            'last_seen_at_utc': now,
            'first_run_ref': old.get('first_run_ref') or self.run_ref,
            'last_run_ref': self.run_ref,
            'attempts': int(old.get('attempts') or 0) + 1,
        }
        self.failed_segment_ids_this_run.add(segment_id)
        return segment_id

    def resolve_segment(self, *, sort_by, start, count):
        segment_id = self.segment_id(sort_by, start, count)
        if segment_id not in self.failed_segment_ids_this_run:
            self.state['unresolved_catalog_segments'].pop(segment_id, None)

    def summary(self, successful_games):
        return {
            'processed_successfully': int(successful_games),
            'problematic_games': len(self.state['unresolved_games']),
            'problematic_catalog_segments': len(self.state['unresolved_catalog_segments']),
            'problematic_system_state': len(self.state['system_problems']),
            'game_failures_this_run': len(self.failed_game_keys_this_run),
            'catalog_segment_failures_this_run': len(self.failed_segment_ids_this_run),
            'failure_queue_recovery_this_run': self.load_incident is not None,
        }

    def write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.state['updated_at_utc'] = self.now_fn()
        tmp = self.path.with_suffix(self.path.suffix + '.tmp')
        tmp.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2, sort_keys=True),
            encoding='utf-8',
        )
        tmp.replace(self.path)


def catalog_run_is_publishable(*, reached_end, unique_count, reported_total):
    # Live Steam totals can move while pagination is in progress. A difference is
    # diagnostic only; the unique rows actually observed are the processing scope.
    del unique_count, reported_total
    return bool(reached_end)


def preserve_last_known_good(current_rows, previous_by_key, failed_keys):
    by_key = {str(row.get('key')): dict(row) for row in current_rows if row.get('key')}
    preserved = []
    for key in sorted(set(map(str, failed_keys))):
        if key in by_key:
            continue
        previous = previous_by_key.get(key)
        if previous:
            copy = dict(previous)
            by_key[key] = copy
            preserved.append(key)
    return list(by_key.values()), preserved


def process_individual_items(items, processor, previous_by_key=None):
    """Small deterministic primitive used by tests and bounded per-game stages."""
    previous_by_key = previous_by_key or {}
    successful = []
    failures = {}
    for item in items:
        key = str(item.get('key') or '')
        try:
            successful.append(processor(item))
        except Exception as exc:
            failures[key] = _error_text(exc)
    merged, preserved = preserve_last_known_good(successful, previous_by_key, failures)
    return {'rows': merged, 'failure_reasons': failures, 'preserved_keys': preserved}


def fetch_segments_resilient(segments, fetcher):
    """Return successes and exact failed segment descriptors without stopping."""
    successful = []
    failed = []
    for segment in segments:
        try:
            successful.append((segment, fetcher(segment)))
        except Exception as exc:
            failed.append((segment, _error_text(exc)))
    return successful, failed


def load_previous_shortlist(root=Path('data/production/shortlist')):
    root = Path(root)
    index_path = root / 'index.json'
    try:
        index = json.loads(index_path.read_text(encoding='utf-8'))
    except Exception:
        return {}, []
    columns = list(index.get('columns') or [])
    chunk_count = int(index.get('chunk_count') or 0)
    pattern = str(index.get('chunk_pattern') or '')
    result = {}
    for number in range(1, chunk_count + 1):
        if pattern:
            rel = pattern.replace('NNN', f'{number:03d}')
            path = Path(rel)
        else:
            path = root / f'chunk_{number:03d}.tsv'
        if not path.exists():
            continue
        for line in path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            cells = line.split('\t')
            if len(cells) != len(columns):
                continue
            row = dict(zip(columns, cells))
            for name in ('discount_percent', 'review_count', 'global_review_count', 'russian_review_count', 'core_fit_count'):
                if row.get(name) != '':
                    try:
                        row[name] = int(float(row[name]))
                    except Exception:
                        pass
            for name in ('final_kzt', 'review_positive', 'global_review_positive', 'russian_review_positive'):
                if row.get(name) != '':
                    try:
                        row[name] = float(row[name])
                    except Exception:
                        pass
            for name in ('reasons', 'fit_tags'):
                if isinstance(row.get(name), str):
                    row[name] = [part for part in row[name].split('|') if part]
            key = row.get('key')
            if key:
                result[str(key)] = row
    return result, columns

#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib import error, parse, request

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / 'config/duration_enrichment_contract.json'
PURCHASE_CONTEXT_PATH = ROOT / 'data/production/pre_ai/chatgpt_purchase_context.jsonl'
CACHE_PATH = ROOT / 'data/cache/duration_estimates.json'

CLIENT_ID_ENV = 'IGDB_CLIENT_ID'
CLIENT_SECRET_ENV = 'IGDB_CLIENT_SECRET'
TRANSIENT_RETRY_MINUTES = 60
QUERY_BATCH_SIZE = 100


class DurationEnrichmentError(RuntimeError):
    pass


class AuthError(DurationEnrichmentError):
    pass


class TransportError(DurationEnrichmentError):
    pass


def utc_now():
    return datetime.now(timezone.utc)


def iso_utc(dt):
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def parse_utc(value):
    if not value:
        return None
    try:
        text = str(value).strip().replace('Z', '+00:00')
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def load_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def empty_cache(contract):
    return {
        'schema_version': int(contract['canonical_cache']['container_schema_version']),
        'contract': contract['contract'],
        'provider': contract['authority']['primary_provider'],
        'updated_at_utc': None,
        'scope': {
            'required_appid_count': 0,
            'required_appids_sha256': None,
        },
        'entries': {},
    }


def load_cache(path, contract):
    path = Path(path)
    if not path.exists():
        return empty_cache(contract)
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError('duration cache must be a JSON object')
    if data.get('schema_version') != contract['canonical_cache']['container_schema_version']:
        raise ValueError('duration cache schema_version mismatch')
    entries = data.get('entries')
    if entries is None:
        data['entries'] = {}
    elif not isinstance(entries, dict):
        raise ValueError('duration cache entries must be an object')
    return data


def canonical_appid(value):
    text = str(value or '').strip()
    if not text.isdecimal() or int(text) <= 0:
        return None
    return str(int(text))


def required_appids_from_purchase_context(rows):
    required = set()
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        semantic = row.get('semantic_condition') or {}
        for raw in semantic.get('base_appids') or []:
            appid = canonical_appid(raw)
            if appid:
                required.add(appid)
    return sorted(required, key=int)


def appid_scope_sha256(appids):
    payload = '\n'.join(appids).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def is_due(entry, now):
    if not isinstance(entry, dict):
        return True
    refresh_after = parse_utc(entry.get('refresh_after_utc'))
    return refresh_after is None or refresh_after <= now


def due_appids(required_appids, entries, now):
    return [appid for appid in required_appids if is_due(entries.get(appid), now)]


def chunked(values, size=QUERY_BATCH_SIZE):
    for index in range(0, len(values), size):
        yield values[index:index + size]


def build_external_game_sources_query():
    return 'fields id,name; limit 500;'


def build_external_games_query(appids, steam_source_id):
    clean = [canonical_appid(x) for x in appids]
    if any(x is None for x in clean) or not clean:
        raise ValueError('external game query requires positive Steam appids')
    quoted = ','.join(json.dumps(x) for x in clean)
    return (
        'fields game,uid,external_game_source; '
        f'where external_game_source = {int(steam_source_id)} & uid = ({quoted}); '
        'limit 500;'
    )


def build_time_to_beat_query(game_ids):
    clean = []
    for value in game_ids:
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError('game_time_to_beats query requires positive IGDB game ids')
        clean.append(value)
    if not clean:
        raise ValueError('game_time_to_beats query requires at least one IGDB game id')
    ids = ','.join(str(x) for x in clean)
    return (
        'fields checksum,completely,count,created_at,game_id,hastily,normally,updated_at; '
        f'where game_id = ({ids}); limit 500;'
    )


class IgdbClient:
    def __init__(self, client_id, client_secret, api_base_url='https://api.igdb.com/v4', min_interval_seconds=0.26, timeout=30):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_base_url = api_base_url.rstrip('/')
        self.min_interval_seconds = min_interval_seconds
        self.timeout = timeout
        self.access_token = None
        self._last_api_started = None

    def authenticate(self):
        params = parse.urlencode({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        })
        req = request.Request(
            f'https://id.twitch.tv/oauth2/token?{params}',
            data=b'',
            method='POST',
            headers={'Accept': 'application/json'},
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode('utf-8'))
        except error.HTTPError as exc:
            raise AuthError(f'OAuth HTTP {exc.code}') from exc
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise AuthError(f'OAuth transport/response failure: {type(exc).__name__}') from exc
        token = payload.get('access_token') if isinstance(payload, dict) else None
        if not token:
            raise AuthError('OAuth response did not contain access_token')
        self.access_token = str(token)
        return self.access_token

    def _pace(self):
        now = time.monotonic()
        if self._last_api_started is not None:
            delay = self.min_interval_seconds - (now - self._last_api_started)
            if delay > 0:
                time.sleep(delay)
        self._last_api_started = time.monotonic()

    def api_post(self, endpoint, body, attempts=3):
        if not self.access_token:
            raise AuthError('IGDB access token is not initialized')
        last_error = None
        for attempt in range(1, attempts + 1):
            self._pace()
            req = request.Request(
                f'{self.api_base_url}/{endpoint.lstrip("/")}',
                data=body.encode('utf-8'),
                method='POST',
                headers={
                    'Accept': 'application/json',
                    'Client-ID': self.client_id,
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'text/plain',
                },
            )
            try:
                with request.urlopen(req, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode('utf-8'))
                if not isinstance(payload, list):
                    raise TransportError(f'IGDB {endpoint} returned non-list JSON')
                return payload
            except error.HTTPError as exc:
                if exc.code in {401, 403}:
                    raise AuthError(f'IGDB {endpoint} HTTP {exc.code}') from exc
                last_error = exc
                if exc.code != 429 and not (500 <= exc.code < 600):
                    raise TransportError(f'IGDB {endpoint} HTTP {exc.code}') from exc
            except (error.URLError, TimeoutError, json.JSONDecodeError, TransportError) as exc:
                last_error = exc
            if attempt < attempts:
                time.sleep(attempt)
        raise TransportError(f'IGDB {endpoint} failed after {attempts} attempts: {type(last_error).__name__}')


def resolve_steam_source_id(rows):
    matches = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        if str(row.get('name') or '').strip().casefold() != 'steam':
            continue
        value = row.get('id')
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            matches.append(value)
    matches = sorted(set(matches))
    if len(matches) != 1:
        raise ValueError(f'expected exactly one current IGDB External Game Source named Steam, got {matches}')
    return matches[0]


def classify_external_game_mappings(appids, rows, steam_source_id):
    requested = set(appids)
    game_ids_by_appid = {appid: set() for appid in appids}
    saw_invalid = set()
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        uid = canonical_appid(row.get('uid'))
        if uid not in requested:
            continue
        if row.get('external_game_source') != steam_source_id:
            saw_invalid.add(uid)
            continue
        game_id = row.get('game')
        if not isinstance(game_id, int) or isinstance(game_id, bool) or game_id <= 0:
            saw_invalid.add(uid)
            continue
        game_ids_by_appid[uid].add(game_id)

    result = {}
    for appid in appids:
        game_ids = sorted(game_ids_by_appid[appid])
        if len(game_ids) == 1 and appid not in saw_invalid:
            result[appid] = {'status': 'mapped', 'igdb_game_id': game_ids[0]}
        elif len(game_ids) > 1:
            result[appid] = {'status': 'steam_mapping_ambiguous'}
        elif appid in saw_invalid:
            result[appid] = {'status': 'invalid_values'}
        else:
            result[appid] = {'status': 'steam_mapping_missing'}
    return result


def duration_rows_by_game_id(rows):
    grouped = {}
    invalid_game_ids = set()
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        game_id = row.get('game_id')
        if not isinstance(game_id, int) or isinstance(game_id, bool) or game_id <= 0:
            continue
        grouped.setdefault(game_id, []).append(row)
    result = {}
    for game_id, candidates in grouped.items():
        if len(candidates) != 1:
            invalid_game_ids.add(game_id)
            continue
        result[game_id] = candidates[0]
    return result, invalid_game_ids


def valid_nonnegative_int_or_none(value):
    return value is None or (isinstance(value, int) and not isinstance(value, bool) and value >= 0)


def normalize_confirmed_entry(appid, mapping, duration_row, steam_source_id, fetched_at, contract):
    for field in ('hastily', 'normally', 'completely', 'count'):
        if not valid_nonnegative_int_or_none(duration_row.get(field)):
            return None
    normally = duration_row.get('normally')
    if not isinstance(normally, int) or isinstance(normally, bool) or normally <= 0:
        return None
    game_id = mapping.get('igdb_game_id')
    if duration_row.get('game_id') != game_id:
        return None

    divisor = float(contract['normalization']['conversion_divisor'])
    hours = float(normally) / divisor
    stale_days = int(contract['freshness']['confirmed_soft_stale_after_days'])
    raw = {
        'provider': 'igdb',
        'provider_schema': 'game_time_to_beats',
        'steam_appid': appid,
        'igdb_game_id': game_id,
        'steam_external_game_uid': appid,
        'steam_external_game_source_id': steam_source_id,
        'hastily_seconds': duration_row.get('hastily'),
        'normally_seconds': normally,
        'completely_seconds': duration_row.get('completely'),
        'count': duration_row.get('count'),
        'fetched_at_utc': iso_utc(fetched_at),
    }
    for field in ('created_at', 'updated_at', 'checksum'):
        if duration_row.get(field) is not None:
            raw[field] = duration_row.get(field)

    return {
        'steam_appid': appid,
        'status': 'confirmed',
        'provider': 'igdb',
        'provider_schema': 'game_time_to_beats',
        'fetched_at_utc': iso_utc(fetched_at),
        'refresh_after_utc': iso_utc(fetched_at + timedelta(days=stale_days)),
        'igdb_game_id': game_id,
        'steam_external_game_uid': appid,
        'steam_external_game_source_id': steam_source_id,
        'raw': raw,
        'selected_metric': contract['normalization']['selected_metric'],
        'estimated_duration_hours': hours,
    }


def unresolved_entry(appid, status, fetched_at, contract, detail=None):
    durable = set(contract['canonical_cache']['entry_schema']['durable_unresolved_statuses'])
    transient = set(contract['canonical_cache']['entry_schema']['transient_error_statuses'])
    if status in durable:
        refresh = fetched_at + timedelta(days=int(contract['freshness']['durable_unresolved_retry_after_days']))
    elif status in transient:
        refresh = fetched_at + timedelta(minutes=TRANSIENT_RETRY_MINUTES)
    else:
        raise ValueError(f'unsupported duration cache status: {status}')
    row = {
        'steam_appid': appid,
        'status': status,
        'provider': 'igdb',
        'provider_schema': 'game_time_to_beats',
        'fetched_at_utc': iso_utc(fetched_at),
        'refresh_after_utc': iso_utc(refresh),
    }
    if detail:
        row['detail'] = str(detail)[:300]
    return row


def merge_entry(existing, incoming, now=None):
    if not isinstance(existing, dict):
        return incoming
    status = incoming.get('status')
    if status in {'auth_failure', 'transport_failure'}:
        if existing.get('status') in {
            'confirmed',
            'provider_row_missing',
            'steam_mapping_missing',
            'steam_mapping_ambiguous',
            'invalid_values',
        }:
            merged = dict(existing)
            merged['last_attempt_at_utc'] = incoming.get('fetched_at_utc') or iso_utc(now or utc_now())
            merged['last_attempt_status'] = status
            if incoming.get('detail'):
                merged['last_attempt_detail'] = incoming['detail']
            return merged
    return incoming


def validate_confirmed_cache_entry(entry):
    if not isinstance(entry, dict) or entry.get('status') != 'confirmed':
        return False
    appid = canonical_appid(entry.get('steam_appid'))
    if not appid:
        return False
    if entry.get('provider') != 'igdb' or entry.get('provider_schema') != 'game_time_to_beats':
        return False
    if entry.get('selected_metric') != 'normally':
        return False
    hours = entry.get('estimated_duration_hours')
    if not isinstance(hours, (int, float)) or isinstance(hours, bool) or hours <= 0:
        return False
    raw = entry.get('raw') or {}
    if canonical_appid(raw.get('steam_appid')) != appid:
        return False
    if canonical_appid(raw.get('steam_external_game_uid')) != appid:
        return False
    if raw.get('normally_seconds') is None or float(raw.get('normally_seconds')) / 3600.0 != float(hours):
        return False
    return True


def structured_duration_for_game(game, entries):
    appids = []
    for raw in game.get('base_appids') or []:
        appid = canonical_appid(raw)
        if appid and appid not in appids:
            appids.append(appid)
    # The contract defines an appid-keyed estimate, not an aggregation rule for
    # multi-game packages. Fail closed instead of inventing sum/max/average semantics.
    if len(appids) != 1:
        return None
    entry = entries.get(appids[0]) if isinstance(entries, dict) else None
    if not validate_confirmed_cache_entry(entry):
        return None
    return {
        'hours': float(entry['estimated_duration_hours']),
        'source': 'igdb_game_time_to_beats_normally',
        'provenance': {
            'provider': 'igdb',
            'provider_schema': 'game_time_to_beats',
            'selected_metric': 'normally',
            'steam_appid': appids[0],
            'igdb_game_id': entry.get('igdb_game_id'),
            'count': (entry.get('raw') or {}).get('count'),
            'fetched_at_utc': entry.get('fetched_at_utc'),
        },
    }


def resolve_duration_for_game(game, projection, entries, legacy_extractor):
    structured = structured_duration_for_game(game, entries)
    if structured:
        return structured
    legacy_hours, legacy_source = legacy_extractor(projection, game)
    if legacy_hours is not None:
        return {
            'hours': float(legacy_hours),
            'source': 'legacy_text_explicit_duration_phrase',
            'provenance': {
                'provider': 'legacy_text',
                'legacy_extractor_source': legacy_source,
                'confidence': 'low_compatibility_fallback',
            },
        }
    return {'hours': None, 'source': None, 'provenance': None}


def write_cache(path, cache, before_text=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(cache, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'
    if before_text is None and path.exists():
        before_text = path.read_text(encoding='utf-8')
    changed = text != (before_text if before_text is not None else '')
    if changed:
        path.write_text(text, encoding='utf-8')
    return changed


def apply_transient_to_appids(entries, appids, status, now, contract, detail):
    for appid in appids:
        incoming = unresolved_entry(appid, status, now, contract, detail)
        entries[appid] = merge_entry(entries.get(appid), incoming, now)


def run_collection(contract, purchase_context_path, cache_path, client_id, client_secret, connectivity_only=False):
    now = utc_now()
    rows = load_jsonl(purchase_context_path)
    required_appids = required_appids_from_purchase_context(rows)
    cache_path = Path(cache_path)
    before_text = cache_path.read_text(encoding='utf-8') if cache_path.exists() else ''
    cache = load_cache(cache_path, contract)
    entries = cache.setdefault('entries', {})
    cache['scope'] = {
        'required_appid_count': len(required_appids),
        'required_appids_sha256': appid_scope_sha256(required_appids),
    }
    due = due_appids(required_appids, entries, now)

    client = IgdbClient(client_id, client_secret, api_base_url=contract['authority']['api_base_url'])
    try:
        client.authenticate()
        sources = client.api_post(contract['authority']['identity_source_endpoint'], build_external_game_sources_query())
        steam_source_id = resolve_steam_source_id(sources)
        print(f'DURATION_IGDB_CONNECTIVITY=PASS steam_external_game_source_id={steam_source_id}')
    except AuthError as exc:
        if not connectivity_only:
            apply_transient_to_appids(entries, due, 'auth_failure', now, contract, exc)
            cache['updated_at_utc'] = iso_utc(now)
            changed = write_cache(cache_path, cache, before_text)
            print(f'DURATION_CACHE_CHANGED={str(changed).lower()}')
        raise
    except (TransportError, ValueError) as exc:
        if not connectivity_only:
            apply_transient_to_appids(entries, due, 'transport_failure', now, contract, exc)
            cache['updated_at_utc'] = iso_utc(now)
            changed = write_cache(cache_path, cache, before_text)
            print(f'DURATION_CACHE_CHANGED={str(changed).lower()}')
        raise TransportError(str(exc)) from exc

    if connectivity_only:
        return {'connectivity': 'pass', 'required': len(required_appids), 'due': len(due), 'cache_changed': False}

    if not due:
        cache['updated_at_utc'] = cache.get('updated_at_utc') or iso_utc(now)
        changed = write_cache(cache_path, cache, before_text)
        print(f'DURATION_REQUIRED_APPIDS={len(required_appids)} DURATION_DUE_APPIDS=0')
        print(f'DURATION_CACHE_CHANGED={str(changed).lower()}')
        return {'connectivity': 'pass', 'required': len(required_appids), 'due': 0, 'cache_changed': changed}

    mapped = {}
    for appid_batch in chunked(due):
        try:
            external_rows = client.api_post(
                contract['authority']['identity_endpoint'],
                build_external_games_query(appid_batch, steam_source_id),
            )
            mapped.update(classify_external_game_mappings(appid_batch, external_rows, steam_source_id))
        except AuthError as exc:
            apply_transient_to_appids(entries, appid_batch, 'auth_failure', now, contract, exc)
        except TransportError as exc:
            apply_transient_to_appids(entries, appid_batch, 'transport_failure', now, contract, exc)

    game_to_appids = {}
    for appid in due:
        mapping = mapped.get(appid)
        if not mapping:
            continue
        if mapping.get('status') == 'mapped':
            game_to_appids.setdefault(mapping['igdb_game_id'], []).append(appid)
        else:
            incoming = unresolved_entry(appid, mapping['status'], now, contract)
            entries[appid] = merge_entry(entries.get(appid), incoming, now)

    game_ids = sorted(game_to_appids)
    duration_rows = {}
    invalid_duration_ids = set()
    for game_batch in chunked(game_ids):
        batch_appids = [appid for gid in game_batch for appid in game_to_appids.get(gid, [])]
        try:
            rows = client.api_post(contract['authority']['duration_endpoint'], build_time_to_beat_query(game_batch))
            grouped, invalid_ids = duration_rows_by_game_id(rows)
            duration_rows.update(grouped)
            invalid_duration_ids.update(invalid_ids)
        except AuthError as exc:
            apply_transient_to_appids(entries, batch_appids, 'auth_failure', now, contract, exc)
            for gid in game_batch:
                game_to_appids.pop(gid, None)
        except TransportError as exc:
            apply_transient_to_appids(entries, batch_appids, 'transport_failure', now, contract, exc)
            for gid in game_batch:
                game_to_appids.pop(gid, None)

    for game_id, appids in game_to_appids.items():
        row = duration_rows.get(game_id)
        for appid in appids:
            if game_id in invalid_duration_ids:
                incoming = unresolved_entry(appid, 'invalid_values', now, contract, 'multiple game_time_to_beats rows')
            elif row is None:
                incoming = unresolved_entry(appid, 'provider_row_missing', now, contract)
            else:
                incoming = normalize_confirmed_entry(
                    appid,
                    {'igdb_game_id': game_id},
                    row,
                    steam_source_id,
                    now,
                    contract,
                )
                if incoming is None:
                    incoming = unresolved_entry(appid, 'invalid_values', now, contract, 'invalid game_time_to_beats values')
            entries[appid] = merge_entry(entries.get(appid), incoming, now)

    cache['updated_at_utc'] = iso_utc(now)
    changed = write_cache(cache_path, cache, before_text)
    status_counts = {}
    for appid in required_appids:
        status = (entries.get(appid) or {}).get('status') or 'missing'
        status_counts[status] = status_counts.get(status, 0) + 1
    print(f'DURATION_REQUIRED_APPIDS={len(required_appids)} DURATION_DUE_APPIDS={len(due)}')
    print('DURATION_STATUS_COUNTS=' + json.dumps(status_counts, sort_keys=True, separators=(',', ':')))
    print(f'DURATION_CACHE_CHANGED={str(changed).lower()}')
    return {
        'connectivity': 'pass',
        'required': len(required_appids),
        'due': len(due),
        'cache_changed': changed,
        'status_counts': status_counts,
    }


def contract_collection_enabled(contract):
    return bool((contract.get('provisioning_gates') or {}).get('production_collection_enabled'))


def main():
    parser = argparse.ArgumentParser(description='GitHub-owned IGDB duration enrichment')
    parser.add_argument('--contract', default=str(CONTRACT_PATH))
    parser.add_argument('--purchase-context', default=str(PURCHASE_CONTEXT_PATH))
    parser.add_argument('--cache', default=str(CACHE_PATH))
    parser.add_argument('--connectivity-only', action='store_true')
    parser.add_argument('--allow-missing-credentials', action='store_true')
    parser.add_argument('--ignore-production-enable-gate', action='store_true')
    args = parser.parse_args()

    contract = load_json(args.contract)
    client_id = os.environ.get(CLIENT_ID_ENV, '').strip()
    client_secret = os.environ.get(CLIENT_SECRET_ENV, '').strip()
    if not client_id or not client_secret:
        print(
            f'DURATION_IGDB_PROVISIONING=missing_credentials '
            f'expected_secrets={CLIENT_ID_ENV},{CLIENT_SECRET_ENV}'
        )
        print('DURATION_CACHE_CHANGED=false')
        if args.allow_missing_credentials:
            return
        raise SystemExit(2)

    if not args.connectivity_only and not args.ignore_production_enable_gate and not contract_collection_enabled(contract):
        print('DURATION_IGDB_PRODUCTION=disabled_by_contract')
        print('DURATION_CACHE_CHANGED=false')
        return

    try:
        run_collection(
            contract,
            args.purchase_context,
            args.cache,
            client_id,
            client_secret,
            connectivity_only=args.connectivity_only,
        )
    except AuthError as exc:
        print(f'DURATION_IGDB_AUTH=FAIL reason={exc}')
        raise SystemExit(3)
    except TransportError as exc:
        print(f'DURATION_IGDB_TRANSPORT=FAIL reason={exc}')
        raise SystemExit(4)


if __name__ == '__main__':
    main()

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('.')
CONTRACT_PATH = ROOT / 'config/site_publication_resilience_contract.json'
QUARANTINE_PATH = ROOT / 'data/production/site/publication_quarantine.json'

QUARANTINE_CONTRACT = 'SITE-PUBLICATION-QUARANTINE-V1'
VALID_STATUSES = {'pending', 'resolved', 'superseded'}
IDENTITY_FIELDS = ('category', 'object_type', 'object_id', 'field')


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding='utf-8'))


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def defect_id_for(defect):
    identity = {key: str(defect.get(key) or '') for key in IDENTITY_FIELDS}
    if any(not identity[key] for key in IDENTITY_FIELDS):
        raise ValueError(f'publication defect identity incomplete: {identity}')
    return hashlib.sha256(canonical_json(identity).encode('utf-8')).hexdigest()


def empty_quarantine():
    return {
        'schema_version': 1,
        'contract': QUARANTINE_CONTRACT,
        'updated_at_utc': None,
        'entries': [],
    }


def validate_quarantine(doc):
    if not isinstance(doc, dict):
        raise ValueError('site publication quarantine must be an object')
    if doc.get('schema_version') != 1 or doc.get('contract') != QUARANTINE_CONTRACT:
        raise ValueError('site publication quarantine contract mismatch')
    entries = doc.get('entries')
    if not isinstance(entries, list):
        raise ValueError('site publication quarantine entries must be a list')
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError('site publication quarantine entry must be an object')
        wanted = defect_id_for(entry)
        if entry.get('defect_id') != wanted:
            raise ValueError('site publication quarantine defect_id mismatch')
        if wanted in seen:
            raise ValueError(f'duplicate site publication quarantine defect: {wanted}')
        seen.add(wanted)
        if entry.get('status') not in VALID_STATUSES:
            raise ValueError(f'invalid site publication quarantine status: {entry.get("status")}')
        reasons = entry.get('reason_codes')
        if not isinstance(reasons, list) or not reasons or any(not isinstance(x, str) or not x for x in reasons):
            raise ValueError('site publication quarantine reason_codes invalid')
        if not isinstance(entry.get('source_binding'), dict):
            raise ValueError('site publication quarantine source_binding missing')
        if not entry.get('first_seen_at_utc') or not entry.get('last_seen_at_utc'):
            raise ValueError('site publication quarantine timestamps missing')
        if entry.get('status') == 'resolved' and not entry.get('resolved_at_utc'):
            raise ValueError('resolved site publication defect missing resolved_at_utc')
    return doc


def load_quarantine(path=QUARANTINE_PATH):
    path = Path(path)
    if not path.exists():
        return empty_quarantine()
    return validate_quarantine(load_json(path))


def _normalized_binding(binding):
    if not isinstance(binding, dict):
        return {}
    return {
        str(key): value
        for key, value in sorted(binding.items())
        if value is not None and value != ''
    }


def _normalize_defect(defect, observed_at, default_binding):
    if not isinstance(defect, dict):
        raise ValueError('publication defect must be an object')
    normalized = {key: str(defect.get(key) or '').strip() for key in IDENTITY_FIELDS}
    defect_id = defect_id_for(normalized)
    reasons = sorted({
        str(value).strip()
        for value in defect.get('reason_codes') or []
        if str(value).strip()
    })
    if not reasons:
        raise ValueError(f'publication defect {defect_id} has no reason_codes')
    binding = dict(_normalized_binding(default_binding))
    binding.update(_normalized_binding(defect.get('source_binding')))
    entry = {
        'defect_id': defect_id,
        **normalized,
        'reason_codes': reasons,
        'status': 'pending',
        'first_seen_at_utc': observed_at,
        'last_seen_at_utc': observed_at,
        'source_binding': binding,
    }
    label = str(defect.get('label') or '').strip()
    if label:
        entry['label'] = label
    return entry


def reconcile_quarantine(defects, *, observed_at_utc=None, source_binding=None, path=QUARANTINE_PATH):
    observed_at = observed_at_utc or utc_now()
    previous = load_quarantine(path)
    previous_by_id = {
        entry['defect_id']: dict(entry)
        for entry in previous.get('entries') or []
    }
    next_entries = []

    normalized_by_id = {}
    for defect in defects or []:
        current = _normalize_defect(defect, observed_at, source_binding or {})
        defect_id = current['defect_id']
        existing = normalized_by_id.get(defect_id)
        if existing is None:
            normalized_by_id[defect_id] = current
            continue
        existing['reason_codes'] = sorted(set(existing['reason_codes']) | set(current['reason_codes']))
        existing['source_binding'].update(current.get('source_binding') or {})
        if current.get('label'):
            existing['label'] = current['label']

    for defect_id, current in sorted(normalized_by_id.items()):
        old = previous_by_id.pop(defect_id, None)
        if old:
            current['first_seen_at_utc'] = old.get('first_seen_at_utc') or observed_at
            same_observation = (
                old.get('status') == 'pending'
                and old.get('reason_codes') == current.get('reason_codes')
                and old.get('source_binding') == current.get('source_binding')
                and old.get('label') == current.get('label')
            )
            if same_observation:
                current['last_seen_at_utc'] = old.get('last_seen_at_utc') or observed_at
            current.pop('resolved_at_utc', None)
        next_entries.append(current)

    for defect_id, old in sorted(previous_by_id.items()):
        if old.get('status') == 'pending':
            old = dict(old)
            old['status'] = 'resolved'
            old['resolved_at_utc'] = observed_at
        next_entries.append(old)

    next_entries.sort(key=lambda entry: entry['defect_id'])
    previous_entries = sorted(previous.get('entries') or [], key=lambda entry: entry.get('defect_id') or '')
    changed = canonical_json(next_entries) != canonical_json(previous_entries)
    doc = {
        'schema_version': 1,
        'contract': QUARANTINE_CONTRACT,
        'updated_at_utc': observed_at if changed else previous.get('updated_at_utc'),
        'entries': next_entries,
    }
    validate_quarantine(doc)
    if changed:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return doc, changed


def active_summary(doc=None):
    doc = validate_quarantine(doc) if doc is not None else load_quarantine()
    active = [entry for entry in doc.get('entries') or [] if entry.get('status') == 'pending']
    categories = Counter(entry.get('category') for entry in active)
    return {
        'pending_count': len(active),
        'category_counts': dict(sorted(categories.items())),
        'last_change_at_utc': doc.get('updated_at_utc'),
    }

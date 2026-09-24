import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import build_progressive_pass1_work
import progressive_pass1
import progressive_work_authority

INBOX = Path('data/ai_inbox/progressive_pass1')
RECEIPTS = Path('data/cache/progressive_pass1_receipts')


def load_documents(paths):
    docs = []
    raw_by_name = {}
    for path in paths:
        raw = path.read_bytes()
        raw_by_name[path.name] = raw
        try:
            doc = json.loads(raw.decode('utf-8'))
            docs.append((path.name, doc, None))
        except Exception as exc:
            docs.append((path.name, None, f'{type(exc).__name__}:{exc}'))
    return docs, raw_by_name


def receipt_path(raw):
    digest = hashlib.sha256(raw).hexdigest()
    return RECEIPTS / f'{digest}.json'


def validate_activation_flags(work):
    if work.get('pass1_active') is not True or work.get('pass2_active') is not True:
        raise SystemExit('Progressive PASS 1 work activation flags are invalid')


def main():
    progressive_pass1.load_contract()
    work = progressive_pass1.load_json(progressive_pass1.WORK)
    if work.get('contract') != 'PROGRESSIVE-PASS1-WORK-V1':
        raise SystemExit('Current Progressive PASS 1 work manifest is missing or incompatible')
    validate_activation_flags(work)

    state = progressive_pass1.load_state()
    paths = sorted(INBOX.glob('*.json')) if INBOX.exists() else []
    accepted_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    docs, raw_by_name = load_documents(paths)
    consumed = progressive_work_authority.consumed_work_ids(RECEIPTS)
    authorized = []
    authorization_errors = {}
    doc_by_name = {name: (name, doc, error) for name, doc, error in docs}
    for path in paths:
        try:
            item = progressive_work_authority.resolve_presemantic_work_item(
                path,
                progressive_pass1.WORK,
                path_field='submission_path',
                expected_contract='PROGRESSIVE-PASS1-WORK-V1',
            )
            progressive_pass1.validate_profile_pin(item.pop('_profile_pin'))
            if item['work_id'] in consumed:
                authorization_errors[path.name] = 'work_id_already_consumed'
                continue
            existing = (state.get('entries') or {}).get(item['family_id'])
            existing_authority = existing.get('work_authority_commit') if isinstance(existing, dict) else None
            incoming_authority = item.get('_work_authority_commit')
            if (
                existing_authority
                and existing.get('work_id') != item.get('work_id')
                and incoming_authority != existing_authority
                and progressive_work_authority.commit_is_ancestor(incoming_authority, existing_authority)
            ):
                authorization_errors[path.name] = 'superseded_by_newer_accepted_work'
                continue
            authorized.append(item)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            authorization_errors[path.name] = str(exc)

    authorized.sort(
        key=lambda item: progressive_work_authority.authority_rank(item['_work_authority_commit'])
    )
    authorized_names = {Path(item['submission_path']).name for item in authorized}
    ordered_docs = [
        doc_by_name[Path(item['submission_path']).name]
        for item in authorized
        if Path(item['submission_path']).name in doc_by_name
    ]
    ordered_docs.extend(row for row in docs if row[0] not in authorized_names)
    acceptance_work = {'contract': 'PROGRESSIVE-PASS1-WORK-V1', 'items': authorized}
    new_state, receipts = progressive_pass1.process_submission_documents(
        acceptance_work,
        state,
        ordered_docs,
        accepted_at_utc=accepted_at,
    )
    for receipt in receipts:
        if (
            receipt.get('status') == 'rejected_stale_or_mismatched'
            and receipt.get('artifact') in authorization_errors
        ):
            receipt['reason'] = (
                'no_current_or_historical_presemantic_authority:'
                + authorization_errors[receipt['artifact']]
            )

    progressive_pass1.STATE.parent.mkdir(parents=True, exist_ok=True)
    progressive_pass1.STATE.write_text(
        json.dumps(new_state, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    RECEIPTS.mkdir(parents=True, exist_ok=True)
    for receipt in receipts:
        name = receipt['artifact']
        raw = raw_by_name.get(name, name.encode('utf-8'))
        out = receipt_path(raw)
        if not out.exists():
            out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    for path in paths:
        path.unlink()

    next_work = build_progressive_pass1_work.build_work_document()
    scope = next_work['scope']
    if scope['pass1_total_scope'] != scope['pass1_attempted_count'] + scope['pass1_remaining_count']:
        raise SystemExit('PASS 1 scope arithmetic mismatch after ingest')
    progressive_pass1.WORK.write_text(
        json.dumps(next_work, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    summary = {
        'processed_artifact_count': len(paths),
        'accepted_count': sum(r['status'] == 'accepted' for r in receipts),
        'accepted_invalid_as_incomplete_count': sum(
            r['status'] == 'accepted_as_incomplete_invalid_result' for r in receipts
        ),
        'rejected_stale_or_mismatched_count': sum(
            r['status'] == 'rejected_stale_or_mismatched' for r in receipts
        ),
        'rejected_unbound_count': sum(r['status'] == 'rejected_unbound' for r in receipts),
        'replay_ignored_count': sum(r['status'] == 'replay_ignored' for r in receipts),
        'pass1_total_scope': scope['pass1_total_scope'],
        'pass1_attempted_count': scope['pass1_attempted_count'],
        'pass1_remaining_count': scope['pass1_remaining_count'],
        'semantic_generation_id': next_work['semantic_generation_id'],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print('PROGRESSIVE_PASS1_INGEST=PASS')


if __name__ == '__main__':
    main()

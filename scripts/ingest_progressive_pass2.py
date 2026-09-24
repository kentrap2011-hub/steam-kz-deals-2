import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import build_progressive_pass2_work
import progressive_pass1
import progressive_pass2
import progressive_work_authority


RESULT_INBOX = Path('data/ai_inbox/progressive_pass2/results')
RECEIPT_INBOX = Path('data/ai_inbox/progressive_pass2/execution_receipts')
INGEST_RECEIPTS = Path('data/cache/progressive_pass2_ingest_receipts')


def load_documents(paths):
    documents = []
    raw_by_name = {}
    sha_by_name = {}
    for path in paths:
        raw = path.read_bytes()
        raw_by_name[path.name] = raw
        sha_by_name[path.name] = hashlib.sha256(raw).hexdigest()
        try:
            documents.append((path.name, json.loads(raw.decode('utf-8')), None))
        except Exception as exc:
            documents.append((path.name, None, f'{type(exc).__name__}:{exc}'))
    return documents, raw_by_name, sha_by_name


def write_ingest_receipts(receipts, raw_by_name):
    INGEST_RECEIPTS.mkdir(parents=True, exist_ok=True)
    for receipt in receipts:
        name = receipt['artifact']
        raw = raw_by_name.get(name, name.encode('utf-8'))
        digest = hashlib.sha256(raw).hexdigest()
        path = INGEST_RECEIPTS / f'{digest}.json'
        if not path.exists():
            path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def removable_names(receipts):
    removable = set()
    for receipt in receipts:
        if receipt.get('status') in {
            'accepted',
            'accepted_terminal_execution_receipt',
            'replay_ignored',
            'rejected_stale_or_mismatched',
        }:
            removable.add(receipt['artifact'])
    return removable


def main():
    contract = progressive_pass2.load_contract()
    if contract.get('active') is not True:
        raise SystemExit('Progressive PASS 2 is implemented but inactive; ingest is not authorized')

    persisted_work = progressive_pass2.load_json(progressive_pass2.WORK)
    if (
        persisted_work.get('contract') != 'PROGRESSIVE-PASS2-WORK-V1'
        or persisted_work.get('implemented') is not True
        or persisted_work.get('pass2_active') is not True
    ):
        raise SystemExit('Current Progressive PASS 2 work manifest is missing, stale, or inactive')

    # Resolve the exact Git-prepared work that existed before each artifact.
    # Profile/main drift is not a liveness gate for started work; Dossier truth is.
    work = persisted_work

    result_paths = sorted(RESULT_INBOX.glob('*.json')) if RESULT_INBOX.exists() else []
    terminal_paths = sorted(RECEIPT_INBOX.glob('*.json')) if RECEIPT_INBOX.exists() else []
    result_docs, result_raw, _result_sha = load_documents(result_paths)
    terminal_docs, terminal_raw, terminal_sha = load_documents(terminal_paths)

    accepted_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    state = progressive_pass2.load_state()
    consumed = progressive_work_authority.consumed_work_ids(INGEST_RECEIPTS)
    authorization_errors = {}
    authorized = []
    for path in result_paths + terminal_paths:
        path_field = (
            'result_submission_path'
            if path.parent.name == 'results'
            else 'terminal_execution_submission_path'
        )
        try:
            item = progressive_work_authority.resolve_presemantic_work_item(
                path,
                progressive_pass2.WORK,
                path_field=path_field,
                expected_contract='PROGRESSIVE-PASS2-WORK-V1',
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
            dossier_live, dossier_reason = progressive_pass2.prepared_work_item_dossier_is_live(item)
            if not dossier_live:
                authorization_errors[path.name] = dossier_reason
                continue
            authorized.append(item)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            authorization_errors[path.name] = str(exc)

    by_work = {}
    for item in sorted(
        authorized,
        key=lambda row: progressive_work_authority.authority_rank(row['_work_authority_commit']),
    ):
        by_work[(item['work_id'], item['authorization_id'])] = item
    acceptance_work = {
        'contract': 'PROGRESSIVE-PASS2-WORK-V1',
        'implemented': True,
        'pass2_active': True,
        'items': list(by_work.values()),
    }
    state_after_results, result_receipts = progressive_pass2.process_result_documents(
        acceptance_work,
        state,
        result_docs,
        accepted_at_utc=accepted_at,
    )
    final_state, terminal_receipts, canonical_receipts = (
        progressive_pass2.process_terminal_execution_documents(
            acceptance_work,
            state_after_results,
            terminal_docs,
            accepted_at_utc=accepted_at,
            source_sha256_by_name=terminal_sha,
        )
    )
    for receipt in result_receipts + terminal_receipts:
        if (
            receipt.get('status') == 'rejected_stale_or_mismatched'
            and receipt.get('artifact') in authorization_errors
        ):
            receipt['reason'] = (
                'no_live_presemantic_authority:'
                + authorization_errors[receipt['artifact']]
            )

    progressive_pass2.STATE.parent.mkdir(parents=True, exist_ok=True)
    # Canonical execution receipts are optional for normal semantic results, but
    # the workflow commit step may still stage this path. Ensure the directory
    # exists even when this ingest produced no terminal execution receipt.
    progressive_pass2.CANONICAL_EXECUTION_RECEIPTS.mkdir(parents=True, exist_ok=True)
    progressive_pass2.STATE.write_text(
        json.dumps(final_state, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    for path_text, receipt in canonical_receipts.items():
        path = Path(path_text)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            existing = json.loads(path.read_text(encoding='utf-8'))
            if existing != receipt:
                raise SystemExit(f'PASS 2 canonical execution receipt conflict: {path}')
        else:
            path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    all_receipts = result_receipts + terminal_receipts
    combined_raw = dict(result_raw)
    combined_raw.update(terminal_raw)
    write_ingest_receipts(all_receipts, combined_raw)

    remove_results = removable_names(result_receipts)
    remove_terminals = removable_names(terminal_receipts)
    for path in result_paths:
        if path.name in remove_results:
            path.unlink()
    for path in terminal_paths:
        if path.name in remove_terminals:
            path.unlink()

    next_work = build_progressive_pass2_work.build_work_document()
    if next_work.get('pass2_active') is not True:
        raise SystemExit('PASS 2 became inactive during ingest; refusing to persist next work')
    progressive_pass2.WORK.write_text(
        json.dumps(next_work, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    summary = {
        'processed_result_artifact_count': len(result_paths),
        'processed_terminal_receipt_count': len(terminal_paths),
        'accepted_result_count': sum(r['status'] == 'accepted' for r in result_receipts),
        'accepted_terminal_receipt_count': sum(
            r['status'] == 'accepted_terminal_execution_receipt' for r in terminal_receipts
        ),
        'rejected_invalid_result_no_attempt_count': sum(
            r['status'] == 'rejected_invalid_result_no_attempt' for r in result_receipts
        ),
        'rejected_invalid_execution_receipt_no_attempt_count': sum(
            r['status'] == 'rejected_invalid_execution_receipt_no_attempt'
            for r in terminal_receipts
        ),
        'deep_first_pass_attempted_count': next_work['scope']['deep_first_pass_attempted_count'],
        'deep_authoritative_completed_count': next_work['scope']['deep_authoritative_completed_count'],
        'deep_incomplete_or_recovery_count': next_work['scope']['deep_incomplete_or_recovery_count'],
        'deep_waiting_for_dossier_count': next_work['scope']['deep_waiting_for_dossier_count'],
        'deep_ready_or_pending_count': next_work['scope']['deep_ready_or_pending_count'],
        'recovery_pending_count': next_work['scope']['recovery_pending_count'],
        'semantic_generation_id': next_work['semantic_generation_id'],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print('PROGRESSIVE_PASS2_INGEST=PASS')


if __name__ == '__main__':
    main()

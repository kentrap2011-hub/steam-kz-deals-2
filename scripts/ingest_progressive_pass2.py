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
RUN_START_INBOX = Path('data/ai_inbox/progressive_pass2/run_starts')
INGEST_RECEIPTS = Path('data/cache/progressive_pass2_ingest_receipts')
RUN_START_RECEIPTS = Path('data/cache/progressive_pass2_run_start_receipts')


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



def _read_json_at_commit(commit, path):
    raw = progressive_work_authority.file_bytes_at_commit(commit, path)
    try:
        return json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'Progressive run-start authority has invalid JSON at {path}') from exc


def _write_run_start_receipt(receipt):
    anchor = receipt.get('run_start_anchor_commit')
    if not isinstance(anchor, str) or len(anchor) != 40:
        raise ValueError('Deep run-start receipt anchor is missing')
    RUN_START_RECEIPTS.mkdir(parents=True, exist_ok=True)
    path = RUN_START_RECEIPTS / f'{anchor}.json'
    raw = json.dumps(receipt, ensure_ascii=False, indent=2) + '\n'
    if path.exists():
        if path.read_text(encoding='utf-8') != raw:
            raise ValueError(f'Deep run-start receipt conflict: {path}')
        return path
    path.write_text(raw, encoding='utf-8')
    return path


def process_run_start_markers():
    paths = sorted(RUN_START_INBOX.glob('*.json')) if RUN_START_INBOX.exists() else []
    receipts = []
    for path in paths:
        anchor = progressive_work_authority.result_introduction_commit(path)
        parent = progressive_work_authority.commit_parent(anchor)
        started = progressive_work_authority.commit_committer_time_utc(anchor)
        raw = path.read_bytes()
        try:
            doc = json.loads(raw.decode('utf-8'))
            parse_error = None
        except Exception as exc:
            doc = None
            parse_error = f'{type(exc).__name__}:{exc}'

        receipt = {
            'schema_version': 1,
            'contract': 'PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1',
            'status': 'rejected',
            'run_start_anchor_commit': anchor,
            'run_start_authority_commit': parent,
            'run_started_at_utc': started,
            'marker_path': path.as_posix(),
            'run_start_nonce': doc.get('run_start_nonce') if isinstance(doc, dict) else None,
            'semantic_generation_id': None,
            'profile_pin_sha256': None,
            'reason': parse_error,
        }
        try:
            if parse_error:
                raise ValueError(parse_error)
            proof = progressive_work_authority.validate_run_start_marker_commit(
                anchor,
                path,
                doc,
            )
            contract = _read_json_at_commit(parent, 'config/progressive_pass2_contract.json')
            work = _read_json_at_commit(parent, progressive_pass2.WORK.as_posix())
            if contract.get('contract') != 'PROGRESSIVE-PASS2-V1':
                raise ValueError('Deep run-start contract mismatch')
            if contract.get('implemented') is not True or contract.get('active') is not True:
                raise ValueError('Deep was not active at the anchored invocation boundary')
            if (
                work.get('contract') != 'PROGRESSIVE-PASS2-WORK-V1'
                or work.get('implemented') is not True
                or work.get('pass2_active') is not True
            ):
                raise ValueError('Deep work was not active at the anchored invocation boundary')
            profile_pin = work.get('profile_pin')
            progressive_pass1.validate_profile_pin(profile_pin)
            receipt.update({
                'status': 'confirmed',
                'run_start_authority_commit': proof['run_start_authority_commit'],
                'run_started_at_utc': proof['run_started_at_utc'],
                'marker_path': proof['marker_path'],
                'run_start_nonce': proof['run_start_nonce'],
                'semantic_generation_id': work.get('semantic_generation_id'),
                'profile_pin_sha256': profile_pin.get('pin_sha256'),
                'reason': None,
            })
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            receipt['reason'] = str(exc)

        _write_run_start_receipt(receipt)
        receipts.append(receipt)
        path.unlink()

    return receipts


def removable_names(receipts):
    removable = set()
    for receipt in receipts:
        if receipt.get('status') in {
            'accepted',
            'accepted_terminal_execution_receipt',
            'replay_ignored',
            'rejected_stale_or_mismatched',
            'rejected_invalid_result_no_attempt',
            'rejected_invalid_execution_receipt_no_attempt',
        }:
            removable.add(receipt['artifact'])
    return removable


def _current_item_for_path(work, path, path_field):
    target = path.as_posix()
    for item in work.get('items') or []:
        if isinstance(item, dict) and str(item.get(path_field) or '') == target:
            return item
    return None


def _same_current_identity(a, b):
    if not isinstance(a, dict) or not isinstance(b, dict):
        return False
    fields = ('work_id', 'authorization_id', 'work_mode', 'profile_pin_sha256')
    return all(a.get(field) == b.get(field) for field in fields)


def resolve_candidate_authority(path, path_field, doc, persisted_work):
    run_anchor = doc.get('run_start_anchor_commit') if isinstance(doc, dict) else None
    exact_error = None

    if isinstance(run_anchor, str):
        try:
            run_receipt = (
                progressive_work_authority.load_confirmed_run_start_receipt_for_artifact(
                    path,
                    run_anchor,
                    receipt_root=RUN_START_RECEIPTS.as_posix(),
                )
            )
            run_commit = run_receipt['run_start_authority_commit']
            run_started = run_receipt['run_started_at_utc']
            if doc.get('run_start_authority_commit') != run_commit:
                raise ValueError('candidate run-start authority does not match GitHub confirmation')
            if doc.get('run_started_at_utc') != run_started:
                raise ValueError('candidate run-start time does not match GitHub confirmation')
            item = progressive_work_authority.resolve_presemantic_work_item_at_commit(
                path,
                progressive_pass2.WORK,
                run_commit,
                path_field=path_field,
                expected_contract='PROGRESSIVE-PASS2-WORK-V1',
            )
            progressive_pass1.validate_profile_pin(item['_profile_pin'])
            if item.get('profile_pin_sha256') != run_receipt.get('profile_pin_sha256'):
                raise ValueError('candidate profile pin does not match GitHub run-start confirmation')
            if item.get('semantic_generation_id') != run_receipt.get('semantic_generation_id'):
                raise ValueError('candidate generation does not match GitHub run-start confirmation')
            progressive_pass2.validate_run_start_authority(
                item,
                run_receipt,
            )
            item['_run_start_anchor_commit'] = run_anchor
            item['_run_start_authority_commit'] = run_commit
            item['_run_started_at_utc'] = run_started
            item['_run_start_authority_verified'] = True
            return item, None
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            exact_error = str(exc)

    current = _current_item_for_path(persisted_work, path, path_field)
    if current is None:
        if exact_error:
            raise ValueError(exact_error)
        raise ValueError('candidate lacks exact GitHub-confirmed run-start authority')

    item = progressive_work_authority.resolve_presemantic_work_item(
        path,
        progressive_pass2.WORK,
        path_field=path_field,
        expected_contract='PROGRESSIVE-PASS2-WORK-V1',
    )
    progressive_pass1.validate_profile_pin(item['_profile_pin'])
    if not _same_current_identity(item, current):
        raise ValueError('candidate path no longer matches current prepared Deep identity')
    item['_run_start_anchor_commit'] = None
    item['_run_start_authority_commit'] = item.get('_work_authority_commit')
    item['_run_started_at_utc'] = None
    item['_run_start_authority_verified'] = False
    return item, exact_error or 'missing_github_confirmed_run_start_authority'

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

    run_start_receipts = process_run_start_markers()

    result_paths = sorted(RESULT_INBOX.glob('*.json')) if RESULT_INBOX.exists() else []
    terminal_paths = sorted(RECEIPT_INBOX.glob('*.json')) if RECEIPT_INBOX.exists() else []
    result_docs, result_raw, _result_sha = load_documents(result_paths)
    terminal_docs, terminal_raw, terminal_sha = load_documents(terminal_paths)
    document_by_name = {
        name: (doc, error)
        for name, doc, error in (result_docs + terminal_docs)
    }

    accepted_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    state = progressive_pass2.load_state()
    consumed = progressive_work_authority.consumed_work_ids(INGEST_RECEIPTS)
    authorization_errors = {}
    invalid_transport_authority_errors = {}
    authorized = []

    for path in result_paths + terminal_paths:
        path_field = (
            'result_submission_path'
            if path.parent.name == 'results'
            else 'terminal_execution_submission_path'
        )
        doc, _parse_error = document_by_name.get(path.name, (None, 'missing_document'))
        try:
            item, invalid_authority_error = resolve_candidate_authority(
                path, path_field, doc, persisted_work
            )
            if invalid_authority_error:
                invalid_transport_authority_errors[path.name] = invalid_authority_error
            if item.get('work_mode') == 'normal_first_pass' and item['work_id'] in consumed:
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
        artifact = receipt.get('artifact')
        if (
            receipt.get('status') == 'rejected_stale_or_mismatched'
            and artifact in authorization_errors
        ):
            receipt['reason'] = (
                'no_run_start_presemantic_authority:'
                + authorization_errors[artifact]
            )
        if (
            receipt.get('status') in {
                'rejected_invalid_result_no_attempt',
                'rejected_invalid_execution_receipt_no_attempt',
            }
            and artifact in invalid_transport_authority_errors
        ):
            receipt['reason'] = (
                'run_start_authority_invalid:'
                + invalid_transport_authority_errors[artifact]
            )

    progressive_pass2.STATE.parent.mkdir(parents=True, exist_ok=True)
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

    # Persist diagnostic rejection/acceptance receipts before active-path cleanup.
    # The canonical writer stages both receipt and deletion in one Git commit.
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
        'processed_run_start_marker_count': len(run_start_receipts),
        'confirmed_run_start_count': sum(r['status'] == 'confirmed' for r in run_start_receipts),
        'rejected_run_start_count': sum(r['status'] == 'rejected' for r in run_start_receipts),
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

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import build_progressive_pass2_work
import progressive_pass2


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

    work = progressive_pass2.load_json(progressive_pass2.WORK)
    if (
        work.get('contract') != 'PROGRESSIVE-PASS2-WORK-V1'
        or work.get('implemented') is not True
        or work.get('pass2_active') is not True
    ):
        raise SystemExit('Current Progressive PASS 2 work manifest is missing, stale, or inactive')

    result_paths = sorted(RESULT_INBOX.glob('*.json')) if RESULT_INBOX.exists() else []
    terminal_paths = sorted(RECEIPT_INBOX.glob('*.json')) if RECEIPT_INBOX.exists() else []
    result_docs, result_raw, _result_sha = load_documents(result_paths)
    terminal_docs, terminal_raw, terminal_sha = load_documents(terminal_paths)

    accepted_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    state = progressive_pass2.load_state()
    state_after_results, result_receipts = progressive_pass2.process_result_documents(
        work,
        state,
        result_docs,
        accepted_at_utc=accepted_at,
    )
    final_state, terminal_receipts, canonical_receipts = (
        progressive_pass2.process_terminal_execution_documents(
            work,
            state_after_results,
            terminal_docs,
            accepted_at_utc=accepted_at,
            source_sha256_by_name=terminal_sha,
        )
    )

    progressive_pass2.STATE.parent.mkdir(parents=True, exist_ok=True)
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
        'pass2_attempted_count': next_work['scope']['pass2_attempted_count'],
        'pass2_eligible_count': next_work['scope']['pass2_eligible_count'],
        'semantic_generation_id': next_work['semantic_generation_id'],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print('PROGRESSIVE_PASS2_INGEST=PASS')


if __name__ == '__main__':
    main()

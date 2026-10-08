#!/usr/bin/env python3
"""Strict nonblocking Stage-1 result ingest; NOT wired to production workflows."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

from deep_stage1 import (
    INBOX, RESULTS, ROOT, Stage1Error, accept_result, empty_state,
    file_sha256, load_json, recompute_progress, record_diagnostic,
    safe_repo_path, require, validate_result, validate_state, validate_work_manifest,
)

DEFAULT_WORK = ROOT / "data/production/pre_ai/deep_stage1_work.json"
DEFAULT_STATE = ROOT / "data/cache/deep_stage1_state.json"
DEFAULT_RECEIPTS = ROOT / "data/cache/deep_stage1_ingest_receipts"


def encode_json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(encode_json(value), encoding="utf-8")


def create_or_identical(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise Stage1Error(f"create-only artifact collision: {path}")
        return
    with path.open("xb") as stream:
        stream.write(data)


def ingest_documents(work: dict, state: dict, submissions: list[Path], *,
                     repo_root: Path = ROOT, canonical_root: Path | None = None,
                     receipts_root: Path | None = None,
                     accepted_at_utc: str | None = None) -> tuple[dict, list[dict]]:
    validate_work_manifest(work)
    validate_state(state)
    canonical_root = canonical_root or (repo_root / RESULTS)
    receipts_root = receipts_root or (repo_root / DEFAULT_RECEIPTS.relative_to(ROOT))
    items = {item["result_submission_path"]: item for item in work["items"]}
    receipts = []

    for submission in sorted(set(submissions), key=str):
        try:
            rel = submission.relative_to(repo_root).as_posix()
        except ValueError:
            rel = ""
        digest = file_sha256(submission)
        item = items.get(rel)
        if item is None:
            record_diagnostic(state, {
                "code": "stale_or_unknown_stage1_transport",
                "submission_path": rel or str(submission),
                "submission_sha256": digest,
            })
            receipts.append({"status": "rejected_no_attempt", "path": rel or str(submission),
                             "reason": "transport not in current exact GitHub work manifest"})
            continue
        try:
            # Work path is bound by manifest. This is a filesystem verification, not acceptance.
            require(safe_repo_path(rel, repo_root) == submission,
                    "submission must be the exact repository-root-relative path")
            raw = submission.read_bytes()
            doc = json.loads(raw.decode("utf-8"))
            validate_result(doc, item, root=repo_root)
            canonical_rel = RESULTS / f"{item['work_id']}.json"
            canonical_path = canonical_root / f"{item['work_id']}.json"
            prev = state["entries"].get(item["work_id"])
            if prev is not None and (
                prev.get("accepted_result_sha256") != digest
                or prev.get("accepted_result_path") != canonical_rel.as_posix()
            ):
                raise Stage1Error("accepted state collision for immutable work identity")
            if canonical_path.exists() and file_sha256(canonical_path) != digest:
                raise Stage1Error("canonical create-only accepted result collision")
            receipt = {
                "schema_version": 1, "contract": "DEEP-STAGE1-INGEST-RECEIPT-V1",
                "work_id": item["work_id"],
                "submission_path": rel, "submission_sha256": digest,
                "outcome": doc["outcome"], "status": "accepted",
                "accepted_result_path": canonical_rel.as_posix(),
                "accepted_result_sha256": digest,
                "accepted_at_utc": prev["accepted_at_utc"] if prev else accepted_at_utc,
            }
            # Fill deterministic acceptance time before making the immutable receipt.
            if prev is None:
                from deep_stage1 import utc_now
                receipt["accepted_at_utc"] = receipt["accepted_at_utc"] or utc_now()
            receipt_path = receipts_root / f"{item['work_id']}.json"
            if receipt_path.exists() and receipt_path.read_bytes() != encode_json(receipt).encode("utf-8"):
                raise Stage1Error("accepted receipt create-only collision")
            create_or_identical(canonical_path, raw)
            accept_result(state, item, doc, path=canonical_rel.as_posix(),
                          sha=digest, accepted_at_utc=receipt["accepted_at_utc"])
            create_or_identical(receipt_path, encode_json(receipt).encode("utf-8"))
            receipts.append(receipt)
        except (Stage1Error, AssertionError, ValueError, UnicodeError, TypeError, KeyError) as exc:
            record_diagnostic(state, {
                "code": "invalid_stage1_transport_no_attempt",
                "work_id": item["work_id"], "submission_path": rel,
                "submission_sha256": digest, "detail": str(exc),
            })
            receipts.append({"status": "rejected_no_attempt", "work_id": item["work_id"],
                             "path": rel, "reason": str(exc)})
            # An invalid item does not block other independently prepared items.
            continue
    recompute_progress(state, work)
    return state, receipts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=str(DEFAULT_WORK))
    ap.add_argument("--state", default=str(DEFAULT_STATE))
    ap.add_argument("--inbox-glob", default=str(ROOT / INBOX / "*.json"))
    args = ap.parse_args()
    work = validate_work_manifest(load_json(args.work))
    state_path = Path(args.state)
    state = validate_state(load_json(state_path)) if state_path.exists() else empty_state()
    submissions = [Path(name) for name in glob.glob(args.inbox_glob)]
    state, receipts = ingest_documents(work, state, submissions)
    write_json(state_path, state)
    print(json.dumps({
        "status": "implemented_not_active",
        "accepted_or_replayed": sum(row["status"] == "accepted" for row in receipts),
        "rejected_no_attempt": sum(row["status"] == "rejected_no_attempt" for row in receipts),
        "progress": state["progress"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

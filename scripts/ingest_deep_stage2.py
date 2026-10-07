#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

from deep_stage2 import (
    CANONICAL_RESULTS_ROOT,
    RESULT_INBOX_ROOT,
    ROOT,
    Stage2Error,
    apply_validated_result,
    empty_state,
    file_sha256,
    load_json,
    recompute_progress,
    result_item_map,
    validate_result,
    validate_state,
    validate_work_manifest,
)

WORK_PATH = ROOT / "data/production/pre_ai/deep_stage2_work.json"
STATE_PATH = ROOT / "data/cache/deep_stage2_state.json"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_json_create_or_identical(path: Path, value: dict) -> None:
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != payload:
            raise Stage2Error(f"create-only collision at {path}")
        return
    path.write_text(payload, encoding="utf-8")


def ingest_documents(
    work: dict,
    state: dict,
    submission_paths: list[Path],
    *,
    accepted_at_utc: str | None = None,
    repo_root: Path = ROOT,
    canonical_results_root: Path | None = None,
    receipts_root: Path | None = None,
    delete_processed: bool = False,
    stage1_loader=None,
) -> tuple[dict, list[dict]]:
    validate_work_manifest(work)
    state = validate_state(state)
    by_path = result_item_map(work)
    canonical_results_root = canonical_results_root or (repo_root / CANONICAL_RESULTS_ROOT)
    receipts_root = receipts_root or (repo_root / "data/cache/deep_stage2_ingest_receipts")
    receipts = []

    for submission_path in sorted(submission_paths, key=lambda p: str(p)):
        try:
            rel = submission_path.relative_to(repo_root)
        except ValueError:
            rel = submission_path
        rel_text = str(rel).replace("\\", "/")
        item = by_path.get(rel_text)
        if item is None:
            raise Stage2Error(f"unknown or stale Stage-2 submission path: {rel_text}")

        raw = submission_path.read_bytes()
        result_sha = file_sha256(submission_path)
        doc = json.loads(raw.decode("utf-8"))
        if stage1_loader is None:
            validate_result(doc, item)
        else:
            validate_result(doc, item, stage1_loader=stage1_loader)

        canonical_rel = CANONICAL_RESULTS_ROOT / f"{item['calibration_work_id']}.json"
        canonical_path = canonical_results_root / f"{item['calibration_work_id']}.json"
        if canonical_path.exists():
            existing_sha = file_sha256(canonical_path)
            if existing_sha != result_sha:
                raise Stage2Error(
                    f"canonical Stage-2 result collision for {item['calibration_work_id']}"
                )
        else:
            canonical_path.parent.mkdir(parents=True, exist_ok=True)
            canonical_path.write_bytes(raw)

        existing_entry = state["entries"].get(item["calibration_work_id"])
        if existing_entry is not None:
            if (
                existing_entry.get("canonical_stage2_result_sha256") != result_sha
                or existing_entry.get("stage1_result_sha256") != item["stage1_result_sha256"]
                or existing_entry.get("anchor_window_id") != item["anchor_window_id"]
                or existing_entry.get("anchor_set_sha256") != item["anchor_set_sha256"]
            ):
                raise Stage2Error(
                    f"accepted Stage-2 state collision for {item['calibration_work_id']}"
                )
        else:
            state = apply_validated_result(
                state,
                item,
                doc,
                canonical_result_path=str(canonical_rel).replace("\\", "/"),
                canonical_result_sha256=result_sha,
                accepted_at_utc=accepted_at_utc,
            )

        accepted_entry = state["entries"][item["calibration_work_id"]]
        receipt = {
            "schema_version": 1,
            "contract": "DEEP-STAGE2-INGEST-RECEIPT-V1",
            "calibration_work_id": item["calibration_work_id"],
            "submission_path": rel_text,
            "submission_sha256": result_sha,
            "outcome": doc["outcome"],
            "canonical_stage2_result_path": str(canonical_rel).replace("\\", "/"),
            "canonical_stage2_result_sha256": result_sha,
            "calibrated_deep_fit_score_0_56": accepted_entry["calibrated_deep_fit_score_0_56"],
            "accepted_at_utc": accepted_entry["accepted_at_utc"],
        }
        receipt_path = receipts_root / f"{item['calibration_work_id']}.json"
        write_json_create_or_identical(receipt_path, receipt)
        receipts.append(receipt)
        if delete_processed:
            submission_path.unlink()

    recompute_progress(
        state,
        stage1_fit_eligible=int(work.get("stage1_fit_eligible") or 0),
        current_work_count=max(len(work.get("items") or []) - len(receipts), 0),
    )
    validate_state(state)
    return state, receipts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", default=str(WORK_PATH))
    parser.add_argument("--state", default=str(STATE_PATH))
    parser.add_argument("--inbox-glob", default=str(ROOT / RESULT_INBOX_ROOT / "*.json"))
    parser.add_argument("--delete-processed", action="store_true")
    args = parser.parse_args()

    work = validate_work_manifest(load_json(Path(args.work)))
    state_path = Path(args.state)
    state = validate_state(load_json(state_path)) if state_path.exists() else empty_state()
    submissions = [Path(p) for p in sorted(glob.glob(args.inbox_glob))]
    if not submissions:
        recompute_progress(
            state,
            stage1_fit_eligible=int(work.get("stage1_fit_eligible") or 0),
            current_work_count=len(work.get("items") or []),
        )
        write_json(state_path, state)
        print(json.dumps({"status": "no_submissions", "submission_count": 0}, indent=2))
        return

    try:
        state, receipts = ingest_documents(
            work,
            state,
            submissions,
            delete_processed=args.delete_processed,
        )
    except Stage2Error as exc:
        raise SystemExit(f"DEEP_STAGE2_INGEST_INVALID: {exc}")
    write_json(state_path, state)
    print(json.dumps({
        "status": "complete",
        "submission_count": len(submissions),
        "accepted_count": len(receipts),
        "calibrated": state["progress"]["calibrated"],
        "diagnostic_incomplete": state["progress"]["diagnostic_incomplete"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

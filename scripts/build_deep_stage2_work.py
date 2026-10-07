#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from deep_stage2 import (
    ROOT,
    Stage2Error,
    build_work_manifest,
    empty_state,
    file_sha256,
    load_json,
    validate_stage1_fit_result,
    validate_state,
)

DEFAULT_STAGE1_STATE = ROOT / "data/cache/deep_stage1_state.json"
DEFAULT_STAGE2_STATE = ROOT / "data/cache/deep_stage2_state.json"
DEFAULT_WORK = ROOT / "data/production/pre_ai/deep_stage2_work.json"


def _entry_candidates(stage1_state: dict) -> list[tuple[str, dict]]:
    entries = stage1_state.get("entries")
    if isinstance(entries, dict):
        return [(str(key), value) for key, value in entries.items() if isinstance(value, dict)]
    if isinstance(entries, list):
        return [(str(index), value) for index, value in enumerate(entries) if isinstance(value, dict)]
    accepted = stage1_state.get("accepted_fit_results")
    if isinstance(accepted, list):
        return [(str(index), value) for index, value in enumerate(accepted) if isinstance(value, dict)]
    return []


def normalize_stage1_candidates(
    stage1_state: dict,
    repo_root: Path = ROOT,
) -> tuple[list[dict], list[dict]]:
    """
    Stage 1 owns its state schema. Stage 2 consumes only entries exposing an
    explicit accepted-result reference plus the frozen Stage-1 result itself.
    Anything else is diagnosed instead of inferred from inbox files.
    """
    candidates = []
    diagnostics = []
    for ordinal, (entry_key, entry) in enumerate(_entry_candidates(stage1_state), start=1):
        accepted = entry.get("accepted")
        status = entry.get("status")
        if accepted is not True and status not in {"accepted", "completed", "analyzed_fit"}:
            continue

        result_path = (
            entry.get("accepted_result_path")
            or entry.get("canonical_result_path")
            or entry.get("result_path")
        )
        result_sha = (
            entry.get("accepted_result_sha256")
            or entry.get("canonical_result_sha256")
            or entry.get("result_sha256")
        )
        profile_pin = entry.get("profile_pin")
        if not isinstance(result_path, str) or not result_path or not isinstance(result_sha, str) or not result_sha:
            diagnostics.append({
                "stage1_entry": entry_key,
                "code": "stage1_accepted_result_reference_missing",
                "detail": "Stage 2 will not infer accepted Stage-1 artifacts from inbox or mutable directories.",
            })
            continue
        path = repo_root / result_path
        if not path.exists():
            diagnostics.append({
                "stage1_entry": entry_key,
                "code": "stage1_accepted_result_missing",
                "detail": result_path,
            })
            continue
        observed = file_sha256(path)
        if observed != result_sha:
            diagnostics.append({
                "stage1_entry": entry_key,
                "code": "stage1_accepted_result_hash_mismatch",
                "detail": f"{result_path}: expected {result_sha}, got {observed}",
            })
            continue
        try:
            result = validate_stage1_fit_result(load_json(path))
        except Stage2Error as exc:
            diagnostics.append({
                "stage1_entry": entry_key,
                "code": "stage1_accepted_result_invalid_for_stage2",
                "detail": str(exc),
            })
            continue
        if profile_pin is None:
            diagnostics.append({
                "stage1_entry": entry_key,
                "code": "stage1_profile_pin_reference_missing",
                "detail": "Frozen Stage-2 work requires the exact pinned profile reference; Stage 2 will not reconstruct it.",
            })
            continue

        candidates.append({
            "sequence": int(entry.get("sequence") or ordinal),
            "stage1_work_id": result["work_id"],
            "family_id": result["family_id"],
            "appid": str(result["appid"]),
            "profile_pin": profile_pin,
            "profile_semantic_sha256": result["profile_semantic_sha256"],
            "stage1_result_path": result_path,
            "stage1_result_sha256": result_sha,
            "stage1_result": result,
            "anchor_window_revision": int(entry.get("stage2_anchor_window_revision") or 1),
        })
    candidates.sort(key=lambda row: (row["sequence"], row["stage1_work_id"]))
    return candidates, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage1-state", default=str(DEFAULT_STAGE1_STATE))
    parser.add_argument("--stage2-state", default=str(DEFAULT_STAGE2_STATE))
    parser.add_argument("--out", default=str(DEFAULT_WORK))
    parser.add_argument("--lower-count", type=int, default=2)
    parser.add_argument("--upper-count", type=int, default=2)
    args = parser.parse_args()

    stage1_path = Path(args.stage1_state)
    if not stage1_path.exists():
        candidates = []
        input_diagnostics = [{
            "stage1_entry": None,
            "code": "stage1_state_unavailable",
            "detail": str(stage1_path),
        }]
    else:
        candidates, input_diagnostics = normalize_stage1_candidates(load_json(stage1_path))

    stage2_path = Path(args.stage2_state)
    state = validate_state(load_json(stage2_path)) if stage2_path.exists() else empty_state()
    work = build_work_manifest(
        candidates,
        state,
        lower_count=args.lower_count,
        upper_count=args.upper_count,
    )
    work["diagnostics"] = input_diagnostics + work["diagnostics"]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(work, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "complete",
        "stage1_fit_eligible": work["stage1_fit_eligible"],
        "work_items": len(work["items"]),
        "diagnostics": len(work["diagnostics"]),
        "out": str(out),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

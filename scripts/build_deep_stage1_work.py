#!/usr/bin/env python3
"""Generate a non-active Stage-1 manifest from GitHub's exact current PASS-2 prepared work.

This is a standalone control-plane implementation for later integration, not a
production pipeline hook or a new scheduling/retry authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import progressive_pass2
from deep_stage1 import (
    ROOT, SOURCE, build_work_manifest, empty_state, load_json, recompute_progress,
    validate_state,
)

DEFAULT_SOURCE = ROOT / SOURCE
DEFAULT_STATE = ROOT / "data/cache/deep_stage1_state.json"
DEFAULT_WORK = ROOT / "data/production/pre_ai/deep_stage1_work.json"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(DEFAULT_SOURCE))
    ap.add_argument("--state", default=str(DEFAULT_STATE))
    ap.add_argument("--out", default=str(DEFAULT_WORK))
    args = ap.parse_args()
    source = load_json(args.source)
    state_path = Path(args.state)
    state = validate_state(load_json(state_path)) if state_path.is_file() else empty_state()
    work = build_work_manifest(
        source, state, root=ROOT,
        dossier_validator=progressive_pass2.dossier_is_eligible,
    )
    # All output remains non-active and read-only to existing PASS-2 control plane.
    recompute_progress(state, work)
    write_json(Path(args.out), work)
    print(json.dumps({
        "status": "implemented_not_active",
        "total_eligible": work["total_eligible"],
        "pending_items": len(work["items"]),
        "diagnostics": len(work["diagnostics"]),
        "out": args.out,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

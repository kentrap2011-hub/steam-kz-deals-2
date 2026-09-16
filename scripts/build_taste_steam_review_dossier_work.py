#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from taste_steam_review_dossier import atomic_write_json
from taste_steam_review_dossier_daily import (
    ensure_submission_group_plan,
    load_contract,
    validate_manifest,
)
from taste_steam_review_dossier_recovery import (
    load_recovery_contract,
    quarantine_stale_snapshot_inbox,
)
from taste_steam_review_dossier_web import (
    _PACKAGE_IDENTITY_POLICY_REVISION,
    build_daily_work_manifest_web,
    ensure_web_evidence_binding,
)
from taste_steam_review_dossier_worker_projection import write_worker_projection

_SAMARA = ZoneInfo("Europe/Samara")


def _read_jsonl(path):
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{n}: {exc}") from exc
    return rows


def build_or_preserve_daily_work(
    *,
    contract,
    queue_path,
    store_dir,
    output_path,
    ttl_days=None,
    now=None,
):
    """Preserve same-day control-plane identity unless the active identity policy revision changed."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    prepared_for_date = now.astimezone(_SAMARA).date().isoformat()
    output_path = Path(output_path)

    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        validate_manifest(existing, contract)
        existing_date = str(existing.get("prepared_for_date") or "")
        if existing_date > prepared_for_date:
            raise ValueError(
                f"existing dossier snapshot date {existing_date} is ahead of current Samara date {prepared_for_date}"
            )
        if (
            existing_date == prepared_for_date
            and existing.get("identity_policy_revision") == _PACKAGE_IDENTITY_POLICY_REVISION
        ):
            if ttl_days is not None and int(existing["ttl_days"]) != int(ttl_days):
                raise ValueError("cannot change TTL inside an already-prepared fixed daily dossier snapshot")
            had_group_plan = existing.get("submission_group_plan") is not None
            manifest = ensure_submission_group_plan(existing, contract)
            had_binding = manifest.get("web_evidence_contract_binding") is not None
            manifest = ensure_web_evidence_binding(manifest)
            return manifest, {
                "mode": "preserved_same_day_snapshot",
                "group_plan_added": not had_group_plan,
                "web_evidence_binding_added": not had_binding,
            }

    queue_rows = _read_jsonl(queue_path)
    manifest = build_daily_work_manifest_web(
        queue_rows,
        contract,
        store_dir,
        now=now,
        ttl_days=ttl_days,
        source_queue_path=queue_path,
    )
    return manifest, {
        "mode": "built_new_daily_snapshot",
        "group_plan_added": True,
        "web_evidence_binding_added": True,
    }


def apply_snapshot_rollover_inbox_cleanup(manifest, transition, contract, recovery_contract=None):
    """Quarantine only old-snapshot inbox artifacts after an actual daily rollover."""
    if transition.get("mode") != "built_new_daily_snapshot":
        return {"moved": [], "preserved_unrecognized": []}
    recovery_contract = recovery_contract or load_recovery_contract()
    return quarantine_stale_snapshot_inbox(
        contract["paths"]["submission_inbox_dir"],
        manifest["snapshot_id"],
        recovery_contract["invalid_expected_artifact_recovery"]["quarantine_dir"],
    )


def main():
    parser = argparse.ArgumentParser(description="Build or preserve one complete fixed daily web-evidence dossier backlog snapshot")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--queue", default="data/production/pre_ai/chatgpt_taste_queue.jsonl")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    parser.add_argument("--output", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--ttl-days", type=int)
    args = parser.parse_args()

    contract = load_contract(args.contract)
    manifest, transition = build_or_preserve_daily_work(
        contract=contract,
        queue_path=args.queue,
        store_dir=args.store_dir,
        output_path=args.output,
        ttl_days=args.ttl_days,
    )
    stale_cleanup = apply_snapshot_rollover_inbox_cleanup(manifest, transition, contract)
    atomic_write_json(args.output, manifest)
    projection = write_worker_projection(manifest, contract)
    print(json.dumps({
        "mode": transition["mode"],
        "group_plan_added": transition["group_plan_added"],
        "web_evidence_binding_added": transition["web_evidence_binding_added"],
        "web_evidence_contract_binding": manifest["web_evidence_contract_binding"],
        "status": manifest["status"],
        "snapshot_id": manifest["snapshot_id"],
        "prepared_for_date": manifest["prepared_for_date"],
        "source_queue_sha256": manifest["source_queue_sha256"],
        "source_row_count": manifest["source_row_count"],
        "eligible_scope_count": manifest["eligible_scope_count"],
        "prepared_required_count": manifest["prepared_required_count"],
        "completed_required_count": manifest["completed_required_count"],
        "current_checkpoint_count": manifest["current_checkpoint_count"],
        "remaining_required_count": manifest["remaining_required_count"],
        "full_backlog_complete": manifest["full_backlog_complete"],
        "worker_index_path": projection["index_path"],
        "worker_descriptor_count": projection["descriptor_count"],
        "worker_canonical_expected_sequence": projection["index"]["canonical_expected_sequence"],
        "stale_inbox_quarantined_count": len(stale_cleanup["moved"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from taste_steam_review_dossier import atomic_write_json, canonical_sha256, dossier_path
from taste_steam_review_dossier_daily import (
    build_submission_group_plan,
    ensure_submission_group_plan,
    load_contract,
    progress_fields,
    validate_manifest,
)
from taste_steam_review_dossier_group_progress import ensure_group_progress
from taste_steam_review_dossier_recovery import (
    load_recovery_contract,
    quarantine_stale_snapshot_inbox,
)
from taste_steam_review_dossier_strict import current_worker_contract_binding
from taste_steam_review_dossier_web import (
    _PACKAGE_IDENTITY_POLICY_REVISION,
    _STORY_DLC_SCOPE_POLICY_REVISION,
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


def _ordered_unique_numeric(values):
    out = []
    seen = set()
    for value in values if isinstance(values, list) else []:
        appid = str(value or "")
        if not appid.isdigit() or appid in seen:
            continue
        seen.add(appid)
        out.append(appid)
    return out


def _snapshot_identity(manifest, contract):
    """Bind snapshot identity to semantic evidence contract and canonical group boundary."""
    return canonical_sha256({
        "prepared_for_date": manifest["prepared_for_date"],
        "source_queue_sha256": manifest["source_queue_sha256"],
        "eligible_scope_sha256": manifest["eligible_scope_sha256"],
        "identity_blocked_sha256": manifest["identity_blocked_sha256"],
        "package_member_mapping_sha256": manifest["package_member_mapping_sha256"],
        "story_dlc_scope_policy_revision": manifest["story_dlc_scope_policy_revision"],
        "story_dlc_scope_sha256": manifest["story_dlc_scope_sha256"],
        "prepared_required_sha256": manifest["prepared_required_sha256"],
        "ttl_days": manifest["ttl_days"],
        "web_evidence_contract_binding": current_worker_contract_binding(),
        "canonical_group_size": int(contract["checkpointing"]["checkpoint_size"]),
    })


def _rebind_snapshot_and_plan(manifest, contract):
    """Create the immutable snapshot/group binding after all package mappings are known."""
    checkpoint_size = int(contract["checkpointing"]["checkpoint_size"])
    manifest["web_evidence_contract_binding"] = current_worker_contract_binding()
    manifest["checkpoint_size"] = checkpoint_size
    snapshot_id = _snapshot_identity(manifest, contract)
    manifest["snapshot_id"] = snapshot_id
    manifest["submission_group_plan"] = build_submission_group_plan(
        snapshot_id=snapshot_id,
        prepared_required_sha256=manifest["prepared_required_sha256"],
        prepared_required_items=manifest["prepared_required_items"],
        checkpoint_size=checkpoint_size,
        scope_source=manifest["scope_source"],
        source_queue_sha256=manifest["source_queue_sha256"],
    )
    manifest.update(progress_fields(
        snapshot_id,
        manifest["prepared_required_items"],
        list(manifest["prepared_required_items"]),
        checkpoint_size,
    ))
    manifest.pop("group_progress", None)
    manifest = ensure_group_progress(manifest, contract)
    validate_manifest(manifest, contract)
    return manifest


def bind_package_member_mappings(manifest, contract, family_graph):
    """Bind commercial package identity without reintroducing package semantic work."""
    if not isinstance(family_graph, dict) or not isinstance(family_graph.get("families"), list):
        raise ValueError("canonical family graph is missing or malformed")
    if int(manifest.get("completed_required_count") or 0) != 0:
        raise ValueError("package identity binding may only be applied to a freshly prepared snapshot")

    scope_appids = set(str(appid) for appid in manifest.get("ordered_appids") or [])
    title_by_appid = {}
    for family in family_graph["families"]:
        if not isinstance(family, dict) or family.get("family_type") != "base_game":
            continue
        appids = _ordered_unique_numeric(family.get("base_appids"))
        if len(appids) != 1:
            continue
        title = str(family.get("primary_title") or "").strip()
        if title:
            title_by_appid[appids[0]] = title

    mappings = []
    for family in family_graph["families"]:
        if not isinstance(family, dict) or family.get("family_type") != "franchise_bundle":
            continue
        member_appids = _ordered_unique_numeric(family.get("base_appids"))
        if not member_appids or not scope_appids.intersection(member_appids):
            continue
        package_key = str(family.get("taste_subject_key") or "")
        package_title = str(family.get("primary_title") or "").strip()
        family_id = str(family.get("family_id") or "")
        if not package_key.startswith("Sub_") or not package_title or not family_id:
            raise ValueError("canonical franchise bundle identity is incomplete")

        members = []
        for appid in member_appids:
            title = title_by_appid.get(appid)
            if not title:
                raise ValueError(f"canonical package member title unresolved for {package_key} appid {appid}")
            members.append({
                "appid": appid,
                "title": title,
                "dossier_key": f"App_{appid}",
                "dossier_path": dossier_path(contract["paths"]["dossier_store_dir"], appid).as_posix(),
            })

        mappings.append({
            "offer_identity": {
                "key": package_key,
                "family_id": family_id,
                "title": package_title,
                "source_row_appid": None,
            },
            "member_count": len(members),
            "member_appids": member_appids,
            "members": members,
            "aggregation_semantics": "per_game_dossier_reuse_by_appid",
        })

    manifest["package_member_mapping_count"] = len(mappings)
    manifest["package_member_mapping_sha256"] = canonical_sha256(mappings)
    manifest["package_member_mappings"] = mappings
    return _rebind_snapshot_and_plan(manifest, contract)


def build_or_preserve_daily_work(
    *,
    contract,
    queue_path,
    store_dir,
    output_path,
    family_graph_path=None,
    ttl_days=None,
    now=None,
):
    """Preserve only a same-day snapshot whose identity and evidence/group binding are still compatible."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    prepared_for_date = now.astimezone(_SAMARA).date().isoformat()
    output_path = Path(output_path)
    expected_binding = current_worker_contract_binding()
    expected_group_size = int(contract["checkpointing"]["checkpoint_size"])

    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        existing_date = str(existing.get("prepared_for_date") or "")
        if existing_date > prepared_for_date:
            raise ValueError(
                f"existing dossier snapshot date {existing_date} is ahead of current Samara date {prepared_for_date}"
            )
        compatible_same_day = (
            existing_date == prepared_for_date
            and existing.get("identity_policy_revision") == _PACKAGE_IDENTITY_POLICY_REVISION
            and existing.get("story_dlc_scope_policy_revision") == _STORY_DLC_SCOPE_POLICY_REVISION
            and existing.get("web_evidence_contract_binding") == expected_binding
            and existing.get("checkpoint_size") == expected_group_size
        )
        if compatible_same_day:
            validate_manifest(existing, contract)
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
    if family_graph_path is not None:
        family_graph = json.loads(Path(family_graph_path).read_text(encoding="utf-8"))
        manifest = bind_package_member_mappings(manifest, contract, family_graph)
    else:
        manifest = _rebind_snapshot_and_plan(manifest, contract)
    return manifest, {
        "mode": "built_new_daily_snapshot",
        "group_plan_added": True,
        "web_evidence_binding_added": True,
    }


def apply_snapshot_rollover_inbox_cleanup(manifest, transition, contract, recovery_contract=None):
    """Quarantine only old-snapshot inbox artifacts after an actual daily rollover or contract rebuild."""
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
    parser.add_argument("--family-graph", default="data/production/pre_ai/family_graph.json")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    parser.add_argument("--output", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--ttl-days", type=int)
    args = parser.parse_args()

    contract = load_contract(args.contract)
    manifest, transition = build_or_preserve_daily_work(
        contract=contract,
        queue_path=args.queue,
        family_graph_path=args.family_graph,
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
        "normal_first_pass_complete": manifest["group_progress"]["normal_first_pass_complete"],
        "accepted_group_count": manifest["group_progress"]["accepted_group_count"],
        "failed_group_count": manifest["group_progress"]["failed_group_count"],
        "pending_group_count": manifest["group_progress"]["pending_group_count"],
        "package_member_mapping_count": manifest["package_member_mapping_count"],
        "story_dlc_considered_count": manifest["story_dlc_scope"]["considered_count"],
        "story_dlc_story_eligible_count": manifest["story_dlc_scope"]["story_eligible_count"],
        "story_dlc_non_story_excluded_count": manifest["story_dlc_scope"]["non_story_excluded_count"],
        "story_dlc_ambiguous_excluded_count": manifest["story_dlc_scope"]["ambiguous_excluded_count"],
        "worker_index_path": projection["index_path"],
        "worker_descriptor_count": projection["descriptor_count"],
        "worker_next_pending_sequence": projection["index"]["next_pending_sequence"],
        "stale_inbox_quarantined_count": len(stale_cleanup["moved"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

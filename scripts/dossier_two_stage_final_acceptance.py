#!/usr/bin/env python3
"""INACTIVE GitHub-owned Research -> Assembly -> original strict group bridge.

No live CLI, inbox scan, receipt publication, queue, canonical writer or scheduler
is added. The only executable interface is guarded disposable-Git offline QA.
The existing buffered Dossier drain remains the sole final acceptance writer.
"""
import copy
import json
import tempfile
from pathlib import Path

from dossier_two_stage_async_buffer import (
    frozen_buffer, inspect_buffered_assembly_candidate,
)
from dossier_two_stage_contract_guard import CONFIG, canonical_sha256
from dossier_two_stage_staging import (
    blob, file_at, first_parent_contains, git, json_at, marker_context, strict_json,
)
from taste_steam_review_dossier_buffered import (
    drain_buffered_groups, expected_buffer_path, validate_buffer_artifact,
)
from taste_steam_review_dossier_daily import (
    BUFFER_GROUP_SCHEMA, validate_group_plan, validate_manifest,
)
from taste_steam_review_dossier_group_progress import ensure_group_progress

CONTRACT_PATH = CONFIG / "dossier_two_stage_final_acceptance_bridge_contract.json"
STATUS_VALID = "valid_pending_original_group"
STATUS_MISSING = "missing_not_yet_submitted"
STATUS_INVALID = "invalid_item_quarantined_locally"
STATUS_GAP = "non_ready_semantic_gap"
STATUS_ACCEPTED = "already_canonically_accepted_no_replay"
STATUS_GROUP_READY = "strict_original_group_ready_for_existing_writer_offline_only"
STATUS_GROUP_PENDING = "original_group_incomplete_no_canonical_acceptance"


def offline_gate(repo, *, offline_fixture=False):
    """No live path even if a caller toggles a flag or forges a receipt."""
    spec = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if (spec.get("schema") != "DOSSIER-TWO-STAGE-FINAL-ACCEPTANCE-BRIDGE-V1"
            or spec.get("active") is not False
            or spec.get("authorized_for_canonical_ingest") is not False
            or spec.get("executable_in_production") is not False
            or type(spec.get("cross_pr_research_original_year_fix_verified")) is not bool
            or spec.get("shared_writer", {}).get("concurrency_group")
            != "taste-steam-review-dossier-canonical-writer"):
        raise ValueError("final bridge contract is not explicitly inactive")
    if not offline_fixture:
        raise ValueError("final bridge is disabled for live GitHub and production")
    root = Path(repo).resolve()
    scratch = Path(tempfile.gettempdir()).resolve()
    if (not root.is_relative_to(scratch) or root == scratch
            or not (root / ".git").exists()
            or not (root / ".dossier-final-offline-fixture").is_file()
            or root == Path.cwd().resolve()
            or Path.cwd().resolve().is_relative_to(root)):
        raise ValueError("offline final bridge requires a separate disposable Git fixture")
    return root


def _descriptor_at_frozen_assembly(repo, marker, descriptor, manifest):
    frozen, _ = marker_context(repo, marker, "assembly")
    path = ("data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
            f"{descriptor['snapshot_id']}/g{descriptor['sequence']:06d}.json")
    header = {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1",
        "schema_version": 1,
        "group_plan_sha256": manifest["submission_group_plan"]["group_plan_sha256"],
        "group_count": manifest["submission_group_plan"]["group_count"],
        "web_evidence_contract_binding": manifest["web_evidence_contract_binding"],
    }
    original = json_at(repo, frozen, path)
    if original != {**header, **descriptor}:
        raise ValueError("stale or altered original GitHub-owned frozen group descriptor")
    index = json_at(repo, frozen, "data/production/pre_ai/taste_steam_review_dossier_worker_index.json")
    if (index.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2"
            or index.get("snapshot_id") != descriptor["snapshot_id"]
            or index.get("prepared_required_sha256") != descriptor["prepared_required_sha256"]
            or index.get("group_plan_sha256") != header["group_plan_sha256"]
            or descriptor["sequence"] not in index.get("pending_group_sequences", [])):
        raise ValueError("original frozen worker index did not authorize this group")
    return frozen


def _inspect_item(repo, descriptor, manifest, slot, ref):
    """All locators are supplied by GitHub. No auto-discovery/retry or rebind."""
    if ref is None or ref.get("result_commit") is None:
        return {"status": STATUS_MISSING, "canonical_dossier_accepted": False}, None
    try:
        if not isinstance(ref, dict) or set(ref) != {
                "sequence", "item_index", "marker_commit", "buffer_path",
                "work_path", "result_commit"}:
            raise ValueError("item locator shape is not exact")
        if ref["sequence"] != descriptor["sequence"] or ref["item_index"] != slot:
            raise ValueError("item locator is out of original order")
        marker = ref["marker_commit"]
        frozen = _descriptor_at_frozen_assembly(repo, marker, descriptor, manifest)
        buff = frozen_buffer(
            repo, marker_commit=marker, buffer_path=ref["buffer_path"],
            phase="assembly")
        matching = [e for e in buff["items"] if e["work_path"] == ref["work_path"]]
        if len(matching) != 1:
            raise ValueError("work is absent from frozen GitHub authorization")
        e = matching[0]
        item = descriptor["items"][slot]
        if (e["snapshot_id"] != descriptor["snapshot_id"]
                or e["group_sequence"] != descriptor["sequence"]
                or e["item_index"] != slot
                or e["appid"] != item["appid"]):
            raise ValueError("frozen item assignment differs from original group")
        plan = json_at(repo, frozen, e["work_path"])
        prepared = json_at(repo, frozen, plan["research_prepared_work_path"])
        for key, expected in (
            ("snapshot_id", descriptor["snapshot_id"]),
            ("group_sequence", descriptor["sequence"]),
            ("item_index", slot),
            ("appid", item["appid"]),
            ("title", item["title"]),
            ("group_sha256", descriptor["group_sha256"]),
            ("group_plan_sha256", manifest["submission_group_plan"]["group_plan_sha256"]),
            ("items_sha256", descriptor["items_sha256"]),
            ("prepared_required_sha256", descriptor["prepared_required_sha256"]),
            ("scope_source", descriptor["scope_source"]),
            ("source_queue_sha256", descriptor["source_queue_sha256"]),
        ):
            if prepared.get(key) != expected:
                raise ValueError("prepared original Research/Assembly item mismatch: " + key)
        checked = inspect_buffered_assembly_candidate(
            repo, marker_commit=marker, buffer_path=ref["buffer_path"],
            work_path=ref["work_path"], result_commit=ref["result_commit"])
        if checked["status"] != "strict_item_valid_pending_existing_atomic_group_ingest":
            if checked["status"] == "research_rejected_item_chain_quarantined":
                return {"status": STATUS_INVALID, "reason": "Research chain rejected",
                        "canonical_dossier_accepted": False}, None
            return {"status": STATUS_GAP, "reason": checked["status"],
                    "canonical_dossier_accepted": False}, None
        # Historical proof is insufficient if HEAD subsequently rewrote the
        # original create-only Research or Assembly transport.
        head = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
        if not first_parent_contains(repo, ref["result_commit"], head):
            raise ValueError("Assembly submission not in current Git history")
        raw = file_at(repo, ref["result_commit"], checked["result_path"])
        if blob(repo, head, checked["result_path"]) != blob(
                repo, ref["result_commit"], checked["result_path"]):
            raise ValueError("Assembly transport changed since its original commit")
        result = strict_json(raw)
        rt = result["research_transport"]
        if blob(repo, head, rt["research_package_path"]) != rt["research_package_blob_sha"]:
            raise ValueError("Research transport changed since its original commit")
        dossier = result["payload"]["dossier"]
        return {"status": STATUS_VALID, "canonical_dossier_accepted": False,
                "result_commit": ref["result_commit"],
                "dossier_sha256": canonical_sha256(dossier)}, copy.deepcopy(dossier)
    except (ValueError, TypeError, KeyError, IndexError, OSError) as exc:
        return {"status": STATUS_INVALID, "reason": str(exc),
                "canonical_dossier_accepted": False}, None


def inspect_original_groups(repo, *, manifest, contract, item_locators,
                            offline_fixture=False):
    """Pure local dispositions; ready groups still have ZERO canonical authority.

    Input contains exact immutable Git locators, never an Assembly worker
    "ready" assertion or claimed accepted Research/GitHub receipt.
    """
    offline_gate(repo, offline_fixture=offline_fixture)
    if type(item_locators) is not list:
        raise ValueError("GitHub item locator list required")
    current = ensure_group_progress(copy.deepcopy(manifest), contract)
    validate_manifest(current, contract)
    group_plan = validate_group_plan(current, contract, required=True)
    if int(contract["checkpointing"]["checkpoint_size"]) != 3:
        raise ValueError("unexpected strict original three-game checkpoint boundary")
    by_slot = {}
    invalid_locators = []
    for ref in item_locators:
        if not isinstance(ref, dict) or type(ref.get("sequence")) is not int or type(ref.get("item_index")) is not int:
            invalid_locators.append({"status": STATUS_INVALID, "reason": "malformed item slot"})
            continue
        slot = (ref["sequence"], ref["item_index"])
        by_slot.setdefault(slot, []).append(ref)
    decisions = []
    ready = []
    progress = {p["sequence"]: p["state"] for p in current["group_progress"]["groups"]}
    for descriptor in group_plan["groups"]:
        seq = descriptor["sequence"]
        if progress[seq] != "pending":
            decisions.append({"sequence": seq, "status": STATUS_ACCEPTED if progress[seq] == "accepted"
                              else STATUS_GROUP_PENDING, "items": [],
                              "canonical_dossier_accepted": progress[seq] == "accepted",
                              "deep_ready_issued": False})
            continue
        results, docs = [], []
        for index in range(len(descriptor["items"])):
            slot = (seq, index)
            refs = by_slot.pop(slot, [])
            if len(refs) > 1:
                results.append({"status": STATUS_INVALID, "reason": "duplicate slot locator",
                                "canonical_dossier_accepted": False})
                continue
            disposition, dossier = _inspect_item(
                repo, descriptor, current, index, refs[0] if refs else None)
            results.append(disposition)
            if dossier is not None:
                docs.append(dossier)
        decision = {"sequence": seq, "status": STATUS_GROUP_PENDING,
                    "items": results, "canonical_dossier_accepted": False,
                    "deep_ready_issued": False}
        if len(descriptor["items"]) == 3 and len(docs) == 3 and all(
                x["status"] == STATUS_VALID for x in results):
            artifact = {
                "schema": BUFFER_GROUP_SCHEMA, "schema_version": 1,
                **copy.deepcopy(descriptor), "dossiers": docs,
            }
            try:
                validate_buffer_artifact(artifact, descriptor, current, contract)
            except (ValueError, KeyError, TypeError) as exc:
                decision["group_validator_failure"] = str(exc)
                decision["status"] = STATUS_GROUP_PENDING
            else:
                ready.append({"sequence": seq, "artifact": artifact})
                decision["status"] = STATUS_GROUP_READY
        decisions.append(decision)
    for refs in by_slot.values():
        for _ in refs:
            invalid_locators.append({"status": STATUS_INVALID, "reason": "foreign or replayed slot"})
    return {"schema": "DOSSIER-TWO-STAGE-OFFLINE-HANDOFF-V1",
            "snapshot_id": current["snapshot_id"],
            "manifest_sha256": canonical_sha256(current),
            "decisions": decisions, "ready": ready,
            "item_locators": copy.deepcopy(item_locators),
            "unmatched_locators": invalid_locators,
            "canonical_dossier_accepted": False, "deep_ready_issued": False}


def offline_existing_writer_handoff(repo, *, inspection, manifest_path, contract,
                                    offline_fixture=False):
    """Test-only reuse of the exact existing writer: never callable on live checkout.

    The real multi-file transaction, shared Actions lock, rebase/push and Deep
    recomputation are still owned by the existing canonical writer workflow.
    """
    root = offline_gate(repo, offline_fixture=offline_fixture)
    manifest_path = Path(manifest_path).resolve()
    inbox = Path(contract["paths"]["submission_inbox_dir"]).resolve()
    store = Path(contract["paths"]["dossier_store_dir"]).resolve()
    if not all(p.is_relative_to(root) and p != root for p in (manifest_path, inbox, store)):
        raise ValueError("offline writer destinations must remain inside disposable Git")
    if inspection.get("schema") != "DOSSIER-TWO-STAGE-OFFLINE-HANDOFF-V1":
        raise ValueError("untrusted offline handoff")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = ensure_group_progress(manifest, contract)
    validate_manifest(manifest, contract)
    if (inspection.get("snapshot_id") != manifest["snapshot_id"]
            or inspection.get("manifest_sha256") != canonical_sha256(manifest)):
        raise ValueError("stale canonical manifest between inspection and writer")
    # An inspector verdict is never an accepted receipt: rerun all immutable
    # Git and strict V2 validations immediately at the offline writer boundary.
    reviewed = inspect_original_groups(
        root, manifest=manifest, contract=contract,
        item_locators=inspection.get("item_locators"), offline_fixture=True)
    if (reviewed["ready"] != inspection.get("ready")
            or reviewed["manifest_sha256"] != inspection["manifest_sha256"]):
        raise ValueError("untrusted, forged or stale final group handoff")
    groups = validate_group_plan(manifest, contract, required=True)["groups"]
    pending = {e["sequence"] for e in manifest["group_progress"]["groups"]
               if e["state"] == "pending"}
    staged, collisions = [], []
    for entry in inspection["ready"]:
        seq = entry["sequence"]
        if type(seq) is not int or seq not in pending:
            raise ValueError("already accepted, stale or unauthorized group replay")
        desc = groups[seq - 1]
        validate_buffer_artifact(entry["artifact"], desc, manifest, contract)
        path = expected_buffer_path(desc, contract).resolve()
        if not path.is_relative_to(inbox):
            raise ValueError("existing group writer path escapes isolated inbox")
        if path.exists():
            collisions.append(seq)
            continue
        staged.append((seq, path, entry["artifact"]))
    if len(set(seq for seq, _, _ in staged)) != len(staged):
        raise ValueError("duplicate canonical group writer handoff")
    for _, path, artifact in staged:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as out:
            json.dump(artifact, out, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            out.write("\n")
    # No bypass: existing drain rechecks the complete original 3-game group,
    # applies canonical progress and persists all Dossiers in its writer.
    result = drain_buffered_groups(
        manifest_path=manifest_path, contract=contract, buffer_dir=inbox,
        store_dir=store, failed_quarantine_root=root / "quarantine" / "failed",
        failure_audit_path=root / "audit" / "failures.jsonl",
        retryable_rejection_root=root / "quarantine" / "rejected",
        rejection_audit_path=root / "audit" / "rejections.jsonl",
        terminal_receipt_archive_root=root / "audit" / "terminals",
        frozen_authority_audit_path=root / "audit" / "frozen.jsonl",
        repo_root=root,
    )
    return {"writer": "existing_drain_buffered_groups_only", "staged_sequences": [
        seq for seq, _, _ in staged], "collision_sequences": collisions,
        "existing_writer_result": result}


if __name__ == "__main__":
    raise SystemExit("Inactive fixture API only; no CLI, production or live GitHub entrypoint")

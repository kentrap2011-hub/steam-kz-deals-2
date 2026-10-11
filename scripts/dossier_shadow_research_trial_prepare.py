#!/usr/bin/env python3
"""Propose (never publish/authorize) the exact GitHub-owned six-group freeze.

This is a deterministic preparation tool for a later, separately approved
GitHub control-plane transaction. Its JSON stdout is NOT a run marker.
Only six approved historical group writer receipts are checked, not 114 sources.
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from dossier_shadow_pilot_preflight import (
    verify_offline_preflight, PROPOSAL_CONTRACTS, SCHEMA,
)
from dossier_shadow_real_baseline_audit import (
    AUDIT, MANIFEST, original_plan, writer_receipts, show, blob,
)
from dossier_shadow_research_trial import (
    CONTRACT, DECISION, PROMPT, RESEARCH_SCHEMA, TRIAL, sha, require,
)
from dossier_two_stage_contract_guard import canonical_sha256


def prepare(repo):
    repo = Path(repo).resolve()
    require((repo / ".git").exists(), "Git checkout required for bounded proposal")
    source = json.loads((repo / DECISION).read_text("utf-8"))
    pinned = source["historical_reference"]
    commit = pinned["head"]
    # Strong historic writer proof is made in a separate disposable detached
    # checkout because existing PR201 preflight requires exact historical HEAD.
    with tempfile.TemporaryDirectory(prefix="dossier-shadow-6x3-") as root:
        replica = Path(root) / "historical"
        cmd = subprocess.run(["git", "clone", "--quiet", "--no-local",
                              "--no-hardlinks", str(repo), str(replica)],
                             capture_output=True)
        require(cmd.returncode == 0, "isolated Git clone unavailable")
        cmd = subprocess.run(["git", "-C", str(replica), "checkout", "--quiet",
                              "--detach", commit], capture_output=True)
        require(cmd.returncode == 0, "exact historical head not in clone")
        (replica / ".dossier-final-offline-fixture").write_text("six-group proof only\n")
        require(blob(replica, commit, MANIFEST) == pinned["work_blob"]
                and blob(replica, commit, AUDIT) == pinned["audit_blob"],
                "historical work/audit Git blobs drifted")
        manifest = json.loads(show(replica, commit, MANIFEST))
        contract = json.loads(show(replica, commit,
                                   "config/taste_steam_review_dossier_contract.json"))
        accepted = {g["sequence"] for g, _ in original_plan(manifest)}
        requests = source["scope"]["groups"]
        require([x["sequence"] for x in requests] == [3, 8, 13, 15, 18, 20]
                and len(requests) == 6 and set(accepted).issuperset(
                    {x["sequence"] for x in requests}),
                "approved original accepted group membership changed")
        groups = manifest["submission_group_plan"]["groups"]
        receipts = writer_receipts(replica, commit, manifest["snapshot_id"])
        proposals = {p: blob(replica, commit, p) for p in PROPOSAL_CONTRACTS}
        items = []
        schema_digest = canonical_sha256(json.loads(
            (repo / RESEARCH_SCHEMA).read_text("utf-8")))
        for selected in requests:
            seq = selected["sequence"]
            group = groups[seq - 1]
            require(group["sequence"] == seq
                    and group["appids"] == selected["appids"]
                    and group["group_sha256"] == selected["group_sha256"]
                    and len(group["items"]) == 3,
                    "selection changed original group or membership")
            require(seq in receipts, "missing original strict writer receipt")
            writer, parent, line, receipt = receipts[seq]
            original = receipt["authority"]["run_start_authority_commit"]
            descriptor = ("data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                          + group["snapshot_id"] + f"/g{seq:06d}.json")
            descriptor_sha = blob(replica, original, descriptor)
            declared, baselines = [], []
            for ix, item in enumerate(group["items"]):
                appid = str(item["appid"])
                cache_path = item["dossier_path"]
                dossier = json.loads(show(replica, writer, cache_path))
                old_hash = canonical_sha256(dossier)
                legacy = {
                    "appid": appid, "path": cache_path, "commit": writer,
                    "git_blob_sha": blob(replica, writer, cache_path),
                    "canonical_sha256": old_hash,
                }
                declared.append({
                    "appid": appid, "title": item["title"],
                    "original_work_year": dossier["game_identity"]["release_year"],
                })
                baselines.append(legacy)
                # IDs derived from exact original content, not from caller selection.
                aid = f"shadow-{seq:02d}-{appid}-{group['group_sha256'][:12]}"
                prepared = {
                    "assignment_id": aid, "snapshot_id": group["snapshot_id"],
                    "group_sequence": seq, "group_sha256": group["group_sha256"],
                    "prepared_required_sha256": group["prepared_required_sha256"],
                    "group_plan_sha256": manifest["submission_group_plan"]["group_plan_sha256"],
                    "items_sha256": group["items_sha256"], "item_index": ix,
                    "appid": appid, "title": item["title"],
                    "scope_source": group["scope_source"],
                    "source_queue_sha256": group["source_queue_sha256"],
                    "research_contract_sha256": schema_digest,
                    "web_evidence_contract_binding": manifest["web_evidence_contract_binding"],
                }
                items.append({
                    "group_sequence": seq, "item_index": ix, "appid": appid,
                    "assignment": prepared, "descriptor_blob_sha": descriptor_sha,
                    "old_cache_path": cache_path,
                    "old_cache_blob_sha": legacy["git_blob_sha"],
                    "old_cache_sha256": old_hash,
                    "old_year": declared[-1]["original_work_year"],
                    "old_writer_commit": writer,
                    "old_receipt_line_sha256": sha(line),
                })
            request = {
                "schema": SCHEMA, "target_head": commit,
                "original_manifest_commit": original,
                "legacy_manifest_path": MANIFEST, "legacy_writer_commit": writer,
                "legacy_writer_parent": parent, "group_sequence": seq,
                "descriptor_path": descriptor, "descriptor_blob_sha": descriptor_sha,
                "original_games": declared, "legacy_baselines": baselines,
                "audit_line_sha256": sha(line),
                "proposal_contract_blobs": proposals,
            }
            result = verify_offline_preflight(replica, request=request,
                                              contract=contract)
            require(result["preflight_ready"] is True,
                    "strict original 3-item group writer receipt rejected")
    record = {
        "schema": "DOSSIER-SHADOW-RESEARCH-BUFFER-V1",
        "version": 1, "trial_id": TRIAL,
        "decision_blob_sha": blob(repo, "HEAD", DECISION),
        "source_head": commit,
        "source_work_blob_sha": pinned["work_blob"],
        "source_audit_blob_sha": pinned["audit_blob"],
        "prompt_blob_sha": blob(repo, "HEAD", PROMPT),
        "research_schema_blob_sha": blob(repo, "HEAD", RESEARCH_SCHEMA),
        "trial_contract_blob_sha": blob(repo, "HEAD", CONTRACT),
        "groups": requests,
        "items": items,
    }
    record["research_buffer_id"] = canonical_sha256(
        {"trial_id": TRIAL, "groups": requests, "items": items})
    require(len(items) == 18, "unexpected result count")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--propose-buffer", action="store_true", required=True)
    args = parser.parse_args()
    proposed = prepare(Path.cwd())
    print(json.dumps(proposed, sort_keys=True, ensure_ascii=False, indent=2))
    # Explicitly NOT a trusted marker/authorization even if stdout is saved:
    print("PROPOSAL_ONLY_NOT_AN_AUTHORIZATION", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()

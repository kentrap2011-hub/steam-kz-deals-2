#!/usr/bin/env python3
"""Read-only, pinned real Dossier baseline audit. NOT a pilot, selector, or writer.

Run only against a separate, marked disposable Git clone with complete history.
The real repository is used as a clone source; no semantic work or live ingest.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from dossier_shadow_pilot_preflight import (
    AUDIT, MANIFEST, PROPOSAL_CONTRACTS, SCHEMA, verify_offline_preflight,
)

HEX40 = re.compile(r"^[0-9a-f]{40}$")


def git(repo, *args):
    run = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if run.returncode:
        raise ValueError("GIT_EVIDENCE_UNAVAILABLE: " + args[0])
    return run.stdout


def show(repo, commit, path):
    return git(repo, "show", commit + ":" + path)


def blob(repo, commit, path):
    return git(repo, "rev-parse", commit + ":" + path).decode().strip()


def original_plan(manifest, accepted_only=True):
    groups = manifest["submission_group_plan"]["groups"]
    states = manifest["group_progress"]["groups"]
    if len(groups) != manifest["submission_group_plan"]["group_count"] or len(groups) != len(states):
        raise ValueError("GROUP_PLAN_PROGRESS_CARDINALITY_MISMATCH")
    seen = set()
    results = []
    for group, state in zip(groups, states):
        seq = group["sequence"]
        if (seq in seen or state["sequence"] != seq
                or state["group_sha256"] != group["group_sha256"]
                or len(group["appids"]) != 3
                or len(set(group["appids"])) != 3
                or [str(x["appid"]) for x in group["items"]] != group["appids"]):
            raise ValueError("GROUP_PLAN_BINDING_MISMATCH")
        seen.add(seq)
        if not accepted_only or state["state"] == "accepted":
            results.append((group, state))
    return results


def writer_receipts(repo, target_head, snapshot_id):
    """Map exact current-snapshot receipt bytes to their first-parent audit writer."""
    history = git(
        repo, "log", "--first-parent", "--max-count=500",
        "--format=%H", target_head, "--", AUDIT,
    ).decode().splitlines()
    if len(history) == 500:
        raise ValueError("AUDIT_HISTORY_SCAN_BOUND_REACHED")
    found = {}
    for writer in history:
        parents = git(repo, "rev-list", "--parents", "-n", "1", writer).decode().split()
        if not parents:
            raise ValueError("AUDIT_HISTORY_UNAVAILABLE")
        parent = parents[1] if len(parents) > 1 else None
        after = show(repo, writer, AUDIT)
        try:
            before = show(repo, parent, AUDIT) if parent else b""
        except ValueError:
            before = b""
        if not after.startswith(before):
            raise ValueError("AUDIT_NOT_APPEND_ONLY")
        for line in after[len(before):].splitlines():
            record = json.loads(line)
            if (record.get("authority_snapshot_id") != snapshot_id
                    or record.get("outcome") != "dossier_candidate_accepted_current_snapshot"):
                continue
            key = record["authority_sequence"]
            if key in found:
                raise ValueError("DUPLICATE_CURRENT_SNAPSHOT_RECEIPT")
            found[key] = (writer, parent, line, record)
    return found


def reason_code(exc):
    msg = str(exc)
    if msg.startswith("GIT_EVIDENCE_UNAVAILABLE"):
        return "GIT_EVIDENCE_UNAVAILABLE"
    if "original" in msg.lower() or "year" in msg.lower():
        return "ORIGINAL_IDENTITY_OR_YEAR_NOT_PROVEN"
    if "receipt" in msg.lower() or "audit" in msg.lower():
        return "HISTORICAL_WRITER_RECEIPT_NOT_PROVEN"
    if "marker" in msg.lower():
        return "FROZEN_RUN_START_NOT_PROVEN"
    if "baseline" in msg.lower() or "cache" in msg.lower():
        return "CACHE_BINDING_NOT_PROVEN"
    if "manifest" in msg.lower() or "group" in msg.lower():
        return "ORIGINAL_GROUP_BINDING_NOT_PROVEN"
    return "STRICT_OFFLINE_PREFLIGHT_REJECTED"


def audit(repo, target_head, expected_work_blob, expected_audit_blob, expected_accepted):
    if not HEX40.fullmatch(target_head):
        raise ValueError("INVALID_TARGET_HEAD")
    if (blob(repo, target_head, MANIFEST) != expected_work_blob
            or blob(repo, target_head, AUDIT) != expected_audit_blob):
        raise ValueError("PINNED_SOURCE_BLOB_MISMATCH")
    manifest = json.loads(show(repo, target_head, MANIFEST))
    contract = json.loads(show(repo, target_head, "config/taste_steam_review_dossier_contract.json"))
    original_groups = original_plan(manifest)
    if len(original_groups) != expected_accepted:
        raise ValueError("ACCEPTED_COUNT_CHANGED_AT_PIN")
    receipts = writer_receipts(repo, target_head, manifest["snapshot_id"])
    target_lines = show(repo, target_head, AUDIT).splitlines()
    frozen_receipts = {
        (json.loads(x).get("authority_sequence"), x)
        for x in target_lines
        if json.loads(x).get("authority_snapshot_id") == manifest["snapshot_id"]
        and json.loads(x).get("outcome") == "dossier_candidate_accepted_current_snapshot"
    }
    proposals = {p: blob(repo, target_head, p) for p in PROPOSAL_CONTRACTS}
    results = []
    for group, state in original_groups:
        seq = group["sequence"]
        row = {
            "sequence": seq, "appids": group["appids"],
            "progress": state["state"], "receipt_present": seq in receipts,
            "writer_commit": None, "identity_and_invariance": "not_verified",
            "git_evidence_status": "not_verifiable",
            "reason_codes": [], "actions_provenance": "unverified",
        }
        try:
            if seq not in receipts:
                raise ValueError("HISTORICAL_WRITER_RECEIPT_NOT_PROVEN")
            writer, parent, line, receipt = receipts[seq]
            row["writer_commit"] = writer
            if ((seq, line) not in frozen_receipts
                    or receipt.get("authority_group_sha256") != group["group_sha256"]
                    or receipt.get("authority_snapshot_id") != group["snapshot_id"]):
                raise ValueError("PINNED_AUDIT_BINDING_MISMATCH")
            marker_parent = receipt["authority"]["run_start_authority_commit"]
            descriptor_path = (
                "data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                + group["snapshot_id"] + "/g" + str(seq).zfill(6) + ".json"
            )
            games, baselines = [], []
            for item in group["items"]:
                appid, path = str(item["appid"]), item["dossier_path"]
                dossier = json.loads(show(repo, writer, path))
                identity = dossier["game_identity"]
                games.append({
                    "appid": appid, "title": item["title"],
                    "original_work_year": identity["release_year"],
                })
                baselines.append({
                    "appid": appid, "path": path, "commit": writer,
                    "git_blob_sha": blob(repo, writer, path),
                    "canonical_sha256": hashlib.sha256(json.dumps(
                        dossier, sort_keys=True, ensure_ascii=False,
                        separators=(",", ":"), allow_nan=False,
                    ).encode("utf-8")).hexdigest(),
                })
            request = {
                "schema": SCHEMA, "target_head": target_head,
                "original_manifest_commit": marker_parent,
                "legacy_manifest_path": MANIFEST,
                "legacy_writer_commit": writer, "legacy_writer_parent": parent,
                "group_sequence": seq, "descriptor_path": descriptor_path,
                "descriptor_blob_sha": blob(repo, marker_parent, descriptor_path),
                "original_games": games, "legacy_baselines": baselines,
                "audit_line_sha256": hashlib.sha256(line).hexdigest(),
                "proposal_contract_blobs": proposals,
            }
            outcome = verify_offline_preflight(repo, request=request, contract=contract)
            if not outcome["preflight_ready"]:
                raise ValueError("STRICT_OFFLINE_PREFLIGHT_REJECTED")
            row["identity_and_invariance"] = "strict_git_local_pass"
            row["git_evidence_status"] = "eligible"
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            row["reason_codes"].append(reason_code(exc))
        results.append(row)
    accepted = len(original_groups)
    eligible = sum(x["git_evidence_status"] == "eligible" for x in results)
    return {
        "schema": "DOSSIER-SHADOW-REAL-BASELINE-AUDIT-V1",
        "target_head": target_head,
        "work_blob_sha": expected_work_blob, "audit_blob_sha": expected_audit_blob,
        "snapshot_id": manifest["snapshot_id"],
        "original_group_count": manifest["submission_group_plan"]["group_count"],
        "accepted_groups": accepted, "eligible_git_local": eligible,
        "not_verifiable_or_ineligible": accepted - eligible,
        "accepted_games": accepted * 3, "git_local_eligible_games": eligible * 3,
        "external_actions_provenance": "must_be_independently_checked",
        "pilot_authorized": False, "quality_verified": False,
        "canonical_readiness": False, "deep_readiness": False,
        "semantic_execution": False, "rows": results,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target-head", required=True)
    p.add_argument("--expected-work-blob", required=True)
    p.add_argument("--expected-audit-blob", required=True)
    p.add_argument("--expected-accepted", type=int, required=True)
    p.add_argument("--min-preflight-ready", type=int, default=6)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    # Write only within the OS temporary directory; no checkout/project writes.
    root = Path.cwd().resolve()
    with tempfile.TemporaryDirectory(prefix="dossier-shadow-real-audit-") as directory:
        replica = Path(directory) / "disposable-replica"
        run = subprocess.run(
            ["git", "clone", "--quiet", "--no-local", "--no-hardlinks",
             str(root), str(replica)], capture_output=True,
        )
        if run.returncode:
            raise SystemExit("DISPOSABLE_CLONE_FAILED (no production writes)")
        git(replica, "checkout", "--detach", args.target_head)
        (replica / ".dossier-final-offline-fixture").write_text(
            "read-only, disposable baseline verification\n", encoding="utf-8"
        )
        result = audit(
            replica, args.target_head, args.expected_work_blob,
            args.expected_audit_blob, args.expected_accepted,
        )
    allowed_temps = {Path(tempfile.gettempdir()).resolve()}
    if os.environ.get("RUNNER_TEMP"):
        allowed_temps.add(Path(os.environ["RUNNER_TEMP"]).resolve())
    target = args.out.resolve()
    if not any(target.is_relative_to(temp) and target != temp
               for temp in allowed_temps):
        raise SystemExit("OUTPUT_MUST_BE_IN_OS_TEMP")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, sort_keys=True))
    for row in result["rows"]:
        print("group", row["sequence"], row["git_evidence_status"],
              ",".join(row["reason_codes"]))
    if result["eligible_git_local"] < args.min_preflight_ready:
        raise SystemExit("BLOCKED: fewer than 6 strictly Git-local-verified groups")


if __name__ == "__main__":
    main()

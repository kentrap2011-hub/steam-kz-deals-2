#!/usr/bin/env python3
"""Read-only exact six-item sandbox writer transaction verification.

Run before and after the existing non-force GitHub push. An isolated receipt is
NOT a main canonical or Deep acceptance.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from dossier_lean_canonical_dual import (
    SANDBOX_GRANT, LEAN_SCHEMA, quality_binding, validate_writer_lean,
)
from taste_steam_review_dossier import canonical_sha256

ROOT_STORE = Path("data/control/dossier_notes_v2/batch_pilot_store")
ROOT_RECEIPTS = Path("data/control/dossier_notes_v2/batch_pilot_accepted")
RECEIPT_SCHEMA = "DOSSIER-NOTES-V2-ISOLATED-TRIAL-RECEIPT-V1"


def git_bytes(repo, *arguments):
    p = subprocess.run(["git", "-C", str(repo), *arguments],
                       capture_output=True, check=False)
    if p.returncode:
        raise ValueError("isolated writer Git readback failed: " + " ".join(arguments))
    return p.stdout


def exact_transaction(repo, *, mode):
    if mode not in ("staged", "committed"):
        raise ValueError("invalid sandbox verification mode")
    repo = Path(repo).resolve()
    grant = json.loads(SANDBOX_GRANT.read_text(encoding="utf-8"))
    trial = grant["trial_id"]
    if (grant.get("schema") != "DOSSIER-NOTES-V2-ISOLATED-LEAN-ACCEPTANCE-V1"
            or grant.get("isolated_only") is not True
            or grant.get("exact_six_atomic_persistence") is not True
            or grant.get("canonical_main_acceptance") is not False
            or grant.get("production_enabled") is not False
            or grant.get("deep_enabled") is not False
            or len(grant.get("items", [])) != 6
            or len({r["appid"] for r in grant["items"]}) != 6):
        raise ValueError("not the exact six-item nonproduction writer grant")
    branch = git_bytes(repo, "symbolic-ref", "--short", "HEAD").decode().strip()
    if branch != "sandbox/" + trial:
        # GitHub Actions checkout may retain a detached checkout; it must not
        # use detached HEAD to claim an isolated branch acceptance.
        raise ValueError("acceptance is not on frozen sandbox branch")
    expected = set()
    for row in grant["items"]:
        appid = row["appid"]
        store_path = ROOT_STORE / trial / ("App_" + appid + ".json")
        receipt_path = ROOT_RECEIPTS / trial / (
            "g" + str(row["group_sequence"]).zfill(6)
        ) / (appid + "--" + row["assignment_id"] + ".json")
        for path in (store_path, receipt_path):
            p = repo / path
            if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(repo):
                raise ValueError("sandbox store/receipt missing or unsafe")
            expected.add(path.as_posix())
            repository_bytes = git_bytes(repo, "show",
                                         (":" if mode == "staged" else "HEAD:") + path.as_posix())
            if repository_bytes != p.read_bytes():
                raise ValueError("sandbox accepted bytes differ from Git stage/commit")
        raw = (repo / store_path).read_bytes()
        doc = json.loads(raw.decode("utf-8"))
        receipt = json.loads((repo / receipt_path).read_text(encoding="utf-8"))
        if (doc.get("schema") != LEAN_SCHEMA
                or doc.get("appid") != appid
                or doc.get("title") != row["title"]
                or receipt.get("schema") != RECEIPT_SCHEMA
                or receipt.get("trial_id") != trial
                or receipt.get("marker_commit") != grant["marker_commit"]
                or receipt.get("research_commit") != row["research_commit"]
                or receipt.get("assembly_commit") != row["assembly_commit"]
                or receipt.get("dossier_sha256") != canonical_sha256(doc)
                or receipt.get("dossier_raw_sha256") != hashlib.sha256(raw).hexdigest()
                or receipt.get("dossier_format") != LEAN_SCHEMA
                or receipt.get("quality_binding") != quality_binding()
                or receipt.get("original_release_year") != doc["game_identity"]["release_year"]
                or receipt.get("isolated_sandbox_acceptance") is not True
                or receipt.get("canonical_acceptance") is not False
                or receipt.get("deep_ready") is not False):
            raise ValueError("Lean sandbox record/receipt/hash mismatch: " + appid)
        assignment = receipt.get("assignment", {})
        if (assignment.get("appid") != appid
                or assignment.get("title") != row["title"]
                or assignment.get("assignment_id") != row["assignment_id"]
                or assignment.get("group_sequence") != row["group_sequence"]
                or assignment.get("trial_id") != trial):
            raise ValueError("Lean sandbox edition/frozen assignment mismatch")
        validate_writer_lean(doc, appid=appid, title=row["title"],
                             expected_ttl_days=14)
        from dossier_research_notes_v2 import assembly_work, inspect_assembly
        status = inspect_assembly(
            repo, marker_commit=grant["marker_commit"], trial_id=trial,
            appid=appid, research_commit=row["research_commit"],
            result_commit=row["assembly_commit"])
        work = assembly_work(repo, marker_commit=grant["marker_commit"],
                             trial_id=trial, appid=appid,
                             research_commit=row["research_commit"])
        from dossier_two_stage_staging import json_at
        original = json_at(repo, row["assembly_commit"], work["output_path"])
        if (status.get("status") != "strict_item_valid_pending_existing_atomic_group_ingest"
                or original.get("outcome") != "assembled_candidate_ready"
                or original.get("final_dossier") != doc):
            raise ValueError("Lean accepted bytes not bound to immutable Assembly")
    if mode == "staged":
        changed = git_bytes(repo, "diff", "--cached", "--name-only").decode().splitlines()
    else:
        changed = git_bytes(repo, "diff-tree", "--no-commit-id", "--name-only",
                            "-r", "HEAD").decode().splitlines()
    if set(changed) != expected or len(changed) != len(expected):
        raise ValueError("Lean sandbox transaction is not exactly 12 new files")
    return {"schema": "DOSSIER-NOTES-V2-SANDBOX-LEAN-READBACK-V1",
            "verified_items": len(grant["items"]), "mode": mode,
            "canonical_acceptance": False, "deep_ready": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--mode", required=True, choices=("staged", "committed"))
    arguments = parser.parse_args()
    print(json.dumps(exact_transaction(arguments.repo, mode=arguments.mode),
                     ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

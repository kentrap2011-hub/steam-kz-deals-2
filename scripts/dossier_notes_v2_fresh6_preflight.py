#!/usr/bin/env python3
"""Offline, READ-ONLY exact-source gate for a prospective six-game Notes V2 pilot.

This DOES NOT issue a V2 grant/manifest/marker, authorize any worker, create
Git commits, call GitHub Actions or publish semantic/sandbox/canonical results.
The old original18 issuer/transport/writer remain the only implemented route.
"""
import argparse
import copy
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/dossier_notes_v2_fresh6_preparation_contract.json"
OLD_V2 = ROOT / "config/dossier_research_notes_v2_contract.json"
H40 = re.compile(r"^[0-9a-f]{40}$")
APPID = re.compile(r"^[1-9][0-9]*$")
TRIAL = "dossier-notes-v2-fresh6-20261111-first"
REPO = "kentrap2011-hub/steam-kz-deals-2"
OFF_FLAGS = (
    "fresh6_manifest_issued", "owner_actions_authorized",
    "semantic_execution_authorized", "sandbox_writer_authorized",
    "canonical_ingest_authorized", "production_enabled",
    "scheduled_tasks_enabled", "automated_retry_enabled",
)


class ScopeBlocked(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ScopeBlocked(message)


def git(repo, *args, check=True):
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if check and p.returncode:
        raise ScopeBlocked("pinned Git read unavailable: " + " ".join(args[:2]))
    return p


def read_pinned(repo, main_sha, path, expected_blob):
    require(isinstance(path, str) and path and not path.startswith("/")
            and ".." not in path.split("/"), "unsafe pinned source path")
    require(isinstance(expected_blob, str) and H40.fullmatch(expected_blob),
            "missing Git blob SHA pin")
    observed = git(repo, "rev-parse", f"{main_sha}:{path}").stdout.decode().strip()
    require(observed == expected_blob, "immutable source Git blob changed: " + path)
    return git(repo, "show", f"{main_sha}:{path}").stdout


def parse_json(data, label):
    try:
        value = json.loads(data)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ScopeBlocked("invalid " + label + ": " + str(exc)) from exc
    require(isinstance(value, dict), label + " must be object")
    return value


def validate_scope(c, index, descriptors, old_v2):
    """Pure validation over pinned, already-read GitHub work objects."""
    require(isinstance(c, dict)
            and c.get("schema") == "DOSSIER-NOTES-V2-FRESH6-PREPARATION-CONTRACT"
            and c.get("schema_version") == 1
            and c.get("status") == "scoped_preparation_only_not_issuer"
            and c.get("repository") == REPO
            and c.get("owner") == "github_control_plane"
            and c.get("trial_id") == TRIAL
            and c.get("proposed_sandbox_branch")
                == "sandbox/" + TRIAL
            and c.get("original18_unchanged") is True
            and c.get("intended_semantic_phases") == ["research", "assembly"],
            "new six-game contract identity/ownership changed")
    require(all(c.get(k) is False for k in OFF_FLAGS),
            "fresh6 execution gate must remain explicitly false")
    p = c.get("provenance")
    require(isinstance(p, dict), "source provenance absent")
    require(isinstance(p.get("main_commit"), str)
            and H40.fullmatch(p["main_commit"]),
            "source main SHA absent")
    require(index.get("schema") == "TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2"
            and index.get("snapshot_id") == p.get("snapshot_id")
            and index.get("prepared_for_date") == p.get("prepared_for_date")
            and index.get("source_queue_sha256") == p.get("source_queue_sha256")
            and index.get("group_plan_sha256") == p.get("group_plan_sha256"),
            "GitHub-prepared worker-index identity disagrees with pinned contract")
    original = old_v2.get("original_groups")
    require(isinstance(original, list) and len(original) == 6
            and sum(len(g.get("appids", [])) for g in original) == 18,
            "original18 source not verified")
    original_appids = {a for group in original for a in group["appids"]}
    require(len(original_appids) == 18, "original18 duplicate AppIDs")
    candidates = c.get("candidates")
    groups = p.get("group_descriptors")
    require(isinstance(candidates, list) and len(candidates) == 6
            and isinstance(groups, list) and len(groups) == 2
            and isinstance(descriptors, dict), "fresh6 must contain two exact triples")
    seen, order, by_group = set(), [], {}
    for row in candidates:
        require(isinstance(row, dict)
                and set(row) == {
                    "appid", "title", "source_group_sequence",
                    "source_item_index", "source_reason", "baseline_blob_sha"
                }, "candidate shape differs")
        a = row["appid"]
        require(isinstance(a, str) and APPID.fullmatch(a)
                and a not in seen and a not in original_appids,
                "duplicate/invalid/original18 candidate AppID")
        require(isinstance(row["title"], str) and row["title"].strip()
                and row["title"] == row["title"].strip()
                and isinstance(row["source_item_index"], int)
                and not isinstance(row["source_item_index"], bool)
                and row["source_item_index"] in (0, 1, 2)
                and isinstance(row["source_group_sequence"], int)
                and row["source_group_sequence"] in (1, 70),
                "invalid exact title/edition/index")
        require(row["source_reason"] in ("refresh_required", "missing_dossier"),
                "invalid source status")
        seen.add(a)
        order.append(a)
        by_group.setdefault(row["source_group_sequence"], []).append(row)
    require([r["source_group_sequence"] for r in candidates] == [1] * 3 + [70] * 3
            and [r["source_item_index"] for r in candidates] == [0, 1, 2] * 2,
            "fresh6 source item order changed")
    require([g.get("sequence") for g in groups] == [1, 70]
            and set(descriptors) == {1, 70}, "unexpected source group")
    for group in groups:
        seq = group["sequence"]
        path = index.get("descriptor_path_template", "").format(
            snapshot_id=p["snapshot_id"], sequence=seq)
        require(group.get("path") == path
                and isinstance(group.get("blob_sha"), str)
                and H40.fullmatch(group["blob_sha"]),
                "not an exact GitHub-prepared descriptor path/blob")
        doc = descriptors[seq]
        require(doc.get("snapshot_id") == p["snapshot_id"]
                and doc.get("source_queue_sha256") == p["source_queue_sha256"]
                and doc.get("group_plan_sha256") == p["group_plan_sha256"]
                and doc.get("prepared_required_sha256")
                    == index.get("prepared_required_sha256")
                and doc.get("sequence") == seq
                and doc.get("group_sha256") == group.get("group_sha256"),
                "source group binding mismatch")
        members = doc.get("items")
        require(isinstance(members, list) and len(members) == 3
                and doc.get("appids") == [r["appid"] for r in by_group[seq]],
                "source group members differ from expected six")
        for idx, row in enumerate(by_group[seq]):
            item = members[idx]
            require(item == {
                "key": "App_" + row["appid"], "appid": row["appid"],
                "title": row["title"],
                "dossier_path":
                    "data/cache/taste_steam_review_dossiers/App_" + row["appid"] + ".json",
                "reason": row["source_reason"]
            }, "AppID/title/edition/source index swapped: " + row["appid"])
    require(len(seen) == 6, "not six independent candidates")
    return {
        "status": "scope_verified_preparation_only",
        "trial_id": c["trial_id"],
        "source_main_sha": p["main_commit"],
        "source_snapshot_id": p["snapshot_id"],
        "appids": order,
        "candidate_count": 6,
        "original18_intersection": [],
        "new_manifest_issued": False,
        "owner_dispatch_authorized": False,
        "semantic_execution_authorized": False,
        "sandbox_writer_authorized": False,
        "canonical_acceptance": False,
        "production_enabled": False,
    }


def inspect(repo=ROOT, contract_path=CONTRACT):
    """Read only the previously committed Git object source and local contracts."""
    repo = Path(repo)
    c = parse_json(Path(contract_path).read_bytes(), "fresh6 preparation contract")
    p = c.get("provenance", {})
    require(isinstance(p, dict) and isinstance(p.get("main_commit"), str)
            and H40.fullmatch(p["main_commit"]), "missing source anchor")
    old_current = parse_json((repo / "config/dossier_research_notes_v2_contract.json").read_bytes(),
                             "current V2 contract")
    require(all(old_current.get(k) is False for k in (
        "active", "authorized_for_semantic_execution",
        "authorized_for_canonical_ingest", "production_enabled")),
        "inactive V2 global contract no longer inactive")
    main = p["main_commit"]
    index = parse_json(read_pinned(repo, main, p["worker_index_path"],
                                   p["worker_index_blob_sha"]), "work index")
    docs = {g["sequence"]: parse_json(
        read_pinned(repo, main, g["path"], g["blob_sha"]),
        "descriptor " + str(g["sequence"]))
        for g in p["group_descriptors"]}
    original = parse_json(read_pinned(
        repo, main, "config/dossier_research_notes_v2_contract.json",
        git(repo, "rev-parse",
            f"{main}:config/dossier_research_notes_v2_contract.json").stdout.decode().strip()),
        "original18 V2 contract")
    status = validate_scope(c, index, docs, original)
    for item in c["candidates"]:
        path = "data/cache/taste_steam_review_dossiers/App_" + item["appid"] + ".json"
        want = item["baseline_blob_sha"]
        result = git(repo, "cat-file", "-e", f"{main}:{path}", check=False)
        if want is None:
            require(result.returncode != 0 and item["source_reason"] == "missing_dossier",
                    "missing baseline is actually present: " + path)
        else:
            require(result.returncode == 0 and item["source_reason"] == "refresh_required",
                    "expected baseline absent: " + path)
            read_pinned(repo, main, path, want)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(), ensure_ascii=False, sort_keys=True))
    except (OSError, ScopeBlocked, TypeError, KeyError, ValueError) as exc:
        parser.exit(2, "BLOCKED_FRESH6_SCOPE: " + str(exc) + "\n")


if __name__ == "__main__":
    main()

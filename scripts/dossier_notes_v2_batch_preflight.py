#!/usr/bin/env python3
"""Read-only reusable V2 batch scope verification against frozen GitHub-prepared blobs.

A batch contract is DATA under config/dossier_notes_v2_batches/{trial_id}.json,
never a grant; this code cannot launch semantics, Actions or a writer.
"""
import argparse
import json
import re
from pathlib import Path

from dossier_notes_v2_fresh6_preflight import (
    git, read_pinned, parse_json, require, ScopeBlocked, H40, APPID,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config/dossier_notes_v2_batch_policy.json"
TRIAL = re.compile(r"^dossier-notes-v2-[a-z0-9][a-z0-9-]{8,70}$")
OFF_FLAGS = (
    "manifest_issued", "owner_actions_authorized",
    "semantic_execution_authorized", "sandbox_writer_authorized",
    "canonical_ingest_authorized", "production_enabled",
    "scheduled_tasks_enabled", "automated_retry_enabled",
)


def policy(repo=ROOT):
    p = parse_json((Path(repo) / "config/dossier_notes_v2_batch_policy.json").read_bytes(), "batch policy")
    require(p.get("schema") == "DOSSIER-NOTES-V2-REUSABLE-BATCH-POLICY"
            and p.get("schema_version") == 1
            and p.get("owner") == "github_control_plane"
            and p.get("repository") == "kentrap2011-hub/steam-kz-deals-2"
            and p.get("maximum_items_per_batch") == 24
            and p.get("minimum_items_per_batch") == 1
            and p.get("maximum_source_groups") == 24
            and p.get("original18_trial_id") == "dossier-notes-v2-original18-first"
            and p.get("active") is False
            and p.get("canonical_ingest") is False
            and p.get("production_enabled") is False
            and p.get("scheduled_worker") is False
            and p.get("automatic_retry") is False
            and p.get("one_use_owner_issued_grant_per_cohort") is True
            and p.get("sandbox_prefix") == "sandbox/"
            and p.get("versioned_cohort_contract_path") ==
                "config/dossier_notes_v2_batches/{trial_id}.json",
            "unrecognized reusable sandbox batch policy")
    return p


def contract_path(trial_id):
    require(isinstance(trial_id, str) and TRIAL.fullmatch(trial_id)
            and trial_id != "dossier-notes-v2-original18-first",
            "invalid, historical or ambiguous batch identity")
    return "config/dossier_notes_v2_batches/" + trial_id + ".json"


def validate_scope(c, index, descriptors, original, p):
    trial_id = c.get("trial_id")
    contract_path(trial_id)
    require(c.get("schema") == "DOSSIER-NOTES-V2-COHORT-PREPARATION-CONTRACT"
            and c.get("schema_version") == 1
            and c.get("status") == "github_prepared_scope_only_requires_distinct_owner_grant"
            and c.get("owner") == "github_control_plane"
            and c.get("repository") == p["repository"]
            and c.get("proposed_sandbox_branch") == "sandbox/" + trial_id
            and c.get("intended_semantic_phases") == ["research", "assembly"]
            and c.get("original18_unchanged") is True
            and c.get("max_items") == p["maximum_items_per_batch"]
            and all(c.get(k) is False for k in OFF_FLAGS),
            "batch data cannot grant execution or change identity")
    src = c.get("provenance")
    require(isinstance(src, dict)
            and isinstance(src.get("main_commit"), str)
            and H40.fullmatch(src["main_commit"])
            and isinstance(src.get("worker_index_blob_sha"), str)
            and H40.fullmatch(src["worker_index_blob_sha"])
            and index.get("schema") == "TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2"
            and index.get("snapshot_id") == src.get("snapshot_id")
            and index.get("prepared_for_date") == src.get("prepared_for_date")
            and index.get("source_queue_sha256") == src.get("source_queue_sha256")
            and index.get("group_plan_sha256") == src.get("group_plan_sha256"),
            "immutable GitHub source index/provenance disagrees")
    old_groups = original.get("original_groups")
    require(isinstance(old_groups, list) and len(old_groups) == 6,
            "original18 exclusion source missing")
    old_ids = {v for group in old_groups for v in group["appids"]}
    require(len(old_ids) == 18, "original18 identity set corrupted")
    candidates = c.get("candidates")
    groups = src.get("group_descriptors")
    require(type(candidates) is list
            and 1 <= len(candidates) <= p["maximum_items_per_batch"]
            and type(groups) is list
            and 1 <= len(groups) <= p["maximum_source_groups"]
            and type(descriptors) is dict,
            "invalid bounded cohort cardinality")
    by_group = {}
    seen = set()
    order = []
    for item in candidates:
        require(type(item) is dict and set(item) == {
            "appid", "title", "source_group_sequence", "source_item_index",
            "source_reason", "baseline_blob_sha",
        }, "invalid GitHub candidate fields")
        a, seq, idx = item["appid"], item["source_group_sequence"], item["source_item_index"]
        require(type(a) is str and APPID.fullmatch(a)
                and a not in seen and a not in old_ids
                and type(seq) is int and seq > 0
                and type(idx) is int and 0 <= idx < 100
                and type(item["title"]) is str and item["title"].strip() == item["title"]
                and len(item["title"]) > 0
                and item["source_reason"] in ("refresh_required", "missing_dossier"),
                "wrong AppID, title, edition, source index or duplicate")
        seen.add(a)
        order.append((seq,idx,a))
        by_group.setdefault(seq,[]).append(item)
    require(order == sorted(order), "candidate order is not GitHub source order")
    source_groups = {}
    for g in groups:
        require(type(g) is dict and type(g.get("sequence")) is int
                and g["sequence"] not in source_groups
                and isinstance(g.get("blob_sha"), str)
                and H40.fullmatch(g["blob_sha"]),
                "duplicate/invalid group descriptors")
        source_groups[g["sequence"]] = g
    require(set(by_group) == set(source_groups), "candidate references absent/mismatched source group")
    require([g["sequence"] for g in groups] == sorted(source_groups), "source groups out of GitHub order")
    for seq,g in source_groups.items():
        expected_path = index.get("descriptor_path_template", "").format(
            snapshot_id=src["snapshot_id"], sequence=seq)
        require(g.get("path") == expected_path and seq in descriptors, "descriptor pathname changed")
        doc = descriptors[seq]
        require(doc.get("sequence") == seq
                and doc.get("snapshot_id") == src["snapshot_id"]
                and doc.get("source_queue_sha256") == src["source_queue_sha256"]
                and doc.get("group_plan_sha256") == src["group_plan_sha256"]
                and doc.get("prepared_required_sha256") == index.get("prepared_required_sha256")
                and doc.get("group_sha256") == g.get("group_sha256"),
                "incorrect immutable group descriptor")
        members = doc.get("items")
        require(type(members) is list and doc.get("appids") ==
                [member.get("appid") for member in members], "descriptor item list is inconsistent")
        for item in by_group[seq]:
            idx = item["source_item_index"]
            require(idx < len(members) and members[idx] == {
                "key": "App_" + item["appid"], "appid": item["appid"],
                "title": item["title"],
                "dossier_path": "data/cache/taste_steam_review_dossiers/App_" + item["appid"] + ".json",
                "reason": item["source_reason"],
            }, "product, edition, source role or group index changed: " + item["appid"])
    return {"status":"batch_source_verified_not_authorized",
            "trial_id":trial_id,"source_main_sha":src["main_commit"],
            "appids":[i[2] for i in order],"candidate_count":len(candidates),
            "original18_intersection":[],"semantic_execution_authorized":False,
            "canonical_acceptance":False,"production_enabled":False}


def inspect(repo=ROOT, trial_id=None):
    repo = Path(repo)
    p = policy(repo)
    path = contract_path(trial_id)
    c = parse_json((repo / path).read_bytes(), "cohort contract")
    require(c.get("trial_id") == trial_id, "cohort filename/data mismatch")
    current = parse_json((repo / "config/dossier_research_notes_v2_contract.json").read_bytes(), "V2 contract")
    require(all(current.get(k) is False for k in ("active",
            "authorized_for_semantic_execution","authorized_for_canonical_ingest",
            "production_enabled")), "global Notes V2 flags must remain inactive")
    src = c.get("provenance")
    require(isinstance(src,dict) and H40.fullmatch(str(src.get("main_commit",""))),
            "missing pinned main source")
    main = src["main_commit"]
    index = parse_json(read_pinned(repo, main, src["worker_index_path"],
                                   src["worker_index_blob_sha"]), "frozen worker index")
    groups = src.get("group_descriptors")
    require(type(groups) is list and len(groups) <= p["maximum_source_groups"],
            "unbounded descriptors")
    docs = {g["sequence"]:parse_json(read_pinned(repo,main,g["path"],g["blob_sha"]),
                                     "frozen group") for g in groups}
    original = parse_json(read_pinned(
        repo,main,"config/dossier_research_notes_v2_contract.json",
        git(repo,"rev-parse",f"{main}:config/dossier_research_notes_v2_contract.json").stdout.decode().strip()
    ),"original18 contract")
    status = validate_scope(c,index,docs,original,p)
    for item in c["candidates"]:
        baseline_path = "data/cache/taste_steam_review_dossiers/App_" + item["appid"] + ".json"
        want = item["baseline_blob_sha"]
        exists = git(repo,"cat-file","-e",f"{main}:{baseline_path}",check=False).returncode == 0
        if want is None:
            require(not exists and item["source_reason"] == "missing_dossier",
                    "claimed absent baseline exists")
        else:
            require(exists and item["source_reason"] == "refresh_required",
                    "claimed existing baseline missing")
            read_pinned(repo,main,baseline_path,want)
    return c,status


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-id",required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(trial_id=args.trial_id)[1],sort_keys=True))
    except (ValueError,ScopeBlocked,OSError,KeyError,TypeError) as exc:
        parser.exit(2,"DOSSIER_V2_BATCH_BLOCKED: "+str(exc)+"\n")

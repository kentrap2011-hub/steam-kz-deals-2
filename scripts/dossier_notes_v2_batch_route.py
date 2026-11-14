#!/usr/bin/env python3
"""Reusable immutable GitHub-owned Notes V2 batch route, isolated from original18.

One explicit versioned source contract per cohort (data, not executable authority).
The contract is checked against pinned historical GitHub-prepared exact AppIDs,
titles/editions, group descriptor blobs and baseline SHA. One owner-issued grant,
manifest, marker and distinct authorization create a one-use isolated sandbox.
The tokenless ChatGPT connector transport checks BOTH owner Actions runs via
connected GitHub; the historical token-backed Python authorizer is preserved.
"""
import hashlib
import json
import re
from pathlib import Path

from dossier_two_stage_staging import (
    blob, blob_for, file_at, first_parent_contains, git,
    json_at, parent, require_only_new, strict_json,
)
import dossier_notes_v2_batch_preflight as preflight

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "kentrap2011-hub/steam-kz-deals-2"
OWNER_LOGIN = "kentrap2011-hub"
OWNER_ID = "315790060"
ISSUE_WORKFLOW = ".github/workflows/issue-dossier-notes-v2-batch.yml"
AUTHORIZE_WORKFLOW = ".github/workflows/authorize-dossier-notes-v2-batch.yml"
WRITER_WORKFLOW = ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml"
SHA = re.compile(r"^[0-9a-f]{40}$")
ORIGINAL_MARKERS = {
    "bb63cc291eba5aa8fc56e2920ef84d131ac28a4f",
    "2a726cf6731c0fc1e7bc809474627383c107ef9b",
    "2c2649fb98322507cd3758ff0ff7992128f94de0",
}


def require(condition, message):
    if not condition:
        raise ValueError("BATCH_V2_BLOCKED: " + message)


def canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(",",":"),
                       ensure_ascii=False) + "\n").encode("utf-8")


def paths(trial_id):
    contract_path = preflight.contract_path(trial_id)
    return {
        "contract": contract_path,
        "branch": "sandbox/" + trial_id,
        "grant": "data/control/dossier_notes_v2/grants/" + trial_id + ".json",
        "manifest": "data/control/dossier_notes_v2/manifests/" + trial_id + ".json",
        "authorization": "data/control/dossier_notes_v2/authorizations/" + trial_id + ".json",
        "store": "data/control/dossier_notes_v2/batch_pilot_store/" + trial_id,
        "accepted": "data/control/dossier_notes_v2/batch_pilot_accepted",
    }


def scope(repo, trial_id):
    c, status = preflight.inspect(repo=Path(repo),trial_id=trial_id)
    require(status["trial_id"] == trial_id and status["candidate_count"] <= 24,
            "batch not strictly source verified")
    return c


def pins(c):
    p=c["provenance"]
    return {
        "source_main_sha":p["main_commit"],
        "worker_index_blob_sha":p["worker_index_blob_sha"],
        "source_snapshot_id":p["snapshot_id"],
        "source_queue_sha256":p["source_queue_sha256"],
        "group_plan_sha256":p["group_plan_sha256"],
        "group_descriptor_blobs":[g["blob_sha"] for g in p["group_descriptors"]],
        "prepared_for_date":p["prepared_for_date"],
    }


def rows(repo, trial_id):
    c=scope(repo,trial_id)
    p=c["provenance"]
    group_map={g["sequence"]:g for g in p["group_descriptors"]}
    out=[]
    for item in c["candidates"]:
        group=group_map[item["source_group_sequence"]]
        identity={
            "trial_id":trial_id,
            "source_main_sha":p["main_commit"],
            "source_snapshot_id":p["snapshot_id"],
            "source_group_blob_sha":group["blob_sha"],
            "source_group_sha256":group["group_sha256"],
            "group_sequence":item["source_group_sequence"],
            "item_index":item["source_item_index"],
            "appid":item["appid"],"title":item["title"],
            "reason":item["source_reason"],
            "baseline_blob_sha":item["baseline_blob_sha"],
        }
        h=hashlib.sha256(canonical(identity)).hexdigest()
        out.append({
            "group_sequence":item["source_group_sequence"],
            "item_index":item["source_item_index"],
            "appid":item["appid"],"title":item["title"],
            "assignment_id":"batch-"+h[:24],
            "original_assignment_sha256":h,
        })
    require(1<=len(out)<=24
            and len({r["appid"] for r in out})==len(out)
            and len({r["assignment_id"] for r in out})==len(out),
            "bounded unique immutable item list required")
    return out


def manifest_blueprint(repo, trial_id):
    c=scope(repo,trial_id)
    document={
        "schema":"DOSSIER-NOTES-V2-FROZEN-MANIFEST",
        "schema_version":2,
        "trial_id":trial_id,
        "original_pins":pins(c),
        "items":rows(repo,trial_id),
    }
    raw=canonical(document)
    return {"path":paths(trial_id)["manifest"],
            "bytes":raw,"blob_sha":blob_for(raw)}


def _one_add(repo, commit, pathname):
    p=require_only_new(repo,commit,[pathname])
    require(p!=commit and first_parent_contains(repo,p,"HEAD"),
            "one-add object does not have required HEAD first-parent ancestry")
    return p


def _unchanged(repo, introduced, pathname):
    require(first_parent_contains(repo,introduced,"HEAD"),
            "immutable source not in current first-parent chain")
    require(not git(repo,"log","--first-parent","--format=%H",
                    f"{introduced}..HEAD","--",pathname).stdout.strip(),
            "immutable path changed (including rewrite/restore): "+pathname)
    require(blob(repo,"HEAD",pathname)==blob(repo,introduced,pathname)
            and file_at(repo,"HEAD",pathname)==file_at(repo,introduced,pathname),
            "immutable bytes drifted: "+pathname)


def _base_contract_proof(repo,base,trial_id):
    # Cohort contract must have been GitHub-reviewed, committed to main BEFORE
    # owner freeze, never supplied by a worker's sandbox or mutable latest view.
    path=paths(trial_id)["contract"]
    require(first_parent_contains(repo,base,"HEAD"),"issuer base outside ancestry")
    original_raw=file_at(repo,base,path)
    local_raw=(Path(repo)/path).read_bytes()
    require(original_raw==local_raw
            and blob(repo,base,path)==blob_for(original_raw),
            "batch contract changed after GitHub owner freeze")
    changed=git(repo,"log","--first-parent","--format=%H",
                f"{base}..HEAD","--",path).stdout.strip()
    require(not changed,"frozen cohort contract modified/reintroduced")
    policy_path="config/dossier_notes_v2_batch_policy.json"
    require(file_at(repo,base,policy_path)==(Path(repo)/policy_path).read_bytes(),
            "batch policy changed since issuer base")
    require(not git(repo,"log","--first-parent","--format=%H",
                    f"{base}..HEAD","--",policy_path).stdout.strip(),
            "batch policy updated after freeze")
    # A semantic result must not be able to alter the Python/Actions source
    # executed by a future manual sandbox writer. Cohort transport is create-only.
    executable_paths = (
        "scripts/dossier_notes_v2_batch_preflight.py",
        "scripts/dossier_notes_v2_batch_route.py",
        "scripts/dossier_notes_v2_batch_issuer.py",
        "scripts/dossier_notes_v2_batch_pilot.py",
        "scripts/dossier_research_notes_v2.py",
        "scripts/dossier_notes_v2_per_item_receipts.py",
        "scripts/taste_steam_review_dossier_buffered.py",
        ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml",
    )
    # New event-driven intake code is immutable only for cohorts frozen after
    # it first existed in main. Older issued cohorts do not have these files:
    # do not invalidate their unchanged legacy issuer or allow retrofit.
    for optional in (
        "scripts/dossier_notes_v2_research_intake.py",
        ".github/workflows/dossier-notes-v2-research-intake.yml",
    ):
        at_base = (git(repo, "cat-file", "-e", f"{base}:{optional}",
                       required=False).returncode == 0)
        at_head = (git(repo, "cat-file", "-e", f"HEAD:{optional}",
                       required=False).returncode == 0)
        require(at_base == at_head, "cannot add or delete post-issuer intake executable")
        if at_base:
            executable_paths += (optional,)
    for executable in executable_paths:
        # The legacy file_at() intentionally supports only config/ and data/.
        # These are STATIC trusted source paths, so compare Git show bytes
        # without broadening that legacy validator's namespace.
        require(git(repo,"show",f"{base}:{executable}").stdout==
                git(repo,"show",f"HEAD:{executable}").stdout,
                "sandbox executable differs from frozen GitHub main source")
        require(not git(repo,"log","--first-parent","--format=%H",
                        f"{base}..HEAD","--",executable).stdout.strip(),
                "sandbox executable modified after GitHub owner issuance")
    return {"contract_blob_sha":blob(repo,base,path),
            "policy_blob_sha":blob(repo,base,policy_path)}


def expected_grant(repo,trial_id,base):
    c=scope(repo,trial_id)
    frozen=_base_contract_proof(repo,base,trial_id)
    bp=manifest_blueprint(repo,trial_id)
    return {
        "schema":"DOSSIER-NOTES-V2-BATCH-OWNER-GRANT",
        "schema_version":1,
        "trial_id":trial_id,
        "base_main_sha":base,
        "cohort_contract_path":paths(trial_id)["contract"],
        "cohort_contract_blob_sha":frozen["contract_blob_sha"],
        "batch_policy_blob_sha":frozen["policy_blob_sha"],
        "source_pins":pins(c),
        "manifest_path":paths(trial_id)["manifest"],
        "manifest_blob_sha":bp["blob_sha"],
        "owner_login":OWNER_LOGIN,"owner_actor_id":OWNER_ID,
        "scope":"one_git_owner_issued_reusable_batch_sandbox_only",
        "semantic_execution_approved":False,
        "production_approved":False,
        "canonical_ingest_approved":False,
    }


def expected_authorization(repo,trial_id,marker,grant_commit,run_id):
    bp=manifest_blueprint(repo,trial_id)
    return {
        "schema":"DOSSIER-NOTES-V2-BATCH-OWNER-AUTHORIZATION",
        "schema_version":1,"trial_id":trial_id,
        "marker_commit":marker,"marker_parent":parent(repo,marker),
        "manifest_blob_sha":bp["blob_sha"],
        "human_grant_commit":grant_commit,
        "human_grant_blob_sha":blob(repo,grant_commit,paths(trial_id)["grant"]),
        "owner_actor_id":OWNER_ID,"owner_login":OWNER_LOGIN,
        "github_authorization_run_id":run_id,
        "scope":"one_manual_batch_research_assembly_sandbox_only",
        "semantic_execution_authorized":True,
        "assembly_authorized":True,
        "sandbox_writer_authorized":True,
        "production_authorized":False,
        "canonical_acceptance":False,
    }


def issuer_structure(repo,*,trial_id,marker_commit,authorization_commit):
    """Structural proof only; actual authenticated owner Actions check separate."""
    repo=Path(repo)
    path=paths(trial_id)
    for value in (marker_commit,authorization_commit):
        require(isinstance(value,str) and SHA.fullmatch(value)
                and value not in ORIGINAL_MARKERS,
                "reused original18 or invalid immutable issuer SHA")
    require(_one_add(repo,authorization_commit,path["authorization"])==marker_commit,
            "authorization must be marker direct one-add child")
    _unchanged(repo,authorization_commit,path["authorization"])
    marker_parent=parent(repo,marker_commit)
    from dossier_research_notes_v2 import _marker_nonce
    nonce=_marker_nonce(repo,marker_commit)
    marker_path="data/control/dossier_notes_v2/run_starts/"+nonce+".json"
    require(_one_add(repo,marker_commit,marker_path)==marker_parent,
            "marker must add only the unique nonce file")
    _unchanged(repo,marker_commit,marker_path)
    require(json_at(repo,marker_commit,marker_path)=={
        "schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
        "trial_id":trial_id,"nonce":nonce,
    },"marker content reused or wrong")
    grant_commit=_one_add(repo,marker_parent,path["manifest"])
    _unchanged(repo,marker_parent,path["manifest"])
    require(file_at(repo,marker_parent,path["manifest"])==
            manifest_blueprint(repo,trial_id)["bytes"],
            "frozen cohort appids/titles/editions/order/assignment changed")
    base=_one_add(repo,grant_commit,path["grant"])
    _unchanged(repo,grant_commit,path["grant"])
    c=scope(repo,trial_id)
    require(first_parent_contains(repo,c["provenance"]["main_commit"],base),
            "immutable prepared source anchor is not on issuer main ancestry")
    require(strict_json(file_at(repo,grant_commit,path["grant"]))==
            expected_grant(repo,trial_id,base),
            "owner grant, policy pin or prepared source differs")
    auth=strict_json(file_at(repo,authorization_commit,path["authorization"]))
    rid=auth.get("github_authorization_run_id") if type(auth) is dict else None
    require(type(rid) is str and rid.isdigit()
            and int(rid)>0
            and auth==expected_authorization(repo,trial_id,marker_commit,grant_commit,rid),
            "authorization actor/run/one-use scope/manifest differs")
    return {
        "trial_id":trial_id,"marker_commit":marker_commit,
        "authorization_commit":authorization_commit,
        "authorization_blob_sha":blob(repo,authorization_commit,path["authorization"]),
        "manifest_blob_sha":manifest_blueprint(repo,trial_id)["blob_sha"],
        "human_grant_commit":grant_commit,
        "base_main_sha":base,
        "github_actor_id":OWNER_ID,
        "github_authorization_run_id":rid,
        "semantic_execution_authorized":True,
        "issuer_structural_only":True,
        "github_run_authenticated":False,
    }


def authenticated_owner_run(anchor,token,github_repository=REPOSITORY):
    """Read GitHub's actual owner-first-attempt successful manual authorizer."""
    require(github_repository==REPOSITORY and bool(token) and anchor.get("trial_id"),
            "missing authenticated exact repository context")
    from dossier_notes_v2_per_item_receipts import _github_get
    rid=anchor["github_authorization_run_id"]
    doc=_github_get(REPOSITORY,"actions/runs/"+rid,token)
    require(type(doc) is dict
            and doc.get("id")==int(rid)
            and doc.get("event")=="workflow_dispatch"
            and doc.get("status")=="completed"
            and doc.get("conclusion")=="success"
            and doc.get("run_attempt")==1
            and doc.get("head_branch")=="main"
            and doc.get("path")==AUTHORIZE_WORKFLOW
            and doc.get("display_title")==(
                "Authorize isolated Notes V2 batch "
                + anchor["trial_id"] + " marker " + anchor["marker_commit"])
            and doc.get("actor",{}).get("id")==int(OWNER_ID)
            and doc.get("actor",{}).get("login")==OWNER_LOGIN
            and isinstance(doc.get("head_sha"),str)
            and SHA.fullmatch(doc["head_sha"]),
            "real successful first-attempt owner manual GitHub authorizer not proven")
    return True

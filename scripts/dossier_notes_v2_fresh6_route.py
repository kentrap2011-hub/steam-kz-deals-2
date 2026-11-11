#!/usr/bin/env python3
"""One-use, six-item V2 sandbox scope and immutable Git issuer verifier.

Separate from original18 authority. No semantics or implicit remote writes.
"""
import hashlib
import json
import re
from pathlib import Path

from dossier_two_stage_staging import (
    blob, blob_for, file_at, first_parent_contains, git, json_at, parent,
    require_only_new, strict_json,
)
import dossier_notes_v2_fresh6_preflight as preflight

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/dossier_notes_v2_fresh6_preparation_contract.json"
TRIAL = "dossier-notes-v2-fresh6-20261111-first"
BRANCH = "sandbox/" + TRIAL
OWNER_LOGIN = "kentrap2011-hub"
OWNER_ID = "315790060"
REPOSITORY = "kentrap2011-hub/steam-kz-deals-2"
ISSUE_WORKFLOW = ".github/workflows/issue-dossier-notes-v2-fresh6.yml"
AUTHORIZE_WORKFLOW = ".github/workflows/authorize-dossier-notes-v2-fresh6.yml"
GRANT_PATH = "data/control/dossier_notes_v2/grants/" + TRIAL + ".json"
MANIFEST_PATH = "data/control/dossier_notes_v2/manifests/" + TRIAL + ".json"
AUTH_PATH = "data/control/dossier_notes_v2/authorizations/" + TRIAL + ".json"
SHA = re.compile(r"^[0-9a-f]{40}$")


def deny(message):
    raise ValueError("FRESH6_BLOCKED: " + message)


def require(condition, message):
    if not condition:
        deny(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def scope(repo=ROOT):
    """Validate actual previously pinned GitHub source; no fallback to latest."""
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(c["trial_id"] == TRIAL and c["proposed_sandbox_branch"] == BRANCH,
            "preparation identity mutated")
    preflight.inspect(repo=Path(repo), contract_path=CONTRACT)
    return c


def pins(c):
    p = c["provenance"]
    return {
        "source_main_sha": p["main_commit"],
        "worker_index_blob_sha": p["worker_index_blob_sha"],
        "source_snapshot_id": p["snapshot_id"],
        "source_queue_sha256": p["source_queue_sha256"],
        "group_plan_sha256": p["group_plan_sha256"],
        "group_descriptor_blobs": [g["blob_sha"] for g in p["group_descriptors"]],
        "prepared_for_date": p["prepared_for_date"],
    }


def rows(repo=ROOT):
    c = scope(repo)
    p = c["provenance"]
    results = []
    for item in c["candidates"]:
        # A unique assignment identity is a GitHub-derived digest of exact
        # product identity and the original *prepared* descriptor blob.
        group = next(g for g in p["group_descriptors"]
                     if g["sequence"] == item["source_group_sequence"])
        identity = {
            "trial_id": TRIAL,
            "source_main_sha": p["main_commit"],
            "source_snapshot_id": p["snapshot_id"],
            "source_group_blob_sha": group["blob_sha"],
            "source_group_sha256": group["group_sha256"],
            "group_sequence": item["source_group_sequence"],
            "item_index": item["source_item_index"],
            "appid": item["appid"],
            "title": item["title"],
            "reason": item["source_reason"],
            "baseline_blob_sha": item["baseline_blob_sha"],
        }
        h = hashlib.sha256(canonical(identity)).hexdigest()
        results.append({
            "group_sequence": item["source_group_sequence"],
            "item_index": item["source_item_index"],
            "appid": item["appid"], "title": item["title"],
            "assignment_id": "fresh6-" + h[:24],
            "original_assignment_sha256": h,
        })
    require(len(results) == 6 and len(set(x["assignment_id"] for x in results)) == 6,
            "duplicate or non-six fresh assignments")
    return results


def manifest_blueprint(repo=ROOT):
    c = scope(repo)
    payload = {
        "schema": "DOSSIER-NOTES-V2-FROZEN-MANIFEST", "schema_version": 2,
        "trial_id": TRIAL, "original_pins": pins(c), "items": rows(repo),
    }
    raw = canonical(payload)
    return {"path": MANIFEST_PATH, "bytes": raw, "blob_sha": blob_for(raw)}


def _one_add(repo, child, path):
    p = require_only_new(repo, child, [path])
    require(p != child and first_parent_contains(repo, p, "HEAD"),
            "one-add chain not on real HEAD ancestry")
    return p


def _unchanged(repo, introduced, path):
    require(first_parent_contains(repo, introduced, "HEAD"),
            "source introduction absent from current first-parent")
    require(not git(repo, "log", "--first-parent", "--format=%H",
                    f"{introduced}..HEAD", "--", path).stdout.strip(),
            "immutable first-parent path was modified: " + path)
    require(blob(repo, "HEAD", path) == blob(repo, introduced, path)
            and file_at(repo, "HEAD", path) == file_at(repo, introduced, path),
            "immutable bytes changed: " + path)


def issuer_structure(repo, *, marker_commit, authorization_commit):
    """Exactly three issue commits + one distinct owner authorize, Git only.

    Caller MUST separately verify actual GitHub workflow run via authenticated
    API before any semantic transport or sandbox persistence.
    """
    repo = Path(repo)
    for value in (marker_commit, authorization_commit):
        require(isinstance(value, str) and SHA.fullmatch(value),
                "exact new Git SHA required")
    c = scope(repo)
    require(marker_commit not in (
        "bb63cc291eba5aa8fc56e2920ef84d131ac28a4f",
        "2a726cf6731c0fc1e7bc809474627383c107ef9b"
    ), "original18 historical marker forbidden")
    require(_one_add(repo, authorization_commit, AUTH_PATH) == marker_commit,
            "authorization must be the marker's direct one-add child")
    _unchanged(repo, authorization_commit, AUTH_PATH)
    marker_parent = parent(repo, marker_commit)
    from dossier_research_notes_v2 import _marker_nonce
    nonce = _marker_nonce(repo, marker_commit)
    marker_path = f"data/control/dossier_notes_v2/run_starts/{nonce}.json"
    require(_one_add(repo, marker_commit, marker_path) == marker_parent,
            "marker must be standalone one-add")
    _unchanged(repo, marker_commit, marker_path)
    require(json_at(repo, marker_commit, marker_path) == {
        "schema": "DOSSIER-NOTES-V2-RUN-START", "schema_version": 2,
        "trial_id": TRIAL, "nonce": nonce,
    }, "wrong fresh6 marker content")
    grant_commit = _one_add(repo, marker_parent, MANIFEST_PATH)
    _unchanged(repo, marker_parent, MANIFEST_PATH)
    require(file_at(repo, marker_parent, MANIFEST_PATH)
            == manifest_blueprint(repo)["bytes"], "fresh6 assignment/edition/pins mutated")
    base_main = _one_add(repo, grant_commit, GRANT_PATH)
    _unchanged(repo, grant_commit, GRANT_PATH)
    require(first_parent_contains(repo, c["provenance"]["main_commit"], base_main),
            "fresh6 source anchor not on original main")
    grant = strict_json(file_at(repo, grant_commit, GRANT_PATH))
    expected_grant = {
        "schema": "DOSSIER-NOTES-V2-FRESH6-OWNER-GRANT",
        "schema_version": 1, "trial_id": TRIAL,
        "base_main_sha": base_main,
        "source_pins": pins(c), "manifest_path": MANIFEST_PATH,
        "manifest_blob_sha": blob_for(file_at(repo, marker_parent, MANIFEST_PATH)),
        "owner_login": OWNER_LOGIN, "owner_actor_id": OWNER_ID,
        "scope": "one_new_fresh6_issuer_only_not_original18",
        "semantic_execution_approved": False,
        "production_approved": False, "canonical_ingest_approved": False,
    }
    require(grant == expected_grant, "fresh6 grant differs from exact issuer scope")
    auth = strict_json(file_at(repo, authorization_commit, AUTH_PATH))
    require(auth == {
        "schema": "DOSSIER-NOTES-V2-FRESH6-OWNER-AUTHORIZATION",
        "schema_version": 1, "trial_id": TRIAL,
        "marker_commit": marker_commit, "marker_parent": marker_parent,
        "manifest_blob_sha": expected_grant["manifest_blob_sha"],
        "human_grant_commit": grant_commit,
        "human_grant_blob_sha": blob(repo, grant_commit, GRANT_PATH),
        "owner_actor_id": OWNER_ID, "owner_login": OWNER_LOGIN,
        "github_authorization_run_id": auth.get("github_authorization_run_id"),
        "scope": "one_manual_fresh6_research_and_assembly_sandbox_only",
        "semantic_execution_authorized": True, "assembly_authorized": True,
        "sandbox_writer_authorized": True, "production_authorized": False,
        "canonical_acceptance": False,
    } and isinstance(auth.get("github_authorization_run_id"), str)
        and auth["github_authorization_run_id"].isdigit(),
        "authorization has wrong actor/grant/scope or untyped GitHub run")
    return {
        "trial_id": TRIAL, "marker_commit": marker_commit,
        "authorization_commit": authorization_commit,
        "authorization_blob_sha": blob(repo, authorization_commit, AUTH_PATH),
        "manifest_blob_sha": expected_grant["manifest_blob_sha"],
        "human_grant_commit": grant_commit,
        "github_actor_id": OWNER_ID,
        "github_authorization_run_id": auth["github_authorization_run_id"],
        "semantic_execution_authorized": True,
        "issuer_structural_only": True, "github_run_authenticated": False,
    }


def authenticated_owner_run(anchor, token, github_repository=REPOSITORY):
    """Validate authoritative GitHub Actions state; never trust Git committer."""
    require(github_repository == REPOSITORY and bool(token),
            "expected repo and authenticated token required")
    from dossier_notes_v2_per_item_receipts import _github_get
    rid = anchor["github_authorization_run_id"]
    doc = _github_get(REPOSITORY, "actions/runs/" + rid, token)
    require(doc.get("id") == int(rid)
            and doc.get("status") == "completed"
            and doc.get("conclusion") == "success"
            and doc.get("event") == "workflow_dispatch"
            and doc.get("run_attempt") == 1
            and doc.get("head_branch") == "main"
            and doc.get("path") == AUTHORIZE_WORKFLOW
            and doc.get("actor", {}).get("id") == int(OWNER_ID)
            and doc.get("actor", {}).get("login") == OWNER_LOGIN,
            "actual GitHub owner authorizing dispatch not confirmed")
    return True

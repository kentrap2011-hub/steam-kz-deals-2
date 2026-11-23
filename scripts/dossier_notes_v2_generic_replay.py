#!/usr/bin/env python3
"""Single-use, owner-authenticated, request-branch triggered Assembly-only Research replay.

A user-approved connector creates ONE new request branch from current main and
ONE create-only request JSON. The *GitHub Action*, not ChatGPT, checks source
Research, allocates the trial, creates the grant/manifest/marker/authorization,
and rebinds old Research into six (or another approved subset) fresh one-adds.
No semantic Research/Assembly, canonical writer, recovery or production runs.
"""
import argparse
import copy
import hashlib
import json
import os
import re
import secrets
import subprocess
import tempfile
from pathlib import Path

import dossier_notes_v2_batch_issuer as issuer
import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_assembly_replay_seed as copy_tool
import dossier_notes_v2_per_item_receipts as receipts
import dossier_notes_v2_research_receipt_ingest as ingest
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import (
    blob, blob_for, file_at, first_parent_contains, json_at, parent,
    require_only_new, strict_json,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY = "config/dossier_notes_v2_generic_replay_policy.json"
WORKFLOW = ".github/workflows/issue-dossier-notes-v2-generic-assembly-replay.yml"
NONCE = re.compile(r"^[0-9a-f]{32}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
SOURCE = re.compile(r"^dossier-notes-v2-[a-z0-9][a-z0-9-]{8,70}$")
PREFIX = "dossier-notes-v2-assembly-replay-"
REQUEST_BRANCH = "dossier-assembly-requests/"
REQUEST_PATH = "data/control/dossier_notes_v2/replay_requests/"
PURPOSE = "repeat_assembly_from_exact_accepted_research"
SCOPE = "one_owner_requested_isolated_assembly_replay_only"


def require(ok, reason):
    if not ok:
        raise ValueError("GENERIC_ASSEMBLY_REPLAY_BLOCKED: " + reason)


def git(repo, *args):
    return copy_tool.command(repo, *args)


def policy(repo=ROOT):
    doc = json.loads((Path(repo) / POLICY).read_text(encoding="utf-8"))
    require(doc["schema"] == "DOSSIER-NOTES-V2-GENERIC-ASSEMBLY-REPLAY-POLICY"
            and doc["schema_version"] == 1
            and doc["owner_actor_id"] == batch.OWNER_ID
            and doc["repository"] == batch.REPOSITORY
            and doc["request_workflow"] == WORKFLOW
            and doc["enabled_for_explicit_owner_request"] is True
            and doc["automatic_launch_on_source_merge"] is False
            and doc["source_generic_replay_as_research_prohibited"] is True
            and doc["one_owner_first_attempt_push_per_request"] is True
            and doc["allow_technical_rerun_to_issue_semantic_attempt"] is False
            and doc["allow_semantic_research"] is False
            and doc["allow_automatic_semantic_retry"] is False
            and doc["allow_automatic_writer"] is False
            and doc["production_enabled"] is False
            and doc["canonical_ingest"] is False
            and doc["scheduled_worker"] is False
            and doc["lean_canonical_reader_writer_deep_enabled"] is False,
            "generic request control contract not safe")
    active = json.loads((Path(repo) / "config/dossier_research_notes_v2_contract.json").read_text())
    require(all(active.get(flag) is False for flag in (
        "active", "authorized_for_semantic_execution",
        "authorized_for_canonical_ingest", "production_enabled")),
        "V2 production source is not disabled")
    lean = json.loads((Path(repo) / "config/dossier_lean_canonical_dual_format_contract.json").read_text())
    require(all(lean.get(flag) is False for flag in (
        "lean_writer_enabled", "lean_reader_enabled", "lean_deep_enabled")),
        "normal Lean canonical/Deep switches must stay off")
    return doc


def trial(nonce):
    require(isinstance(nonce, str) and NONCE.fullmatch(nonce),
            "non-hex/ambiguous 128-bit request namespace")
    return PREFIX + nonce


def is_generic(trial_id):
    return isinstance(trial_id, str) and trial_id.startswith(PREFIX) and bool(
        NONCE.fullmatch(trial_id[len(PREFIX):]))


def request_path(nonce):
    trial(nonce)
    return REQUEST_PATH + nonce + ".json"


def request_doc(nonce, source_trial_id, appids):
    trial(nonce)
    require(type(source_trial_id) is str and SOURCE.fullmatch(source_trial_id)
            and not is_generic(source_trial_id)
            and source_trial_id != "dossier-notes-v2-original18-first",
            "source must be an independently owner-issued non-generic Notes V2 cohort")
    require(type(appids) is list and 1 <= len(appids) <= 24
            and all(type(a) is str and re.fullmatch(r"[0-9]{1,12}", a) for a in appids)
            and len(set(appids)) == len(appids),
            "bounded unique exact AppID selection required")
    return {
        "schema": "DOSSIER-NOTES-V2-GENERIC-ASSEMBLY-REPLAY-REQUEST-V1",
        "schema_version": 1, "nonce": nonce, "source_trial_id": source_trial_id,
        "appids": appids, "purpose": PURPOSE,
    }


def request_guard(repo, env):
    """Only the real owner first push ADDING one file to an existing request branch."""
    policy(repo)
    require(env.get("GITHUB_ACTIONS") == "true"
            and env.get("GITHUB_EVENT_NAME") == "push"
            and env.get("GITHUB_REPOSITORY") == batch.REPOSITORY
            and env.get("GITHUB_REPOSITORY_OWNER_ID") == batch.OWNER_ID
            and env.get("GITHUB_ACTOR_ID") == batch.OWNER_ID
            and env.get("GITHUB_ACTOR") == batch.OWNER_LOGIN
            and env.get("GITHUB_TRIGGERING_ACTOR") == batch.OWNER_LOGIN
            and env.get("GITHUB_RUN_ATTEMPT") == "1"
            and str(env.get("GITHUB_RUN_ID", "")).isdigit()
            and int(env.get("GITHUB_RUN_ID", "0")) > 0,
            "not real owner first-attempt request push")
    ref = env.get("GITHUB_REF", "")
    require(ref.startswith("refs/heads/" + REQUEST_BRANCH), "not a request ref")
    nonce = ref[len("refs/heads/" + REQUEST_BRANCH):]
    tr = trial(nonce)
    require(env.get("GITHUB_WORKFLOW_REF") == (
        batch.REPOSITORY + "/" + WORKFLOW + "@" + ref),
        "executing workflow not pinned to exact request branch")
    sha = env.get("GITHUB_SHA", "")
    require(type(sha) is str and SHA.fullmatch(sha)
            and git(repo, "rev-parse", "HEAD") == sha, "request commit identity missing")
    require(git(repo, "symbolic-ref", "--short", "HEAD") == REQUEST_BRANCH + nonce,
            "not checked out on original immutable request ref")
    before = parent(repo, sha)
    require(SHA.fullmatch(before) and
            git(repo, "diff-tree", "--no-commit-id", "--name-status", "-r",
                before, sha) == "A\t" + request_path(nonce),
            "not one brand-new original request file")
    require(issuer.remote(repo, "refs/heads/" + REQUEST_BRANCH + nonce) == sha
            and issuer.remote(repo, "refs/heads/main") == before,
            "request branch or main source moved; do not retry")
    require(git(repo, "remote", "get-url", "origin") in {
        "https://github.com/" + batch.REPOSITORY,
        "https://github.com/" + batch.REPOSITORY + ".git",
        "git@github.com:" + batch.REPOSITORY,
        "git@github.com:" + batch.REPOSITORY + ".git",
        "ssh://git@github.com/" + batch.REPOSITORY + ".git",
    }, "not canonical remote")
    require(not git(repo, "status", "--porcelain", "--untracked-files=all"),
            "request checkout dirty")
    try:
        event = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    except (OSError, KeyError, ValueError) as exc:
        raise ValueError("original GitHub request event missing") from exc
    require(event.get("ref") == ref and event.get("before") == before
            and event.get("after") == sha and event.get("created") is False
            and event.get("deleted") is False and event.get("forced") is False
            and event.get("head_commit", {}).get("id") == sha
            and event.get("repository", {}).get("full_name") == batch.REPOSITORY
            and event.get("repository", {}).get("owner", {}).get("id") == int(batch.OWNER_ID)
            and event.get("sender", {}).get("id") == int(batch.OWNER_ID),
            "request not genuine first-owner GitHub push")
    doc = strict_json(file_at(repo, sha, request_path(nonce)))
    require(doc == request_doc(nonce, doc.get("source_trial_id"), doc.get("appids")),
            "request schema, selection, purpose or owner binding invalid")
    require(not issuer.remote(repo, "refs/heads/sandbox/" + tr),
            "new trial already issued; workflow rerun cannot unlock another attempt")
    return {"nonce": nonce, "trial_id": tr, "request": doc,
            "request_commit": sha, "request_blob_sha": blob(repo, sha, request_path(nonce)),
            "base_main_sha": before, "request_ref": ref}


def _source_from_git(repo, request, token):
    """Re-check real owner-issued old Notes/receipt provenance in the exact old branch."""
    source = request["request"]["source_trial_id"]
    selected = request["request"]["appids"]
    require(not is_generic(source), "cannot recursively replay prior generated trial")
    branch = batch.paths(source)["branch"]
    source_head = issuer.remote(repo, "refs/heads/" + branch)
    require(bool(source_head) and SHA.fullmatch(source_head),
            "original source sandbox not found")
    git(repo, "fetch", "--no-tags", "origin", "refs/heads/" + branch)
    require(git(repo, "rev-parse", "FETCH_HEAD") == source_head,
            "original source changed during GitHub fetch")
    with tempfile.TemporaryDirectory(prefix="generic-replay-src-") as tmp:
        checkout = Path(tmp) / "source"
        git(repo, "worktree", "add", "--detach", str(checkout), source_head)
        try:
            src = batch.scope(checkout, source)
            auth = ingest.single_introduction(checkout, batch.paths(source)["authorization"])
            require(bool(auth), "original GitHub owner authorization absent")
            marker = parent(checkout, auth)
            anchor = batch.issuer_structure(checkout, trial_id=source,
                marker_commit=marker, authorization_commit=auth)
            require(anchor.get("semantic_execution_authorized") is True
                    and anchor.get("authority_origin") in (None, "owner_main_push"),
                    "only independently issued original Research source is eligible")
            batch.authenticated_owner_run(anchor, token, batch.REPOSITORY)
            manifest, manifest_blob = v2._manifest(checkout, marker, source)
            ordered = [r for r in manifest["items"] if r["appid"] in selected]
            require(len(ordered) == len(selected)
                    and [r["appid"] for r in ordered] == selected,
                    "requested games not exact ordered subset of frozen source manifest")
            docs = {}
            source_proof = []
            for row in ordered:
                appid = row["appid"]
                original = v2.frozen_assignment(checkout, marker_commit=marker,
                    trial_id=source, appid=appid)
                file = v2._path("research", original)
                intro = ingest.single_introduction(checkout, file)
                require(bool(intro), "source Research first introduction absent: " + appid)
                receipt = receipts.require_batch_research_receipt(
                    checkout, marker_commit=marker, trial_id=source, appid=appid,
                    authorization_commit=auth, research_commit=intro)
                proof = v2.submitted_research(checkout, marker_commit=marker,
                    trial_id=source, appid=appid, introduction_commit=intro)
                require(proof["status"] == "safe_incomplete_research",
                        "source Research not safe: " + appid)
                doc = json_at(checkout, intro, file)
                v2.validate_notes(doc, original)
                docs[appid] = doc
                receipt_path = ingest._receipt_path(original)
                source_proof.append({
                    "appid": appid, "title": row["title"],
                    "group_sequence": row["group_sequence"], "item_index": row["item_index"],
                    "source_assignment_id": row["assignment_id"],
                    "research_commit": intro, "research_blob_sha": blob(checkout, intro, file),
                    "research_receipt_commit": receipt,
                    "research_receipt_blob_sha": blob(checkout, receipt, receipt_path),
                })
            pins = {
                "source_trial_id": source, "source_sandbox_head": source_head,
                "source_marker_commit": marker, "source_authorization_commit": auth,
                "source_manifest_blob_sha": manifest_blob,
                "source_manifest_pins": manifest["original_pins"],
                "source_research": source_proof,
                "request_commit": request["request_commit"],
                "request_blob_sha": request["request_blob_sha"],
                "request_nonce": request["nonce"],
            }
            return docs, pins
        finally:
            git(repo, "worktree", "remove", "--force", str(checkout))


def rows_from_pins(trial_id, pins):
    require(is_generic(trial_id) and pins["request_nonce"] == trial_id[len(PREFIX):],
            "wrong replay trial/source nonce")
    records = pins["source_research"]
    require(type(records) is list and 1 <= len(records) <= 24, "missing bounded Research source")
    result = []
    last = None
    seen = set()
    for source in records:
        a = source["appid"]
        position = (source["group_sequence"], source["item_index"])
        require(type(a) is str and a not in seen and
                isinstance(source["title"], str) and source["title"].strip() and
                isinstance(position[0], int) and isinstance(position[1], int) and
                (last is None or position > last) and
                all(type(source[k]) is str and SHA.fullmatch(source[k])
                    for k in ("research_commit", "research_blob_sha",
                              "research_receipt_commit", "research_receipt_blob_sha")),
                "source Research rows malformed or reordered")
        seen.add(a)
        last = position
        identity = {
            "trial_id": trial_id, "source_trial_id": pins["source_trial_id"],
            "source_manifest_blob_sha": pins["source_manifest_blob_sha"],
            "source_assignment_id": source["source_assignment_id"],
            "research_commit": source["research_commit"],
            "group_sequence": position[0], "item_index": position[1],
            "appid": a, "title": source["title"],
        }
        digest = hashlib.sha256(batch.canonical(identity)).hexdigest()
        result.append({"group_sequence": position[0], "item_index": position[1],
                       "appid": a, "title": source["title"],
                       "assignment_id": "batch-" + digest[:24],
                       "original_assignment_sha256": digest})
    return result


def frozen_plan(repo, trial_id, marker_commit):
    """Offline reader: immutable grant validates manifest without a new main source PR."""
    require(is_generic(trial_id), "not a generic trial")
    manifest_commit = parent(repo, marker_commit)
    grant_commit = parent(repo, manifest_commit)
    path = batch.paths(trial_id)["grant"]
    grant = json_at(repo, grant_commit, path)
    require(grant.get("schema") == "DOSSIER-NOTES-V2-BATCH-OWNER-GRANT"
            and grant.get("schema_version") == 1
            and grant.get("scope") == SCOPE and grant.get("trial_id") == trial_id
            and grant.get("base_main_sha") == parent(repo, grant_commit)
            and grant.get("request_ref") == (
                "refs/heads/" + REQUEST_BRANCH + trial_id[len(PREFIX):])
            and grant.get("request_commit") == grant.get("source_pins", {}).get("request_commit")
            and grant.get("request_blob_sha") == grant.get("source_pins", {}).get("request_blob_sha")
            and grant.get("source_pins", {}).get("source_trial_id")
            and not is_generic(grant["source_pins"]["source_trial_id"])
            and grant.get("frozen_rows") == rows_from_pins(trial_id, grant["source_pins"]),
            "frozen owner grant or exact Research rows inconsistent")
    require(file_at(repo, grant_commit, path) == file_at(repo, "HEAD", path),
            "owner replay grant was modified")
    return grant["source_pins"], grant["frozen_rows"]


def expected_grant(repo, request, pins):
    tr = request["trial_id"]
    rows = rows_from_pins(tr, pins)
    manifest = {
        "schema": "DOSSIER-NOTES-V2-FROZEN-MANIFEST", "schema_version": 2,
        "trial_id": tr, "original_pins": pins, "items": rows,
    }
    return {
        "schema": "DOSSIER-NOTES-V2-BATCH-OWNER-GRANT", "schema_version": 1,
        "scope": SCOPE, "trial_id": tr,
        "base_main_sha": request["base_main_sha"],
        "request_ref": request["request_ref"],
        "request_commit": request["request_commit"],
        "request_blob_sha": request["request_blob_sha"],
        "source_pins": pins, "frozen_rows": rows,
        "manifest_path": batch.paths(tr)["manifest"],
        "manifest_blob_sha": blob_for(batch.canonical(manifest)),
        "owner_login": batch.OWNER_LOGIN, "owner_actor_id": batch.OWNER_ID,
        "semantic_execution_approved": False, "production_approved": False,
        "canonical_ingest_approved": False,
    }, manifest


def expected_authorization(repo, trial_id, marker_commit, grant_commit, run_id):
    paths = batch.paths(trial_id)
    grant = json_at(repo, grant_commit, paths["grant"])
    return {
        "schema": "DOSSIER-NOTES-V2-BATCH-OWNER-AUTHORIZATION", "schema_version": 1,
        "trial_id": trial_id, "marker_commit": marker_commit,
        "marker_parent": parent(repo, marker_commit),
        "manifest_blob_sha": grant["manifest_blob_sha"],
        "human_grant_commit": grant_commit,
        "human_grant_blob_sha": blob(repo, grant_commit, paths["grant"]),
        "owner_actor_id": batch.OWNER_ID, "owner_login": batch.OWNER_LOGIN,
        "github_authorization_run_id": str(run_id),
        "scope": SCOPE, "authority_origin": "generic_owner_request",
        "request_ref": grant["request_ref"], "request_commit": grant["request_commit"],
        "semantic_execution_authorized": True, "assembly_authorized": True,
        "sandbox_writer_authorized": True, "production_authorized": False,
        "canonical_acceptance": False,
    }


def issuer_structure(repo, *, trial_id, marker_commit, authorization_commit):
    """Immutable one-add lineage proof. Real completed Actions check is separate."""
    require(is_generic(trial_id) and all(
        SHA.fullmatch(str(x)) for x in (marker_commit, authorization_commit)),
        "unrecognized generic authorization")
    paths = batch.paths(trial_id)
    require(require_only_new(repo, authorization_commit, [paths["authorization"]]) ==
            marker_commit, "authorization not direct child of nonce marker")
    manifest_commit = parent(repo, marker_commit)
    nonce = v2._marker_nonce(repo, marker_commit)
    require(trial_id == trial(nonce) and
            require_only_new(repo, marker_commit, [
                "data/control/dossier_notes_v2/run_starts/" + nonce + ".json"]) == manifest_commit,
            "marker not unique one-add for exact trial")
    require(json_at(repo, marker_commit,
                "data/control/dossier_notes_v2/run_starts/" + nonce + ".json") == {
                "schema": "DOSSIER-NOTES-V2-RUN-START",
                "schema_version": 2, "nonce": nonce, "trial_id": trial_id},
            "marker payload differs")
    grant_commit = require_only_new(repo, manifest_commit, [paths["manifest"]])
    base = require_only_new(repo, grant_commit, [paths["grant"]])
    pins, rows = frozen_plan(repo, trial_id, marker_commit)
    manifest = json_at(repo, manifest_commit, paths["manifest"])
    require(manifest == {
        "schema": "DOSSIER-NOTES-V2-FROZEN-MANIFEST",
        "schema_version": 2, "trial_id": trial_id, "original_pins": pins, "items": rows,
    }, "frozen manifest does not match exact GitHub-prepared Research")
    grant = json_at(repo, grant_commit, paths["grant"])
    require(grant["manifest_blob_sha"] == blob(repo, manifest_commit, paths["manifest"])
            and grant["base_main_sha"] == base
            and grant["owner_actor_id"] == batch.OWNER_ID
            and grant["owner_login"] == batch.OWNER_LOGIN
            and grant["semantic_execution_approved"] is False
            and grant["canonical_ingest_approved"] is False
            and grant["production_approved"] is False,
            "owner grant shape/flags unsafe")
    auth = json_at(repo, authorization_commit, paths["authorization"])
    run_id = auth.get("github_authorization_run_id")
    require(type(run_id) is str and run_id.isdigit() and int(run_id) > 0
            and auth == expected_authorization(repo, trial_id, marker_commit,
                                               grant_commit, run_id),
            "owner request authorization not exact or self-claimed")
    for commit, path in ((grant_commit, paths["grant"]),
                         (manifest_commit, paths["manifest"]),
                         (authorization_commit, paths["authorization"])):
        require(first_parent_contains(repo, commit, "HEAD")
                and file_at(repo, commit, path) == file_at(repo, "HEAD", path),
                "immutable issuer path changed after one-add")
    return {
        "trial_id": trial_id, "marker_commit": marker_commit,
        "authorization_commit": authorization_commit,
        "authorization_blob_sha": blob(repo, authorization_commit, paths["authorization"]),
        "manifest_blob_sha": blob(repo, manifest_commit, paths["manifest"]),
        "human_grant_commit": grant_commit, "base_main_sha": base,
        "github_actor_id": batch.OWNER_ID, "github_authorization_run_id": run_id,
        "authority_origin": "generic_owner_request",
        "request_commit": grant["request_commit"],
        "request_ref": grant["request_ref"], "source_pins": pins,
        "semantic_execution_authorized": True,
        "issuer_structural_only": True, "github_run_authenticated": False,
    }


def authenticated_owner_run(anchor, token, repository):
    require(repository == batch.REPOSITORY and bool(token)
            and anchor.get("authority_origin") == "generic_owner_request",
            "actual owner GitHub Actions token required")
    from dossier_notes_v2_per_item_receipts import _github_get
    doc = _github_get(repository, "actions/runs/" +
                      anchor["github_authorization_run_id"], token)
    branch = anchor["request_ref"].removeprefix("refs/heads/")
    nonce = anchor["trial_id"][len(PREFIX):]
    require(doc.get("id") == int(anchor["github_authorization_run_id"])
            and doc.get("event") == "push"
            and doc.get("status") == "completed"
            and doc.get("conclusion") == "success"
            and doc.get("run_attempt") == 1
            and doc.get("head_branch") == branch
            and doc.get("head_sha") == anchor["request_commit"]
            and doc.get("path") == WORKFLOW
            and doc.get("display_title") == (
                "Authorize Assembly replay " + branch + " at " + anchor["request_commit"])
            and doc.get("actor", {}).get("id") == int(batch.OWNER_ID)
            and doc.get("actor", {}).get("login") == batch.OWNER_LOGIN
            and doc.get("triggering_actor", {}).get("id") == int(batch.OWNER_ID)
            and doc.get("triggering_actor", {}).get("login") == batch.OWNER_LOGIN,
            "real successful first-attempt owner request run not confirmed")
    return True


def launch(repo, env):
    repo = Path(repo).resolve()
    request = request_guard(repo, env)
    source_docs, pins = _source_from_git(repo, request, env["GITHUB_TOKEN"])
    # Recheck expected main, request and source references immediately before issuing.
    require(issuer.remote(repo, "refs/heads/main") == request["base_main_sha"]
            and issuer.remote(repo, request["request_ref"]) == request["request_commit"]
            and issuer.remote(repo, "refs/heads/sandbox/" + pins["source_trial_id"]) ==
                pins["source_sandbox_head"],
            "main or owner-approved Research moved before the one-use grant")
    grant, manifest = expected_grant(repo, request, pins)
    tr = request["trial_id"]
    paths = batch.paths(tr)
    git(repo, "checkout", "-B", "main", request["base_main_sha"])
    require(not git(repo, "status", "--porcelain", "--untracked-files=all"),
            "main source checkout not clean")
    git(repo, "checkout", "-b", paths["branch"])
    gc = issuer.add_commit(repo, paths["grant"], grant,
                           "Dossier V2 generic replay: owner request grant")
    mc = issuer.add_commit(repo, paths["manifest"], batch.canonical(manifest),
                           "Dossier V2 generic replay: frozen Research subset manifest")
    nonce = request["nonce"]
    marker = issuer.add_commit(repo, "data/control/dossier_notes_v2/run_starts/" +
        nonce + ".json", {
            "schema": "DOSSIER-NOTES-V2-RUN-START", "schema_version": 2,
            "trial_id": tr, "nonce": nonce,
        }, "Dossier V2 generic replay: unique owner marker")
    authorization = issuer.add_commit(repo, paths["authorization"],
        expected_authorization(repo, tr, marker, gc, env["GITHUB_RUN_ID"]),
        "Dossier V2 generic replay: separate Assembly-only authorization")
    issuer_structure(repo, trial_id=tr, marker_commit=marker,
                     authorization_commit=authorization)
    outcomes = []
    for row in manifest["items"]:
        appid = row["appid"]
        assignment = v2.frozen_assignment(repo, marker_commit=marker,
                                          trial_id=tr, appid=appid)
        doc = copy.deepcopy(source_docs[appid])
        doc["assignment"] = assignment
        proposal = receipts.prepare_candidate(repo, marker_commit=marker,
            trial_id=tr, appid=appid, authorization_commit=authorization,
            document=doc)
        candidate = copy_tool.single_add(repo, proposal["output_path"],
                proposal["bytes"], "Dossier V2 generic replay: copied Research " + appid)
        checked = receipts.inspect_candidate(repo, marker_commit=marker,
            trial_id=tr, appid=appid, authorization_commit=authorization,
            introduction_commit=candidate)
        require(checked["status"] == "safe_incomplete_research",
                "new Research copy failed immutable validation")
        receipt_doc = receipts.prepare_receipt(repo, marker_commit=marker,
            trial_id=tr, appid=appid, authorization_commit=authorization,
            introduction_commit=candidate)
        receipt = copy_tool.single_add(repo, receipt_doc["receipt_path"],
            receipt_doc["receipt_bytes"], "Dossier V2 generic replay: Research receipt " + appid)
        checked_receipt = receipts.inspect_receipt_commit(repo, marker_commit=marker,
            trial_id=tr, appid=appid, authorization_commit=authorization,
            introduction_commit=candidate, receipt_commit=receipt)
        require(checked_receipt["disposition"] == "safe_incomplete_research",
                "new Research typed receipt failed immutable validation")
        outcomes.append({"appid": appid, "research_commit": candidate,
                         "research_receipt_commit": receipt})
    head = git(repo, "rev-parse", "HEAD")
    require(not git(repo, "status", "--porcelain", "--untracked-files=all")
            and issuer.remote(repo, "refs/heads/main") == request["base_main_sha"]
            and issuer.remote(repo, "refs/heads/" + paths["branch"]) is None,
            "request or sandbox changed during copy, no replay allowed")
    # One nonforce push. A missing/ambiguous readback must STOP, never retry.
    git(repo, "push", "origin", head + ":refs/heads/" + paths["branch"])
    require(issuer.remote(repo, "refs/heads/" + paths["branch"]) == head,
            "remote readback uncertain; STOP, no second push")
    return {"status": "new_assembly_only_trial_research_rebound_not_semantics",
            "trial_id": tr, "request_commit": request["request_commit"],
            "source_trial_id": pins["source_trial_id"], "branch": paths["branch"],
            "marker_commit": marker, "authorization_commit": authorization,
            "head": head, "research": outcomes,
            "canonical_acceptance": False, "deep_enabled": False,
            "assembly_performed": False, "production_written": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("owner-request-launch",))
    options = parser.parse_args()
    try:
        print(json.dumps(launch(Path.cwd(), os.environ), sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        parser.exit(2, "DOSSIER_GENERIC_REPLAY_REFUSED: " + str(exc) + "\n")


if __name__ == "__main__":
    main()

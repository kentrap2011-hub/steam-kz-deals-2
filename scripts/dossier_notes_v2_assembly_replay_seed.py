#!/usr/bin/env python3
"""One-use GitHub owner-push seeding of six old immutable Research Notes into a NEW sandbox.

This is a deterministic transport *copy*, NOT semantic Research or Assembly.
Called only inside the authenticated fresh owner main-push issuer job, after
separate grant -> manifest -> nonce marker -> direct-child authorization.
The old sandbox is fetched read-only at an exact immutable commit. Every old
Research introduction and typed receipt is rechecked; all newly rebound
Research candidates and typed receipts are committed as individual Git one-adds.
Exactly one nonforce sandbox push is attempted at the end.

Old sandbox and canonical/Deep/V1/production are never written.
"""
import copy
import json
import os
import subprocess
import tempfile
from pathlib import Path

import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_per_item_receipts as receipts
import dossier_notes_v2_research_receipt_ingest as ingest
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import blob, exists, json_at, parent, require_only_new

NEW = batch.OWNER_PUSH_REPLAY_TRIAL
NEW3 = batch.OWNER_PUSH_REPLAY_TRIAL3
REPLAYS = {NEW, NEW3}
OLD = "dossier-notes-v2-fresh6-20261114-rerun1"
OLD_HEAD = "c4232fb579fa88c4ed01afd5c45c57792c309984"
OLD_MARKER = "cdc8bcf79cef6d6e7c3c97ab91b5fb9416ab96d1"
OLD_MANIFEST_BLOB = "752d5689c3f7d055c94c1844877337eea13ebd79"
SIX = ("1000010", "102600", "1029690", "49520", "499180", "501590")


def command(repo, *args):
    p = subprocess.run(["git", *args], cwd=str(repo), check=False,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise ValueError("REPLAY_SEED_BLOCKED: Git failed (" +
                         " ".join(args[:2]) + "), exit=" + str(p.returncode) +
                         ": " + p.stderr.decode("utf-8", "replace")[:300])
    return p.stdout.decode("utf-8", "replace").strip()


def only_clean(repo):
    batch.require(not command(repo, "status", "--porcelain", "--untracked-files=all"),
                  "replay issuer checkout is dirty")


def remote_head(repo, branch):
    out = command(repo, "ls-remote", "--exit-code", "origin", "refs/heads/" + branch)
    rows = out.splitlines()
    batch.require(len(rows) == 1 and rows[0].endswith("\trefs/heads/" + branch),
                  "remote ref not unique")
    return rows[0].split("\t")[0]


def single_add(repo, path, raw, title):
    batch.require(not exists(repo, "HEAD", path) and not (repo / path).exists(),
                  "new replay path collision: " + path)
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=False) if not target.parent.exists() else None
    target.write_bytes(raw)
    command(repo, "add", "--", path)
    command(repo, "diff", "--cached", "--check")
    command(repo, "-c", "user.name=github-actions[bot]",
            "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit", "-m", title)
    commit = command(repo, "rev-parse", "HEAD")
    batch.require(require_only_new(repo, commit, [path]) == parent(repo, commit),
                  "Research candidate/receipt not independently single-added")
    return commit


def validate_source_contract(repo, trial_id=NEW):
    batch.require(trial_id in REPLAYS, "not a preapproved replay source")
    c = batch.scope(repo, trial_id)
    src = c.get("replay_source")
    batch.require(isinstance(src, dict) and set(src) == {
        "mode", "trial_id", "sandbox_head", "manifest_blob_sha", "marker_commit",
        "candidate_commits", "candidate_blobs", "research_receipt_blobs"
    }, "expected single frozen research-replay source proof absent")
    batch.require(src["mode"] == "github_verified_deterministic_rebind_of_existing_research_no_semantic_rerun"
                  and src["trial_id"] == OLD and src["sandbox_head"] == OLD_HEAD
                  and src["manifest_blob_sha"] == OLD_MANIFEST_BLOB
                  and src["marker_commit"] == OLD_MARKER,
                  "frozen original research identity not the approved old trial")
    for name in ("candidate_commits", "candidate_blobs", "research_receipt_blobs"):
        batch.require(type(src[name]) is dict and set(src[name]) == set(SIX)
                      and all(type(x) is str and batch.SHA.fullmatch(x)
                              for x in src[name].values()),
                      "frozen original Research SHA map changed: " + name)
    batch.require([row["appid"] for row in c["candidates"]] == list(SIX),
                  "replay cannot change frozen six-item scope/order")
    return src


def source_notes(old_repo, src):
    """Reverify each original single-add Git introduction and typed Research receipt."""
    batch.require(command(old_repo, "rev-parse", "HEAD") == OLD_HEAD,
                  "old sandbox has changed from its exact pinned head")
    old_authorizer = ingest.single_introduction(
        old_repo, batch.paths(OLD)["authorization"])
    batch.require(bool(old_authorizer) and parent(old_repo, old_authorizer) == OLD_MARKER,
                  "original authorizer is missing or marker changed")
    old_anchor = batch.issuer_structure(
        old_repo, trial_id=OLD, marker_commit=OLD_MARKER,
        authorization_commit=old_authorizer)
    batch.authenticated_owner_run(
        old_anchor, os.environ["GITHUB_TOKEN"], batch.REPOSITORY)
    old_manifest, old_manifest_blob = v2._manifest(old_repo, OLD_MARKER, OLD)
    batch.require(old_manifest_blob == OLD_MANIFEST_BLOB
                  and [row["appid"] for row in old_manifest["items"]] == list(SIX),
                  "original frozen manifest differs")
    result = {}
    for appid in SIX:
        intro = src["candidate_commits"][appid]
        old_assignment = v2.frozen_assignment(
            old_repo, marker_commit=OLD_MARKER, trial_id=OLD, appid=appid)
        old_path = v2._path("research", old_assignment)
        batch.require(blob(old_repo, intro, old_path) == src["candidate_blobs"][appid]
                      and blob(old_repo, "HEAD", old_path) == src["candidate_blobs"][appid],
                      "original Research blob differs: " + appid)
        receipt_commit = receipts.require_batch_research_receipt(
            old_repo, marker_commit=OLD_MARKER, trial_id=OLD,
            appid=appid, authorization_commit=old_authorizer,
            research_commit=intro)
        receipt_path = ingest._receipt_path(old_assignment)
        batch.require(blob(old_repo, receipt_commit, receipt_path)
                      == src["research_receipt_blobs"][appid],
                      "old Research typed receipt blob changed: " + appid)
        submitted = v2.submitted_research(
            old_repo, marker_commit=OLD_MARKER, trial_id=OLD,
            appid=appid, introduction_commit=intro)
        batch.require(submitted["status"] == "safe_incomplete_research",
                      "old Research is not safe and exact: " + appid)
        doc = json_at(old_repo, intro, old_path)
        v2.validate_notes(doc, old_assignment)
        result[appid] = doc
    return result


def seed(repo, *, trial_id, marker_commit, authorization_commit):
    repo = Path(repo).resolve()
    batch.require(trial_id in REPLAYS, "seed cannot authorize arbitrary trials")
    only_clean(repo)
    original = validate_source_contract(repo, trial_id)
    branch = batch.paths(trial_id)["branch"]
    current = command(repo, "rev-parse", "HEAD")
    batch.require(remote_head(repo, branch) == authorization_commit
                  and current == authorization_commit,
                  "new sandbox is not at direct-child authorization (one use)")
    anchor = batch.issuer_structure(
        repo, trial_id=trial_id, marker_commit=marker_commit,
        authorization_commit=authorization_commit)
    batch.require(anchor.get("authority_origin") == "owner_main_push"
                  and anchor["github_authorization_run_id"] == os.environ["GITHUB_RUN_ID"]
                  and anchor["semantic_execution_authorized"] is True,
                  "new sandbox not from current authenticated owner issuer")

    old_branch = batch.paths(OLD)["branch"]
    batch.require(remote_head(repo, old_branch) == OLD_HEAD,
                  "old immutable sandbox remote HEAD has moved")
    command(repo, "fetch", "--no-tags", "origin", "refs/heads/" + old_branch)
    batch.require(command(repo, "rev-parse", "FETCH_HEAD") == OLD_HEAD,
                  "old immutable Research fetch not at pinned head")

    with tempfile.TemporaryDirectory(prefix="dossier-replay-old-") as temp:
        old_checkout = Path(temp) / "old"
        command(repo, "worktree", "add", "--detach", str(old_checkout), OLD_HEAD)
        try:
            old_notes = source_notes(old_checkout, original)
        finally:
            command(repo, "worktree", "remove", "--force", str(old_checkout))

    manifest, manifest_blob = v2._manifest(repo, marker_commit, trial_id)
    batch.require(manifest_blob == anchor["manifest_blob_sha"]
                  and [row["appid"] for row in manifest["items"]] == list(SIX),
                  "new GitHub owner manifest scope drift")
    items = []
    for appid in SIX:
        assignment = v2.frozen_assignment(
            repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid)
        doc = copy.deepcopy(old_notes[appid])
        doc["assignment"] = assignment
        new_work = receipts.prepare_candidate(
            repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid,
            authorization_commit=authorization_commit, document=doc)
        candidate = single_add(repo, new_work["output_path"], new_work["bytes"],
                               "dossier v2 replay: GitHub rebind immutable Research " + appid)
        checked = receipts.inspect_candidate(
            repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid,
            authorization_commit=authorization_commit, introduction_commit=candidate)
        batch.require(checked["status"] == "safe_incomplete_research",
                      "fresh copy research introduction not independently valid")
        proposed = receipts.prepare_receipt(
            repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid,
            authorization_commit=authorization_commit, introduction_commit=candidate)
        batch.require(proposed["disposition"] == "safe_incomplete_research",
                      "copied Research receipt did not pass strict technical check")
        receipt = single_add(repo, proposed["receipt_path"], proposed["receipt_bytes"],
                             "dossier v2 replay: GitHub typed Research receipt " + appid)
        proven = receipts.inspect_receipt_commit(
            repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid,
            authorization_commit=authorization_commit, introduction_commit=candidate,
            receipt_commit=receipt)
        batch.require(proven["disposition"] == "safe_incomplete_research",
                      "new typed Research receipt not independently exact")
        items.append({"appid": appid, "original_research_commit": original["candidate_commits"][appid],
                      "rebound_candidate_commit": candidate, "new_receipt_commit": receipt})

    new_tip = command(repo, "rev-parse", "HEAD")
    only_clean(repo)
    batch.require(remote_head(repo, branch) == authorization_commit,
                  "new sandbox moved during deterministic Research preparation")
    # Exactly one non-force authenticated push: no retry if its result is ambiguous.
    command(repo, "push", "origin", new_tip + ":refs/heads/" + branch)
    batch.require(remote_head(repo, branch) == new_tip
                  and remote_head(repo, old_branch) == OLD_HEAD,
                  "GitHub readback failed; do not retry or overwrite")
    return {"status": "six_Research_rebound_by_GitHub_not_semantic_research",
            "trial_id": trial_id, "new_sandbox_head": new_tip,
            "marker_commit": marker_commit, "authorization_commit": authorization_commit,
            "items": items, "canonical_acceptance": False,
            "assembly_performed": False, "production_written": False}

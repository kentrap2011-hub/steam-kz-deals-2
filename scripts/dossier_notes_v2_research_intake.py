#!/usr/bin/env python3
"""GitHub-owned, event-driven intake of one plain Research note.

The semantic chat writes ONE small, create-only input file. This program derives
all frozen identity fields and creates the existing strict Research candidate
and typed receipt as separate Git commits. It never writes a canonical dossier,
changes a queue, retries a failed push, or performs semantic research.
Only a GitHub Actions push of an issued sandbox intake file invokes the CLI.
"""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path

import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_per_item_receipts as receipts
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import (
    file_at, first_parent_contains, git, parent, require_only_new, strict_json,
)

INTAKE_PREFIX = "data/ai_inbox/dossier_notes_v2_intake"
TRIAL = re.compile(r"^dossier-notes-v2-[a-z0-9-]+$")
APPID = re.compile(r"^[1-9][0-9]*$")
FIELDS = {"appid", "notes", "unknowns", "conflicts", "source_urls"}


def input_path(trial_id, appid):
    if not TRIAL.fullmatch(trial_id) or not APPID.fullmatch(str(appid)):
        raise ValueError("invalid bounded Research intake identity")
    return f"{INTAKE_PREFIX}/{trial_id}/{appid}.json"


def normalized_document(raw, assignment):
    """Reject unexpected fields; the chat never constructs Git/issuer metadata."""
    if (type(raw) is not dict or not {"appid", "notes"} <= raw.keys()
            or set(raw) - FIELDS or raw["appid"] != assignment["appid"]):
        raise ValueError("unexpected Research submission fields or AppID")
    notes = raw["notes"]
    if type(notes) is not str or len(notes) > 1200:
        raise ValueError("notes must be at most 1200 characters")
    optional = {}
    for simple, target in (("unknowns", "unknowns_text"), ("conflicts", "conflicts_text")):
        value = raw.get(simple)
        if value is not None and (type(value) is not str or len(value) > 1200):
            raise ValueError(simple + " must be text or null, max 1200 characters")
        optional[target] = value
    urls = raw.get("source_urls", [])
    if type(urls) is not list or len(urls) > 20 or len(set(map(str, urls))) != len(urls):
        raise ValueError("source_urls must contain at most 20 unique links")
    sources = []
    for url in urls:
        if type(url) is not str:
            raise ValueError("source URL must be text")
        locator = {"url": url}
        v2._locator(locator)
        sources.append({
            "locator": locator,
            "access": "unknown",
            "observation": "Reference supplied with Research; access not independently asserted.",
        })
    if not notes.strip() and sources:
        raise ValueError("empty research notes cannot attach asserted findings")
    doc = {
        "schema": "DOSSIER-RESEARCH-NOTES-V2",
        "schema_version": 2,
        "assignment": assignment,
        "notes_text": notes,
        "source_log": sources,
        "research_status": "notes_recorded" if notes.strip() else "no_verifiable_findings",
        **optional,
    }
    return doc


def plan(repo, branch, submission_commit, token):
    """Read-only: bind one added input file to genuine owner-authorized sandbox."""
    repo = Path(repo).resolve()
    if not isinstance(branch, str) or not branch.startswith("sandbox/"):
        raise ValueError("only separately authorized sandbox branches allowed")
    trial_id = branch[len("sandbox/"):]
    if (not TRIAL.fullmatch(trial_id)
            or branch != batch.paths(trial_id)["branch"]
            or not isinstance(token, str) or not token.strip()
            or not re.fullmatch(r"[0-9a-f]{40}", str(submission_commit))):
        raise ValueError("missing frozen trial, commit, or GitHub owner token")
    if git(repo, "symbolic-ref", "--short", "HEAD").stdout.decode().strip() != branch:
        raise ValueError("checkout is not the exact sandbox branch")
    changed = git(repo, "diff-tree", "--no-commit-id", "--name-status",
                  "-r", submission_commit).stdout.decode().strip().splitlines()
    if len(changed) != 1 or not changed[0].startswith("A\t"):
        raise ValueError("intake push must add exactly one file")
    path = changed[0][2:]
    match = re.fullmatch(re.escape(INTAKE_PREFIX) + "/" + re.escape(trial_id)
                         + r"/([1-9][0-9]*)\.json", path)
    if not match or input_path(trial_id, match.group(1)) != path:
        raise ValueError("not the exact Research intake path")
    appid = match.group(1)
    require_only_new(repo, submission_commit, [path])
    if not first_parent_contains(repo, submission_commit, "HEAD"):
        raise ValueError("intake commit not on current branch first-parent ancestry")
    auth_path = batch.paths(trial_id)["authorization"]
    history = git(repo, "log", "--first-parent", "--format=%H",
                  "HEAD", "--", auth_path).stdout.decode().splitlines()
    if len(history) != 1:
        raise ValueError("missing one-use owner authorization")
    authorization_commit = history[0]
    marker_commit = parent(repo, authorization_commit)
    if not first_parent_contains(repo, authorization_commit, submission_commit):
        raise ValueError("Research submission predates authorization")
    anchor = receipts.verify_scoped_semantic_run(
        repo, marker_commit=marker_commit, trial_id=trial_id,
        authorization_commit=authorization_commit,
        github_repository=batch.REPOSITORY, github_token=token)
    if anchor.get("github_run_authenticated") is not True:
        raise ValueError("GitHub owner-authorized run not verified")
    assignment = v2.frozen_assignment(
        repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid)
    submitted = strict_json(file_at(repo, submission_commit, path))
    doc = normalized_document(submitted, assignment)
    candidate = v2.prepare_research(
        repo, marker_commit=marker_commit, trial_id=trial_id,
        appid=appid, document=doc)
    receipt_path = (
        "data/control/dossier_notes_v2/receipts/" + trial_id
        + f"/g{assignment['group_sequence']:06d}/"
        + appid + "--" + assignment["assignment_id"] + "--research.json"
    )
    if (repo / receipt_path).exists():
        raise ValueError("typed receipt already exists: no replay")
    return {
        "trial_id": trial_id, "branch": branch, "appid": appid,
        "marker_commit": marker_commit,
        "authorization_commit": authorization_commit,
        "candidate": candidate, "receipt_path": receipt_path,
    }


def _commit_one(repo, path, raw, message):
    target = Path(repo) / path
    if target.exists():
        raise ValueError("create-only destination already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    git(repo, "add", "--", path)
    git(repo, "diff", "--cached", "--check")
    git(repo, "-c", "user.name=github-actions[bot]",
        "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
        "commit", "-m", message)
    sha = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
    require_only_new(repo, sha, [path])
    return sha


def materialize(repo, work):
    """Two existing standard single-add commits, no remote write yet."""
    repo = Path(repo).resolve()
    candidate = work["candidate"]
    appid = work["appid"]
    introduction = _commit_one(
        repo, candidate["output_path"], candidate["bytes"],
        "dossier notes v2: GitHub intake Research item " + appid)
    proof = receipts.inspect_candidate(
        repo, marker_commit=work["marker_commit"], trial_id=work["trial_id"],
        appid=appid, authorization_commit=work["authorization_commit"],
        introduction_commit=introduction)
    if (proof["transport_technically_verified"] is not True
            or proof["research_package_blob_sha"] != candidate["blob_sha"]):
        raise ValueError("Research candidate failed strict original Git inspection")
    recipe = receipts.prepare_receipt(
        repo, marker_commit=work["marker_commit"], trial_id=work["trial_id"],
        appid=appid, authorization_commit=work["authorization_commit"],
        introduction_commit=introduction)
    if recipe["receipt_path"] != work["receipt_path"]:
        raise ValueError("unexpected receipt location")
    receipt = _commit_one(
        repo, recipe["receipt_path"], recipe["receipt_bytes"],
        "dossier notes v2: GitHub intake Research receipt " + appid)
    receipts.inspect_receipt_commit(
        repo, marker_commit=work["marker_commit"], trial_id=work["trial_id"],
        appid=appid, authorization_commit=work["authorization_commit"],
        introduction_commit=introduction, receipt_commit=receipt)
    return {"candidate_commit": introduction, "receipt_commit": receipt,
            "appid": appid, "canonical_acceptance": False}


def publish(repo, branch, result):
    """One fast-forward push; never force or retry an ambiguous GitHub write."""
    if git(repo, "status", "--porcelain").stdout.strip():
        raise ValueError("cannot publish with uncommitted worktree changes")
    origin = git(repo, "remote", "get-url", "origin").stdout.decode().strip()
    if origin not in {
        "https://github.com/" + batch.REPOSITORY,
        "https://github.com/" + batch.REPOSITORY + ".git",
    }:
        raise ValueError("refuse to push to any unexpected Git remote")
    proc = subprocess.run(
        ["git", "-C", str(repo), "push", "origin", "HEAD:refs/heads/" + branch],
        capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError("sandbox GitHub push refused; no automatic retry")
    remote = git(repo, "ls-remote", "--exit-code", "origin",
                 "refs/heads/" + branch).stdout.decode().split()[0]
    if remote != result["receipt_commit"]:
        raise RuntimeError("GitHub receipt ref readback did not match")
    return {**result, "github_receipt_confirmed": True}


def reconcile(repo, branch, trigger_commit, token):
    """Process *all* unreceipted immutable inputs in frozen order, once per push.

    GitHub Actions concurrency can replace intermediate pending push jobs. A
    later event must therefore cover earlier plain inputs, not only the last
    event commit. This is bounded receipt materialization for <=24 prepared
    items, not semantic retry or a newly selected work queue.
    """
    repo = Path(repo).resolve()
    trial_id = branch.removeprefix("sandbox/")
    if not TRIAL.fullmatch(trial_id) or branch != "sandbox/" + trial_id:
        raise ValueError("non-cohort sandbox branch")
    event_changes = git(repo, "diff-tree", "--no-commit-id", "--name-status",
                        "-r", trigger_commit).stdout.decode().strip().splitlines()
    if (len(event_changes) != 1
            or not event_changes[0].startswith("A\t")
            or not event_changes[0][2:].startswith(
                INTAKE_PREFIX + "/" + trial_id + "/")
            or not first_parent_contains(repo, trigger_commit, "HEAD")):
        raise ValueError("trigger is not one issued immutable Research input")
    completed, errors = [], []
    for row in batch.rows(repo, trial_id):
        appid = row["appid"]
        raw_path = input_path(trial_id, appid)
        if not (repo / raw_path).is_file():
            continue
        target = ("data/ai_inbox/dossier_notes_v2/" + trial_id
                  + f"/g{row['group_sequence']:06d}/"
                  + appid + "--" + row["assignment_id"] + ".json")
        receipt_path = ("data/control/dossier_notes_v2/receipts/" + trial_id
                        + f"/g{row['group_sequence']:06d}/"
                        + appid + "--" + row["assignment_id"] + "--research.json")
        # Existing complete items (from either supported transport) are never
        # resubmitted. Incomplete legacy items are left untouched for diagnosis.
        if (repo / target).exists() or (repo / receipt_path).exists():
            if not ((repo / target).exists() and (repo / receipt_path).exists()):
                errors.append({"appid": appid, "problem": "partial_existing_transport"})
            continue
        history = git(repo, "log", "--first-parent", "--format=%H",
                      "HEAD", "--", raw_path).stdout.decode().splitlines()
        if len(history) != 1:
            errors.append({"appid": appid, "problem": "changed_or_unproven_input"})
            continue
        try:
            work = plan(repo, branch, history[0], token)
        except (ValueError, OSError, RuntimeError, KeyError, v2.NotesV2Error) as exc:
            errors.append({"appid": appid, "problem": type(exc).__name__})
            continue
        # A failure after candidate creation must STOP, not create an
        # orphaned candidate plus unrelated receipt or partial remote push.
        completed.append(materialize(repo, work))
    pushed = None
    if completed:
        pushed = publish(repo, branch, completed[-1])
    return {
        "plain_inputs_processed": len(completed),
        "submitted_candidates": [r["candidate_commit"] for r in completed],
        "typed_receipts": [r["receipt_commit"] for r in completed],
        "unresolved": errors,
        "github_receipt_confirmed": bool(pushed),
        "canonical_acceptance": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--submission-commit", required=True)
    args = parser.parse_args()
    if (os.environ.get("GITHUB_ACTIONS") != "true"
            or os.environ.get("GITHUB_EVENT_NAME") != "push"
            or os.environ.get("GITHUB_REPOSITORY") != batch.REPOSITORY
            or os.environ.get("GITHUB_REF_NAME") != args.branch):
        parser.error("only the exact sandbox push Action may generate receipts")
    token = os.environ.get("GH_TOKEN")
    try:
        result = reconcile(args.repo, args.branch, args.submission_commit, token)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    except (ValueError, OSError, RuntimeError, KeyError, v2.NotesV2Error) as exc:
        parser.exit(2, "DOSSIER_V2_INTAKE_BLOCKED: " + str(exc) + "\n")


if __name__ == "__main__":
    main()

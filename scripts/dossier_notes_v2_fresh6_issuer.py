#!/usr/bin/env python3
"""GitHub-owner-only, distinct two-dispatch fresh6 sandbox issuer.

Freeze: one create-only owner grant -> manifest -> run marker in NEW branch.
Authorize: a separate one-add marker-child authorization, no semantics.
No changes to original18, main, V1, Deep or canonical cache.
"""
import argparse
import json
import os
import re
import secrets
import subprocess
from pathlib import Path

from dossier_two_stage_staging import blob, file_at, git, json_at, parent, require_only_new
import dossier_notes_v2_fresh6_route as fresh
from dossier_research_notes_v2 import _marker_nonce

SHA = re.compile(r"^[0-9a-f]{40}$")
FREEZE_CONFIRM = "FREEZE_DOSSIER_NOTES_V2_FRESH6_ONCE"
AUTH_CONFIRM = "AUTHORIZE_DOSSIER_NOTES_V2_FRESH6_ONCE"
GIT_BRANCH = "refs/heads/" + fresh.BRANCH


def execute(repo, *args):
    p = git(repo, *args)
    return p.stdout.decode().strip()


def remote(repo, ref):
    p = git(repo, "ls-remote", "--exit-code", "origin", ref, required=False)
    if p.returncode == 2:
        return None
    fresh.require(p.returncode == 0, "remote ref lookup failed")
    lines = p.stdout.decode().strip().splitlines()
    fresh.require(len(lines) == 1 and lines[0].endswith("\t" + ref),
                  "remote reference ambiguous")
    return lines[0].split("\t")[0]


def guard(repo, mode, sha, confirmation, env):
    fresh.require(isinstance(sha, str) and SHA.fullmatch(sha),
                  "expected current main SHA invalid")
    workflow = fresh.ISSUE_WORKFLOW if mode == "freeze" else fresh.AUTHORIZE_WORKFLOW
    required = FREEZE_CONFIRM if mode == "freeze" else AUTH_CONFIRM
    fresh.require(confirmation == required, "separate explicit owner confirmation missing")
    fresh.require(
        env.get("GITHUB_ACTIONS") == "true"
        and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
        and env.get("GITHUB_REPOSITORY") == fresh.REPOSITORY
        and env.get("GITHUB_REPOSITORY_OWNER_ID") == fresh.OWNER_ID
        and env.get("GITHUB_ACTOR_ID") == fresh.OWNER_ID
        and env.get("GITHUB_ACTOR") == fresh.OWNER_LOGIN
        and env.get("GITHUB_TRIGGERING_ACTOR") == fresh.OWNER_LOGIN
        and env.get("GITHUB_REF") == "refs/heads/main"
        and env.get("GITHUB_WORKFLOW_REF") == f"{fresh.REPOSITORY}/{workflow}@refs/heads/main"
        and env.get("GITHUB_SHA") == sha
        and env.get("GITHUB_RUN_ATTEMPT") == "1"
        and str(env.get("GITHUB_RUN_ID", "")).isdigit(),
        "only actual first-attempt owner GitHub Actions workflow_dispatch may issue")
    fresh.require(execute(repo, "symbolic-ref", "--short", "HEAD") == "main"
                  and execute(repo, "rev-parse", "HEAD") == sha
                  and remote(repo, "refs/heads/main") == sha,
                  "main SHA or branch changed during owner confirmation")
    origin = execute(repo, "remote", "get-url", "origin")
    fresh.require(origin in {
        "https://github.com/" + fresh.REPOSITORY,
        "https://github.com/" + fresh.REPOSITORY + ".git",
        "git@github.com:" + fresh.REPOSITORY + ".git",
        "git@github.com:" + fresh.REPOSITORY,
        "ssh://git@github.com/" + fresh.REPOSITORY + ".git",
    }, "only canonical GitHub repository remote may receive issuer commits")
    fresh.require(not execute(repo, "status", "--porcelain", "--untracked-files=all"),
                  "dirty Git checkout cannot issue authority")
    fresh.scope(repo)


def add_commit(repo, path, document, message):
    f = Path(repo) / path
    fresh.require(not f.exists(), "create-only artifact already exists: " + path)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(fresh.canonical(document) if isinstance(document, dict) else document)
    execute(repo, "add", "--", path)
    execute(repo, "diff", "--cached", "--check")
    execute(repo, "-c", "user.name=github-actions[bot]",
            "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit", "-m", message)
    child = execute(repo, "rev-parse", "HEAD")
    require_only_new(repo, child, [path])
    return child


def freeze(repo, expected):
    fresh.require(remote(repo, GIT_BRANCH) is None,
                  "fresh6 sandbox already exists, second freeze forbidden")
    c = fresh.scope(repo)
    blueprint = fresh.manifest_blueprint(repo)
    base = execute(repo, "rev-parse", "HEAD")
    execute(repo, "checkout", "-b", fresh.BRANCH)
    grant_doc = {
        "schema": "DOSSIER-NOTES-V2-FRESH6-OWNER-GRANT",
        "schema_version": 1, "trial_id": fresh.TRIAL,
        "base_main_sha": base,
        "source_pins": fresh.pins(c), "manifest_path": fresh.MANIFEST_PATH,
        "manifest_blob_sha": blueprint["blob_sha"],
        "owner_login": fresh.OWNER_LOGIN, "owner_actor_id": fresh.OWNER_ID,
        "scope": "one_new_fresh6_issuer_only_not_original18",
        "semantic_execution_approved": False,
        "production_approved": False, "canonical_ingest_approved": False,
    }
    grant_commit = add_commit(repo, fresh.GRANT_PATH, grant_doc,
                              "Grant exact fresh6 sandbox issuance only")
    manifest_commit = add_commit(repo, fresh.MANIFEST_PATH, blueprint["bytes"],
                                 "Freeze six exact GitHub-prepared V2 assignments")
    nonce = secrets.token_hex(16)
    marker = {
        "schema": "DOSSIER-NOTES-V2-RUN-START", "schema_version": 2,
        "trial_id": fresh.TRIAL, "nonce": nonce,
    }
    marker_commit = add_commit(
        repo, f"data/control/dossier_notes_v2/run_starts/{nonce}.json",
        marker, "Freeze fresh6 inactive run-start marker")
    fresh.require(parent(repo, marker_commit) == manifest_commit
                  and parent(repo, manifest_commit) == grant_commit
                  and remote(repo, "refs/heads/main") == expected
                  and remote(repo, GIT_BRANCH) is None,
                  "frozen original source, clean chain or new-ref lease drifted")
    execute(repo, "push", "--porcelain",
            "--force-with-lease=" + GIT_BRANCH + ":",
            "origin", "HEAD:" + GIT_BRANCH)
    fresh.require(remote(repo, GIT_BRANCH) == marker_commit, "marker remote proof failed")
    execute(repo, "fetch", "--no-tags", "origin", GIT_BRANCH)
    fresh.require(execute(repo, "rev-parse", "FETCH_HEAD") == marker_commit,
                  "new marker readback failed")
    return {
        "status": "fresh6_issued_marker_only_not_semantics",
        "sandbox_branch": fresh.BRANCH, "grant_commit": grant_commit,
        "manifest_commit": manifest_commit, "marker_commit": marker_commit,
        "authorization_commit": None, "semantic_execution_authorized": False,
        "canonical_acceptance": False, "production_enabled": False,
    }


def authorize(repo, expected, marker_commit, env):
    fresh.require(isinstance(marker_commit, str) and SHA.fullmatch(marker_commit),
                  "exact new marker SHA required")
    fresh.require(remote(repo, GIT_BRANCH) == marker_commit,
                  "new sandbox not exactly unconsumed marker HEAD")
    execute(repo, "fetch", "--no-tags", "origin", GIT_BRANCH)
    fresh.require(execute(repo, "rev-parse", "FETCH_HEAD") == marker_commit,
                  "remote marker not durable")
    grant_commit = execute(repo, "rev-parse", marker_commit + "^^")
    manifest_commit = parent(repo, marker_commit)
    base = parent(repo, grant_commit)
    from dossier_two_stage_staging import first_parent_contains
    fresh.require(first_parent_contains(repo, base, expected)
                  and execute(repo, "rev-parse", base) == base,
                  "marker issuer base must be on current main FIRST-parent history")
    fresh.require(require_only_new(repo, grant_commit, [fresh.GRANT_PATH]) == base
                  and require_only_new(repo, manifest_commit, [fresh.MANIFEST_PATH]) == grant_commit,
                  "grant/manifest Git chain differs")
    nonce = _marker_nonce(repo, marker_commit)
    path = f"data/control/dossier_notes_v2/run_starts/{nonce}.json"
    fresh.require(require_only_new(repo, marker_commit, [path]) == manifest_commit,
                  "frozen marker not single-add")
    fresh.require(json_at(repo, marker_commit, path) == {
        "schema": "DOSSIER-NOTES-V2-RUN-START", "schema_version": 2,
        "nonce": nonce, "trial_id": fresh.TRIAL,
    }, "marker payload differs from granted trial")
    bp = fresh.manifest_blueprint(repo)
    fresh.require(file_at(repo, manifest_commit, fresh.MANIFEST_PATH) == bp["bytes"],
                  "manifest identity/edition drift")
    execute(repo, "checkout", "--detach", marker_commit)
    grant = json_at(repo, grant_commit, fresh.GRANT_PATH)
    expected_grant = {
        "schema": "DOSSIER-NOTES-V2-FRESH6-OWNER-GRANT",
        "schema_version": 1, "trial_id": fresh.TRIAL,
        "base_main_sha": base, "source_pins": fresh.pins(fresh.scope(repo)),
        "manifest_path": fresh.MANIFEST_PATH, "manifest_blob_sha": bp["blob_sha"],
        "owner_login": fresh.OWNER_LOGIN, "owner_actor_id": fresh.OWNER_ID,
        "scope": "one_new_fresh6_issuer_only_not_original18",
        "semantic_execution_approved": False,
        "production_approved": False, "canonical_ingest_approved": False,
    }
    fresh.require(grant == expected_grant, "grant was not exact new fresh6 owner issue")
    record = {
        "schema": "DOSSIER-NOTES-V2-FRESH6-OWNER-AUTHORIZATION",
        "schema_version": 1, "trial_id": fresh.TRIAL,
        "marker_commit": marker_commit, "marker_parent": manifest_commit,
        "manifest_blob_sha": bp["blob_sha"],
        "human_grant_commit": grant_commit,
        "human_grant_blob_sha": blob(repo, grant_commit, fresh.GRANT_PATH),
        "owner_actor_id": fresh.OWNER_ID, "owner_login": fresh.OWNER_LOGIN,
        "github_authorization_run_id": env["GITHUB_RUN_ID"],
        "scope": "one_manual_fresh6_research_and_assembly_sandbox_only",
        "semantic_execution_authorized": True, "assembly_authorized": True,
        "sandbox_writer_authorized": True, "production_authorized": False,
        "canonical_acceptance": False,
    }
    auth_commit = add_commit(repo, fresh.AUTH_PATH, record,
                             "Authorize one fresh6 semantic sandbox pilot only")
    checked = fresh.issuer_structure(repo, marker_commit=marker_commit,
                                     authorization_commit=auth_commit)
    fresh.require(checked["semantic_execution_authorized"]
                  and remote(repo, GIT_BRANCH) == marker_commit
                  and remote(repo, "refs/heads/main") == expected,
                  "issuer validation or remote lease changed")
    execute(repo, "push", "--porcelain",
            "--force-with-lease=" + GIT_BRANCH + ":" + marker_commit,
            "origin", "HEAD:" + GIT_BRANCH)
    fresh.require(remote(repo, GIT_BRANCH) == auth_commit, "authorization remote proof failed")
    execute(repo, "fetch", "--no-tags", "origin", GIT_BRANCH)
    fresh.require(execute(repo, "rev-parse", "FETCH_HEAD") == auth_commit,
                  "authorization readback changed")
    return {
        "status": "fresh6_owner_authorization_issued_not_semantic_execution",
        "sandbox_branch": fresh.BRANCH, "marker_commit": marker_commit,
        "authorization_commit": auth_commit, "github_authorization_run_id": env["GITHUB_RUN_ID"],
        "semantic_execution_authorized": True, "authenticated_run_completed": False,
        "canonical_acceptance": False, "production_enabled": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["freeze", "authorize"])
    parser.add_argument("--expected-main-sha", required=True)
    parser.add_argument("--marker-commit")
    parser.add_argument("--confirmation", required=True)
    args = parser.parse_args()
    repo = Path.cwd()
    try:
        guard(repo, args.mode, args.expected_main_sha, args.confirmation, os.environ)
        result = (freeze(repo, args.expected_main_sha)
                  if args.mode == "freeze" else
                  authorize(repo, args.expected_main_sha, args.marker_commit, os.environ))
        print(json.dumps(result, sort_keys=True))
    except (ValueError, OSError, subprocess.CalledProcessError, KeyError) as exc:
        parser.exit(2, "FRESH6_ISSUER_REFUSED: " + str(exc) + "\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read-only owner/generic route preflight for the existing isolated V2 writer.

This handles ONLY correctly shaped generic request trials. Genuine legacy
cohorts keep their unmodified dossier_notes_v2_batch_preflight.py route.
This code never stages, creates authority, dispatches, or writes records.
"""
import argparse
import json
import os
import re
from pathlib import Path

import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_generic_replay as generic
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import git


H40 = re.compile(r"[0-9a-f]{40}\Z")


def require(ok, message):
    if not ok:
        raise ValueError("GENERIC_V2_WRITER_PREFLIGHT_BLOCKED: " + message)


def inspect(repo, *, trial_id, marker_commit, item_commits, env=None):
    """Prove existing issuer/owner scope before entering the writer's data path.

    The writer independently repeats authorization, receipt and final dossier
    verification. An issuer/owner failure here must not enter that path.
    """
    root = Path(repo).resolve()
    env = os.environ if env is None else env
    require(generic.is_generic(trial_id),
            "unknown, malformed or legacy trial is not a generic owner request")
    require(isinstance(marker_commit, str) and H40.fullmatch(marker_commit),
            "invalid immutable marker")
    require(env.get("GITHUB_ACTIONS") == "true"
            and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
            and env.get("GITHUB_REF") == "refs/heads/main"
            and env.get("GITHUB_WORKFLOW_REF") ==
                batch.REPOSITORY + "/" + batch.WRITER_WORKFLOW + "@refs/heads/main"
            and env.get("GITHUB_REPOSITORY") == batch.REPOSITORY
            and env.get("GITHUB_ACTOR_ID") == batch.OWNER_ID
            and env.get("GITHUB_REPOSITORY_OWNER_ID") == batch.OWNER_ID
            and env.get("GITHUB_ACTOR") == batch.OWNER_LOGIN
            and env.get("GITHUB_TRIGGERING_ACTOR") == batch.OWNER_LOGIN
            and env.get("GITHUB_RUN_ATTEMPT") == "1"
            and str(env.get("GITHUB_RUN_ID", "")).isdigit()
            and int(env["GITHUB_RUN_ID"]) > 0,
            "not the real owner first-attempt main-ref writer dispatch")
    require(type(item_commits) is dict and 1 <= len(item_commits) <= 24,
            "bounded per-item immutable SHA map required")
    path = batch.paths(trial_id)
    require(git(root, "symbolic-ref", "--short", "HEAD").stdout.decode().strip()
            == path["branch"], "not the exact isolated sandbox branch")
    generic.policy(root)
    auths = git(root, "log", "--first-parent", "--format=%H", "HEAD", "--",
                path["authorization"]).stdout.decode().splitlines()
    require(len(auths) == 1 and H40.fullmatch(auths[0]),
            "missing, ambiguous or rewritten owner authorization")
    anchor = batch.issuer_structure(
        root, trial_id=trial_id, marker_commit=marker_commit,
        authorization_commit=auths[0])
    require(anchor.get("authority_origin") == "generic_owner_request"
            and anchor.get("semantic_execution_authorized") is True,
            "no immutable generic owner grant")
    manifest, manifest_sha = v2._manifest(root, marker_commit, trial_id)
    _, rows = generic.frozen_plan(root, trial_id, marker_commit)
    require(manifest.get("items") == rows
            and manifest_sha == anchor["manifest_blob_sha"]
            and 1 <= len(rows) <= 24
            and len({r["appid"] for r in rows}) == len(rows),
            "frozen manifest, immutable assignments or version differs")
    allowed = {r["appid"] for r in rows}
    for appid, pair in item_commits.items():
        require(appid in allowed and type(pair) is dict
                and set(pair) == {"research_commit", "assembly_commit"}
                and all(isinstance(pair.get(key), str)
                        and H40.fullmatch(pair[key])
                        for key in ("research_commit", "assembly_commit")),
                "per-item Git transport differs from frozen scope")
    token = env.get("GITHUB_TOKEN")
    require(bool(token), "real owner GitHub authentication token absent")
    # Must query the real completed first-attempt owner request Actions run.
    # The immutable Git commit/actor fields alone are never authorization.
    require(batch.authenticated_owner_run(anchor, token, batch.REPOSITORY) is True,
            "completed authenticated owner Actions request not confirmed")

    # For the one approved Lean transaction, preserve its independently frozen
    # six pairs, typed Assembly receipt blobs, exact HEAD and 0/6 one-use gate
    # before any main writer verification could stage a file.
    from dossier_lean_canonical_dual import SANDBOX_GRANT, require_isolated_sandbox_writer
    lean_grant = json.loads(SANDBOX_GRANT.read_text(encoding="utf-8"))
    if trial_id == lean_grant["trial_id"]:
        require_isolated_sandbox_writer(
            root, trial_id=trial_id, marker_commit=marker_commit,
            item_commits=item_commits, issuer=anchor)
    return {
        "status": "authenticated_generic_owner_preflight_passed_read_only",
        "trial_id": trial_id, "marker_commit": marker_commit,
        "candidate_count": len(rows), "selected_count": len(item_commits),
        "source_kind": "immutable_generic_owner_request",
        "canonical_acceptance": False, "production_authorized": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--marker-commit", required=True)
    parser.add_argument("--item-commits-json", required=True)
    args = parser.parse_args()
    try:
        items = json.loads(args.item_commits_json)
        print(json.dumps(inspect(
            args.repo, trial_id=args.trial_id, marker_commit=args.marker_commit,
            item_commits=items), ensure_ascii=False, sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError, v2.NotesV2Error) as exc:
        parser.exit(2, "GENERIC_V2_WRITER_PREFLIGHT_BLOCKED: " + str(exc) + "\n")


if __name__ == "__main__":
    main()

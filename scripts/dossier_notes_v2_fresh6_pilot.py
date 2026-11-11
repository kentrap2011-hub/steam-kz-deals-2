#!/usr/bin/env python3
"""Bounded one-game-at-a-time fresh6 Research/Assembly GitHub transport.

No semantic generation, retry, queue walking, new schedules or canonical writes.
Run ONLY after a separately authenticated successful owner manual authorizer.
"""
import argparse
import json
import os
import re
from pathlib import Path

import dossier_notes_v2_fresh6_route as fresh
import dossier_notes_v2_per_item_receipts as transport
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import git


def execute(args):
    repo = Path(args.repo).resolve()
    c = v2._contract()
    scope = fresh.scope(repo)
    if (c.get("active") is not False
            or c.get("production_enabled") is not False
            or c.get("authorized_for_canonical_ingest") is not False
            or scope["trial_id"] != fresh.TRIAL
            or scope["proposed_sandbox_branch"] != fresh.BRANCH):
        v2.reject("wrong_binding", "only inactive isolated six-game trial is allowed")
    head_branch = git(repo, "symbolic-ref", "--short", "HEAD").stdout.decode().strip()
    if head_branch != fresh.BRANCH:
        v2.reject("wrong_binding", "not on exact separately issued fresh6 Git sandbox")
    anchor = fresh.issuer_structure(
        repo, marker_commit=args.marker_commit,
        authorization_commit=args.authorization_commit)
    manifest, manifest_blob = v2._manifest(repo, args.marker_commit, fresh.TRIAL)
    if (len(manifest["items"]) != 6 or len(set(i["appid"] for i in manifest["items"])) != 6
            or manifest_blob != anchor["manifest_blob_sha"]):
        v2.reject("wrong_binding", "frozen fresh6 issuer does not bind exactly six games")
    if args.command == "inspect":
        return {
            "status": "fresh6_issuer_structure_only_not_run_authentication",
            "trial_id": fresh.TRIAL, "branch": fresh.BRANCH,
            "issuer": anchor,
            "items": [{k: item[k] for k in (
                "appid", "title", "group_sequence", "item_index", "assignment_id"
            )} for item in manifest["items"]],
            "semantic_execution_performed": False,
            "production_authorized": False, "canonical_acceptance": False,
        }
    if args.appid not in {i["appid"] for i in manifest["items"]}:
        v2.reject("wrong_binding", "AppID not in exact six frozen GitHub assignments")
    if not (isinstance(args.expected_remote_head, str)
            and re.fullmatch(r"[0-9a-f]{40}", args.expected_remote_head)):
        v2.reject("wrong_binding", "explicit exact new remote SHA required")
    if args.document is None or not Path(args.document).is_file():
        v2.reject("wrong_binding", "a worker-provided single-item JSON is mandatory")
    document = json.loads(Path(args.document).read_text(encoding="utf-8"))
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        v2.reject("wrong_binding", "actual authenticated GitHub token required")
    checked = transport.verify_scoped_semantic_run(
        repo, marker_commit=args.marker_commit, trial_id=fresh.TRIAL,
        authorization_commit=args.authorization_commit,
        github_repository=fresh.REPOSITORY, github_token=token)
    if not checked["github_run_authenticated"]:
        v2.reject("wrong_binding", "GitHub owner authorizing run has not succeeded")
    kwargs = {
        "repo": repo, "branch": fresh.BRANCH,
        "expected_remote_head": args.expected_remote_head,
        "marker_commit": args.marker_commit, "trial_id": fresh.TRIAL,
        "authorization_commit": args.authorization_commit,
        "appid": args.appid, "document": document,
        "github_repository": fresh.REPOSITORY, "github_token": token,
    }
    if args.command == "research":
        return transport.publish_one_research_item_remote(**kwargs)
    if args.command == "assembly":
        if not args.research_commit or not re.fullmatch(r"[0-9a-f]{40}", args.research_commit):
            v2.reject("wrong_binding", "exact original Research SHA required for Assembly")
        return transport.publish_one_assembly_item_remote(
            **kwargs, research_commit=args.research_commit)
    v2.reject("wrong_binding", "unsupported one-item semantic phase")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("inspect", "research", "assembly"))
    p.add_argument("--repo", default=".")
    p.add_argument("--marker-commit", required=True)
    p.add_argument("--authorization-commit", required=True)
    p.add_argument("--appid")
    p.add_argument("--expected-remote-head")
    p.add_argument("--research-commit")
    p.add_argument("--document")
    args = p.parse_args()
    try:
        print(json.dumps(execute(args), ensure_ascii=False, indent=2, sort_keys=True))
    except (ValueError, OSError, KeyError, v2.NotesV2Error) as exc:
        p.exit(2, "FRESH6_PILOT_REFUSED: " + str(exc) + "\n")


if __name__ == "__main__":
    main()

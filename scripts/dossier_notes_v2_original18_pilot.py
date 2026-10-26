#!/usr/bin/env python3
"""Bounded V2 original-18 per-item GitHub transport and frozen-scope inspection.

Only the two existing semantic stages are external. This tool NEVER performs
Research, Assembly, retries, authorization, or canonical publication. The
original V2 issuer and this repo's authenticated GitHub transport are reused.
"""
import argparse
import json
import os
from pathlib import Path

import dossier_research_notes_v2 as v2
import dossier_notes_v2_per_item_receipts as transport

REPOSITORY = "kentrap2011-hub/steam-kz-deals-2"


def run(args):
    repo = Path(args.repo).resolve()
    cfg = v2._contract()
    issuer = cfg["manual_v2_issuer"]
    trial_id = issuer["trial_id"]
    branch = issuer["sandbox_branch"]
    if (trial_id != "dossier-notes-v2-original18-first"
            or branch != "sandbox/dossier-notes-v2-original18-first"
            or cfg["production_enabled"] is not False
            or cfg["authorized_for_canonical_ingest"] is not False
            or cfg["active"] is not False):
        v2.reject("wrong_binding", "only the inactive, pinned original-18 pilot is supported")
    authorization = transport.issuer_structure(
        repo, marker_commit=args.marker_commit, trial_id=trial_id,
        authorization_commit=args.authorization_commit)
    manifest, _ = v2._manifest(repo, args.marker_commit, trial_id)
    frozen = [item["appid"] for item in manifest["items"]]
    if len(frozen) != 18 or len(set(frozen)) != 18:
        v2.reject("wrong_binding", "original frozen 18 not verified")
    if args.command == "inspect":
        return {
            "status": "structural_only_no_semantic_permission",
            "trial_id": trial_id, "sandbox_branch": branch,
            "marker_commit": args.marker_commit,
            "authorization_commit": args.authorization_commit,
            "items": [{"appid": i["appid"], "group_sequence": i["group_sequence"],
                       "item_index": i["item_index"], "title": i["title"]}
                      for i in manifest["items"]],
            "issuer": authorization,
            "semantic_execution_authorized": False,
            "canonical_acceptance": False,
        }
    # Original GitHub issuer evidence is only structural: the already merged\n    # V2 contract intentionally denies live semantics. Never let a CLI flag or\n    # user-supplied document promote it to semantic authorization.\n    if (cfg.get("authorized_for_semantic_execution") is not True\n            or authorization.get("semantic_execution_authorized") is not True):\n        v2.reject("wrong_binding",\n                  "V2 semantic authorization is disabled; structural issuer is insufficient")\n    if args.appid not in frozen:\n        v2.reject("wrong_binding", "item not in immutable original-18 pilot")
    if args.expected_remote_head is None or len(args.expected_remote_head) != 40:
        v2.reject("wrong_binding", "fresh exact remote parent SHA required")
    if (not isinstance(args.document, str)
            or not Path(args.document).is_file()):
        v2.reject("wrong_binding", "separate worker-provided JSON document required")
    document = json.loads(Path(args.document).read_text(encoding="utf-8"))
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        v2.reject("wrong_binding", "authenticated GitHub readback token missing")
    # Authenticated Actions evidence closes the gap between an immutable Git
    # authorizer document and an actually successful human dispatch.
    run_id = authorization["github_authorization_run_id"]
    event = transport._github_get(REPOSITORY, "actions/runs/" + run_id, token)
    identity = cfg["original18_trial_scoped_authorization"]
    if (event.get("id") != int(run_id)
            or event.get("event") != "workflow_dispatch"
            or event.get("head_branch") != "main"
            or event.get("run_attempt") != 1
            or event.get("status") != "completed"
            or event.get("conclusion") != "success"
            or event.get("actor", {}).get("id") != int(identity["github_owner_actor_id"])
            or event.get("actor", {}).get("login") != identity["github_owner_login"]
            or event.get("path") != ".github/workflows/authorize-dossier-shadow-research-feasibility.yml"):
        v2.reject("wrong_binding", "successful authenticated original18 authorizer run not proven")
    kwargs = {
        "repo": repo, "branch": branch, "expected_remote_head": args.expected_remote_head,
        "marker_commit": args.marker_commit, "trial_id": trial_id,
        "appid": args.appid, "authorization_commit": args.authorization_commit,
        "document": document, "github_repository": REPOSITORY, "github_token": token,
    }
    if args.command == "research":
        return transport.publish_one_research_item_remote(**kwargs)
    if args.command == "assembly":
        if args.research_commit is None:
            v2.reject("wrong_binding", "original Research Git introduction SHA required")
        return transport.publish_assembly_item_remote(
            research_commit=args.research_commit, **kwargs)
    v2.reject("wrong_binding", "unrecognized phase")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inspect", "research", "assembly"))
    parser.add_argument("--repo", default=".")
    parser.add_argument("--marker-commit", required=True)
    parser.add_argument("--authorization-commit", required=True)
    parser.add_argument("--appid")
    parser.add_argument("--expected-remote-head")
    parser.add_argument("--research-commit")
    parser.add_argument("--document", help="Path to exact one-item JSON from an authorized worker")
    args = parser.parse_args()
    try:
        out = run(args)
    except (v2.NotesV2Error, ValueError, OSError, KeyError) as exc:
        parser.exit(2, "V2 pilot refused: " + str(exc) + "\n")
    print(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

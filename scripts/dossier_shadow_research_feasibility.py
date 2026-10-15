#!/usr/bin/env python3
"""Independent GitHub-owned, create-once feasibility authority AFTER original freeze.

Original publisher and frozen_trial status are NEVER changed.  Only a separate
manual GitHub Action may add one authorization commit directly on the original
marker.  --verify is read-only and requires the actual durable remote branch.
"""
import argparse
import json
import os
import re
from pathlib import Path

from dossier_shadow_research_trial import (
    CONTRACT as ORIGINAL_CONTRACT, PROMPT as ORIGINAL_PROMPT,
    PREFIX, TRIAL, frozen_trial, require, json_git, blob,
    validate_candidate, inspect_transport,
)
from dossier_shadow_research_trial_publish import (
    BRANCH, BUFFER, EXPECTED_APPIDS, ORDER, REPOSITORY,
    assert_clean, assert_one_new_path, commit_new, remote_sha, run,
)
from dossier_two_stage_staging import first_parent_contains, git

FEASIBILITY_CONTRACT = "config/dossier_shadow_research_feasibility_contract_v1.json"
FEASIBILITY_PROMPT = "config/dossier_shadow_research_feasibility_one_shot_prompt.md"
FEASIBILITY_VERIFIER = "scripts/dossier_shadow_research_feasibility.py"
AUTH_PATH = PREFIX + "/authorizations/research-feasibility-v1.json"
WORKFLOW = ".github/workflows/authorize-dossier-shadow-research-feasibility.yml"
CONFIRMATION = "AUTHORIZE_DOSSIER_SHADOW_18_FEASIBILITY_ONCE"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def check_contract(repo, parent):
    cfg = json_git(repo, parent, FEASIBILITY_CONTRACT)
    require(cfg.get("schema") == "DOSSIER-SHADOW-RESEARCH-FEASIBILITY-AUTHORITY-V1"
            and cfg.get("version") == 1 and cfg.get("trial_id") == TRIAL
            and cfg.get("owner") == "github_actions_control_plane"
            and cfg.get("mode") == "nonproduction_manual_real_research_feasibility_only"
            and cfg.get("original_marker_branch") == BRANCH
            and cfg.get("original_buffer_path") == BUFFER
            and cfg.get("authorization_path") == AUTH_PATH
            and cfg.get("predeclared_semantic_prompt") == FEASIBILITY_PROMPT
            and cfg.get("predeclared_verifier") == FEASIBILITY_VERIFIER
            and cfg.get("group_order") == ORDER
            and cfg.get("appids") == EXPECTED_APPIDS
            and cfg.get("research_schema") == "config/dossier_research_package_v1.schema.json"
            and cfg.get("reviewer_AB_C_appointment_required_before_feasibility") is False
            and cfg.get("original_sandbox_flags_must_stay_false") is True
            and cfg.get("original_frozen_trial_status_must_stay") == "blocked"
            and cfg.get("one_stage_owner_unchanged") is True
            and cfg.get("production_execution") is False
            and cfg.get("canonical_production_authority_active") is False
            and cfg.get("assembly_authorized") is False
            and cfg.get("scheduled_tasks") is False
            and cfg.get("new_retry_or_recovery") is False
            and cfg.get("implied_acceptance") is False,
            "feasibility predeclared sandbox/production boundary modified")
    return cfg


def original_blocked_trial(repo, marker_commit, buffer_path):
    trial = frozen_trial(repo, marker_commit=marker_commit, buffer_path=buffer_path)
    parent = trial["marker_parent"]
    original = json_git(repo, parent, ORIGINAL_CONTRACT)
    require(trial["status"] == "blocked"
            and trial["sandbox_semantics_authorized"] is False
            and trial["canonical_acceptance"] is False
            and original["standalone_sandbox_semantics_approved"] is False
            and original["reviewer_roles_finalized"] is False
            and original["production_execution"] is False
            and original["canonical_production_authority_active"] is False,
            "original immutable publisher BLOCKED gate must not be reinterpreted")
    check_contract(repo, parent)
    require(len(trial["items"]) == 18
            and [x["group_sequence"] for x in trial["items"]]
                == [seq for seq in ORDER for _ in range(3)]
            and [x["item_index"] for x in trial["items"]] == [0, 1, 2] * 6
            and [x["appid"] for x in trial["items"]] == EXPECTED_APPIDS,
            "frozen scope cannot be selected or changed by worker")
    require(git(repo, "cat-file", "-e", marker_commit + ":" + AUTH_PATH,
                required=False).returncode != 0,
            "authorization existed in original marker; not additive")
    return trial


def expected_authorization(repo, trial):
    parent = trial["marker_parent"]
    frozen = json_git(repo, parent, BUFFER)
    return {
        "schema": "DOSSIER-SHADOW-RESEARCH-FEASIBILITY-START-V1",
        "version": 1, "trial_id": TRIAL,
        "original_marker_commit": trial["marker_commit"],
        "original_marker_parent": parent, "original_marker_nonce": trial["nonce"],
        "research_buffer_path": BUFFER,
        "research_buffer_blob_sha": trial["buffer_blob_sha"],
        "research_buffer_id": frozen["research_buffer_id"],
        "original_trial_contract_blob_sha": blob(repo, parent, ORIGINAL_CONTRACT),
        "original_semantic_prompt_blob_sha": blob(repo, parent, ORIGINAL_PROMPT),
        "feasibility_contract_blob_sha": blob(repo, parent, FEASIBILITY_CONTRACT),
        "feasibility_prompt_blob_sha": blob(repo, parent, FEASIBILITY_PROMPT),
        "feasibility_verifier_blob_sha": blob(repo, parent, FEASIBILITY_VERIFIER),
        "research_schema_blob_sha": blob(repo, parent,
                                        "config/dossier_research_package_v1.schema.json"),
        "group_order": list(ORDER), "appids": list(EXPECTED_APPIDS),
        "mode": "sandbox_feasibility_Research_only_not_quality_approval",
        "quality_gate": "independent_AB_C_required_later_before_production",
        "canonical_acceptance": False, "assembly_authorized": False,
        "production_authorized": False, "scheduled_tasks": False,
    }


def verify_authorization_commit(repo, *, marker_commit, buffer_path, authorization_commit):
    """Structural verification only: NOT semantic readiness until remote proof."""
    require(isinstance(authorization_commit, str)
            and SHA40.fullmatch(authorization_commit), "exact authorization SHA required")
    trial = original_blocked_trial(repo, marker_commit, buffer_path)
    parents = git(repo, "rev-list", "--parents", "-n", "1",
                  authorization_commit).stdout.decode().split()
    require(parents == [authorization_commit, marker_commit],
            "authorization MUST be a single direct child of original marker")
    delta = git(repo, "diff-tree", "--no-commit-id", "--name-status", "-r",
                authorization_commit).stdout.decode().splitlines()
    require(delta == ["A\t" + AUTH_PATH],
            "authorization must add ONLY original fixed create-only path")
    require(json_git(repo, authorization_commit, AUTH_PATH)
            == expected_authorization(repo, trial),
            "authorization marker/parent/contract/prompt/buffer/18-item binding mismatch")
    return trial


def assert_canonical_remote(repo):
    """Remote source must be this actual GitHub repository, not a local fixture."""
    origin = run(repo, "remote", "get-url", "origin")
    pattern = (r"(?:https://(?:[^/@]+@)?github\.com/|git@github\.com:|"
               r"ssh://git@github\.com/)" + re.escape(REPOSITORY) + r"(?:\.git)?")
    require(re.fullmatch(pattern, origin) is not None,
            "origin is not exact canonical public GitHub repository")


def authorized_trial(repo, *, marker_commit, buffer_path, authorization_commit):
    """Read-only READY only with remote durable authority and exact first parent."""
    trial = verify_authorization_commit(
        repo, marker_commit=marker_commit, buffer_path=buffer_path,
        authorization_commit=authorization_commit)
    assert_canonical_remote(repo)
    # The publisher/authorizer actions are the only permitted issuers. Never
    # trust an arbitrary local Git commit, SHA supplied by chat or test fixture.
    remote = remote_sha(repo, "refs/heads/" + BRANCH)
    require(remote is not None, "actual GitHub-owned sandbox branch absent")
    require(first_parent_contains(repo, authorization_commit, remote),
            "authorization is not on live sandbox first-parent chain")
    require(first_parent_contains(repo, marker_commit, authorization_commit),
            "original frozen marker lineage lost")
    # Must also be on the checked-out sandbox history to prevent accidental main writes.
    head = run(repo, "rev-parse", "HEAD")
    require(first_parent_contains(repo, authorization_commit, head)
            and first_parent_contains(repo, marker_commit, head),
            "checkout is not on exact authorized sandbox first-parent lineage")
    return {**trial, "status": "sandbox_research_invocation_ready",
            "sandbox_semantics_authorized": True,
            "feasibility_authorization_commit": authorization_commit,
            "remote_head": remote, "canonical_acceptance": False,
            "assembly_authorized": False, "production_authorized": False,
            "quality_AB_C_completed": False}


def authorized_item(repo, *, marker_commit, buffer_path,
                    authorization_commit, ordinal):
    """Only one of original exact 18 items; never caller-selected bindings."""
    trial = authorized_trial(repo, marker_commit=marker_commit,
                             buffer_path=buffer_path,
                             authorization_commit=authorization_commit)
    require(type(ordinal) is int and 0 <= ordinal < 18,
            "item must be exact original frozen ordinal 0..17")
    return trial, trial["items"][ordinal]


def validate_authorized_candidate(repo, *, marker_commit, buffer_path,
                                  authorization_commit, ordinal, package):
    """Only an authorized original immutable assignment may be validated."""
    trial, item = authorized_item(
        repo, marker_commit=marker_commit, buffer_path=buffer_path,
        authorization_commit=authorization_commit, ordinal=ordinal)
    return validate_candidate(item, package, marker_commit=trial["marker_commit"],
                              nonce=trial["nonce"])


def inspect_authorized_transport(repo, *, marker_commit, buffer_path,
                                 authorization_commit, ordinal, result_commit,
                                 expected_raw=None):
    """Actual first-parent create-only original item provenance; no acceptance."""
    trial, item = authorized_item(
        repo, marker_commit=marker_commit, buffer_path=buffer_path,
        authorization_commit=authorization_commit, ordinal=ordinal)
    return inspect_transport(repo, trial=trial, item=item,
                             result_commit=result_commit, expected_raw=expected_raw)


def assert_authorizing_dispatch(expected, marker_commit, confirmation, env):
    require(bool(SHA40.fullmatch(str(expected)))
            and bool(SHA40.fullmatch(str(marker_commit))),
            "40-hex main + original marker commits mandatory")
    require(confirmation == CONFIRMATION, "explicit once-only approval missing")
    require(env.get("GITHUB_ACTIONS") == "true"
            and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
            and env.get("GITHUB_REPOSITORY") == REPOSITORY
            and env.get("GITHUB_REF") == "refs/heads/main"
            and env.get("GITHUB_WORKFLOW_REF")
                == REPOSITORY + "/" + WORKFLOW + "@refs/heads/main"
            and env.get("GITHUB_SHA") == expected
            and env.get("GITHUB_RUN_ATTEMPT") == "1",
            "only a first-attempt manual main GitHub workflow can authorize")


def publish_authorization(repo, *, expected_main, marker_commit):
    """One GH-owned dispatch, create-only descendant push with exact remote lease."""
    assert_canonical_remote(repo)
    require(run(repo, "symbolic-ref", "--short", "HEAD") == "main"
            and run(repo, "rev-parse", "HEAD") == expected_main
            and remote_sha(repo, "refs/heads/main") == expected_main,
            "main checkout/remote SHA drifted")
    assert_clean(repo)
    ref = "refs/heads/" + BRANCH
    require(remote_sha(repo, ref) == marker_commit,
            "original live sandbox branch must be exact marker HEAD; no replay")
    run(repo, "fetch", "--no-tags", "origin", ref)
    require(run(repo, "rev-parse", "FETCH_HEAD") == marker_commit,
            "cannot fetch genuine marker from the exact sandbox ref")
    trial = original_blocked_trial(repo, marker_commit, BUFFER)
    # All new predeclared bytes must come from the original marker parent,
    # and must not have changed on main between independent dispatches.
    for path in (FEASIBILITY_CONTRACT, FEASIBILITY_PROMPT, FEASIBILITY_VERIFIER):
        require(blob(repo, trial["marker_parent"], path)
                == blob(repo, expected_main, path),
                "predeclared feasibility authority changed after original freeze: " + path)
    run(repo, "checkout", "--detach", marker_commit)
    assert_clean(repo)
    raw = (json.dumps(expected_authorization(repo, trial),
                      sort_keys=True, separators=(",", ":"), ensure_ascii=False)
           + "\n").encode("utf-8")
    auth_commit = commit_new(repo, AUTH_PATH, raw,
                             "Authorize original 18-game sandbox Research feasibility only")
    assert_one_new_path(repo, marker_commit, auth_commit, AUTH_PATH)
    verify_authorization_commit(repo, marker_commit=marker_commit,
                                buffer_path=BUFFER, authorization_commit=auth_commit)
    require(remote_sha(repo, ref) == marker_commit
            and remote_sha(repo, "refs/heads/main") == expected_main,
            "remote sandbox or main drifted before authorization push")
    # Fast-forward-only + exact old ref lease, never reconstruct a failed freeze.
    run(repo, "push", "--porcelain", "--force-with-lease=" + ref + ":" + marker_commit,
        "origin", "HEAD:" + ref)
    require(remote_sha(repo, ref) == auth_commit,
            "durable GitHub authorization not at remote branch head")
    run(repo, "fetch", "--no-tags", "origin", ref)
    require(run(repo, "rev-parse", "FETCH_HEAD") == auth_commit,
            "published GitHub authorization cannot be fetched back")
    ready = authorized_trial(repo, marker_commit=marker_commit,
                             buffer_path=BUFFER, authorization_commit=auth_commit)
    return {k: v for k, v in ready.items() if k != "items"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--authorize", action="store_true")
    ap.add_argument("--marker-commit", required=True)
    ap.add_argument("--buffer-path", default=BUFFER)
    ap.add_argument("--authorization-commit")
    ap.add_argument("--expected-main-sha")
    ap.add_argument("--confirmation")
    a = ap.parse_args()
    repo = Path.cwd().resolve()
    if a.authorize:
        assert_authorizing_dispatch(a.expected_main_sha, a.marker_commit,
                                    a.confirmation, os.environ)
        require(a.buffer_path == BUFFER and a.authorization_commit is None,
                "publisher has no alternate buffer/authorization input")
        result = publish_authorization(repo, expected_main=a.expected_main_sha,
                                       marker_commit=a.marker_commit)
    else:
        require(a.expected_main_sha is None and a.confirmation is None,
                "read-only verifier must not be used as issuer")
        result = authorized_trial(repo, marker_commit=a.marker_commit,
                                  buffer_path=a.buffer_path,
                                  authorization_commit=a.authorization_commit)
        result = {k: v for k, v in result.items() if k != "items"}
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))
    print("sandbox_research_invocation_ready=ready")
    if a.authorize and os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### Sandbox Research FEASIBILITY ONLY; A/B/C quality NOT approved\n\n")
            for key in ("marker_commit", "feasibility_authorization_commit",
                        "marker_parent", "buffer_blob_sha", "status", "remote_head"):
                f.write("- " + key + ": `" + str(result[key]) + "`\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fail-closed, sandbox-only source preflight for one owner-approved Lean writer recovery.

This module must be executed from reviewed main source. Merely reading a ready
sandbox is never a new semantic grant, canonical acceptance or permission to
retry an attempted writer. Runtime activation stays separate.
"""
import json
import os
import re
import subprocess
from pathlib import Path

import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_generic_replay as generic
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import git, json_at
from dossier_notes_v2_per_item_receipts import (
    _github_get, require_batch_terminal_receipts,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/dossier_lean_writer_auto_ready_v1.json"
SHA = re.compile(r"[0-9a-f]{40}\Z")
SIGNAL_WORKFLOW = ".github/workflows/dossier-lean-writer-ready-signal.yml"
AUTO_WORKFLOW = ".github/workflows/dossier-lean-writer-auto-ready.yml"
CLAIM_PREFIX = "refs/heads/dossier-lean-auto-attempts/"


def require(value, message):
    if not value:
        raise ValueError("LEAN_AUTO_READY_BLOCKED: " + message)


def policy():
    contract = json.loads(POLICY.read_text(encoding="utf-8"))
    recovery = contract.get("recovery", {})
    from dossier_lean_canonical_dual import SANDBOX_GRANT, _policy
    original = json.loads(SANDBOX_GRANT.read_text(encoding="utf-8"))
    require(contract.get("schema") ==
            "DOSSIER-LEAN-WRITER-AUTO-READY-AUTHORIZATION-V1"
            and contract.get("schema_version") == 1
            and contract.get("repository") == batch.REPOSITORY
            and contract.get("owner") == "github_control_plane"
            and contract.get("source_merge_is_not_activation") is True
            and contract.get("requires_independent_L3_final_head_review") is True
            and contract.get("requires_separate_owner_approved_activation") is True
            and contract.get("automatic_retry_after_failure") is False
            and contract.get("per_trial_at_most_one_attempt") is True
            and contract.get("shared_writer_concurrency_group") ==
                "taste-steam-review-dossier-canonical-writer"
            and contract.get("no_automatic_semantic_research_assembly_or_deep") is True
            and contract.get("canonical_main_acceptance") is False
            and type(contract.get("activation_enabled")) is bool,
            "unrecognized source approval/activation contract")
    require(recovery.get("trial_id") == original["trial_id"]
            and recovery.get("marker_commit") == original["marker_commit"]
            and recovery.get("original_frozen_sandbox_head") ==
                original["frozen_sandbox_head"]
            and recovery.get("failed_manual_workflow_run_id") == 45540222575
            and recovery.get("failed_manual_run_attempt") == 1
            and recovery.get("failed_manual_workflow") == batch.WRITER_WORKFLOW
            and recovery.get("failed_manual_head_sha") ==
                "147be762d217dc1e7dc53a6fbd896f323f6af08c"
            and str(recovery.get("original_owner_source_run_id")) ==
                original["owner_source_actions_run_id"]
            and recovery.get("original_request_commit") ==
                original["original_request_commit"]
            and recovery.get("new_one_use_recovery_permission") ==
                "explicit_user_approved_2026-11-25_this_conversation"
            and recovery.get("permission_bound_to_exact_previous_failed_run") is True
            and recovery.get("owner_one_use_scope_is_only_one_new_automatic_attempt") is True
            and recovery.get("legacy_manual_first_attempt_must_not_be_reused") is True
            and recovery.get("accepted_or_failed_new_attempt_ends_authority") is True,
            "new recovery grant or failed first run not uniquely bound")
    replay = json.loads((ROOT / "config/dossier_notes_v2_generic_replay_policy.json").read_text())
    require(replay.get("allow_automatic_writer") is False
            and replay.get("allow_automatic_semantic_retry") is False
            and replay.get("automatic_launch_on_source_merge") is False
            and replay.get("production_enabled") is False
            and replay.get("canonical_ingest") is False
            and all(_policy().get("lean_" + key + "_enabled") is False
                    for key in ("writer", "reader", "deep")),
            "generic/Lean production flags must remain off")
    return contract


def exact_pairs():
    from dossier_lean_canonical_dual import SANDBOX_GRANT
    original = json.loads(SANDBOX_GRANT.read_text(encoding="utf-8"))
    items = original["items"]
    require(len(items) == 6 and len({r["appid"] for r in items}) == 6,
            "exact six-item original grant required")
    return {row["appid"]: {"research_commit": row["research_commit"],
                            "assembly_commit": row["assembly_commit"]}
            for row in items}


def authentic_old_failure(token):
    """The failure was real and consumed the first manual writer attempt."""
    require(bool(token), "GitHub Actions credential missing")
    from dossier_lean_canonical_dual import SANDBOX_GRANT
    cfg = json.loads(SANDBOX_GRANT.read_text(encoding="utf-8"))
    c = policy()["recovery"]
    run = _github_get(batch.REPOSITORY,
                      "actions/runs/" + str(c["failed_manual_workflow_run_id"]), token)
    require(run.get("id") == c["failed_manual_workflow_run_id"]
            and run.get("event") == "workflow_dispatch"
            and run.get("path") == batch.WRITER_WORKFLOW
            and run.get("run_attempt") == 1
            and run.get("status") == "completed"
            and run.get("conclusion") == "failure"
            and run.get("head_sha") == c["failed_manual_head_sha"]
            and run.get("head_branch") == "main"
            and run.get("actor", {}).get("id") == int(batch.OWNER_ID)
            and run.get("actor", {}).get("login") == batch.OWNER_LOGIN
            and run.get("triggering_actor", {}).get("id") == int(batch.OWNER_ID)
            and run.get("triggering_actor", {}).get("login") == batch.OWNER_LOGIN
            and cfg["frozen_sandbox_head"] ==
                c["original_frozen_sandbox_head"],
            "real previous failed manual first attempt not authenticated")
    return True


def verify_source_signal(event, env):
    """Read a GitHub-authenticated event, not free-form dispatch inputs."""
    contract = policy()
    require(contract["activation_enabled"] is True,
            "activation pending separate owner review")
    require(env.get("GITHUB_ACTIONS") == "true"
            and env.get("GITHUB_REPOSITORY") == batch.REPOSITORY
            and env.get("GITHUB_REPOSITORY_OWNER_ID") == batch.OWNER_ID
            and env.get("GITHUB_REF") == "refs/heads/main"
            and env.get("GITHUB_WORKFLOW_REF") ==
                batch.REPOSITORY + "/" + AUTO_WORKFLOW + "@refs/heads/main"
            and env.get("GITHUB_RUN_ATTEMPT") == "1"
            and str(env.get("GITHUB_RUN_ID", "")).isdigit()
            and int(env["GITHUB_RUN_ID"]) > 0,
            "not a trusted main-workflow first attempt")
    from dossier_lean_canonical_dual import SANDBOX_GRANT
    original = json.loads(SANDBOX_GRANT.read_text(encoding="utf-8"))
    expected = original["trial_id"]
    if env.get("GITHUB_EVENT_NAME") == "workflow_run":
        prior = event.get("workflow_run", {})
        repository = prior.get("head_repository") or {}
        require(prior.get("event") == "push"
                and prior.get("status") == "completed"
                and prior.get("conclusion") == "success"
                and prior.get("run_attempt") == 1
                and prior.get("path") == SIGNAL_WORKFLOW
                and prior.get("head_branch") == "sandbox/" + expected
                and prior.get("head_sha") == original["frozen_sandbox_head"]
                and repository.get("full_name") == batch.REPOSITORY
                and prior.get("id") and type(prior["id"]) is int,
                "wrong ready-signal source run, repo, branch or HEAD")
        return {"trial_id": expected,
                "source_signal_run_id": prior["id"],
                "source_signal_sha": prior["head_sha"],
                "event_kind": "terminal_receipt_push"}
    if env.get("GITHUB_EVENT_NAME") == "push":
        require(event.get("ref") == "refs/heads/main"
                and event.get("created") is False
                and event.get("deleted") is False
                and event.get("forced") is False
                and event.get("after") == env.get("GITHUB_SHA")
                and event.get("repository", {}).get("full_name") == batch.REPOSITORY
                and event.get("sender", {}).get("id") == int(batch.OWNER_ID)
                and env.get("GITHUB_ACTOR_ID") == batch.OWNER_ID
                and env.get("GITHUB_TRIGGERING_ACTOR") == batch.OWNER_LOGIN,
                "catch-up requires genuine approved main owner activation push")
        changed = event.get("head_commit", {}).get("modified", [])
        added = event.get("head_commit", {}).get("added", [])
        require("config/dossier_lean_writer_auto_ready_v1.json" in changed
                and not added,
                "catch-up only on a genuine separate activation contract change")
        return {"trial_id": expected,
                "source_signal_run_id": None,
                "source_signal_sha": original["frozen_sandbox_head"],
                "event_kind": "owner_activation_catchup"}
    raise ValueError("LEAN_AUTO_READY_BLOCKED: unrecognized automatic event")


def validate_ready(repo, *, token):
    """Verify existing immutable six all the way through Lean final without writes."""
    repo = Path(repo).resolve()
    cfg = policy()
    require(cfg["activation_enabled"] is True,
            "no auto-run before separate owner activation")
    original = json.loads((ROOT / "config/dossier_notes_v2_isolated_lean_acceptance.json").read_text())
    trial = original["trial_id"]
    require(git(repo, "symbolic-ref", "--short", "HEAD").stdout.decode().strip() ==
            "sandbox/" + trial, "not the original sandbox")
    require(git(repo, "rev-parse", "HEAD").stdout.decode().strip() ==
            original["frozen_sandbox_head"], "frozen sandbox HEAD changed")
    marker = original["marker_commit"]
    path = batch.paths(trial)
    authorizers = git(repo, "log", "--first-parent", "--format=%H",
                      "HEAD", "--", path["authorization"]).stdout.decode().splitlines()
    require(authorizers == [original["authorization_commit"]],
            "original owner authorization altered")
    issuer = batch.issuer_structure(repo, trial_id=trial,
                                    marker_commit=marker,
                                    authorization_commit=authorizers[0])
    require(issuer.get("authority_origin") == "generic_owner_request"
            and issuer.get("semantic_execution_authorized") is True,
            "no authenticated original issuer")
    generic.policy(repo)
    batch.authenticated_owner_run(issuer, token, batch.REPOSITORY)
    authentic_old_failure(token)
    from dossier_lean_canonical_dual import (
        require_isolated_sandbox_writer, validate_writer_lean,
    )
    pairs = exact_pairs()
    frozen = require_isolated_sandbox_writer(
        repo, trial_id=trial, marker_commit=marker,
        item_commits=pairs, issuer=issuer)
    projection = v2.individual_final_readiness(
        repo, trial_id=trial, marker_commit=marker, item_commits=pairs)
    status = {r["appid"]: r["status"] for r in projection["items"]}
    if set(status) != set(pairs) or any(s != "ready" for s in status.values()):
        return {"status": "not_ready", "ready": False,
                "trial_id": trial, "statuses": status}
    for appid, row in frozen.items():
        pair = pairs[appid]
        require_batch_terminal_receipts(
            repo, marker_commit=marker, trial_id=trial, appid=appid,
            authorization_commit=authorizers[0],
            research_commit=pair["research_commit"],
            assembly_commit=pair["assembly_commit"])
        result = v2.inspect_assembly(
            repo, marker_commit=marker, trial_id=trial,
            appid=appid, research_commit=pair["research_commit"],
            result_commit=pair["assembly_commit"])
        require(result.get("status") ==
                "strict_item_valid_pending_existing_atomic_group_ingest",
                "immutable Assembly or typed receipt not terminal-ready")
        work = v2.assembly_work(
            repo, marker_commit=marker, trial_id=trial,
            appid=appid, research_commit=pair["research_commit"])
        original_doc = json_at(repo, pair["assembly_commit"], work["output_path"])
        require(work.get("status") == "ready_for_autonomous_assembly"
                and original_doc.get("outcome") == "assembled_candidate_ready"
                and original_doc.get("assignment") == work["assignment"]
                and original_doc.get("research_transport") == work["research_transport"]
                and work["assignment"]["appid"] == appid
                and work["assignment"]["title"] == row["title"]
                and work["assignment"]["assignment_id"] == row["assignment_id"]
                and work["assignment"]["group_sequence"] == row["group_sequence"],
                "original source/work/edition/title/assignment inconsistent")
        doc = original_doc["final_dossier"]
        validate_writer_lean(doc, appid=appid, title=row["title"],
                             expected_ttl_days=14)
        require(doc["game_identity"]["release_year"] == row["original_release_year"],
                "original work release year not equal to frozen independent grant")
    return {"status": "ready_exact_six_read_only", "ready": True,
            "trial_id": trial, "marker_commit": marker,
            "sandbox_head": original["frozen_sandbox_head"],
            "pairs": pairs, "canonical_acceptance": False,
            "deep_ready": False}


def check_claim_ref(repo, trial_id):
    require(generic.is_generic(trial_id), "invalid trial claim identity")
    sha = subprocess.run(
        ["git", "-C", str(repo), "ls-remote", "origin",
         CLAIM_PREFIX + trial_id.removeprefix(generic.PREFIX)],
        capture_output=True, text=True, check=True).stdout.strip()
    if not sha:
        return None
    require(len(sha.split()) == 2 and SHA.fullmatch(sha.split()[0]),
            "unrecognized prior attempt record")
    return sha.split()[0]


if __name__ == "__main__":
    # No executing entrypoint: the offline source cannot dispatch, claim or run
    # a writer. A separately reviewed runtime workflow is mandatory.
    print(json.dumps({"status": "source_preflight_only_inactive",
                      "activation_enabled": policy()["activation_enabled"]}))

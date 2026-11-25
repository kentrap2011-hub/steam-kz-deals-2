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
    # Owner may waive only the independent L3 process for this reviewed
    # isolated activation. This never weakens real GitHub actor/event,
    # immutable grant, one-use claim, TTL, or postpush readback checks.
    expected_waiver = {
        "explicit": True,
        "approved_on": "2026-11-25",
        "authorization": "user_direct_instruction_activate_without_independent_review",
        "scope": "isolated_sandbox_auto_writer_activation_only",
        "does_not_waive_runtime_gates": True,
    }
    independent_review = contract.get("requires_independent_L3_final_head_review")
    review_gate = (
        (independent_review is True and contract.get("owner_L3_waiver") is None)
        or (independent_review is False
            and contract.get("owner_L3_waiver") == expected_waiver
            and contract.get("activation_enabled") is True)
    )
    require(review_gate, "independent L3 or exact scoped owner waiver required")
    require(contract.get("schema") ==
            "DOSSIER-LEAN-WRITER-AUTO-READY-AUTHORIZATION-V1"
            and contract.get("schema_version") == 1
            and contract.get("repository") == batch.REPOSITORY
            and contract.get("owner") == "github_control_plane"
            and contract.get("source_merge_is_not_activation") is True
            and contract.get("requires_separate_owner_approved_activation") is True
            and contract.get("automatic_retry_after_failure") is True
            and contract.get("per_trial_at_most_one_attempt") is False
            and contract.get("shared_writer_concurrency_group") ==
                "taste-steam-review-dossier-canonical-writer"
            and contract.get("no_automatic_semantic_research_assembly_or_deep") is True
            and contract.get("canonical_main_acceptance") is False
            and type(contract.get("activation_enabled")) is bool,
            "unrecognized source approval/activation contract")
    lifecycle = contract.get("retry_lifecycle", {})
    require(lifecycle.get("schema") == "DOSSIER-LEAN-WRITER-RESUMABLE-V1"
            and lifecycle.get("enabled_for_new_scoped_grants") is True
            and lifecycle.get("max_total_attempts") == 3
            and lifecycle.get("exclusive_lease_minutes") == 30
            and lifecycle.get("minimum_retry_minutes") == 2
            and lifecycle.get("historical_spent_claim_sha") ==
                "6df354d024b0e3104ee408e815a1e5d141fb8e84"
            and lifecycle.get("historical_failed_auto_run_id") == 45628656098
            and type(lifecycle.get("historical_live_retry_authorized")) is bool,
            "lifecycle source proposal must not silently restore a spent historic grant")
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
        branch = prior.get("head_branch")
        trial_id = branch[len("sandbox/"):] if isinstance(branch, str) and branch.startswith("sandbox/") else None
        require(generic.is_generic(trial_id)
                and prior.get("event") == "push"
                and prior.get("status") == "completed"
                and prior.get("conclusion") == "success"
                and prior.get("run_attempt") == 1
                and prior.get("path") == SIGNAL_WORKFLOW
                and isinstance(prior.get("head_sha"), str)
                and SHA.fullmatch(prior["head_sha"])
                and (trial_id != expected or
                     prior["head_sha"] == original["frozen_sandbox_head"])
                and repository.get("full_name") == batch.REPOSITORY
                and type(prior.get("id")) is int
                and prior["id"] > 0,
                "wrong ready-signal source run, repo, trial, workflow or HEAD")
        return {"trial_id": trial_id,
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
        # GitHub Actions push payloads omit head_commit.modified/added.
        # The exact activation path is proven against real Git objects after
        # trusted main checkout, rather than trusting absent event fields.
        return {"trial_id": expected,
                "source_signal_run_id": None,
                "source_signal_sha": original["frozen_sandbox_head"],
                "event_kind": "owner_activation_catchup"}
    raise ValueError("LEAN_AUTO_READY_BLOCKED: unrecognized automatic event")


def require_activation_git_change(source_repo, event, env):
    """Fail closed unless the owner push really changed the existing contract.

    The workflow paths filter is useful but can be bypassed by GitHub's
    documented large-push/diff-timeout behavior. The Git tree pair is the
    source of truth, not missing head_commit.modified/added event fields.
    """
    require(env.get("GITHUB_EVENT_NAME") == "push",
            "activation diff requires an owner main push")
    before = event.get("before")
    after = event.get("after")
    require(isinstance(before, str) and SHA.fullmatch(before)
            and before != "0" * 40 and after == env.get("GITHUB_SHA"),
            "activation push lacks a real Git before/after range")
    ancestry = command(source_repo, "merge-base", "--is-ancestor",
                       before, after, check=False)
    require(ancestry.returncode == 0,
            "activation push before commit is not an ancestor of after")
    # An owner-reviewed source fix is itself a bounded recovery wakeup;
    # GitHub's paths trigger is only a hint and NEVER an authorization proof.
    allowed = (
        "config/dossier_lean_writer_auto_ready_v1.json",
        "scripts/dossier_lean_writer_auto_ready.py",
        "scripts/dossier_lean_writer_retry_state.py",
        ".github/workflows/dossier-lean-writer-auto-ready.yml",
    )
    verified_delta = False
    for path in allowed:
        previous = command(source_repo, "rev-parse", "--verify",
                           before + ":" + path, check=False)
        current = command(source_repo, "rev-parse", "--verify",
                          after + ":" + path, check=False)
        old_blob = previous.stdout.strip()
        new_blob = current.stdout.strip()
        # Both sides must exist. New source files are allowed only if at
        # least one preexisting owner-controlled policy/source file changed.
        if (previous.returncode == 0 and current.returncode == 0
                and SHA.fullmatch(old_blob) and SHA.fullmatch(new_blob)
                and old_blob != new_blob):
            verified_delta = True
    require(verified_delta,
            "owner main push did not change reviewed existing Lean writer source")


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
            "pairs": pairs, "issuer": issuer, "canonical_acceptance": False,
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



def future_plan(repo, *, trial_id, token):
    """Verify one opt-in owner-issued immutable Lean batch; never choose scope.

    Exact immutable typed Assembly receipts supply Git commit pairs. Missing
    receipts are NOT READY, never a request to issue new semantic work.
    """
    from dossier_two_stage_staging import parent, file_at
    from dossier_lean_canonical_dual import validate_writer_lean
    repo = Path(repo).resolve()
    require(generic.is_generic(trial_id), "not a generic scoped trial")
    grant_policy = policy()
    require(grant_policy["activation_enabled"] is True,
            "future auto writer cannot be activated by an issuer alone")
    path = batch.paths(trial_id)
    require(git(repo, "symbolic-ref", "--short", "HEAD").stdout.decode().strip()
            == path["branch"], "future ready state not its exact sandbox")
    auths = git(repo, "log", "--first-parent", "--format=%H", "HEAD", "--",
                path["authorization"]).stdout.decode().splitlines()
    require(len(auths) == 1 and SHA.fullmatch(auths[0]),
            "future owner authorization not unique")
    marker = parent(repo, auths[0])
    anchor = batch.issuer_structure(
        repo, trial_id=trial_id, marker_commit=marker,
        authorization_commit=auths[0])
    if anchor.get("sandbox_lean_auto_writer_authorized") is not True:
        return {"status": "suppressed_no_individual_owner_auto_grant",
                "ready": False, "trial_id": trial_id}
    batch.authenticated_owner_run(anchor, token, batch.REPOSITORY)
    _, rows = generic.frozen_plan(repo, trial_id, marker)
    require(1 <= len(rows) <= 24 and len({r["appid"] for r in rows}) == len(rows),
            "future auto scope malformed")
    source_pins = anchor.get("source_pins", {})
    require(source_pins.get("lean_auto_writer") is True,
            "signed source does not opt in to Lean automatic writer")
    source_by_appid = {r["appid"]: r for r in source_pins["source_research"]}
    item_pairs = {}
    for row in rows:
        a = row["appid"]
        baseline_sha = row.get("baseline_blob_sha")
        year = row.get("original_release_year")
        require(type(year) is int and 1970 <= year <= 2100
                and isinstance(baseline_sha, str) and SHA.fullmatch(baseline_sha)
                and source_by_appid[a].get("baseline_blob_sha") == baseline_sha
                and source_by_appid[a].get("original_release_year") == year,
                "future owner-issued baseline/year evidence mismatch")
        strict_original = json.loads(
            git(repo, "cat-file", "blob", baseline_sha).stdout.decode("utf-8"))
        require(strict_original.get("schema") == "TASTE-STEAM-REVIEW-DOSSIER-V2"
                and strict_original.get("appid") == a
                and strict_original.get("title") == row["title"]
                and strict_original.get("game_identity", {}).get("release_year") == year,
                "future pinned old strict game edition/year blob invalid")
        receipt_path = (
            "data/control/dossier_notes_v2/receipts/" + trial_id
            + "/g" + str(row["group_sequence"]).zfill(6)
            + "/" + a + "--" + row["assignment_id"] + "--assembly.json"
        )
        found = git(repo, "cat-file", "-e", "HEAD:" + receipt_path,
                    required=False)
        if found.returncode != 0:
            return {"status": "not_ready_missing_assembly_receipt",
                    "ready": False, "trial_id": trial_id, "missing_appid": a}
        typed = json_at(repo, "HEAD", receipt_path)
        source = typed.get("source", {})
        pair = {key: source.get(key) for key in ("research_commit", "assembly_commit")}
        require(typed.get("schema") == "DOSSIER-NOTES-V2-ITEM-RECEIPT"
                and typed.get("phase") == "assembly"
                and typed.get("trial_id") == trial_id
                and typed.get("appid") == a
                and typed.get("disposition") ==
                    "strict_item_valid_pending_existing_atomic_group_ingest"
                and typed.get("assignment", {}).get("assignment_id") ==
                    row["assignment_id"]
                and typed.get("assignment", {}).get("title") == row["title"]
                and all(isinstance(val, str) and SHA.fullmatch(val)
                        for val in pair.values()),
                "future terminal receipt malformed or not ready")
        item_pairs[a] = pair
    projection = v2.individual_final_readiness(
        repo, marker_commit=marker, trial_id=trial_id, item_commits=item_pairs)
    require(len(projection["items"]) == len(rows)
            and all(i["status"] == "ready" for i in projection["items"]),
            "future terminal receipts do not all pass strict Git lineage")
    for row in rows:
        a = row["appid"]
        pair = item_pairs[a]
        require_batch_terminal_receipts(
            repo, marker_commit=marker, trial_id=trial_id, appid=a,
            authorization_commit=auths[0],
            research_commit=pair["research_commit"],
            assembly_commit=pair["assembly_commit"])
        checked = v2.inspect_assembly(
            repo, marker_commit=marker, trial_id=trial_id, appid=a,
            research_commit=pair["research_commit"],
            result_commit=pair["assembly_commit"])
        require(checked.get("status") ==
                "strict_item_valid_pending_existing_atomic_group_ingest",
                "original Assembly final Git lineage changed")
        work = v2.assembly_work(
            repo, marker_commit=marker, trial_id=trial_id,
            appid=a, research_commit=pair["research_commit"])
        original = json_at(repo, pair["assembly_commit"], work["output_path"])
        require(work.get("status") == "ready_for_autonomous_assembly"
                and original.get("outcome") == "assembled_candidate_ready"
                and original.get("assignment") == work["assignment"]
                and original.get("research_transport") == work["research_transport"]
                and work["assignment"]["appid"] == a
                and work["assignment"]["title"] == row["title"]
                and work["assignment"]["assignment_id"] == row["assignment_id"]
                and work["assignment"]["group_sequence"] == row["group_sequence"],
                "future frozen work/edition/assignment mismatch")
        doc = original["final_dossier"]
        validate_writer_lean(doc, appid=a, title=row["title"],
                             expected_ttl_days=14)
        require(doc["game_identity"]["release_year"] == row["original_release_year"],
                "future Lean work year differs from original strict pinned baseline")
        store = repo / path["store"] / ("App_" + a + ".json")
        accepted = repo / path["accepted"] / trial_id / (
            "g" + str(row["group_sequence"]).zfill(6)) / (
                a + "--" + row["assignment_id"] + ".json")
        require(not store.exists() and not accepted.exists(),
                "future writer collision or prior acceptance")
    return {
        "status": "ready_future_exact_owner_grant", "ready": True,
        "trial_id": trial_id, "marker_commit": marker,
        "sandbox_head": git(repo, "rev-parse", "HEAD").stdout.decode().strip(),
        "rows": rows, "pairs": item_pairs, "issuer": anchor,
        "canonical_acceptance": False, "deep_ready": False,
    }


def exact_generic_transaction(repo, *, plan, mode):
    """Same byte/atomic/readback standard for immutable owner-opted-in future trial."""
    import hashlib
    from dossier_lean_canonical_dual import LEAN_SCHEMA, quality_binding, validate_writer_lean
    from taste_steam_review_dossier import canonical_sha256
    require(mode in ("staged", "committed"), "invalid future readback mode")
    repo = Path(repo).resolve()
    trial = plan["trial_id"]
    marker = plan["marker_commit"]
    expected = set()
    for row in plan["rows"]:
        appid = row["appid"]
        store = ("data/control/dossier_notes_v2/batch_pilot_store/" + trial
                 + "/App_" + appid + ".json")
        receipt = ("data/control/dossier_notes_v2/batch_pilot_accepted/" + trial
                   + "/g" + str(row["group_sequence"]).zfill(6)
                   + "/" + appid + "--" + row["assignment_id"] + ".json")
        for path in (store, receipt):
            dest = repo / path
            require(not dest.is_symlink() and dest.is_file()
                    and dest.resolve().is_relative_to(repo),
                    "missing or unsafe isolated future accepted record")
            stored = subprocess.run(
                ["git", "-C", str(repo), "show",
                 (":" if mode == "staged" else "HEAD:") + path],
                capture_output=True, check=True).stdout
            require(stored == dest.read_bytes(),
                    "Git stage/committed accepted record differs from actual raw bytes")
            expected.add(path)
        raw = (repo / store).read_bytes()
        doc = json.loads(raw.decode("utf-8"))
        record = json.loads((repo / receipt).read_text(encoding="utf-8"))
        pair = plan["pairs"][appid]
        assignment = v2.frozen_assignment(
            repo, marker_commit=marker, trial_id=trial, appid=appid)
        require(doc.get("schema") == LEAN_SCHEMA
                and doc.get("appid") == appid
                and doc.get("title") == row["title"]
                and doc.get("game_identity", {}).get("release_year") ==
                    row["original_release_year"]
                and record.get("schema") ==
                    "DOSSIER-NOTES-V2-ISOLATED-TRIAL-RECEIPT-V1"
                and record.get("trial_id") == trial
                and record.get("marker_commit") == marker
                and record.get("assignment") == assignment
                and record.get("research_commit") == pair["research_commit"]
                and record.get("assembly_commit") == pair["assembly_commit"]
                and record.get("dossier_sha256") == canonical_sha256(doc)
                and record.get("dossier_raw_sha256") ==
                    hashlib.sha256(raw).hexdigest()
                and record.get("dossier_format") == LEAN_SCHEMA
                and record.get("quality_binding") == quality_binding()
                and record.get("original_release_year") == row["original_release_year"]
                and record.get("isolated_sandbox_acceptance") is True
                and record.get("canonical_acceptance") is False
                and record.get("deep_ready") is False,
                "future Lean accepted object, edition, digests or receipt mismatch")
        validate_writer_lean(doc, appid=appid, title=row["title"],
                             expected_ttl_days=14)
        work = v2.assembly_work(
            repo, marker_commit=marker, trial_id=trial, appid=appid,
            research_commit=pair["research_commit"])
        original = json_at(repo, pair["assembly_commit"], work["output_path"])
        require(original.get("outcome") == "assembled_candidate_ready"
                and original.get("final_dossier") == doc,
                "future accepted data differs from original immutable Assembly")
    changed = (output(repo, "diff", "--cached", "--name-only")
               if mode == "staged" else output(
                   repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"))
    changed_paths = changed.splitlines()
    require(set(changed_paths) == expected
            and len(changed_paths) == len(expected) == 2 * len(plan["rows"]),
            "future isolated transaction must be exactly N docs + N receipts")
    return {"schema": "DOSSIER-LEAN-AUTO-FUTURE-SANDBOX-READBACK-V1",
            "trial_id": trial, "verified_items": len(plan["rows"]),
            "mode": mode, "canonical_acceptance": False, "deep_ready": False}


def command(repo, *args, check=True):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=check)


def output(repo, *args):
    return command(repo, *args).stdout.strip()


def verify_main_checkout(repo, env):
    require(output(repo, "rev-parse", "HEAD") == env.get("GITHUB_SHA"),
            "reviewed main checkout does not match GitHub event SHA")
    require(output(repo, "symbolic-ref", "--short", "HEAD") == "main",
            "runtime must execute trusted main source only")
    require(output(repo, "ls-remote", "origin", "refs/heads/main").split()[0] ==
            env["GITHUB_SHA"], "trusted main moved before automation")
    require(not output(repo, "status", "--porcelain", "--untracked-files=all"),
            "source checkout dirty")
    remote = output(repo, "remote", "get-url", "origin")
    require(remote in (
        "https://github.com/" + batch.REPOSITORY,
        "https://github.com/" + batch.REPOSITORY + ".git",
        "git@github.com:" + batch.REPOSITORY,
        "git@github.com:" + batch.REPOSITORY + ".git",
    ), "unrecognized writer source remote")


def exact_pairs_digest(pairs):
    import hashlib
    return hashlib.sha256(json.dumps(
        pairs, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()


def claim_record(signal, env, readiness):
    trial = signal["trial_id"]
    historical = trial == policy()["recovery"]["trial_id"]
    return {
        "schema": "DOSSIER-LEAN-AUTO-WRITER-ATTEMPT-V1",
        "trial_id": trial,
        "original_frozen_sandbox_head": readiness["sandbox_head"],
        "marker_commit": readiness["marker_commit"],
        "item_commits_sha256": exact_pairs_digest(readiness["pairs"]),
        "owner_source_run_id": str(
            readiness["issuer"]["github_authorization_run_id"]),
        "previous_terminal_failed_run_id": 45540222575 if historical else None,
        "automation_run_id": env["GITHUB_RUN_ID"],
        "automation_source_main_sha": env["GITHUB_SHA"],
        "source_event": signal["event_kind"],
        "source_signal_sha": signal["source_signal_sha"],
        "source_signal_run_id": signal["source_signal_run_id"],
        "attempt": 1, "no_retry": historical,
        "canonical_acceptance": False, "production": False, "deep": False,
    }


def claim_once(source_repo, signal, env, readiness):
    """Atomic create-only control ref, independent of frozen sandbox HEAD.

    A successful claim consumes the NEW recovery attempt even if the subsequent
    writer fails before writing, during commit, or on push. Never rerun this.
    """
    from tempfile import TemporaryDirectory
    trial = signal["trial_id"]
    ref = CLAIM_PREFIX + trial.removeprefix(generic.PREFIX)
    require(check_claim_ref(source_repo, trial) is None,
            "attempt already claimed: running, accepted or terminal failed")
    claim_path = "data/control/dossier_notes_v2/auto_writer_attempts/" + trial + ".json"
    record = claim_record(signal, env, readiness)
    with TemporaryDirectory(prefix="lean-auto-claim-") as tmp:
        worktree = Path(tmp) / "control"
        command(source_repo, "worktree", "add", "--detach", str(worktree),
                env["GITHUB_SHA"])
        try:
            command(worktree, "checkout", "-b",
                    "dossier-lean-auto-attempt-" + trial.removeprefix(generic.PREFIX))
            file = worktree / claim_path
            require(not file.exists(), "claim path not create-only")
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n",
                            encoding="utf-8")
            command(worktree, "add", "--", claim_path)
            require(output(worktree, "diff", "--cached", "--name-status") ==
                    "A\t" + claim_path, "only one claim file may be created")
            command(worktree, "config", "user.name", "steam-kz-bot")
            command(worktree, "config", "user.email",
                    "steam-kz-bot@users.noreply.github.com")
            command(worktree, "commit", "-m", "Claim one Lean auto writer attempt")
            target = output(worktree, "rev-parse", "HEAD")
            require(check_claim_ref(source_repo, trial) is None,
                    "claim appeared before push")
            # Exactly ONE non-force Git push. Failure/uncertainty is terminal.
            command(worktree, "push", "origin", "HEAD:" + ref)
            require(check_claim_ref(source_repo, trial) == target,
                    "claim remote readback mismatch; never retry push")
            return target
        finally:
            command(source_repo, "worktree", "remove", "--force", str(worktree),
                    check=False)


def authenticated_auto_context(repo, trial_id, marker_commit, item_commits, env=None):
    """Separate, owner-signed once-only auto permission; never relax manual path."""
    env = os.environ if env is None else env
    require(policy()["activation_enabled"] is True
            and generic.is_generic(trial_id)
            and env.get("GITHUB_TOKEN")
            and env.get("LEAN_AUTO_CLAIM_SHA")
            and isinstance(env["LEAN_AUTO_CLAIM_SHA"], str)
            and SHA.fullmatch(env["LEAN_AUTO_CLAIM_SHA"])
            and env.get("GITHUB_EVENT_PATH"),
            "missing separate authenticated GitHub-owned auto context")
    event = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    signal = verify_source_signal(event, env)
    require(signal["trial_id"] == trial_id,
            "source event not for this exact trial")
    recovery = policy()["recovery"]
    readiness = (validate_ready(repo, token=env["GITHUB_TOKEN"])
                 if trial_id == recovery["trial_id"] else
                 future_plan(repo, trial_id=trial_id, token=env["GITHUB_TOKEN"]))
    require(readiness["ready"] is True
            and readiness["marker_commit"] == marker_commit
            and readiness["pairs"] == item_commits
            and readiness["sandbox_head"] ==
                output(repo, "rev-parse", "HEAD"),
            "no exact trial, immutable SHA pairs or terminal-ready source")
    # A V2 execution lease is a separate append-only event after the
    # immutable original claim. Legacy claim alone cannot authorize a retry.
    if env.get("LEAN_AUTO_ATTEMPT_REF_SHA"):
        from dossier_lean_writer_retry_state import active_for_writer
        from dossier_lean_writer_retry_state import remote_head as retry_head
        grant_hash = exact_pairs_digest(readiness["pairs"])
        old_anchor = (policy()["retry_lifecycle"]["historical_spent_claim_sha"]
                      if trial_id == recovery["trial_id"] else None)
        active_for_writer(
            repo, {**readiness, "pairs_sha256": grant_hash}, env,
            env["LEAN_AUTO_ATTEMPT_REF_SHA"], historic_anchor=old_anchor)
        require(retry_head(repo, trial_id) == env["LEAN_AUTO_ATTEMPT_REF_SHA"],
                "active lease changed before sandbox writer")
        return True
    remote_claim = check_claim_ref(repo, trial_id)
    require(remote_claim == env["LEAN_AUTO_CLAIM_SHA"],
            "durable one-use control ref missing or modified")
    path = ("data/control/dossier_notes_v2/auto_writer_attempts/" +
            trial_id + ".json")
    from dossier_two_stage_staging import require_only_new
    require(require_only_new(repo, remote_claim, [path]) == env["GITHUB_SHA"],
            "auto control claim not one-add on this exact reviewed main source")
    claim = json.loads(output(repo, "show", remote_claim + ":" + path))
    require(claim == claim_record(signal, env, readiness),
            "claim must bind exact owner issuer, all SHA pairs and GitHub run")
    return True


def sandbox_writer_destinations(sandbox_repo, trial_id):
    """Use the existing V2 writer-owned namespaces INSIDE the sandbox worktree.

    The auto workflow runs from main, but the writer resolves destination
    paths itself; passing workflow-relative paths points outside its repo.
    """
    paths = batch.paths(trial_id)
    root = Path(sandbox_repo).resolve()
    return root / paths["store"], root / paths["accepted"]


def authentic_failed_auto_run(token, expected_id, claim):
    """Live GitHub Actions proof of the old postclaim failure, never a new grant."""
    actual = _github_get(batch.REPOSITORY, "actions/runs/" + str(expected_id), token)
    require(actual.get("id") == expected_id
            and actual.get("path") == AUTO_WORKFLOW
            and actual.get("event") == "push"
            and actual.get("run_attempt") == 1
            and actual.get("head_branch") == "main"
            and actual.get("head_sha") == claim["automation_source_main_sha"]
            and actual.get("status") == "completed"
            and actual.get("conclusion") == "failure",
            "historical postclaim Action failure not authenticated")


def run(source_repo, env):
    """Trusted existing Actions trigger; one CAS lease per exact frozen trial."""
    from tempfile import TemporaryDirectory
    import dossier_lean_writer_retry_state as retry

    source_repo = Path(source_repo).resolve()
    cfg = policy()
    if not cfg["activation_enabled"]:
        return {"status": "activation_disabled_source_only", "writer_launched": False}
    event = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    signal = verify_source_signal(event, env)
    verify_main_checkout(source_repo, env)
    if signal["event_kind"] == "owner_activation_catchup":
        require_activation_git_change(source_repo, event, env)
    trial = signal["trial_id"]
    historical = trial == cfg["recovery"]["trial_id"]
    lifecycle = cfg["retry_lifecycle"]
    # V1's consumed historical owner permission is never reinterpreted as V2.
    # Only a *separate* exact owner migration decision can flip this gate.
    if historical and not lifecycle["historical_live_retry_authorized"]:
        return {"status": "historical_spent_claim_awaits_scoped_owner_migration",
                "trial_id": trial, "writer_launched": False}

    # A receipt event is only a read-only hint; trust the completed Actions run.
    if signal["source_signal_run_id"] is not None:
        original = _github_get(
            batch.REPOSITORY, "actions/runs/" + str(signal["source_signal_run_id"]),
            env["GITHUB_TOKEN"])
        require(original.get("id") == signal["source_signal_run_id"]
                and original.get("path") == SIGNAL_WORKFLOW
                and original.get("event") == "push"
                and original.get("run_attempt") == 1
                and original.get("status") == "completed"
                and original.get("conclusion") == "success"
                and original.get("head_branch") == "sandbox/" + trial
                and original.get("head_sha") == signal["source_signal_sha"],
                "upstream ready signal not authenticated")

    sandbox_ref = "refs/heads/sandbox/" + trial
    with TemporaryDirectory(prefix="lean-auto-resumable-") as tmp:
        dest = Path(tmp) / "sandbox"
        remote_before = retry.git(
            source_repo, "ls-remote", "origin", sandbox_ref).stdout.strip().split()
        require(len(remote_before) == 2 and SHA.fullmatch(remote_before[0]),
                "sandbox branch unavailable or ambiguous")
        sandbox_head = remote_before[0]
        # An accepted sandbox is recognized only by exact immutable readback;
        # never rebuild it or overwrite a receipt.
        retry.git(source_repo, "fetch", "--no-tags", "origin", sandbox_ref)
        original_head = (cfg["recovery"]["original_frozen_sandbox_head"]
                         if historical else signal["source_signal_sha"])
        accepted_candidate = sandbox_head != original_head
        source_head = original_head if accepted_candidate else sandbox_head
        if not accepted_candidate:
            require(sandbox_head == signal["source_signal_sha"],
                    "sandbox moved before ready signal")
        else:
            require(retry.sha(source_repo, "rev-parse", sandbox_head + "^") ==
                    original_head, "sandbox has unexpected ancestry; no replay")
        retry.git(source_repo, "worktree", "add", "--detach", str(dest), source_head)
        try:
            retry.git(dest, "checkout", "-b", "sandbox/" + trial)
            readiness = (validate_ready(dest, token=env["GITHUB_TOKEN"])
                         if historical else future_plan(
                             dest, trial_id=trial, token=env["GITHUB_TOKEN"]))
            if not readiness["ready"]:
                return {"status": "not_ready_no_attempt",
                        "trial_id": trial, "writer_launched": False}
            require(readiness["sandbox_head"] == original_head,
                    "frozen ready head differs from authorization")
            grant_hash = exact_pairs_digest(readiness["pairs"])
            old_anchor = (lifecycle["historical_spent_claim_sha"]
                          if historical else None)
            state = retry.read(source_repo, trial, grant_hash,
                               historical_anchor=old_anchor)
            if historical:
                require(state is not None, "spent historical claim missing")
                authentic_failed_auto_run(
                    env["GITHUB_TOKEN"],
                    lifecycle["historical_failed_auto_run_id"], state["claim"])
            elif state is None:
                # First attempt only: old one-add anchor remains part of provenance.
                claim_once(source_repo, signal, env, readiness)
                state = retry.read(source_repo, trial, grant_hash)
            require(state is not None, "GitHub control state unavailable")
            if not historical:
                require(state["claim"].get("no_retry") is False,
                        "legacy future one-use claim cannot migrate silently")
            require(state["claim"]["original_frozen_sandbox_head"] ==
                    original_head and
                    state["claim"]["marker_commit"] == readiness["marker_commit"]
                    and state["claim"]["owner_source_run_id"] ==
                    str(readiness["issuer"]["github_authorization_run_id"]),
                    "immutable control-grant mismatch")

            def readback_remote(commit):
                # All checks run against a separately checked-out immutable
                # remote commit; no canonical/Deep promotion is involved.
                with TemporaryDirectory(prefix="lean-accepted-readback-") as extra:
                    proof = Path(extra) / "accepted"
                    retry.git(source_repo, "clone", "--quiet", "--shared",
                              "--no-checkout", str(source_repo), str(proof))
                    retry.git(proof, "checkout", "-b", "sandbox/" + trial, commit)
                    try:
                        if historical:
                            from dossier_notes_v2_isolated_lean_readback import exact_transaction
                            exact_transaction(proof, mode="committed")
                        else:
                            exact_generic_transaction(
                                proof, plan=readiness, mode="committed")
                    finally:
                        pass

            # Uncertain postwrite must be reconciled before any new attempt.
            if accepted_candidate:
                readback_remote(sandbox_head)
                last = state["last"]
                if last is not None and last["kind"] == "started":
                    previous_env = {"GITHUB_RUN_ID": last["run_id"],
                                    "GITHUB_SHA": last["main_sha"]}
                    accepted = retry.make_event(
                        state, readiness, previous_env, "accepted",
                        last["attempt"], sandbox_commit=sandbox_head)
                    retry.append(source_repo, trial, state, accepted)
                elif last is not None and last["kind"] != "accepted":
                    raise ValueError("verified accepted bytes conflict with terminal journal")
                return {"status": "verified_noop_already_accepted",
                        "trial_id": trial, "commit_sha": sandbox_head,
                        "writer_launched": False}
            last = state["last"]
            if last is not None and last["kind"] == "started":
                if retry.minutes_since(last) < lifecycle["exclusive_lease_minutes"]:
                    return {"status": "active_lease_no_second_writer",
                            "trial_id": trial, "writer_launched": False}
                # Lease expired and sandbox remains exactly frozen: prior
                # attempt had no committed acceptance. Preserve history.
                old_env = {"GITHUB_RUN_ID": last["run_id"],
                           "GITHUB_SHA": last["main_sha"]}
                failed = retry.make_event(state, readiness, old_env,
                                          "retryable_failed", last["attempt"],
                                          detail="stale_lease_frozen_sandbox_readback")
                retry.append(source_repo, trial, state, failed)
                state = retry.read(source_repo, trial, grant_hash,
                                   historical_anchor=old_anchor)
            eligible, reason = retry.eligible(
                state, source_sha=env["GITHUB_SHA"],
                max_attempts=lifecycle["max_total_attempts"],
                stale_minutes=lifecycle["exclusive_lease_minutes"],
                retry_delay_minutes=lifecycle["minimum_retry_minutes"])
            if not eligible:
                return {"status": str(reason), "trial_id": trial,
                        "writer_launched": False}
            attempt = reason
            started = retry.make_event(state, readiness, env, "started", attempt)
            head = retry.append(source_repo, trial, state, started)
            env["LEAN_AUTO_CLAIM_SHA"] = state["anchor"]
            env["LEAN_AUTO_ATTEMPT_REF_SHA"] = head
            os.environ["LEAN_AUTO_CLAIM_SHA"] = state["anchor"]
            os.environ["LEAN_AUTO_ATTEMPT_REF_SHA"] = head
            state = retry.read(source_repo, trial, grant_hash,
                               historical_anchor=old_anchor)
            from taste_steam_review_dossier_buffered import drain_buffered_groups
            try:
                store_dest, accepted_dest = sandbox_writer_destinations(dest, trial)
                result = drain_buffered_groups(notes_v2={
                    "repo": dest, "marker_commit": readiness["marker_commit"],
                    "trial_id": trial, "item_commits": readiness["pairs"],
                    "store_dir": store_dest, "accepted_dir": accepted_dest,
                    "offline_fixture": False, "trial_sandbox": True,
                })
                from dossier_notes_v2_isolated_lean_readback import exact_transaction
                verify = (lambda mode: exact_transaction(dest, mode=mode)
                          if historical else exact_generic_transaction(
                              dest, plan=readiness, mode=mode))
                paths = batch.paths(trial)
                retry.git(dest, "add", "--", paths["store"], paths["accepted"])
                retry.git(dest, "diff", "--cached", "--check")
                verify("staged")
                retry.git(dest, "config", "user.name", "steam-kz-bot")
                retry.git(dest, "config", "user.email",
                          "steam-kz-bot@users.noreply.github.com")
                retry.git(dest, "commit", "-m",
                          "Persist one owner-issued Lean isolated sandbox batch")
                verify("committed")
                require(not retry.sha(dest, "status", "--porcelain",
                                      "--untracked-files=all"),
                        "sandbox dirty after isolated transaction")
                require(retry.remote_head(source_repo, trial) == head,
                        "exclusive control lease was superseded")
                require(retry.git(source_repo, "ls-remote", "origin",
                                  sandbox_ref).stdout.split()[0] == original_head,
                        "sandbox CAS changed before publication")
                # A non-fast-forward or racing push cannot overwrite existing
                # files; uncertain network response is reconciled below.
                retry.git(dest, "push", "origin", "HEAD:" + sandbox_ref)
                final = retry.sha(dest, "rev-parse", "HEAD")
                require(retry.git(source_repo, "ls-remote", "origin",
                                  sandbox_ref).stdout.split()[0] == final,
                        "postpush sandbox hash differs")
                readback_remote(final)
            except Exception as exc:
                actual = retry.git(source_repo, "ls-remote", "origin",
                                   sandbox_ref).stdout.split()
                if len(actual) == 2 and actual[0] != original_head:
                    # Unknown remote state: prove exact acceptance or block.
                    try:
                        require(retry.sha(source_repo, "rev-parse",
                                          actual[0] + "^") == original_head,
                                "unexpected postwrite parent")
                        retry.git(source_repo, "fetch", "--no-tags", "origin",
                                  sandbox_ref)
                        readback_remote(actual[0])
                    except Exception:
                        blocked = retry.make_event(
                            state, readiness, env, "blocked_invalid_input", attempt,
                            detail="uncertain_or_conflicting_remote_write")
                        retry.append(source_repo, trial, state, blocked)
                        raise
                    final = actual[0]
                    result = {"reconciled_after_uncertain_push": True}
                elif len(actual) == 2 and actual[0] == original_head:
                    failed = retry.make_event(
                        state, readiness, env, "retryable_failed", attempt,
                        detail=type(exc).__name__ + ": no_sandbox_write;_new_source_required")
                    retry.append(source_repo, trial, state, failed)
                    raise
                else:
                    raise ValueError("remote sandbox ref unverifiable; lease held for later reconcile") from exc

            accepted = retry.make_event(
                state, readiness, env, "accepted", attempt, sandbox_commit=final)
            retry.append(source_repo, trial, state, accepted)
            return {"status": "accepted_sandbox_only_after_postpush_readback",
                    "trial_id": trial, "commit_sha": final,
                    "claim_anchor_sha": state["anchor"],
                    "attempt": attempt, "canonical_acceptance": False,
                    "deep_ready": False, "writer_result": result}
        finally:
            retry.git(source_repo, "worktree", "remove", "--force", str(dest),
                      check_result=False)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("inspect-policy", "run"), nargs="?",
                        default="inspect-policy")
    args = parser.parse_args()
    if args.mode == "inspect-policy":
        enabled = policy()["activation_enabled"]
        print(json.dumps({"status": ("versioned_activation_enabled" if enabled
                                       else "source_review_only"),
                          "activation_enabled": enabled}))
        return
    try:
        result = run(Path.cwd(), os.environ)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError,
            subprocess.CalledProcessError) as exc:
        parser.exit(2, "LEAN_AUTO_READY_TERMINAL_OR_PRECHECK_BLOCKED: " +
                    str(exc) + "\n")


if __name__ == "__main__":
    main()

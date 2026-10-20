#!/usr/bin/env python3
"""Prospective, fail-closed GitHub-only authority for the ORIGINAL shadow 18.

This program never performs semantics or Git writes. It consumes ONLY the
immutable Stage B Python inspect output and verifies distinct prospective
permission; original blocked flags remain blocked. Real run proof is the
successful, independently verified GitHub Actions workflow run AND its
uploaded receipt, not a JSON argument or public confirmation string.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from dossier_shadow_18_github_python_handoff import (
    FIXED_MARKER, FIXED_BUFFER, FIXED_RESEARCH_MARKER, FIXED_AUTH,
    FIXED_MISSING, FIXED_RESEARCH_COMMITS, require,
)
from dossier_shadow_research_trial_publish import EXPECTED_APPIDS

TRIAL = "dossier-shadow-calibration-20261011-6x3"
CONTRACT = "DOSSIER-SHADOW-18-TRIAL-WIDE-SEMANTIC-AUTHORITY-V1"
APPOINTMENTS = "DOSSIER-SHADOW-18-INDEPENDENT-REVIEWER-APPOINTMENTS-V1"
GROUPS = [3, 8, 13, 15, 18, 20]
INVALID = {"2124120", "2138710"}
HANDLE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$")
PRODUCTION_PREFIXES = ("data/production/", "data/cache/", "data/ai_inbox/",
                       "data/control/", "web/", ".github/workflows/")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_authority(contract, original, decision, pins, appointments, state,
                       *, github_context):
    """Pure exhaustive contract gate; not proof that claimed GHA context is real."""
    c, o, d, p, a, s = contract, original, decision, pins, appointments, state
    require(c.get("schema") == CONTRACT and c.get("version") == 1
            and c.get("trial_id") == TRIAL and c.get("historical_authority_preserved") is True
            and c.get("decision") == "conditional_permission_not_execution_receipt"
            and c.get("scope") == "prospective_nonproduction_manual_assembly_only"
            and c.get("original_assembly_marker") == FIXED_MARKER
            and c.get("original_assembly_buffer_commit") == FIXED_BUFFER
            and c.get("original_assembly_buffer_blob")
                == "5c7e66db7d3880098c0cd85f0690661c9655cd09"
            and c.get("research_marker") == FIXED_RESEARCH_MARKER
            and c.get("research_feasibility_commit") == FIXED_AUTH
            and c.get("original_issuer_run_id") == 39054131983,
            "not separately scoped prospective immutable trial authority")
    require(c.get("group_order") == GROUPS and len(c.get("groups", [])) == 6
            and [str(v) for group in c["groups"] for v in group] == EXPECTED_APPIDS,
            "original eighteen or six-group order mutated")
    require(c.get("handoff_branch") == "handoff/dossier-shadow-18-assembly-typed"
            and c.get("handoff_branch_initial_base") == FIXED_MARKER
            and c.get("handoff_prefix") ==
              "reviews/dossier_shadow_offline/handoff/" + TRIAL
            and c.get("manual_one_shot") is True
            and c.get("no_automatic_execution") is True
            and c.get("no_recurring_schedule") is True
            and c.get("no_retry") is True and c.get("no_new_queue") is True
            and c.get("no_batch_quota") is True
            and c.get("publish_requires_separate_human_approval_per_appid") is True
            and c.get("old_flags_are_not_approval") is True
            and c.get("old_research_auth_is_not_assembly_auth") is True
            and c.get("typed_result_exact_keys")
              == ["outcome", "payload", "supplemental_operations"]
            and c.get("typed_one_add_only_direct_parent_per_appid") is True
            and c.get("canonical_acceptance") is False
            and c.get("deep_ready") is False
            and c.get("two_stage_production_active") is False
            and c.get("one_stage_dossier_production_unchanged") is True,
            "trial boundary or production policy changed")
    require(c.get("requires", {}).get("independent_reviewer_appointments") ==
            "reviews/dossier_shadow_offline/authorizations/"
            "dossier-shadow-18-assembly-reviewer-appointments-v1.json",
            "reviewer appointment gate removed")
    require(o.get("no_assembly_activation") is True
            and o.get("standalone_sandbox_semantics_approved") is False
            and o.get("reviewer_roles_finalized") is False
            and o.get("canonical_production_authority_active") is False
            and o.get("trial_id") == TRIAL,
            "historic Research permit was relabeled as Assembly authority")
    operator = d.get("operator_authority", {})
    require(operator.get("actual_semantic_execution_permitted_now") is False
            and operator.get("source_protocol_and_independent_reviewer_roles_finalized")
            is False and d.get("two_stage_production_active") is False
            and d.get("automatic_trial_launch") is False,
            "original Director decision must remain historically blocked")
    require(p.get("assembly_marker_commit") == FIXED_MARKER
            and p.get("assembly_buffer_commit") == FIXED_BUFFER
            and p.get("research_marker_commit") == FIXED_RESEARCH_MARKER
            and p.get("research_feasibility_authorization_commit") == FIXED_AUTH
            and p.get("issuer_run_id") == 39054131983
            and p.get("original_research_introduction_commits") == FIXED_RESEARCH_COMMITS
            and set(p.get("missing_research_appids", [])) == FIXED_MISSING
            and p.get("submission_branch") == c["handoff_branch"]
            and p.get("submission_namespace") == c["handoff_prefix"]
            and p.get("canonical_acceptance") is False and p.get("deep_ready") is False
            and p.get("production_writes") == [] and p.get("retry_enabled") is False,
            "original GitHub handoff pin differs")
    require(a is not None and a.get("schema") == APPOINTMENTS
            and a.get("trial_id") == TRIAL
            and a.get("appointed_for") == "prospective_nonproduction_assembly"
            and a.get("director_approved") is True,
            "independent A/B/C reviewers not appointed by Director")
    roles = a.get("reviewer_roles", {})
    require(type(roles) is dict and set(roles) == {"A", "B", "C"}
            and all(type(v) is str and HANDLE.fullmatch(v) for v in roles.values())
            and len(set(roles.values())) == 3,
            "A/B independent and separate C distinct GitHub reviewers required")
    require(type(a.get("quality_review_completed")) is bool
            and a.get("source_privacy_rules") == "strict_original_Stage_B_source_first_privacy",
            "appointments do not mean completed quality review")
    require([r.get("appid") for r in s.get("rows", [])] == EXPECTED_APPIDS
            and len(s["rows"]) == 18 and s.get("semantic_attempts") == 0
            and s.get("canonical_acceptance") is False
            and s.get("deep_ready") is False,
            "not original GitHub Python zero-attempt inspect")
    statuses = {r["appid"]: r.get("status") for r in s["rows"]}
    require({k for k,v in statuses.items() if v == "ready"}
            == set(FIXED_RESEARCH_COMMITS) - INVALID
            and {k for k,v in statuses.items() if v == "research_transport_invalid"} == INVALID
            and {k for k,v in statuses.items() if v == "research_not_submitted"}
            == FIXED_MISSING,
            "not the original strict 12-ready/2-invalid/4-missing state")
    ctx = github_context
    require(ctx.get("event") == "workflow_dispatch"
            and ctx.get("repository") == "kentrap2011-hub/steam-kz-deals-2"
            and ctx.get("ref") == "refs/heads/main"
            and ctx.get("actor") == "kentrap2011-hub"
            and str(ctx.get("run_attempt")) == "1"
            and isinstance(ctx.get("run_id"), str)
            and ctx["run_id"].isdigit()
            and bool(re.fullmatch("[0-9a-f]{40}", str(ctx.get("sha", "")))),
            "fresh owner-dispatched main GitHub Actions authority run required")
    ready = [r["appid"] for r in s["rows"] if r["status"] == "ready"]
    return {"schema": "DOSSIER-SHADOW-18-TRIAL-WIDE-READONLY-GATE-RECEIPT-V1",
            "trial_id": TRIAL, "github_run_id": ctx["run_id"],
            "github_main_sha": ctx["sha"], "original_marker": FIXED_MARKER,
            "issuer_run_id": 39054131983, "original_order": EXPECTED_APPIDS,
            "ready_appids_in_original_order": ready,
            "invalid_appids": [i for i in EXPECTED_APPIDS if i in INVALID],
            "missing_appids": [i for i in EXPECTED_APPIDS if i in FIXED_MISSING],
            "appointees": roles, "semantics_executed": False,
            "submission_is_not_acceptance": True, "production_active": False}


def verified_handoff_progress(repo, stage, contract, inspect):
    """Verify the REMOTE single-introduction typed history; never trust chat memory.

    Branch MUST be precreated at the marker by GitHub control plane. A missing
    first-use branch is a blocking prerequisite, not a mandate to create it.
    """
    from dossier_shadow_18_github_python_handoff import remote_tip
    branch = contract["handoff_branch"]
    tip = remote_tip(repo, stage, branch)
    tracked = stage.git(repo, "rev-parse", "refs/remotes/origin/" + branch).stdout.decode().strip()
    require(tracked == tip and stage.first_parent_contains(repo, FIXED_MARKER, tip),
            "typed remote tip stale or not descended from exact original marker")
    ordered = [r["appid"] for r in inspect["rows"] if r["status"] == "ready"]
    commits = stage.git(repo, "rev-list", "--reverse", FIXED_MARKER + ".." + tip).stdout.decode().split()
    require(len(commits) <= len(ordered), "typed handoff contains extra items")
    prior = FIXED_MARKER
    for index, commit in enumerate(commits):
        parents = stage.git(repo, "rev-list", "--parents", "-n", "1", commit).stdout.decode().split()
        require(parents == [commit, prior], "handoff commit is not direct-parent append")
        appid = ordered[index]
        path = contract["handoff_prefix"] + "/" + appid + ".json"
        stage.require_only_new(repo, commit, [path])
        require(stage.blob(repo, commit, path) == stage.blob(repo, tip, path),
                "typed result replaced after first introduction")
        raw = stage.git(repo, "show", commit + ":" + path).stdout
        require(len(raw) <= 2_000_000, "oversize typed semantic result")
        from dossier_shadow_18_github_python_handoff import semantic_submission
        # Only the original immutable typed transport verifier may admit a result.
        semantic_submission(repo, stage, {
            "submission_branch": branch, "submission_namespace": contract["handoff_prefix"]},
            appid, commit, tip)
        prior = commit
    return {"verified_submitted_appids": ordered[:len(commits)],
            "next_unsubmitted_appid": ordered[len(commits)] if len(commits) < len(ordered) else None,
            "verified_tip": tip, "verified_count": len(commits),
            "no_automatic_resume_for_uncommitted_attempt": True}



def validate_github_authority_receipt(run, receipt, *, appid):
    """Verifier of separately REST-fetched Actions run + Actions artifact.

    Caller must obtain run and artifact independently from GitHub API; a
    chat-supplied run ID/receipt string by itself has zero authority.
    """
    require(type(run) is dict and type(receipt) is dict
            and type(run.get("actor")) is dict
            and run["actor"].get("login") == "kentrap2011-hub"
            and run.get("event") == "workflow_dispatch"
            and run.get("run_attempt") == 1
            and run.get("conclusion") == "success"
            and run.get("status") == "completed"
            and run.get("head_branch") == "main"
            and run.get("path") ==
              ".github/workflows/validate-dossier-shadow-18-trial-wide-authority.yml"
            and str(run.get("id")) == receipt.get("github_run_id")
            and run.get("head_sha") == receipt.get("github_main_sha")
            and receipt.get("schema") ==
              "DOSSIER-SHADOW-18-TRIAL-WIDE-READONLY-GATE-RECEIPT-V1"
            and receipt.get("original_marker") == FIXED_MARKER
            and receipt.get("trial_id") == TRIAL
            and receipt.get("issuer_run_id") == 39054131983
            and receipt.get("original_order") == EXPECTED_APPIDS
            and receipt.get("semantics_executed") is False
            and receipt.get("production_active") is False
            and receipt.get("submission_is_not_acceptance") is True
            and type(receipt.get("appointees")) is dict
            and set(receipt["appointees"]) == {"A","B","C"}
            and len(set(receipt["appointees"].values())) == 3
            and type(receipt.get("ready_appids_in_original_order")) is list
            and len(receipt["ready_appids_in_original_order"]) == 12
            and receipt["ready_appids_in_original_order"] ==
              [i for i in EXPECTED_APPIDS if i not in FIXED_MISSING | INVALID]
            and str(appid) in receipt["ready_appids_in_original_order"],
            "forged, stale, mismatched or absent GitHub Actions Assembly permit")
    return True


def validate_publish_approval(comment, *, appid, semantic_commit):
    """Verify an API-fetched GitHub owner comment scoped to ONE typed commit.

    A public workflow confirmation string, a task prompt, or this Python
    function's in-memory argument alone is NEVER human consent. Real workflow
    must fetch this record from GitHub REST using its readonly issues token.
    """
    require(type(comment) is dict and str(comment.get("id", "")).isdigit()
            and comment.get("user", {}).get("login") == "kentrap2011-hub"
            and comment.get("issue_url") ==
              "https://api.github.com/repos/kentrap2011-hub/steam-kz-deals-2/issues/230"
            and isinstance(comment.get("created_at"), str),
            "no separately recorded original PR #230 owner approval")
    require(str(appid) in FIXED_RESEARCH_COMMITS
            and re.fullmatch("[0-9a-f]{40}", str(semantic_commit)) is not None,
            "invalid AppID or exact typed introduction")
    expected = ("AUTHORIZE_SHADOW_ASSEMBLY_PUBLISH_V1 "
                "trial_id=" + TRIAL + " appid=" + str(appid)
                + " semantic_commit=" + semantic_commit)
    require(comment.get("body", "").strip() == expected,
            "GitHub approval must match this exact AppID and semantic commit")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for field in ("contract", "original", "decision", "pins", "appointments", "inspect"):
        ap.add_argument("--" + field, required=True)
    args = ap.parse_args()
    import os
    # ONLY run as GitHub Actions on main, never user-supplied pseudo-receipts.
    require(os.getenv("GITHUB_ACTIONS") == "true", "run in verified GitHub Actions only")
    ctx = {"event": os.getenv("GITHUB_EVENT_NAME"), "ref": os.getenv("GITHUB_REF"),
           "repository": os.getenv("GITHUB_REPOSITORY"), "actor": os.getenv("GITHUB_ACTOR"),
           "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"), "run_id": os.getenv("GITHUB_RUN_ID"),
           "sha": os.getenv("GITHUB_SHA")}
    receipt = validate_authority(*(load(getattr(args, x)) for x in
                                   ("contract","original","decision","pins","appointments","inspect")),
                                 github_context=ctx)
    print(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

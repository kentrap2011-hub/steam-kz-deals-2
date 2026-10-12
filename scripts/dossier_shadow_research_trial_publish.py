#!/usr/bin/env python3
"""One-use GitHub Actions control-plane publication of a frozen SHADOW Research trial.

This script never grants semantic authority. The only remote write is the
create-only sandbox branch containing exactly two single-parent commits:
(1) the strict six-group proposed buffer, (2) one marker-only commit.
No developer/semantic worker may use this as a general Git write utility.
"""
import argparse
import json
import os
import re
import secrets
import subprocess
import sys
from pathlib import Path

from dossier_shadow_research_trial import (
    CONTRACT, DECISION, PREFIX, TRIAL, frozen_trial, exact_marker, sha, blob,
)

REPOSITORY = "kentrap2011-hub/steam-kz-deals-2"
WORKFLOW = ".github/workflows/publish-dossier-shadow-research-freeze.yml"
BRANCH = "sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research"
BUFFER = PREFIX + "/research_buffer.json"
APPROVAL = "PUBLISH_DOSSIER_SHADOW_18_ONCE"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
ORDER = [3, 8, 13, 15, 18, 20]
EXPECTED_APPIDS = [
    "1508750", "1517180", "1533420",
    "1590230", "1599600", "1607130",
    "1849000", "1857090", "1868140",
    "1999170", "1999360", "2009010",
    "206420", "2067050", "2076140",
    "2124120", "213610", "2138710",
]


def check(ok, why):
    if not ok:
        raise RuntimeError("SANDBOX_FREEZE_BLOCKED: " + why)


def run(repo, *args, check_success=True):
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if check_success and result.returncode:
        raise RuntimeError("SANDBOX_FREEZE_BLOCKED: Git operation failed: " + " ".join(args[:3]))
    return result.stdout.decode("utf-8").strip()


def assert_github_dispatch(expected, confirmation, env):
    """This gate precedes every filesystem or remote mutation."""
    check(bool(SHA40.fullmatch(expected)), "expected main SHA must be 40 lowercase hex")
    check(confirmation == APPROVAL, "explicit single-use Director confirmation missing")
    check(env.get("GITHUB_ACTIONS") == "true"
          and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
          and env.get("GITHUB_REPOSITORY") == REPOSITORY
          and env.get("GITHUB_REF") == "refs/heads/main"
          and env.get("GITHUB_WORKFLOW_REF") == REPOSITORY + "/" + WORKFLOW + "@refs/heads/main"
          and env.get("GITHUB_SHA") == expected,
          "only the actual main-branch GitHub manual workflow can publish")
    check(env.get("GITHUB_RUN_ATTEMPT") == "1", "workflow rerun is forbidden")


def remote_sha(repo, ref):
    out = run(repo, "ls-remote", "--heads", "origin", ref)
    rows = [x.split() for x in out.splitlines() if x.strip()]
    check(len(rows) <= 1, "remote ref is ambiguous")
    return rows[0][0] if rows else None


def assert_clean(repo):
    check(not run(repo, "status", "--porcelain", "--untracked-files=all"),
          "checkout must be clean before publication")


def assert_one_new_path(repo, parent, child, path):
    parents = run(repo, "rev-list", "--parents", "-n", "1", child).split()
    check(parents == [child, parent], "commit must have exactly one actual Git parent")
    delta = run(repo, "diff-tree", "--no-commit-id", "--name-status", "-r", child)
    check(delta == "A\t" + path, "unexpected or overwritten Git path")
    previous = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", parent + ":" + path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    check(previous.returncode != 0, "create-only path collision")


def commit_new(repo, path, data, message):
    destination = repo / path
    check(not destination.exists(), "original path already exists: " + path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    run(repo, "add", "--", path)
    check(run(repo, "diff", "--cached", "--name-status") == "A\t" + path,
          "only allowlisted new file can be staged")
    parent = run(repo, "rev-parse", "HEAD")
    run(repo, "-c", "user.name=GitHub sandbox control plane",
        "-c", "user.email=github-sandbox-control-plane@users.noreply.github.com",
        "commit", "--no-gpg-sign", "-m", message, "--", path)
    commit = run(repo, "rev-parse", "HEAD")
    assert_one_new_path(repo, parent, commit, path)
    assert_clean(repo)
    return commit


def strict_proposal(repo):
    """Only the already accepted PR #201 verifier / PR #215 --propose-buffer."""
    task = subprocess.run(
        [sys.executable, str(repo / "scripts/dossier_shadow_research_trial_prepare.py"),
         "--propose-buffer"],
        cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    check(task.returncode == 0
          and b"PROPOSAL_ONLY_NOT_AN_AUTHORIZATION" in task.stderr,
          "existing six-group strict historical verifier rejected buffer proposal")
    proposal = json.loads(task.stdout.decode("utf-8"))
    decision = json.loads((repo / DECISION).read_text("utf-8"))
    contract = json.loads((repo / CONTRACT).read_text("utf-8"))
    check(proposal.get("schema") == "DOSSIER-SHADOW-RESEARCH-BUFFER-V1"
          and proposal.get("trial_id") == TRIAL
          and [g["sequence"] for g in proposal["groups"]] == ORDER
          and proposal["groups"] == decision["scope"]["groups"]
          and len(proposal["items"]) == 18
          and [x["appid"] for x in proposal["items"]] == EXPECTED_APPIDS
          and [x["group_sequence"] for x in proposal["items"]] == [x for x in ORDER for _ in range(3)]
          and [x["item_index"] for x in proposal["items"]] == list(range(3)) * 6
          and proposal["source_head"] == "95a4bf4990a60082ecb3302da5bc7f23b618d93e"
          and proposal["source_work_blob_sha"] == "ef40fc186aabc79dfd24c72864dbe43817a56039"
          and proposal["source_audit_blob_sha"] == "8dbf4437d7ba439942f58a6f36d89d6a7ddeec7b",
          "proposal changed six historical original three-game groups or writer SHA")
    check(contract["standalone_sandbox_semantics_approved"] is False
          and contract["reviewer_roles_finalized"] is False
          and contract["production_execution"] is False
          and contract["canonical_production_authority_active"] is False,
          "inactive sandbox/production gates cannot be modified by publication")
    return task.stdout


def local_two_commit_freeze(repo, proposal_raw, nonce):
    """Only called by main after GH gate; tests use disposable isolated repos."""
    check(bool(re.fullmatch(r"[0-9a-f]{32}", nonce)), "nonce invalid")
    source = run(repo, "rev-parse", "HEAD")
    buffer_commit = commit_new(
        repo, BUFFER, proposal_raw, "Freeze exact nonproduction six-group Research buffer")
    marker_path = PREFIX + "/run_starts/" + nonce + ".json"
    marker_raw = (json.dumps({
        "schema": "DOSSIER-SHADOW-RESEARCH-RUN-START-V1",
        "schema_version": 1, "trial_id": TRIAL, "nonce": nonce,
    }, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    marker_commit = commit_new(
        repo, marker_path, marker_raw, "Start immutable nonproduction Research trial marker")
    parent, seen_nonce = exact_marker(repo, marker_commit)
    check(parent == buffer_commit and seen_nonce == nonce,
          "marker did not freeze the exact buffer commit")
    check(run(repo, "diff", "--name-status", source, marker_commit).splitlines() ==
          ["A\t" + BUFFER, "A\t" + marker_path],
          "two Git commits wrote outside exact frozen Research allowlist")
    return {"source_commit": source, "buffer_commit": buffer_commit,
            "marker_commit": marker_commit, "marker_parent": buffer_commit,
            "buffer_path": BUFFER, "marker_path": marker_path}


def publish(repo, expected):
    check(run(repo, "rev-parse", "HEAD") == expected,
          "checked-out main differs from expected SHA")
    check(run(repo, "symbolic-ref", "--short", "HEAD") == "main",
          "not checked out on main")
    assert_clean(repo)
    check(remote_sha(repo, "refs/heads/main") == expected,
          "live main head drifted before publication")
    check(remote_sha(repo, "refs/heads/" + BRANCH) is None,
          "one-use sandbox ref already exists; replay/collision forbidden")
    proposal_raw = strict_proposal(repo)
    assert_clean(repo)
    run(repo, "checkout", "-b", BRANCH)
    proof = local_two_commit_freeze(repo, proposal_raw, secrets.token_hex(16))
    frozen = frozen_trial(repo, marker_commit=proof["marker_commit"],
                          buffer_path=BUFFER)
    check(frozen["marker_parent"] == proof["buffer_commit"]
          and frozen["source_head"] == "95a4bf4990a60082ecb3302da5bc7f23b618d93e"
          and len(frozen["items"]) == 18
          and frozen["sandbox_semantics_authorized"] is False
          and frozen["canonical_acceptance"] is False
          and frozen["status"] == "blocked",
          "read-only strict frozen_trial original Git ancestry/contract proof failed")
    check(remote_sha(repo, "refs/heads/main") == expected
          and remote_sha(repo, "refs/heads/" + BRANCH) is None,
          "ref drift or one-use ref replay detected before push")
    # Explicit empty expected ref is an atomic create-only remote lease.
    ref = "refs/heads/" + BRANCH
    run(repo, "push", "--porcelain", "--force-with-lease=" + ref + ":",
        "origin", "HEAD:" + ref)
    check(remote_sha(repo, ref) == proof["marker_commit"],
          "durable GitHub sandbox branch does not reference original marker")
    run(repo, "fetch", "--no-tags", "origin", ref)
    check(run(repo, "rev-parse", "FETCH_HEAD") == proof["marker_commit"],
          "published Git marker ref cannot be fetched back")
    verified = frozen_trial(repo, marker_commit=proof["marker_commit"],
                            buffer_path=BUFFER)
    check(verified["marker_parent"] == proof["buffer_commit"]
          and verified["status"] == "blocked",
          "post-publication Git frozen_trail unexpectedly changed")
    return {
        **proof, "sandbox_branch": BRANCH,
        "buffer_blob_sha": verified["buffer_blob_sha"],
        "trial_id": TRIAL,
        "group_sequences": ORDER,
        "total_games": len(verified["items"]),
        "status": "published_real_GitHub_marker_and_buffer",
        "sandbox_research_invocation_ready": "blocked",
        "standalone_sandbox_semantics_approved": False,
        "semantic_calls": 0, "production_mutations": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-main-sha", required=True)
    parser.add_argument("--approval", required=True)
    args = parser.parse_args()
    assert_github_dispatch(args.expected_main_sha, args.approval, os.environ)
    output = publish(Path.cwd().resolve(), args.expected_main_sha)
    print(json.dumps(output, sort_keys=True, indent=2))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write("### Immutable Research sandbox freeze (NOT semantic approval)\n\n")
            for key in ("sandbox_branch", "source_commit", "buffer_commit",
                        "marker_commit", "buffer_path", "buffer_blob_sha",
                        "status", "sandbox_research_invocation_ready",
                        "semantic_calls", "production_mutations"):
                handle.write("- " + key + ": \`" + str(output[key]) + "\`\n")


if __name__ == "__main__":
    main()

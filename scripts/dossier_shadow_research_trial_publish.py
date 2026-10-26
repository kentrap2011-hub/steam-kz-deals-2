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



# V2 reuses the V1 Git control-plane primitives above. This prospective mode
# is intentionally disabled by the V2 contract; it is NOT a semantic grant.
def v2_scope(repo):
    from dossier_research_notes_v2 import _contract, _original_rows, blob_for
    cfg = _contract()
    m = cfg["manual_v2_issuer"]
    check(cfg["active"] is False and cfg["authorized_for_semantic_execution"] is False
          and cfg["authorized_for_canonical_ingest"] is False
          and cfg["production_enabled"] is False,
          "V2 issuer must not activate semantic/production paths")
    check(m["trial_id"] == "dossier-notes-v2-original18-first"
          and m["sandbox_branch"] == "sandbox/dossier-notes-v2-original18-first"
          and m["manifest_path"] == "data/control/dossier_notes_v2/manifests/" + m["trial_id"] + ".json"
          and m["authorization_path"] == "data/control/dossier_notes_v2/authorizations/" + m["trial_id"] + ".json"
          and m["frozen_original_buffer_blob_sha"] == "c8a6b6f515162f431c0e3d86175376114c0acf7e"
          and m["workflow_freeze"] == WORKFLOW
          and m["workflow_authorize"] == ".github/workflows/authorize-dossier-shadow-research-feasibility.yml"
          and m["canonical_acceptance"] is False and m["assembly_authorized"] is False
          and m["semantic_execution_authorized"] is False,
          "prospective V2 namespace/scope changed")
    rows = _original_rows()  # authentic V1 Git blob, complete edition/assignment pins
    check(len(rows) == 18
          and [r["appid"] for r in rows] == EXPECTED_APPIDS
          and [r["group_sequence"] for r in rows] == [n for n in ORDER for _ in range(3)],
          "V2 scope differs from the actual frozen original 18")
    check(blob_for((repo / "config/dossier_notes_v2_pinned_original_research_buffer_v1.json").read_bytes())
          == m["frozen_original_buffer_blob_sha"],
          "original immutable Research buffer copy changed")
    return cfg, m, rows


def v2_grant(repo, expected, env):
    """Require separately Git-committed scoped human evidence before any V2 write.

    A task prompt, hardcoded confirmation string and old V1 SHA are not a grant.
    The *actual* Actions actor is bound by the GitHub-controlled environment.
    """
    from dossier_two_stage_staging import first_parent_contains
    cfg, m, rows = v2_scope(repo)
    g = m["human_grant"]
    check(m["enabled"] is True and m["enabled_by_default"] is False,
          "inactive V2 issuer: distinct human grant and later enablement required")
    check(isinstance(g["commit"], str) and SHA40.fullmatch(g["commit"])
          and isinstance(g["blob_sha"], str) and SHA40.fullmatch(g["blob_sha"])
          and isinstance(g["github_actor_id"], str) and g["github_actor_id"].isdigit(),
          "missing immutable scoped V2 human grant")
    check(env.get("GITHUB_ACTOR_ID") == g["github_actor_id"]
          and bool(env.get("GITHUB_ACTOR"))
          and env.get("GITHUB_TRIGGERING_ACTOR") == env.get("GITHUB_ACTOR")
          and str(env.get("GITHUB_RUN_ID", "")).isdigit(),
          "GitHub actor identity/run not verified against preapproved grant")
    check(first_parent_contains(repo, g["commit"], expected),
          "V2 human grant does not precede exact main SHA on first-parent history")
    grant_path = g["path"]
    check(grant_path == "config/dossier_notes_v2_issuer_human_grant.json",
          "human grant path altered")
    assert_one_new_path(repo, run(repo, "rev-parse", g["commit"] + "^"),
                        g["commit"], grant_path)
    data_sha = run(repo, "rev-parse", g["commit"] + ":" + grant_path)
    check(data_sha == g["blob_sha"]
          and run(repo, "rev-parse", expected + ":" + grant_path) == g["blob_sha"],
          "immutable approved grant blob not preserved on main")
    check(not run(repo, "log", "--first-parent", "--format=%H",
                  g["commit"] + ".." + expected, "--", grant_path),
          "scoped grant mutated or replaced after approval")
    record = json.loads(run(repo, "show", g["commit"] + ":" + grant_path))
    check(record == {
        "schema":"DOSSIER-NOTES-V2-MANUAL-ISSUER-HUMAN-GRANT",
        "schema_version":2,
        "trial_id":m["trial_id"],
        "original_buffer_blob_sha":m["frozen_original_buffer_blob_sha"],
        "original_pins":cfg["immutable_original_pins"],
        "original_groups":cfg["original_groups"],
        "github_actor_id":g["github_actor_id"],
        "scope":"issue_single_original18_V2_manifest_marker_then_separate_authorization_only",
        "semantic_execution_approved":False,
        "production_approved":False,
    }, "human evidence is not an exact scoped original-18 approval")
    return cfg, m, rows


def v2_scoped_owner_dispatch(cfg, env):
    """Real GitHub owner/manual workflow identity, not a chat-supplied actor."""
    p = cfg.get("original18_trial_scoped_authorization") or {}
    check(p.get("enabled") is True
          and p.get("exact_trial_id") == "dossier-notes-v2-original18-first"
          and p.get("github_owner_login") == "kentrap2011-hub"
          and p.get("github_owner_actor_id") == "315790060"
          and p.get("semantic_phases") == ["research", "assembly"]
          and p.get("isolated_sandbox_only") is True
          and p.get("production") is False
          and p.get("canonical_ingest") is False
          and env.get("GITHUB_ACTOR") == p["github_owner_login"]
          and env.get("GITHUB_TRIGGERING_ACTOR") == env.get("GITHUB_ACTOR")
          and env.get("GITHUB_ACTOR_ID") == p["github_owner_actor_id"]
          and env.get("GITHUB_REPOSITORY_OWNER_ID") == env.get("GITHUB_ACTOR_ID")
          and env.get("GITHUB_RUN_ATTEMPT") == "1"
          and str(env.get("GITHUB_RUN_ID", "")).isdigit(),
          "original18 pilot requires actual first-attempt authenticated owner Actions dispatch")
    return p


def local_v2_scoped_owner_grant(repo, cfg, m, env):
    """First sandbox commit: create-only owner grant, immutable in this Git tree.

    No production/main write, no arbitrary human-provided actor identity.
    A *separate* real GitHub manual authorization must follow the frozen marker.
    """
    v2_scoped_owner_dispatch(cfg, env)
    path = m["human_grant"]["path"]
    check(path == "config/dossier_notes_v2_issuer_human_grant.json"
          and m["human_grant"]["commit"] is None
          and m["human_grant"]["blob_sha"] is None
          and m["human_grant"]["github_actor_id"] is None,
          "scoped first-trial grant cannot replace preexisting authority")
    record = {
        "schema":"DOSSIER-NOTES-V2-MANUAL-ISSUER-HUMAN-GRANT",
        "schema_version":2,
        "trial_id":m["trial_id"],
        "original_buffer_blob_sha":m["frozen_original_buffer_blob_sha"],
        "original_pins":cfg["immutable_original_pins"],
        "original_groups":cfg["original_groups"],
        "github_actor_id":env["GITHUB_ACTOR_ID"],
        "scope":"issue_single_original18_V2_manifest_marker_then_separate_authorization_only",
        "semantic_execution_approved":True,
        "production_approved":False,
    }
    raw = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    source = run(repo, "rev-parse", "HEAD")
    check(not run(repo, "ls-files", "--", path), "scoped owner grant path already exists")
    grant = commit_new(repo, path, raw, "Grant one original18 V2 pilot on sandbox only")
    assert_one_new_path(repo, source, grant, path)
    return {"path":path,"commit":grant,
            "blob_sha":run(repo, "rev-parse", grant + ":" + path),
            "github_actor_id":env["GITHUB_ACTOR_ID"]}


def assert_v2_freeze_dispatch(expected, confirmation, env):
    check(isinstance(expected, str) and SHA40.fullmatch(expected),
          "V2 expected main SHA invalid")
    check(confirmation == "FREEZE_DOSSIER_NOTES_V2_ORIGINAL18_ONCE",
          "fresh V2-only manual freeze confirmation missing")
    check(env.get("GITHUB_ACTIONS") == "true"
          and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
          and env.get("GITHUB_REPOSITORY") == REPOSITORY
          and env.get("GITHUB_REF") == "refs/heads/main"
          and env.get("GITHUB_WORKFLOW_REF") == REPOSITORY + "/" + WORKFLOW + "@refs/heads/main"
          and env.get("GITHUB_SHA") == expected
          and env.get("GITHUB_RUN_ATTEMPT") == "1",
          "only first-attempt GitHub manual main issuer can freeze V2")


def local_v2_freeze(repo, trial_id, rows, nonce):
    """Real two-commit freeze logic on the supplied Git repo (offline fixtures)."""
    from dossier_research_notes_v2 import manifest_blueprint, _manifest
    check(bool(re.fullmatch("[a-f0-9]{32}", nonce)), "V2 marker nonce invalid")
    blueprint = manifest_blueprint(trial_id, rows)
    source = run(repo, "rev-parse", "HEAD")
    manifest_commit = commit_new(repo, blueprint["output_path"], blueprint["bytes"],
                                 "Freeze original-18 Dossier Notes V2 manifest only")
    marker_path = "data/control/dossier_notes_v2/run_starts/" + nonce + ".json"
    marker = {"schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
              "trial_id":trial_id,"nonce":nonce}
    marker_raw = (json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n").encode()
    marker_commit = commit_new(repo, marker_path, marker_raw,
                               "Start immutable inactive Dossier Notes V2 marker")
    frozen, manifest_blob = _manifest(repo, marker_commit, trial_id)
    check(frozen["items"] == rows and manifest_blob == blueprint["blob_sha"]
          and run(repo, "rev-parse", marker_commit + "^") == manifest_commit
          and run(repo, "diff", "--name-status", source, marker_commit).splitlines()
              == ["A\t" + blueprint["output_path"], "A\t" + marker_path],
          "V2 manifest/marker parent, original-18 scope or one-add proof failed")
    return {"source_commit":source,"manifest_commit":manifest_commit,
            "marker_commit":marker_commit,"marker_parent":manifest_commit,
            "manifest_path":blueprint["output_path"],"manifest_blob_sha":manifest_blob,
            "marker_path":marker_path,"nonce":nonce,"trial_id":trial_id,
            "semantic_execution_authorized":False}


def publish_v2(repo, expected):
    """Same original create-only remote lease; permanently inactive until grant."""
    assert_canonical = __import__("dossier_shadow_research_feasibility").assert_canonical_remote
    assert_canonical(repo)
    check(run(repo, "rev-parse", "HEAD") == expected
          and run(repo, "symbolic-ref", "--short", "HEAD") == "main"
          and remote_sha(repo, "refs/heads/main") == expected,
          "V2 exact remote main SHA drifted")
    assert_clean(repo)
    cfg, m, rows = v2_scope(repo)
    check(m["enabled"] is True and m["enabled_by_default"] is False,
          "scoped issuer not explicitly enabled")
    ref = "refs/heads/" + m["sandbox_branch"]
    check(remote_sha(repo, ref) is None, "V2 branch already exists; no second marker or replay")
    if m["human_grant"]["commit"] is None:
        # The first manual owner dispatch writes the immutable scoped grant to
        # the NEW sandbox (never main); then immediately freezes the original18.
        v2_scoped_owner_dispatch(cfg, os.environ)
        run(repo, "checkout", "-b", m["sandbox_branch"])
        m = {**m, "human_grant": local_v2_scoped_owner_grant(
            repo, cfg, m, os.environ)}
    else:
        # Preserve the older verified, already-pinned issuer path unchanged.
        cfg, m, rows = v2_grant(repo, expected, os.environ)
        run(repo, "checkout", "-b", m["sandbox_branch"])
    proof = local_v2_freeze(repo, m["trial_id"], rows, secrets.token_hex(16))
    check(remote_sha(repo, "refs/heads/main") == expected
          and remote_sha(repo, ref) is None,
          "V2 main or new branch changed before first publication")
    run(repo, "push", "--porcelain", "--force-with-lease=" + ref + ":",
        "origin", "HEAD:" + ref)
    check(remote_sha(repo, ref) == proof["marker_commit"], "V2 marker not durable")
    run(repo, "fetch", "--no-tags", "origin", ref)
    check(run(repo, "rev-parse", "FETCH_HEAD") == proof["marker_commit"], "V2 freeze re-fetch mismatch")
    return {**proof,"sandbox_branch":m["sandbox_branch"],
            "human_grant_commit":m["human_grant"]["commit"],
            "issuer_gh_run_id":os.environ["GITHUB_RUN_ID"],
            "issuer_gh_actor_id":os.environ["GITHUB_ACTOR_ID"],
            "status":"issued_inactive_V2_marker_not_semantics"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-main-sha", required=True)
    parser.add_argument("--approval", required=True)
    parser.add_argument("--version", choices=("v1", "v2"), default="v1")
    args = parser.parse_args()
    if args.version == "v1":
        assert_github_dispatch(args.expected_main_sha, args.approval, os.environ)
        output = publish(Path.cwd().resolve(), args.expected_main_sha)
    else:
        assert_v2_freeze_dispatch(args.expected_main_sha, args.approval, os.environ)
        output = publish_v2(Path.cwd().resolve(), args.expected_main_sha)
    print(json.dumps(output, sort_keys=True, indent=2))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            if args.version == "v1":
                handle.write("### Immutable Research sandbox freeze (NOT semantic approval)\n\n")
                for key in ("sandbox_branch", "source_commit", "buffer_commit",
                            "marker_commit", "buffer_path", "buffer_blob_sha",
                            "status", "sandbox_research_invocation_ready",
                            "semantic_calls", "production_mutations"):
                    handle.write("- " + key + ": " + chr(96) + str(output[key]) + chr(96) + "\n")
            else:
                handle.write("### Inactive V2 marker, no semantic authorization\n\n")
                for key in ("sandbox_branch", "source_commit", "manifest_commit",
                            "marker_commit", "manifest_path", "manifest_blob_sha",
                            "human_grant_commit", "status"):
                    handle.write("- " + key + ": `" + str(output[key]) + "`\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Append-only GitHub-owned Lean writer attempt journal; no semantic or main writes.

The original one-use claim is an immutable anchor in the SAME control ref.
Only fast-forward, one-add event commits are permitted. The shared Actions
writer concurrency group serializes normal runs; Git ref CAS/readback protects
against a second actor or an uncertain publication.
"""
import datetime as dt
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import dossier_notes_v2_generic_replay as generic

PREFIX = "refs/heads/dossier-lean-auto-attempts/"
BASE = "data/control/dossier_notes_v2/auto_writer_attempts/"
SCHEMA = "DOSSIER-LEAN-AUTO-WRITER-EVENT-V2"
KINDS = {"started", "retryable_failed", "blocked_invalid_input", "accepted"}


def check(condition, message):
    if not condition:
        raise ValueError("LEAN_RETRY_BLOCKED: " + message)


def git(repo, *args, check_result=True):
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if check_result and p.returncode:
        raise ValueError("LEAN_RETRY_GIT: " + " ".join(args) + ": " + p.stderr[:350])
    return p


def sha(repo, *args):
    return git(repo, *args).stdout.strip()


def ref_for(trial):
    check(generic.is_generic(trial), "invalid trial ID")
    return PREFIX + trial.removeprefix(generic.PREFIX)


def remote_head(repo, trial):
    result = git(repo, "ls-remote", "origin", ref_for(trial)).stdout.splitlines()
    check(len(result) <= 1, "ambiguous control ref")
    if not result:
        return None
    fields = result[0].split()
    check(len(fields) == 2 and fields[1] == ref_for(trial)
          and len(fields[0]) == 40 and
          all(c in "0123456789abcdef" for c in fields[0]), "bad control ref")
    return fields[0]


def read(repo, trial, expected_grant_hash, historical_anchor=None):
    """Return authenticated linear append-only control history, or None."""
    head = remote_head(repo, trial)
    if head is None:
        return None
    ref = ref_for(trial)
    git(repo, "fetch", "--no-tags", "origin", ref)
    check(git(repo, "cat-file", "-e", head + "^{commit}", check_result=False).returncode == 0,
          "remote journal commit unavailable")
    claim_path = BASE + trial + ".json"
    anchors = sha(repo, "log", "--reverse", "--format=%H", head, "--", claim_path).splitlines()
    check(len(anchors) == 1, "claim was replaced or rewritten")
    anchor = anchors[0]
    if historical_anchor:
        check(anchor == historical_anchor, "historic consumed claim cannot be substituted")
    first = json.loads(sha(repo, "show", anchor + ":" + claim_path))
    from dossier_two_stage_staging import require_only_new
    check(require_only_new(repo, anchor, [claim_path]) ==
          first.get("automation_source_main_sha"), "claim not original one-add")
    check(first.get("schema") == "DOSSIER-LEAN-AUTO-WRITER-ATTEMPT-V1"
          and first.get("trial_id") == trial
          and first.get("item_commits_sha256") == expected_grant_hash
          and first.get("canonical_acceptance") is False
          and first.get("production") is False
          and first.get("deep") is False, "original claim/grant mismatch")
    commits = sha(repo, "rev-list", "--reverse", anchor + ".." + head).splitlines()
    events = []
    previous = anchor
    for commit in commits:
        check(sha(repo, "rev-list", "--parents", "-n", "1", commit).split() ==
              [commit, previous], "journal is not a single-parent append-only chain")
        delta = sha(repo, "diff-tree", "--no-commit-id", "--name-status", "-r", commit)
        parts = delta.split("\t")
        check(len(parts) == 2 and parts[0] == "A"
              and parts[1].startswith(BASE + trial + "/events/")
              and parts[1].endswith(".json"), "journal changed existing content")
        event = json.loads(sha(repo, "show", commit + ":" + parts[1]))
        check(event.get("schema") == SCHEMA and event.get("trial_id") == trial
              and event.get("item_commits_sha256") == expected_grant_hash
              and event.get("claim_anchor_sha") == anchor
              and event.get("kind") in KINDS
              and type(event.get("attempt")) is int
              and type(event.get("run_id")) is str
              and event["run_id"].isdigit()
              and type(event.get("main_sha")) is str
              and len(event["main_sha"]) == 40,
              "invalid append-only event contents")
        check(parts[1] == BASE + trial + "/events/" +
              f"{len(events)+1:04d}-{event['kind']}.json",
              "nonsequential journal event")
        if not events:
            check(event["kind"] == "started"
                  and event["attempt"] == (2 if historical_anchor else 1),
                  "initial attempt must follow consumed original claim")
        else:
            last = events[-1]
            check((event["kind"] == "started"
                   and last["kind"] == "retryable_failed"
                   and event["attempt"] == last["attempt"] + 1
                   and event["main_sha"] != last["main_sha"])
                  or (event["kind"] != "started"
                      and last["kind"] == "started"
                      and event["attempt"] == last["attempt"]
                      and event["main_sha"] == last["main_sha"]
                      and event["run_id"] == last["run_id"]),
                  "invalid retry transition, actor or duplicate acceptance")
        events.append(event)
        previous = commit
    check(remote_head(repo, trial) == head, "journal moved during immutable read")
    return {"head": head, "anchor": anchor, "claim": first,
            "events": events, "last": events[-1] if events else None}


def append(repo, trial, snapshot, event):
    """Fast-forward CAS, remote readback; no retry on uncertain control push."""
    head = snapshot["head"]
    previous = snapshot["events"]
    event_path = BASE + trial + "/events/" + (
        f"{len(previous)+1:04d}-{event['kind']}.json")
    with TemporaryDirectory(prefix="lean-retry-control-") as tmp:
        tree = Path(tmp) / "journal"
        git(repo, "worktree", "add", "--detach", str(tree), head)
        try:
            path = tree / event_path
            check(not path.exists(), "attempt event already exists")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(event, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
            git(tree, "add", "--", event_path)
            check(sha(tree, "diff", "--cached", "--name-status") ==
                  "A\t" + event_path, "journal attempted other write")
            git(tree, "config", "user.name", "steam-kz-bot")
            git(tree, "config", "user.email", "steam-kz-bot@users.noreply.github.com")
            git(tree, "commit", "-m", "Record Lean writer " + event["kind"])
            target = sha(tree, "rev-parse", "HEAD")
            check(remote_head(repo, trial) == head,
                  "journal CAS lease lost before push")
            push = git(tree, "push", "origin", "HEAD:" + ref_for(trial),
                       check_result=False)
            # An accepted push with a lost response is safe only when the
            # EXACT target hash is observed. Never blindly retry a push.
            check(remote_head(repo, trial) == target,
                  "control push uncertain or rejected: " + push.stderr[:250])
            return target
        finally:
            git(repo, "worktree", "remove", "--force", str(tree),
                check_result=False)


def make_event(snapshot, readiness, env, kind, attempt, *, detail=None,
               sandbox_commit=None):
    check(kind in KINDS, "unknown transition")
    event = {
        "schema": SCHEMA, "trial_id": readiness["trial_id"],
        "claim_anchor_sha": snapshot["anchor"],
        "item_commits_sha256": snapshot["claim"]["item_commits_sha256"],
        "marker_commit": readiness["marker_commit"],
        "frozen_sandbox_head": readiness["sandbox_head"],
        "owner_source_run_id": str(
            readiness["issuer"]["github_authorization_run_id"]),
        "attempt": attempt, "kind": kind,
        "run_id": env["GITHUB_RUN_ID"], "main_sha": env["GITHUB_SHA"],
        "at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "detail": detail, "accepted_sandbox_commit": sandbox_commit,
        "canonical_acceptance": False, "deep_ready": False,
    }
    return event


def minutes_since(event):
    seen = dt.datetime.fromisoformat(event["at_utc"])
    check(seen.tzinfo is not None, "journal time must be offset-aware")
    delta = (dt.datetime.now(dt.timezone.utc) - seen).total_seconds()
    check(delta >= -120, "future-dated lease")
    return delta / 60.0


def eligible(snapshot, *, source_sha, max_attempts=3, stale_minutes=30,
             retry_delay_minutes=2):
    """No same-code retry; live active lease wins until proven stale."""
    last = snapshot["last"]
    if last is None:
        return True, 2 if snapshot["claim"].get("no_retry") is True else 1
    if last["kind"] == "accepted":
        return False, "already_accepted"
    if last["kind"] == "blocked_invalid_input":
        return False, "blocked_invalid_input_requires_new_grant"
    if last["kind"] == "started":
        if minutes_since(last) < stale_minutes:
            return False, "writer_lease_active"
        return False, "stale_lease_requires_reconcile"
    if last["attempt"] >= max_attempts:
        return False, "attempt_budget_exhausted"
    if source_sha == last["main_sha"]:
        return False, "same_source_retry_disallowed"
    if minutes_since(last) < retry_delay_minutes:
        return False, "retry_backoff"
    return True, last["attempt"] + 1


def active_for_writer(repo, readiness, env, expected_sha, historic_anchor=None):
    snapshot = read(repo, readiness["trial_id"], readiness["pairs_sha256"],
                    historical_anchor=historic_anchor)
    check(snapshot is not None and snapshot["head"] == expected_sha,
          "active execution lease ref not current")
    last = snapshot["last"]
    check(last is not None and last["kind"] == "started"
          and last["run_id"] == env["GITHUB_RUN_ID"]
          and last["main_sha"] == env["GITHUB_SHA"]
          and last["marker_commit"] == readiness["marker_commit"]
          and last["frozen_sandbox_head"] == readiness["sandbox_head"]
          and last["owner_source_run_id"] ==
              str(readiness["issuer"]["github_authorization_run_id"]),
          "no verified active lease for this run and immutable grant")
    return True

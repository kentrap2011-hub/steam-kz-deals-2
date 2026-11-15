#!/usr/bin/env python3
"""GitHub-owned receipt materialization for V2 Research submissions.

Research publishes one create-only document using GitHub's contents API. Only
this verified owner GitHub Actions runner may authenticate the issuer, inspect
immutable candidate commits and add typed receipts to the isolated sandbox.

No semantic generation, source browsing attestations, retries, Assembly,
production/canonical state, queue ownership or scheduled execution.
"""
import argparse
import json
import os
import re
import time
from pathlib import Path

import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_per_item_receipts as receipts
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import (
    blob, blob_for, exists, first_parent_contains, git, parent, require_only_new,
)

WORKFLOW = ".github/workflows/ingest-dossier-notes-v2-research.yml"
AUTO_WORKFLOW = ".github/workflows/ingest-dossier-notes-v2-research-on-owner-push.yml"
SHA = re.compile(r"^[0-9a-f]{40}$")


def run(repo, *args):
    return git(repo, *args).stdout.decode("utf-8").strip()


def single_introduction(repo, path):
    """Return the sole first-parent Git introduction; never choose from edits."""
    history = run(repo, "log", "--first-parent", "--format=%H", "HEAD", "--", path).splitlines()
    if not history:
        return None
    if len(history) != 1:
        raise ValueError("candidate/receipt path has more than one Git-changing commit: " + path)
    return history[0]


def issuer_from_sandbox(repo, trial_id):
    """Owner identity is NOT taken from a worker submission."""
    p = batch.paths(trial_id)
    authorization_commit = single_introduction(repo, p["authorization"])
    if not authorization_commit or not SHA.fullmatch(authorization_commit):
        raise ValueError("missing unique immutable batch authorization")
    marker_commit = parent(repo, authorization_commit)
    anchor = batch.issuer_structure(
        repo, trial_id=trial_id, marker_commit=marker_commit,
        authorization_commit=authorization_commit,
    )
    if (anchor.get("semantic_execution_authorized") is not True
            or not first_parent_contains(repo, authorization_commit, "HEAD")):
        raise ValueError("sandbox does not contain authorized frozen batch")
    return anchor


def _receipt_path(assignment):
    return ("data/control/dossier_notes_v2/receipts/"
            + assignment["trial_id"] + "/g%06d/" % assignment["group_sequence"]
            + assignment["appid"] + "--" + assignment["assignment_id"]
            + "--research.json")


def ingest_local(repo, *, trial_id, anchor):
    """Deterministic sandbox-only materialization. CLI calls this AFTER real auth.

    This function is deliberately side-effect-limited to new typed receipt
    commits. It has no network access; the authenticated CLI owns the push.
    """
    repo = Path(repo).resolve()
    if run(repo, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("dirty sandbox checkout")
    if trial_id != anchor["trial_id"]:
        raise ValueError("wrong authorized batch")
    marker = anchor["marker_commit"]
    authorization = anchor["authorization_commit"]
    verified = batch.issuer_structure(
        repo, trial_id=trial_id, marker_commit=marker,
        authorization_commit=authorization,
    )
    if verified != anchor:
        raise ValueError("batch authorization changed")
    manifest, manifest_blob = v2._manifest(repo, marker, trial_id)
    if manifest_blob != anchor["manifest_blob_sha"]:
        raise ValueError("frozen manifest mismatch")

    started = time.monotonic()
    output = []
    for row in manifest["items"]:
        appid = row["appid"]
        assignment = v2.frozen_assignment(
            repo, marker_commit=marker, trial_id=trial_id, appid=appid,
        )
        candidate_path = v2._path("research", assignment)
        receipt_path = _receipt_path(assignment)

        if exists(repo, "HEAD", receipt_path):
            output.append({"appid": appid, "status": "existing_receipt_not_replayed"})
            continue
        try:
            introduction = single_introduction(repo, candidate_path)
            if introduction is None:
                output.append({"appid": appid, "status": "not_submitted"})
                continue
            plan = receipts.prepare_receipt(
                repo, marker_commit=marker, trial_id=trial_id, appid=appid,
                authorization_commit=authorization,
                introduction_commit=introduction,
            )
            if plan["receipt_path"] != receipt_path or exists(repo, "HEAD", receipt_path):
                raise ValueError("receipt target changed")
            target = repo / receipt_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(plan["receipt_bytes"])
            run(repo, "add", "--", receipt_path)
            run(repo, "diff", "--cached", "--check")
            run(repo, "-c", "user.name=github-actions[bot]",
                "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                "commit", "-m", "dossier notes v2: GitHub Research receipt " + appid)
            receipt_commit = run(repo, "rev-parse", "HEAD")
            if (require_only_new(repo, receipt_commit, [receipt_path])
                    != parent(repo, receipt_commit)
                    or blob(repo, receipt_commit, receipt_path)
                    != blob_for(plan["receipt_bytes"])):
                raise ValueError("GitHub-generated receipt not an original one-add")
            proven = receipts.inspect_receipt_commit(
                repo, marker_commit=marker, trial_id=trial_id, appid=appid,
                authorization_commit=authorization,
                introduction_commit=introduction,
                receipt_commit=receipt_commit,
            )
            if proven["receipt_blob_sha"] != plan["receipt_blob_sha"]:
                raise ValueError("receipt validation mismatch")
            output.append({"appid": appid, "status": plan["disposition"],
                           "candidate_commit": introduction,
                           "receipt_commit": receipt_commit})
        except (ValueError, v2.NotesV2Error) as exc:
            # Do not let one malformed candidate prevent independent siblings.
            if run(repo, "status", "--porcelain", "--untracked-files=all"):
                raise ValueError("uncommitted receipt residue after item error") from exc
            output.append({"appid": appid, "status": "item_blocked",
                           "reason": str(exc)[:200]})
    return {"trial_id": trial_id, "items": output,
            "receipts_created": sum(bool(x.get("receipt_commit")) for x in output),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "canonical_acceptance": False, "research_quality_audited": False}


def _remote_head(repo, branch):
    ref = "refs/heads/" + branch
    response = run(repo, "ls-remote", "--exit-code", "origin", ref)
    lines = response.splitlines()
    if len(lines) != 1 or not lines[0].endswith("\t" + ref):
        raise ValueError("sandbox Git remote ref missing or ambiguous")
    sha = lines[0].split("\t", 1)[0]
    if not SHA.fullmatch(sha):
        raise ValueError("invalid remote Git SHA")
    return sha


def _owner_action_gate(trial_id, env):
    if (env.get("GITHUB_ACTIONS") != "true"
            or env.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
            or env.get("GITHUB_REPOSITORY") != batch.REPOSITORY
            or env.get("GITHUB_REPOSITORY_OWNER_ID") != batch.OWNER_ID
            or env.get("GITHUB_ACTOR_ID") != batch.OWNER_ID
            or env.get("GITHUB_ACTOR") != batch.OWNER_LOGIN
            or env.get("GITHUB_TRIGGERING_ACTOR") != batch.OWNER_LOGIN
            or env.get("GITHUB_REF") != "refs/heads/main"
            or env.get("GITHUB_WORKFLOW_REF")
            != batch.REPOSITORY + "/" + WORKFLOW + "@refs/heads/main"
            or env.get("GITHUB_RUN_ATTEMPT") != "1"
            or not str(env.get("GITHUB_RUN_ID", "")).isdigit()):
        raise ValueError("only first-attempt owner manual GitHub Actions ingest is allowed")
    batch.paths(trial_id)


def _owner_push_candidate_gate(repo,trial_id,env):
    """An owner candidate create_file push can trigger only its EXACT one-add.

    The candidate event is an immutable Git ancestor; a later candidate or bot
    receipt may advance HEAD. All receipts are serialized and CAS at the newest
    checked-out sandbox tip. A stale ref is never overwritten/rebased.
    """
    branch=batch.paths(trial_id)["branch"]
    if trial_id!=batch.OWNER_PUSH_TRIAL:
        raise ValueError("auto receipt only for exact authorized rerun1")
    if not (env.get("GITHUB_ACTIONS")=="true"
            and env.get("GITHUB_EVENT_NAME")=="push"
            and env.get("GITHUB_REPOSITORY")==batch.REPOSITORY
            and env.get("GITHUB_REPOSITORY_OWNER_ID")==batch.OWNER_ID
            and env.get("GITHUB_ACTOR_ID")==batch.OWNER_ID
            and env.get("GITHUB_ACTOR")==batch.OWNER_LOGIN
            and env.get("GITHUB_TRIGGERING_ACTOR")==batch.OWNER_LOGIN
            and env.get("GITHUB_REF")=="refs/heads/"+branch
            and env.get("GITHUB_WORKFLOW_REF")==
                batch.REPOSITORY+"/"+AUTO_WORKFLOW+"@refs/heads/"+branch
            and env.get("GITHUB_RUN_ATTEMPT")=="1"
            and str(env.get("GITHUB_RUN_ID","")).isdigit()
            and int(env.get("GITHUB_RUN_ID","0"))>0):
        raise ValueError("not authenticated first-attempt owner sandbox candidate push")
    event_sha=env.get("GITHUB_SHA")
    event_file=env.get("GITHUB_EVENT_PATH")
    if not (isinstance(event_sha,str) and SHA.fullmatch(event_sha)
            and isinstance(event_file,str) and Path(event_file).is_file()):
        raise ValueError("candidate push SHA or GitHub payload missing")
    try:
        event=json.loads(Path(event_file).read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise ValueError("unparseable genuine candidate push event") from exc
    commits=run(repo,"rev-list","--parents","-n","1",event_sha).split()
    if len(commits)!=2 or commits[0]!=event_sha:
        raise ValueError("candidate must have one real first parent")
    if not (event.get("ref")=="refs/heads/"+branch
            and event.get("before")==commits[1]
            and event.get("after")==event_sha
            and event.get("created") is False
            and event.get("deleted") is False
            and event.get("forced") is False
            and isinstance(event.get("head_commit"),dict)
            and event["head_commit"].get("id")==event_sha
            and event.get("sender",{}).get("id")==int(batch.OWNER_ID)
            and event.get("repository",{}).get("full_name")==batch.REPOSITORY
            and event["repository"].get("owner",{}).get("id")==int(batch.OWNER_ID)):
        raise ValueError("candidate event origin is not proven")
    if not first_parent_contains(repo,event_sha,"HEAD"):
        raise ValueError("candidate push is not on current sandbox first-parent")
    from dossier_two_stage_staging import require_only_new
    changes=run(repo,"diff-tree","--no-commit-id","--name-status",
                "-r",commits[1],event_sha).splitlines()
    if len(changes)!=1 or not changes[0].startswith("A\t"):
        raise ValueError("push commit did not introduce exactly one new candidate")
    candidate=changes[0][2:]
    anchor=issuer_from_sandbox(repo,trial_id)
    manifest,_=v2._manifest(repo,anchor["marker_commit"],trial_id)
    expected=set()
    for item in manifest["items"]:
        assignment=v2.frozen_assignment(
            repo,marker_commit=anchor["marker_commit"],
            trial_id=trial_id,appid=item["appid"])
        expected.add(v2._path("research",assignment))
    if candidate not in expected:
        raise ValueError("new path is not one of the six frozen assignments")
    if (require_only_new(repo,event_sha,[candidate])!=commits[1]
            or single_introduction(repo,candidate)!=event_sha):
        raise ValueError("candidate added more than once or modified since source push")
    return candidate


def run_authorized(repo, trial_id, env):
    """Actual entry point: token and real GitHub Actions are mandatory."""
    started = time.monotonic()
    repo = Path(repo).resolve()
    if env.get("GITHUB_EVENT_NAME")=="push":
        _owner_push_candidate_gate(repo,trial_id,env)
    else:
        _owner_action_gate(trial_id,env)
    token = env.get("GITHUB_TOKEN")
    if not isinstance(token, str) or not token.strip():
        raise ValueError("authenticated GitHub token missing")
    expected_branch = batch.paths(trial_id)["branch"]
    head = run(repo, "rev-parse", "HEAD")
    if run(repo, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("dirty sandbox")
    if _remote_head(repo, expected_branch) != head:
        raise ValueError("sandbox remote moved before ingest")
    if receipts._github_tip(batch.REPOSITORY, expected_branch, token) != head:
        raise ValueError("GitHub authenticated sandbox HEAD mismatch")
    anchor = issuer_from_sandbox(repo, trial_id)
    batch.authenticated_owner_run(anchor, token, batch.REPOSITORY)
    result = ingest_local(repo, trial_id=trial_id, anchor=anchor)
    after = run(repo, "rev-parse", "HEAD")
    if result["receipts_created"]:
        if _remote_head(repo, expected_branch) != head:
            raise ValueError("sandbox moved; refusing receipt push")
        if receipts._github_tip(batch.REPOSITORY, expected_branch, token) != head:
            raise ValueError("authenticated sandbox moved; refusing receipt push")
        run(repo, "push", "origin", after + ":refs/heads/" + expected_branch)
        if (_remote_head(repo, expected_branch) != after
                or receipts._github_tip(batch.REPOSITORY, expected_branch, token) != after):
            raise ValueError("GitHub receipt push could not be confirmed")
    result.update({"head_before": head, "head_after": after,
                   "github_receipts_confirmed": bool(result["receipts_created"]),
                   "total_elapsed_seconds": round(time.monotonic() - started, 3)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--trial-id", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run_authorized(args.repo, args.trial_id, os.environ),
                         ensure_ascii=False, sort_keys=True))
    except (ValueError, OSError, RuntimeError, v2.NotesV2Error) as exc:
        parser.exit(2, "V2_RESEARCH_INGEST_REFUSED: " + str(exc) + "\n")


if __name__ == "__main__":
    main()

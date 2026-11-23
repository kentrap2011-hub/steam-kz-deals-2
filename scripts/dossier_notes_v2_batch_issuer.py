#!/usr/bin/env python3
"""Owner-controlled Notes V2 cohort issuer: manual or exact first owner main push.

Only separately validated owner GitHub Actions events create immutable Git commits.
No semantics, retries, production or arbitrary trial auto-launch.
"""
import argparse
import json
import os
import re
import secrets
import subprocess
from pathlib import Path

from dossier_two_stage_staging import (
    blob, file_at, first_parent_contains, git, json_at, parent, require_only_new,
)
import dossier_notes_v2_batch_route as batch
from dossier_research_notes_v2 import _marker_nonce

SHA=re.compile(r"^[0-9a-f]{40}$")
FREEZE_CONFIRM="FREEZE_DOSSIER_NOTES_V2_BATCH_ONCE:"
AUTH_CONFIRM="AUTHORIZE_DOSSIER_NOTES_V2_BATCH_ONCE:"


def execute(repo,*args):
    return git(repo,*args).stdout.decode().strip()


def remote(repo, ref):
    p=git(repo,"ls-remote","--exit-code","origin",ref,required=False)
    if p.returncode==2:
        return None
    batch.require(p.returncode==0,"remote lookup failed")
    lines=p.stdout.decode().strip().splitlines()
    batch.require(len(lines)==1 and lines[0].endswith("\t"+ref),
                  "remote ref ambiguous")
    return lines[0].split("\t")[0]


def guard(repo,mode,trial_id,sha,confirmation,env):
    batch.require(trial_id != batch.OWNER_PUSH_REPLAY_TRIAL3,
                  "rerun3 requires one owner-main-push issuer; manual issue refused")
    batch.paths(trial_id)  # canonical safe slug and no original18
    batch.require(isinstance(sha,str) and SHA.fullmatch(sha),
                  "current main SHA required")
    workflow=batch.ISSUE_WORKFLOW if mode=="freeze" else batch.AUTHORIZE_WORKFLOW
    required=(FREEZE_CONFIRM if mode=="freeze" else AUTH_CONFIRM)+trial_id
    batch.require(confirmation==required,"exact new owner batch confirmation absent")
    batch.require(
        env.get("GITHUB_ACTIONS")=="true"
        and env.get("GITHUB_EVENT_NAME")=="workflow_dispatch"
        and env.get("GITHUB_REPOSITORY")==batch.REPOSITORY
        and env.get("GITHUB_REPOSITORY_OWNER_ID")==batch.OWNER_ID
        and env.get("GITHUB_ACTOR_ID")==batch.OWNER_ID
        and env.get("GITHUB_ACTOR")==batch.OWNER_LOGIN
        and env.get("GITHUB_TRIGGERING_ACTOR")==batch.OWNER_LOGIN
        and env.get("GITHUB_REF")=="refs/heads/main"
        and env.get("GITHUB_WORKFLOW_REF")==
            batch.REPOSITORY+"/"+workflow+"@refs/heads/main"
        and env.get("GITHUB_SHA")==sha
        and env.get("GITHUB_RUN_ATTEMPT")=="1"
        and str(env.get("GITHUB_RUN_ID","")).isdigit()
        and int(env.get("GITHUB_RUN_ID","0"))>0,
        "only original first-attempt GitHub OWNER manual Actions dispatch")
    batch.require(execute(repo,"symbolic-ref","--short","HEAD")=="main"
                  and execute(repo,"rev-parse","HEAD")==sha
                  and remote(repo,"refs/heads/main")==sha,
                  "checkout/remote main SHA drift")
    origin=execute(repo,"remote","get-url","origin")
    batch.require(origin in {
        "https://github.com/"+batch.REPOSITORY,
        "https://github.com/"+batch.REPOSITORY+".git",
        "git@github.com:"+batch.REPOSITORY+".git",
        "git@github.com:"+batch.REPOSITORY,
        "ssh://git@github.com/"+batch.REPOSITORY+".git",
    }, "cannot issue on noncanonical GitHub remote")
    batch.require(not execute(repo,"status","--porcelain","--untracked-files=all"),
                  "dirty checkout cannot issue owner authority")
    c=batch.scope(repo,trial_id)
    batch.require(first_parent_contains(repo,c["provenance"]["main_commit"],sha),
                  "prepared source anchor not on current main first-parent")
    batch._base_contract_proof(repo,sha,trial_id)


def add_commit(repo,path,document,message):
    f=Path(repo)/path
    batch.require(not f.exists(),"create-only batch artifact already exists: "+path)
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_bytes(batch.canonical(document) if type(document) is dict else document)
    execute(repo,"add","--",path)
    execute(repo,"diff","--cached","--check")
    execute(repo,"-c","user.name=github-actions[bot]",
            "-c","user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit","-m",message)
    child=execute(repo,"rev-parse","HEAD")
    require_only_new(repo,child,[path])
    return child


def freeze(repo,expected,trial_id):
    path=batch.paths(trial_id)
    ref="refs/heads/"+path["branch"]
    batch.require(remote(repo,ref) is None,"batch branch already issued: one use only")
    c=batch.scope(repo,trial_id)
    blueprint=batch.manifest_blueprint(repo,trial_id)
    base=execute(repo,"rev-parse","HEAD")
    execute(repo,"checkout","-b",path["branch"])
    doc=batch.expected_grant(repo,trial_id,base)
    grant_commit=add_commit(repo,path["grant"],doc,"Grant isolated Notes V2 cohort only")
    manifest_commit=add_commit(repo,path["manifest"],blueprint["bytes"],
                               "Freeze GitHub-prepared V2 cohort assignments")
    nonce=secrets.token_hex(16)
    marker_commit=add_commit(repo,
        "data/control/dossier_notes_v2/run_starts/"+nonce+".json",
        {"schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
         "trial_id":trial_id,"nonce":nonce},
        "Freeze inactive one-use Notes V2 batch marker")
    batch.require(parent(repo,marker_commit)==manifest_commit
                  and parent(repo,manifest_commit)==grant_commit
                  and remote(repo,"refs/heads/main")==expected
                  and remote(repo,ref) is None,
                  "source/issuer drift before first push")
    execute(repo,"push","--porcelain","--force-with-lease="+ref+":",
            "origin","HEAD:"+ref)
    batch.require(remote(repo,ref)==marker_commit,"remote marker readback failed")
    execute(repo,"fetch","--no-tags","origin",ref)
    batch.require(execute(repo,"rev-parse","FETCH_HEAD")==marker_commit,
                  "marker fetch proof unavailable")
    return {"status":"batch_marker_issued_not_semantics",
            "trial_id":trial_id,"sandbox_branch":path["branch"],
            "grant_commit":grant_commit,"manifest_commit":manifest_commit,
            "marker_commit":marker_commit,"authorization_commit":None,
            "semantic_execution_authorized":False,
            "production_enabled":False,"canonical_acceptance":False}


def authorize(repo,expected,trial_id,marker_commit,env,authority_origin="manual"):
    batch.require(isinstance(marker_commit,str) and SHA.fullmatch(marker_commit)
                  and marker_commit not in batch.ORIGINAL_MARKERS,
                  "new marker SHA required")
    path=batch.paths(trial_id)
    ref="refs/heads/"+path["branch"]
    batch.require(remote(repo,ref)==marker_commit,
                  "sandbox not at original unconsumed marker")
    execute(repo,"fetch","--no-tags","origin",ref)
    batch.require(execute(repo,"rev-parse","FETCH_HEAD")==marker_commit,
                  "cannot independently fetch marker")
    manifest_commit=parent(repo,marker_commit)
    grant_commit=parent(repo,manifest_commit)
    base=parent(repo,grant_commit)
    batch.require(first_parent_contains(repo,base,expected)
                  and require_only_new(repo,grant_commit,[path["grant"]])==base
                  and require_only_new(repo,manifest_commit,[path["manifest"]])==grant_commit,
                  "manifest/grant chain or current main ancestry invalid")
    nonce=_marker_nonce(repo,marker_commit)
    marker_path="data/control/dossier_notes_v2/run_starts/"+nonce+".json"
    batch.require(require_only_new(repo,marker_commit,[marker_path])==manifest_commit
                  and json_at(repo,marker_commit,marker_path)=={
                      "schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
                      "trial_id":trial_id,"nonce":nonce,
                  }, "original marker not exact new cohort")
    # Directly compare against immutable main-held source before any auth commit.
    execute(repo,"checkout","--detach",marker_commit)
    batch.require(file_at(repo,manifest_commit,path["manifest"])==
                  batch.manifest_blueprint(repo,trial_id)["bytes"],
                  "manifest differs from prepared source")
    batch.require(json_at(repo,grant_commit,path["grant"])==
                  batch.expected_grant(repo,trial_id,base),
                  "immutable one-use owner grant differs")
    doc=batch.expected_authorization(repo,trial_id,marker_commit,
                                     grant_commit,env["GITHUB_RUN_ID"],authority_origin)
    auth_commit=add_commit(repo,path["authorization"],doc,
                           "Authorize one isolated Notes V2 batch pilot")
    anchor=batch.issuer_structure(
        repo,trial_id=trial_id,marker_commit=marker_commit,
        authorization_commit=auth_commit)
    batch.require(anchor["semantic_execution_authorized"]
                  and remote(repo,ref)==marker_commit
                  and remote(repo,"refs/heads/main")==expected,
                  "authorization Git source/lease drift")
    execute(repo,"push","--porcelain",
            "--force-with-lease="+ref+":"+marker_commit,
            "origin","HEAD:"+ref)
    batch.require(remote(repo,ref)==auth_commit,"authorization remote proof failed")
    execute(repo,"fetch","--no-tags","origin",ref)
    batch.require(execute(repo,"rev-parse","FETCH_HEAD")==auth_commit,
                  "authorization readback failed")
    return {"status":"batch_owner_authorization_written_not_semantic_execution",
            "trial_id":trial_id,"sandbox_branch":path["branch"],
            "marker_commit":marker_commit,"authorization_commit":auth_commit,
            "github_authorization_run_id":env["GITHUB_RUN_ID"],
            "authenticated_authorizer_run_completed":False,
            "semantic_execution_authorized":True,
            "canonical_acceptance":False,"production_enabled":False}


def guard_owner_push(repo,trial_id,sha,env):
    """Actual original owner main push must FIRST introduce the exact new cohort."""
    batch.require(trial_id in batch.OWNER_PUSH_TRIALS,
                  "push authorization is restricted to exact preapproved cohorts")
    batch.paths(trial_id)
    batch.require(isinstance(sha,str) and SHA.fullmatch(sha),
                  "exact main push SHA missing")
    batch.require(
        env.get("GITHUB_ACTIONS")=="true"
        and env.get("GITHUB_EVENT_NAME")=="push"
        and env.get("GITHUB_REPOSITORY")==batch.REPOSITORY
        and env.get("GITHUB_REPOSITORY_OWNER_ID")==batch.OWNER_ID
        and env.get("GITHUB_ACTOR_ID")==batch.OWNER_ID
        and env.get("GITHUB_ACTOR")==batch.OWNER_LOGIN
        and env.get("GITHUB_TRIGGERING_ACTOR")==batch.OWNER_LOGIN
        and env.get("GITHUB_REF")=="refs/heads/main"
        and env.get("GITHUB_WORKFLOW_REF")==
            batch.REPOSITORY+"/"+batch.owner_push_workflow(trial_id)+"@refs/heads/main"
        and env.get("GITHUB_SHA")==sha
        and env.get("GITHUB_RUN_ATTEMPT")=="1"
        and str(env.get("GITHUB_RUN_ID","")).isdigit()
        and int(env.get("GITHUB_RUN_ID","0"))>0,
        "not first-attempt owner-authenticated source push")
    event_path=env.get("GITHUB_EVENT_PATH")
    batch.require(isinstance(event_path,str) and Path(event_path).is_file(),
                  "actual GitHub push event payload missing")
    try:
        event=json.loads(Path(event_path).read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise ValueError("invalid owner push event") from exc
    parents=execute(repo,"rev-list","--parents","-n","1",sha).split()
    batch.require(len(parents)>=2 and parents[0]==sha,
                  "source main push has no real parent")
    before=parents[1]
    batch.require(
        event.get("ref")=="refs/heads/main"
        and event.get("before")==before and event.get("after")==sha
        and event.get("created") is False and event.get("deleted") is False
        and event.get("forced") is False
        and isinstance(event.get("head_commit"),dict)
        and event["head_commit"].get("id")==sha
        and event.get("sender",{}).get("id")==int(batch.OWNER_ID)
        and event.get("repository",{}).get("full_name")==batch.REPOSITORY
        and event["repository"].get("owner",{}).get("id")==int(batch.OWNER_ID),
        "not the actual owner first-parent GitHub main push")
    source=batch.paths(trial_id)["contract"]
    batch.require(
        execute(repo,"diff-tree","--no-commit-id","--name-status","-r",
                before,sha,"--",source)=="A\t"+source
        and execute(repo,"symbolic-ref","--short","HEAD")=="main"
        and execute(repo,"rev-parse","HEAD")==sha
        and remote(repo,"refs/heads/main")==sha
        and not execute(repo,"status","--porcelain","--untracked-files=all"),
        "new source not introduced once at the actual main SHA")
    batch.require(execute(repo,"remote","get-url","origin") in {
        "https://github.com/"+batch.REPOSITORY,
        "https://github.com/"+batch.REPOSITORY+".git",
        "git@github.com:"+batch.REPOSITORY,
        "git@github.com:"+batch.REPOSITORY+".git",
        "ssh://git@github.com/"+batch.REPOSITORY+".git",
    }, "noncanonical origin")
    scope=batch.scope(repo,trial_id)
    batch.require(scope["provenance"]["prepared_for_date"]=="2026-11-11"
                  and first_parent_contains(repo,scope["provenance"]["main_commit"],sha),
                  "historical immutable source anchor is not proven")
    batch._base_contract_proof(repo,sha,trial_id)
    batch.require(remote(repo,"refs/heads/"+batch.paths(trial_id)["branch"]) is None,
                  "one-use trial branch already exists")


def owner_push_launch(repo,trial_id,sha,env):
    guard_owner_push(repo,trial_id,sha,env)
    frozen=freeze(repo,sha,trial_id)
    execute(repo,"checkout","main")
    batch.require(execute(repo,"rev-parse","HEAD")==sha
                  and remote(repo,"refs/heads/main")==sha,
                  "source main moved before separate authorization commit")
    granted=authorize(repo,sha,trial_id,frozen["marker_commit"],env,
                      authority_origin="owner_main_push")
    replay = {}
    if trial_id in (batch.OWNER_PUSH_REPLAY_TRIAL, batch.OWNER_PUSH_REPLAY_TRIAL3):
        # The same one-use authenticated owner run can copy the old immutable
        # Research content. It must never generate new semantic Research.
        from dossier_notes_v2_assembly_replay_seed import seed
        replay = {"research_replay": seed(
            repo, trial_id=trial_id, marker_commit=frozen["marker_commit"],
            authorization_commit=granted["authorization_commit"])}
    return {"source_main_sha":sha,"owner_action_run_id":env["GITHUB_RUN_ID"],
            "grant_commit":frozen["grant_commit"],
            "manifest_commit":frozen["manifest_commit"],**granted,**replay}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=["freeze","authorize","owner-push-launch"])
    parser.add_argument("--trial-id",required=True)
    parser.add_argument("--expected-main-sha",required=True)
    parser.add_argument("--marker-commit")
    parser.add_argument("--confirmation")
    args=parser.parse_args()
    try:
        repo=Path.cwd()
        if args.mode=="owner-push-launch":
            doc=owner_push_launch(repo,args.trial_id,args.expected_main_sha,os.environ)
        else:
            guard(repo,args.mode,args.trial_id,args.expected_main_sha,
                  args.confirmation,os.environ)
            doc=(freeze(repo,args.expected_main_sha,args.trial_id) if args.mode=="freeze"
                 else authorize(repo,args.expected_main_sha,args.trial_id,
                                args.marker_commit,os.environ))
        print(json.dumps(doc,sort_keys=True))
    except (ValueError,OSError,KeyError,subprocess.CalledProcessError) as exc:
        parser.exit(2,"DOSSIER_V2_BATCH_ISSUER_REFUSED: "+str(exc)+"\n")


if __name__=="__main__":
    main()

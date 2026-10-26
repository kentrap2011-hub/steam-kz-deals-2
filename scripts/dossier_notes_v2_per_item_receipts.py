#!/usr/bin/env python3
"""Inactive Notes V2 per-item Research transport and receipt validation.

The optional, explicitly invoked single-item Git writer uses the existing Git
transport; it never runs semantics, schedules work or accepts final Dossier.
Authenticated GitHub REST read-back is required for a GitHub receipt claim.
A V2 issuer commit alone expressly does NOT authorize Research semantics.
"""
import base64
import json
import re
import tempfile
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import (
    blob, blob_for, exists, file_at, first_parent_contains, git, parent,
    require_only_new, strict_json,
)

H40 = re.compile(r"^[0-9a-f]{40}$")
ISSUER_SCHEMA = "DOSSIER-NOTES-V2-MANUAL-RESEARCH-ISSUER-AUTHORIZATION"


def _sha(value, label):
    if not isinstance(value, str) or not H40.fullmatch(value):
        v2.reject("wrong_binding", "invalid " + label)
    return value


def issuer_structure(repo, *, marker_commit, trial_id, authorization_commit):
    """Check immutable local Git shape, NOT genuine user or GitHub run consent.

    The exact independent issuer #266 evidence must additionally be checked
    against authenticated GitHub Actions and a separately approved semantic
    permission by the future GitHub-controlled writer.
    """
    _sha(marker_commit, "V2 marker")
    _sha(authorization_commit, "V2 issuer")
    c = v2._contract()  # remains inactive
    assignment_manifest, manifest_sha = v2._manifest(repo, marker_commit, trial_id)
    if authorization_commit == marker_commit or authorization_commit in (
            c["immutable_original_pins"]["research_marker"],
            c["immutable_original_pins"]["research_authorization"]):
        v2.reject("wrong_binding", "historical or reused authorization is forbidden")
    path = "data/control/dossier_notes_v2/authorizations/" + trial_id + ".json"
    issuer_parent = require_only_new(repo, authorization_commit, [path])
    if issuer_parent != marker_commit or not first_parent_contains(
            repo, authorization_commit, "HEAD"):
        v2.reject("broken_git_provenance", "issuer is not direct child of V2 marker on HEAD")
    v2._assert_unchanged_since(repo, authorization_commit, path)
    if blob(repo, "HEAD", path) != blob(repo, authorization_commit, path):
        v2.reject("broken_git_provenance", "issuer was overwritten")
    record = strict_json(file_at(repo, authorization_commit, path))
    marker_parent = parent(repo, marker_commit)
    grant_commit = record.get("human_grant_commit") if isinstance(record, dict) else None
    grant_path = "config/dossier_notes_v2_issuer_human_grant.json"
    _sha(grant_commit, "immutable human grant")
    grant_record = strict_json(file_at(repo, grant_commit, grant_path))
    pilot = c.get("original18_trial_scoped_authorization") or {}
    scoped = (
        pilot.get("enabled") is True
        and grant_record.get("semantic_execution_approved") is True
        and grant_commit == parent(repo, marker_parent)
        and record.get("github_actor_id") == pilot.get("github_owner_actor_id")
        and grant_record.get("github_actor_id") == pilot.get("github_owner_actor_id")
        and pilot.get("isolated_sandbox_only") is True
        and pilot.get("canonical_ingest") is False
        and pilot.get("production") is False
    )
    nonce = v2._marker_nonce(repo, marker_commit)
    required = {
        "schema": ISSUER_SCHEMA,
        "schema_version": 2,
        "trial_id": trial_id,
        "marker_commit": marker_commit,
        "marker_parent": marker_parent,
        "marker_nonce": nonce,
        "manifest_path": "data/control/dossier_notes_v2/manifests/" + trial_id + ".json",
        "manifest_blob_sha": manifest_sha,
        "original_pins": c["immutable_original_pins"],
        "original_buffer_blob_sha": c["original_research_identity_authority"]["original_buffer_git_blob_sha"],
        "mode": ("original18_scoped_nonproduction_semantic_trial" if scoped
                 else "original18_inactive_V2_control_plane_issuance_only"),
        "semantic_execution_authorized": scoped,
        "canonical_acceptance": False,
        "assembly_authorized": scoped,
        "production_authorized": False,
    }
    extra = {
        "human_grant_commit", "human_grant_blob_sha",
        "v2_contract_blob_sha", "v2_research_guard_blob_sha",
        "github_actor_id", "github_authorization_run_id",
    }
    if (not isinstance(record, dict)
            or set(record) != set(required) | extra
            or any(record.get(k) != val for k, val in required.items())):
        v2.reject("wrong_binding", "V2 issuer document disagrees with frozen marker/manifest")
    for key in ("human_grant_commit", "human_grant_blob_sha",
                "v2_contract_blob_sha", "v2_research_guard_blob_sha"):
        _sha(record.get(key), key)
    if not all(isinstance(record.get(key), str) and record[key].isdigit()
               for key in ("github_actor_id", "github_authorization_run_id")):
        v2.reject("wrong_binding", "issuer actor/run identity is malformed")
    grant_commit = record["human_grant_commit"]
    if not first_parent_contains(repo, grant_commit, marker_parent):
        v2.reject("wrong_binding", "issuer grant is not an ancestor of marker parent")
    require_only_new(repo, grant_commit, [grant_path])
    v2._assert_unchanged_since(repo, grant_commit, grant_path)
    if (blob(repo, grant_commit, grant_path) != record["human_grant_blob_sha"]
            or blob(repo, marker_parent, grant_path) != record["human_grant_blob_sha"]):
        v2.reject("broken_git_provenance", "V2 grant blob is not preserved")
    grant = strict_json(file_at(repo, grant_commit, grant_path))
    expected_grant = {
        "schema": "DOSSIER-NOTES-V2-MANUAL-ISSUER-HUMAN-GRANT",
        "schema_version": 2, "trial_id": trial_id,
        "original_buffer_blob_sha": required["original_buffer_blob_sha"],
        "original_pins": c["immutable_original_pins"],
        "original_groups": c["original_groups"],
        "github_actor_id": record["github_actor_id"],
        "scope": "issue_single_original18_V2_manifest_marker_then_separate_authorization_only",
        "semantic_execution_approved": scoped, "production_approved": False,
    }
    if grant != expected_grant:
        v2.reject("wrong_binding", "issuer does not refer to an exact scoped structural grant")
    # Exact source guards belong to the same GitHub-side issuer, not a worker claim.
    for key, source_path in (
            ("v2_contract_blob_sha", "config/dossier_research_notes_v2_contract.json"),
            ("v2_research_guard_blob_sha", "scripts/dossier_research_notes_v2.py")):
        if blob(repo, marker_parent, source_path) != record[key]:
            v2.reject("wrong_binding", "issuer source pin differs from actual marker parent")
    if assignment_manifest["items"] != v2._original_rows():
        v2.reject("wrong_binding", "issuer no longer scopes exact original eighteen")
    return {
        "trial_id": trial_id, "marker_commit": marker_commit,
        "marker_parent": marker_parent, "marker_nonce": nonce,
        "manifest_blob_sha": manifest_sha,
        "authorization_commit": authorization_commit,
        "authorization_blob_sha": blob(repo, authorization_commit, path),
        "human_grant_commit": record["human_grant_commit"],
        "github_actor_id": record["github_actor_id"],
        "github_authorization_run_id": record["github_authorization_run_id"],
        "issuer_structural_only": True,
        "semantic_execution_authorized": scoped,
        "github_run_authenticated": False,
    }


def prepare_candidate(repo, *, marker_commit, trial_id, appid,
                      authorization_commit, document):
    """Pure strict one-item V2 submission plan; never publish it from this API."""
    anchor = issuer_structure(repo, marker_commit=marker_commit,
                              trial_id=trial_id, authorization_commit=authorization_commit)
    prepared = v2.prepare_research(repo, marker_commit=marker_commit,
                                   trial_id=trial_id, appid=appid, document=document)
    return {
        **prepared, "issuer": anchor, "candidate_transport_only": True,
        "github_receipt_confirmed": False, "semantic_execution_authorized": False,
        "attempt_state": "unknown",
    }


def inspect_candidate(repo, *, marker_commit, trial_id, appid,
                      authorization_commit, introduction_commit):
    """Local Git/semantic-safe transport classification, not GitHub acceptance."""
    anchor = issuer_structure(repo, marker_commit=marker_commit,
                              trial_id=trial_id, authorization_commit=authorization_commit)
    if introduction_commit is not None:
        _sha(introduction_commit, "candidate introduction")
        if not first_parent_contains(repo, authorization_commit, introduction_commit):
            v2.reject("broken_git_provenance", "candidate predates distinct issuer")
    result = v2.classify_research(repo, marker_commit=marker_commit,
                                  trial_id=trial_id, appid=appid,
                                  introduction_commit=introduction_commit)
    return {
        **result, "issuer": anchor, "transport_technically_verified":
        result["status"] == "safe_incomplete_research",
        "github_receipt_confirmed": False, "semantic_quality_accepted": False,
        "canonical_acceptance": False, "attempt_state": "unknown",
    }


def _receipt(repo, *, marker_commit, trial_id, appid,
             authorization_commit, introduction_commit, receipt_parent):
    anchor = issuer_structure(repo, marker_commit=marker_commit,
                              trial_id=trial_id, authorization_commit=authorization_commit)
    if receipt_parent is None or not first_parent_contains(repo, authorization_commit, receipt_parent):
        v2.reject("broken_git_provenance", "receipt parent is outside issuer ancestry")
    if introduction_commit is not None and not first_parent_contains(
            repo, introduction_commit, receipt_parent):
        v2.reject("broken_git_provenance", "receipt cannot predate its candidate introduction")
    outcome = inspect_candidate(repo, marker_commit=marker_commit, trial_id=trial_id,
                                appid=appid, authorization_commit=authorization_commit,
                                introduction_commit=introduction_commit)
    disposition = outcome["status"]
    if disposition not in v2._contract()["receipts"]:
        v2.reject("wrong_binding", "unexpected Research classification")
    source = {
        "issuer": anchor, "receipt_parent_commit": receipt_parent,
        "introduction_commit": introduction_commit,
        "candidate_status": disposition,
        "transport_technically_verified": outcome["transport_technically_verified"],
        "github_receipt_confirmed": False,
    }
    if outcome["transport_technically_verified"]:
        source["candidate"] = {
            "path": outcome["research_package_path"],
            "commit": outcome["research_package_git_commit"],
            "blob_sha": outcome["research_package_blob_sha"],
            "raw_sha256": outcome["research_package_raw_sha256"],
            "canonical_sha256": outcome["research_package_sha256"],
        }
    doc = v2.item_receipt_blueprint(
        repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid,
        phase="research", disposition=disposition, source=source)
    a = doc["assignment"]
    path = ("data/control/dossier_notes_v2/receipts/" + trial_id
            + "/g%06d/" % a["group_sequence"] + a["appid"]
            + "--" + a["assignment_id"] + "--research.json")
    raw = v2._canonical(doc)
    return {
        "status": "offline_receipt_proposal_not_github_confirmation",
        "disposition": disposition,
        "receipt_path": path, "receipt_bytes": raw,
        "receipt_blob_sha": blob_for(raw), "receipt_raw_sha256": v2.digest(raw),
        "technical_acceptance_proposed": disposition == "safe_incomplete_research",
        "semantic_quality_accepted": False, "canonical_acceptance": False,
        "github_receipt_confirmed": False, "attempt_state": "unknown",
    }


def prepare_receipt(repo, *, marker_commit, trial_id, appid,
                    authorization_commit, introduction_commit):
    """One fixed create-only receipt path even for refusal/missing transport."""
    if exists(repo, "HEAD", "data/control/dossier_notes_v2/receipts/" + trial_id
              + "/g%06d/" % v2.frozen_assignment(
                  repo, marker_commit=marker_commit, trial_id=trial_id,
                  appid=appid)["group_sequence"]
              + str(appid) + "--" + v2.frozen_assignment(
                  repo, marker_commit=marker_commit, trial_id=trial_id,
                  appid=appid)["assignment_id"] + "--research.json"):
        v2.reject("broken_git_provenance", "one-item-once receipt already exists")
    return _receipt(repo, marker_commit=marker_commit, trial_id=trial_id,
                    appid=appid, authorization_commit=authorization_commit,
                    introduction_commit=introduction_commit,
                    receipt_parent=git(repo, "rev-parse", "HEAD").stdout.decode().strip())


def inspect_receipt_commit(repo, *, marker_commit, trial_id, appid,
                           authorization_commit, introduction_commit, receipt_commit):
    """Verify exact local one-add immutable Git bytes; remote success is NOT inferred."""
    _sha(receipt_commit, "receipt commit")
    if not first_parent_contains(repo, receipt_commit, "HEAD"):
        v2.reject("broken_git_provenance", "receipt not on current first-parent Git history")
    a = v2.frozen_assignment(repo, marker_commit=marker_commit, trial_id=trial_id,
                             appid=appid)
    path = ("data/control/dossier_notes_v2/receipts/" + trial_id
            + "/g%06d/" % a["group_sequence"] + a["appid"]
            + "--" + a["assignment_id"] + "--research.json")
    p = require_only_new(repo, receipt_commit, [path])
    expected = _receipt(repo, marker_commit=marker_commit, trial_id=trial_id,
                        appid=appid, authorization_commit=authorization_commit,
                        introduction_commit=introduction_commit, receipt_parent=p)
    raw = file_at(repo, receipt_commit, path)
    if raw != expected["receipt_bytes"] or blob(repo, receipt_commit, path) != expected["receipt_blob_sha"]:
        v2.reject("broken_git_provenance", "immutable receipt bytes/provenance do not match")
    if blob(repo, "HEAD", path) != expected["receipt_blob_sha"] or file_at(repo, "HEAD", path) != raw:
        v2.reject("broken_git_provenance", "receipt overwritten after introduction")
    v2._assert_unchanged_since(repo, receipt_commit, path)
    return {**expected, "status": "local_git_receipt_proved_remote_unconfirmed",
            "receipt_commit": receipt_commit, "github_receipt_confirmed": False}


# This is a transport primitive, not an executor or a second acceptance path.
# The caller/GitHub owner must separately authorize the invocation and its
# immutable trial; a structurally valid inactive issuer grants NO semantics.
def _remote_tip(repo, branch):
    if (not isinstance(branch, str) or not branch.startswith("sandbox/")
            or git(repo, "check-ref-format", "--branch", branch,
                   required=False).returncode):
        v2.reject("wrong_binding", "expected explicitly selected nonproduction sandbox branch")
    ref = "refs/heads/" + branch
    result = git(repo, "ls-remote", "--exit-code", "origin", ref,
                 required=False)
    if result.returncode:
        v2.reject("broken_git_provenance", "cannot read the authoritative remote branch")
    entries = result.stdout.decode("ascii").strip().splitlines()
    if len(entries) != 1 or entries[0].split("\t")[-1] != ref:
        v2.reject("broken_git_provenance", "ambiguous remote branch")
    return _sha(entries[0].split("\t")[0], "remote branch tip")


def _github_get(repository, endpoint, token):
    """Authenticated official GitHub REST GET, with no retry or write side effects."""
    url = "https://api.github.com/repos/" + repository + "/" + endpoint
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token,
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urlopen(request, timeout=20) as response:
            if response.status != 200:
                v2.reject("broken_git_provenance", "GitHub returned non-200 on read-back")
            return json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        v2.reject("broken_git_provenance", "authenticated GitHub read-back failed: "
                  + type(exc).__name__)


def _github_tip(repository, branch, token):
    obj = _github_get(repository, "git/ref/heads/" + quote(branch, safe="/"), token)
    sha = obj.get("object", {}).get("sha") if isinstance(obj, dict) else None
    return _sha(sha, "authenticated GitHub branch ref")


def _github_preflight(repo, branch, expected_head, repository, token):
    url = git(repo, "remote", "get-url", "origin").stdout.decode().strip()
    if token is None and repository is None:
        # Only a disposable local bare repository may skip GitHub authority.
        # In particular never push to GitHub over configured Git credentials
        # while omitting authenticated GitHub read-back.
        if not Path(url).is_absolute():
            v2.reject("wrong_binding", "remote publication requires authenticated GitHub")
        return False
    if (not isinstance(token, str) or not token.strip()
            or repository != "kentrap2011-hub/steam-kz-deals-2"):
        v2.reject("wrong_binding", "GitHub confirmation requires exact repository and token")
    expected_urls = {
        "https://github.com/" + repository,
        "https://github.com/" + repository + ".git",
        "git@github.com:" + repository + ".git",
        "git@github.com:" + repository,
        "ssh://git@github.com/" + repository + ".git",
    }
    if url not in expected_urls:
        v2.reject("wrong_binding", "origin does not point to the exact GitHub repository")
    if _github_tip(repository, branch, token) != expected_head:
        v2.reject("broken_git_provenance", "GitHub ref moved before publication")
    return True


def _single_remote_add(repo, *, branch, expected_remote_head, make_plan,
                       check_commit, message, github_repository=None,
                       github_token=None):
    """One clean temporary Git worktree, one create-only commit, one non-force push.

    No retries: a failed/ambiguous push or read-back MUST NOT become success.
    Git first-parent + exact bytes are checked again against freshly fetched
    remote objects, and optionally against authenticated GitHub REST.
    """
    expected_remote_head = _sha(expected_remote_head, "expected remote parent")
    current = _remote_tip(repo, branch)
    if current != expected_remote_head:
        v2.reject("broken_git_provenance", "remote branch changed; no write attempted")
    authenticated = _github_preflight(repo, branch, current,
                                       github_repository, github_token)
    git(repo, "fetch", "--no-tags", "origin", "refs/heads/" + branch)
    fetched = git(repo, "rev-parse", "FETCH_HEAD").stdout.decode().strip()
    if fetched != current:
        v2.reject("broken_git_provenance", "remote changed during fetch")
    with tempfile.TemporaryDirectory(prefix="notes-v2-single-add-") as d:
        work = Path(d) / "checkout"
        git(repo, "worktree", "add", "--detach", str(work), fetched)
        try:
            if git(work, "status", "--porcelain", "--untracked-files=all").stdout.strip():
                v2.reject("broken_git_provenance", "temporary Git worktree is not clean")
            plan = make_plan(work)
            path = plan.get("output_path") or plan.get("receipt_path")
            raw = plan.get("bytes") if "bytes" in plan else plan.get("receipt_bytes")
            if (not isinstance(path, str) or not isinstance(raw, bytes)
                    or not raw or exists(work, "HEAD", path)):
                v2.reject("broken_git_provenance", "invalid, empty or duplicate create-only artifact")
            target = work / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            git(work, "add", "--", path)
            git(work, "commit", "-m", message)
            commit_sha = git(work, "rev-parse", "HEAD").stdout.decode().strip()
            if (parent(work, commit_sha) != fetched
                    or require_only_new(work, commit_sha, [path]) != fetched
                    or blob(work, commit_sha, path) != blob_for(raw)):
                v2.reject("broken_git_provenance", "new Git commit is not exact one-add")
            check_commit(work, commit_sha, plan)
            if _remote_tip(repo, branch) != fetched:
                v2.reject("broken_git_provenance", "remote branch changed before push")
            if authenticated and _github_tip(github_repository, branch, github_token) != fetched:
                v2.reject("broken_git_provenance", "authenticated GitHub ref moved before push")
            # Ordinary non-force push is a server-enforced fast-forward check.
            # On concurrent writers the loser cannot replace the winner.
            push = git(repo, "push", "--porcelain", "origin",
                       commit_sha + ":refs/heads/" + branch, required=False)
            if push.returncode:
                v2.reject("broken_git_provenance", "Git remote rejected or did not confirm push")
            if _remote_tip(repo, branch) != commit_sha:
                v2.reject("broken_git_provenance", "remote did not retain exact new commit")
            git(repo, "fetch", "--no-tags", "origin", "refs/heads/" + branch)
            if git(repo, "rev-parse", "FETCH_HEAD").stdout.decode().strip() != commit_sha:
                v2.reject("broken_git_provenance", "remote fetch does not confirm new commit")
            if (parent(repo, commit_sha) != fetched
                    or require_only_new(repo, commit_sha, [path]) != fetched
                    or file_at(repo, commit_sha, path) != raw
                    or blob(repo, commit_sha, path) != blob_for(raw)):
                v2.reject("broken_git_provenance", "remote Git bytes or ancestry differ")
            if authenticated:
                if _github_tip(github_repository, branch, github_token) != commit_sha:
                    v2.reject("broken_git_provenance", "authenticated GitHub ref differs")
                doc = _github_get(github_repository,
                                  "contents/" + quote(path, safe="/") +
                                  "?ref=" + commit_sha, github_token)
                try:
                    body = base64.b64decode(doc["content"], validate=False)
                    valid = (doc["sha"] == blob_for(raw)
                             and doc["encoding"] == "base64" and body == raw)
                except (ValueError, KeyError, TypeError):
                    valid = False
                if not valid or _github_tip(github_repository, branch, github_token) != commit_sha:
                    v2.reject("broken_git_provenance", "GitHub ref or content read-back mismatch")
            if _remote_tip(repo, branch) != commit_sha:
                v2.reject("broken_git_provenance", "remote ref changed after read-back")
            return {
                **{k: val for k, val in plan.items() if k not in ("bytes", "receipt_bytes")},
                "remote_branch": branch, "remote_parent_commit": fetched,
                "remote_commit": commit_sha, "remote_path": path,
                "remote_git_confirmed": True,
                "github_candidate_confirmed": False,
                "github_receipt_confirmed": False,
                "authenticated_github_readback": authenticated,
                "semantic_quality_accepted": False, "canonical_acceptance": False,
            }
        finally:
            git(repo, "worktree", "remove", "--force", str(work), required=False)


def verify_scoped_semantic_run(repo, *, marker_commit, trial_id,
                               authorization_commit, github_repository, github_token):
    """Authenticate exact original18 owner Actions authorizer before ANY semantic push.

    The inert historical fixture does not authorize semantics or claim GitHub
    confirmation; its disposable bare Git regression remains operational.
    """
    anchor = issuer_structure(repo, marker_commit=marker_commit, trial_id=trial_id,
                              authorization_commit=authorization_commit)
    if not anchor["semantic_execution_authorized"]:
        return anchor
    config = v2._contract()
    pilot = config.get("original18_trial_scoped_authorization") or {}
    if (github_repository != "kentrap2011-hub/steam-kz-deals-2"
            or not isinstance(github_token, str) or not github_token.strip()
            or pilot.get("enabled") is not True):
        v2.reject("wrong_binding", "scoped original18 semantic transport needs authenticated GitHub")
    run_id = anchor["github_authorization_run_id"]
    observed = _github_get(github_repository, "actions/runs/" + run_id, github_token)
    if (observed.get("id") != int(run_id)
            or observed.get("event") != "workflow_dispatch"
            or observed.get("head_branch") != "main"
            or observed.get("status") != "completed"
            or observed.get("conclusion") != "success"
            or observed.get("run_attempt") != 1
            or observed.get("path") != config["manual_v2_issuer"]["workflow_authorize"]
            or observed.get("actor", {}).get("id") != int(pilot["github_owner_actor_id"])
            or observed.get("actor", {}).get("login") != pilot["github_owner_login"]):
        v2.reject("wrong_binding", "original18 real owner GitHub Actions authorization not confirmed")
    return {**anchor, "github_run_authenticated": True}


def publish_candidate_remote(repo, *, branch, expected_remote_head,
                             marker_commit, trial_id, appid,
                             authorization_commit, document,
                             github_repository=None, github_token=None):
    """Publish ONE preexisting semantic document; never generate Research."""
    verify_scoped_semantic_run(
        repo, marker_commit=marker_commit, trial_id=trial_id,
        authorization_commit=authorization_commit,
        github_repository=github_repository, github_token=github_token)
    def plan(work):
        return prepare_candidate(work, marker_commit=marker_commit, trial_id=trial_id,
                                 appid=appid, authorization_commit=authorization_commit,
                                 document=document)

    def inspect(work, commit_sha, planned):
        proof = inspect_candidate(work, marker_commit=marker_commit, trial_id=trial_id,
                                  appid=appid, authorization_commit=authorization_commit,
                                  introduction_commit=commit_sha)
        if (not proof["transport_technically_verified"]
                or proof["research_package_blob_sha"] != planned["blob_sha"]):
            v2.reject("broken_git_provenance", "new candidate failed existing validator")

    result = _single_remote_add(
        repo, branch=branch, expected_remote_head=expected_remote_head,
        make_plan=plan, check_commit=inspect,
        message="dossier notes v2: create-only Research item " + str(appid),
        github_repository=github_repository, github_token=github_token)
    result["status"] = ("github_candidate_confirmed" if result["authenticated_github_readback"]
                        else "disposable_remote_candidate_only")
    result["github_candidate_confirmed"] = result["authenticated_github_readback"]
    return result


def publish_receipt_remote(repo, *, branch, expected_remote_head,
                           marker_commit, trial_id, appid,
                           authorization_commit, introduction_commit,
                           github_repository=None, github_token=None):
    """Publish ONE typed receipt after candidate introduction is on remote."""
    _sha(introduction_commit, "candidate introduction")
    def plan(work):
        proof = inspect_candidate(work, marker_commit=marker_commit, trial_id=trial_id,
                                  appid=appid, authorization_commit=authorization_commit,
                                  introduction_commit=introduction_commit)
        if not proof["transport_technically_verified"]:
            v2.reject("broken_git_provenance", "candidate not verified on authoritative remote")
        return prepare_receipt(work, marker_commit=marker_commit, trial_id=trial_id,
                               appid=appid, authorization_commit=authorization_commit,
                               introduction_commit=introduction_commit)

    def inspect(work, commit_sha, planned):
        proof = inspect_receipt_commit(work, marker_commit=marker_commit, trial_id=trial_id,
                                       appid=appid, authorization_commit=authorization_commit,
                                       introduction_commit=introduction_commit,
                                       receipt_commit=commit_sha)
        if proof["receipt_blob_sha"] != planned["receipt_blob_sha"]:
            v2.reject("broken_git_provenance", "new receipt failed existing validator")

    result = _single_remote_add(
        repo, branch=branch, expected_remote_head=expected_remote_head,
        make_plan=plan, check_commit=inspect,
        message="dossier notes v2: create-only Research receipt " + str(appid),
        github_repository=github_repository, github_token=github_token)
    result["status"] = ("github_receipt_confirmed" if result["authenticated_github_readback"]
                        else "disposable_remote_receipt_only")
    result["github_receipt_confirmed"] = result["authenticated_github_readback"]
    return result

def publish_assembly_item_remote(repo, *, branch, expected_remote_head,
                                 marker_commit, trial_id, appid,
                                 authorization_commit, research_commit, document,
                                 github_repository=None, github_token=None):
    """Create-only second-stage result using the SAME checked remote Git lease.

    The original Notes introduction must exist in the frozen issuer descendant
    chain. A typed terminal Assembly result is valid transport, NOT acceptance.
    Each item is independent; no scheduler, retry or final writer is invoked.
    """
    _sha(research_commit, "original Research introduction")
    verify_scoped_semantic_run(
        repo, marker_commit=marker_commit, trial_id=trial_id,
        authorization_commit=authorization_commit,
        github_repository=github_repository, github_token=github_token)
    def plan(work_repo):
        issuer_structure(work_repo, marker_commit=marker_commit,
                         trial_id=trial_id,
                         authorization_commit=authorization_commit)
        if not first_parent_contains(work_repo, authorization_commit, research_commit):
            v2.reject("wrong_binding", "Research introduction predates the exact V2 issuer")
        work = v2.assembly_work(
            work_repo, marker_commit=marker_commit, trial_id=trial_id,
            appid=appid, research_commit=research_commit)
        return v2.prepare_assembly_transport(work_repo, work, document)

    def inspect(work_repo, commit_sha, planned):
        checked = v2.inspect_assembly(
            work_repo, marker_commit=marker_commit, trial_id=trial_id,
            appid=appid, research_commit=research_commit, result_commit=commit_sha)
        if checked["status"] not in (
            "strict_item_valid_pending_existing_atomic_group_ingest",
            "assembly_missing_evidence", "assembly_semantic_conflict",
            "runtime_or_tool_interrupted", "assembly_technical_error",
        ):
            v2.reject("broken_git_provenance", "Assembly candidate failed V2 strict transport: "
                      + str(checked["status"]))
        if blob(work_repo, commit_sha, planned["output_path"]) != planned["blob_sha"]:
            v2.reject("broken_git_provenance", "Assembly published blob differs from proposal")

    result = _single_remote_add(
        repo, branch=branch, expected_remote_head=expected_remote_head,
        make_plan=plan, check_commit=inspect,
        message="dossier notes v2: create-only independent Assembly item " + str(appid),
        github_repository=github_repository, github_token=github_token)
    result["status"] = ("github_assembly_transport_confirmed"
                        if result["authenticated_github_readback"]
                        else "disposable_remote_assembly_only")
    result["github_assembly_transport_confirmed"] = result["authenticated_github_readback"]
    result["research_commit"] = research_commit
    return result


def _assembly_receipt(repo, *, marker_commit, trial_id, appid,
                      authorization_commit, research_commit,
                      assembly_commit, receipt_parent):
    """Deterministic typed Assembly terminal or strict-ready receipt, never acceptance."""
    anchor = issuer_structure(repo, marker_commit=marker_commit, trial_id=trial_id,
                              authorization_commit=authorization_commit)
    if not first_parent_contains(repo, assembly_commit, receipt_parent):
        v2.reject("broken_git_provenance", "Assembly receipt cannot precede its result")
    verdict = v2.inspect_assembly(
        repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid,
        research_commit=research_commit, result_commit=assembly_commit)
    disposition = verdict["status"]
    if disposition not in (
        "strict_item_valid_pending_existing_atomic_group_ingest",
        "assembly_missing_evidence", "assembly_semantic_conflict",
        "runtime_or_tool_interrupted", "assembly_technical_error",
    ):
        v2.reject("wrong_binding", "Assembly result cannot receive a success/terminal receipt")
    doc = v2.item_receipt_blueprint(
        repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid,
        phase="assembly", disposition=disposition,
        source={
            "issuer": anchor, "receipt_parent_commit": receipt_parent,
            "research_commit": research_commit, "assembly_commit": assembly_commit,
            "candidate_status": disposition, "canonical_acceptance": False,
        })
    a = doc["assignment"]
    path = ("data/control/dossier_notes_v2/receipts/" + trial_id
            + "/g%06d/" % a["group_sequence"] + appid
            + "--" + a["assignment_id"] + "--assembly.json")
    raw = v2._canonical(doc)
    return {"status":"assembly_receipt_proposal_not_github_confirmed",
            "receipt_path":path, "receipt_bytes":raw,
            "receipt_blob_sha":blob_for(raw), "disposition":disposition,
            "canonical_acceptance":False, "semantic_quality_accepted":False}


def publish_assembly_receipt_remote(repo, *, branch, expected_remote_head,
                                    marker_commit, trial_id, appid,
                                    authorization_commit, research_commit,
                                    assembly_commit,
                                    github_repository=None, github_token=None):
    """One-create-only typed mechanical receipt AFTER an Assembly Git introduction."""
    verify_scoped_semantic_run(
        repo, marker_commit=marker_commit, trial_id=trial_id,
        authorization_commit=authorization_commit,
        github_repository=github_repository, github_token=github_token)

    def plan(work):
        return _assembly_receipt(
            work, marker_commit=marker_commit, trial_id=trial_id,
            appid=appid, authorization_commit=authorization_commit,
            research_commit=research_commit, assembly_commit=assembly_commit,
            receipt_parent=git(work, "rev-parse", "HEAD").stdout.decode().strip())

    def inspect(work, commit_sha, planned):
        p = require_only_new(work, commit_sha, [planned["receipt_path"]])
        exact = _assembly_receipt(
            work, marker_commit=marker_commit, trial_id=trial_id,
            appid=appid, authorization_commit=authorization_commit,
            research_commit=research_commit, assembly_commit=assembly_commit,
            receipt_parent=p)
        if (file_at(work, commit_sha, planned["receipt_path"]) != exact["receipt_bytes"]
                or blob(work, commit_sha, planned["receipt_path"])
                != exact["receipt_blob_sha"]):
            v2.reject("broken_git_provenance", "typed Assembly receipt bytes changed")

    result = _single_remote_add(
        repo, branch=branch, expected_remote_head=expected_remote_head,
        make_plan=plan, check_commit=inspect,
        message="dossier notes v2: create-only Assembly receipt " + str(appid),
        github_repository=github_repository, github_token=github_token)
    result["status"] = ("github_assembly_receipt_confirmed"
                        if result["authenticated_github_readback"]
                        else "disposable_remote_assembly_receipt_only")
    result["github_assembly_receipt_confirmed"] = result["authenticated_github_readback"]
    return result


def publish_one_assembly_item_remote(repo, *, branch, expected_remote_head,
                                     marker_commit, trial_id, appid,
                                     authorization_commit, research_commit,
                                     document, github_repository=None, github_token=None):
    """Research-bound Assembly candidate and separately proven receipt, one attempt."""
    shared = {
        "repo": repo, "branch": branch,
        "marker_commit": marker_commit, "trial_id": trial_id,
        "appid": appid, "authorization_commit": authorization_commit,
        "research_commit": research_commit,
        "github_repository": github_repository, "github_token": github_token,
    }
    proposal = publish_assembly_item_remote(
        expected_remote_head=expected_remote_head, document=document, **shared)
    receipt = publish_assembly_receipt_remote(
        expected_remote_head=proposal["remote_commit"],
        assembly_commit=proposal["remote_commit"], **shared)
    return {
        "status": ("github_assembly_receipt_confirmed"
                   if receipt["github_assembly_receipt_confirmed"]
                   else "disposable_remote_assembly_item_only"),
        "research_commit": research_commit,
        "assembly_commit": proposal["remote_commit"],
        "receipt_commit": receipt["remote_commit"],
        "assembly_path": proposal["remote_path"],
        "receipt_path": receipt["remote_path"],
        "disposition": receipt["disposition"],
        "github_assembly_receipt_confirmed": receipt["github_assembly_receipt_confirmed"],
        "canonical_acceptance": False,
        "semantic_quality_accepted": False,
    }


def publish_one_research_item_remote(repo, *, branch, expected_remote_head,
                                     marker_commit, trial_id, appid,
                                     authorization_commit, document,
                                     github_repository=None, github_token=None):
    """One-item candidate then one-item receipt, no siblings, retries or semantic run.

    A failure of receipt publication does not erase an already pushed candidate.
    It raises rather than inventing acceptance; the operator must inspect remote
    state explicitly before any follow-up, never resubmit the candidate.
    """
    shared = {
        "branch": branch, "marker_commit": marker_commit,
        "trial_id": trial_id, "appid": appid,
        "authorization_commit": authorization_commit,
        "github_repository": github_repository, "github_token": github_token,
    }
    candidate = publish_candidate_remote(
        repo, expected_remote_head=expected_remote_head, document=document, **shared)
    receipt = publish_receipt_remote(
        repo, expected_remote_head=candidate["remote_commit"],
        introduction_commit=candidate["remote_commit"], **shared)
    return {
        "status": ("github_research_receipt_confirmed"
                   if receipt["github_receipt_confirmed"]
                   else "disposable_remote_item_only"),
        "candidate_commit": candidate["remote_commit"],
        "receipt_commit": receipt["remote_commit"],
        "candidate_path": candidate["remote_path"],
        "receipt_path": receipt["remote_path"],
        "github_candidate_confirmed": candidate["github_candidate_confirmed"],
        "github_receipt_confirmed": receipt["github_receipt_confirmed"],
        "semantic_quality_accepted": False,
        "canonical_acceptance": False,
        "attempt_state": "unknown",
    }

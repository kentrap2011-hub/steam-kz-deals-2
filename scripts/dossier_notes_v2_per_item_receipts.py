#!/usr/bin/env python3
"""Inactive Notes V2 per-item transport/receipt adapter, for disposable Git only.

No network, push, Git commit, semantic execution, retry, or canonical writer.
GitHub must separately authenticate the human semantic grant, Actions run,
remote compare-and-swap and re-fetched receipt before claiming a durable receipt.
A V2 issuer commit alone expressly does NOT authorize Research semantics.
"""
import json
import re
from pathlib import Path

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
        "mode": "original18_inactive_V2_control_plane_issuance_only",
        "semantic_execution_authorized": False,
        "canonical_acceptance": False,
        "assembly_authorized": False,
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
    grant_path = "config/dossier_notes_v2_issuer_human_grant.json"
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
        "semantic_execution_approved": False, "production_approved": False,
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
        "semantic_execution_authorized": False,
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

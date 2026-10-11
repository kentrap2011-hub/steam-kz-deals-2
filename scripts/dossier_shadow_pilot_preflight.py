#!/usr/bin/env python3
"""Fail-closed, OFFLINE shadow-pilot evidence preflight.

Reads only caller-pinned commits in a marked disposable Git fixture. This is
not a selector, historical writer, semantic executor, acceptance receipt,
quality evaluator or production entrypoint. Never invoke on a live checkout.
"""
import hashlib
import json
import re
from pathlib import Path

from dossier_two_stage_final_acceptance import offline_gate
from dossier_two_stage_shadow_quality import _baseline
from dossier_two_stage_staging import blob, first_parent_contains, git, parent, strict_json
from taste_steam_review_dossier_daily import validate_group_plan, validate_manifest
from taste_steam_review_dossier_group_progress import ensure_group_progress

SCHEMA = "DOSSIER-SHADOW-PILOT-PREFLIGHT-V1"
AUDIT = "data/audit/taste_steam_review_dossier_frozen_invocations.jsonl"
MANIFEST = "data/production/pre_ai/taste_steam_review_dossier_work.json"
PROPOSAL_CONTRACTS = (
    "config/dossier_two_stage_interfaces_contract.json",
    "config/dossier_two_stage_staging_contract.json",
    "config/dossier_two_stage_async_buffer_contract.json",
    "config/dossier_two_stage_final_acceptance_bridge_contract.json",
)
H40 = re.compile(r"^[0-9a-f]{40}$")
H64 = re.compile(r"^[0-9a-f]{64}$")


def require(value, message):
    if not value:
        raise ValueError("shadow pilot preflight: " + message)


def _commit(value, label):
    require(isinstance(value, str) and H40.fullmatch(value), "invalid " + label)
    return value


def _path(value):
    require(isinstance(value, str) and value and not value.startswith("/")
            and "\\" not in value and all(p not in ("", ".", "..") for p in value.split("/")),
            "unsafe Git path")
    return value


def _read(repo, commit, path):
    return git(repo, "show", _commit(commit, "file commit") + ":" + _path(path)).stdout


def _document(repo, commit, path):
    return strict_json(_read(repo, commit, path))


def _diff(repo, commit):
    rows = git(repo, "diff-tree", "--no-commit-id", "--name-status",
               "-r", _commit(commit, "transaction commit")).stdout.decode().splitlines()
    return {line.split("\t", 1)[1]: line.split("\t", 1)[0]
            for line in rows if "\t" in line}


def _relative_manifest(repo, contract):
    configured = Path(contract["paths"]["work_manifest"])
    if not configured.is_absolute():
        return _path(configured.as_posix())
    root = Path(repo).resolve()
    require(configured.resolve().is_relative_to(root), "manifest escapes fixture")
    return _path(configured.resolve().relative_to(root).as_posix())


def _inert_proposal(repo, head, hashes):
    require(type(hashes) is dict and set(hashes) == set(PROPOSAL_CONTRACTS),
            "four exact proposal contract blob bindings required")
    for path in PROPOSAL_CONTRACTS:
        value = _commit(hashes[path], "proposal blob SHA")
        require(blob(repo, head, path) == value,
                "proposal Git contract binding changed: " + path)
        doc = _document(repo, head, path)
        require(doc.get("active") is False, "proposal stage no longer inactive: " + path)
        for flag in ("authorized_for_semantic_execution", "authorized_for_canonical_ingest",
                     "executable_in_production"):
            require(doc.get(flag) is not True, "proposal has active authority: " + path)
    bridge = _document(repo, head, PROPOSAL_CONTRACTS[-1])
    require(bridge.get("schema") == "DOSSIER-TWO-STAGE-FINAL-ACCEPTANCE-BRIDGE-V1"
            and bridge.get("authorized_for_canonical_ingest") is False
            and bridge.get("executable_in_production") is False,
            "inactive bridge contract not proven")


def verify_offline_preflight(repo, *, request, contract):
    """Require a real historical *writer transaction AND frozen writer audit*.

    A strict cache JSON, one-stage schema or accepted progress flag alone cannot
    pass. The independent audit must have been appended in the exact writer
    transaction; only the existing writer generates that audit in production.
    """
    root = offline_gate(repo, offline_fixture=True)
    require(type(request) is dict and request.get("schema") == SCHEMA,
            "unsupported request marker")
    head = _commit(request.get("target_head"), "target HEAD")
    require(git(root, "rev-parse", "HEAD").stdout.decode().strip() == head,
            "target Git snapshot changed")
    writer = _commit(request.get("legacy_writer_commit"), "writer commit")
    writer_parent = _commit(request.get("legacy_writer_parent"), "writer parent")
    require(parent(root, writer) == writer_parent,
            "wrong writer transaction Git parent")
    require(first_parent_contains(root, writer, head), "writer not in target first-parent history")
    manifest_path = _relative_manifest(root, contract)
    require(request.get("legacy_manifest_path") == manifest_path,
            "legacy manifest not at canonical writer path")
    original = _commit(request.get("original_manifest_commit"), "original authority")
    require(first_parent_contains(root, original, writer_parent),
            "original plan is not a predecessor of writer")
    before = ensure_group_progress(_document(root, writer_parent, manifest_path), contract)
    after = ensure_group_progress(_document(root, writer, manifest_path), contract)
    validate_manifest(before, contract)
    validate_manifest(after, contract)
    require(before["snapshot_id"] == after["snapshot_id"]
            and before["prepared_required_sha256"] == after["prepared_required_sha256"]
            and before["submission_group_plan"] == after["submission_group_plan"],
            "writer mutated immutable snapshot / original group plan")
    at_original = ensure_group_progress(_document(root, original, manifest_path), contract)
    validate_manifest(at_original, contract)
    require(at_original["snapshot_id"] == before["snapshot_id"]
            and at_original["submission_group_plan"] == before["submission_group_plan"],
            "original group plan rebound")
    seq = request.get("group_sequence")
    groups = validate_group_plan(at_original, contract, required=True)["groups"]
    require(type(seq) is int and 1 <= seq <= len(groups), "invalid original group sequence")
    group = groups[seq - 1]
    require(group["sequence"] == seq and len(group["items"]) == 3
            and len({str(i["appid"]) for i in group["items"]}) == 3
            and contract["checkpointing"]["checkpoint_size"] == 3,
            "not an exact immutable original three-game group")
    descriptor_path = ("data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                       f"{at_original['snapshot_id']}/g{seq:06d}.json")
    require(request.get("descriptor_path") == descriptor_path,
            "wrong original descriptor path")
    require(blob(root, original, descriptor_path)
            == _commit(request.get("descriptor_blob_sha"), "descriptor blob"),
            "original descriptor blob mismatch")
    desc = _document(root, original, descriptor_path)
    require(desc == {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1",
        "schema_version": 1,
        "group_plan_sha256": at_original["submission_group_plan"]["group_plan_sha256"],
        "group_count": len(groups),
        "web_evidence_contract_binding": at_original["web_evidence_contract_binding"],
        **group,
    }, "original descriptor not the authoritative GitHub group")
    old_state = before["group_progress"]["groups"][seq-1]
    new_state = after["group_progress"]["groups"][seq-1]
    require(old_state["state"] == "pending" and new_state["state"] == "accepted"
            and old_state["group_sha256"] == new_state["group_sha256"] == group["group_sha256"],
            "missing exact pending-to-accepted group writer receipt")
    changes = _diff(root, writer)
    require(changes.get(manifest_path) == "M", "missing writer manifest transaction")
    require(changes.get(AUDIT) in ("A", "M"), "missing historical writer audit transaction")
    audit = _read(root, writer, AUDIT)
    previous = (_read(root, writer_parent, AUDIT)
                if changes.get(AUDIT) == "M" else b"")
    require(audit.startswith(previous) and len(audit) > len(previous),
            "writer audit not append-only")
    delta = audit[len(previous):].splitlines()
    audit_line_sha = request.get("audit_line_sha256")
    require(isinstance(audit_line_sha, str) and H64.fullmatch(audit_line_sha),
            "missing exact historical writer receipt hash")
    matches = [line for line in delta if hashlib.sha256(line).hexdigest() == audit_line_sha]
    require(len(matches) == 1, "absent/mismatched newly committed writer receipt")
    receipt = strict_json(matches[0])
    authority = receipt.get("authority") if isinstance(receipt, dict) else None
    require(receipt.get("schema") == "TASTE-STEAM-REVIEW-DOSSIER-FROZEN-INVOCATION-AUDIT-V1"
            and receipt.get("consumed") is True
            and receipt.get("outcome") == "dossier_candidate_accepted_current_snapshot"
            and receipt.get("authority_snapshot_id") == group["snapshot_id"]
            and receipt.get("authority_group_sha256") == group["group_sha256"]
            and receipt.get("authority_sequence") == seq
            and isinstance(authority, dict)
            and authority.get("schema") == "TASTE-STEAM-REVIEW-DOSSIER-FROZEN-AUTHORITY-V1"
            and authority.get("snapshot_id") == group["snapshot_id"]
            and authority.get("sequence") == seq
            and authority.get("group_sha256") == group["group_sha256"]
            and authority.get("group_plan_sha256") ==
                at_original["submission_group_plan"]["group_plan_sha256"]
            and authority.get("prepared_required_sha256") == group["prepared_required_sha256"],
            "historical writer receipt lacks exact accepted group authority")
    anchor = _commit(authority.get("run_start_anchor_commit"), "legacy marker")
    require(_commit(authority.get("run_start_authority_commit"), "legacy marker parent")
            == parent(root, anchor), "wrong immutable run-start marker Git parent")
    require(first_parent_contains(root, original, anchor)
            and first_parent_contains(root, anchor, writer_parent),
            "marker not between frozen original group and writer")
    marker_path = authority.get("marker_path")
    nonce = authority.get("run_start_nonce")
    require(isinstance(nonce, str) and re.fullmatch("[0-9a-f]{32}", nonce)
            and isinstance(marker_path, str)
            and marker_path.endswith("/run_starts/" + nonce + ".json")
            and _diff(root, anchor) == {marker_path: "A"}
            and _document(root, anchor, marker_path) == {
                "schema": "TASTE-STEAM-REVIEW-DOSSIER-RUN-START-MARKER-V1",
                "schema_version": 1, "run_start_nonce": nonce},
            "unsupported, forged or changed legacy marker")
    introduction = _commit(authority.get("result_introduction_commit"), "candidate introduction")
    require(first_parent_contains(root, anchor, introduction)
            and first_parent_contains(root, introduction, writer_parent),
            "legacy artifact introduction not on immutable first-parent chain")
    artifact_path = receipt.get("artifact_path")
    require(artifact_path == str(artifact_path) and isinstance(artifact_path, str)
            and _diff(root, introduction).get(artifact_path) == "A"
            and hashlib.sha256(_read(root, introduction, artifact_path)).hexdigest()
                == receipt.get("artifact_sha256"),
            "candidate does not bind historical writer audit")
    declared = request.get("original_games")
    baselines = request.get("legacy_baselines")
    require(type(declared) is list and type(baselines) is list
            and len(declared) == len(baselines) == 3, "require three exact original identities/baselines")
    actions = receipt.get("dossier_actions")
    require(type(actions) is list and len(actions) == 3,
            "historical receipt missing all three persisted cache actions")
    safe_appids = []
    for item, game, base, action in zip(group["items"], declared, baselines, actions):
        appid = str(item["appid"])
        require(type(game) is dict and set(game) == {
            "appid", "title", "original_work_year"} and game["appid"] == appid
            and game["title"] == item["title"]
            and type(game["original_work_year"]) is int
            and game["original_work_year"] > 0,
            "wrong original game/AppID/work year identity")
        require(type(base) is dict and base.get("appid") == appid
                and base.get("commit") == writer
                and base.get("path") == item["dossier_path"]
                and changes.get(item["dossier_path"]) in ("A", "M"),
                "legacy cache not persisted by exact writer transaction")
        old = _baseline(root, appid, base, contract, head)
        identity = old["game_identity"]
        require(identity.get("release_year") == game["original_work_year"]
                and identity.get("title") == item["title"],
                "legacy original-work-year/title mismatch")
        require(action == {
            "appid": appid, "action": "persisted_current_group_dossier",
            "candidate_dossier_sha256": base["canonical_sha256"],
            "kept_dossier_sha256": base["canonical_sha256"],
        }, "writer receipt/cache/AppID binding mismatch")
        safe_appids.append(appid)
    require(len(set(safe_appids)) == 3, "duplicate original AppID")
    _inert_proposal(root, head, request.get("proposal_contract_blobs"))
    # This does NOT assert substantive source truth, quality, sample approval or
    # an actual Research/Assembly result. Existing strict V2 + shadow harness
    # still run separately against later explicit frozen candidate locators.
    return {
        "schema": SCHEMA, "diagnostic_only": True, "preflight_ready": True,
        "quality_verified": False, "pilot_authorized": False,
        "canonical_readiness": False, "deep_readiness": False,
        "original_group_sequence": seq, "original_group_sha256": group["group_sha256"],
        "target_head": head, "writer_commit": writer, "writer_receipt_sha256": audit_line_sha,
        "accepted_baseline_appids": safe_appids,
        "evidence": "exact_writer_transition_plus_append_only_frozen_audit_plus_unchanged_three_blobs",
        "semantic_execution": False, "writes": [],
    }


if __name__ == "__main__":
    raise SystemExit("Offline API only: no live CLI, trial selector or production entrypoint")

#!/usr/bin/env python3
"""INACTIVE offline two-stage Dossier authorization and eventual chain checker.

GitHub preauthorizes finite immutable scope once. Research and Assembly semantic
execution is never gated on Github receipt, slot release or sibling completion.
Nothing here runs a semantic worker, scans an inbox, writes canonical state or
activates production. The final strict V2 validator remains mandatory.
"""
import copy
import hashlib
import json
import re

from dossier_two_stage_contract_guard import (
    CONFIG, canonical_sha256, schema_validate, validate_assembly_result,
)
from dossier_two_stage_staging import (
    gate, fail, blob, blob_for, bytes_json, file_at, first_parent_contains,
    json_at, marker_context, research_authority, receive_research, receipt_paths,
    require_only_new, strict_json,
)

SCHEMA = "DOSSIER-TWO-STAGE-ASYNC-BUFFER-V2"
PHASES = ("research", "assembly")
BUFFER_PREFIX = "data/control/dossier_two_stage_buffers"
RESEARCH_PREFIX = "data/control/dossier_research_assignments"
ASSEMBLY_PREFIX = "data/control/dossier_assembly_plans"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
AID = re.compile(r"^[a-z0-9][a-z0-9._-]{7,127}$")


def inactive_gate():
    interfaces, staging = gate()
    config = json.loads((CONFIG / "dossier_two_stage_async_buffer_contract.json").read_text("utf-8"))
    if (config.get("schema") != "DOSSIER-TWO-STAGE-ASYNC-BUFFER-CONTRACT-V2"
            or config.get("active") is not False or config.get("authoritative") is not False
            or config.get("executable_in_production") is not False
            or config.get("semantic_workers_implemented") is not False
            or config.get("capacity", {}).get("semantic_liveness_depends_on_open_slots") is not False
            or staging.get("asynchronous_buffers", {}).get("activation") is not False
            or interfaces.get("asynchronous_buffered_execution", {}).get("activation") is not False):
        fail("fully async contract must remain inactive and GitHub-owned")
    return config


def _research_entry(repo, revision, path):
    m = re.fullmatch(re.escape(RESEARCH_PREFIX) +
                     r"/([0-9a-f]{64})/g([0-9]{6})/([0-9]+)--([a-z0-9._-]+)\.json", path)
    if not m:
        fail("Research work outside exact authorized namespace")
    snapshot, sequence, appid, aid = m.groups()
    prepared = json_at(repo, revision, path)
    if (not isinstance(prepared, dict) or prepared.get("assignment_id") != aid
            or prepared.get("snapshot_id") != snapshot
            or prepared.get("group_sequence") != int(sequence)
            or prepared.get("appid") != appid
            or type(prepared.get("item_index")) is not int):
        fail("Research prepared binding mismatch")
    return {
        "work_path": path, "work_blob_sha": blob(repo, revision, path),
        "snapshot_id": snapshot, "group_sequence": int(sequence),
        "item_index": prepared["item_index"], "appid": appid, "assignment_id": aid,
    }


def _assembly_entry(repo, revision, path):
    m = re.fullmatch(re.escape(ASSEMBLY_PREFIX) +
                     r"/([0-9a-f]{64})/g([0-9]{6})/([0-9]+)--([a-z0-9._-]+)\.json", path)
    if not m:
        fail("Assembly plan outside exact authorized namespace")
    snapshot, sequence, appid, aid = m.groups()
    plan = json_at(repo, revision, path)
    required = {"schema", "schema_version", "research_assignment_id",
                "research_prepared_work_path", "research_prepared_work_blob_sha",
                "assembly_assignment_id", "assembly_contract_sha256",
                "assembly_prompt_sha256", "assembly_prompt_revision",
                "canonical_dossier_target"}
    if not isinstance(plan, dict) or set(plan) != required or (
            plan["schema"] != "DOSSIER-ASSEMBLY-GITHUB-PREAUTH-PLAN-V2"
            or plan["schema_version"] != 2 or plan["research_assignment_id"] != aid
            or not AID.fullmatch(str(plan["assembly_assignment_id"]))
            or not isinstance(plan["assembly_prompt_revision"], str)
            or not plan["assembly_prompt_revision"]):
        fail("invalid GitHub-preauthorized Assembly plan")
    for key in ("research_prepared_work_blob_sha",):
        if not HEX40.fullmatch(str(plan[key])):
            fail("invalid preauthorized Research Git blob")
    for key in ("assembly_contract_sha256", "assembly_prompt_sha256"):
        if not HEX64.fullmatch(str(plan[key])):
            fail("invalid preauthorized Assembly digest")
    r = _research_entry(repo, revision, plan["research_prepared_work_path"])
    if ((r["snapshot_id"], r["group_sequence"], r["appid"], r["assignment_id"]) !=
            (snapshot, int(sequence), appid, aid)
            or r["work_blob_sha"] != plan["research_prepared_work_blob_sha"]):
        fail("Assembly plan not tied to same exact frozen Research work")
    prepared = json_at(repo, revision, r["work_path"])
    target = {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-V2", "schema_version": 2,
        "worker_schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2",
        "worker_schema_version": 2,
        "web_evidence_contract": "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2",
        "web_evidence_contract_version": 2,
        "canonical_worker_binding_sha256": canonical_sha256(
            prepared["web_evidence_contract_binding"]),
    }
    if plan["canonical_dossier_target"] != target:
        fail("Assembly canonical target differs from frozen original binding")
    return {**r, "work_path": path, "work_blob_sha": blob(repo, revision, path),
            "research_prepared_work_path": r["work_path"],
            "research_prepared_work_blob_sha": r["work_blob_sha"],
            "assembly_assignment_id": plan["assembly_assignment_id"]}


def _entry(repo, revision, phase, path):
    return (_research_entry if phase == "research" else _assembly_entry)(repo, revision, path)


def _ordered(entries):
    identities = [(x["group_sequence"], x["item_index"], x["appid"], x["assignment_id"])
                  for x in entries]
    if identities != sorted(identities) or len(set(identities)) != len(identities):
        fail("scope must contain unique exact GitHub ordered work")
    if len({x["work_path"] for x in entries}) != len(entries):
        fail("duplicate GitHub work path")


def make_buffer(repo, *, source_commit, phase, ordered_work_paths, new_authorization_limit=None):
    """GitHub-only finite preauthorization. Optional limit applies BEFORE issuance.

    Once issued, the entire buffer may be traversed irrespective of unresolved
    work, pending ingest, acknowledgements, or subsequent GitHub movement.
    """
    inactive_gate()
    if phase not in PHASES or not HEX40.fullmatch(str(source_commit)):
        fail("invalid source commit or phase")
    if (not isinstance(ordered_work_paths, (list, tuple)) or not ordered_work_paths
            or any(not isinstance(p, str) for p in ordered_work_paths)):
        fail("must preauthorize nonempty finite explicit work scope")
    if new_authorization_limit is not None and (
            type(new_authorization_limit) is not int or new_authorization_limit < 1
            or len(ordered_work_paths) > new_authorization_limit):
        fail("new GitHub authorization exceeds upstream resource budget")
    entries = [_entry(repo, source_commit, phase, p) for p in ordered_work_paths]
    _ordered(entries)
    snapshot = entries[0]["snapshot_id"]
    if any(e["snapshot_id"] != snapshot for e in entries):
        fail("cross-snapshot authorization forbidden")
    body = {"schema": SCHEMA, "schema_version": 2, "phase": phase,
            "snapshot_id": snapshot, "items": entries}
    doc = {**body, "buffer_id": canonical_sha256(body)}
    path = f"{BUFFER_PREFIX}/{phase}/{snapshot}/{doc['buffer_id']}.json"
    # Explicit immutable GitHub-prepared buffer only; no worker-chosen scope.
    from dossier_two_stage_staging import exists
    if exists(repo, source_commit, path):
        fail("preauthorization already exists")
    return {"path": path, "manifest": doc, "reserved_count": len(entries)}


def frozen_buffer(repo, *, marker_commit, buffer_path, phase):
    inactive_gate()
    if phase not in PHASES:
        fail("invalid phase")
    frozen, _ = marker_context(repo, marker_commit, phase)
    doc = json_at(repo, frozen, buffer_path)
    if (not isinstance(doc, dict) or set(doc) !=
            {"schema", "schema_version", "phase", "snapshot_id", "items", "buffer_id"}
            or doc["schema"] != SCHEMA or doc["schema_version"] != 2
            or doc["phase"] != phase or not isinstance(doc["items"], list)
            or not doc["items"] or not HEX64.fullmatch(str(doc["snapshot_id"]))
            or not HEX64.fullmatch(str(doc["buffer_id"]))):
        fail("invalid frozen two-stage authorization")
    if canonical_sha256({k: v for k, v in doc.items() if k != "buffer_id"}) != doc["buffer_id"]:
        fail("tampered immutable buffer content hash")
    if buffer_path != f"{BUFFER_PREFIX}/{phase}/{doc['snapshot_id']}/{doc['buffer_id']}.json":
        fail("frozen buffer path/hash mismatch")
    entries = [_entry(repo, frozen, phase, e["work_path"]) for e in doc["items"]]
    if entries != doc["items"] or any(e["snapshot_id"] != doc["snapshot_id"] for e in entries):
        fail("frozen Git work blobs/order/bindings changed")
    _ordered(entries)
    if phase == "research":
        for e in entries:
            research_authority(repo, marker_commit, e["work_path"])
    # NO Research accepted receipt, sibling ack or unresolved-slot read here.
    return doc


def _member(doc, path):
    for entry in doc["items"]:
        if entry["work_path"] == path:
            return entry
    fail("out-of-scope, worker-invented or recovery work")


def receive_buffered_research(repo, *, marker_commit, buffer_path, work_path, package_commit):
    doc = frozen_buffer(repo, marker_commit=marker_commit, buffer_path=buffer_path,
                        phase="research")
    _member(doc, work_path)
    return receive_research(repo, marker_commit=marker_commit,
                            prepared_work_path=work_path, package_commit=package_commit)


def submitted_research_transport(repo, *, assembly_frozen, plan_entry, package_commit):
    """Read exact raw Research bytes without misrepresenting GH acceptance.

    Invalid Research semantics are intentionally NOT an Assembly liveness gate;
    GitHub's eventual validation rejects the corresponding item chain.
    """
    rpath = plan_entry["research_prepared_work_path"]
    prepared = json_at(repo, assembly_frozen, rpath)
    a_id = plan_entry["assignment_id"]
    path = (f"data/ai_inbox/dossier_research/{plan_entry['snapshot_id']}/"
            f"g{plan_entry['group_sequence']:06d}/{plan_entry['appid']}--{a_id}.json")
    if not HEX40.fullmatch(str(package_commit)):
        fail("Research package commit was not supplied exactly")
    introduction = require_only_new(repo, package_commit, [path])
    raw = file_at(repo, package_commit, path)
    package = strict_json(raw)
    if not isinstance(package, dict) or not isinstance(package.get("assignment"), dict):
        fail("submitted Research package has no exact preauthorized binding")
    a = package["assignment"]
    marker = a.get("research_marker_anchor_commit")
    if not HEX40.fullmatch(str(marker)):
        fail("missing immutable Research run-start marker")
    frozen_research, nonce = marker_context(repo, marker, "research")
    exact = research_authority(repo, marker, rpath)
    if (a != exact or plan_entry["research_prepared_work_blob_sha"] !=
            blob(repo, frozen_research, rpath)
            or blob(repo, assembly_frozen, rpath) != blob(repo, frozen_research, rpath)
            or not first_parent_contains(repo, marker, introduction)):
        fail("Research source marker/work/assignment Git ancestry mismatch")
    actual_blob = blob(repo, package_commit, path)
    if actual_blob != blob_for(raw):
        fail("raw submitted Research Git blob identity changed")
    return a, package, {
        "research_marker_anchor_commit": marker,
        "research_package_git_commit": package_commit,
        "research_package_path": path,
        "research_package_blob_sha": actual_blob,
        "research_package_raw_sha256": hashlib.sha256(raw).hexdigest(),
        "research_package_sha256": canonical_sha256(package),
        "research_prepared_work_path": rpath,
        "research_prepared_work_blob_sha": plan_entry["research_prepared_work_blob_sha"],
        "assembly_plan_blob_sha": plan_entry["work_blob_sha"],
    }


def provisional_assembly_work(repo, *, marker_commit, buffer_path, work_path, package_commit):
    """Exact submitted Research handoff, with no GH acceptance/ack prerequisite."""
    doc = frozen_buffer(repo, marker_commit=marker_commit, buffer_path=buffer_path,
                        phase="assembly")
    entry = _member(doc, work_path)
    frozen, nonce = marker_context(repo, marker_commit, "assembly")
    a, package, transport = submitted_research_transport(
        repo, assembly_frozen=frozen, plan_entry=entry, package_commit=package_commit)
    if not first_parent_contains(repo, transport["research_marker_anchor_commit"], marker_commit):
        fail("Assembly marker not descended from Research authorization")
    plan = json_at(repo, frozen, work_path)
    work = {
        "schema": "DOSSIER-ASYNC-ASSEMBLY-PREAUTHORIZED-WORK-V1",
        "assembly_assignment_id": plan["assembly_assignment_id"],
        "original_research_assignment": a,
        "research_transport": transport,
        "assembly_marker_anchor_commit": marker_commit,
        "assembly_marker_nonce": nonce,
        "assembly_contract_sha256": plan["assembly_contract_sha256"],
        "assembly_prompt_sha256": plan["assembly_prompt_sha256"],
        "assembly_prompt_revision": plan["assembly_prompt_revision"],
        "canonical_dossier_target": plan["canonical_dossier_target"],
        "output_path": (f"data/ai_inbox/dossier_assembly/{entry['snapshot_id']}/"
                        f"g{entry['group_sequence']:06d}/{entry['appid']}--"
                        f"{plan['assembly_assignment_id']}.json"),
        "create_only": True,
        "canonical_dossier_accepted": False,
    }
    return work


def inspect_buffered_assembly_candidate(repo, *, marker_commit, buffer_path,
                                        work_path, result_commit):
    """Eventual GitHub per-item chain check. Never itself accepts canonical data."""
    # Candidate's untrusted transport locator is not an authority: GH checks its
    # create-only original commit, exact plan, marker parent and original bytes.
    frozen, _ = marker_context(repo, marker_commit, "assembly")
    entry = _member(frozen_buffer(repo, marker_commit=marker_commit,
                                  buffer_path=buffer_path, phase="assembly"), work_path)
    plan = json_at(repo, frozen, work_path)
    result_path = (f"data/ai_inbox/dossier_assembly/{entry['snapshot_id']}/"
                   f"g{entry['group_sequence']:06d}/{entry['appid']}--"
                   f"{plan['assembly_assignment_id']}.json")
    require_only_new(repo, result_commit, [result_path])
    if not first_parent_contains(repo, marker_commit, result_commit):
        fail("Assembly result predates frozen marker")
    raw = file_at(repo, result_commit, result_path)
    if blob(repo, result_commit, result_path) != blob_for(raw):
        fail("Assembly raw immutable blob mismatch")
    result = strict_json(raw)
    from jsonschema import Draft202012Validator
    schema = json.loads((CONFIG / "dossier_async_assembly_result_v1.schema.json").read_text("utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(result))
    if errors:
        fail("invalid fully-async Assembly candidate schema: " + errors[0].message)
    transport = result["research_transport"]
    package_commit = transport["research_package_git_commit"]
    if not first_parent_contains(repo, package_commit, result_commit):
        fail("Assembly result did not consume ancestor submitted Research Git commit")
    work = provisional_assembly_work(repo, marker_commit=marker_commit,
                                     buffer_path=buffer_path, work_path=work_path,
                                     package_commit=package_commit)
    for key in ("assembly_assignment_id", "original_research_assignment",
                "research_transport", "assembly_marker_anchor_commit",
                "assembly_marker_nonce", "assembly_contract_sha256",
                "assembly_prompt_sha256", "canonical_dossier_target", "output_path"):
        if result[key] != work[key]:
            fail("Assembly result did not use exact immutable Research/plan bytes: " + key)
    # GitHub Research verdict is downstream, NOT in the Assembly execution path.
    a = work["original_research_assignment"]
    proposal = receive_research(repo, marker_commit=a["research_marker_anchor_commit"],
                                prepared_work_path=transport["research_prepared_work_path"],
                                package_commit=package_commit)
    if proposal["status"] != "accepted_structural_evidence":
        return {"status": "research_rejected_item_chain_quarantined",
                "research_status": proposal["status"], "canonical_dossier_accepted": False,
                "deep_ready": False, "item_local_only": True}
    receipt = proposal["files"][proposal["receipt_path"]]
    package = strict_json(file_at(repo, package_commit, transport["research_package_path"]))
    # Reuse P1's strict Assembly provenance/gap semantics AFTER GH has validated
    # Research. The adapter is local validation input, never worker provenance.
    accepted_work = {
        "schema": "DOSSIER-ASSEMBLY-ASSIGNMENT-V1", "schema_version": 1,
        "assembly_assignment_id": work["assembly_assignment_id"],
        "original_research_assignment": a,
        "accepted_research": receipt,
        "accepted_research_receipt_blob_sha": proposal["receipt_blob_sha"],
        "assembly_marker_anchor_commit": work["assembly_marker_anchor_commit"],
        "assembly_marker_nonce": work["assembly_marker_nonce"],
        "assembly_contract_sha256": work["assembly_contract_sha256"],
        "assembly_prompt_sha256": work["assembly_prompt_sha256"],
        "assembly_prompt_revision": work["assembly_prompt_revision"],
        "canonical_dossier_target": work["canonical_dossier_target"],
        "output_path": work["output_path"],
        "permitted_result_namespace": "data/ai_inbox/dossier_assembly/",
        "create_only": True,
        "canonical_acceptance_authority": "existing_github_strict_v2_validator_and_group_ingest_only",
    }
    accepted_result = copy.deepcopy(result)
    accepted_result["schema"] = "DOSSIER-ASSEMBLY-RESULT-V1"
    del accepted_result["research_transport"]
    accepted_result["accepted_research_package_sha256"] = receipt["research_package_sha256"]
    accepted_result["accepted_research_receipt_blob_sha"] = proposal["receipt_blob_sha"]
    validate_assembly_result(accepted_result, accepted_work, package)
    if result["outcome"] == "assembled_candidate_ready":
        # Strict validator + existing atomic 3-game group ingest are both still
        # mandatory. This local verdict is NOT canonical acceptance.
        from taste_steam_review_dossier_strict import validate_dossier_strict
        contract = json.loads((CONFIG / "taste_steam_review_dossier_contract.json").read_text("utf-8"))
        validate_dossier_strict(result["payload"]["dossier"], contract,
                                expected_appid=a["appid"], expected_title=a["title"])
        status = "strict_item_valid_pending_existing_atomic_group_ingest"
    else:
        status = "typed_assembly_item_pending_github_classification"
    return {"status": status, "research_status": proposal["status"],
            "canonical_dossier_accepted": False, "deep_ready": False,
            "item_local_only": True, "result_path": result_path}

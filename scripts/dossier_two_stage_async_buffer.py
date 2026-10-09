#!/usr/bin/env python3
"""Inactive GitHub-owned async Research/Assembly buffer planner and provenance guard.

Pure planning/validation against immutable Git history; NO CLI, live scanner,
scheduler, semantic worker, canonical Dossier ingest or production writes.
"""
import copy
import json
import re

from dossier_two_stage_contract_guard import CONFIG, canonical_sha256, validate_assembly_result
from dossier_two_stage_staging import (
    gate, fail, git, file_at, json_at, blob, blob_for, exists, marker_context,
    research_authority, assembly_authority, prepare_assembly, receive_research,
    strict_json, require_only_new, first_parent_contains, bytes_json, no_collisions,
)

SCHEMA = "DOSSIER-TWO-STAGE-ASYNC-BUFFER-V1"
CAPACITY = 8
PHASES = ("research", "assembly")
WORK_PREFIX = {
    "research": "data/control/dossier_research_assignments",
    "assembly": "data/control/dossier_assembly_plans",
}
BUFFER_PREFIX = "data/control/dossier_two_stage_buffers"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def inactive_gate():
    interfaces, staging = gate()
    config = json.loads((CONFIG / "dossier_two_stage_async_buffer_contract.json").read_text("utf-8"))
    if (config.get("schema") != "DOSSIER-TWO-STAGE-ASYNC-BUFFER-CONTRACT-V1"
            or config.get("active") is not False or config.get("authoritative") is not False
            or config.get("executable_in_production") is not False
            or config.get("semantic_workers_implemented") is not False
            or config.get("capacity", {}).get("max_open_slots_per_phase") != CAPACITY
            or staging.get("asynchronous_buffers", {}).get("activation") is not False
            or interfaces.get("asynchronous_buffered_execution", {}).get("activation") is not False):
        fail("async contract must remain inactive and GitHub-owned")
    return config


def _entry(repo, revision, phase, work_path):
    prefix = WORK_PREFIX[phase]
    match = re.fullmatch(
        re.escape(prefix) + r"/([0-9a-f]{64})/g([0-9]{6})/([0-9]+)--([a-z0-9._-]+)[.]json",
        work_path,
    )
    if not match:
        fail("not an exact GitHub-prepared work path")
    snapshot, seq, appid, assignment_id = match.groups()
    doc = json_at(repo, revision, work_path)
    if not isinstance(doc, dict):
        fail("invalid immutable work record")
    if phase == "research":
        if (doc.get("assignment_id") != assignment_id or doc.get("snapshot_id") != snapshot
                or doc.get("group_sequence") != int(seq) or doc.get("appid") != appid
                or not isinstance(doc.get("item_index"), int)):
            fail("Research immutable assignment mismatch")
        idx = doc["item_index"]
    else:
        if (doc.get("schema") != "DOSSIER-ASSEMBLY-GITHUB-PLAN-V1"
                or doc.get("research_assignment_id") != assignment_id
                or doc.get("schema_version") != 1):
            fail("Assembly predeclared plan mismatch")
        accepted_path = (f"data/control/dossier_research_accepted/"
                         f"{snapshot}/g{seq}/{appid}--{assignment_id}.json")
        accepted = json_at(repo, revision, accepted_path)
        a = accepted.get("assignment", {})
        if (accepted.get("status") != "accepted_structural_evidence_not_canonical_dossier"
                or a.get("snapshot_id") != snapshot or a.get("appid") != appid
                or a.get("group_sequence") != int(seq)
                or a.get("assignment_id") != assignment_id
                or not isinstance(a.get("item_index"), int)):
            fail("Assembly plan not tied to an accepted exact Research item")
        idx = a["item_index"]
    return {
        "work_path": work_path, "work_blob_sha": blob(repo, revision, work_path),
        "assignment_id": assignment_id, "snapshot_id": snapshot,
        "group_sequence": int(seq), "item_index": idx, "appid": appid,
    }


def _ordered_unique(entries):
    identities = [(x["group_sequence"], x["item_index"], x["appid"], x["assignment_id"])
                  for x in entries]
    if len(set(identities)) != len(identities):
        fail("duplicate immutable buffer assignment")
    if identities != sorted(identities):
        fail("buffer order must be exact canonical group/item order")
    if len({x["work_path"] for x in entries}) != len(entries):
        fail("duplicate immutable work path")


def make_buffer(repo, *, source_commit, phase, ordered_work_paths, occupied_slots=0):
    """GitHub control plane only: reserve remaining capacity, not wait for ack.

    occupied_slots MUST be computed from GitHub's unresolved reserved work state;
    submitted but not ingested items remain occupied. Nothing is persisted here.
    """
    inactive_gate()
    if phase not in PHASES or not HEX40.fullmatch(str(source_commit)):
        fail("invalid buffer phase or Git authority")
    if not isinstance(occupied_slots, int) or isinstance(occupied_slots, bool) or not 0 <= occupied_slots <= CAPACITY:
        fail("invalid GitHub-owned occupied slot count")
    if not isinstance(ordered_work_paths, (tuple, list)) or any(
            not isinstance(p, str) for p in ordered_work_paths):
        fail("buffer scope must be explicit GitHub work paths")
    if len(set(ordered_work_paths)) != len(ordered_work_paths):
        fail("duplicate GitHub work request")
    # Validate ALL candidate order before applying capacity, so overflow cannot
    # conceal a malformed or re-ordered candidate list.
    entries = [_entry(repo, source_commit, phase, p) for p in ordered_work_paths]
    _ordered_unique(entries)
    entries = entries[:CAPACITY - occupied_slots]
    if not entries:
        return None
    snapshot = entries[0]["snapshot_id"]
    if any(x["snapshot_id"] != snapshot for x in entries):
        fail("buffer mixes snapshot identities")
    body = {
        "schema": SCHEMA, "schema_version": 1,
        "phase": phase, "snapshot_id": snapshot,
        "capacity": CAPACITY, "items": entries,
    }
    doc = {**body, "buffer_id": canonical_sha256(body)}
    path = f"{BUFFER_PREFIX}/{phase}/{snapshot}/{doc['buffer_id']}.json"
    if exists(repo, source_commit, path):
        fail("buffer manifest already exists; never overwrite")
    return {"path": path, "manifest": doc, "reserved_count": len(entries)}


def frozen_buffer(repo, *, marker_commit, buffer_path, phase):
    """Prove buffer membership from the marker's actual Git parent, not HEAD."""
    inactive_gate()
    if phase not in PHASES:
        fail("invalid buffer phase")
    frozen, _ = marker_context(repo, marker_commit, phase)
    doc = json_at(repo, frozen, buffer_path)
    if not isinstance(doc, dict) or set(doc) != {
            "schema", "schema_version", "phase", "snapshot_id",
            "capacity", "items", "buffer_id"}:
        fail("invalid immutable buffer document")
    if (doc["schema"] != SCHEMA or doc["schema_version"] != 1
            or doc["phase"] != phase or doc["capacity"] != CAPACITY
            or not isinstance(doc["items"], list)
            or not 1 <= len(doc["items"]) <= CAPACITY
            or not HEX64.fullmatch(str(doc["snapshot_id"]))
            or not HEX64.fullmatch(str(doc["buffer_id"]))):
        fail("bad frozen buffer gate/capacity/identity")
    body = {k: v for k, v in doc.items() if k != "buffer_id"}
    if canonical_sha256(body) != doc["buffer_id"]:
        fail("buffer content hash mismatch")
    if buffer_path != f"{BUFFER_PREFIX}/{phase}/{doc['snapshot_id']}/{doc['buffer_id']}.json":
        fail("buffer path not exactly bound")
    verified = [_entry(repo, frozen, phase, x["work_path"]) for x in doc["items"]]
    if verified != doc["items"]:
        fail("work SHA, scope or item bindings differ from immutable marker parent")
    _ordered_unique(verified)
    if any(x["snapshot_id"] != doc["snapshot_id"] for x in verified):
        fail("mixed snapshot buffer")
    # Individual authorizations share the exact marker parent and NEVER depend
    # on a sibling's submission, receipt, rejection or final acceptance.
    for x in verified:
        if phase == "research":
            a = research_authority(repo, marker_commit, x["work_path"])
            if (a["assignment_id"], a["appid"]) != (x["assignment_id"], x["appid"]):
                fail("Research buffer authority mismatch")
        else:
            assembly_authority(repo, marker_commit, x["work_path"])
            prepare_assembly(repo, marker_commit=marker_commit,
                             plan_path=x["work_path"], check_collisions=False)
    return doc


def _member(doc, work_path):
    for x in doc["items"]:
        if x["work_path"] == work_path:
            return x
    fail("worker requested an unprepared item/retry outside frozen buffer")


def receive_buffered_research(repo, *, marker_commit, buffer_path, work_path, package_commit):
    doc = frozen_buffer(repo, marker_commit=marker_commit, buffer_path=buffer_path,
                        phase="research")
    _member(doc, work_path)
    # Previous Research acceptance/rejection is deliberately never inspected.
    return receive_research(repo, marker_commit=marker_commit,
                            prepared_work_path=work_path, package_commit=package_commit)


def stage_assembly_buffer(repo, *, marker_commit, buffer_path):
    """Return one atomic create-only proposal for all accepted Research members."""
    doc = frozen_buffer(repo, marker_commit=marker_commit, buffer_path=buffer_path,
                        phase="assembly")
    files = {}
    assignment_by_work_path = {}
    for entry in doc["items"]:
        work_path = entry["work_path"]
        proposal = prepare_assembly(repo, marker_commit=marker_commit, plan_path=work_path,
                                    check_collisions=False)
        for path, value in proposal["files"].items():
            if path in files:
                fail("two Assembly assignments collide")
            files[path] = value
        assignment_by_work_path[work_path] = proposal["assignment_path"]
    no_collisions(repo, files)
    return {"files": files, "assignments": assignment_by_work_path,
            "status": "staged_inactive", "canonical_acceptance": False}


def staged_assembly_member(repo, *, marker_commit, buffer_path, work_path, staging_commit):
    """Read exact already-prepared Stage-B work; sibling A receipt is irrelevant."""
    doc = frozen_buffer(repo, marker_commit=marker_commit, buffer_path=buffer_path,
                        phase="assembly")
    _member(doc, work_path)
    if not first_parent_contains(repo, marker_commit, staging_commit):
        fail("staged Assembly work is not descended from frozen marker")
    # Stage one immutable batch of all GitHub-owned assignments + states.
    expected = {}
    assignment_path = None
    for entry in doc["items"]:
        proposal = prepare_assembly(repo, marker_commit=marker_commit,
                                    plan_path=entry["work_path"], check_collisions=False)
        expected.update(proposal["files"])
        if entry["work_path"] == work_path:
            assignment_path = proposal["assignment_path"]
    require_only_new(repo, staging_commit, list(expected))
    for path, value in expected.items():
        raw = file_at(repo, staging_commit, path)
        if raw != bytes_json(value) or blob_for(raw) != blob(repo, staging_commit, path):
            fail("staged assignment/state bytes differ from GitHub proposal")
    return strict_json(file_at(repo, staging_commit, assignment_path))


def inspect_buffered_assembly_candidate(repo, *, marker_commit, buffer_path,
                                        work_path, staging_commit, result_commit):
    """Offline strict interface check, NOT final canonical strict Dossier acceptance."""
    work = staged_assembly_member(repo, marker_commit=marker_commit,
                                  buffer_path=buffer_path, work_path=work_path,
                                  staging_commit=staging_commit)
    if not first_parent_contains(repo, staging_commit, result_commit):
        fail("Assembly result predates staging")
    result_path = work["output_path"]
    require_only_new(repo, result_commit, [result_path])
    raw = file_at(repo, result_commit, result_path)
    if blob_for(raw) != blob(repo, result_commit, result_path):
        fail("Assembly candidate blob mismatch")
    result = strict_json(raw)
    receipt = work["accepted_research"]
    source = strict_json(file_at(
        repo, receipt["research_package_git_commit"], receipt["research_package_path"]))
    validate_assembly_result(result, work, source)
    return {"status": "candidate_submitted_pending_github_final_strict_ingest",
            "canonical_dossier_accepted": False, "result_path": result_path}

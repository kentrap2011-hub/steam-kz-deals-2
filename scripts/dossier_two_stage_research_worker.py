#!/usr/bin/env python3
"""INACTIVE Research worker's pure frozen-authority/transport interface.

No CLI, HTTP, semantic processing, Git writes, production-data fixture, retry
engine, inbox scanner or acceptance decision. Called only in offline tests or
after a separately authorized future activation/integration.
"""
import copy
import hashlib
from functools import lru_cache
from pathlib import Path

from dossier_two_stage_async_buffer import frozen_buffer, inactive_gate
from dossier_two_stage_contract_guard import canonical_sha256, validate_research
from dossier_two_stage_staging import (
    blob, blob_for, bytes_json, exists, file_at, first_parent_contains,
    git, marker_context, receipt_paths, require_only_new, research_authority,
    strict_json, validate_physical_sources, fail,
)

PROMPT_PATH = "config/dossier_two_stage_research_semantic_worker_prompt.md"
ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=32)
def _immutable_research_batch(repo, marker_commit, buffer_path, local_prompt_sha):
    """Return only independently GitHub-prepared work, in frozen manifest order.

    Exact prompt bytes are bound by the marker's *actual first parent*. No
    acknowledgement, current queue head, slot limit or accept receipt is read.
    """
    manifest = frozen_buffer(repo, marker_commit=marker_commit,
                             buffer_path=buffer_path, phase="research")
    parent, nonce = marker_context(repo, marker_commit, "research")
    source_prompt = file_at(repo, parent, PROMPT_PATH)
    if not source_prompt or source_prompt != (ROOT / PROMPT_PATH).read_bytes():
        fail("Research semantic prompt not identical to actual marker parent")
    prompt_blob = blob(repo, parent, PROMPT_PATH)
    if blob_for(source_prompt) != prompt_blob:
        fail("Research prompt Git blob mismatch")
    result = []
    for entry in manifest["items"]:
        assignment = research_authority(repo, marker_commit, entry["work_path"])
        if (entry["work_blob_sha"] != blob(repo, parent, entry["work_path"])
                or assignment["research_marker_anchor_commit"] != marker_commit
                or assignment["research_marker_nonce"] != nonce):
            fail("Research original frozen work or marker changed")
        result.append({
            "work_path": entry["work_path"],
            "work_blob_sha": entry["work_blob_sha"],
            "assignment": assignment,
            "output_path": receipt_paths(assignment)["candidate"],
        })
    return {
        "marker_commit": marker_commit,
        "marker_parent": parent,
        "marker_nonce": nonce,
        "buffer_path": buffer_path,
        "buffer_blob_sha": blob(repo, parent, buffer_path),
        "buffer_id": manifest["buffer_id"],
        "prompt_path": PROMPT_PATH,
        "prompt_blob_sha": prompt_blob,
        "prompt_sha256": hashlib.sha256(source_prompt).hexdigest(),
        "items": result,
    }


def frozen_research_batch(repo, *, marker_commit, buffer_path):
    """Re-use the same verified immutable Git-parent proof within an invocation.

    Each caller gets its own copy. This cache cannot create authority: the key
    includes exact marker, buffer path, repository and local prompt content.
    A separate inactive gate is rechecked on every entry.
    """
    inactive_gate()
    prompt_digest = hashlib.sha256((ROOT / PROMPT_PATH).read_bytes()).hexdigest()
    result = _immutable_research_batch(
        str(Path(repo).resolve()), marker_commit, buffer_path, prompt_digest)
    return copy.deepcopy(result)


def _exact_item(repo, marker_commit, buffer_path, work_path):
    batch = frozen_research_batch(repo, marker_commit=marker_commit,
                                  buffer_path=buffer_path)
    for item in batch["items"]:
        if item["work_path"] == work_path:
            return item
    fail("Research work is not in exact frozen manifest")


def _validated_bytes(item, document):
    if not isinstance(document, dict):
        fail("Research must provide one JSON object")
    validate_research(document, expected_assignment=item["assignment"])
    validate_physical_sources(document)
    return bytes_json(document)


def inspect_existing_research_transport(repo, *, marker_commit, buffer_path,
                                        work_path, expected_bytes=None):
    """Check original immutable create-only bytes; never claim GH acceptance.

    A replay is 'submitted_unaccepted' only if the candidate was introduced
    alone on marker-first-parent ancestry and has not subsequently changed.
    """
    item = _exact_item(repo, marker_commit, buffer_path, work_path)
    path = item["output_path"]
    if not exists(repo, "HEAD", path):
        return {"status": "not_submitted", "output_path": path}
    if not first_parent_contains(repo, marker_commit, "HEAD"):
        fail("Research transport HEAD outside frozen first-parent lineage")
    introduced = git(repo, "log", "--first-parent", "--diff-filter=A",
                     "--format=%H", "HEAD", "--", path).stdout.decode().splitlines()
    if len(introduced) != 1:
        fail("Research original create-only introduction unprovable")
    commit = introduced[0]
    original_parent = require_only_new(repo, commit, [path])
    if not first_parent_contains(repo, marker_commit, original_parent):
        fail("Research transport not descended from frozen marker")
    raw = file_at(repo, commit, path)
    original_blob = blob(repo, commit, path)
    if (blob_for(raw) != original_blob
            or blob(repo, "HEAD", path) != original_blob
            or file_at(repo, "HEAD", path) != raw):
        fail("Research original submitted bytes were overwritten")
    package = strict_json(raw)
    _validated_bytes(item, package)
    if expected_bytes is not None and raw != expected_bytes:
        fail("Research create-only path collision with different raw bytes")
    return {
        "status": "submitted_unaccepted",
        "output_path": path,
        "research_package_git_commit": commit,
        "research_package_blob_sha": original_blob,
        "research_package_raw_sha256": hashlib.sha256(raw).hexdigest(),
        "research_package_sha256": canonical_sha256(package),
    }


def prepare_research_transport(repo, *, marker_commit, buffer_path,
                               work_path, document):
    """Validate one semantic result and yield its sole authorized transport.

    Does NOT create/modify files or guarantee GitHub acceptance. Caller must
    perform an atomic create-only Git submission and check actual commit/blob.
    """
    item = _exact_item(repo, marker_commit, buffer_path, work_path)
    raw = _validated_bytes(item, document)
    previous = inspect_existing_research_transport(
        repo, marker_commit=marker_commit, buffer_path=buffer_path,
        work_path=work_path, expected_bytes=raw)
    if previous["status"] == "submitted_unaccepted":
        return {**previous, "transport_bytes": None}
    return {
        "status": "ready_for_create_only_submission",
        "output_path": item["output_path"],
        "transport_bytes": raw,
        "expected_git_blob_sha": blob_for(raw),
        "expected_raw_sha256": hashlib.sha256(raw).hexdigest(),
        "expected_canonical_sha256": canonical_sha256(document),
        "canonical_acceptance": False,
    }

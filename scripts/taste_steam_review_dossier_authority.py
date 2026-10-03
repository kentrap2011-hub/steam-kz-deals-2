#!/usr/bin/env python3
"""Git-backed frozen invocation authority for Taste Steam review Dossier work."""

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier import canonical_sha256


COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
NONCE_RE = re.compile(r"^[0-9a-f]{32}$")
MARKER_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-RUN-START-MARKER-V1"
REFERENCE_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-RUN-START-REFERENCE-V1"
AUTHORITY_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-FROZEN-AUTHORITY-V1"
WORKER_INDEX_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2"
WORKER_GROUP_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1"


def _git(repo, *args, check=True):
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode:
        raise ValueError(
            f"Dossier Git authority proof failed: git {' '.join(args)}: "
            f"{(proc.stderr or proc.stdout).strip()}"
        )
    return proc


def _text(repo, *args):
    return _git(repo, *args).stdout.strip()


def _relative(repo, path):
    repo = Path(repo).resolve()
    value = Path(path)
    if not value.is_absolute():
        value = repo / value
    try:
        return value.resolve().relative_to(repo).as_posix()
    except ValueError as exc:
        raise ValueError("Dossier authority path must stay inside the canonical checkout") from exc


def _bytes_at(repo, commit, relative_path):
    proc = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        raise ValueError(
            f"Dossier frozen authority snapshot is missing {relative_path} at {commit}"
        )
    return proc.stdout


def _json_at(repo, commit, relative_path, label):
    try:
        return json.loads(_bytes_at(repo, commit, relative_path).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Dossier frozen authority {label} is not valid JSON") from exc


def file_blob_sha_at_commit(commit, relative_path, repo_root=Path(".")):
    repo = Path(repo_root).resolve()
    commit = str(commit or "").lower()
    if not COMMIT_SHA_RE.fullmatch(commit):
        raise ValueError("Dossier frozen authority commit is invalid")
    relative = _relative(repo, relative_path)
    blob_sha = _text(repo, "rev-parse", f"{commit}:{relative}").lower()
    if not COMMIT_SHA_RE.fullmatch(blob_sha):
        raise ValueError(f"Dossier frozen authority blob is invalid for {relative}")
    return blob_sha


def commit_parent(commit, repo_root=Path(".")):
    repo = Path(repo_root).resolve()
    commit = str(commit or "").lower()
    if not COMMIT_SHA_RE.fullmatch(commit):
        raise ValueError("Dossier run-start anchor commit is invalid")
    parts = _text(repo, "rev-list", "--parents", "-n", "1", commit).split()
    if len(parts) != 2 or parts[0] != commit:
        raise ValueError("Dossier run-start anchor must be a single-parent Git commit")
    return parts[1]


def commit_committer_time_utc(commit, repo_root=Path(".")):
    repo = Path(repo_root).resolve()
    raw = _text(repo, "show", "-s", "--format=%cI", str(commit))
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Dossier run-start marker Git time is invalid") from exc
    if parsed.tzinfo is None:
        raise ValueError("Dossier run-start marker Git time must be timezone-aware")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def commit_is_ancestor(older, newer, repo_root=Path(".")):
    if not older or not newer:
        return False
    if older == newer:
        return True
    return _git(
        Path(repo_root).resolve(),
        "merge-base",
        "--is-ancestor",
        str(older),
        str(newer),
        check=False,
    ).returncode == 0


def commit_is_first_parent_ancestor(older, newer, repo_root=Path(".")):
    repo = Path(repo_root).resolve()
    older = str(older or "").lower()
    newer = str(newer or "").lower()
    if not COMMIT_SHA_RE.fullmatch(older) or not COMMIT_SHA_RE.fullmatch(newer):
        return False
    if older == newer:
        return True
    return older in {
        value
        for value in _text(repo, "rev-list", "--first-parent", newer).splitlines()
        if value
    }


def result_introduction_commit(artifact_path, repo_root=Path(".")):
    repo = Path(repo_root).resolve()
    artifact = Path(artifact_path)
    relative = _relative(repo, artifact)
    absolute = repo / relative
    if not absolute.is_file():
        raise ValueError("Dossier result transport is missing from the canonical checkout")
    raw = absolute.read_bytes()
    commits = [
        value
        for value in _text(repo, "log", "--diff-filter=A", "--format=%H", "--", relative).splitlines()
        if value
    ]
    for commit in commits:
        try:
            if _bytes_at(repo, commit, relative) == raw:
                return commit
        except ValueError:
            continue
    raise ValueError("Dossier result lacks a durable immutable Git introduction commit")


def run_start_marker_path(nonce, inbox_dir="data/ai_inbox/taste_steam_review_dossiers"):
    nonce = str(nonce or "").lower()
    if not NONCE_RE.fullmatch(nonce):
        raise ValueError("Dossier run-start nonce is invalid")
    return Path(inbox_dir) / "run_starts" / f"{nonce}.json"


def _validate_marker_doc(marker_doc):
    if not isinstance(marker_doc, dict):
        raise ValueError("Dossier run-start marker must be a JSON object")
    if set(marker_doc) != {"schema", "schema_version", "run_start_nonce"}:
        raise ValueError("Dossier run-start marker field set is invalid")
    if marker_doc.get("schema") != MARKER_SCHEMA or marker_doc.get("schema_version") != 1:
        raise ValueError("Dossier run-start marker schema is unsupported")
    nonce = str(marker_doc.get("run_start_nonce") or "").lower()
    if not NONCE_RE.fullmatch(nonce):
        raise ValueError("Dossier run-start marker nonce is invalid")
    return nonce


def _validate_reference(reference):
    if not isinstance(reference, dict):
        raise ValueError("Dossier frozen run-start reference is missing")
    expected = {
        "schema",
        "schema_version",
        "run_start_anchor_commit",
        "run_start_nonce",
    }
    if set(reference) != expected:
        raise ValueError("Dossier frozen run-start reference field set is invalid")
    if reference.get("schema") != REFERENCE_SCHEMA or reference.get("schema_version") != 1:
        raise ValueError("Dossier frozen run-start reference schema is unsupported")
    anchor = str(reference.get("run_start_anchor_commit") or "").lower()
    nonce = str(reference.get("run_start_nonce") or "").lower()
    if not COMMIT_SHA_RE.fullmatch(anchor):
        raise ValueError("Dossier frozen run-start anchor commit is invalid")
    if not NONCE_RE.fullmatch(nonce):
        raise ValueError("Dossier frozen run-start nonce is invalid")
    return anchor, nonce


def _validate_descriptor_identity(descriptor):
    if (
        not isinstance(descriptor, dict)
        or descriptor.get("schema") != WORKER_GROUP_SCHEMA
        or descriptor.get("schema_version") != 1
    ):
        raise ValueError("Dossier frozen worker descriptor schema is invalid")
    items = descriptor.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("Dossier frozen worker descriptor items are missing")
    if descriptor.get("items_sha256") != canonical_sha256(items):
        raise ValueError("Dossier frozen worker descriptor items hash mismatch")
    appids = [str(item.get("appid") or "") for item in items if isinstance(item, dict)]
    if appids != descriptor.get("appids") or len(appids) != len(items):
        raise ValueError("Dossier frozen worker descriptor appid order mismatch")
    identity = {
        "snapshot_id": descriptor.get("snapshot_id"),
        "prepared_required_sha256": descriptor.get("prepared_required_sha256"),
        "sequence": descriptor.get("sequence"),
        "start_index": descriptor.get("start_index"),
        "end_index_exclusive": descriptor.get("end_index_exclusive"),
        "appids": descriptor.get("appids"),
        "items_sha256": descriptor.get("items_sha256"),
        "scope_source": descriptor.get("scope_source"),
        "source_queue_sha256": descriptor.get("source_queue_sha256"),
    }
    if descriptor.get("group_sha256") != canonical_sha256(identity):
        raise ValueError("Dossier frozen worker descriptor group hash mismatch")


def _load_authority_view(authority_commit, sequence, contract, repo):
    index_path = _relative(repo, contract["paths"]["worker_index"])
    work_path = _relative(repo, contract["paths"]["work_manifest"])
    index = _json_at(repo, authority_commit, index_path, "worker index")
    manifest = _json_at(repo, authority_commit, work_path, "work manifest")

    if (
        not isinstance(index, dict)
        or index.get("schema") != WORKER_INDEX_SCHEMA
        or index.get("schema_version") != 2
    ):
        raise ValueError("Dossier frozen worker index is missing or unsupported")
    if not isinstance(manifest, dict) or manifest.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-WORK-V2":
        raise ValueError("Dossier frozen canonical work manifest is missing or unsupported")
    if manifest.get("schema_version") != 2:
        raise ValueError("Dossier frozen canonical work manifest version is unsupported")

    pending = index.get("pending_group_sequences")
    if not isinstance(pending, list) or not pending:
        raise ValueError("Dossier run-start authority has no pending semantic work")
    if any(not isinstance(value, int) or value <= 0 for value in pending):
        raise ValueError("Dossier frozen pending sequence projection is invalid")
    if int(sequence) not in pending:
        raise ValueError("Dossier result group was not pending at the frozen invocation boundary")
    if index.get("normal_first_pass_complete") is True:
        raise ValueError("Dossier run-start authority was already normal-first-pass complete")

    for field in (
        "snapshot_id",
        "prepared_required_sha256",
        "scope_source",
        "source_queue_sha256",
        "web_evidence_contract_binding",
    ):
        if index.get(field) != manifest.get(field):
            raise ValueError(f"Dossier frozen index/manifest binding mismatch: {field}")

    plan = manifest.get("submission_group_plan")
    if not isinstance(plan, dict) or not isinstance(plan.get("groups"), list):
        raise ValueError("Dossier frozen immutable group plan is missing")
    if (
        index.get("group_plan_sha256") != plan.get("group_plan_sha256")
        or index.get("group_count") != plan.get("group_count")
        or len(plan["groups"]) != int(index.get("group_count") or -1)
    ):
        raise ValueError("Dossier frozen group-plan projection mismatch")

    group = None
    for value in plan["groups"]:
        if isinstance(value, dict) and value.get("sequence") == int(sequence):
            group = value
            break
    if group is None:
        raise ValueError("Dossier frozen group sequence is outside the immutable plan")

    progress = manifest.get("group_progress")
    entries = progress.get("groups") if isinstance(progress, dict) else None
    if not isinstance(entries, list):
        raise ValueError("Dossier frozen group progress is missing")
    progress_entry = next(
        (
            value
            for value in entries
            if isinstance(value, dict) and value.get("sequence") == int(sequence)
        ),
        None,
    )
    if (
        progress_entry is None
        or progress_entry.get("group_sha256") != group.get("group_sha256")
        or progress_entry.get("state") != "pending"
    ):
        raise ValueError("Dossier frozen group was not canonically pending at run start")

    template = index.get("descriptor_path_template")
    if not isinstance(template, str) or not template:
        raise ValueError("Dossier frozen descriptor template is missing")
    try:
        rendered = template.format(
            snapshot_id=index["snapshot_id"],
            sequence=int(sequence),
        )
    except (KeyError, ValueError) as exc:
        raise ValueError("Dossier frozen descriptor template is invalid") from exc
    descriptor_path = _relative(repo, rendered)
    descriptor = _json_at(repo, authority_commit, descriptor_path, "worker descriptor")
    _validate_descriptor_identity(descriptor)

    expected_descriptor = {
        "schema": WORKER_GROUP_SCHEMA,
        "schema_version": 1,
        "snapshot_id": manifest["snapshot_id"],
        "prepared_required_sha256": manifest["prepared_required_sha256"],
        "group_plan_sha256": plan["group_plan_sha256"],
        "group_count": plan["group_count"],
        "web_evidence_contract_binding": manifest["web_evidence_contract_binding"],
        **group,
    }
    if descriptor != expected_descriptor:
        raise ValueError("Dossier frozen descriptor does not exactly match canonical prepared work")

    runtime_path = index.get("runtime_prompt_path")
    runtime_sha = index.get("runtime_prompt_sha256")
    runtime_revision = index.get("runtime_prompt_revision")
    if not isinstance(runtime_path, str) or not runtime_path:
        raise ValueError("Dossier frozen runtime prompt path is missing")
    if not isinstance(runtime_revision, str) or not runtime_revision:
        raise ValueError("Dossier frozen runtime prompt revision is missing")
    runtime_relative = _relative(repo, runtime_path)
    runtime_bytes = _bytes_at(repo, authority_commit, runtime_relative)
    if hashlib.sha256(runtime_bytes).hexdigest() != runtime_sha:
        raise ValueError("Dossier frozen runtime prompt hash does not match its Git bytes")

    return {
        "index": index,
        "manifest": manifest,
        "descriptor": descriptor,
        "descriptor_path": descriptor_path,
        "runtime_prompt_path": runtime_relative,
    }


def validate_run_start_marker_commit(
    anchor_commit,
    marker_path,
    marker_doc,
    *,
    contract,
    sequence,
    repo_root=Path("."),
):
    """Prove a nonce-only marker and resolve GitHub's actual marker parent as authority."""
    repo = Path(repo_root).resolve()
    anchor = str(anchor_commit or "").lower()
    if not COMMIT_SHA_RE.fullmatch(anchor):
        raise ValueError("Dossier run-start anchor commit is invalid")
    if _text(repo, "rev-parse", f"{anchor}^{{commit}}").lower() != anchor:
        raise ValueError("Dossier run-start anchor commit does not resolve exactly")

    nonce = _validate_marker_doc(marker_doc)
    parent = commit_parent(anchor, repo)
    relative_marker = _relative(repo, marker_path)
    expected_marker = _relative(
        repo,
        run_start_marker_path(nonce, contract["paths"]["submission_inbox_dir"]),
    )
    if relative_marker != expected_marker:
        raise ValueError("Dossier run-start marker path does not match its nonce identity")

    changes = [
        value
        for value in _text(
            repo,
            "diff-tree",
            "--no-commit-id",
            "--name-status",
            "-r",
            anchor,
        ).splitlines()
        if value
    ]
    if changes != [f"A\t{relative_marker}"]:
        raise ValueError("Dossier run-start anchor is not marker-only create-only transport")

    durable_doc = _json_at(repo, anchor, relative_marker, "durable run-start marker")
    if durable_doc != marker_doc:
        raise ValueError("Dossier durable run-start marker content mismatch")

    view = _load_authority_view(parent, int(sequence), contract, repo)
    proof = {
        "schema": AUTHORITY_SCHEMA,
        "schema_version": 1,
        "run_start_anchor_commit": anchor,
        "run_start_authority_commit": parent,
        "run_start_nonce": nonce,
        "run_started_at_utc": commit_committer_time_utc(anchor, repo),
        "marker_path": relative_marker,
        "snapshot_id": view["descriptor"]["snapshot_id"],
        "prepared_required_sha256": view["descriptor"]["prepared_required_sha256"],
        "group_plan_sha256": view["descriptor"]["group_plan_sha256"],
        "sequence": view["descriptor"]["sequence"],
        "group_sha256": view["descriptor"]["group_sha256"],
        "worker_index_blob_sha": file_blob_sha_at_commit(parent, contract["paths"]["worker_index"], repo),
        "worker_descriptor_blob_sha": file_blob_sha_at_commit(parent, view["descriptor_path"], repo),
        "runtime_prompt_blob_sha": file_blob_sha_at_commit(parent, view["runtime_prompt_path"], repo),
        "dossier_contract_blob_sha": file_blob_sha_at_commit(
            parent, "config/taste_steam_review_dossier_contract.json", repo
        ),
        "persistence_bridge_blob_sha": file_blob_sha_at_commit(
            parent, "config/taste_steam_review_dossier_persistence_bridge.json", repo
        ),
    }
    return proof, view


def resolve_frozen_transport_authority(
    artifact_path,
    artifact,
    contract,
    *,
    repo_root=Path("."),
):
    """Resolve one result/terminal to the exact marker-parent descriptor it was allowed to use."""
    if not isinstance(artifact, dict):
        raise ValueError("Dossier frozen transport must be a JSON object")
    reference = artifact.get("run_start_authority")
    anchor, nonce = _validate_reference(reference)
    repo = Path(repo_root).resolve()
    marker_path = run_start_marker_path(nonce, contract["paths"]["submission_inbox_dir"])
    marker_relative = _relative(repo, marker_path)
    marker_doc = _json_at(repo, anchor, marker_relative, "run-start marker")

    sequence = artifact.get("sequence")
    if not isinstance(sequence, int) or sequence <= 0:
        raise ValueError("Dossier frozen transport sequence is invalid")
    proof, view = validate_run_start_marker_commit(
        anchor,
        marker_path,
        marker_doc,
        contract=contract,
        sequence=sequence,
        repo_root=repo,
    )
    descriptor = view["descriptor"]

    for field, value in descriptor.items():
        if field in {"schema", "schema_version"}:
            continue
        if artifact.get(field) != value:
            raise ValueError(f"Dossier frozen transport descriptor mismatch: {field}")

    introduction = result_introduction_commit(artifact_path, repo)
    result_parent = commit_parent(introduction, repo)
    if not commit_is_ancestor(anchor, result_parent, repo):
        raise ValueError("Dossier run-start marker does not predate result transport")
    if not commit_is_first_parent_ancestor(anchor, result_parent, repo):
        raise ValueError("Dossier run-start marker is not on the result mainline first-parent history")

    proof = {
        **proof,
        "result_introduction_commit": introduction,
    }
    return proof, view


def frozen_consumption_key(proof):
    if not isinstance(proof, dict):
        raise ValueError("Dossier frozen authority proof is missing")
    return (
        str(proof.get("run_start_anchor_commit") or ""),
        str(proof.get("snapshot_id") or ""),
        int(proof.get("sequence") or 0),
        str(proof.get("group_sha256") or ""),
    )

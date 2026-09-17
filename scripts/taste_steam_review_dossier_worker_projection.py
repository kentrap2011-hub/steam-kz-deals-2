#!/usr/bin/env python3
"""GitHub-owned compact read projection for the Steam-review-dossier worker."""
import copy
import json
import shutil
from pathlib import Path

from taste_steam_review_dossier import atomic_write_json, canonical_sha256
from taste_steam_review_dossier_daily import (
    expected_group_sequence,
    validate_group_plan,
    validate_manifest,
)

WORKER_INDEX_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V1"
WORKER_GROUP_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1"


def _projection_contract(contract):
    projection = contract.get("worker_read_projection") or {}
    if projection.get("status") != "active" or projection.get("owner") != "github_control_plane":
        raise ValueError("compact dossier worker projection contract is missing or inactive")
    if projection.get("index_schema") != WORKER_INDEX_SCHEMA or projection.get("group_schema") != WORKER_GROUP_SCHEMA:
        raise ValueError("compact dossier worker projection schema binding is invalid")
    paths = contract.get("paths") or {}
    for key in ("work_manifest", "worker_index", "worker_groups_root"):
        if not isinstance(paths.get(key), str) or not paths[key]:
            raise ValueError(f"compact dossier worker projection path is missing: {key}")
    template = projection.get("descriptor_path_template")
    expected_template = paths["worker_groups_root"].rstrip("/") + "/{snapshot_id}/g{sequence:06d}.json"
    if template != expected_template:
        raise ValueError("compact dossier worker descriptor path template is invalid")
    return projection


def _serialized_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _manifest_binding(manifest):
    binding = manifest.get("web_evidence_contract_binding")
    if not isinstance(binding, dict) or not binding:
        raise ValueError("canonical manifest is missing the active web-evidence compatibility binding")
    return copy.deepcopy(binding)


def build_worker_projection(manifest, contract):
    """Derive the complete worker read projection only from canonical manifest state."""
    validate_manifest(manifest, contract)
    plan = validate_group_plan(manifest, contract, required=True)
    projection = _projection_contract(contract)
    binding = _manifest_binding(manifest)
    if manifest.get("sampling_policy") != contract.get("sampling"):
        raise ValueError("canonical manifest sampling policy no longer matches the active contract")

    index = {
        "schema": WORKER_INDEX_SCHEMA,
        "schema_version": 1,
        "work_manifest_path": contract["paths"]["work_manifest"],
        "snapshot_id": manifest["snapshot_id"],
        "prepared_for_date": manifest["prepared_for_date"],
        "prepared_required_sha256": manifest["prepared_required_sha256"],
        "group_plan_sha256": plan["group_plan_sha256"],
        "group_count": plan["group_count"],
        "canonical_expected_sequence": expected_group_sequence(manifest, contract),
        "prepared_required_count": manifest["prepared_required_count"],
        "completed_required_count": manifest["completed_required_count"],
        "remaining_required_count": manifest["remaining_required_count"],
        "full_backlog_complete": manifest["full_backlog_complete"],
        "ttl_days": manifest["ttl_days"],
        "sampling_policy": copy.deepcopy(manifest["sampling_policy"]),
        "web_evidence_contract_binding": binding,
        "scope_source": manifest["scope_source"],
        "source_queue_path": manifest["source_queue_path"],
        "source_queue_sha256": manifest["source_queue_sha256"],
        "descriptor_path_template": projection["descriptor_path_template"],
    }

    descriptors = []
    for group in plan["groups"]:
        descriptor = {
            "schema": WORKER_GROUP_SCHEMA,
            "schema_version": 1,
            "snapshot_id": manifest["snapshot_id"],
            "prepared_required_sha256": manifest["prepared_required_sha256"],
            "group_plan_sha256": plan["group_plan_sha256"],
            "group_count": plan["group_count"],
            "web_evidence_contract_binding": copy.deepcopy(binding),
            **copy.deepcopy(group),
        }
        descriptors.append(descriptor)
    validate_worker_projection(index, descriptors, manifest, contract)
    return index, descriptors


def validate_worker_projection(index, descriptors, manifest, contract):
    """Fail closed unless projection content exactly equals the canonical derivation."""
    validate_manifest(manifest, contract)
    plan = validate_group_plan(manifest, contract, required=True)
    projection = _projection_contract(contract)
    binding = _manifest_binding(manifest)
    if not isinstance(index, dict) or index.get("schema") != WORKER_INDEX_SCHEMA or index.get("schema_version") != 1:
        raise ValueError("compact dossier worker index is missing or unsupported")
    if not isinstance(descriptors, list) or len(descriptors) != plan["group_count"]:
        raise ValueError("compact dossier worker descriptor set is incomplete")

    expected_index = {
        "schema": WORKER_INDEX_SCHEMA,
        "schema_version": 1,
        "work_manifest_path": contract["paths"]["work_manifest"],
        "snapshot_id": manifest["snapshot_id"],
        "prepared_for_date": manifest["prepared_for_date"],
        "prepared_required_sha256": manifest["prepared_required_sha256"],
        "group_plan_sha256": plan["group_plan_sha256"],
        "group_count": plan["group_count"],
        "canonical_expected_sequence": expected_group_sequence(manifest, contract),
        "prepared_required_count": manifest["prepared_required_count"],
        "completed_required_count": manifest["completed_required_count"],
        "remaining_required_count": manifest["remaining_required_count"],
        "full_backlog_complete": manifest["full_backlog_complete"],
        "ttl_days": manifest["ttl_days"],
        "sampling_policy": copy.deepcopy(manifest["sampling_policy"]),
        "web_evidence_contract_binding": binding,
        "scope_source": manifest["scope_source"],
        "source_queue_path": manifest["source_queue_path"],
        "source_queue_sha256": manifest["source_queue_sha256"],
        "descriptor_path_template": projection["descriptor_path_template"],
    }
    if index != expected_index:
        raise ValueError("compact dossier worker index does not exactly match canonical manifest state")

    for sequence, (actual, group) in enumerate(zip(descriptors, plan["groups"]), 1):
        expected = {
            "schema": WORKER_GROUP_SCHEMA,
            "schema_version": 1,
            "snapshot_id": manifest["snapshot_id"],
            "prepared_required_sha256": manifest["prepared_required_sha256"],
            "group_plan_sha256": plan["group_plan_sha256"],
            "group_count": plan["group_count"],
            "web_evidence_contract_binding": copy.deepcopy(binding),
            **copy.deepcopy(group),
        }
        if actual != expected:
            raise ValueError(f"compact dossier worker descriptor mismatch at sequence {sequence}")
        if actual["sequence"] != sequence:
            raise ValueError(f"compact dossier worker descriptor sequence mismatch at {sequence}")
        if actual["items_sha256"] != canonical_sha256(actual["items"]):
            raise ValueError(f"compact dossier worker descriptor items hash mismatch at {sequence}")
        identity = {
            "snapshot_id": actual["snapshot_id"],
            "prepared_required_sha256": actual["prepared_required_sha256"],
            "sequence": actual["sequence"],
            "start_index": actual["start_index"],
            "end_index_exclusive": actual["end_index_exclusive"],
            "appids": actual["appids"],
            "items_sha256": actual["items_sha256"],
            "scope_source": actual["scope_source"],
            "source_queue_sha256": actual["source_queue_sha256"],
        }
        if actual["group_sha256"] != canonical_sha256(identity):
            raise ValueError(f"compact dossier worker descriptor group hash mismatch at {sequence}")
    return True


def _descriptor_path(contract, snapshot_id, sequence):
    template = _projection_contract(contract)["descriptor_path_template"]
    return Path(template.format(snapshot_id=snapshot_id, sequence=sequence))


def validate_worker_projection_files(manifest, contract, *, index_path=None):
    index_path = Path(index_path or contract["paths"]["worker_index"])
    if not index_path.exists():
        raise ValueError("compact dossier worker index file is missing")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    plan = validate_group_plan(manifest, contract, required=True)
    descriptors = []
    for sequence in range(1, plan["group_count"] + 1):
        path = _descriptor_path(contract, manifest["snapshot_id"], sequence)
        if not path.exists():
            raise ValueError(f"compact dossier worker descriptor file is missing at sequence {sequence}")
        doc = json.loads(path.read_text(encoding="utf-8"))
        if path.read_text(encoding="utf-8") != _serialized_json(doc):
            raise ValueError(f"compact dossier worker descriptor serialization is noncanonical at sequence {sequence}")
        descriptors.append(doc)
    validate_worker_projection(index, descriptors, manifest, contract)
    return index, descriptors


def write_worker_projection(manifest, contract, *, index_path=None, groups_root=None):
    """Synchronize the GitHub-owned projection while preserving same-snapshot descriptor bytes."""
    index, descriptors = build_worker_projection(manifest, contract)
    index_path = Path(index_path or contract["paths"]["worker_index"])
    groups_root = Path(groups_root or contract["paths"]["worker_groups_root"])
    snapshot_id = manifest["snapshot_id"]
    target_dir = groups_root / snapshot_id

    groups_root.mkdir(parents=True, exist_ok=True)
    for child in list(groups_root.iterdir()):
        if child.name == snapshot_id:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            raise ValueError(f"unexpected non-directory worker projection entry: {child.as_posix()}")
    target_dir.mkdir(parents=True, exist_ok=True)

    expected_names = set()
    for descriptor in descriptors:
        path = _descriptor_path(contract, snapshot_id, descriptor["sequence"])
        if path.parent != target_dir:
            raise ValueError("compact dossier worker descriptor resolved outside active snapshot directory")
        expected_names.add(path.name)
        expected_text = _serialized_json(descriptor)
        if path.exists():
            if path.read_text(encoding="utf-8") != expected_text:
                raise ValueError(
                    f"same-snapshot compact dossier worker descriptor changed at sequence {descriptor['sequence']}"
                )
        else:
            atomic_write_json(path, descriptor)

    unexpected = sorted(
        child.name for child in target_dir.iterdir()
        if child.is_file() and child.name not in expected_names
    )
    if unexpected:
        raise ValueError(f"unexpected same-snapshot compact dossier worker descriptors: {unexpected}")
    if any(child.is_dir() for child in target_dir.iterdir()):
        raise ValueError("unexpected nested compact dossier worker descriptor directory")

    atomic_write_json(index_path, index)
    read_index, read_descriptors = validate_worker_projection_files(manifest, contract, index_path=index_path)
    return {
        "index": read_index,
        "descriptors": read_descriptors,
        "index_path": index_path.as_posix(),
        "descriptor_count": len(read_descriptors),
        "snapshot_id": snapshot_id,
    }

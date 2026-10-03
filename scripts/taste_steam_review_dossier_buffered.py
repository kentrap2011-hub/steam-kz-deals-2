#!/usr/bin/env python3
"""GitHub-owned non-blocking buffered transport for Steam review dossiers."""
import copy
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier import (
    atomic_write_json,
    canonical_sha256,
    dossier_path,
    load_dossier_if_present,
)
from taste_steam_review_dossier_authority import (
    frozen_consumption_key,
    resolve_frozen_transport_authority,
)
from taste_steam_review_dossier_compact_provenance import (
    load_compact_provenance_policy,
    validate_compact_provenance,
)
from taste_steam_review_dossier_daily import (
    BUFFER_GROUP_SCHEMA,
    progress_fields,
    validate_group_plan,
    validate_manifest,
)
from taste_steam_review_dossier_group_progress import (
    ACCEPTED,
    FAILED,
    accepted_contiguous_prefix_item_count,
    ensure_group_progress,
    next_pending_sequence,
    pending_sequences,
    set_group_state,
)
from taste_steam_review_dossier_strict import (
    current_worker_contract_binding,
    load_web_evidence_contract,
    load_worker_schema,
    validate_dossiers_against_expected_items,
)
from taste_steam_review_dossier_terminal import (
    current_snapshot_terminal_receipts,
    expected_terminal_receipt_path,
    validate_terminal_receipt,
)


_BUFFER_NAME_RE = re.compile(r"^(?P<snapshot>[0-9a-f]{64})--g(?P<sequence>[0-9]{6})--(?P<group>[0-9a-f]{64})\.json$")
_TERMINAL_NAME_RE = re.compile(
    r"^(?P<snapshot>[0-9a-f]{64})--g(?P<sequence>[0-9]{6})--"
    r"(?P<group>[0-9a-f]{64})--terminal\.json$"
)
_DEFAULT_FAILED_QUARANTINE = Path("data/quarantine/taste_steam_review_dossier_inbox/failed_group")
_DEFAULT_FAILURE_AUDIT = Path("data/audit/taste_steam_review_dossier_group_failures.jsonl")
_DEFAULT_RETRYABLE_REJECTION_QUARANTINE = Path("data/quarantine/taste_steam_review_dossier_inbox/retryable_transport")
_DEFAULT_RETRYABLE_REJECTION_AUDIT = Path("data/audit/taste_steam_review_dossier_transport_rejections.jsonl")
_DEFAULT_TERMINAL_RECEIPT_ARCHIVE = Path("data/audit/taste_steam_review_dossier_terminal_receipts")
_DEFAULT_FROZEN_AUTHORITY_AUDIT = Path("data/audit/taste_steam_review_dossier_frozen_invocations.jsonl")


def expected_buffer_path(descriptor, contract):
    inbox = Path(contract["paths"]["submission_inbox_dir"])
    return inbox / (
        f"{descriptor['snapshot_id']}--g{int(descriptor['sequence']):06d}--"
        f"{descriptor['group_sha256']}.json"
    )


def _descriptor_fields():
    return (
        "snapshot_id",
        "prepared_required_sha256",
        "sequence",
        "start_index",
        "end_index_exclusive",
        "items",
        "appids",
        "items_sha256",
        "group_sha256",
        "scope_source",
        "source_queue_sha256",
    )


def validate_buffer_artifact(artifact, descriptor, manifest, contract):
    """Validate one buffered group exactly against its immutable descriptor."""
    if not isinstance(artifact, dict):
        raise ValueError("buffered dossier group must be an object")
    if artifact.get("schema") != BUFFER_GROUP_SCHEMA or artifact.get("schema_version") != 1:
        raise ValueError("unsupported buffered dossier group schema")
    for field in _descriptor_fields():
        if artifact.get(field) != descriptor.get(field):
            raise ValueError(f"buffered dossier group identity mismatch: {field}")
    if artifact.get("items_sha256") != canonical_sha256(artifact.get("items")):
        raise ValueError("buffered dossier group items_sha256 mismatch")
    docs = artifact.get("dossiers")
    if not isinstance(docs, list):
        raise ValueError("buffered dossier group must contain dossiers list")
    actual_appids = [str(doc.get("appid") or "") if isinstance(doc, dict) else "" for doc in docs]
    if actual_appids != descriptor["appids"] or len(actual_appids) != len(set(actual_appids)):
        raise ValueError("buffered dossier group dossiers must exactly cover planned appids in order")
    docs = validate_dossiers_against_expected_items(
        docs,
        descriptor["items"],
        contract,
        expected_ttl_days=manifest["ttl_days"],
    )
    compact_policy = load_compact_provenance_policy()
    for doc in docs:
        validate_compact_provenance(doc, compact_policy)
    return docs


def _current_snapshot_candidates(buffer_dir, snapshot_id):
    """Return current-snapshot group files keyed by sequence; old snapshots are inert."""
    root = Path(buffer_dir)
    candidates = {}
    malformed = []
    if not root.exists():
        return candidates, malformed
    prefix = f"{snapshot_id}--g"
    for path in sorted(root.glob("*.json")):
        name = path.name
        if not name.startswith(prefix):
            continue
        # Terminal receipts share the inbox and have their own strict scanner.
        # Never reinterpret them as malformed/alternate Dossier candidates.
        if name.endswith("--terminal.json"):
            continue
        match = _BUFFER_NAME_RE.fullmatch(name)
        if not match or match.group("snapshot") != snapshot_id:
            partial = re.match(rf"^{re.escape(snapshot_id)}--g([0-9]{{6}})--", name)
            if partial:
                candidates.setdefault(int(partial.group(1)), []).append(path)
            else:
                malformed.append(path)
            continue
        candidates.setdefault(int(match.group("sequence")), []).append(path)
    return candidates, malformed


def current_expected_buffer_paths(manifest, contract, buffer_dir=None):
    """Compatibility helper: files claiming the current next-pending group."""
    manifest = ensure_group_progress(manifest, contract)
    validate_manifest(manifest, contract)
    validate_group_plan(manifest, contract, required=True)
    sequence = next_pending_sequence(manifest, contract)
    if sequence is None:
        return []
    root = Path(buffer_dir or contract["paths"]["submission_inbox_dir"])
    candidates, malformed = _current_snapshot_candidates(root, manifest["snapshot_id"])
    if malformed:
        return malformed
    return list(candidates.get(sequence, []))


def _quarantine_target(path, manifest, sequence, artifact_sha, root):
    return Path(root) / manifest["snapshot_id"] / f"g{sequence:06d}" / f"{path.name}.invalid-{artifact_sha[:12]}"


def _failure_entry(*, manifest, descriptor, paths, validator_error, quarantine_root):
    expected = expected_buffer_path(descriptor, {"paths": {"submission_inbox_dir": str(Path(paths[0]).parent) if paths else ""}})
    primary = paths[0] if paths else expected
    if len(paths) == 1 and paths[0].exists():
        artifact_sha = hashlib.sha256(paths[0].read_bytes()).hexdigest()
    else:
        artifact_sha = canonical_sha256([p.as_posix() for p in paths] or [expected.as_posix()])
    targets = [
        _quarantine_target(p, manifest, int(descriptor["sequence"]), hashlib.sha256(p.read_bytes()).hexdigest(), quarantine_root)
        for p in paths if p.exists()
    ]
    primary_target = targets[0] if targets else Path(quarantine_root) / manifest["snapshot_id"] / f"g{int(descriptor['sequence']):06d}" / "missing-invalid-artifact"
    failure = {
        "validator_error": validator_error,
        "artifact_path": primary.as_posix(),
        "artifact_sha256": artifact_sha,
        "quarantine_artifact_path": primary_target.as_posix(),
        "recovery_eligible": True,
    }
    return {
        "descriptor": descriptor,
        "paths": list(paths),
        "quarantine_targets": targets,
        "failure": failure,
    }


def _transport_rejection_entry(*, manifest, descriptor, paths, validator_error, transport_kind, quarantine_root):
    targets = []
    for path in paths:
        if not path.exists():
            continue
        artifact_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        target = (
            Path(quarantine_root)
            / manifest["snapshot_id"]
            / f"g{int(descriptor['sequence']):06d}"
            / f"{path.name}.rejected-{artifact_sha[:12]}"
        )
        targets.append(target)
    artifact_sha = (
        hashlib.sha256(paths[0].read_bytes()).hexdigest()
        if len(paths) == 1 and paths[0].exists()
        else canonical_sha256([p.as_posix() for p in paths])
    )
    return {
        "descriptor": descriptor,
        "paths": list(paths),
        "quarantine_targets": targets,
        "rejection": {
            "transport_kind": transport_kind,
            "validator_error": validator_error,
            "artifact_sha256": artifact_sha,
            "normal_first_pass_attempt_consumed": False,
            "group_state_remains_pending": True,
        },
    }


def _semantic_terminal_failure_entry(*, manifest, descriptor, path, receipt, archive_root):
    artifact_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    archive_target = (
        Path(archive_root)
        / manifest["snapshot_id"]
        / f"g{int(descriptor['sequence']):06d}--{descriptor['group_sha256']}--terminal.json"
    )
    stop_class = receipt["semantic_stop_class"]
    failure = {
        "validator_error": f"semantic_exhaustion:{stop_class}",
        "artifact_path": path.as_posix(),
        "artifact_sha256": artifact_sha,
        "quarantine_artifact_path": archive_target.as_posix(),
        "recovery_eligible": True,
        "failure_class": "semantic_exhaustion",
        "semantic_stop_class": stop_class,
        "normal_first_pass_attempt_consumed": True,
        "valid_dossier_produced": False,
        "terminal_receipt_archive_path": archive_target.as_posix(),
    }
    return {
        "descriptor": descriptor,
        "path": path,
        "archive_target": archive_target,
        "receipt": receipt,
        "failure": failure,
    }



def _current_web_evidence_binding():
    schema_doc = load_worker_schema()
    evidence_contract = load_web_evidence_contract()
    return current_worker_contract_binding(schema_doc, evidence_contract)


def _validate_frozen_current_compatibility(view, current_manifest, contract):
    descriptor = view["descriptor"]
    index = view["index"]
    active_binding = _current_web_evidence_binding()
    if descriptor.get("web_evidence_contract_binding") != active_binding:
        raise ValueError("frozen Dossier evidence/schema/worker binding is no longer current-compatible")
    if index.get("web_evidence_contract_binding") != active_binding:
        raise ValueError("frozen Dossier worker index evidence binding is no longer current-compatible")
    if current_manifest.get("web_evidence_contract_binding") != active_binding:
        raise ValueError("current Dossier manifest is not bound to the active evidence contract")
    if int(index.get("ttl_days") or -1) != int(current_manifest.get("ttl_days") or -2):
        raise ValueError("frozen Dossier TTL contract is no longer current-compatible")

    current_items = {
        str(item.get("appid") or ""): item
        for item in current_manifest.get("items") or []
        if isinstance(item, dict) and str(item.get("appid") or "")
    }
    for item in descriptor.get("items") or []:
        appid = str(item.get("appid") or "")
        current = current_items.get(appid)
        if current is None:
            continue
        if current.get("title") != item.get("title") or current.get("key") != item.get("key"):
            raise ValueError(
                "frozen Dossier exact product/work identity changed for a current appid"
            )
    return active_binding


def compatible_cached_dossier(item, manifest, contract, store_dir, *, now=None):
    """Return one exact current-compatible cached dossier, otherwise None."""
    if not isinstance(item, dict):
        return None
    appid = str(item.get("appid") or "")
    if not appid.isdigit():
        return None
    doc = load_dossier_if_present(store_dir, appid)
    if doc is None:
        return None
    try:
        docs = validate_dossiers_against_expected_items(
            [doc],
            [item],
            contract,
            expected_ttl_days=int(manifest["ttl_days"]),
            now=now,
        )
        compact_policy = load_compact_provenance_policy()
        validate_compact_provenance(docs[0], compact_policy)
    except (ValueError, KeyError, TypeError):
        return None
    return docs[0]


def reconcile_current_pending_groups_from_cache(
    manifest,
    contract,
    store_dir,
    *,
    now=None,
):
    """Accept only current groups whose exact items are all satisfied by compatible cache."""
    next_manifest = ensure_group_progress(manifest, contract)
    plan = validate_group_plan(next_manifest, contract, required=True)
    reused = []
    for sequence in pending_sequences(next_manifest, contract):
        group = plan["groups"][sequence - 1]
        docs = [
            compatible_cached_dossier(
                item,
                next_manifest,
                contract,
                store_dir,
                now=now,
            )
            for item in group["items"]
        ]
        if any(doc is None for doc in docs):
            continue
        next_manifest = set_group_state(next_manifest, contract, sequence, ACCEPTED)
        reused.append(sequence)

    frozen_accepted, frozen_terminals, frozen_rejected, frozen_replays = _frozen_rollover_transports(
        manifest,
        contract,
        buffer_dir,
        repo_root=repo_root,
        frozen_authority_audit_path=frozen_authority_audit_path,
        retryable_rejection_root=retryable_rejection_root,
        terminal_receipt_archive_root=terminal_receipt_archive_root,
        frozen_authority_audit_path=frozen_authority_audit_path,
        repo_root=repo_root,
    )

    prefix_count = accepted_contiguous_prefix_item_count(next_manifest, contract)
    next_manifest.update(progress_fields(
        next_manifest["snapshot_id"],
        next_manifest["prepared_required_items"],
        list(next_manifest["prepared_required_items"])[prefix_count:],
        int(contract["checkpointing"]["checkpoint_size"]),
    ))
    validate_manifest(next_manifest, contract)
    return next_manifest, reused


def _read_frozen_audit(path):
    consumed = set()
    path = Path(path)
    if not path.exists():
        return consumed
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        key = record.get("consumption_key")
        if (
            record.get("consumed") is True
            and isinstance(key, list)
            and len(key) == 4
        ):
            consumed.add((str(key[0]), str(key[1]), int(key[2]), str(key[3])))
    return consumed


def _frozen_rejection(path, validator_error, quarantine_root):
    path = Path(path)
    artifact_sha = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else canonical_sha256(path.as_posix())
    target = (
        Path(quarantine_root)
        / "frozen_authority"
        / f"{path.name}.rejected-{artifact_sha[:12]}"
    )
    return {
        "path": path,
        "quarantine_target": target,
        "validator_error": validator_error,
        "artifact_sha256": artifact_sha,
    }


def _frozen_rollover_transports(
    manifest,
    contract,
    buffer_dir,
    *,
    repo_root=Path("."),
    frozen_authority_audit_path=_DEFAULT_FROZEN_AUTHORITY_AUDIT,
    retryable_rejection_root=_DEFAULT_RETRYABLE_REJECTION_QUARANTINE,
    terminal_receipt_archive_root=_DEFAULT_TERMINAL_RECEIPT_ARCHIVE,
):
    """Resolve authority-bearing old-snapshot transports without rebinding them to current work."""
    root = Path(buffer_dir)
    accepted = []
    terminals = []
    rejected = []
    replays = []
    consumed = _read_frozen_audit(frozen_authority_audit_path)
    if not root.exists():
        return accepted, terminals, rejected, replays

    for path in sorted(root.glob("*.json")):
        candidate_match = _BUFFER_NAME_RE.fullmatch(path.name)
        terminal_match = _TERMINAL_NAME_RE.fullmatch(path.name)
        match = terminal_match or candidate_match
        if match is None or match.group("snapshot") == manifest["snapshot_id"]:
            continue
        try:
            artifact = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            # Legacy stale artifacts stay inert. Only authority-bearing old work
            # is eligible for rollover-safe classification.
            continue
        if not isinstance(artifact, dict) or artifact.get("run_start_authority") is None:
            continue

        try:
            proof, view = resolve_frozen_transport_authority(
                path,
                artifact,
                contract,
                repo_root=repo_root,
            )
            descriptor = view["descriptor"]
            if proof["snapshot_id"] == manifest["snapshot_id"]:
                raise ValueError("frozen rollover scanner received a current-snapshot authority")
            if (
                match.group("snapshot") != proof["snapshot_id"]
                or int(match.group("sequence")) != int(proof["sequence"])
                or match.group("group") != proof["group_sha256"]
            ):
                raise ValueError("frozen transport filename does not match marker-parent authority")
            _validate_frozen_current_compatibility(view, manifest, contract)
            key = frozen_consumption_key(proof)
            if key in consumed:
                replays.append({"path": path, "proof": proof})
                continue

            if terminal_match is not None:
                deterministic = expected_terminal_receipt_path(descriptor, contract)
                if path.as_posix() != deterministic.as_posix():
                    raise ValueError("frozen terminal receipt path is non-deterministic")
                validate_terminal_receipt(artifact, descriptor)
                archive_target = (
                    Path(terminal_receipt_archive_root)
                    / proof["snapshot_id"]
                    / f"g{int(proof['sequence']):06d}--{proof['group_sha256']}--terminal.json"
                )
                terminals.append({
                    "path": path,
                    "descriptor": descriptor,
                    "receipt": artifact,
                    "proof": proof,
                    "archive_target": archive_target,
                })
                continue

            deterministic = expected_buffer_path(descriptor, contract)
            if path.as_posix() != deterministic.as_posix():
                raise ValueError("frozen Dossier candidate path is non-deterministic")
            docs = validate_buffer_artifact(
                artifact,
                descriptor,
                view["manifest"],
                contract,
            )
            accepted.append({
                "path": path,
                "descriptor": descriptor,
                "dossiers": docs,
                "proof": proof,
            })
        except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            rejected.append(_frozen_rejection(path, str(exc), retryable_rejection_root))

    return accepted, terminals, rejected, replays


def plan_buffered_drain(
    manifest,
    contract,
    buffer_dir,
    *,
    failed_quarantine_root=_DEFAULT_FAILED_QUARANTINE,
    retryable_rejection_root=_DEFAULT_RETRYABLE_REJECTION_QUARANTINE,
    terminal_receipt_archive_root=_DEFAULT_TERMINAL_RECEIPT_ARCHIVE,
):
    """Validate/classify present transports without conflating transport failure with semantic exhaustion."""
    manifest = ensure_group_progress(manifest, contract)
    validate_manifest(manifest, contract)
    group_plan = validate_group_plan(manifest, contract, required=True)
    candidates, malformed_names = _current_snapshot_candidates(buffer_dir, manifest["snapshot_id"])
    terminal_receipts, malformed_terminal_names = current_snapshot_terminal_receipts(
        buffer_dir, manifest["snapshot_id"]
    )
    groups = {int(group["sequence"]): group for group in group_plan["groups"]}
    state_by_sequence = {
        int(entry["sequence"]): entry for entry in manifest["group_progress"]["groups"]
    }
    accepted = []
    failed = []
    rejected = []
    terminal_replays = []
    next_manifest = copy.deepcopy(manifest)
    pending = set(pending_sequences(manifest, contract))

    for sequence in sorted(pending):
        descriptor = groups[sequence]
        paths = candidates.get(sequence, [])
        terminal_paths = terminal_receipts.get(sequence, [])

        if paths and terminal_paths:
            rejected.append(_transport_rejection_entry(
                manifest=manifest,
                descriptor=descriptor,
                paths=list(paths) + list(terminal_paths),
                validator_error="conflicting_candidate_and_terminal_receipt",
                transport_kind="conflicting_group_transports",
                quarantine_root=retryable_rejection_root,
            ))
            continue

        if terminal_paths:
            deterministic = expected_terminal_receipt_path(descriptor, contract)
            if len(terminal_paths) != 1:
                rejected.append(_transport_rejection_entry(
                    manifest=manifest,
                    descriptor=descriptor,
                    paths=terminal_paths,
                    validator_error="duplicate_or_alternate_terminal_receipt",
                    transport_kind="terminal_receipt",
                    quarantine_root=retryable_rejection_root,
                ))
                continue
            path = terminal_paths[0]
            if path.as_posix() != deterministic.as_posix():
                rejected.append(_transport_rejection_entry(
                    manifest=manifest,
                    descriptor=descriptor,
                    paths=terminal_paths,
                    validator_error="non_deterministic_terminal_receipt_path",
                    transport_kind="terminal_receipt",
                    quarantine_root=retryable_rejection_root,
                ))
                continue
            try:
                receipt = json.loads(path.read_text(encoding="utf-8"))
                authority_proof = None
                if receipt.get("run_start_authority") is not None:
                    authority_proof, authority_view = resolve_frozen_transport_authority(
                        path,
                        receipt,
                        contract,
                        repo_root=repo_root,
                    )
                    if authority_view["descriptor"] != descriptor:
                        raise ValueError("current terminal run-start authority descriptor mismatch")
                    _validate_frozen_current_compatibility(
                        authority_view,
                        manifest,
                        contract,
                    )
                    if frozen_consumption_key(authority_proof) in _read_frozen_audit(
                        frozen_authority_audit_path
                    ):
                        raise ValueError("current terminal run-start authority was already consumed")
                validate_terminal_receipt(receipt, descriptor)
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError, KeyError, TypeError) as exc:
                rejected.append(_transport_rejection_entry(
                    manifest=manifest,
                    descriptor=descriptor,
                    paths=terminal_paths,
                    validator_error=str(exc),
                    transport_kind="terminal_receipt",
                    quarantine_root=retryable_rejection_root,
                ))
                continue
            entry = _semantic_terminal_failure_entry(
                manifest=manifest,
                descriptor=descriptor,
                path=path,
                receipt=receipt,
                archive_root=terminal_receipt_archive_root,
            )
            if authority_proof is not None:
                entry["authority_proof"] = authority_proof
            failed.append(entry)
            next_manifest = set_group_state(
                next_manifest, contract, sequence, FAILED, failure=entry["failure"]
            )
            continue

        if not paths:
            continue
        deterministic = expected_buffer_path(descriptor, contract)
        if len(paths) != 1:
            rejected.append(_transport_rejection_entry(
                manifest=manifest,
                descriptor=descriptor,
                paths=paths,
                validator_error="duplicate_or_alternate_buffer_artifact",
                transport_kind="dossier_candidate",
                quarantine_root=retryable_rejection_root,
            ))
            continue
        path = paths[0]
        if path.as_posix() != deterministic.as_posix():
            rejected.append(_transport_rejection_entry(
                manifest=manifest,
                descriptor=descriptor,
                paths=paths,
                validator_error="non_deterministic_buffer_path",
                transport_kind="dossier_candidate",
                quarantine_root=retryable_rejection_root,
            ))
            continue
        try:
            artifact = json.loads(path.read_text(encoding="utf-8"))
            authority_proof = None
            if artifact.get("run_start_authority") is not None:
                authority_proof, authority_view = resolve_frozen_transport_authority(
                    path,
                    artifact,
                    contract,
                    repo_root=repo_root,
                )
                if authority_view["descriptor"] != descriptor:
                    raise ValueError("current candidate run-start authority descriptor mismatch")
                _validate_frozen_current_compatibility(
                    authority_view,
                    manifest,
                    contract,
                )
                if frozen_consumption_key(authority_proof) in _read_frozen_audit(
                    frozen_authority_audit_path
                ):
                    raise ValueError("current candidate run-start authority was already consumed")
            docs = validate_buffer_artifact(artifact, descriptor, manifest, contract)
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError, KeyError, TypeError) as exc:
            rejected.append(_transport_rejection_entry(
                manifest=manifest,
                descriptor=descriptor,
                paths=paths,
                validator_error=str(exc),
                transport_kind="dossier_candidate",
                quarantine_root=retryable_rejection_root,
            ))
            continue
        accepted_entry = {"path": path, "descriptor": descriptor, "dossiers": docs}
        if authority_proof is not None:
            accepted_entry["authority_proof"] = authority_proof
        accepted.append(accepted_entry)
        next_manifest = set_group_state(next_manifest, contract, sequence, ACCEPTED)

    # Exact replay of an already-consumed semantic terminal receipt is a cleanup-only no-op.
    for sequence, terminal_paths in sorted(terminal_receipts.items()):
        if sequence in pending or sequence not in groups:
            continue
        entry = state_by_sequence[sequence]
        descriptor = groups[sequence]
        if entry["state"] != FAILED or len(terminal_paths) != 1:
            continue
        path = terminal_paths[0]
        if path.as_posix() != expected_terminal_receipt_path(descriptor, contract).as_posix():
            continue
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
            validate_terminal_receipt(receipt, descriptor)
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError, KeyError, TypeError):
            continue
        failure = entry.get("failure") or {}
        artifact_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if (
            failure.get("failure_class") == "semantic_exhaustion"
            and failure.get("artifact_sha256") == artifact_sha
            and failure.get("semantic_stop_class") == receipt.get("semantic_stop_class")
        ):
            terminal_replays.append(path)

    prefix_count = accepted_contiguous_prefix_item_count(next_manifest, contract)
    next_remaining = list(next_manifest["prepared_required_items"])[prefix_count:]
    next_manifest.update(progress_fields(
        next_manifest["snapshot_id"],
        next_manifest["prepared_required_items"],
        next_remaining,
        int(contract["checkpointing"]["checkpoint_size"]),
    ))
    validate_manifest(next_manifest, contract)

    return {
        "accepted": accepted,
        "failed": failed,
        "rejected": rejected,
        "terminal_replays": terminal_replays,
        "frozen_accepted": frozen_accepted,
        "frozen_terminals": frozen_terminals,
        "frozen_rejected": frozen_rejected,
        "frozen_replays": frozen_replays,
        "accepted_count": len(accepted),
        "accepted_dossier_count": sum(len(entry["dossiers"]) for entry in accepted),
        "failed_count": len(failed),
        "rejected_count": len(rejected),
        "frozen_accepted_count": len(frozen_accepted),
        "frozen_terminal_count": len(frozen_terminals),
        "frozen_rejected_count": len(frozen_rejected),
        "frozen_replay_count": len(frozen_replays),
        "malformed_current_snapshot_artifacts": [
            path.as_posix() for path in list(malformed_names) + list(malformed_terminal_names)
        ],
        "next_manifest": next_manifest,
    }


def _append_failure_audit(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")



def _active_existing_dossier(appid, current_manifest, contract, store_dir):
    existing = load_dossier_if_present(store_dir, appid)
    if existing is None:
        return None
    title = existing.get("title") if isinstance(existing, dict) else None
    if not isinstance(title, str) or not title:
        return None
    try:
        docs = validate_dossiers_against_expected_items(
            [existing],
            [{"appid": str(appid), "title": title}],
            contract,
            expected_ttl_days=int(current_manifest["ttl_days"]),
        )
        compact_policy = load_compact_provenance_policy()
        validate_compact_provenance(docs[0], compact_policy)
    except (ValueError, KeyError, TypeError):
        return None
    return docs[0]


def _authority_audit_record(
    proof,
    *,
    outcome,
    current_snapshot_id,
    artifact_path,
    artifact_sha256,
    dossier_actions=None,
    semantic_stop_class=None,
):
    record = {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-FROZEN-INVOCATION-AUDIT-V1",
        "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "consumed": True,
        "consumption_key": list(frozen_consumption_key(proof)),
        "outcome": outcome,
        "authority_snapshot_id": proof["snapshot_id"],
        "authority_sequence": proof["sequence"],
        "authority_group_sha256": proof["group_sha256"],
        "current_snapshot_id_at_ingest": current_snapshot_id,
        "artifact_path": Path(artifact_path).as_posix(),
        "artifact_sha256": artifact_sha256,
        "authority": proof,
    }
    if dossier_actions is not None:
        record["dossier_actions"] = dossier_actions
    if semantic_stop_class is not None:
        record["semantic_stop_class"] = semantic_stop_class
    return record


def _cleanup_authority_marker(proof, repo_root):
    marker = Path(repo_root).resolve() / proof["marker_path"]
    if marker.exists():
        marker.unlink()


def _persist_frozen_dossiers(
    entry,
    *,
    current_manifest,
    contract,
    store_dir,
):
    actions = []
    persisted = []
    for doc in entry["dossiers"]:
        appid = str(doc["appid"])
        path = dossier_path(store_dir, appid)
        existing = _active_existing_dossier(
            appid,
            current_manifest,
            contract,
            store_dir,
        )
        if existing is not None:
            actions.append({
                "appid": appid,
                "action": "kept_existing_current_compatible",
                "candidate_dossier_sha256": canonical_sha256(doc),
                "kept_dossier_sha256": canonical_sha256(existing),
            })
            continue
        atomic_write_json(path, doc)
        sha = canonical_sha256(doc)
        persisted.append({
            "appid": appid,
            "path": path.as_posix(),
            "dossier_sha256": sha,
        })
        actions.append({
            "appid": appid,
            "action": "persisted_frozen_authority_dossier",
            "candidate_dossier_sha256": sha,
            "kept_dossier_sha256": sha,
        })
    return persisted, actions


def apply_buffered_drain(
    plan,
    *,
    manifest_path,
    store_dir,
    contract=None,
    failure_audit_path=_DEFAULT_FAILURE_AUDIT,
    rejection_audit_path=_DEFAULT_RETRYABLE_REJECTION_AUDIT,
    frozen_authority_audit_path=_DEFAULT_FROZEN_AUTHORITY_AUDIT,
    repo_root=Path("."),
):
    """Apply accepted dossiers, consumed semantic terminals, and retryable transport cleanup."""
    persisted = []
    for entry in plan["accepted"]:
        for doc in entry["dossiers"]:
            path = dossier_path(store_dir, str(doc["appid"]))
            atomic_write_json(path, doc)
            persisted.append({
                "appid": str(doc["appid"]),
                "path": path.as_posix(),
                "dossier_sha256": canonical_sha256(doc),
            })

    current_snapshot_id = plan["next_manifest"]["snapshot_id"]

    for entry in plan.get("frozen_accepted", []):
        frozen_persisted, dossier_actions = _persist_frozen_dossiers(
            entry,
            current_manifest=plan["next_manifest"],
            contract=contract,
            store_dir=store_dir,
        )
        persisted.extend(frozen_persisted)
        artifact_sha = hashlib.sha256(entry["path"].read_bytes()).hexdigest()
        _append_failure_audit(
            frozen_authority_audit_path,
            _authority_audit_record(
                entry["proof"],
                outcome="dossier_candidate_accepted_after_rollover",
                current_snapshot_id=current_snapshot_id,
                artifact_path=entry["path"],
                artifact_sha256=artifact_sha,
                dossier_actions=dossier_actions,
            ),
        )
        _cleanup_authority_marker(entry["proof"], repo_root)

    for entry in plan["accepted"]:
        proof = entry.get("authority_proof")
        if proof is not None:
            artifact_sha = hashlib.sha256(entry["path"].read_bytes()).hexdigest()
            _append_failure_audit(
                frozen_authority_audit_path,
                _authority_audit_record(
                    proof,
                    outcome="dossier_candidate_accepted_current_snapshot",
                    current_snapshot_id=current_snapshot_id,
                    artifact_path=entry["path"],
                    artifact_sha256=artifact_sha,
                    dossier_actions=[
                        {
                            "appid": str(doc["appid"]),
                            "action": "persisted_current_group_dossier",
                            "candidate_dossier_sha256": canonical_sha256(doc),
                            "kept_dossier_sha256": canonical_sha256(doc),
                        }
                        for doc in entry["dossiers"]
                    ],
                ),
            )
            _cleanup_authority_marker(proof, repo_root)

    for entry in plan["failed"]:
        source = entry["path"]
        target = entry["archive_target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise ValueError(f"semantic terminal receipt archive already exists: {target.as_posix()}")
        shutil.move(source.as_posix(), target.as_posix())
        _append_failure_audit(failure_audit_path, {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-GROUP-FAILURE-AUDIT-V1",
            "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "snapshot_id": plan["next_manifest"]["snapshot_id"],
            "sequence": entry["descriptor"]["sequence"],
            "group_sha256": entry["descriptor"]["group_sha256"],
            **entry["failure"],
            "normal_forward_progress_blocked": False,
        })
        proof = entry.get("authority_proof")
        if proof is not None:
            _append_failure_audit(
                frozen_authority_audit_path,
                _authority_audit_record(
                    proof,
                    outcome="semantic_exhaustion_consumed_current_snapshot",
                    current_snapshot_id=current_snapshot_id,
                    artifact_path=source,
                    artifact_sha256=entry["failure"]["artifact_sha256"],
                    semantic_stop_class=entry["receipt"]["semantic_stop_class"],
                ),
            )
            _cleanup_authority_marker(proof, repo_root)

    for entry in plan.get("frozen_terminals", []):
        source = entry["path"]
        target = entry["archive_target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise ValueError(f"frozen terminal receipt archive already exists: {target.as_posix()}")
        artifact_sha = hashlib.sha256(source.read_bytes()).hexdigest()
        shutil.move(source.as_posix(), target.as_posix())
        _append_failure_audit(
            frozen_authority_audit_path,
            _authority_audit_record(
                entry["proof"],
                outcome="semantic_exhaustion_consumed_after_rollover",
                current_snapshot_id=current_snapshot_id,
                artifact_path=source,
                artifact_sha256=artifact_sha,
                semantic_stop_class=entry["receipt"]["semantic_stop_class"],
            ),
        )
        _cleanup_authority_marker(entry["proof"], repo_root)

    for entry in plan["rejected"]:
        for source, target in zip(entry["paths"], entry["quarantine_targets"]):
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError(f"retryable transport quarantine target already exists: {target.as_posix()}")
            shutil.move(source.as_posix(), target.as_posix())
        _append_failure_audit(rejection_audit_path, {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-TRANSPORT-REJECTION-AUDIT-V1",
            "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "snapshot_id": plan["next_manifest"]["snapshot_id"],
            "sequence": entry["descriptor"]["sequence"],
            "group_sha256": entry["descriptor"]["group_sha256"],
            **entry["rejection"],
        })

    for entry in plan.get("frozen_rejected", []):
        source = entry["path"]
        target = entry["quarantine_target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise ValueError(f"frozen transport quarantine target already exists: {target.as_posix()}")
        shutil.move(source.as_posix(), target.as_posix())
        _append_failure_audit(rejection_audit_path, {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-FROZEN-TRANSPORT-REJECTION-AUDIT-V1",
            "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "current_snapshot_id": current_snapshot_id,
            "artifact_path": source.as_posix(),
            "artifact_sha256": entry["artifact_sha256"],
            "validator_error": entry["validator_error"],
            "current_snapshot_progress_changed": False,
        })

    cache_reused_sequences = []
    if contract is not None:
        reconciled, cache_reused_sequences = reconcile_current_pending_groups_from_cache(
            plan["next_manifest"],
            contract,
            store_dir,
        )
        plan["next_manifest"] = reconciled
    plan["cache_reused_sequences"] = cache_reused_sequences

    atomic_write_json(manifest_path, plan["next_manifest"])
    for entry in plan["accepted"]:
        entry["path"].unlink()
    for entry in plan.get("frozen_accepted", []):
        if entry["path"].exists():
            entry["path"].unlink()
    for replay in plan.get("frozen_replays", []):
        if replay["path"].exists():
            replay["path"].unlink()
        _cleanup_authority_marker(replay["proof"], repo_root)
    for path in plan["terminal_replays"]:
        path.unlink()
    return persisted


def drain_buffered_groups(
    *,
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
    contract=None,
    buffer_dir="data/ai_inbox/taste_steam_review_dossiers",
    store_dir="data/cache/taste_steam_review_dossiers",
    failed_quarantine_root=_DEFAULT_FAILED_QUARANTINE,
    failure_audit_path=_DEFAULT_FAILURE_AUDIT,
    retryable_rejection_root=_DEFAULT_RETRYABLE_REJECTION_QUARANTINE,
    rejection_audit_path=_DEFAULT_RETRYABLE_REJECTION_AUDIT,
    terminal_receipt_archive_root=_DEFAULT_TERMINAL_RECEIPT_ARCHIVE,
    frozen_authority_audit_path=_DEFAULT_FROZEN_AUTHORITY_AUDIT,
    repo_root=Path("."),
):
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    plan = plan_buffered_drain(
        manifest,
        contract,
        buffer_dir,
        failed_quarantine_root=failed_quarantine_root,
        retryable_rejection_root=retryable_rejection_root,
        terminal_receipt_archive_root=terminal_receipt_archive_root,
    )
    persisted = apply_buffered_drain(
        plan,
        manifest_path=manifest_path,
        store_dir=store_dir,
        contract=contract,
        failure_audit_path=failure_audit_path,
        rejection_audit_path=rejection_audit_path,
        frozen_authority_audit_path=frozen_authority_audit_path,
        repo_root=repo_root,
    )
    progress = plan["next_manifest"]["group_progress"]
    return {
        "accepted_group_count_this_run": plan["accepted_count"],
        "accepted_dossier_count_this_run": plan["accepted_dossier_count"],
        "failed_group_count_this_run": plan["failed_count"],
        "cache_reused_group_count_this_run": len(plan.get("cache_reused_sequences", [])),
        "frozen_authority_accepted_count_this_run": plan.get("frozen_accepted_count", 0),
        "frozen_authority_terminal_count_this_run": plan.get("frozen_terminal_count", 0),
        "frozen_authority_rejected_count_this_run": plan.get("frozen_rejected_count", 0),
        "frozen_authority_replay_cleanup_count_this_run": plan.get("frozen_replay_count", 0),
        "retryable_transport_rejection_count_this_run": plan["rejected_count"],
        "terminal_replay_cleanup_count_this_run": len(plan["terminal_replays"]),
        "accepted_sequences": [entry["descriptor"]["sequence"] for entry in plan["accepted"]],
        "failed_sequences": [entry["descriptor"]["sequence"] for entry in plan["failed"]],
        "rejected_sequences": [entry["descriptor"]["sequence"] for entry in plan["rejected"]],
        "cache_reused_sequences": list(plan.get("cache_reused_sequences", [])),
        "frozen_authority_accepted_sequences": [
            entry["descriptor"]["sequence"] for entry in plan.get("frozen_accepted", [])
        ],
        "malformed_current_snapshot_artifacts": plan["malformed_current_snapshot_artifacts"],
        "persisted": persisted,
        "snapshot_id": plan["next_manifest"]["snapshot_id"],
        "next_pending_sequence": next_pending_sequence(plan["next_manifest"], contract),
        "accepted_group_count": progress["accepted_group_count"],
        "failed_group_count": progress["failed_group_count"],
        "pending_group_count": progress["pending_group_count"],
        "accepted_dossier_count": progress["accepted_dossier_count"],
        "failed_dossier_count": progress["failed_dossier_count"],
        "pending_dossier_count": progress["pending_dossier_count"],
        "normal_first_pass_complete": progress["normal_first_pass_complete"],
        "all_groups_accepted": progress["all_groups_accepted"],
        "legacy_contiguous_remaining_required_count": plan["next_manifest"]["remaining_required_count"],
        "full_backlog_complete": plan["next_manifest"]["full_backlog_complete"],
    }


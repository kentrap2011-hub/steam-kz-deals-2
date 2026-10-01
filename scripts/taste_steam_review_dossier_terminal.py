#!/usr/bin/env python3
"""Exact-bound terminal receipt for exhausted Taste Steam review Dossier semantics."""
import re
from pathlib import Path

from taste_steam_review_dossier import canonical_sha256

TERMINAL_RECEIPT_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-TERMINAL-RECEIPT-V1"
TERMINAL_EXECUTION_STATUS = "semantic_exhaustion_no_valid_dossier"
TERMINAL_STOP_CLASSES = {
    "existence_established_retrieval_unresolved",
    "existence_established_access_unresolved",
    "critical_evidence_insufficient_after_required_routes_exhausted",
}
_ROUTE_KEYS = {
    "russian",
    "source_diversification",
    "identity",
    "temporal",
    "next_required_step_status",
}
_ROUTE_STATES = {"exhausted", "not_applicable"}
_TERMINAL_NAME_RE = re.compile(
    r"^(?P<snapshot>[0-9a-f]{64})--g(?P<sequence>[0-9]{6})--"
    r"(?P<group>[0-9a-f]{64})--terminal\.json$"
)


def expected_terminal_receipt_path(descriptor, contract):
    inbox = Path(contract["paths"]["submission_inbox_dir"])
    return inbox / (
        f"{descriptor['snapshot_id']}--g{int(descriptor['sequence']):06d}--"
        f"{descriptor['group_sha256']}--terminal.json"
    )


def current_snapshot_terminal_receipts(buffer_dir, snapshot_id):
    """Return current-snapshot terminal receipts keyed by group sequence."""
    root = Path(buffer_dir)
    receipts = {}
    malformed = []
    if not root.exists():
        return receipts, malformed
    prefix = f"{snapshot_id}--g"
    for path in sorted(root.glob("*--terminal.json")):
        name = path.name
        if not name.startswith(prefix):
            continue
        match = _TERMINAL_NAME_RE.fullmatch(name)
        if not match or match.group("snapshot") != snapshot_id:
            partial = re.match(rf"^{re.escape(snapshot_id)}--g([0-9]{{6}})--", name)
            if partial:
                receipts.setdefault(int(partial.group(1)), []).append(path)
            else:
                malformed.append(path)
            continue
        receipts.setdefault(int(match.group("sequence")), []).append(path)
    return receipts, malformed


def validate_terminal_receipt(receipt, descriptor):
    """Validate exact descriptor binding and the narrow semantic-exhaustion boundary."""
    if not isinstance(receipt, dict):
        raise ValueError("dossier terminal receipt must be an object")
    if receipt.get("schema") != TERMINAL_RECEIPT_SCHEMA or receipt.get("schema_version") != 1:
        raise ValueError("unsupported dossier terminal receipt schema")

    descriptor_fields = set(descriptor) - {"schema", "schema_version"}
    terminal_fields = {
        "schema",
        "schema_version",
        "execution_status",
        "semantic_stop_class",
        "valid_dossier_produced",
        "normal_first_pass_attempt_consumed",
        "blocked_game",
        "route_exhaustion",
    }
    expected_fields = descriptor_fields | terminal_fields
    if set(receipt) != expected_fields:
        raise ValueError("dossier terminal receipt field set is invalid")

    for field in descriptor_fields:
        if receipt.get(field) != descriptor.get(field):
            raise ValueError(f"dossier terminal receipt identity mismatch: {field}")
    if receipt.get("items_sha256") != canonical_sha256(receipt.get("items")):
        raise ValueError("dossier terminal receipt items_sha256 mismatch")

    if receipt.get("execution_status") != TERMINAL_EXECUTION_STATUS:
        raise ValueError("dossier terminal receipt execution_status is invalid")
    stop_class = receipt.get("semantic_stop_class")
    if stop_class not in TERMINAL_STOP_CLASSES:
        raise ValueError("dossier terminal receipt semantic_stop_class is not consumable")
    if receipt.get("valid_dossier_produced") is not False:
        raise ValueError("dossier terminal receipt must assert no valid dossier was produced")
    if receipt.get("normal_first_pass_attempt_consumed") is not True:
        raise ValueError("dossier terminal receipt must consume exactly one normal first-pass attempt")

    blocked = receipt.get("blocked_game")
    if not isinstance(blocked, dict) or set(blocked) != {"appid", "title"}:
        raise ValueError("dossier terminal receipt blocked_game is invalid")
    if not any(
        str(item.get("appid") or "") == blocked.get("appid")
        and item.get("title") == blocked.get("title")
        for item in descriptor.get("items") or []
        if isinstance(item, dict)
    ):
        raise ValueError("dossier terminal receipt blocked_game is outside the exact group")

    routes = receipt.get("route_exhaustion")
    if not isinstance(routes, dict) or set(routes) != _ROUTE_KEYS:
        raise ValueError("dossier terminal receipt route_exhaustion is invalid")
    if routes.get("next_required_step_status") != "none_all_required_routes_exhausted":
        raise ValueError("dossier terminal receipt cannot consume while a required next step remains")
    for key in ("russian", "source_diversification", "identity", "temporal"):
        if routes.get(key) not in _ROUTE_STATES:
            raise ValueError(f"dossier terminal receipt route state is invalid: {key}")

    if stop_class in {
        "existence_established_retrieval_unresolved",
        "existence_established_access_unresolved",
    }:
        if routes["russian"] != "exhausted" or routes["source_diversification"] != "exhausted":
            raise ValueError("unresolved Russian evidence may consume only after Russian and diversification routes are exhausted")
    if routes["identity"] != "not_applicable":
        raise ValueError("dossier terminal receipt requires exact product identity to be resolved before attempt consumption")
    return receipt

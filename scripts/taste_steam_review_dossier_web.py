#!/usr/bin/env python3
"""V2 web-evidence helpers layered on the unchanged GitHub dossier control plane."""
import copy
from datetime import datetime, timezone

from taste_package_member_aggregation import (
    PACKAGE_AI_CONDITION,
    ordered_unique_numeric,
)
from taste_steam_review_dossier import (
    SEMANTIC_INPUT_SCHEMA,
    atomic_write_json,
    canonical_sha256,
    dossier_path,
    load_dossier_if_present,
    parse_utc,
    resolve_ttl_days,
    utc_iso,
    validate_pin,
)
from taste_steam_review_dossier_daily import (
    WORK_SCHEMA,
    build_submission_group_plan,
    progress_fields,
    validate_manifest,
)
from taste_steam_review_dossier_strict import (
    current_worker_contract_binding,
    dossier_state_strict,
    validate_dossiers_against_expected_items,
)

_PACKAGE_IDENTITY_POLICY_REVISION = "package-member-dossier-aggregation-v1"


def ensure_web_evidence_binding(manifest):
    """Add/validate semantic worker version metadata without changing snapshot/group identity."""
    out = copy.deepcopy(manifest)
    expected = current_worker_contract_binding()
    existing = out.get("web_evidence_contract_binding")
    if existing is not None and existing != expected:
        raise ValueError("existing daily dossier snapshot has incompatible web-evidence binding")
    out["web_evidence_contract_binding"] = expected
    return out


def _offer_identity(row, key, source_row_appid):
    """Keep the commercial/store subject separate from per-game dossier targets."""
    return {
        "key": key,
        "family_id": row.get("family_id"),
        "title": str(row.get("title") or ""),
        "source_row_appid": source_row_appid,
    }


def _member_titles_by_appid(bundle_members):
    out = {}
    for member in bundle_members if isinstance(bundle_members, list) else []:
        if not isinstance(member, dict):
            continue
        appid = str(member.get("appid") or "")
        title = str(member.get("name") or "").strip()
        if not appid.isdigit() or not title:
            continue
        titles = out.setdefault(appid, [])
        if title not in titles:
            titles.append(title)
    return out


def _normalized_policy_text(value):
    return " ".join(str(value or "").casefold().split())


def _matching_policy_phrases(text, phrases):
    return [
        phrase for phrase in phrases if _normalized_policy_text(phrase) and _normalized_policy_text(phrase) in text
    ]


def classify_story_dlc_scope(row, contract):
    """Classify only canonical DLC/add-on rows; positive story evidence is required."""
    policy = contract["scope"]["story_dlc_policy"]
    markers = policy["dlc_identity_markers"]
    family_id = str(row.get("family_id") or "")
    family_type = str(row.get("family_type") or "")
    condition = row.get("semantic_condition") if isinstance(row.get("semantic_condition"), dict) else {}
    is_dlc_like = (
        any(family_id.startswith(prefix) for prefix in markers["family_id_prefixes"])
        or family_type in set(markers["family_types"])
        or condition.get("ai_condition") in set(markers["semantic_ai_conditions"])
    )
    if not is_dlc_like:
        return None

    key = row.get("taste_subject_key") if "taste_subject_key" in row else row.get("key")
    appid = str(row.get("appid") or "")
    title = str(row.get("title") or "")
    source_field = policy["positive_story_evidence"]["source_field"]
    description = _normalized_policy_text(row.get(source_field))
    title_text = _normalized_policy_text(title)
    combined = f"{title_text} {description}".strip()

    story_hits = _matching_policy_phrases(description, policy["positive_story_evidence"]["phrases"])
    container_hits = _matching_policy_phrases(
        combined, policy["entitlement_container_negative_hints"]["title_or_description_phrases"]
    )
    non_story_hits = _matching_policy_phrases(
        combined, policy["explicit_non_story_negative_hints"]["title_or_description_phrases"]
    )

    if container_hits:
        classification = "non_story_dlc_excluded"
        reason_code = "entitlement_container_not_independent_story_content"
    elif story_hits:
        classification = "story_dlc_eligible"
        reason_code = "positive_story_content_evidence"
    elif non_story_hits:
        classification = "non_story_dlc_excluded"
        reason_code = "explicit_non_story_product_metadata"
    else:
        classification = "story_content_unproven_excluded"
        reason_code = "positive_story_content_evidence_missing"

    return {
        "key": key,
        "appid": appid,
        "title": title,
        "classification": classification,
        "reason_code": reason_code,
        "evidence_source": f"canonical_taste_queue.{source_field}",
        "identity_source": "canonical_family_and_semantic_metadata",
        "matched_story_signals": story_hits,
        "matched_container_signals": container_hits,
        "matched_non_story_signals": non_story_hits,
    }


def _story_dlc_scope_summary(classifications):
    counts = {
        "dlc_like_considered": len(classifications),
        "story_eligible": 0,
        "non_story_excluded": 0,
        "ambiguous_excluded": 0,
    }
    for item in classifications:
        value = item["classification"]
        if value == "story_dlc_eligible":
            counts["story_eligible"] += 1
        elif value == "non_story_dlc_excluded":
            counts["non_story_excluded"] += 1
        elif value == "story_content_unproven_excluded":
            counts["ambiguous_excluded"] += 1
        else:
            raise ValueError(f"unsupported story DLC classification: {value}")
    return counts


def _resolve_queue_row_dossier_identities(row, index):
    """Resolve one eligible queue row to exact game dossier identities.

    A package offer is not itself a dossier identity. Its authoritative
    semantic_condition.base_appids are expanded to member games, while
    arbitrary bundle members (for example costume DLC) are ignored.
    """
    source_row_appid = str(row.get("appid") or "")
    key = row.get("taste_subject_key") if "taste_subject_key" in row else row.get("key")
    if not source_row_appid.isdigit() or not isinstance(key, str) or not key:
        raise ValueError(f"canonical Taste queue row {index} lacks appid/taste subject identity")

    condition = row.get("semantic_condition") if isinstance(row.get("semantic_condition"), dict) else {}
    is_package_offer = key.startswith("Sub_") or condition.get("ai_condition") == PACKAGE_AI_CONDITION
    if not is_package_offer:
        return {
            "status": "resolved",
            "rows": [{
                "key": key,
                "appid": source_row_appid,
                "title": str(row.get("title") or ""),
                "taste_fingerprint": row.get("taste_fingerprint"),
                "candidate_context_sha256": row.get("candidate_context_sha256"),
                "work_required": list(row["work_required"]),
                "source_kind": "direct",
            }],
            "package_mapping": None,
        }

    offer = _offer_identity(row, key, source_row_appid)
    base_appids = ordered_unique_numeric(condition.get("base_appids"))
    if not base_appids:
        return {
            "status": "blocked",
            "blocked": {
                "key": key,
                "reason": "package_offer_has_no_authoritative_game_members",
                "offer_identity": offer,
                "candidate_game_appids": [],
            },
        }

    member_titles = _member_titles_by_appid(row.get("bundle_members"))
    targets = []
    unresolved = []
    mapping_members = []
    for appid in base_appids:
        titles = member_titles.get(appid) or []
        if len(titles) != 1:
            unresolved.append({"appid": appid, "candidate_titles": titles})
            continue
        title = titles[0]
        targets.append({
            "key": f"App_{appid}",
            "appid": appid,
            "title": title,
            "taste_fingerprint": row.get("taste_fingerprint"),
            "candidate_context_sha256": row.get("candidate_context_sha256"),
            "work_required": list(row["work_required"]),
            "source_kind": "package_member",
            "offer_identity": offer,
            "package_member_title": title,
        })
        mapping_members.append({
            "appid": appid,
            "title": title,
            "dossier_key": f"App_{appid}",
            "dossier_path": None,
        })

    if unresolved:
        return {
            "status": "blocked",
            "blocked": {
                "key": key,
                "reason": "authoritative_package_member_title_unresolved",
                "offer_identity": offer,
                "candidate_game_appids": base_appids,
                "unresolved_members": unresolved,
            },
        }

    return {
        "status": "resolved",
        "rows": targets,
        "package_mapping": {
            "offer_identity": offer,
            "member_count": len(mapping_members),
            "member_appids": list(base_appids),
            "members": mapping_members,
            "aggregation_semantics": "per_game_dossier_reuse_by_appid",
        },
    }


def _merge_offer_identity(target, offer):
    if not isinstance(offer, dict):
        return
    offers = target.setdefault("offer_identities", [])
    identity_key = (offer.get("key"), offer.get("family_id"), offer.get("title"), offer.get("source_row_appid"))
    for existing in offers:
        existing_key = (
            existing.get("key"), existing.get("family_id"), existing.get("title"), existing.get("source_row_appid")
        )
        if existing_key == identity_key:
            return
    offers.append(copy.deepcopy(offer))


def resolve_dossier_scope_identities(queue_rows, contract):
    """Expand packages to member games and dedupe globally to one dossier node per appid."""
    if not isinstance(queue_rows, list):
        raise ValueError("canonical Taste queue rows must be a list")
    markers = set(contract["scope"]["taste_semantic_work_required_any"])
    rows_by_appid = {}
    order = []
    blocked = []
    package_mappings = []
    story_dlc_classifications = []
    eligible_row_count = 0
    deduplicated_row_count = 0

    for index, row in enumerate(queue_rows):
        if not isinstance(row, dict):
            raise ValueError(f"canonical Taste queue row {index} is malformed")
        work = row.get("work_required")
        if not isinstance(work, list):
            raise ValueError(f"canonical Taste queue row {index} has no canonical work_required")
        if not any(item in markers for item in work):
            continue
        story_dlc = classify_story_dlc_scope(row, contract)
        if story_dlc is not None:
            story_dlc_classifications.append(story_dlc)
            if story_dlc["classification"] != "story_dlc_eligible":
                continue
        eligible_row_count += 1
        resolved = _resolve_queue_row_dossier_identities(row, index)
        if resolved["status"] == "blocked":
            blocked.append(resolved["blocked"])
            continue
        if resolved.get("package_mapping") is not None:
            package_mappings.append(resolved["package_mapping"])

        for target in resolved["rows"]:
            appid = target["appid"]
            existing = rows_by_appid.get(appid)
            if existing is None:
                canonical = copy.deepcopy(target)
                canonical["dossier_identity_resolution"] = (
                    "authoritative_package_base_appid_member"
                    if target.get("source_kind") == "package_member"
                    else "direct_queue_game_identity"
                )
                canonical["offer_identities"] = []
                _merge_offer_identity(canonical, target.get("offer_identity"))
                rows_by_appid[appid] = canonical
                order.append(appid)
                continue

            deduplicated_row_count += 1
            _merge_offer_identity(existing, target.get("offer_identity"))
            if target.get("source_kind") == "direct":
                existing.update({
                    "key": target["key"],
                    "title": target["title"],
                    "taste_fingerprint": target.get("taste_fingerprint"),
                    "candidate_context_sha256": target.get("candidate_context_sha256"),
                    "work_required": list(target["work_required"]),
                    "source_kind": "direct",
                    "dossier_identity_resolution": (
                        "direct_appid_reused_by_package_member"
                        if existing.get("offer_identities")
                        else "direct_queue_game_identity"
                    ),
                })

    rows = []
    for appid in order:
        row = rows_by_appid[appid]
        if row.get("source_kind") == "package_member" and row.get("offer_identities"):
            row["dossier_identity_resolution"] = "package_member_appid_dossier_node"
        row.pop("offer_identity", None)
        row.pop("package_member_title", None)
        row.pop("source_kind", None)
        rows.append(row)

    for mapping in package_mappings:
        for member in mapping["members"]:
            member["dossier_path"] = dossier_path(contract["paths"]["dossier_store_dir"], member["appid"]).as_posix()

    return {
        "rows": rows,
        "identity_blocked_items": blocked,
        "package_member_mappings": package_mappings,
        "story_dlc_classifications": story_dlc_classifications,
        "story_dlc_scope_summary": _story_dlc_scope_summary(story_dlc_classifications),
        "eligible_row_count": eligible_row_count,
        "deduplicated_row_count": deduplicated_row_count,
    }


def build_daily_work_manifest_web(queue_rows, contract, store_dir, *, now=None, ttl_days=None, source_queue_path=None):
    """Prepare a fixed daily snapshot while treating legacy/non-V2 cache entries as invalid."""
    from zoneinfo import ZoneInfo
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    ttl = resolve_ttl_days(contract, ttl_days)
    checkpoint_size = int(contract["checkpointing"]["checkpoint_size"])
    source_queue_sha = canonical_sha256(queue_rows)
    resolution = resolve_dossier_scope_identities(queue_rows, contract)
    scope_rows = resolution["rows"]
    identity_blocked_items = resolution["identity_blocked_items"]
    package_member_mappings = resolution["package_member_mappings"]
    story_dlc_classifications = resolution["story_dlc_classifications"]
    story_dlc_scope_summary = resolution["story_dlc_scope_summary"]
    story_dlc_policy_revision = contract["scope"]["story_dlc_policy"]["policy_revision"]
    story_dlc_classification_sha = canonical_sha256(story_dlc_classifications)
    eligible_row_count = resolution["eligible_row_count"]
    items = []
    required = []
    for row in scope_rows:
        appid = row["appid"]
        existing = load_dossier_if_present(store_dir, appid)
        try:
            state = dossier_state_strict(
                existing,
                contract,
                now=now,
                expected_appid=appid,
                expected_title=row["title"],
                expected_ttl_days=ttl,
            )
        except ValueError:
            state = "invalid"
        item = {
            "key": row["key"], "appid": appid, "title": row["title"],
            "dossier_path": dossier_path(store_dir, appid).as_posix(), "state": state,
        }
        if existing and state == "fresh":
            item.update({
                "generated_at_utc": existing["generated_at_utc"],
                "expires_at_utc": existing["expires_at_utc"],
                "dossier_sha256": canonical_sha256(existing),
            })
        else:
            reason = "refresh_required" if state in {"stale", "invalid", "invalid_future"} else "missing_dossier"
            item["reason"] = reason
            required.append({
                "key": row["key"], "appid": appid, "title": row["title"],
                "dossier_path": item["dossier_path"], "reason": reason,
            })
        items.append(item)

    prepared_date = now.astimezone(ZoneInfo("Europe/Samara")).date().isoformat()
    eligible_binding = [{"key": r["key"], "appid": r["appid"]} for r in scope_rows]
    eligible_sha = canonical_sha256(eligible_binding)
    identity_blocked_sha = canonical_sha256(identity_blocked_items)
    package_mapping_sha = canonical_sha256(package_member_mappings)
    required_sha = canonical_sha256(required)
    snapshot_id = canonical_sha256({
        "prepared_for_date": prepared_date,
        "source_queue_sha256": source_queue_sha,
        "eligible_scope_sha256": eligible_sha,
        "story_dlc_scope_policy_revision": story_dlc_policy_revision,
        "story_dlc_scope_classification_sha256": story_dlc_classification_sha,
        "identity_blocked_sha256": identity_blocked_sha,
        "package_member_mapping_sha256": package_mapping_sha,
        "prepared_required_sha256": required_sha,
        "ttl_days": ttl,
    })
    source_path = source_queue_path or contract["paths"]["taste_queue"]
    group_plan = build_submission_group_plan(
        snapshot_id=snapshot_id,
        prepared_required_sha256=required_sha,
        prepared_required_items=required,
        checkpoint_size=checkpoint_size,
        scope_source=contract["scope"]["source"],
        source_queue_sha256=source_queue_sha,
    )
    manifest = {
        "schema": WORK_SCHEMA,
        "schema_version": 2,
        "preparation_mode": "daily_fixed_full_backlog",
        "snapshot_id": snapshot_id,
        "prepared_at_utc": utc_iso(now),
        "prepared_for_date": prepared_date,
        "ttl_days": ttl,
        "scope_source": contract["scope"]["source"],
        "source_queue_path": source_path,
        "source_queue_sha256": source_queue_sha,
        "source_row_count": len(queue_rows),
        "eligible_row_count": eligible_row_count,
        "excluded_row_count": len(queue_rows) - eligible_row_count,
        "unique_appid_count": len(scope_rows),
        "deduplicated_row_count": resolution["deduplicated_row_count"],
        "identity_policy_revision": _PACKAGE_IDENTITY_POLICY_REVISION,
        "story_dlc_scope_policy_revision": story_dlc_policy_revision,
        "story_dlc_scope_classification_count": len(story_dlc_classifications),
        "story_dlc_scope_classification_sha256": story_dlc_classification_sha,
        "story_dlc_scope_classifications": story_dlc_classifications,
        "story_dlc_scope_summary": story_dlc_scope_summary,
        "identity_blocked_count": len(identity_blocked_items),
        "identity_blocked_sha256": identity_blocked_sha,
        "identity_blocked_items": identity_blocked_items,
        "package_member_mapping_count": len(package_member_mappings),
        "package_member_mapping_sha256": package_mapping_sha,
        "package_member_mappings": package_member_mappings,
        "eligible_scope_count": len(scope_rows),
        "eligible_scope_sha256": eligible_sha,
        "ordered_appids": [r["appid"] for r in scope_rows],
        "items": items,
        "prepared_required_items": required,
        "prepared_required_count": len(required),
        "prepared_required_sha256": required_sha,
        "checkpoint_size": checkpoint_size,
        "checkpoint_semantics": "internal_durability_boundary_not_scope_quota",
        "sampling_policy": contract["sampling"],
        "web_evidence_contract_binding": current_worker_contract_binding(),
        "submission_group_plan": group_plan,
    }
    manifest.update(progress_fields(snapshot_id, required, list(required), checkpoint_size))
    validate_manifest(manifest, contract)
    return manifest


def persist_submission_and_advance_snapshot_strict(submission, manifest, contract, store_dir, *, manifest_output_path=None):
    if not isinstance(submission, dict) or submission.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-SUBMISSION-V1" or submission.get("schema_version") != 1:
        raise ValueError("unsupported dossier submission schema")
    current = validate_manifest(manifest, contract)
    if manifest["status"] != "work_required" or not current:
        raise ValueError("no dossier checkpoint work is currently prepared")
    for field in ("snapshot_id", "scope_sha256", "scope_source", "source_queue_sha256"):
        if submission.get(field) != manifest.get(field):
            raise ValueError(f"dossier submission {field} mismatch")
    docs = validate_dossiers_against_expected_items(
        submission.get("dossiers"), current, contract, expected_ttl_days=manifest["ttl_days"]
    )
    persisted = []
    for doc in docs:
        path = dossier_path(store_dir, str(doc["appid"]))
        atomic_write_json(path, doc)
        persisted.append({"appid": str(doc["appid"]), "path": path.as_posix(), "dossier_sha256": canonical_sha256(doc)})

    next_manifest = copy.deepcopy(manifest)
    remaining = list(manifest["remaining_required_items"])
    if remaining[:len(current)] != list(current):
        raise ValueError("current checkpoint is not the canonical prefix of remaining daily snapshot scope")
    next_remaining = remaining[len(current):]
    next_manifest.update(progress_fields(
        manifest["snapshot_id"], manifest["prepared_required_items"], next_remaining,
        int(contract["checkpointing"]["checkpoint_size"]),
    ))
    next_manifest = ensure_web_evidence_binding(next_manifest)
    validate_manifest(next_manifest, contract)
    if manifest_output_path is not None:
        atomic_write_json(manifest_output_path, next_manifest)
    return persisted, next_manifest


def build_semantic_input_strict(pin, contract, store_dir, *, now=None):
    """Keep Taste Semantic Producer input shape unchanged while requiring fresh V2 dossiers."""
    validate_pin(pin)
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    rows = []
    missing = []
    for row in pin["ordered_rows"]:
        appid = str(row["appid"])
        doc = load_dossier_if_present(store_dir, appid)
        try:
            state = dossier_state_strict(doc, contract, now=now, expected_appid=appid)
        except ValueError as exc:
            missing.append({"key": row["key"], "appid": appid, "state": "invalid", "error": str(exc)})
            continue
        if state != "fresh":
            missing.append({"key": row["key"], "appid": appid, "state": state})
            continue
        rows.append({
            "key": row["key"],
            "appid": appid,
            "taste_fingerprint": row.get("taste_fingerprint"),
            "candidate_context_sha256": row.get("candidate_context_sha256"),
            "work_required": list(row.get("work_required") or []),
            "dossier": doc,
            "dossier_binding": {
                "dossier_sha256": canonical_sha256(doc),
                "generated_at_utc": doc["generated_at_utc"],
                "expires_at_utc": doc["expires_at_utc"],
            },
        })
    if missing:
        raise ValueError("Taste semantic input held: missing/stale/invalid web-evidence dossier(s): " + __import__("json").dumps(missing, ensure_ascii=False))
    out = {
        "schema": SEMANTIC_INPUT_SCHEMA,
        "schema_version": 1,
        "status": "ready_for_taste_semantic_producer",
        "prepared_at_utc": utc_iso(now),
        "pin": {
            "schema": pin["schema"],
            "ordered_work_unit_sha256": pin["ordered_work_unit_sha256"],
            "producer_id": pin.get("producer_id"),
            "producer_generation": pin.get("producer_generation"),
            "profile_identity": pin.get("profile_identity"),
            "bindings": pin.get("bindings"),
        },
        "rows": rows,
    }
    out["semantic_input_sha256"] = canonical_sha256({"pin": out["pin"], "rows": rows})
    return out
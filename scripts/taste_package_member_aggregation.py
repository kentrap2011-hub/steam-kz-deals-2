#!/usr/bin/env python3
"""Deterministic package-member identity and Taste aggregation helpers.

This module is intentionally price/deal blind.  It does not evaluate package
quality and never averages Taste across package size.  Package commercial
identity remains upstream/downstream of these helpers.
"""
import copy

PACKAGE_AI_CONDITION = "bundle_or_package_taste_evaluation_required"
PACKAGE_MEMBER_AGGREGATION_POLICY = "best-qualifying-member-no-average-v1"
PACKAGE_MEMBER_FAMILY_TYPES = {"franchise_bundle"}
INDEPENDENT_GAME_FAMILY_TYPES = {"base_game", "edition_family"}
_FIT_PRIORITY = {"strong": 2, "moderate": 1}


def ordered_unique_numeric(values):
    out = []
    seen = set()
    for value in values if isinstance(values, list) else []:
        appid = str(value or "")
        if not appid.isdigit() or appid in seen:
            continue
        seen.add(appid)
        out.append(appid)
    return out


def package_base_appids(value):
    """Return authoritative meaningful game appids, never arbitrary bundle members."""
    if isinstance(value, dict) and isinstance(value.get("semantic_condition"), dict):
        return ordered_unique_numeric(value["semantic_condition"].get("base_appids"))
    if isinstance(value, dict):
        return ordered_unique_numeric(value.get("base_appids"))
    return []


def build_member_subject_index(families):
    """Map exact base appids to their existing independent-game Taste subject.

    Addon/DLC and package families are deliberately excluded.  Edition-family
    members may share one canonical game Taste subject, which is existing
    family-graph behavior rather than a new package-specific semantic worker.
    """
    index = {}
    for family in families if isinstance(families, list) else []:
        if not isinstance(family, dict) or family.get("family_type") not in INDEPENDENT_GAME_FAMILY_TYPES:
            continue
        key = family.get("taste_subject_key")
        if not isinstance(key, str) or not key:
            continue
        for appid in ordered_unique_numeric(family.get("base_appids")):
            existing = index.get(appid)
            if existing is not None and existing != key:
                raise ValueError(
                    f"base appid {appid} maps to multiple independent Taste subjects: "
                    f"{existing!r}, {key!r}"
                )
            index[appid] = key
    return index


def _member_signal(appid, key, row):
    signal = {
        "appid": appid,
        "taste_subject_key": key,
        "status": row.get("status") if isinstance(row, dict) else "missing",
        "verdict": None,
        "fit_level": None,
        "negative_analysis_ready": False,
        "fit_evidence_backfill_required": False,
    }
    if not isinstance(row, dict) or row.get("status") != "cache_hit":
        return signal
    cached = row.get("cached_taste")
    if not isinstance(cached, dict):
        raise ValueError(f"cache_hit member {key} has no cached_taste")
    verdict = cached.get("verdict")
    fit = cached.get("fit_level")
    if verdict == "INCLUDE" and fit not in _FIT_PRIORITY:
        raise ValueError(f"package member {key} has unsupported INCLUDE fit level {fit!r}")
    if verdict not in {"INCLUDE", "EXCLUDE"}:
        raise ValueError(f"package member {key} has unsupported verdict {verdict!r}")
    signal.update({
        "verdict": verdict,
        "fit_level": fit,
        "negative_analysis_ready": bool(row.get("negative_analysis_ready")),
        "fit_evidence_backfill_required": bool(row.get("fit_evidence_backfill_required")),
    })
    return signal


def aggregate_package_member_taste(family, taste_entries, member_subject_index):
    """Resolve package Taste from independently evaluated member-game signals.

    Rules:
    - each authoritative base_appid is mapped to an existing independent game
      Taste subject;
    - any known INCLUDE/strong or INCLUDE/moderate member keeps the package
      Taste-eligible, even when another member is weak or unresolved;
    - strong outranks moderate; ties follow canonical base_appid order;
    - no numeric/fit averaging is performed;
    - when no member qualifies and any member is unresolved, the package waits
      on member work instead of creating package semantic work;
    - when every member is resolved below threshold, the first canonical member
      supplies the existing below-threshold semantic shape for downstream
      compatibility.  Package-quality penalties remain outside Taste.
    """
    if not isinstance(family, dict) or family.get("family_type") not in PACKAGE_MEMBER_FAMILY_TYPES:
        raise ValueError("package member Taste aggregation requires a franchise_bundle family")
    base_appids = ordered_unique_numeric(family.get("base_appids"))
    if len(base_appids) < 2:
        raise ValueError("franchise_bundle must expose at least two authoritative base_appids")

    members = []
    resolved_rows = []
    qualifying = []
    unresolved = []
    for order, appid in enumerate(base_appids):
        key = member_subject_index.get(appid)
        if not key:
            raise ValueError(f"package base appid {appid} has no independent game Taste subject")
        row = taste_entries.get(key) if isinstance(taste_entries, dict) else None
        signal = _member_signal(appid, key, row)
        signal["order"] = order
        members.append(signal)
        if signal["status"] != "cache_hit":
            unresolved.append(signal)
            continue
        resolved_rows.append((signal, row))
        if signal["verdict"] == "INCLUDE" and signal["fit_level"] in _FIT_PRIORITY:
            qualifying.append((signal, row))

    if qualifying:
        selected_signal, selected_row = max(
            qualifying,
            key=lambda pair: (_FIT_PRIORITY[pair[0]["fit_level"]], -pair[0]["order"]),
        )
        status = "resolved_eligible"
        eligible = True
    elif unresolved:
        return {
            "policy": PACKAGE_MEMBER_AGGREGATION_POLICY,
            "status": "member_semantic_pending",
            "package_taste_eligible": None,
            "base_appids": base_appids,
            "members": members,
            "selected_member": None,
            "effective_taste_row": None,
            "semantic_dependency_pending": True,
        }
    else:
        if not resolved_rows:
            raise ValueError("package member aggregation has no resolved member rows")
        selected_signal, selected_row = resolved_rows[0]
        status = "resolved_all_below_threshold"
        eligible = False

    selected = {
        "appid": selected_signal["appid"],
        "taste_subject_key": selected_signal["taste_subject_key"],
        "verdict": selected_signal["verdict"],
        "fit_level": selected_signal["fit_level"],
    }
    dependency_pending = (
        bool(selected_signal["fit_evidence_backfill_required"])
        or not bool(selected_signal["negative_analysis_ready"])
    )
    return {
        "policy": PACKAGE_MEMBER_AGGREGATION_POLICY,
        "status": status,
        "package_taste_eligible": eligible,
        "base_appids": base_appids,
        "members": members,
        "selected_member": selected,
        "effective_taste_row": copy.deepcopy(selected_row),
        "semantic_dependency_pending": dependency_pending,
    }

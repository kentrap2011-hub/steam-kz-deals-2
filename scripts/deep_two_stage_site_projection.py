#!/usr/bin/env python3
"""Non-active Deep two-stage site projection. GitHub-owned; browser only renders it.

Integration/cutover must explicitly call project_visual after the new ranking and
purchase producers have populated producer-owned purchase_score_0_40 and
wishlist_bonus_0_or_4. This module never activates itself or writes production.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from decimal import Decimal, InvalidOperation
from pathlib import Path

CONTRACT = "DEEP-TWO-STAGE-SITE-PROJECTION-V1"
STAGE1_WORK = "DEEP-STAGE1-WORK-V1"
STAGE1_STATE = "DEEP-STAGE1-STATE-V1"
STAGE2_STATE = "DEEP-STAGE2-STATE-V1"


class ProjectionError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ProjectionError(message)


def score(value, maximum):
    require(value is not None and not isinstance(value, bool), "missing canonical score")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ProjectionError("invalid canonical score") from None
    require(number.is_finite() and 0 <= number <= maximum,
            "canonical score outside allowed bounds")
    return number


def display(value):
    return float(value.quantize(Decimal("0.01")))


def percent(done, total):
    require(isinstance(done, int) and isinstance(total, int) and
            0 <= done <= total, "invalid canonical statistics denominator")
    return round(100 * done / total, 1) if total else 0.0


def load_accepted_stage1(entry, *, root):
    """Read only the SHA-bound result referenced by GitHub's accepted Stage-1 state."""
    require(entry.get("status") == "accepted" and entry.get("accepted") is True,
            "unaccepted Stage-1 state cannot be displayed")
    rel = entry.get("accepted_result_path")
    digest = entry.get("accepted_result_sha256")
    require(isinstance(rel, str) and isinstance(digest, str) and len(digest) == 64,
            "Stage-1 result path/digest missing")
    path = Path(rel)
    require(not path.is_absolute() and ".." not in path.parts and
            path.parent == Path("data/cache/deep_stage1_results"),
            "noncanonical Stage-1 result path")
    contents = (Path(root) / path).read_bytes()
    require(hashlib.sha256(contents).hexdigest() == digest,
            "Stage-1 result bytes no longer match accepted state")
    doc = json.loads(contents)
    require(doc.get("contract") == "DEEP-STAGE1-RESULT-V1" and
            doc.get("work_id") == entry.get("work_id") and
            doc.get("family_id") == entry.get("family_id") and
            str(doc.get("appid")) == str(entry.get("appid")) and
            doc.get("profile_semantic_sha256") == entry.get("profile_semantic_sha256") and
            doc.get("dossier_content_sha256") == entry.get("dossier_content_sha256"),
            "Stage-1 result binding mismatch")
    return doc


def canonical_states(stage1_work, stage1_state, stage2_state):
    require(stage1_work.get("contract") == STAGE1_WORK and
            stage1_state.get("contract") == STAGE1_STATE and
            stage2_state.get("contract") == STAGE2_STATE,
            "noncanonical frozen stage state/work")
    eligible = stage1_work.get("eligible_work_ids")
    entries1 = stage1_state.get("entries")
    entries2 = stage2_state.get("entries")
    require(isinstance(eligible, list) and len(set(eligible)) == len(eligible) and
            isinstance(entries1, dict) and isinstance(entries2, dict),
            "invalid GitHub-owned stage state")
    require(isinstance(stage1_state.get("progress"), dict) and
            isinstance(stage2_state.get("progress"), dict),
            "canonical stage progress unavailable")
    return set(eligible), entries1, entries2


def stage_statistics(stage1_work, stage1_state, stage2_state, dossier_status):
    """Statistics come from canonical work/progress, never visible-card counts."""
    eligible, entries1, _ = canonical_states(stage1_work, stage1_state, stage2_state)
    outcomes = [entries1[w].get("outcome") for w in eligible if w in entries1]
    fit = outcomes.count("analyzed_fit")
    not_fit = outcomes.count("analyzed_not_fit")
    diagnostic = outcomes.count("analysis_incomplete")
    pending = len(eligible) - len(outcomes)
    progress1 = stage1_state["progress"]
    expected1 = {
        "total_eligible": len(eligible), "completed_fit": fit,
        "completed_not_fit": not_fit, "diagnostic_incomplete": diagnostic,
        "pending": pending,
    }
    require(all(progress1.get(k) == v for k, v in expected1.items()),
            "stale Stage-1 canonical progress")
    progress2 = stage2_state["progress"]
    eligible2 = progress2.get("stage1_fit_eligible")
    calibrated = progress2.get("calibrated")
    awaiting = progress2.get("awaiting_calibration")
    diagnostic2 = progress2.get("diagnostic_incomplete")
    require(all(type(v) is int and v >= 0 for v in
                (eligible2, calibrated, awaiting, diagnostic2)) and
            calibrated + awaiting + diagnostic2 <= eligible2 and eligible2 == fit,
            "invalid Stage-2 canonical progress")
    require(isinstance(dossier_status, dict), "canonical Dossier status missing")
    dossier = {
        "total_eligible": dossier_status.get("dossier_total_current_scope"),
        "completed": dossier_status.get("dossier_accepted_count"),
        "pending": dossier_status.get("dossier_pending_count"),
        "diagnostic_incomplete": dossier_status.get("dossier_failed_or_recovery_count"),
        "last_attempt_at_utc": dossier_status.get("dossier_last_write_at_utc"),
        # Last write is NOT proof of successful Dossier acceptance.
        "last_successful_result_at_utc": dossier_status.get(
            "dossier_last_successful_result_at_utc"),
    }
    if all(type(dossier[k]) is int and dossier[k] >= 0 for k in
           ("total_eligible", "completed", "pending", "diagnostic_incomplete")):
        require(dossier["total_eligible"] == dossier["completed"] +
                dossier["pending"] + dossier["diagnostic_incomplete"],
                "Dossier current-scope arithmetic mismatch")
        dossier["progress_percent"] = percent(
            dossier["completed"], dossier["total_eligible"])
    else:
        dossier["progress_percent"] = None
    return {
        "deep_two_stage_site_contract": CONTRACT,
        "dossier": dossier,
        "deep_stage1": {
            **expected1,
            "completed": fit + not_fit,
            "last_attempt_at_utc": progress1.get("last_attempt_at_utc"),
            "last_successful_result_at_utc": progress1.get("last_successful_result_at_utc"),
            "progress_percent": percent(fit + not_fit, len(eligible)),
        },
        "deep_stage2": {
            "stage1_fit_eligible": eligible2,
            "calibrated": calibrated, "awaiting_calibration": awaiting,
            "diagnostic_incomplete": diagnostic2,
            "last_attempt_at_utc": progress2.get("last_attempt_at_utc"),
            "last_successful_calibration_at_utc": progress2.get(
                "last_successful_calibration_at_utc"),
            "progress_percent": percent(calibrated, eligible2),
        },
    }


def finding_text(rows):
    require(isinstance(rows, list), "accepted Stage-1 findings must be lists")
    return [row["text_ru"] for row in rows]


def project_game(game, *, stage1_entry=None, stage1_result=None,
                 stage2_entry=None, stage1_eligible=False,
                 anchor_catalog=None):
    """Mirror exactly supplied, already-bound GitHub state into one card."""
    result = deepcopy(game)
    dossier = result.get("dossier_stage_state")
    result["deep_two_stage_site_contract"] = CONTRACT
    result["dossier_status"] = {
        "accepted": "ready", "failed_or_recovery": "failed_or_recovery",
        "not_ready": "pending", "not_required": "not_required",
    }.get(dossier, "pending")
    result["stage1_status"] = "pending" if stage1_eligible else "not_ready"
    result["stage2_status"] = "not_eligible"
    result["stage1_provisional_deep_fit_score_0_56"] = None
    result["stage2_calibrated_deep_fit_score_0_56"] = None
    result["stage2_calibration_delta"] = None
    result["stage1_point_breakdown"] = []
    result["stage2_neighbor_comparisons"] = []
    result["stage2_why_changed_ru"] = None
    result["stage1_summary_ru"] = None
    result["stage1_positives"] = []
    result["stage1_negatives"] = []
    result["stage1_nuances"] = []
    result["stage2_why_above_ru"] = []
    result["stage2_why_below_ru"] = []
    bonus = score(result.get("wishlist_bonus_0_or_4"), 4)
    require(bonus in {Decimal(0), Decimal(4)}, "Wishlist must be 0 or +4")
    purchase = score(result.get("purchase_score_0_40"), 40)
    result["wishlist_bonus_0_or_4"] = int(bonus)
    result["purchase_score_0_40"] = display(purchase)
    result["personal_quality_score_0_60"] = None
    result["total_score_0_100"] = None
    if stage1_entry is not None:
        require(stage1_eligible and stage1_result is not None and
                stage1_entry.get("status") == "accepted",
                "Stage-1 state must be current and accepted")
        require(stage1_result.get("work_id") == stage1_entry.get("work_id"),
                "Stage-1 result and state identity mismatch")
        outcome = stage1_entry.get("outcome")
        result["stage1_status"] = {
            "analyzed_fit": "completed_fit",
            "analyzed_not_fit": "completed_not_fit",
            "analysis_incomplete": "diagnostic_incomplete",
        }[outcome]
        result["stage1_summary_ru"] = stage1_result.get("summary_ru")
        for source, target in (("positives", "stage1_positives"),
                               ("negatives", "stage1_negatives"),
                               ("nuances", "stage1_nuances")):
            result[target] = finding_text(stage1_result[source])
        reasons = {
            finding["finding_id"]: finding["text_ru"]
            for part in ("positives", "negatives", "nuances")
            for finding in stage1_result[part]
        }
        breakdown = deepcopy(stage1_result["point_breakdown"])
        for row in breakdown:
            refs = row.get("finding_refs") or []
            require(all(ref in reasons for ref in refs),
                    "Stage-1 point breakdown has unbound findings")
            row["finding_reasons_ru"] = [reasons[ref] for ref in refs]
        result["stage1_point_breakdown"] = breakdown
        if outcome == "analyzed_fit":
            provisional = score(stage1_result["provisional_deep_fit_score_0_56"], 56)
            result["stage1_provisional_deep_fit_score_0_56"] = display(provisional)
            result["stage2_status"] = "awaiting_calibration"
        if stage2_entry is not None:
            require(outcome == "analyzed_fit" and
                    stage2_entry.get("stage1_work_id") == stage1_entry.get("work_id") and
                    stage2_entry.get("stage1_result_sha256") ==
                    stage1_entry.get("accepted_result_sha256") and
                    stage2_entry.get("profile_semantic_sha256") ==
                    stage1_entry.get("profile_semantic_sha256"),
                    "Stage-2 entry not bound to exactly accepted Stage-1 result")
            if stage2_entry.get("status") == "calibrated":
                calibrated = score(stage2_entry.get("calibrated_deep_fit_score_0_56"), 56)
                require((calibrated * 100) == (calibrated * 100).to_integral_value(),
                        "Stage-2 score requires 0.01 precision")
                result["stage2_status"] = "calibrated"
                result["stage2_calibrated_deep_fit_score_0_56"] = display(calibrated)
                result["stage2_calibration_delta"] = display(calibrated - provisional)
                result["personal_quality_score_0_60"] = display(calibrated + bonus)
                result["total_score_0_100"] = display(calibrated + bonus + purchase)
                comparisons = deepcopy(stage2_entry.get("comparisons") or [])
                for comparison in comparisons:
                    anchor = (anchor_catalog or {}).get(comparison.get("anchor_id"))
                    if anchor:
                        comparison["anchor_appid"] = anchor["appid"]
                        comparison["anchor_title_ru"] = anchor["title_ru"]
                result["stage2_neighbor_comparisons"] = comparisons
                result["stage2_why_changed_ru"] = stage2_entry.get("why_stage2_changed_ru")
                result["stage2_why_above_ru"] = deepcopy(stage2_entry.get("why_above_ru") or [])
                result["stage2_why_below_ru"] = deepcopy(stage2_entry.get("why_below_ru") or [])
            elif stage2_entry.get("status") in {"calibration_incomplete", "stage1_contradiction"}:
                result["stage2_status"] = "diagnostic_incomplete"
            else:
                raise ProjectionError("unrecognized Stage-2 canonical entry")
    elif stage2_entry is not None:
        raise ProjectionError("Stage-2 entry without current Stage-1 acceptance")
    # Legacy Fast/Deep score and score_breakdown are never authority in this mode.
    result.pop("score_breakdown", None)
    result.pop("personal_score", None)
    result.pop("total_score", None)
    if result["stage2_status"] == "calibrated":
        # Legacy card/queue consumers may use this canonical calibrated alias,
        # but no older Fast/Stage-1 score survives before Stage 2.
        result["total_score"] = result["total_score_0_100"]
    return result


def project_visual(visual, *, stage1_work, stage1_state, stage2_state,
                   root="."):
    """Explicit cutover-only entrypoint; caller must supply new scorer fields.

    No implicit use from existing build_final_visual_payload.py: integration
    owns activation and pass-through of the new ranking/purchase outputs.
    """
    eligible, entries1, entries2 = canonical_states(stage1_work, stage1_state, stage2_state)
    # Work.items contains pending eligible scope, while accepted entries carry
    # completed work that is no longer present in the pending item list.
    stage1_by_family = {}
    for item in stage1_work.get("items", []):
        work_id = item.get("work_id")
        require(work_id in eligible, "non-eligible Stage-1 work item")
        key = (item.get("family_id"), str(item.get("appid")))
        require(key not in stage1_by_family, "duplicate Stage-1 work family/appid")
        stage1_by_family[key] = work_id
    for work_id in eligible:
        entry = entries1.get(work_id)
        if entry:
            key = (entry.get("family_id"), str(entry.get("appid")))
            require(key not in stage1_by_family or stage1_by_family[key] == work_id,
                    "ambiguous Stage-1 family/appid binding")
            stage1_by_family[key] = work_id
    stage2_by_stage1 = {}
    for entry in entries2.values():
        key = entry.get("stage1_work_id")
        if key:
            require(key not in stage2_by_stage1, "ambiguous Stage-2 stage1 binding")
            stage2_by_stage1[key] = entry
    projected = deepcopy(visual)
    # The calibrated anchor ID is a SHA, not a useful game name. Resolve
    # canonical Stage-2 anchor identities to the published title when present,
    # otherwise expose the exact Steam AppID instead of inventing a title.
    items = projected.get("items", [])
    titles = {(game.get("family_id"), str(game.get("appid"))): game.get("title")
              for game in items}
    anchor_catalog = {}
    for anchor_id, entry in entries2.items():
        if entry.get("status") != "calibrated":
            continue
        family, appid = entry.get("family_id"), str(entry.get("appid"))
        anchor_catalog[anchor_id] = {
            "appid": appid,
            "title_ru": titles.get((family, appid)) or f"Steam AppID {appid}",
        }
    output = []
    for game in items:
        family = game.get("family_id")
        appid = game.get("appid")
        work_id = stage1_by_family.get((family, str(appid)))
        match = entries1.get(work_id) if work_id else None
        stage1_result = load_accepted_stage1(match, root=root) if match else None
        output.append(project_game(
            game, stage1_entry=match, stage1_result=stage1_result,
            stage2_entry=stage2_by_stage1.get(work_id) if work_id else None,
            stage1_eligible=work_id is not None,
            anchor_catalog=anchor_catalog,
        ))
    projected["items"] = output
    old_status = projected.get("processing_status") or {}
    projected["processing_status"] = {
        **old_status,
        **stage_statistics(stage1_work, stage1_state, stage2_state, old_status),
    }
    projected["deep_two_stage_site_contract"] = CONTRACT
    return projected

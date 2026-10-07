#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
STATE_CONTRACT = "DEEP-STAGE2-STATE-V1"
WORK_CONTRACT = "DEEP-STAGE2-WORK-V1"
RESULT_CONTRACT = "DEEP-STAGE2-RESULT-V1"
CANONICAL_RESULTS_ROOT = Path("data/cache/deep_stage2_results")
RESULT_INBOX_ROOT = Path("data/ai_inbox/deep_stage2/results")
REL_ABOVE = {"target_above", "near_tie_target_above"}
REL_BELOW = {"target_below", "near_tie_target_below"}
DIAGNOSTIC_CODES = {
    "window_not_bracketed",
    "strict_direction_not_supported",
    "stage1_evidence_contradiction",
    "stage2_worker_failure",
    "stale_anchor_window",
}


class Stage2Error(ValueError):
    pass


def fail(message: str) -> None:
    raise Stage2Error(message)


def load_json(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def file_sha256(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return value == value.lower()


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def dec(value: Any, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as exc:
        fail(f"{field}: invalid decimal {value!r}: {exc}")


def q2(value: Any) -> Decimal:
    return dec(value, "score").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def cents(value: Any) -> int:
    q = q2(value)
    c = q * 100
    if c != c.to_integral_value():
        fail(f"score is not representable at 0.01 precision: {value!r}")
    n = int(c)
    if not 0 <= n <= 5600:
        fail(f"score out of range 0..56: {value!r}")
    return n


def score_from_cents(value: int) -> float:
    if not 0 <= value <= 5600:
        fail(f"score cents out of range: {value}")
    return float((Decimal(value) / 100).quantize(Decimal("0.01")))


def empty_state() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "contract": STATE_CONTRACT,
        "implementation_status": "implemented_not_active",
        "entries": {},
        "diagnostic_history": [],
        "progress": {
            "stage1_fit_eligible": 0,
            "calibrated": 0,
            "awaiting_calibration": 0,
            "diagnostic_incomplete": 0,
            "last_attempt_at_utc": None,
            "last_successful_calibration_at_utc": None,
        },
        "last_placement": None,
    }


def validate_state(state: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(state, dict):
        fail("Stage-2 state must be an object")
    if state.get("schema_version") != 1 or state.get("contract") != STATE_CONTRACT:
        fail("Stage-2 state contract mismatch")
    if state.get("implementation_status") != "implemented_not_active":
        fail("Stage-2 implementation must remain non-active before cutover")
    if not isinstance(state.get("entries"), dict):
        fail("Stage-2 state entries must be an object")
    if not isinstance(state.get("diagnostic_history"), list):
        fail("Stage-2 diagnostic_history must be an array")
    if not isinstance(state.get("progress"), dict):
        fail("Stage-2 progress must be an object")
    active_scores: dict[int, str] = {}
    for key, entry in state["entries"].items():
        if not isinstance(entry, dict):
            fail(f"state entry {key!r} must be an object")
        if entry.get("status") != "calibrated":
            continue
        c = cents(entry.get("calibrated_deep_fit_score_0_56"))
        other = active_scores.get(c)
        if other is not None and other != key:
            fail(f"duplicate active calibrated score: {other}, {key}")
        active_scores[c] = key
    return state


def stage1_finding_ids(doc: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for field in ("positives", "negatives", "nuances"):
        rows = doc.get(field)
        if not isinstance(rows, list):
            fail(f"Stage-1 {field} must be an array")
        for row in rows:
            if not isinstance(row, dict):
                fail(f"Stage-1 {field} row must be an object")
            finding_id = row.get("finding_id")
            if not isinstance(finding_id, str) or not finding_id:
                fail(f"Stage-1 {field} finding_id missing")
            if finding_id in ids:
                fail(f"duplicate Stage-1 finding_id {finding_id}")
            ids.add(finding_id)
    return ids


def validate_stage1_fit_result(doc: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(doc, dict):
        fail("Stage-1 result must be an object")
    if doc.get("schema_version") != 1 or doc.get("contract") != "DEEP-STAGE1-RESULT-V1":
        fail("Stage-1 result contract mismatch")
    if doc.get("outcome") != "analyzed_fit":
        fail("Stage 2 accepts only analyzed_fit Stage-1 results")
    for field in ("work_id", "family_id", "appid", "profile_pin_sha256", "profile_semantic_sha256"):
        if not doc.get(field):
            fail(f"Stage-1 result missing {field}")
    for field in ("work_id", "profile_pin_sha256", "profile_semantic_sha256"):
        if not is_sha256(doc.get(field)):
            fail(f"Stage-1 {field} must be sha256")
    score = dec(doc.get("provisional_deep_fit_score_0_56"), "Stage-1 provisional score")
    if score < 0 or score > 56 or score * 10 != (score * 10).to_integral_value():
        fail("Stage-1 provisional score must be 0..56 at 0.1 precision")
    finding_ids = stage1_finding_ids(doc)
    breakdown = doc.get("point_breakdown")
    if not isinstance(breakdown, list) or not breakdown:
        fail("Stage-1 fit result requires point_breakdown")
    total = Decimal("0")
    for row in breakdown:
        if not isinstance(row, dict):
            fail("Stage-1 point_breakdown row must be object")
        total += dec(row.get("points"), "Stage-1 point_breakdown points")
        refs = row.get("finding_refs")
        if not isinstance(refs, list) or not refs:
            fail("Stage-1 point_breakdown finding_refs missing")
        unknown = set(refs) - finding_ids
        if unknown:
            fail(f"Stage-1 point_breakdown references unknown findings: {sorted(unknown)}")
    if total != score:
        fail(f"Stage-1 point breakdown {total} != provisional score {score}")
    return doc


def load_stage1_result(path: str, expected_sha256: str) -> dict[str, Any]:
    p = ROOT / path
    if not p.exists():
        fail(f"Stage-1 result path missing: {path}")
    observed = file_sha256(p)
    if observed != expected_sha256:
        fail(f"Stage-1 result hash mismatch for {path}")
    return validate_stage1_fit_result(load_json(p))


def anchor_descriptor_from_entry(entry: dict[str, Any]) -> dict[str, Any]:
    required = (
        "anchor_id",
        "family_id",
        "appid",
        "stage1_result_path",
        "stage1_result_sha256",
        "canonical_stage2_result_path",
        "canonical_stage2_result_sha256",
        "calibrated_deep_fit_score_0_56",
    )
    missing = [field for field in required if field not in entry]
    if missing:
        fail(f"calibrated state entry missing anchor fields: {missing}")
    return {field: entry[field] for field in required}


def active_calibrated_entries(state: dict[str, Any]) -> list[dict[str, Any]]:
    validate_state(state)
    rows = []
    for work_id, entry in state["entries"].items():
        if entry.get("status") != "calibrated":
            continue
        row = deepcopy(entry)
        row.setdefault("anchor_id", work_id)
        cents(row["calibrated_deep_fit_score_0_56"])
        rows.append(row)
    rows.sort(key=lambda row: (
        cents(row["calibrated_deep_fit_score_0_56"]),
        str(row.get("anchor_id") or ""),
    ))
    return rows


def select_anchor_window(
    provisional_score: Any,
    state: dict[str, Any],
    *,
    lower_count: int = 2,
    upper_count: int = 2,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if lower_count < 0 or upper_count < 0:
        fail("anchor counts cannot be negative")
    target = q2(provisional_score)
    rows = active_calibrated_entries(state)
    lower = [row for row in rows if q2(row["calibrated_deep_fit_score_0_56"]) < target]
    upper = [row for row in rows if q2(row["calibrated_deep_fit_score_0_56"]) > target]
    selected_lower = lower[-lower_count:] if lower_count else []
    selected_upper = upper[:upper_count] if upper_count else []
    return (
        [anchor_descriptor_from_entry(row) for row in selected_lower],
        [anchor_descriptor_from_entry(row) for row in selected_upper],
    )


def _normalized_anchor_set(
    lower_anchors: list[dict[str, Any]],
    upper_anchors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for side, anchors in (("lower", lower_anchors), ("upper", upper_anchors)):
        for anchor in anchors:
            row = deepcopy(anchor)
            row["side"] = side
            rows.append(row)
    return rows


def make_work_item(
    candidate: dict[str, Any],
    state: dict[str, Any],
    *,
    sequence: int,
    lower_count: int = 2,
    upper_count: int = 2,
    anchor_window_revision: int = 1,
) -> dict[str, Any]:
    if anchor_window_revision < 1:
        fail("anchor_window_revision must be >= 1")
    result = candidate.get("stage1_result")
    if not isinstance(result, dict):
        fail("candidate requires stage1_result")
    validate_stage1_fit_result(result)
    result_path = candidate.get("stage1_result_path")
    result_sha = candidate.get("stage1_result_sha256")
    profile_pin = candidate.get("profile_pin")
    if not isinstance(result_path, str) or not result_path:
        fail("candidate stage1_result_path missing")
    if not is_sha256(result_sha):
        fail("candidate stage1_result_sha256 invalid")
    if profile_pin is None:
        fail("candidate profile_pin missing")
    if candidate.get("profile_semantic_sha256") != result.get("profile_semantic_sha256"):
        fail("candidate profile semantic binding disagrees with Stage-1 result")
    if candidate.get("stage1_work_id") != result.get("work_id"):
        fail("candidate stage1_work_id disagrees with Stage-1 result")
    if candidate.get("family_id") != result.get("family_id"):
        fail("candidate family_id disagrees with Stage-1 result")
    if str(candidate.get("appid")) != str(result.get("appid")):
        fail("candidate appid disagrees with Stage-1 result")

    lower, upper = select_anchor_window(
        result["provisional_deep_fit_score_0_56"],
        state,
        lower_count=lower_count,
        upper_count=upper_count,
    )
    if not lower and not upper:
        fail("no already-calibrated anchors available; Stage-2 bootstrap is not defined by the frozen contract")

    anchor_set = _normalized_anchor_set(lower, upper)
    anchor_set_sha256 = canonical_sha256(anchor_set)
    anchor_window_id = canonical_sha256({
        "target_stage1_result_sha256": result_sha,
        "anchor_window_revision": anchor_window_revision,
        "anchor_set_sha256": anchor_set_sha256,
        "anchors": anchor_set,
    })
    calibration_work_id = canonical_sha256({
        "stage1_work_id": result["work_id"],
        "stage1_result_sha256": result_sha,
        "profile_pin": profile_pin,
        "profile_semantic_sha256": result["profile_semantic_sha256"],
        "anchor_window_id": anchor_window_id,
        "anchor_window_revision": anchor_window_revision,
        "anchor_set_sha256": anchor_set_sha256,
    })
    return {
        "sequence": int(sequence),
        "calibration_work_id": calibration_work_id,
        "target_family_id": result["family_id"],
        "target_appid": str(result["appid"]),
        "profile_pin": deepcopy(profile_pin),
        "profile_semantic_sha256": result["profile_semantic_sha256"],
        "stage1_result_path": result_path,
        "stage1_result_sha256": result_sha,
        "stage1_work_id": result["work_id"],
        "anchor_window_id": anchor_window_id,
        "anchor_window_revision": anchor_window_revision,
        "anchor_set_sha256": anchor_set_sha256,
        "lower_anchors": lower,
        "upper_anchors": upper,
        "result_submission_path": str(RESULT_INBOX_ROOT / f"{calibration_work_id}.json"),
    }


def build_work_manifest(
    candidates: Iterable[dict[str, Any]],
    state: dict[str, Any],
    *,
    generated_at_utc: str | None = None,
    lower_count: int = 2,
    upper_count: int = 2,
) -> dict[str, Any]:
    validate_state(state)
    fit_candidates = list(candidates)
    items: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    for ordinal, candidate in enumerate(fit_candidates, start=1):
        result = candidate.get("stage1_result")
        try:
            validate_stage1_fit_result(result)
        except Stage2Error as exc:
            diagnostics.append({
                "stage1_work_id": candidate.get("stage1_work_id"),
                "code": "stage1_candidate_invalid",
                "detail": str(exc),
            })
            continue

        prior = None
        for entry in state["entries"].values():
            if (
                entry.get("stage1_work_id") == result["work_id"]
                and entry.get("stage1_result_sha256") == candidate.get("stage1_result_sha256")
                and entry.get("profile_semantic_sha256") == result["profile_semantic_sha256"]
            ):
                prior = entry
                break
        if prior and prior.get("status") == "calibrated":
            continue
        if prior and prior.get("status") in {"calibration_incomplete", "stage1_contradiction"}:
            diagnostics.append({
                "stage1_work_id": result["work_id"],
                "code": "explicit_retry_or_reanalysis_required",
                "detail": "GitHub must explicitly authorize a new window/retry; builder does not auto-retry diagnostics.",
            })
            continue

        try:
            item = make_work_item(
                candidate,
                state,
                sequence=int(candidate.get("sequence") or ordinal),
                lower_count=lower_count,
                upper_count=upper_count,
                anchor_window_revision=int(candidate.get("anchor_window_revision") or 1),
            )
        except Stage2Error as exc:
            diagnostics.append({
                "stage1_work_id": result["work_id"],
                "code": "anchor_window_unavailable",
                "detail": str(exc),
            })
            continue
        items.append(item)

    items.sort(key=lambda row: (row["sequence"], row["calibration_work_id"]))
    return {
        "schema_version": 1,
        "contract": WORK_CONTRACT,
        "generated_at_utc": generated_at_utc or now_utc_iso(),
        "stage1_fit_eligible": len(fit_candidates),
        "items": items,
        "diagnostics": diagnostics,
    }


def validate_work_manifest(work: dict[str, Any]) -> dict[str, Any]:
    if work.get("schema_version") != 1 or work.get("contract") != WORK_CONTRACT:
        fail("Stage-2 work contract mismatch")
    if not isinstance(work.get("items"), list) or not isinstance(work.get("diagnostics"), list):
        fail("Stage-2 work items/diagnostics shape invalid")
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    last_sequence = None
    required = {
        "sequence", "calibration_work_id", "target_family_id", "target_appid",
        "profile_pin", "profile_semantic_sha256", "stage1_result_path",
        "stage1_result_sha256", "stage1_work_id", "anchor_window_id",
        "anchor_window_revision", "anchor_set_sha256", "lower_anchors",
        "upper_anchors", "result_submission_path",
    }
    for item in work["items"]:
        if set(item) != required:
            fail("Stage-2 work item fields mismatch")
        if not is_sha256(item["calibration_work_id"]):
            fail("calibration_work_id invalid")
        if item["calibration_work_id"] in seen_ids:
            fail("duplicate calibration_work_id")
        seen_ids.add(item["calibration_work_id"])
        expected_path = str(RESULT_INBOX_ROOT / f"{item['calibration_work_id']}.json")
        if item["result_submission_path"] != expected_path:
            fail("result_submission_path mismatch")
        if item["result_submission_path"] in seen_paths:
            fail("duplicate result_submission_path")
        seen_paths.add(item["result_submission_path"])
        if last_sequence is not None and item["sequence"] < last_sequence:
            fail("work item sequence is not monotonic")
        last_sequence = item["sequence"]
        anchors = _normalized_anchor_set(item["lower_anchors"], item["upper_anchors"])
        if canonical_sha256(anchors) != item["anchor_set_sha256"]:
            fail("anchor_set_sha256 mismatch")
        if not item["lower_anchors"] and not item["upper_anchors"]:
            fail("work item must contain at least one calibrated anchor")
        anchor_ids = []
        for row in item["lower_anchors"] + item["upper_anchors"]:
            descriptor = anchor_descriptor_from_entry(row)
            if descriptor != row:
                fail("anchor descriptor contains unknown fields")
            if not is_sha256(row["stage1_result_sha256"]):
                fail("anchor stage1_result_sha256 invalid")
            if not is_sha256(row["canonical_stage2_result_sha256"]):
                fail("anchor canonical_stage2_result_sha256 invalid")
            cents(row["calibrated_deep_fit_score_0_56"])
            anchor_ids.append(row["anchor_id"])
        if len(anchor_ids) != len(set(anchor_ids)):
            fail("duplicate anchor in work item")
    return work


RESULT_REQUIRED = {
    "schema_version", "contract", "calibration_work_id", "target_family_id",
    "target_appid", "profile_pin_sha256", "profile_semantic_sha256",
    "stage1_result_sha256", "anchor_window_id", "anchor_window_revision",
    "anchor_set_sha256", "outcome", "comparisons",
    "semantic_calibrated_deep_fit_target_0_56",
    "comparative_adjustment_from_stage1", "why_stage2_changed_ru",
    "why_above_ru", "why_below_ru", "diagnostic_code",
}


def validate_result(
    doc: dict[str, Any],
    item: dict[str, Any],
    *,
    stage1_loader=load_stage1_result,
) -> dict[str, Any]:
    if not isinstance(doc, dict) or set(doc) != RESULT_REQUIRED:
        fail("Stage-2 result shape mismatch")
    if doc.get("schema_version") != 1 or doc.get("contract") != RESULT_CONTRACT:
        fail("Stage-2 result contract mismatch")
    exact = {
        "calibration_work_id": item["calibration_work_id"],
        "target_family_id": item["target_family_id"],
        "target_appid": item["target_appid"],
        "profile_semantic_sha256": item["profile_semantic_sha256"],
        "stage1_result_sha256": item["stage1_result_sha256"],
        "anchor_window_id": item["anchor_window_id"],
        "anchor_window_revision": item["anchor_window_revision"],
        "anchor_set_sha256": item["anchor_set_sha256"],
    }
    for field, expected in exact.items():
        if doc.get(field) != expected:
            fail(f"Stage-2 exact binding mismatch for {field}")

    target = stage1_loader(item["stage1_result_path"], item["stage1_result_sha256"])
    if doc["profile_pin_sha256"] != target["profile_pin_sha256"]:
        fail("Stage-2 profile_pin_sha256 mismatch")
    if target["profile_semantic_sha256"] != item["profile_semantic_sha256"]:
        fail("Stage-2 profile semantic hash mismatch")
    target_findings = stage1_finding_ids(target)

    anchors_by_id: dict[str, tuple[str, dict[str, Any], dict[str, Any]]] = {}
    for side, rows in (("lower", item["lower_anchors"]), ("upper", item["upper_anchors"])):
        for anchor in rows:
            anchor_doc = stage1_loader(anchor["stage1_result_path"], anchor["stage1_result_sha256"])
            anchor_id = anchor["anchor_id"]
            if anchor_id in anchors_by_id:
                fail(f"duplicate anchor {anchor_id}")
            anchors_by_id[anchor_id] = (side, anchor, anchor_doc)

    outcome = doc["outcome"]
    if outcome not in {"calibrated_fit", "calibration_incomplete", "stage1_contradiction"}:
        fail(f"invalid Stage-2 outcome {outcome!r}")
    comparisons = doc["comparisons"]
    if not isinstance(comparisons, list):
        fail("comparisons must be an array")
    seen = set()
    for comp in comparisons:
        expected_keys = {
            "anchor_id", "relation", "reasons_ru",
            "target_stage1_finding_refs", "anchor_stage1_finding_refs",
        }
        if not isinstance(comp, dict) or set(comp) != expected_keys:
            fail("comparison shape mismatch")
        anchor_id = comp["anchor_id"]
        if anchor_id in seen or anchor_id not in anchors_by_id:
            fail(f"duplicate/out-of-window comparison anchor {anchor_id}")
        seen.add(anchor_id)
        side, _, anchor_doc = anchors_by_id[anchor_id]
        relation = comp["relation"]
        if relation not in REL_ABOVE | REL_BELOW:
            fail(f"invalid relation {relation!r}")
        if outcome == "calibrated_fit":
            if side == "lower" and relation not in REL_ABOVE:
                fail(f"lower anchor {anchor_id} requires target-above relation")
            if side == "upper" and relation not in REL_BELOW:
                fail(f"upper anchor {anchor_id} requires target-below relation")
        reasons = comp["reasons_ru"]
        target_refs = comp["target_stage1_finding_refs"]
        anchor_refs = comp["anchor_stage1_finding_refs"]
        if not isinstance(reasons, list) or not reasons or any(not isinstance(x, str) or not x for x in reasons):
            fail("comparison reasons_ru invalid")
        if len(reasons) != len(set(reasons)):
            fail("comparison reasons_ru must be unique")
        if not isinstance(target_refs, list) or not target_refs:
            fail("comparison target finding refs required")
        if not isinstance(anchor_refs, list) or not anchor_refs:
            fail("comparison anchor finding refs required")
        if len(target_refs) != len(set(target_refs)) or len(anchor_refs) != len(set(anchor_refs)):
            fail("comparison finding refs must be unique")
        if set(target_refs) - target_findings:
            fail("comparison cites unknown target finding")
        if set(anchor_refs) - stage1_finding_ids(anchor_doc):
            fail("comparison cites unknown anchor finding")

    if outcome == "calibrated_fit":
        if seen != set(anchors_by_id):
            fail("calibrated result must compare every supplied anchor exactly once")
        semantic = dec(doc["semantic_calibrated_deep_fit_target_0_56"], "semantic target")
        adjustment = dec(doc["comparative_adjustment_from_stage1"], "comparative adjustment")
        if semantic < 0 or semantic > 56 or semantic * 100 != (semantic * 100).to_integral_value():
            fail("semantic Stage-2 target must be 0..56 at 0.01 precision")
        if adjustment * 100 != (adjustment * 100).to_integral_value():
            fail("comparative adjustment must use 0.01 precision")
        provisional = dec(target["provisional_deep_fit_score_0_56"], "Stage-1 provisional score")
        if semantic - provisional != adjustment:
            fail("comparative adjustment mismatch")
        lower_scores = [
            dec(anchor["calibrated_deep_fit_score_0_56"], "lower anchor score")
            for anchor in item["lower_anchors"]
        ]
        upper_scores = [
            dec(anchor["calibrated_deep_fit_score_0_56"], "upper anchor score")
            for anchor in item["upper_anchors"]
        ]
        if lower_scores and semantic < max(lower_scores):
            fail("semantic target contradicts lower-anchor placement")
        if upper_scores and semantic > min(upper_scores):
            fail("semantic target contradicts upper-anchor placement")
        if not isinstance(doc["why_stage2_changed_ru"], str) or not doc["why_stage2_changed_ru"]:
            fail("calibrated result requires why_stage2_changed_ru")
        if item["lower_anchors"] and not doc["why_above_ru"]:
            fail("calibrated result requires why_above_ru")
        if item["upper_anchors"] and not doc["why_below_ru"]:
            fail("calibrated result requires why_below_ru")
        if doc["diagnostic_code"] is not None:
            fail("calibrated result diagnostic_code must be null")
    else:
        if doc["semantic_calibrated_deep_fit_target_0_56"] is not None:
            fail("diagnostic result cannot carry semantic target")
        if doc["comparative_adjustment_from_stage1"] is not None:
            fail("diagnostic result cannot carry adjustment")
        if doc["diagnostic_code"] not in DIAGNOSTIC_CODES:
            fail("diagnostic result requires valid diagnostic_code")
        if outcome == "stage1_contradiction" and doc["diagnostic_code"] != "stage1_evidence_contradiction":
            fail("stage1_contradiction diagnostic mismatch")

    for field in ("why_above_ru", "why_below_ru"):
        values = doc[field]
        if not isinstance(values, list) or any(not isinstance(x, str) or not x for x in values):
            fail(f"{field} invalid")
        if len(values) != len(set(values)):
            fail(f"{field} must contain unique strings")
    return doc


@dataclass(frozen=True)
class Cascade:
    side: str
    indices: tuple[int, ...]
    target_cent: int
    moved_count: int
    semantic_distance: int


def _find_lower_cascade(scores: list[int], lower_index: int, semantic_cent: int) -> Cascade | None:
    start = lower_index
    while start > 0 and scores[start] - scores[start - 1] == 1:
        start -= 1
    if scores[start] == 0:
        return None
    indices = tuple(range(start, lower_index + 1))
    return Cascade("lower", indices, scores[lower_index], len(indices), abs(scores[lower_index] - semantic_cent))


def _find_upper_cascade(scores: list[int], upper_index: int, semantic_cent: int) -> Cascade | None:
    end = upper_index
    while end + 1 < len(scores) and scores[end + 1] - scores[end] == 1:
        end += 1
    if scores[end] == 5600:
        return None
    indices = tuple(range(upper_index, end + 1))
    return Cascade("upper", indices, scores[upper_index], len(indices), abs(scores[upper_index] - semantic_cent))


def _choose_free_cent(lo: int, hi: int, semantic_cent: int, occupied: set[int]) -> int | None:
    if lo > hi:
        return None
    target = min(max(semantic_cent, lo), hi)
    if target not in occupied:
        return target
    max_delta = max(target - lo, hi - target)
    for delta in range(1, max_delta + 1):
        choices = []
        left, right = target - delta, target + delta
        if lo <= left <= hi and left not in occupied:
            choices.append(left)
        if lo <= right <= hi and right not in occupied:
            choices.append(right)
        if choices:
            return min(choices)
    return None


def place_canonical_score(
    state: dict[str, Any],
    item: dict[str, Any],
    semantic_target: Any,
) -> tuple[float, dict[str, Any]]:
    validate_state(state)
    entries = state["entries"]
    active = sorted(
        (
            cents(entry["calibrated_deep_fit_score_0_56"]),
            key,
            entry,
        )
        for key, entry in entries.items()
        if entry.get("status") == "calibrated"
    )
    scores = [row[0] for row in active]
    keys = [row[1] for row in active]
    occupied = set(scores)
    index_by_key = {key: idx for idx, key in enumerate(keys)}
    lower_ids = [row["anchor_id"] for row in item["lower_anchors"]]
    upper_ids = [row["anchor_id"] for row in item["upper_anchors"]]
    for anchor_id in lower_ids + upper_ids:
        if anchor_id not in index_by_key:
            fail(f"current state no longer contains calibrated anchor {anchor_id}")

    lower_index = max((index_by_key[a] for a in lower_ids), default=None)
    upper_index = min((index_by_key[a] for a in upper_ids), default=None)
    if lower_index is not None and upper_index is not None and lower_index >= upper_index:
        fail("anchor window is not strictly bracketed in current state")
    lower_cent = scores[lower_index] if lower_index is not None else -1
    upper_cent = scores[upper_index] if upper_index is not None else 5601
    semantic_cent = cents(semantic_target)
    chosen = _choose_free_cent(lower_cent + 1, upper_cent - 1, semantic_cent, occupied)
    respace: list[dict[str, Any]] = []

    if chosen is None:
        options: list[Cascade] = []
        if lower_index is not None:
            option = _find_lower_cascade(scores, lower_index, semantic_cent)
            if option:
                options.append(option)
        if upper_index is not None:
            option = _find_upper_cascade(scores, upper_index, semantic_cent)
            if option:
                options.append(option)
        if not options:
            fail("local deterministic re-spacing is impossible")
        cascade = min(options, key=lambda c: (c.moved_count, c.semantic_distance, c.side))
        if cascade.side == "lower":
            for idx in cascade.indices:
                key, old = keys[idx], scores[idx]
                entries[key]["calibrated_deep_fit_score_0_56"] = score_from_cents(old - 1)
                respace.append({"anchor_id": key, "from": score_from_cents(old), "to": score_from_cents(old - 1)})
            chosen = cascade.target_cent
        else:
            for idx in reversed(cascade.indices):
                key, old = keys[idx], scores[idx]
                entries[key]["calibrated_deep_fit_score_0_56"] = score_from_cents(old + 1)
                respace.append({"anchor_id": key, "from": score_from_cents(old), "to": score_from_cents(old + 1)})
            respace.reverse()
            chosen = cascade.target_cent

    final_score = score_from_cents(chosen)
    state["last_placement"] = {
        "calibration_work_id": item["calibration_work_id"],
        "semantic_target_0_56": float(q2(semantic_target)),
        "calibrated_deep_fit_score_0_56": final_score,
        "local_respace": respace,
    }
    seen = {}
    for key, entry in entries.items():
        if entry.get("status") != "calibrated":
            continue
        c = cents(entry["calibrated_deep_fit_score_0_56"])
        if c in seen:
            fail(f"local re-spacing produced duplicate score for {seen[c]} and {key}")
        seen[c] = key
    if chosen in seen:
        fail(f"target placement collides at {final_score}")
    return final_score, state["last_placement"]


def recompute_progress(
    state: dict[str, Any],
    *,
    stage1_fit_eligible: int | None = None,
    current_work_count: int | None = None,
) -> dict[str, Any]:
    entries = state["entries"].values()
    calibrated = sum(1 for e in entries if e.get("status") == "calibrated")
    diagnostics = sum(
        1 for e in entries
        if e.get("status") in {"calibration_incomplete", "stage1_contradiction"}
    )
    progress = state["progress"]
    if stage1_fit_eligible is not None:
        progress["stage1_fit_eligible"] = int(stage1_fit_eligible)
    if current_work_count is not None:
        progress["awaiting_calibration"] = int(current_work_count)
    else:
        progress["awaiting_calibration"] = max(
            int(progress.get("stage1_fit_eligible") or 0) - calibrated - diagnostics, 0
        )
    progress["calibrated"] = calibrated
    progress["diagnostic_incomplete"] = diagnostics
    return progress


def validate_item_against_state(item: dict[str, Any], state: dict[str, Any]) -> None:
    validate_state(state)
    for anchor in item["lower_anchors"] + item["upper_anchors"]:
        anchor_id = anchor["anchor_id"]
        current = state["entries"].get(anchor_id)
        if not isinstance(current, dict) or current.get("status") != "calibrated":
            fail(f"stale anchor window: anchor {anchor_id} is no longer calibrated")
        if anchor_descriptor_from_entry(current) != anchor:
            fail(f"stale anchor window: descriptor changed for anchor {anchor_id}")


def apply_validated_result(
    state: dict[str, Any],
    item: dict[str, Any],
    doc: dict[str, Any],
    *,
    canonical_result_path: str,
    canonical_result_sha256: str,
    accepted_at_utc: str | None = None,
) -> dict[str, Any]:
    state = deepcopy(validate_state(state))
    validate_item_against_state(item, state)
    accepted_at_utc = accepted_at_utc or now_utc_iso()
    if not is_sha256(canonical_result_sha256):
        fail("canonical result sha256 invalid")
    outcome = doc["outcome"]
    base = {
        "anchor_id": item["calibration_work_id"],
        "calibration_work_id": item["calibration_work_id"],
        "family_id": item["target_family_id"],
        "appid": item["target_appid"],
        "stage1_work_id": item["stage1_work_id"],
        "stage1_result_path": item["stage1_result_path"],
        "stage1_result_sha256": item["stage1_result_sha256"],
        "profile_semantic_sha256": item["profile_semantic_sha256"],
        "anchor_window_id": item["anchor_window_id"],
        "anchor_window_revision": item["anchor_window_revision"],
        "anchor_set_sha256": item["anchor_set_sha256"],
        "canonical_stage2_result_path": canonical_result_path,
        "canonical_stage2_result_sha256": canonical_result_sha256,
        "semantic_calibrated_deep_fit_target_0_56": doc["semantic_calibrated_deep_fit_target_0_56"],
        "comparative_adjustment_from_stage1": doc["comparative_adjustment_from_stage1"],
        "comparisons": deepcopy(doc["comparisons"]),
        "why_stage2_changed_ru": doc["why_stage2_changed_ru"],
        "why_above_ru": deepcopy(doc["why_above_ru"]),
        "why_below_ru": deepcopy(doc["why_below_ru"]),
        "diagnostic_code": doc["diagnostic_code"],
        "accepted_at_utc": accepted_at_utc,
    }
    if outcome == "calibrated_fit":
        final_score, placement = place_canonical_score(
            state, item, doc["semantic_calibrated_deep_fit_target_0_56"]
        )
        base.update({
            "status": "calibrated",
            "outcome": "calibrated_fit",
            "calibrated_deep_fit_score_0_56": final_score,
            "placement": deepcopy(placement),
        })
        state["progress"]["last_successful_calibration_at_utc"] = accepted_at_utc
    else:
        base.update({
            "status": outcome,
            "outcome": outcome,
            "calibrated_deep_fit_score_0_56": None,
            "placement": None,
        })
        state["diagnostic_history"].append({
            "calibration_work_id": item["calibration_work_id"],
            "stage1_work_id": item["stage1_work_id"],
            "outcome": outcome,
            "diagnostic_code": doc["diagnostic_code"],
            "anchor_window_id": item["anchor_window_id"],
            "anchor_window_revision": item["anchor_window_revision"],
            "accepted_at_utc": accepted_at_utc,
        })
    state["entries"][item["calibration_work_id"]] = base
    state["progress"]["last_attempt_at_utc"] = accepted_at_utc
    recompute_progress(state)
    validate_state(state)
    return state


def result_item_map(work: dict[str, Any]) -> dict[str, dict[str, Any]]:
    validate_work_manifest(work)
    return {item["result_submission_path"]: item for item in work["items"]}

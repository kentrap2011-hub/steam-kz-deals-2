#!/usr/bin/env python3
"""Non-active, GitHub-owned Deep Stage-1 manifest/state and strict result checks."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORK_CONTRACT = "DEEP-STAGE1-WORK-V1"
RESULT_CONTRACT = "DEEP-STAGE1-RESULT-V1"
STATE_CONTRACT = "DEEP-STAGE1-STATE-V1"
INBOX = Path("data/ai_inbox/deep_stage1/results")
RESULTS = Path("data/cache/deep_stage1_results")
DOSSIERS = Path("data/cache/taste_steam_review_dossiers")
SOURCE = "data/production/pre_ai/progressive_pass2_work.json"
WORK_REQUIRED = {
    "sequence", "semantic_generation_id", "work_id", "family_id",
    "taste_subject_key", "appid", "candidate_context_sha256",
    "profile_pin", "profile_semantic_sha256", "dossier_path",
    "dossier_content_sha256", "dossier_compatibility_binding",
    "semantic_input", "result_submission_path",
}
RESULT_REQUIRED = {
    "schema_version", "contract", "semantic_generation_id", "work_id",
    "family_id", "taste_subject_key", "appid", "candidate_context_sha256",
    "profile_pin_sha256", "profile_semantic_sha256", "dossier_content_sha256",
    "outcome", "confidence", "summary_ru", "positives", "negatives",
    "nuances", "provisional_deep_fit_score_0_56", "point_breakdown",
    "analysis_issue_code",
}
ISSUE_CODES = {
    "insufficient_evidence", "evidence_unavailable", "stage1_worker_failure",
    "profile_binding_unresolved", "dossier_binding_unresolved",
}


class Stage1Error(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Stage1Error(message)


def load_json(path: Path | str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def safe_repo_path(path: str, root: Path = ROOT) -> Path:
    require(isinstance(path, str) and path and "\\" not in path,
            "unsafe repository path")
    rel = Path(path)
    require(not rel.is_absolute() and ".." not in rel.parts, "repository path traversal")
    return root / rel


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def empty_state() -> dict:
    return {
        "schema_version": 1, "contract": STATE_CONTRACT,
        "implementation_status": "implemented_not_active",
        "entries": {}, "diagnostic_history": [],
        "progress": {
            "total_eligible": 0, "completed_fit": 0,
            "completed_not_fit": 0, "pending": 0,
            "diagnostic_incomplete": 0,
            "last_attempt_at_utc": None,
            "last_successful_result_at_utc": None,
        },
    }


def validate_state(state: dict) -> dict:
    require(isinstance(state, dict) and state.get("schema_version") == 1
            and state.get("contract") == STATE_CONTRACT, "Stage-1 state contract mismatch")
    require(state.get("implementation_status") == "implemented_not_active",
            "Stage-1 cannot become active before dedicated integration cutover")
    require(isinstance(state.get("entries"), dict), "Stage-1 entries must be mapping")
    require(isinstance(state.get("diagnostic_history"), list), "diagnostic history missing")
    require(isinstance(state.get("progress"), dict), "Stage-1 progress missing")
    for key, entry in state["entries"].items():
        require(is_sha(key) and isinstance(entry, dict)
                and entry.get("work_id") == key, "invalid Stage-1 state entry")
        require(entry.get("status") == "accepted" and entry.get("accepted") is True,
                "Stage-1 entries must only contain canonically accepted results")
        require(entry.get("outcome") in (
            "analyzed_fit", "analyzed_not_fit", "analysis_incomplete"
        ), "invalid accepted Stage-1 outcome")
        require(is_sha(entry.get("accepted_result_sha256")), "accepted result hash missing")
        require(isinstance(entry.get("accepted_result_path"), str),
                "accepted result path missing")
    return state


def _decimal_tenth(value: Any, field: str, low: Decimal, high: Decimal) -> Decimal:
    require(isinstance(value, (int, float, Decimal)) and not isinstance(value, bool),
            f"{field}: numeric value required")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise Stage1Error(f"{field}: invalid decimal") from exc
    require(result.is_finite() and low <= result <= high
            and result * 10 == (result * 10).to_integral_value(),
            f"{field}: out of range or not 0.1 precision")
    return result


def validate_work_manifest(work: dict) -> dict:
    require(isinstance(work, dict) and work.get("schema_version") == 1
            and work.get("contract") == WORK_CONTRACT, "Stage-1 work contract mismatch")
    require(work.get("implementation_status") == "implemented_not_active",
            "Stage-1 work cannot activate production")
    require(work.get("source") == SOURCE, "Stage-1 work source mismatch")
    require(isinstance(work.get("items"), list), "Stage-1 items missing")
    require(isinstance(work.get("diagnostics"), list), "Stage-1 diagnostics missing")
    eligible = work.get("eligible_work_ids")
    require(isinstance(eligible, list) and all(is_sha(x) for x in eligible)
            and len(set(eligible)) == len(eligible), "eligible Stage-1 work IDs invalid")
    require(work.get("total_eligible") == len(eligible), "total eligible mismatch")
    seen, paths, sequence = set(), set(), 0
    for item in work["items"]:
        require(isinstance(item, dict) and WORK_REQUIRED <= item.keys(),
                "missing frozen Stage-1 work item fields")
        require(isinstance(item["sequence"], int) and item["sequence"] > sequence,
                "Stage-1 work order must be monotonic and deterministic")
        sequence = item["sequence"]
        wid = item["work_id"]
        require(is_sha(wid) and wid not in seen and wid in eligible,
                "duplicate or unknown Stage-1 work identity")
        seen.add(wid)
        require(is_sha(item["semantic_generation_id"])
                and is_sha(item["candidate_context_sha256"])
                and is_sha(item["profile_semantic_sha256"])
                and is_sha(item["dossier_content_sha256"]),
                "Stage-1 binding SHA invalid")
        require(isinstance(item["family_id"], str) and item["family_id"]
                and isinstance(item["taste_subject_key"], str)
                and item["taste_subject_key"], "Stage-1 identity missing")
        require(isinstance(item["appid"], str) and item["appid"].isdigit(),
                "Stage-1 appid must be digit string")
        pin = item["profile_pin"]
        require(isinstance(pin, dict) and is_sha(pin.get("pin_sha256")),
                "immutable profile pin invalid")
        require(isinstance(item["dossier_compatibility_binding"], dict)
                and bool(item["dossier_compatibility_binding"]),
                "Dossier compatibility binding missing")
        require(isinstance(item["semantic_input"], dict), "semantic input missing")
        require(not set(item["semantic_input"]) & {
            "price", "purchase", "wishlist", "discount", "ranking_neighbors",
            "lower_anchors", "upper_anchors",
        }, "commercial/wishlist/comparative input forbidden in Stage 1")
        dossier_path = item["dossier_path"]
        safe_repo_path(dossier_path)
        require(Path(dossier_path).parent == DOSSIERS,
                "Stage-1 dossier must use canonical accepted store")
        expected = str(INBOX / f"{wid}.json")
        require(item["result_submission_path"] == expected and expected not in paths,
                "Stage-1 create-only submission path mismatch")
        paths.add(expected)
    return work


def make_work_item(source: dict, row: dict, sequence: int) -> dict:
    pin = source["profile_pin"]
    binding = source["semantic_bindings"]
    required = (
        "semantic_generation_id", "work_id", "family_id",
        "taste_subject_key", "appid", "candidate_context_sha256",
        "dossier_path", "dossier_content_sha256",
        "dossier_compatibility_binding", "semantic_input",
    )
    for field in required:
        require(row.get(field) is not None, f"prepared upstream item missing {field}")
    require(row.get("work_mode") == "normal_first_pass",
            "only GitHub-prepared normal first-pass work is an eligible Stage-1 source")
    require(is_sha(row["semantic_generation_id"])
            and row["semantic_generation_id"] == source["semantic_generation_id"],
            "upstream generation mismatch")
    require(is_sha(row["work_id"]) and is_sha(row["candidate_context_sha256"]),
            "upstream work binding invalid")
    require(row.get("profile_semantic_sha256") == binding.get("profile_semantic_sha256"),
            "upstream profile semantics mismatch")
    require(row["dossier_compatibility_binding"] == source["dossier_compatibility_binding"],
            "upstream dossier compatibility mismatch")
    require(is_sha(row["dossier_content_sha256"]), "dossier SHA invalid")
    require(isinstance(pin, dict) and is_sha(pin.get("pin_sha256")),
            "GitHub-owned immutable profile pin missing")
    semantic = deepcopy(row["semantic_input"])
    require(isinstance(semantic, dict), "semantic input invalid")
    # A distinct Stage-1 work ID ensures dossiers and profile revisions cannot collide.
    work_id = canonical_sha256({
        "contract": WORK_CONTRACT,
        "semantic_generation_id": row["semantic_generation_id"],
        "upstream_work_id": row["work_id"],
        "candidate_context_sha256": row["candidate_context_sha256"],
        "profile_pin_sha256": pin["pin_sha256"],
        "profile_semantic_sha256": binding["profile_semantic_sha256"],
        "dossier_content_sha256": row["dossier_content_sha256"],
        "dossier_compatibility_binding": row["dossier_compatibility_binding"],
    })
    return {
        "sequence": sequence,
        "semantic_generation_id": row["semantic_generation_id"],
        "work_id": work_id, "source_work_id": row["work_id"],
        "family_id": row["family_id"],
        "taste_subject_key": row["taste_subject_key"],
        "appid": str(row["appid"]),
        "candidate_context_sha256": row["candidate_context_sha256"],
        "profile_pin": deepcopy(pin),
        "profile_semantic_sha256": binding["profile_semantic_sha256"],
        "dossier_path": row["dossier_path"],
        "dossier_content_sha256": row["dossier_content_sha256"],
        "dossier_compatibility_binding": deepcopy(row["dossier_compatibility_binding"]),
        "dossier_expires_at_utc": row.get("dossier_expires_at_utc"),
        "semantic_input": semantic,
        "result_submission_path": str(INBOX / f"{work_id}.json"),
    }


def verify_dossier(item: dict, root: Path = ROOT, *, validator=None) -> dict:
    path = safe_repo_path(item["dossier_path"], root)
    require(path.is_file(), "canonically accepted dossier unavailable")
    require(file_sha256(path) == item["dossier_content_sha256"],
            "accepted dossier content hash changed")
    dossier = load_json(path)
    require(dossier.get("appid") is not None
            and str(dossier["appid"]) == item["appid"], "dossier appid mismatch")
    require(dossier.get("web_evidence_contract_binding")
            == item["dossier_compatibility_binding"], "dossier contract binding mismatch")
    require(dossier.get("expires_at_utc") == item.get("dossier_expires_at_utc"),
            "dossier expiration binding mismatch")
    if validator is not None:
        eligible, reason = validator(
            binding=item, semantic_input=item["semantic_input"],
            dossier_record={"doc": dossier, "path": item["dossier_path"],
                            "content_sha256": item["dossier_content_sha256"]},
            current_binding=item["dossier_compatibility_binding"],
        )
        require(eligible, f"canonical Dossier gate: {reason}")
    return dossier


def build_work_manifest(source: dict, state: dict, *, root: Path = ROOT,
                        dossier_validator=None, generated_at_utc: str | None = None) -> dict:
    validate_state(state)
    require(source.get("contract") == "PROGRESSIVE-PASS2-WORK-V1",
            "only canonical GitHub-prepared source is allowed")
    require(isinstance(source.get("items"), list), "upstream GitHub items missing")
    require(isinstance(source.get("semantic_bindings"), dict)
            and isinstance(source.get("profile_pin"), dict),
            "upstream profile pin/binding missing")
    require(is_sha(source.get("semantic_generation_id"))
            and is_sha(source["profile_pin"].get("pin_sha256"))
            and is_sha(source["semantic_bindings"].get("profile_semantic_sha256")),
            "upstream global binding invalid")
    items, diagnostics, eligible = [], [], []
    if source.get("projection_status") != "current_github_owned_fast_dossier_deep_v1_projection":
        return {
            "schema_version": 1, "contract": WORK_CONTRACT,
            "implementation_status": "implemented_not_active",
            "source": SOURCE, "generated_at_utc": generated_at_utc or utc_now(),
            "total_eligible": 0, "eligible_work_ids": [], "items": [],
            "diagnostics": [{"code": "upstream_migration_or_non_normal_authority",
                             "detail": "Stage-1 cannot infer migration/recovery activation from legacy PASS-2 source."}],
        }
    for sequence, row in enumerate(source["items"], 1):
        try:
            item = make_work_item(source, row, sequence)
            verify_dossier(item, root, validator=dossier_validator)
            require(item["work_id"] not in eligible, "duplicate current Stage-1 item")
        except (Stage1Error, KeyError, TypeError, ValueError) as exc:
            diagnostics.append({"source_sequence": sequence,
                                "code": "prepared_item_ineligible",
                                "detail": str(exc)})
            continue
        eligible.append(item["work_id"])
        existing = state["entries"].get(item["work_id"])
        if existing:
            require(existing.get("dossier_content_sha256") == item["dossier_content_sha256"]
                    and existing.get("profile_pin") == item["profile_pin"],
                    "accepted Stage-1 state binding collision")
            continue
        items.append(item)
    work = {
        "schema_version": 1, "contract": WORK_CONTRACT,
        "implementation_status": "implemented_not_active",
        "source": SOURCE, "generated_at_utc": generated_at_utc or utc_now(),
        "total_eligible": len(eligible), "eligible_work_ids": eligible,
        "items": items, "diagnostics": diagnostics,
    }
    return validate_work_manifest(work)


def _finding_rows(doc: dict, field: str, dossier: dict, used_ids: set[str]) -> None:
    rows = doc[field]
    require(isinstance(rows, list), f"{field} must be array")
    for row in rows:
        require(isinstance(row, dict) and set(row) == {
            "finding_id", "text_ru", "candidate_evidence_refs", "profile_evidence_refs"
        }, f"{field} finding shape invalid")
        fid = row["finding_id"]
        require(isinstance(fid, str) and fid and fid not in used_ids,
                "missing or duplicate finding ID")
        used_ids.add(fid)
        require(isinstance(row["text_ru"], str) and row["text_ru"].strip(),
                "finding text missing")
        candidate = row["candidate_evidence_refs"]
        require(isinstance(candidate, list) and candidate, "candidate evidence refs required")
        require(len({json.dumps(ref, sort_keys=True) for ref in candidate}) == len(candidate),
                "duplicate candidate evidence ref")
        for ref in candidate:
            require(isinstance(ref, dict) and set(ref) == {"kind", "index"},
                    "candidate evidence ref shape invalid")
            kind, index = ref["kind"], ref["index"]
            require(kind in ("observation", "conflict")
                    and type(index) is int and index >= 0,
                    "candidate evidence ref kind/index invalid")
            collection = dossier.get("observations" if kind == "observation" else "conflicts")
            require(isinstance(collection, list) and index < len(collection),
                    "candidate evidence ref outside exact dossier")
        profile = row["profile_evidence_refs"]
        require(isinstance(profile, list), "profile evidence refs must be array")
        if field != "nuances":
            require(bool(profile), "personalized positive/negative requires pinned profile reference")
        require(len({json.dumps(ref, sort_keys=True) for ref in profile}) == len(profile),
                "duplicate profile evidence reference")
        for ref in profile:
            require(isinstance(ref, dict) and set(ref) == {"path"}
                    and isinstance(ref["path"], str) and ref["path"].startswith("$")
                    and len(ref["path"]) > 1,
                    "pinned profile evidence ref path invalid")


def validate_result(result: dict, item: dict, *, root: Path = ROOT,
                    dossier: dict | None = None) -> dict:
    require(isinstance(result, dict) and set(result) == RESULT_REQUIRED,
            "Stage-1 result must exactly match frozen field set")
    require(result["schema_version"] == 1 and result["contract"] == RESULT_CONTRACT,
            "Stage-1 result contract mismatch")
    for field in (
        "semantic_generation_id", "work_id", "family_id", "taste_subject_key",
        "appid", "candidate_context_sha256", "profile_semantic_sha256",
        "dossier_content_sha256",
    ):
        require(result[field] == item[field], f"Stage-1 result {field} binding mismatch")
    require(result["profile_pin_sha256"] == item["profile_pin"]["pin_sha256"],
            "Stage-1 immutable pinned-profile binding mismatch")
    require(result["outcome"] in (
        "analyzed_fit", "analyzed_not_fit", "analysis_incomplete"
    ), "Stage-1 outcome invalid")
    require(result["confidence"] in ("medium", "high"), "confidence invalid")
    require(isinstance(result["summary_ru"], str)
            and result["summary_ru"].strip(), "conclusion required")
    if dossier is None:
        dossier = verify_dossier(item, root)
    used_ids: set[str] = set()
    for field in ("positives", "negatives", "nuances"):
        _finding_rows(result, field, dossier, used_ids)
    require(isinstance(result["point_breakdown"], list),
            "point breakdown must be array")
    outcome = result["outcome"]
    if outcome == "analyzed_fit":
        score = _decimal_tenth(result["provisional_deep_fit_score_0_56"],
                               "provisional score", Decimal(0), Decimal(56))
        require(bool(result["point_breakdown"]) and result["analysis_issue_code"] is None,
                "fit requires dynamic point breakdown and no issue code")
        total, breakdown_ids = Decimal(0), set()
        for part in result["point_breakdown"]:
            require(isinstance(part, dict) and set(part) == {
                "breakdown_id", "label_ru", "direction", "points", "finding_refs"
            }, "breakdown shape invalid")
            pid = part["breakdown_id"]
            require(isinstance(pid, str) and pid and pid not in breakdown_ids,
                    "duplicate or missing breakdown ID")
            breakdown_ids.add(pid)
            require(isinstance(part["label_ru"], str) and part["label_ru"].strip(),
                    "game-specific breakdown label required")
            value = _decimal_tenth(part["points"], "breakdown points",
                                   Decimal(-56), Decimal(56))
            direction = part["direction"]
            require((direction == "positive" and value > 0)
                    or (direction == "negative" and value < 0)
                    or (direction == "neutral" and value == 0),
                    "breakdown point sign differs from direction")
            refs = part["finding_refs"]
            require(isinstance(refs, list) and refs
                    and len(set(refs)) == len(refs)
                    and all(isinstance(ref, str) and ref in used_ids for ref in refs),
                    "breakdown must reference real distinct findings")
            total += value
        require(total == score,
                f"dynamic point breakdown {total} does not equal provisional score {score}")
    else:
        require(result["provisional_deep_fit_score_0_56"] is None
                and result["point_breakdown"] == [],
                "not-fit/incomplete must never enter positive 0-56 ladder")
        if outcome == "analysis_incomplete":
            require(result["analysis_issue_code"] in ISSUE_CODES,
                    "incomplete requires frozen diagnostic issue code")
        else:
            require(result["analysis_issue_code"] is None,
                    "not-fit is an authoritative outcome, not an incomplete diagnostic")
    return result


def record_diagnostic(state: dict, row: dict) -> None:
    require(isinstance(row, dict) and bool(row.get("code")), "diagnostic code required")
    if row not in state["diagnostic_history"]:
        state["diagnostic_history"].append(row)


def accept_result(state: dict, item: dict, result: dict, *,
                  path: str, sha: str, accepted_at_utc: str | None = None) -> dict:
    validate_state(state)
    require(is_sha(sha) and Path(path).parent == RESULTS,
            "canonical Stage-1 accepted result reference invalid")
    existing = state["entries"].get(item["work_id"])
    if existing is not None:
        require(existing["accepted_result_sha256"] == sha
                and existing["accepted_result_path"] == path,
                "create-only accepted Stage-1 state collision")
        return state
    when = accepted_at_utc or utc_now()
    state["entries"][item["work_id"]] = {
        "status": "accepted", "accepted": True, "sequence": item["sequence"],
        "semantic_generation_id": item["semantic_generation_id"],
        "work_id": item["work_id"], "family_id": item["family_id"],
        "appid": item["appid"], "profile_pin": deepcopy(item["profile_pin"]),
        "profile_semantic_sha256": item["profile_semantic_sha256"],
        "dossier_content_sha256": item["dossier_content_sha256"],
        "outcome": result["outcome"],
        "accepted_result_path": path, "accepted_result_sha256": sha,
        "accepted_at_utc": when,
    }
    state["progress"]["last_attempt_at_utc"] = when
    if result["outcome"] != "analysis_incomplete":
        state["progress"]["last_successful_result_at_utc"] = when
    return validate_state(state)


def recompute_progress(state: dict, work: dict) -> dict:
    validate_state(state)
    validate_work_manifest(work)
    eligible = work["eligible_work_ids"]
    rows = [state["entries"][wid] for wid in eligible if wid in state["entries"]]
    counts = {
        "analyzed_fit": sum(r["outcome"] == "analyzed_fit" for r in rows),
        "analyzed_not_fit": sum(r["outcome"] == "analyzed_not_fit" for r in rows),
        "analysis_incomplete": sum(r["outcome"] == "analysis_incomplete" for r in rows),
    }
    state["progress"].update({
        "total_eligible": len(eligible),
        "completed_fit": counts["analyzed_fit"],
        "completed_not_fit": counts["analyzed_not_fit"],
        "diagnostic_incomplete": counts["analysis_incomplete"],
        "pending": len(eligible) - len(rows),
    })
    return validate_state(state)

"""Non-active Stage-2-only score/ranking candidate for the atomic Deep cutover.

No production caller is wired here before the integration task. The input
bindings must be selected from the current GitHub-owned Stage-1 scope; legacy
Fast/Deep scores and card text are never used or forwarded.
"""
from decimal import Decimal, InvalidOperation
from typing import Any

import priority_ranking

STAGE1_STATE_CONTRACT = "DEEP-STAGE1-STATE-V1"
STAGE2_STATE_CONTRACT = "DEEP-STAGE2-STATE-V1"
CANDIDATE_CONTRACT = "DEEP-TWO-STAGE-RANKING-PREPARED-V1"
SHA_LEN = 64
STAGES = {"calibrated": 0, "awaiting_calibration": 1,
          "diagnostic_incomplete": 2, "not_analyzed": 3}


class NewRankingError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise NewRankingError(message)


def _sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == SHA_LEN and all(
        char in "0123456789abcdef" for char in value
    )


def _decimal(value: Any, field: str, low: int, high: int, places: str) -> Decimal:
    require(type(value) in (int, float, Decimal), f"{field} must be numeric")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise NewRankingError(f"{field}: invalid decimal") from exc
    require(number.is_finite() and low <= number <= high
            and number == number.quantize(Decimal(places)),
            f"{field} must be {low}..{high} at {places} precision")
    return number


def _state(doc: dict, contract: str) -> dict:
    require(isinstance(doc, dict) and doc.get("schema_version") == 1
            and doc.get("contract") == contract
            and isinstance(doc.get("entries"), dict),
            f"{contract}: expected canonical accepted state")
    return doc["entries"]


def _stage1_entry(entries: dict, binding: dict, family: str) -> dict | None:
    work_id = binding.get("work_id")
    require(_sha(work_id) and _sha(binding.get("profile_semantic_sha256"))
            and _sha(binding.get("dossier_content_sha256"))
            and str(binding.get("appid") or "").isdigit(),
            f"{family}: current exact Stage-1 binding missing")
    entry = entries.get(work_id)
    if entry is None:
        return None
    require(entry.get("accepted") is True and entry.get("status") == "accepted"
            and entry.get("work_id") == work_id
            and entry.get("family_id") == family
            and str(entry.get("appid")) == str(binding["appid"])
            and entry.get("profile_semantic_sha256") == binding["profile_semantic_sha256"]
            and entry.get("dossier_content_sha256") == binding["dossier_content_sha256"]
            and _sha(entry.get("accepted_result_sha256"))
            and isinstance(entry.get("accepted_result_path"), str)
            and entry["accepted_result_path"].startswith("data/cache/deep_stage1_results/"),
            f"{family}: accepted Stage-1 state conflicts with current identity")
    require(entry.get("outcome") in
            ("analyzed_fit", "analyzed_not_fit", "analysis_incomplete"),
            f"{family}: unknown Stage-1 outcome")
    return entry


def _calibration(entries: dict, stage1: dict, binding: dict, family: str) -> dict | None:
    matches = []
    for entry in entries.values():
        if not isinstance(entry, dict) or entry.get("status") != "calibrated":
            continue
        if (entry.get("family_id") != family
                or entry.get("stage1_work_id") != stage1["work_id"]
                or entry.get("stage1_result_sha256") != stage1["accepted_result_sha256"]
                or entry.get("stage1_result_path") != stage1["accepted_result_path"]
                or entry.get("profile_semantic_sha256") != binding["profile_semantic_sha256"]
                or str(entry.get("appid")) != str(binding["appid"])):
            continue  # historical mismatched calibration is audit-only
        require(entry.get("outcome") == "calibrated_fit"
                and _sha(entry.get("canonical_stage2_result_sha256"))
                and isinstance(entry.get("canonical_stage2_result_path"), str)
                and entry["canonical_stage2_result_path"].startswith("data/cache/deep_stage2_results/"),
                f"{family}: Stage-2 accepted-result provenance invalid")
        matches.append(entry)
    require(len(matches) <= 1, f"{family}: multiple current calibrated identities")
    return matches[0] if matches else None


def _purchase(game: dict, policy: dict) -> dict:
    # The existing deterministic standalone/fixed-package economics stays 0..40.
    # This is the ONLY reuse of the old ranking implementation.
    purchase = priority_ranking.build_purchase_breakdown(game, policy)
    points = _decimal(purchase.get("purchase_score"), "purchase", 0, 40, "0.1")
    require(_decimal(purchase.get("purchase_max"), "purchase_max", 40, 40, "0.1") == 40,
            "purchase contract changed")
    return {**purchase, "purchase_score": float(points)}


def project_candidate_ranking(games: list[dict], *, current_bindings: dict,
                              stage1_state: dict, stage2_state: dict,
                              policy: dict | None = None) -> list[dict]:
    """Produce *isolated* candidate rows, not a patch to published legacy cards.

    Integration must supply exact current bindings and apply this projection
    atomically with the Stage-1/2 site model. Missing/stale Stage-2 results
    receive purchase-only operational ordering, NEVER a personal/total score.
    """
    require(isinstance(games, list) and isinstance(current_bindings, dict),
            "explicit current games/bindings required")
    s1 = _state(stage1_state, STAGE1_STATE_CONTRACT)
    s2 = _state(stage2_state, STAGE2_STATE_CONTRACT)
    if policy is None:
        policy = priority_ranking.load_final_policy()
    require(policy.get("contract") == "FINAL-PRIORITY-RANKING-V2",
            "purchase model must remain current deterministic V2")
    model = policy.get("score_model") or {}
    require(model.get("purchase", {}).get("max") == 40
            and model.get("personal", {}).get("wishlist", {}).get("present_points") == 4
            and model.get("personal", {}).get("wishlist", {}).get("absent_points") == 0,
            "frozen 56+4+40 composition disagrees with purchase/wishlist policy")

    output = []
    seen_families = set()
    used_calibrated_cents = set()
    for game in games:
        require(isinstance(game, dict), "candidate must be object")
        family = str(game.get("id") or "")
        require(family and family not in seen_families,
                f"duplicate or empty candidate family: {family}")
        seen_families.add(family)
        binding = current_bindings.get(family)
        require(isinstance(binding, dict),
                f"{family}: no GitHub-prepared current Stage-1 binding")
        entry = _stage1_entry(s1, binding, family)
        purchase = _purchase(game, policy)
        wishlist = game.get("wishlist")
        require(type(wishlist) is bool, f"{family}: exact deterministic Wishlist bool required")
        bonus = 4 if wishlist else 0
        stage1_status = "pending"
        stage2_status = "not_eligible"
        rank_stage = "not_analyzed"
        calibrated = personal = total = None
        calibrated_source = None
        score_breakdown = None

        if entry:
            if entry["outcome"] == "analyzed_not_fit":
                stage1_status = "completed_not_fit"
            elif entry["outcome"] == "analysis_incomplete":
                stage1_status, rank_stage = "diagnostic_incomplete", "diagnostic_incomplete"
            else:
                stage1_status = "completed_fit"
                stage2_status = "awaiting_calibration"
                rank_stage = "awaiting_calibration"
                calibration = _calibration(s2, entry, binding, family)
                if calibration:
                    score = _decimal(calibration.get("calibrated_deep_fit_score_0_56"),
                                     "calibrated Stage-2 fit", 0, 56, "0.01")
                    cents = int(score * 100)
                    require(cents not in used_calibrated_cents,
                            "current calibrated Stage-2 scores cannot tie")
                    used_calibrated_cents.add(cents)
                    calibrated = float(score)
                    personal = float(score + bonus)
                    total = float(score + bonus + Decimal(str(purchase["purchase_score"])))
                    calibrated_source = calibration["canonical_stage2_result_path"]
                    stage2_status, rank_stage = "calibrated", "calibrated"
                    score_breakdown = {
                        "contract": CANDIDATE_CONTRACT,
                        "precision": {"code": "calibrated_deep_stage2", "is_coarse_legacy": False},
                        "personal_components": [
                            {"id": "calibrated_deep_fit", "points": calibrated, "max_points": 56,
                             "source": calibrated_source},
                            {"id": "wishlist", "points": bonus, "max_points": 4},
                        ],
                        "personal_score": personal, "personal_max": 60,
                        "purchase_score": purchase["purchase_score"], "purchase_max": 40,
                        "purchase_components": purchase["purchase_components"],
                        "purchase_route": purchase["purchase_route"],
                        "total_score": total, "total_max": 100,
                    }
        row = {
            "id": family, "title": str(game.get("title") or ""),
            "ranking_stage": rank_stage if stage1_status != "completed_not_fit" else None,
            "ranking_stage_rank": STAGES.get(rank_stage) if stage1_status != "completed_not_fit" else None,
            "stage1_status": stage1_status, "stage2_status": stage2_status,
            "stage2_calibrated_deep_fit_score_0_56": calibrated,
            "wishlist_bonus_0_or_4": bonus,
            "personal_quality_score_0_60": personal,
            "purchase_score_0_40": purchase["purchase_score"],
            "total_score_0_100": total,
            "score_breakdown": score_breakdown,
            "purchase_route": purchase["purchase_route"],
            "deterministic_purchase_score": purchase["purchase_score"],
            "priority_rank": None,
            "stage2_accepted_result_path": calibrated_source,
        }
        # No legacy why_fit, positive evidence, Fast score or personal subweights
        # can leak into this isolated candidate; site projection is separately owned.
        output.append(row)

    visible = [row for row in output if row["ranking_stage"] is not None]
    visible.sort(key=lambda row: (
        row["ranking_stage_rank"],
        -(row["total_score_0_100"] if row["total_score_0_100"] is not None
          else row["deterministic_purchase_score"]),
        row["title"].casefold(), row["id"].casefold(),
    ))
    for rank, row in enumerate(visible, 1):
        row["priority_rank"] = rank
    return output

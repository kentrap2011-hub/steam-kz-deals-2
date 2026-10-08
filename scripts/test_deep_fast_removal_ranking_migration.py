#!/usr/bin/env python3
"""Bounded regression for proposed post-cutover ranking; no runtime activation."""
from copy import deepcopy
from pathlib import Path

import deep_two_stage_ranking as new
import priority_ranking

ROOT = Path(__file__).resolve().parents[1]
H = lambda char: char * 64


def binding(char, appid):
    return {
        "work_id": H(char), "appid": str(appid),
        "profile_semantic_sha256": H("a"),
        "dossier_content_sha256": H("d"),
    }


def stage1(char, appid, family, outcome="analyzed_fit"):
    return {
        "accepted": True, "status": "accepted", "work_id": H(char),
        "family_id": family, "appid": str(appid),
        "profile_semantic_sha256": H("a"), "dossier_content_sha256": H("d"),
        "outcome": outcome, "accepted_result_sha256": H(char),
        "accepted_result_path": f"data/cache/deep_stage1_results/{H(char)}.json",
    }


def stage2(char, appid, family, score):
    return {
        "status": "calibrated", "outcome": "calibrated_fit",
        "family_id": family, "appid": str(appid),
        "stage1_work_id": H(char), "stage1_result_sha256": H(char),
        "stage1_result_path": f"data/cache/deep_stage1_results/{H(char)}.json",
        "profile_semantic_sha256": H("a"),
        "calibrated_deep_fit_score_0_56": score,
        "canonical_stage2_result_sha256": H("f"),
        "canonical_stage2_result_path": f"data/cache/deep_stage2_results/{H(char)}.json",
    }


def state(which, rows):
    return {
        "schema_version": 1, "contract": f"DEEP-STAGE{which}-STATE-V1",
        "implementation_status": "implemented_not_active",
        "entries": rows,
    }


def game(family, *, wishlist=False, **extra):
    return {
        "id": family, "title": family, "wishlist": wishlist,
        "original_price_rub": 1000, "current_price_rub": 300,
        "history_quality": "record", **extra,
    }


def attempt(games, bindings, s1, s2):
    return new.project_candidate_ranking(
        games, current_bindings=bindings, stage1_state=state(1, s1),
        stage2_state=state(2, s2),
    )


def fails(fn, message):
    try:
        fn()
    except new.NewRankingError:
        return
    raise AssertionError(message)


def test_scores():
    a = game("a", wishlist=True, fit="strong", taste_factors={"bad": 100},
             risk_level="high", duration_preference_band="extreme_length",
             practical={"steam_achievements": False},
             direct_user_evidence={"rating": 5}, total_score=999, personal_score=777,
             fast_stage_state="completed", effective_analysis_source="fast",
             why_fit=["LEGACY FAST REASON"], priority_rank=1)
    b = game("b", wishlist=False, direct_user_evidence={"rating": 1})
    bindings = {"a": binding("b", 1), "b": binding("c", 2)}
    s1 = {H("b"): stage1("b", 1, "a"), H("c"): stage1("c", 2, "b")}
    s2 = {H("e"): stage2("b", 1, "a", 42.37),
          H("f"): stage2("c", 2, "b", 41.89)}
    rows = attempt([a, b], bindings, s1, s2)
    a_row, b_row = rows
    purchase = priority_ranking.build_purchase_breakdown(a)["purchase_score"]
    assert a_row["purchase_score_0_40"] == purchase and 0 <= purchase <= 40
    assert a_row["personal_quality_score_0_60"] == 46.37
    assert a_row["total_score_0_100"] == round(46.37 + purchase, 2)
    assert b_row["personal_quality_score_0_60"] == 41.89
    assert b_row["total_score_0_100"] == round(41.89 + purchase, 2)
    assert a_row["priority_rank"] == 1 and b_row["priority_rank"] == 2
    assert a_row["score_breakdown"]["precision"]["code"] == "calibrated_deep_stage2"
    assert [part["id"] for part in a_row["score_breakdown"]["personal_components"]] == [
        "calibrated_deep_fit", "wishlist"
    ]
    for forbidden in ("why_fit", "taste_factors", "direct_user_evidence", "fast_stage_state",
                      "total_score", "personal_score", "pass1_attempted", "risk_penalty"):
        assert forbidden not in a_row, forbidden
    assert not any(x["id"] in ("achievements", "duration", "risk", "taste")
                   for x in a_row["score_breakdown"]["personal_components"])
    # Legacy Fast, direct ratings, duration, achievement and risk mutations cannot
    # change the proposed semantic score, even when legacy total_score is huge.
    mutated = deepcopy(a)
    mutated.update(total_score=-100, fit="moderate", direct_user_evidence={"rating": 1},
                   practical={"steam_achievements": True}, risk_level="low",
                   duration_preference_band="preferred_medium")
    other = attempt([mutated, b], bindings, s1, s2)[0]
    assert other["total_score_0_100"] == a_row["total_score_0_100"]


def test_fail_closed():
    g = game("a", wishlist=True, total_score=100, fit="strong",
             effective_analysis_source="fast", why_fit=["should never appear"])
    bindings = {"a": binding("b", 1)}
    s1 = {H("b"): stage1("b", 1, "a")}
    accepted = stage2("b", 1, "a", 42.37)
    pending = attempt([g], bindings, s1, {})
    assert pending[0]["stage2_status"] == "awaiting_calibration"
    assert pending[0]["total_score_0_100"] is None
    assert pending[0]["personal_quality_score_0_60"] is None
    assert pending[0]["score_breakdown"] is None
    assert pending[0]["priority_rank"] == 1
    assert pending[0]["deterministic_purchase_score"] > 0

    stale = dict(accepted, stage1_result_sha256=H("a"))
    assert attempt([g], bindings, s1, {H("e"): stale})[0]["total_score_0_100"] is None
    bad_bindings = deepcopy(bindings)
    bad_bindings["a"]["dossier_content_sha256"] = H("e")
    fails(lambda: attempt([g], bad_bindings, s1, {H("e"): accepted}),
          "changed Dossier identity must not retain Stage-1 score")
    fails(lambda: attempt([g, g], bindings, s1, {}),
          "duplicate family should be rejected")
    fails(lambda: attempt([dict(g, wishlist=1)], bindings, s1, {}),
          "Wishlist must be boolean, not truthy")
    fails(lambda: attempt([g], {}, s1, {}),
          "unbound Fast card must not be treated as new Deep")

    notfit = {H("b"): stage1("b", 1, "a", "analyzed_not_fit")}
    excluded = attempt([g], bindings, notfit, {H("e"): accepted})[0]
    assert excluded["stage1_status"] == "completed_not_fit"
    assert excluded["priority_rank"] is None and excluded["total_score_0_100"] is None
    assert excluded["ranking_stage"] is None
    diagnostic = attempt(
        [g], bindings,
        {H("b"): stage1("b", 1, "a", "analysis_incomplete")}, {}
    )[0]
    assert diagnostic["ranking_stage"] == "diagnostic_incomplete"
    assert diagnostic["total_score_0_100"] is None

    fails(lambda: attempt([g], bindings, s1, {H("e"): stage2("b", 1, "a", 56.001)}),
          "no scores finer than the frozen hundredth")
    fails(lambda: attempt([g], bindings, s1, {H("e"): stage2("b", 1, "a", 57)}),
          "Stage-2 score capped at 56")
    fails(lambda: attempt([g], bindings, s1, {
        H("e"): accepted, H("f"): dict(accepted),
    }), "multiple compatible Stage-2 artifacts are ambiguous")


def test_order_is_explicit():
    games = [game("z"), game("a"), game("b")]
    bindings = {"z": binding("b", 1), "a": binding("c", 2), "b": binding("e", 3)}
    s1 = {H("b"): stage1("b", 1, "z"),
          H("c"): stage1("c", 2, "a", "analysis_incomplete")}
    s2 = {H("f"): stage2("b", 1, "z", 0)}
    rows = attempt(games, bindings, s1, s2)
    assert {row["id"]: row["priority_rank"] for row in rows} == {
        "z": 1, "a": 2, "b": 3
    }
    # The audit-only Fast score is never considered for a not-analyzed row.
    poisoned = attempt(
        [dict(game("z"), fast_score=100), dict(game("a"), total_score=1000),
         dict(game("b"), total_score=9999)],
        bindings, s1, s2
    )
    assert [row["priority_rank"] for row in rows] == [
        row["priority_rank"] for row in poisoned
    ]


def test_frozen_boundary():
    assert "deep_two_stage_ranking" not in (
        ROOT / "scripts/progressive_personalization.py"
    ).read_text(encoding="utf-8")
    assert "deep_two_stage_ranking" not in (
        ROOT / "scripts/build_final_visual_payload.py"
    ).read_text(encoding="utf-8")
    assert "deep_two_stage_ranking" not in (
        ROOT / "config/final_ranking_policy.json"
    ).read_text(encoding="utf-8")
    assert priority_ranking.load_final_policy()["contract"] == "FINAL-PRIORITY-RANKING-V2"


if __name__ == "__main__":
    test_scores()
    test_fail_closed()
    test_order_is_explicit()
    test_frozen_boundary()
    print("DEEP_FAST_REMOVAL_RANKING_PREPARED=PASS no Fast score/semantic fallback or cutover")

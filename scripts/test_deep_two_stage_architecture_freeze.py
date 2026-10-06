#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main():
    architecture = load("config/deep_two_stage_architecture_contract.json")
    stage1 = load("config/deep_stage1_contract.json")
    stage1_schema = load("config/deep_stage1_result_schema.json")
    stage2 = load("config/deep_stage2_contract.json")
    stage2_schema = load("config/deep_stage2_result_schema.json")
    site = load("config/deep_two_stage_site_projection_contract.json")
    migration = load("config/deep_two_stage_migration_contract.json")
    deps = load("config/deep_two_stage_dependency_map.json")
    ranking = load("config/final_ranking_policy.json")
    current_progressive = load("config/progressive_personalization_contract.json")
    current_deep = load("config/progressive_pass2_contract.json")

    assert architecture["contract"] == "DEEP-TWO-STAGE-ARCHITECTURE-V1"
    assert architecture["status"] == "frozen_not_active"
    assert architecture["production_cutover_authorized"] is False
    assert architecture["pipeline"] == [
        "taste_steam_review_dossier",
        "deep_stage1_analysis",
        "deep_stage2_comparative_calibration",
        "ranking_and_publication",
    ]

    score = architecture["score_model"]
    assert score["stage1_provisional_deep_fit"]["maximum"] == 56
    assert score["stage1_provisional_deep_fit"]["ranking_authority"] is False
    assert score["stage2_calibrated_deep_fit"]["maximum"] == 56
    assert score["stage2_calibrated_deep_fit"]["integer_only_forbidden"] is True
    assert score["stage2_calibrated_deep_fit"]["canonical_display_precision_decimal_places"] == 2
    assert score["stage2_calibrated_deep_fit"]["active_ranked_fit_scores_must_be_unique"] is True
    assert score["wishlist"]["values"] == [0, 4]
    assert score["personal_quality"]["maximum"] == 60
    assert score["purchase"]["maximum"] == 40
    assert score["combined_offer"]["maximum"] == 100
    assert set(score["retired_after_cutover_as_independent_personal_arithmetic"]) == {
        "achievements", "duration", "risk"
    }

    assert stage1["status"] == "frozen_not_active"
    assert stage2["status"] == "frozen_not_active"
    assert stage1["semantic_worker_identity"] != stage2["semantic_worker_identity"]
    assert stage1["manual_prompt_path"] != stage2["manual_prompt_path"]
    assert stage1["work_manifest"]["path"] != stage2["work_manifest"]["path"]
    assert stage1["result"]["accepted_state_path"] != stage2["result"]["accepted_state_path"]
    assert stage1["inputs"]["ranking_neighbors_forbidden"] is True
    assert stage1["scoring"]["fixed_factor_weights_forbidden"] is True
    assert stage1["scoring"]["wishlist_excluded"] is True
    assert stage2["evidence_boundary"]["web_research_forbidden"] is True
    assert stage2["work_manifest"]["window_selection_owner"] == "github_control_plane"
    assert stage2["scoring"]["github_assigns_final_unique_numeric_coordinate"] is True
    assert stage2["scoring"]["canonical_precision_decimal_places"] == 2

    assert stage1_schema["properties"]["contract"]["const"] == "DEEP-STAGE1-RESULT-V1"
    assert stage2_schema["properties"]["contract"]["const"] == "DEEP-STAGE2-RESULT-V1"
    assert stage1_schema["properties"]["provisional_deep_fit_score_0_56"]["oneOf"][1]["maximum"] == 56
    assert stage2_schema["properties"]["semantic_calibrated_deep_fit_target_0_56"]["oneOf"][1]["maximum"] == 56

    assert site["status"] == "frozen_not_active"
    assert site["detail_view"]["ordered_sections"] == [
        "short_summary",
        "positives",
        "negatives",
        "other_nuances",
        "stage2_score_change",
        "why_above_below_neighbors",
    ]
    assert site["compact_card"]["fast_label_or_score_forbidden"] is True
    assert site["compact_card"]["stage1_provisional_score_as_final_forbidden"] is True
    stat_ids = [row["id"] for row in site["statistics"]["top_level_blocks"]]
    assert stat_ids == ["dossier", "deep_stage1", "deep_stage2"]

    assert migration["status"] == "frozen_not_active"
    assert migration["no_mixed_authority"]["partial_cutover_forbidden"] is True
    assert migration["semantic_execution_authorized_by_this_contract"] is False
    assert migration["mass_migration_authorized"] is False
    assert migration["old_personal_components"]["wishlist"]["disposition"] == "preserve_as_deterministic_plus_4"
    for key in ("achievements", "duration", "risk"):
        assert "retire_as_independent_arithmetic" in migration["old_personal_components"][key]["disposition"]

    parallel = {row["task"] for row in deps["parallelizable_after_freeze"]}
    assert parallel == {
        "WORKER_TASK_DEEP_STAGE1_WORKER_IMPLEMENT_01.md",
        "WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md",
        "WORKER_TASK_DEEP_FAST_REMOVAL_RANKING_MIGRATION_01.md",
        "WORKER_TASK_DEEP_SITE_MIRROR_UI_STATISTICS_IMPLEMENT_01.md",
    }
    assert deps["integration_gate"]["task"] == "WORKER_TASK_DEEP_TWO_STAGE_INTEGRATION_CUTOVER_01.md"

    # Freeze must not itself cut over production.
    assert current_progressive["stage_model"]["revision"] == "FAST-DOSSIER-DEEP-V1"
    assert current_deep["active"] is True
    assert ranking["contract"] == "FINAL-PRIORITY-RANKING-V2"
    assert ranking["score_model"]["personal"]["max"] == 60
    assert ranking["score_model"]["purchase"]["max"] == 40
    assert ranking["score_model"]["total_max"] == 100

    print("DEEP_TWO_STAGE_ARCHITECTURE_FREEZE=PASS")


if __name__ == "__main__":
    main()

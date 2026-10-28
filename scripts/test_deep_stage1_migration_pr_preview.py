#!/usr/bin/env python3
"""PR-only, read-only Stage-1 preview against a freshly computed PASS2 view.

The committed PASS2 work may legitimately predate a proposed producer fix.
Do not rewrite it, disable the Stage-1 gate, or activate either stage.
"""
import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import build_progressive_pass2_work as producer
import deep_stage1 as stage1
import prepare_deep_stage1_migration_work as preparation
import progressive_pass1 as pass1
import progressive_pass2 as pass2


CURRENT_MODE = "current_github_owned_fast_dossier_deep_v1_projection"
STALE_MODE = "score_explainability_migration_active"


def bytes_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assert_rejected(snapshot, kwargs, reason):
    try:
        preparation.make_plan(legacy=snapshot, **kwargs)
    except preparation.PreparationError as exc:
        assert str(exc) == reason, (
            "Stage-1 rejected for the wrong reason (or a broken source): " + str(exc)
        )
    else:
        raise AssertionError("Stage-1 accepted incompatible one-stage Deep work")


def validate_pr_preview(preview_path):
    # All four canonical artifacts must remain byte-for-byte untouched.
    watched = (
        preparation.OLD_WORK, preparation.OLD_STATE,
        preparation.NEW_STATE, preparation.CANONICAL_WORK,
    )
    before = {str(path): bytes_sha256(path) for path in watched}
    now = datetime.now(timezone.utc)
    fresh = producer.build_work_document(now=now)  # PURE: never producer.main()
    scope = fresh["scope"]
    score = scope["score_explainability_migration"]
    assert fresh["pass2_active"] is True
    assert fresh["projection_status"] == CURRENT_MODE
    assert scope["deep_normal_work_paused_for_score_explainability_migration"] is False
    assert scope["deep_normal_work_paused_for_legacy_reanalysis"] is False
    assert score["pending_count"] == 0 and score["submitted_count"] == 0
    assert score["complete"] is False and score["exhausted"] is True
    assert score["total_count"] == 43
    assert score["accepted_count"] == 42
    assert score["stale_or_missing_prior_count"] == 1
    assert len(fresh["items"]) == scope["pass2_eligible_count"]
    # A valid GitHub-owned Deep snapshot may have zero runnable items while
    # current identities wait for Dossier or have already consumed first pass.
    # Check the full, recovery-aware accounting instead of requiring work > 0.
    assert len(fresh["items"]) == scope["normal_pass2_eligible_count"]
    assert scope["deep_ready_or_pending_count"] == len(fresh["items"])
    assert 0 <= scope["recovery_pending_count"] <= len(fresh["items"])
    assert scope["deep_normal_first_pass_remaining_count"] == (
        scope["deep_waiting_for_dossier_count"]
        + len(fresh["items"]) - scope["recovery_pending_count"]
    )
    assert scope["deep_total_current_coverage_target"] == (
        scope["deep_first_pass_attempted_count"]
        + scope["deep_normal_first_pass_remaining_count"]
    )
    assert all(row["work_mode"] == "normal_first_pass" for row in fresh["items"])
    assert [row["sequence"] for row in fresh["items"]] == list(range(1, len(fresh["items"]) + 1))
    assert len({(row["family_id"], row["authorization_id"]) for row in fresh["items"]}) == len(fresh["items"])

    contexts = pass1.load_jsonl(pass1.PROGRESSIVE_CONTEXT)
    projection = stage1.load_json(pass1.TASTE_PROJECTION)
    queue = pass1.load_jsonl(pass1.TASTE_QUEUE)
    generation, bindings, by_family = pass1.current_bindings(contexts, projection, queue)
    dossier_binding = pass2.current_dossier_binding()
    kwargs = {
        "previous": stage1.load_json(preparation.OLD_STATE),
        "stage1_state": stage1.load_json(preparation.NEW_STATE),
        "migration": stage1.load_json(preparation.CONTRACT),
        "ownership": stage1.load_json(preparation.OWNERSHIP),
        "generation": generation,
        "bindings": bindings,
        "by_family": by_family,
        "contexts": contexts,
        "ordering": pass2.load_contract(),
        "dossier_binding": dossier_binding,
        "dossier_loader": pass2.canonical_dossier_loader,
        "now": now,
    }
    # First prove that the same unmodified Stage-1 gate rejects the genuinely
    # stale committed production snapshot, not a synthetic happy-path substitute.
    committed = stage1.load_json(preparation.OLD_WORK)
    if committed["projection_status"] != CURRENT_MODE:
        assert committed["projection_status"] == STALE_MODE
        assert committed["items"] == []
        assert committed["scope"]["score_explainability_migration"]["pending_count"] == 0
        assert_rejected(
            committed, kwargs, "current canonical one-stage Deep work not available"
        )
        committed_status = "confirmed_rejected_stale_committed_snapshot"
    else:
        # If a future canonical producer has already refreshed the committed
        # snapshot, CI still checks fail-closed rejection on a stale input.
        committed_status = "already_current_canonical_projection"
    stale = copy.deepcopy(fresh)
    stale["projection_status"] = STALE_MODE
    stale["items"] = []
    assert_rejected(stale, kwargs, "current canonical one-stage Deep work not available")
    wrong_binding = copy.deepcopy(fresh)
    wrong_binding["semantic_generation_id"] = "incompatible-generation"
    assert_rejected(wrong_binding, kwargs, "current Progressive candidate/profile/Dossier binding drift")

    # Exact same pure Stage-1 reconciliation used by the CLI. No materialize,
    # no second queue, no monkeypatch to the Stage-1 safety contract.
    plan = preparation.make_plan(legacy=fresh, **kwargs)
    assert plan["contract"] == "DEEP-STAGE1-MIGRATION-PREPARATION-V1"
    assert plan["semantic_execution_authorized"] is False
    assert plan["production_cutover_performed"] is False
    assert plan["research_assembly_dossier_used"] is False
    assert plan["executable_materialization_authorized"] is False
    assert plan["authorization_blocker"] == (
        "config/deep_two_stage_migration_contract.json: mass_migration_authorized=false"
    )
    assert 0 <= plan["requires_stage1_semantics"] <= plan["eligible_with_current_dossier"] <= plan["current_scope_total"]
    assert plan["current_scope_total"] == scope["deep_total_current_coverage_target"]
    assert len(plan["canonical_work_if_authorized"]["items"]) == plan["requires_stage1_semantics"]
    assert plan["canonical_work_if_authorized"]["implementation_status"] == "implemented_not_active"
    stage1.validate_work_manifest(plan["canonical_work_if_authorized"])
    assert stage1.load_json(preparation.CANONICAL_WORK)["implementation_status"] == "implemented_not_active"
    assert stage1.load_json(preparation.CANONICAL_WORK)["items"] == []
    assert kwargs["migration"]["mass_migration_authorized"] is False
    after = {str(path): bytes_sha256(path) for path in watched}
    assert before == after, "PR read-only validation changed canonical Deep/Stage-1 state"
    preview_path = Path(preview_path).resolve()
    assert preview_path not in {path.resolve() for path in watched}
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("DEEP_STAGE1_PR_PREVIEW=PASS "
          f"committed={committed_status} normal_work={len(fresh['items'])} "
          f"score_migration=43/42/1/0 stage1_candidates={plan['requires_stage1_semantics']} "
          "stage1_activation=false canonical_files_unchanged=true")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview-out", type=Path, required=True)
    args = parser.parse_args()
    validate_pr_preview(args.preview_out)


if __name__ == "__main__":
    main()

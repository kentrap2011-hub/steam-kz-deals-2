#!/usr/bin/env python3
"""GitHub-owned Stage-1 migration scope preparation; never executes semantics.

Preview is audit-only while mass_migration_authorized=false. An executable
canonical manifest can only be materialized after explicit contract authority.
All candidate identities come from current Progressive truth, NEVER legacy scores.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import build_progressive_pass2_work as legacy_builder
import deep_stage1 as s1
import progressive_pass1 as p1
import progressive_pass2 as p2

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/deep_two_stage_migration_contract.json"
OWNERSHIP = ROOT / "config/execution_ownership_contract.json"
OLD_WORK = ROOT / "data/production/pre_ai/progressive_pass2_work.json"
OLD_STATE = ROOT / "data/cache/progressive_pass2_state.json"
NEW_STATE = ROOT / "data/cache/deep_stage1_state.json"
CANONICAL_WORK = ROOT / "data/production/pre_ai/deep_stage1_work.json"


class PreparationError(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise PreparationError(reason)


def bounded_block(blocked, row, code):
    blocked.append({
        "family_id": row["family_id"], "appid": row["appid"],
        "source_work_id": row["work_id"], "reason": str(code),
    })


def make_plan(*, legacy, previous, stage1_state, migration, ownership,
              generation, bindings, by_family, contexts, ordering,
              dossier_binding, dossier_loader, now, root=ROOT,
              dossier_validator=p2.dossier_is_eligible, priority=None):
    """Pure deterministic reconciliation for a fixed repository/time snapshot."""
    s1.validate_state(stage1_state)
    require(migration.get("contract") == "DEEP-TWO-STAGE-MIGRATION-V1"
            and migration.get("status") == "frozen_not_active",
            "canonical migration contract unavailable or activated unexpectedly")
    require((ownership.get("progressive_personalization_phase_c_pass2_core") or {})
            .get("production_execution_authorized") is True,
            "current one-stage Deep must remain production authority")
    require(legacy.get("contract") == "PROGRESSIVE-PASS2-WORK-V1"
            and legacy.get("projection_status")
                == "current_github_owned_fast_dossier_deep_v1_projection",
            "current canonical one-stage Deep work not available")
    require(legacy.get("semantic_generation_id") == generation["semantic_generation_id"]
            and legacy.get("semantic_bindings") == generation["bindings"]
            and legacy.get("profile_pin") == generation["profile_pin"]
            and legacy.get("dossier_compatibility_binding") == dossier_binding,
            "current Progressive candidate/profile/Dossier binding drift")
    require(type((legacy.get("scope") or {}).get("deep_total_current_coverage_target")) is int
            and legacy["scope"]["deep_total_current_coverage_target"] == len(bindings),
            "current Deep coverage and exact Progressive bindings disagree")
    require(isinstance(previous.get("entries"), dict)
            and previous.get("contract") == "PROGRESSIVE-PASS2-STATE-V2",
            "legacy Deep historical state invalid")

    candidates = []
    seen = set()
    for context in contexts:
        fid = str(context.get("family_id") or "")
        if fid not in bindings:
            continue
        require(fid not in seen, "duplicate current family in Progressive context")
        seen.add(fid)
        binding = bindings[fid]
        source_queue = by_family[fid]
        score, priority_error = None, None
        try:
            if priority is not None:
                score = float(priority(context))
            else:
                score = float(legacy_builder.semantic_queue_priority(
                    context, ordering["ordering"])["score"])
        except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
            priority_error = "canonical_semantic_queue_priority_invalid: " + str(exc)
        candidates.append((binding, source_queue, score, priority_error))
    require(len(seen) == len(bindings), "current Deep identities absent from context")
    candidates.sort(key=lambda row: (
        1 if legacy_builder.has_authoritative_deep_history(
            previous, row[0]["family_id"]) else 0,
        row[2] is None, -(row[2] or 0), row[0]["family_id"],
    ))

    source = {
        "profile_pin": generation["profile_pin"],
        "semantic_bindings": generation["bindings"],
        "semantic_generation_id": generation["semantic_generation_id"],
        "dossier_compatibility_binding": dossier_binding,
    }
    eligible, items, completed, blocked, diagnostics = [], [], [], [], []
    for sequence, (binding, source_queue, _, priority_error) in enumerate(candidates, 1):
        if priority_error:
            bounded_block(blocked, binding, priority_error)
            continue
        try:
            semantic = p2._semantic_input(source_queue)
            record = dossier_loader(binding["appid"])
            ok, reason = dossier_validator(
                binding=binding, semantic_input=semantic,
                dossier_record=record, current_binding=dossier_binding, now=now,
            )
            if not ok:
                bounded_block(blocked, binding, reason)
                continue
            require(isinstance(record, dict)
                    and isinstance(record.get("doc"), dict),
                    "accepted canonical Dossier record missing")
            row = {
                **binding, "work_mode": "normal_first_pass",
                "semantic_input": semantic,
                "dossier_path": record["path"],
                "dossier_content_sha256": record["content_sha256"],
                "dossier_compatibility_binding": dossier_binding,
                "dossier_expires_at_utc": record["doc"].get("expires_at_utc"),
            }
            item = s1.make_work_item(source, row, sequence)
            s1.verify_dossier(item, root=root, validator=dossier_validator)
            require(item["work_id"] not in eligible,
                    "duplicate exact Stage-1 work ID")
        except (s1.Stage1Error, PreparationError, KeyError, ValueError, TypeError) as exc:
            bounded_block(blocked, binding, "dossier_or_binding_invalid: " + str(exc))
            continue

        eligible.append(item["work_id"])
        existing = stage1_state["entries"].get(item["work_id"])
        if existing is None:
            items.append(item)
            continue
        try:
            path = str(s1.RESULTS / (item["work_id"] + ".json"))
            require(existing["accepted_result_path"] == path
                    and existing["family_id"] == item["family_id"]
                    and str(existing["appid"]) == item["appid"]
                    and existing["profile_pin"] == item["profile_pin"]
                    and existing["profile_semantic_sha256"] == item["profile_semantic_sha256"]
                    and existing["dossier_content_sha256"] == item["dossier_content_sha256"],
                    "accepted Stage-1 binding or path mismatch")
            actual = s1.safe_repo_path(path, root)
            require(actual.is_file()
                    and s1.file_sha256(actual) == existing["accepted_result_sha256"],
                    "accepted Stage-1 result bytes missing or changed")
            result = s1.load_json(actual)
            s1.validate_result(result, item, root=root)
            if existing["outcome"] != result["outcome"]:
                raise PreparationError("accepted Stage-1 outcome mismatch")
            if result["outcome"] == "analysis_incomplete":
                bounded_block(blocked, binding,
                              "accepted_stage1_incomplete_requires_separate_recovery")
            else:
                completed.append({"work_id": item["work_id"], "family_id": item["family_id"],
                                  "outcome": result["outcome"], "sequence": sequence})
        except (s1.Stage1Error, PreparationError, KeyError, ValueError, TypeError) as exc:
            bounded_block(blocked, binding, "accepted_stage1_invalid_no_retry: " + str(exc))

    work = {
        "schema_version": 1, "contract": s1.WORK_CONTRACT,
        "implementation_status": "implemented_not_active",
        "source": s1.SOURCE, "generated_at_utc": None,
        "total_eligible": len(eligible), "eligible_work_ids": eligible,
        "items": items, "diagnostics": diagnostics,
        "migration_source": "current_progressive_bindings_and_one_stage_canonical_dossiers_only",
    }
    s1.validate_work_manifest(work)
    require(len(completed) + len(items)
            + sum(row["reason"].startswith(("accepted_stage1_",)) for row in blocked)
            >= len(eligible), "current eligible Stage-1 reconciliation incomplete")
    allowed = migration.get("mass_migration_authorized") is True
    return {
        "schema_version": 1,
        "contract": "DEEP-STAGE1-MIGRATION-PREPARATION-V1",
        "executable_materialization_authorized": allowed,
        "semantic_execution_authorized": False,
        "production_cutover_performed": False,
        "canonical_dossier": "accepted_one_stage_only",
        "research_assembly_dossier_used": False,
        "current_scope_total": len(bindings),
        "eligible_with_current_dossier": len(eligible),
        "accepted_current_stage1": completed,
        "requires_stage1_semantics": len(items),
        "blocked_or_waiting": blocked,
        "canonical_work_if_authorized": work,
        "authorization_blocker": None if allowed else
            "config/deep_two_stage_migration_contract.json: mass_migration_authorized=false",
    }


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-out", type=Path)
    ap.add_argument("--materialize", action="store_true",
                    help="write the canonical Stage-1 work only after contract authorization")
    args = ap.parse_args()
    migration = s1.load_json(CONTRACT)
    ownership = s1.load_json(OWNERSHIP)
    contexts = p1.load_jsonl(p1.PROGRESSIVE_CONTEXT)
    projection = s1.load_json(p1.TASTE_PROJECTION)
    queue = p1.load_jsonl(p1.TASTE_QUEUE)
    generation, bindings, by_family = p1.current_bindings(contexts, projection, queue)
    plan = make_plan(
        legacy=s1.load_json(OLD_WORK), previous=s1.load_json(OLD_STATE),
        stage1_state=s1.load_json(NEW_STATE), migration=migration,
        ownership=ownership, generation=generation, bindings=bindings,
        by_family=by_family, contexts=contexts, ordering=p2.load_contract(),
        dossier_binding=p2.current_dossier_binding(),
        dossier_loader=p2.canonical_dossier_loader,
        now=datetime.now(timezone.utc),
    )
    if args.preview_out:
        require(args.preview_out.resolve() != CANONICAL_WORK.resolve(),
                "preview cannot overwrite executable canonical Stage-1 work")
        write_json(args.preview_out, plan)
    if args.materialize:
        require(plan["executable_materialization_authorized"],
                "Stage-1 migration queue is blocked by explicit canonical authorization")
        # Execution is a DIFFERENT authority from preparation. No Stage-1 semantic
        # worker may run just because this non-active work file exists.
        write_json(CANONICAL_WORK, plan["canonical_work_if_authorized"])
    print(json.dumps({
        "scope": plan["current_scope_total"],
        "eligible_dossier": plan["eligible_with_current_dossier"],
        "already_stage1": len(plan["accepted_current_stage1"]),
        "requires_new_stage1": plan["requires_stage1_semantics"],
        "blocked_or_waiting": len(plan["blocked_or_waiting"]),
        "materialization_authorized": plan["executable_materialization_authorized"],
        "semantic_execution_authorized": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read-only, fail-closed Deep two-stage migration and cutover preflight.

Emits audit classification and *already GitHub-authorized* semantic queues.
It never treats a legacy score as new Stage-1 evidence, makes Stage-2 anchors,
alters canonical state, or enables cutover. All executable item bindings come
exclusively from the accepted canonical Stage-1/Stage-2 work manifests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATHS = {
    "architecture": "config/deep_two_stage_architecture_contract.json",
    "migration": "config/deep_two_stage_migration_contract.json",
    "ownership": "config/execution_ownership_contract.json",
    "old_deep": "data/cache/progressive_pass2_state.json",
    "old_deep_work": "data/production/pre_ai/progressive_pass2_work.json",
    "stage1_work": "data/production/pre_ai/deep_stage1_work.json",
    "stage1_state": "data/cache/deep_stage1_state.json",
    "stage2_work": "data/production/pre_ai/deep_stage2_work.json",
    "stage2_state": "data/cache/deep_stage2_state.json",
}


class PreflightError(ValueError):
    pass


def require(condition, explanation):
    if not condition:
        raise PreflightError(explanation)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_digest(value):
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode("utf-8"))


def snapshot(root=ROOT):
    documents, fingerprints = {}, {}
    for name, relpath in PATHS.items():
        raw = (Path(root) / relpath).read_bytes()
        documents[name] = json.loads(raw)
        fingerprints[name] = {"path": relpath, "sha256": digest(raw)}
    return documents, fingerprints


def checked_work(doc, contract):
    require(doc.get("schema_version") == 1 and doc.get("contract") == contract,
            f"{contract}: prepared work contract mismatch")
    require(isinstance(doc.get("items"), list),
            f"{contract}: missing immutable GitHub work item list")
    return doc["items"]


def checked_state(doc, contract):
    require(doc.get("contract") == contract and
            doc.get("schema_version") == 1 and
            isinstance(doc.get("entries"), dict),
            f"{contract}: canonical state contract mismatch")
    return doc["entries"]


def legacy_classification(entries):
    """Never coerce old fixed-five-factor arithmetic into holistic Stage 1."""
    classified = []
    for key, entry in sorted(entries.items()):
        require(isinstance(key, str) and isinstance(entry, dict),
                "legacy Deep history contains an invalid identity or entry")
        classified.append({
            "legacy_state_key": key,
            "legacy_entry_sha256": canonical_digest(entry),
            "classification": "requires_stage1_reanalysis",
            "reason": "new_holistic_dynamic_point_breakdown_and_new_evidence_contract_not_proven",
            "family_id_unverified": entry.get("family_id"),
            "appid_unverified": entry.get("appid"),
            "semantic_execution_authorized": False,
        })
    return classified


def unique_calibrations(entries):
    seen = {}
    for key, entry in entries.items():
        require(isinstance(entry, dict), f"Stage-2 entry {key}: invalid")
        if entry.get("status") != "calibrated":
            continue
        try:
            score = Decimal(str(entry["calibrated_deep_fit_score_0_56"]))
        except (KeyError, InvalidOperation, ValueError) as exc:
            raise PreflightError(f"Stage-2 {key}: invalid calibrated score") from exc
        require(score.is_finite() and Decimal("0") <= score <= Decimal("56")
                and score == score.quantize(Decimal("0.01")),
                f"Stage-2 {key}: calibrated score must have <=2 decimals in 0..56")
        require(score not in seen,
                f"Stage-2 displayed tie between {seen.get(score)} and {key}")
        seen[score] = key
    return len(seen)


def plan(documents, fingerprints):
    d = documents
    architecture = d["architecture"]
    migration = d["migration"]
    ownership = d["ownership"]
    require(architecture.get("contract") == "DEEP-TWO-STAGE-ARCHITECTURE-V1"
            and architecture.get("status") == "frozen_not_active"
            and architecture.get("production_cutover_authorized") is False,
            "architecture has unexpectedly changed: do not run migration preflight")
    require(migration.get("contract") == "DEEP-TWO-STAGE-MIGRATION-V1"
            and migration.get("mass_migration_authorized") is False
            and migration.get("semantic_execution_authorized_by_this_contract") is False,
            "migration unexpectedly authorizes semantic or mass execution")
    require((ownership.get("progressive_personalization_phase_c_pass2_core") or {})
            .get("production_execution_authorized") is True,
            "current canonical monolithic Deep production authority is not proven")
    scope = d["old_deep_work"].get("scope") or {}
    require(d["old_deep_work"].get("contract") == "PROGRESSIVE-PASS2-WORK-V1"
            and isinstance(scope, dict), "canonical legacy Deep source missing")
    old_entries = checked_state_legacy(d["old_deep"])
    w1 = checked_work(d["stage1_work"], "DEEP-STAGE1-WORK-V1")
    s1 = checked_state(d["stage1_state"], "DEEP-STAGE1-STATE-V1")
    w2 = checked_work(d["stage2_work"], "DEEP-STAGE2-WORK-V1")
    s2 = checked_state(d["stage2_state"], "DEEP-STAGE2-STATE-V1")
    require(d["stage1_work"].get("implementation_status") == "implemented_not_active"
            and d["stage1_state"].get("implementation_status") == "implemented_not_active"
            and d["stage2_state"].get("implementation_status") == "implemented_not_active",
            "new semantic state unexpectedly activated")
    for work, label, id_field in ((w1, "Stage-1", "work_id"),
                                  (w2, "Stage-2", "calibration_work_id")):
        identities = [item.get(id_field) for item in work]
        require(all(isinstance(x, str) and len(x) == 64 for x in identities)
                and len(set(identities)) == len(identities),
                f"{label}: prepared work identities invalid or duplicated")
    total = scope.get("deep_total_current_coverage_target")
    dossier_waiting = scope.get("deep_waiting_for_dossier_count")
    require(type(total) is int and total >= 0 and
            type(dossier_waiting) is int and 0 <= dossier_waiting <= total,
            "legacy Deep coverage scope is not current and countable")
    calibrated = unique_calibrations(s2)
    eligible_ids = d["stage1_work"].get("eligible_work_ids")
    require(isinstance(eligible_ids, list) and
            all(isinstance(x, str) and len(x) == 64 for x in eligible_ids) and
            len(set(eligible_ids)) == len(eligible_ids),
            "GitHub prepared Stage-1 full eligibility ledger is invalid")
    eligible = set(eligible_ids)
    require({item["work_id"] for item in w1}.issubset(eligible),
            "Stage-1 queue escapes its canonical eligibility ledger")
    current_s1 = {key: value for key, value in s1.items()
                  if key in eligible and isinstance(value, dict)
                  and value.get("status") == "accepted"
                  and value.get("accepted") is True
                  and value.get("outcome") in ("analyzed_fit", "analyzed_not_fit")}
    stage1_completed = len(current_s1)
    fit_ids = {key for key, value in current_s1.items()
               if value["outcome"] == "analyzed_fit"}
    fit = len(fit_ids)
    linked_fit_ids = set()
    for stage2 in s2.values():
        if stage2.get("status") != "calibrated":
            continue
        work_id = stage2.get("stage1_work_id")
        prior = current_s1.get(work_id)
        if (prior is not None and work_id in fit_ids
                and stage2.get("outcome") == "calibrated_fit"
                and stage2.get("family_id") == prior.get("family_id")
                and str(stage2.get("appid")) == str(prior.get("appid"))
                and stage2.get("profile_semantic_sha256") == prior.get("profile_semantic_sha256")
                and stage2.get("stage1_result_path") == prior.get("accepted_result_path")
                and stage2.get("stage1_result_sha256") == prior.get("accepted_result_sha256")):
            require(work_id not in linked_fit_ids,
                    f"two calibrated Stage-2 states bind the same current Stage-1 fit {work_id}")
            linked_fit_ids.add(work_id)
    missing = []
    if total == 0:
        missing.append("no_current_scope_to_verify")
    if dossier_waiting:
        missing.append("current_canonical_dossier_evidence_incomplete")
    if d["stage1_work"].get("total_eligible") != total or len(eligible) != total:
        missing.append("stage1_eligible_scope_does_not_cover_current_games")
    if stage1_completed != total:
        missing.append("stage1_authoritative_semantics_not_complete")
    if fit != len(linked_fit_ids):
        missing.append("stage2_calibrations_not_complete_for_all_stage1_fit")
    if w1 or w2:
        missing.append("authorized_semantic_items_still_pending")
    if calibrated == 0:
        missing.append("stage2_seed_or_anchors_not_yet_proven")
    # Readiness is deliberately not cutover authority: only a separate exact
    # future authorized integration can switch machine contracts atomically.
    return {
        "schema_version": 1,
        "contract": "DEEP-TWO-STAGE-PRECUTOVER-PREFLIGHT-V1",
        "source_files": fingerprints,
        "production_authority": "FAST-DOSSIER-DEEP-V1",
        "cutover_performed": False,
        "cutover_ready": not missing,
        "blocking_gates": missing,
        "current_legacy_scope": scope,
        "legacy_classification": legacy_classification(old_entries),
        "legacy_reuse_policy": "all_history_requires_stage1_reanalysis_without_exact_new_structured_proof",
        "canonical_stage1_authorized_queue": w1,
        "canonical_stage2_authorized_queue": w2,
        "stage1_accepted_entries": len(s1),
        "stage1_authoritative_completed": stage1_completed,
        "stage1_fit_accepted": fit,
        "stage2_accepted_entries": len(s2),
        "stage2_unique_calibrated": calibrated,
        "stage2_current_exactly_linked_fit_calibrations": len(linked_fit_ids),
        "canonical_dossier": "current_accepted_taste_steam_review_dossier_only",
        "research_assembly_dossier_used": False,
        "semantic_execution_performed": False,
        "next_action": "external_explicit_GitHub_prepared_semantic_work_only_after_separate_authorization",
    }


def checked_state_legacy(doc):
    require(doc.get("contract") == "PROGRESSIVE-PASS2-STATE-V2"
            and doc.get("schema_version") == 2
            and isinstance(doc.get("entries"), dict),
            "legacy monolithic Deep state contract mismatch")
    return doc["entries"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = plan(*snapshot(args.root))
    serialized = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(serialized, encoding="utf-8")
    print(json.dumps({
        "cutover_ready": result["cutover_ready"],
        "cutover_performed": result["cutover_performed"],
        "legacy_entries_classified": len(result["legacy_classification"]),
        "stage1_authorized": len(result["canonical_stage1_authorized_queue"]),
        "stage2_authorized": len(result["canonical_stage2_authorized_queue"]),
        "stage1_accepted": result["stage1_accepted_entries"],
        "stage2_calibrated": result["stage2_unique_calibrated"],
        "blocking_gates": result["blocking_gates"],
        "report_path": str(args.out) if args.out else None,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

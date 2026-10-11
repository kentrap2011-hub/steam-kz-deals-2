#!/usr/bin/env python3
"""Inactive, read-only Research -> Assembly / accepted one-stage V2 shadow diagnostics.

This module does not fetch sources, select games, persist a report, accept
Dossiers, or grant Deep readiness. The public Git-bound entrypoint requires an
explicitly marked disposable Git fixture and delegates all chain/strict V2
validation to the existing final-acceptance bridge.
"""
import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from dossier_two_stage_contract_guard import canonical_sha256
from dossier_two_stage_final_acceptance import (
    STATUS_GROUP_READY, STATUS_VALID, inspect_original_groups,
)
from dossier_two_stage_staging import blob, file_at, first_parent_contains, git, json_at, marker_context, strict_json
from taste_steam_review_dossier_strict import validate_dossier_strict

SCHEMA = "DOSSIER-TWO-STAGE-SHADOW-QUALITY-DIAGNOSTIC-V1"
H40 = re.compile(r"^[0-9a-f]{40}$")
H64 = re.compile(r"^[0-9a-f]{64}$")
DIMENSIONS = (
    "core_play_mechanics", "controls_game_feel", "progression_development_unlocks",
    "variety_repetition_over_time", "difficulty_mastery_learning_friction",
    "pacing_structure_direction", "exploration_mission_activity_structure",
    "multiplayer_coop_dependence", "story_characters_identity_hooks",
    "recurring_strengths", "recurring_complaints_tradeoffs",
    "technical_performance_localization_regional",
)
JUDGMENTS = ("unknown", "needs_review", "confirmed_issue", "confirmed_no_issue")
AREAS = (
    "source_truth", "independence", "research_completeness", "negative_risks",
    "meaningful_omissions", "unsupported_claims", "contradictions",
    "temporal_fidelity", "privacy_fidelity", "conclusion_quality",
)


def _require(ok, reason):
    if not ok:
        raise ValueError("shadow quality fail closed: " + reason)


def _one_year(value):
    _require(type(value) is int or value is None, "invalid original work year")
    return value


def _unique(items, what):
    _require(len(items) == len(set(items)), "duplicate " + what)


def _material_statements(dossier):
    return [
        {"category": obs["category"], "sentiment": obs["sentiment"],
         "statement": obs["statement"], "source_ids": obs["source_ids"],
         "player_feedback_ids": obs["player_feedback_ids"],
         "evidence_status": obs["evidence_status"]}
        for obs in dossier["observations"]
    ]


def _negative(dossier):
    return [item for item in _material_statements(dossier)
            if item["sentiment"] in ("negative", "mixed")]


def _source_rows(dossier):
    return [{
        "source_id": s["source_id"],
        "locator": s.get("url") or s.get("public_ref"),
        "source_type": s["source_type"],
        "player_feedback": s["player_feedback"],
        "language": s["language"],
        "publication_date": s["publication_date"],
        "freshness": s["freshness"],
    } for s in dossier["provenance"]["sources"]]


def _physical_sources(research):
    sources = research["sources"]
    ids = [s.get("physical_source_identity") or s.get("normalized_locator")
           or (s["locator"].get("url") or s["locator"].get("public_ref"))
           for s in sources if s["player_feedback"]]
    return {"research_source_refs": [s["ref"] for s in sources],
            "physical_player_source_identities": ids,
            "duplicate_physical_player_source_identities": sorted(
                key for key, n in Counter(ids).items() if n > 1)}


def _review(review):
    # Human semantic assessments are NEVER inferred from lexical comparison.
    if review is None:
        return {area: {"status": "unknown", "evidence_refs": [], "note": None}
                for area in AREAS}
    _require(type(review) is dict and set(review) == set(AREAS),
             "human-review areas must be exact")
    for area, finding in review.items():
        _require(type(finding) is dict and set(finding) == {"status", "evidence_refs", "note"},
                 "invalid review finding: " + area)
        _require(finding["status"] in JUDGMENTS and type(finding["evidence_refs"]) is list
                 and all(type(x) is str and x for x in finding["evidence_refs"])
                 and (finding["note"] is None or (type(finding["note"]) is str
                     and 4 <= len(finding["note"]) <= 800)), "bad reviewer evidence: " + area)
        _require(finding["status"] not in ("confirmed_issue", "confirmed_no_issue")
                 or (finding["evidence_refs"] and finding["note"]),
                 "confirmed human judgment needs evidence and reason: " + area)
    return copy.deepcopy(review)


def compare_records(research, assembly, baseline, *, human_review=None):
    """Pure diagnostic projection over ALREADY-validated/synthetic objects.

    Never call this standalone projection proof of Git binding or acceptance.
    Source citations and baseline statements are preserved for later reviewers;
    exact-text mismatch means REVIEW NEEDED, not a semantic regression.
    """
    _require(all(type(x) is dict for x in (research, assembly, baseline)),
             "input objects required")
    _require(assembly.get("outcome") == "assembled_candidate_ready"
             and assembly.get("payload", {}).get("status") == "assembled_candidate_ready",
             "only final assembled candidate is comparable")
    candidate = assembly["payload"]["dossier"]
    a = research["assignment"]
    _require(a["appid"] == candidate["appid"] == baseline["appid"]
             and a["title"] == candidate["title"] == baseline["title"],
             "exact appid and storefront title mismatch")
    _require(research["identity"]["resolution"] == "resolved"
             and candidate["game_identity"]["resolution_status"] == "resolved"
             and baseline["game_identity"]["resolution_status"] == "resolved",
             "unresolved game identity")
    year_research = _one_year(research["identity"]["original_work_release_year"])
    year_new = _one_year(candidate["game_identity"]["release_year"])
    year_old = _one_year(baseline["game_identity"]["release_year"])
    _require(year_research == year_new, "Research/Assembly original-work-year contradiction")
    audit = research["research_audit"]
    survey = audit["dimension_survey"]
    _require(type(survey) is list and len(survey) == 12
             and {x["dimension"] for x in survey} == set(DIMENSIONS),
             "not exactly twelve Research dimensions")
    new_coverage = candidate["evidence"]["coverage"]["dimensions"]
    old_coverage = baseline["evidence"]["coverage"]["dimensions"]
    _require({x["dimension"] for x in new_coverage} == set(DIMENSIONS)
             and len(new_coverage) == 12
             and {x["dimension"] for x in old_coverage} == set(DIMENSIONS)
             and len(old_coverage) == 12, "malformed V2 twelve-dimension coverage")
    findings = {f["ref"] for f in research["findings"]}
    _unique([f["ref"] for f in research["findings"]], "Research finding refs")
    for dim in survey:
        _require(set(dim["finding_refs"]).issubset(findings), "unbound Research dimension finding")
    dims = {x["dimension"]: {"research": x["investigation_state"],
                             "research_finding_refs": list(x["finding_refs"])}
            for x in survey}
    for key, rows in (("two_stage", new_coverage), ("one_stage", old_coverage)):
        for row in rows:
            dims[row["dimension"]][key] = row["state"]
    gaps = audit["unresolved_gaps"]
    gap_ids = [g["gap_id"] for g in gaps]
    _unique(gap_ids, "Research gaps")
    operations = assembly["supplemental_operations"]
    for op in operations:
        _require(op["gap_id"] in gap_ids and
                 op["source_ref"] in [s["ref"] for s in research["sources"]],
                 "unbound supplemental exact-source revisit")
        lookup = op["narrow_gap_lookup"]
        _require(lookup is None or (
            op["exact_source_revisit"]["status"] == "genuinely_absent"
            and lookup["gap_id"] == op["gap_id"] and lookup["appid"] == a["appid"]
            and lookup["original_work_release_year"] == year_research
            and lookup["original_work_title"] == research["identity"]["resolved_title"]),
            "ineligible narrow lookup")
    old_observations = _material_statements(baseline)
    new_observations = _material_statements(candidate)
    # Exact text agreement is weak evidence; never infer semantic equivalence.
    new_exact = {(x["category"], x["sentiment"], x["statement"].strip().casefold())
                 for x in new_observations}
    unmatched = [x for x in old_observations if
                 (x["category"], x["sentiment"], x["statement"].strip().casefold())
                 not in new_exact]
    reviewed = _review(human_review)
    contradiction = year_old != year_new
    confirmed_issues = [area for area, v in reviewed.items() if v["status"] == "confirmed_issue"]
    return {
        "appid": a["appid"], "title": a["title"], "measured": True,
        "identity": {"original_work_year_research": year_research,
                     "original_work_year_two_stage": year_new,
                     "original_work_year_one_stage": year_old,
                     "year_conflict_with_baseline": contradiction,
                     "steam_storefront_release_year": "not_measured_separate_identity_kind"},
        "research": {"twelve_dimensions": {k: dims[k] for k in DIMENSIONS},
                     "research_completeness": audit["completeness"],
                     "research_completion_basis": audit["completion_basis"],
                     "gaps": copy.deepcopy(gaps),
                     "strengths_investigated": audit["strengths_investigated"],
                     "weaknesses_tradeoffs_investigated": audit["weaknesses_tradeoffs_investigated"],
                     "russian_attempt": audit["russian_attempt_observed"]},
        "sources": {"research": _physical_sources(research),
                    "two_stage": _source_rows(candidate),
                    "one_stage": _source_rows(baseline),
                    "source_truth_human_verification": reviewed["source_truth"]["status"],
                    "independence_human_verification": reviewed["independence"]["status"]},
        "gaps_and_revisits": {"exact_source_first_operations": copy.deepcopy(operations),
                              "unresolved_material_gap_ids": [
                                  g["gap_id"] for g in gaps if g["material"]]},
        "comparison_evidence": {
            "one_stage_statements": old_observations,
            "two_stage_statements": new_observations,
            "one_stage_negative_or_mixed": _negative(baseline),
            "two_stage_negative_or_mixed": _negative(candidate),
            "lexically_unmatched_baseline_statements_needing_human_review": unmatched,
            "one_stage_conflicts": copy.deepcopy(baseline["conflicts"]),
            "two_stage_conflicts": copy.deepcopy(candidate["conflicts"]),
            "research_findings": [{
                "ref": f["ref"], "text": f["safe_neutral_synthesis"],
                "polarity": f["polarity_hint"], "support_feedback_refs": f["support_feedback_refs"],
                "source_refs": f["contextual_source_refs"],
                "uncertainty": f["uncertainty_note"]} for f in research["findings"]],
        },
        "fidelity": {"new_generated_at": candidate["generated_at_utc"],
                     "old_generated_at": baseline["generated_at_utc"],
                     "new_ttl_days": candidate["ttl_days"],
                     "old_ttl_days": baseline["ttl_days"],
                     "strict_v2": "validated_by_GitHub_existing_inspector",
                     "temporal_semantics": reviewed["temporal_fidelity"]["status"],
                     "privacy_semantics": reviewed["privacy_fidelity"]["status"]},
        "human_quality_review": reviewed,
        "hard_stop_reasons": (["original_work_year_disagrees_with_one_stage"]
                              if contradiction else []) +
                             (["human_confirmed_" + area for area in confirmed_issues
                               if area in ("source_truth", "contradictions", "privacy_fidelity")]),
        "semantic_quality_verdict": "human_review_required",
        "canonical_acceptance_granted": False, "deep_readiness_granted": False,
    }


def _baseline(repo, appid, spec, contract, head):
    _require(type(spec) is dict and set(spec) == {
        "appid", "commit", "path", "git_blob_sha", "canonical_sha256"},
        "exact baseline immutable locator fields required")
    _require(spec["appid"] == appid
             and spec["path"] == f"data/cache/taste_steam_review_dossiers/App_{appid}.json"
             and isinstance(spec["commit"], str) and H40.fullmatch(spec["commit"])
             and isinstance(spec["git_blob_sha"], str) and H40.fullmatch(spec["git_blob_sha"])
             and isinstance(spec["canonical_sha256"], str) and H64.fullmatch(spec["canonical_sha256"]),
             "baseline must point to exact canonical one-stage cache path with hashes")
    _require(first_parent_contains(repo, spec["commit"], head),
             "baseline commit not in frozen Git history")
    raw = file_at(repo, spec["commit"], spec["path"])
    _require(blob(repo, spec["commit"], spec["path"]) == spec["git_blob_sha"]
             and blob(repo, head, spec["path"]) == spec["git_blob_sha"],
             "baseline cache bytes changed")
    data = strict_json(raw)
    _require(canonical_sha256(data) == spec["canonical_sha256"], "baseline hash mismatch")
    validate_dossier_strict(data, contract, expected_appid=appid,
                            require_fresh_at_acceptance=False)
    return data


def evaluate_offline_fixture(repo, *, manifest, contract, item_locators,
                             baseline_references, human_reviews=None):
    """Bounded Git fixture only. No production CLI and no mutation.

    Existing final inspector is called FIRST. Validating a frozen cache file is
    not proof of its historical accepted-state transition; trial operator must
    independently attest that from GitHub writer receipts before claiming parity.
    """
    _require(type(baseline_references) is list and type(human_reviews or {}) is dict,
             "explicit baseline list and optional reviewer map required")
    _require(all(type(x) is dict for x in baseline_references), "invalid baseline list")
    base = {x.get("appid"): x for x in baseline_references}
    _require(len(base) == len(baseline_references), "duplicate baseline AppID")
    # This call gates disposable Git safety and performs authoritative frozen
    # Research -> Assembly -> strict V2 original-three-game fixture validation.
    inspected = inspect_original_groups(
        repo, manifest=manifest, contract=contract, item_locators=item_locators,
        offline_fixture=True)
    _require(not inspected["unmatched_locators"], "foreign/replayed item locators")
    head = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
    reviews = human_reviews or {}
    result = []
    used = set()
    for decision in inspected["decisions"]:
        descriptor = next(x for x in manifest["submission_group_plan"]["groups"]
                          if x["sequence"] == decision["sequence"])
        for slot, item in enumerate(descriptor["items"]):
            appid = item["appid"]
            _require(appid not in used, "duplicate original group AppID")
            used.add(appid)
            info = {"appid": appid, "title": item["title"],
                    "group_sequence": decision["sequence"], "item_index": slot,
                    "chain_status": decision["items"][slot]["status"]
                    if decision["items"] else decision["status"],
                    "baseline_acceptance": "not_verified_separate_writer_receipt_required",
                    "canonical_acceptance_granted": False, "deep_readiness_granted": False}
            if decision["status"] != STATUS_GROUP_READY:
                info["comparison"] = None
                info["reason"] = "strict_original_group_not_ready_or_not_submitted"
            else:
                _require(info["chain_status"] == STATUS_VALID,
                         "ready group contains invalid item")
                _require(appid in base, "missing exact one-stage baseline locator")
                ref = next((r for r in item_locators if r["sequence"] == decision["sequence"]
                            and r["item_index"] == slot), None)
                _require(ref is not None, "missing validated transport locator")
                frozen, _ = marker_context(repo, ref["marker_commit"], "assembly")
                plan = json_at(repo, frozen, ref["work_path"])
                transport_path = (f"data/ai_inbox/dossier_assembly/{descriptor['snapshot_id']}/"
                                  f"g{decision['sequence']:06d}/{appid}--"
                                  f"{plan['assembly_assignment_id']}.json")
                assembly = strict_json(file_at(repo, ref["result_commit"], transport_path))
                rt = assembly["research_transport"]
                research = strict_json(file_at(repo, rt["research_package_git_commit"],
                                               rt["research_package_path"]))
                old = _baseline(repo, appid, base[appid], contract, head)
                info["comparison"] = compare_records(
                    research, assembly, old, human_review=reviews.get(appid))
                info["immutable_evidence"] = {
                    "assembly_result_commit": ref["result_commit"],
                    "assembly_path": transport_path,
                    "assembly_git_blob_sha": blob(repo, ref["result_commit"], transport_path),
                    "research_result_commit": rt["research_package_git_commit"],
                    "research_path": rt["research_package_path"],
                    "research_git_blob_sha": rt["research_package_blob_sha"],
                    "baseline": copy.deepcopy(base[appid]),
                    "two_stage_dossier_canonical_sha256":
                        canonical_sha256(assembly["payload"]["dossier"])}
            result.append(info)
    _require(set(base).issubset(used), "baseline references for foreign AppIDs")
    _require(set(reviews).issubset(used), "human findings for foreign AppIDs")
    stats = Counter("compared" if item["comparison"] else "not_measured" for item in result)
    stops = sorted({reason for item in result if item["comparison"]
                    for reason in item["comparison"]["hard_stop_reasons"]})
    return {"schema": SCHEMA, "active": False, "authoritative": False,
            "snapshot_id": inspected["snapshot_id"],
            "frozen_manifest_sha256": inspected["manifest_sha256"],
            "per_game": result,
            "cohort": {"games": len(result), "compared": stats["compared"],
                       "not_measured": stats["not_measured"],
                       "hard_stop_reasons": stops,
                       "baseline_acceptance_verified": False,
                       "real_source_truth_verified": False,
                       "semantic_parity_approved": False,
                       "approved_failure_rates": None,
                       "canonical_readiness": False, "deep_readiness": False},
            "diagnostic_only": True, "writes": [], "semantic_execution": False}

#!/usr/bin/env python3
"""Bounded, INACTIVE 18-game sandbox Assembly operator and quality-pair adapter.

Only disposable Git replicas are accepted. No CLI that invokes semantics, no
network, Git writes, live canonical writer, cache, Deep or scheduler interface.
An offline-ready status never grants permission to execute a semantic worker.
"""
import copy
import hashlib
import json
import re
from pathlib import Path

from dossier_two_stage_assembly_semantic_worker import (
    frozen_assembly_traversal, inactive_assembly_gate,
)
from dossier_two_stage_async_buffer import frozen_buffer
from dossier_two_stage_contract_guard import ROOT, canonical_sha256
from dossier_two_stage_final_acceptance import offline_gate, inspect_original_groups
from dossier_two_stage_staging import (
    blob, file_at, first_parent_contains, git, json_at, marker_context,
    require_only_new, strict_json,
)
from dossier_shadow_quality_review_gate import evaluate_offline_fixture as quality_gate

DECISION = (ROOT / "reviews/dossier_shadow_offline/"
            "dossier_shadow_calibration_20261011_6x3_director_decision_v1.json")
AUTHORITY_SCHEMA = "DOSSIER-SHADOW-18-SANDBOX-ASSEMBLY-AUTHORITY-V1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
AUTHORITY_PREFIX = "reviews/dossier_shadow_offline/"
SEQUENCES = (3, 8, 13, 15, 18, 20)


def require(condition, reason):
    if not condition:
        raise ValueError("18-game sandbox Assembly: " + reason)


def _decision():
    d = json.loads(DECISION.read_text(encoding="utf-8"))
    scope = d["scope"]
    require(d["schema"] == "DOSSIER-SHADOW-CALIBRATION-DIRECTOR-DECISION-V1"
            and d["trial_id"] == "dossier-shadow-calibration-20261011-6x3"
            and tuple(scope["group_order"]) == SEQUENCES
            and len(scope["groups"]) == 6 and scope["total_games"] == 18
            and scope["total_groups"] == 6
            and [x["sequence"] for x in scope["groups"]] == list(SEQUENCES)
            and all(len(x["appids"]) == 3 and SHA64.fullmatch(x["group_sha256"])
                    for x in scope["groups"])
            and len({appid for g in scope["groups"] for appid in g["appids"]}) == 18
            and d["operator_authority"]["actual_semantic_execution_permitted_now"] is False
            and d["two_stage_production_active"] is False,
            "the immutable Director selection or pilot prohibition has changed")
    return d


def _rows(decision):
    return [
        {"sequence": group["sequence"], "item_index": i, "appid": appid,
         "status": "waiting_for_authorized_research",
         "research_submission": "not_proven", "assembly_semantic_attempt_consumed": False,
         "research_elapsed_ms": None, "assembly_elapsed_ms": None,
         "pair_quality_status": "not_measured"}
        for group in decision["scope"]["groups"]
        for i, appid in enumerate(group["appids"])
    ]


def _frozen_authority(repo, ref, decision):
    require(type(ref) is dict and set(ref) == {"commit", "path", "git_blob_sha"},
            "exact original Director integration locator required")
    commit, path, sha = (ref[k] for k in ("commit", "path", "git_blob_sha"))
    require(isinstance(commit, str) and SHA40.fullmatch(commit)
            and isinstance(sha, str) and SHA40.fullmatch(sha)
            and isinstance(path, str) and path.startswith(AUTHORITY_PREFIX)
            and path.endswith(".json") and ".." not in Path(path).parts,
            "unsafe sandbox Git authority locator")
    head = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
    require(first_parent_contains(repo, commit, head)
            and blob(repo, commit, path) == sha and blob(repo, head, path) == sha,
            "stale, replaced or out-of-history sandbox authority")
    doc = strict_json(file_at(repo, commit, path))
    require(type(doc) is dict and set(doc) == {
        "schema", "trial_id", "director_decision_sha256", "group_order",
        "groups", "sandbox_only", "external_semantic_authorized",
        "production_writes", "scheduled_tasks_mutated"
    } and doc["schema"] == AUTHORITY_SCHEMA
            and doc["trial_id"] == decision["trial_id"]
            and doc["director_decision_sha256"] == canonical_sha256(decision)
            and doc["group_order"] == list(SEQUENCES)
            and type(doc["groups"]) is list and len(doc["groups"]) == 6
            and [g.get("sequence") for g in doc["groups"]] == list(SEQUENCES)
            and doc["sandbox_only"] is True
            and doc["external_semantic_authorized"] is False
            and doc["production_writes"] == []
            and doc["scheduled_tasks_mutated"] is False,
            "pilot sandbox authority does not bind the fixed Director scope")
    return doc


def _inspect_group(repo, expected, authority_group, commits):
    """Both original stage markers/buffers, exactly three old group slots.

    Shared marker/buffer failure is group-fatal. Per-item Research failure is
    zero-attempt and never prevents a valid sibling's independent readiness.
    """
    require(type(authority_group) is dict and set(authority_group) == {
        "sequence", "research_marker_commit", "research_buffer_path",
        "assembly_marker_commit", "assembly_buffer_path"},
        "unexpected authority field or missing pinned stage marker")
    seq = expected["sequence"]
    rmarker, amarker = (authority_group[k] for k in (
        "research_marker_commit", "assembly_marker_commit"))
    rparent, _ = marker_context(repo, rmarker, "research")
    aparent, _ = marker_context(repo, amarker, "assembly")
    require(first_parent_contains(repo, rmarker, amarker),
            "Assembly marker predates original Research marker")
    research = frozen_buffer(repo, marker_commit=rmarker,
                             buffer_path=authority_group["research_buffer_path"],
                             phase="research")
    assembly = frozen_buffer(repo, marker_commit=amarker,
                             buffer_path=authority_group["assembly_buffer_path"],
                             phase="assembly")
    ritems, aitems = research["items"], assembly["items"]
    require(len(ritems) == len(aitems) == 3
            and all(e["group_sequence"] == seq and e["item_index"] == i
                    and e["appid"] == expected["appids"][i]
                    for i, e in enumerate(ritems))
            and all(e["group_sequence"] == seq and e["item_index"] == i
                    and e["appid"] == expected["appids"][i]
                    for i, e in enumerate(aitems))
            and research["snapshot_id"] == assembly["snapshot_id"],
            "original frozen three-game group order/identity mismatch")
    path = ("data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
            f"{assembly['snapshot_id']}/g{seq:06d}.json")
    desc_a, desc_r = json_at(repo, aparent, path), json_at(repo, rparent, path)
    require(desc_a == desc_r
            and desc_a["sequence"] == seq
            and desc_a["group_sha256"] == expected["group_sha256"]
            and desc_a["appids"] == expected["appids"]
            and [str(e["appid"]) for e in desc_a["items"]] == expected["appids"]
            and len(desc_a["items"]) == 3,
            "original descriptor or group SHA changed between stages")
    require(all(a["research_prepared_work_path"] == r["work_path"]
                and a["research_prepared_work_blob_sha"] == r["work_blob_sha"]
                for a, r in zip(aitems, ritems)),
            "Assembly plan does not bind original stage-A assignment/blob")
    require(type(commits) is dict and set(commits) <= {e["work_path"] for e in aitems},
            "foreign Research commit locator or unauthorized scope")
    decisions = frozen_assembly_traversal(
        repo, marker_commit=amarker,
        buffer_path=authority_group["assembly_buffer_path"],
        submitted_commits=commits)
    require([e["work_path"] for e in decisions] == [e["work_path"] for e in aitems],
            "worker traversal reordered original group")
    # Strict final ingest also rechecks the live Git tree. Refuse stale or
    # overwritten original submitted bytes *before* any future semantic work.
    # Preserve B/C liveness when only A's submitted transport was rewritten.
    for item_index, item in enumerate(decisions):
        if item["status"] != "ready":
            continue
        rt = item["work"]["research_transport"]
        try:
            unchanged = (first_parent_contains(
                repo, rt["research_package_git_commit"], "HEAD")
                and blob(repo, "HEAD", rt["research_package_path"])
                == rt["research_package_blob_sha"])
        except (ValueError, KeyError):
            unchanged = False
        if not unchanged:
            item.clear()
            item.update({"work_path": aitems[item_index]["work_path"],
                         "status": "research_transport_invalid",
                         "attempt_consumed": False,
                         "diagnostic_code": "research_original_blob_changed"})
    return decisions


def inspect_offline_pilot(repo, *, authority_ref=None, submitted_commits=None,
                          offline_fixture=False):
    """18 fixed denominator rows and finite ordered source-safe one-shot plan.

    A future operator needs a separately Director-pinned Git authority, stage-A
    submissions, explicit reviewer authorization and fresh semantic permission.
    This function is NOT that authorization and cannot run semantic analysis.
    """
    offline_gate(repo, offline_fixture=offline_fixture)
    inactive_assembly_gate()
    decision = _decision()
    rows = _rows(decision)
    result = {"schema": "DOSSIER-SHADOW-18-ASSEMBLY-PLAN-V1",
              "trial_id": decision["trial_id"], "sandbox_only": True,
              "semantic_execution_permitted": False, "canonical_acceptance": False,
              "deep_ready": False, "production_writes": [], "scheduled_tasks_mutated": False,
              "quality_verified": False, "quality_thresholds_approved": False,
              "real_source_authenticity_verified": False, "per_game": rows,
              "groups": [], "timing_provenance": "no_measured_semantic_timestamps_yet"}
    if authority_ref is None:
        result["status"] = "waiting_for_authorized_research"
        result["counts"] = {"frozen_groups": 6, "frozen_games": 18,
                            "research_not_submitted_or_unproven": 18,
                            "assembly_transport_ready": 0, "semantic_attempts": 0}
        return result
    doc = _frozen_authority(repo, authority_ref, decision)
    require(submitted_commits is not None and type(submitted_commits) is dict
            and set(submitted_commits) <= set(SEQUENCES),
            "Research original introducing Git commit map must be bounded")
    ready = 0
    for index, (expected, group) in enumerate(zip(decision["scope"]["groups"],
                                                   doc["groups"])):
        decisions = _inspect_group(repo, expected, group, submitted_commits.get(
            expected["sequence"], {}))
        for i, entry in enumerate(decisions):
            row = rows[index * 3 + i]
            row["status"] = entry["status"]
            row["research_submission"] = (
                "original_git_transport_proven" if entry["status"] in
                ("ready", "candidate_already_submitted") else "not_proven")
            if entry["status"] == "ready":
                ready += 1
                # Work carries the full nine-field Research Git transport proof.
                row["immutable_work"] = copy.deepcopy(entry["work"])
            if entry["status"] == "research_transport_invalid":
                row["diagnostic_code"] = "research_origin_or_binding_invalid"
        result["groups"].append({
            "sequence": expected["sequence"], "group_sha256": expected["group_sha256"],
            "denominator": 3, "ready_items": sum(x["status"] == "ready" for x in decisions),
            "final_strict_group_accepted": False,
        })
    result["status"] = ("sandbox_assembly_invocation_ready" if ready
                        else "waiting_for_authorized_research")
    result["counts"] = {"frozen_groups": 6, "frozen_games": 18,
                        "research_not_submitted_or_unproven": sum(
                            row["research_submission"] == "not_proven" for row in rows),
                        "assembly_transport_ready": ready, "semantic_attempts": 0}
    return result


def compare_offline_pilot(repo, *, authority_ref, submitted_commits, frozen,
                          manifest, contract, item_locators, historical_requests,
                          review_locators, offline_fixture=False):
    """Strict existing writer-proof + group acceptance + independent A/B/C gate.

    No synthetic mechanical result can prove external sources or approve parity.
    Historical source-year disagreement remains a visible quality issue.
    """
    plan = inspect_offline_pilot(
        repo, authority_ref=authority_ref, submitted_commits=submitted_commits,
        offline_fixture=offline_fixture)
    decision = _decision()
    require(frozen["trial_id"] == decision["trial_id"]
            and [x["sequence"] for x in frozen["groups"]] == list(SEQUENCES)
            and [x["group_sha256"] for x in frozen["groups"]] ==
            [x["group_sha256"] for x in decision["scope"]["groups"]]
            and [[g["appid"] for g in u["games"]] for u in frozen["groups"]] ==
            [x["appids"] for x in decision["scope"]["groups"]],
            "quality freeze reordered, replaced or resampled the original 18")
    # The canonical gate independently validates immutable historical writer
    # receipts, strict original three-game Research/Assembly V2 chain and the
    # independently frozen reviewer A/B and optional later C adjudication.
    comparison = quality_gate(
        repo, frozen=frozen, manifest=manifest, contract=contract,
        item_locators=item_locators, historical_requests=historical_requests,
        review_locators=review_locators)
    require(comparison["cohort"]["frozen_games"] == 18
            and comparison["cohort"]["frozen_groups"] == 6
            and len(comparison["per_game"]) == 18,
            "comparison silently dropped an original game/group")
    return {"plan": plan, "comparison": comparison, "semantic_execution": False,
            "quality_verified": False, "real_source_authenticity_verified": False,
            "approved_numeric_quality_thresholds": None,
            "group_atomic_acceptance_only": True, "writes": []}


if __name__ == "__main__":
    raise SystemExit("Disposable-Git offline API only; no live invocation or writes")

#!/usr/bin/env python3
"""Inactive, offline-only Assembly semantic handoff checks.

Pure planning/validation helpers. No CLI, web research, semantic execution,
Git writes, inbox scan, scheduler, retry, GitHub acceptance or canonical ingest.
Actual production activation requires a separate Director-approved integration.
"""
import copy
import json
import subprocess

from jsonschema import Draft202012Validator

from dossier_two_stage_async_buffer import (
    frozen_buffer, inactive_gate, provisional_assembly_work,
)
from dossier_two_stage_contract_guard import CONFIG, _privacy
from dossier_two_stage_staging import (
    exists, fail, file_at, first_parent_contains, strict_json,
)


def inactive_assembly_gate():
    """Do not confuse an implemented offline helper with production authority."""
    config = inactive_gate()
    interfaces = json.loads(
        (CONFIG / "dossier_two_stage_interfaces_contract.json").read_text("utf-8"))
    staging = json.loads(
        (CONFIG / "dossier_two_stage_staging_contract.json").read_text("utf-8"))
    if (config["active"] is not False
            or config["executable_in_production"] is not False
            or config["semantic_workers_implemented"] is not False
            or interfaces["active"] is not False
            or interfaces["authorized_for_semantic_execution"] is not False
            or interfaces["authorized_for_canonical_ingest"] is not False
            or staging["active"] is not False
            or staging["executable_in_production"] is not False):
        fail("Assembly offline-only non-activation guard failed")
    return config


def frozen_assembly_traversal(repo, *, marker_commit, buffer_path, submitted_commits):
    """Return an ordered independent decision for every frozen plan.

    submitted_commits is ONLY a read-only mapping of exact preauthorized plan
    paths to actual submitted single-parent Research Git commits (or None).
    This function never discovers a new game, waits for a GitHub receipt, opens
    a retry/lease, or treats a missing/invalid package as an attempted item.
    """
    inactive_assembly_gate()
    doc = frozen_buffer(repo, marker_commit=marker_commit, buffer_path=buffer_path,
                        phase="assembly")
    paths = [row["work_path"] for row in doc["items"]]
    if not isinstance(submitted_commits, dict) or set(submitted_commits) - set(paths):
        fail("worker supplied out-of-scope Research commits")
    result = []
    for path in paths:
        commit = submitted_commits.get(path)
        if commit is None:
            result.append({"work_path": path, "status": "research_not_submitted",
                           "attempt_consumed": False})
            continue
        try:
            work = provisional_assembly_work(
                repo, marker_commit=marker_commit, buffer_path=buffer_path,
                work_path=path, package_commit=commit)
            if not first_parent_contains(repo, commit, "HEAD"):
                fail("Research original submission is not in the candidate Git lineage")
            if exists(repo, "HEAD", work["output_path"]):
                result.append({"work_path": path, "status": "candidate_already_submitted",
                               "attempt_consumed": False, "output_path": work["output_path"]})
                continue
        except (ValueError, subprocess.CalledProcessError) as exc:
            # A mismatched/unavailable A is an item-local zero-attempt condition.
            result.append({"work_path": path, "status": "research_transport_invalid",
                           "attempt_consumed": False, "diagnostic": str(exc)[:240]})
            continue
        result.append({"work_path": path, "status": "ready", "attempt_consumed": False,
                       "work": work})
    return result


def _check_exact_source_first(package, operations):
    """Research package source/gap identities are frozen, not new work authority."""
    sources = {row["ref"] for row in package["sources"]}
    gaps = {row["gap_id"]: row for row in package["research_audit"]["unresolved_gaps"]}
    if len(sources) != len(package["sources"]) or len(gaps) != len(
            package["research_audit"]["unresolved_gaps"]):
        fail("duplicate original Research source/gap identity")
    seen = set()
    for op in operations:
        gap = gaps.get(op["gap_id"])
        if (gap is None or op["source_ref"] not in sources
                or op["source_ref"] not in gap["source_refs"]
                or op["missing_field_or_dimension"] != gap["field_or_dimension"]):
            fail("unsolicited or rebound Assembly gap/source")
        key = (op["gap_id"], op["source_ref"])
        if key in seen:
            fail("duplicated exact-source revisit")
        seen.add(key)
        revisit = op["exact_source_revisit"]
        if revisit["status"] == "fact_found" and not revisit["observed_fact_present"]:
            fail("claimed exact-source resolution without observed fact")
        if revisit["status"] != "fact_found" and revisit["observed_fact_present"]:
            fail("unavailable/absent source cannot claim observed fact")
        narrow = op["narrow_gap_lookup"]
        if narrow is not None:
            if revisit["status"] != "genuinely_absent":
                fail("narrow lookup without genuinely absent exact source")
            if (narrow["gap_id"] != op["gap_id"]
                    or narrow["missing_field_or_dimension"] != gap["field_or_dimension"]
                    or narrow["appid"] != package["assignment"]["appid"]
                    or narrow["original_work_title"] != package["assignment"]["title"]
                    or narrow["original_work_release_year"] !=
                    package["identity"]["original_work_release_year"]):
                fail("narrow lookup changed frozen Research identity or named gap")
        _privacy(op)  # Reject author identifiers, personal references and raw quotes.


def offline_assembly_candidate(repo, *, marker_commit, buffer_path, work_path,
                               research_package_commit, outcome, payload,
                               supplemental_operations):
    """Return a schema-valid create-only proposal, NOT a GitHub-accepted dossier.

    The caller supplies offline test semantic content; this function does not
    generate content or run a live Assembly worker. Only an externally authorized
    later data-plane worker may ever use this interface in production.
    """
    inactive_assembly_gate()
    work = provisional_assembly_work(
        repo, marker_commit=marker_commit, buffer_path=buffer_path,
        work_path=work_path, package_commit=research_package_commit)
    if not first_parent_contains(repo, research_package_commit, "HEAD"):
        fail("Research original submission is not in the candidate Git lineage")
    if exists(repo, "HEAD", work["output_path"]):
        fail("create-only Assembly candidate already exists; no rename or overwrite")
    package = strict_json(file_at(
        repo, research_package_commit, work["research_transport"]["research_package_path"]))
    doc = {
        "schema": "DOSSIER-ASYNC-ASSEMBLY-RESULT-V1",
        "schema_version": 1,
        **{key: copy.deepcopy(work[key]) for key in (
            "assembly_assignment_id", "original_research_assignment",
            "research_transport", "assembly_marker_anchor_commit",
            "assembly_marker_nonce", "assembly_contract_sha256",
            "assembly_prompt_sha256", "canonical_dossier_target", "output_path")},
        "outcome": outcome,
        "payload": copy.deepcopy(payload),
        "supplemental_operations": copy.deepcopy(supplemental_operations),
        "staged_only": True,
        "canonical_acceptance": False,
    }
    schema = json.loads((CONFIG / "dossier_async_assembly_result_v1.schema.json").read_text("utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(doc))
    if errors:
        fail("Assembly candidate schema invalid: " + errors[0].message)
    if payload["status"] != outcome:
        fail("Assembly outcome differs from typed payload status")
    if outcome == "assembled_candidate_ready":
        dossier = payload["dossier"]
        if (dossier["appid"] != work["original_research_assignment"]["appid"]
                or dossier["title"] != work["original_research_assignment"]["title"]):
            fail("assembled target identity not frozen Research assignment")
    _check_exact_source_first(package, supplemental_operations)
    return work["output_path"], doc

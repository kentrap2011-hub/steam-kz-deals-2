#!/usr/bin/env python3
"""Read-only, fail-closed authority + strict Research transport for ONE shadow trial.

No issuer, semantic runner, Git writer, inbox scanner, retry/queue owner or
production flag. All Git authorities must already exist from the GitHub-owned
trial preparation; the developer/operator cannot mint them here.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from dossier_shadow_real_baseline_audit import (
    AUDIT, MANIFEST, original_plan, writer_receipts, show, blob,
)
from dossier_two_stage_contract_guard import canonical_sha256, validate_research
from dossier_two_stage_staging import (
    git, require_only_new, first_parent_contains, validate_physical_sources,
    strict_json,
)
from taste_steam_review_dossier_strict import validate_dossier_strict

TRIAL = "dossier-shadow-calibration-20261011-6x3"
PREFIX = "reviews/dossier_shadow_offline/trials/" + TRIAL
DECISION = "reviews/dossier_shadow_offline/dossier_shadow_calibration_20261011_6x3_director_decision_v1.json"
CONTRACT = "config/dossier_shadow_research_trial_contract_v1.json"
PROMPT = "config/dossier_shadow_research_trial_semantic_prompt.md"
RESEARCH_SCHEMA = "config/dossier_research_package_v1.schema.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
NONCE = re.compile(r"^[0-9a-f]{32}$")
ITEM_KEYS = {"group_sequence", "item_index", "appid", "assignment",
             "descriptor_blob_sha", "old_cache_path", "old_cache_blob_sha",
             "old_cache_sha256", "old_year", "old_writer_commit",
             "old_receipt_line_sha256"}
MAIN_KEYS = {"schema", "version", "trial_id", "decision_blob_sha", "source_head",
             "source_work_blob_sha", "source_audit_blob_sha", "prompt_blob_sha",
             "research_schema_blob_sha", "trial_contract_blob_sha",
             "groups", "items", "research_buffer_id"}
RESEARCH_FIELDS = {"assignment_id", "snapshot_id", "group_sequence", "group_sha256",
                   "prepared_required_sha256", "group_plan_sha256", "items_sha256",
                   "item_index", "appid", "title", "scope_source",
                   "source_queue_sha256", "research_contract_sha256",
                   "web_evidence_contract_binding"}


def require(ok, reason):
    if not ok:
        raise ValueError("shadow Research BLOCKED: " + reason)


def json_git(repo, commit, path):
    return strict_json(show(repo, commit, path))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def exact_marker(repo, marker_commit):
    require(isinstance(marker_commit, str) and HEX40.fullmatch(marker_commit),
            "marker Git commit required")
    parents = git(repo, "rev-list", "--parents", "-n", "1", marker_commit).stdout.decode().split()
    require(len(parents) == 2 and parents[0] == marker_commit,
            "marker must have exactly one actual Git parent")
    parent = parents[1]
    delta = git(repo, "diff-tree", "--no-commit-id", "--name-status", "-r",
                marker_commit).stdout.decode().splitlines()
    require(len(delta) == 1 and delta[0].startswith("A\t"), "marker-only create-only commit required")
    path = delta[0].split("\t", 1)[1]
    match = re.fullmatch(re.escape(PREFIX) + r"/run_starts/([0-9a-f]{32})\.json", path)
    require(match is not None, "non-shadow or malformed marker path")
    nonce = match.group(1)
    require(json_git(repo, marker_commit, path) == {
        "schema": "DOSSIER-SHADOW-RESEARCH-RUN-START-V1",
        "schema_version": 1, "trial_id": TRIAL, "nonce": nonce,
    }, "marker contents/binding changed")
    require(not git(repo, "cat-file", "-e", parent + ":" + path,
                    required=False).returncode == 0, "marker already existed")
    return parent, nonce


def _three_by_six(decision, groups):
    requested = decision["scope"]["groups"]
    require(decision.get("trial_id") == TRIAL
            and decision["scope"]["group_order"] == [3, 8, 13, 15, 18, 20]
            and len(requested) == 6 and decision["scope"]["total_games"] == 18,
            "decision does not bind approved six original groups")
    seen = set()
    for d in requested:
        seq = d["sequence"]
        require(seq in [3, 8, 13, 15, 18, 20] and seq not in seen,
                "duplicate or foreign approved group")
        seen.add(seq)
        group = groups[seq - 1]
        require(group["sequence"] == seq and group["group_sha256"] == d["group_sha256"]
                and group["appids"] == d["appids"] and len(group["items"]) == 3,
                "original GitHub group SHA or 3-game membership mismatch")
    require([d["sequence"] for d in requested] == [3, 8, 13, 15, 18, 20],
            "approved group ordering drift")
    return requested


def frozen_trial(repo, *, marker_commit, buffer_path):
    """Only GitHub-prepared immutable manifest at ACTUAL marker parent.

    Public Repo note: only metadata/hashes here, never raw feedback/identifiers
    of review authors; actual Research results are separate, safety-checked.
    """
    parent, nonce = exact_marker(repo, marker_commit)
    require(buffer_path == PREFIX + "/research_buffer.json",
            "not the single versioned original sandbox Research buffer")
    contract = json_git(repo, parent, CONTRACT)
    require(contract["schema"] == "DOSSIER-SHADOW-RESEARCH-TRIAL-CONTRACT-V1"
            and contract["production_execution"] is False
            and contract["one_stage_owner_unchanged"] is True
            and type(contract.get("standalone_sandbox_semantics_approved")) is bool
            and type(contract.get("reviewer_roles_finalized")) is bool,
            "trial contract fails closed; no implicit execution")
    for path in ("config/dossier_two_stage_interfaces_contract.json",
                 "config/dossier_two_stage_staging_contract.json",
                 "config/dossier_two_stage_async_buffer_contract.json"):
        inactive = json_git(repo, parent, path)
        require(inactive.get("active") is False
                and inactive.get("executable_in_production") is not True
                and inactive.get("authoritative") is False
                and inactive.get("authorized_for_semantic_execution") is not True,
                "canonical inactive two-stage gate unexpectedly changed")
    decision = json_git(repo, parent, DECISION)
    require(decision["operator_authority"]["github_prepared_snapshot_marker_and_transport"] is False
            and decision["allowed_production_writes"] == [],
            "frozen decision must not have been reinterpreted as a marker")
    frozen = json_git(repo, parent, buffer_path)
    require(type(frozen) is dict and set(frozen) == MAIN_KEYS
            and frozen["schema"] == "DOSSIER-SHADOW-RESEARCH-BUFFER-V1"
            and frozen["version"] == 1 and frozen["trial_id"] == TRIAL,
            "missing or invalid GitHub-prepared sandbox buffer")
    pinned = decision["historical_reference"]
    require(frozen["decision_blob_sha"] == blob(repo, parent, DECISION)
            and frozen["source_head"] == pinned["head"]
            and frozen["source_work_blob_sha"] == pinned["work_blob"]
            and frozen["source_audit_blob_sha"] == pinned["audit_blob"]
            and blob(repo, pinned["head"], MANIFEST) == pinned["work_blob"]
            and blob(repo, pinned["head"], AUDIT) == pinned["audit_blob"],
            "historical baseline commit/blob or decision pin mismatch")
    for key, path in [("prompt_blob_sha", PROMPT),
                      ("research_schema_blob_sha", RESEARCH_SCHEMA),
                      ("trial_contract_blob_sha", CONTRACT)]:
        require(frozen[key] == blob(repo, parent, path),
                "immutable code/schema/prompt Git blob pin mismatch: " + key)
    items = frozen["items"]
    require(type(items) is list and len(items) == 18 and
            frozen["research_buffer_id"] == canonical_sha256(
                {"trial_id": TRIAL, "groups": frozen["groups"], "items": items}),
            "buffer self-hash/cardinality changed")
    old = json_git(repo, pinned["head"], MANIFEST)
    c = json_git(repo, pinned["head"], "config/taste_steam_review_dossier_contract.json")
    groups = old["submission_group_plan"]["groups"]
    _three_by_six(decision, groups)
    require(frozen["groups"] == decision["scope"]["groups"],
            "shadow cannot modify or reorder the Director scope")
    accepted = {group["sequence"] for group, _ in original_plan(old)}
    require(set(decision["scope"]["group_order"]).issubset(accepted),
            "baseline group not accepted at historical frozen head")
    receipts = writer_receipts(repo, pinned["head"], old["snapshot_id"])
    schema_hash = canonical_sha256(json_git(repo, parent, RESEARCH_SCHEMA))
    expected_order = []
    for group in decision["scope"]["groups"]:
        original = groups[group["sequence"] - 1]
        descriptor = ("data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                      + old["snapshot_id"] + f"/g{group['sequence']:06d}.json")
        for ix, entry in enumerate(original["items"]):
            expected_order.append((group["sequence"], ix, str(entry["appid"])))
    require([(x.get("group_sequence"), x.get("item_index"), x.get("appid"))
             for x in items] == expected_order, "18-item original order changed")
    seen_aids = set()
    for entry in items:
        require(type(entry) is dict and set(entry) == ITEM_KEYS,
                "unexpected Research item metadata shape")
        seq, idx, appid = entry["group_sequence"], entry["item_index"], entry["appid"]
        group = groups[seq - 1]
        original = group["items"][idx]
        prepared = entry["assignment"]
        require(type(prepared) is dict and set(prepared) == RESEARCH_FIELDS,
                "Research assignment must have only exact original fields")
        source = {**prepared, "research_marker_anchor_commit": marker_commit,
                  "research_marker_nonce": nonce}
        expected = {
            "snapshot_id": old["snapshot_id"], "group_sequence": seq,
            "group_sha256": group["group_sha256"],
            "prepared_required_sha256": group["prepared_required_sha256"],
            "group_plan_sha256": old["submission_group_plan"]["group_plan_sha256"],
            "items_sha256": group["items_sha256"], "item_index": idx,
            "appid": appid, "title": original["title"],
            "scope_source": group["scope_source"],
            "source_queue_sha256": group["source_queue_sha256"],
            "research_contract_sha256": schema_hash,
            "web_evidence_contract_binding": old["web_evidence_contract_binding"],
        }
        require(all(prepared.get(k) == v for k, v in expected.items())
                and re.fullmatch("[a-z0-9][a-z0-9._-]{7,127}", str(prepared["assignment_id"]))
                and prepared["assignment_id"] not in seen_aids,
                "Research assignment not the original immutable group item")
        seen_aids.add(prepared["assignment_id"])
        descriptor = ("data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                      + old["snapshot_id"] + f"/g{seq:06d}.json")
        require(entry["descriptor_blob_sha"] == blob(repo, pinned["head"], descriptor),
                "frozen original descriptor Git blob mismatch")
        require(seq in receipts, "missing original historical writer receipt")
        writer, _, audit_line, _ = receipts[seq]
        cache_path = original["dossier_path"]
        require(entry["old_writer_commit"] == writer
                and entry["old_receipt_line_sha256"] == sha(audit_line)
                and entry["old_cache_path"] == cache_path
                and entry["old_cache_blob_sha"] == blob(repo, writer, cache_path)
                and entry["old_cache_blob_sha"] == blob(repo, pinned["head"], cache_path),
                "strict writer baseline receipt or original cache bytes changed")
        raw = show(repo, writer, cache_path)
        dossier = strict_json(raw)
        require(entry["old_cache_sha256"] == canonical_sha256(dossier)
                and entry["old_year"] == dossier["game_identity"]["release_year"],
                "old baseline original-year/cache hash mismatch")
        validate_dossier_strict(dossier, c, expected_appid=appid,
                                require_fresh_at_acceptance=False)
        # This confirms OLD recorded claim, not truth of the original release year.
        require(source["appid"] == appid and source["title"] == original["title"],
                "identity title/source mismatched")
    ready = (contract["standalone_sandbox_semantics_approved"] is True
             and contract["reviewer_roles_finalized"] is True)
    return {"status": ("sandbox_research_invocation_ready" if ready else "blocked"),
            "sandbox_semantics_authorized": ready,
            "marker_commit": marker_commit, "marker_parent": parent,
            "nonce": nonce, "buffer_path": buffer_path,
            "buffer_blob_sha": blob(repo, parent, buffer_path),
            "source_head": pinned["head"], "items": items,
            "canonical_acceptance": False, "research_calls": 0}


def sandbox_output_path(item):
    a = item["assignment"]
    return (PREFIX + "/research/g" + f"{item['group_sequence']:06d}" + "/"
            + item["appid"] + "--" + a["assignment_id"] + ".json")


def validate_candidate(item, package, *, marker_commit, nonce):
    """Reuse exact production-proposed strict Research schema/privacy validators."""
    expected = {**item["assignment"], "research_marker_anchor_commit": marker_commit,
                "research_marker_nonce": nonce}
    validate_research(package, expected_assignment=expected)
    validate_physical_sources(package)
    original = package["identity"]["original_work_release_year"]
    old = item["old_year"]
    year_status = ("identity_unresolved" if original is None
                   else "legacy_original_year_conflict_needs_comparison_adjudication"
                   if original != old else "legacy_year_claim_matches_unverified")
    return {"status": "structural_research_valid_not_accepted",
            "year_comparison": year_status, "old_year_claim": old,
            "research_original_year": original, "canonical_acceptance": False}


def inspect_transport(repo, *, trial, item, result_commit, expected_raw=None):
    """Original single-added sandbox path only; no writer, no live ingest."""
    path = sandbox_output_path(item)
    require(path.startswith(PREFIX + "/research/") and "/../" not in path,
            "transport escapes isolated trial")
    prior = require_only_new(repo, result_commit, [path])
    require(first_parent_contains(repo, trial["marker_commit"], prior),
            "transport not under exact sandbox marker-first-parent history")
    raw = show(repo, result_commit, path)
    require(blob(repo, result_commit, path) == hashlib.sha1(
        b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest(),
        "raw Git object digest changed")
    if expected_raw is not None:
        require(raw == expected_raw, "create-only collision with different raw bytes")
    head = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
    require(first_parent_contains(repo, result_commit, head)
            and blob(repo, result_commit, path) == blob(repo, head, path),
            "submitted original research path was overwritten")
    pkg = strict_json(raw)
    result = validate_candidate(item, pkg, marker_commit=trial["marker_commit"],
                                nonce=trial["nonce"])
    return {**result, "status": "submitted_unaccepted_shadow_only",
            "result_commit": result_commit, "path": path,
            "raw_sha256": sha(raw), "git_blob_sha": blob(repo, result_commit, path),
            "canonical_sha256": canonical_sha256(pkg)}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--marker-commit", required=True)
    cli.add_argument("--buffer-path", required=True)
    args = cli.parse_args()
    # Read-only only: a missing marker MUST return blocked, never create one.
    trial = frozen_trial(Path.cwd(), marker_commit=args.marker_commit,
                         buffer_path=args.buffer_path)
    print(json.dumps({k: v for k, v in trial.items() if k != "items"},
                     ensure_ascii=False, sort_keys=True, indent=2))
    print("sandbox_research_invocation_ready=" +
          ("ready" if trial["sandbox_semantics_authorized"] else "blocked"))


if __name__ == "__main__":
    main()

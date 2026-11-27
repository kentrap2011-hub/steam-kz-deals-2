#!/usr/bin/env python3
"""Read-only, fail-closed validator for the one-time six-game old-format Dossier control.

Not a semantic producer or a canonical writer. GitHub PR checks may validate
a completed separate sandbox branch but never ingest into production.
"""
import argparse
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from taste_steam_review_dossier_strict import validate_dossiers_against_expected_items
from taste_steam_review_dossier import parse_utc

ROOT = Path(__file__).resolve().parents[1]
CONFIG_REL = "config/dossier_old6_fresh_strict_control_v1.json"
CONFIG = ROOT / CONFIG_REL
TRIAL = "dossier-old6-20261127-exact-six-01"
RESULT_ROOT = "reviews/dossier_old6_controls/" + TRIAL
GROUPS = (
    (("1000010", "Crown Trick"), ("102600", "Orcs Must Die!"),
     ("1029690", "Sniper Elite 5")),
    (("49520", "Borderlands 2"), ("499180", "Braid, Anniversary Edition"),
     ("501590", "Bulletstorm: Full Clip Edition")),
)
SCOPED_SHA = "665f5d0202859a6bac20566671f10158538e4764"
SOURCE_SNAPSHOT = "25c227d782188699f56b5702b3f0cfa63b101d890f09620b7b59893fab93c1af"


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def config():
    doc = json.loads(CONFIG.read_text(encoding="utf-8"))
    _require(doc.get("schema") == "DOSSIER-OLD6-FRESH-STRICT-CONTROL-V1"
             and type(doc.get("schema_version")) is int and doc["schema_version"] == 1,
             "wrong trial schema")
    _require(doc.get("trial_id") == TRIAL and
             doc.get("mode") == "one_shot_nonproduction_strict_V2_control",
             "wrong trial or mode")
    _require(doc.get("status") == "source_prepared_not_activated",
             "unexpected activation-state mutation")
    _require(doc.get("source_repository") == "kentrap2011-hub/steam-kz-deals-2"
             and doc.get("source_main_sha") == SCOPED_SHA
             and doc.get("source_snapshot_id") == SOURCE_SNAPSHOT,
             "frozen source authority changed")
    _require(doc.get("schema_to_produce") == "TASTE-STEAM-REVIEW-DOSSIER-V2"
             and doc.get("ttl_days") == 20
             and doc.get("sandbox_result_root") == RESULT_ROOT,
             "strict output contract changed")
    _require(doc.get("strict_validator") ==
             "scripts/taste_steam_review_dossier_strict.py::validate_dossiers_against_expected_items",
             "strict validator changed")
    _require(doc.get("original_worker_prompt") ==
             "config/taste_steam_review_dossier_worker_prompt.md"
             and doc.get("source_evidence_contract") ==
             "config/taste_steam_review_dossier_web_evidence_contract.json",
             "legacy semantic/evidence contracts changed")
    _require(doc.get("earliest_generated_at_utc") == "2026-11-27T00:00:00Z",
             "minimum freshness changed")
    for flag in ("minimum_fresh_research",):
        _require(doc.get(flag) is True, flag + " must remain enabled")
    for flag in ("reuse_prior_strict_cache", "reuse_lean_or_notes_v2_research",
                 "copy_prior_dossier_text", "canonical_cache_write_allowed",
                 "deep_or_production_allowed", "recurring_or_background_execution_allowed",
                 "semantic_launch_authorized_by_source_pr_alone"):
        _require(doc.get(flag) is False, flag + " must remain disabled")
    _require(doc.get("compare_to_lean_acceptance_commit") ==
             "372efa1e7e1f95905a3d16dd95f531f12bed2d9c",
             "comparison anchor changed")
    groups = doc.get("work_groups")
    _require(isinstance(groups, list) and len(groups) == 2,
             "expected two frozen three-game groups")
    for group, expected, sequence in zip(groups, GROUPS, (1, 70)):
        _require(group.get("group_sequence") == sequence, "wrong historical group identity")
        _require([(i.get("appid"), i.get("title")) for i in group.get("items", [])]
                 == list(expected), "wrong exact group items, order or edition")
    _require(doc.get("acceptance_condition") ==
             "six_new_full_strict_json_files_plus_git_one_add_provenance_plus_exact_PR_HEAD_CI_plus_explicit_semantic_quality_review",
             "acceptance gate changed")
    return doc


def _git(*args):
    p = subprocess.run(["git", "-C", str(ROOT), *args], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.stdout.strip()


def _one_add_commit(path):
    hits = [s for s in _git("log", "--format=%H", "--diff-filter=A", "--", path).splitlines()
            if s.strip()]
    _require(len(hits) == 1, "expected exactly one Git add for " + path)
    commit = hits[0]
    parent = _git("rev-parse", commit + "^")
    diff = _git("diff-tree", "--no-commit-id", "--name-status", "-r", commit).splitlines()
    _require(diff == ["A\t" + path], "a publication commit must add exactly one path: " + path)
    return commit, parent


def validate_outputs():
    doc = config()
    base = ROOT / RESULT_ROOT
    marker_rel = RESULT_ROOT + "/run_start.json"
    marker_path = ROOT / marker_rel
    _require(marker_path.is_file(), "missing create-only run-start marker")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    _require(set(marker) == {"schema", "trial_id", "source_commit"} and
             marker["schema"] == "DOSSIER-OLD6-RUN-START-V1" and
             marker["trial_id"] == TRIAL, "invalid run-start marker")
    marker_commit, source_commit = _one_add_commit(marker_rel)
    _require(marker["source_commit"] == source_commit,
             "marker source_commit is not its actual Git parent")
    _require(_git("show", source_commit + ":" + CONFIG_REL) ==
             CONFIG.read_text(encoding="utf-8").strip(),
             "marker parent did not freeze the exact source trial")
    _git("merge-base", "--is-ancestor", source_commit, "origin/main")
    marker_date = datetime.fromisoformat(_git("show", "-s", "--format=%cI", marker_commit))
    valid_paths = {marker_rel}
    dossiers = []
    items = []
    for group in doc["work_groups"]:
        for item in group["items"]:
            appid = item["appid"]
            path = RESULT_ROOT + "/App_" + appid + ".json"
            valid_paths.add(path)
            dossier_path = ROOT / path
            _require(dossier_path.is_file(), "missing strict candidate: " + path)
            create_commit, _ = _one_add_commit(path)
            _git("merge-base", "--is-ancestor", marker_commit, create_commit)
            dossier = json.loads(dossier_path.read_text(encoding="utf-8"))
            _require(dossier.get("appid") == appid and dossier.get("title") == item["title"],
                     "candidate game identity/edition mismatch: " + appid)
            generated = parse_utc(dossier.get("generated_at_utc"))
            _require(generated >= parse_utc(doc["earliest_generated_at_utc"])
                     and generated >= marker_date - timedelta(minutes=5),
                     "candidate predates this independent run: " + appid)
            dossiers.append(dossier)
            items.append(item)
    existing = {str(p.relative_to(ROOT)).replace("\\", "/")
                for p in base.rglob("*") if p.is_file()}
    _require(existing == valid_paths, "unexpected or missing files inside isolated trial")
    contract = json.loads((ROOT / "config/taste_steam_review_dossier_contract.json")
                          .read_text(encoding="utf-8"))
    validate_dossiers_against_expected_items(
        dossiers, items, contract, expected_ttl_days=doc["ttl_days"],
        now=datetime.now(timezone.utc))
    print("STRICT_OLD6_CANDIDATES_VALID_6_OF_6 / nonproduction only / quality review required")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-config", action="store_true")
    parser.add_argument("--check-outputs", action="store_true")
    args = parser.parse_args()
    _require(args.check_config != args.check_outputs,
             "choose --check-config or --check-outputs")
    if args.check_config:
        config()
        print("EXACT_OLD6_SOURCE_CONFIG_VALID / no semantic work launched")
    else:
        validate_outputs()


if __name__ == "__main__":
    main()

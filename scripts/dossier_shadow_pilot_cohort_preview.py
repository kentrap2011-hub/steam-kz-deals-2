#!/usr/bin/env python3
"""INERT read-only cohort preview from the PR #201 pinned, strictly proved frame.

Never a semantic-worker, real-source auditor, authorization, queue, writer,
quality evaluator or production entry point. Only Git metadata/identity read.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

PIN = "95a4bf4990a60082ecb3302da5bc7f23b618d93e"
WORK_BLOB = "ef40fc186aabc79dfd24c72864dbe43817a56039"
AUDIT_BLOB = "8dbf4437d7ba439942f58a6f36d89d6a7ddeec7b"
ATTESTATION_BLOB = "d10041652593024c9fcf7772580d0a8ec9c5f12d"
ATTESTATION = "reviews/worker_reports/dossier-shadow-real-baseline-eligibility-audit-01.md"
WORK = "data/production/pre_ai/taste_steam_review_dossier_work.json"
AUDIT = "data/audit/taste_steam_review_dossier_frozen_invocations.jsonl"
SEED = "dossier-shadow-6x3-calibration-proposal-v1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
# A metadata-only group row: no review excerpts, author identities or URLs.
UNKNOWN_CATEGORIES = (
    "original_vs_storefront_year_mismatch",
    "independently_confirmed_original_remaster_dlc_identity",
    "russian_multilingual_player_review_evidence",
    "recent_older_unknown_review_publication_dates",
    "independent_player_source_parent_diversity",
    "negative_or_mixed_material_findings",
    "technical_localization_regional_risks",
    "source_gaps_revisits_and_exhaustion",
)


def git(repo, *args):
    p = subprocess.run(
        ["git", "-C", str(repo), *args], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if p.returncode:
        raise ValueError("PINNED_GIT_READ_UNAVAILABLE: " + args[0])
    return p.stdout


def git_object(repo, ref, path):
    if not HEX40.fullmatch(ref) and not re.fullmatch(r"[A-Za-z0-9_./-]+", ref):
        raise ValueError("INVALID_REF")
    if (not path or path.startswith("/") or ".." in path.split("/")
            or "\\" in path):
        raise ValueError("UNSAFE_PATH")
    return git(repo, "show", ref + ":" + path)


def blob(repo, ref, path):
    return git(repo, "rev-parse", ref + ":" + path).decode().strip()


def attested_rows(text):
    """Read only exact report-table rows; reject incomplete or altered evidence."""
    rows = {}
    for line in text.splitlines():
        columns = [p.strip() for p in line.strip().strip("|").split("|")]
        if (len(columns) != 9 or not columns[0].isdigit()
                or columns[2:4] != ["accepted", "yes"]):
            continue
        seq = int(columns[0])
        ids = columns[1].replace(" ", "").split(",")
        commit_cell, action_cell = columns[4:6]
        if ("/commit/" not in commit_cell or "/actions/runs/" not in action_cell
                or "github.com/" not in commit_cell
                or "github.com/" not in action_cell
                or not columns[6].startswith("pass")
                or not columns[7].startswith("eligible")
                or columns[8] != "`NONE`"):
            raise ValueError("ATTESTED_STRICT_STATUS_OR_PROVENANCE_MISSING")
        writer = commit_cell.split("/commit/", 1)[1].rstrip(")")
        run = action_cell.split("/actions/runs/", 1)[1].rstrip(")")
        if (not HEX40.fullmatch(writer) or not run.isdigit()
                or not action_cell.startswith("[" + run + "](")
                or seq in rows or len(ids) != 3
                or len(set(ids)) != 3
                or not all(x.isdigit() for x in ids)):
            raise ValueError("DUPLICATE_OR_MALFORMED_ATTESTED_GROUP")
        rows[seq] = {"appids": ids, "writer_commit": writer,
                     "verified_actions_run": run}
    if len(rows) != 20:
        raise ValueError("ATTESTATION_MUST_LIST_EXACTLY_20_STRICT_GROUPS")
    return rows


def validate_frame(groups):
    """Validate full, ordered, indivisible 20x3 frame before *any* sampling."""
    if len(groups) != 20:
        raise ValueError("FRAME_NOT_COMPLETE_20_GROUPS")
    sequences, appids = set(), set()
    last_seq = 0
    for g in groups:
        seq = g.get("sequence")
        games = g.get("games")
        if (type(seq) is not int or seq <= last_seq or seq in sequences
                or not HEX64.fullmatch(g.get("group_sha256", ""))
                or not HEX40.fullmatch(g.get("writer_commit", ""))
                or not re.fullmatch(r"[0-9]+", str(g.get("verified_actions_run", "")))
                or type(games) is not list or len(games) != 3):
            raise ValueError("FROZEN_GROUP_ORDER_OR_RECEIPT_INVALID")
        sequences.add(seq)
        last_seq = seq
        for game in games:
            appid = game.get("appid")
            if (type(appid) is not str or not re.fullmatch(r"[1-9][0-9]*", appid)
                    or appid in appids or type(game.get("work_title")) is not str
                    or not game["work_title"] or type(game.get("original_work_year_binding")) is not int
                    or not 1970 <= game["original_work_year_binding"] <= 2100
                    or not HEX40.fullmatch(game.get("baseline_git_blob_sha", ""))):
                raise ValueError("IMMUTABLE_GAME_IDENTITY_INVALID_OR_DUPLICATE")
            appids.add(appid)
    if len(appids) != 60:
        raise ValueError("FRAME_MUST_HAVE_60_DISTINCT_APPIDS")
    return groups


def choose_cohort(groups, snapshot, seed=SEED):
    """3/6 older-year-binding and 3/14 other; deterministic, NOT representative."""
    validate_frame(groups)
    strata = {"has_pre_2015_work_year_binding": [], "no_pre_2015_work_year_binding": []}
    for row in groups:
        key = ("has_pre_2015_work_year_binding"
               if any(x["original_work_year_binding"] < 2015 for x in row["games"])
               else "no_pre_2015_work_year_binding")
        row["year_binding_stratum"] = key
        material = "|".join((
            seed, PIN, WORK_BLOB, snapshot, str(row["sequence"]), row["group_sha256"]
        ))
        row["selection_sha256"] = hashlib.sha256(material.encode("utf-8")).hexdigest()
        strata[key].append(row)
    if len(strata["has_pre_2015_work_year_binding"]) != 6 or len(
            strata["no_pre_2015_work_year_binding"]) != 14:
        raise ValueError("PINNED_YEAR_BINDING_STRATA_DIFFER_FROM_AUDIT_6_14")
    selected = set()
    for entries in strata.values():
        chosen = sorted(entries, key=lambda x: (x["selection_sha256"], x["sequence"]))[:3]
        selected.update(x["sequence"] for x in chosen)
    if len(selected) != 6:
        raise ValueError("SELECTION_NOT_SIX_GROUPS")
    for row in groups:
        row["provisionally_selected"] = row["sequence"] in selected
    return [row for row in groups if row["provisionally_selected"]], strata


def source_differences(repo, compare_ref):
    """Pin always wins; surface moving-main differences without rebinding."""
    if (".." in compare_ref or compare_ref.startswith("/")
            or not re.fullmatch(r"[A-Za-z0-9_./-]+", compare_ref)):
        raise ValueError("INVALID_COMPARE_REF")
    try:
        other = git(repo, "rev-parse", "--verify", compare_ref + "^{commit}").decode().strip()
        work = blob(repo, other, WORK)
        audit = blob(repo, other, AUDIT)
        return {
            "compare_ref": compare_ref, "compare_head": other,
            "head_moved_from_pin": other != PIN,
            "work_blob_differs": work != WORK_BLOB,
            "audit_blob_differs": audit != AUDIT_BLOB,
            "comparison_status": "known",
        }
    except ValueError:
        return {"compare_ref": compare_ref, "comparison_status": "unknown",
                "reason": "COMPARE_REF_OR_FILES_UNAVAILABLE"}


def frozen_frame(repo):
    """Consult accepted #201 attestation; do not rerun proven strict verifier."""
    if (blob(repo, PIN, WORK) != WORK_BLOB
            or blob(repo, PIN, AUDIT) != AUDIT_BLOB
            or blob(repo, "HEAD", ATTESTATION) != ATTESTATION_BLOB):
        raise ValueError("PINNED_MANIFEST_AUDIT_OR_ATTESTATION_CHANGED")
    attest = git_object(repo, "HEAD", ATTESTATION).decode("utf-8")
    if PIN not in attest or "20/20" not in attest:
        raise ValueError("ATTESTATION_SOURCE_OR_RESULT_MISMATCH")
    receipt_rows = attested_rows(attest)
    manifest = json.loads(git_object(repo, PIN, WORK))
    if (manifest.get("snapshot_id") !=
            "4d7be57c9a1a90482d948270ab034c49eca3dd84102d28fc67b6fbc1d33f8239"
            or manifest.get("prepared_required_sha256") !=
            "824e3ca4afb741dfac707284cb82e5eb594d1180d6c7a84bc63cb827a6f4e4e8"
            or manifest["submission_group_plan"]["group_count"] != 76):
        raise ValueError("PINNED_SNAPSHOT_GROUP_PLAN_MISMATCH")
    plan = manifest["submission_group_plan"]["groups"]
    progress = manifest["group_progress"]["groups"]
    if len(plan) != 76 or len(progress) != 76:
        raise ValueError("ORIGINAL_PLAN_INCOMPLETE")
    groups = []
    for g, state in zip(plan, progress):
        seq = g["sequence"]
        if (state["sequence"] != seq or state["group_sha256"] != g["group_sha256"]
                or g["appids"] != [str(i["appid"]) for i in g["items"]]
                or len(g["items"]) != 3):
            raise ValueError("ORIGINAL_GROUP_BINDING_MISMATCH")
        if state["state"] != "accepted":
            continue
        receipt = receipt_rows.get(seq)
        if receipt is None or receipt["appids"] != g["appids"]:
            raise ValueError("MISSING_EXACT_HISTORICAL_WRITER_ATTESTATION")
        games = []
        writer = receipt["writer_commit"]
        for it in g["items"]:
            path = it["dossier_path"]
            appid = str(it["appid"])
            if path != "data/cache/taste_steam_review_dossiers/App_" + appid + ".json":
                raise ValueError("WRONG_CANONICAL_BASELINE_PATH")
            cache_blob = blob(repo, writer, path)
            if blob(repo, PIN, path) != cache_blob:
                raise ValueError("HISTORICAL_BASELINE_BYTES_CHANGED")
            baseline = json.loads(git_object(repo, writer, path))
            ident = baseline["game_identity"]
            if (str(baseline["appid"]) != appid
                    or ident["work_title"] != it["title"]
                    or type(ident["release_year"]) is not int):
                raise ValueError("ORIGINAL_WORK_BINDING_MISMATCH")
            games.append({"appid": appid, "work_title": it["title"],
                          "original_work_year_binding": ident["release_year"],
                          "baseline_git_blob_sha": cache_blob})
        groups.append({"sequence": seq, "group_sha256": g["group_sha256"],
                       "writer_commit": writer,
                       "verified_actions_run": receipt["verified_actions_run"],
                       "games": games})
    validate_frame(groups)
    if set(receipt_rows) != {g["sequence"] for g in groups}:
        raise ValueError("ATTESTED_GROUP_SET_IS_NOT_COMPLETE")
    return manifest["snapshot_id"], groups


def build_preview(repo, compare_ref="origin/main"):
    snapshot, frame = frozen_frame(repo)
    chosen, strata = choose_cohort(frame, snapshot)
    gaps = {name: {"state": "not_measured", "evaluated_groups": 0,
                   "frame_groups": 20} for name in UNKNOWN_CATEGORIES}
    return {
        "schema": "DOSSIER-SHADOW-COHORT-PREVIEW-V1",
        "purpose": "user_decision_packet_only_inert",
        "source": {"target_head": PIN, "work_git_blob_sha": WORK_BLOB,
                   "audit_git_blob_sha": AUDIT_BLOB,
                   "accepted_pr201_report_blob_sha": ATTESTATION_BLOB,
                   "snapshot_id": snapshot, "strict_history_attestation": "PR_201_20_of_20"},
        "source_movement": source_differences(repo, compare_ref),
        "sampling": {"seed": SEED, "method": "sha256_seeded_3_per_year_binding_stratum",
                     "sampling_unit": "whole_original_three_game_group",
                     "original_sequence_order_preserved": True,
                     "stratum_counts": {name: len(v) for name, v in strata.items()},
                     "inclusion_fraction": {"has_pre_2015_work_year_binding": "3/6",
                                            "no_pre_2015_work_year_binding": "3/14"},
                     "nonrepresentative_older_binding_oversample": True,
                     "year_binding_is_not_independent_original_year_truth": True},
        "accounting": {"original_groups": 76, "pinned_accepted_and_eligible_groups": 20,
                       "predeclared_selected_groups": 6, "selected_appids": 18,
                       "nonselected_eligible_groups": 14, "pending_outside_frame": 56,
                       "eligible_excluded_for_integrity": 0,
                       "semantic_executions": 0, "quality_reviews": 0},
        "baseline_integrity_verified": True, "sample_proposed": True,
        "pilot_authorized": False, "semantic_quality_not_evaluated": True,
        "quality_verified": False, "canonical_readiness": False,
        "deep_readiness": False, "approval_status": "NOT_READY_FOR_APPROVAL",
        "approval_blockers": ["eight_pre_output_strata_unmeasured_all_20",
                              "external_original_work_year_and_product_identity_not_independently_verified",
                              "source_review_authenticity_and_source_safety_unverified",
                              "auditors_adjudicator_and_stop_thresholds_unapproved",
                              "user_has_not_approved_exact_cohort_or_semantic_owner_path"],
        "unmeasured_dimensions": gaps,
        "selected_groups_original_order": [g["sequence"] for g in chosen],
        "complete_frame_original_order": frame,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target-head", required=True)
    p.add_argument("--expected-work-blob", required=True)
    p.add_argument("--expected-audit-blob", required=True)
    p.add_argument("--compare-ref", default="origin/main")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if (args.target_head != PIN or args.expected_work_blob != WORK_BLOB
            or args.expected_audit_blob != AUDIT_BLOB):
        raise SystemExit("ONLY_PR201_STRICTLY_PROVEN_PIN_AUTHORIZED_FOR_PREVIEW")
    out = args.out.resolve()
    allowed = {Path(tempfile.gettempdir()).resolve()}
    if os.environ.get("RUNNER_TEMP"):
        allowed.add(Path(os.environ["RUNNER_TEMP"]).resolve())
    if not any(out != root and out.is_relative_to(root) for root in allowed):
        raise SystemExit("ONLY_OS_TEMP_METADATA_OUTPUT_ALLOWED")
    payload = build_preview(Path.cwd(), compare_ref=args.compare_ref)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
                   + "\n", encoding="utf-8")
    print(json.dumps({
        "approval_status": payload["approval_status"],
        "selected_groups": payload["selected_groups_original_order"],
        "selected_appids": 18, "frame_groups": 20,
        "source_movement": payload["source_movement"],
        "pilot_authorized": False, "semantic_execution": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

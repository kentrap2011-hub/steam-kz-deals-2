#!/usr/bin/env python3
"""Inactive Dossier shadow quality adjudication gate; offline Git evidence only.

No live CLI, web access, semantic worker, queue, cache, writer or readiness authority.
Synthetic tests prove enforcement, never real semantic accuracy or source truth.
"""
import hashlib
import json
import re
import subprocess
from collections import Counter

SCHEMA = "DOSSIER-SHADOW-QUALITY-REVIEW-GATE-V1"
DIMENSIONS = (
    "supported_claims", "source_authenticity", "source_independence",
    "negative_mixed_retention", "material_omissions", "unknown_gap_fidelity",
    "original_work_year", "storefront_date_distinction", "russian_language_quality",
    "identity_version", "privacy_safety", "technical_localization_risk",
    "confidence_calibration",
)
STATES = {"confirmed_no_issue", "confirmed_issue", "needs_review", "unknown"}
SEVERITIES = {"none", "minor", "material", "critical"}
REASONS = {
    "evidence_supported", "supported_correction", "not_applicable", "insufficient_evidence",
    "unsupported_claim", "source_not_verifiable", "not_independent", "source_identity_conflict",
    "negative_dropped", "material_omission", "unknown_overstated", "year_kind_conflict",
    "wrong_product", "translation_problem", "personal_data_leak", "technical_risk_omitted",
    "confidence_overstated", "reviewer_difference",
}
FAULTS = REASONS - {
    "evidence_supported", "supported_correction", "not_applicable", "insufficient_evidence",
    "reviewer_difference",
}
H40 = re.compile(r"^[0-9a-f]{40}$")
H64 = re.compile(r"^[0-9a-f]{64}$")
TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,110}$")


def guard(ok, reason):
    if not ok:
        raise ValueError("offline review gate: " + reason)


def _unique(values, label):
    guard(len(values) == len(set(values)), "duplicate " + label)


def _anchor_set(c):
    """Create allowed IDs from already strictly Git-validated documents only.

    This method is NOT an external source authenticity check; raw texts and
    personal records are never returned in the review gate output.
    """
    e = c["comparison_evidence"]
    anchors = set()
    for side, rows in (("old", e["one_stage_statements"]),
                       ("new", e["two_stage_statements"])):
        for idx, row in enumerate(rows):
            anchors.add(f"{side}:obs:{idx}")
            anchors.update(f"{side}:source:{x}" for x in row["source_ids"])
            anchors.update(f"{side}:feedback:{x}" for x in row["player_feedback_ids"])
    anchors.update(f"research:finding:{x['ref']}" for x in e["research_findings"])
    anchors.update(f"research:source:{x}" for x in c["sources"]["research"]["research_source_refs"])
    anchors.update(f"research:gap:{x['gap_id']}" for x in c["research"]["gaps"])
    guard(all(TOKEN.fullmatch(x) for x in anchors), "invalid immutable source anchor")
    return anchors


def _review(record, role, anchors, comparison, subject):
    guard(type(record) is dict and set(record) ==
          {"role", "subject", "dimensions", "negative_retention", "unknown_resolution"}
          and record["role"] == role and record["subject"] == subject,
          "missing independent reviewer/unsafe fields or wrong game subject")
    dimensions = record["dimensions"]
    guard(type(dimensions) is dict and set(dimensions) == set(DIMENSIONS),
          "incomplete quality dimensions")
    for name, finding in dimensions.items():
        guard(type(finding) is dict and set(finding) ==
              {"state", "severity", "reason_code", "anchors"}, "invalid review fields")
        state, severity, reason, refs = (finding[k] for k in
                                         ("state", "severity", "reason_code", "anchors"))
        guard(state in STATES and severity in SEVERITIES and reason in REASONS
              and type(refs) is list and all(type(x) is str and x in anchors for x in refs),
              "invalid verdict or fake source anchor")
        _unique(refs, "reused source anchor")
        if state.startswith("confirmed_"):
            guard(bool(refs) and reason != "insufficient_evidence",
                  "unverified confirmation without evidence anchor")
        if state == "confirmed_issue":
            guard(severity != "none" and reason in FAULTS, "uncategorized issue")
        else:
            guard(severity == "none", "non-issue has severity")
        if state == "confirmed_no_issue":
            guard(reason in ("evidence_supported", "supported_correction", "not_applicable"),
                  "confirmation lacks support")
    if dimensions["source_independence"]["state"] == "confirmed_no_issue":
        sources = comparison["sources"]["research"]
        guard(not sources["duplicate_physical_player_source_identities"]
              and len(set(sources["physical_player_source_identities"])) >= 2,
              "physical player source independence not proven even structurally")
        guard(len({x for x in dimensions["source_independence"]["anchors"]
                   if x.startswith("research:source:")}) >= 2,
              "fewer than two exact Research source references")
    old = comparison["comparison_evidence"]["one_stage_statements"]
    new = comparison["comparison_evidence"]["two_stage_statements"]
    required = {f"old:obs:{idx}" for idx, item in enumerate(old)
                if item["sentiment"] in ("negative", "mixed")}
    mapping = record["negative_retention"]
    guard(type(mapping) is dict and set(mapping) == required,
          "negative/mixed evidence silently omitted")
    for item in mapping.values():
        guard(type(item) is dict and set(item) == {"disposition", "anchors"}
              and item["disposition"] in ("preserved", "supported_correction", "missing", "unknown")
              and type(item["anchors"]) is list
              and all(x in anchors for x in item["anchors"]), "bad negative retention")
        _unique(item["anchors"], "negative map anchor")
        matched = [new[int(x.split(":")[-1])] for x in item["anchors"]
                   if x.startswith("new:obs:")]
        if item["disposition"] in ("preserved", "supported_correction"):
            guard(matched, "no exact new observation for historic negative")
        if item["disposition"] == "preserved":
            guard(any(x["sentiment"] in ("negative", "mixed") for x in matched),
                  "substantive negative dropped")
        if item["disposition"] == "supported_correction":
            guard(dimensions["negative_mixed_retention"]["reason_code"] ==
                  "supported_correction", "unjustified negative deletion")
    gaps = {f"research:gap:{x['gap_id']}" for x in comparison["research"]["gaps"]}
    resolution = record["unknown_resolution"]
    guard(type(resolution) is dict and set(resolution) == gaps, "Research unknown omitted")
    for item in resolution.values():
        guard(type(item) is dict and set(item) == {"disposition", "anchors"}
              and item["disposition"] in ("still_unknown", "confirmed_with_source", "omitted")
              and type(item["anchors"]) is list
              and all(x in anchors for x in item["anchors"]), "invalid unknown evidence")
        _unique(item["anchors"], "unknown anchor")
        if item["disposition"] == "confirmed_with_source":
            guard(any(x.startswith(("research:source:", "new:source:"))
                      for x in item["anchors"]), "unknown falsely declared confirmed")
    return record


def _adjudicate(a, b, result, anchors, subject):
    conflicts = sorted(x for x in DIMENSIONS if a["dimensions"][x] != b["dimensions"][x])
    conflicts += sorted("negative:" + k for k in a["negative_retention"]
                        if a["negative_retention"][k] != b["negative_retention"][k])
    conflicts += sorted("gap:" + k for k in a["unknown_resolution"]
                        if a["unknown_resolution"][k] != b["unknown_resolution"][k])
    if result is None:
        return conflicts, False, bool(conflicts)
    guard(type(result) is dict and set(result) == {"role", "subject", "resolved", "justifications"}
          and result["role"] == "adjudicator" and result["subject"] == subject and type(result["resolved"]) is dict
          and type(result["justifications"]) is dict
          and set(result["resolved"]) == set(conflicts)
          and set(result["justifications"]) == set(conflicts),
          "unrecorded or fabricated adjudication")
    for key in conflicts:
        guard(result["resolved"][key] in ("A", "B", "unresolved"),
              "adjudicator must reference frozen first round")
        v = result["justifications"][key]
        guard(type(v) is dict and set(v) == {"reason_code", "anchors"}
              and v["reason_code"] in REASONS and type(v["anchors"]) is list and bool(v["anchors"])
              and all(x in anchors for x in v["anchors"]),
              "unjustified adjudication")
    return conflicts, True, any(x == "unresolved" for x in result["resolved"].values())


def _evaluate_rows(frame, comparisons, baseline_proven, strict_groups, reviews):
    """Pure non-authoritative mechanical kernel, with test-supplied trust sets.

    Only the public disposable-Git adapter below is allowed to assemble trusted
    sets from existing historical and candidate validators. No user booleans.
    """
    guard(type(frame) is dict and set(frame) == {"trial_id", "groups"}
          and type(frame["trial_id"]) is str and TOKEN.fullmatch(frame["trial_id"])
          and type(frame["groups"]) is list and bool(frame["groups"]), "invalid frozen frame")
    games, sequences = [], []
    for g in frame["groups"]:
        guard(type(g) is dict and set(g) == {"sequence", "group_sha256", "games"}
              and type(g["sequence"]) is int and type(g["group_sha256"]) is str
              and H64.fullmatch(g["group_sha256"]) and type(g["games"]) is list
              and len(g["games"]) == 3, "invalid original three-game group")
        sequences.append(g["sequence"])
        for idx, item in enumerate(g["games"]):
            guard(type(item) is dict and set(item) == {"appid", "title", "original_work_year"}
                  and type(item["appid"]) is str and item["appid"].isdigit()
                  and type(item["title"]) is str and bool(item["title"])
                  and type(item["original_work_year"]) is int
                  and 1000 <= item["original_work_year"] <= 2100,
                  "original work identity not frozen")
            games.append((g["sequence"], idx, item))
    _unique(sequences, "group sequence")
    appids = [g[2]["appid"] for g in games]
    _unique(appids, "original AppID")
    guard(set(comparisons) <= set(appids) and set(reviews) <= set(appids)
          and set(baseline_proven) <= set(appids) and set(strict_groups) <= set(sequences),
          "unfrozen/cherry-picked/resampled pair")
    rows = []
    for seq, index, item in games:
        appid = item["appid"]
        c = comparisons.get(appid)
        reasons = []
        if appid not in baseline_proven:
            reasons.append("baseline_writer_provenance_not_verified")
        if seq not in strict_groups:
            reasons.append("strict_research_assembly_v2_group_not_ready")
        if c is None:
            reasons.append("pair_not_measured")
        else:
            identity = c["identity"]
            if (str(c["appid"]) != appid or c["title"] != item["title"]
                    or identity["original_work_year_research"] != item["original_work_year"]
                    or identity["original_work_year_two_stage"] != item["original_work_year"]
                    or identity["original_work_year_one_stage"] != item["original_work_year"]
                    or identity["year_conflict_with_baseline"]):
                reasons.append("original_work_identity_year_conflict")
        disagreements, adjudicated = [], False
        if not reasons:
            try:
                refs = _anchor_set(c)
                data = reviews.get(appid)
                guard(type(data) is dict and set(data) ==
                      {"A", "B", "adjudication"}, "missing independent reviewer")
                subject = {"trial_id": frame["trial_id"], "group_sequence": seq, "appid": appid}
                a = _review(data["A"], "A", refs, c, subject)
                b = _review(data["B"], "B", refs, c, subject)
                disagreements, adjudicated, unresolved = _adjudicate(
                    a, b, data["adjudication"], refs, subject)
                if unresolved:
                    reasons.append("adjudication_missing_or_unresolved")
                for r in (a, b):
                    if any(x["state"] in ("unknown", "needs_review")
                           for x in r["dimensions"].values()):
                        reasons.append("human_dimension_not_verified")
                    if any(x["state"] == "confirmed_issue" for x in r["dimensions"].values()):
                        reasons.append("human_confirmed_quality_defect")
                    if any(x["disposition"] in ("missing", "unknown")
                           for x in r["negative_retention"].values()):
                        reasons.append("substantive_negative_not_proven_preserved")
                    if any(x["disposition"] == "omitted"
                           for x in r["unknown_resolution"].values()):
                        reasons.append("unknown_omitted_or_overstated")
            except (ValueError, TypeError, KeyError, IndexError) as exc:
                # Do not leak a raw free-form reviewer note or source text.
                msg = str(exc)
                reasons.append("fake_or_reused_source_anchor" if "anchor" in msg
                               else "review_record_invalid_or_unfrozen")
        fatal = {"original_work_identity_year_conflict", "human_confirmed_quality_defect",
                 "substantive_negative_not_proven_preserved", "unknown_omitted_or_overstated",
                 "review_record_invalid_or_unfrozen", "fake_or_reused_source_anchor"}
        status = "offline_gate_ready" if not reasons else (
            "rejected" if set(reasons) & fatal else "not_measured")
        rows.append({"sequence": seq, "item_index": index, "appid": appid,
                     "status": status, "reason_codes": sorted(set(reasons)),
                     "reviewer_disagreements": len(disagreements), "adjudicated": adjudicated})
    counts = Counter(r["status"] for r in rows)
    return {
        "schema": SCHEMA, "active": False, "diagnostic_only": True,
        "cohort": {
            "frozen_groups": len(sequences), "frozen_games": len(games),
            "historical_baseline_proven_games": len(baseline_proven),
            "strict_candidate_ready_groups": len(strict_groups),
            "eligible_comparable_games": sum(
                x["appid"] in baseline_proven and x["sequence"] in strict_groups
                and comparisons.get(x["appid"]) is not None for x in rows),
            "offline_gate_ready": counts["offline_gate_ready"],
            "rejected": counts["rejected"], "not_measured": counts["not_measured"],
            "reviewer_disagreements": sum(x["reviewer_disagreements"] for x in rows),
            "adjudicated_games": sum(x["adjudicated"] for x in rows),
            "unadjudicated_disagreements": sum(
                x["reviewer_disagreements"] for x in rows if not x["adjudicated"]),
        },
        "per_game": rows, "real_source_authenticity_verified": False,
        "quality_verified": False, "pilot_authorized": False,
        "canonical_readiness": False, "deep_readiness": False,
        "approved_stop_thresholds": None, "writes": [], "semantic_execution": False,
    }


def _frozen_json(root, ref):
    """Strict content-addressed reviewer/cohort Git object; no working tree read."""
    guard(type(ref) is dict and set(ref) == {"commit", "path", "blob_sha256"},
          "missing immutable Git locator")
    commit, path, sha = ref["commit"], ref["path"], ref["blob_sha256"]
    guard(type(commit) is str and H40.fullmatch(commit)
          and type(sha) is str and H40.fullmatch(sha)
          and type(path) is str and path.startswith("reviews/dossier_shadow_offline/")
          and path.endswith(".json") and all(x not in ("", ".", "..") for x in path.split("/")),
          "unsafe Git review locator")

    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True)

    ancestry = git("merge-base", "--is-ancestor", commit, "HEAD")
    original, latest = git("rev-parse", commit + ":" + path), git("rev-parse", "HEAD:" + path)
    value = git("show", commit + ":" + path)
    guard(ancestry.returncode == original.returncode == latest.returncode ==
          value.returncode == 0
          and original.stdout.decode().strip() == latest.stdout.decode().strip() == sha,
          "stale wrong-commit review/cohort data")
    return json.loads(value.stdout)


def evaluate_offline_fixture(repo, *, frozen, manifest, contract,
                             item_locators, historical_requests, review_locators):
    """Guarded integration, requiring existing exact Git-history validators.

    No live route; no claimed writer acceptance from present JSON, status or
    operator boolean. Real source authenticity/human blinding remain separate.
    """
    from dossier_two_stage_final_acceptance import (
        offline_gate, inspect_original_groups, STATUS_GROUP_READY,
    )
    from dossier_shadow_pilot_preflight import verify_offline_preflight
    from dossier_two_stage_shadow_quality import evaluate_offline_fixture as old_comparison
    from dossier_two_stage_contract_guard import canonical_sha256
    from dossier_two_stage_staging import git

    root = offline_gate(repo, offline_fixture=True)
    head = git(root, "rev-parse", "HEAD").stdout.decode().strip()
    guard(type(frozen) is dict and set(frozen) ==
          {"trial_id", "groups", "freeze_commit", "freeze_ref", "candidate_manifest_sha256"},
          "unfrozen cohort")
    lock = _frozen_json(root, frozen["freeze_ref"])
    guard(frozen["freeze_ref"]["commit"] == frozen["freeze_commit"]
          and lock == {"trial_id": frozen["trial_id"], "groups": frozen["groups"],
                       "candidate_manifest_sha256": frozen["candidate_manifest_sha256"]}
          and canonical_sha256(manifest) == frozen["candidate_manifest_sha256"],
          "wrong-commit, moved or forged cohort freeze")
    guard(type(item_locators) is list and type(historical_requests) is list
          and type(review_locators) is dict, "invalid exact metadata")
    selected = {g["sequence"] for g in frozen["groups"]}
    guard(len(selected) == len(frozen["groups"]), "duplicate selected original group")
    plan = {x["sequence"]: x for x in manifest["submission_group_plan"]["groups"]}
    for unit in frozen["groups"]:
        g = plan.get(unit["sequence"])
        guard(g is not None and g["group_sha256"] == unit["group_sha256"]
              and [(str(x["appid"]), x["title"]) for x in g["items"]]
              == [(x["appid"], x["title"]) for x in unit["games"]],
              "original immutable three-game membership drift")
    guard(all(type(x) is dict and x.get("sequence") in selected for x in item_locators),
          "foreign resampled candidate locator")
    appids = {item["appid"] for unit in frozen["groups"] for item in unit["games"]}
    guard(set(review_locators) <= appids, "foreign/cherry-picked reviewer row")

    inspected = inspect_original_groups(
        root, manifest=manifest, contract=contract,
        item_locators=item_locators, offline_fixture=True)
    guard(not inspected["unmatched_locators"], "unbound candidate transport")
    ready = {x["sequence"] for x in inspected["decisions"]
             if x["sequence"] in selected and x["status"] == STATUS_GROUP_READY}
    guard(selected <= {x["sequence"] for x in inspected["decisions"]},
          "inspector omitted original selected group")
    verified, baselines = set(), []
    seqs = [r.get("group_sequence") for r in historical_requests]
    _unique(seqs, "historical writer receipt")
    guard(set(seqs) <= selected, "foreign/resampled historical receipt")
    for req in historical_requests:
        try:
            proof = verify_offline_preflight(root, request=req, contract=contract)
            unit = next(x for x in frozen["groups"] if x["sequence"] == req["group_sequence"])
            if (proof.get("preflight_ready") is True
                    and [x["appid"] for x in unit["games"]] == proof["accepted_baseline_appids"]
                    and [(x["appid"], x["title"], x["original_work_year"]) for x in unit["games"]]
                    == [(x["appid"], x["title"], x["original_work_year"])
                        for x in req["original_games"]]):
                verified.update(proof["accepted_baseline_appids"])
                baselines.extend(req["legacy_baselines"])
        except (ValueError, KeyError, TypeError):
            # The historical verifier must prove the writer itself, not file existence.
            continue
    comparisons = {}
    for unit in frozen["groups"]:
        seq = unit["sequence"]
        ids = {x["appid"] for x in unit["games"]}
        if seq not in ready or not ids <= verified:
            continue
        try:
            diagnostic = old_comparison(
                root, manifest=manifest, contract=contract,
                item_locators=[x for x in item_locators if x["sequence"] == seq],
                baseline_references=[x for x in baselines if x["appid"] in ids])
            comparisons.update({str(x["appid"]): x["comparison"] for x in diagnostic["per_game"]
                                if x["comparison"] is not None and x["group_sequence"] == seq})
        except (ValueError, KeyError, TypeError):
            continue
    reviews = {}
    # Exactly one immutable reviewer file per role and game; no cross-game
    # replay of the same citation/review artifact, even if local IDs coincide.
    all_round_refs = []
    for locator in review_locators.values():
        if isinstance(locator, dict):
            for role in ("A", "B"):
                ref = locator.get(role)
                if isinstance(ref, dict):
                    all_round_refs.append((ref.get("commit"), ref.get("path")))
    _unique(all_round_refs, "cross-game frozen reviewer file")
    for appid, locator in review_locators.items():
        try:
            guard(type(locator) is dict and set(locator) == {"A", "B", "adjudication"},
                  "incomplete reviewer freeze")
            a, b = locator["A"], locator["B"]
            guard(a["commit"] != b["commit"] and
                  git(root, "merge-base", a["commit"], b["commit"]).stdout.decode().strip()
                  == frozen["freeze_commit"], "first rounds not separately frozen")
            ra, rb = _frozen_json(root, a), _frozen_json(root, b)
            adj = locator["adjudication"]
            if adj is not None:
                guard(all(subprocess.run(
                    ["git", "-C", str(root), "merge-base", "--is-ancestor",
                     ref["commit"], adj["commit"]], capture_output=True).returncode == 0
                    for ref in (a, b)), "adjudication preceded both reviewer locks")
            reviews[appid] = {"A": ra, "B": rb,
                              "adjudication": _frozen_json(root, adj) if adj else None}
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            reviews[appid] = None
    out = _evaluate_rows({"trial_id": frozen["trial_id"], "groups": frozen["groups"]},
                         comparisons, verified, ready, reviews)
    out["frozen_head_sha"] = head
    out["source_trust"] = {
        "historical": "existing full-history strict writer preflight only",
        "candidate": "existing strict Research/Assembly three-game inspector only",
        "review": "separate immutable A/B and later adjudication Git artifacts",
        "external_source_reality": "not_verified_by_this_offline_gate",
    }
    return out


if __name__ == "__main__":
    raise SystemExit("Offline API only; no live semantic, source or writer execution")

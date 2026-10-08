#!/usr/bin/env python3
"""Bounded Stage-1 frozen contract/semantic/ingest regression without test fixtures in production."""
from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path

from deep_stage1 import (
    RESULTS, Stage1Error, build_work_manifest, empty_state, file_sha256,
    recompute_progress, validate_result, validate_state, validate_work_manifest,
    verify_dossier,
)
from ingest_deep_stage1 import ingest_documents
from build_deep_stage2_work import normalize_stage1_candidates


def sha(symbol: str) -> str:
    return symbol * 64


def fails(callback, message: str) -> None:
    try:
        callback()
    except Stage1Error:
        return
    raise AssertionError(message)


def dossier(appid: str) -> dict:
    return {
        "appid": appid,
        "web_evidence_contract_binding": {"revision": "exact-test-binding"},
        "expires_at_utc": "2030-01-01T00:00:00Z",
        "observations": [{"text": "varied gameplay"}, {"text": "cooperative play"}],
        "conflicts": [{"text": "repeated sections"}],
    }


def source_and_work(root: Path, ids=("42", "43")) -> tuple[dict, dict]:
    source = {
        "contract": "PROGRESSIVE-PASS2-WORK-V1",
        "projection_status": "current_github_owned_fast_dossier_deep_v1_projection",
        "semantic_generation_id": sha("a"),
        "semantic_bindings": {"profile_semantic_sha256": sha("d")},
        "profile_pin": {"pin_sha256": sha("c"), "immutable_raw_url": "https://example.invalid/pinned"},
        "dossier_compatibility_binding": {"revision": "exact-test-binding"},
        "items": [],
    }
    for index, appid in enumerate(ids):
        data = dossier(appid)
        path = root / f"data/cache/taste_steam_review_dossiers/App_{appid}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        source["items"].append({
            "semantic_generation_id": sha("a"),
            "work_id": sha("b" if index == 0 else "f"),
            "family_id": f"family-{appid}",
            "taste_subject_key": f"App_{appid}", "appid": appid,
            "candidate_context_sha256": sha("e"),
            "profile_semantic_sha256": sha("d"),
            "work_mode": "normal_first_pass",
            "dossier_path": f"data/cache/taste_steam_review_dossiers/App_{appid}.json",
            "dossier_content_sha256": file_sha256(path),
            "dossier_compatibility_binding": {"revision": "exact-test-binding"},
            "dossier_expires_at_utc": data["expires_at_utc"],
            "semantic_input": {"title": f"Fixture {appid}", "fit_tags": ["variety"]},
        })
    work = build_work_manifest(
        source, empty_state(), root=root,
        dossier_validator=lambda **kwargs: (True, "test-only accepted Dossier fixture"),
        generated_at_utc="2026-10-07T00:00:00Z",
    )
    return source, work


def result(item: dict, outcome="analyzed_fit") -> dict:
    row = {
        "schema_version": 1, "contract": "DEEP-STAGE1-RESULT-V1",
        "semantic_generation_id": item["semantic_generation_id"],
        "work_id": item["work_id"],
        "family_id": item["family_id"], "taste_subject_key": item["taste_subject_key"],
        "appid": item["appid"], "candidate_context_sha256": item["candidate_context_sha256"],
        "profile_pin_sha256": item["profile_pin"]["pin_sha256"],
        "profile_semantic_sha256": item["profile_semantic_sha256"],
        "dossier_content_sha256": item["dossier_content_sha256"],
        "outcome": outcome, "confidence": "high",
        "summary_ru": "Подходит по разнообразию, но есть риск повторов.",
        "positives": [{
            "finding_id": "positive-variety", "text_ru": "Разнообразие механик заинтересует игрока.",
            "candidate_evidence_refs": [{"kind": "observation", "index": 0}],
            "profile_evidence_refs": [{"path": "$.likes[0]"}],
        }],
        "negatives": [{
            "finding_id": "negative-repetition", "text_ru": "Повторы могут утомлять.",
            "candidate_evidence_refs": [{"kind": "conflict", "index": 0}],
            "profile_evidence_refs": [{"path": "$.dislikes[0]"}],
        }],
        "nuances": [{
            "finding_id": "nuance-coop",
            "text_ru": "Кооператив стоит учитывать только при желании играть совместно.",
            "candidate_evidence_refs": [{"kind": "observation", "index": 1}],
            "profile_evidence_refs": [],
        }],
        "provisional_deep_fit_score_0_56": 46.0,
        "point_breakdown": [
            {"breakdown_id": "variety", "label_ru": "Интерес к разнообразию",
             "direction": "positive", "points": 48.0,
             "finding_refs": ["positive-variety", "nuance-coop"]},
            {"breakdown_id": "repetition", "label_ru": "Риск повторяющихся участков",
             "direction": "negative", "points": -2.0,
             "finding_refs": ["negative-repetition"]},
        ],
        "analysis_issue_code": None,
    }
    if outcome != "analyzed_fit":
        row["provisional_deep_fit_score_0_56"] = None
        row["point_breakdown"] = []
        if outcome == "analysis_incomplete":
            row["analysis_issue_code"] = "insufficient_evidence"
    return row


def main() -> None:
    contract = json.loads(Path("config/deep_stage1_contract.json").read_text(encoding="utf-8"))
    schema = json.loads(Path("config/deep_stage1_result_schema.json").read_text(encoding="utf-8"))
    architecture = json.loads(Path("config/deep_two_stage_architecture_contract.json").read_text(encoding="utf-8"))
    prompt = Path("config/deep_stage1_manual_worker_prompt.md").read_text(encoding="utf-8")

    assert architecture["production_cutover_authorized"] is False
    assert contract["status"] == "frozen_not_active"
    assert contract["work_manifest"]["github_owned"] is True
    assert contract["result"]["create_only"] is True
    assert schema["properties"]["contract"]["const"] == "DEEP-STAGE1-RESULT-V1"
    assert set(schema["required"]) == set(result_field for result_field in result(
        {"semantic_generation_id": sha("a"), "work_id": sha("b"),
         "family_id": "fixture", "taste_subject_key": "App_42", "appid": "42",
         "candidate_context_sha256": sha("e"), "profile_pin": {"pin_sha256": sha("c")},
         "profile_semantic_sha256": sha("d"), "dossier_content_sha256": sha("f")}
    ))
    for phrase in (
        "NOT ACTIVE", "GitHub owns scope", "Dossier is the factual evidence source",
        "Ignore all Wishlist", "dynamic", "EXACTLY", "Scheduled Task",
        "Do not read Stage-2 work/anchors",
    ):
        assert phrase in prompt, phrase

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source, work = source_and_work(root)
        assert work["total_eligible"] == 2 and len(work["items"]) == 2
        assert [item["sequence"] for item in work["items"]] == [1, 2]
        validate_work_manifest(work)
        item = work["items"][0]
        d = dossier(item["appid"])
        valid = result(item)
        validate_result(valid, item, root=root)
        assert valid["point_breakdown"][0]["points"] + valid["point_breakdown"][1]["points"] == 46.0

        bad = deepcopy(valid); bad["provisional_deep_fit_score_0_56"] = 46.1
        fails(lambda: validate_result(bad, item, dossier=d), "arithmetic reconciliation")
        bad = deepcopy(valid); bad["point_breakdown"][1]["direction"] = "positive"
        fails(lambda: validate_result(bad, item, dossier=d), "wrong point direction")
        bad = deepcopy(valid); bad["positives"][0]["candidate_evidence_refs"][0]["index"] = 99
        fails(lambda: validate_result(bad, item, dossier=d), "missing exact dossier evidence")
        bad = deepcopy(valid); bad["positives"][0]["profile_evidence_refs"] = []
        fails(lambda: validate_result(bad, item, dossier=d), "ungrounded personal impact")
        bad = deepcopy(valid); bad["profile_pin_sha256"] = sha("0")
        fails(lambda: validate_result(bad, item, dossier=d), "stale profile binding")
        bad = deepcopy(valid); bad["stage2_neighbors"] = []
        fails(lambda: validate_result(bad, item, dossier=d), "unexpected Stage-2 field")
        bad = deepcopy(valid); bad["point_breakdown"][0]["finding_refs"] = ["made-up"]
        fails(lambda: validate_result(bad, item, dossier=d), "unbound point ref")
        bad = deepcopy(valid); bad["point_breakdown"][0]["points"] = 47.95
        fails(lambda: validate_result(bad, item, dossier=d), "invalid 0.1 precision")
        for outcome in ("analyzed_not_fit", "analysis_incomplete"):
            validate_result(result(item, outcome), item, dossier=d)
        bad = result(item, "analyzed_not_fit")
        bad["provisional_deep_fit_score_0_56"] = 3.0
        fails(lambda: validate_result(bad, item, dossier=d), "not-fit numerical ladder")
        bad = result(item, "analysis_incomplete")
        bad["analysis_issue_code"] = None
        fails(lambda: validate_result(bad, item, dossier=d), "incomplete without issue")

        broken = deepcopy(source)
        broken["projection_status"] = "legacy_full_reanalysis_migration_active"
        dormant = build_work_manifest(broken, empty_state(), root=root)
        assert dormant["total_eligible"] == 0 and not dormant["items"] and dormant["diagnostics"]
        forbidden = deepcopy(source)
        forbidden["items"][0]["semantic_input"]["wishlist"] = True
        rejected = build_work_manifest(forbidden, empty_state(), root=root)
        assert rejected["total_eligible"] == 1 and len(rejected["diagnostics"]) == 1

        mutated = root / item["dossier_path"]
        mutated.write_text(mutated.read_text(encoding="utf-8") + " ", encoding="utf-8")
        fails(lambda: verify_dossier(item, root), "Dossier content immutable binding")
        mutated.write_text(json.dumps(d), encoding="utf-8")

        # First invalid result must not prevent acceptance of the later sibling item.
        submission_one = root / work["items"][0]["result_submission_path"]
        submission_two = root / work["items"][1]["result_submission_path"]
        submission_one.parent.mkdir(parents=True, exist_ok=True)
        submission_one.write_text(json.dumps(bad), encoding="utf-8")
        good_two = result(work["items"][1])
        submission_two.write_text(json.dumps(good_two), encoding="utf-8")
        state, receipts = ingest_documents(
            work, empty_state(), [submission_two, submission_one],
            repo_root=root, accepted_at_utc="2026-10-07T00:00:00Z",
        )
        assert len(receipts) == 2 and receipts[0]["status"] == "rejected_no_attempt"
        assert receipts[1]["status"] == "accepted"
        assert state["progress"] == {
            "total_eligible": 2, "completed_fit": 1, "completed_not_fit": 0,
            "pending": 1, "diagnostic_incomplete": 0,
            "last_attempt_at_utc": "2026-10-07T00:00:00Z",
            "last_successful_result_at_utc": "2026-10-07T00:00:00Z",
        }
        assert len(state["diagnostic_history"]) == 1
        assert len(state["entries"]) == 1

        # Idempotent replay is accepted without rewriting canonical result.
        replay_state, replay_receipts = ingest_documents(
            work, state, [submission_two], repo_root=root,
            accepted_at_utc="2026-10-08T00:00:00Z",
        )
        assert replay_state["entries"] == state["entries"]
        assert replay_receipts[0]["accepted_at_utc"] == "2026-10-07T00:00:00Z"
        accepted_path = root / replay_state["entries"][work["items"][1]["work_id"]]["accepted_result_path"]
        assert accepted_path.is_file()
        candidates, issues = normalize_stage1_candidates(replay_state, root)
        assert len(candidates) == 1 and not issues
        assert candidates[0]["stage1_result"]["work_id"] == work["items"][1]["work_id"]

        # Already-accepted Stage-1 work does not auto-retry; other item remains pending.
        regenerated = build_work_manifest(source, replay_state, root=root)
        assert regenerated["total_eligible"] == 2 and len(regenerated["items"]) == 1
        assert regenerated["items"][0]["work_id"] == item["work_id"]
        assert recompute_progress(replay_state, regenerated)["progress"]["pending"] == 1

        # Valid incomplete consumes one bound item, but does not become a Stage-2 fit.
        incompleted = result(item, "analysis_incomplete")
        submission_one.write_text(json.dumps(incompleted), encoding="utf-8")
        later, good_receipts = ingest_documents(
            regenerated, replay_state, [submission_one], repo_root=root,
            accepted_at_utc="2026-10-08T00:00:00Z",
        )
        assert good_receipts[0]["status"] == "accepted"
        assert later["progress"]["diagnostic_incomplete"] == 1
        assert later["progress"]["pending"] == 0
        validate_state(later)
    print("PASS: frozen Deep Stage-1 manifest, Dossier/profile bindings, 0.1 score,"
          " dynamic breakdown, nonblocking transport, replay, Stage-2 fit handoff")


if __name__ == "__main__":
    main()

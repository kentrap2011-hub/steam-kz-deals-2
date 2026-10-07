#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import tempfile
from copy import deepcopy
from pathlib import Path

from deep_stage2 import (
    RESULT_REQUIRED,
    Stage2Error,
    apply_validated_result,
    build_work_manifest,
    canonical_sha256,
    empty_state,
    make_work_item,
    place_canonical_score,
    select_anchor_window,
    validate_result,
    validate_state,
    validate_work_manifest,
)
from ingest_deep_stage2 import ingest_documents


def sha(ch: str) -> str:
    return ch * 64


def stage1(work_ch: str, family: str, appid: str, score: float, finding_id: str) -> dict:
    return {
        "schema_version": 1,
        "contract": "DEEP-STAGE1-RESULT-V1",
        "semantic_generation_id": sha("a"),
        "work_id": sha(work_ch),
        "family_id": family,
        "taste_subject_key": f"App_{appid}",
        "appid": appid,
        "candidate_context_sha256": sha("b"),
        "profile_pin_sha256": sha("c"),
        "profile_semantic_sha256": sha("d"),
        "dossier_content_sha256": sha("e"),
        "outcome": "analyzed_fit",
        "confidence": "high",
        "summary_ru": f"Fixture {family}",
        "positives": [{
            "finding_id": finding_id,
            "text_ru": f"Сильная сторона {family}",
            "candidate_evidence_refs": [{"kind": "observation", "index": 0}],
            "profile_evidence_refs": [{"path": "$.fixture"}],
        }],
        "negatives": [],
        "nuances": [],
        "provisional_deep_fit_score_0_56": score,
        "point_breakdown": [{
            "breakdown_id": f"p-{finding_id}",
            "label_ru": f"Вклад {family}",
            "direction": "positive",
            "points": score,
            "finding_refs": [finding_id],
        }],
        "analysis_issue_code": None,
    }


def anchor_entry(
    anchor_id: str,
    family: str,
    appid: str,
    score: float,
    stage1_path: str,
    stage1_sha: str,
) -> dict:
    return {
        "anchor_id": anchor_id,
        "calibration_work_id": anchor_id,
        "family_id": family,
        "appid": appid,
        "stage1_work_id": sha("1" if appid == "1" else "2"),
        "stage1_result_path": stage1_path,
        "stage1_result_sha256": stage1_sha,
        "profile_semantic_sha256": sha("d"),
        "anchor_window_id": sha("6"),
        "anchor_window_revision": 1,
        "anchor_set_sha256": sha("7"),
        "canonical_stage2_result_path": f"data/cache/deep_stage2_results/{anchor_id}.json",
        "canonical_stage2_result_sha256": sha("8" if appid == "1" else "9"),
        "semantic_calibrated_deep_fit_target_0_56": score,
        "comparative_adjustment_from_stage1": 0.0,
        "comparisons": [],
        "why_stage2_changed_ru": "fixture",
        "why_above_ru": [],
        "why_below_ru": [],
        "diagnostic_code": None,
        "accepted_at_utc": "2026-10-07T00:00:00+00:00",
        "status": "calibrated",
        "outcome": "calibrated_fit",
        "calibrated_deep_fit_score_0_56": score,
        "placement": None,
    }


def result_for(item: dict, target: dict, relations: dict[str, str], semantic: float) -> dict:
    comparisons = []
    for anchor in item["lower_anchors"] + item["upper_anchors"]:
        comparisons.append({
            "anchor_id": anchor["anchor_id"],
            "relation": relations[anchor["anchor_id"]],
            "reasons_ru": ["Сравнение опирается только на принятые Stage-1 findings."],
            "target_stage1_finding_refs": [target["positives"][0]["finding_id"]],
            "anchor_stage1_finding_refs": [f"f-{anchor['appid']}"],
        })
    return {
        "schema_version": 1,
        "contract": "DEEP-STAGE2-RESULT-V1",
        "calibration_work_id": item["calibration_work_id"],
        "target_family_id": item["target_family_id"],
        "target_appid": item["target_appid"],
        "profile_pin_sha256": target["profile_pin_sha256"],
        "profile_semantic_sha256": item["profile_semantic_sha256"],
        "stage1_result_sha256": item["stage1_result_sha256"],
        "anchor_window_id": item["anchor_window_id"],
        "anchor_window_revision": item["anchor_window_revision"],
        "anchor_set_sha256": item["anchor_set_sha256"],
        "outcome": "calibrated_fit",
        "comparisons": comparisons,
        "semantic_calibrated_deep_fit_target_0_56": semantic,
        "comparative_adjustment_from_stage1": round(
            semantic - target["provisional_deep_fit_score_0_56"], 2
        ),
        "why_stage2_changed_ru": "Сравнение с соседями уточнило относительную позицию.",
        "why_above_ru": ["Выше нижнего соседа по принятому Stage-1 evidence."],
        "why_below_ru": ["Ниже верхнего соседа по принятому Stage-1 evidence."],
        "diagnostic_code": None,
    }


def expect_fail(fn, message: str) -> None:
    try:
        fn()
    except Stage2Error:
        return
    raise AssertionError(message)


def main() -> None:
    prompt = Path("config/deep_stage2_manual_worker_prompt.md").read_text(encoding="utf-8")
    contract = json.loads(Path("config/deep_stage2_contract.json").read_text(encoding="utf-8"))
    schema = json.loads(Path("config/deep_stage2_result_schema.json").read_text(encoding="utf-8"))
    architecture = json.loads(
        Path("config/deep_two_stage_architecture_contract.json").read_text(encoding="utf-8")
    )

    assert contract["status"] == "frozen_not_active"
    assert architecture["production_cutover_authorized"] is False
    assert contract["work_manifest"]["window_selection_owner"] == "github_control_plane"
    assert contract["scoring"]["github_assigns_final_unique_numeric_coordinate"] is True
    assert schema["properties"]["contract"]["const"] == "DEEP-STAGE2-RESULT-V1"
    for phrase in [
        "web search or new external game research",
        "Do not rebuild scope, choose anchors, expand the window",
        "Scheduled Task",
        "GitHub alone assigns",
    ]:
        assert phrase in prompt

    lower_id, upper_id = sha("3"), sha("4")
    target = stage1("5", "target", "3", 30.0, "f-3")
    lower_doc = stage1("1", "lower", "1", 29.9, "f-1")
    upper_doc = stage1("2", "upper", "2", 30.1, "f-2")

    state = empty_state()
    state["entries"] = {
        lower_id: anchor_entry(lower_id, "lower", "1", 29.99, "s1-lower.json", sha("f")),
        upper_id: anchor_entry(upper_id, "upper", "2", 30.01, "s1-upper.json", sha("0")),
    }
    validate_state(state)

    candidate = {
        "sequence": 7,
        "stage1_work_id": target["work_id"],
        "family_id": target["family_id"],
        "appid": target["appid"],
        "profile_pin": {
            "path": "data/control/profile-pin.json",
            "sha256": target["profile_pin_sha256"],
        },
        "profile_semantic_sha256": target["profile_semantic_sha256"],
        "stage1_result_path": "s1-target.json",
        "stage1_result_sha256": sha("a"),
        "stage1_result": target,
    }

    lower, upper = select_anchor_window(30.0, state, lower_count=1, upper_count=1)
    assert [row["anchor_id"] for row in lower] == [lower_id]
    assert [row["anchor_id"] for row in upper] == [upper_id]

    item = make_work_item(candidate, state, sequence=7, lower_count=1, upper_count=1)
    assert item["result_submission_path"].endswith(f"{item['calibration_work_id']}.json")
    serialized_item = json.dumps(item).lower()
    assert "price" not in serialized_item
    assert "discount" not in serialized_item
    assert "wishlist" not in serialized_item

    manifest = build_work_manifest([candidate], state, lower_count=1, upper_count=1)
    validate_work_manifest(manifest)
    assert len(manifest["items"]) == 1

    docs = {
        "s1-target.json": target,
        "s1-lower.json": lower_doc,
        "s1-upper.json": upper_doc,
    }
    hashes = {
        "s1-target.json": item["stage1_result_sha256"],
        "s1-lower.json": state["entries"][lower_id]["stage1_result_sha256"],
        "s1-upper.json": state["entries"][upper_id]["stage1_result_sha256"],
    }

    def loader(path: str, expected: str) -> dict:
        assert expected == hashes[path]
        return docs[path]

    good = result_for(
        item,
        target,
        {lower_id: "near_tie_target_above", upper_id: "near_tie_target_below"},
        30.0,
    )
    assert set(good) == RESULT_REQUIRED
    validate_result(good, item, stage1_loader=loader)

    placed = apply_validated_result(
        state,
        item,
        good,
        canonical_result_path=f"data/cache/deep_stage2_results/{item['calibration_work_id']}.json",
        canonical_result_sha256=sha("b"),
        accepted_at_utc="2026-10-07T01:00:00+00:00",
    )
    assert placed["entries"][item["calibration_work_id"]][
        "calibrated_deep_fit_score_0_56"
    ] == 30.0
    scores = [
        e["calibrated_deep_fit_score_0_56"]
        for e in placed["entries"].values()
        if e.get("status") == "calibrated"
    ]
    assert len(scores) == len(set(scores))

    dense = empty_state()
    dense["entries"] = {
        lower_id: anchor_entry(lower_id, "lower", "1", 30.00, "s1-lower.json", sha("f")),
        upper_id: anchor_entry(upper_id, "upper", "2", 30.01, "s1-upper.json", sha("0")),
    }
    dense_item = deepcopy(item)
    dense_item["lower_anchors"] = [
        dict(item["lower_anchors"][0], calibrated_deep_fit_score_0_56=30.00)
    ]
    dense_item["upper_anchors"] = [
        dict(item["upper_anchors"][0], calibrated_deep_fit_score_0_56=30.01)
    ]
    dense_item["anchor_set_sha256"] = canonical_sha256([
        dict(dense_item["lower_anchors"][0], side="lower"),
        dict(dense_item["upper_anchors"][0], side="upper"),
    ])
    dense_item["anchor_window_id"] = sha("6")
    dense_item["calibration_work_id"] = sha("7")
    final, placement = place_canonical_score(dense, dense_item, 30.00)
    assert len(placement["local_respace"]) == 1
    dense_scores = [
        e["calibrated_deep_fit_score_0_56"]
        for e in dense["entries"].values()
        if e.get("status") == "calibrated"
    ] + [final]
    assert len(dense_scores) == len(set(dense_scores))
    assert all(round(value, 2) == value for value in dense_scores)

    missing = deepcopy(good)
    missing["comparisons"] = missing["comparisons"][:-1]
    expect_fail(
        lambda: validate_result(missing, item, stage1_loader=loader),
        "missing supplied anchor comparison must fail closed",
    )

    forged = deepcopy(good)
    forged["comparisons"][0]["target_stage1_finding_refs"] = ["invented-fact"]
    expect_fail(
        lambda: validate_result(forged, item, stage1_loader=loader),
        "invented Stage-1 finding ref must fail closed",
    )

    bad_adjustment = deepcopy(good)
    bad_adjustment["comparative_adjustment_from_stage1"] = 1.0
    expect_fail(
        lambda: validate_result(bad_adjustment, item, stage1_loader=loader),
        "wrong comparative adjustment must fail closed",
    )

    stale = deepcopy(state)
    stale["entries"][lower_id]["calibrated_deep_fit_score_0_56"] = 29.98
    expect_fail(
        lambda: apply_validated_result(
            stale,
            item,
            good,
            canonical_result_path=f"data/cache/deep_stage2_results/{item['calibration_work_id']}.json",
            canonical_result_sha256=sha("b"),
            accepted_at_utc="2026-10-07T01:30:00+00:00",
        ),
        "stale anchor descriptor must fail closed",
    )

    diagnostic = deepcopy(good)
    diagnostic.update({
        "outcome": "stage1_contradiction",
        "comparisons": [],
        "semantic_calibrated_deep_fit_target_0_56": None,
        "comparative_adjustment_from_stage1": None,
        "why_stage2_changed_ru": "",
        "why_above_ru": [],
        "why_below_ru": [],
        "diagnostic_code": "stage1_evidence_contradiction",
    })
    validate_result(diagnostic, item, stage1_loader=loader)
    diag_state = apply_validated_result(
        state,
        item,
        diagnostic,
        canonical_result_path=f"data/cache/deep_stage2_results/{item['calibration_work_id']}.json",
        canonical_result_sha256=sha("c"),
        accepted_at_utc="2026-10-07T02:00:00+00:00",
    )
    assert diag_state["entries"][item["calibration_work_id"]][
        "calibrated_deep_fit_score_0_56"
    ] is None
    assert diag_state["progress"]["diagnostic_incomplete"] == 1

    no_anchor = build_work_manifest([candidate], empty_state(), lower_count=1, upper_count=1)
    assert no_anchor["items"] == []
    assert no_anchor["diagnostics"][0]["code"] == "anchor_window_unavailable"

    retry_state = empty_state()
    retry_state["entries"][sha("9")] = {
        "stage1_work_id": target["work_id"],
        "stage1_result_sha256": candidate["stage1_result_sha256"],
        "profile_semantic_sha256": target["profile_semantic_sha256"],
        "status": "calibration_incomplete",
        "calibrated_deep_fit_score_0_56": None,
    }
    retry_manifest = build_work_manifest([candidate], retry_state)
    assert retry_manifest["items"] == []
    assert retry_manifest["diagnostics"][0]["code"] == "explicit_retry_or_reanalysis_required"

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        submission = temp / item["result_submission_path"]
        submission.parent.mkdir(parents=True, exist_ok=True)
        submission.write_text(
            json.dumps(good, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        work = {
            "schema_version": 1,
            "contract": "DEEP-STAGE2-WORK-V1",
            "generated_at_utc": "2026-10-07T00:00:00+00:00",
            "stage1_fit_eligible": 3,
            "items": [item],
            "diagnostics": [],
        }
        ingested, receipts = ingest_documents(
            work,
            state,
            [submission],
            accepted_at_utc="2026-10-07T03:00:00+00:00",
            repo_root=temp,
            canonical_results_root=temp / "data/cache/deep_stage2_results",
            receipts_root=temp / "data/cache/deep_stage2_ingest_receipts",
            stage1_loader=loader,
        )
        assert len(receipts) == 1
        assert ingested["progress"]["calibrated"] == 3
        canonical = temp / receipts[0]["canonical_stage2_result_path"]
        assert canonical.exists()
        assert hashlib.sha256(canonical.read_bytes()).hexdigest() == receipts[0][
            "canonical_stage2_result_sha256"
        ]
        first_score = ingested["entries"][item["calibration_work_id"]][
            "calibrated_deep_fit_score_0_56"
        ]
        ingested_again, receipts_again = ingest_documents(
            work,
            ingested,
            [submission],
            accepted_at_utc="2026-10-07T04:00:00+00:00",
            repo_root=temp,
            canonical_results_root=temp / "data/cache/deep_stage2_results",
            receipts_root=temp / "data/cache/deep_stage2_ingest_receipts",
            stage1_loader=loader,
        )
        assert len(receipts_again) == 1
        assert ingested_again["entries"][item["calibration_work_id"]][
            "calibrated_deep_fit_score_0_56"
        ] == first_score
        assert ingested_again["entries"][item["calibration_work_id"]][
            "accepted_at_utc"
        ] == "2026-10-07T03:00:00+00:00"

    print("DEEP_STAGE2_CALIBRATION=PASS")


if __name__ == "__main__":
    main()

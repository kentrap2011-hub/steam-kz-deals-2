#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

from build_pre_ai_family_graph import resolve as resolve_family_graph
from story_dlc_scope import (
    NON_STORY_DLC_EXCLUDED,
    STORY_CONTENT_UNPROVEN_EXCLUDED,
    STORY_DLC_ELIGIBLE,
    classify_story_dlc,
    summarize_story_dlc_classifications,
)
from taste_steam_review_dossier_web import (
    build_daily_work_manifest_web,
    resolve_dossier_scope_identities,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "config/taste_steam_review_dossier_contract.json").read_text(encoding="utf-8"))
OFFER_CONTRACT = json.loads((ROOT / "config/offer_family_contract.json").read_text(encoding="utf-8"))
META = json.loads((ROOT / "data/production/pre_ai/content_metadata.json").read_text(encoding="utf-8"))["entries"]
QUEUE = [
    json.loads(line)
    for line in (ROOT / "data/production/pre_ai/chatgpt_taste_queue.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]


def _metadata(title, description):
    return {
        "store_name": title,
        "short_description": description,
        "app_type": "dlc",
        "metadata_source": "test_authoritative_product_metadata",
    }


def _base_row(appid, title):
    return {
        "family_id": f"game:{appid}",
        "taste_subject_key": f"App_{appid}",
        "appid": str(appid),
        "title": title,
        "taste_fingerprint": f"fp-{appid}",
        "candidate_context_sha256": f"ctx-{appid}",
        "work_required": ["evaluate_taste_fit"],
        "semantic_condition": {
            "ai_condition": "taste_subject_include_controls_purchase_family",
            "requires_ai_base_support": False,
            "base_appids": [str(appid)],
        },
    }



def _resolve_single_addon(appid, title, metadata):
    key = f"App_{appid}"
    feed = {key: {"appid": str(appid), "title": title}}
    store = {key: {
        "final_kzt": 1000,
        "discount_percent": 50,
        "discount_end_utc": "2026-09-20T00:00:00Z",
        "discount_end_europe_berlin": "2026-09-20T02:00:00+02:00",
    }}
    meta = {key: {**metadata, "store_name": title}}
    rules = {key: {
        "mechanical_kind": "dlc",
        "base_appid": "999999",
    }}
    families = resolve_family_graph({key}, feed, store, meta, rules, OFFER_CONTRACT)
    assert len(families) == 1
    return families[0]


def _assert_status(metadata, expected):
    got = classify_story_dlc(metadata)
    assert got["status"] == expected, got
    assert got["eligible"] is (expected == STORY_DLC_ELIGIBLE), got
    assert got["reason_code"]
    assert isinstance(got["evidence"], list) and got["evidence"]
    return got


def test_story_dlc_01_bg3_digital_deluxe_excluded():
    bg3_meta = META["App_2378500"]
    result = _assert_status(bg3_meta, NON_STORY_DLC_EXCLUDED)
    assert result["reason_code"] == "entitlement_or_upgrade_container_not_independent_story_content"
    assert any(e["signal"] == "digital_deluxe_or_upgrade" for e in result["evidence"])
    family = _resolve_single_addon("2378500", bg3_meta["store_name"], bg3_meta)
    assert family["family_type"] == "external_base_addon"
    assert family["taste_semantic_eligible"] is False
    assert family["addon_story_scope"][0]["classification"]["status"] == NON_STORY_DLC_EXCLUDED


def test_story_dlc_02_obvious_non_story_categories_excluded():
    fixtures = [
        _metadata("Example OST", "The original soundtrack in lossless audio."),
        _metadata("Example Digital Artbook", "A digital artbook with concept art."),
        _metadata("Example Cosmetic Pack", "Adds cosmetic skins and outfits."),
        _metadata("Example Weapon Pack", "Adds a weapon pack and equipment pack."),
        _metadata("Example Bonus Pack", "Includes bonus items and digital extras."),
        _metadata("Example Supporter Pack", "A supporter pack with bonus cosmetics."),
    ]
    for fixture in fixtures:
        _assert_status(fixture, NON_STORY_DLC_EXCLUDED)


def test_story_dlc_03_real_story_expansion_included():
    result = _assert_status(
        _metadata(
            "Example: The Lost Road",
            "A substantial expansion with a new story campaign and a new questline to play through.",
        ),
        STORY_DLC_ELIGIBLE,
    )
    assert result["reason_code"] == "positive_playable_narrative_content_confirmed"
    family = _resolve_single_addon("444", "Example: The Lost Road", _metadata(
        "Example: The Lost Road",
        "A substantial expansion with a new story campaign and a new questline to play through.",
    ))
    assert family["taste_semantic_eligible"] is True
    assert family["addon_story_scope"][0]["classification"]["status"] == STORY_DLC_ELIGIBLE


def test_story_dlc_04_ambiguous_dlc_fails_closed():
    result = _assert_status(
        _metadata(
            "Example Challenge Add-on",
            "Adds a new challenge map, a playable character and an extra game mode.",
        ),
        STORY_CONTENT_UNPROVEN_EXCLUDED,
    )
    assert result["reason_code"] == "positive_story_content_not_proven"
    title_only = _assert_status(
        _metadata("New Story Campaign DLC", "Adds content for the base game."),
        STORY_CONTENT_UNPROVEN_EXCLUDED,
    )
    assert title_only["reason_code"] == "positive_story_content_not_proven"


def test_story_dlc_05_mixed_story_and_cosmetics_included():
    result = _assert_status(
        _metadata(
            "Example Story Expansion",
            "Play an all-new story campaign with new quests, plus three bonus cosmetic outfits.",
        ),
        STORY_DLC_ELIGIBLE,
    )
    assert any(e["signal"] == "story_campaign" for e in result["evidence"])


def test_story_dlc_06_season_pass_container_does_not_inherit_child_story():
    result = _assert_status(
        _metadata(
            "Example Season Pass",
            "The Season Pass grants access to two story expansions, cosmetic packs and future DLC.",
        ),
        NON_STORY_DLC_EXCLUDED,
    )
    assert result["reason_code"] == "entitlement_or_upgrade_container_not_independent_story_content"
    assert any(e["signal"] == "season_pass_or_entitlement_container" for e in result["evidence"])


def test_story_dlc_07_base_game_dossier_scope_unchanged():
    rows = [_base_row(111, "Base Game")]
    resolved = resolve_dossier_scope_identities(rows, CONTRACT)
    assert [row["appid"] for row in resolved["rows"]] == ["111"]
    assert resolved["story_scope_excluded_items"] == []


def test_story_dlc_08_group_plan_regeneration_excludes_bg3():
    bg3 = next(row for row in QUEUE if str(row.get("appid")) == "2378500")
    # The stale/current input deliberately lacks the new positive story-scope
    # classification.  The dossier producer must fail closed even before the
    # upstream queue is regenerated.
    rows = [
        bg3,
        _base_row(111, "Base One"),
        _base_row(222, "Base Two"),
        _base_row(333, "Base Three"),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        manifest = build_daily_work_manifest_web(rows, CONTRACT, tmp)
    assert "2378500" not in manifest["ordered_appids"]
    assert manifest["story_scope_excluded_count"] == 1
    assert manifest["story_scope_excluded_items"][0]["appid"] == "2378500"
    assert manifest["story_scope_excluded_items"][0]["reason"] == "story_dlc_classification_missing_or_invalid"
    assert manifest["prepared_required_count"] == 3
    assert manifest["submission_group_plan"]["group_count"] == 1
    assert [item["appid"] for item in manifest["submission_group_plan"]["groups"][0]["items"]] == ["111", "222", "333"]


def test_machine_readable_summary():
    items = [
        {"key": "A", "appid": "1", "title": "Story", "classification": classify_story_dlc(
            _metadata("Story DLC", "Adds a new story campaign.")
        )},
        {"key": "B", "appid": "2", "title": "OST", "classification": classify_story_dlc(
            _metadata("OST", "Original soundtrack.")
        )},
        {"key": "C", "appid": "3", "title": "Unknown", "classification": classify_story_dlc(
            _metadata("Unknown DLC", "Adds a map.")
        )},
    ]
    summary = summarize_story_dlc_classifications(items)
    assert summary["dlc_like_items_considered"] == 3
    assert summary["story_eligible_count"] == 1
    assert summary["non_story_excluded_count"] == 1
    assert summary["ambiguous_unproven_excluded_count"] == 1


def main():
    tests = [
        test_story_dlc_01_bg3_digital_deluxe_excluded,
        test_story_dlc_02_obvious_non_story_categories_excluded,
        test_story_dlc_03_real_story_expansion_included,
        test_story_dlc_04_ambiguous_dlc_fails_closed,
        test_story_dlc_05_mixed_story_and_cosmetics_included,
        test_story_dlc_06_season_pass_container_does_not_inherit_child_story,
        test_story_dlc_07_base_game_dossier_scope_unchanged,
        test_story_dlc_08_group_plan_regeneration_excludes_bg3,
        test_machine_readable_summary,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"story DLC scope regressions passed: {len(tests)}")


if __name__ == "__main__":
    main()

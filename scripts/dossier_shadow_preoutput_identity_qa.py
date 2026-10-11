#!/usr/bin/env python3
"""INACTIVE offline identity/year pre-output gate. No semantics, I/O writes or web."""
import json
import re
from pathlib import Path

PIN = "95a4bf4990a60082ecb3302da5bc7f23b618d93e"
WORK_BLOB = "ef40fc186aabc79dfd24c72864dbe43817a56039"
AUDIT_BLOB = "8dbf4437d7ba439942f58a6f36d89d6a7ddeec7b"
EXPECTED = {
  1: ("d065f37a830c598eee13c64bd4190f0e9fc376ff55f8c98c436211a5a54e3770", "1119710 1202690 1409740"),
  2: ("ce045d5884ca86c85ef48ffbad989835bcfc1abb1fc448a80cb13f5e28f70509", "1430680 1438480 1507190"),
  3: ("f5c600719f68970cff87f5623cae9120f23b01de6b61e4e7f028485ffecd1d18", "1508750 1517180 1533420"),
  4: ("ed4bd0dc34f1ecaf9740c2f93fc8e16fcf9e36e57184a746b25e46fc2583883a", "1536090 1545560 1557740"),
  5: ("1c5236d29710206a6cfb6cacdfb0bbd5c298f3afd06d7a8933473a9e4236a3ce", "1562430 1574240 1574580"),
  6: ("56bad36fecb4dcb85ef3f7bbdf8bd11b9eb77e6050bcc806a1b35d1aa7fe6c4c", "1574820 1578220 1578650"),
  7: ("a5b678bb37fe44815416c137dfbf32ace8e5847bd57e32d384f95dbfb2d43ecf", "1582650 1583230 1583850"),
  8: ("4884c6ebcf1740d707e81290d735ba672f5cb5b2d2b582dcf46ce5e2f5ec4d3f", "1590230 1599600 1607130"),
  9: ("3e31472124818670fae658a3a923adacd0070c8ffec968931560c8a7c228db2a", "1620720 1627570 1638220"),
  10: ("97f462ddd60c60520bd81c0dafd7a3c6667bdc746efb94c8a5a522b6ec36f089", "1649080 1651560 1658150"),
  11: ("a549aa7960ef9b6417f29684a076441db6173e57a689fb0d74df4a5665efe0c6", "1681430 1740300 1808680"),
  12: ("c60e12c198b633f4e3d65895b07d281c0c44a6a0482966386a03881025fc014e", "1835240 1836160 1837330"),
  13: ("dea2dd46e0b65fa8db54e5a4f814144f27190bb99085b1c6493ea3c519f07995", "1849000 1857090 1868140"),
  14: ("b187c38e38c4cc84fb88a7dcbc880eb285192f4a223baebc8b5c8d98a798609c", "1898500 1939970 1948280"),
  15: ("7d4e60accd77c948e8b9dacd98278ba3754fb6f4827b0cbd84a8aefab64ff27f", "1999170 1999360 2009010"),
  16: ("36db2b3b84d8f0596d8a16618eae9df4dbf0347bc7575276edb5cb15a4144961", "2015240 201810 203750"),
  17: ("397f791ceb236b5c1a7145832e8640619f17aee32e093139ac72a7f54ab11f71", "204100 204300 2060130"),
  18: ("90b8b2fe89477ae02a3a7f91764979949d0a418200ba155c9ef05383d246f763", "206420 2067050 2076140"),
  20: ("d1eaa93cbf9c51851a12069d3b34506b09c39f304c1aac1ee3b7888bde395c99", "2124120 213610 2138710"),
  21: ("a94fb22ee386faaac05aa311dcee4dc338d90ead030195633772ed200730bf6b", "2140020 214950 220440"),
}
PRODUCT_DOMAINS = (
    "https://store.steampowered.com/app/",
    "https://sonic.sega.jp/",
    "https://www.sifugame.com/",
    "https://www.mobygames.com/game/",
    "https://fireflyworlds.com/",
    "https://steamdb.info/app/",
)
NEEDED_SOURCE_CATEGORIES = (
    "independent_player_source_parents",
    "russian_multilingual_source_metadata",
    "recent_older_undated_feedback_metadata",
    "negative_mixed_material_metadata",
    "gaps_revisits_exhaustion_metadata",
)


def inspect(payload):
    """Fail-closed structure and fact-kind guard, never grants approval."""
    errors = []
    source = payload.get("immutable_source", {})
    if (source.get("pinned_commit"), source.get("work_git_blob_sha"),
            source.get("audit_git_blob_sha")) != (PIN, WORK_BLOB, AUDIT_BLOB):
        errors.append("PIN_DRIFT")
    groups = payload.get("groups")
    if not isinstance(groups, list) or len(groups) != 20:
        return ["FRAME_NOT_EXACT_20_GROUPS"]
    seen = set()
    for expected_seq, group in zip(EXPECTED, groups):
        hash_, ids = EXPECTED[expected_seq]
        if group.get("sequence") != expected_seq or group.get("group_sha256") != hash_:
            errors.append("PINNED_ORIGINAL_GROUP_BINDING")
        games = group.get("games")
        if not isinstance(games, list) or len(games) != 3:
            errors.append("GROUP_SPLIT_OR_SIZE")
            continue
        if [g.get("appid") for g in games] != ids.split():
            errors.append("GROUP_SPLIT_OR_APPID_REBOUND")
        for game in games:
            appid = game.get("appid")
            if appid in seen:
                errors.append("DUPLICATE_APPID")
            seen.add(appid)
            if (not isinstance(game.get("work_title"), str)
                    or not game["work_title"]
                    or type(game.get("original_work_year_binding_claim")) is not int
                    or not 1970 <= game["original_work_year_binding_claim"] <= 2100
                    or game.get("steam_product_url") != "https://store.steampowered.com/app/" + str(appid) + "/"):
                errors.append("ORIGINAL_WORK_CLAIM_OR_APPID_INVALID")
            original = game.get("verified_original_work_year")
            store = game.get("verified_storefront_date")
            if original is not None and (type(original) is not int or not 1970 <= original <= 2100):
                errors.append("INVALID_ORIGINAL_WORK_YEAR")
            if store is not None and not re.fullmatch(r"20\d\d-\d\d-\d\d|19\d\d-\d\d-\d\d", str(store)):
                errors.append("INVALID_STOREFRONT_DATE")
            if game.get("date_unknown") is not (original is None or store is None):
                errors.append("UNKNOWN_CONVERTED_TO_KNOWN")
            if game.get("disagrees_with_old_binding"):
                if original is None or original == game["original_work_year_binding_claim"]:
                    errors.append("CLAIMED_CONFLICT_WITHOUT_POSITIVE_ORIGINAL_WORK_PROOF")
                if game.get("same_version_comparison") in ("not_verifiable", "edition_identity_unresolved", "not_comparable_distinct_definitive_edition"):
                    errors.append("DIFFERENT_VERSIONS_CALLED_CONFLICT")
            sources = game.get("public_sources", [])
            if not isinstance(sources, list) or any(
                not isinstance(s, dict) or not any(str(s.get("url", "")).startswith(prefix) for prefix in PRODUCT_DOMAINS)
                for s in sources
            ):
                errors.append("UNSAFE_OR_NONPRODUCT_PUBLIC_REFERENCE")
            if original is not None and not any(
                s.get("source_class") != "official_steam_store" for s in sources
            ):
                errors.append("ORIGINAL_YEAR_INFERRED_FROM_STORE_ONLY")
    if len(seen) != 60:
        errors.append("INCOMPLETE_60_APPIDS")
    if (payload.get("provisional_groups_from_pr205") != [3, 8, 13, 15, 18, 20]
            or payload.get("sample_proposed_only") is not True):
        errors.append("NONAUTHORITATIVE_PREVIEW_MUTATED")
    for forbidden in ("pilot_authorized", "quality_verified", "semantic_execution", "canonical_readiness", "deep_readiness"):
        if payload.get(forbidden) is not False:
            errors.append("INACTIVE_AUTHORITY_OVERRIDDEN")
    return sorted(set(errors))


def compatibility_check(payload, candidate_sequences, later_source_categories=None):
    """Advisory only. No pilot selector/authorization and NO Chat1 file reads."""
    errors = inspect(payload)
    groups_by_id = {g["sequence"]: g for g in payload.get("groups", []) if "sequence" in g}
    if not isinstance(candidate_sequences, list) or len(candidate_sequences) != 6 or len(set(candidate_sequences)) != 6:
        errors.append("SIX_GROUPS_OVERCLAIM")
    if any(seq not in groups_by_id for seq in candidate_sequences):
        errors.append("ORIGINAL_GROUP_SPLIT_OR_OUTSIDE_FRAME")
    proposed_games = [game for seq in candidate_sequences if seq in groups_by_id for game in groups_by_id[seq]["games"]]
    if len(proposed_games) != 18 or len({g["appid"] for g in proposed_games}) != 18:
        errors.append("EIGHTEEN_GAMES_OVERCLAIM")
    if any(g["date_unknown"] or g["edition_or_work_identity_ambiguity"] is not False or
           g["disagrees_with_old_binding"] is not False for g in proposed_games):
        errors.append("UNKNOWN_OR_CONFLICT_NEEDS_INDEPENDENT_ADJUDICATION")
    if later_source_categories is None:
        errors.append("CHAT1_SOURCE_METADATA_NOT_INDEPENDENTLY_DELIVERED")
        strata = {name: "not_measured" for name in NEEDED_SOURCE_CATEGORIES}
    else:
        strata = {name: later_source_categories.get(name, "not_measured")
                  for name in NEEDED_SOURCE_CATEGORIES}
        if any(value != "independently_verified_with_all_20_groups_accounted"
               for value in strata.values()):
            errors.append("PREOUTPUT_CATEGORY_ABSENT_OR_UNVERIFIED")
    available_groups = [g for g in payload["groups"]
                        if any(x["verified_original_work_year"] is not None and
                               x["verified_original_work_year"] < 2015 for x in g["games"])]
    if not available_groups:
        errors.append("NO_EXTERNALLY_CORROBORATED_HISTORIC_WORK_COVERAGE")
    if not any(g["verified_original_work_year"] is None for g in proposed_games):
        pass  # Verified groups alone still do not constitute approval.
    return {
        "state": "PREOUTPUT_DECISION_ONLY_NOT_READY_FOR_APPROVAL",
        "errors": sorted(set(errors)),
        "source_categories": strata,
        "groups_in_full_frozen_frame": 20,
        "proposed_group_count": len(candidate_sequences),
        "proposed_game_count": len(proposed_games),
        "sampling_unit": "whole_pinned_original_three_game_group",
        "sample_proposed_only": True,
        "pilot_authorized": False,
        "quality_verified": False,
        "semantic_execution": False,
    }


def main():
    path = Path(__file__).resolve().parents[1] / "reviews/dossier_shadow_preoutput/identity_year_20_groups_v1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(compatibility_check(payload, [3, 8, 13, 15, 18, 20]),
                     ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

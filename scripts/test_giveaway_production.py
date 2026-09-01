from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from giveaway_core import SourceCollection, SourceSchemaError, base_candidate, build_snapshot, classify_candidate, group_accepted_offers, iso_utc
from giveaway_epic import normalize_payload as normalize_epic
from giveaway_gog import normalize_product as normalize_gog
from giveaway_steam import normalize_candidate as normalize_steam

NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)

FIRST_PARTY_URLS = {
    "steam": "https://store.steampowered.com/app/10/",
    "epic": "https://store.epicgames.com/en-US/p/test-game",
    "gog": "https://www.gog.com/en/game/test_game",
}


def generic(source="steam", title="Test Game"):
    item = base_candidate(source, NOW)
    item.update({
        "source_product_id": f"{source}-1",
        "source_offer_id": f"{source}:offer:1",
        "title": title,
        "claim_url": FIRST_PARTY_URLS[source],
        "promotion_start_utc": iso_utc(NOW - timedelta(hours=1)),
        "promotion_end_utc": iso_utc(NOW + timedelta(days=2)),
        "promotion_type": "claim_to_keep",
        "ownership_semantics": "permanent_after_claim",
        "active_now_evidence": True,
        "explicit_giveaway_evidence": True,
        "base_price": 1000,
        "final_price": 0,
        "currency": "KZT",
        "discount_percent": 100,
        "region_status": "available",
        "content_type": "game",
        "requires_subscription": False,
        "access_expires_after_claim": False,
        "identity_publishers": ["Example Studio"],
    })
    return item


def collection(source_id, candidates, complete=True):
    return SourceCollection(source_id, candidates, complete, "ok" if complete else "failed", FIRST_PARTY_URLS[source_id], iso_utc(NOW), {}, None if complete else "SOURCE_ERROR", None if complete else "fixture failure")


class GiveawayTests(unittest.TestCase):
    def test_true_active_steam_claim_to_keep(self):
        row = {"appid": "10", "discount_percent": "100", "title": "Steam Gift"}
        payload = {"10": {"success": True, "data": {"name": "Steam Gift", "type": "game", "publishers": ["Example Studio"], "price_overview": {"initial": 2000, "final": 0, "currency": "KZT", "discount_percent": 100}}}}
        page = '<div data-discount-expiration="1788451200">Free to keep when you get it before September 4</div>'
        item = classify_candidate(normalize_steam(row, payload, page, NOW), NOW)
        self.assertEqual(item["classification_status"], "accepted")

    def test_true_active_epic_claim_to_keep(self):
        payload = {"data": {"Catalog": {"searchStore": {"elements": [{
            "id": "offer-1", "namespace": "namespace-1", "title": "Epic Gift", "offerType": "BASE_GAME",
            "seller": {"name": "Example Studio"},
            "price": {"totalPrice": {"originalPrice": 1999, "discountPrice": 0, "currencyCode": "KZT"}},
            "catalogNs": {"mappings": [{"pageSlug": "epic-gift"}]},
            "promotions": {"promotionalOffers": [{"promotionalOffers": [{"startDate": "2026-09-01T00:00:00Z", "endDate": "2026-09-08T00:00:00Z", "discountSetting": {"discountType": "PERCENTAGE", "discountPercentage": 0}}]}], "upcomingPromotionalOffers": []},
        }]}}}}
        items = normalize_epic(payload, NOW)
        self.assertEqual(len(items), 1)
        self.assertEqual(classify_candidate(items[0], NOW)["classification_status"], "accepted")

    def test_true_active_gog_claim_to_keep(self):
        product = {"id": 42, "title": "GOG Gift", "productType": "game", "slug": "gog_gift", "publishers": ["Example Studio"], "price": {"base": "29.99", "final": "0.00", "currency": "USD"}}
        page = '<script>{"promotionEndDate":"2026-09-07T12:00:00Z"}</script>'
        item = classify_candidate(normalize_gog(product, page, NOW), NOW)
        self.assertEqual(item["classification_status"], "accepted")

    def test_permanent_f2p_false_positive(self):
        item = generic()
        item.update({"promotion_type": "permanent_f2p", "base_price": 0, "explicit_giveaway_evidence": False})
        result = classify_candidate(item, NOW)
        self.assertEqual((result["classification_status"], result["classification_reason_codes"][0]), ("rejected", "PERMANENT_F2P"))

    def test_free_weekend_access_only_false_positive(self):
        item = generic()
        item.update({"promotion_type": "access_only", "ownership_semantics": "access_only", "access_expires_after_claim": True})
        result = classify_candidate(item, NOW)
        self.assertEqual(result["classification_reason_codes"], ["ACCESS_ONLY_FREE_WEEKEND"])

    def test_dlc_non_game_false_positive(self):
        item = generic()
        item["content_type"] = "dlc"
        result = classify_candidate(item, NOW)
        self.assertEqual(result["classification_reason_codes"], ["NON_GAME_CONTENT"])

    def test_upcoming_not_yet_active(self):
        item = generic()
        item["promotion_start_utc"] = iso_utc(NOW + timedelta(hours=1))
        result = classify_candidate(item, NOW)
        self.assertEqual(result["classification_reason_codes"], ["UPCOMING_NOT_ACTIVE"])

    def test_expired_offer(self):
        item = generic()
        item["promotion_end_utc"] = iso_utc(NOW - timedelta(seconds=1))
        result = classify_candidate(item, NOW)
        self.assertEqual(result["classification_reason_codes"], ["PROMOTION_EXPIRED"])

    def test_unknown_kz_region(self):
        item = generic()
        item["region_status"] = "unknown"
        result = classify_candidate(item, NOW)
        self.assertEqual((result["classification_status"], result["classification_reason_codes"][0]), ("unverified", "KZ_REGION_UNKNOWN"))

    def test_epic_source_schema_failure(self):
        with self.assertRaises(SourceSchemaError):
            normalize_epic({"data": {}}, NOW)

    def test_unknown_ownership_semantics(self):
        item = generic()
        item["ownership_semantics"] = "unknown"
        result = classify_candidate(item, NOW)
        self.assertEqual((result["classification_status"], result["classification_reason_codes"][0]), ("unverified", "OWNERSHIP_SEMANTICS_UNKNOWN"))

    def test_same_logical_game_groups_without_offer_loss(self):
        steam = classify_candidate(generic("steam", "Shared Game"), NOW)
        epic = classify_candidate(generic("epic", "Shared Game"), NOW)
        groups = group_accepted_offers([steam, epic])
        self.assertEqual(len(groups), 1)
        self.assertEqual({x["source_id"] for x in groups[0]["offers"]}, {"steam", "epic"})

    def test_similar_titles_do_not_merge(self):
        first = classify_candidate(generic("steam", "Portal 2"), NOW)
        second = classify_candidate(generic("epic", "Portal II"), NOW)
        self.assertEqual(len(group_accepted_offers([first, second])), 2)

    def test_required_source_failure_marks_snapshot_incomplete(self):
        collections = {
            "steam": collection("steam", [generic("steam")]),
            "epic": collection("epic", [generic("epic")]),
            "gog": collection("gog", [], complete=False),
        }
        snapshot, _ = build_snapshot(collections, NOW)
        self.assertEqual(snapshot["snapshot_status"], "incomplete")
        self.assertFalse(snapshot["source_health"]["gog"]["complete"])

    def test_stale_offer_not_retained_beyond_deadline(self):
        expired = generic("steam", "Expired")
        expired["promotion_end_utc"] = iso_utc(NOW - timedelta(minutes=1))
        collections = {source: collection(source, [expired] if source == "steam" else []) for source in ("steam", "epic", "gog")}
        snapshot, audit = build_snapshot(collections, NOW)
        self.assertEqual(snapshot["accepted_offer_count"], 0)
        self.assertEqual(snapshot["games"], [])
        self.assertEqual(audit[0]["classification_reason_codes"], ["PROMOTION_EXPIRED"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from giveaway_core import SourceCollection, SourceSchemaError, base_candidate, iso_utc, parse_iso, source_offer_key
from giveaway_http import get_json

ENDPOINT = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
PARAMS = {"locale": "en-US", "country": "KZ", "allowCountries": "KZ"}


def _store_slug(element: dict[str, Any]) -> str | None:
    catalog_ns = element.get("catalogNs")
    if isinstance(catalog_ns, dict):
        mappings = catalog_ns.get("mappings")
        if isinstance(mappings, list):
            for mapping in mappings:
                if isinstance(mapping, dict) and mapping.get("pageSlug"):
                    return str(mapping["pageSlug"])
    for key in ("productSlug", "urlSlug"):
        value = element.get(key)
        if isinstance(value, str) and value.strip() and value != "[]":
            return value.strip().strip("/")
    return None


def _promotion_rows(element: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    promotions = element.get("promotions")
    if promotions is None:
        return []
    if not isinstance(promotions, dict):
        raise SourceSchemaError("Epic promotions field changed type")

    result: list[tuple[str, dict[str, Any]]] = []
    for state, key in (("current", "promotionalOffers"), ("upcoming", "upcomingPromotionalOffers")):
        blocks = promotions.get(key) or []
        if not isinstance(blocks, list):
            raise SourceSchemaError(f"Epic {key} changed type")
        for block in blocks:
            if not isinstance(block, dict) or not isinstance(block.get("promotionalOffers"), list):
                raise SourceSchemaError(f"Epic {key} block schema changed")
            for offer in block["promotionalOffers"]:
                if not isinstance(offer, dict):
                    raise SourceSchemaError("Epic promotional offer changed type")
                result.append((state, offer))
    return result


def _current_free_promotion_rows(
    element: dict[str, Any], observed: datetime
) -> list[tuple[dict[str, Any], datetime, datetime]]:
    result: list[tuple[dict[str, Any], datetime, datetime]] = []
    for state, promo in _promotion_rows(element):
        if state != "current":
            continue

        start = parse_iso(promo.get("startDate"))
        end = parse_iso(promo.get("endDate"))
        if start is None or end is None:
            raise SourceSchemaError("Epic promotion dates missing or unparseable")
        if observed < start or observed >= end:
            continue

        discount_setting = promo.get("discountSetting")
        if not isinstance(discount_setting, dict):
            raise SourceSchemaError("Epic promotion discountSetting schema changed")
        discount_percentage = discount_setting.get("discountPercentage")
        if not isinstance(discount_percentage, int) or isinstance(discount_percentage, bool):
            raise SourceSchemaError("Epic promotion discountPercentage schema changed")
        if discount_percentage == 0:
            result.append((promo, start, end))

    return result


def _required_price_int(total: dict[str, Any], key: str) -> int:
    value = total.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise SourceSchemaError(f"Epic price.totalPrice.{key} schema changed")
    return value


def normalize_payload(payload: Any, observed: datetime) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise SourceSchemaError("Epic response is not an object")
    data = payload.get("data")
    catalog = data.get("Catalog") if isinstance(data, dict) else None
    search_store = catalog.get("searchStore") if isinstance(catalog, dict) else None
    elements = search_store.get("elements") if isinstance(search_store, dict) else None
    if not isinstance(elements, list):
        raise SourceSchemaError("Epic data.Catalog.searchStore.elements missing")

    candidates: list[dict[str, Any]] = []
    for element in elements:
        if not isinstance(element, dict):
            raise SourceSchemaError("Epic element is not an object")
        required = ("id", "namespace", "title", "offerType")
        if any(key not in element for key in required):
            raise SourceSchemaError("Epic element required fields changed")

        current_free_promotions = _current_free_promotion_rows(element, observed)
        if not current_free_promotions:
            continue

        price = element.get("price")
        if not isinstance(price, dict):
            raise SourceSchemaError("Epic price schema changed")
        total = price.get("totalPrice")
        if not isinstance(total, dict):
            raise SourceSchemaError("Epic price.totalPrice schema changed")
        discount_price = _required_price_int(total, "discountPrice")
        original_price = _required_price_int(total, "originalPrice")
        if discount_price != 0:
            raise SourceSchemaError("Epic current 100% promotion has non-zero discountPrice")
        if original_price < 0:
            raise SourceSchemaError("Epic price.totalPrice.originalPrice is negative")

        namespace = str(element["namespace"])
        offer_id = str(element["id"])
        title = str(element["title"])
        slug = _store_slug(element)
        publishers = []
        seller = element.get("seller")
        if isinstance(seller, dict) and seller.get("name"):
            publishers.append(str(seller["name"]))

        for _promo, start, end in current_free_promotions:
            item = base_candidate("epic", observed)
            item.update({
                "source_product_id": f"{namespace}:{offer_id}",
                "source_offer_id": source_offer_key("epic", f"{namespace}:{offer_id}", iso_utc(end), iso_utc(start)),
                "title": title,
                "claim_url": f"https://store.epicgames.com/en-US/p/{slug}" if slug else None,
                "promotion_start_utc": iso_utc(start),
                "promotion_end_utc": iso_utc(end),
                "base_price": original_price,
                "final_price": discount_price,
                "currency": total.get("currencyCode"),
                "discount_percent": 100 if discount_price == 0 and original_price > 0 else None,
                "region_status": "available",
                "region_evidence": {"requested_country": "KZ", "allowCountries": "KZ", "endpoint_returned_offer": True},
                "content_type": "game" if str(element.get("offerType")) == "BASE_GAME" else "other",
                "requires_subscription": False,
                "access_expires_after_claim": False,
                "identity_publishers": publishers,
                "source_provenance": {
                    "endpoint": ENDPOINT,
                    "params": PARAMS,
                    "namespace": namespace,
                    "epic_offer_id": offer_id,
                    "promotion_state_array": "current",
                    "offer_type": element.get("offerType"),
                },
            })

            if "mystery game" in title.casefold() or title.strip().casefold() == "mystery game":
                item["precheck_reason"] = "MYSTERY_PLACEHOLDER"
            elif item["content_type"] != "game":
                item["precheck_reason"] = "NON_GAME_CONTENT"
            elif original_price <= 0:
                item["promotion_type"] = "permanent_f2p"
            else:
                item["promotion_type"] = "claim_to_keep"
                item["ownership_semantics"] = "permanent_after_claim"
                item["active_now_evidence"] = True
                item["explicit_giveaway_evidence"] = True

            candidates.append(item)

    return candidates


def collect(session: requests.Session, now: datetime) -> SourceCollection:
    payload = get_json(session, ENDPOINT, PARAMS)
    candidates = normalize_payload(payload, now)
    return SourceCollection(
        source_id="epic",
        candidates=candidates,
        complete=True,
        status="ok",
        endpoint=ENDPOINT,
        observed_at_utc=iso_utc(now) or "",
        details={
            "country": "KZ",
            "allowCountries": "KZ",
            "candidate_count": len(candidates),
            "schema_guard": "strict",
            "api_stability": "undocumented_storefront_backend",
        },
    )

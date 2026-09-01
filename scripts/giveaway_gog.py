from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

import requests

from giveaway_core import SourceCollection, SourceSchemaError, base_candidate, iso_utc, parse_iso, safe_number, source_offer_key
from giveaway_http import get_json, get_text, html_to_text

ENDPOINT = "https://catalog.gog.com/v1/catalog"
BASE_PARAMS = {
    "limit": 48,
    "order": "desc:score",
    "productType": "in:game,pack",
    "discounted": "eq:true",
    "price": "between:0,0",
    "countryCode": "KZ",
}
MAX_PAGES = 5


def _price_value(price: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = price.get(key)
        if isinstance(value, dict):
            for subkey in ("amount", "value"):
                parsed = safe_number(value.get(subkey))
                if parsed is not None:
                    return parsed
        parsed = safe_number(value)
        if parsed is not None:
            return parsed
    return None


def _claim_url(product: dict[str, Any]) -> str | None:
    for key in ("storeLink", "url"):
        value = product.get(key)
        if isinstance(value, str) and value.strip():
            return urljoin("https://www.gog.com", value.strip())
    slug = product.get("slug")
    if isinstance(slug, str) and slug.strip():
        return f"https://www.gog.com/en/game/{slug.strip()}"
    return None


def _promotion_end_from_html(raw_html: str) -> datetime | None:
    patterns = (
        r'(?i)["\'](?:promotionEnd|promotionEndDate|discountEnd|discountEndDate|endDate|endTime)["\']\s*[:=]\s*["\']([^"\']+)["\']',
        r'(?i)offer\s+ends[^<]{0,80}<[^>]*datetime=["\']([^"\']+)["\']',
        r'(?i)datetime=["\']([^"\']+)["\'][^>]*>[^<]{0,80}offer\s+ends',
    )
    for pattern in patterns:
        for match in re.finditer(pattern, raw_html or ""):
            parsed = parse_iso(match.group(1))
            if parsed is not None:
                return parsed

    text = html_to_text(raw_html)
    match = re.search(
        r"(?i)Offer\s+ends(?:\s+on)?\s*:?\s*([A-Z][a-z]+\s+\d{1,2},\s+\d{4}(?:\s+\d{1,2}:\d{2})?)",
        text,
    )
    if match:
        for fmt in ("%B %d, %Y %H:%M", "%B %d, %Y"):
            try:
                return datetime.strptime(match.group(1), fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                pass
    return None


def normalize_product(product: dict[str, Any], page_html: str, observed: datetime) -> dict[str, Any]:
    if not isinstance(product, dict) or "id" not in product or "title" not in product or "price" not in product:
        raise SourceSchemaError("GOG product required fields changed")
    price = product.get("price")
    if not isinstance(price, dict):
        raise SourceSchemaError("GOG product price changed type")

    product_id = str(product["id"])
    product_type = str(product.get("productType") or product.get("type") or "unknown").casefold()
    base_price = _price_value(price, "base", "baseMoney", "full", "regular")
    final_price = _price_value(price, "final", "finalMoney", "discounted", "amount")
    currency = price.get("currency") or (price.get("finalMoney") or {}).get("currency") if isinstance(price.get("finalMoney"), dict) else price.get("currency")
    claim_url = _claim_url(product)
    deadline = _promotion_end_from_html(page_html)

    item = base_candidate("gog", observed)
    item.update({
        "source_product_id": product_id,
        "source_offer_id": source_offer_key("gog", product_id, iso_utc(deadline)),
        "title": str(product["title"]),
        "claim_url": claim_url,
        "promotion_end_utc": iso_utc(deadline),
        "base_price": base_price,
        "final_price": final_price,
        "currency": currency,
        "discount_percent": 100 if final_price == 0 and (base_price or 0) > 0 else None,
        "region_status": "available",
        "region_evidence": {"requested_country": "KZ", "catalog_returned_product": True},
        "content_type": "game" if product_type == "game" else ("complete_edition" if product_type == "pack" else "other"),
        "requires_subscription": False,
        "access_expires_after_claim": False,
        "identity_publishers": [str(x) for x in (product.get("publishers") or []) if x] if isinstance(product.get("publishers"), list) else [],
        "source_provenance": {
            "endpoint": ENDPOINT,
            "countryCode": "KZ",
            "catalog_product_id": product_id,
            "product_type": product_type,
            "store_page": claim_url,
            "temporal_evidence": "first-party product page deadline" if deadline else "missing",
        },
    })

    if item["content_type"] not in {"game", "complete_edition"}:
        item["precheck_reason"] = "NON_GAME_CONTENT"
    elif final_price is None:
        item["precheck_reason"] = "FINAL_PRICE_UNKNOWN"
    elif final_price != 0:
        item["precheck_reason"] = "NOT_ZERO_PRICE"
    elif base_price is None or base_price <= 0:
        item["promotion_type"] = "permanent_f2p"
    elif deadline is None:
        item["promotion_type"] = "claim_to_keep"
        item["ownership_semantics"] = "permanent_after_claim"
        item["explicit_giveaway_evidence"] = True
        item["active_now_evidence"] = True
    elif observed >= deadline:
        item["precheck_reason"] = "PROMOTION_EXPIRED"
    else:
        item["promotion_type"] = "claim_to_keep"
        item["ownership_semantics"] = "permanent_after_claim"
        item["explicit_giveaway_evidence"] = True
        item["active_now_evidence"] = True

    return item


def normalize_catalog_payload(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("products"), list):
        raise SourceSchemaError("GOG products array missing")
    products = payload["products"]
    for product in products:
        if not isinstance(product, dict):
            raise SourceSchemaError("GOG product row changed type")
    return products


def collect(session: requests.Session, now: datetime) -> SourceCollection:
    products: list[dict[str, Any]] = []
    pages_fetched = 0
    seen_ids: set[str] = set()

    for page in range(1, MAX_PAGES + 1):
        params = dict(BASE_PARAMS)
        params["page"] = page
        payload = get_json(session, ENDPOINT, params)
        batch = normalize_catalog_payload(payload)
        pages_fetched += 1
        for product in batch:
            product_id = str(product.get("id"))
            if product_id not in seen_ids:
                products.append(product)
                seen_ids.add(product_id)
        if len(batch) < int(BASE_PARAMS["limit"]):
            break
    else:
        raise SourceSchemaError(f"GOG zero-price discounted candidate set exceeded bounded {MAX_PAGES}-page scan")

    candidates: list[dict[str, Any]] = []
    validation_errors = 0
    for product in products:
        claim_url = _claim_url(product)
        if not claim_url:
            candidates.append(normalize_product(product, "", now))
            continue
        try:
            page_html = get_text(session, claim_url, {"countryCode": "KZ"})
            candidates.append(normalize_product(product, page_html, now))
        except Exception as exc:
            validation_errors += 1
            item = normalize_product(product, "", now)
            item["source_provenance"]["validation_error"] = str(exc)
            candidates.append(item)

    complete = validation_errors == 0
    return SourceCollection(
        source_id="gog",
        candidates=candidates,
        complete=complete,
        status="ok" if complete else "degraded",
        endpoint=ENDPOINT,
        observed_at_utc=iso_utc(now) or "",
        details={
            "countryCode": "KZ",
            "pages_fetched": pages_fetched,
            "candidate_count": len(candidates),
            "targeted_validation_errors": validation_errors,
            "schema_guard": "strict",
            "api_stability": "undocumented_storefront_backend",
        },
        error_code=None if complete else "SOURCE_VALIDATION_FETCH_FAILED",
        error=None if complete else f"{validation_errors} GOG product page validation request(s) failed",
    )

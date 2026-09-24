#!/usr/bin/env python3
"""Strict V2 validation for neutral multi-source web-evidence Taste dossiers."""
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from taste_steam_review_dossier import (
    _validate_no_raw_or_personal_payload,
    canonical_sha256,
    parse_utc,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = ROOT / "config/taste_steam_review_dossier_schema.json"
DEFAULT_EVIDENCE_CONTRACT_PATH = ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json"
DEFAULT_WORKER_PROMPT_PATH = ROOT / "config/taste_steam_review_dossier_worker_prompt.md"
_DOMAIN_RE = re.compile(r"^[a-z0-9.-]+$")
_RAW_BODY_LIKE_KEYS = {
    "raw_reviews", "review_text", "review_body", "review_bodies", "reviews_raw",
    "raw_text", "body", "post_body", "comment_body", "source_text", "content_text",
    "snippet", "excerpt", "quote", "quotes", "full_text", "full_review", "review",
    "usernames", "authors",
}
_RECURRENCE_RANK = {"anecdotal": 1, "limited": 2, "moderate": 3, "strong": 4}
_TRACKING_QUERY_KEYS = {
    "fbclid", "gclid", "mc_cid", "mc_eid", "ref", "referrer", "source", "share",
    "share_id", "tracking", "tracking_id",
}
_ITEM_QUERY_KEYS = {
    "comment", "comment_id", "commentid", "entry", "entry_id", "id", "item", "item_id",
    "post", "post_id", "postid", "recommendationid", "review", "review_id", "reviewid",
    "thread", "thread_id", "threadid",
}
_GENERIC_COLLECTION_BASENAMES = {
    "community", "comments", "discussion", "discussions", "forum", "forums", "index", "list",
    "listing", "posts", "review", "reviews", "search",
}
_STABLE_PUBLIC_REF_TOKEN_RE = re.compile(
    r"(?:^|[\s:/#_-])(?:review|recommendation|post|comment|contribution|entry|item|record|discussion|thread)"
    r"[:#/_-][a-z0-9][a-z0-9._:-]{1,}",
    re.IGNORECASE,
)
_MACHINE_PUBLIC_REF_RE = re.compile(r"^[a-z0-9][a-z0-9._:/#-]{2,}$", re.IGNORECASE)
_SOURCE_ID_RE = re.compile(r"^source-[0-9]{3}$")
_STABLE_FEEDBACK_ID_RE = re.compile(r"^feedback-[0-9]{3}$")
_FALLBACK_FEEDBACK_ID_RE = re.compile(r"^fallback-[0-9]{3}$")
_FALLBACK_FORBIDDEN_AUTHOR_KEYS = {
    "username", "displayname", "author", "authorid", "userid", "steamid",
    "steamaccountid", "accountid", "profile", "profileid", "profileurl",
    "vanityid", "vanityurl", "reviewer", "reviewerid",
}


def load_worker_schema(path=DEFAULT_SCHEMA_PATH):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if (
        doc.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2"
        or type(doc.get("version")) is not int
        or doc.get("version") != 2
        or doc.get("status") != "active"
        or doc.get("dossier_schema") != "TASTE-STEAM-REVIEW-DOSSIER-V2"
        or doc.get("dossier_schema_version") != 2
    ):
        raise ValueError("worker-facing dossier schema is missing, stale or unsupported")
    return doc


def load_web_evidence_contract(path=DEFAULT_EVIDENCE_CONTRACT_PATH):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if (
        doc.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2"
        or type(doc.get("version")) is not int
        or doc.get("version") != 2
        or doc.get("status") != "active"
    ):
        raise ValueError("web evidence dossier contract is missing, stale or unsupported")
    return doc


def current_worker_contract_binding(schema_doc=None, evidence_contract=None, *, worker_prompt_text=None):
    """Content-complete semantic compatibility binding for snapshot/cache/worker projection use."""
    schema_doc = schema_doc or load_worker_schema()
    evidence_contract = evidence_contract or load_web_evidence_contract()
    prompt_text = (
        DEFAULT_WORKER_PROMPT_PATH.read_text(encoding="utf-8")
        if worker_prompt_text is None
        else str(worker_prompt_text)
    )
    return {
        "evidence_contract_schema": evidence_contract["schema"],
        "evidence_contract_version": evidence_contract["version"],
        "evidence_contract_revision": evidence_contract.get("contract_revision"),
        "evidence_contract_sha256": canonical_sha256(evidence_contract),
        "worker_schema": schema_doc["schema"],
        "worker_schema_version": schema_doc["version"],
        "worker_schema_revision": schema_doc.get("schema_revision"),
        "worker_schema_sha256": canonical_sha256(schema_doc),
        "dossier_schema": schema_doc["dossier_schema"],
        "dossier_schema_version": schema_doc["dossier_schema_version"],
        "worker_prompt_revision": evidence_contract["worker_prompt_revision"],
        "worker_prompt_sha256": hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
    }


def _json_int(value):
    return type(value) is int


def _feedback_identity_mode(record):
    return str(record.get("identity_mode") or "stable_locator")


def _is_profile_scoped_url(value, evidence_contract):
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    policy = evidence_contract["compact_provenance"]
    path = parsed.path or "/"
    if any(re.search(pattern, path, flags=re.IGNORECASE) for pattern in policy["forbidden_profile_url_path_regexes"]):
        return True
    forbidden_query = {key.casefold() for key in policy["forbidden_profile_url_query_keys"]}
    return any(key.casefold() in forbidden_query for key, _ in parse_qsl(parsed.query, keep_blank_values=True))


def _validate_no_fallback_author_identity_payload(dossier, evidence_contract):
    """Fail closed on author/profile identity fields once fallback serialization is used."""
    for path, key, value in _walk(dossier):
        normalized_key = re.sub(r"[^a-z0-9]", "", str(key).casefold())
        if normalized_key in _FALLBACK_FORBIDDEN_AUTHOR_KEYS:
            raise ValueError(f"fallback dossier contains forbidden author identity field at {path}.{key}")
        if isinstance(value, str) and value.lower().startswith(("http://", "https://")):
            if _is_profile_scoped_url(value, evidence_contract):
                raise ValueError(f"fallback dossier contains forbidden author/profile URL at {path}.{key}")


def _validate_recurrence_identity_strength(recurrence, records, schema_doc, label):
    stable_count = sum(_feedback_identity_mode(record) == "stable_locator" for record in records)
    strength = schema_doc["observation_invariants"]["recurrence_identity_strength"]
    if recurrence == "moderate" and stable_count < int(strength["stable_locator_moderate_minimum"]):
        raise ValueError(f"{label} moderate recurrence requires at least three stable-locator records")
    if recurrence == "strong" and stable_count < int(strength["stable_locator_strong_minimum"]):
        raise ValueError(f"{label} strong recurrence requires at least five stable-locator records")


def _require_fields(obj, fields, label):
    if not isinstance(obj, dict):
        raise ValueError(f"{label} must be an object")
    missing = [field for field in fields if field not in obj]
    if missing:
        raise ValueError(f"{label} is missing required fields: {', '.join(missing)}")


def _walk(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield path, key, child
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _validate_no_raw_body_like_payload(dossier):
    for path, key, _ in _walk(dossier):
        if str(key).lower() in _RAW_BODY_LIKE_KEYS:
            raise ValueError(f"raw review/post body-like field is forbidden at {path}.{key}")


def _normalize_domain(value):
    text = str(value or "").strip().lower().rstrip(".")
    if text.startswith("www."):
        text = text[4:]
    return text


def _source_ref(source):
    url = source.get("url")
    public_ref = source.get("public_ref")
    if bool(url) == bool(public_ref):
        raise ValueError("provenance record must contain exactly one of url or public_ref")
    return str(url or public_ref)


def _canonical_url_identity(value):
    parsed = urlparse(str(value))
    host = _normalize_domain(parsed.hostname)
    path = re.sub(r"/+", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    query = []
    for key, val in parse_qsl(parsed.query, keep_blank_values=True):
        normalized_key = key.strip().lower()
        if normalized_key.startswith("utm_") or normalized_key in _TRACKING_QUERY_KEYS:
            continue
        query.append((normalized_key, val.strip()))
    query.sort()
    return urlunparse(("https", host, path, "", urlencode(query, doseq=True), ""))


def _normalized_public_ref(value):
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


def _source_locator_identity(source):
    if source.get("url"):
        return "url:" + _canonical_url_identity(source["url"])
    return f"public:{_normalize_domain(source.get('domain'))}:{_normalized_public_ref(source.get('public_ref'))}"


def _has_stable_public_item_ref(value):
    text = str(value or "").strip()
    if not text:
        return False
    if _STABLE_PUBLIC_REF_TOKEN_RE.search(text):
        return True
    if not any(ch.isdigit() for ch in text):
        return False
    return bool(_MACHINE_PUBLIC_REF_RE.fullmatch(text) and any(sep in text for sep in ("-", ":", "/", "#")))


def _has_item_level_url_locator(url, source):
    parsed = urlparse(str(url))
    path = re.sub(r"/+", "/", parsed.path or "/").rstrip("/") or "/"
    lower_path = path.casefold()
    query = {key.casefold(): val for key, val in parse_qsl(parsed.query, keep_blank_values=True)}
    if any(key in _ITEM_QUERY_KEYS and str(val).strip() for key, val in query.items()):
        return True
    source_type = source.get("source_type")
    if source_type in {"steam_reviews", "steam_community"}:
        if re.fullmatch(r"/app/[0-9]+/(?:reviews?|discussions?)", lower_path):
            return False
        if re.search(r"/discussions/[0-9]+/[a-z0-9_-]+(?:/|$)", lower_path):
            return True
    if source_type == "reddit":
        if lower_path == "/search" or re.fullmatch(r"/r/[^/]+", lower_path):
            return False
        if re.search(r"/comments/[a-z0-9]+(?:/|$)", lower_path):
            return True
    segments = [segment for segment in lower_path.split("/") if segment]
    if not segments:
        return False
    if segments[-1] in _GENERIC_COLLECTION_BASENAMES:
        return False
    if "search" in segments:
        return False
    return True


def _feedback_item_identity(record, source, label):
    if record.get("url"):
        if not _has_item_level_url_locator(record["url"], source):
            raise ValueError(f"{label}.url must identify one attributable feedback item, not a collection/search/index surface")
        return "url:" + _canonical_url_identity(record["url"])
    public_ref = record.get("public_ref")
    if not _has_stable_public_item_ref(public_ref):
        raise ValueError(f"{label}.public_ref must contain a stable non-identifying feedback item locator")
    return f"public:{_normalize_domain(source.get('domain'))}:{_normalized_public_ref(public_ref)}"


def _reddit_locator_parts(url):
    if not url:
        return None, None
    parsed = urlparse(str(url))
    if _normalize_domain(parsed.hostname) != "reddit.com":
        return None, None
    segments = [segment.casefold() for segment in re.sub(r"/+", "/", parsed.path or "/").split("/") if segment]
    subreddit = None
    thread_id = None
    if "r" in segments:
        index = segments.index("r")
        if index + 1 < len(segments):
            subreddit = segments[index + 1]
    if "comments" in segments:
        index = segments.index("comments")
        if index + 1 < len(segments):
            thread_id = segments[index + 1]
    return subreddit, thread_id


def _public_ref_surface(value):
    text = _normalized_public_ref(value)
    if not text:
        return None
    if re.match(r"^steam-(?:review|recommendation)(?::|-)", text):
        return "steam_review"
    if re.match(r"^steam-discussion(?::|-)", text):
        return "steam_discussion"
    if re.match(r"^reddit-(?:comment|post|thread)(?::|-)", text):
        return "reddit"
    return None


def _url_surface(value):
    if not value:
        return None
    parsed = urlparse(str(value))
    host = _normalize_domain(parsed.hostname)
    path = re.sub(r"/+", "/", parsed.path or "/").casefold()
    if host == "reddit.com":
        return "reddit"
    if host == "steamcommunity.com":
        if "/discussions/" in path or path.rstrip("/").endswith("/discussions"):
            return "steam_discussion"
        if "/reviews/" in path or path.rstrip("/").endswith("/reviews"):
            return "steam_review"
    return None


def _record_surface(record):
    return _url_surface(record.get("url")) or _public_ref_surface(record.get("public_ref"))


def _source_surface(source):
    surface = _url_surface(source.get("url")) or _public_ref_surface(source.get("public_ref"))
    if surface:
        return surface
    if source.get("source_type") == "reddit":
        return "reddit"
    if source.get("source_type") == "steam_reviews":
        return "steam_review"
    return None


def _validate_parent_item_relationship(record, source, label):
    source_type = source.get("source_type")
    parent_surface = _source_surface(source)
    child_surface = _record_surface(record)

    if source_type == "reddit":
        if child_surface and child_surface != "reddit":
            raise ValueError(f"{label} feedback item surface conflicts with its Reddit parent source")
        if record.get("url") and source.get("url"):
            parent_subreddit, parent_thread = _reddit_locator_parts(source["url"])
            child_subreddit, child_thread = _reddit_locator_parts(record["url"])
            if parent_subreddit and child_subreddit and parent_subreddit != child_subreddit:
                raise ValueError(f"{label} child Reddit item does not belong to its parent Reddit source locator")
            if parent_thread and child_thread and parent_thread != child_thread:
                raise ValueError(f"{label} child Reddit item does not belong to its parent Reddit thread")
        return

    if child_surface == "reddit" and source_type != "reddit":
        raise ValueError(f"{label} Reddit feedback item cannot use a non-Reddit parent source")

    if source_type == "steam_reviews" and child_surface == "steam_discussion":
        raise ValueError(f"{label} Steam discussion item cannot use an explicit Steam reviews parent source")
    if source_type in {"community_discussion"} and child_surface == "steam_review":
        raise ValueError(f"{label} Steam review item cannot use an explicit discussion parent source")
    if parent_surface in {"steam_review", "steam_discussion"} and child_surface in {"steam_review", "steam_discussion"}:
        if parent_surface != child_surface:
            raise ValueError(f"{label} Steam feedback item surface conflicts with its parent source locator")
    parent_discussion = _steam_discussion_locator_parts(source)
    child_discussion = _steam_discussion_locator_parts(record)
    if parent_discussion and child_discussion:
        for component in ("appid", "forum", "thread"):
            parent_value = parent_discussion.get(component)
            child_value = child_discussion.get(component)
            if parent_value is not None and child_value is not None and parent_value != child_value:
                raise ValueError(
                    f"{label} Steam feedback item does not belong to its parent Steam discussion/container"
                )


def _validate_publication_date(value, generated_date, label):
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}.publication_date must be YYYY-MM-DD or null")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label}.publication_date must be YYYY-MM-DD or null") from exc
    if parsed > generated_date + timedelta(days=1):
        raise ValueError(f"{label}.publication_date cannot be materially future-dated")
    return parsed


def _validate_dated_freshness(publication_date, freshness, generated_date, evidence_contract, label):
    if publication_date is None:
        return
    threshold = int(evidence_contract["recency"]["recent_max_age_days"])
    age_days = (generated_date - publication_date).days
    expected = "recent" if age_days <= threshold else "older"
    if freshness != expected:
        raise ValueError(
            f"{label}.freshness is incoherent with publication_date: expected {expected} at {age_days} days old"
        )


def _is_steam_store_app_page(source):
    if _normalize_domain(source.get("domain")) != "store.steampowered.com" or not source.get("url"):
        return False
    parsed = urlparse(source["url"])
    return bool(re.match(r"^/app/[0-9]+(?:/|$)", parsed.path or ""))


def _steam_appid_from_url(value):
    if not value:
        return None
    parsed = urlparse(str(value))
    if _normalize_domain(parsed.hostname) not in {"steamcommunity.com", "store.steampowered.com"}:
        return None
    match = re.match(r"^/app/([0-9]+)(?:/|$)", parsed.path or "")
    return match.group(1) if match else None


def _steam_appid_from_public_ref(value):
    text = _normalized_public_ref(value)
    if not text:
        return None
    for pattern in (
        r"^steam-(?:review|recommendation|discussion):app(?:id)?[-:=]([0-9]+)(?:[:/#_-]|$)",
        r"^steam-app[-:=]([0-9]+)(?:[:/#_-]|$)",
    ):
        match = re.match(pattern, text)
        if match:
            return match.group(1)
    return None


def _steam_appid_from_record(record):
    return _steam_appid_from_url(record.get("url")) or _steam_appid_from_public_ref(record.get("public_ref"))


def _steam_discussion_locator_parts(record):
    """Return only deterministically exposed Steam discussion/container components."""
    value = record.get("url")
    if value:
        parsed = urlparse(str(value))
        if _normalize_domain(parsed.hostname) == "steamcommunity.com":
            path = re.sub(r"/+", "/", parsed.path or "")
            match = re.match(r"^/app/([0-9]+)/discussions/([0-9]+)/([0-9]+)(?:/|$)", path, flags=re.IGNORECASE)
            if match:
                return {"appid": match.group(1), "forum": match.group(2), "thread": match.group(3)}
    text = _normalized_public_ref(record.get("public_ref"))
    if text:
        match = re.match(r"^steam-discussion(?::|-)([0-9]+)(?::|-)", text)
        if match:
            return {"appid": None, "forum": None, "thread": match.group(1)}
    return None


def _validate_source(source, index, enums, schema_doc, generated_date, evidence_contract, *, exact_appid=None):
    label = f"provenance.sources[{index}]"
    _require_fields(source, schema_doc["provenance_source_required_fields"], label)
    allowed = set(schema_doc["provenance_source_allowed_fields"])
    extras = sorted(set(source) - allowed)
    if extras:
        raise ValueError(f"{label} contains unsupported fields: {', '.join(extras)}")

    source_id = source.get("source_id")
    if not isinstance(source_id, str) or not _SOURCE_ID_RE.fullmatch(source_id):
        raise ValueError(f"{label}.source_id must be a dossier-local source-NNN token")
    source_type = source.get("source_type")
    if source_type not in enums["source_type"]:
        raise ValueError(f"{label}.source_type is invalid")
    domain = _normalize_domain(source.get("domain"))
    if not domain or not _DOMAIN_RE.fullmatch(domain) or "." not in domain:
        raise ValueError(f"{label}.domain is invalid")

    _source_ref(source)
    if source.get("url"):
        if not isinstance(source["url"], str):
            raise ValueError(f"{label}.url must be a plain HTTPS URL string")
        parsed = urlparse(source["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(f"{label}.url must be an HTTPS public URL")
        if _normalize_domain(parsed.hostname) != domain:
            raise ValueError(f"{label}.domain must match URL host")
    elif not isinstance(source.get("public_ref"), str) or not 3 <= len(source["public_ref"]) <= 500:
        raise ValueError(f"{label}.public_ref is invalid")

    publication_date = _validate_publication_date(source.get("publication_date"), generated_date, label)
    if source.get("language") not in enums["source_language"]:
        raise ValueError(f"{label}.language is invalid")
    freshness = source.get("freshness")
    if freshness not in enums["source_freshness"]:
        raise ValueError(f"{label}.freshness is invalid")
    _validate_dated_freshness(publication_date, freshness, generated_date, evidence_contract, label)
    role = source.get("evidence_role")
    if role not in enums["source_evidence_role"]:
        raise ValueError(f"{label}.evidence_role is invalid")
    if role == "current_state" and freshness != "recent":
        raise ValueError(f"{label} current_state evidence must be classified recent")
    if type(source.get("player_feedback")) is not bool:
        raise ValueError(f"{label}.player_feedback must be JSON boolean")
    feedback_surface_mode = source.get("feedback_surface_mode")
    if feedback_surface_mode is not None:
        if feedback_surface_mode not in enums["source_feedback_surface_mode"]:
            raise ValueError(f"{label}.feedback_surface_mode is invalid")
        if source["player_feedback"] is not True:
            raise ValueError(f"{label}.feedback_surface_mode requires player_feedback=true")

    player_types = set(evidence_contract["source_policy"]["player_feedback_source_types"])
    context_types = set(evidence_contract["source_policy"]["context_only_source_types"])
    if source_type in player_types and source["player_feedback"] is not True:
        raise ValueError(f"{label} player-feedback source type must be marked player_feedback=true")
    if source_type in context_types and source["player_feedback"] is not False:
        raise ValueError(f"{label} context-only source cannot be marked player feedback")
    if _is_steam_store_app_page(source) and (source["player_feedback"] is True or source_type in player_types):
        if feedback_surface_mode != "concrete_item_collection":
            raise ValueError(
                f"{label} Steam Store app page is not a player-feedback item; "
                "it may only classify as a player-feedback surface when explicitly used as a concrete-item fallback collection parent"
            )
        if source_type not in {"steam_reviews", "store_user_reviews"}:
            raise ValueError(
                f"{label} Steam Store concrete-item fallback parent must use a review-surface source type"
            )
    if source["player_feedback"] is True and exact_appid is not None:
        exposed_steam_appid = (
            _steam_appid_from_url(source.get("url"))
            or _steam_appid_from_public_ref(source.get("public_ref"))
        )
        if exposed_steam_appid is not None and exposed_steam_appid != str(exact_appid):
            raise ValueError(f"{label} Steam player-feedback source appid does not match exact dossier appid")
    return source_id, _source_locator_identity(source)


def _validate_feedback_record(record, index, source_map, enums, schema_doc, generated_date, evidence_contract, *, exact_appid=None):
    label = f"provenance.player_feedback_records[{index}]"
    _require_fields(record, schema_doc["player_feedback_record_required_fields"], label)
    allowed = set(schema_doc["player_feedback_record_allowed_fields"])
    extras = sorted(set(record) - allowed)
    if extras:
        raise ValueError(f"{label} contains unsupported fields: {', '.join(extras)}")
    feedback_id = record.get("feedback_id")
    if not isinstance(feedback_id, str) or not 1 <= len(feedback_id) <= 80:
        raise ValueError(f"{label}.feedback_id is invalid")
    source_id = record.get("source_id")
    if source_id not in source_map or source_map[source_id].get("player_feedback") is not True:
        raise ValueError(f"{label}.source_id must resolve to a player-feedback source")
    source = source_map[source_id]

    identity_mode = _feedback_identity_mode(record)
    if identity_mode not in enums["feedback_identity_mode"]:
        raise ValueError(f"{label}.identity_mode is invalid")

    if identity_mode == "stable_locator":
        if not _STABLE_FEEDBACK_ID_RE.fullmatch(str(feedback_id)):
            raise ValueError(f"{label} stable-locator feedback_id must be a dossier-local feedback-NNN token")
        _source_ref(record)
        if source.get("feedback_surface_mode") == "concrete_item_collection" and _is_steam_store_app_page(source):
            raise ValueError(f"{label} stable-locator path cannot rely on a collection-only Steam Store parent")
        if record.get("url"):
            if not isinstance(record["url"], str):
                raise ValueError(f"{label}.url must be a plain HTTPS URL string")
            parsed = urlparse(record["url"])
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValueError(f"{label}.url must be an HTTPS public URL")
            source_domain = _normalize_domain(source.get("domain"))
            if _normalize_domain(parsed.hostname) != source_domain:
                raise ValueError(f"{label}.url host must match its player-feedback source domain")
        elif not isinstance(record.get("public_ref"), str) or not 3 <= len(record["public_ref"]) <= 500:
            raise ValueError(f"{label}.public_ref is invalid")
        exposed_steam_appid = _steam_appid_from_record(record)
        if exposed_steam_appid is not None and exact_appid is not None and exposed_steam_appid != str(exact_appid):
            raise ValueError(f"{label} Steam stable child appid does not match exact dossier appid")
        item_identity = _feedback_item_identity(record, source, label)
        _validate_parent_item_relationship(record, source, label)
    else:
        if "url" in record or "public_ref" in record:
            raise ValueError(f"{label} transient-author fallback must not persist item/profile url or public_ref")
        if not _FALLBACK_FEEDBACK_ID_RE.fullmatch(feedback_id):
            raise ValueError(f"{label} transient-author fallback feedback_id must be dossier-local fallback-NNN")
        if not _SOURCE_ID_RE.fullmatch(str(source_id)):
            raise ValueError(f"{label} transient-author fallback source_id must be a neutral dossier-local source-NNN token")
        if source.get("feedback_surface_mode") != "concrete_item_collection":
            raise ValueError(f"{label} transient-author fallback requires a concrete-item collection parent")
        if not isinstance(source.get("url"), str):
            raise ValueError(f"{label} transient-author fallback parent requires a non-profile HTTPS URL")
        if _is_profile_scoped_url(source["url"], evidence_contract):
            raise ValueError(f"{label} transient-author fallback parent URL must not be author/profile-scoped")
        item_identity = f"fallback:{source_id}:{feedback_id}"

    publication_date = _validate_publication_date(record.get("publication_date"), generated_date, label)
    if publication_date is not None:
        threshold = int(evidence_contract["recency"]["recent_max_age_days"])
        if (generated_date - publication_date).days > threshold and source.get("freshness") == "recent":
            raise ValueError(f"{label} older feedback cannot inherit recent parent-source freshness")
    language = record.get("language")
    if language not in enums["source_language"]:
        raise ValueError(f"{label}.language is invalid")
    source_language = source.get("language")
    if language == "russian" and source_language not in {"russian", "mixed"}:
        raise ValueError(f"{label} Russian feedback conflicts with source language")
    if language == "non_russian" and source_language not in {"non_russian", "mixed"}:
        raise ValueError(f"{label} non-Russian feedback conflicts with source language")
    return feedback_id, item_identity


def _validate_game_identity(identity, dossier, source_map, enums, schema_doc, generated):
    _require_fields(identity, ("work_title", "release_year", "resolution_status", "identity_source_ids", "corroborators"), "game_identity")
    if identity["work_title"] != dossier["title"]:
        raise ValueError("game_identity.work_title must exactly equal dossier title")
    release_year = identity["release_year"]
    rule = schema_doc["integer_rules"]["release_year"]
    if not _json_int(release_year) or not rule["minimum"] <= release_year <= rule["maximum"]:
        raise ValueError("game_identity.release_year must be a canonical JSON integer in range")
    if release_year > generated.year + 1:
        raise ValueError("game_identity.release_year is implausibly future-dated")
    if identity["resolution_status"] not in enums["identity_resolution_status"]:
        raise ValueError("game identity is not resolved")
    source_ids = identity["identity_source_ids"]
    if not isinstance(source_ids, list) or not source_ids or len(source_ids) != len(set(source_ids)):
        raise ValueError("game_identity.identity_source_ids must be a non-empty unique list")
    if any(source_id not in source_map for source_id in source_ids):
        raise ValueError("game identity references unknown provenance source")
    if not any(source_map[source_id].get("evidence_role") == "identity" for source_id in source_ids):
        raise ValueError("game identity requires an identity-role provenance source")
    corroborators = identity["corroborators"]
    if not isinstance(corroborators, list) or not corroborators:
        raise ValueError("game identity requires at least one corroborator")
    seen = set()
    has_appid = False
    for index, item in enumerate(corroborators):
        _require_fields(item, ("kind", "value"), f"game_identity.corroborators[{index}]")
        kind, value = item["kind"], item["value"]
        if kind not in enums["identity_corroborator_kind"] or not isinstance(value, str) or not value.strip():
            raise ValueError("game identity corroborator is invalid")
        key = (kind, value)
        if key in seen:
            raise ValueError("game identity contains duplicate corroborator")
        seen.add(key)
        if kind == "appid" and value == dossier["appid"]:
            has_appid = True
    if not has_appid:
        raise ValueError("game identity must corroborate the exact work-item appid")


def _validate_observations(dossier, source_map, feedback_map, enums, schema_doc):
    observations = dossier.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("dossier observations must be a non-empty list")
    seen = set()
    recurrence_min = schema_doc["observation_invariants"]["recurrence_minimum_mentions"]
    used_feedback_ids = set()
    for index, observation in enumerate(observations):
        _require_fields(observation, ("category", "statement", "sentiment", "recurrence", "mention_count", "evidence_languages", "evidence_status", "source_ids", "player_feedback_ids"), f"observation {index}")
        if observation["category"] not in enums["observation_category"]:
            raise ValueError(f"observation {index} has unsupported category")
        statement = observation["statement"]
        if not isinstance(statement, str) or not 4 <= len(statement.strip()) <= 600:
            raise ValueError(f"observation {index} statement is missing or too long")
        if observation["sentiment"] not in enums["sentiment"]:
            raise ValueError(f"observation {index} sentiment is invalid")
        recurrence = observation["recurrence"]
        if recurrence not in enums["recurrence"]:
            raise ValueError(f"observation {index} recurrence is invalid")
        source_ids = observation["source_ids"]
        if not isinstance(source_ids, list) or not source_ids or len(source_ids) != len(set(source_ids)):
            raise ValueError(f"observation {index} source_ids must be a non-empty unique list")
        if any(source_id not in source_map for source_id in source_ids):
            raise ValueError(f"observation {index} references unknown provenance source")
        feedback_ids = observation["player_feedback_ids"]
        if not isinstance(feedback_ids, list) or not feedback_ids or len(feedback_ids) != len(set(feedback_ids)):
            raise ValueError(f"observation {index} player_feedback_ids must be a non-empty unique list")
        if any(feedback_id not in feedback_map for feedback_id in feedback_ids):
            raise ValueError(f"observation {index} references unknown player-feedback record")
        feedback_records = [feedback_map[feedback_id] for feedback_id in feedback_ids]
        if any(record["source_id"] not in source_ids for record in feedback_records):
            raise ValueError(f"observation {index} bound player-feedback source must also appear in source_ids")
        mention_count = observation["mention_count"]
        if not _json_int(mention_count) or mention_count != len(feedback_ids):
            raise ValueError(f"observation {index} mention_count must exactly equal distinct bound player-feedback records")
        if recurrence == "anecdotal":
            if mention_count != 1:
                raise ValueError(f"observation {index} anecdotal recurrence must be one mention")
        elif mention_count < int(recurrence_min[recurrence]):
            raise ValueError(f"observation {index} recurrence exceeds bound player-feedback support")
        _validate_recurrence_identity_strength(recurrence, feedback_records, schema_doc, f"observation {index}")
        languages = observation["evidence_languages"]
        if not isinstance(languages, list) or not languages or any(x not in enums["evidence_languages"] for x in languages):
            raise ValueError(f"observation {index} evidence_languages are invalid")
        projected = set()
        for record in feedback_records:
            record_language = record["language"]
            if record_language == "russian":
                projected.add("russian")
            elif record_language == "non_russian":
                projected.add("non_russian")
            elif record_language == "mixed":
                projected.update(("russian", "non_russian"))
            elif record_language == "unknown":
                projected.add("unknown")
        expected_languages = [token for token in ("russian", "non_russian", "unknown") if token in projected]
        if languages != expected_languages:
            raise ValueError(
                f"observation {index} evidence_languages must exactly equal the canonical bound-record language projection"
            )
        referenced = [source_map[source_id] for source_id in source_ids]
        status = observation["evidence_status"]
        if status not in enums["evidence_status"]:
            raise ValueError(f"observation {index} evidence_status is invalid")
        if status == "current" and not any(s["evidence_role"] == "current_state" and s["freshness"] == "recent" for s in referenced):
            raise ValueError(f"observation {index} current claim lacks recent current-state evidence")
        if status == "historical":
            if not any(s["evidence_role"] == "historical" for s in referenced):
                raise ValueError(f"observation {index} historical claim lacks historical evidence")
            if not any(s["evidence_role"] == "current_state" and s["freshness"] == "recent" for s in referenced):
                raise ValueError(f"observation {index} historical/fixed claim lacks recent current-state check")
        if status == "durable" and not any(s["evidence_role"] == "durable_trait" for s in referenced):
            raise ValueError(f"observation {index} durable claim lacks durable-trait evidence")
        digest = canonical_sha256(observation)
        if digest in seen:
            raise ValueError("dossier contains an exact duplicate observation")
        seen.add(digest)
        used_feedback_ids.update(feedback_ids)
    return observations, used_feedback_ids


def _validate_conflicts(dossier, source_map, feedback_map, enums, schema_doc):
    conflicts = dossier.get("conflicts")
    if not isinstance(conflicts, list):
        raise ValueError("dossier conflicts must be a list")
    recurrence_min = schema_doc["observation_invariants"]["recurrence_minimum_mentions"]
    used_feedback_ids = set()
    seen = set()
    for index, conflict in enumerate(conflicts):
        _require_fields(
            conflict,
            ("statement", "recurrence", "mention_count", "source_ids", "player_feedback_ids"),
            f"conflict {index}",
        )
        if not isinstance(conflict["statement"], str) or not 4 <= len(conflict["statement"].strip()) <= 600:
            raise ValueError(f"conflict {index} statement is invalid")
        recurrence = conflict["recurrence"]
        if recurrence not in enums["recurrence"]:
            raise ValueError(f"conflict {index} recurrence is invalid")
        source_ids = conflict["source_ids"]
        if not isinstance(source_ids, list) or not source_ids or len(source_ids) != len(set(source_ids)):
            raise ValueError(f"conflict {index} source_ids are invalid")
        if any(source_id not in source_map for source_id in source_ids):
            raise ValueError(f"conflict {index} references unknown provenance source")
        feedback_ids = conflict["player_feedback_ids"]
        if not isinstance(feedback_ids, list) or not feedback_ids or len(feedback_ids) != len(set(feedback_ids)):
            raise ValueError(f"conflict {index} player_feedback_ids must be a non-empty unique list")
        if any(feedback_id not in feedback_map for feedback_id in feedback_ids):
            raise ValueError(f"conflict {index} references unknown player-feedback record")
        records = [feedback_map[feedback_id] for feedback_id in feedback_ids]
        if any(record["source_id"] not in source_ids for record in records):
            raise ValueError(f"conflict {index} bound player-feedback source must also appear in source_ids")
        mention_count = conflict["mention_count"]
        if not _json_int(mention_count) or mention_count != len(feedback_ids):
            raise ValueError(f"conflict {index} mention_count must exactly equal distinct bound player-feedback records")
        if recurrence == "anecdotal":
            if mention_count != 1:
                raise ValueError(f"conflict {index} anecdotal recurrence must be one mention")
        elif mention_count < int(recurrence_min[recurrence]):
            raise ValueError(f"conflict {index} recurrence exceeds bound player-feedback support")
        _validate_recurrence_identity_strength(recurrence, records, schema_doc, f"conflict {index}")
        digest = canonical_sha256(conflict)
        if digest in seen:
            raise ValueError("dossier contains an exact duplicate conflict")
        seen.add(digest)
        used_feedback_ids.update(feedback_ids)
    return used_feedback_ids



def _validate_coverage_sufficiency(evidence, observations, schema_doc):
    """Validate the neutral machine-readable coverage attestation for persisted sufficient dossiers."""
    coverage = evidence.get("coverage")
    required = ("dimensions", "closure_basis", "strengths_investigated", "weaknesses_tradeoffs_investigated")
    _require_fields(coverage, required, "evidence.coverage")
    if set(coverage) != set(required):
        raise ValueError("evidence.coverage contains unsupported fields")

    enums = schema_doc["enums"]
    dimensions = coverage["dimensions"]
    if not isinstance(dimensions, list):
        raise ValueError("evidence.coverage.dimensions must be a list")

    expected_dimensions = set(enums["coverage_dimension"])
    seen_dimensions = set()
    state_by_dimension = {}
    for index, item in enumerate(dimensions):
        _require_fields(item, ("dimension", "state", "observation_indices"), f"coverage dimension {index}")
        if set(item) != {"dimension", "state", "observation_indices"}:
            raise ValueError(f"coverage dimension {index} contains unsupported fields")
        dimension = item["dimension"]
        state = item["state"]
        observation_indices = item["observation_indices"]
        if dimension not in expected_dimensions:
            raise ValueError(f"coverage dimension {index} is invalid")
        if dimension in seen_dimensions:
            raise ValueError("coverage dimensions must classify every dimension exactly once")
        seen_dimensions.add(dimension)
        if state not in enums["coverage_state"]:
            raise ValueError(f"coverage dimension {dimension} state is invalid")
        if (
            not isinstance(observation_indices, list)
            or len(observation_indices) != len(set(observation_indices))
            or any(not _json_int(value) or value < 0 or value >= len(observations) for value in observation_indices)
        ):
            raise ValueError(f"coverage dimension {dimension} observation_indices are invalid")
        if state == "covered" and not observation_indices:
            raise ValueError(f"covered coverage dimension {dimension} requires bound observation indices")
        if state != "covered" and observation_indices:
            raise ValueError(f"non-covered coverage dimension {dimension} must not bind observations")
        state_by_dimension[dimension] = state

    if seen_dimensions != expected_dimensions:
        raise ValueError("coverage dimensions must classify every canonical dimension exactly once")

    if coverage["closure_basis"] not in enums["coverage_closure_basis"]:
        raise ValueError("evidence.coverage closure_basis is invalid")
    if coverage["strengths_investigated"] is not True:
        raise ValueError("sufficient dossier coverage requires neutral investigation of meaningful strengths")
    if coverage["weaknesses_tradeoffs_investigated"] is not True:
        raise ValueError("sufficient dossier coverage requires neutral investigation of weaknesses and trade-offs")

    unresolved = [
        dimension for dimension, state in state_by_dimension.items()
        if state == "materially_unresolved"
    ]
    if unresolved:
        raise ValueError("sufficient/evidence_stable dossier has materially unresolved game-experience coverage")

    exhausted = {
        dimension for dimension, state in state_by_dimension.items()
        if state == "exhausted_unavailable"
    }
    closure_basis = coverage["closure_basis"]
    if exhausted and closure_basis != "sufficient_after_route_exhaustion":
        raise ValueError("exhausted unavailable coverage requires route-exhaustion closure basis")
    if closure_basis == "sufficient_after_route_exhaustion" and not exhausted:
        raise ValueError("route-exhaustion closure basis requires at least one exhausted unavailable dimension")

    central_dimensions = {
        "core_play_mechanics",
        "controls_game_feel",
        "progression_development_unlocks",
        "variety_repetition_over_time",
        "difficulty_mastery_learning_friction",
        "pacing_structure_direction",
        "exploration_mission_activity_structure",
        "multiplayer_coop_dependence",
        "story_characters_identity_hooks",
    }
    covered_central = {
        dimension for dimension in central_dimensions
        if state_by_dimension.get(dimension) == "covered"
    }
    exhausted_central = {
        dimension for dimension in central_dimensions
        if state_by_dimension.get(dimension) == "exhausted_unavailable"
    }
    if not covered_central and not (
        closure_basis == "sufficient_after_route_exhaustion" and exhausted_central
    ):
        raise ValueError(
            "sufficient/evidence_stable dossier is only a narrow nonrepresentative slice of game experience"
        )


def derive_dossier_summary(observations, conflicts):
    """Return the only canonical top-level summary projection from validated structured findings."""
    if not isinstance(observations, list) or not observations or not isinstance(conflicts, list):
        raise ValueError("canonical dossier summary requires observations and conflicts")
    return (
        f"Evidence summary: {len(observations)} validated structured observations; "
        "consult observations and conflicts for supported findings."
    )


def validate_dossier_strict(
    dossier,
    contract,
    *,
    expected_appid=None,
    expected_title=None,
    expected_ttl_days=None,
    now=None,
    schema_doc=None,
    evidence_contract=None,
    require_fresh_at_acceptance=True,
):
    """Validate the active V2 web-evidence dossier and all prior hardening invariants."""
    schema_doc = schema_doc or load_worker_schema()
    evidence_contract = evidence_contract or load_web_evidence_contract()
    if schema_doc.get("evidence_contract") != evidence_contract["schema"] or schema_doc.get("evidence_contract_version") != evidence_contract["version"]:
        raise ValueError("worker schema and web evidence contract binding mismatch")
    _require_fields(dossier, schema_doc["required_top_level_fields"], "dossier")
    if "review_sample" in dossier:
        raise ValueError("legacy review_sample payload is forbidden by the active web-evidence schema")
    if dossier.get("schema") != schema_doc["dossier_schema"]:
        raise ValueError("unsupported web evidence dossier schema")
    if not _json_int(dossier.get("schema_version")) or dossier["schema_version"] != schema_doc["dossier_schema_version"]:
        raise ValueError("dossier schema_version must be canonical JSON integer 2")
    expected_binding = current_worker_contract_binding(schema_doc, evidence_contract)
    if dossier.get("web_evidence_contract_binding") != expected_binding:
        raise ValueError("dossier web-evidence compatibility binding is missing or stale")
    appid = dossier.get("appid")
    if not isinstance(appid, str) or not appid.isdigit():
        raise ValueError("dossier appid must be a numeric string")
    if expected_appid is not None and appid != str(expected_appid):
        raise ValueError("dossier appid does not match prepared work scope")
    title = dossier.get("title")
    if not isinstance(title, str) or not title.strip() or len(title) > 300:
        raise ValueError("dossier title is missing or invalid")
    if expected_title is not None and title != expected_title:
        raise ValueError("dossier title does not exactly match prepared descriptor title")
    ttl = dossier.get("ttl_days")
    ttl_rule = schema_doc["integer_rules"]["ttl_days"]
    if not _json_int(ttl) or not ttl_rule["minimum"] <= ttl <= ttl_rule["maximum"]:
        raise ValueError("dossier ttl_days must be a canonical JSON integer in range")
    if expected_ttl_days is not None and ttl != expected_ttl_days:
        raise ValueError("dossier TTL does not match prepared work manifest")
    generated = parse_utc(dossier.get("generated_at_utc"))
    expires = parse_utc(dossier.get("expires_at_utc"))
    if expires != generated + timedelta(days=ttl):
        raise ValueError("dossier expiry must equal generated_at + ttl_days")
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    max_future = int(schema_doc["timestamp_rules"]["maximum_future_skew_minutes_at_ingest"])
    if generated > now_utc + timedelta(minutes=max_future):
        raise ValueError("future-generated dossier cannot be canonically ingested")
    if require_fresh_at_acceptance and now_utc >= expires:
        raise ValueError("already-expired dossier cannot be canonically ingested")
    summary = dossier.get("summary")
    if not isinstance(summary, str) or not 20 <= len(summary.strip()) <= 1200:
        raise ValueError("dossier neutral summary is missing or too long")

    provenance = dossier.get("provenance")
    _require_fields(provenance, ("sources", "player_feedback_records"), "provenance")
    if set(provenance) != {"sources", "player_feedback_records"}:
        raise ValueError("provenance may contain only compact source and player-feedback records")
    sources = provenance["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValueError("provenance.sources must be a non-empty list")
    enums = schema_doc["enums"]
    source_map, source_refs, source_identity_map = {}, set(), {}
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError(f"provenance.sources[{index}] must be an object")
        source_id, ref_identity = _validate_source(
            source,
            index,
            enums,
            schema_doc,
            generated.date(),
            evidence_contract,
            exact_appid=appid,
        )
        if source_id in source_map:
            raise ValueError("provenance source_id values must be unique")
        if ref_identity in source_refs:
            raise ValueError("duplicate or aliased provenance source reference is forbidden")
        source_refs.add(ref_identity)
        source_map[source_id] = source
        source_identity_map[source_id] = ref_identity

    serialized_source_ids = [source["source_id"] for source in sources]
    expected_source_ids = [f"source-{index:03d}" for index in range(1, len(serialized_source_ids) + 1)]
    if serialized_source_ids != expected_source_ids:
        raise ValueError("provenance source ids must be sequential dossier-local source-NNN tokens")

    feedback_records = provenance["player_feedback_records"]
    if not isinstance(feedback_records, list) or not feedback_records:
        raise ValueError("provenance.player_feedback_records must be a non-empty list")
    feedback_map, feedback_item_identities = {}, set()
    for index, record in enumerate(feedback_records):
        if not isinstance(record, dict):
            raise ValueError(f"provenance.player_feedback_records[{index}] must be an object")
        feedback_id, item_identity = _validate_feedback_record(
            record,
            index,
            source_map,
            enums,
            schema_doc,
            generated.date(),
            evidence_contract,
            exact_appid=appid,
        )
        if feedback_id in feedback_map:
            raise ValueError("player-feedback feedback_id values must be unique")
        if item_identity in feedback_item_identities:
            raise ValueError("duplicate or aliased attributable player-feedback item is forbidden")
        feedback_item_identities.add(item_identity)
        feedback_map[feedback_id] = record

    stable_ids = [
        record["feedback_id"]
        for record in feedback_records
        if _feedback_identity_mode(record) == "stable_locator"
    ]
    expected_stable_ids = [f"feedback-{index:03d}" for index in range(1, len(stable_ids) + 1)]
    if stable_ids != expected_stable_ids:
        raise ValueError("stable-locator feedback ids must be sequential dossier-local feedback-NNN tokens")

    fallback_ids = [
        record["feedback_id"]
        for record in feedback_records
        if _feedback_identity_mode(record) == "transient_author_deduped"
    ]
    expected_fallback_ids = [f"fallback-{index:03d}" for index in range(1, len(fallback_ids) + 1)]
    if fallback_ids != expected_fallback_ids:
        raise ValueError("transient-author fallback ids must be sequential dossier-local fallback-NNN tokens")
    if fallback_ids:
        _validate_no_fallback_author_identity_payload(dossier, evidence_contract)

    _validate_game_identity(dossier.get("game_identity"), dossier, source_map, enums, schema_doc, generated)
    observations, used_feedback_ids = _validate_observations(dossier, source_map, feedback_map, enums, schema_doc)
    used_feedback_ids.update(_validate_conflicts(dossier, source_map, feedback_map, enums, schema_doc))

    expected_summary = derive_dossier_summary(observations, dossier["conflicts"])
    if summary != expected_summary:
        raise ValueError("dossier summary must equal canonical structured-finding derivation")

    evidence = dossier.get("evidence")
    _require_fields(evidence, ("strategy", "research_state", "source_mix_status", "single_source_reason", "russian_attempt", "overall_strength", "stop_reason", "coverage"), "evidence")
    if set(evidence) != {"strategy", "research_state", "source_mix_status", "single_source_reason", "russian_attempt", "overall_strength", "stop_reason", "coverage"}:
        raise ValueError("evidence contains unsupported fields")
    if evidence["strategy"] not in enums["research_strategy"]:
        raise ValueError("evidence strategy is invalid")
    if evidence["research_state"] not in enums["research_state"]:
        raise ValueError("only semantically sufficient evidence may be persisted")
    if evidence["source_mix_status"] not in enums["source_mix_status"]:
        raise ValueError("source_mix_status is invalid")
    if evidence["russian_attempt"] not in enums["russian_attempt_status"]:
        raise ValueError("russian_attempt status is invalid")
    if evidence["overall_strength"] not in enums["overall_strength"]:
        raise ValueError("overall_strength is invalid")
    if evidence["stop_reason"] not in enums["research_stop_reason"]:
        raise ValueError("evidence stop_reason is invalid")
    _validate_coverage_sufficiency(evidence, observations, schema_doc)

    used_records = [feedback_map[feedback_id] for feedback_id in used_feedback_ids]
    used_player_source_identities = {source_identity_map[record["source_id"]] for record in used_records}
    if not used_player_source_identities:
        raise ValueError("at least one bound player-feedback record is required")
    if evidence["source_mix_status"] == "multi_source":
        if len(used_player_source_identities) < 2:
            raise ValueError("multi_source evidence requires at least two distinct physical used player-feedback sources")
        if evidence["single_source_reason"] is not None:
            raise ValueError("multi_source evidence must not carry a single-source reason")
    else:
        reason = evidence["single_source_reason"]
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 500:
            raise ValueError("single_source_only evidence requires a compact reason")
        if len(used_player_source_identities) != 1:
            raise ValueError("single_source_only must have exactly one distinct physical used player-feedback source")

    russian_attempt = evidence["russian_attempt"]
    complete_russian_states = set(evidence_contract["russian_evidence"]["complete_dossier_allowed_states"])
    if russian_attempt == "existence_established_retrieval_unresolved":
        raise ValueError(
            "Russian exact-product existence is established but attributable item-level retrieval is unresolved"
        )
    if russian_attempt == "existence_established_access_unresolved":
        raise ValueError(
            "Russian exact-product existence is established but access prevents attributable item-level retrieval"
        )
    if russian_attempt not in complete_russian_states:
        raise ValueError("russian_attempt is not a complete-dossier state")

    used_russian = any(record["language"] in {"russian", "mixed"} for record in used_records)
    if russian_attempt == "found_and_used" and not used_russian:
        raise ValueError("russian found_and_used requires a bound Russian player-feedback record")
    if russian_attempt != "found_and_used" and used_russian:
        raise ValueError("used Russian/mixed player feedback requires russian_attempt=found_and_used")

    max_recurrence_rank = max(_RECURRENCE_RANK[observation["recurrence"]] for observation in observations)
    if evidence["overall_strength"] == "strong" and max_recurrence_rank < _RECURRENCE_RANK["strong"]:
        raise ValueError("overall strong evidence requires at least one strongly recurring observation")
    if evidence["overall_strength"] == "moderate" and max_recurrence_rank < _RECURRENCE_RANK["moderate"]:
        raise ValueError("overall moderate evidence requires at least one moderately recurring observation")

    _validate_no_raw_body_like_payload(dossier)
    _validate_no_raw_or_personal_payload(dossier)
    return dossier


def dossier_state_strict(dossier, contract, *, now=None, expected_appid=None, expected_title=None, expected_ttl_days=None):
    if dossier is None:
        return "missing"
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    validate_dossier_strict(
        dossier,
        contract,
        expected_appid=expected_appid,
        expected_title=expected_title,
        expected_ttl_days=expected_ttl_days,
        now=now_utc,
        require_fresh_at_acceptance=False,
    )
    expires = parse_utc(dossier["expires_at_utc"])
    return "fresh" if now_utc < expires else "stale"


def validate_dossiers_against_expected_items(dossiers, expected_items, contract, *, expected_ttl_days, now=None, schema_doc=None, evidence_contract=None):
    if not isinstance(dossiers, list) or not isinstance(expected_items, list):
        raise ValueError("dossiers and expected items must be lists")
    if len(dossiers) != len(expected_items):
        raise ValueError("dossier count does not match exact prepared item count")
    schema_doc = schema_doc or load_worker_schema()
    evidence_contract = evidence_contract or load_web_evidence_contract()
    validated = []
    for index, (dossier, item) in enumerate(zip(dossiers, expected_items)):
        if not isinstance(item, dict):
            raise ValueError(f"prepared item {index} is malformed")
        validated.append(validate_dossier_strict(
            dossier,
            contract,
            expected_appid=str(item.get("appid") or ""),
            expected_title=item.get("title"),
            expected_ttl_days=expected_ttl_days,
            now=now,
            schema_doc=schema_doc,
            evidence_contract=evidence_contract,
            require_fresh_at_acceptance=True,
        ))
    return validated

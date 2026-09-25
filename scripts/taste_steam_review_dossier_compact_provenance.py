#!/usr/bin/env python3
"""Shared fail-closed compact-provenance validation for Taste dossier groups."""
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_CONTRACT = ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json"

_SOURCE_ID_RE = re.compile(r"^source-[0-9]{3}$")
_STABLE_FEEDBACK_ID_RE = re.compile(r"^feedback-[0-9]{3}$")
_FALLBACK_FEEDBACK_ID_RE = re.compile(r"^fallback-[0-9]{3}$")
_SOURCE_OBSERVATION_FEEDBACK_ID_RE = re.compile(r"^observation-[0-9]{3}$")


def load_compact_provenance_policy(path=DEFAULT_EVIDENCE_CONTRACT):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if (
        doc.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2"
        or doc.get("version") != 2
        or doc.get("status") != "active"
    ):
        raise ValueError("web evidence contract is missing, stale or unsupported")
    policy = doc.get("compact_provenance")
    if not isinstance(policy, dict):
        raise ValueError("compact provenance policy is missing")
    required_false = (
        "author_identity_allowed",
        "profile_scoped_urls_allowed",
        "review_or_post_content_in_locator_metadata_allowed",
        "raw_body_or_body_like_fields_allowed",
        "public_ref_url_text_allowed",
        "direct_author_identity_hash_as_anonymization_allowed",
    )
    if any(policy.get(key) is not False for key in required_false):
        raise ValueError("compact provenance policy is not fail-closed")
    for key in (
        "forbidden_profile_url_path_regexes",
        "forbidden_profile_url_query_keys",
        "forbidden_public_ref_regexes",
    ):
        values = policy.get(key)
        if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v for v in values):
            raise ValueError(f"compact provenance policy {key} is missing or invalid")
    internal_ids = policy.get("internal_join_ids")
    if not isinstance(internal_ids, dict) or internal_ids.get("author_identity_independent") is not True:
        raise ValueError("compact provenance internal join-id policy is missing or not author-independent")
    return policy


def _validate_url(url, label, policy):
    if not isinstance(url, str):
        raise ValueError(f"{label}.url must be a plain HTTPS URL string")
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{label}.url must be an HTTPS public URL")
    path = parsed.path or "/"
    for pattern in policy["forbidden_profile_url_path_regexes"]:
        if re.search(pattern, path, flags=re.IGNORECASE):
            raise ValueError(f"{label}.url is author/profile-scoped and forbidden")
    forbidden_query = {key.casefold() for key in policy["forbidden_profile_url_query_keys"]}
    for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
        if key.casefold() in forbidden_query:
            raise ValueError(f"{label}.url contains author/profile identity query metadata")


def _validate_public_ref(value, label, policy):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}.public_ref is invalid")
    text = value.strip()
    if re.match(r"^https?://", text, flags=re.IGNORECASE):
        raise ValueError(f"{label}.public_ref must be neutral locator metadata, not URL text")
    for pattern in policy["forbidden_public_ref_regexes"]:
        if re.search(pattern, text, flags=re.IGNORECASE):
            lowered = pattern.casefold()
            if "summari" in lowered:
                raise ValueError(f"{label}.public_ref contains review/post content-like summary")
            raise ValueError(f"{label}.public_ref contains author/user identity attribution")


def validate_compact_provenance(dossier, policy=None):
    """Reject author identity, profile-scoped links and content-like compact refs."""
    policy = policy or load_compact_provenance_policy()
    if not isinstance(dossier, dict):
        raise ValueError("dossier must be an object for compact provenance validation")
    provenance = dossier.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("dossier provenance is required")
    for container_key in ("sources", "player_feedback_records"):
        records = provenance.get(container_key)
        if not isinstance(records, list):
            raise ValueError(f"provenance.{container_key} must be a list")
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise ValueError(f"provenance.{container_key}[{index}] must be an object")
            label = f"provenance.{container_key}[{index}]"
            source_id = record.get("source_id")
            if not isinstance(source_id, str) or not _SOURCE_ID_RE.fullmatch(source_id):
                raise ValueError(f"{label}.source_id must be a dossier-local source-NNN token")
            if container_key == "player_feedback_records":
                feedback_id = record.get("feedback_id")
                identity_mode = str(record.get("identity_mode") or "stable_locator")
                if identity_mode == "transient_author_deduped":
                    pattern, expected = _FALLBACK_FEEDBACK_ID_RE, "fallback-NNN"
                elif identity_mode == "source_observation":
                    pattern, expected = _SOURCE_OBSERVATION_FEEDBACK_ID_RE, "observation-NNN"
                else:
                    pattern, expected = _STABLE_FEEDBACK_ID_RE, "feedback-NNN"
                if not isinstance(feedback_id, str) or not pattern.fullmatch(feedback_id):
                    raise ValueError(f"{label}.feedback_id must be a dossier-local {expected} token")
            if record.get("url") is not None:
                _validate_url(record["url"], label, policy)
            if record.get("public_ref") is not None:
                _validate_public_ref(record["public_ref"], label, policy)
    return dossier

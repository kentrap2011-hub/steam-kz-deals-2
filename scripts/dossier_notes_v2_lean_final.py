#!/usr/bin/env python3
"""Inactive Notes V2 lean-final validation. Never authorizes canonical Dossier/Deep ingest.

The contract validates exact identity, balanced usable findings, safe high-level
source links and dated temporal claims. It deliberately does NOT require a
per-review ledger, invented mention counts or twelve coverage declarations.
"""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "config" / "dossier_notes_v2_lean_final.schema.json"
LEAN_SCHEMA = "DOSSIER-NOTES-V2-LEAN-FINAL-V1"

def _utc(value, field):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        raise ValueError(f"{field} must be a valid UTC timestamp") from None

def _date(value, field):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError(f"{field} must be a real calendar date") from None

def validate_lean_final(dossier, *, expected_appid=None, expected_title=None,
                        expected_ttl_days=None, now=None):
    """Read-only validation for an explicitly isolated Notes V2 trial only."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(dossier),
                    key=lambda e: (list(map(str, e.path)), e.message))
    if errors:
        error = errors[0]
        where = ".".join(map(str, error.path)) or "dossier"
        raise ValueError(f"lean final {where}: {error.message}")
    if expected_appid is not None and dossier["appid"] != str(expected_appid):
        raise ValueError("lean final wrong frozen appid")
    if expected_title is not None and dossier["title"] != expected_title:
        raise ValueError("lean final wrong frozen title or edition")
    identity = dossier["game_identity"]
    if identity["appid"] != dossier["appid"] or identity["work_title"] != dossier["title"]:
        raise ValueError("lean final conflicting game identity")
    if expected_ttl_days is not None and dossier["ttl_days"] != expected_ttl_days:
        raise ValueError("lean final wrong prepared TTL")
    generated = _utc(dossier["generated_at_utc"], "generated_at_utc")
    expires = _utc(dossier["expires_at_utc"], "expires_at_utc")
    if expires != generated + timedelta(days=dossier["ttl_days"]):
        raise ValueError("lean final expiration does not match TTL")
    clock = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if generated > clock + timedelta(minutes=5) or clock >= expires:
        raise ValueError("lean final future-generated or expired")
    sources = dossier["sources"]
    seen_urls = set()
    for i, src in enumerate(sources):
        url = urlsplit(src["url"])
        if (url.scheme != "https" or not url.hostname or url.username or url.password
                or url.fragment or url.hostname in {"localhost", "127.0.0.1"}):
            raise ValueError(f"lean final unsafe public source link {i}")
        if re.search(r"/(?:profiles|users|user|members)/[^/]+", url.path, re.I):
            raise ValueError("lean final author/profile scoped source forbidden")
        canonical = (url.scheme, url.hostname.lower(), url.path.rstrip("/"), url.query)
        if canonical in seen_urls:
            raise ValueError("lean final duplicate source URL")
        seen_urls.add(canonical)
    seen_claims, sentiments = set(), set()
    central = {"mechanics", "structure", "pacing", "progression", "repetition",
               "difficulty", "friction", "multiplayer", "coop"}
    if not any(row["category"] in central for row in dossier["observations"]):
        raise ValueError("lean final lacks a central game-experience observation")
    for i, row in enumerate(dossier["observations"]):
        statement = row["statement"].strip()
        if statement.casefold() in seen_claims:
            raise ValueError("lean final duplicate observation")
        seen_claims.add(statement.casefold())
        sentiments.add(row["sentiment"])
    if "positive" not in sentiments and "mixed" not in sentiments:
        raise ValueError("lean final lacks a substantive strength")
    if "negative" not in sentiments and "mixed" not in sentiments:
        raise ValueError("lean final lacks a substantive trade-off")
    for section in ("observations", "conflicts"):
        for i, row in enumerate(dossier[section]):
            refs = row["source_indices"]
            if any(ref >= len(sources) for ref in refs):
                raise ValueError(f"lean final {section}[{i}] has unbound source index")
            if section != "observations":
                continue
            state, when = row["evidence_status"], row["as_of"]
            if state in {"current", "historical"}:
                if not refs or not when:
                    raise ValueError("lean final dated temporal claim needs dated source support")
                date = _date(when, f"{section}[{i}].as_of")
                if date > generated.date():
                    raise ValueError("lean final temporal claim postdates dossier generation")
                if state == "current" and (generated.date() - date).days > 365:
                    raise ValueError("lean final current-state evidence is too old")
            elif when is not None:
                raise ValueError("lean final undated/uncertain claim must not assert as_of")
    if not sources and dossier["confidence"] != "limited":
        raise ValueError("lean final without sources cannot claim moderate confidence")
    if not sources and not dossier["unknowns"]:
        raise ValueError("lean final without sources must state its uncertainty")
    # Preserve the existing privacy boundary without carrying a review archive.
    from taste_steam_review_dossier_strict import _validate_no_raw_body_like_payload
    _validate_no_raw_body_like_payload(dossier)
    return dossier

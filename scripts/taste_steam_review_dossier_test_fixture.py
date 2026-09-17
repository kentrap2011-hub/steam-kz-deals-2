#!/usr/bin/env python3
"""Shared synthetic V2 dossier fixtures for control-plane regressions."""
from datetime import timedelta


def web_dossier(appid, generated, *, title=None, release_year=2020, russian_status="found_and_used"):
    from taste_steam_review_dossier_strict import current_worker_contract_binding

    appid = str(appid)
    title = title or f"Game {appid}"
    recent_date = generated.date().isoformat()
    older_date = (generated.date() - timedelta(days=400)).isoformat()
    sources = [
        {
            "source_id": "m1",
            "source_type": "official_metadata",
            "domain": "store.steampowered.com",
            "url": f"https://store.steampowered.com/app/{appid}/",
            "publication_date": None,
            "language": "non_russian",
            "freshness": "unknown",
            "evidence_role": "identity",
            "player_feedback": False,
        },
        {
            "source_id": "p1",
            "source_type": "steam_community",
            "domain": "steamcommunity.com",
            "url": f"https://steamcommunity.com/app/{appid}/reviews/",
            "publication_date": older_date,
            "language": "non_russian",
            "freshness": "older",
            "evidence_role": "durable_trait",
            "player_feedback": True,
        },
        {
            "source_id": "p2",
            "source_type": "reddit",
            "domain": "reddit.com",
            "url": f"https://www.reddit.com/r/games/comments/test{appid}/game_{appid}/",
            "publication_date": recent_date,
            "language": "russian" if russian_status == "found_and_used" else "non_russian",
            "freshness": "recent",
            "evidence_role": "current_state",
            "player_feedback": True,
        },
    ]
    feedback_records = [
        {
            "feedback_id": "pf1",
            "source_id": "p1",
            "public_ref": f"steam-review-{appid}-1",
            "publication_date": older_date,
            "language": "non_russian",
        },
        {
            "feedback_id": "pf2",
            "source_id": "p1",
            "public_ref": f"steam-review-{appid}-2",
            "publication_date": older_date,
            "language": "non_russian",
        },
        {
            "feedback_id": "pf3",
            "source_id": "p1",
            "public_ref": f"steam-review-{appid}-3",
            "publication_date": older_date,
            "language": "non_russian",
        },
        {
            "feedback_id": "pf4",
            "source_id": "p2",
            "url": f"https://www.reddit.com/r/games/comments/test{appid}/game_{appid}/comment1/",
            "publication_date": recent_date,
            "language": "russian" if russian_status == "found_and_used" else "non_russian",
        },
    ]
    observations = [
        {
            "category": "mechanics",
            "statement": "Players repeatedly describe deliberate movement and resource management as durable mechanics.",
            "sentiment": "mixed",
            "recurrence": "moderate",
            "mention_count": 3,
            "evidence_languages": ["non_russian"],
            "evidence_status": "durable",
            "source_ids": ["p1"],
            "player_feedback_ids": ["pf1", "pf2", "pf3"],
        }
    ]
    if russian_status == "found_and_used":
        observations.append({
            "category": "localization",
            "statement": "Recent Russian-language player feedback provides a current localization check.",
            "sentiment": "neutral",
            "recurrence": "anecdotal",
            "mention_count": 1,
            "evidence_languages": ["russian"],
            "evidence_status": "current",
            "source_ids": ["p2"],
            "player_feedback_ids": ["pf4"],
        })
    else:
        observations.append({
            "category": "friction",
            "statement": "Recent player feedback provides a current technical-state check without Russian evidence.",
            "sentiment": "neutral",
            "recurrence": "anecdotal",
            "mention_count": 1,
            "evidence_languages": ["non_russian"],
            "evidence_status": "current",
            "source_ids": ["p2"],
            "player_feedback_ids": ["pf4"],
        })
    return {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-V2",
        "schema_version": 2,
        "web_evidence_contract_binding": current_worker_contract_binding(),
        "key": f"App_{appid}",
        "appid": appid,
        "title": title,
        "generated_at_utc": generated.isoformat(),
        "expires_at_utc": (generated + timedelta(days=20)).isoformat(),
        "ttl_days": 20,
        "game_identity": {
            "work_title": title,
            "release_year": release_year,
            "resolution_status": "resolved",
            "identity_source_ids": ["m1"],
            "corroborators": [{"kind": "appid", "value": appid}],
        },
        "summary": "A compact neutral synthesis of multi-source player feedback with temporal and language provenance.",
        "observations": observations,
        "conflicts": [],
        "evidence": {
            "strategy": "adaptive_multi_source_web",
            "research_state": "sufficient",
            "source_mix_status": "multi_source",
            "single_source_reason": None,
            "russian_attempt": russian_status,
            "overall_strength": "moderate",
            "stop_reason": "evidence_stable",
        },
        "provenance": {"sources": sources, "player_feedback_records": feedback_records},
    }

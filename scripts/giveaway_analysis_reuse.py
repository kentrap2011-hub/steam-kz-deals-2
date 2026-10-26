"""Precomputed giveaway presentation consumes exact Steam identity and canonical cards.

No ITAD/IGDB-specific fields, title matching, Taste recomputation or paid scoring.
If a canonical analyzed card is absent, no semantic facts are manufactured.
"""
from __future__ import annotations


def _exact_appid(value):
    if type(value) is int and value > 0:
        return value
    if isinstance(value, str) and value.isdecimal() and value.isascii() and int(value) > 0:
        return int(value)
    return None


def attach(giveaways, canonical_items):
    if giveaways.get("state") != "active":
        return giveaways
    by_appid = {}
    for card in canonical_items:
        if not isinstance(card, dict):
            continue
        appids = card.get("base_appids") or []
        if not isinstance(appids, list):
            continue
        for raw in appids:
            appid = _exact_appid(raw)
            if appid is not None:
                by_appid.setdefault(appid, []).append(card)
    for game in giveaways.get("games", []):
        identity = game.get("analysis_identity") or {}
        appid = _exact_appid(identity.get("steam_appid")) if identity.get("status") == "resolved" else None
        analysis = {
            "status": "incomplete", "reason": "exact_identity_unresolved",
            "steam_appid": appid, "summary": None, "why_fit": [], "risks": [],
        }
        if appid is not None:
            matches = by_appid.get(appid, [])
            analysis["reason"] = "canonical_card_missing_or_ambiguous"
            if len(matches) == 1 and matches[0].get("analysis_state") == "analyzed_fit":
                source = matches[0]
                summary = source.get("summary") if source.get("description_status") == "ready_ru" else None
                why_fit = source.get("why_fit") if (source.get("why_fit_status") or {}).get("grounding") == "grounded" else []
                why_fit = why_fit if isinstance(why_fit, list) else []
                # 'risks' on the canonical final card have already passed
                # card_explanation_policy.visible_risk_payload(); do not synthesize cons.
                risks = source.get("risks") if isinstance(source.get("risks"), list) else []
                analysis.update({
                    "summary": summary if isinstance(summary, str) and summary.strip() else None,
                    "why_fit": [v for v in why_fit if isinstance(v, str)],
                    "risks": [v for v in risks if isinstance(v, str)],
                    "risk_status": source.get("risk_status"),
                    "provenance": {
                        "canonical_family_id": source.get("id"),
                        "description_source_appid": source.get("description_source_appid"),
                        "description_source_path": source.get("description_source_path"),
                        "positive_evidence": source.get("why_fit_provenance"),
                        "negative_evidence": source.get("risk_provenance"),
                    },
                })
                if analysis["summary"] and analysis["why_fit"] and source.get("risk_status"):
                    analysis.update(status="ready", reason="canonical_precomputed_analysis")
                else:
                    analysis["reason"] = "canonical_analysis_incomplete"
        game["analysis"] = analysis
    return giveaways

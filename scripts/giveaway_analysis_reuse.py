"""Precomputed giveaway presentation consumes exact Steam identity and canonical cards.

No ITAD/IGDB-specific fields, title matching, Taste recomputation or paid scoring.
If a canonical analyzed card is absent, no semantic facts are manufactured.
"""
from __future__ import annotations

from card_explanation_policy import GROUNDED_RISK_SOURCES


def _exact_appid(value):
    if type(value) is int and value > 0:
        return value
    if isinstance(value, str) and value.isdecimal() and value.isascii() and int(value) > 0:
        return int(value)
    return None



# The final visual payload contains only the paid top-100 after publication cap.
# Retain the smallest source-bound analysis projection of the *entire* canonical
# ranked scope in that same payload, so refreshes need no new Taste computation.
SOURCE_FIELDS = (
    "id", "base_appids", "analysis_state", "description_status", "summary",
    "why_fit", "why_fit_status", "why_fit_provenance", "risks", "risk_status",
    "risk_provenance", "description_source_appid", "description_source_path",
)


def capture_canonical_sources(canonical_items, semantic_binding):
    """Prepared non-commercial evidence index, never a second paid listing."""
    if not isinstance(semantic_binding, dict) or not semantic_binding or not all(
        isinstance(v, str) and v for v in semantic_binding.values()
    ):
        # An unbound cache must never acquire source authority during refresh.
        return {"schema_version": 1, "semantic_binding": None, "cards": []}
    cards = []
    for card in canonical_items:
        if isinstance(card, dict) and isinstance(card.get("base_appids"), list):
            cards.append({key: card.get(key) for key in SOURCE_FIELDS})
    return {"schema_version": 1, "semantic_binding": dict(semantic_binding), "cards": cards}


def canonical_sources_for_refresh(saved, visible_items, semantic_binding):
    """A matching full-build source index plus the freshest visible cards.

    If semantic inputs have changed, do not reuse off-screen results until the
    canonical full producer rebuilds them. A visible card supersedes its stored
    family, preventing conflicting old/new evidence from being combined.
    """
    visible = [c for c in (visible_items or []) if isinstance(c, dict)]
    if not (
        isinstance(saved, dict) and saved.get("schema_version") == 1
        and isinstance(semantic_binding, dict) and bool(semantic_binding)
        and all(isinstance(v, str) and v for v in semantic_binding.values())
        and saved.get("semantic_binding") == semantic_binding
        and isinstance(saved.get("cards"), list)
    ):
        return visible
    visible_ids = {c["id"] for c in visible if isinstance(c.get("id"), str) and c["id"]}
    cached = []
    for card in saved["cards"]:
        if not isinstance(card, dict):
            return visible  # invalid index is not authority
        if card.get("id") not in visible_ids:
            cached.append(card)
    return cached + visible


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
                negative_provenance = source.get("risk_provenance")
                negatives_grounded = (
                    isinstance(negative_provenance, list)
                    and len(negative_provenance) == len(risks)
                    and all(
                        isinstance(p, dict) and p.get("source") in GROUNDED_RISK_SOURCES
                        for p in negative_provenance
                    )
                )
                if not negatives_grounded:
                    risks = []
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
                        "negative_evidence": negative_provenance if negatives_grounded else [],
                    },
                })
                if analysis["summary"] and analysis["why_fit"] and source.get("risk_status") and negatives_grounded:
                    analysis.update(status="ready", reason="canonical_precomputed_analysis")
                else:
                    analysis["reason"] = "canonical_analysis_incomplete"
        game["analysis"] = analysis
    return giveaways

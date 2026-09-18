#!/usr/bin/env python3
"""Canonical deterministic story-DLC semantic scope classification.

The classifier is intentionally fail-closed.  Steam product metadata may prove
that a DLC contains substantial playable narrative content; title hints alone
can never create positive eligibility.
"""
import re

POLICY_REVISION = "story-dlc-positive-evidence-v1"

STORY_DLC_ELIGIBLE = "story_dlc_eligible"
NON_STORY_DLC_EXCLUDED = "non_story_dlc_excluded"
STORY_CONTENT_UNPROVEN_EXCLUDED = "story_content_unproven_excluded"

_STATUS_VALUES = {
    STORY_DLC_ELIGIBLE,
    NON_STORY_DLC_EXCLUDED,
    STORY_CONTENT_UNPROVEN_EXCLUDED,
}

_CONTAINER_PATTERNS = (
    ("digital_deluxe_or_upgrade", re.compile(r"\b(?:digital\s+deluxe|deluxe\s+(?:edition\s+)?(?:upgrade|pack)|upgrade\s+pack)\b", re.I)),
    ("season_pass_or_entitlement_container", re.compile(r"\b(?:season\s+pass|expansion\s+pass|dlc\s+pass)\b", re.I)),
)

_HARD_NON_STORY_TITLE_PATTERNS = (
    ("soundtrack_or_ost_product", re.compile(r"\b(?:soundtrack|ost)\b", re.I)),
    ("digital_artbook_product", re.compile(r"\b(?:digital\s+)?art\s*book\b", re.I)),
    ("cosmetic_or_skin_pack_product", re.compile(r"\b(?:cosmetic|skin|costume|outfit|appearance)\s+(?:pack|bundle)\b", re.I)),
    ("item_or_equipment_pack_product", re.compile(r"\b(?:weapon|item|equipment|gear)\s+(?:pack|bundle)\b", re.I)),
    ("currency_or_resource_pack_product", re.compile(r"\b(?:currency|resource|credits?|coins?|gems?)\s+(?:pack|bundle)\b", re.I)),
    ("music_or_song_pack_product", re.compile(r"\b(?:bonus\s+song|song|music)\s+(?:pack|bundle)\b", re.I)),
    ("digital_extras_product", re.compile(r"\b(?:wallpaper|avatar|digital\s+extras?)\s+(?:pack|bundle)?\b", re.I)),
    ("upgrade_or_bonus_pack_product", re.compile(r"\b(?:upgrade|bonus)\s+(?:pack|bundle)\b", re.I)),
)

_EXPLICIT_NON_STORY_PATTERNS = (
    ("soundtrack_or_ost", re.compile(r"\b(?:original\s+(?:game\s+)?soundtrack|soundtrack|ost)\b", re.I)),
    ("digital_artbook", re.compile(r"\b(?:digital\s+)?art\s*book\b", re.I)),
    ("cosmetic_or_skin_content", re.compile(r"\b(?:cosmetic|skin(?:s)?|outfit(?:s)?|costume(?:s)?|appearance\s+pack)\b", re.I)),
    ("item_or_equipment_pack", re.compile(r"\b(?:weapon|item|equipment|gear)\s+(?:pack|bundle)\b", re.I)),
    ("currency_or_resource_pack", re.compile(r"\b(?:currency|resource|credits?|coins?|gems?)\s+(?:pack|bundle)\b", re.I)),
    ("bonus_song_pack", re.compile(r"\b(?:bonus\s+song|song\s+pack|music\s+pack)\b", re.I)),
    ("digital_extras", re.compile(r"\b(?:wallpapers?|avatars?|character\s+sheets?|digital\s+extras?)\b", re.I)),
)

# Each match must describe playable narrative content, not merely a theme.
_POSITIVE_STORY_PATTERNS = (
    ("story_campaign", re.compile(r"\b(?:new|all[- ]new|additional|standalone|separate)\s+(?:story\s+)?campaign\b|\bstory\s+campaign\b", re.I)),
    ("story_chapter_or_episode", re.compile(r"\b(?:new|additional|standalone|separate)\s+(?:story\s+)?(?:chapter|episode)\b|\bstory\s+(?:chapter|episode)\b", re.I)),
    ("storyline", re.compile(r"\b(?:new|additional|standalone|separate)\s+story\s*line\b|\bnew\s+story\b", re.I)),
    ("story_quests_or_questline", re.compile(r"\b(?:new|additional|standalone|separate)\s+(?:story\s+)?quest\s*line\b|\bstory\s+quests?\b", re.I)),
    ("narrative_or_story_expansion", re.compile(r"\b(?:narrative|story)\s+expansion\b|\bexpansion\s+(?:with|featuring)\s+(?:an?\s+)?(?:new|additional)\s+story\b", re.I)),
    ("standalone_story_adventure", re.compile(r"\b(?:standalone|separate|new|all[- ]new)\s+(?:story(?:-driven)?\s+)?adventure\b", re.I)),
    ("continues_story", re.compile(r"\b(?:continue|continues|continuing)\s+(?:the\s+)?story\b", re.I)),
)


def _text(value):
    return " ".join(str(value or "").split())


def _evidence(source, field, signal, excerpt=None):
    item = {
        "source": source,
        "field": field,
        "signal": signal,
    }
    if excerpt:
        item["excerpt"] = excerpt[:240]
    return item


def validate_classification(value):
    if not isinstance(value, dict):
        raise ValueError("story DLC classification must be an object")
    if value.get("policy_revision") != POLICY_REVISION:
        raise ValueError("story DLC classification policy revision mismatch")
    if value.get("status") not in _STATUS_VALUES:
        raise ValueError("unsupported story DLC classification status")
    if bool(value.get("eligible")) != (value.get("status") == STORY_DLC_ELIGIBLE):
        raise ValueError("story DLC classification eligible/status mismatch")
    if not isinstance(value.get("reason_code"), str) or not value["reason_code"]:
        raise ValueError("story DLC classification reason_code missing")
    if not isinstance(value.get("evidence"), list):
        raise ValueError("story DLC classification evidence must be a list")
    return value


def classify_story_dlc(metadata, *, mechanical_kind="dlc"):
    """Classify one DLC using only GitHub-accessible authoritative product metadata."""
    if mechanical_kind != "dlc":
        raise ValueError("story DLC classifier may only classify mechanical_kind=dlc")
    if not isinstance(metadata, dict):
        metadata = {}

    source = _text(metadata.get("metadata_source")) or "unknown_product_metadata"
    title = _text(metadata.get("store_name"))
    description = _text(metadata.get("short_description"))
    combined = f"{title}\n{description}".strip()

    # Entitlement/upgrade containers are not independent story objects even when
    # their description references story DLC children.
    container_hits = []
    for signal, pattern in _CONTAINER_PATTERNS:
        if pattern.search(combined):
            container_hits.append(_evidence(source, "store_name+short_description", signal))
    if container_hits:
        return validate_classification({
            "policy_revision": POLICY_REVISION,
            "status": NON_STORY_DLC_EXCLUDED,
            "eligible": False,
            "reason_code": "entitlement_or_upgrade_container_not_independent_story_content",
            "evidence": container_hits,
        })

    hard_title_hits = []
    for signal, pattern in _HARD_NON_STORY_TITLE_PATTERNS:
        if pattern.search(title):
            hard_title_hits.append(_evidence(source, "store_name", signal))
    if hard_title_hits:
        return validate_classification({
            "policy_revision": POLICY_REVISION,
            "status": NON_STORY_DLC_EXCLUDED,
            "eligible": False,
            "reason_code": "product_identity_is_non_story_bonus_content",
            "evidence": hard_title_hits,
        })

    positive = []
    for signal, pattern in _POSITIVE_STORY_PATTERNS:
        match = pattern.search(description)
        if match:
            positive.append(_evidence(source, "short_description", signal, match.group(0)))

    # Confirmed substantial story content wins over ordinary bonus/cosmetic
    # content for mixed DLC, because the narrative component is independently
    # playable and positively evidenced.
    if positive:
        return validate_classification({
            "policy_revision": POLICY_REVISION,
            "status": STORY_DLC_ELIGIBLE,
            "eligible": True,
            "reason_code": "positive_playable_narrative_content_confirmed",
            "evidence": positive,
        })

    negative = []
    for signal, pattern in _EXPLICIT_NON_STORY_PATTERNS:
        if pattern.search(combined):
            negative.append(_evidence(source, "store_name+short_description", signal))
    if negative:
        return validate_classification({
            "policy_revision": POLICY_REVISION,
            "status": NON_STORY_DLC_EXCLUDED,
            "eligible": False,
            "reason_code": "product_metadata_confirms_non_story_bonus_content",
            "evidence": negative,
        })

    evidence = []
    if description:
        evidence.append(_evidence(source, "short_description", "no_positive_story_signal"))
    elif title:
        evidence.append(_evidence(source, "store_name", "title_only_insufficient_for_positive_story_eligibility"))
    else:
        evidence.append(_evidence(source, "metadata", "product_metadata_missing"))

    return validate_classification({
        "policy_revision": POLICY_REVISION,
        "status": STORY_CONTENT_UNPROVEN_EXCLUDED,
        "eligible": False,
        "reason_code": "positive_story_content_not_proven",
        "evidence": evidence,
    })



def external_addon_story_scope(family):
    """Return the validated classification for one independent addon family."""
    if not isinstance(family, dict) or family.get("family_type") != "external_base_addon":
        return None
    items = family.get("addon_story_scope")
    if not isinstance(items, list) or len(items) != 1:
        raise ValueError("external addon family must have exactly one story-DLC classification")
    item = items[0]
    if not isinstance(item, dict) or item.get("key") != family.get("taste_subject_key"):
        raise ValueError("external addon family story-DLC classification identity mismatch")
    return validate_classification(item.get("classification"))


def external_addon_taste_semantic_eligible(family):
    classification = external_addon_story_scope(family)
    if classification is None:
        return True
    return classification["status"] == STORY_DLC_ELIGIBLE and classification["eligible"] is True

def summarize_story_dlc_classifications(classified_items, *, example_limit=5):
    """Return compact audit/debug summary for the complete classified DLC scope."""
    counts = {
        STORY_DLC_ELIGIBLE: 0,
        NON_STORY_DLC_EXCLUDED: 0,
        STORY_CONTENT_UNPROVEN_EXCLUDED: 0,
    }
    examples = {key: [] for key in counts}
    for item in classified_items:
        classification = validate_classification(item["classification"])
        status = classification["status"]
        counts[status] += 1
        if len(examples[status]) < example_limit:
            examples[status].append({
                "key": item.get("key"),
                "appid": str(item.get("appid") or ""),
                "title": item.get("title"),
                "reason_code": classification["reason_code"],
            })
    return {
        "policy_revision": POLICY_REVISION,
        "dlc_like_items_considered": sum(counts.values()),
        "story_eligible_count": counts[STORY_DLC_ELIGIBLE],
        "non_story_excluded_count": counts[NON_STORY_DLC_EXCLUDED],
        "ambiguous_unproven_excluded_count": counts[STORY_CONTENT_UNPROVEN_EXCLUDED],
        "representative_examples": examples,
    }

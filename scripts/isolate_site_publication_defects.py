#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import giveaway_visual_handoff
import site_publication_resilience
import validate_card_explanations
from russian_description_quality import classify_description

VISUAL = Path('data/production/visual/current.json')
UNTRANSLATED_STATUSES = {
    'needs_translation',
    'needs_ru_rewrite',
    'technical_source',
    'missing_source',
    'publication_quarantined',
}
EXPLANATION_FIELDS = (
    'why_fit',
    'why_fit_status',
    'why_fit_provenance',
    'risks',
    'risk_codes',
    'risk_status',
    'risk_provenance',
    'cautions',
    'caution_provenance',
)


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def reason_code(error):
    text = str(error or '').casefold()
    if 'commercial/ranking-only' in text:
        return 'positive_commercial_or_ranking_language'
    if 'generic positive fallback' in text:
        return 'generic_positive_fallback'
    if 'personal-taste link' in text:
        return 'positive_missing_personal_link'
    if 'positive' in text or 'why_fit' in text:
        return 'positive_explanation_invalid'
    if 'caution' in text:
        return 'caution_presentation_invalid'
    if 'risk' in text or 'negative-assessment' in text or 'negative assessment' in text:
        return 'risk_presentation_invalid'
    return 'card_explanation_invalid'


def card_binding(game):
    binding = {}
    for key in (
        'analysis_semantic_generation_id',
        'analysis_semantic_source',
        'analysis_resolution_pass',
        'effective_analysis_source',
    ):
        value = game.get(key)
        if value is not None and value != '':
            binding[key] = value
    return binding


def description_blocking_failure(game):
    if game.get('analysis_state') in {'analysis_incomplete', 'not_analyzed'}:
        return None
    summary = game.get('summary')
    category = classify_description(summary)
    status = game.get('description_status')
    pass1_pending_translation = (
        game.get('analysis_semantic_source') == 'progressive_pass1'
        and not summary
        and status in UNTRANSLATED_STATUSES
    )
    if pass1_pending_translation:
        return None
    invalid = category != 'good_ru' or (status is not None and status != 'ready_ru')
    explicit_untranslated = status in UNTRANSLATED_STATUSES and category != 'good_ru'
    if invalid and not explicit_untranslated:
        return {
            'category': category,
            'status': status,
        }
    return None


def visual_source_binding(data):
    contract = data.get('production_contract') or {}
    binding = {}
    for key in (
        'source_chatgpt_payload_blob_sha',
        'source_progressive_candidate_context_blob_sha',
        'progressive_pass1_state_blob_sha',
        'progressive_pass2_state_blob_sha',
        'source_taste_steam_review_dossier_work_blob_sha',
        'source_russian_description_status_blob_sha',
        'source_giveaway_snapshot_blob_sha',
        'site_publication_resilience_contract_blob_sha',
    ):
        value = contract.get(key)
        if value:
            binding[key] = value
    return binding


def isolate_document(
    data,
    *,
    quarantine_path=site_publication_resilience.QUARANTINE_PATH,
    observed_at_utc=None,
    giveaway_snapshot_path=giveaway_visual_handoff.DEFAULT_SNAPSHOT,
):
    defects = list(data.pop('_publication_local_defects', []) or [])
    changed = False

    # Giveaway snapshot trust remains fail-closed at the sibling level, but one
    # identifiable bad offer/game no longer hides independent valid giveaway rows.
    giveaways, giveaway_defects = giveaway_visual_handoff.derive_from_path_with_diagnostics(
        path=giveaway_snapshot_path,
    )
    if data.get('giveaways') != giveaways:
        data['giveaways'] = giveaways
        changed = True
    defects.extend(giveaway_defects)

    for game in data.get('items') or []:
        family_id = str(game.get('id') or '')
        if not family_id:
            # Missing stable item identity is not safely isolatable here.
            raise RuntimeError('visual item missing stable id during publication isolation')

        errors = validate_card_explanations.validate_item(game)
        if errors:
            defect = {
                'category': 'card_explanation',
                'object_type': 'paid_game',
                'object_id': family_id,
                'field': 'player_facing_explanations',
                'reason_codes': sorted({reason_code(error) for error in errors}),
                'label': game.get('title'),
                'source_binding': card_binding(game),
            }
            defects.append(defect)
            for field in EXPLANATION_FIELDS:
                game.pop(field, None)
            state = dict(game.get('publication_presentation_state') or {})
            state['explanations'] = 'quarantined'
            game['publication_presentation_state'] = state
            changed = True

        description_failure = description_blocking_failure(game)
        if description_failure:
            defects.append({
                'category': 'description',
                'object_type': 'paid_game',
                'object_id': family_id,
                'field': 'summary',
                'reason_codes': [
                    f"invalid_{description_failure['category']}",
                    f"invalid_status_{description_failure['status'] or 'missing'}",
                ],
                'label': game.get('title'),
                'source_binding': {
                    **card_binding(game),
                    'description_source_appid': game.get('description_source_appid'),
                    'description_source_path': game.get('description_source_path'),
                },
            })
            game.pop('summary', None)
            game['description_status'] = 'publication_quarantined'
            state = dict(game.get('publication_presentation_state') or {})
            state['description'] = 'quarantined'
            game['publication_presentation_state'] = state
            changed = True

    observed_at = observed_at_utc or data.get('generated_at_utc') or utc_now()
    quarantine, quarantine_changed = site_publication_resilience.reconcile_quarantine(
        defects,
        observed_at_utc=observed_at,
        source_binding=visual_source_binding(data),
        path=quarantine_path,
    )
    return data, quarantine, changed or quarantine_changed


def isolate_file(path=VISUAL, *, quarantine_path=site_publication_resilience.QUARANTINE_PATH):
    target = Path(path)
    data = json.loads(target.read_text(encoding='utf-8'))
    data, quarantine, changed = isolate_document(data, quarantine_path=quarantine_path)
    if changed:
        target.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    summary = site_publication_resilience.active_summary(quarantine)
    print(
        'SITE_PUBLICATION_ISOLATION=PASS '
        f"changed={str(changed).lower()} "
        f"pending={summary['pending_count']} "
        f"categories={json.dumps(summary['category_counts'], ensure_ascii=False, separators=(',', ':'))}"
    )
    return data, quarantine, changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default=str(VISUAL))
    args = parser.parse_args()
    isolate_file(args.path)


if __name__ == '__main__':
    main()

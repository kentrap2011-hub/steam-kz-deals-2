"""Finalize paid-card negative explanations from structured Taste findings.

This module is intentionally run after the legacy visual builder and before final
validation/commit. It makes the structured finding contract authoritative for
both visible grounded negatives and the existing risk/fit ranking semantics, so
free-text keyword recognition is no longer a critical filter.
"""

import json
from pathlib import Path

import apply_fixed_package_purchase_options as package_options
import priority_ranking
import refine_visual_ranking as refiner
from taste_negative_contract import negative_readiness, structured_grounded_risks

VISUAL = Path('data/production/visual/current.json')
PURCHASE_CONTEXT = Path('data/production/pre_ai/chatgpt_purchase_context.jsonl')
TASTE_PROJECTION = Path('data/production/pre_ai/taste_projection.json')


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def load_jsonl(path):
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding='utf-8').splitlines()
        if line.strip()
    ]


def merge_risk(risks, row):
    code = str(row.get('code') or '')
    text = str(row.get('text') or '').strip()
    if not code or not text:
        return
    current = risks.get(code)
    score = int(row.get('score') or 0)
    if current is None or score > int(current.get('score') or 0):
        risks[code] = dict(row)


def all_risk_candidates(taste_entry, projection, practical):
    risks = {}
    for row in structured_grounded_risks(taste_entry).values():
        merge_risk(risks, row)
    for row in refiner.structural_risks(projection, practical).values():
        merge_risk(risks, row)
    return risks


def visible_grounded_payload(risks):
    taste_rows = [
        row for row in risks.values()
        if isinstance(row, dict) and row.get('source') == 'taste_negative_evidence'
    ]
    practical_rows = [
        row for row in risks.values()
        if isinstance(row, dict) and row.get('source') == 'confirmed_practical'
    ]
    taste_rows.sort(key=lambda row: (-int(row.get('score') or 0), str(row.get('code') or '')))
    practical_rows.sort(key=lambda row: (-int(row.get('score') or 0), str(row.get('code') or '')))

    if not taste_rows:
        raise ValueError('normal paid card has no visible grounded Taste negative candidate')

    # The mandatory Taste witness always occupies one visible slot. A stronger
    # confirmed practical downside may occupy the second slot.
    visible = [taste_rows[0]]
    remaining = taste_rows[1:] + practical_rows
    remaining.sort(key=lambda row: (-int(row.get('score') or 0), str(row.get('code') or '')))
    for row in remaining:
        if row.get('code') == visible[0].get('code') and row.get('source') == visible[0].get('source'):
            continue
        visible.append(row)
        break

    heuristic_candidates = sum(
        1
        for row in risks.values()
        if isinstance(row, dict) and row.get('source') not in {'taste_negative_evidence', 'confirmed_practical'}
    )
    provenance = []
    for row in visible:
        item = {
            'code': str(row.get('code')),
            'source': str(row.get('source')),
        }
        if row.get('source') == 'taste_negative_evidence':
            item.update({
                'category': str(row.get('category') or ''),
                'evidence': str(row.get('evidence') or ''),
            })
        provenance.append(item)

    return {
        'risks': [str(row.get('text')).strip() for row in visible],
        'risk_codes': [str(row.get('code')) for row in visible],
        'risk_status': {
            'has_described_risk': True,
            'described_risk_count': len(visible),
            'grounding': 'grounded',
            'grounded_taste_negative_witness': True,
            'heuristic_candidate_count': heuristic_candidates,
        },
        'risk_provenance': provenance,
    }


def canonical_fit_from_structured_risks(game, risks):
    source_fit = game.get('source_fit') or game.get('fit') or 'moderate'
    evidence = game.get('direct_user_evidence') or None
    if isinstance(evidence, dict) and evidence.get('level') == 'none':
        evidence = None
    fit, reason = refiner.direct_fit_cap(source_fit, evidence)
    if not evidence and fit == 'strong' and refiner.serious_taste_risk(risks):
        fit = 'moderate'
        reason = 'serious_confirmed_personal_risk_caps_strong'
    game['source_fit'] = source_fit
    game['fit'] = fit
    game['fit_adjustment_reason'] = reason


def apply_to_document(ready, *, contexts, taste_entries, projections):
    unresolved = []
    corrected = []
    mapped_count = 0
    neutral_other_count = 0
    fit_change_count = 0
    removed_after_structured_fit = 0

    for game in ready.get('items') or []:
        family_id = str(game.get('id') or '')
        context = contexts.get(family_id) or {}
        taste_key = context.get('taste_subject_key')
        taste_entry = taste_entries.get(taste_key) if taste_key else None
        projection = projections.get(taste_key) if taste_key else None
        taste_entry = taste_entry if isinstance(taste_entry, dict) else {}
        projection = projection if isinstance(projection, dict) else {}

        readiness = negative_readiness(taste_entry)
        current_bound = projection.get('status') == 'cache_hit'
        verdict = taste_entry.get('verdict')
        if not current_bound or verdict != 'INCLUDE' or not readiness['negative_analysis_ready']:
            unresolved.append({
                'family_id': family_id,
                'taste_subject_key': taste_key,
                'projection_status': projection.get('status'),
                'verdict': verdict,
                **readiness,
            })
            continue

        risks = all_risk_candidates(taste_entry, projection, game.get('practical') or {})
        visible = visible_grounded_payload(risks)
        structured = structured_grounded_risks(taste_entry)
        mapped_count += len(structured)
        neutral_other_count += int('other_grounded_taste_risk' in structured)

        old_fit = game.get('fit')
        canonical_fit_from_structured_risks(game, risks)
        if game.get('fit') != old_fit:
            fit_change_count += 1

        game['risks'] = visible['risks']
        game['risk_codes'] = visible['risk_codes']
        game['risk_status'] = visible['risk_status']
        game['risk_provenance'] = visible['risk_provenance']
        _, _, risk_penalty, risk_level = refiner.risk_summary(risks)
        game['risk_penalty'] = risk_penalty
        game['risk_level'] = risk_level

        if not refiner.apply_commercial_branch(game, context):
            removed_after_structured_fit += 1
            continue
        corrected.append(game)

    if unresolved:
        sample = unresolved[:10]
        raise RuntimeError(
            'grounded negative readiness incomplete for normal paid visual: '
            + json.dumps(sample, ensure_ascii=False, separators=(',', ':'))
        )

    ready['items'] = corrected
    ready['item_count'] = len(corrected)
    package_options.apply_current_artifacts_to_visual(ready)
    ranked, final_priority_order = priority_ranking.apply_final_priority_order(ready.get('items') or [])
    ready['items'] = ranked
    ready['item_count'] = len(ranked)

    contract = ready.setdefault('production_contract', {})
    contract['grounded_negative_contract'] = 'TASTE-SEMANTIC-RESULT-V4'
    contract['grounded_negative_mapper'] = 'structured_code_category_no_keyword_admission'
    contract['normal_paid_card_requires_grounded_taste_negative_witness'] = True
    contract['legacy_free_text_keyword_mapper_is_readiness_critical'] = False
    contract['other_grounded_taste_risk_ranking_score'] = 0
    contract['grounded_negative_mapped_finding_count'] = mapped_count
    contract['grounded_negative_neutral_other_count'] = neutral_other_count
    contract['grounded_negative_fit_change_count'] = fit_change_count
    contract['grounded_negative_removed_after_structured_fit_count'] = removed_after_structured_fit
    contract['priority_factors'] = final_priority_order
    return {
        'visible_item_count': len(ranked),
        'mapped_finding_count': mapped_count,
        'neutral_other_count': neutral_other_count,
        'fit_change_count': fit_change_count,
        'removed_after_structured_fit_count': removed_after_structured_fit,
    }


def apply_to_current_visual():
    if not VISUAL.exists():
        raise RuntimeError(f'missing visual payload: {VISUAL}')
    ready = load_json(VISUAL)
    contexts = {
        str(row.get('family_id')): row
        for row in load_jsonl(PURCHASE_CONTEXT)
        if row.get('family_id')
    }
    taste_entries = refiner.effective_taste_entries()
    projections = (load_json(TASTE_PROJECTION).get('entries') or {}) if TASTE_PROJECTION.exists() else {}

    before = json.dumps(ready, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    stats = apply_to_document(
        ready,
        contexts=contexts,
        taste_entries=taste_entries,
        projections=projections,
    )
    after = json.dumps(ready, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    changed = before != after
    if changed:
        VISUAL.write_text(json.dumps(ready, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    return changed, stats


if __name__ == '__main__':
    changed, stats = apply_to_current_visual()
    print(json.dumps({'changed': changed, **stats}, ensure_ascii=False, indent=2))
    print('GROUNDED_NEGATIVE_VISUAL=PASS')

import json
import sys
from pathlib import Path

import build_daily_visual_payload as readiness_builder
from card_explanation_policy import GROUNDED_RISK_SOURCES


CURRENT_VISUAL = Path('data/production/visual/current.json')
GENERIC_POSITIVE_PREFIX = 'Игра прошла строгий вкусовой отбор'
COMMERCIAL_ONLY_TERMS = ('скидк', 'цена', 'цене', 'руб', 'rank', 'score', 'рейтинг')


def load_items(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    items = data.get('items') or []
    return sorted(items, key=lambda game: int(game.get('priority_rank') or 999999))


def semantic_validation_required(path):
    candidate = Path(path)
    if candidate.resolve() != CURRENT_VISUAL.resolve():
        return True
    source_key, _payload = readiness_builder.current_production_readiness()
    return source_key is not None


def validate_item(game):
    errors = []
    title = str(game.get('title') or game.get('id') or '<unknown>')

    reasons = [str(x).strip() for x in game.get('why_fit') or [] if str(x).strip()]
    fit_status = game.get('why_fit_status') or {}
    fit_provenance = game.get('why_fit_provenance') or []

    for reason in reasons:
        if reason.startswith(GENERIC_POSITIVE_PREFIX):
            errors.append(f'{title}: generic positive fallback is visible')
        if 'теб' not in reason.casefold():
            errors.append(f'{title}: positive lacks explicit personal-taste link')
        lowered = reason.casefold()
        if any(term in lowered for term in COMMERCIAL_ONLY_TERMS):
            errors.append(f'{title}: positive contains commercial/ranking-only language')

    if reasons:
        if fit_status.get('has_described_fit') is not True:
            errors.append(f'{title}: positive text exists but why_fit_status is not described')
        if len(fit_provenance) < len(reasons):
            errors.append(f'{title}: positive text lacks provenance')
        for row in fit_provenance[:len(reasons)]:
            if row.get('source') != 'taste_positive_evidence' or not str(row.get('evidence') or '').strip():
                errors.append(f'{title}: positive provenance is not grounded Taste evidence')
    elif fit_status.get('has_described_fit') is True:
        errors.append(f'{title}: why_fit_status describes a positive but why_fit is empty')

    risks = [str(x).strip() for x in game.get('risks') or [] if str(x).strip()]
    risk_codes = [str(x).strip() for x in game.get('risk_codes') or [] if str(x).strip()]
    risk_status = game.get('risk_status') or {}
    risk_provenance = game.get('risk_provenance') or []

    # Normal paid-card readiness is intentionally strict: absence of a grounded
    # downside means analysis is incomplete upstream, never "no risks found".
    if not risks:
        errors.append(f'{title}: normal paid card has no visible grounded negative')
    if risk_status.get('has_described_risk') is not True:
        errors.append(f'{title}: normal paid card lacks described-risk status')
    if risk_status.get('grounded_taste_negative_witness') is not True:
        errors.append(f'{title}: normal paid card lacks grounded Taste negative witness status')
    if len(risk_codes) != len(risks):
        errors.append(f'{title}: visible risk count and risk_codes count differ')
    if len(risk_provenance) != len(risks):
        errors.append(f'{title}: visible risk count and provenance count differ')

    taste_witnesses = 0
    for row in risk_provenance:
        source = row.get('source')
        if source not in GROUNDED_RISK_SOURCES or not row.get('code'):
            errors.append(f'{title}: visible risk lacks grounded provenance')
            continue
        if source == 'taste_negative_evidence':
            taste_witnesses += 1
            if not str(row.get('category') or '').strip():
                errors.append(f'{title}: Taste negative provenance lacks category')
            if not str(row.get('evidence') or '').strip():
                errors.append(f'{title}: Taste negative provenance lacks raw grounded evidence')
    if taste_witnesses < 1:
        errors.append(f'{title}: visible risks contain no grounded Taste negative provenance')

    return errors


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else str(CURRENT_VISUAL)
    sample_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    items = load_items(path)

    if not semantic_validation_required(path):
        print(json.dumps({
            'path': path,
            'sample_size': min(len(items), sample_limit),
            'item_count': len(items),
            'validation_mode': 'preserve_existing_semantics',
            'reason': 'pending_ai_queue',
        }, ensure_ascii=False, indent=2))
        print('CARD_EXPLANATION_VALIDATION=SKIP reason=pending_ai_queue_preserve_existing_semantics')
        return

    sample = items[:sample_limit]
    errors = []
    for game in sample:
        errors.extend(validate_item(game))

    summary = {
        'path': path,
        'sample_size': len(sample),
        'visible_positive_cards': sum(bool(game.get('why_fit')) for game in sample),
        'omitted_positive_cards': sum(not bool(game.get('why_fit')) for game in sample),
        'visible_risk_cards': sum(bool(game.get('risks')) for game in sample),
        'no_visible_risk_cards': sum(not bool(game.get('risks')) for game in sample),
        'grounded_taste_witness_cards': sum(
            any((row or {}).get('source') == 'taste_negative_evidence' for row in game.get('risk_provenance') or [])
            for game in sample
        ),
        'sample_titles': [str(game.get('title') or game.get('id') or '') for game in sample[:5]],
        'violation_count': len(errors),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        for error in errors[:30]:
            print(f'CARD_EXPLANATION_VIOLATION={error}')
        raise SystemExit(f'CARD_EXPLANATION_VALIDATION=FAIL count={len(errors)}')
    print('CARD_EXPLANATION_VALIDATION=PASS')


if __name__ == '__main__':
    main()

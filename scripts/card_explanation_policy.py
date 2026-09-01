"""Deterministic player-facing card explanation policy.

This module deliberately separates explanation visibility from ranking/scoring. It
only turns already-bound Taste/practical evidence into player-facing text; price,
discount, rank and deal score are not inputs.
"""

from typing import Dict, Iterable, List, Tuple


GROUNDED_RISK_SOURCES = {'taste_negative_evidence', 'confirmed_practical'}


def _normalized_evidence(value):
    return ' '.join(str(value or '').strip().split())


def _positive_reason(value):
    evidence = _normalized_evidence(value)
    text = evidence.casefold()
    if not text:
        return None, None

    if '2.5d platformer' in text and 'first-person' in text:
        return (
            'mixed_2_5d_first_person',
            'Игра чередует 2.5D-платформинг и эпизоды от первого лица — тебе обычно лучше заходят игры, которые меняют формат и игровые ситуации, а не повторяют один цикл.',
        )

    tactical_details = []
    if 'formation' in text:
        tactical_details.append('построение')
    if 'army composition' in text:
        tactical_details.append('состав армии')
    if 'unit types' in text:
        tactical_details.append('типы юнитов')
    if tactical_details:
        detail = ', '.join(tactical_details[:2])
        return (
            'tactical_configuration',
            f'В тактических ситуациях здесь можно менять {detail} — тебе особенно подходят игры, где результат зависит от анализа ситуации и осмысленной настройки системы.',
        )

    if any(phrase in text for phrase in ['different solutions', 'multiple ways', 'multiple approaches', 'alternative approaches']):
        return (
            'multiple_solutions',
            'Для игровых задач предусмотрено несколько разных решений или подходов — тебе особенно подходят игры, где можно самому выбирать способ прохождения.',
        )

    traversal_terms = [
        ('parkour', 'паркур'),
        ('glide', 'планирование'),
        ('levitation', 'левитация'),
        ('climbing', 'лазание'),
        ('climb', 'лазание'),
        ('flying', 'полёт'),
    ]
    traversal = next((label for needle, label in traversal_terms if needle in text), None)
    if traversal:
        return (
            'specific_traversal',
            f'Важная часть перемещения здесь — {traversal}; тебе особенно нравятся игры, где само движение и контроль персонажа интересны как отдельная механика.',
        )

    if any(phrase in text for phrase in ['new abilities', 'unlock abilities', 'unlock new', 'upgrade abilities', 'ability upgrades']):
        return (
            'ability_progression',
            'По мере прохождения здесь открываются или улучшаются способности с игровым эффектом — тебе особенно подходят игры с ясным прогрессом, который реально меняет возможности персонажа.',
        )

    investigation_details = []
    if 'clue' in text:
        investigation_details.append('улики')
    if 'interrogat' in text:
        investigation_details.append('допросы')
    if investigation_details:
        detail = ' и '.join(dict.fromkeys(investigation_details))
        return (
            'investigation_details',
            f'Расследование опирается на {detail} — тебе такие загадки лучше заходят, когда поиск ответа строится на конкретных действиях и понятных зацепках.',
        )

    if any(phrase in text for phrase in ['choice consequences', 'choices have consequences', 'decisions have consequences', 'meaningful consequences']):
        return (
            'meaningful_consequences',
            'Решения здесь имеют заметные последствия для происходящего — тебе обычно интереснее игры, где выбор действительно меняет ситуацию, а не остаётся декоративным.',
        )

    if any(phrase in text for phrase in ['clear objective', 'clear goal', 'escape premise']):
        return (
            'clear_objective',
            'У игры есть явно обозначенная цель, которая направляет отдельные действия и исследование — тебе такой вектор подходит лучше, чем бесцельное блуждание по системам или миру.',
        )

    # Fail closed: broad genre labels, score/rank/eligibility language and other
    # weak descriptors are intentionally not converted into praise.
    return None, None


def positive_reasons(positive_evidence: Iterable[str], limit: int = 2):
    reasons: List[str] = []
    provenance: List[dict] = []
    for raw in positive_evidence or []:
        code, reason = _positive_reason(raw)
        if not code or not reason or reason in reasons:
            continue
        reasons.append(reason)
        provenance.append({
            'source': 'taste_positive_evidence',
            'policy_code': code,
            'evidence': _normalized_evidence(raw),
        })
        if len(reasons) >= limit:
            break
    return reasons, provenance


def visible_risk_payload(risks: Dict[str, dict], limit: int = 2):
    rows = []
    for row in (risks or {}).values():
        if not isinstance(row, dict):
            continue
        source = str(row.get('source') or '')
        code = str(row.get('code') or '')
        text = str(row.get('text') or '').strip()
        if source not in GROUNDED_RISK_SOURCES or not code or not text:
            continue
        rows.append(row)

    rows.sort(key=lambda row: (-int(row.get('score') or 0), str(row.get('code') or '')))
    visible = rows[:limit]
    risk_codes = [str(row.get('code')) for row in visible]
    risk_texts = [str(row.get('text')).strip() for row in visible]
    provenance = [
        {
            'code': str(row.get('code')),
            'source': str(row.get('source')),
        }
        for row in visible
    ]
    heuristic_candidates = sum(
        1
        for row in (risks or {}).values()
        if isinstance(row, dict) and str(row.get('source') or '') not in GROUNDED_RISK_SOURCES
    )
    status = {
        'has_described_risk': bool(visible),
        'described_risk_count': len(visible),
        'grounding': 'grounded' if visible else 'none',
        'heuristic_candidate_count': heuristic_candidates,
    }
    return {
        'risks': risk_texts,
        'risk_codes': risk_codes,
        'risk_status': status,
        'risk_provenance': provenance,
    }

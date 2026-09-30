"""Deterministic player-facing card explanation policy.

This module deliberately separates explanation visibility from ranking/scoring. It
only turns already-bound Taste/practical evidence into player-facing text; price,
discount, rank and deal score are not inputs.
"""

from typing import Dict, Iterable, List, Tuple


GROUNDED_RISK_SOURCES = {'taste_negative_evidence', 'confirmed_practical'}


def _normalized_evidence(value):
    return ' '.join(str(value or '').strip().split())


POSITIVE_BINDING_FIELDS = (
    'semantic_source',
    'semantic_generation_id',
    'profile_pin_sha256',
    'work_id',
    'family_id',
    'taste_subject_key',
    'appid',
    'taste_fingerprint',
    'candidate_context_sha256',
    'dossier_content_sha256',
    'authorization_id',
    'accepted_at_utc',
    'work_authority_commit',
)

DEEP_SCORE_REQUIRED_BINDING_FIELDS = (
    'semantic_generation_id',
    'profile_pin_sha256',
    'work_id',
    'family_id',
    'taste_subject_key',
    'appid',
    'taste_fingerprint',
    'candidate_context_sha256',
    'dossier_content_sha256',
    'authorization_id',
    'accepted_at_utc',
)


def _normalized_binding(value):
    if not isinstance(value, dict):
        return None
    binding = {
        field: value.get(field)
        for field in POSITIVE_BINDING_FIELDS
        if value.get(field) not in {None, ''}
    }
    return binding or None


def linked_deep_score_binding(value):
    """Return only complete accepted linked-Deep provenance bindings."""
    binding = _normalized_binding(value)
    if (
        binding is None
        or binding.get('semantic_source') != 'progressive_pass2'
        or any(binding.get(field) in {None, ''} for field in DEEP_SCORE_REQUIRED_BINDING_FIELDS)
    ):
        return None
    return binding


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

    mastery_details = []
    if 'parry' in text or 'parrying' in text:
        mastery_details.append('парирование')
    if 'dodge' in text or 'dodging' in text:
        mastery_details.append('уклонения')
    if any(phrase in text for phrase in ['enemy reading', 'read enemies', 'reading enemies', 'enemy patterns']):
        mastery_details.append('чтение действий противника')
    if len(mastery_details) >= 2:
        detail = ' и '.join(dict.fromkeys(mastery_details[:2]))
        return (
            'combat_mastery',
            f'Боевая система заметно опирается на {detail} — тебе особенно подходят игры, где важны навык игрока, точные действия и понимание противника.',
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

    ability_progression = (
        ('abilit' in text or 'skill' in text)
        and any(phrase in text for phrase in ['new ', 'unlock', 'upgrade', 'expand', 'progress'])
    )
    if ability_progression:
        return (
            'ability_progression',
            'По мере прохождения здесь открываются или развиваются способности с игровым эффектом — тебе особенно подходят игры с ясным прогрессом, который реально меняет возможности персонажа.',
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



def deep_score_reasons(taste_entry: dict, limit: int = 2):
    """Project accepted score-bearing Deep findings without lexical reinterpretation."""
    if (
        not isinstance(taste_entry, dict)
        or taste_entry.get('semantic_source') != 'progressive_pass2'
        or taste_entry.get('deep_score_explainability_status') != 'linked_v1'
    ):
        return [], []
    binding = linked_deep_score_binding(taste_entry.get('deep_score_evidence_binding'))
    if binding is None:
        return [], []
    reasons = []
    provenance = []
    for finding in taste_entry.get('deep_score_findings') or []:
        if not isinstance(finding, dict):
            continue
        impacts = [row for row in finding.get('factor_impacts') or [] if isinstance(row, dict)]
        if not any(row.get('effect') == 'supports' for row in impacts):
            continue
        text = _normalized_evidence(finding.get('text_ru'))
        evidence_refs = [dict(ref) for ref in finding.get('candidate_evidence_refs') or [] if isinstance(ref, dict)]
        profile_refs = [dict(ref) for ref in finding.get('profile_evidence_refs') or [] if isinstance(ref, dict)]
        if not text or not impacts or not evidence_refs or not profile_refs:
            continue
        reasons.append(text)
        provenance.append({
            'source': 'deep_score_finding',
            'finding_id': finding.get('finding_id'),
            'factor_impacts': [dict(row) for row in impacts],
            'evidence_refs': evidence_refs,
            'profile_evidence_refs': profile_refs,
            'semantic_binding': dict(binding),
        })
        if len(reasons) >= limit:
            break
    return reasons, provenance


def deep_score_qualifiers(taste_entry: dict, limit: int = 2):
    """Expose non-risk score qualifiers without turning them into a second penalty."""
    if (
        not isinstance(taste_entry, dict)
        or taste_entry.get('semantic_source') != 'progressive_pass2'
        or taste_entry.get('deep_score_explainability_status') != 'linked_v1'
    ):
        return [], []
    binding = _normalized_binding(taste_entry.get('deep_score_evidence_binding'))
    if binding is None:
        return [], []
    cautions = []
    provenance = []
    for finding in taste_entry.get('deep_score_findings') or []:
        if not isinstance(finding, dict):
            continue
        impacts = [row for row in finding.get('factor_impacts') or [] if isinstance(row, dict)]
        effects = {row.get('effect') for row in impacts}
        if not effects.intersection({'lowers', 'qualifies'}) or 'supports' in effects:
            continue
        text = _normalized_evidence(finding.get('text_ru'))
        evidence_refs = [dict(ref) for ref in finding.get('candidate_evidence_refs') or [] if isinstance(ref, dict)]
        profile_refs = [dict(ref) for ref in finding.get('profile_evidence_refs') or [] if isinstance(ref, dict)]
        if not text or not evidence_refs or not profile_refs:
            continue
        cautions.append(text)
        provenance.append({
            'source': 'deep_score_finding_qualifier',
            'finding_id': finding.get('finding_id'),
            'factor_impacts': [dict(row) for row in impacts],
            'evidence_refs': evidence_refs,
            'profile_evidence_refs': profile_refs,
            'semantic_binding': dict(binding),
        })
        if len(cautions) >= limit:
            break
    return cautions, provenance

def positive_reasons(positive_evidence: Iterable[str], limit: int = 2, source_binding=None):
    reasons: List[str] = []
    provenance: List[dict] = []
    semantic_binding = _normalized_binding(source_binding)
    for raw in positive_evidence or []:
        code, reason = _positive_reason(raw)
        if not code or not reason or reason in reasons:
            continue
        reasons.append(reason)
        row = {
            'source': 'taste_positive_evidence',
            'policy_code': code,
            'evidence': _normalized_evidence(raw),
        }
        if semantic_binding is not None:
            row['semantic_binding'] = dict(semantic_binding)
        provenance.append(row)
        if len(reasons) >= limit:
            break
    return reasons, provenance


def deep_cautions(taste_entry: dict, limit: int = 2):
    if not isinstance(taste_entry, dict) or taste_entry.get('semantic_source') != 'progressive_pass2':
        return [], []
    status = taste_entry.get('deep_negative_assessment_status')
    if status not in {'completed_with_confirmed_risk', 'completed_with_caution', 'completed_no_relevant_negative'}:
        return [], []
    binding = _normalized_binding(taste_entry.get('deep_negative_assessment_binding'))
    if binding is None:
        return [], []
    cautions = []
    provenance = []
    for finding in taste_entry.get('deep_negative_findings') or []:
        if not isinstance(finding, dict) or finding.get('disposition') != 'caution':
            continue
        text = _normalized_evidence(finding.get('text_ru'))
        refs = finding.get('evidence_refs') or []
        if not text or not refs:
            continue
        cautions.append(text)
        provenance.append({
            'source': 'deep_dossier_caution',
            'disposition': 'caution',
            'evidence_refs': [dict(ref) for ref in refs if isinstance(ref, dict)],
            'semantic_binding': dict(binding),
        })
        if len(cautions) >= limit:
            break
    return cautions, provenance


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
    provenance = []
    for row in visible:
        item = {
            'code': str(row.get('code')),
            'source': str(row.get('source')),
        }
        for field in ('category', 'evidence', 'evidence_refs', 'semantic_binding', 'disposition'):
            value = row.get(field)
            if value is not None and value != '':
                item[field] = value
        provenance.append(item)
    heuristic_candidates = sum(
        1
        for row in (risks or {}).values()
        if isinstance(row, dict) and str(row.get('source') or '') not in GROUNDED_RISK_SOURCES
    )
    status = {
        'has_described_risk': bool(visible),
        'described_risk_count': len(visible),
        'grounding': 'grounded' if visible else 'none',
        'grounded_taste_negative_witness': any(
            str(row.get('source') or '') == 'taste_negative_evidence'
            for row in visible
        ),
        'heuristic_candidate_count': heuristic_candidates,
    }
    return {
        'risks': risk_texts,
        'risk_codes': risk_codes,
        'risk_status': status,
        'risk_provenance': provenance,
    }

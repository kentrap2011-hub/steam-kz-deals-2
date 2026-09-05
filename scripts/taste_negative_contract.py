"""Grounded negative-analysis contract shared by Taste cache, queue and visual output.

V5 adds explicit provenance/strength for personal negatives while retaining
legacy V4 parsing during migration. Candidate-quality complaints live in the
separate evidence-state layer and never become personal negatives here.
"""

NEGATIVE_ANALYSIS_STATUSES = {
    'complete_with_confirmed_negative',
    'incomplete_no_confirmed_negative',
}

NEGATIVE_FINDING_CATALOG = {
    'unchanged_repetition': {'category': 'repetition', 'score': 4},
    'low_active_gameplay': {'category': 'activity_balance', 'score': 3},
    'directionlessness': {'category': 'direction', 'score': 4},
    'management_routine': {'category': 'management_routine', 'score': 3},
    'difficulty_punishment': {'category': 'difficulty_friction', 'score': 2},
    'stealth_restart_pressure': {'category': 'stealth_friction', 'score': 2},
    'felt_technical_burden': {'category': 'felt_burden', 'score': 4},
    'other_grounded_taste_risk': {'category': 'other_grounded', 'score': 0},
}
V4_FIELDS = {'category', 'code', 'evidence', 'risk_text_ru'}
V5_FIELDS = V4_FIELDS | {'evidence_origin', 'evidence_strength', 'personal_relevance'}
V5_ORIGINS = {
    'direct_user_reaction', 'title_specific_inspection', 'historical_user_experience',
    'same_series_continuity', 'candidate_specific_profile_conflict',
}
V5_STRENGTH = {'weak', 'moderate', 'strong'}


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a non-empty string')
    return value.strip()


def validate_negative_analysis(status, findings, negative_evidence, require_v5=False):
    if status not in NEGATIVE_ANALYSIS_STATUSES:
        raise ValueError(f'Unknown negative_analysis_status: {status!r}')
    if not isinstance(findings, list):
        raise ValueError('negative_findings must be an array')
    if not isinstance(negative_evidence, list):
        raise ValueError('negative_evidence must be an array')

    normalized = []
    evidence_projection = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise ValueError(f'negative_findings[{index}] must be an object')
        is_v5 = require_v5 or bool(set(finding) & (V5_FIELDS - V4_FIELDS))
        expected_fields = V5_FIELDS if is_v5 else V4_FIELDS
        unknown = set(finding) - expected_fields
        missing = expected_fields - set(finding)
        if unknown:
            raise ValueError(f'negative_findings[{index}] has unexpected fields: {sorted(unknown)}')
        if missing:
            raise ValueError(f'negative_findings[{index}] missing fields: {sorted(missing)}')

        code = _text(finding['code'], f'negative_findings[{index}].code')
        category = _text(finding['category'], f'negative_findings[{index}].category')
        spec = NEGATIVE_FINDING_CATALOG.get(code)
        if spec is None:
            raise ValueError(f'negative_findings[{index}] has unknown code: {code!r}')
        if category != spec['category']:
            raise ValueError(f'negative_findings[{index}] category/code mismatch: category={category!r} code={code!r}')
        evidence = _text(finding['evidence'], f'negative_findings[{index}].evidence')
        risk_text_ru = _text(finding['risk_text_ru'], f'negative_findings[{index}].risk_text_ru')
        row = {'category': category, 'code': code, 'evidence': evidence, 'risk_text_ru': risk_text_ru}
        if is_v5:
            origin = _text(finding['evidence_origin'], f'negative_findings[{index}].evidence_origin')
            strength = _text(finding['evidence_strength'], f'negative_findings[{index}].evidence_strength')
            relevance = _text(finding['personal_relevance'], f'negative_findings[{index}].personal_relevance')
            if origin not in V5_ORIGINS:
                raise ValueError(f'negative_findings[{index}] has invalid personal-negative evidence origin')
            if strength not in V5_STRENGTH:
                raise ValueError(f'negative_findings[{index}] has invalid evidence strength')
            if relevance != 'confirmed':
                raise ValueError(f'negative_findings[{index}] personal_relevance must be confirmed')
            row.update({
                'evidence_origin': origin,
                'evidence_strength': strength,
                'personal_relevance': relevance,
            })
        normalized.append(row)
        evidence_projection.append(evidence)

    if status == 'complete_with_confirmed_negative':
        if not normalized:
            raise ValueError('complete_with_confirmed_negative requires at least one negative finding')
    elif normalized or negative_evidence:
        raise ValueError('incomplete_no_confirmed_negative requires empty findings and evidence')

    if negative_evidence != evidence_projection:
        raise ValueError('negative_evidence must equal the ordered projection of negative_findings[].evidence')
    return normalized


def validate_entry_negative_fields(entry, *, require_v4=False, require_v5=False):
    has_status = 'negative_analysis_status' in entry
    has_findings = 'negative_findings' in entry
    if (require_v4 or require_v5) and (not has_status or not has_findings):
        raise ValueError('Taste entry requires negative_analysis_status and negative_findings')
    if not has_status and not has_findings:
        return None
    if has_status != has_findings:
        raise ValueError('negative_analysis_status and negative_findings must appear together')
    return validate_negative_analysis(
        entry.get('negative_analysis_status'), entry.get('negative_findings'),
        entry.get('negative_evidence'), require_v5=require_v5,
    )


def negative_readiness(entry):
    if not isinstance(entry, dict) or 'negative_analysis_status' not in entry:
        return {'negative_analysis_status': None, 'confirmed_negative_count': 0, 'negative_analysis_ready': False}
    try:
        findings = validate_entry_negative_fields(entry, require_v4=True)
    except ValueError:
        return {
            'negative_analysis_status': entry.get('negative_analysis_status'),
            'confirmed_negative_count': 0, 'negative_analysis_ready': False,
        }
    status = entry.get('negative_analysis_status')
    count = len(findings or [])
    return {
        'negative_analysis_status': status,
        'confirmed_negative_count': count,
        'negative_analysis_ready': status == 'complete_with_confirmed_negative' and count >= 1,
    }


def structured_grounded_risks(entry):
    readiness = negative_readiness(entry)
    if not readiness['negative_analysis_ready']:
        return {}
    findings = validate_entry_negative_fields(entry, require_v4=True)
    risks = {}
    for finding in findings:
        spec = NEGATIVE_FINDING_CATALOG[finding['code']]
        score = int(spec['score'])
        if 'evidence_strength' in finding:
            if finding['evidence_strength'] == 'weak':
                score = min(score, 1)
            elif finding['evidence_strength'] == 'moderate':
                score = min(score, 3)
        row = {
            'code': finding['code'], 'score': score, 'text': finding['risk_text_ru'],
            'source': 'taste_negative_evidence', 'category': finding['category'],
            'evidence': finding['evidence'],
        }
        for field in ('evidence_origin', 'evidence_strength', 'personal_relevance'):
            if field in finding:
                row[field] = finding[field]
        current = risks.get(finding['code'])
        if current is None or row['score'] > current['score']:
            risks[finding['code']] = row
    return risks

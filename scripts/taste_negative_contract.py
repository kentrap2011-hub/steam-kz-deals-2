"""Grounded negative-analysis contract shared by Taste cache, queue and visual output.

The contract deliberately separates fit-cache validity from negative-analysis
readiness. Legacy entries remain fit-reusable, but they are never considered
negative-ready merely because free-text ``negative_evidence`` exists.
"""

NEGATIVE_ANALYSIS_STATUSES = {
    'complete_with_confirmed_negative',
    'incomplete_no_confirmed_negative',
}

NEGATIVE_FINDING_CATALOG = {
    'unchanged_repetition': {
        'category': 'repetition',
        'score': 4,
    },
    'low_active_gameplay': {
        'category': 'activity_balance',
        'score': 3,
    },
    'directionlessness': {
        'category': 'direction',
        'score': 4,
    },
    'management_routine': {
        'category': 'management_routine',
        'score': 3,
    },
    'difficulty_punishment': {
        'category': 'difficulty_friction',
        'score': 2,
    },
    'stealth_restart_pressure': {
        'category': 'stealth_friction',
        'score': 2,
    },
    'other_grounded_taste_risk': {
        'category': 'other_grounded',
        'score': 0,
    },
}


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a non-empty string')
    return value.strip()


def validate_negative_analysis(status, findings, negative_evidence):
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
        allowed = {'category', 'code', 'evidence', 'risk_text_ru'}
        unknown = set(finding) - allowed
        missing = allowed - set(finding)
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
            raise ValueError(
                f'negative_findings[{index}] category/code mismatch: '
                f'category={category!r} code={code!r}'
            )
        evidence = _text(finding['evidence'], f'negative_findings[{index}].evidence')
        risk_text_ru = _text(finding['risk_text_ru'], f'negative_findings[{index}].risk_text_ru')
        normalized.append({
            'category': category,
            'code': code,
            'evidence': evidence,
            'risk_text_ru': risk_text_ru,
        })
        evidence_projection.append(evidence)

    if status == 'complete_with_confirmed_negative':
        if not normalized:
            raise ValueError('complete_with_confirmed_negative requires at least one negative finding')
    elif normalized or negative_evidence:
        raise ValueError('incomplete_no_confirmed_negative requires empty findings and evidence')

    if negative_evidence != evidence_projection:
        raise ValueError(
            'negative_evidence must equal the ordered projection of negative_findings[].evidence'
        )
    return normalized


def validate_entry_negative_fields(entry, *, require_v4=False):
    has_status = 'negative_analysis_status' in entry
    has_findings = 'negative_findings' in entry
    if require_v4 and (not has_status or not has_findings):
        raise ValueError('V4 Taste entry requires negative_analysis_status and negative_findings')
    if not has_status and not has_findings:
        return None
    if has_status != has_findings:
        raise ValueError('negative_analysis_status and negative_findings must appear together')
    return validate_negative_analysis(
        entry.get('negative_analysis_status'),
        entry.get('negative_findings'),
        entry.get('negative_evidence'),
    )


def negative_readiness(entry):
    """Return readiness metadata without promoting legacy free text.

    Invalid V4-shaped data fails closed rather than silently becoming ready.
    """
    if not isinstance(entry, dict) or 'negative_analysis_status' not in entry:
        return {
            'negative_analysis_status': None,
            'confirmed_negative_count': 0,
            'negative_analysis_ready': False,
        }
    try:
        findings = validate_entry_negative_fields(entry, require_v4=True)
    except ValueError:
        return {
            'negative_analysis_status': entry.get('negative_analysis_status'),
            'confirmed_negative_count': 0,
            'negative_analysis_ready': False,
        }
    status = entry.get('negative_analysis_status')
    count = len(findings or [])
    return {
        'negative_analysis_status': status,
        'confirmed_negative_count': count,
        'negative_analysis_ready': status == 'complete_with_confirmed_negative' and count >= 1,
    }


def structured_grounded_risks(entry):
    """Map validated structured findings directly to stable grounded risks.

    Evidence prose is never keyword-classified. ``other_grounded_taste_risk`` is
    intentionally retained with score 0 so a real unfamiliar downside cannot be
    lost merely because the deterministic ranking taxonomy is narrower.
    """
    readiness = negative_readiness(entry)
    if not readiness['negative_analysis_ready']:
        return {}
    findings = validate_entry_negative_fields(entry, require_v4=True)
    risks = {}
    for finding in findings:
        spec = NEGATIVE_FINDING_CATALOG[finding['code']]
        row = {
            'code': finding['code'],
            'score': int(spec['score']),
            'text': finding['risk_text_ru'],
            'source': 'taste_negative_evidence',
            'category': finding['category'],
            'evidence': finding['evidence'],
        }
        current = risks.get(finding['code'])
        if current is None or row['score'] > current['score']:
            risks[finding['code']] = row
    return risks

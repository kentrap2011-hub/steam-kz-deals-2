import json
from pathlib import Path

import play_priority_context as play_context
from taste_evidence_contract import current_evidence_contract_sha

PAYLOAD_PATH = Path('data/production/pre_ai/chatgpt_payload.json')
PROJECTION_PATH = Path('data/production/pre_ai/taste_projection.json')
QUEUE_PATH = Path('data/production/pre_ai/chatgpt_taste_queue.jsonl')
VISUAL_PATH = Path('data/production/visual/current.json')

CONTROLS = {
    'Sifu': ['Sifu'],
    'High On Life': ['High On Life'],
    'Amnesia: The Bunker': ['Amnesia: The Bunker'],
    'Terminator: Resistance': ['Terminator: Resistance'],
    'Tails of Iron 2': ['Tails of Iron 2', 'Tails of Iron 2: Whiskers of Winter'],
    'Trine 4': ['Trine 4', 'Trine 4: The Nightmare Prince'],
    'TMNT: Splintered Fate': ['TMNT: Splintered Fate', 'Teenage Mutant Ninja Turtles: Splintered Fate'],
    'HighFleet': ['HighFleet'],
    'Batman: Arkham': ['Batman: Arkham'],
    'Red Dead Redemption 2': ['Red Dead Redemption 2'],
}

ROLE_START_EXPECTED = {
    'Sifu': ['main_full', 'high'],
    'High On Life': ['main_full', 'ordinary'],
    'Amnesia: The Bunker': ['main_full', 'ordinary'],
    'Terminator: Resistance': ['main_full', 'ordinary'],
    'Tails of Iron 2': ['secondary_palate_cleanser', 'ordinary'],
    'Trine 4': ['family_coop', 'ordinary'],
    'TMNT: Splintered Fate': ['unresolved', 'unresolved'],
    'HighFleet': ['unresolved', 'low'],
}


def norm(value):
    return ' '.join(str(value or '').casefold().split())


def matches(control, title):
    text = norm(title)
    if control == 'Batman: Arkham':
        return 'batman' in text and 'arkham' in text
    return any(text == norm(alias) for alias in CONTROLS[control])


def highfleet_confirmed_negative_entry():
    return {
        'evidence_contract_sha': current_evidence_contract_sha(),
        'verdict': 'EXCLUDE',
        'fit_level': 'below_moderate',
        'reason_code': 'exclude_direct_conflict',
        'fit_evidence_state': 'confirmed_negative',
        'fit_evidence_confidence': 'high',
        'fit_evidence_basis': ['direct_user_current_reaction'],
        'historical_negative_context': None,
        'candidate_quality_findings': [],
        'negative_analysis_status': 'complete_with_confirmed_negative',
        'negative_findings': [{
            'evidence_strength': 'strong',
            'personal_relevance': 'confirmed',
            'evidence_origin': 'direct_user_current_reaction',
        }],
    }


def queue_rows():
    rows = []
    for line in QUEUE_PATH.read_text(encoding='utf-8').splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def visual_card_titles(root):
    titles = []

    def visit(value):
        if isinstance(value, dict):
            title = value.get('title')
            if isinstance(title, str) and any(
                key in value for key in (
                    'priority_rank', 'fit', 'taste_fit', 'decision', 'purchase_decision',
                    'play_role', 'relative_start_priority', 'total_score',
                )
            ):
                titles.append(title)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(root)
    return titles


def projection_matches(entries, control):
    out = []
    for key, entry in entries.items():
        if matches(control, entry.get('taste_subject_title')):
            out.append((key, entry))
    return out


def main():
    payload = json.loads(PAYLOAD_PATH.read_text(encoding='utf-8'))
    projection = json.loads(PROJECTION_PATH.read_text(encoding='utf-8'))
    queue = queue_rows()
    visual = json.loads(VISUAL_PATH.read_text(encoding='utf-8'))

    semantic = payload.get('semantic_completeness') or {}
    runtime = payload.get('semantic_runtime_observability') or {}
    assert semantic.get('total_relevant_semantic_scope') == payload.get('ai_queue_count')
    assert semantic.get('resolved_semantic_count') + semantic.get('unresolved_semantic_count') == semantic.get('total_relevant_semantic_scope')

    queue_keys = {str(row.get('taste_subject_key') or row.get('key') or '') for row in queue}
    deterministic_excluded = set(payload.get('deterministically_excluded_primary_keys') or [])
    entries = projection.get('entries') or {}
    current_visual_titles = visual_card_titles(visual)

    contract = play_context.load_contract()
    control_rows = {}
    for control in CONTROLS:
        hits = projection_matches(entries, control)
        keys = [key for key, _ in hits]
        projection_statuses = [entry.get('status') for _, entry in hits]
        pending_keys = sorted(set(keys) & queue_keys)
        excluded_keys = sorted(set(keys) & deterministic_excluded)
        visual_hits = sorted({title for title in current_visual_titles if matches(control, title)})

        if not hits:
            live_state = 'not_currently_materialized:not_in_current_source_scope'
        elif excluded_keys and len(excluded_keys) == len(keys):
            live_state = 'not_currently_materialized:deterministically_excluded_without_ai'
        elif pending_keys:
            live_state = 'semantic_pending_current_scope'
        else:
            live_state = 'source_present_not_semantic_pending'

        taste_entry = highfleet_confirmed_negative_entry() if control == 'HighFleet' else {}
        resolved_context = play_context.context_for_game({'title': CONTROLS[control][0]}, taste_entry, contract)
        deterministic_context = [resolved_context['play_role'], resolved_context['relative_start_priority']]
        if control in ROLE_START_EXPECTED:
            assert deterministic_context == ROLE_START_EXPECTED[control], (control, deterministic_context)

        control_rows[control] = {
            'live_state': live_state,
            'projection_keys': keys,
            'projection_statuses': projection_statuses,
            'semantic_pending_keys': pending_keys,
            'deterministically_excluded_keys': excluded_keys,
            'current_visual_hits': visual_hits,
            'current_visual_is_steps123_acceptance_evidence': bool(
                visual_hits and semantic.get('sufficiently_complete_for_publication') is True
            ),
            'deterministic_role_start': deterministic_context,
        }

    highfleet = control_rows['HighFleet']
    assert highfleet['deterministic_role_start'] == ['unresolved', 'low']
    assert control_rows['TMNT: Splintered Fate']['deterministic_role_start'] == ['unresolved', 'unresolved']

    publication_ready = semantic.get('sufficiently_complete_for_publication') is True
    if not publication_ready:
        assert semantic.get('unresolved_semantic_count', 0) > 0
        assert all(row['current_visual_is_steps123_acceptance_evidence'] is False for row in control_rows.values())

    result = {
        'status': 'ready_for_publication_acceptance' if publication_ready else 'blocked_semantic_runtime',
        'semantic_completeness': {
            'status': semantic.get('status'),
            'resolved': semantic.get('resolved_semantic_count'),
            'unresolved': semantic.get('unresolved_semantic_count'),
            'total': semantic.get('total_relevant_semantic_scope'),
            'sufficiently_complete_for_publication': publication_ready,
        },
        'runtime_observability': {
            'status': runtime.get('status'),
            'runtime_owner': runtime.get('runtime_owner'),
            'last_successful_semantic_execution_at_utc': runtime.get('last_successful_semantic_execution_at_utc'),
            'current_scope_source_mailing_updated_at_utc': runtime.get('current_scope_source_mailing_updated_at_utc'),
            'current_scope_progress_observed': runtime.get('current_scope_progress_observed'),
        },
        'queue_count_observed': len(queue),
        'controls': control_rows,
        'highfleet_guard': {
            'confirmed_negative_forces_play_role': 'unresolved',
            'confirmed_negative_forces_relative_start_priority': 'low',
        },
        'old_visual_snapshot_rejected_as_acceptance_evidence_when_semantic_incomplete': not publication_ready,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print('TASTE_STEPS123_PRODUCTION_ACCEPTANCE=' + ('READY' if publication_ready else 'BLOCKED_SEMANTIC_RUNTIME'))


if __name__ == '__main__':
    main()

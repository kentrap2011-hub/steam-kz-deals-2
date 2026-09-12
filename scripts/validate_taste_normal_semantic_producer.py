from normalize_next_taste_semantic_pin import TASTE_SEMANTIC_WORK_CODE, select_taste_semantic_rows
from taste_pinned_work_unit import CANONICAL_BATCH_SIZE, build_pinned_work_unit


def _row(key, work):
    suffix = key.encode('utf-8').hex()[:8].ljust(8, '0')
    return {
        'taste_subject_key': key,
        'appid': suffix,
        'taste_fingerprint': (suffix * 8)[:64],
        'candidate_context_sha256': ((suffix[::-1]) * 8)[:64],
        'work_required': list(work),
    }


def _projection():
    return {
        'status': 'complete',
        'complete_coverage': True,
        'source_mailing_updated_at_utc': '2026-09-12T00:00:00+00:00',
        'current_profile': {
            'repository': 'example/profile',
            'path': 'gaming_taste_live.json',
            'resolved_commit_sha': '1' * 40,
            'blob_sha': '2' * 40,
            'content_sha256': '3' * 64,
            'bytes': 123,
        },
        'current_binding': {
            'taste_model_version': 'taste-v3',
            'taste_semantics_sha256': '4' * 64,
        },
    }


def main():
    base_only = ['resolve_base_support_condition']
    semantic = [TASTE_SEMANTIC_WORK_CODE]
    rows = [
        _row('App_base_1', base_only),
        _row('App_sem_1', semantic),
        _row('App_base_2', base_only),
        _row('App_sem_2', semantic),
    ]
    selected = select_taste_semantic_rows(rows)
    assert [row['taste_subject_key'] for row in selected] == ['App_sem_1', 'App_sem_2']

    many = []
    for index in range(CANONICAL_BATCH_SIZE + 3):
        many.append(_row(f'App_sem_{index:02d}', semantic))
        many.append(_row(f'App_base_{index:02d}', base_only))
    selected_many = select_taste_semantic_rows(many)
    expected = [f'App_sem_{index:02d}' for index in range(CANONICAL_BATCH_SIZE + 3)]
    assert [row['taste_subject_key'] for row in selected_many] == expected

    projection = _projection()
    pin = build_pinned_work_unit(
        projection,
        selected_many,
        projection['current_profile'],
        prepared_at_utc='2026-09-12T00:00:00+00:00',
    )
    assert len(pin['ordered_rows']) == CANONICAL_BATCH_SIZE
    assert [row['key'] for row in pin['ordered_rows']] == expected[:CANONICAL_BATCH_SIZE]
    assert all(TASTE_SEMANTIC_WORK_CODE in row['work_required'] for row in pin['ordered_rows'])

    # Re-running deterministic selection against unchanged queue state produces
    # the same ordered semantic prefix; measurement checkpoint size is not a
    # production quota and no age/commercial signal participates in selection.
    selected_again = select_taste_semantic_rows(many)
    pin_again = build_pinned_work_unit(
        projection,
        selected_again,
        projection['current_profile'],
        prepared_at_utc='2026-09-12T00:00:00+00:00',
    )
    assert pin_again['ordered_rows'] == pin['ordered_rows']
    assert pin_again['ordered_work_unit_sha256'] == pin['ordered_work_unit_sha256']

    print('normal Taste semantic producer filtering regression: ok')


if __name__ == '__main__':
    main()

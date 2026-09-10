import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_daily_visual_payload as builder


def write_json(path, obj):
    path.write_text(json.dumps(obj), encoding='utf-8')


def bind_case(root, *, status, ai_count, ready_count):
    root = Path(root)
    builder.PAYLOAD = root / 'payload.json'
    builder.TASTE_QUEUE = root / 'queue.jsonl'
    builder.PURCHASE_CONTEXT = root / 'purchase.jsonl'
    source_count = ai_count + ready_count
    write_json(
        builder.PAYLOAD,
        {
            'status': status,
            'complete_family_partition': True,
            'source_family_count': source_count,
            'ready_without_ai_count': ready_count,
            'deterministically_excluded_without_ai_count': 0,
            'ai_queue_count': ai_count,
            'purchase_context_line_count': ai_count + ready_count,
            'source_mailing_updated_at_utc': '2026-09-10T00:00:00Z',
        },
    )
    builder.TASTE_QUEUE.write_text(''.join('{}\n' for _ in range(ai_count)), encoding='utf-8')
    builder.PURCHASE_CONTEXT.write_text(
        ''.join('{}\n' for _ in range(ai_count + ready_count)), encoding='utf-8'
    )


with tempfile.TemporaryDirectory() as tmp:
    bind_case(tmp, status='degraded', ai_count=1, ready_count=0)
    source_key, payload = builder.current_production_readiness()
    assert source_key is None
    assert payload['status'] == 'degraded'

with tempfile.TemporaryDirectory() as tmp:
    bind_case(tmp, status='degraded', ai_count=0, ready_count=1)
    try:
        builder.current_production_readiness()
    except SystemExit as exc:
        assert str(exc) == 'ChatGPT production payload is not complete'
    else:
        raise AssertionError('degraded payload with closed queue must remain fail-closed')

with tempfile.TemporaryDirectory() as tmp:
    bind_case(tmp, status='unknown', ai_count=1, ready_count=0)
    try:
        builder.current_production_readiness()
    except SystemExit as exc:
        assert str(exc) == 'ChatGPT production payload is not complete'
    else:
        raise AssertionError('unknown payload status must remain fail-closed')

print('visual degraded-readiness regression: ok')

import json
import os
import subprocess
from pathlib import Path

import build_visual_feed_v2 as visual_builder

ROOT = Path('.')
PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'
TASTE_QUEUE = ROOT / 'data/production/pre_ai/chatgpt_taste_queue.jsonl'
PURCHASE_CONTEXT = ROOT / 'data/production/pre_ai/chatgpt_purchase_context.jsonl'
OUT = ROOT / 'data/production/visual/current.json'


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def nonempty_line_count(path: Path):
    return sum(1 for line in path.read_text(encoding='utf-8').splitlines() if line.strip())


def git_sha(path: str):
    return subprocess.check_output(['git', 'rev-parse', f'HEAD:{path}'], text=True).strip()


def current_production_readiness():
    payload = load_json(PAYLOAD)
    if payload.get('status') != 'complete':
        raise SystemExit('ChatGPT production payload is not complete')
    if payload.get('complete_family_partition') is not True:
        raise SystemExit('Production family partition is not complete')

    source_count = int(payload.get('source_family_count') or 0)
    ready_count = int(payload.get('ready_without_ai_count') or 0)
    excluded_count = int(payload.get('deterministically_excluded_without_ai_count') or 0)
    ai_queue_count = int(payload.get('ai_queue_count') or 0)
    purchase_context_count = int(payload.get('purchase_context_line_count') or 0)

    actual_queue_count = nonempty_line_count(TASTE_QUEUE)
    actual_purchase_context_count = nonempty_line_count(PURCHASE_CONTEXT)

    if ai_queue_count != actual_queue_count:
        raise SystemExit(
            f'AI queue count mismatch: payload={ai_queue_count} actual={actual_queue_count}'
        )
    if purchase_context_count != actual_purchase_context_count:
        raise SystemExit(
            'Purchase context count mismatch: '
            f'payload={purchase_context_count} actual={actual_purchase_context_count}'
        )
    if ready_count + excluded_count + ai_queue_count != source_count:
        raise SystemExit(
            'Production partition arithmetic mismatch: '
            f'ready={ready_count} excluded={excluded_count} ai={ai_queue_count} source={source_count}'
        )

    source_key = payload.get('source_mailing_updated_at_utc')
    if not source_key:
        raise SystemExit('Production payload has no source_mailing_updated_at_utc')

    if ai_queue_count != 0:
        return None, payload

    if ready_count != purchase_context_count:
        raise SystemExit(
            'Closed AI queue must leave one purchase-context row per ready family: '
            f'ready={ready_count} purchase_context={purchase_context_count}'
        )

    return source_key, payload


def existing_source_key():
    if not OUT.exists():
        return None
    try:
        return load_json(OUT).get('source_mailing_updated_at_utc')
    except Exception:
        return None


def main():
    source_key, payload = current_production_readiness()
    if source_key is None:
        print(
            'VISUAL_DAILY_BUILD=WAIT '
            f'source={payload.get("source_mailing_updated_at_utc")} '
            f'ai_queue={payload.get("ai_queue_count")}'
        )
        return

    force = os.environ.get('FORCE_VISUAL_BUILD') == '1'
    if not force and existing_source_key() == source_key:
        print(f'VISUAL_DAILY_BUILD=SKIP source={source_key}')
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    visual_builder.OUT = OUT
    visual_builder.main()

    ready = load_json(OUT)
    ready['production_contract'] = {
        'schema_version': 2,
        'mode': 'daily_precomputed_read_only_for_ui',
        'heavy_calculation_allowed_in_ui': False,
        'external_lookup_allowed_in_ui': False,
        'source_chatgpt_payload_blob_sha': git_sha('data/production/pre_ai/chatgpt_payload.json'),
        'source_purchase_context_blob_sha': git_sha('data/production/pre_ai/chatgpt_purchase_context.jsonl'),
        'source_taste_queue_blob_sha': git_sha('data/production/pre_ai/chatgpt_taste_queue.jsonl'),
        'source_family_count': payload.get('source_family_count'),
        'ready_family_count': payload.get('ready_without_ai_count'),
        'ai_queue_count': payload.get('ai_queue_count'),
        'complete_family_partition': payload.get('complete_family_partition'),
        'canonical_profile_blob_sha': (payload.get('profile_binding') or {}).get('canonical_profile_blob_sha'),
        'taste_model_version': (payload.get('profile_binding') or {}).get('taste_model_version'),
    }
    OUT.write_text(json.dumps(ready, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'VISUAL_DAILY_BUILD=BUILT source={source_key} items={ready.get("item_count")} force={force}')


if __name__ == '__main__':
    main()

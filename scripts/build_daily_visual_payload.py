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


HISTORY_QUALITY_ORDER = {
    'record': 0,
    'near_record': 1,
    'good_vs_history': 2,
    'previously_free': 3,
    'unverified': 4,
    'well_above_history': 5,
}

WINDOWS_ORDER = {
    'modern': 0,
    'unknown': 1,
    'older_but_plausible': 3,
    'legacy': 4,
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding='utf-8').splitlines()
        if line.strip()
    ]


def nonempty_line_count(path: Path):
    return sum(1 for line in path.read_text(encoding='utf-8').splitlines() if line.strip())


def git_sha(path: str):
    return subprocess.check_output(['git', 'rev-parse', f'HEAD:{path}'], text=True).strip()


def achievements_rank(value):
    return 0 if value is True else (1 if value is None else 2)


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


def existing_identity():
    if not OUT.exists():
        return None, None, None
    try:
        current = load_json(OUT)
        contract = current.get('production_contract') or {}
        return (
            current.get('source_mailing_updated_at_utc'),
            contract.get('visual_builder_blob_sha'),
            contract.get('daily_visual_builder_blob_sha'),
        )
    except Exception:
        return None, None, None


def apply_canonical_priority_order(ready):
    context_by_family = {
        str(row.get('family_id')): row
        for row in load_jsonl(PURCHASE_CONTEXT)
        if row.get('family_id')
    }

    def key(game):
        row = context_by_family.get(str(game.get('id'))) or {}
        history = row.get('history') or {}
        history_quality = history.get('quality') or 'unverified'
        practical = game.get('practical') or {}
        windows_status = practical.get('windows_status') or 'unknown'
        return (
            int(game.get('priority_bucket') or 99),
            WINDOWS_ORDER.get(windows_status, 1),
            achievements_rank(practical.get('steam_achievements')),
            -int(bool(game.get('wishlist'))),
            HISTORY_QUALITY_ORDER.get(history_quality, 99),
            -int(game.get('discount_percent') or 0),
            int(game.get('current_price_rub') or 999999),
            (game.get('title') or '').casefold(),
        )

    items = ready.get('items') or []
    items.sort(key=key)
    for index, game in enumerate(items, 1):
        game['priority_rank'] = index
    ready['items'] = items
    ready['item_count'] = len(items)
    return ready


def main():
    source_key, payload = current_production_readiness()
    if source_key is None:
        print(
            'VISUAL_DAILY_BUILD=WAIT '
            f'source={payload.get("source_mailing_updated_at_utc")} '
            f'ai_queue={payload.get("ai_queue_count")}'
        )
        return

    builder_sha = git_sha('scripts/build_visual_feed_v2.py')
    daily_builder_sha = git_sha('scripts/build_daily_visual_payload.py')
    current_source, current_builder, current_daily_builder = existing_identity()
    force = os.environ.get('FORCE_VISUAL_BUILD') == '1'
    if (
        not force
        and current_source == source_key
        and current_builder == builder_sha
        and current_daily_builder == daily_builder_sha
    ):
        print(
            f'VISUAL_DAILY_BUILD=SKIP source={source_key} '
            f'builder={builder_sha} daily_builder={daily_builder_sha}'
        )
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    visual_builder.OUT = OUT
    visual_builder.main()

    ready = apply_canonical_priority_order(load_json(OUT))
    ready['production_contract'] = {
        'schema_version': 3,
        'mode': 'daily_precomputed_read_only_for_ui',
        'heavy_calculation_allowed_in_ui': False,
        'external_lookup_allowed_in_ui': False,
        'visual_builder_blob_sha': builder_sha,
        'daily_visual_builder_blob_sha': daily_builder_sha,
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
    print(
        f'VISUAL_DAILY_BUILD=BUILT source={source_key} items={ready.get("item_count")} '
        f'builder={builder_sha} daily_builder={daily_builder_sha} force={force}'
    )


if __name__ == '__main__':
    main()

import json
import subprocess
from pathlib import Path

import build_visual_feed_v2 as visual_builder

ROOT = Path('.')
FINAL_CHECK = ROOT / 'data/cache/final_self_check.validation.json'
PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'
TASTE_QUEUE = ROOT / 'data/production/pre_ai/chatgpt_taste_queue.jsonl'
OUT = ROOT / 'data/production/visual/current.json'


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def git_sha(path: str):
    return subprocess.check_output(['git', 'rev-parse', f'HEAD:{path}'], text=True).strip()


def assert_ready():
    final_check = load_json(FINAL_CHECK)
    payload = load_json(PAYLOAD)

    if final_check.get('status') != 'complete' or int(final_check.get('mechanical_assertions_failed') or 0) != 0:
        raise SystemExit('Final self-check is not complete')
    if payload.get('status') != 'complete':
        raise SystemExit('ChatGPT production payload is not complete')

    queue_lines = [line for line in TASTE_QUEUE.read_text(encoding='utf-8').splitlines() if line.strip()]
    ai_queue_count = int(payload.get('ai_queue_count') or 0)
    if ai_queue_count != len(queue_lines):
        raise SystemExit('AI queue count does not match JSONL line count')
    if ai_queue_count != 0:
        raise SystemExit(f'AI taste queue is not closed: {ai_queue_count} candidates remain')

    bindings = final_check.get('bindings') or {}
    current_bindings = {
        'policy_blob_sha': git_sha('config/mailing_policy.json'),
        'mailing_tree_sha': git_sha('data/production/mailing'),
        'feed_ingest_blob_sha': git_sha('data/cache/feed_ingest.validation.json'),
        'taste_index_blob_sha': git_sha('data/cache/taste_fit.index.json'),
        'taste_validation_blob_sha': git_sha('data/cache/taste_fit.validation.json'),
        'ledger_blob_sha': git_sha('data/cache/taste_fit.ledger_validation.json'),
        'checkpoint_blob_sha': git_sha('data/cache/taste_fit.checkpoint_validation.json'),
        'content_blob_sha': git_sha('data/cache/content_eligibility.validation.json'),
        'family_blob_sha': git_sha('data/cache/offer_family.validation.json'),
        'store_blob_sha': git_sha('data/cache/store_state.validation.json'),
        'steamdb_blob_sha': git_sha('data/cache/steamdb_cache.validation.json'),
        'deal_quality_blob_sha': git_sha('data/cache/deal_quality.validation.json'),
    }
    stale = [name for name, sha in current_bindings.items() if bindings.get(name) != sha]
    if stale:
        raise SystemExit('Final self-check is stale for current production state: ' + ', '.join(stale))

    source_key = payload.get('source_mailing_updated_at_utc')
    if not source_key:
        raise SystemExit('Production payload has no source_mailing_updated_at_utc')
    return source_key, final_check


def existing_source_key():
    if not OUT.exists():
        return None
    try:
        return load_json(OUT).get('source_mailing_updated_at_utc')
    except Exception:
        return None


def main():
    source_key, final_check = assert_ready()
    if existing_source_key() == source_key:
        print(f'VISUAL_DAILY_BUILD=SKIP source={source_key}')
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    visual_builder.OUT = OUT
    visual_builder.main()

    ready = load_json(OUT)
    ready['production_contract'] = {
        'schema_version': 1,
        'mode': 'daily_precomputed_read_only_for_ui',
        'heavy_calculation_allowed_in_ui': False,
        'external_lookup_allowed_in_ui': False,
        'source_final_self_check_blob_sha': git_sha('data/cache/final_self_check.validation.json'),
        'source_final_self_check_status': final_check.get('status'),
    }
    OUT.write_text(json.dumps(ready, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'VISUAL_DAILY_BUILD=BUILT source={source_key} items={ready.get("item_count")}')


if __name__ == '__main__':
    main()

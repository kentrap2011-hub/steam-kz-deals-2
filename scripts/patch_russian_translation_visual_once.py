#!/usr/bin/env python3
from pathlib import Path

PATH = Path('scripts/build_visual_feed_v2.py')
text = PATH.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor, found {count}')
    text = text.replace(old, new, 1)


replace_once(
    "from russian_description_quality import classify_description, resolve_description\n",
    "from russian_description_quality import classify_description\n"
    "from russian_description_translation_runtime import (\n"
    "    load_translation_cache,\n"
    "    resolve_description_for_appids as resolve_description_with_translation_cache,\n"
    ")\n",
    'translation runtime import',
)
replace_once(
    "CHATGPT_PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'\nOUT = ROOT / 'web/data/current.json'\n",
    "CHATGPT_PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'\n"
    "TRANSLATION_CACHE = ROOT / 'data/cache/russian_description_translations.json'\n"
    "OUT = ROOT / 'web/data/current.json'\n",
    'translation cache constant',
)

start = text.index('def resolve_description_for_appids(appids, media, content_metadata_by_appid):\n')
end = text.index('\n\ndef classify_windows(requirements):', start)
replacement = '''def resolve_description_for_appids(appids, media, content_metadata_by_appid, translation_cache):
    return resolve_description_with_translation_cache(
        appids,
        media,
        content_metadata_by_appid,
        translation_cache,
    )
'''
text = text[:start] + replacement + text[end:]

replace_once(
    "    payload = load_json(CHATGPT_PAYLOAD)\n    rate = (payload.get('fx_binding') or {}).get('kzt_per_rub')\n",
    "    payload = load_json(CHATGPT_PAYLOAD)\n"
    "    translation_cache = load_translation_cache(TRANSLATION_CACHE)\n"
    "    rate = (payload.get('fx_binding') or {}).get('kzt_per_rub')\n",
    'load translation cache',
)
replace_once(
    "        description = resolve_description_for_appids(\n            base_appids,\n            media,\n            content_metadata_by_appid,\n        )\n",
    "        description_resolution = resolve_description_for_appids(\n"
    "            base_appids,\n"
    "            media,\n"
    "            content_metadata_by_appid,\n"
    "            translation_cache,\n"
    "        )\n",
    'cache-aware description call',
)
replace_once(
    "        description = projection.get('short_description') or ''\n",
    "        taste_description = projection.get('short_description') or ''\n",
    'taste description variable',
)
replace_once(
    "            translated = reason_ru(ev, tags, description)\n",
    "            translated = reason_ru(ev, tags, taste_description)\n",
    'reason description variable',
)
replace_once(
    "            reasons.append(reason_ru(None, tags, description))\n",
    "            reasons.append(reason_ru(None, tags, taste_description))\n",
    'fallback reason description variable',
)
replace_once(
    "        risks = derive_risks(taste_entry.get('negative_evidence') or [], tags, description, projection.get('release_date'), practical)\n",
    "        risks = derive_risks(taste_entry.get('negative_evidence') or [], tags, taste_description, projection.get('release_date'), practical)\n",
    'risk description variable',
)
for field in [
    'summary',
    'description_status',
    'description_source_locale',
    'description_source_quality',
    'description_source_appid',
    'description_source_path',
    'description_source_text',
]:
    replace_once(
        f"            '{field}': description.get('{field}'),\n",
        f"            '{field}': description_resolution.get('{field}'),\n",
        f'visible {field}',
    )

# Expose exact cache provenance without making the UI responsible for resolution.
replace_once(
    "            'description_source_text': description_resolution.get('description_source_text'),\n            'gameplay_points': [],\n",
    "            'description_source_text': description_resolution.get('description_source_text'),\n"
    "            'description_translation_request_id': description_resolution.get('description_translation_request_id'),\n"
    "            'description_translation_source_text_sha256': description_resolution.get('description_translation_source_text_sha256'),\n"
    "            'description_translation_source_version': description_resolution.get('description_translation_source_version'),\n"
    "            'gameplay_points': [],\n",
    'visible translation provenance',
)

PATH.write_text(text, encoding='utf-8')
print('RUSSIAN_TRANSLATION_VISUAL_PATCH_APPLIED')

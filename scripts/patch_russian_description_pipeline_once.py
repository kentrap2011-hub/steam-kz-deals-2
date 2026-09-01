from pathlib import Path


def read(path):
    return Path(path).read_text(encoding='utf-8')


def write(path, text):
    Path(path).write_text(text, encoding='utf-8')


def replace_once(path, old, new, label):
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, found {count}')
    write(path, text.replace(old, new))


def insert_after(path, anchor, addition, label):
    replace_once(path, anchor, anchor + addition, label)


def insert_before(path, anchor, addition, label):
    replace_once(path, anchor, addition + anchor, label)


visual = 'scripts/build_visual_feed_v2.py'
final = 'scripts/build_final_visual_payload.py'
daily = '.github/workflows/build-daily-visual-payload.yml'
deploy = '.github/workflows/deploy-visual.yml'

insert_after(
    visual,
    'from pathlib import Path\n',
    '\nfrom russian_description_quality import classify_description, resolve_description\n',
    'visual import',
)
insert_after(
    visual,
    "STORE_SNAPSHOT = ROOT / 'data/production/pre_ai/store_snapshot.json'\n",
    "CONTENT_METADATA = ROOT / 'data/production/pre_ai/content_metadata.json'\n",
    'content metadata constant',
)
replace_once(
    visual,
    "    return bool(value and re.search(r'[А-Яа-яЁё]', str(value)))",
    "    return classify_description(value) == 'good_ru'",
    'Russian quality gate',
)
insert_after(
    visual,
    "            desc = str((store_item.get('basic_info') or {}).get('short_description') or '').strip() or None\n",
    "            desc_quality = classify_description(desc)\n",
    'description quality classification',
)
replace_once(
    visual,
    "                'short_description_ru': desc if has_russian_text(desc) else None,\n",
    "                'short_description_source': desc,\n"
    "                'short_description_source_quality': desc_quality,\n"
    "                'short_description_ru': desc if desc_quality == 'good_ru' else None,\n",
    'preserve raw source',
)
resolver = r'''

def load_content_metadata_by_appid():
    entries = load_json(CONTENT_METADATA).get('entries') or {}
    return {
        str(entry.get('steam_id')): entry
        for entry in entries.values()
        if isinstance(entry, dict)
        and entry.get('entity_kind') == 'app'
        and entry.get('steam_id')
    }


def resolve_description_for_appids(appids, media, content_metadata_by_appid):
    resolutions = []
    for appid in [str(x) for x in appids]:
        m = media.get(appid) or {}
        metadata = content_metadata_by_appid.get(appid) or {}
        resolution = resolve_description(
            m.get('short_description_source'),
            metadata.get('short_description'),
        )
        resolution['description_source_appid'] = appid
        if resolution.get('description_source_locale') == 'english':
            resolution['description_source_path'] = 'data/production/pre_ai/content_metadata.json'
        elif resolution.get('description_source_locale') == 'russian':
            resolution['description_source_path'] = 'IStoreBrowseService/GetItems(language=russian)'
        else:
            resolution['description_source_path'] = None
        if resolution.get('description_status') == 'ready_ru':
            return resolution
        resolutions.append(resolution)

    if not resolutions:
        return resolve_description(None, None)

    priority = {
        'needs_translation': 0,
        'needs_ru_rewrite': 1,
        'technical_source': 2,
        'missing_source': 3,
    }
    return min(resolutions, key=lambda row: priority.get(row.get('description_status'), 99))


'''.lstrip('\n')
insert_before(visual, 'def classify_windows(requirements):\n', resolver, 'description resolver')
insert_after(
    visual,
    "    store_entries = load_json(STORE_SNAPSHOT).get('entries') or {}\n",
    "    content_metadata_by_appid = load_content_metadata_by_appid()\n",
    'load content metadata',
)
replace_once(
    visual,
    '        screenshots, header, summary = [], None, None\n',
    '        screenshots, header = [], None\n',
    'description loop init',
)
replace_once(
    visual,
    "            summary = summary or m.get('short_description_ru')\n",
    '',
    'remove legacy summary selection',
)
description_block = r'''        description = resolve_description_for_appids(
            base_appids,
            media,
            content_metadata_by_appid,
        )

'''
insert_before(
    visual,
    "        taste_key = row.get('taste_subject_key')\n",
    description_block,
    'resolve card description',
)
replace_once(
    visual,
    "            'summary': summary or 'Русское краткое описание для этой игры пока не подготовлено.',\n",
    "            'summary': description.get('summary'),\n"
    "            'description_status': description.get('description_status'),\n"
    "            'description_source_locale': description.get('description_source_locale'),\n"
    "            'description_source_quality': description.get('description_source_quality'),\n"
    "            'description_source_appid': description.get('description_source_appid'),\n"
    "            'description_source_path': description.get('description_source_path'),\n"
    "            'description_source_text': description.get('description_source_text'),\n",
    'remove published placeholder',
)

insert_after(
    final,
    "    media = base_builder.visual_builder.storebrowse_media(wanted_appids) if wanted_appids else {}\n",
    "    content_metadata_by_appid = base_builder.visual_builder.load_content_metadata_by_appid()\n",
    'refresh content metadata',
)
refresh_block = r'''
        description = base_builder.visual_builder.resolve_description_for_appids(
            game.get('base_appids') or [],
            media,
            content_metadata_by_appid,
        )
        description_fields = {
            'summary': description.get('summary'),
            'description_status': description.get('description_status'),
            'description_source_locale': description.get('description_source_locale'),
            'description_source_quality': description.get('description_source_quality'),
            'description_source_appid': description.get('description_source_appid'),
            'description_source_path': description.get('description_source_path'),
            'description_source_text': description.get('description_source_text'),
        }
        for key, value in description_fields.items():
            if game.get(key) != value:
                game[key] = value
                changed = True

'''.lstrip('\n')
insert_before(
    final,
    "        if changed:\n            touched += 1\n",
    refresh_block,
    'refresh descriptions',
)

insert_after(
    daily,
    '      - "scripts/build_visual_feed_v2.py"\n',
    '      - "scripts/russian_description_quality.py"\n'
    '      - "scripts/test_russian_description_quality.py"\n'
    '      - "scripts/validate_russian_descriptions.py"\n',
    'daily trigger paths',
)
daily_test = '''      - name: Validate Russian description quality rules
        shell: bash
        run: |
          set -euo pipefail
          python scripts/test_russian_description_quality.py

'''
insert_before(
    daily,
    '      - name: Require complete history classification coverage before replacing daily visual\n',
    daily_test,
    'daily targeted regression',
)
daily_gate = '''      - name: Require meaningful Russian descriptions before canonical commit
        if: steps.build.outputs.built == 'true'
        shell: bash
        run: |
          set -euo pipefail
          python scripts/validate_russian_descriptions.py data/production/visual/current.json

'''
insert_before(
    daily,
    '      - name: Build ranking review export\n',
    daily_gate,
    'daily pre-commit gate',
)

insert_after(
    deploy,
    "      - 'data/production/visual/current.json'\n",
    "      - 'scripts/russian_description_quality.py'\n"
    "      - 'scripts/validate_russian_descriptions.py'\n",
    'deploy trigger paths',
)
deploy_gate = '''      - name: Require meaningful Russian descriptions
        shell: bash
        run: |
          set -euo pipefail
          python scripts/validate_russian_descriptions.py data/production/visual/current.json

'''
insert_before(
    deploy,
    '      - name: Run UI regressions\n',
    deploy_gate,
    'deploy gate',
)

print('RUSSIAN_DESCRIPTION_PIPELINE_PATCH=PASS')

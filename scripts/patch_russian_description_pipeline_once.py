from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one patch fragment, found {count}')
    p.write_text(text.replace(old, new), encoding='utf-8')


replace_once(
    'scripts/build_visual_feed_v2.py',
    '''from pathlib import Path

ROOT = Path('.')''',
    '''from pathlib import Path

from russian_description_quality import classify_description, resolve_description

ROOT = Path('.')''',
    'visual import',
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    '''STORE_SNAPSHOT = ROOT / 'data/production/pre_ai/store_snapshot.json'
FAMILY_GRAPH = ROOT / 'data/production/pre_ai/family_graph.json' ''',
    '''STORE_SNAPSHOT = ROOT / 'data/production/pre_ai/store_snapshot.json'
CONTENT_METADATA = ROOT / 'data/production/pre_ai/content_metadata.json'
FAMILY_GRAPH = ROOT / 'data/production/pre_ai/family_graph.json' ''',
    'content metadata constant',
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    '''def has_russian_text(value):
    return bool(value and re.search(r'[А-Яа-яЁё]', str(value)))''',
    '''def has_russian_text(value):
    return classify_description(value) == 'good_ru' ''',
    'Russian quality gate',
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    '''            desc = str((store_item.get('basic_info') or {}).get('short_description') or '').strip() or None
            result[result_key] = {
                'screenshots': shots,
                'header_image': header,
                'short_description_ru': desc if has_russian_text(desc) else None,
            }
    return result


def classify_windows(requirements):''',
    '''            desc = str((store_item.get('basic_info') or {}).get('short_description') or '').strip() or None
            desc_quality = classify_description(desc)
            result[result_key] = {
                'screenshots': shots,
                'header_image': header,
                'short_description_source': desc,
                'short_description_source_quality': desc_quality,
                'short_description_ru': desc if desc_quality == 'good_ru' else None,
            }
    return result


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
    return min(
        resolutions,
        key=lambda row: priority.get(row.get('description_status'), 99),
    )


def classify_windows(requirements):''',
    'source preservation and resolver',
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    '''    rows = load_jsonl(PURCHASE_CONTEXT)
    store_entries = load_json(STORE_SNAPSHOT).get('entries') or {}
    family_obj = load_json(FAMILY_GRAPH)''',
    '''    rows = load_jsonl(PURCHASE_CONTEXT)
    store_entries = load_json(STORE_SNAPSHOT).get('entries') or {}
    content_metadata_by_appid = load_content_metadata_by_appid()
    family_obj = load_json(FAMILY_GRAPH)''',
    'load persisted source metadata',
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    '''        screenshots, header, summary = [], None, None
        for appid in base_appids:
            m = media.get(appid) or {}
            header = header or m.get('header_image')
            summary = summary or m.get('short_description_ru')
            for url in m.get('screenshots') or []:
                if url not in screenshots:
                    screenshots.append(url)
                if len(screenshots) >= 5:
                    break
''',
    '''        screenshots, header = [], None
        for appid in base_appids:
            m = media.get(appid) or {}
            header = header or m.get('header_image')
            for url in m.get('screenshots') or []:
                if url not in screenshots:
                    screenshots.append(url)
                if len(screenshots) >= 5:
                    break

        description = resolve_description_for_appids(
            base_appids,
            media,
            content_metadata_by_appid,
        )
''',
    'card description resolution',
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    '''            'summary': summary or 'Русское краткое описание для этой игры пока не подготовлено.',
            'gameplay_points': [],''',
    '''            'summary': description.get('summary'),
            'description_status': description.get('description_status'),
            'description_source_locale': description.get('description_source_locale'),
            'description_source_quality': description.get('description_source_quality'),
            'description_source_appid': description.get('description_source_appid'),
            'description_source_path': description.get('description_source_path'),
            'description_source_text': description.get('description_source_text'),
            'gameplay_points': [],''',
    'remove published placeholder',
)

replace_once(
    'scripts/build_final_visual_payload.py',
    '''    media = base_builder.visual_builder.storebrowse_media(wanted_appids) if wanted_appids else {}
    touched = 0
    for game in items:''',
    '''    media = base_builder.visual_builder.storebrowse_media(wanted_appids) if wanted_appids else {}
    content_metadata_by_appid = base_builder.visual_builder.load_content_metadata_by_appid()
    touched = 0
    for game in items:''',
    'refresh source metadata load',
)
replace_once(
    'scripts/build_final_visual_payload.py',
    '''        changed = False
        if screenshots and screenshots != (game.get('screenshots') or []):
            game['screenshots'] = screenshots
            changed = True
        if header and header != game.get('header_image'):
            game['header_image'] = header
            changed = True
        if changed:
            touched += 1
''',
    '''        changed = False
        if screenshots and screenshots != (game.get('screenshots') or []):
            game['screenshots'] = screenshots
            changed = True
        if header and header != game.get('header_image'):
            game['header_image'] = header
            changed = True

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

        if changed:
            touched += 1
''',
    'deterministic refresh descriptions',
)

replace_once(
    '.github/workflows/build-daily-visual-payload.yml',
    '''      - "scripts/build_visual_feed_v2.py"
      - "scripts/apply_fixed_package_purchase_options.py"''',
    '''      - "scripts/build_visual_feed_v2.py"
      - "scripts/russian_description_quality.py"
      - "scripts/test_russian_description_quality.py"
      - "scripts/validate_russian_descriptions.py"
      - "scripts/apply_fixed_package_purchase_options.py"''',
    'visual workflow trigger paths',
)
replace_once(
    '.github/workflows/build-daily-visual-payload.yml',
    '''      - name: Require complete history classification coverage before replacing daily visual
        id: history''',
    '''      - name: Validate Russian description quality rules
        shell: bash
        run: |
          set -euo pipefail
          python scripts/test_russian_description_quality.py

      - name: Require complete history classification coverage before replacing daily visual
        id: history''',
    'targeted description regression step',
)
replace_once(
    '.github/workflows/build-daily-visual-payload.yml',
    '''      - name: Build ranking review export
        if: steps.build.outputs.built == 'true' ''',
    '''      - name: Require meaningful Russian descriptions before canonical commit
        if: steps.build.outputs.built == 'true'
        shell: bash
        run: |
          set -euo pipefail
          python scripts/validate_russian_descriptions.py data/production/visual/current.json

      - name: Build ranking review export
        if: steps.build.outputs.built == 'true' ''',
    'pre-commit description validation',
)

replace_once(
    '.github/workflows/deploy-visual.yml',
    '''      - 'data/production/visual/current.json'
      - '.github/workflows/deploy-visual.yml' ''',
    '''      - 'data/production/visual/current.json'
      - 'scripts/russian_description_quality.py'
      - 'scripts/validate_russian_descriptions.py'
      - '.github/workflows/deploy-visual.yml' ''',
    'deploy trigger paths',
)
replace_once(
    '.github/workflows/deploy-visual.yml',
    '''      - name: Run UI regressions
        shell: bash''',
    '''      - name: Require meaningful Russian descriptions
        shell: bash
        run: |
          set -euo pipefail
          python scripts/validate_russian_descriptions.py data/production/visual/current.json

      - name: Run UI regressions
        shell: bash''',
    'deploy description validation',
)

print('RUSSIAN_DESCRIPTION_PIPELINE_PATCH=PASS')

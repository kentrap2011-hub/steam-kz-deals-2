from pathlib import Path
import importlib.util
import re

visual_path = Path('scripts/build_visual_feed_v2.py')
visual = visual_path.read_text(encoding='utf-8')
old = """        for store_item in (data.get('response') or {}).get('store_items') or []:
            appid = str(store_item.get('appid') or store_item.get('id') or '')
            if not appid:
                continue
            shots = []
            for shot in ((store_item.get('screenshots') or {}).get('all_ages_screenshots') or []):
                filename = str(shot.get('filename') or '').strip()
                if filename:
                    img = f'https://shared.fastly.steamstatic.com/store_item_assets/{filename}'
                    if img not in shots:
                        shots.append(img)
                if len(shots) >= 5:
                    break
            assets = store_item.get('assets') or {}
            header_file = str(assets.get('header') or '').strip()
            header = f'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/{header_file}' if header_file else None
            desc = str((store_item.get('basic_info') or {}).get('short_description') or '').strip() or None
            result[appid] = {'screenshots': shots, 'header_image': header, 'short_description_ru': desc if has_russian_text(desc) else None}
"""
new = """        requested_ids = set(batch)
        for store_item in (data.get('response') or {}).get('store_items') or []:
            # StoreBrowse may resolve a requested storefront app to another internal
            # appid for its assets. `id` preserves the requested storefront identity;
            # `appid` is still the correct path component for the returned assets.
            request_id = str(store_item.get('id') or '').strip()
            asset_appid = str(store_item.get('appid') or request_id).strip()
            result_key = request_id if request_id in requested_ids else asset_appid
            if not result_key or not asset_appid:
                continue
            shots = []
            for shot in ((store_item.get('screenshots') or {}).get('all_ages_screenshots') or []):
                filename = str(shot.get('filename') or '').strip()
                if filename:
                    img = f'https://shared.fastly.steamstatic.com/store_item_assets/{filename}'
                    if img not in shots:
                        shots.append(img)
                if len(shots) >= 5:
                    break
            assets = store_item.get('assets') or {}
            header_file = str(assets.get('header') or '').strip()
            header = f'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{asset_appid}/{header_file}' if header_file else None
            desc = str((store_item.get('basic_info') or {}).get('short_description') or '').strip() or None
            result[result_key] = {
                'screenshots': shots,
                'header_image': header,
                'short_description_ru': desc if has_russian_text(desc) else None,
            }
"""
if old not in visual:
    raise SystemExit('StoreBrowse media source block not found')
visual_path.write_text(visual.replace(old, new, 1), encoding='utf-8')

final_path = Path('scripts/build_final_visual_payload.py')
final = final_path.read_text(encoding='utf-8')
marker = """    ready['items'] = refined
    ready['item_count'] = len(refined)
    contract = ready.setdefault('production_contract', {})
"""
replacement = """    ready['items'] = refined
    ready['item_count'] = len(refined)
    with_screenshots = sum(bool(game.get('screenshots')) for game in refined)
    with_any_image = sum(bool(game.get('screenshots') or game.get('header_image')) for game in refined)
    ready['media_coverage'] = {
        'visible_item_count': len(refined),
        'with_screenshots': with_screenshots,
        'with_any_image': with_any_image,
        'without_any_image': len(refined) - with_any_image,
        'coverage_percent': round((with_any_image / len(refined)) * 100, 1) if refined else 100.0,
    }
    contract = ready.setdefault('production_contract', {})
"""
if marker not in final:
    raise SystemExit('final producer media coverage marker not found')
final_path.write_text(final.replace(marker, replacement, 1), encoding='utf-8')

backlog_path = Path('BACKLOG.md')
backlog = backlog_path.read_text(encoding='utf-8')
title = 'Media: устранить карточки без скриншотов'
pattern = rf'\n### {re.escape(title)}\n.*?(?=\n### |\Z)'
backlog, count = re.subn(pattern, '\n', backlog, count=1, flags=re.S)
if count != 1:
    raise SystemExit('media backlog section not found exactly once')
backlog_path.write_text(backlog, encoding='utf-8')

spec = importlib.util.spec_from_file_location('visual_media_regression', visual_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
media = module.storebrowse_media(['901735'])
row = media.get('901735') or {}
print(
    'STRONGHOLD_MEDIA_REGRESSION=',
    {
        'keys': list(media),
        'screenshots': len(row.get('screenshots') or []),
        'header': bool(row.get('header_image')),
    },
)
if not row.get('screenshots') or not row.get('header_image'):
    raise SystemExit(f'Stronghold media regression failed: {media}')

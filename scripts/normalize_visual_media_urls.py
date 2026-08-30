import json
import re
import urllib.request
from pathlib import Path

PAYLOAD = Path('data/production/visual/current.json')
AKAMAI_PREFIX = 'https://shared.akamai.steamstatic.com/'
FASTLY_PREFIX = 'https://shared.fastly.steamstatic.com/'
ASSET_APP_RE = re.compile(r'/steam/apps/(\d+)/')


def undo_forced_akamai(value):
    if isinstance(value, str) and value.startswith(AKAMAI_PREFIX):
        return FASTLY_PREFIX + value[len(AKAMAI_PREFIX):], True
    return value, False


def asset_appid(item):
    values = [item.get('header_image'), *(item.get('screenshots') or [])]
    for value in values:
        match = ASSET_APP_RE.search(str(value or ''))
        if match:
            return match.group(1)
    return None


def appdetails_media(appid):
    url = f'https://store.steampowered.com/api/appdetails?appids={appid}&cc=kz&l=russian'
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'steam-kz-deals-visual/3.1', 'Accept': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode('utf-8'))
        wrapper = payload.get(str(appid)) or {}
        data = wrapper.get('data') if wrapper.get('success') else None
        if not isinstance(data, dict):
            return None
        screenshots = []
        for shot in data.get('screenshots') or []:
            value = str(shot.get('path_full') or shot.get('path_thumbnail') or '').strip()
            if value and value not in screenshots:
                screenshots.append(value)
            if len(screenshots) >= 5:
                break
        header = str(data.get('header_image') or '').strip() or None
        if not screenshots and not header:
            return None
        return {'screenshots': screenshots, 'header_image': header}
    except Exception as exc:
        print(f'VISUAL_MEDIA_ALIAS_FETCH_FAILED appid={appid} error={type(exc).__name__}:{exc}')
        return None


def main():
    if not PAYLOAD.exists():
        raise SystemExit(f'missing payload: {PAYLOAD}')

    data = json.loads(PAYLOAD.read_text(encoding='utf-8'))
    changed_items = 0
    host_reverts = 0
    aliases_seen = 0
    aliases_refreshed = 0
    appdetails_cache = {}

    for item in data.get('items') or []:
        item_changed = False

        header, did_change = undo_forced_akamai(item.get('header_image'))
        if did_change:
            item['header_image'] = header
            host_reverts += 1
            item_changed = True

        screenshots = []
        for value in item.get('screenshots') or []:
            normalized, did_change = undo_forced_akamai(value)
            screenshots.append(normalized)
            if did_change:
                host_reverts += 1
                item_changed = True
        if screenshots:
            item['screenshots'] = screenshots

        requested = {str(x) for x in item.get('base_appids') or [] if str(x).isdigit()}
        actual = asset_appid(item)
        if actual and requested and actual not in requested:
            aliases_seen += 1
            if actual not in appdetails_cache:
                appdetails_cache[actual] = appdetails_media(actual)
            canonical = appdetails_cache.get(actual)
            if canonical:
                canonical_screens = canonical.get('screenshots') or []
                canonical_header = canonical.get('header_image')
                if canonical_screens and canonical_screens != (item.get('screenshots') or []):
                    item['screenshots'] = canonical_screens
                    item_changed = True
                if canonical_header and canonical_header != item.get('header_image'):
                    item['header_image'] = canonical_header
                    item_changed = True
                aliases_refreshed += 1
                print(
                    f'VISUAL_MEDIA_ALIAS_REFRESHED item={item.get("id")} '
                    f'asset_appid={actual} screenshots={len(canonical_screens)}'
                )

        if item_changed:
            changed_items += 1

    if changed_items:
        PAYLOAD.write_text(
            json.dumps(data, ensure_ascii=False, separators=(',', ':')),
            encoding='utf-8',
        )

    print(
        f'VISUAL_MEDIA_ITEMS_CHANGED={changed_items} '
        f'HOST_REVERTS={host_reverts} ALIASES_SEEN={aliases_seen} '
        f'ALIASES_REFRESHED={aliases_refreshed}'
    )


if __name__ == '__main__':
    main()

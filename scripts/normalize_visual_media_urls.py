import json
from pathlib import Path

PAYLOAD = Path('data/production/visual/current.json')
OLD_PREFIX = 'https://shared.fastly.steamstatic.com/'
NEW_PREFIX = 'https://shared.akamai.steamstatic.com/'


def normalize_url(value):
    if isinstance(value, str) and value.startswith(OLD_PREFIX):
        return NEW_PREFIX + value[len(OLD_PREFIX):], True
    return value, False


def main():
    if not PAYLOAD.exists():
        raise SystemExit(f'missing payload: {PAYLOAD}')

    data = json.loads(PAYLOAD.read_text(encoding='utf-8'))
    changed = 0

    for item in data.get('items') or []:
        header, did_change = normalize_url(item.get('header_image'))
        if did_change:
            item['header_image'] = header
            changed += 1

        screenshots = []
        for url in item.get('screenshots') or []:
            normalized, did_change = normalize_url(url)
            screenshots.append(normalized)
            changed += int(did_change)
        if screenshots:
            item['screenshots'] = screenshots

    if changed:
        PAYLOAD.write_text(
            json.dumps(data, ensure_ascii=False, separators=(',', ':')),
            encoding='utf-8',
        )

    print(f'VISUAL_MEDIA_URLS_NORMALIZED={changed}')


if __name__ == '__main__':
    main()

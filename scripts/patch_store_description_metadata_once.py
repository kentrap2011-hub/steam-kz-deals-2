from pathlib import Path

p = Path('scripts/build_pre_ai_store_snapshot.py')
text = p.read_text(encoding='utf-8')
changes = [
    (
        "            'store_name': store_name,\n            'package_apps': [",
        "            'store_name': store_name,\n            'short_description': str((store_item.get('basic_info') or {}).get('short_description') or '').strip() or None,\n            'package_apps': [",
        'sub',
    ),
    (
        "        'store_name': store_name,\n        'app_type': app_type,",
        "        'store_name': store_name,\n        'short_description': str((store_item.get('basic_info') or {}).get('short_description') or '').strip() or None,\n        'app_type': app_type,",
        'app',
    ),
]
for old, new, label in changes:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label} patch fragment count={count}')
    text = text.replace(old, new)
p.write_text(text, encoding='utf-8')
print('STORE_DESCRIPTION_METADATA_PATCH=PASS')

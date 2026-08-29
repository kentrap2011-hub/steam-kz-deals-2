from pathlib import Path

PATH = Path('scripts/build_pre_ai_taste_projection.py')
text = PATH.read_text(encoding='utf-8')

text = text.replace(
    "import hashlib\nimport json\nimport subprocess\nimport time\nimport unicodedata\nimport urllib.request\n",
    "import concurrent.futures\nimport hashlib\nimport json\nimport subprocess\nimport time\nimport unicodedata\nimport urllib.parse\nimport urllib.request\n",
    1,
)

marker = "\ndef main():\n    started = time.monotonic()\n"
helper = r'''

def fetch_appdetails_descriptions(targets, max_workers=8):
    def fetch(item):
        key, appid = item
        appid = str(appid)
        params = urllib.parse.urlencode({'appids': appid, 'cc': 'kz', 'l': 'english'})
        req = urllib.request.Request(
            'https://store.steampowered.com/api/appdetails?' + params,
            headers={'User-Agent': 'steam-kz-deals/1.0'},
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                doc = json.loads(resp.read().decode('utf-8'))
            node = doc.get(appid) or {}
            value = (node.get('data') or {}).get('short_description')
            description = value.strip() if node.get('success') is True and isinstance(value, str) and value.strip() else None
            return key, description, None, round(time.monotonic() - started, 3)
        except Exception as exc:
            return key, None, f'{type(exc).__name__}: {exc}', round(time.monotonic() - started, 3)

    items = list(targets.items())
    if not items:
        return {}, [], 0.0, 0.0
    started = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = list(pool.map(fetch, items))
    wall = round(time.monotonic() - started, 3)
    descriptions = {key: description for key, description, error, elapsed in results if description}
    failures = [
        {'key': key, 'error': error or 'short_description_missing', 'elapsed_seconds': elapsed}
        for key, description, error, elapsed in results
        if not description
    ]
    slowest = max((elapsed for key, description, error, elapsed in results), default=0.0)
    return descriptions, failures, wall, slowest
'''
if marker not in text:
    raise SystemExit('main marker not found')
text = text.replace(marker, helper + marker, 1)

old = r'''    current_context = {}
    description_known_count = 0
    bundle_subject_count = 0
    for key in subjects:
        meta = metadata[key]
        short_description = meta.get('short_description') or ''
        bundle_members = meta.get('package_apps') or [] if meta.get('entity_kind') == 'sub' else []
        digest, projected = candidate_context_digest(
            feed[key]['taste_fingerprint'],
            short_description,
            bundle_members,
        )
        if projected['normalized_short_description']:
            description_known_count += 1
        if bundle_members:
            bundle_subject_count += 1
        current_context[key] = {
            'candidate_context_sha256': digest,
            'short_description': short_description or None,
            'bundle_members': bundle_members,
        }
'''
new = r'''    direct_description_known_count = sum(
        bool((metadata[key].get('short_description') or '').strip()) for key in subjects
    )
    missing_app_targets = {
        key: feed[key]['appid']
        for key in subjects
        if key.startswith('App_') and not (metadata[key].get('short_description') or '').strip()
    }
    appdetails_descriptions, appdetails_failures, appdetails_wall_seconds, appdetails_slowest_seconds = (
        fetch_appdetails_descriptions(missing_app_targets, max_workers=8)
    )

    current_context = {}
    description_known_count = 0
    appdetails_fallback_count = 0
    bundle_description_fallback_count = 0
    bundle_subject_count = 0
    for key in subjects:
        meta = metadata[key]
        direct_description = (meta.get('short_description') or '').strip()
        short_description = direct_description
        description_source = 'storebrowse_basic_info' if direct_description else None
        bundle_members = meta.get('package_apps') or [] if meta.get('entity_kind') == 'sub' else []
        bundle_member_descriptions = []

        if not short_description and key.startswith('App_'):
            fallback = appdetails_descriptions.get(key)
            if fallback:
                short_description = fallback
                description_source = 'steam_appdetails_fallback'
                appdetails_fallback_count += 1

        if bundle_members:
            bundle_subject_count += 1
            for member in bundle_members:
                member_meta = metadata.get(f"App_{member['appid']}") or {}
                member_description = (member_meta.get('short_description') or '').strip()
                if member_description:
                    bundle_member_descriptions.append({
                        'appid': str(member['appid']),
                        'name': member.get('name'),
                        'short_description': member_description,
                    })
            if not short_description and bundle_member_descriptions:
                short_description = ' | '.join(
                    f"{member['name']}: {member['short_description']}"
                    for member in bundle_member_descriptions
                )
                description_source = 'bundle_member_descriptions'
                bundle_description_fallback_count += 1

        digest, projected = candidate_context_digest(
            feed[key]['taste_fingerprint'],
            short_description,
            bundle_members,
        )
        if projected['normalized_short_description']:
            description_known_count += 1
        current_context[key] = {
            'candidate_context_sha256': digest,
            'short_description': short_description or None,
            'description_source': description_source,
            'bundle_members': bundle_members,
            'bundle_member_descriptions': bundle_member_descriptions,
        }
'''
if old not in text:
    raise SystemExit('current_context block not found')
text = text.replace(old, new, 1)

old = "            'short_description': context['short_description'],\n            'bundle_members': context['bundle_members'],\n"
new = "            'short_description': context['short_description'],\n            'description_source': context['description_source'],\n            'bundle_members': context['bundle_members'],\n            'bundle_member_descriptions': context['bundle_member_descriptions'],\n"
if old not in text:
    raise SystemExit('row context fields block not found')
text = text.replace(old, new, 1)

old = r'''        'candidate_context': {
            'binding_required_for_cache_hit': True,
            'description_known_count': description_known_count,
            'description_missing_count': len(subjects) - description_known_count,
            'description_coverage': round(description_known_count / len(subjects), 6) if subjects else 1.0,
            'bundle_subject_count': bundle_subject_count,
        },
'''
new = r'''        'candidate_context': {
            'binding_required_for_cache_hit': True,
            'direct_storebrowse_description_known_count': direct_description_known_count,
            'appdetails_fallback_requested_count': len(missing_app_targets),
            'appdetails_fallback_success_count': appdetails_fallback_count,
            'appdetails_fallback_failure_count': len(appdetails_failures),
            'appdetails_fallback_wall_seconds': appdetails_wall_seconds,
            'appdetails_fallback_slowest_request_seconds': appdetails_slowest_seconds,
            'appdetails_fallback_max_workers': 8,
            'bundle_description_fallback_count': bundle_description_fallback_count,
            'description_known_count': description_known_count,
            'description_missing_count': len(subjects) - description_known_count,
            'description_coverage': round(description_known_count / len(subjects), 6) if subjects else 1.0,
            'bundle_subject_count': bundle_subject_count,
            'fallback_failures': appdetails_failures,
        },
'''
if old not in text:
    raise SystemExit('candidate_context summary block not found')
text = text.replace(old, new, 1)

text = text.replace("        'external_calls': 1,\n        'entries': rows,", "        'external_calls': 1 + len(missing_app_targets),\n        'entries': rows,", 1)

old = "        'description_known_count': description_known_count,\n        'description_missing_count': len(subjects) - description_known_count,\n"
new = "        'direct_description_known_count': direct_description_known_count,\n        'appdetails_fallback_requested_count': len(missing_app_targets),\n        'appdetails_fallback_success_count': appdetails_fallback_count,\n        'appdetails_fallback_failure_count': len(appdetails_failures),\n        'appdetails_fallback_wall_seconds': appdetails_wall_seconds,\n        'bundle_description_fallback_count': bundle_description_fallback_count,\n        'description_known_count': description_known_count,\n        'description_missing_count': len(subjects) - description_known_count,\n"
if old not in text:
    raise SystemExit('print description block not found')
text = text.replace(old, new, 1)

text = text.replace("        'external_calls': 1,\n        'elapsed_seconds': out['elapsed_seconds'],", "        'external_calls': 1 + len(missing_app_targets),\n        'elapsed_seconds': out['elapsed_seconds'],", 1)

PATH.write_text(text, encoding='utf-8')
print('TASTE_DESCRIPTION_FALLBACK_SOURCE_PATCH=PASS')

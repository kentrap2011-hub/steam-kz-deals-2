import html
import math
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


USER_AGENT = 'steam-kz-deals-achievements/1.0'

CHALLENGE_PATTERNS = [
    r'\bwithout (?:getting )?hit\b',
    r'\bwithout taking damage\b',
    r'\bno[- ]?hit\b',
    r'\bno[- ]?death\b',
    r'\bwithout dying\b',
    r'\bone life\b',
    r'\bpacifist\b',
    r'\bspeed ?run\b',
    r'\bunder \d+ (?:minute|minutes|hour|hours|second|seconds)\b',
    r'\bwithin \d+ (?:minute|minutes|hour|hours|second|seconds)\b',
    r'\bexpert\b',
    r'\bhardest\b',
    r'\bnightmare\b',
    r'\binsane\b',
    r'\bs[- ]?rank\b',
    r'\ba[- ]?rank\b',
    r'\bperfect\b',
    r'\bflawless\b',
    r'\bnew game\+?\b',
    r'\bng\+\b',
    r'\buse only\b',
    r'\busing only\b',
    r'\bwithout using\b',
    r'\bwithout (?:any )?upgrades\b',
    r'\bno upgrades\b',
    r'\bwithout killing\b',
]

MASTERY_PATTERNS = [
    r'\bparr(?:y|ies|ied)\b',
    r'\bcombo\b',
    r'\bcounter\b',
    r'\bdodge\b',
    r'\bdefeat .+ with\b',
    r'\bkill .+ with\b',
    r'\bcomplete .+ with\b',
    r'\bperform\b',
    r'\bspecial move\b',
    r'\bsuper art\b',
    r'\bability\b',
    r'\babilities\b',
    r'\btechnique\b',
    r'\bmaster\b',
    r'\bchain\b',
]

OPTIONAL_PATTERNS = [
    r'\bsecret\b',
    r'\bhidden\b',
    r'\bdiscover\b',
    r'\bfind all\b',
    r'\bfind every\b',
    r'\bcollect all\b',
    r'\bcollect every\b',
    r'\ball endings\b',
    r'\balternate ending\b',
    r'\bside quest\b',
    r'\boptional\b',
]

STORY_PATTERNS = [
    r'\bcomplete (?:chapter|act|episode|mission|level|stage|game|campaign)\b',
    r'\bfinish (?:chapter|act|episode|mission|level|stage|game|campaign)\b',
    r'\bdefeat (?:the )?[a-z0-9 \-]+$',
    r'\bbeat (?:the )?[a-z0-9 \-]+$',
]

GRIND_PATTERNS = [
    r'\b(?:kill|defeat|collect|obtain|earn|win|play|complete|perform|use)\s+(\d{3,})\b',
    r'\b(\d{3,})\s+(?:kills|enemies|matches|games|items|coins|collectibles|times)\b',
    r'\bplay for \d+ hours\b',
    r'\breach level (?:5\d|[6-9]\d|\d{3,})\b',
    r'\bmax(?:imum)? level\b',
    r'\bbuy everything\b',
]


def _clean(value):
    value = re.sub(r'<[^>]+>', ' ', value or '')
    value = html.unescape(value)
    return re.sub(r'\s+', ' ', value).strip()


def parse_achievement_pairs(page_html):
    pairs = []
    for name, desc in re.findall(
        r'<h3[^>]*>(.*?)</h3>\s*<h5[^>]*>(.*?)</h5>',
        page_html or '',
        flags=re.I | re.S,
    ):
        name = _clean(name)
        desc = _clean(desc)
        if name:
            pairs.append((name, desc))
    return pairs


def _matches(patterns, text):
    return any(re.search(pattern, text, flags=re.I) for pattern in patterns)


def classify_achievement(name, description):
    text = f'{name} {description}'.strip().lower()
    if not text:
        return None
    if _matches(GRIND_PATTERNS, text):
        return 2
    if _matches(CHALLENGE_PATTERNS, text):
        return 5
    if _matches(MASTERY_PATTERNS, text):
        return 4
    if _matches(OPTIONAL_PATTERNS, text):
        return 3
    if _matches(STORY_PATTERNS, text):
        return 1
    return 3 if description else None


def rate_achievement_set(pairs):
    ratings = [classify_achievement(name, desc) for name, desc in pairs]
    ratings = [x for x in ratings if x is not None]
    if not ratings:
        return None, {'assessed': 0, 'total_visible': len(pairs), 'counts': {}}

    counts = {score: ratings.count(score) for score in range(1, 6)}
    n = len(ratings)

    # Canonical user profile:
    # 5 = new play styles/challenges; 4 = deeper mechanic use;
    # 3 = meaningful optional goals/secrets; 2 = grind/collectathon;
    # 1 = mostly automatic/story progression.
    if counts[5] >= max(2, math.ceil(n * 0.08)):
        quality = 5
    elif counts[5] + counts[4] >= max(2, math.ceil(n * 0.15)):
        quality = 4
    elif counts[5] + counts[4] + counts[3] >= max(2, math.ceil(n * 0.20)):
        quality = 3
    elif counts[2] >= max(2, math.ceil(n * 0.25)):
        quality = 2
    else:
        quality = 1

    return quality, {
        'assessed': n,
        'total_visible': len(pairs),
        'counts': {str(k): v for k, v in counts.items() if v},
    }


def fetch_achievement_quality(appid, timeout=15):
    url = f'https://steamcommunity.com/stats/{appid}/achievements/?l=english'
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.8',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            page_html = response.read().decode('utf-8', errors='replace')
        pairs = parse_achievement_pairs(page_html)
        quality, evidence = rate_achievement_set(pairs)
        return str(appid), {
            'achievement_quality': quality,
            'achievement_quality_source': 'steam_global_achievement_descriptions',
            'achievement_quality_evidence': evidence,
        }
    except Exception as exc:
        return str(appid), {
            'achievement_quality': None,
            'achievement_quality_source': 'unavailable',
            'achievement_quality_error': type(exc).__name__,
        }


def fetch_achievement_quality_many(appids, max_workers=12):
    ids = sorted({str(x) for x in appids if str(x).isdigit()}, key=int)
    result = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(fetch_achievement_quality, appid) for appid in ids]
        for future in as_completed(futures):
            appid, data = future.result()
            result[appid] = data
    return result


def enrich_visual_items(items):
    wanted = set()
    for game in items or []:
        practical = game.get('practical') or {}
        if practical.get('steam_achievements') is True:
            wanted.update(str(x) for x in (game.get('base_appids') or []) if str(x).isdigit())

    by_appid = fetch_achievement_quality_many(wanted) if wanted else {}

    for game in items or []:
        practical = game.setdefault('practical', {})
        has_achievements = practical.get('steam_achievements')
        if has_achievements is False:
            practical['achievement_quality'] = 0
            practical['achievement_quality_source'] = 'no_steam_achievements'
            continue
        if has_achievements is not True:
            practical['achievement_quality'] = None
            practical['achievement_quality_source'] = 'achievement_presence_unknown'
            continue

        rows = [
            by_appid.get(str(appid))
            for appid in (game.get('base_appids') or [])
            if by_appid.get(str(appid))
        ]
        assessed = [row for row in rows if isinstance(row.get('achievement_quality'), int)]
        if not assessed:
            practical['achievement_quality'] = None
            practical['achievement_quality_source'] = 'steam_global_achievement_descriptions_unavailable'
            continue

        quality = int(round(sum(row['achievement_quality'] for row in assessed) / len(assessed)))
        practical['achievement_quality'] = max(1, min(5, quality))
        practical['achievement_quality_source'] = 'steam_global_achievement_descriptions'
        practical['achievement_quality_assessed_games'] = len(assessed)
    return items

import html
import math
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


USER_AGENT = 'steam-kz-deals-achievements/1.1'

# The order matters: a constrained/challenge version of an otherwise ordinary
# action must beat generic story/grind wording.
CHALLENGE_PATTERNS = [
    r'\bwithout (?:getting )?hit\b',
    r'\bwithout taking (?:any )?damage\b',
    r'\bwithout dying\b',
    r'\bwithout killing\b',
    r'\bwithout using\b',
    r'\bwithout (?:any )?upgrades\b',
    r'\bno[- ]?hit\b',
    r'\bno[- ]?death\b',
    r'\bno upgrades\b',
    r'\bone life\b',
    r'\bpacifist\b',
    r'\bpermadeath\b',
    r'\biron ?man\b',
    r'\bspeed ?run\b',
    r'\bunder \d+ (?:second|seconds|minute|minutes|hour|hours)\b',
    r'\bwithin \d+ (?:second|seconds|minute|minutes|hour|hours)\b',
    r'\b(?:complete|finish|beat) .+ on (?:hard|very hard|expert|master|nightmare|insane|legendary|ultra)\b',
    r'\b(?:hardest|nightmare|insane|legendary) difficulty\b',
    r'\bs[- ]?rank\b',
    r'\ba[- ]?rank\b',
    r'\bperfect\b',
    r'\bflawless\b',
    r'\bnew game\+?\b',
    r'\bng\+\b',
    r'\buse only\b',
    r'\busing only\b',
    r'\bwith only\b',
    r'\bwithout .+ ability\b',
    r'\bwithout .+ weapon\b',
]

MASTERY_PATTERNS = [
    r'\bparr(?:y|ies|ied)\b',
    r'\bdeflect\b',
    r'\bcombo\b',
    r'\bcounter\b',
    r'\bdodge\b',
    r'\bheadshot\b',
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

GRIND_PATTERNS = [
    r'\b(?:kill|defeat|collect|obtain|earn|win|play|complete|perform|use|craft|open)\s+(\d{3,})\b',
    r'\b(\d{3,})\s+(?:kills|enemies|matches|games|items|coins|collectibles|times|objects|points)\b',
    r'\bplay for \d+ hours\b',
    r'\breach level (?:5\d|[6-9]\d|\d{3,})\b',
    r'\bmax(?:imum)? level\b',
    r'\bbuy everything\b',
    r'\bcomplete all (?:activities|challenges|events|locations|objectives)\b',
    r'\bclear (?:every|all) (?:area|areas|location|locations|region|regions)\b',
    r'\b100% (?:the )?(?:map|game|completion)\b',
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
    r'\bevery ending\b',
    r'\balternate ending\b',
    r'\bside quest\b',
    r'\bside mission\b',
    r'\boptional\b',
    r'\beaster egg\b',
]

STORY_PATTERNS = [
    r'\b(?:complete|finish|clear) (?:the )?(?:prologue|epilogue|chapter|act|episode|mission|level|stage|game|campaign)\b',
    r'\b(?:complete|finish|clear) (?:chapter|act|episode|mission|level|stage)\s*[0-9ivx]+\b',
    r'\b(?:beat|finish|complete) the game\b',
    r"\bdefeat (?:the )?[a-z0-9][a-z0-9 '\-:]+$",
    r"\bbeat (?:the )?[a-z0-9][a-z0-9 '\-:]+$",
    r'\breach (?:the )?(?:ending|finale|credits)\b',
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

    if _matches(CHALLENGE_PATTERNS, text):
        return 5
    if _matches(MASTERY_PATTERNS, text):
        return 4
    if _matches(GRIND_PATTERNS, text):
        return 2
    if _matches(OPTIONAL_PATTERNS, text):
        return 3
    if _matches(STORY_PATTERNS, text):
        return 1

    # Unknown wording is deliberately not treated as 3/5. 3/5 means that an
    # explicit meaningful optional goal/secret was actually detected.
    return None


def _threshold(total_visible, fraction, minimum=2):
    return max(minimum, math.ceil(max(total_visible, 1) * fraction))


def rate_achievement_set(pairs):
    ratings = [classify_achievement(name, desc) for name, desc in pairs]
    ratings = [x for x in ratings if x is not None]
    counts = {score: ratings.count(score) for score in range(1, 6)}
    total_visible = len(pairs)
    assessed = len(ratings)

    evidence = {
        'assessed': assessed,
        'total_visible': total_visible,
        'coverage_percent': int(round(100 * assessed / total_visible)) if total_visible else 0,
        'counts': {str(k): v for k, v in counts.items() if v},
    }
    if not ratings:
        return None, evidence

    # Canonical user profile, applied as transparent qualitative tiers:
    # 5 = a meaningful challenge/restriction layer exists;
    # 4 = meaningful mastery/deeper-mechanics layer exists;
    # 3 = meaningful optional goals/secrets;
    # 2 = grind/cleanup is the main detected extra-achievement layer;
    # 1 = detected set is mostly ordinary progression/story milestones.
    challenge_needed = 1 if total_visible <= 15 else _threshold(total_visible, 0.05)
    mastery_needed = 1 if total_visible <= 12 else _threshold(total_visible, 0.08)
    optional_needed = 1 if total_visible <= 10 else _threshold(total_visible, 0.10)

    if counts[5] >= challenge_needed:
        quality = 5
    elif counts[5] + counts[4] >= mastery_needed:
        quality = 4
    elif counts[5] + counts[4] + counts[3] >= optional_needed:
        quality = 3
    elif counts[2] and counts[2] >= max(counts[1], counts[3] + counts[4] + counts[5]):
        quality = 2
    elif counts[1] and counts[1] >= counts[2] + counts[3] + counts[4] + counts[5]:
        quality = 1
    elif counts[2] > counts[1]:
        quality = 2
    elif counts[1] > 0:
        quality = 1
    else:
        quality = None

    return quality, evidence


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

        # A bundle/family can have several base games. The most interesting
        # achievement set is a real reason to prefer the purchase, so keep the
        # best confirmed quality instead of diluting it with a simple mean.
        best = max(assessed, key=lambda row: int(row['achievement_quality']))
        practical['achievement_quality'] = int(best['achievement_quality'])
        practical['achievement_quality_source'] = 'steam_global_achievement_descriptions'
        practical['achievement_quality_assessed_games'] = len(assessed)
        practical['achievement_quality_evidence'] = best.get('achievement_quality_evidence') or {}
    return items

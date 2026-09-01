import re

PLACEHOLDER_TEXTS = {
    'Русское краткое описание для этой игры пока не подготовлено.',
    'Краткое описание пока недоступно.',
}

TECHNICAL_PATTERNS = [
    re.compile(
        r'(?:в\s+состав|издани[ея]|комплект).{0,100}'
        r'(?:входят|включает|содержит).{0,220}'
        r'(?:основн(?:ая|ую)\s+игр|дополнени|dlc|season\s+pass|контент)',
        re.IGNORECASE,
    ),
    re.compile(
        r'(?:ultimate|deluxe|complete|definitive)\s+edition.{0,120}'
        r'(?:includes|contains).{0,220}'
        r'(?:base\s+game|dlc|expansion|season\s+pass)',
        re.IGNORECASE,
    ),
    re.compile(
        r'(?:bundle|package).{0,100}(?:includes|contains).{0,220}'
        r'(?:base\s+game|dlc|expansion|season\s+pass)',
        re.IGNORECASE,
    ),
]


def normalize_description(value):
    text = re.sub(r'<[^>]+>', ' ', str(value or ''))
    return re.sub(r'\s+', ' ', text).strip()


def classify_description(value):
    text = normalize_description(value)
    if not text:
        return 'missing'
    if text in PLACEHOLDER_TEXTS:
        return 'placeholder_or_technical'
    if any(pattern.search(text) for pattern in TECHNICAL_PATTERNS):
        return 'placeholder_or_technical'

    cyrillic = len(re.findall(r'[А-Яа-яЁё]', text))
    latin = len(re.findall(r'[A-Za-z]', text))
    letters = cyrillic + latin
    words = re.findall(r'[A-Za-zА-Яа-яЁё]+', text)

    if letters == 0:
        return 'weak_ru'
    cyrillic_share = cyrillic / letters
    if cyrillic >= 20 and cyrillic_share >= 0.55 and len(words) >= 5:
        return 'good_ru'
    if cyrillic:
        return 'weak_ru' if cyrillic_share >= 0.35 else 'non_ru'
    return 'non_ru'


def resolve_description(russian_candidate, fallback_candidate=None):
    candidates = [
        ('russian', normalize_description(russian_candidate)),
        ('english', normalize_description(fallback_candidate)),
    ]
    classified = [(locale, text, classify_description(text)) for locale, text in candidates]

    for locale, text, category in classified:
        if category == 'good_ru':
            return {
                'summary': text,
                'description_status': 'ready_ru',
                'description_source_locale': locale,
                'description_source_quality': category,
                'description_source_text': None,
            }

    for locale, text, category in classified:
        if category == 'non_ru' and text:
            return {
                'summary': None,
                'description_status': 'needs_translation',
                'description_source_locale': locale,
                'description_source_quality': category,
                'description_source_text': text,
            }

    for locale, text, category in classified:
        if category == 'weak_ru' and text:
            return {
                'summary': None,
                'description_status': 'needs_ru_rewrite',
                'description_source_locale': locale,
                'description_source_quality': category,
                'description_source_text': text,
            }

    for locale, text, category in classified:
        if category == 'placeholder_or_technical' and text:
            return {
                'summary': None,
                'description_status': 'technical_source',
                'description_source_locale': locale,
                'description_source_quality': category,
                'description_source_text': text,
            }

    return {
        'summary': None,
        'description_status': 'missing_source',
        'description_source_locale': None,
        'description_source_quality': 'missing',
        'description_source_text': None,
    }

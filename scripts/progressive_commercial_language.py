"""Lexical commercial-evidence guard shared by Progressive Fast and Deep.

Reject actual commercial vocabulary, not character sequences embedded in
unrelated words (e.g. "грубую", "сцена", "wholesale", "scrub").
NFKC/casefold handles typography and case; Unicode word boundaries prevent
Cyrillic/Latin word-interior matches. Numeric+currency forms remain covered.
Only mixed-script candidate words receive limited visual-confusable folding,
never transliteration of the entire evidence text.
"""
import re
import unicodedata


def _normalized(text):
    folded = unicodedata.normalize('NFKC', text).casefold()
    # Optional printed stress marks are not lexical word boundaries.
    return folded.replace('\u0301', '').replace('\u0300', '')


def _word(pattern):
    return re.compile(r'(?<!\w)(?:' + pattern + r')(?!\w)')


def _currency(pattern):
    # Permit 100RUB and USD100 (including a decimal numeric suffix), but
    # never word-interior "scrub", "грубую", or identifiers like USD100foo.
    return re.compile(
        r'(?:(?<!\w)|(?<=\d))(?:' + pattern
        + r')(?:(?!\w)|(?=\d[\d.,]*(?!\w)))'
    )

COMMERCIAL_PATTERNS = (
    ('price', _word(r'prices?|priced|pricing')),
    ('discount', _word(r'discounts?|discounted|discounting')),
    ('wishlist', _word(r'wishlists?')),
    ('steamdb', _word(r'steamdb')),
    ('sale', _word(r'sales?')),
    ('rub', _currency(r'rub(?:les?)?')),
    ('kzt', _currency(r'kzt')),
    ('usd', _currency(r'usd')),
    ('eur', _currency(r'eur')),
    ('цена', _word(r'цен(?:а|ы|е|у|ой|ою|ам|ами|ах)?')),
    ('скидк', _word(r'скидк[а-яё]*')),
    ('вишлист', _word(r'вишлист[а-яё]*')),
    ('распродаж', _word(r'распродаж[а-яё]*')),
    ('руб', _currency(r'руб(?:л(?:ь|я|ю|е|ем|ём|и|ей|ям|ями|ях|\.))?')),
    ('тенге', _currency(r'тенге')),
    ('доллар', _currency(r'доллар(?:ы|а|у|ом|ов|ам|ами|ах)?')),
    ('евро', _currency(r'евро')),
    ('currency_symbol', re.compile(r'(?:(?<!\w)[₽$€₸£¥]\s*\d|\d\s*[₽$€₸£¥])')),
)

# The score-finding text has additional rank/score-only terms, in addition to
# the same commercial terms forbidden in Fast/Deep positive/negative evidence.
SCORE_ONLY_PATTERNS = tuple(
    (phrase, _word(re.escape(phrase).replace(r'\ ', r'\s+')))
    for phrase in (
        'personal score', 'total score', 'purchase score', 'deal score',
        'ranking position', 'priority rank',
        'место в рейтинге', 'персональный балл',
        'итоговый балл', 'оценка сделки',
    )
) + (('место в очеред', _word(r'место\s+в\s+очеред(?:и|ь)?')),)


# Only visually confusable letters relevant to our canonical token families.
# Translating a whole string would turn unrelated mixed-language prose into
# spurious matches. Instead, require both scripts in an individual word and
# full-match the folded word against the existing commercial inventory.
_CYR_TO_LATIN = str.maketrans({
    'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c',
    'у': 'y', 'х': 'x', 'і': 'i', 'ѕ': 's',
    'к': 'k', 'м': 'm', 'т': 't',
})
_LATIN_TO_CYR = str.maketrans({
    'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'c': 'с',
    'y': 'у', 'x': 'х', 'k': 'к', 'm': 'м', 't': 'т',
})
_WORD_TOKEN = re.compile(r'\w+')
_LATIN_LETTER = re.compile(r'[a-z]')
_CYRILLIC_LETTER = re.compile(r'[а-яёіѕ]')


def _commercial_candidate_hit(normalized):
    """Check only complete mixed-script candidate words, not substrings."""
    for match in _WORD_TOKEN.finditer(normalized):
        token = match.group()
        if not (_LATIN_LETTER.search(token) and _CYRILLIC_LETTER.search(token)):
            continue
        for folded in (token.translate(_CYR_TO_LATIN),
                       token.translate(_LATIN_TO_CYR)):
            for label, pattern in COMMERCIAL_PATTERNS:
                if pattern.fullmatch(folded):
                    return label
    return None


def commercial_evidence_hit(text):
    """Return canonical token label, or None for noncommercial prose."""
    normalized = _normalized(text)
    native_hit = next((label for label, pattern in COMMERCIAL_PATTERNS
                       if pattern.search(normalized)), None)
    return native_hit if native_hit is not None else _commercial_candidate_hit(normalized)

def score_explanation_hit(text):
    """Return commercial/ranking-only label, or None."""
    commercial = commercial_evidence_hit(text)
    if commercial is not None:
        return commercial
    normalized = _normalized(text)
    return next((label for label, pattern in SCORE_ONLY_PATTERNS
                 if pattern.search(normalized)), None)

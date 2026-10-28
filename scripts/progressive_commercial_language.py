"""Lexical commercial-evidence guard shared by Progressive Fast and Deep.

Reject actual commercial vocabulary, not character sequences embedded in
unrelated words (e.g. "грубую", "сцена", "wholesale", "scrub").
NFKC/casefold handles typography and case; Unicode word boundaries prevent
Cyrillic/Latin word-interior matches. Numeric+currency forms remain covered.
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
    # Currency codes and names can be written immediately after an amount:
    # "100руб", "100RUB", but not inside "грубую" or "scrub".
    return re.compile(r'(?:(?<!\w)|(?<=\d))(?:' + pattern + r')(?!\w)')


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
    ('руб', _currency(r'руб(?:л(?:ь|я|ю|е|ем|ём|и|ей|ям|ями|ях))?')),
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


def commercial_evidence_hit(text):
    """Return canonical token label, or None for noncommercial prose."""
    normalized = _normalized(text)
    return next((label for label, pattern in COMMERCIAL_PATTERNS
                 if pattern.search(normalized)), None)


def score_explanation_hit(text):
    """Return commercial/ranking-only label, or None."""
    commercial = commercial_evidence_hit(text)
    if commercial is not None:
        return commercial
    normalized = _normalized(text)
    return next((label for label, pattern in SCORE_ONLY_PATTERNS
                 if pattern.search(normalized)), None)

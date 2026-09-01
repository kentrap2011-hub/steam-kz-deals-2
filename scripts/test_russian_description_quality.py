from russian_description_quality import classify_description, resolve_description


def expect(value, expected):
    actual = classify_description(value)
    assert actual == expected, (value, actual, expected)


expect(
    'Psychonauts 2 — это платформер о невероятных парапсихических способностях '
    'и таинственных заговорах, стильный, зрелищный и с отличным юмором.',
    'good_ru',
)
expect('A deep action adventure with И one Cyrillic fragment and many English words.', 'non_ru')
expect('Русское краткое описание для этой игры пока не подготовлено.', 'placeholder_or_technical')
expect(
    'В состав издания CONTROL Ultimate Edition входят основная игра Control '
    'и дополнения The Foundation и AWE.',
    'placeholder_or_technical',
)
expect('', 'missing')

ready = resolve_description('Это полноценное русское описание игры с понятным смыслом и достаточным количеством слов.')
assert ready['description_status'] == 'ready_ru'
assert ready['summary']

needs_translation = resolve_description(
    'An English short description returned even from the requested Russian locale.',
    'A complete English source description for the game, with enough useful context.',
)
assert needs_translation['description_status'] == 'needs_translation'
assert needs_translation['summary'] is None
assert needs_translation['description_source_text']

technical_then_source = resolve_description(
    'В состав издания CONTROL Ultimate Edition входят основная игра Control и дополнения The Foundation и AWE.',
    'A supernatural third-person action adventure about regaining control of a secret agency.',
)
assert technical_then_source['description_status'] == 'needs_translation'
assert technical_then_source['description_source_locale'] == 'english'

missing = resolve_description(None, None)
assert missing['description_status'] == 'missing_source'
assert missing['summary'] is None

print('RUSSIAN_DESCRIPTION_QUALITY_TEST=PASS')

"""Focused token-boundary regressions for canonical Fast and Deep ingest."""
from pathlib import Path

import progressive_commercial_language as lexical
import progressive_pass1
import progressive_pass2
import test_progressive_pass1 as fast_fixture
import test_progressive_pass2 as deep_fixture


SAFE = (
    'Грубую структуру заданий сопровождают напряжённые решения.',
    'Сцена с персонажем раскрывается постепенно.',
    'Труба и рубежи видны на дальнем плане.',
    'Рубленые движения сочетаются с динамичной постановкой.',
    'The scrub animation is mechanically demanding.',
    'The Salem setting has an eerie atmosphere.',
    'Discountenance is an old English word for disapproval.',
    'Переоценка собственных решений меняет тактику.',
    'Конкретные действия приводят к переменам в игровом мире.',
    'Сцeна с героем раскрывается постепенно.',  # Latin e, not цена
    'Груbую фактуру передаёт анимация.',  # no word-interior rub
    'The Sаlem setting is atmospheric.',  # Cyrillic a, not sale
    'Diѕcountenance is a valid noncommercial English word.',
    'Prіceless character growth is shown through choices.',
    'RUBicon is the name of a landmark.',
    'Символ ₽ на рисунке не сообщает сумму.',  # bare glyph is ambiguous
    'R U B 500 is a sequence of separate letters, not a currency token.',
)
FORBIDDEN = (
    ('Цена 499 руб.', 'цена'),
    ('Стоит 100 рублей', 'руб'),
    ('Около 500 рублями', 'руб'),
    ('100руб', 'руб'),
    ('100RUB', 'rub'),
    ('РуБ.', 'руб'),
    ('Цена́ 99', 'цена'),
    ('Скидки и распродажи', 'скидк'),
    ('50% скидка', 'скидк'),
    ('Вишлист Steam', 'вишлист'),
    ('Историческая цена', 'цена'),
    ('Historical price', 'price'),
    ('DISCOUNTED price', 'price'),
    ('Full PRICE', 'price'),
    ('SteamDB', 'steamdb'),
    ('On sale', 'sale'),
    ('Wishlist', 'wishlist'),
    ('１００ ＲＵＢ', 'rub'),
    ('100\u202f₽', 'currency_symbol'),
    ('€\u00a019.99', 'currency_symbol'),
    ('$20', 'currency_symbol'),
    ('10,50 £', 'currency_symbol'),
    ('500 ₸', 'currency_symbol'),
    ('2000 тенге', 'тенге'),
    ('USD', 'usd'),
    ('EUR', 'eur'),
    ('20 долларов', 'доллар'),
    ('50 евро', 'евро'),
    ('KZT', 'kzt'),
    ('USD100', 'usd'),
    ('RUB100', 'rub'),
    ('EUR100', 'eur'),
    ('KZT100', 'kzt'),
    ('ＵＳＤ１００', 'usd'),
    ('100USD', 'usd'),
    ('рубл. 500', 'руб'),
    ('РУБЛ.500', 'руб'),
    ('цeна 100', 'цена'),  # Latin e in Cyrillic token
    ('cкидка 20%', 'скидк'),  # Latin c
    ('prіce 100', 'price'),  # Cyrillic Ukrainian i
    ('diѕcount 20%', 'discount'),  # Cyrillic dze
    ('ѕale', 'sale'),
    ('Рrice', 'price'),  # Cyrillic р
)
RANKING_ONLY = (
    'Personal score increased',
    'Total score is high',
    'Purchase score',
    'Deal score',
    'Ranking position',
    'Priority rank',
    'Место в рейтинге',
    'Место в очереди',
    'Персональный балл',
    'Итоговый балл',
    'Оценка сделки',
)


def raises_commercial(callback):
    try:
        callback()
    except ValueError as exc:
        assert 'commercial' in str(exc), str(exc)
    else:
        raise AssertionError('commercial evidence should have been rejected')


def check_lexical_inventory():
    for example in SAFE:
        assert lexical.commercial_evidence_hit(example) is None, example
        assert lexical.score_explanation_hit(example) is None, example
        assert progressive_pass1._validate_text_list(
            'not_fit_evidence', [example], require_nonempty=True
        ) == [example]
    for example, expected in FORBIDDEN:
        assert lexical.commercial_evidence_hit(example) == expected, (example, expected, lexical.commercial_evidence_hit(example))
        assert lexical.score_explanation_hit(example) is not None, example
        raises_commercial(lambda x=example: progressive_pass1._validate_text_list(
            'positive_evidence', [x], require_nonempty=True
        ))
        raises_commercial(lambda x=example: progressive_pass1._validate_text_list(
            'not_fit_evidence', [x], require_nonempty=True
        ))
    for example in RANKING_ONLY:
        assert lexical.commercial_evidence_hit(example) is None, example
        assert lexical.score_explanation_hit(example) is not None, example
    for example in (
        'После сцены начинается новый акт: цена не обсуждается.',
        'Управление грубую ошибку не компенсирует: 150 рублей.',
    ):
        assert lexical.commercial_evidence_hit(example) is not None, example


def check_fast_canonical():
    projection = fast_fixture.projection()
    queue = fast_fixture.queue_rows()
    _, bindings, _ = progressive_pass1.current_bindings(
        fast_fixture.contexts(), projection, queue
    )
    item = fast_fixture.work_doc(bindings, queue)['items'][0]
    for example in SAFE:
        doc = fast_fixture.submission(
            item, 'analyzed_not_fit', confidence='medium',
            not_fit_basis='completed_below_threshold', not_fit_evidence=[example]
        )
        assert progressive_pass1.normalize_submission(doc, item)['not_fit_evidence'] == [example]
        fit = fast_fixture.submission(
            item, 'analyzed_fit', fit_level='moderate', confidence='medium',
            positive_evidence=[example], taste_factors=fast_fixture.FACTOR_VALUES
        )
        assert progressive_pass1.normalize_submission(fit, item)['positive_evidence'] == [example]
    for example, _ in FORBIDDEN:
        doc = fast_fixture.submission(
            item, 'analyzed_not_fit', confidence='medium',
            not_fit_basis='completed_below_threshold', not_fit_evidence=[example]
        )
        raises_commercial(lambda d=doc: progressive_pass1.normalize_submission(d, item))
        fit = fast_fixture.submission(
            item, 'analyzed_fit', fit_level='moderate', confidence='medium',
            positive_evidence=[example], taste_factors=fast_fixture.FACTOR_VALUES
        )
        raises_commercial(lambda d=fit: progressive_pass1.normalize_submission(d, item))


def check_deep_canonical():
    ctx, queue, projection = deep_fixture.contexts(), deep_fixture.queue(), deep_fixture.projection()
    _, bindings, _ = progressive_pass1.current_bindings(ctx, projection, queue)
    binding = {'binding': 'current-v1', 'schema': 'Dossier-V2'}
    dossiers = {
        '1': deep_fixture.dossier_record('1', 'Game 1', binding),
        '2': deep_fixture.dossier_record('2', 'Game 2', binding),
    }
    ready = deep_fixture.recompute(
        bindings, deep_fixture.empty_pass1_state(), deep_fixture.empty_pass2_state(),
        dossiers, binding
    )
    item = next(x for x in ready['items'] if x['family_id'] == 'game:1')
    for example in SAFE:
        doc = deep_fixture.result_doc(
            item, outcome='analyzed_not_fit', confidence='medium',
            not_fit_basis='completed_below_threshold', not_fit_evidence=[example]
        )
        assert progressive_pass2.normalize_result(doc, item)['not_fit_evidence'] == [example]
    score_ok = deep_fixture.fit_result(item)
    score_ok['positive_evidence'] = [SAFE[0]]
    score_ok['score_findings'][0]['text_ru'] = SAFE[0]
    assert progressive_pass2.normalize_result(score_ok, item)['score_findings']
    for example, _ in FORBIDDEN:
        doc = deep_fixture.result_doc(
            item, outcome='analyzed_not_fit', confidence='medium',
            not_fit_basis='completed_below_threshold', not_fit_evidence=[example]
        )
        raises_commercial(lambda d=doc: progressive_pass2.normalize_result(d, item))
        fit_evidence_bad = deep_fixture.fit_result(item)
        fit_evidence_bad['positive_evidence'] = [example]
        raises_commercial(lambda d=fit_evidence_bad: progressive_pass2.normalize_result(d, item))
        score_bad = deep_fixture.fit_result(item)
        score_bad['score_findings'][0]['text_ru'] = 'Механика помогает освоить навык. ' + example
        try:
            progressive_pass2.normalize_result(score_bad, item)
        except ValueError as exc:
            assert 'commercial/ranking-only' in str(exc), str(exc)
        else:
            raise AssertionError('Deep score findings must reject commercial text')
    for example in RANKING_ONLY:
        score_bad = deep_fixture.fit_result(item)
        score_bad['score_findings'][0]['text_ru'] = 'Механика понятна игроку. ' + example
        try:
            progressive_pass2.normalize_result(score_bad, item)
        except ValueError as exc:
            assert 'commercial/ranking-only' in str(exc), str(exc)
        else:
            raise AssertionError('Deep score findings must reject ranking-only text')

    # Exercise the actual Deep ingest/receipt boundary without touching any
    # production state: fresh in-memory fixture for accepted and rejected rows.
    name = Path(item['result_submission_path']).name
    good = deep_fixture.result_doc(
        item, outcome='analyzed_not_fit', confidence='medium',
        not_fit_basis='completed_below_threshold', not_fit_evidence=[SAFE[0]]
    )
    _, receipts = progressive_pass2.process_result_documents(
        deep_fixture.work_doc([item]), deep_fixture.empty_pass2_state(),
        [(name, good, None)], accepted_at_utc='2026-09-22T12:01:00+00:00'
    )
    assert receipts[0]['status'] == 'accepted', receipts[0]
    for example in (
        'Цена 100 рублей', 'USD100', 'RUB100', 'EUR100', 'KZT100',
        'цeна 100', 'cкидка 20%', 'prіce 100', 'diѕcount 20%', 'рубл. 500'
    ):
        bad = deep_fixture.result_doc(
            item, outcome='analyzed_not_fit', confidence='medium',
            not_fit_basis='completed_below_threshold', not_fit_evidence=[example]
        )
        _, receipts = progressive_pass2.process_result_documents(
            deep_fixture.work_doc([item]), deep_fixture.empty_pass2_state(),
            [(name, bad, None)], accepted_at_utc='2026-09-22T12:01:00+00:00'
        )
        assert receipts[0]['status'] == 'rejected_semantic_contract_result_attempt_consumed', (example, receipts[0])
    for example in (SAFE[0], 'Сцeна с героем раскрывается постепенно.'):
        safe_doc = deep_fixture.result_doc(
            item, outcome='analyzed_not_fit', confidence='medium',
            not_fit_basis='completed_below_threshold', not_fit_evidence=[example]
        )
        _, receipts = progressive_pass2.process_result_documents(
            deep_fixture.work_doc([item]), deep_fixture.empty_pass2_state(),
            [(name, safe_doc, None)], accepted_at_utc='2026-09-22T12:01:00+00:00'
        )
        assert receipts[0]['status'] == 'accepted', (example, receipts[0])


if __name__ == '__main__':
    check_lexical_inventory()
    check_fast_canonical()
    check_deep_canonical()
    print('Progressive commercial lexical boundaries / Fast / Deep ingest: OK')

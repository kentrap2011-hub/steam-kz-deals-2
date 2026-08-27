# GAME-DEALS-MAILING v1.8

Этот файл — человекочитаемое описание `config/mailing_policy.json`. Канонический источник правил — JSON; при любом расхождении приоритет у JSON.

## Базовые инварианты

- Выпуск — полный ежедневный snapshot, не delta и не TOP-N.
- Все активные подходящие скидки повторяются ежедневно, пока действуют.
- Пройденная игра не исключается автоматически.
- Discovery платных игр — только полный production-feed Steam Kazakhstan.
- Все выбранные chunks читаются полностью; QA fail-closed.
- Wishlist не используется как discovery, доказательство вкуса или доказательство владения.
- SteamDB не используется для discovery.
- Пользовательские суммы выводятся только в рублях.
- Около 500 ₽ — мягкий ориентир, не жёсткий потолок.

## Главное изменение v1.8: вкус отделён от выгодности

Taste verdict формируется **до** оценки сделки и не видит:

- цену и скидку;
- глобальный/русский review score и число отзывов;
- исторический минимум;
- дату окончания акции;
- SteamDB;
- commercial feed-флаги вроде `exceptional_discount` и `very_high_rating`.

`strong_fit`, `strong_niche_fit`, `recent_fit` и похожие feed-флаги могут только отправить спорный EXCLUDE на targeted audit. Они не являются доказательством вкуса и сами не повышают кандидата до `moderate`.

Для нового кандидата нужен структурированный price-blind разбор по `gaming_taste_live.json`. Порог `moderate`: минимум два независимых содержательных положительных сигнала из канонического профиля и отсутствие прямого сильного отрицательного сигнала/известного конкретного конфликта структуры игры.

## Persistent taste-cache

Файл: `data/cache/taste_fit.json`.

Это **не второй профиль вкуса и не пользовательское evidence**. Это только кэш уже вычисленного verdict.

Cache hit разрешён, только если одновременно совпадают:

- exact production key;
- Git blob SHA текущего `gaming_taste_live.json`;
- `taste_model_version`;
- price-blind fingerprint кандидата.

Fingerprint включает identity/title/tags/core-fit/release-date и специально **не включает** цену, скидку, отзывы, feed reason flags или SteamDB.

Если профиль изменился, старые verdict не переиспользуются. За один run taste-cache обновляется максимум одним GitHub write. Ошибка maintenance-write не ломает корректную рассылку.

## Targeted false-negative audit

Audit остаётся локальным и price-blind. Store, SteamDB, reviews, цена и скидка в нём запрещены.

Перепроверяются только конфликтные EXCLUDE: borderline, неясная причина, конфликт recall-флагов с taste verdict, сильные профильные аналогии, sparse metadata при заметном core-fit и риск исчезновения релевантной family.

Никаких whitelist конкретных игр и никаких control-game names в policy нет.

## DLC, editions и bundles

DLC/Chapter не рекомендуется самостоятельно по умолчанию. Он может попасть в выпуск, если:

- base-game family сама прошла taste filter;
- канонический профиль/актуальный пользовательский контекст прямо поддерживает базовую игру;
- либо addon фактически является самостоятельным game-like продуктом и сам проходит threshold.

Cosmetic/soundtrack/artbook не выводятся. Wishlist не считается владением.

Для включённой family сравниваются локальные App/Sub/edition/bundle варианты. В выпуске одна основная строка на purchase family с лучшим вариантом покупки; полезная альтернатива может быть указана в той же строке.

## Store и SteamDB cache

`data/cache/store_state.json` строится из того же валидного production snapshot. Поэтому текущая цена/скидка не перепроверяются live Store для каждой игры. Live Store — только по conditional triggers.

`data/cache/steamdb_history.json` с v1.8 пишется как schema v2, но старый v1 читается совместимо.

Поддерживаются статусы:

- `confirmed_min`;
- `previously_free`;
- `unavailable_exact_history`.

Если SteamDB был успешно достигнут, но exact history действительно недоступна, это можно сохранить как negative-cache на 14 дней. Network/tool failure как negative-cache не сохраняется.

`entry_count` всегда считается как фактический `len(entries)`; stale metadata не используется для статистики и исправляется на следующем разрешённом write.

Нулевой historical minimum означает `previously_free`, а не обычный paid minimum и сам по себе не переводит игру в «ждать».

## Runtime pipeline

1. Сначала canonical policy.
2. Один раз canonical taste profile + его blob SHA.
3. QA полного production-feed и чтение всех chunks.
4. Для каждого кандидата price-blind fingerprint и проверка taste-cache.
5. Semantic taste evaluation только для cache misses.
6. Targeted price-blind audit только для свежих конфликтных verdict.
7. Content eligibility + offer-family resolution.
8. Максимум один write taste-cache при изменениях.
9. Current price/discount из fresh production snapshot; Store только условно.
10. SteamDB cache сначала; lookup только для настоящих misses/expired negatives/new-low cases.
11. Единый `provider + exact key` registry запрещает повторные внешние lookup.
12. Максимум один SteamDB cache write при изменениях.
13. Финальная сортировка: `БРАТЬ СЕЙЧАС` → `МОЖНО БРАТЬ` → `ЛУЧШЕ ЖДАТЬ`, затем taste fit и качество цены.

## Пользовательский вывод

- Показываются только INCLUDE.
- EXCLUDE и причины их отсутствия не перечисляются.
- В progress-сообщениях нельзя заранее называть кандидатов, которые потом могут быть исключены.
- Freebies проходят тот же minimum taste threshold.
- Upcoming — максимум одно ближайшее релевантное событие.
- Internal ledger показывается только по явному debug-запросу.

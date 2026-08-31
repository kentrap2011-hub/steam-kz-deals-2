# CURRENT TASK

Последнее обновление: 2026-08-31

## Завершено

### Taste V3
Статус: `complete`.
- canonical `ai_queue_count=0`;
- final Taste ingest, downstream visual build и deploy подтверждены зелёными;
- model binding: `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`.

### Steam fixed-package purchase options
Статус: `complete_production_validated`.

Правило:
- только fixed Steam Store Package (`Sub_`);
- >=2 currently visible base-game families;
- покрытие только по actual included appids / canonical family membership;
- original/remaster equivalence не угадывается;
- package должен быть строго дешевле суммы standalone current KZT prices;
- family считается один раз, unknown extra content value = 0;
- dynamic/personalized Complete-the-Set `/bundle/` исключён fail-closed;
- Taste/ranking не меняются, UI только отображает producer-owned `better_purchase_option` / package offer.

Production proof:
- merge PR #1 -> main commit `1438d6531062cd884a42177b33151606fc5e5fe9`;
- pre-AI run #65 / `33418890981` success, package regression success;
- real `fixed_package_options.json`: 679 app candidates, 795 package ids discovered, 19 eligible fixed packages, classification complete;
- visual run #110 / `33418941938` success: `items=445`, `qualifying_packages=7`, `touched_games=17`, `RANKING_REVIEW_ROWS=445`;
- visual commit `5b3b9244e207fb11cd32de22ed866f04ee896df8`;
- deploy run #149 / `33418983959` success;
- durable fast route: `docs/fixed_package_purchase_options.md`.

Diagnostic note: large generated JSON may be surfaced as empty by the GitHub connector. For this feature, bounded workflow logs and ranking-lookup counts are authoritative validation before attempting huge-file reads.

## Не активная основная работа

### SteamDB tail
Статус: `blocked_low_priority`.
- `App_901735` remains blocked/retryable;
- exact Kazakhstan historical minimum remains unproven and must not be fabricated.

## Запланировано, но ещё НЕ начато

### A. Ranking and card explanation quality audit
Статус: `planned`.
- audit минимум top-30 + boundary cases;
- trace `evidence -> Taste factors -> personal/purchase score -> rank -> card explanation`;
- высокий rank не должен необъяснимо получаться из одного слабого generic factor;
- служебная фраза вроде `Игра прошла строгий вкусовой отбор` не считается плюсом;
- каждая visible recommendation должна иметь минимум один конкретный содержательный плюс и минимум один доказуемый минус/ограничение/trade-off;
- `Подтверждённых персональных рисков не найдено` не считается минусом;
- если evidence недостаточно для содержательных плюса/минуса, карточка считается incomplete и требует enrichment, а не placeholder;
- добавить score/explanation regression guards.

### B. Russian language availability as a ranking factor
Статус: `planned`.
- проверять минимум русский интерфейс: `yes/no/unknown` + evidence;
- полного русского нет -> сильный practical/final-ranking penalty и видимый существенный минус;
- `unknown` не равно `no`;
- Taste semantics не менять.

### C. YouTube reviews for games
Статус: `planned`.
- полезный релевантный обзор перед покупкой;
- приоритет качественному русскоязычному ролику или подтверждённой русской аудиодорожке;
- не подставлять случайные/спойлерные видео ради ссылки;
- producer-owned choice, UI display-only.

### D. Fix stale/wrong game image when swiping cards
Статус: `planned`.
- при переходе на новую игру иногда остаётся изображение предыдущей до ручного refresh;
- text/price/image должны атомарно соответствовать текущей игре;
- проверить image state/key/cache и async race при быстрых переходах;
- добавить regression на несколько быстрых последовательных swipes.

### E. Guarantee Russian game descriptions
Статус: `planned`.
- 100% visible cards должны иметь содержательное русское описание;
- Steam Russian -> использовать/сокращать;
- Steam English/другой язык -> автоматически переводить на русский;
- английский fallback, скрытый блок и technical placeholder не допустимы;
- если у Steam действительно нет никакого source description, это отдельный exceptional data-quality case для разбора;
- добавить pre-deploy validation на nonempty Russian description и запрет placeholder strings.

## Текущий статус работ

Сейчас незавершённой `in_progress` задачи нет. Следующую плановую задачу начинать только после явного выбора пользователя; наличие пункта в backlog не означает, что он активен.

# CURRENT TASK

Последнее обновление: 2026-08-31

## Завершено

### Taste V3
Статус: `complete`.
- canonical `ai_queue_count=0`;
- final Taste ingest, downstream visual build и deploy подтверждены зелёными;
- model binding: `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`.

## Активная работа

### Steam fixed-package purchase options — visibility + ranking value
Статус: `reopened_in_progress`.

Почему переоткрыто:
- предыдущая production-validation доказала только, что producer нашёл package options и записал их в visual payload;
- пользователь фактически не видит наборы на странице, поэтому UI acceptance не была доказана;
- старое правило `Taste/ranking не меняются` неверно для продукта: выгодный multi-game package должен повышать ценность покупки и итоговый рейтинг.

Сохраняемые safety-инварианты:
- только fixed Steam Store Package (`Sub_`);
- >=2 currently visible base-game families;
- покрытие только по actual included appids / canonical family membership;
- original/remaster equivalence не угадывается;
- package должен быть строго дешевле суммы standalone current prices;
- family считается один раз, unknown extra content value = 0;
- dynamic/personalized Complete-the-Set `/bundle/` исключён fail-closed.

Новые обязательные требования:
1. На карточке выгодный набор показывается отдельным заметным producer-owned блоком, а не как неотличимый дополнительный offer.
2. Блок показывает как минимум: название набора, package price, сколько видимых игр он покрывает, их названия, standalone total, абсолютную экономию и ориентировочную цену за одну покрытую игру.
3. Есть явная кнопка открытия package в Steam.
4. Выгодность package влияет на final purchase score / `total_score`, а значит и на automatic rank.
5. Пример продуктового смысла: одна игра за ~150 ₽ хороша, но фиксированный набор примерно за 300 ₽ с 4 подходящими играми должен получить заметно более высокую оценку покупки, если сам package укладывается в practical purchase constraints.
6. Package boost должен быть прозрачным отдельным компонентом `score_breakdown`, а не скрытой сортировкой.
7. Нельзя повысить Taste: package влияет только на practical/purchase часть.
8. Не допускать двойного счёта одной и той же выгоды; формула должна явно различать standalone economics и дополнительную multi-game value.
9. Ranking review должен экспортировать package count/price/savings/value points, чтобы top-30 audit видел реальный driver.
10. UI regression: fixture с `better_purchase_option` обязан рендерить заметный package block; ranking regression: при прочих равных выгодный 4-game package существенно выше standalone-only варианта.

Предыдущий production proof (не является Definition of Done после reopening):
- merge PR #1 -> main commit `1438d6531062cd884a42177b33151606fc5e5fe9`;
- pre-AI run #65 / `33418890981` success;
- real `fixed_package_options.json`: 679 app candidates, 795 package ids discovered, 19 eligible fixed packages;
- visual run #110 / `33418941938`: `qualifying_packages=7`, `touched_games=17`;
- deploy run #149 / `33418983959` success.

Definition of done теперь:
- реальный deployed page явно показывает package block хотя бы на одном production game с `better_purchase_option`;
- package economics входят в transparent final score и реально меняют rank на regression + production data;
- score остаётся в каноническом диапазоне и не повышает Taste;
- ranking review показывает package driver;
- downstream build/deploy зелёные после изменений;
- docs/decision/routing синхронизированы только после этой пользовательской acceptance-границы.

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

Сейчас активна одна задача: fixed-package visibility + ranking value. Не закрывать её только по producer/log proof без проверки фактического UI и изменения рейтинга.

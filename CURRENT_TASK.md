# CURRENT TASK

Последнее обновление: 2026-09-01

## Завершено

### Taste V3 migration
Статус: `complete`.
- исходная миграция Taste V3 была завершена и production-validated;
- model binding: `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`.

Важно: это не означает, что текущий новый source snapshot уже полностью переоценён. Последний scheduled Taste run увидел authoritative queue `147`, но опубликовал `0`, потому что в `main` уже лежат 9 неингестированных submission-файлов с duplicate-key transactional hazard. Это отдельный GitHub-owned ingest/rebuild blocker; вручную строить «остаточную очередь» в ChatGPT нельзя.

### Steam fixed-package purchase options — BioShock + fresh commercial ranking
Статус: `complete_production_validated`.

Итог:
- fixed Steam `Sub_` package показывается, если покрывает >=2 visible base-game families по exact included appid или explicit verified purchase equivalence;
- original/remaster не угадываются по названию/fuzzy matching и не сливаются в Taste family;
- canonical purchase-only equivalence: `7670 -> 409710` (BioShock -> BioShock Remastered), `8850 -> 409720` (BioShock 2 -> BioShock 2 Remastered);
- package может быть видимым даже если сейчас не дешевле покрываемых игр отдельно; в таком случае UI пишет `Набор Steam`, а не `Выгодный набор Steam`, и package не получает ranking boost;
- Taste остаётся price-blind и не пересчитывается при изменении цены;
- fresh commercial refresh независимо обновляет current offers, RUB/KZT price, discount, history quality и sale end из текущего GitHub-owned `store_snapshot + family_graph + history_snapshot`;
- после commercial refresh выполняется package comparison, затем ровно один canonical final ranking pass;
- старый semantic snapshot сохраняет fit/taste factors/explanations/risks; semantic source и commercial source хранятся отдельно;
- semantic cards, которых больше нет в текущем complete family graph, удаляются из текущей витрины вместо сохранения stale цены.

Production proof:
- verified purchase-equivalence merge: `6783029ffe783a3971adaf57d64fa7b6aa76ec8f`;
- deterministic package refresh merge: `1aea1408aaf54810101bb296c547999e22f81503`;
- safe stale-source display merge: `e4b8dbb124c41b3d2ac7c947bab5cc99696c752e`;
- fresh commercial refresh merge: `5ba7ef744fb3fd706ae9e1bbf4e114f26278a561`;
- stale-family follow-up merge: `9a5ff38ac564c66526c04db6dbb41b09d91f8474`;
- visual run #130 / `33473546907`: success;
- `commercial refresh tests: 3 passed`;
- `fixed package purchase option tests: 19 passed`;
- `PRIORITY_RANKING_VALIDATION=PASS`;
- build completed with `ai_queue=147`, proving commercial/package ranking no longer waits for Taste completion;
- final visual: `442` cards, `PACKAGE_VISIBLE_CARDS=19`, `PACKAGE_RANKING_DRIVERS=15`;
- package diagnostics: `package_qualifying=8`, `package_strict=7`, `package_equivalence=1`, `package_touched=19`;
- visual commit: `15db361d25bdb16693bc080f1bdbbb3b71235371`;
- deploy #171 / `33473567370`: success;
- actual Pages artifact `9787352509` inspected: BioShock Collection is present on both `BioShock® 2` and `BioShock Infinite` with source-aligned commercial comparison.

Current BioShock production economics from deployed artifact:
- `BioShock® 2`: 74 ₽;
- `BioShock Infinite`: 182 ₽;
- covered standalone total: 256 ₽;
- `BioShock: The Collection`: 265 ₽;
- current delta: package is 9 ₽ more expensive (`savings_rub=-9`, `-3.5%`), therefore `strict_current_price_savings=false` and both cards correctly keep `purchase_route=standalone`;
- if future fresh prices make the package route better, the next deterministic commercial refresh will automatically recalculate package value and final rank without waiting for a new Taste evaluation.

Fast route:
- `docs/fixed_package_purchase_options.md`;
- `docs/RANK-013-fixed-package-purchase-route.md`;
- `docs/RANK-014-commercial-freshness-independent-of-taste.md`;
- `scripts/refresh_visual_commercial_fields.py`;
- `scripts/apply_fixed_package_purchase_options.py`;
- `scripts/build_final_visual_payload.py`;
- `.github/workflows/build-daily-visual-payload.yml`.

## Не активная основная работа

### Current Taste source ingestion
Статус: `blocked_requires_github_ingestion_rebuild`, не выбран как текущая interactive-задача.
- authoritative prepared queue: 147;
- last scheduled run evaluated/published: 0/0;
- blocker: 9 existing non-ingested Taste submissions and duplicate keys across inbox files;
- canonical ingestion/downstream completion for this source is not proven;
- GitHub-owned ingest/rebuild must resolve this before the scheduled semantic worker continues.

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

### F. Redesign detailed score breakdown UI
Статус: `planned`.
- раскрытая `Детальная оценка` визуально перегружена: слишком много pills/chips, слабая иерархия и лишняя высота на мобильном;
- сохранить всю прозрачность score, но сделать блок компактнее и визуально спокойнее;
- явно отделить `Подходит тебе` и `Выгодность покупки`, внутри перейти к более компактным строкам;
- package-driver встроить в коммерческую секцию, не превращая его в отдельную стену текста;
- технические подписи преобразовывать в пользовательские;
- ranking math не менять ради дизайна;
- regression/snapshot на mobile viewport.

## Текущий статус работ

Незавершённой `in_progress` interactive-задачи сейчас нет. Current Taste ingestion остаётся известным GitHub-owned blocker, но не должен тормозить fresh commercial/package ranking. Остальной backlog остаётся `planned`.

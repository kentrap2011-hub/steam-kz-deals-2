# CURRENT TASK

Последнее обновление: 2026-09-01

## Завершено

### Taste V3 migration
Статус: `complete`.
- исходная миграция Taste V3 была завершена и production-validated;
- model binding: `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`.

Важно: это не означает, что текущий новый source snapshot уже полностью переоценён. Последний scheduled Taste run увидел authoritative queue `147`, но опубликовал `0`, потому что в `main` уже лежат 9 неингестированных submission-файлов с duplicate-key transactional hazard. Это отдельный GitHub-owned ingest/rebuild blocker; вручную строить «остаточную очередь» в ChatGPT нельзя.

### Steam fixed-package purchase options — verified complete-content valuation
Статус: `complete`.

Финальная acceptance:
- feature implementation: `80789541b1d3384324beb64ba1fa067f08149eab`;
- double-count regression: `b2680f5740d2a45ea23287c33b2263aafded9b9f`;
- regression run `33486496289`, job `99787681615`: fixed package tests `19 passed`, complete-content tests `6 passed`;
- refreshed pre-AI commit: `e6ba0081d74970338aefa82a25fb68b3b5a09b63`;
- refreshed visual commit: `24b2890d0c85b14213fd0b91256afcfb306eb01e`;
- visual build run `33486538903`, job `99787819857`: success;
- deploy run `33486561472`, job `99787892867`: success; Pages artifact `9791985882`;
- latest deployed BioShock control case keeps all 6 verified included items and shows `256 ₽` visible games + `173 ₽` verified incremental content = `429 ₽` comparable value vs `265 ₽` package, savings `164 ₽` (`38.2%`);
- Season Pass / constituent overlap regression proves one entitlement is counted once; no production-code fix was required;
- final acceptance report: `reviews/worker_reports/package-acceptance-02.md`.

Все пункты Definition of Done для этой fixed-package задачи подтверждены. Следующая planned-задача здесь не начата.

## Завершённые package-инварианты, которые сохраняются

- только fixed Steam Store Package (`Sub_`);
- dynamic/personalized Complete-the-Set `/bundle/` исключён fail-closed;
- exact included appid + explicit verified directional purchase equivalence; title/fuzzy remaster guessing запрещён;
- package info может быть visible без ranking boost;
- Taste не меняется от цены;
- fresh commercial refresh обновляет standalone commercial fields независимо от semantic queue;
- scorer сравнивает standalone и eligible package routes без stacking одного и того же commercial value;
- verified top-level DLC/content может добавлять commercial value только при детерминированном current KZ acquisition route;
- unknown/unpriced и nonpersonalized content не получают выдуманную персональную стоимость;
- Season Pass / edition constituent content не считается рекурсивно второй раз.

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

### G. Compact purchase options — best option first, full list on demand
Статус: `planned`.
- в карточке по умолчанию показывать только самый выгодный/рекомендуемый способ покупки вместо длинного списка всех вариантов;
- пользователь должен явно видеть, что есть другие варианты, и по нажатию раскрывать полный список;
- после раскрытия должны оставаться доступны все подтверждённые варианты покупки и состав набора;
- выбор «лучшего варианта» должен использовать уже рассчитанную producer-owned оценку/экономику, а UI не должен самостоятельно пересчитывать ranking или цены;
- длинные package explanations и список standalone/DLC вариантов не должны занимать большую часть мобильного экрана в свернутом состоянии;
- техническую фразу вроде `одиночный вариант сейчас получает не меньший балл покупки` убрать из пользовательского текста или заменить понятным объяснением практического смысла;
- пользовательский текст должен отвечать на вопрос `что выгоднее купить и почему`, а не раскрывать внутреннюю терминологию score;
- добавить mobile regression/snapshot для свернутого и раскрытого состояний.

## Текущий статус работ

Fixed-package complete-content valuation завершена и закрыта. Новая planned-задача в этом worker-чате не начата. Current Taste ingestion остаётся отдельным GitHub-owned blocker.
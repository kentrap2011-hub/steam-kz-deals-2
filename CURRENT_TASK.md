# CURRENT TASK

Последнее обновление: 2026-08-31

## Что реально в работе сейчас

### 1. Taste V3 migration

Статус: `complete`.

Canonical binding:
- profile_blob_sha: `c478cda9bb7a9b024a30ca188dce4b98a2de24ea`
- taste_model_version: `taste-v3`
- taste_semantics_sha256: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- source_mailing_updated_at_utc: `2026-08-30T20:37:43.818127+00:00`

Canonical completion proof:
- final scheduled run started from authoritative queue `124`, evaluated all `124`, and published 7 checkpoints;
- final checkpoint `007` ingest run #47 (`33404093378`) completed `success`;
- active Taste inbox is empty / directory absent;
- canonical `data/production/pre_ai/chatgpt_payload.json` now has `ai_queue_count=0`;
- downstream `Build daily visual payload` run #108 (`33404127331`) completed `success`;
- subsequent `Deploy visual mailing` run #147 (`33404175193`) completed `success`.

### 2. Steam fixed-package purchase options

Статус: `in_progress`.

Old feature branch: `purchase-options-fixed-packages-20260831`.
Current integration branch: `purchase-options-fixed-packages-integration-20260831`.

Goal:
- fixed Steam Store Package (`Sub_`) becomes a producer-owned `better_purchase_option` when it actually covers >=2 visible base-game families and is strictly cheaper than their standalone current prices;
- UI remains display-only;
- Taste and ranking semantics do not change.

Already done:
- StoreBrowse discovery of fixed `Sub_` packages works;
- producer-side comparison/enrichment implemented;
- dynamic `/bundle/` / personalized Complete-the-Set excluded fail-closed;
- unknown extra content value=0;
- no original/remaster guessing;
- corrected BioShock live regression passed green;
- integration branch exists with package contract, discovery producer, visual enrichment, regressions and workflow integrations.

Current next step:
1. Refresh/recreate integration branch from current `main` after Taste completion.
2. Verify final diff contains only package files + minimal changes to two production workflows.
3. Integrate into `main`.
4. Run normal pre-AI build and inspect real `fixed_package_options.json`.
5. Run downstream visual build and verify real `better_purchase_option` / package `offers`.
6. Sync `PROJECT_ROUTES.md` / `PROJECT_DECISIONS.md` after production validation.

### 3. SteamDB tail

Статус: `blocked_low_priority`, не активная основная работа.
- `App_901735` remains blocked/retryable;
- exact Kazakhstan historical minimum is unproven and must not be fabricated;
- does not block package integration.

## Запланировано, но ещё НЕ начато

### A. Ranking and card explanation quality audit

Статус: `planned`.

Наблюдаемый дефект:
- встречаются высоко стоящие игры, где «Почему может зайти» содержит только общий/служебный текст вроде `Игра прошла строгий вкусовой отбор...`;
- встречается блок «Риск», где вместо реального минуса показан дисклеймер `Подтверждённых персональных рисков не найдено`;
- пример со скриншота: `Legend of Grimrock Bundle` фактически показывает 0 конкретных плюсов и 0 конкретных минусов, хотя находится высоко в ленте;
- нужно отличить defect ranking от defect explanation.

Требования к плюсам/минусам:
- служебные фразы о том, что игра «прошла отбор», не считаются плюсом и не должны отображаться как пользовательское объяснение;
- каждая видимая рекомендуемая игра должна иметь как минимум один конкретный содержательный плюс, объясняющий, что именно в игре может подойти пользователю;
- каждая видимая рекомендуемая игра должна иметь как минимум один конкретный содержательный минус/ограничение/trade-off: у игры могут не быть подтверждённых персональных конфликтов, но это не означает отсутствия недостатков вообще;
- минус не нужно выдумывать: если персонального риска нет, следует показать доказуемый общий gameplay/design drawback или ограничение, которое реально может повлиять на решение о покупке;
- если доказательств недостаточно даже для одного содержательного плюса или минуса, оценка карточки считается `incomplete` и требует дополнительного evidence/enrichment до финального отображения; нельзя заменять недостающую информацию мета-дисклеймером;
- блок лучше трактовать как `Минусы / что может не зайти`, а не только как «персональный риск», чтобы туда могли попадать реальные общие trade-offs;
- высокий rank должен иметь видимую содержательную причину на карточке, а не только внутренний score.

План аудита:
- аудит минимум top-30 + несколько игр возле границ priority buckets;
- трассировка `evidence -> Taste factors -> personal/purchase score -> rank -> card explanation`;
- проверить, не может ли высокий rank получаться почти из одного слабого фактора;
- проверить соответствие strengths/minuses фактическому evidence и score drivers;
- при необходимости изменить ranking constraints/weights и producer-owned explanation;
- добавить regression tests score/explanation consistency и запрет пользовательских placeholder/meta-фраз в strengths/minuses.

Definition of done:
- в top-30 нет карточек с нулём реальных плюсов или нулём реальных минусов/trade-offs;
- служебные фразы не маскируются под причины рекомендации;
- для каждой высокой позиции понятна цепочка `evidence -> score -> rank -> конкретные плюсы/минусы на карточке`.

### B. Russian language availability as a ranking factor

Статус: `planned`.

Требование:
- проверять наличие русского языка как минимум в интерфейсе;
- `yes/no/unknown` с проверяемым source/evidence;
- полное отсутствие русского должно давать сильный practical/final-ranking penalty;
- `unknown` не равно `no`;
- отсутствие русского должно быть видно на карточке как значимый минус;
- Taste semantics язык не меняет;
- добавить regression tests и language fields в ranking review.

### C. YouTube reviews for games

Статус: `planned`.

Цель:
- добавлять к играм полезные YouTube-ролики/обзоры, помогающие понять игру перед покупкой;
- приоритет качественным русскоязычным роликам или роликам с подтверждённой русской аудиодорожкой;
- не подставлять случайные, спойлерные или нерелевантные видео только ради наличия ссылки;
- источник/выбор должен быть producer-owned, UI только отображает готовый результат;
- перед внедрением определить критерии качества, актуальности, языка и fallback при отсутствии хорошего ролика.

### D. Fix stale/wrong game image when swiping cards

Статус: `planned`.

Симптом:
- при перелистывании на следующую игру карточка уже показывает данные новой игры, но изображение часто остаётся от предыдущей;
- правильная картинка появляется только после ручного обновления страницы.

Требование:
- при каждом переходе изображение должно сразу соответствовать текущей игре;
- не должно быть состояния, где текст/цена/игра уже новые, а картинка ещё от предыдущей;
- ручное обновление страницы не должно требоваться;
- проверить клиентское состояние изображения, ключи/кэш и гонки асинхронной загрузки при быстром перелистывании;
- добавить regression-проверку как минимум для нескольких быстрых последовательных переходов.

### E. Guarantee Russian game descriptions

Статус: `planned`.

Наблюдаемый дефект:
- для части игр вместо нормального описания показывается техническая заглушка вроде `Русское краткое описание для этой игры пока не подготовлено.`

Требование:
- у каждой видимой игры на карточке должно быть содержательное описание на русском языке;
- если Steam уже отдаёт русское описание, использовать/сокращать его без потери смысла;
- если Steam отдаёт описание только на английском или другом языке, автоматически переводить его на русский и показывать русский текст;
- английский fallback в пользовательской карточке не является допустимым конечным состоянием;
- скрывать блок из-за того, что перевод не подготовлен, тоже не является допустимым конечным состоянием;
- никакие внутренние placeholder-строки не должны доходить до production UI;
- если у игры в Steam действительно отсутствует какое-либо исходное описание, это отдельный exceptional data-quality case: пометить его явно и разбирать отдельно, а не молча публиковать карточку без описания;
- добавить pre-deploy validation: каждая visible game имеет непустое русское описание и не содержит известных placeholder-строк;
- проверить все текущие visible games и устранить уже существующие заглушки.

Definition of done:
- 100% visible game cards имеют нормальное русское описание;
- иностранное Steam-описание автоматически переводится;
- отсутствие исходного описания фиксируется как отдельная ошибка данных и разбирается отдельно.

## Overall Definition of done

Active work now:
- package integration reaches production validation.

Planned backlog after that includes at least:
- ranking/card explanation quality audit;
- Russian-language ranking factor;
- YouTube reviews for games;
- stale/wrong game image on card swipe;
- guaranteed Russian game descriptions.

`CURRENT_TASK.md` should clearly distinguish `in_progress` from `planned`; adding a future task must not automatically mark it active.

# CURRENT TASK

Последнее обновление: 2026-08-31

## 1. Taste V3 migration

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
- canonical `data/production/pre_ai/chatgpt_payload.json` now has `ai_queue_count=0`, `ready_without_ai_count=566`, `purchase_context_line_count=566`, `deterministically_excluded_without_ai_count=93`, `complete_family_partition=true`, `sale_end_coverage=1.0`;
- downstream `Build daily visual payload` run #108 (`33404127331`) completed `success` after the final ingest;
- subsequent `Deploy visual mailing` run #147 (`33404175193`) completed `success`;
- Taste V3 Definition of Done is satisfied: queue exhausted, current-bound V3 results persisted, downstream visual/deploy succeeded.

Historical recovery notes retained only as audit context:
- permanent fail-closed identity mismatch diagnostics: commit `c0201333b86f0efad6a1ee57b35b022b48698031`;
- one-shot repair workflow was used only for proven serialization/identity-copy errors and did not change verdict/evidence/taste_factors.

SteamDB:
- `App_901735` remains blocked/retryable;
- exact Kazakhstan historical minimum is still unproven and must not be fabricated;
- this is an independent low-priority tail and does not block package integration.

## 2. Steam fixed-package purchase options

Статус: `ready_for_final_integration`.

Old feature branch: `purchase-options-fixed-packages-20260831`.
Current integration branch: `purchase-options-fixed-packages-integration-20260831`.

Goal:
- fixed Steam Store Package (`Sub_`) becomes a producer-owned `better_purchase_option` when it actually covers >=2 visible base-game families and is strictly cheaper than their standalone current prices;
- UI remains display-only;
- Taste and ranking semantics do not change.

Already proven:
- StoreBrowse discovery of fixed `Sub_` packages works;
- producer-side comparison/enrichment implemented;
- dynamic `/bundle/` / personalized Complete-the-Set excluded fail-closed;
- unknown extra content value=0;
- no original/remaster guessing: coverage only through actual included appids / canonical family membership;
- BioShock live regression uses current package members `409710`, `409720`, `8870`;
- corrected read-only live package test passed green;
- fresh integration branch was created from then-current `main` with package contract, discovery producer, visual enrichment, regressions and minimal workflow integrations;
- temporary live-test workflow is intentionally not part of production integration.

Next steps:
1. Refresh/recreate the integration branch from current `main` now that Taste is complete.
2. Verify final diff contains only package files + minimal changes to the two production workflows.
3. Integrate package feature into `main`.
4. Run normal pre-AI build and inspect real `data/production/pre_ai/fixed_package_options.json`.
5. Run downstream visual build and verify real `better_purchase_option` / package `offers` entries.
6. After production validation, sync `PROJECT_ROUTES.md` / `PROJECT_DECISIONS.md`.
7. Clean up obsolete temporary branches/workflows when safe.

## 3. Ranking and card explanation quality audit

Статус: `active_parallel`.
Причина: пользователь при просмотре витрины видит случаи, когда игра стоит высоко, но карточка объясняет это одним слабым/узким плюсом вроде «удобное управление», иногда без единого минуса. По карточке непонятно, почему рекомендация действительно высокая: либо ranking скрывает важные причины, либо сама оценка может быть завышена.

Цель:
- проверить не только корректность численного ranking, но и качество semantic evaluation и объяснений на карточке;
- высокая позиция должна быть либо реально обоснована несколькими сильными сигналами, либо карточка должна ясно показывать тот сильный сигнал/контекст, который её объясняет;
- не придумывать минусы ради заполнения карточки: отсутствие минусов допустимо только если evidence действительно не содержит существенных рисков/конфликтов.

Аудит оценки:
1. Взять репрезентативную выборку верхней части витрины (минимум top-30) + несколько игр возле границ priority buckets.
2. Для каждой игры трассировать фактический путь до позиции: normalized Taste factors, personal score, purchase score, direct-user evidence, wishlist, deal/history/savings, risk/penalty, priority bucket и tie-breaks.
3. Проверить, может ли top/high placement фактически получаться почти из одного узкого фактора (например controls/accessibility) при слабой поддержке остальных факторов.
4. Если да — определить, это допустимый результат из-за другого сильного evidence/context или defect weighting/aggregation. Если высокий rank реально достигается одной слабой причиной, изменить ranking constraints/weights так, чтобы top placement требовал более широкой поддержки либо отдельного действительно сильного доказательства.
5. Проверить consistency между `taste_factors`, verdict/fit, `why_fit`, risks и итоговым personal score: высокая factor-оценка должна иметь видимое evidence, а слабая/противоречивая evidence не должна превращаться в высокий персональный score без объяснимой причины.

Аудит карточки/описаний:
1. Для каждой top-игры сравнить фактические ranking drivers с тем, что пользователь видит в карточке.
2. Карточка должна отвечать на вопрос «почему эта игра так высоко именно для меня», а не показывать случайный один плюс.
3. Если несколько факторов реально внесли большой вклад, показать несколько конкретных причин или отдельный короткий блок `Почему высоко` / эквивалентное producer-owned explanation.
4. Проверить, что `why_fit`/strengths не состоят из повторяющихся generic-фраз и не скрывают более сильные персональные причины.
5. Проверить risks/minuses: если pipeline знает отрицательное evidence/risk, карточка не должна показывать пустой список; если отрицательного evidence действительно нет, не генерировать искусственный минус.
6. Описание должно отражать ranking truth: UI не придумывает причины самостоятельно, producer передаёт готовое объяснение, связанное с реальными score drivers.

Проверки качества/регрессии:
- top-ranked fixture не должен иметь необъяснимо высокий personal score при одном слабом factor без отдельного strong evidence;
- если high rank объясняется wishlist/сильной выгодой/direct-user evidence, карточка должна явно показывать это как причину позиции;
- если есть nonzero risk/negative evidence, пользователь должен видеть соответствующий meaningful risk/minus;
- не требовать фиксированного количества плюсов/минусов: требовать полноту относительно фактического evidence;
- ranking review export должен позволять одним row увидеть score components + отображаемые explanation fields для ручной сверки.

Definition of done:
- ручной аудит top-30 не находит необъяснимых высоких позиций;
- для каждой высокой позиции можно восстановить понятную цепочку `evidence -> factors/scores -> rank -> card explanation`;
- карточка показывает основные причины высокой позиции и реальные существенные риски, если они есть;
- один generic-плюс сам по себе не способен необъяснимо поднять игру в топ;
- regression tests защищают score/explanation consistency;
- изменения синхронизированы с ranking/explanation contracts и PROJECT_DECISIONS после проверки.

## Overall Definition of done

Taste: COMPLETE.

Purchase options:
- fixed `Sub_` discovery/comparison works in production;
- package advice is producer-owned and UI display-only;
- no edition guessing;
- production artifact and visual field are validated.

Ranking/explanation quality:
- top recommendations are both numerically justified and visibly explainable from the card;
- score drivers and displayed reasons stay consistent.

`CURRENT_TASK.md` is removed only when package integration and ranking/explanation quality audit are complete and no active task remains.

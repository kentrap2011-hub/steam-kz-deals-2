# WORKER TASK — Steam semantic queue priority implementation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

## Repository scope guard

Работай только в репозитории `kentrap2011-hub/steam-kz-deals-2`.
Не ищи, не читай, не меняй и не используй другой репозиторий для выполнения этой задачи.
Если GitHub/tool открыл другой repo по умолчанию или target неоднозначен — остановись и сначала переключись на `kentrap2011-hub/steam-kz-deals-2`.

## Task ID

`STEAM-SEMANTIC-QUEUE-PRIORITY-IMPLEMENT-01`

## Mode

`IMPLEMENT / VALIDATE`

## User product decision

Предыдущая идея `first semantic wave + deferred reserve` отклонена как production direction.

Новая продуктовая семантика:

1. Не сокращать semantic pool только ради экономии semantic-work.
2. Не переводить обычные подходящие игры в `deferred_reserve`.
3. Все текущие канонически допустимые semantic candidates остаются eligible по существующим правилам.
4. Меняется только порядок обработки:
   - в первую очередь игры, по которым никогда не было глубокого анализа;
   - внутри этой приоритетной группы выше должны идти игры с лучшим сочетанием:
     - Steam positive rating;
     - Steam review count;
     - current price;
     - current discount.
5. Это должен быть прозрачный детерминированный приоритет, а не скрытое taste-решение и не hard top-N.

## Important interpretation

Не реализуй буквальную наивную дробь из четырех величин, если она создает очевидные перекосы.

Нужно выбрать и документировать простую, объяснимую, монотонную формулу/lexicographic score, в которой:
- более высокий Steam rating не ухудшает priority;
- большее число отзывов повышает confidence, но не должно линейно задавить нишевые игры; допускается log/bucket normalization;
- более низкая current price повышает commercial priority;
- более высокий discount повышает commercial priority;
- score не становится personal taste score и не меняет Deep score/ranking semantics.

Если в canonical policy уже есть approved purchase-value/order primitives, переиспользуй их вместо параллельной формулы, если это не противоречит этому task.

## Exact first-priority cohort

Сначала установи из текущего canonical state, какой GitHub-owned признак надежно означает:

`never had deep analysis`.

Предпочтительная семантика — отсутствие любого исторически принятого/authoritative Deep результата для данного taste subject/family.

Не путай:
- `never analyzed`;
- `authoritative fit`;
- `authoritative not-fit`;
- incomplete/recovery/failed transport;
- legacy result that current canonical contracts still consider authoritative.

Если текущие contracts проводят более точное различие, используй canonical definition и зафиксируй его в report.

## Architecture / ownership boundary

Эта задача меняет только GitHub-owned queue priority / ordering policy и существующий producer/orderer, который готовит semantic/Deep work.

Нельзя:
- менять Deep Stage 1 scoring logic;
- менять Deep Stage 2 calibration logic;
- менять frozen interfaces PR #156;
- менять Dossier semantic judgment;
- менять final ranking formula;
- менять site/UI;
- создавать второй queue owner;
- переносить ordering ownership в ChatGPT prompt;
- менять Scheduled Tasks, их расписания или настройки;
- создавать новый scheduler/retry/backlog manager.

ЧАТ 2 остается единственным владельцем текущих Deep Stage 1/Stage 2 logic implementation tasks.

Если выяснится, что требуемая сортировка физически живет в том же изменяемом implementation surface, где сейчас работает ЧАТ 2, и безопасно разделить изменения нельзя — не лезь туда. Зафиксируй конфликт и остановись с bounded report.

## Required preflight

Перед кодом:
1. найди exact current GitHub owner semantic/Deep ordering;
2. найди current canonical queue-order policy/instruction file, если он уже существует;
3. подтверди, что изменение не меняет eligibility/scope;
4. подтверди отсутствие пересечения с активной Stage 2 веткой ЧАТ 2;
5. зафиксируй current ordering before-change.

Не делай широкий архитектурный аудит.

## Required implementation

С минимальным diff:

1. Добавь/обнови один canonical GitHub-owned queue-order policy/instruction artifact.
2. Измени существующий GitHub producer/orderer так, чтобы:
   - eligible semantic pool не уменьшался;
   - first ordering key = never-deep-analyzed cohort before previously Deep-analyzed subjects, когда оба реально требуют work;
   - within comparable cohort применяется прозрачный commercial/quality priority по rating + review confidence + current price + discount;
   - ordering стабильный и детерминированный при ties.
3. Не используй sale expiry как приоритетный фактор.
4. Не вводи hard top-N.
5. Не меняй worker prompt ради ownership логики, если prompt только consumer manifest.
6. Сохрани exact manifest/work bindings и fail-closed поведение.

## Validation

Нужны детерминированные тесты/fixtures, доказывающие минимум:

- semantic candidate count до/после одинаков при одинаковом input;
- ни один candidate не становится deferred/excluded только из-за новой очередности;
- never-deep-analyzed идет раньше уже анализировавшегося при прочих равных;
- rating monotonicity;
- review-confidence monotonicity без линейного popularity domination;
- lower-price monotonicity;
- higher-discount monotonicity;
- deterministic tie-break;
- Wishlist/package/DLC lanes не теряются из scope;
- authoritative Deep fit/not-fit semantics не переписываются новой сортировкой;
- frozen Stage 1/Stage 2 interfaces не меняются.

Если возможно безопасно, покажи offline before/after первые 20–30 queue positions на текущем production snapshot без semantic execution.

## Do not execute semantic workers

Не запускай Dossier, Deep Stage 1, Deep Stage 2 или manual semantic workers как validation.

Не создавай и не изменяй ChatGPT Scheduled Tasks / automations.

## Deliverables

1. bounded implementation branch;
2. tests/validation;
3. PR;
4. compact report:
   `reviews/worker_reports/steam-semantic-queue-priority-implement-01.md`.

Report должен содержать:
- exact owner/policy path;
- old ordering;
- new ordering;
- exact definition of `never deep analyzed`;
- chosen score/normalization;
- proof candidate count is unchanged;
- overlap/conflict check with active ЧАТ 2 Stage 2 work;
- validation results;
- PR number/head;
- remaining risks.

## CURRENT_TASK.md

Можно обновить только в конце, когда implementation и validation действительно завершены.
Не переписывай чужие concurrent sections.

## Completion criteria

Задача завершена только если:
- full semantic eligibility remains unchanged;
- ordering semantics соответствуют user decision;
- no hard top-N/deferred-reserve gating introduced;
- no Deep Stage 1/2 scoring change;
- validations green;
- PR и durable report созданы.

## Expected next step

После worker completion Director проверяет только compact report + PR/check status и решает, принимать ли ordering change.

Не начинай никакую следующую задачу проекта.

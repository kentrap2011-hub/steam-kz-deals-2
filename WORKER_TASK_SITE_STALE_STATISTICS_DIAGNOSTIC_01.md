# WORKER TASK — Site stale statistics diagnostic 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

## Repository scope guard

Работай только в репозитории `kentrap2011-hub/steam-kz-deals-2`.
Не ищи, не читай, не меняй и не используй другой репозиторий для выполнения этой задачи.
Если GitHub/tool открыл другой repo по умолчанию или target неоднозначен — остановись и сначала переключись на `kentrap2011-hub/steam-kz-deals-2`.

## Task ID

`SITE-STALE-STATISTICS-DIAGNOSTIC-01`

## Mode

`READ-ONLY / DIAGNOSTIC / PRODUCTION TRACE`

## User-visible symptom

На странице сайта «Статистика» отображаются устаревшие данные относительно текущего canonical GitHub state.

Наблюдавшийся пользователем экран:

### «Глубокий разбор»
- всего игр для глубокого разбора: 2293
- последняя запись: 05.10.2026, 20:29
- окончательно разобрано: 117
- завершено: подходит: 104
- завершено: не подходит: 13
- не удалось завершить / требуется восстановление: 18
- ждёт досье: 2135
- готово к разбору / ожидает: 23
- осталось до окончательного разбора: 2176

Но при последней директорской проверке текущий canonical
`data/production/pre_ai/progressive_pass2_work.json` уже показывал:
- coverage target: 2301
- authoritative completed: 147
- fit: 133
- not fit: 14
- incomplete/recovery: 19
- waiting for dossier: 2135
- ready/pending: 0
- remaining until all authoritative: 2154
- `items: []`

Deep semantic worker поэтому корректно остановился с пустым manifest.

### «Переводы описаний»

На том же пользовательском экране отображалось:
- игр без перевода: 813
- на диагностике перевода: 1
- последний успешный перевод: 05.10.2026, 16:48
- последняя попытка перевода: 05.10.2026, 16:48

Проверь этот блок также против текущего canonical translation state. Не используй приведённые числа как source of truth — они только наблюдаемый UI symptom.

## Goal

Установить **первый причинный этап**, из-за которого Statistics page публикует/читает устаревшие значения.

Нужно понять, где именно рассинхронизация:

1. canonical production state свежий, а derived statistics artifact не пересобирается;
2. derived artifact свежий, но Pages/site bundle использует старую копию;
3. workflow trigger/order не запускает нужную публикацию;
4. Statistics UI читает неправильный/legacy source;
5. cache/service-worker/CDN держит старый payload;
6. или другая конкретно доказанная причина.

Не выбирай причину по предположению — проследи exact data path.

## Scope

Проверь только цепочку данных, необходимую для страницы «Статистика», начиная от canonical источников соответствующих метрик до опубликованного site artifact.

Минимально охвати:
- Deep/Progressive statistics block;
- Russian-description translation statistics block;
- общую отметку freshness/last-write для этих блоков;
- при необходимости сам statistics data payload/site artifact, который реально читает UI.

Не делай широкий аудит всего сайта.

## Required diagnostic steps

1. Найди exact source path(s), из которых UI «Статистика» получает эти значения.
2. Сопоставь их с текущими canonical:
   - Progressive/Deep state/work;
   - Dossier state только в той мере, в какой он участвует в Deep counts;
   - translation queue/status/cache only for translation block.
3. Определи, на каком exact этапе последний раз обновился statistics payload.
4. Найди owner/workflow/script, который обязан обновлять/публиковать этот payload.
5. Проверь последний релевантный production run/status без широкого перебора workflow history.
6. Установи first causal stale stage.
7. Отдельно ответь:
   - почему UI всё ещё показывает Deep ready/pending = 23, когда current canonical = 0;
   - почему Deep totals/completed отстают;
   - является ли translation block тем же дефектом или отдельным stale path;
   - может ли обычное обновление браузера исправить состояние, или опубликованный payload сам устарел.

## Important boundaries

Не исправляй код в этой задаче.

Не меняй:
- production canonical data;
- Dossier/Deep/translation state;
- semantic worker prompts;
- ranking;
- queue ordering;
- Stage 1/Stage 2 logic;
- site UI;
- workflows;
- Service Worker;
- Scheduled Tasks / automations.

Не запускай semantic workers.

Если обнаружишь несколько независимых stale-path defects, перечисли их раздельно и ранжируй по причинности/влиянию. Не превращай diagnostic в большой сайт-аудит.

## Deliverable

Создай только compact report:

`reviews/worker_reports/site-stale-statistics-diagnostic-01.md`

Report должен содержать:
- current canonical values;
- exact UI/published source values;
- exact data flow from canonical state to Statistics page;
- first stale stage/root cause;
- affected blocks;
- latest relevant production run/status;
- whether browser/service-worker cache is causal or merely secondary;
- smallest bounded implementation fix;
- какие файлы/owner должен менять следующий worker;
- риски/acceptance check после fix.

## CURRENT_TASK.md

Не менять, кроме случая, когда действующий CHAT_PROTOCOL явно требует минимального closeout update. Если меняешь — только минимально и не перезаписывай concurrent sections.

## Completion criteria

Диагностика завершена только когда:
- доказан first causal stale stage;
- объяснены наблюдаемые Deep discrepancies;
- translation block классифицирован как same-root-cause или separate-root-cause;
- предложен минимальный bounded fix;
- production ничего не изменено.

## Expected next step

После report Director решит, давать ли ЧАТ 1 отдельную IMPLEMENT-задачу на найденный минимальный fix.

Не переходи к реализации и не начинай следующую задачу.

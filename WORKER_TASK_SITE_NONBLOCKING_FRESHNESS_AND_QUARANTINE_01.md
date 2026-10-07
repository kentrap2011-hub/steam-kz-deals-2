# WORKER TASK — Site nonblocking freshness and quarantine 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

## Repository scope guard

Работай только в репозитории `kentrap2011-hub/steam-kz-deals-2`.
Если GitHub/tool открыл другой repo или target неоднозначен — остановись и сначала переключись на этот repo.

## Task ID

`SITE-NONBLOCKING-FRESHNESS-AND-QUARANTINE-01`

## Mode

`IMPLEMENT / ARCHITECTURE AUDIT / VALIDATE`

## Supersedes

Эта задача заменяет узкий follow-up:
`WORKER_TASK_SITE_STALE_STATISTICS_FIX_01.md`.

Не ограничивайся Tetris или одним validator. Используй завершённую диагностику:
`reviews/worker_reports/site-stale-statistics-diagnostic-01.md`
как уже доказанный пример системной проблемы.

## User product decision

Сайт должен максимально продолжать показывать **актуальную информацию**, даже если отдельный объект, карточка, текст, semantic result или иной единичный фрагмент не проходит проверку.

Правило продукта:

1. Ошибка одного конкретного элемента не должна блокировать публикацию независимых свежих данных сайта.
2. Нельзя просто отключать проверки.
3. Не прошедший элемент должен:
   - быть изолирован;
   - попасть в отдельное GitHub-owned место ожидания/диагностики;
   - быть видимым в статистике сайта;
   - не мешать обработке и публикации остальных корректных изменений.
4. Для пользовательского отображения проблемного элемента:
   - использовать последний известный корректный вариант, если он безопасно и однозначно доступен;
   - иначе скрыть только проблемный фрагмент/элемент с нейтральным состоянием;
   - не блокировать из-за него глобальное обновление.
5. Статистика должна отдельно показывать число объектов, ожидающих исправления/диагностики, с понятной категорией причины.
6. Новые ошибки должны накапливаться в отдельной диагностической области GitHub, а не превращаться в общий publication stop.
7. Сайт не должен оставаться целиком на старом snapshot только из-за локальной ошибки одного объекта.

## Important safety boundary

Не превращай требование "не блокировать сайт" в "публиковать любые битые данные".

Раздели ошибки на два класса:

### A. Local / isolatable defect

Пример:
- неподходящий player-facing explanation одной игры;
- невалидный отдельный semantic/card field;
- один результат не прошёл локальную проверку;
- отдельная карточка не может быть безопасно обновлена.

Такие ошибки должны быть quarantined/nonblocking.

### B. Global integrity / authority failure

Пример:
- невозможно доказать, к какому production snapshot относится весь payload;
- сломана/нечитаема общая schema;
- отсутствует обязательная global binding/authority;
- невозможно определить, какие данные вообще являются canonical;
- потенциально небезопасный глобальный corruption.

Такие ошибки могут оставаться fail-closed для глобальной публикации.

Цель задачи — найти и убрать **ложные глобальные блокировки, вызванные локальными ошибками**, а не отменить настоящие глобальные гарантии целостности.

## Goal

Найти по всей актуальной цепочке публикации сайта все места, где локальная проблема одного объекта может остановить публикацию независимых актуальных данных, и изменить архитектуру так, чтобы:

- локальные ошибки изолировались;
- остальные свежие данные продолжали публиковаться;
- проблемные элементы попадали в отдельную GitHub-owned quarantine/diagnostic surface;
- Statistics page показывала такие проблемы;
- publication freshness больше не зависела от безошибочности каждого отдельного элемента.

## Required architecture preflight

До кода:

1. Проследи текущую production publication chain от canonical data до Pages.
2. Найди **все blocking gates** этой цепочки, которые могут остановить persistence/deploy.
3. Для каждого gate классифицируй:
   - global integrity blocker — оставить fail-closed;
   - local item/content blocker — сделать isolatable/nonblocking;
   - mixed — разделить global и local части.
4. Не делай широкий аудит не относящихся к публикации подсистем.
5. Не меняй semantic truth/ranking/Deep scoring для обхода display validation.

## Required implementation properties

### 1. Separate current site-status/statistics surface

Создай или используй существующий отдельный GitHub-owned current statistics/status artifact, который:
- строится из актуальных canonical production states;
- не зависит от успешности рендера всех карточек;
- публикуется независимо от локальных card/content failures;
- используется Statistics page как источник актуальных счётчиков.

Он должен включать как минимум:
- Deep totals/completed/fit/not-fit/incomplete/waiting/ready/remaining;
- Dossier progress, если он уже является частью пользовательской Statistics page или нужен для объяснения Deep waiting;
- Russian description untranslated/diagnostic/last attempt/last success;
- количество текущих quarantined/diagnostic site items;
- разбивку проблем по основным категориям;
- timestamps/freshness/source binding, достаточные чтобы видеть, насколько данные свежие.

Не заставляй browser собирать эти цифры напрямую из нескольких внутренних GitHub файлов.

### 2. Quarantine / diagnostic surface

Добавь одно canonical GitHub-owned место для локальных publication/display defects.

Требования:
- append/reconcile behavior должен оставаться GitHub-owned;
- стабильная identity проблемного объекта;
- category/reason;
- first_seen / last_seen или эквивалентная наблюдаемость;
- source/build binding;
- current status: pending/resolved/superseded или эквивалент;
- без raw private reasoning и без лишних пользовательских данных;
- не создавать бесконечные дубликаты одной и той же проблемы.

Не придумывай второй scheduler или ChatGPT-owned queue.

### 3. Per-item fallback/isolation

Для каждого local-failure класса:
- isolate only failed item/field;
- если есть последний известный корректный presentation fragment — разрешён deterministic reuse только при доказанной same-item identity/compatibility;
- иначе omit/hide only failed presentation fragment;
- продолжить сборку остальных current data;
- record diagnostic/quarantine entry.

### 4. Statistics observability

На сайте должно быть видно:
- что есть элементы, ожидающие диагностики/исправления;
- сколько их;
- краткие категории причин;
- дата/время последней актуальной статистики.

Не нужно показывать пользователю внутренние stack traces или технический мусор.

### 5. Publication behavior

После refactor:
- local card/content defect не должен оставлять Statistics на старом snapshot;
- local defect одной игры не должен блокировать обновление других корректных игр;
- deploy должен публиковать fresh current status/statistics даже при наличии quarantine;
- global integrity failure по-прежнему может остановить unsafe global publish.

## Specific known regression

Обязательно воспроизведи и закрой текущий доказанный случай:

`Tetris® Effect: Connected`

Accepted Deep score/provenance не менять.
Commercial/ranking-only wording не должен публиковаться как positive player-facing `why_fit`.
Этот локальный дефект должен либо:
- безопасно убрать только неподходящую positive explanation,
- либо использовать доказанный last-known-good presentation fragment,
и зарегистрироваться/разрешиться через новую diagnostic surface без остановки свежей статистики и остальной публикации.

## Audit targets

Проверь только publication-relevant surfaces, включая при необходимости:
- visual payload build;
- card explanation validation;
- material/freshness validation;
- canonical visual persistence;
- deploy staging;
- site statistics payload;
- any per-item validation currently escalated to whole-payload failure;
- any last-known-good mechanism that can itself freeze unrelated current state.

Не надо исследовать все workflows проекта.

## Non-goals / forbidden changes

Не меняй ради этой задачи:
- Deep Stage 1 / Stage 2 scoring semantics;
- Dossier semantic judgment;
- translation semantic judgment;
- final recommendation/ranking formula;
- semantic queue ordering;
- Steam discovery/filter semantics;
- Scheduled Tasks / automations;
- user taste profile;
- unrelated UI pages.

Не запускай semantic workers для validation.

## Validation requirements

Нужно доказать минимум:

1. inventory всех найденных publication-blocking gates с классификацией local/global/mixed;
2. все local blockers больше не блокируют независимую fresh publication;
3. genuine global integrity blockers остаются fail-closed;
4. Tetris regression больше не останавливает общий publish;
5. один synthetic/fixture local card failure приводит к quarantine + свежей публикации остальных данных;
6. Statistics получает fresh canonical counters независимо от local card failure;
7. quarantine count/category видны в statistics payload/UI;
8. исправленный/исчезнувший defect корректно выходит из active pending diagnostics;
9. нет duplication explosion одной и той же проблемы;
10. current visual/site deploy succeeds through one real fresh production-relevant cycle;
11. published Statistics Deep values совпадают с exact canonical snapshot binding used for that status build;
12. translation values остаются current and independently observable;
13. no Scheduled Task changes;
14. no Stage 1/Stage 2 scoring changes.

## Deliverables

- implementation branch;
- PR;
- tests/validation;
- compact report:
  `reviews/worker_reports/site-nonblocking-freshness-and-quarantine-01.md`.

Report должен содержать:
- список всех найденных blocking gates;
- какие из них были true global blockers и оставлены;
- какие local/mixed blockers изменены;
- exact quarantine/status artifact paths;
- как теперь публикуется Statistics;
- поведение last-known-good/omit fallback;
- Tetris regression result;
- real fresh build/deploy result;
- before/after counters;
- remaining risks;
- PR/head/checks.

## CURRENT_TASK.md

Обновлять только минимально при завершении и не перезаписывать concurrent sections.

## Completion criteria

Задача завершена только если:
- локальная ошибка отдельного объекта больше не способна заморозить независимые свежие данные сайта;
- Statistics page получает отдельный свежий status source;
- local failures видны в статистике и отдельной diagnostic/quarantine surface;
- genuine global integrity protections сохранены;
- один свежий end-to-end publication cycle это доказал.

## Expected next step

Вернуться к Director для acceptance.
Не переходить к задаче Current Tasks page или другой новой работе.

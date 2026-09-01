# PARALLEL WORKER TASK

Task ID: `image-swipe-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/image-swipe-01.md`

## Goal

Исправить отдельный пользовательский баг: при быстром перелистывании карточек иногда остаётся изображение предыдущей игры, хотя текст и остальные данные уже относятся к новой игре.

Эта задача должна быть независима от текущей работы по fixed Steam packages и не должна менять package valuation, Taste, ranking, production contracts или package tests.

## Background

В `CURRENT_TASK.md` эта проблема уже записана как planned-задача:

`D. Fix stale/wrong game image when swiping cards`

Перед работой прочитай актуальные `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `CURRENT_TASK.md`, релевантный route и только нужные `web/**` файлы.

## What to do

1. Воспроизведи/локализуй причину, почему при переходе на следующую карточку изображение может остаться от предыдущей.
2. Проверь прежде всего состояние текущей карточки, ключ/источник изображения, кэш и возможную гонку асинхронной загрузки при быстрых переходах.
3. Сделай минимальное исправление только в UI-слое.
4. Не меняй смысловые данные игры, ranking, package logic или production payload.
5. Добавь проверку, которая моделирует несколько быстрых последовательных перелистываний и подтверждает, что текст, цена и изображение всегда принадлежат одной и той же текущей игре.

## Validation

Проверь релевантный JS/UI validator или тесты проекта.

Если изменение касается `app.js`/`styles.css` и проект требует cache-busting в `web/index.html`, обнови его по существующему fast path.

Не запускай тяжёлый production rebuild: эта задача должна работать поверх уже готового payload.

## Parallel safety

Не изменяй:
- `WORKER_TASK.md`;
- package test files;
- package contracts;
- package valuation/ranking code;
- `CURRENT_TASK.md`, кроме случая, когда для этой параллельной задачи нужен отдельный краткий handoff и это можно сделать без потери основной активной package-задачи. Предпочтительно не трогать `CURRENT_TASK.md` вовсе.

Если обнаружишь, что необходимая правка всё же пересекается с текущей package-задачей или теми же файлами, остановись и зафиксируй конфликт в отчёте вместо продолжения.

## Done when

- причина stale image локализована;
- сделано минимальное UI-исправление;
- есть проверка на несколько быстрых перелистываний;
- связанные UI checks проходят;
- не изменена package/production semantics;
- создан компактный report.

## Report format

Сохрани результат в:

`reviews/worker_reports/image-swipe-01.md`

Структура:

### Task
Что было сделано.

### Verified facts
Что оказалось причиной.

### Changes
Какие файлы изменены и зачем.

### Validation
Какие проверки прошли.

### Unresolved
Что осталось.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
Один следующий шаг.

Укажи commit SHA. Не копируй большие логи или полный diff.

В финальном ответе обязательно назови путь:

`reviews/worker_reports/image-swipe-01.md`
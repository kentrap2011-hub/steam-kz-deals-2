# PARALLEL WORKER TASK

Task ID: `ru-description-audit-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/ru-description-audit-01.md`

## Goal

Понять реальный масштаб проблемы русских описаний карточек до системной реализации.

Проверить ограниченную, но полезную выборку видимых игр и определить:
- где описание уже нормальное русское;
- где оно английское/другое;
- где пустое;
- где техническое/шаблонное/малосодержательное;
- где источник есть, но текущая карточка показывает плохой fallback.

Ничего не исправлять в этой задаче.

## Background

Плановая задача E в `CURRENT_TASK.md` требует 100% meaningful Russian descriptions для visible cards, но до реализации нужно установить фактический масштаб проблемы.

Параллельно другой worker меняет только UI `Детальной оценки`. Этот аудит не должен менять UI или production data.

Перед работой прочитай актуальные:
- `CHAT_PROTOCOL.md`;
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- relevant routes/contracts для current published card data;
- текущий production/current payload, достаточный для выбора видимых карточек;
- description-related producer/source fields только для проверяемой выборки.

## Sample

Проверь минимум 25 и максимум 30 карточек:
- первые 20 текущего видимого/приоритетного списка;
- ещё 5–10 boundary/разнотипных случаев, если они доступны: package-related, older game, game with non-Russian source, missing/short description или другой явно отличающийся case.

Не расширяй исследование на весь каталог.

## Classification

Для каждой проверенной карточки присвой ровно одну основную категорию:
- `good_ru` — содержательное русское описание;
- `non_ru` — содержательное описание есть, но не на русском;
- `empty` — фактически нет описания;
- `placeholder_or_technical` — служебный/шаблонный/технический текст вместо нормального описания;
- `weak_ru` — русский есть, но слишком бедный/обрубленный/неинформативный для карточки.

Дополнительно для проблемных случаев установи, если возможно без широкого исследования:
- есть ли у Steam/source нормальное исходное описание;
- проблема похожа на отсутствие перевода, плохой fallback или отсутствие source data.

## What to determine

1. Сколько карточек в каждой категории.
2. Сколько из выборки требуют реального исправления.
3. Какие 3–5 типовых причин дают большую часть плохих случаев.
4. Похожа ли задача E на:
   - локальный cleanup нескольких карточек;
   - системную проблему translation/fallback producer path;
   - смесь обоих случаев.
5. Какой минимальный следующий IMPLEMENT scope разумен на основании фактов.

## Hard boundaries

Не:
- менять descriptions;
- запускать перевод;
- менять producer logic;
- менять UI;
- менять ranking/Taste;
- делать полный аудит всего каталога;
- менять `CURRENT_TASK.md`.

Если source language невозможно надёжно установить для конкретной карточки в bounded scope — пометь `unknown_source`, не гадай.

## Done when

- проверено 25–30 карточек;
- есть таблица/компактный список `game/key -> category -> краткая причина`;
- посчитано распределение категорий;
- названы главные причины проблемы;
- предложен один ограниченный следующий IMPLEMENT шаг;
- project data не менялась;
- создан компактный report.

## Report format

Сохрани результат в:
`reviews/worker_reports/ru-description-audit-01.md`

Структура:

### Task
Что проверялось и какая выборка использована.

### Verified facts
Короткая таблица/список 25–30 cases и итоговые counts.

### Changes
`none` (кроме report-файла).

### Validation
Какие current payload/source files подтверждают вывод.

### Unresolved
Что осталось неизвестным.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
Один bounded IMPLEMENT scope на основании аудита.

Не копируй большие payloads или длинные описания целиком.

В финальном ответе обязательно назови путь:
`reviews/worker_reports/ru-description-audit-01.md`
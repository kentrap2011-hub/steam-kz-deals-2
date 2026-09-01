# WORKER TASK

Task ID: `detailed-score-ui-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/detailed-score-ui-fix-01.md`

## Goal

Исправить три конкретных дефекта, обнаруженных пользователем на реальном телефоне после `detailed-score-ui-01`, не расширяя scope и не меняя ranking/scoring math без отдельного доказанного основания.

## User feedback from real phone

На опубликованной карточке пользователь увидел:

1. Нажатие на `Детальная оценка` / `подробнее` не сворачивает уже раскрытую детализацию. Блок должен реально работать как toggle: раскрыться и снова свернуться.
2. Строка вида `Вкус · по детальному профилю вкуса` непонятна человеку. Нужна простая подпись, объясняющая смысл показателя без внутренней терминологии.
3. Строка `Длительность · длительность не подтверждена` одновременно показывает `+2/3`, что выглядит противоречиво. Нужно установить, почему при отсутствии подтверждения даётся 2/3, и сделать состояние понятным.

Previous report:
`reviews/worker_reports/detailed-score-ui-01.md`

Перед работой прочитай актуальный `main`, `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `CURRENT_TASK.md`, previous report и только релевантные score UI/scoring contract files.

## What to do

### 1. Toggle bug
- Найди причину, почему disclosure после раскрытия нельзя свернуть обратно.
- Исправь так, чтобы одно и то же пользовательское действие корректно переключало collapsed <-> expanded.
- Сохрани client-only state; никаких production вычислений при нажатии.
- Добавь regression на последовательность: collapsed -> expanded -> collapsed -> expanded.

### 2. Human-readable taste label
- Убери из пользовательской строки формулировку `по детальному профилю вкуса` и аналогичную внутреннюю лексику.
- Подпись должна простыми словами отвечать, что означает этот вклад: совпадение игры с предпочтениями пользователя / насколько она подходит по вкусам.
- Используй уже существующие producer-owned данные. Не изобретай новые Taste категории, thresholds или semantic interpretation во frontend.
- Если без дополнительной producer-информации можно лишь безопасно переименовать сам показатель, сделай именно это и не выдумывай объяснение точнее имеющихся данных.

### 3. Duration contradiction
- Сначала установи, откуда берётся `+2/3` при `duration not confirmed`.
- Если это канонически предусмотренный нейтральный/default score для unknown duration, **не меняй математику**. Перепиши строку так, чтобы пользователь понимал смысл, например как нейтральную оценку из-за отсутствия подтверждённых данных, но только в формулировке, которая точно соответствует существующей логике.
- Если `+2/3` при unknown является реальным producer/scoring defect и противоречит canonical contract, не чинить ranking math в рамках этого UI follow-up. Зафиксировать точный источник и вернуть `needs_fix` с отдельным producer task recommendation.
- Недопустимо оставлять одновременно `не подтверждена` и положительный балл без понятного объяснения.

## Hard boundaries

Не менять без доказанного отдельного дефекта:
- ranking/scoring weights/math;
- Taste semantics/model;
- purchase route/package economics;
- prices/evidence;
- description data path;
- production queues/schedule.

Не трогать параллельный `ru-description-audit-01` и его report.

## Validation

Минимум:
- disclosure toggle работает в обе стороны несколько раз;
- summary state снова скрывает обе detail sections;
- visible copy не содержит непонятной фразы `по детальному профилю вкуса`;
- duration unknown case больше не выглядит как необъяснимое `не подтверждена +2/3`;
- все числовые scores остаются прежними, если canonical logic подтверждает их корректность;
- существующие detailed score, compact purchase и image swipe UI regressions остаются green;
- mobile deploy/visual validation по обычному fast path.

## CURRENT_TASK

Задачу F не считать окончательно закрытой до повторной пользовательской проверки после этого fix. Соседние planned tasks не начинать.

## Done when

- детализация сворачивается обратно;
- Taste-подпись понятна без знания внутреннего проекта;
- duration row либо понятно объясняет корректный neutral/default score, либо доказан отдельный producer bug без самовольной смены math;
- regressions и deploy проходят;
- создан компактный report.

## Report format

Сохрани итог в:
`reviews/worker_reports/detailed-score-ui-fix-01.md`

### Task
Что исправлено.

### Verified facts
Особенно: почему duration unknown получает текущий балл и является ли это корректной canonical логикой.

### Changes
Файлы и краткая причина.

### Validation
Tests/deploy refs.

### Unresolved
`none` либо точный producer/scoring gap.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
Один следующий шаг; если UI исправлен — повторный phone spot-check.

Не копируй большие логи/full diff.

В финальном ответе обязательно назови путь:
`reviews/worker_reports/detailed-score-ui-fix-01.md`
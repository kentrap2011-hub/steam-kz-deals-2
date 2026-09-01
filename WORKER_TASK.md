# WORKER TASK

Task ID: `detailed-score-ui-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/detailed-score-ui-01.md`

## Goal

Сделать раскрываемый блок `Детальная оценка` заметно компактнее и понятнее на мобильном экране, не меняя саму математику рейтинга/оценки.

Пользователь должен быстро понимать две разные вещи:
- насколько игра подходит ему;
- насколько выгодна текущая покупка.

Подробности должны оставаться доступными, но блок не должен выглядеть как длинная стена pills/chips и технических подписей.

## Background

Плановая задача F в актуальном `CURRENT_TASK.md`:
`Redesign detailed score breakdown UI`.

Недавно отдельно завершена компактная выдача purchase options. Не ломай и не переделывай этот блок заново.

Перед работой прочитай актуальные:
- `CHAT_PROTOCOL.md`;
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- relevant UI route/contracts;
- только нужные `web/**` файлы и существующие UI regressions.

## What to do

1. Найди текущий renderer `Детальной оценки` и связанные стили.
2. Сохрани всю реально полезную прозрачность, но перестрой визуальную иерархию:
   - отдельный понятный раздел `Подходит тебе`;
   - отдельный понятный раздел `Выгодность покупки`;
   - внутри использовать компактные строки/группы вместо россыпи высоких pills/chips, где это возможно.
3. Технические внутренние названия преобразовать в пользовательские подписи, не меняя смысл данных.
4. Package/commercial driver, если он уже показывается в score details, должен быть частью секции покупки, а не отдельной длинной стеной текста.
5. Не дублировать содержимое уже существующего компактного блока вариантов покупки без необходимости.
6. Состояние раскрытия остаётся client-only UI state.
7. На мобильном экране блок после раскрытия должен быть визуально спокойнее и существенно короче текущей версии при сохранении содержания.

## Hard boundaries

Не менять:
- ranking/scoring math;
- Taste semantics;
- purchase route selection;
- package valuation/economics;
- prices/evidence;
- producer payload semantics;
- русские описания игр — их параллельно только аудирует другой worker;
- production queue/schedule.

Если выяснится, что часть перегруженности возникает из producer-owned избыточных/дублирующихся полей и без изменения producer schema невозможно выполнить задачу корректно — не придумывай frontend semantics. Зафиксируй точный gap в report.

## Validation

Добавь/обнови проверки минимум для:
- явного разделения `Подходит тебе` и `Выгодность покупки`;
- сохранения всех существенных score components, которые раньше были видимы;
- package/commercial explanation внутри purchase section;
- отсутствия изменения числовых score/rank values;
- mobile collapsed/expanded state;
- заметного уменьшения вертикальной/структурной перегруженности через существующий snapshot/DOM guard или аналогичный deterministic test.

Запусти релевантные UI tests и syntax checks.

Если проект требует cache-busting при изменении клиентских assets — обнови его по существующему пути.

Если штатный visual/deploy workflow запускается автоматически после UI commit — дождись результата и сохрани refs.

## CURRENT_TASK

Можно менять только статус задачи F (`planned` -> `in_progress`/`complete`) по фактическому результату. Не менять статусы соседних задач и не начинать следующую planned-задачу.

## Parallel safety

Параллельно другой worker выполняет read-only аудит русских описаний. Не трогай его task/report и не меняй description producer/data path.

## Done when

- `Детальная оценка` стала заметно компактнее на телефоне;
- personal fit и purchase value разделены и понятны;
- внутренняя терминология заменена понятной пользовательской там, где она видна;
- score/ranking math не изменился;
- UI regressions проходят;
- deploy/visual validation выполнена по правилам проекта;
- создан компактный report.

## Report format

Сохрани итог в:

`reviews/worker_reports/detailed-score-ui-01.md`

Структура:

### Task
Что сделано.

### Verified facts
Что установлено о текущем UI и сохранённых score данных.

### Changes
Какие файлы изменены и зачем.

### Validation
Какие tests/build/deploy прошли, с refs.

### Unresolved
Что осталось. Если нужна проверка пользователя на реальном телефоне — явно напиши.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
Один следующий шаг.

Не копируй большие логи/full diff.

В финальном ответе обязательно назови путь:
`reviews/worker_reports/detailed-score-ui-01.md`
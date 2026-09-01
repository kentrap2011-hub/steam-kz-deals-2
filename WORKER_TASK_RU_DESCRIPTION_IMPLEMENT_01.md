# WORKER TASK — CHAT 1

Task ID: `ru-description-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/ru-description-implement-01.md`
Previous report: `reviews/worker_reports/ru-description-audit-01.md`

## Goal

Исправить системный pipeline русских описаний, выявленный bounded audit-ом, так чтобы production сам обеспечивал нормальные русские описания без ручной обработки карточек в интерактивном ChatGPT-чате.

## Canonical ownership rule

Перед изменениями сверить актуальные:
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `config/execution_ownership_contract.json`
- релевантные description/translation contracts и существующие workflow/stages.

Обязательная граница:
- interactive worker исправляет **код, контракты/валидацию в разрешённом scope и автоматизацию**;
- worker НЕ переводит/не переписывает production-каталог вручную по играм;
- после исправления полный объём определяет и обрабатывает GitHub-owned pipeline;
- если для перевода нужен scheduled ChatGPT runtime, GitHub обязан сам подготовить точный scope/queue/input и принять результаты через canonical artifact interface;
- не создавать новую recurring очередь/стадию/ретрай-логику без явного canonical разрешения.

## Verified diagnosis

Audit `ru-description-audit-01` показал:
- 15/30 sampled cards требуют исправления;
- 14 — literal placeholder из producer fallback;
- 1 — technical/edition blurb вместо содержательного описания;
- UI не является root cause;
- текущий `has_russian_text()` слишком слабый: одного кириллического символа достаточно;
- raw/non-Russian source не сохраняется достаточно хорошо для последующего корректного resolver-а;
- placeholder публикуется напрямую при отсутствии принятого RU short description.

## What to implement

Сделать минимальный producer-owned системный fix, разрешённый каноническими контрактами:

1. Сохранять достаточный исходный Steam short-description/source metadata, чтобы downstream resolver мог отличать:
   - нормальный русский текст;
   - непустой нерусский текст;
   - реально отсутствующий source.
2. Заменить проверку `один кириллический символ = русский текст` на надёжную детерминированную проверку, не принимающую явно нерусский/технический мусор за нормальное русское описание.
3. Не публиковать literal placeholder как нормальное итоговое описание.
4. Не принимать edition/package/technical blurb как meaningful game description без соответствующей проверки.
5. Если уже существует canonical automatic translation path для non-Russian source — корректно подключить/починить именно его.
6. Если такого canonical translation path **нет или ownership не разрешён однозначно**, не изобретать новый recurring semantic stage. Реализовать всё детерминированное, что разрешено, а translation gap вернуть как `needs_user_decision`/`needs_fix` с точным contract gap.
7. Добавить targeted regression/pre-deploy validation, которая гарантирует:
   - placeholder/technical blurb не проходит как готовое описание;
   - нормальный RU source проходит;
   - non-RU source не маскируется как RU;
   - full production catalog не обрабатывается вручную worker-ом.

## Production completion

После code fix не выполнять ручную поштучную обработку игр.

Если существующий GitHub workflow автоматически перестраивает production после разрешённых изменений, можно дать ему отработать и проверить результат.

Если нужен запуск canonical workflow — допустим только существующий GitHub-owned запуск/repair path. Нельзя создавать ad-hoc список игр и вручную заполнять его в этом чате.

Критерий архитектурной готовности: intended owning component должен уметь обработать весь актуальный scope автоматически. Частично вручную заполненные карточки не считаются исправлением.

## Validation

Минимум:
- targeted unit/regression checks;
- relevant producer/pre-deploy validation;
- доказательство, что старый literal placeholder/technical acceptance больше не считается нормальным success;
- если canonical pipeline может выполнить полный rebuild без нового semantic architecture — дождаться/проверить его normal path;
- bounded spot-check допускается только как validation, а не как способ заполнения production data.

## CURRENT_TASK

Можно менять только статус/факты task E, если они действительно подтверждены результатом. Соседние planned tasks не начинать.

## Hard boundaries

Не менять:
- ranking/scoring;
- Taste;
- package economics/purchase route;
- duration pipeline;
- UI кроме строго необходимой compatibility wiring, если producer contract этого требует;
- production scope/queue/retry ownership.

Не переводить вручную 15, 30, 180 или весь каталог игр в worker-чате.

## Done when

Либо:
- producer/validation/существующий canonical translation path исправлены, GitHub-owned production способен сам обработать актуальный scope, проверки green;

либо:
- детерминированная часть исправлена, но доказан конкретный canonical gap для semantic translation и задача возвращена без создания самодельной очереди.

## Report format

Сохрани:
`reviews/worker_reports/ru-description-implement-01.md`

### Task
Что системно исправлялось.

### Verified facts
Кто владеет full-catalog processing и translation path.

### Changes
Только код/контракты/валидация/workflow wiring в разрешённом scope.

### Validation
Tests/workflow/run refs.

### Production handling
Явно написать, что было сделано автоматически GitHub pipeline и что НЕ делалось вручную.

### Unresolved
`none` либо точный contract/translation gap.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
Один шаг.

Не копируй большие логи/full payloads/full diffs.

В финальном ответе обязательно назови report path.
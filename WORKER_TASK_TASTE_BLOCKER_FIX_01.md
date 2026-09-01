# PARALLEL WORKER TASK

Task ID: `taste-ingest-blocker-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/taste-ingest-blocker-fix-01.md`

## Goal

Исправить только подтверждённую несовместимость финальной transactional proof в Taste ingestion: после успешного Taste ingest некоторые keys законно остаются в AI queue для отдельной работы `resolve_base_support_condition`, но текущая proof ошибочно считает это незавершённым Taste ingest.

После исправления повторно запустить canonical ingestion workflow и доказать, что 147 уже полученных Taste results принимаются без повторной semantic оценки, а три retained base-support rows остаются только для своей отдельной downstream работы.

## Background

Диагностика:

`reviews/worker_reports/taste-ingest-blocker-diagnosis-01.md`

Она установила:
- 9 inbox files содержат 147 results и 147 уникальных `result.key`;
- duplicate-key violation нет;
- canonical ingest временно принимает все 147 и увеличивает safe cache hits на 147;
- после rebuild остаются ровно 3 строки для `resolve_base_support_condition` у family с `requires_ai_base_support=true`;
- workflow падает только потому, что proof требует полного исчезновения ingest keys из queue;
- это proof mismatch, а не необходимость повторной Taste оценки.

Перед работой перечитай актуальный `main`, `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `CURRENT_TASK.md`, diagnostic report, ownership contract, `scripts/process_taste_inbox.py`, `scripts/build_pre_ai_chatgpt_payload.py` и соответствующий ingestion workflow.

## Architecture boundary

GitHub остаётся владельцем ingestion, persistence, queue, completeness и downstream orchestration.

Это изменение не должно:
- переносить управление queue в ChatGPT;
- создавать новую очередь/стадию/retry loop;
- менять Taste semantics/model/policy;
- выбирать результаты вручную;
- создавать residual Taste queue;
- повторно оценивать 147 games;
- менять UI/package/ranking code.

Исправляется только proof так, чтобы он соответствовал уже существующей canonical queue semantics.

## What to do

1. Добавь минимальную proof-логику, которая разрешает ingest key оставаться после Taste ingest только если доказано, что:
   - Taste для этого key уже является safe cache hit;
   - текущая queue row требует не Taste evaluation, а `work_required=["resolve_base_support_condition"]`;
   - соответствующая family действительно имеет `requires_ai_base_support=true` по canonical state.
2. Все остальные ingest keys по-прежнему должны исчезнуть из Taste-required queue; ослаблять guard в общем виде нельзя.
3. `ai_queue_decrement_exact`, `queue_file_count_exact` и `all_ingested_keys_removed_from_queue` должны учитывать только разрешённые retained base-support rows, а не просто игнорировать остаток queue.
4. Добавь regression test минимум для двух случаев:
   - законный retained key с `resolve_base_support_condition` проходит proof;
   - обычный ingest key, который незаконно остаётся в queue, всё ещё fail-closed.
5. Не изменяй сами 9 submission files и их Taste results.
6. После tests повторно запусти canonical `.github/workflows/ingest-taste-batch.yml` либо штатный эквивалентный путь, если contracts указывают другой exact invocation.
7. Проверь, что:
   - inbox batch успешно ingested/receipted canonical способом;
   - 147 Taste results становятся persisted safe cache hits;
   - повторная semantic evaluation этих 147 не требуется;
   - три base-support rows остаются ровно как отдельная downstream работа, если canonical builder по-прежнему этого требует;
   - downstream state не получает ручных/выдуманных правок.

## CURRENT_TASK

Можно обновить текущий Taste-ingestion blocker status только по фактическому результату canonical workflow. Не начинать semantic worker вручную и не выбирать следующую product task.

## Parallel safety

Параллельно другой worker меняет UI purchase options. Не трогай `web/**` и его task/report files.

Если неожиданно выяснится, что безопасный fix требует изменения queue semantics, ownership contract или Taste policy, остановись и верни `needs_user_decision` вместо расширения scope.

## Done when

- proof соответствует существующей retained base-support semantics, не ослабляя fail-closed guard для прочих keys;
- regression tests проходят;
- canonical ingestion workflow завершён успешно;
- 147 Taste results не требуют повторной semantic оценки;
- сохранён компактный report.

## Report format

Сохрани результат в:

`reviews/worker_reports/taste-ingest-blocker-fix-01.md`

Структура:

### Task
Что исправлено.

### Verified facts
Что доказано после исправления.

### Changes
Какие файлы изменены и зачем.

### Validation
Tests/workflow/commit/run refs.

### Unresolved
Что осталось. Если всё ingestion-wise закрыто, указать `none` и отдельно назвать штатную downstream base-support работу, если она ещё существует.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
Один следующий шаг.

Не копируй большие логи/JSON/full diff.

В финальном ответе обязательно назови путь:

`reviews/worker_reports/taste-ingest-blocker-fix-01.md`
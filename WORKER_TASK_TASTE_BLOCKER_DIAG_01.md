# PARALLEL WORKER TASK

Task ID: `taste-ingest-blocker-diagnosis-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/taste-ingest-blocker-diagnosis-01.md`

## Goal

Быстро и точно установить, почему текущая GitHub-owned Taste ingestion/rebuild остановилась на 9 существующих submission-файлах с duplicate-key hazard, и подготовить безопасный план следующего шага.

Ничего не исправлять в этой задаче. Не строить вручную остаточную очередь и не подменять GitHub-owned ingestion logic.

## Background

`CURRENT_TASK.md` фиксирует:
- authoritative prepared Taste queue: `147`;
- последний scheduled Taste run оценил/опубликовал `0/0`;
- в `main` уже есть 9 неингестированных submission-файлов;
- duplicate keys между inbox-файлами создают transactional hazard;
- ingestion/downstream completion не доказан.

Это отдельный blocker, не связанный с параллельной UI-задачей compact purchase options.

Перед началом прочитай актуальные:
- `CHAT_PROTOCOL.md`;
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный route в `PROJECT_ROUTES.md`;
- ownership/ingestion contracts, на которые ссылается текущая Taste pipeline;
- только затем конкретные 9 submission/inbox files и нужные checkpoint/state files.

## What to determine

1. Какие именно 9 submission-файлов сейчас не ингестированы.
2. Какие exact keys дублируются:
   - ключ;
   - в каких файлах он встречается;
   - одинаковы ли payload/results для дублей или они конфликтуют по содержимому.
3. Почему canonical ingestion не может безопасно продолжить:
   - какой guard/contract её останавливает;
   - на каком шаге это происходит;
   - является ли это ожидаемым fail-closed поведением.
4. Определи минимальный безопасный способ устранения blocker-а, но **не выполняй его**.
5. Установи, можно ли устранить blocker чисто GitHub-side ingestion/rebuild без повторной semantic оценки этих игр.
6. Проверь, не существует ли уже canonical recovery/ingestion path, который просто не был выполнен.

## Hard boundaries

Не:
- изменять submission/inbox files;
- удалять дубли;
- выбирать «правильный» результат без contract evidence;
- создавать residual/manual Taste queue;
- повторно оценивать игры;
- менять Taste policy/model;
- запускать новый semantic backlog;
- менять UI/package/ranking files;
- менять `CURRENT_TASK.md`.

Если дубли конфликтуют по содержанию и canonical contract не говорит, какой имеет приоритет, статус должен быть `needs_user_decision` или `blocked`, а не догадка.

## Bounded work

Это должна быть короткая диагностика. После того как найдены:
- 9 файлов;
- duplicate keys;
- canonical guard;
- безопасный recovery path;

не продолжай широкое исследование соседних Taste тем.

## Done when

- перечислены все затронутые файлы;
- перечислены все duplicate keys и характер дублей;
- понятна точная причина блокировки;
- известен один минимальный безопасный следующий шаг;
- никаких project state/semantic изменений не сделано;
- создан компактный report.

## Report format

Сохрани результат в:

`reviews/worker_reports/taste-ingest-blocker-diagnosis-01.md`

Структура:

### Task
Что проверялось.

### Verified facts
Какие файлы/ключи/guard фактически найдены.

### Changes
`none` (кроме report-файла).

### Validation
Какие canonical contracts/state/files подтверждают вывод.

### Unresolved
Что нельзя решить автоматически/однозначно.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
Один конкретный безопасный следующий шаг.

Не копируй большие JSON или полные submission payloads. Для каждого дубля достаточно key + filenames + `identical/conflicting`.

В финальном ответе обязательно назови путь:

`reviews/worker_reports/taste-ingest-blocker-diagnosis-01.md`
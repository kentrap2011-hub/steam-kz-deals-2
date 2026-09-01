# PARALLEL WORKER TASK

Task ID: `duration-data-diagnosis-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/duration-data-diagnosis-01.md`

## Goal

Установить, почему в видимой рекомендованной карточке `duration_preference_band = unknown` и UI вынужден показывать neutral/default `2/3`, хотя пользователь ожидает подтверждённую длительность для видимых рекомендаций.

Не исправлять систему в этой задаче. Сначала определить реальную причину и масштаб.

## User requirement

Пользователь подтвердил, что UI `Детальной оценки` после fix теперь работает нормально, но считает состояние `длительность не подтверждена` нежелательным: для видимой recommendation card длительность должна быть подтверждена всегда, когда её можно надёжно получить из канонических источников.

Neutral `unknown = 2/3` может оставаться только fail-safe/default поведением, а не нормальным способом заполнения видимых карточек при доступных данных.

## Background

Previous UI report:
`reviews/worker_reports/detailed-score-user-fixes-01.md`

Он подтвердил, что `unknown = 2/3` является текущей canonical scoring policy и не является UI/scoring bug. Новая задача — не менять этот fallback, а установить, почему duration data вообще оказалось `unknown`.

Перед работой прочитай актуальные:
- `CHAT_PROTOCOL.md`;
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- `PROJECT_ROUTES.md`;
- relevant duration/scoring/data contracts;
- текущий published/precomputed recommendation payload/state;
- только необходимые duration-related producer/source files/scripts.

## Scope

Проверить ограниченно:

1. Точный current visible case, где duration = unknown (если key/title можно однозначно восстановить из current ranked/published payload по показанным score components; если таких несколько — перечислить кандидатов и не гадать).
2. Минимум top-30 текущих видимых/приоритетных recommendation cards: сколько имеют confirmed duration и сколько `unknown`.
3. Для каждого `unknown` в этой выборке установить по возможности:
   - какой duration source должен был его заполнять;
   - есть ли source data фактически;
   - где именно данные теряются/не извлекаются/не доходят до producer;
   - это source absence, ingestion gap, mapping issue, stale cache, validation failure или намеренное contract rule.
4. Установить, является ли проблема единичной или системной.
5. Найти canonical ownership: какой GitHub-owned stage обязан делать duration enrichment/persistence.
6. Определить один минимальный безопасный IMPLEMENT scope, который устранит реальные `unknown` при доступных данных.

## Important distinctions

Разделяй:
- **реально неизвестно** — надёжного source data нет;
- **данные существуют, но pipeline не подхватывает** — defect;
- **данные есть, но mapping/normalization не проходит** — defect;
- **данные устарели/не были обновлены** — refresh/enrichment defect;
- **контракт сознательно запрещает использовать имеющийся источник** — policy boundary, не менять без решения.

Не считать сам canonical fallback `unknown = 2/3` причиной проблемы. Это только последняя страховка.

## Hard boundaries

Не:
- менять scoring math/weights;
- менять `unknown = 2/3`;
- вручную вписывать duration для отдельных игр;
- делать внешний semantic backlog в ChatGPT;
- создавать новую recurring queue/stage;
- менять Taste/package/UI/descriptions;
- менять `CURRENT_TASK.md`;
- расширять аудит за пределы top-30 + только необходимые source checks для найденных unknown cases.

Если для получения duration нужен внешний источник/API, только установи существующий canonical path и его состояние. Не создавай новый механизм без contract evidence.

## Done when

- найден/локализован current unknown-duration visible case либо доказано, почему его нельзя однозначно сопоставить;
- top-30 посчитаны по confirmed vs unknown duration;
- для каждого unknown дана причина или честный `unresolved`;
- установлен owner/stage, который должен исправлять такие случаи;
- определён один bounded IMPLEMENT next step;
- ничего кроме report не изменено.

## Report format

Сохрани:
`reviews/worker_reports/duration-data-diagnosis-01.md`

### Task
Что проверено.

### Verified facts
- current visible case;
- top-30 confirmed/unknown counts;
- компактная таблица unknown cases: key/title -> expected source -> actual state -> cause.

### Changes
`none` кроме report.

### Validation
Какие canonical files/contracts/payloads подтверждают вывод.

### Unresolved
Что реально осталось неизвестным.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
Один bounded IMPLEMENT scope.

Не копируй большие payloads/logs.

В финальном ответе обязательно назови путь:
`reviews/worker_reports/duration-data-diagnosis-01.md`
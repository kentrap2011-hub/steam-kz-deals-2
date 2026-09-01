# WORKER TASK — CHAT 2

Task ID: `duration-provider-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/duration-provider-recon-01.md`
Previous reports:
- `reviews/worker_reports/duration-data-diagnosis-01.md`
- `reviews/worker_reports/duration-source-recon-01.md`

## Goal

Сравнить пригодные authoritative источники/провайдеры данных о длительности прохождения на уровне архитектуры проекта и подготовить обоснованную рекомендацию для будущего canonical duration contract.

Это НЕ задача на получение длительности конкретных игр и НЕ задача на изменение кода.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `config/final_ranking_policy.json`
- `reviews/worker_reports/duration-data-diagnosis-01.md`
- `reviews/worker_reports/duration-source-recon-01.md`

## Architecture preflight

Соблюдать `config/execution_ownership_contract.json`:
- GitHub владеет scope/order/retry/completeness/cache/ingestion;
- scheduled ChatGPT может только получать внешние факты для GitHub-prepared exact scope, если это явно закрепит будущий contract;
- interactive worker не создаёт production queue и не собирает каталог вручную.

## What to investigate

Сравнить небольшой набор реально пригодных классов/провайдеров duration data (обычно 2–4 наиболее жизнеспособных варианта), достаточный для принятия архитектурного решения.

Для каждого варианта установить:
1. Что именно измеряется: main story / main+extras / completionist / single estimate / community average и насколько это соответствует нашему `estimated_duration_hours`.
2. Покрытие Steam-каталога и идентификация игр: Steam appid напрямую или через title/ID mapping.
3. Есть ли официальный/стабильный API, публичный endpoint или иной автоматизируемый access path.
4. Может ли GitHub Actions получать данные напрямую без браузерной/anti-bot зависимости.
5. Если прямой GitHub access ненадёжен — может ли источник разумно использоваться только через GitHub-prepared scheduled ChatGPT external-fact worker.
6. Rate limits, auth/API key, pricing/free-tier, licensing/ToS/redistribution constraints, насколько это можно установить из доступной публичной документации.
7. Stability/maintenance risk.
8. Как обновлять данные: reasonable freshness для game duration (например, при первом появлении и редком refresh), без придумывания production schedule — только рекомендация semantics.
9. Confidence/provenance: какие поля имеет смысл сохранять в canonical record.
10. Основные плюсы/минусы для именно нашего проекта.

## Important

Можно пользоваться web/public documentation для исследования провайдеров и API, но:
- не искать длительность Fable, Psychonauts или других конкретных игр;
- не делать catalog sampling;
- не собирать реальные duration values;
- не создавать код, cache, queue, workflow или contract в этой задаче.

## Decision output

В report должна быть:
- компактная сравнительная таблица;
- **один recommended primary option**;
- при необходимости один fallback option;
- ясный вывод: `GitHub-direct` или `scheduled ChatGPT external fact worker` предпочтителен для recommended option;
- какие существенные риски/условия должны попасть в будущий contract.

Если нет достаточно надёжного/легального/автоматизируемого варианта — так и написать, не придумывая источник.

## Hard boundaries

Не:
- менять repository code/config/contracts;
- делать per-game duration lookup;
- выполнять массовую обработку;
- выбирать production scope/queue/retries;
- менять scoring или `unknown = 2/3`;
- менять UI/Taste/descriptions/ranking weights.

## Done when

- сравнены жизнеспособные provider options;
- recommendation основана на проверяемых фактах, а не предположениях;
- понятно, какой executor class подходит;
- понятно, какие поля/ограничения должен зафиксировать следующий canonical contract step;
- никаких production data не обработано.

## Report format

Сохрани:
`reviews/worker_reports/duration-provider-recon-01.md`

### Task
Что исследовалось.

### Verified facts
Краткая сравнительная таблица провайдеров.

### Recommendation
Primary option + почему.

### Executor
`GitHub-direct`, `scheduled ChatGPT`, либо `undecided` с причиной.

### Contract requirements
Что обязательно закрепить перед IMPLEMENT.

### Changes
`none` кроме report.

### Validation
Ссылки/названия официальных документов и canonical repo contracts; не копировать длинные страницы.

### Unresolved
Только реальные неизвестные/риски.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
Один следующий шаг: contract task либо user decision.

В финальном ответе обязательно назови report path и commit ref.
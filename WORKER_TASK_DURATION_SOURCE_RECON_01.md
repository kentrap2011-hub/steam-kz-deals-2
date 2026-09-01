# WORKER TASK — CHAT 2

Task ID: `duration-source-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/duration-source-recon-01.md`
Previous report: `reviews/worker_reports/duration-data-diagnosis-01.md`

## Goal

Не искать длительность по отдельным играм. Установить только системно, какой canonical source/path уже существует или разрешён проектом для normalized duration data и какой GitHub-owned stage должен его собирать/хранить до final ranking.

## Why this task exists

Предыдущая диагностика доказала, что текущий final visual producer извлекает длительность opportunistically из `projection.short_description` / `game.summary`, поэтому нормальные карточки могут получать `duration_preference_band = unknown`.

Нельзя сразу внедрять новый источник, очередь или external lookup без проверки canonical ownership/contracts.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md` при необходимости для rationale
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `config/final_ranking_policy.json`
- все явно релевантные duration/enrichment/data contracts и существующие pipeline files/routes
- `reviews/worker_reports/duration-data-diagnosis-01.md`

## Questions to answer

1. Есть ли уже в репозитории canonical structured duration field/cache/source, который должен использовать final ranking, но сейчас не подключён или теряется?
2. Есть ли существующий GitHub-accessible источник/API/path, уже разрешённый контрактами для получения duration без ChatGPT?
3. Есть ли существующий GitHub-prepared external/semantic runtime path, которому канонически разрешено получать duration, если GitHub сам не может?
4. Какой конкретный stage должен владеть:
   - source collection;
   - normalization;
   - persistence/cache;
   - передачей duration в final visual/ranking?
5. Если источника/ownership ещё нет, какой именно canonical contract gap мешает реализации?

## Hard boundaries

Не:
- проверять top-30, top-N или весь каталог по играм;
- искать HowLongToBeat/SteamDB/Google/веб-источники для конкретных игр;
- вручную вписывать duration values;
- менять код;
- создавать новую queue/stage/retry loop;
- менять scoring math или `unknown = 2/3`;
- менять UI/Taste/descriptions/package economics;
- менять `CURRENT_TASK.md`.

Это только архитектурная/source-path диагностика по существующему коду, контрактам и данным проекта.

## Done when

- назван существующий canonical duration source/path и owner, если он есть;
- либо доказано, что такого source/path сейчас нет;
- указано, можно ли следующий IMPLEMENT сделать без изменения architecture contract;
- если можно — один минимальный IMPLEMENT scope;
- если нельзя — точный contract/user decision gap, без самодельного решения.

## Report

Сохрани:
`reviews/worker_reports/duration-source-recon-01.md`

### Task
Что системно проверено.

### Verified facts
Canonical duration fields/sources/stages и ownership.

### Changes
`none` кроме report.

### Validation
Какие contracts/routes/scripts подтверждают вывод.

### Unresolved
Только реальные недоказанные места.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
Один bounded IMPLEMENT либо одно contract/user decision.

Не копируй большие логи или payloads.

В финальном ответе обязательно назови report path и commit ref.
# WORKER TASK — PROGRESSIVE PERSONALIZED DEALS PASS 1 SCHEDULED RUNTIME CONFIGURE 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repository target неоднозначен — остановись и сначала переключись на `kentrap2011-hub/steam-kz-deals-2`.

Task ID: `progressive-personalized-deals-pass1-scheduled-runtime-configure-01`
Mode: `IMPLEMENT / RUNTIME CONFIGURE`

User authorization:
- Director сообщил, что после runtime audit нужен отдельный bounded CONFIGURE;
- пользователь явно ответил: `Отдай задачу чату 1`;
- это разрешает только bounded runtime configuration, описанную ниже;
- это НЕ разрешает `Run now`, реальный PASS 1 semantic attempt, backlog drain, PASS 2 или изменение GitHub-owned control-plane semantics.

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.

Затем полностью открой этот task-файл из `main`.

После этого используй только минимально нужные canonical sources:
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- `reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-worker-entrypoint-audit-01.md`
- релевантный участок `DIRECTOR_TASK_BOARD.md`
- при необходимости только релевантный route/decision, найденный через `PROJECT_ROUTES.md` / `PROJECT_DECISIONS.md`.

Не восстанавливай проект из истории чатов и не исследуй старые automation-задачи шире необходимого.

## Confirmed runtime observation from Director/user UI

Owner-scope Scheduled Tasks UI был проверен пользователем 2026-09-21:

- в фильтре active видна проектная active task `Taste Steam Review Dossier`;
- отдельная active task `Progressive PASS 1` не наблюдается;
- среди старых completed/paused задач видны исторические `Taste Semantic Producer`, `Nightly Production Runtime` и другие;
- старое имя задачи само по себе НЕ доказывает, что она является текущим Progressive PASS 1 runtime;
- audit-report классифицировал прежнюю формулировку `existing authorized Scheduled PASS 1 worker` как `unproven`.

Не трактуй старую paused/completed задачу как текущего owner-а только по названию.

## Objective

Установить корректный Scheduled ChatGPT runtime binding для Progressive PASS 1, сохранив GitHub единственным control-plane owner.

В конце должно быть доказано одно из двух:

A. существует и безопасно сконфигурирован ровно один runtime entrypoint, который может выполнять current `config/progressive_pass1_worker_prompt.md`, при этом он оставлен НЕ ЗАПУЩЕННЫМ до отдельного live-acceptance разрешения;

или

B. canonical architecture не позволяет безопасно выполнить configuration без отдельного user/contract decision; тогда ничего runtime-changing не делать и вернуть точный blocker.

## Mandatory architecture preflight

До любой runtime write явно проверь:

1. GitHub остаётся владельцем scope/order/attempt/retry/completeness/validation/persistence.
2. Scheduled ChatGPT остаётся только bounded semantic data plane.
3. `config/execution_ownership_contract.json` фиксирует `new_independent_scheduler_created=false` для Phase B implementation.
4. `config/daily_execution_contract.json` запрещает новую отдельную recurring-stage без прямого canonical основания.
5. Создание, переиспользование или rebinding Scheduled Task не должно создавать новый queue/retry/completeness owner.
6. Cadence/timezone нельзя придумывать из удобства. Используй только доказанный canonical schedule/role. Если его нельзя однозначно вывести из canonical state — STOP before write с `needs_user_decision`.

Если создание отдельной новой recurring task означало бы архитектурно новую stage, не создавай её. Если canonical contracts однозначно разрешают именно один Progressive PASS 1 Scheduled data-plane entrypoint как реализацию уже существующей canonical stage, это нужно доказать в report до создания.

## Runtime inventory / identity check

Перед mutation выполни один bounded read-only owner-scope inventory check, если interface доступен.

Нужно установить для возможных кандидатов только:
- title;
- task id;
- enabled/paused/completed state;
- schedule/timezone;
- effective prompt/instruction or canonical-loader reference.

Не читай unrelated personal tasks.

Особенно:
- `Taste Steam Review Dossier` не является PASS 1 runtime;
- `Taste Semantic Producer` не является PASS 1 runtime автоматически;
- `Nightly Production Runtime` не является PASS 1 runtime автоматически.

Если exact compatible entrypoint уже существует — не создавай duplicate.

## Allowed configuration

Только если architecture preflight и identity доказаны:

- переиспользовать/перенастроить один доказанный canonical semantic runtime entrypoint ИЛИ создать ровно один entrypoint, если это прямо разрешено current canonical architecture;
- effective instruction должен быть thin loader на latest `main`, а не frozen copy старого prompt:
  - repo `kentrap2011-hub/steam-kz-deals-2`;
  - `main`;
  - на каждом invocation читать current `config/progressive_pass1_worker_prompt.md`;
  - соблюдать `config/progressive_pass1_contract.json` и `config/execution_ownership_contract.json`;
  - работать только с GitHub-prepared `data/production/pre_ai/progressive_pass1_work.json`;
  - не выбирать scope/order самостоятельно;
  - не retry PASS 1;
  - не начинать PASS 2;
  - не требовать Dossier/Russian review универсально;
  - писать только exact create-only per-item result artifact по manifest.
- runtime после configuration должен быть оставлен paused/disabled до отдельного Director live-acceptance шага, если platform это позволяет.
- если platform нельзя безопасно сконфигурировать без риска автоматического production-run до проверки — не делай mutation, верни blocker.

## Strict prohibitions

Не выполнять:
- `Run now`;
- Tower Dominion semantic analysis;
- создание PASS 1 result artifact;
- ingest PASS 1 result;
- consume attempt;
- second item;
- backlog drain;
- PASS 2;
- изменение PASS 1 business semantics;
- изменение GitHub queue/order/retry/completeness ownership;
- resurrection/reuse старой task только из-за похожего имени;
- создание второго competing semantic scheduler.

## Validation

После допустимой configuration read-only перечитай actual task definition и докажи:
- exact task identity;
- enabled/paused state;
- schedule/timezone;
- effective instruction/binding;
- current repo/main loader;
- no `Run now` / no production result;
- no duplicate Progressive PASS 1 task;
- no conflict with Taste Dossier;
- GitHub control plane unchanged;
- PASS 2 remains inactive.

Не считать config complete только по намерению или по repo prompt.

## Durable report

Обязательно создать и commit в `main`:

`reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-runtime-configure-01.md`

Report должен быть компактным и содержать:
1. Task.
2. Architecture preflight result.
3. Runtime inventory fact.
4. Changes.
5. Validation.
6. Unresolved.
7. Status.
8. Recommended next step — ровно один.
9. Exact task id / schedule / commit refs, достаточные для Director.
10. Efficiency / reusable lesson.

Allowed final statuses:
- `complete_configured_paused_ready_for_live_acceptance`
- `complete_existing_compatible_runtime_confirmed`
- `needs_user_decision`
- `blocked_external`
- `needs_fix`

После commit перечитай exact report из `main` и только затем заверши задачу.

## CURRENT_TASK.md

Не уничтожай другую активную работу.
Меняй `CURRENT_TASK.md` только если это требуется актуальным CHAT_PROTOCOL для реально исполняемой подзадачи, и при завершении оставь его согласованным с фактическим статусом.

## Completion boundary

Эта задача заканчивается на корректно доказанной runtime configuration / blocker.

Даже при успешной configuration:
- НЕ запускать worker;
- НЕ делать live acceptance;
- НЕ начинать PASS 2.

Следующий шаг выбирает Director после чтения durable report.

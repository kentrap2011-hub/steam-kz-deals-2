# WORKER TASK — PROGRESSIVE PERSONALIZED DEALS PASS 1 SCHEDULED WORKER ENTRYPOINT AUDIT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repository target неоднозначен — остановись и сначала переключись на `kentrap2011-hub/steam-kz-deals-2`.

Task ID: `progressive-personalized-deals-pass1-scheduled-worker-entrypoint-audit-01`
Mode: `READ-ONLY / ENTRYPOINT + OWNERSHIP AUDIT`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.

Затем открой этот task-файл и зафиксируй его checklist до широкого поиска.

Минимальные обязательные источники:
- `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PHASE_B_PASS1_IMPLEMENT_01.md`
- `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PHASE_B_PASS1_LIVE_ACCEPTANCE_01.md`
- `reviews/worker_reports/progressive-personalized-deals-phase-b-pass1-implement-01.md`
- `reviews/worker_reports/progressive-personalized-deals-phase-b-pass1-live-acceptance-01.md`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- `config/execution_ownership_contract.json`
- `PROJECT_DECISIONS.md`
- релевантный блок `DIRECTOR_TASK_BOARD.md`.

Если нужно понять маршрут/entrypoint, прочитай только релевантный раздел `PROJECT_ROUTES.md` и при наличии соответствующего operational trigger — только релевантную запись `KNOWN_WORKER_PITFALLS.md`.

## Причина аудита

Текущий live-acceptance report остановился как `blocked_external` и сослался на отсутствие интерфейса запуска **existing authorized Scheduled PASS 1 worker**.

Нужно проверить, является ли это утверждение фактически и архитектурно корректным.

Критический вопрос:

> Существует ли реально отдельный Scheduled ChatGPT worker для Progressive PASS 1, уже настроенный на текущий canonical PASS 1 prompt/manifest, или repository implementation создал только contract/prompt/control-plane и ошибочно предположил существование runtime entrypoint?

## Главная цель

Дать Director однозначный read-only ответ, что именно существует сейчас на трёх разных уровнях:

1. **Repository contract** — canonical PASS 1 worker contract/prompt/manifest.
2. **Runtime entrypoint** — реальная Scheduled Task / automation / иной авторизованный ChatGPT execution entrypoint.
3. **Callable interface** — можно ли этот entrypoint действительно вызвать сейчас для одного bounded live acceptance.

Не смешивать эти три уровня.

## Что проверить

### A. Canonical intent

Установить по task/contracts/decisions:

- должен ли Phase B был:
  - только подготовить worker contract/prompt и GitHub control plane;
  - переиспользовать уже существующий Scheduled worker;
  - перенастроить существующий Scheduled worker;
  - или создать/активировать отдельный Scheduled PASS 1 worker;
- есть ли в canonical документах доказательство, что такой runtime worker **уже существовал** до Phase B;
- где впервые появляется формулировка `existing authorized Scheduled PASS 1 worker`;
- является ли она доказанным фактом или неподтверждённым предположением.

### B. Actual Scheduled Task inventory

Если среда worker-чата позволяет read-only увидеть Scheduled Tasks / automations:

- перечислить только релевантные task titles/ids/state/schedule/prompt purpose;
- проверить, существует ли task, назначение которого реально соответствует `config/progressive_pass1_worker_prompt.md`;
- отдельно проверить существующие:
  - `Taste Steam Review Dossier`;
  - `Taste Semantic Producer`;
- установить, можно ли хотя бы один из них считать PASS 1 worker **без нарушения canonical ownership/prompt semantics**.

Не запускать, не изменять, не включать и не перенастраивать никакую Scheduled Task.

Если inventory недоступен — явно зафиксировать эту границу observability и не делать вывод "worker exists" только из repo prompt-файла.

### C. Prompt / binding compatibility

Если реальный Scheduled entrypoint найден и его prompt/config можно прочитать:

- сравнить его назначение с `config/progressive_pass1_worker_prompt.md`;
- проверить, что он:
  - читает GitHub-owned `data/production/pre_ai/progressive_pass1_work.json`;
  - не выбирает scope/order;
  - пишет только exact create-only per-item result artifact;
  - не запускает PASS 2;
  - не делает retry;
  - не использует Dossier как universal PASS 1 prerequisite;
  - не является старым one-game canary или dossier worker под другим названием.

Не требовать буквального совпадения текста, если canonical entrypoint специально загружает prompt из repo; но это должно быть доказано.

### D. Execution surface

Определить отдельно:

- worker существует, но текущий chat/tool не умеет его запускать;
- worker существует и может быть запущен пользователем через UI / Run now;
- worker не существует и его сначала надо создать/настроить;
- worker существует, но связан с неправильным prompt/role;
- недостаточно наблюдаемости, чтобы классифицировать.

### E. Architecture ownership

Проверить, не возникает ли новый owner при предлагаемом next step.

Инварианты:
- GitHub остаётся control plane;
- Scheduled ChatGPT — только bounded semantic data plane;
- interactive ChatGPT не становится production backlog worker;
- не создавать второй competing scheduler/retry owner;
- PASS 2 остаётся выключен.

## Обязательные сравнения

Отдельной таблицей сравни:

- Progressive PASS 1 worker contract;
- Taste Semantic Producer;
- Taste Steam Review Dossier.

Для каждого:
- purpose;
- canonical input;
- semantic depth;
- output transport;
- retry/backlog ownership;
- можно ли законно переиспользовать для PASS 1;
- если нельзя — точная причина.

## Ключевой finding, который нужно разрешить

Проверь гипотезу:

> Phase B repository implementation создал новый PASS 1 worker **contract**, но не создал actual Scheduled Task entrypoint; затем live-acceptance task/Board назвали этот entrypoint "existing authorized" без доказательства его фактического существования.

Не подтверждай и не опровергай гипотезу заранее. Нужны доказательства.

## Запреты

Не:
- запускай Scheduled ChatGPT;
- не нажимай Run now;
- не анализируй Tower Dominion семантически;
- не создавай PASS 1 result artifact;
- не consume PASS 1 attempt;
- не запускай второй item;
- не запускай backlog drain;
- не начинай PASS 2;
- не меняй prompt/contracts/workflows/source;
- не создавай и не перенастраивай automation;
- не исправляй найденный дефект в этой задаче;
- не трогай другой repository.

## Acceptance checks

AUDIT-01 — repository contract и actual Scheduled entrypoint различены явно.

AUDIT-02 — установлено, требовал ли canonical Phase B реальный runtime worker и кто должен был его обеспечить.

AUDIT-03 — утверждение `existing authorized Scheduled PASS 1 worker` классифицировано как proven / disproven / unproven.

AUDIT-04 — если Scheduled inventory доступен, релевантные реальные tasks проверены read-only.

AUDIT-05 — `Taste Semantic Producer` не считается PASS 1 worker только из-за сходства semantic role.

AUDIT-06 — `Taste Steam Review Dossier` не считается PASS 1 worker только из-за Scheduled ChatGPT execution.

AUDIT-07 — если найден настоящий PASS 1 task, доказана его prompt/input/output compatibility.

AUDIT-08 — если task отсутствует, указано, какой exact setup gap существует, без реализации.

AUDIT-09 — live acceptance blocker переклассифицирован точно: missing execution interface vs missing runtime entrypoint vs wrong binding vs insufficient observability.

AUDIT-10 — recommended next step не создаёт нового control-plane owner и прошёл architecture preflight.

AUDIT-11 — никаких production attempts/state changes не произошло.

AUDIT-12 — durable report committed и reread из `main`.

## Durable report

Запиши:

`reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-worker-entrypoint-audit-01.md`

Обязательные разделы:
1. Task / repo / mode.
2. Sources read.
3. Canonical Phase B intent.
4. Repository worker contract vs runtime entrypoint vs callable interface.
5. Actual Scheduled Task inventory / observability boundary.
6. PASS 1 vs Taste Semantic Producer vs Taste Steam Review Dossier comparison.
7. Origin/status of the phrase `existing authorized Scheduled PASS 1 worker`.
8. Runtime binding/prompt compatibility.
9. Correct blocker classification.
10. Architecture/ownership preflight.
11. AUDIT-01..12.
12. Findings.
13. Unresolved.
14. Status.
15. Exactly one recommended next step.
16. Exact refs.
17. Efficiency / reusable lesson.

Allowed statuses:
- `complete_existing_worker_identified`
- `complete_worker_missing_setup_required`
- `complete_wrong_runtime_binding_identified`
- `complete_insufficient_observability`
- `needs_fix`
- `needs_user_decision`

## Completion rule

Не исправляй проблему.

Если настоящий PASS 1 Scheduled worker существует и совместим — укажи exact user/runtime action, который нужен для **одного** bounded live acceptance, но не выполняй его.

Если worker отсутствует/не настроен — вернись к Director с exact setup gap. Следующая задача должна быть отдельным bounded IMPLEMENT/CONFIGURE только после Director/user authorization.

Если нельзя доказать наличие/отсутствие — верни `complete_insufficient_observability` с точным способом получить недостающий факт.

После durable report остановись и вернись к Director.

# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины, но эта board новее и выигрывает при расхождении статусов.

## Ключевые правила

1. По умолчанию держать два worker-чата занятыми параллельно, если задачи независимы и не конфликтуют.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
3. Worker-чат удалять только после durable report + Director decision + ближайших user checks.
4. В каждой копируемой worker-команде первая строка явно начинается с `=== ЧАТ N ===`.
5. Номер принадлежит worker-слоту.
6. Не запускать параллельно конфликтующие Taste/ranking IMPLEMENT.
7. Taste Reviewer recommendations имеют VERY HIGH USER PRIORITY.
8. Automation migration может идти параллельно backlog, но сначала только shadow/read-only safety phases.

## Review checkpoint

Latest System Audit: `reviews/system_audits/giveaway-cache-post-incident-audit-01.md`
Result: accepted.
`system_audit_due: false`.

## Active

### ЧАТ 1 — VERY HIGH PRIORITY Taste IMPLEMENT 1

Task:
`WORKER_TASK_TASTE_EVIDENCE_STATE_AND_CONFIDENCE_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`
Status: `running_or_ready_in_existing_chat_1`.

### ЧАТ 2 — Phase 1 orchestration shadow observer IMPLEMENT

Recon complete:
`reviews/worker_reports/autonomous-director-orchestration-recon-01.md`
Status: `complete`.
Feasibility: cloud-first without always-on home PC is feasible; ordinary worker chats are not a reliable automatable substrate and should later be replaced by GitHub-hosted cloud worker jobs using the official Codex Action / `codex exec` path.

Current implementation task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_SHADOW_OBSERVER_IMPLEMENT_01.md`
Task ID: `director-orchestration-shadow-observer-implement-01`
Mode: `IMPLEMENT`
Expected report:
`reviews/worker_reports/director-orchestration-shadow-observer-implement-01.md`
Status: `ready_continue_existing_chat_2`.

Phase 1 scope only:
- machine-readable orchestration contract/state;
- current Chat 1 represented as external/manual occupied slot;
- deterministic priority/dependency/conflict planner;
- max 2 logical slots;
- GitHub Actions shadow workflow producing `shadow-plan.json` artifact;
- no OpenAI/Codex call;
- no worker dispatch;
- no product task mutation;
- no secret required.

If Phase 1 repeatedly matches Director decisions, next phase may add automatic READ-ONLY RECON/AUDIT cloud workers.

## Steam access policy

User approved:
- Steam Web API key for read-only `GetOwnedGames`: yes;
- authenticated Steam Store session for personalized Complete The Set payable price: no for now.
Never ask for secret values in ordinary chat/report/task files.

## Taste sequence after current step

1. evidence state/confidence/reconsideration semantics;
2. play role + relative start priority;
3. reconsideration commercial bridge + wishlist-good-deal override.

Independent Taste Review required at the chosen material acceptance boundary.

## Queued

- DLC ownership eligibility IMPLEMENT: policy-approved in principle, pending proper GitHub secret provisioning; no Steam session.
- Personalized Complete The Set actual payable price: blocked by no-session decision.
- `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Russian-language availability ranking factor.
- YouTube review selection.
- modern Windows compatibility evidence.
- semantic/Russian-description completion remains blocked on existing scheduled semantic runtime evidence; do not create another scheduler.

## Next decision

1. Keep Chat 1 on Taste IMPLEMENT 1.
2. Continue existing Chat 2 with shadow observer IMPLEMENT.
3. Read both exact reports before advancing either product semantics or automation phase.
4. Do not add OpenAI API key until Phase 1 shadow safety has been proven.

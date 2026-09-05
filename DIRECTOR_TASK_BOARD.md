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
8. Autonomous IMPLEMENT остаётся запрещён до отдельного разрешения.
9. User will not pay additional money for OpenAI API usage or another new automation service unless explicitly reversed. Future automation work must target zero incremental paid cost.

## Review checkpoint

Latest System Audit:
`reviews/system_audits/director-orchestration-phase2a-audit-01.md`
Status: `PASS`.
Closure: `accepted`.
`system_audit_due: false`.

## ЧАТ 1 — Taste step 3 full bounded self-recheck

Task:
`WORKER_TASK_RECONSIDERATION_COMMERCIAL_BRIDGE_AND_WISHLIST_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`
Status: `continue_existing_chat_1_full_bounded_self_recheck`.

Chat 1 independently verifies the whole bounded Step 3 scope from current GitHub truth, fixes only real in-scope defects, cleans temporary one-shot machinery if appropriate, and saves the exact durable report. Independent Taste Review starts only after Director consumes that report.

## ЧАТ 2 — zero-incremental-cost Director automation recon

Task:
`WORKER_TASK_ZERO_INCREMENTAL_COST_DIRECTOR_AUTOMATION_RECON_01.md`
Task ID: `zero-incremental-cost-director-automation-recon-01`
Mode: `READ-ONLY / RECON`
Expected report:
`reviews/worker_reports/zero-incremental-cost-director-automation-recon-01.md`
Priority: `VERY_HIGH_INFRASTRUCTURE_PRIORITY`.
Status: `ready_new_chat_2`.

Goal:
- determine whether materially similar Director/worker automation is currently possible without any additional paid API/service cost;
- verify current ChatGPT Plus/Codex, GitHub-native/model and reputable free-cloud options from current official sources;
- distinguish truly zero-cost, limited free-tier, separately paid and non-programmable options;
- map which orchestration pieces can be automated deterministically for free;
- if full autonomous LLM execution is not genuinely zero-cost, design the best Android-first semi-automated fallback and quantify residual user actions per worker cycle;
- no implementation, secrets, billing, workflow or product changes.

## Phase 2B paid API route — stopped

Durable report:
`reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`
Outcome: real pinned Codex worker reached OpenAI Responses API but was blocked by zero API credits. Security failed closed: no automatic Epic report, no unauthorized write, no second task, no autonomous IMPLEMENT.

User will not fund separately billed OpenAI API. Do not retry this route or ask for API credits.

## Taste sequence

1. evidence state/confidence/reconsideration — complete internally;
2. play role + relative start priority — complete internally;
3. commercial reconsideration/wishlist bridge — self-recheck + durable closeout pending;
4. independent current Taste Review — mandatory after Step 3 report.

## Steam access policy

User approved Steam Web API key for read-only `GetOwnedGames`.
Authenticated Steam Store session for personalized Complete The Set payable price is not approved.

## Other queued

- DLC ownership eligibility IMPLEMENT.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Russian-language availability ranking factor.
- YouTube review selection.
- modern Windows compatibility evidence.
- semantic/Russian-description completion remains blocked on existing scheduled semantic runtime evidence; do not create another scheduler.

## Next decision

1. Existing Chat 1 completes Step 3 self-recheck and exact report.
2. Fresh Chat 2 performs zero-cost automation recon only.
3. Director consumes each exact report before advancing either track.

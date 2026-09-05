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
8. Automation migration идёт по отдельным gated phases; autonomous IMPLEMENT остаётся запрещён.
9. User will not pay additional money for OpenAI API usage. Do not ask user to add API credits or continue an architecture that requires separately billed OpenAI API usage. Any future automation redesign must target zero incremental paid API cost unless user explicitly changes this decision.

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

Implementation/probe evidence exists; Chat 1 must independently re-read current GitHub truth, verify all bounded Step 3 requirements, clean temporary one-shot machinery if appropriate, fix only genuine in-scope defects, and save the exact durable report. Do not start independent Taste Review until Director consumes that report.

## Automation — Phase 2B API route stopped by user cost constraint

Task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2B_LIVE_READONLY_PILOT_01.md`
Durable report:
`reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`

Outcome:
- real pinned Codex worker reached OpenAI Responses API under intended read-only security boundary;
- run was blocked by `You have no credits remaining. Add credits to continue using the API`;
- expected Epic worker report was not published, correctly fail-closed;
- no unauthorized worker write, no second task, no autonomous IMPLEMENT.

User decision after learning API billing is separate from ChatGPT Plus:
- user will not purchase/add OpenAI API credits;
- do not request API funding again;
- do not retry Phase 2B through separately billed OpenAI API;
- current API-key/GitHub-action route is paused/stopped as an automation solution under current cost policy;
- a future automation design may be investigated only if it can run without additional paid API cost, unless user explicitly changes this decision.

Current Chat 2 may be deleted. Do not create a replacement Phase 2B retry chat for the paid API route.

## Taste sequence

1. evidence state/confidence/reconsideration — complete internally;
2. play role + relative start priority — complete internally;
3. reconsideration commercial bridge + wishlist-good-deal override — implementation/probe evidence present, full bounded self-recheck + durable closeout pending;
4. independent current Taste Review — mandatory after Step 3 durable report before final acceptance.

## Steam access policy

User approved:
- Steam Web API key for read-only `GetOwnedGames`: yes;
- authenticated Steam Store session for personalized Complete The Set payable price: no for now.

DLC ownership eligibility remains queued. Personalized Complete The Set actual payable price remains fail-closed/unknown.

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

1. Existing Chat 1 continues full bounded Step 3 self-recheck until its exact report exists.
2. Do not spend money on or retry the separately billed OpenAI API automation route.
3. If automation remains desired, investigate a zero-incremental-cost alternative as a separate bounded design task; do not assume ChatGPT Plus can fund GitHub Actions API calls.

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

## ЧАТ 2 — Phase 2B live READ-ONLY pilot

Task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2B_LIVE_READONLY_PILOT_01.md`
Expected report:
`reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`

Durable Phase 2B report exists and was consumed by Director.
Status: `blocked_user_openai_api_credits`.

Verified bounded outcome from the report:
- real pinned Codex worker reached the OpenAI Responses API under the intended read-only security boundary;
- exact logical pilot remained `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`, revision 1 / attempt 1;
- final worker failed with non-secret billing error: `You have no credits remaining. Add credits to continue using the API`;
- expected automatic worker report `reviews/worker_reports/epic-ru-availability-source-probe-01.md` was correctly NOT published because no structured worker result existed;
- trusted publisher skipped fail-closed;
- no unauthorized worker write occurred;
- no second task and no attempt `a2` were dispatched;
- `dispatch_enabled` remains false;
- autonomous IMPLEMENT remains disabled.

Phase 2B is therefore not accepted as successful yet. One bounded next step only: user restores/adds OpenAI API credits, then Director authorizes a separate bounded retry. Do not auto-retry and do not drain the queue.

The current Chat 2 has a complete durable blocked report and may be deleted; a fresh replacement Chat 2 should be created only after credits are restored and Director prepares/authorizes the bounded retry.

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
2. User restores/adds OpenAI API credits.
3. Only after user confirms credits are available, Director authorizes a fresh bounded Phase 2B retry in replacement Chat 2.
4. After a successful retry, Director must verify the auto-published Epic RU report before advancing automation.

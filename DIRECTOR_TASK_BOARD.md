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

User reports Chat 1 finished, but Director durable closure check found the required report is still absent from `main`.

Implementation evidence already exists and should be treated as evidence to verify rather than blindly redo:
- `a3e39f6b98573616f19f444909742d3378d25d20` — align Step 3 guards with V5 reconsiderable semantics;
- `0b95d364376f7553965d2e7505c25ef9e261fe42` — align mailing-policy validator;
- `0fddfd3fc58373645bb648348dd5dc013b347eea` — bounded Taste commercial reconsideration bridge implementation;
- `f64d518a203604051bcda032780c5bb515976197` and `960a749fbf65b79eb0df629d11ad0c67c853ab72` — refreshed fixed-package/BioShock validation adjustments;
- production probe commit `685972c2c8a4399a76ac56d7f1ab67f92bd9f3a2`.

Known production probe evidence:
- workflow `Taste step 3 production probe once`;
- run `33973331054` — success;
- job `101325600995` — success;
- all producer/provenance verification steps passed;
- canonical pre-AI status remained `degraded` because existing semantic queues remain unresolved;
- current bridge counts were `{}` because refreshed current inputs had zero exact reconsiderable/strict-savings candidates;
- complete family partition remained true;
- visual producer built 523 items and bridge provenance check passed.

Because Chat 1 had a very long context, it must now re-open the authoritative task and sources from current `main` and independently revalidate the whole bounded Step 3 scope before closure. The worker must not rely on its conversational memory or previous self-summary.

Required self-recheck:
1. re-read the exact task plus Step 1/Step 2 reports and the three authoritative design/recon sources named by the task;
2. inspect current owner code/contracts on `main`, not only previous diffs;
3. verify every required outcome, preserve rule, required regression and control from the task one-by-one;
4. confirm canonical good-deal semantics are reused with no invented threshold;
5. confirm `confirmed_negative` and direct conflict remain non-overridable;
6. confirm reconsiderable/package and wishlist-good-deal exceptions preserve original Taste/evidence state, role/start priority, risks, warnings and provenance;
7. confirm fixed-package behavior is authoritative and no personalized Complete-the-Set arithmetic was fabricated;
8. rerun bounded deterministic regressions and current canonical regeneration/probe as needed;
9. inspect whether current `{}` bridge counts are legitimate current-data absence rather than a wiring defect;
10. remove temporary one-shot workflow if it is no longer needed;
11. if any real bounded defect is found, fix it in this same task and rerun relevant regressions;
12. save the exact required durable report with one allowed status and exact commits/runs/evidence.

Status: `continue_existing_chat_1_full_bounded_self_recheck`.
Do not start independent Taste Review until exact Step 3 report exists and Director consumes it.
Chat 1 remains occupied/manual until recheck and durable closure are complete.

After exact Step 3 report is consumed, the implementation Chat 1 may be deleted and a fresh independent Chat 1 should run the combined current Taste Review for steps 1–3 before final semantic acceptance.

## ЧАТ 2 — Phase 2B live READ-ONLY pilot

Task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2B_LIVE_READONLY_PILOT_01.md`
Expected report:
`reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`
Status: `created_and_running_or_working_new_chat_2`.

User confirmed repository Actions secret `OPENAI_API_KEY` exists; value is never requested/known/logged.

Pilot target exactly:
`WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`
Expected automatic cloud-worker report:
`reviews/worker_reports/epic-ru-availability-source-probe-01.md`

Critical pilot proof:
- one real Codex READ_ONLY_RECON worker only;
- Director must later observe the automatic Epic report in GitHub without user relaying worker output;
- max two slots and current Chat 1 manual occupancy preserved;
- LLM job no GitHub write credential;
- trusted publisher exact report path only;
- stale/current-state barrier enforced;
- no second auto-dispatch;
- IMPLEMENT structurally excluded.

Do not delete/reassign Chat 2 until the exact Phase 2B report is consumed.

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

1. Existing Chat 1 performs full bounded self-recheck from current GitHub truth, fixes only genuine in-scope defects if found, cleans temporary one-shot machinery if no longer needed, and saves the exact required Step 3 report.
2. Keep current Chat 2 running Phase 2B untouched.
3. Read exact Step 3 report before creating fresh independent Taste Reviewer Chat 1.
4. Read exact Phase 2B report and independently fetch auto-published Epic report before advancing automation.

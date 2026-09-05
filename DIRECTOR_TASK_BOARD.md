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

## Active product work

### ЧАТ 1 — Taste step 3

Task:
`WORKER_TASK_RECONSIDERATION_COMMERCIAL_BRIDGE_AND_WISHLIST_IMPLEMENT_01.md`
Task ID: `reconsideration-commercial-bridge-and-wishlist-implement-01`
Mode: `IMPLEMENT`
Expected report:
`reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`
Priority: `VERY_HIGH_USER_PRIORITY`.
Status: `running_or_ready_existing_chat_1`.

After step 3, independent current Taste Review is mandatory before final material acceptance of the combined three-step Taste sequence.

## Automation

### Phase 1

Shadow observer implemented + independently accepted.

### Phase 2A

Security/state/cloud-worker boundary implemented + independently accepted.
Audit:
`reviews/system_audits/director-orchestration-phase2a-audit-01.md`.

### Phase 2B — READY

User confirmed on 2026-09-05 that repository Actions secret named exactly `OPENAI_API_KEY` has been added to `kentrap2011-hub/steam-kz-deals-2`.

Secret handling:
- confirmation is presence-only;
- value is not known to Director and must never be pasted into chat, Git, task/report files or logs.

Task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2B_LIVE_READONLY_PILOT_01.md`
Task ID: `director-orchestration-phase2b-live-readonly-pilot-01`
Mode: `IMPLEMENT`
Expected report:
`reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`
Status: `ready_new_chat_2`.

Pilot scope exactly:
- reconcile current orchestration state and current manual Chat 1 occupancy;
- implement audit-required optimistic-concurrency/current-state stale barrier;
- enable exactly one live cloud `READ_ONLY_RECON` pilot;
- pilot target: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`;
- pinned official Codex Action only;
- LLM job remains repository-read-only with no GitHub write credential;
- trusted publisher may write only exact expected report path;
- no second automatic dispatch;
- autonomous IMPLEMENT remains structurally excluded.

The completed Phase 2A audit Chat 2 may be deleted. Create a fresh Chat 2 for the Phase 2B pilot.

## Taste sequence

1. evidence state/confidence/reconsideration — complete internally;
2. play role + relative start priority — complete internally;
3. reconsideration commercial bridge + wishlist-good-deal override — active;
4. independent current Taste Review — mandatory after step 3 before final acceptance.

## Steam access policy

User approved:
- Steam Web API key for read-only `GetOwnedGames`: yes;
- authenticated Steam Store session for personalized Complete The Set payable price: no for now.

DLC ownership eligibility remains queued. Personalized Complete The Set actual payable price remains fail-closed/unknown.

## Other queued

- `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md` — selected as first live cloud READ-ONLY pilot.
- DLC ownership eligibility IMPLEMENT.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Russian-language availability ranking factor.
- YouTube review selection.
- modern Windows compatibility evidence.
- semantic/Russian-description completion remains blocked on existing scheduled semantic runtime evidence; do not create another scheduler.

## Next decision

1. Start a fresh Chat 2 with `WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2B_LIVE_READONLY_PILOT_01.md`.
2. Keep Chat 1 on Taste step 3 until its exact report is available.
3. After Phase 2B pilot report, Director must verify the automatically published Epic RU worker report exists without user relay.
4. Only after successful pilot verification may the next automation phase be designed.

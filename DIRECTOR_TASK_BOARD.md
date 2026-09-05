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

Phase 2A audit explicitly permits user provisioning of repository Actions secret `OPENAI_API_KEY` and one separately enabled bounded Phase 2B READ-ONLY pilot afterward.

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

### Phase 2B — blocked on one-time user secret setup

Prepared task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2B_LIVE_READONLY_PILOT_01.md`
Task ID: `director-orchestration-phase2b-live-readonly-pilot-01`
Mode: `IMPLEMENT`
Expected report:
`reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`
Status: `blocked_user_must_confirm_OPENAI_API_KEY_repository_secret_exists`.

User action required exactly once:
- create/use a dedicated OpenAI API key;
- add it directly to repository `kentrap2011-hub/steam-kz-deals-2` -> Settings -> Secrets and variables -> Actions as repository secret named exactly `OPENAI_API_KEY`;
- never paste the value into ChatGPT, Git, task/report files or logs.

Provisioning the secret alone does NOT enable dispatch.

After user confirms secret presence, create a fresh Chat 2 for Phase 2B IMPLEMENT.
The Phase 2B implementation must enable exactly one live `READ_ONLY_RECON` cloud pilot for:
`WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`.

Critical audit carry-forward:
- current-state / optimistic-concurrency stale barrier before publication;
- exact task/revision/attempt/lease/base/blob/report binding;
- max two slots;
- current Chat 1 represented as external/manual occupancy if still active;
- LLM job has no GitHub write credential;
- trusted publisher writes only exact expected report path;
- no second automatic dispatch;
- IMPLEMENT structurally excluded from cloud worker path.

The Phase 2A audit Chat 2 is complete and can be deleted.

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

- `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md` — selected as first future cloud READ-ONLY pilot.
- DLC ownership eligibility IMPLEMENT.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Russian-language availability ranking factor.
- YouTube review selection.
- modern Windows compatibility evidence.
- semantic/Russian-description completion remains blocked on existing scheduled semantic runtime evidence; do not create another scheduler.

## Next decision

1. User adds repository Actions secret `OPENAI_API_KEY` and confirms only that it exists.
2. Do not ask user to reveal the key.
3. After confirmation, delete completed audit Chat 2 if not already deleted and create fresh Chat 2 for `WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2B_LIVE_READONLY_PILOT_01.md`.
4. Keep Chat 1 on Taste step 3 until its exact report is available.

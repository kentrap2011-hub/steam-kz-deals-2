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
8. Automation migration идёт по отдельным gated phases; Phase 2A ещё не включает реальный Codex dispatch.

## Review checkpoint

Latest System Audit:
`reviews/system_audits/director-orchestration-phase1-audit-01.md`
Status: complete.
Closure: accepted.
`system_audit_due: false`.

## Latest completed

### Taste step 1

Report:
`reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`
Status: `complete`.
Implementation commit: `2a1708ad598ea9baf7095478b646da689eb8f890`.
Validation run: `33962387867`.

Implemented explicit price-blind evidence states:
- sufficient;
- insufficient;
- reconsiderable;
- confirmed_negative.

Confirmed negative remains non-overridable by paid commercial signals. Step 2 may start. This is internal sequence progress, not final Taste acceptance.

### Automation Phase 1

Implementation report:
`reviews/worker_reports/director-orchestration-shadow-observer-implement-01.md`.
Independent audit:
`reviews/system_audits/director-orchestration-phase1-audit-01.md`.

Phase 1 systemic closure accepted. Safe foundation for separately gated Phase 2.

## Active next pair

### ЧАТ 1 — Taste step 2: play role + relative start priority

Task:
`WORKER_TASK_PLAY_ROLE_AND_START_PRIORITY_IMPLEMENT_01.md`
Task ID: `play-role-and-start-priority-implement-01`
Mode: `IMPLEMENT`
Expected report:
`reviews/worker_reports/play-role-and-start-priority-implement-01.md`
Priority: `VERY_HIGH_USER_PRIORITY`.
Status: `ready_continue_existing_chat_1`.

Goal:
- explicit main/full vs secondary/palate-cleanser vs family/co-op vs unresolved role;
- explicit relative start/queue priority;
- keep these separate from personal fit and sale urgency;
- preserve Step 1 evidence states;
- no wishlist-good-deal/commercial reconsideration bridge yet;
- no second ranker/sorter.

### ЧАТ 2 — Automation Phase 2A security/state boundary

Task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2A_SECURITY_BOUNDARY_IMPLEMENT_01.md`
Task ID: `director-orchestration-phase2a-security-boundary-implement-01`
Mode: `IMPLEMENT`
Expected report:
`reviews/worker_reports/director-orchestration-phase2a-security-boundary-implement-01.md`
Priority: `VERY_HIGH_INFRASTRUCTURE_PRIORITY`.
Status: `ready_new_chat_2_after_audit_chat_deleted`.

Goal:
- single authoritative state writer/controller;
- immutable intake/revision/attempt/lease semantics;
- READ-ONLY RECON/AUDIT worker request/result contracts;
- trusted report publisher boundary;
- future official Codex Action worker definition pinned and permission-bounded;
- real dispatch stays disabled;
- no OpenAI API key required in Phase 2A;
- no OpenAI/Codex invocation;
- no autonomous IMPLEMENT.

After Phase 2A acceptance, user will perform one-time `OPENAI_API_KEY` setup directly in GitHub Actions Secrets before Phase 2B live READ-ONLY worker pilot. Secret must never be pasted into chat/task/report/Git.

These two tasks are safely parallel: Chat 1 changes Taste/product semantics; Chat 2 changes disabled orchestration infrastructure only and must not touch product/Taste logic.

## Taste sequence

1. evidence state/confidence/reconsideration — complete internally;
2. play role + relative start priority — active next;
3. reconsideration commercial bridge + wishlist-good-deal override — after step 2.

If all three remain one bounded internal sequence, run one independent current Taste Review after step 3 before final material acceptance.

## Steam access policy

User approved:
- Steam Web API key for read-only `GetOwnedGames`: yes;
- authenticated Steam Store session for personalized Complete The Set payable price: no for now.

DLC ownership implementation remains queued pending later proper secret provisioning. Personalized Complete The Set actual payable price remains fail-closed/unknown.

## Other queued

- `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`.
- DLC ownership eligibility IMPLEMENT.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Russian-language availability ranking factor.
- YouTube review selection.
- modern Windows compatibility evidence.
- semantic/Russian-description completion remains blocked on existing scheduled semantic runtime evidence; do not create another scheduler.

## Next decision

1. Continue existing Chat 1 with Taste step 2.
2. Phase 1 audit Chat 2 may be deleted; create a fresh Chat 2 for Phase 2A IMPLEMENT.
3. Read both exact reports before Taste step 3 or Phase 2B.
4. Do not provision `OPENAI_API_KEY` until Phase 2A security boundary is validated.

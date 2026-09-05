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
7. Taste Reviewer recommendations have VERY HIGH USER PRIORITY.
8. Automation migration may begin before backlog completion, but must start in shadow/read-only phases and must not interrupt active product work.

## Review checkpoint

Latest System Audit: `reviews/system_audits/giveaway-cache-post-incident-audit-01.md`
Result: accepted.
`system_audit_due: false`.

## Active

### ЧАТ 1 — VERY HIGH PRIORITY Taste IMPLEMENT 1

Task:
`WORKER_TASK_TASTE_EVIDENCE_STATE_AND_CONFIDENCE_IMPLEMENT_01.md`
Task ID: `taste-evidence-state-and-confidence-implement-01`
Mode: `IMPLEMENT`
Expected report:
`reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`
Status: `running_or_ready_in_existing_chat_1`.

Goal:
- explicit insufficient / reconsiderable / confirmed-negative evidence state;
- stronger evidence provenance/strength rules;
- old shallow historical negatives can be weaker/reconsiderable;
- candidate-quality complaints separate from personal dislike;
- preserve price-blind Taste and no-discount-rescue.

### ЧАТ 2 — autonomous Director orchestration recon

Task:
`WORKER_TASK_AUTONOMOUS_DIRECTOR_ORCHESTRATION_RECON_01.md`
Task ID: `autonomous-director-orchestration-recon-01`
Mode: `READ-ONLY / RECON`
Expected report:
`reviews/worker_reports/autonomous-director-orchestration-recon-01.md`
Priority: `VERY_HIGH_INFRASTRUCTURE_PRIORITY`.
Status: `ready_new_chat_2`.

Goal:
- design cloud-first automation for an Android-first user;
- no always-on PC;
- user adds tasks only through Director chat in natural language;
- GitHub stores durable machine-readable queue/state;
- two worker slots auto-fill when safe;
- reports/CI/deploy/review gates auto-observed;
- user notified only at real user gates;
- staged rollout: shadow observer -> autonomous RECON/AUDIT -> bounded IMPLEMENT -> mature autopilot.

Automation must not interrupt the active Taste IMPLEMENT and must not jump directly to fully autonomous product writes.

## Steam access policy — user decision resolved

User explicitly approved on 2026-09-05:

1. **Steam Web API key: APPROVED** for a read-only canonical owned-games snapshot using Valve `IPlayerService/GetOwnedGames`, for DLC eligibility and related deterministic ownership checks.
2. **Authenticated Steam Store account/session integration: NOT APPROVED for now**. Do not design/store session cookies or authenticated storefront context for personalized Complete The Set payable prices.

Security rule:
- never ask user to paste Steam Web API key into ordinary chat/task/report;
- implementation must use an approved secret store/path, e.g. GitHub Actions secret, with no secret value committed or logged.

DLC ownership implementation may proceed later once the secret-provisioning path is prepared/approved. Personalized Complete The Set savings remain fail-closed/unknown until a future explicit decision changes the account-session boundary.

Previous Chat 2 DLC recon is durably complete and no longer needs its local chat context after this decision.
Report:
`reviews/worker_reports/dlc-personalized-bundle-economics-recon-01.md`.

## Taste sequence after current step

From `reviews/worker_reports/taste-review-recommendations-gap-recon-01.md`:
1. evidence state/confidence/reconsideration semantics;
2. play role + relative start priority;
3. reconsideration commercial bridge + wishlist-good-deal override.

Do not start step 3 before step 1 establishes stable non-negative insufficiency/reconsideration semantics.
Independent Taste Review required at the chosen material acceptance boundary.

## Other queued

- DLC ownership eligibility IMPLEMENT: now policy-approved in principle, pending proper secret provisioning path; no Steam session.
- Personalized Complete The Set actual payable price: blocked by explicit no-session decision; fail closed.
- `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md` queued blocker-resolution recon.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md` ready.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md` ready.
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` queued larger integration.
- Russian-language availability ranking factor planned.
- YouTube review selection planned.
- modern Windows compatibility evidence planned.
- semantic/Russian-description completion remains blocked on existing scheduled semantic runtime evidence; do not create another scheduler.

## Next decision

1. Keep Chat 1 on Taste IMPLEMENT 1.
2. Old DLC Chat 2 may be deleted; start a fresh Chat 2 for autonomous orchestration recon.
3. After automation recon, choose the smallest shadow-mode IMPLEMENT that can coexist with ongoing product work.
4. Do not wait for the whole backlog to finish before migration to automation.

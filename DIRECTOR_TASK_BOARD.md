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
8. Automation migration может идти параллельно backlog, но новая orchestration authority проходит обязательный System Audit перед Phase 2.

## Review checkpoint

`system_audit_due: true`.
Reason: accepted Phase 1 orchestration/state/queue boundary.
Audit task: `WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE1_SYSTEM_AUDIT_01.md`.
Expected report: `reviews/system_audits/director-orchestration-phase1-audit-01.md`.

## ЧАТ 1 — Taste IMPLEMENT 1 needs continuation

Task:
`WORKER_TASK_TASTE_EVIDENCE_STATE_AND_CONFIDENCE_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`

Current durable status: **not complete**.

Evidence:
- expected report does not exist on `main`;
- latest one-shot workflow `Taste evidence state implement once` run `33955749866` failed;
- job `101278674109`:
  - `Apply bounded implementation`: success;
  - `Validate contracts and controls`: failure;
  - commit/report cleanup steps skipped;
- exact failure: `SyntaxError: unterminated string literal` in temporary modified `scripts/build_pre_ai_chatgpt_payload.py`, line 198.

Recent one-shot helper commits include:
- `8a432d7037ea33db8b5e4610f88c7f614324fbf3`
- `3e7b69c8e819369bb69a95b9337897526170dd83`
- `b695dd82356d89d46509d5a1d2981570a123e00a`
- `08f1c5c200556e2f7214ec3817f9df4e37af2ec4`

Status: `continue_existing_chat_1_same_scope_fix_validation_then_report`.

Do not start Taste step 2 until the exact required report exists and Director verifies successful validation.

## ЧАТ 2 — Phase 1 shadow observer complete; independent audit next

Implementation report:
`reviews/worker_reports/director-orchestration-shadow-observer-implement-01.md`
Status: `complete`.

Verified implementation evidence:
- run `33955350364` success;
- job `101277589011` success;
- artifact `9966167937` / `shadow-plan`;
- exact simulated assignment: `epic-ru-availability-source-probe-01` to free `slot_2`;
- current manual Chat 1 occupied `slot_1`;
- conflicting Taste/wishlist task blocked;
- no OpenAI/Codex invocation;
- no real worker dispatch;
- no product mutation.

Because this establishes a new orchestration/state/queue boundary, Phase 2 must not start before an independent System Audit.

Audit task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE1_SYSTEM_AUDIT_01.md`
Mode: `READ-ONLY / AUDIT`
Expected report:
`reviews/system_audits/director-orchestration-phase1-audit-01.md`
Status: `ready_new_chat_2_independent_auditor`.

The implementation Chat 2 may be deleted before creating the independent audit Chat 2.

## Steam access policy

User approved:
- Steam Web API key for read-only `GetOwnedGames`: yes;
- authenticated Steam Store session for personalized Complete The Set payable price: no for now.
Never ask for secret values in ordinary chat/report/task files.

## Taste sequence after current step

1. evidence state/confidence/reconsideration semantics — current step, not yet complete;
2. play role + relative start priority;
3. reconsideration commercial bridge + wishlist-good-deal override.

Independent Taste Review required at the chosen material acceptance boundary.

## Automation sequence

Phase 1 shadow observer: implemented and technically validated; independent System Audit pending.

If audit accepts:
- close `system_audit_due`;
- proceed to a bounded Phase 2 security/dispatch boundary for automatic READ-ONLY RECON/AUDIT cloud workers;
- before actual Codex worker execution, provision `OPENAI_API_KEY` only through approved GitHub Actions secret storage and perform bounded permissions/security review;
- no autonomous product IMPLEMENT yet.

## Other queued

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

1. Existing Chat 1 fixes the exact current validation failure and completes the same Taste task/report.
2. Existing Phase 1 implementation Chat 2 can be deleted.
3. Create a fresh independent Chat 2 for `director-orchestration-phase1-system-audit-01`.
4. Read both exact reports before advancing Taste step 2 or automation Phase 2.

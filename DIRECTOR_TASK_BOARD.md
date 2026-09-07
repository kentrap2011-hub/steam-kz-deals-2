# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from an old chat history alone.
- Do not infer that a newly assigned worker task has actually been launched merely because the task command was prepared. Treat a slot as running only after the user says the new chat was created/sent the task or provides equivalent confirmation.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.
- All future non-trivial worker tasks must obey `WORKER_REPORT_DURABILITY_PROTOCOL.md`: create the exact report path early with `in_progress`, checkpoint it before long verification, and never claim completion before the report is committed and re-read from `main`.

## Worker report reliability
Canonical protocol:
`WORKER_REPORT_DURABILITY_PROTOCOL.md`

Reason:
workers have repeatedly completed substantial work but failed to persist the required durable report before the response cycle ended. This is now treated as an orchestration/process defect, not a normal closeout condition.

Required behavior:
- report-first lifecycle;
- incremental checkpoint updates;
- preserve report before one-more-check behavior;
- missing report means task not durably closed;
- worker prose never overrides missing GitHub report.

## Taste — logic implemented, production materialization still pending
Authoritative existing singleton:
- task title: `Taste Semantic Producer`;
- task instance id: `6a9d6fdddc00819193ed670d782045c4`;
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- producer generation: `1`;
- no second producer may be created.

### Chat 2 — pre-AI deal contract guard IMPLEMENT CLOSEOUT STILL MISSING
Task:
`WORKER_TASK_TASTE_PRE_AI_DEAL_CONTRACT_GUARD_FIX_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/taste-pre-ai-deal-contract-guard-fix-implement-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `worker_explicitly_did_not_finish_saving_report`.

User supplied the worker's exact message: `Не успел завершить сохранение отчёта в main в этом ходе.` Director independently checked the exact expected path and the report is absent from `main`.

Existing Chat 2 must continue only long enough to self-verify and save the exact required report. Director will not reconstruct outcome from commits/logs/Actions.

Hard invariants remain:
- no new Taste canary in this task;
- existing producer remains disabled/fail-closed;
- old Prototype result must not be reused;
- no second task/producer/generation;
- no paid API or Copilot.

Do not delete Chat 2 yet.

## Chat 1 — main list freshness recon COMPLETE
Completed task:
`WORKER_TASK_VISUAL_MAIN_LIST_FRESHNESS_RECON_01.md`
Durable report:
`reviews/worker_reports/visual-main-list-freshness-recon-01.md`
Status: `complete`.

Accepted Director-level conclusion:
- published paid-discount main list is stale and must not be treated as a current active-discounts list;
- last proven commercial freshness behind published paid `items` is the source snapshot rendered as `31 авг. 2026, 00:37`;
- later visual/giveaway writes did not refresh paid items;
- top expired rows are stale commercial rows whose stored sale end passed while the old snapshot remained published;
- Steam collection itself is still running;
- blocker is a missing active handoff/orchestration link from fresh daily Steam shortlist into the existing canonical commercial mailing/visual build-and-publish path;
- old label-only `Данные:` -> `Рассылка:` fix remains insufficient and cancelled;
- truthful UI freshness must be domain-specific: paid-list freshness independent from giveaway freshness, with explicit stale status when overdue.

Completed recon worker Chat 1 is deletable.

### Next Chat 1 — PRE-FIX FORENSIC RECON BEFORE REPAIR
Task:
`WORKER_TASK_PUBLICATION_FRESHNESS_PRE_FIX_FORENSIC_RECON_01.md`
Expected report:
`reviews/worker_reports/publication-freshness-pre-fix-forensic-recon-01.md`
Mode: `READ-ONLY / RECON / FORENSIC`
Priority: `VERY_HIGH_RELIABILITY`
Status: `ready_fresh_chat_1_before_repair`.

Reason:
repairing the commercial handoff first may mutate the very workflow/receipt/artifact state needed to explain how the incident arose and why safeguards failed. Capture the broken state first.

Required outcome:
- exact current broken edge/handoff;
- whether/when it historically stopped is proven or only bounded;
- why upstream freshness coexisted with stale published paid items;
- why current monitoring/receipts/fail-closed logic did not escalate the stale domain;
- compare with giveaway incident before repair changes the evidence;
- freeze pre-fix identities/timestamps/state for later comparison;
- verify whether the already-written repair task is safe as-is or needs one bounded correction.

### Then Chat 1 — main list refresh handoff IMPLEMENT
Task:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `blocked_on_pre_fix_forensic_recon`.

Do not run this IMPLEMENT until the pre-fix forensic report is consumed.

## Publication freshness recurrence postmortem — REQUIRED AFTER CURRENT RECOVERY
Task:
`WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Expected report:
`reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`
Mode: `READ-ONLY / RECON / POSTMORTEM`
Priority: `VERY_HIGH_RELIABILITY`
Status: `queued_after_main_list_refresh_recovery`.

This remains required after repair. It will compare the captured broken state, the actual repair, and the earlier giveaway incident, then define one systemic prevention package.

## Giveaway publication
User has verified on Android that the free giveaway is visible again.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Fresh Chat 1 runs the pre-fix forensic recon first; do not repair the main-list handoff yet.
2. Existing Chat 2 must save its missing durable report and must not start another task.
3. After Director consumes the pre-fix forensic report, run the bounded main-list repair, adjusted only if the forensic report proves the current task unsafe/incomplete.
4. After repair and user verification, run the cross-incident recurrence postmortem before unrelated backlog work.
5. Do not run a fresh Taste semantic canary until Director consumes Chat 2's exact implementation report.

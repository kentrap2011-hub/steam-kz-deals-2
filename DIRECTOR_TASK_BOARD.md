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

Current evidence:
- new report-first protocol protected Chat 1 forensic work: its report exists in `main` with substantial `in_progress` checkpoint evidence even though the worker did not finalize in the same response cycle;
- legacy Chat 2 task still has no report at all and remains a true durability failure until it persists one.

## Taste — logic implemented, production materialization still pending
Authoritative existing singleton:
- task title: `Taste Semantic Producer`;
- task instance id: `6a9d6fdddc00819193ed670d782045c4`;
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- producer generation: `1`;
- no second producer may be created.

### Chat 2 — pre-AI deal contract guard IMPLEMENT REPORT STILL ABSENT
Task:
`WORKER_TASK_TASTE_PRE_AI_DEAL_CONTRACT_GUARD_FIX_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/taste-pre-ai-deal-contract-guard-fix-implement-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `worker_finished_response_cycle_report_absent`.

Director rechecked only the exact expected path after the latest worker completion message; the report is still absent from `main`.

Existing Chat 2 must perform report persistence first. No new analysis or task may begin before the exact report exists.

Hard invariants remain:
- no new Taste canary;
- existing producer remains disabled/fail-closed;
- old Prototype result must not be reused;
- no second task/producer/generation;
- no paid API or Copilot.

Do not delete Chat 2 yet.

## Chat 1 — PRE-FIX FORENSIC RECON CHECKPOINT SAFELY PERSISTED
Task:
`WORKER_TASK_PUBLICATION_FRESHNESS_PRE_FIX_FORENSIC_RECON_01.md`
Report:
`reviews/worker_reports/publication-freshness-pre-fix-forensic-recon-01.md`
Mode: `READ-ONLY / RECON / FORENSIC`
Priority: `VERY_HIGH_RELIABILITY`
Status: `in_progress_checkpoint_persisted_worker_response_cycle_ended_before_finalize`.

Important: this is NOT a missing-report failure. The report exists in `main` and contains substantial frozen pre-fix evidence, including the current source/visual identities and the currently proven break classification.

Current checkpoint already proves:
- fresh Steam-derived state reaches shortlist, mailing and deterministic pre-AI state;
- full visual rebuild is correctly blocked by semantic incompleteness;
- scoped deterministic commercial refresh helper already exists;
- production workflow has a `giveaway_only` scoped branch but no equivalent `commercial_only` production orchestration/receipt branch;
- the active break is therefore the deterministic commercial state -> canonical paid visual publication orchestration edge;
- common systemic pattern with giveaway is coupling independently refreshable deterministic domains to a full semantic-completion gate without a wired scoped handoff/liveness invariant.

The report is not final yet. Existing Chat 1 should only finish the bounded unresolved evidence items already listed in its report, then set final status and re-read the report. Do not repair anything yet.

### Then Chat 1 — main list refresh handoff IMPLEMENT
Task:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `blocked_on_final_pre_fix_forensic_report`.

Do not run this IMPLEMENT until Director consumes the finalized pre-fix forensic report.

## Publication freshness recurrence postmortem — REQUIRED AFTER CURRENT RECOVERY
Task:
`WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Expected report:
`reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`
Mode: `READ-ONLY / RECON / POSTMORTEM`
Priority: `VERY_HIGH_RELIABILITY`
Status: `queued_after_main_list_refresh_recovery`.

## Giveaway publication
User has verified on Android that the free giveaway is visible again.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Existing Chat 1 finalizes only its already-persisted forensic report; no repair yet.
2. Existing Chat 2 persists its missing exact report before doing anything else.
3. After Director consumes the final forensic report, run the bounded main-list repair, adjusted only if the forensic report proves the current task unsafe/incomplete.
4. After repair and user verification, run the cross-incident recurrence postmortem before unrelated backlog work.
5. Do not run a fresh Taste semantic canary until Director consumes Chat 2's exact implementation report.

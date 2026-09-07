# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from an old chat history alone.
- Do not infer that a newly assigned worker task has actually been launched merely because the task command was prepared. Treat a slot as running only after the user says the new chat was created/sent the task or provides equivalent confirmation.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.
- All future non-trivial worker tasks must obey `WORKER_REPORT_DURABILITY_PROTOCOL.md`: create the exact report path early with `in_progress`, checkpoint it before long verification, and never claim completion before the report is committed and re-read from `main`.
- Every user-facing worker closeout must obey `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`: explain in ordinary Russian what was wrong, what the worker actually did, why, what succeeded, what remains unresolved, and what the next stage is and why. Internal technical labels are never a substitute for explanation.

## User communication
Canonical protocol:
`DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`

Required behavior after every consumed worker report:
- explain the result in plain language before giving the next worker command;
- cover what we did, why we did it, what changed, what is still not solved, and why the next step is necessary;
- do not make the user decode internal terms such as `pre-AI`, `commercial_only`, `blocked`, `canary`, `receipt`, `fail-closed`, `handoff` or workflow/task names;
- if a technical name is needed for traceability or a copy-paste command, place it after the plain-language explanation;
- do not omit a deeper unresolved cause merely because the current local fix succeeded.

## Worker report reliability
Canonical protocol:
`WORKER_REPORT_DURABILITY_PROTOCOL.md`

Current evidence:
- report-first protocol protected Chat 1 forensic work and allowed the same report to be finalized on the next turn;
- Chat 2's legacy missing-report failure was recovered and the exact report now exists in `main`.

## Taste — logic implemented, production materialization still pending
Authoritative existing singleton:
- task title: `Taste Semantic Producer`;
- task instance id: `6a9d6fdddc00819193ed670d782045c4`;
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- producer generation: `1`;
- no second producer may be created.

### Chat 2 — pre-AI deal contract guard IMPLEMENT DURABLY CLOSED AS BLOCKED
Task:
`WORKER_TASK_TASTE_PRE_AI_DEAL_CONTRACT_GUARD_FIX_IMPLEMENT_01.md`
Durable report:
`reviews/worker_reports/taste-pre-ai-deal-contract-guard-fix-implement-01.md`
Final status: `blocked`.

Accepted Director-level result:
- stale deal-quality contract guard was fixed from exact v1.3 to canonical exact v1.5;
- focused fail-closed regressions passed;
- normal `Build pre-AI deterministic payload` workflow completed successfully and reached atomic commit;
- fresh pre-AI artifacts were persisted and aligned with current mailing source;
- old Prototype result was not reused;
- no new canary or second producer/task/generation was created.

Only remaining blocker from the worker report:
- live control-plane state of singleton task `6a9d6fdddc00819193ed670d782045c4` could not be authoritatively confirmed as disabled in that closing pass.

Do not launch a fresh canary until that exact disabled state is positively confirmed by a separate bounded step.

Completed Chat 2 worker can be deleted; its result is durable.

## Chat 1 — PRE-FIX FORENSIC RECON COMPLETE
Task:
`WORKER_TASK_PUBLICATION_FRESHNESS_PRE_FIX_FORENSIC_RECON_01.md`
Durable report:
`reviews/worker_reports/publication-freshness-pre-fix-forensic-recon-01.md`
Final status: `complete_ready_for_repair`.

Accepted Director-level result:
- fresh Steam-derived data reaches shortlist, mailing and deterministic pre-AI state;
- full visual rebuild is correctly blocked when semantic ChatGPT payload is incomplete;
- deterministic commercial scoped helper already exists: `scripts/refresh_visual_commercial_fields.py`;
- production visual workflow has a wired `giveaway_only` scoped path but no equivalent `commercial_only` orchestration/receipt path;
- therefore the active break is deterministic commercial truth -> canonical paid visual publication orchestration, not Steam ingestion or shortlist/mailing;
- exact first historical missed commercial invocation is not reconstructible and was not guessed;
- common systemic pattern with giveaway is that independently refreshable deterministic subdomains can remain stale indefinitely when full visual publication is blocked by semantic incompleteness and no scoped liveness path exists.

Repair task assessment:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md` is directionally correct but requires one bounded correction before execution:
- explicitly reuse `scripts/refresh_visual_commercial_fields.py`;
- wire `commercial_only` into the existing visual workflow;
- add scoped commercial freshness receipt/proof;
- preserve the existing full semantic fail-closed guard;
- require current deterministic source binding plus safe prior semantic coverage;
- prove giveaway preservation;
- no new scheduler/writer.

Completed Chat 1 forensic worker can be deleted; it is not stuck.

### Next paid-list step
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Status: `needs_bounded_task_correction_before_launch`.

Do not launch the repair task until Director updates it to match the finalized forensic report.

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
Task:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Correct the paid-list repair task using the finalized forensic report, then launch a fresh Chat 1 for the bounded repair.
2. Run one separate bounded control-plane confirmation that the existing Taste singleton is disabled before allowing exactly one fresh canary.
3. After paid-list repair and user verification, run the cross-incident recurrence postmortem before unrelated backlog work.

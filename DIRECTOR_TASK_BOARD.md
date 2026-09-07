# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from an old chat history alone.
- Do not infer that a newly assigned worker task has actually been launched merely because the task command was prepared. Treat a slot as running only after the user says the new chat was created/sent the task or provides equivalent confirmation.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.

## Taste — logic implemented, production materialization still pending
Authoritative existing singleton:
- task title: `Taste Semantic Producer`;
- task instance id: `6a9d6fdddc00819193ed670d782045c4`;
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- producer generation: `1`;
- no second producer may be created.

### Chat 2 — atomic ingest failure recon COMPLETE
Completed task:
`WORKER_TASK_TASTE_CANARY_ATOMIC_INGEST_FAILURE_RECON_01.md`
Durable report:
`reviews/worker_reports/taste-canary-atomic-ingest-failure-recon-01.md`
Status: `complete`.

Accepted Director-level diagnosis:
- Prototype semantic result itself was not the immediate cause;
- canary ingest failed before row-level ingest because committed pre-AI state was stale versus current mailing;
- upstream root cause is obsolete exact contract guard in `scripts/build_pre_ai_deal_scenarios.py`: builder expects deal-quality v1.3 while canonical contract is v1.5;
- this caused pre-AI run `33991072184` to fail before atomic commit, leaving Sep-3 pre-AI state beside newer Sep-5 mailing state;
- old Prototype result is bound to the stale snapshot and must NOT be reused after repair;
- after repair, a completely fresh one-row canary will be required as a separate later task;
- existing Taste Scheduled Task remains disabled/fail-closed.

Completed recon worker Chat 2 is deletable.

### Next Chat 2 — pre-AI deal contract guard IMPLEMENT
Task:
`WORKER_TASK_TASTE_PRE_AI_DEAL_CONTRACT_GUARD_FIX_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/taste-pre-ai-deal-contract-guard-fix-implement-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `ready_fresh_chat_2`.

Scope:
- align the obsolete deal-scenario builder compatibility guard with canonical v1.5;
- preserve fail-closed behavior for incompatible contracts;
- prove the normal pre-AI atomic workflow succeeds and commits fresh state aligned with current mailing;
- do NOT run a new semantic canary in this task;
- keep the existing Taste producer disabled;
- never reuse old Prototype result;
- no second task/producer/generation, paid API or Copilot.

## Chat 1 — old header-date recon COMPLETE
Completed task:
`WORKER_TASK_VISUAL_HEADER_DATA_DATE_RECON_01.md`
Durable report:
`reviews/worker_reports/visual-header-data-date-recon-01.md`
Status: `complete`.

This is the old Chat 1 the user still had open. It completed correctly and is deletable.

The old label-only recommendation was rejected by the user as insufficient. Task `WORKER_TASK_VISUAL_HEADER_DATA_LABEL_IMPLEMENT_01.md` remains SUPERSEDED / DO NOT RUN.

### Next Chat 1 — main list freshness recon NOT YET LAUNCHED
Task:
`WORKER_TASK_VISUAL_MAIN_LIST_FRESHNESS_RECON_01.md`
Expected report:
`reviews/worker_reports/visual-main-list-freshness-recon-01.md`
Mode: `READ-ONLY / RECON`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `ready_fresh_chat_1_not_yet_launched`.

User explicitly clarified that this new Chat 1 has not yet been created/launched. Therefore the absence of its durable report is expected and is NOT a worker closeout failure.

User-visible evidence to investigate when launched:
- giveaway works;
- header shows old date;
- first three visible main-list games show `скидка закончилась`.

Goals when launched:
- establish the real last successful refresh of the displayed discounted-games list;
- determine why the first visible rows already show ended discounts;
- decide whether the main list is stale/degraded;
- identify the exact blocking boundary if stale;
- determine a truthful user-facing freshness date/status;
- define one minimal next IMPLEMENT action.

## Giveaway publication
User has verified on Android that the free giveaway is visible again.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. User may delete the old completed Chat 1.
2. User still needs to launch fresh Chat 1 with `WORKER_TASK_VISUAL_MAIN_LIST_FRESHNESS_RECON_01.md`.
3. Fresh Chat 2 may run the bounded pre-AI contract-guard fix.
4. Do not run a new Taste semantic canary until Chat 2's implementation report proves fresh current bindings are committed.
5. If future Chat 1 proves the main list stale, prioritize the real freshness/publication fix before cosmetic header wording.

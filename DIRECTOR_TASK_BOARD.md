# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from an old chat history alone.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.

## Taste — logic implemented, production materialization still pending
The Taste Steps 1–3 semantic logic and the independent Taste Reviewer maintenance recommendations are already implemented and regression-covered.

Authoritative existing singleton:
- task title: `Taste Semantic Producer`;
- task instance id: `6a9d6fdddc00819193ed670d782045c4`;
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- producer generation: `1`;
- no second producer may be created.

## Chat 1 — giveaway visual publication recovery COMPLETE
Task:
`WORKER_TASK_GIVEAWAY_VISUAL_PUBLICATION_RECOVERY_IMPLEMENT_01.md`
Durable report:
`reviews/worker_reports/giveaway-visual-publication-recovery-implement-01.md`
Status: `complete_ready_for_user_verification`.

Accepted production outcome:
- giveaway publication is repaired through the existing canonical visual writer;
- no second scheduler/writer and no manual patch were introduced;
- canonical giveaway blob is now bound into `data/production/visual/current.json`;
- giveaway state is active with one offer at acceptance time;
- freshness receipt proves a real produced/persisted scoped visual refresh;
- full independent Taste visual freshness remains explicitly false and was not fabricated;
- normal Pages deploy succeeded.

Next action: user verifies the real giveaway section on Android. Chat 1 worker is durably complete and deletable.

## Chat 2 — Taste existing singleton canary durable closeout MISSING
Task:
`WORKER_TASK_TASTE_EXISTING_SINGLETON_CANARY_EXECUTE_01.md`
Expected report:
`reviews/worker_reports/taste-existing-singleton-canary-execute-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`.
Status: `worker_claimed_finished_but_required_report_missing`.

Director checked only the exact expected report path after the worker completion claim; it is absent from `main`. Director will not reconstruct task outcome from logs/Actions/commits. Existing Chat 2 must self-verify and write the exact durable report even if final status is `blocked`.

Hard invariants remain:
- reuse only task instance `6a9d6fdddc00819193ed670d782045c4`;
- no second Scheduled Task/producer/generation;
- no paid OpenAI API;
- no Copilot fallback;
- no manual semantic processing;
- no throughput widening.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. User verifies giveaways on the real Android site now.
2. Existing Chat 2 performs only its own durable Taste canary closeout and writes `reviews/worker_reports/taste-existing-singleton-canary-execute-01.md`.
3. Do not widen Taste throughput until Director consumes that exact report.
4. Do not start unrelated work in either slot before these gates are resolved.

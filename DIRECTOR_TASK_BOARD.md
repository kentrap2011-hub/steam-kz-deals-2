# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from an old chat history alone.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.

## Taste — logic implemented, production materialization still pending
The Taste Steps 1–3 semantic logic and the independent Taste Reviewer maintenance recommendations are already implemented and regression-covered.

Durable implementation/acceptance report:
`reviews/worker_reports/taste-steps-1-3-production-materialization-acceptance-01.md`

Current blocking truth from that report:
- semantic scope: 701;
- resolved: 0;
- unresolved: 701;
- publication completeness: false;
- current site is not yet a valid verification target for the new Taste behavior.

Authoritative existing singleton:
- task title: `Taste Semantic Producer`;
- task instance id: `6a9d6fdddc00819193ed670d782045c4`;
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- producer generation: `1`;
- GitHub-owned producer fence is implemented;
- no second producer may be created.

## Chat 1 — giveaway visual publication recovery IMPLEMENT COMPLETE
Completed task:
`WORKER_TASK_GIVEAWAY_VISUAL_PUBLICATION_RECOVERY_IMPLEMENT_01.md`

Durable report:
`reviews/worker_reports/giveaway-visual-publication-recovery-implement-01.md`

Status: `complete_ready_for_user_verification`.

Accepted production outcome:
- exact prior full-build failure remains fail-closed on incomplete independent ChatGPT/Taste production payload;
- bounded existing giveaway refresh now activates from canonical giveaway/visual provenance mismatch even when the giveaway snapshot arrived in a mixed production commit;
- no second scheduler, giveaway writer, visual writer, cache path, or UI workaround was created;
- canonical giveaway blob `04a913e4be29689d7ded6c8cf0f3f81f2030d23f` is now bound into canonical visual blob `61b20125acdcddd722df8efa0f67ed0dc23341af`;
- canonical visual producer commit: `1d7fb4d172d6d36dec4e78a5db2cdf51fa26b6ab`;
- giveaway state is `active`, offer count `1`, validated fresh-until `2026-09-07T02:45:35.089580Z`;
- visual build run `34047960720`: success through existing `giveaway_refresh`; paid items remained unchanged;
- freshness receipt: `fresh_build=true`, `scope=giveaway_only`, exact produced/persisted/staged identity verified, `full_visual_freshness=false`;
- normal deploy run `34047980496`: success; `VISUAL_PUBLICATION_OUTCOME=fresh`; GitHub Pages deployment success.

Chat 1 worker is complete and must not start another implementation task. The next action for this incident is real user verification on the deployed site/Android device.

## Chat 2 — Taste existing singleton canary execution
Task:
`WORKER_TASK_TASTE_EXISTING_SINGLETON_CANARY_EXECUTE_01.md`
Expected report:
`reviews/worker_reports/taste-existing-singleton-canary-execute-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`.
Status: `ready_or_running_chat_2`.

This task must reuse the SAME existing Scheduled Task instance `6a9d6fdddc00819193ed670d782045c4` and process exactly one semantic row before Director review.

Hard prohibitions:
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
1. Ask the user to verify the giveaway section on the real deployed site/Android device; the publication recovery is now a valid verification target.
2. Chat 2 continues the one-row Taste singleton canary independently.
3. Do not start another Chat 1 implementation task from this worker.
4. Do not widen Taste throughput before Director consumes its canary report.
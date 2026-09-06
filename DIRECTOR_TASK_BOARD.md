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

## Chat 1 — giveaway recurrence recon COMPLETE
Completed task:
`WORKER_TASK_GIVEAWAY_EMPTY_FEED_RECURRENCE_RECON_01.md`

Durable report:
`reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`

Accepted Director-level diagnosis:
- canonical giveaway snapshot is healthy, complete and fresh;
- one valid active Epic giveaway exists (`Alone With You` at recon time);
- current site-facing `data/production/visual/current.json` is bound to an older expired giveaway snapshot;
- canonical `Build daily visual payload` run `34037436064` failed/degraded at `Build and refresh canonical visual payload once`;
- no fresh visual was persisted;
- fail-closed is behaving correctly and must not be weakened;
- incident is NOT the old browser cache/identity issue and NOT an upstream giveaway-source outage.

User should NOT re-check the site yet.

Completed recon worker Chat 1 is deletable.

### Next Chat 1 — giveaway visual publication recovery IMPLEMENT
Task:
`WORKER_TASK_GIVEAWAY_VISUAL_PUBLICATION_RECOVERY_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/giveaway-visual-publication-recovery-implement-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `ready_fresh_chat_1`.

Scope:
- repair/recover only the existing canonical daily visual build/publication path;
- identify the actual failure inside the proven boundary;
- preserve a single visual writer;
- preserve fail-closed freshness/completeness;
- if unrelated subsystem incompleteness blocks the whole visual build, allow only a minimal safe section-level refresh architecture if it keeps unrelated sections explicitly degraded and does not fabricate freshness;
- no manual patch of visual/cache;
- no second scheduler/writer;
- no UI workaround.

Acceptance requires the published visual artifact to bind exactly to the then-current canonical giveaway blob, with a fresh handoff and fresh produced/persisted visual receipt. Only then may status be `complete_ready_for_user_verification`.

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
1. Fresh Chat 1 runs the bounded giveaway visual publication recovery implementation.
2. Chat 2 continues the one-row Taste singleton canary independently.
3. If giveaway recovery reaches `complete_ready_for_user_verification`, Director asks for real Android verification before closing the incident.
4. Do not widen Taste throughput before Director consumes its canary report.

# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
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

A singleton replacement ChatGPT Scheduled Task was then implemented:
`reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`

That report closed `blocked` only at the live execution boundary:
- exactly one replacement `Taste Semantic Producer` exists;
- task instance id: `6a9d6fdddc00819193ed670d782045c4`;
- producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- generation: 1;
- GitHub-owned producer fence is implemented;
- task retained disabled/fail-closed;
- `last_run_time = null`;
- semantic rows processed: 0;
- no second producer may be created.

The worker chat that created the canary was deleted by the user after its durable report was already saved. Therefore no active worker is currently advancing Taste. The next Taste worker must reuse the exact existing task instance above and perform only the bounded one-row execution/ingest continuation; it must never create another Taste producer.

Priority: `VERY_HIGH_USER_PRIORITY`.

## Chat 1 — current giveaway incident
Task:
`WORKER_TASK_GIVEAWAY_EMPTY_FEED_RECURRENCE_RECON_01.md`
Expected report:
`reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`
Mode: `READ-ONLY / RECON`
Priority: `VERY_HIGH_USER_PRIORITY`.

User has created the current Chat 1 for this task.
Current durable report path is still absent from `main`, so this worker is considered running/not durably complete.

Important: Chat 1 is currently diagnosing the empty/fail-closed giveaway feed; it is NOT yet an implementation fix. Once the durable recon identifies one bounded root cause/action, the next immediate task in this slot should be the corresponding IMPLEMENT fix before ordinary backlog work.

User-visible incident evidence:
- `Данные: 31 авг., 00:37`;
- active `🎁 Раздачи (!)` tab;
- warning `Раздачи временно не удалось проверить полностью.`;
- no giveaway cards visible.

Do not ask user to re-check giveaways until diagnosis -> bounded fix -> deploy reaches the user verification gate.

## Chat 2 — slot free, must return to Taste
The previous Taste canary worker chat was deleted by the user after durable closeout.

Status: `FREE_BUT_TASTE_CONTINUATION_REQUIRED`.

Do NOT assign UI/top-summary or ordinary backlog work to Chat 2 yet.
The next Chat 2 assignment must continue Taste production materialization using the SAME existing Scheduled Task instance `6a9d6fdddc00819193ed670d782045c4` and must not create another producer.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Chat 1 finishes the giveaway recurrence recon and then immediately moves to the bounded giveaway fix based on its durable diagnosis.
2. Fresh Chat 2 continues the existing Taste singleton canary path; no second Taste producer.
3. Taste site verification waits for legitimate semantic materialization and regenerated production output.
4. Giveaway site verification waits for diagnosis, implementation fix, deploy, then real Android verification.

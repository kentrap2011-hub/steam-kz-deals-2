# WORKER TASK — Publication Freshness Pre-Fix Forensic Recon 01

## Task ID
`publication-freshness-pre-fix-forensic-recon-01`

## Mode
`READ-ONLY / RECON / FORENSIC`

## Priority
`VERY_HIGH_RELIABILITY`

## Expected report
`reviews/worker_reports/publication-freshness-pre-fix-forensic-recon-01.md`

## Run order
Run **before** `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md` while the paid-list freshness failure is still present in production/repository state.

## Why now
The current broken state is valuable evidence. Repairing the handoff first can change workflow state, receipts, artifacts, timestamps, queue/handoff relationships, and make the original failure mode harder to distinguish from the repaired state.

This task captures the incident before mutation. A separate post-repair postmortem remains required afterward so the final analysis can compare pre-fix evidence with the actual repair and verify the prevention design.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`
- `reviews/worker_reports/giveaway-visual-publication-recovery-implement-01.md`
- `reviews/worker_reports/visual-main-list-freshness-recon-01.md`
- relevant current commercial shortlist/mailing/visual workflows, freshness receipts and contracts only as needed.

## Goal
Capture and explain the current broken end-to-end freshness state **before any repair**, with enough evidence to answer not only where the paid-list update stops, but why this class of failure was able to persist silently and whether it is structurally related to the earlier giveaway publication failure.

## Required forensic questions
1. What exact current path should move fresh Steam shortlist data into the canonical commercial mailing/visual publication?
2. Which exact edge/handoff in that path is absent, inactive, mis-triggered, blocked or semantically disconnected right now?
3. Was this handoff ever active? If evidence exists, identify when/how it stopped advancing. If not provable, state the narrowest proven boundary rather than guessing.
4. Is the failure due to a deleted/missing trigger, incompatible contract/version, stale provenance guard, workflow condition/scope mismatch, ownership split, schedule gap, or another exact mechanism?
5. Why does the existing system continue to look partly healthy while the paid list remains stale?
6. Which current checks/receipts prove upstream freshness but fail to prove end-to-end publication freshness?
7. Why did no existing guard automatically escalate or visibly mark the paid-list domain stale?
8. Compare against the earlier giveaway publication failure: what exact mechanism was different and what systemic pattern, if any, is shared?
9. Identify any fragile architectural pattern that could cause a third freshness domain to stop advancing in the future.
10. Record the exact pre-fix state needed to compare against the later repaired state: relevant source timestamps, accepted artifact identities, workflow/trigger state, freshness receipts/statuses, and published-domain freshness.

## Important boundaries
- READ-ONLY only.
- Do not repair the handoff.
- Do not re-run or mutate production workflows solely to change state.
- Do not manually refresh data.
- Do not edit schedules/triggers/writers/contracts.
- Do not create a second scheduler/writer/pipeline.
- Do not change Taste.
- Do not hide the stale state.
- Do not start `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`.

## Required output
Save exactly:
`reviews/worker_reports/publication-freshness-pre-fix-forensic-recon-01.md`

Follow `WORKER_REPORT_DURABILITY_PROTOCOL.md`: create this report early with `in_progress` before expensive investigation and checkpoint it during the task.

Report must include:
- final status exactly one of:
  - `complete_ready_for_repair`
  - `blocked`
- exact current end-to-end commercial publication path;
- exact current broken/disconnected boundary;
- whether the historical break point is proven or only bounded;
- why existing monitoring/freshness checks did not protect the user-visible result;
- comparison with giveaway incident: local difference + any common systemic pattern;
- frozen pre-fix evidence/identities/timestamps needed for later comparison;
- any architecture/reliability invariants the repair must preserve;
- whether `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md` is safe to run as currently written or needs one bounded correction before implementation.

Do not implement the repair in this task.

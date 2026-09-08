# WORKER TASK — Publication Freshness Recurrence Postmortem 01

## Task ID
`publication-freshness-recurrence-postmortem-01`

## Mode
`READ-ONLY / RECON / POSTMORTEM`

## Priority
`VERY_HIGH_RELIABILITY`

## Expected report
`reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`

## When to run
Run after the current main paid-list refresh recovery is durably accepted and user-verified, before moving on from the freshness incident family to unrelated backlog work.

## Why this task exists
This is not an isolated incident anymore.

Recent user-visible/reliability freshness failures include at least:
1. giveaway data was fresh upstream but failed to reach the published site until a section-level publication recovery was implemented;
2. the main paid-discount list continued showing a stale Aug-31 commercial snapshot even while Steam collection itself was still fresh, because the fresh shortlist was not reaching the canonical commercial publication path;
3. automatic ChatGPT semantic analysis last proved successful on 2026-09-01 21:03 UTC, fresh unresolved work existed on the next expected daily cycle, but no new ChatGPT result arrived and the system produced no prompt durable incident signal while the queue accumulated for days.

The purpose is to understand why independently refreshed domains can silently stop advancing, why existing health/freshness checks did not prevent a stale or partially stale user-visible system, and what systemic guard would prevent recurrence.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`
- `reviews/worker_reports/giveaway-visual-publication-recovery-implement-01.md`
- `reviews/worker_reports/visual-main-list-freshness-recon-01.md`
- `reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`
- `reviews/worker_reports/taste-daily-automation-failure-forensic-recon-01.md`
- relevant current freshness receipts/contracts/workflows only as needed.

## Goal
Produce a cross-incident root-cause/postmortem that separates:
- one-off local bugs;
- recurring architectural/process failure modes;
- missing monitoring/detection;
- missing automatic recovery/escalation;
- misleading user-facing freshness semantics.

Then recommend the smallest systemic prevention package that preserves the existing single-writer/fail-closed architecture.

## Required questions
1. For the giveaway incident, what exact condition allowed fresh upstream giveaway data to coexist with stale/empty user-visible publication?
2. For the paid-list incident, what exact condition allowed fresh Steam shortlist data to coexist with a stale published commercial list?
3. For the automatic ChatGPT incident, what exact proven boundary exists between fresh unresolved work and the missing next expected semantic result, and why did that absence remain silent for days?
4. What do all three incidents have in common, and which parts are genuinely separate local failures?
5. Why did existing workflows/receipts/fail-closed rules detect or suppress bad data but fail to ensure eventual fresh publication/progress?
6. Was there any durable alert/status that would have told the user/Director promptly that a domain had stopped advancing? If not, why not?
7. Which freshness domains exist today (paid deals, giveaways, ChatGPT semantic/Taste progress, Taste-dependent visual data, etc.) and which ones can advance independently?
8. What invariant should prove end-to-end health for each domain, e.g. `fresh source -> canonical handoff -> accepted artifact/result -> published/consumed state`?
9. What exact expected cadence and grace window should define these user-facing states for each daily domain:
   - `current` / «Данные актуальны»;
   - `delayed` / «Обновление задерживается»;
   - `stale` / «Данные не обновляются»?
   The rule must derive from the actual expected schedule plus a bounded grace period, not from artifact generation time alone.
10. What should happen automatically when a domain stops advancing beyond its allowed freshness window, so the user does not need to remember and compare dates manually?
11. Which regression/contract tests should catch a disconnected handoff, obsolete version guard, scoped-refresh mismatch, or missing semantic progress before multi-day production staleness reaches the user?
12. What user-visible freshness/status model prevents a partially fresh site from looking globally current? Paid deals, giveaways, and ChatGPT/Taste analysis must not mask one another.
13. What durable backend/system signal should exist for each domain when an expected daily refresh/progress event is missed, and where should it be surfaced without requiring a paid API or a second scheduler per domain?

## Prevention design constraints
- Do not create duplicate writers/schedulers for the same domain.
- Preserve fail-closed behavior.
- Prefer explicit end-to-end freshness receipts/health contracts over artifact mtime or commit time.
- Prefer one bounded health/alert mechanism that understands per-domain freshness over ad-hoc fixes.
- No paid API requirement.
- No manual daily checking by the user.
- Do not depend on ChatGPT Scheduled itself successfully running in order to detect that ChatGPT Scheduled has stopped running.
- No unrelated feature work.

## Required output
Save exactly:
`reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`

Report must include:
- incident timeline for giveaway, paid-list, and automatic ChatGPT failures;
- local root cause/bounded proven cause for each, without guessing unavailable historical scheduler state;
- common systemic cause(s), or an explicit finding where failures are unrelated;
- why the current safeguards were insufficient;
- missing detection/alert/recovery capability;
- proposed per-domain end-to-end freshness invariant;
- exact proposed `current/delayed/stale` rules and grace windows for paid deals, giveaways, and ChatGPT/Taste progress;
- proposed user-visible wording/placement that does not make a partially fresh site look globally current;
- proposed automatic durable missed-refresh/progress signal within the first missed day;
- exactly one bounded next reliability IMPLEMENT task, with acceptance criteria;
- whether an independent System Audit should follow that reliability implementation.

Final status exactly one of:
- `complete_reliability_action_required`
- `complete_no_common_systemic_defect`
- `blocked`

Create the exact report path early with status `in_progress` per `WORKER_REPORT_DURABILITY_PROTOCOL.md`, checkpoint it before long verification, and do not claim completion until the report is committed and re-read from `main`.

Do not implement the prevention package in this task.
Do not start another task.

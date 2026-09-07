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
Run after the current main paid-list refresh recovery is durably accepted, before moving on from the freshness incident family to unrelated backlog work.

## Why this task exists
This is not an isolated incident anymore.

Recent user-visible freshness failures include at least:
1. giveaway data was fresh upstream but failed to reach the published site until a section-level publication recovery was implemented;
2. the main paid-discount list continued showing a stale Aug-31 commercial snapshot even while Steam collection itself was still fresh, because the fresh shortlist was not reaching the canonical commercial publication path.

The purpose is to understand why publication/update paths can silently stop advancing, why existing health/freshness checks did not prevent a stale user-visible site, and what systemic guard would prevent recurrence.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`
- `reviews/worker_reports/giveaway-visual-publication-recovery-implement-01.md`
- `reviews/worker_reports/visual-main-list-freshness-recon-01.md`
- final report from `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
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
3. What do the incidents have in common, if anything?
4. Why did existing workflows/receipts/fail-closed rules detect or suppress bad data but fail to ensure eventual fresh publication?
5. Was there any durable alert/status that would have told the user/Director promptly that a domain had stopped advancing? If not, why not?
6. Which freshness domains exist today (paid deals, giveaways, Taste-dependent visual data, etc.) and which ones can advance independently?
7. What invariant should prove end-to-end health for each domain: `fresh source -> canonical handoff -> accepted artifact -> published site`?
8. What should happen automatically when a domain stops advancing beyond its allowed freshness window?
9. Which regression/contract tests should catch a disconnected handoff, obsolete version guard, or scoped-refresh mismatch before production staleness reaches the user?
10. What user-visible freshness/status model prevents a partially fresh site from looking globally current?

## Prevention design constraints
- Do not create duplicate writers/schedulers for the same domain.
- Preserve fail-closed behavior.
- Prefer explicit end-to-end freshness receipts/health contracts over artifact mtime or commit time.
- Prefer one bounded health/alert mechanism that understands per-domain freshness over ad-hoc fixes.
- No paid API requirement.
- No manual daily checking by the user.
- No unrelated feature work.

## Required output
Save exactly:
`reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`

Report must include:
- incident timeline for both giveaway and paid-list failures;
- local root cause for each;
- common systemic cause(s), or an explicit finding that they are unrelated;
- why the current safeguards were insufficient;
- missing detection/alert/recovery capability;
- proposed per-domain end-to-end freshness invariant;
- proposed user-visible stale/current semantics;
- exactly one bounded next reliability IMPLEMENT task, with acceptance criteria;
- whether an independent System Audit should follow that reliability implementation.

Final status exactly one of:
- `complete_reliability_action_required`
- `complete_no_common_systemic_defect`
- `blocked`

Do not implement the prevention package in this task.

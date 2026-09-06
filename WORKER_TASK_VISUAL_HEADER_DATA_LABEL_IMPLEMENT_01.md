# WORKER TASK — Visual Header Data Label Implement 01

## Task ID
`visual-header-data-label-implement-01`

## Mode
`IMPLEMENT / ACCEPTANCE`

## Priority
`HIGH_USER_VISIBLE`

## Expected report
`reviews/worker_reports/visual-header-data-label-implement-01.md`

## Direct predecessor
Read first:
`reviews/worker_reports/visual-header-data-date-recon-01.md`

Accepted predecessor conclusion:
- header currently renders `source_mailing_updated_at_utc`;
- the value means source mailing snapshot time, not universal page freshness;
- giveaway can refresh independently and therefore be fresher than this timestamp;
- the timestamp itself is technically correct;
- label `Данные:` is misleading;
- minimal fix: change only the label to `Рассылка:` while keeping the same field.

## Goal
Implement the smallest possible UX correction so the header accurately communicates what the displayed timestamp means.

## Required implementation
In the current frontend code path that renders the header, change only:

`Данные: <formatted source_mailing_updated_at_utc>`

to:

`Рассылка: <formatted source_mailing_updated_at_utc>`

Keep the timestamp source exactly the same:
`data.source_mailing_updated_at_utc`.

Do not substitute `generated_at_utc` or any giveaway timestamp.

## Hard boundaries
Do NOT:
- change any production JSON schema;
- change source timestamps;
- change giveaway data or refresh logic;
- change Taste/ranking logic;
- change deploy/freshness rules;
- change unrelated UI wording/design;
- add a second timestamp system in this task.

## Validation
Need focused verification that:
1. header now says `Рассылка:`;
2. the shown date/time value is still sourced from `source_mailing_updated_at_utc`;
3. giveaway remains visible/unchanged;
4. no runtime payload/schema change was introduced;
5. normal deploy path completes.

## User verification gate
After successful production deploy, mark whether Android verification is required. Do not claim final user-visible acceptance before Director/user verification.

## Final status — exactly one
- `complete_ready_for_user_verification`
- `blocked`
- `needs_followup_fix`

## Required report
Save exactly:
`reviews/worker_reports/visual-header-data-label-implement-01.md`

Include:
- status;
- exact file/line-level change;
- commit(s);
- focused validation;
- deploy evidence;
- explicit confirmation that timestamp source field was not changed;
- `ready_for_user_mobile_verification: true|false`;
- any remaining blocker.

Do not start another task.

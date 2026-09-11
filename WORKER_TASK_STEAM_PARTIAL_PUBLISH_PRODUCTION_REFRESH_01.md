# TASK — steam-partial-publish-production-refresh-01

Status: `authorized_dispatched_chat_1`
Mode: `IMPLEMENT_AND_PRODUCTION_ACCEPTANCE`

## Goal

Integrate the accepted Steam partial-publish implementation into current `main`, allow the canonical real Steam workflow to run, and verify the real production result under the new rules.

User has explicitly authorized the real production refresh.

## Accepted implementation source

Worker branch:
`worker/steam-partial-publish-failure-queue-01`

Accepted worker head:
`5556ce5c763d886a42b3c89ba69df711ba745adb`

Accepted report:
`reviews/worker_reports/steam-partial-publish-failure-queue-01.md`

## Required work

1. Integrate only the accepted implementation from the worker branch into current `main` safely.
   - Preserve intervening Director/task-board/task files already present on current `main`.
   - Do not blindly reset `main` to the old worker branch.
   - Integrate the implementation files/report needed for the accepted Steam partial-publish behavior.

2. The canonical workflow `.github/workflows/steam-test.yml` should then use:
   `python scripts/steam_partial_publish_runner.py`
   and run the focused partial-publish regression test first.

3. Allow/trigger the real canonical Steam production workflow after integration.
   - The user has explicitly authorized this real refresh.
   - Do not run a separate fake/full test crawl first.

4. Wait for the real workflow to finish and inspect the actual result.

5. Verify at minimum:
   - workflow run ID and final conclusion;
   - whether the Steam catalog publication completed;
   - number of successfully processed games/items reported by the partial-publish summary;
   - number and identities of unresolved known problematic games, if any;
   - number and exact descriptors of unresolved problematic catalog segments, if any;
   - number of system-state problems, if any;
   - whether any failed known game kept last-known-good data;
   - whether source metadata is `complete` or `partial` and why;
   - whether live total-count drift remained informational rather than causing a global failure;
   - whether production data was committed to `main`;
   - whether the downstream visual refresh/deploy was dispatched when production data changed;
   - whether the site is now using the refreshed ordinary Steam dataset.

6. If the real refresh exposes individual problematic games/segments:
   - DO NOT investigate or repair them in this task;
   - record them exactly in the report so the Director can surface them to the user for separate follow-up.

7. If the workflow fails for a new infrastructure/code reason:
   - do not perform broad unrelated repairs;
   - perform bounded self-diagnosis per worker protocol;
   - state exact failed step, first real error, proven/likely cause, what changed, retry safety, and smallest next action.

## Scope limits

Do not:
- work on giveaway decoupling beyond whatever the existing canonical workflow already does;
- create the queued ChatGPT error notification task;
- change Taste;
- start the queued Code Architect review;
- investigate individual Steam problem entries automatically;
- redesign unrelated project architecture.

## Durable report

Write:
`reviews/worker_reports/steam-partial-publish-production-refresh-01.md`

Report must include:
- integration method and resulting `main` commit SHA;
- workflow run ID / URL reference if available;
- final workflow conclusion;
- production summary counts;
- unresolved game list with AppID/key/name/stage/error when present;
- unresolved catalog segment list when present;
- system-state problem list when present;
- source complete/partial status;
- last-known-good preservation count/list when present;
- publication/commit result;
- downstream visual refresh/deploy dispatch/result known at report time;
- exact blockers or next action if not fully successful.

Final status must be exactly one of:
- `complete_real_steam_refresh_verified`
- `complete_with_problem_entries_for_separate_review`
- `blocked_requires_followup`

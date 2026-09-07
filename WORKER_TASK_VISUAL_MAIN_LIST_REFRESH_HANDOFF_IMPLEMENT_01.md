# WORKER TASK — Visual Main List Refresh Handoff Implement 01

## Task ID
`visual-main-list-refresh-handoff-implement-01`

## Mode
`IMPLEMENT / ACCEPTANCE`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`

## Direct predecessors
Read first:
- `reviews/worker_reports/visual-main-list-freshness-recon-01.md`
- `reviews/worker_reports/publication-freshness-pre-fix-forensic-recon-01.md`

Accepted forensic conclusion:
- the published paid-discount main list is stale and must not be treated as current;
- last proven commercial freshness represented by published paid `items` is the source snapshot shown to the user as `31 авг. 2026, 00:37`;
- fresh Steam -> shortlist -> mailing -> deterministic pre-AI commercial data is already working;
- the missing edge is narrower: deterministic commercial state -> canonical visual paid publication;
- existing helper `scripts/refresh_visual_commercial_fields.py` already performs the required scoped deterministic commercial refresh with preservation/provenance checks;
- `.github/workflows/build-daily-visual-payload.yml` has `giveaway_only` but lacks the analogous production `commercial_only` orchestration/receipt path;
- full visual rebuild must continue to fail closed when ChatGPT semantic payload is incomplete;
- do not modify the already-working Steam -> shortlist -> mailing handoff;
- do not hide the problem by deleting expired rows or changing the header cosmetically;
- freshness must be truthful by domain, with paid-list freshness independent from giveaway freshness.

## Bounded repair target
Repair ONLY the missing deterministic **commercial-only visual handoff** inside the existing canonical visual orchestration:
- reuse `scripts/refresh_visual_commercial_fields.py` from the current deterministic commercial/pre-AI source;
- wire it through the existing `.github/workflows/build-daily-visual-payload.yml` as a scoped `commercial_only` path;
- add/use a truthful scoped commercial freshness receipt;
- preserve giveaway state;
- leave the full semantic `ChatGPT production payload is not complete` fail-closed guard unchanged;
- do NOT modify the already-working Steam -> shortlist -> mailing handoff;
- do NOT add a scheduler, writer, or parallel pipeline.

This is a bounded orchestration repair, not a redesign.

## Goal
Make fresh deterministic commercial truth reach the existing canonical visual paid publication path even when the full semantic visual rebuild is correctly blocked by incomplete ChatGPT semantics.

Also expose/persist a truthful paid-list freshness timestamp/status that advances only after a successful canonical paid-list publication, without confusing it with giveaway freshness.

## Required implementation
1. Start from current `main`.
2. Read:
   - `CHAT_PROTOCOL.md`
   - `CHAT_CONTEXT.md`
   - `DIRECTOR_PROTOCOL.md`
   - both predecessor reports above;
   - `scripts/refresh_visual_commercial_fields.py`;
   - `.github/workflows/build-daily-visual-payload.yml`;
   - `scripts/visual_freshness_receipt.py`;
   - current canonical visual writer/deploy path and freshness contracts only as needed.
3. Implement only the missing `commercial_only` production-orchestration path in the existing visual workflow, reusing the existing commercial refresh helper.
4. Reuse existing canonical writer/build/deploy paths. Do not create a parallel commercial pipeline.
5. Preserve all helper provenance/coverage validation and fail closed if current source binding or prior semantic-row coverage is unsafe/incomplete.
6. Preserve the full semantic visual path and its ChatGPT-completion guard unchanged.
7. Extend/produce scoped freshness proof for `commercial_only` so it truthfully records the exact commercial lineage published and does not claim full visual freshness.
8. Execute/observe the normal route and prove current deterministic commercial source reaches published paid `items`.
9. Ensure rows whose sales have ended are no longer retained merely because the old commercial snapshot never advanced.
10. Persist/expose truthful paid-list freshness identity/timestamp based on the successful canonical paid-list refresh/publication event.
11. Keep giveaway freshness/state independent and prove the commercial-only refresh preserves giveaway state. A giveaway-only refresh must not advance paid-list freshness.
12. If the current frontend already has a suitable status location, implement the minimum truthful display for paid-list freshness/staleness. If a UI change would require a broader redesign, keep this task to the smallest safe display necessary for acceptance and report any follow-up separately.

## Hard boundaries
Do NOT:
- modify/rebuild the already-working Steam -> shortlist -> mailing handoff unless required only to read its current provenance for validation;
- create a second scheduler for the same commercial refresh purpose;
- create a second commercial writer;
- create a parallel mailing source;
- create a parallel visual/commercial pipeline;
- manually patch prices, rows, caches, handoffs or production visual JSON;
- manually delete expired games;
- weaken freshness, provenance, semantic-completeness, or fail-closed gates;
- bypass the existing commercial helper's source-binding or semantic-row coverage checks;
- fake a new timestamp from artifact generation time alone;
- let giveaway-only publication advance paid-list freshness;
- change Taste recommendation semantics/ranking;
- run or modify the Taste Scheduled Task;
- use paid OpenAI API or Copilot;
- work on unrelated backlog.

## Acceptance
Status `complete_ready_for_user_verification` only if:
1. the existing current deterministic commercial/pre-AI source reaches the canonical paid-list visual writer through the new scoped `commercial_only` orchestration;
2. the existing canonical visual writer publishes fresh paid `items`;
3. normal deploy/publication succeeds;
4. the paid-list source freshness is newer than the stale 31 Aug snapshot and is tied to the actually published paid items/current deterministic source lineage;
5. expired rows from the old snapshot are not present merely due to stale carryover;
6. no second scheduler/writer/pipeline was created and Steam -> shortlist -> mailing was not unnecessarily changed;
7. giveaway remains independently functional and its state is preserved by commercial-only refresh;
8. paid-list freshness shown/persisted to the user cannot be advanced by giveaway-only refresh;
9. scoped commercial freshness receipt/proof records exact source/output lineage and does not claim `full_visual_freshness=true` merely because commercial fields refreshed;
10. full semantic ChatGPT-completion guard remains fail closed and unchanged in meaning;
11. no Taste semantics were changed.

## Final status — exactly one
- `complete_ready_for_user_verification`
- `blocked`
- `needs_followup_fix`

## Required report
Save exactly:
`reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`

Create this exact report path early with status `in_progress` per `WORKER_REPORT_DURABILITY_PROTOCOL.md`, checkpoint it before long acceptance/workflow verification, and do not claim completion until it is committed and re-read from `main`.

Include:
- final status;
- exact root implementation change;
- commit(s);
- exact workflows/runs used for acceptance;
- proof current deterministic commercial source reached canonical paid `items`;
- old vs new paid-list freshness identity/timestamp;
- proof the timestamp/status is tied to the published paid list, not artifact time or giveaway time;
- scoped `commercial_only` receipt/proof and exact lineage;
- proof giveaway state was preserved;
- proof full semantic guard was not weakened;
- proof no duplicate scheduler/writer/pipeline was added and healthy Steam -> shortlist -> mailing was not altered unnecessarily;
- deploy evidence;
- whether Android verification can now begin;
- any remaining blocker.

Do not start another task.

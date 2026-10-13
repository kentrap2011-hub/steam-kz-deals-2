# Worker report — Deep versioned history PR #222 closeout 01

**Task:** `WORKER_TASK_DEEP_VERSIONED_HISTORY_PR222_CLOSEOUT_01.md`  
**Scope:** independent ACCEPTANCE review, bounded PR-scoped corrections.  
**Repository / branch:** `kentrap2011-hub/steam-kz-deals-2` / `implement/deep-versioned-history-first-core-01`  
**PR:** https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/222  
**Tested implementation head:** `a235108e7bc17eda3308ec5af0b94a74f0eeaec2` (report/handoff documentation commits follow).  
**Status:** `accepted_for_director_merge_review_producer_only`; **not merged**.  
**Review date:** 2026-10-13 UTC.

## START, architecture and independent acceptance

Read current `main` CHAT_PROTOCOL.md, CHAT_CONTEXT.md, both exact worker tasks, original PR #222 worker report, relevant Deep PROJECT_ROUTES.md, CURRENT_TASK.md and ownership/PASS2/personalization contracts. GitHub remains owner of current Deep eligibility/order, immutable profile and Dossier bindings, attempt/recovery accounting, version-history persistence, projections and publication. No interactive or Scheduled Task is made a production executor; no new retry authority/queue/scheduler is introduced. Frozen Deep two-stage activation and UI remain out of scope.

Independently checked PR #222 changes to `scripts/progressive_deep_history.py`, `scripts/progressive_pass2.py`, `scripts/build_progressive_pass2_work.py`, `scripts/progressive_personalization.py`, contracts and regressions. Canonical accepted successes remain separately recoverable from V1 additive history, V2 root and legacy revision_history, including punctuation/profile-content changes and later incomplete attempts; byte-identical provenance-only commits remain one content version. Historic source pin uncertainty is not disguised as an attested version. Order is current eligible never-successful first, then oldest **last successful** timestamp, with exact-game tie breaking. Fast is not a prerequisite; stale Deep is never promoted into current scoring/ranking or an unauthorized retry. Statistics deduplicate per actual game/profile version; the 30 legacy and 43 score migration targets are not summed as disjoint groups. This is a producer-only phase and does not claim website rendering changes.

## Confirmed defect and bounded correction

**Confirmed:** `completed_versions()` silently overwrote conflicting V1 rows sharing a revision ID, and did not check stored accepted timestamp versus the immutable result or historical profile pin association. Such contradictions could falsify provenance/statistics. Hardened fail-closed checks against mismatched row timestamps, profile pins and conflicting duplicate V1 revisions; protected already-attested immutable completions from conflicting replacement in `preserve_completion()`. Retained legitimate one-time attestation of the *same* newly accepted V2 root (not mutation of a different completed result). Added targeted regressions for conflicting duplicate content, mismatched accepted time and mismatched version pin.

Initial strengthened guard exposed a test-fixture profile-pin mismatch and disallowed the legitimate just-accepted-root attestation: `Validate Progressive PASS 2 core` run `38451810892` failed specifically at that new regression. Repaired fixture to use the exact pinned profile and constrained the guard to permit identical-result root attestation while rejecting actual conflicting revisions. **Final source head `a235108...` checks passed:**
- `Validate Progressive PASS 2 core`: run **38451997073**, success; includes new history regression and existing core/profile/ordering/ingest checks.
- `Validate site publication resilience`: run **38451997144**, success.
- `Validate Deep Stage 1 migration preparation`: run **38451997056**, success.
- `Validate backlog dispositions`: run **38451997420**, success.

CI is authoritative evidence here; local full checkout was unavailable because the container could not resolve github.com. No unsupported local test success is claimed.

## Mergeability, limitations, Director action

Raw GitHub PR API recheck for the tested implementation head: `mergeable=true`, `mergeable_state=clean`, no inline review threads or review submissions. Earlier connector `mergeable=false` was a stale/non-final result; raw API temporarily reported `mergeable=null`/`unknown`, then confirmed clean, **not a proven file conflict**. `main` advanced by 96 mostly GitHub-owned production commits since merge base; non-overlapping live-state commits were not force-rebased or rewritten. PR was still draft during this check; ready-for-review conversion is an administrative closeout step, not a merge.

**Bounded limitations:** historical accepted revisions no longer represented by V2 root/revision_history cannot be fabricated; recovering them would require separate exact Git-attested accepted provenance and an authorized backfill. Sept 30's 47 completed versus Oct 13's 8 compatible are different snapshots, not proof of deletion. The frozen profile pin has content identity and source commit SHA but no independently attested **Git source commit timestamp**, so both historical and current profile version date fields remain null unless a separate GitHub-proven provenance task supplies the date. Site cards/Statistics still need their own user-approved presentation phase; no `web/**` change was made.

**One recommended Director action:** review and merge PR #222 after confirming its final green checks; then assign the separately scoped Git-proven profile-date provenance and site cards/Statistics work. Do not interpret producer acceptance as UI deployment.

No PR merge, Dossier/Fast changes, live-state writes, semantic backlog run, mass history migration, two-stage cutover or Scheduled Task mutation.

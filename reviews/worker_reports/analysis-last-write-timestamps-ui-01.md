# Analysis last write timestamps UI 01

## Task

Implement `WORKER_TASK_ANALYSIS_LAST_WRITE_TIMESTAMPS_UI_01.md`: add a visible, machine-readable and producer-owned `Последняя запись` time for Fast / Dossier / Deep on the existing Statistics page, without changing any stage execution semantics.

Repository: `kentrap2011-hub/steam-kz-deals-2`  
Implementation PR: #104  
Merge commit: `132baf949178b7d57dd164c2ab12cd5d1d890082`

## Architecture preflight

1. GitHub remains the canonical owner of state, persistence, aggregate projection, validation and publication.
2. The browser remains `read_only_presentation`: it receives timestamp values from `processing_status` and only formats them for the viewer's local timezone.
3. No control-plane responsibility moved to the browser or Scheduled Task.
4. No scheduler, heartbeat, watchdog, poller, queue, retry owner, checkpoint owner or semantic stage was added.
5. Fast/Dossier/Deep eligibility, order, recovery, completeness, attempt accounting and effective-result precedence are unchanged.
6. Dossier worker execution/evidence/recovery code was not modified. No Fast/Dossier/Deep backlog item was manually processed. No Scheduled Task setting or run was changed.

No new project-level architecture decision was required; this is an additive observability projection under the existing ownership contract.

## Timestamp definitions

### Fast / PASS 1

Field: `fast_last_write_at_utc`.

Definition: latest `accepted_at_utc` among current exact-bound durable PASS 1 state records that belong to the current Fast statistics scope.

Historical/stale PASS 1 state from another current binding is not used. If the current Fast scope has no accepted current record, the value is `null`.

### Dossier

Field: `dossier_last_write_at_utc`.

The current Dossier manifest does not store a direct accepted timestamp on successful group transitions. The GitHub-owned visual producer therefore derives the timestamp from durable Git history of the canonical `data/production/pre_ai/taste_steam_review_dossier_work.json` for the current snapshot.

A timestamp is recorded only when canonical `group_progress` enters either:

- `accepted`; or
- `failed_or_invalid_pending_recovery`.

The value is the GitHub commit time of the latest such current-snapshot transition. A later manifest rewrite with no classification transition does not advance the value. Buffered/unaccepted candidate creation time is excluded.

If there is no trustworthy current-snapshot classified transition, the value is `null`.

### Deep / PASS 2

Field: `deep_last_write_at_utc`.

Definition: latest `accepted_at_utc` among current exact-bound durable PASS 2 state records in the current Deep statistics scope.

If the current scope has no accepted durable Deep record, the value is `null`.

### UI rule

All producer values are UTC ISO-8601 strings or `null`. The UI only calls `Date(...).toLocaleString('ru-RU', {dateStyle:'short', timeStyle:'short'})` without setting a timezone, so the browser renders the viewer's local timezone.

Null/invalid presentation is fail-safe:

`Последняя запись: ещё не было записей`.

Page load time, visual build time, deploy time, Scheduled Task run time, counts and inbox/candidate timestamps are never used as substitutes.

## Changes

- `scripts/progressive_personalization.py`
  - projects current Fast/Deep durable timestamps from the exact-bound current state entries;
  - derives Dossier current-snapshot transition time from canonical Git history;
  - publishes the three top-level fields and corresponding nested stage-count fields;
  - validates timestamp presence/type while leaving all existing arithmetic invariants unchanged.
- `config/progressive_personalization_contract.json`
  - documents the three timestamp fields, UTC/null semantics, producer ownership and browser formatting-only rule.
- `scripts/progressive_visual_activation_routing.py`
  - requires all three timestamp fields to exist in a compatible Progressive visual payload; `null` remains valid.
- `web/progressive-personalization-ui.js`, `web/app.js`, `web/styles.css`, `web/index.html`
  - expose `Последняя запись` under each stage in Statistics;
  - format only the supplied value;
  - add responsive styling and cache-bust changed browser assets.
- Focused regressions were added to `scripts/test_progressive_personalization.py`, `scripts/test_progressive_visual_activation_routing.py` and `web/progressive-personalization-ui.test.js`.

## Parallel reconciliation

The worker branch started from fresh `main` at `46b236309e4e068f6fbe03afc98d2c52a2c8daab`.

During implementation, concurrent production Dossier writes advanced `main`. Immediately before merge, fresh `main` was reread at `8f2e58c6d484e43feaff9380d41009dd9b737528`. The commits since the PR base changed only Dossier production/audit/quarantine data and generated `data/production/visual/current.json`; none overlapped the source/config/UI files modified by PR #104.

The Russian-description work from ЧАТ 1 was already present in the base, including implementation `f950944b1e9e7ee4433e0ed90c4d262b6ac24c91` and its publication closeout. PR #104 was merged with expected head `9c018fb7370337845afed9acd2758df4b90d018c`, producing merge `132baf949178b7d57dd164c2ab12cd5d1d890082` without replacing concurrent production data.

A later ЧАТ 1 acceptance commit `8ba1313142b2343f747dcd23aca131fc24840080` is also preserved; this report/closeout was prepared from fresh `main` after that commit.

## Validation

### PR / source validation

- PR #104 Progressive PASS 2 core: run `36340958074` — success.
  - Progressive personalization regression — success.
  - Visual activation routing regression — success.
  - PASS 1 and PASS 2 regressions — success.
- PR package/browser validation: run `36340958023` — success, including changed JavaScript syntax validation.
- PR backlog disposition validation: run `36340957832` — success.
- Post-merge Progressive PASS 2 core: run `36341084282` — success.

Focused regression coverage proves:

- Fast selects the latest supplied durable current-stage timestamp, not generic analysis/build time.
- Dossier advances only on current-snapshot accepted/failed canonical transitions; a later no-transition rewrite does not act as a heartbeat.
- Deep selects the latest supplied durable current-stage timestamp.
- No current record yields `null`.
- `stamp_processing_status()` carries the fields through the normal visual producer path.
- Browser Statistics sections use only the three supplied fields, and the formatter contains no `Date.now()` progress inference.
- Adding/removing only the timestamp inputs leaves all pre-existing processing-status fields/counts identical.

### Normal production publication

- Merge: `132baf949178b7d57dd164c2ab12cd5d1d890082`.
- Normal `Build daily visual payload` run #813: `36341084329` — success.
  - Progressive tests passed in the build.
  - `VISUAL_FINAL_BUILD=BUILT`.
  - resulting visual commit: `0d02729f1cd3589fc9a4504e7a4020a769d20e1d`.
- Following Pages deploy #853: `36341118795` — success.
  - explicitly downloaded freshness receipt from build run `36341084329`;
  - staged `visual_commit=0d02729f1cd3589fc9a4504e7a4020a769d20e1d`;
  - `Run UI regressions` — success;
  - GitHub Pages deploy — success;
  - Pages artifact: `10938613629`.
- Subsequent normal commercial-preserving deploy #854: `36341150523` — success; Pages artifact `10938673520`; the new timestamps and UI assets remained present.

### Published artifact verification

Direct inspection of Pages artifact `10938613629` confirmed:

- `fast_last_write_at_utc = null`;
- `dossier_last_write_at_utc = 2026-09-27T18:32:06+00:00`;
- `deep_last_write_at_utc = 2026-09-27T17:36:44+00:00`;
- the deployed `app.js` contains the `Последняя запись:` rendering;
- the deployed formatter is present;
- `index.html` references cache-busted `analysis-last-write-timestamps-ui-01` assets.

Fast is intentionally null in this published current scope because the same payload has `fast_attempted_count = 0`; the UI therefore shows `Последняя запись: ещё не было записей` instead of borrowing historical Fast time.

Published stage counts in that artifact:

- Fast: total `397`, attempted `0`, skipped by authoritative Deep `29`, remaining `368`;
- Dossier: total `418`, accepted `42`, pending `346`, failed/recovery `30`;
- Deep: total `397`, first-pass attempted `29`, authoritative completed `29`, remaining `368`.

A deployed pre-feature control artifact from deploy #851 (`36341051175`, artifact `10938917257`) was compared with artifact `10938613629`. After removing only the new timestamp keys, the full `processing_status` objects were identical. The canonical provenance blobs also matched exactly:

- Dossier work: `1a1a9c233888355149868eecdfcabbdd24367732`;
- PASS 1 state: `7ada757c14f44ee62001b04a6f05d62d306913dd`;
- PASS 2 state: `dd0bbb5150fad574a1ef17bbe0eaab440de050d6`.

This proves the observability change did not alter stage counts or source provenance.

## Published result

The Statistics page now exposes a separate `Последняя запись` line for Fast, Dossier and Deep.

It is a durable-progress timestamp, not a heartbeat:

- current Fast with no accepted current record safely says there have not yet been records;
- Dossier shows the last canonical current-snapshot accepted/failed group transition;
- Deep shows the last accepted current PASS 2 record;
- the visible clock is converted only by the browser to the viewer's local timezone.

## Unresolved

None within this task's scope.

Ongoing Fast/Dossier/Deep work may naturally advance these values later through the existing canonical pipelines; no monitoring or retry mechanism was added.

## Status

`complete_ready_for_director_acceptance`.

## Recommended next step

Director acceptance only: open the already deployed Statistics page once on a phone-width viewport and confirm the three `Последняя запись` lines are visually comfortable to read; do not run or change any worker/Scheduled Task for this check.

## Efficiency / reusable lesson

When a canonical state transition lacks its own timestamp field, Git commit history of the canonical state file can provide a durable persistence time without modifying the worker or inventing a heartbeat. The safe pattern is: bind to the current snapshot, detect only meaningful state transitions, return `null` when proof is absent, and keep browser logic formatting-only.

# DIRECTOR HANDOFF — CURRENT

Repository: `kentrap2011-hub/steam-kz-deals-2`
Branch: `main`
Purpose: compact handoff for a replacement Director chat without replaying prior conversation history.

## Start here

Read in this order:
1. `DIRECTOR_PROTOCOL.md`
2. `DIRECTOR_HANDOFF_CURRENT.md`
3. `DIRECTOR_TASK_BOARD.md`
4. `DIRECTOR_REVIEW_CHECKPOINTS.md`

Do not broadly inspect Git history, workflow history, old tasks, artifacts or source code just to rebuild context. Use exact current reports and minimum evidence. The Director delegates investigation/implementation to worker chats.

## User communication / operating rules

- Russian, direct and practical.
- Always label worker instructions as **НОВЫЙ ЧАТ** or **СУЩЕСТВУЮЩИЙ ЧАТ**.
- Prefer copyable code blocks for worker commands.
- Do not claim UI/user-visible incident fixed before actual device/site verification where required.
- The user explicitly asked the Director not to spend time/context manually following CI/log/history. If a check becomes nontrivial, delegate it to the worker chat.
- If Director preparation takes >1 minute, visibly explain what is taking time instead of silently waiting.

## Current live worker state

### ЧАТ 1 — visual freshness release closeout only

Task:
`WORKER_TASK_VISUAL_FRESHNESS_RELEASE_01.md`

Report:
`reviews/worker_reports/visual-freshness-release-01.md`

Current situation:
- accepted visual-freshness fix has already landed unchanged on `main` via PR #13;
- landing commit: `ddbf25d855f3ed7b86aca5ecbebb834e87178012`;
- production build run `33788418064` failed upstream on `ChatGPT production payload is not complete`;
- freshness protection itself worked correctly and emitted truthful `fresh_build=false / degraded/no_fresh_build` and uploaded its receipt artifact;
- resulting workflow-run deploy `33788465486` was correctly skipped;
- exact triggering-run binding is installed on `main`, but a successful build->deploy chain has not yet dynamically exercised it.

Important closeout issue:
- worker report used status `STOP`, which is not an allowed task status.
- Existing Chat 1 was instructed to change only the report status to an allowed exact status (likely `blocked` based on existing evidence), with **no new investigation or implementation**.

Do not give Chat 1 new work until this status-only closeout is saved. After canonical closeout, Chat 1 can be deleted.

Separate prepared recon for the upstream blocker:
`WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md`
Expected report:
`reviews/worker_reports/visual-build-input-incomplete-recon-01.md`

Do not start it before mandatory review ordering permits, unless a more urgent concrete production problem justifies it.

### ЧАТ 2 — Epic final CI closeout only

Recon report:
`reviews/worker_reports/epic-giveaway-schema-recon-01.md`
blob `32d487e13a916424693bd05d0d0ced41cf688bc2`

Fix task:
`WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_FIX_01.md`

Fix report:
`reviews/worker_reports/epic-giveaway-schema-fix-01.md`
blob at first closeout: `4e79874e4d4d0b4ed9d101ec7dba8791686dd69b`

Implemented:
- parser now identifies current 100% Epic promotion first;
- irrelevant/non-current elements can be skipped without requiring `price.totalPrice`;
- actual current giveaways still require strict/fail-closed price contract;
- no ITAD/IGDB/title guessing/fallback source was added.

Key refs:
- parser fix commit: `aa7cea8d06d4d71a5ff6fe4c23a71c2cbda28783`;
- regression commit: `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`;
- canonical code-run `33790369125` completed `success`;
- regression run `33790442843` was still running when the previous Director last checked.

Production itself is already recovered:
- `data/production/giveaways/v1/current.json` is `snapshot_status=complete`;
- Epic is `status=ok`, `complete=true`;
- Epic candidate_count `1`, accepted_count `1`;
- active giveaway is `Alone With You`, 100% discount, KZ available;
- no Epic source error.

The user explicitly asked not to have the Director keep polling this CI. Existing Chat 2 was instructed to wait/check run `33790442843` itself, then update the fix report with final CI evidence and final allowed Status, without new implementation or ITAD work.

Do not delete Chat 2 until it reports final closeout.

## Mandatory review checkpoint — currently DUE

`DIRECTOR_REVIEW_CHECKPOINTS.md` currently has:
`system_audit_due: true`

Reason:
The user-visible Epic giveaway incident has now been stabilized in production.

Prepared short audit:
`WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md`

Expected report:
`reviews/system_audits/epic-post-incident-audit-01.md`

Start this only after the existing Epic fix Chat 2 has final closeout. It should be a **NEW Chat 2** (or whichever slot is free) and is READ-ONLY/AUDIT.

Until this mandatory audit completes, do not start ordinary backlog/ITAD work unless the user explicitly gives a more urgent concrete production priority.

## Mobile feed incident — CLOSED and user accepted

Original mobile blank/loading incident is fixed.

Final production cache-first release:
`f745dac844213880cd7eb984573877f58803a3f0`

Pages run:
`33779042331` success.

User real-device acceptance on affected Android phone:
`works`.

Post-incident audit:
`reviews/system_audits/mobile-post-incident-audit-01.md`
blob `db07eb4f7848d18e3a8cc62d5cb754e245695db4`

Systemic conclusion:
- canonical `data/current.json` remains source of truth;
- browser Cache Storage is only one bounded last-known-good presentation fallback;
- no second renderer, polling, service worker, scheduler or unbounded client data plane.

Remaining bounded follow-up:
`WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`

Goal only:
wire existing `tests/feed-bootstrap.test.js` into canonical Pages deploy regression gate and prove one passing normal Pages run. No client redesign.

Prepared, not next while mandatory Epic post-incident audit is due.

## Visual freshness — code active, full successful-chain proof pending

Accepted implementation:
- `reviews/worker_reports/visual-freshness-chain-fix-01.md`
- final acceptance `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`

The protection is now on production `main` and has already proved truthful degraded/no-fresh-build behavior.

Do NOT reopen/redesign the freshness solution just because the first production cycle could not complete the stronger successful-build -> exact-run deploy proof. The blocker is upstream payload completeness, not the accepted freshness receipt design.

If `ChatGPT production payload is not complete` remains a real blocker after mandatory review, use the already prepared bounded recon:
`WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md`.

## Semantic runtime / completeness

Semantic runtime heartbeat/observability fix is accepted and closed.

Final acceptance:
`reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`
blob `5b4a25c89845ab258651a30608658e90d7d1840d`.

System Audit 02 still left one separate UI-truth gap:
canonical degraded/incomplete semantic state is not visibly surfaced to the user. This is later bounded work, not reason to reopen runtime implementation now.

## Giveaway identity — ITAD prepared, NOT started

Provider permission is confirmed.

Prepared task:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`

Architecture:
- provider-neutral identity interface;
- active provider `itad`;
- reserved future provider `igdb`;
- no automatic fallback / dual voting;
- downstream Steam identity consumer remains provider-agnostic.

Status:
`prepared_not_started`.

Do not start before current mandatory Epic post-incident audit and more urgent production blockers are cleared, unless user explicitly reprioritizes.

Twitch/IGDB remains waiting on Twitch Support.

## Taste Reviewer

Baseline report:
`reviews/taste_reviews/baseline-01.md`
blob `f243047d9bbb3d8515e7929e2962da66688243c4`.

Advisory only. Material Taste/ranking policy changes require a current Taste Review checkpoint before acceptance.

## Operational health watch

An hourly ChatGPT automation named `Steam KZ Health Watch` was created.

Purpose:
- check canonical project health;
- notify only on new/materially worsened production problems;
- known tracked incidents should not generate duplicate alerts.

This monitoring layer is not a second canonical scheduler/writer and must not become one.

## Priority order right now

Unless the user explicitly changes priority:
1. Get **existing Chat 1** status-only visual-freshness report closeout; then delete it.
2. Get **existing Chat 2** final CI/report closeout for Epic; then delete it.
3. Start **NEW audit chat** for `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md` because `system_audit_due=true`.
4. After audit, choose between the concrete visual-build-input blocker recon and the prepared mobile deploy regression gate based on current production state; the visual-build blocker is likely higher priority if still active.
5. ITAD implementation only after current review/production blockers permit it.

## Context-protection rule

The replacement Director must preserve this strictly:
- exact expected report first;
- minimum current evidence only;
- no broad Git/workflow/history archaeology;
- do not manually follow long-running CI if a worker chat can own that follow-up;
- delegate investigation and implementation;
- keep Director responses fast and decision-oriented.

## Source of truth

If this handoff conflicts with a newer `DIRECTOR_TASK_BOARD.md`, `DIRECTOR_REVIEW_CHECKPOINTS.md`, or exact newer worker report, prefer the newer durable evidence and update this handoff. Do not use chat memory as the final authority.
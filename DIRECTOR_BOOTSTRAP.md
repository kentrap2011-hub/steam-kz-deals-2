# DIRECTOR BOOTSTRAP

Last refreshed: 2026-09-27

Purpose: compact restart context for a **NEW physical Director conversation** after the previous Director chat reached its context limit.

This file is a bootstrap snapshot, not a replacement for canonical project truth. The new Director must read current `CHAT_PROTOCOL.md`, `DIRECTOR_PROTOCOL.md`, and fresh `DIRECTOR_TASK_BOARD.md` first. Newer canonical GitHub state always wins over this file.

## Repository scope

Repository: `kentrap2011-hub/steam-kz-deals-2`  
Base branch / source of truth: `main`

Use only this repository unless an exact task explicitly authorizes another repository.

## Director operating rules

- Director orchestrates; worker chats perform nontrivial project investigation/implementation.
- GitHub owns production control-plane state.
- Do not turn the Director chat into the Dossier/Fast/Deep production worker or backlog manager.
- No nontrivial IMPLEMENT without explicit user authorization.
- Before any decision/handoff: reconcile fresh Board -> exact task -> exact durable report.
- For a new worker task, write the full instruction into `WORKER_TASK.md` / exact `WORKER_TASK_*.md`, then give the user only the short protocol-entry launch prompt.
- Every launch prompt must name repository, `main`, repository guard, `CHAT_PROTOCOL.md` START gate, exact task file, slot number, and whether the physical worker chat is NEW or EXISTING.
- Retired physical worker chats are not reused for unrelated work. Slot numbers `ЧАТ 1/2` may be reused only with an explicitly NEW physical chat.
- The user personally controls ChatGPT Scheduled Task UI. Do not create/edit/enable/disable/pause/delete/reschedule/rename/recreate/run a Scheduled Task unless the user explicitly requests that exact action.
- User prefers project explanations in simple Russian with minimal untranslated technical terminology. Exact filenames, statuses, errors and identifiers may remain literal.

## Current Director state

There is **no currently assigned top-level worker task**.

Latest Director Board current-state commit before this bootstrap:
`0cdb6c1cc48410413f29359aef25c0914d1ce2f6`

The Board now has a top `CURRENT DIRECTOR STATE — 2026-09-27` section. Older lower Board sections with headings such as `ACTIVE`, `LIVE`, or `PAUSED` are historical records and may be stale; do not revive them without fresh verification.

Latest physical worker chats are retired:
- ЧАТ 1 — Dossier production failure diagnostic;
- ЧАТ 2 — GitHub-derived Dossier dates + ingest atomicity fix.

Both may be deleted.

## Current Dossier architecture — important accepted rules

### Purpose / completeness

Dossier prepares a **neutral, sufficiently complete picture of the exact game** for later personalized Deep analysis.

Accepted rules:
- Dossier itself is profile-agnostic;
- completeness/downstream usefulness outrank speed/tool minimization;
- 12 neutral experience dimensions are assessed;
- materially unresolved important dimensions prevent a sufficient/stable Dossier;
- narrow evidence such as only localization or one isolated complaint is not enough when broader relevant evidence remains reasonably discoverable;
- no fixed minimum review/source/search/page count;
- retrieval is semantically/adaptively bounded, not controlled by old 8-search/16-page limits.

Relevant accepted decision family: TASTE-014 / TASTE-015.

### Pragmatic player evidence model

Accepted implementation:
`WORKER_TASK_TASTE_DOSSIER_PRAGMATIC_EVIDENCE_MODEL_FIX_01.md`

Report:
`reviews/worker_reports/taste-dossier-pragmatic-evidence-model-fix-01.md`

PR #98 merged as:
`d3b0e40256b31b5444fe7c5ddd8ced49c078b81c`

Current evidence principles:
- exact-product/AppID/release/DLC/remake identity remains strict;
- useful concrete player feedback directly observed in a search-result representation or exact-product collection/card may be used even without a permanent per-review locator or author identity;
- raw review/search-result text, quotes, usernames/profile identifiers are not persisted;
- permanent per-item locator is useful auditability, not a validity requirement;
- exact per-review counting is not a completion threshold;
- recurrence is qualitative/evidence-grounded;
- Russian `found_and_used` depends on actual usable observed Russian/mixed player feedback, not on permanent item identity.

### GitHub-derived dates — latest accepted change

Task:
`WORKER_TASK_TASTE_DOSSIER_GITHUB_DATE_DERIVATION_AND_INGEST_ATOMICITY_FIX_01.md`

Report:
`reviews/worker_reports/taste-dossier-github-date-derivation-and-ingest-atomicity-fix-01.md`

PR #99 merged to `main` as:
`5a296a98b256ea32ea1e0eb6e7d05b64ebefffc3`

Director acceptance commit:
`fea60f54b5d007c458f62b1889e765b01a526ff1`

Full validation was green:
- buffered Dossier validation: `36312723478`;
- Progressive PASS 2 core: `36312723454`;
- backlog dispositions: `36312723552`.

User-approved responsibility model:
- Scheduled semantic worker records only factual `publication_date` or `null`;
- worker no longer decides `recent / older / unknown`;
- GitHub derives temporal state deterministically under the unchanged 365-day boundary;
- <=365 days = recent;
- >365 days = older;
- unknown date = unknown, never assumed recent;
- current-state claims requiring recent support must use actual supporting feedback dates;
- mixed old/recent feedback under one parent is classified per supporting record, not by a guessed parent-page freshness label.

Current active Dossier binding:
`github-derived-temporal-classification-2026-09-27`

### Failed-group audit/quarantine atomicity — latest accepted change

The production diagnostic proved that failed-group audit and quarantine outputs were intentional, but the old workflow could leave them unstaged because it used one combined optional-path `git add` with a missing `data/control` path and suppressed the failure.

PR #99 fixed this:
- optional paths are staged independently;
- staging errors are no longer broadly hidden;
- failed-group audit/quarantine remain canonical outputs;
- after the local canonical commit and before rebase/push, GitHub checks `git status --porcelain --untracked-files=all`;
- if any leftover exists, workflow fails and prints the exact paths;
- no stash/discard/implicit unknown-file add is used.

## Production incident that led to the fix

Diagnostic task:
`WORKER_TASK_TASTE_DOSSIER_PRODUCTION_FAILURE_DIAGNOSTIC_01.md`

Report:
`reviews/worker_reports/taste-dossier-production-failure-diagnostic-01.md`

Old production snapshot:
`b98f8691529d9c4d1bdf66227f08537fbb5dd385ba8798280da05aa98f4054d5`

Old sequence 1 candidate contained:
- Crown Trick / 1000010;
- Tiny Snow / 1002560;
- EARTH DEFENSE FORCE 5 / 1007040.

Candidate commit:
`2a3a2e2dbd99faf784f22878f0b7ec2252d1f5fa`

Failed ingest run:
`36241650284`

What was proven:
1. Tiny Snow had real temporal contradictions under the old worker-authored freshness model.
2. GitHub correctly classified the old group as failed in the runner working tree.
3. Separate staging bug prevented that failed state from reaching `main`.
4. The two defects were independent and were both fixed structurally by PR #99.

Do **not** manually rewrite or repair that old candidate.

## Current Dossier production state

Fresh current state after the binding change:

Current snapshot:
`81e44a924e2df85dcd3acab12954c12a5b2a04ab42f09405460a53d42ea241ea`

Current binding:
`github-derived-temporal-classification-2026-09-27`

Current projection at the last Director check:
- next pending sequence: 1;
- accepted groups: 0;
- failed groups: 0;
- pending groups: 140;
- remaining required dossiers: 418;
- full backlog complete: false.

Important consequence:
the old failed experiment snapshot `b98f...` is no longer the current snapshot.

Therefore the new Director must **not automatically issue recovery for old g000001**. Before any recovery/reconciliation action, do a bounded READ-ONLY current-state check to determine whether the old snapshot needs any explicit cleanup at all or is already superseded by normal binding/snapshot rollover.

No recovery action is currently authorized.

## Fast / Dossier / Deep architecture

Accepted high-level model:
- Fast / PASS 1 = provisional personalized analysis;
- Dossier = independent neutral evidence preparation;
- Deep / PASS 2 = authoritative/final personalized analysis;
- Deep does not require prior Fast;
- current exact-compatible canonically accepted Dossier is the Deep evidence gate;
- Deep may precede Fast;
- authoritative Deep fit/not-fit supersedes Fast;
- Deep incomplete/error preserves a still-valid Fast result;
- Deep recovery is GitHub-owned, separate, and requires explicit authorization; no blind retry loop.

GitHub owns:
- scope/order;
- validation;
- persistence;
- retry/recovery eligibility;
- completeness;
- canonical state.

Scheduled ChatGPT owns only bounded semantic/evidence work explicitly assigned by contract.

## What NOT to do on restart

- Do not ask the user to repeat the project history.
- Do not reconstruct truth from the retired Director conversation.
- Do not reuse retired physical worker chats as existing chats.
- Do not manually recover the old Dossier g000001.
- Do not manually rerun Tiny Snow.
- Do not process the Dossier backlog from the Director chat.
- Do not change Scheduled Tasks without exact user instruction.
- Do not assume historical Board sections marked ACTIVE/LIVE are current.
- Do not create another freshness self-check in ChatGPT; date classification is now GitHub-owned.

## Recommended first action in the new Director chat

1. Read fresh `CHAT_PROTOCOL.md`.
2. Read fresh `DIRECTOR_PROTOCOL.md`.
3. Read this `DIRECTOR_BOOTSTRAP.md`.
4. Read the top/current sections of fresh `DIRECTOR_TASK_BOARD.md`.
5. Confirm that there is no active worker assignment.
6. If the user wants to continue the Dossier thread, perform only a bounded current-state reconciliation decision:
   - verify current snapshot/binding/index;
   - determine whether the obsolete old g000001 snapshot requires any explicit cleanup/recovery;
   - if cleanup/recovery is actually required, create a separate task and obtain user authorization before execution;
   - otherwise continue with normal current-snapshot Dossier production under the accepted contract.

## Rotation state

The Director conversation that produced this bootstrap has reached its context limit and is retired.

Continue project work only in a **NEW physical Director conversation**.

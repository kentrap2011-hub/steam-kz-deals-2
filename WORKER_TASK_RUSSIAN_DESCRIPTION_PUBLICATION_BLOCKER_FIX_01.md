# WORKER TASK — RUSSIAN DESCRIPTION PUBLICATION BLOCKER FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or the target is ambiguous, stop and switch first;
- do not use another repository.

Task ID: `russian-description-publication-blocker-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/russian-description-publication-blocker-fix-01.md`

## Goal

Remove the currently proven publication blocker for:
- `game:1213210`
- `Command & Conquer™ Remastered Collection`

The latest accepted worker report proved that:
- the earlier Deep visual-binding defect is already fixed and merged in PR #102;
- full visual generation now reaches `VISUAL_FINAL_BUILD=BUILT`;
- publication then fails at the existing Russian-description validation gate because this game's current description has status `needs_translation`;
- because that later gate fails, canonical visual persistence and Pages deploy are skipped.

Restore this game to the existing canonical Russian-description path and prove that the normal visual build and Pages deployment can complete.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current `CHAT_CONTEXT.md`;
3. current top of `DIRECTOR_TASK_BOARD.md`;
4. relevant description/translation/visual routes in `PROJECT_ROUTES.md`;
5. accepted report `reviews/worker_reports/deep-visual-authoritative-binding-fix-01.md`;
6. `config/execution_ownership_contract.json`;
7. only the smallest description/translation contracts, canonical state and producer/validator files needed to establish the exact owner and repair path.

Do not re-diagnose Deep or Dossier.

## Architecture preflight

Before implementation, prove:
- which existing GitHub-owned component owns Russian description acquisition/translation/persistence;
- where `game:1213210` currently becomes `needs_translation`;
- whether this is one stale/missing canonical description, an unprocessed canonical translation input, or a defect in the existing description path;
- the repair uses the existing canonical path rather than bypassing the meaningful-Russian validation gate;
- no scheduler, new queue, retry daemon, semantic stage or ChatGPT-owned production authority is introduced.

If the exact blocker is already resolved on fresh `main` by normal production before implementation begins, do not make unnecessary changes; prove the state and proceed to end-to-end validation.

## Required repair

Make the smallest canonical fix needed so `game:1213210` obtains a valid meaningful Russian description under the existing repository-owned rules.

Allowed examples only if supported by current canonical architecture:
- repair the existing description retrieval/translation projection for this item;
- repair a deterministic mapping/normalization defect that incorrectly leaves the item at `needs_translation`;
- repair the existing canonical ingestion/persistence path if valid Russian content is already available but not reaching the canonical state.

Do not:
- hard-code a one-off Russian description directly into the final visual payload;
- weaken or disable the meaningful-Russian validator;
- mark an untranslated description as valid;
- add a second translation pipeline;
- use browser-side fallback semantics.

If the root cause proves broader than this one title, fix the smallest shared defect that explains this title and add a focused regression.

## Validation

Require all of the following:
1. focused regression for the proven blocker;
2. existing relevant repository validation gates green;
3. PR clean/green before merge;
4. merge to `main`;
5. one successful normal full visual build on `main`;
6. one successful following Pages deploy;
7. inspect the deployed artifact and confirm:
   - `game:1213210` no longer fails Russian-description validation;
   - Deep counters are no longer the old zero values;
   - deployed Deep provenance/counts correspond to then-current canonical PASS 2 state sufficiently to prove the stale publication chain is repaired.

Do not manually process Deep, Dossier or Fast semantic backlog for validation.

## Scope exclusions

Explicitly out of scope:
- Dossier diagnosis, state, semantics, recovery or Scheduled Task;
- Deep semantic conclusions, queue, recovery or Scheduled Task;
- Fast semantic execution;
- unrelated game-description cleanup;
- browser/frontend semantic changes.

## Scheduled Tasks

Do not create, edit, pause, resume, enable, disable or manually trigger any ChatGPT Scheduled Task.

## Report

Write:
`reviews/worker_reports/russian-description-publication-blocker-fix-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Verified blocker`
4. `Root cause`
5. `Changes`
6. `Validation`
7. `Published result`
8. `Unresolved`
9. `Status`
10. `Recommended next step` — exactly one bounded next step
11. exact PR/commit/run/artifact refs
12. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another task after this one.

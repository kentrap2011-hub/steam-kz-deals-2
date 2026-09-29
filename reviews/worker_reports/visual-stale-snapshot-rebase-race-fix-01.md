# Visual stale-snapshot rebase race fix 01

## Task

- Task: `WORKER_TASK_VISUAL_STALE_SNAPSHOT_REBASE_RACE_FIX_01.md`.
- Mode: IMPLEMENT / VALIDATE.
- Accepted diagnosis was reused without redoing root-cause discovery: full visual run could build from an older material state, lose the first push race, rebase the already-generated JSON onto newer `main`, then persist a mixed-parent/mixed-source visual.
- Historical pinned case preserved by regression: build checkout `53767218c890c9bdb5698d039a5651fa416c4963`, old PASS2 blob `4435430a967f94474c41aa77ea97374f7d276cf1`, newer parent `dede9ea264b834819642b6e23f778cabd85a4fdd`, newer PASS2 blob `b1967e420ef55cc3c2368f25f71ef99df8041aec`, stale visual commit `2202a668cad11f67f0659aa6bcfe5e6cf34bb9ab`.

## Architecture preflight

1. GitHub/GitHub Actions remains the sole owner of deterministic full-visual rebuild, freshness validation, canonical persistence and Pages publication.
2. Browser remains read-only; no browser recount or freshness inference was added.
3. No Scheduled Task, semantic worker, queue, scheduler, retry owner, Fast/Dossier/Deep ownership, ranking rule, sale-expiry rule, or translation semantic was changed.
4. Full visual identity is bound to exact material blobs already used by the producer contract, plus the profile identity carried by the prepared payload.
5. Whole-`HEAD` stability is explicitly not required: unrelated `main` movement may rebase; material movement may not.
6. A rejected push now compares exact material blobs. Material drift forces one fresh-`main` rebuild; a second material drift/rebuild failure aborts without replacing canonical visual.

## Verified current persistence path

Canonical path remains:

`.github/workflows/build-daily-visual-payload.yml`
→ deterministic producer/validators
→ `data/production/visual/current.json`
→ material-bound persistence guard
→ durable freshness receipt
→ `.github/workflows/deploy-visual.yml`
→ exact staging to `web/data/current.json`
→ GitHub Pages.

The former unsafe full-build sequence was a blind `git rebase origin/main` after the visual commit had already been generated. The corrected path first proves whether the newer parent changed any material source. It rebases only when those blobs are unchanged.

## Source binding model

`scripts/visual_material_freshness_guard.py` captures both:
- parent blobs from the build parent, used to decide whether a newer `main` is materially equivalent;
- exact working-tree blobs actually consumed by the build, used to validate generated and persisted visual provenance.

Material bindings cover the producer/policy helpers and the current production-contract source identities for history/commercial/giveaway inputs, PASS1/PASS2 state and contracts, Dossier work, Russian-description status/contract, taste queue, progressive candidate context, duration cache, package inputs and prepared payload. The prepared payload additionally binds `canonical_profile_blob_sha` and `taste_model_version`.

`scripts/build_daily_visual_payload.py::git_sha` now uses `git hash-object` so producer-owned inputs modified earlier in the same workflow, notably duration cache, record the exact bytes actually consumed rather than stale `HEAD:path` bytes.

## Changes

- Added `scripts/visual_material_freshness_guard.py`.
- Added focused historical/concurrency regressions in `scripts/test_visual_material_freshness_guard.py`.
- Extended `scripts/visual_freshness_receipt.py` to verify full material binding and distinguish material-drift aborts.
- Extended freshness-receipt fixtures/regressions for exact full material provenance.
- Replaced the inline ranking-review generator with deterministic `scripts/build_ranking_review.py` so the same derivative can be rebuilt after a drift-triggered fresh-main reset.
- Corrected full-build persistence in `.github/workflows/build-daily-visual-payload.yml`.
- Extended deploy verification in `.github/workflows/deploy-visual.yml`.
- Added focused PR validation to the existing PASS2 validation workflow; no new recurring workflow/scheduler was introduced.
- Recorded durable decision `PROJECT_DECISIONS.md#VISUAL-001` and the guarded publication route in `PROJECT_ROUTES.md`.

## Race regression

Focused regression proves:
- historical PASS2 blobs at `53767218...` and `dede9ea...` are different;
- unrelated `HEAD` movement is accepted;
- PASS2 movement is material and blocks stale persistence;
- concurrent Dossier + Deep movement is material;
- first material drift permits one fresh-main rebuild;
- second material drift after that rebuilt baseline is fail-closed;
- exact working-tree bytes are required by visual provenance;
- the workflow contains the rebuild/abort path rather than a blind rebase.

Production acceptance run did not encounter material drift: it built on merge `f57d5b922ee333759c951de38686eb448a8c10fd`, persisted visual commit `51a37b14c38b7f27d103c5f50e2e0788dece4a25`, then emitted `VISUAL_PERSISTED_MATERIAL_BINDING=pass ref=HEAD`. Therefore acceptance proves the corrected no-drift path; the drift branch is covered by the focused regression suite.

## Freshness classification

The freshness receipt no longer treats workflow success as freshness proof.

Supported full-build outcomes are:
- `fresh_build` only when the existing semantic freshness rules and exact material bindings both pass;
- `degraded/no_fresh_build` for legitimate cases such as `deterministic_refresh_preserved_semantic_history`, while still proving exact deterministic material binding when a new canonical visual was persisted;
- `aborted_on_material_drift` when a second material drift/rebuild failure prevents persistence.

Post-merge run #959 truthfully produced:
`fresh_build=false`, `scope=full_visual`, `outcome=degraded/no_fresh_build`, reason `deterministic_refresh_preserved_semantic_history`.

Deploy #997 independently verified the same receipt against current `main` and staged payload:
`material_binding=exact`, visual blob `603254a1dc9a813453baf217bc62afb0e747ce1e`.

## Validation

Final pre-merge branch head after fresh-main rebuild: `fd788904b0a6ad09a1d0ac1695e134529bb26aa5`, parent `main@4c8a6d27cb7affc1ff21ba35b5b57fb17b02ef4c`.

Final PR checks on that exact head:
- Validate Progressive PASS 2 core: run `36596738251` — success; this includes the new visual material/freshness regressions and full Git history for the pinned historical case.
- Validate package purchase value: run `36596738383` — success.
- Validate backlog dispositions: run `36596738541` — success.

Post-merge build #959 also passed:
- freshness-receipt regressions;
- material freshness guard regressions;
- priority/progressive validation;
- Russian translation contract, quality, runtime, manual-worker and publication/statistics regressions;
- Russian validation with explicit nonblocking unresolved mode;
- generated card and giveaway validation;
- exact visual material binding;
- ranking-review/lookup generation;
- canonical persistence.

Translation behavior from PR #125 remains intact: unresolved translation is publication-nonblocking; invalid/wrong-bound/non-Russian masquerade remains fail-closed in the existing regressions. Production payload currently reports `untranslated_game_count=0`.

## Production acceptance

Normal post-merge GitHub-owned path completed successfully.

Build run #959 / run id `36596838833`:
- merge source: `f57d5b922ee333759c951de38686eb448a8c10fd`;
- captured PASS2 material blob: `e7af05911ac9c90c3da74d22def68ca367eddee3`;
- exact generated material validation: pass;
- canonical visual commit: `51a37b14c38b7f27d103c5f50e2e0788dece4a25`;
- persisted material verification: pass;
- freshness receipt artifact: `11046685316` (`visual-freshness-receipt`).

Accepted canonical visual:
- blob: `603254a1dc9a813453baf217bc62afb0e747ce1e`;
- generated_at: `2026-09-29T16:19:48.618159+00:00`;
- PASS2 binding: `e7af05911ac9c90c3da74d22def68ca367eddee3`;
- Dossier binding: `a7b97d4ca8df6ca7980192d247fe37faef9a7939`;
- translation-status binding: `8947bcfac181f52c42871d6d5550d033032a288f`;
- translation-contract binding: `cbd18b4b8234b1ad937483ac4aa040020661272a`;
- history binding: `4162663d13e88d5c80ae436eda5e51a5cb90badd`;
- profile binding: `9b9926031889dbd98ba6585c57836d52c739a0bb`.

Producer-owned Statistics in that payload include:
- Dossier last write `2026-09-29T16:14:41+00:00`, accepted 54, pending 211, failed/recovery 18;
- Deep last write `2026-09-29T16:05:12+00:00`, authoritative completed 39, first-pass attempted 46;
- translation attempt/success `2026-09-29T16:04:04+00:00`, untranslated 0.

Pages deploy #997 / run id `36596937298`:
- triggered by build #959 as `workflow_run`;
- classified the canonical visual commit as `51a37b14c38b7f27d103c5f50e2e0788dece4a25`;
- copied canonical `data/production/visual/current.json` to `web/data/current.json`;
- verified receipt with `material_binding=exact`;
- Pages artifact `11046512431` (`github-pages`) uploaded successfully;
- Pages deployment created for exact build version `51a37b14c38b7f27d103c5f50e2e0788dece4a25`.

No mixed-parent/mixed-source condition was observed.

## Unresolved

No task-blocking defect remains. The current receipt is intentionally semantically degraded because the project still has in-progress Fast/Dossier/Deep work; this is not a stale-material condition and was not relabeled as fresh.

## Status

`complete_ready_for_director_acceptance`

## Exact PR / commit / run / artifact refs

- Implementation PR: `#126` — Fix full visual stale-snapshot persistence race.
- Final tested PR head: `fd788904b0a6ad09a1d0ac1695e134529bb26aa5`.
- Implementation merge: `f57d5b922ee333759c951de38686eb448a8c10fd`.
- Production visual commit: `51a37b14c38b7f27d103c5f50e2e0788dece4a25`.
- Build: run #959, id `36596838833`, build job `109503926541`.
- Freshness artifact: `11046685316`.
- Deploy: run #997, id `36596937298`, deploy job `109504165250`.
- Pages artifact: `11046512431`.
- Canonical visual blob: `603254a1dc9a813453baf217bc62afb0e747ce1e`.
- Final pre-merge validation runs: PASS2 `36596738251`, package `36596738383`, backlog `36596738541`.

## Recommended next step

Director should review this report plus PR #126 / production acceptance refs and, if accepted, close task `visual-stale-snapshot-rebase-race-fix-01` without starting another implementation.

## Efficiency / reusable lesson

For derived repository snapshots, freshness should be content/material-bound rather than branch-head-bound. The reusable pattern is: capture exact material identities → build → validate generated provenance → optimistic push → on rejection compare only material identities → harmless movement may rebase, material movement must rebuild → verify persisted identities → let deploy independently re-verify the same receipt. This preserves concurrency without allowing a newer parent to legitimize stale derived data.

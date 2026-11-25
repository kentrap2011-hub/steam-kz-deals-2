# ЧАТ 3 — Lean automatic writer sandbox path-layout FIX

Task: `dossier-lean-writer-auto-path-layout-fix-01`
Source of truth: `kentrap2011-hub/steam-kz-deals-2:main@2a98a3d57b2a97e2c1239804ec0285a55220b513`
Mode: narrow source-only FIX, original shared writer, disposable offline tests; no live retry.

## Confirmed failing production evidence

- GitHub Actions `45628656098`, job `139255581611`, `main@4ccf23005166a1ae3c35800e1b38e0c295e29d8e`: first-attempt owner activation `push` failed with `LEAN_AUTO_READY_TERMINAL_OR_PRECHECK_BLOCKED: V2 single-item paths must be separate writer-owned subdirectories`.
- Cause: `scripts/dossier_lean_writer_auto_ready.py::run` invoked the existing V2 writer with relative `store_dir=data/control/dossier_notes_v2/batch_pilot_store/<trial_id>` and `accepted_dir=data/control/dossier_notes_v2/batch_pilot_accepted` while running from **main source checkout**, not the detached temporary `sandbox` worktree. `taste_steam_review_dossier_buffered.py::_drain_notes_v2_individual` resolves these relative paths using current process cwd and rightly rejects destinations outside `Path(repo).resolve()` BEFORE attempting any isolated writes. The paths must refer to the **sandbox Git checkout**, not be resolved against the workflow current directory.
- Exact expected writer-owned paths: `<sandbox_checkout>/data/control/dossier_notes_v2/batch_pilot_store/<trial_id>` and `<sandbox_checkout>/data/control/dossier_notes_v2/batch_pilot_accepted` (receipt files further under `<trial_id>/gNNNNNN/<appid>--<assignment>.json`). These are the existing `dossier_notes_v2_batch_route.py::paths(trial_id)` store/accepted names; `_drain_notes_v2_individual` already enforces them. No validator relaxation is appropriate.

## Immutable one-use claim / frozen sandbox

- Live `refs/heads/dossier-lean-auto-attempts/cdcdb4951e2fc98336729af75b954da4` **EXISTS** at `6df354d024b0e3104ee408e815a1e5d141fb8e84`. Immutable claim document is `data/control/dossier_notes_v2/auto_writer_attempts/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4.json`: it binds `automation_run_id=45628656098`, `automation_source_main_sha=4ccf23005166a1ae3c35800e1b38e0c295e29d8e`, `attempt=1`, `no_retry=true`, `canonical_acceptance=false`, `production=false`, `deep=false`. **Postclaim failure**, not preclaim; recovery authorization was irrevocably consumed.
- Live sandbox ref `refs/heads/sandbox/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4` remains `d1b9a9e78dcde879a03370682ade4969763fd9d1`. Exact trial subdirectories under `batch_pilot_store` and `batch_pilot_accepted` are absent at that immutable SHA (404 each), i.e. **0/6 accepted docs, 0/6 accepted receipts**.
- **NO rerun** of `45540222575`, `45591943959`, `45603534459` or `45628656098`. Neither reissue owner grant nor change one-use claim or sandbox. Any future real trial requires separately validated fresh owner authorization; no implicit recovery.

## Source FIX

- `scripts/dossier_lean_writer_auto_ready.py`: `sandbox_writer_destinations(sandbox_repo, trial_id)` takes the existing `batch.paths(trial_id)` and roots both paths under `Path(sandbox_repo).resolve()`. `run` passes those absolute destinations to the unchanged shared V2 writer.
- `scripts/test_dossier_notes_v2_isolated_lean_acceptance.py`: executable disposable Git six-item writer uses the same automatic destination selector; positive staged exact-six readback, negative original workflow-relative paths, negative overlapping writer directories, negative manual isolated writer targeting strict canonical namespace. Existing test for 12 exact committed files, SHA/edition/year/TTL/source safety and legacy strict/manual tests remain in existing CI.
- No change to source event/actor/grant/one-use claim, source safety, TTL, original release-year, namespace guard, writer lock, 6+6 atomic postcommit readback or production/Deep switches. No real writer or semantic jobs executed by this source worker.

## Verification and release boundary

- Offline verification target: existing `.github/workflows/validate-dossier-research-notes-v2.yml`, including `scripts/test_dossier_notes_v2_isolated_lean_acceptance.py`, `scripts/test_dossier_lean_writer_auto_ready.py`, strict/manual `scripts/test_dossier_two_stage_final_acceptance.py` cases. No new Action or audit stage.
- Exact-final-HEAD GitHub CI: **pending at report creation**. Require SUCCESS for actual final PR HEAD before Director merge; check PR status/CI run on that SHA (not a preceding SHA). Local environment has no direct GitHub clone network access.
- Status: **source fix prepared; SOURCE_READY_AWAITING_DIRECTOR_MERGE only upon exact-final-HEAD CI PASS**. The spent one-use claim is a separate live-activation **BLOCKED_ALREADY_CLAIMED_NO_RETRY** state and remains blocked even after source merge.
- One Director decision: whether to accept the source-only path fix once exact-final-HEAD CI is green. Do not make a live recovery decision from this PR.

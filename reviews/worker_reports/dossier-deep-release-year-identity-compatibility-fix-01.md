# Dossier / Deep release-year identity compatibility fix 01

## Task

Completed `WORKER_TASK_DOSSIER_DEEP_RELEASE_YEAR_IDENTITY_COMPATIBILITY_FIX_01.md` for `kentrap2011-hub/steam-kz-deals-2`. The repair addresses the accepted 46-Dossier / 38-Deep-ready gap caused by comparing two different kinds of release year.

## Architecture preflight

GitHub remains the control plane for Dossier acceptance, Deep eligibility/recomputation, persistence, attempt accounting, recovery and publication. Scheduled ChatGPT remains only the bounded semantic data plane. No scheduler, queue, retry loop, recovery owner or Scheduled Task configuration was added or changed. Dossier and Deep remain independently runnable.

## Canonical identity decision

`PPD-011` defines two distinct year semantics:

- Dossier `game_identity.release_year` = original/work release year used as identity evidence/corroboration.
- Progressive semantic-input `release_year` / year extracted from `release_date` = Steam/storefront release-date year.

Cross-kind equality is not a hard compatibility key. A year equality may be a hard gate only when both compared values have the same canonical semantic meaning/source class. The machine-readable shared rule is `config/dossier_deep_identity_compatibility_contract.json`.

Exact AppID, exact prepared title/work identity, resolved identity, current Dossier evidence binding and non-expired status remain fail-closed requirements. Exact-product provenance/corroboration remains required; edition/remaster/DLC/cross-product mismatches remain rejected.

## Accepted root cause

The accepted diagnostic was correct. Eight fresh exact-product Dossiers used original/work years while current Steam queue metadata used storefront/re-release years. `scripts/progressive_pass2.py::dossier_is_eligible` treated these unlike year kinds as identical and returned `dossier_wrong_release_year`.

The repair does not delete year semantics. It gives them explicit kinds and removes only the invalid cross-kind equality gate.

## Changes

Implementation PR #111 added/updated:

- `config/dossier_deep_identity_compatibility_contract.json`;
- `PROJECT_DECISIONS.md#PPD-011`;
- Dossier and PASS 2 contracts with a shared compatibility binding;
- `scripts/progressive_pass2.py` release-year compatibility logic and exact identity guards;
- focused eight-AppID and negative regressions;
- canonical test fixtures;
- PASS 2 CI coverage.

Historical accepted Dossier files were not rewritten. Implementation PR #111 contains no `data/cache/taste_steam_review_dossiers/App_*.json` changes. The post-merge deterministic pre-AI publication commit likewise changed only derived pre-AI files and did not rewrite Dossier cache history.

## Eight-AppID regression

Focused CI explicitly passed all eight real pairs:

- 1170760 — Steam 2020 / Dossier work 2003;
- 1237950 — 2020 / 2017;
- 1237970 — 2020 / 2016;
- 1237980 — 2020 / 2015;
- 1238040 — 2020 / 2011;
- 1238060 — 2020 / 2013;
- 1238820 — 2020 / 2011;
- 13500 — 2009 / 2004.

Post-merge `data/production/pre_ai/progressive_pass2_work.json` contains all eight as ordinary Deep items. Published `data/production/visual/current.json` shows all eight with `dossier_stage_state=accepted`, `deep_stage_state=eligible_or_pending`, and `pass2_attempted=false`.

## Negative identity regressions

The focused regression preserves fail-closed behavior for:

- wrong AppID;
- wrong title/product;
- unresolved/ambiguous identity;
- expired Dossier;
- incompatible Dossier evidence-contract binding;
- cross-product mismatch using a real different current Dossier;
- forged/missing exact AppID corroboration;
- missing/incompatible identity provenance.

Therefore the fix is not “ignore year and trust any Dossier”.

## Legacy migration reconciliation

The finite PPD-010 migration `deep-legacy-full-reanalysis-with-preserved-positives-01` completed concurrently during this task. Fresh production state is:

- total 30;
- accepted 30;
- accepted completed 30;
- pending 0;
- incomplete 0;
- complete true.

No frozen target, migration result, migration authority, PPD-010 behavior or migration data was edited by this task. The migration regression was adjusted only so a naturally completed production migration is not incorrectly expected to remain active; its frozen 30-target semantics continue to be exercised.

## Dossier parallelism

Dossier was never paused, manually processed or regenerated for these eight games. Scheduled Task settings were not changed. The final deterministic rebuild reports 46 accepted Dossiers and 353 pending in the current 399-game scope; Dossier remains on its existing independent path.

## Validation

Final implementation head validation:

- focused eight-AppID identity compatibility regression — PASS;
- Progressive async/frozen-start regressions — PASS;
- PASS 2 core — PASS;
- Dossier/PASS 2 integration — PASS;
- balanced Deep negative assessment — PASS;
- PPD-010 migration regression — PASS;
- backlog disposition validation — PASS;
- buffered Dossier runtime, including strict identity/provenance/package regressions — PASS;
- deterministic current-production recomputation — PASS with zero Deep attempts.

Post-merge:

- PASS 2 core — PASS;
- normal `Build pre-AI deterministic payload` — PASS and published the regenerated Deep projection;
- normal daily visual path — PASS;
- normal visual deploy — PASS.

## Current production counters

Final published current state:

- total current scope: 399;
- Dossier accepted: 46;
- Dossier pending: 353;
- Deep ready/pending: 46;
- Deep waiting for Dossier: 353;
- Deep first-pass attempted: 0;
- Deep authoritative completed: 0;
- PPD-010 migration: 30/30 accepted completed, complete true.

Arithmetic reconciles exactly: 46 current accepted Dossiers -> 46 ordinary Deep-compatible identities. The previous false gap of 8 is gone.

## Published result

The GitHub-owned pre-AI rebuild emitted `PROGRESSIVE_PASS2_WORK=READY ... waiting_dossier=353 ready_or_pending=46` and committed `data/production/pre_ai/progressive_pass2_work.json`.

Published visual state independently confirms `dossier_accepted_count=46`, `deep_ready_or_pending_count=46`, `deep_waiting_for_dossier_count=353`, `deep_first_pass_attempted_count=0`. All eight repaired identities are visible as accepted/eligible without a semantic Deep attempt.

## Unresolved

No compatibility defect remains within this task scope. Ordinary Deep semantic work has not been manually executed; the 46 published ready/pending items remain for the existing worker's normal execution path.

## Status

`complete_ready_for_director_acceptance`

## Recommended next step

Allow the existing Progressive Deep worker to consume the published ordinary 46-item queue on its next natural invocation; do not manually run the eight or change its schedule.

## Exact PR/commit/run/artifact refs

- implementation PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/111
- implementation final head: `8f5b6a86d33db7513e421b0530228cc0d7a19070`
- implementation merge: `ebaa18ff406fb9c1744ed559990043570080b7b2`
- PR PASS 2 core: run `36423277328` / #310 — success
- PR backlog dispositions: run `36423277253` / #1357 — success
- PR buffered Dossier runtime: run `36423277162` / #201 — success
- post-merge PASS 2 core: run `36423455438` / #311 — success
- post-merge pre-AI deterministic build: run `36423455359` / #217 — success
- regenerated pre-AI publication commit: `62524865133ae585c6aaf2264eb7c05a31847fbc`
- daily visual: run `36423532818` / #858 — success
- visual publication commit: `f09c1c3035844b12b06cae4d69aede9055651745`
- visual deploy: run `36423530324` / #897 — success
- published visual artifact: `data/production/visual/current.json`, blob `60db87fbe97fab13adc355c1d8844408d8b98cec`

## Efficiency / reusable lesson

The implementation required several CI iterations for two reasons: strengthened exact-identity checks exposed simplified legacy test fixtures, and PPD-010 completed concurrently so an old migration regression still assumed “migration active”. Neither production behavior was weakened to satisfy those tests. The reusable rule is to define identity-field semantics before cross-stage equality checks, and to keep migration regressions invariant-based rather than tied to a transient production phase.

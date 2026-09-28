# Dossier / Deep ready count gap diagnostic 01

## 1. Task

Task ID: `dossier-deep-ready-count-gap-diagnostic-01`

Mode: `READ-ONLY / RECON`

Question: explain exactly why the current Dossier statistics show 46 accepted/prepared items while ordinary Deep shows 38 ready/pending items, identify the exact eight identities, classify the reason for each, decide whether the behavior is expected or defective, and separate it from the finite 30-game legacy Deep reanalysis migration.

No Dossier, Fast, Deep, migration backlog, recovery authorization, Scheduled Task, or production worker was run or changed by this diagnostic.

## 2. Pinned current truth

Primary diagnostic pin:

- repository: `kentrap2011-hub/steam-kz-deals-2`
- branch: `main`
- commit: `637b5e9cdda16f73e31aac05b09b99c88f9f5ce9`
- commit message: `Assign Dossier Deep ready count gap diagnostic`
- observed at START before any diagnostic read beyond the protocol/task gates.

All set arithmetic and the exact eight discrepant identities below are derived from that exact commit.

While the diagnostic was running, `main` advanced independently. A bounded liveness recheck at `d34260d177a51d7c209fef44e4dd7eb55b80f798` showed that only PASS 2 migration state/work/receipts and the visual payload had changed relative to the pin. The Dossier work/store/queue/contracts relevant to the eight identities had not changed. At that later commit the same public counters remained Dossier 46 and ordinary Deep 38, while the separate migration had advanced from 0 to 8 accepted results. Therefore the diagnosed 46 -> 38 gap is stable across that concurrent migration progress.

## 3. Counter definitions

### Dossier 46

Canonical current-scope source:

- `data/production/pre_ai/taste_steam_review_dossier_work.json`
- producer: `scripts/progressive_personalization.py::_dossier_processing_metrics()`
- published through `data/production/visual/current.json#processing_status`

At the pin:

- `eligible_scope_count = 399`
- `prepared_required_count = 353`
- current group-progress `accepted_dossier_count = 0`
- current group-progress `pending_dossier_count = 353`

The UI/visual Dossier accepted metric intentionally includes already-current reusable dossiers that did not need to enter the new prepared-required work set:

```text
already_current_accepted = eligible_scope_count - prepared_required_count
                         = 399 - 353
                         = 46

dossier_accepted_count = already_current_accepted + newly_accepted_required
                       = 46 + 0
                       = 46
```

Therefore 46 is a **Dossier current-scope freshness/acceptance count**. It is not a Deep eligibility count.

This also explains why the compact Dossier worker index itself says `accepted_dossier_count = 0`: that index counts progress only inside the 353-item current prepared-required work set. The visual Dossier metric additionally includes the 46 already-current dossier files.

### Ordinary Deep 38

Canonical source:

- `scripts/progressive_pass2.py::recompute_eligibility()`
- projected into `data/production/pre_ai/progressive_pass2_work.json#scope`
- published through `data/production/visual/current.json#processing_status`

At the pin:

- `deep_total_current_coverage_target = 399`
- `deep_first_pass_attempted_count = 0`
- `deep_authoritative_completed_count = 0`
- `deep_incomplete_or_recovery_count = 0`
- `deep_waiting_for_dossier_count = 361`
- `deep_ready_or_pending_count = 38`
- `normal_pass2_eligible_count = 38`

Thus ordinary Deep arithmetic is:

```text
399 current Deep identities
= 38 eligible_or_pending
+ 361 waiting_for_dossier
```

The 38 is an **ordinary Deep eligibility scope**, not the currently emitted semantic-worker item count while the one-off migration is active.

### Deep waiting-for-Dossier 361

The 361 consists of:

```text
353 Dossier items that are actually pending/refresh-required
+ 8 already-current Dossiers rejected by Deep compatibility
= 361
```

### Legacy migration 30

Canonical source:

- `data/control/progressive_pass2_legacy_full_reanalysis_manifest.json`
- `data/production/pre_ai/progressive_pass2_work.json#scope.legacy_full_reanalysis`

At the primary pin:

- migration ID: `deep-legacy-full-reanalysis-with-preserved-positives-01`
- target count: 30
- pending: 30
- accepted: 0
- actual current PASS 2 worker projection: 30 migration items
- `deep_normal_work_paused_for_legacy_reanalysis = true`
- ordinary Deep readiness remains separately recorded as `normal_pass2_eligible_count = 38`.

At the later bounded liveness recheck `d34260d...`, migration work had advanced to 8 accepted / 22 pending, while Dossier 46 and ordinary Deep 38 were unchanged.

Therefore 30 is a **finite one-off migration scope**, not a denominator used in 46 -> 38.

## 4. 46 -> 38 arithmetic

Exact reconciliation:

```text
Dossier current scope:                 399
Dossier pending/refresh-required:      353
Dossier already-current/fresh:          46

Deep current coverage target:          399
Deep ordinary ready/pending:            38
Deep waiting for Dossier:              361

46 current/fresh Dossiers
= 38 Deep-compatible current Dossiers
+ 8 current/fresh but Deep-incompatible Dossiers

361 Deep waiting
= 353 genuinely pending Dossiers
+ 8 current/fresh but Deep-incompatible Dossiers
```

No current authoritative Deep completion, consumed first pass, recovery state, package/family handling, or migration ownership is needed to explain the eight-item difference.

## 5. Exact discrepant identities

| AppID | Title | Dossier state | Queue/current year used by Deep | Dossier resolved year | Deep state |
|---|---|---:|---:|---:|---|
| 1170760 | XIII - Classic | fresh/current | 2020 | 2003 | waiting_for_dossier |
| 1237950 | STAR WARS™ Battlefront™ II | fresh/current | 2020 | 2017 | waiting_for_dossier |
| 1237970 | Titanfall® 2 | fresh/current | 2020 | 2016 | waiting_for_dossier |
| 1237980 | STAR WARS™ Battlefront | fresh/current | 2020 | 2015 | waiting_for_dossier |
| 1238040 | Dragon Age II: Ultimate Edition | fresh/current | 2020 | 2011 | waiting_for_dossier |
| 1238060 | Dead Space™ 3 | fresh/current | 2020 | 2013 | waiting_for_dossier |
| 1238820 | Battlefield 3™ | fresh/current | 2020 | 2011 | waiting_for_dossier |
| 13500 | Prince of Persia: Warrior Within™ | fresh/current | 2009 | 2004 | waiting_for_dossier |

For all eight:

- canonical Dossier file exists;
- Dossier work projection classifies it `fresh`;
- Dossier `game_identity.resolution_status = resolved`;
- Dossier AppID is the exact current AppID;
- Dossier `work_title` exactly matches the current queue title;
- current web-evidence contract binding matches;
- Dossier is not expired at the diagnostic pin;
- Deep rejects only on the release-year equality check.

The exact Deep rejection reason is `dossier_wrong_release_year`.

## 6. Reason per identity

All eight share one proven reason category:

**current/fresh exact-AppID Dossier exists, but Dossier and Deep use incompatible release-year semantics for the same current product identity.**

Deep's gate in `scripts/progressive_pass2.py::dossier_is_eligible()` requires:

- exact AppID;
- exact work title;
- exact release year when the current item exposes one;
- resolved identity;
- current evidence-contract binding;
- non-expired Dossier.

Deep obtains that year through `release_year_from_semantic_input()`, which first uses `release_year` if supplied and otherwise extracts a year from the current queue's `release_date`.

The Dossier evidence contract, however, defines its research identity as `title + release_year` with:

`release_year_source = reliable_public_metadata_resolved_by_semantic_worker`.

The strict Dossier validator verifies that this resolved year is a valid identity year and that the exact AppID is corroborated, but it does **not** require that Dossier `game_identity.release_year` equal the current queue/store `release_date` year.

That means both stages are behaving according to their local contracts, but they are not using the same semantic definition of “release year”.

Per identity:

1. **1170760 — XIII - Classic**: Deep derives 2020; accepted Dossier resolves 2003. AppID/title/binding are otherwise exact. Rejected as `dossier_wrong_release_year`.
2. **1237950 — STAR WARS™ Battlefront™ II**: Deep derives 2020; Dossier resolves 2017. Same rejection.
3. **1237970 — Titanfall® 2**: Deep derives 2020; Dossier resolves 2016. Same rejection.
4. **1237980 — STAR WARS™ Battlefront**: Deep derives 2020; Dossier resolves 2015. Same rejection.
5. **1238040 — Dragon Age II: Ultimate Edition**: Deep derives 2020; Dossier resolves 2011. Same rejection.
6. **1238060 — Dead Space™ 3**: Deep derives 2020; Dossier resolves 2013. Same rejection.
7. **1238820 — Battlefield 3™**: Deep derives 2020; Dossier resolves 2011. Same rejection.
8. **13500 — Prince of Persia: Warrior Within™**: Deep derives 2009; Dossier resolves 2004. Same rejection.

This is not a title mismatch, AppID mismatch, stale Dossier, old evidence binding, unresolved identity, package/family mismatch, current Deep completion, recovery state, or migration ownership.

## 7. Legacy migration interaction

The 30-game legacy migration is separate from the 46 -> 38 arithmetic.

Exact set relation at the pin:

- migration targets: 30;
- all 30 migration target AppIDs are inside the 38 current Dossier-compatible ordinary-Deep set;
- intersection between the 30 migration targets and the eight discrepant identities: **0**.

While migration is active, `scripts/build_progressive_pass2_work.py` deliberately emits migration work instead of ordinary work and records that ordinary Deep work is paused, not consumed or reordered. The same work file preserves `normal_pass2_eligible_count = 38` separately.

Therefore:

- **46 -> 38 is not caused by the migration.**
- The migration can temporarily determine what the Deep worker receives, but it does not create the eight-item Dossier/Deep compatibility gap.
- Concurrent migration progress from 0 accepted at the primary pin to 8 accepted at the later recheck left 46 and 38 unchanged, which independently confirms the separation.

## 8. Expected vs defect

### Is 46 vs 38 expected under the current contracts?

**Mechanically, yes.** The two counters intentionally mean different things:

- Dossier 46 = current-scope dossiers that are already accepted/fresh under the Dossier contract;
- Deep 38 = current ordinary Deep identities whose accepted Dossier also passes Deep's stricter compatibility gate.

Therefore the counters are not required to be equal.

### Are the labels semantically correct?

They are technically correct if read literally as separate stage metrics, but they are easy to misread as “46 dossiers are prepared, therefore 46 games should be ready for Deep.” The current UI does not expose the eight-item compatibility rejection breakdown, so the difference is confusing without diagnostic context.

### Is the specific eight-item gap healthy expected behavior?

**No. The fail-closed guard is intentional, but these eight hits expose a cross-stage contract-boundary defect.**

The exact-product protection itself is correct: Deep must reject wrong release/edition/remaster/cross-product evidence. The defect is that the two canonical stages use different meanings for the release year of the same exact AppID/title:

- Dossier accepts a worker-resolved product/work release year;
- Deep derives a year from current queue `release_date` and requires exact equality.

For these eight exact-AppID/exact-title dossiers this creates a false incompatibility rather than proving a different product.

### Are the eight blocked indefinitely?

Under the current unchanged semantics, there is no deterministic normal projection path that makes them eligible.

They are currently `fresh`, so Dossier does not place them into the 353-item refresh work. Deep continues to classify them `waiting_for_dossier`. When TTL eventually expires they may be researched again, but the current Dossier identity contract can legitimately resolve the same original/work year again, so ordinary refresh is not a guaranteed repair.

Thus they can remain blocked across normal Dossier/Deep projections until the shared identity/release-year boundary or one side's canonical data semantics changes.

## 9. User-facing explanation

The simple explanation is:

Dossier has 46 games for which a current valid dossier file already exists. Deep can use only 38 of those files. The other eight are not missing and are not failed dossiers. They are rejected because Dossier records the game's resolved release year, while Deep compares that value with the year taken from the current queue's release date. For eight older titles those years differ even though AppID and title are the same.

So the eight-game difference is a release-year compatibility bug between Dossier and Deep, not work still waiting in Dossier and not the separate 30-game old-Deep migration.

## 10. Changes

Report only:

- created `reviews/worker_reports/dossier-deep-ready-count-gap-diagnostic-01.md`.

No source, contract, workflow, Dossier, Fast, Deep, migration, recovery, backlog, Board, or Scheduled Task state was changed by this diagnostic.

## 11. Unresolved

No unresolved cause remains for the 46 -> 38 discrepancy.

The correct implementation choice for a shared Dossier/Deep release-year identity rule is intentionally unresolved here because this task is diagnostic only. It must be decided contract-first rather than patched ad hoc in data or by manually reprocessing the eight games.

A separate unrelated observation from the post-pin liveness recheck is that migration execution was concurrently advancing on `main`; this did not alter the diagnosed gap and is not part of this task.

## 12. Status

`needs_fix`

Diagnosis is complete. The counters themselves are arithmetically correct, but the exact eight-item difference reveals a release-year semantic mismatch at the Dossier -> Deep compatibility boundary.

## 13. Recommended next step

Create exactly one bounded **contract-first Dossier/Deep identity compatibility task** that defines one shared release-year semantic for the Deep evidence gate and adds regression coverage for these exact eight AppIDs before any backlog reprocessing is authorized.

## 14. Exact file / commit refs

Primary diagnostic commit:

- `main@637b5e9cdda16f73e31aac05b09b99c88f9f5ce9`

Post-pin bounded liveness recheck:

- `main@d34260d177a51d7c209fef44e4dd7eb55b80f798`

Canonical inputs / logic:

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `WORKER_TASK_DOSSIER_DEEP_READY_COUNT_GAP_DIAGNOSTIC_01.md`
- `DIRECTOR_TASK_BOARD.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md#PPD-004`
- `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- `data/production/pre_ai/taste_steam_review_dossier_work.json`
- `data/production/pre_ai/chatgpt_taste_queue.jsonl`
- `data/production/pre_ai/progressive_pass2_work.json`
- `data/cache/progressive_pass2_state.json`
- `data/production/visual/current.json`
- `data/control/progressive_pass2_legacy_full_reanalysis_manifest.json`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `config/progressive_pass2_contract.json`
- `scripts/progressive_personalization.py::_dossier_processing_metrics`
- `scripts/progressive_personalization.py::build_processing_status`
- `scripts/progressive_pass2.py::dossier_is_eligible`
- `scripts/progressive_pass2.py::release_year_from_semantic_input`
- `scripts/progressive_pass2.py::recompute_eligibility`
- `scripts/build_progressive_pass2_work.py`

Exact discrepant Dossier files:

- `data/cache/taste_steam_review_dossiers/App_1170760.json`
- `data/cache/taste_steam_review_dossiers/App_1237950.json`
- `data/cache/taste_steam_review_dossiers/App_1237970.json`
- `data/cache/taste_steam_review_dossiers/App_1237980.json`
- `data/cache/taste_steam_review_dossiers/App_1238040.json`
- `data/cache/taste_steam_review_dossiers/App_1238060.json`
- `data/cache/taste_steam_review_dossiers/App_1238820.json`
- `data/cache/taste_steam_review_dossiers/App_13500.json`

## 15. Efficiency / reusable lesson

For future Dossier-vs-Deep count diagnostics, do not scan all 399 dossiers first.

A bounded route is sufficient:

1. establish `dossier_accepted_count`, `dossier_pending_count`, `deep_ready_or_pending_count`, and `deep_waiting_for_dossier_count`;
2. compute `deep_waiting - dossier_pending`;
3. inspect only the already-current/fresh Dossier set and apply `dossier_is_eligible`;
4. read canonical Dossier files only for the resulting discrepant identities.

Here that immediately reduces the problem to:

`361 - 353 = 8`

and then to eight exact files.

Route candidate for a later permitted documentation update: add this differential method to the Progressive Fast/Dossier/Deep section of `PROJECT_ROUTES.md`. It was not edited here because this task allows report-only changes.

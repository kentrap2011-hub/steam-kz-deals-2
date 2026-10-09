# Worker report — commercial refresh independent of Dossier failure 01

**Task:** `WORKER_TASK_COMMERCIAL_REFRESH_INDEPENDENT_FROM_DOSSIER_FAILURE_01.md`  
**Base:** `main`  
**Branch:** `fix/commercial-refresh-dossier-failure-01`  
**Status:** implementation ready for CI / review; no production run or merge asserted.

## Root cause and original boundary

On 2026-10-08 the Steam shortlist and mailing feed succeeded, but the
`Build pre-AI deterministic payload` workflow stopped in
`scripts/test_taste_steam_review_dossier_prepublication.py` before its single
`Commit atomic pre-AI payload` step. That regression file constructed **valid**
Dossiers using the fixed timestamp `2026-09-16T20:00:00Z` plus a 20-day TTL,
so the strict validator correctly judged those synthetic records expired in
October. This was a fixture bug, **not** a reason to relax the validator.

Consequences: current Store/family/purchase/progressive-input artifacts existed
only in the unsuccessful runner workspace, GitHub `main` remained on an older
commercial source, and the visual `workflow_run` normally refused a failed
pre-AI upstream.

## Persistence and failure boundary after this change

1. The unchanged Steam/mailing/source validators and deterministic
   Store/content, fixed-package, FX, family, taste projection, history,
   deal-scenarios, full pre-AI payload, purchase context, candidate universe
   and PASS 1 work builders execute first.
2. **New durable boundary:** `scripts/persist_pre_ai_commercial.sh` stages
   *only* these deterministic commercial/current-cycle artifacts and commits
   them to `main` with the existing bounded fetch/rebase/push policy. A failed
   push is fatal. The Dossier manifest, inbox/acceptance, Deep work and Russian
   translation state are **not** in this commit.
3. The normal Dossier prepare, inbox reconcile, strict validators/tests,
   Deep eligibility, pin/translation steps and final atomic Dossier-state
   persistence still execute afterward. Their failure cannot roll back the
   earlier durable commercial commit.
4. When the upstream pre-AI run reports failure, the visual workflow can
   exceptionally enter the **existing full Progressive visual producer**
   after verifying that the fresh commercial snapshot is durably committed,
   complete and source-bound, that the existing visual has a valid semantic
   overlay, and that Dossier/Fast/Deep **acceptance** blobs are unchanged.
   This also works when a prior commercial-only publish already stamped today's
   paid freshness but the semantic visual and its new-family lineup remain old.
   The previous commercial-only path was insufficient because it could only
   retain/remove old cards. Other upstream failures or unsafe global state
   remain fail-closed.
5. The full producer enumerates the **fresh current
   `progressive_candidate_context.jsonl`**, not the previous visual
   `items`, via `build_visual_feed_v2.py`; its canonical
   `progressive_personalization.build_state_index()` attaches a compatible
   accepted Taste/Fast/Deep result only through the existing exact bindings.
   An entirely new family without accepted semantic evidence is rendered as
   `not_analyzed` with `dossier_stage_state=not_ready` and
   `deep_stage_state=waiting_for_dossier`; no fake execution/acceptance.
6. This full path runs the existing known-expiry/removal, fixed-package
   purchase, ranking, status, card/translation/giveaway, material-binding and
   visual publication validators. Expired/removed families are omitted,
   current discounts/prices come from the fresh Store snapshot; Dossier
   worker manifests and acceptance are **not** updated on this path.
   Existing Dossier write timestamps and source-binding remain old, while
   current commercial source/blobs advance. The normal successful
   pre-AI pathway is unchanged.


There is **no** manual production JSON/date modification, new schedule,
semantic queue, retry manager, or direct Dossier acceptance.

## Strict Dossier validation unchanged

`scripts/taste_steam_review_dossier_strict.py`, schema, expiry gates,
provenance, web evidence, group acceptance and Deep acceptance code are
untouched. The test fixture now uses a runtime-relative synthetic clock so
valid cases cannot expire simply because the real date advances. A separate
regression explicitly supplies a genuinely expired candidate and expects
`already-expired dossier cannot be canonically ingested`.

## Files changed

- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/build-daily-visual-payload.yml`
- `.github/workflows/validate-site-publication-resilience.yml`
- `scripts/persist_pre_ai_commercial.sh` (new)
- `scripts/progressive_visual_activation_routing.py`
- `scripts/test_commercial_dossier_failure_isolation.py` (new; extended)
- `scripts/test_taste_steam_review_dossier_prepublication.py`
- This report.

## Regression / verification

- `python scripts/test_commercial_dossier_failure_isolation.py`:
  checks producer step order, runs an **actual local Git commit/push**
  into a temporary bare remote, injects a later synthetic Dossier failure,
  proves that the complete latest deterministic commercial source is still
  durable while old valid Dossier state is unchanged; separately checks
  unchanged-Dossier/Fast/Deep fallback gates and real paid-card price/discount
  updates with old semantic timestamps/fields. An additional case calls
  **real** `progressive_personalization.build_state_index()` over a freshly
  added game with no accepted semantic/Dossier state, then invokes the
  canonical `build_visual_feed_v2.main()` in an isolated temporary output:
  the new previously absent game enters the current visual as
  `not_analyzed / waiting_for_dossier`, with current price/discount and
  no fabricated Fast/Deep result. Workflow-routing assertions verify that
  failed-upstream fallback goes through the full producer (not the
  old-card-only path) and never emits a contradictory no-build receipt.
  The gate also permits full rebuilding an older semantic visual even when
  its commercial stamp already matches the newly persisted current cycle.
  A separate regression invokes the canonical full-build expiry guard and
  proves an already-expired old family is removed while a newly current
  `not_analyzed` family's current offer survives.
- `python scripts/test_taste_steam_review_dossier_prepublication.py`:
  valid fixture parity and deliberately expired strict rejection.
- Existing `scripts/test_progressive_visual_activation_routing.py`,
  `scripts/test_commercial_refresh.py`,
  `scripts/test_site_publication_resilience.py`, and full buffered Dossier
  PR suite remain wired into the relevant validation workflows.
- Commercial visual workflow's existing runtime validation continues to
  assert full current source/blob bindings, no expired visible offers,
  unique family IDs, unchanged giveaway sibling, and no semantic rewrite.

**Merge-ready production verification:** let the next authentic
Steam → mailing → pre-AI cycle run (or use the existing GitHub manual
dispatch without synthetic production input); check the durable commercial
commit and exact `source_mailing_updated_at_utc`/blob identities; check the
next visual build or guarded failed-upstream commercial-only build and Pages
deploy; verify `commercial_source_mailing_updated_at_utc` advanced while
Dossier's own write/acceptance state did not claim a new result; verify any
failed Dossier validation still rejects that candidate, and Deep has not
ingested unvalidated evidence.

## Remaining conditions and verification boundary

The failed-upstream exception is deliberately limited to a durably persisted,
complete and source-bound current commercial snapshot with an intact old
semantic overlay and unchanged canonical Dossier/Fast/Deep acceptance blobs.
A global data corruption or changed/ambiguous semantic authority still fails
closed. New items do not require Dossier or Deep for honest unanalysed
publication; previously accepted results are reused only with exact bindings.

The full producer still uses all its normal global validation and
read-only site publication gates. This PR proves routing and the new-item
regression, but **does not** claim post-merge success of an authentic
Steam/mailing → pre-AI (Dossier failure) → full visual → Pages sequence.
That real run and latest live site must be inspected after merge.

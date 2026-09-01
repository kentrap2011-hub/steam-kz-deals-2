# WORKER TASK — CHAT 1

Task ID: `steam-recommendation-count-fix-01`
Mode: `IMPLEMENT / FIX`
Report: `reviews/worker_reports/steam-recommendation-count-fix-01.md`

## Goal

Fix only the bounded upstream Steam production failure that blocks the already-wired cross-platform giveaway producer:

`recommendation_count_for_appid_out_of_range_1328240`

Do not repeat giveaway recon, redesign giveaway adapters, or change unrelated Steam ranking semantics.

## Read first

- `reviews/worker_reports/cross-platform-giveaway-production-fix-01.md`
- current owning Steam production path around:
  - `scripts/steam_production_cached.py`
  - `update_search_reviews_from_search_html`
  - `parse_recommendation_count`
- relevant existing tests/guards for Steam recommendation/review-count parsing
- relevant `KNOWN_WORKER_PITFALLS.md` entry only if a trigger matches

Do not perform broad history archaeology.

## Required work

1. Reproduce the exact `App_1328240` failure in the smallest bounded way.
2. Determine whether the out-of-range value is:
   - a parsing error / wrong number extracted from current Steam HTML;
   - a legitimate large recommendation count rejected by an obsolete bound;
   - malformed/untrusted source data that should fail closed or be ignored.
3. Fix the owning Steam production parser/validation rule generically.
   - Do not special-case appid `1328240`.
   - Do not silently clamp/fabricate a count unless the canonical contract explicitly calls for that behavior.
4. Add a deterministic regression for the exact failure shape plus nearby normal cases.
5. Run the owning focused tests.
6. Rerun the same canonical workflow:
   - `Steam KZ production shortlist`
7. If the Steam stage passes, allow the already-wired giveaway stages to run and record:
   - Steam/Epic/GOG `source_health`;
   - `snapshot_status`;
   - `accepted_offer_count`;
   - existence/validation of `data/production/giveaways/v1/current.json`.
8. If a different unrelated upstream blocker appears, stop and report that exact blocker instead of broadening scope.

## Validation

Use behavioral/output validation, not source-shape proxies.

Required checks:
- exact failing App_1328240 input no longer crashes for the correct semantic reason;
- normal recommendation-count parsing still works;
- malformed/untrusted values still fail closed or are handled according to the canonical parser contract;
- canonical Steam production stage completes past the former failure;
- if reached, giveaway artifact contract validates and source completeness is reported truthfully.

## Hard boundaries

Do NOT:
- special-case `1328240`;
- weaken validation globally just to make the run green;
- change Taste/ranking weights;
- redesign Steam/Epic/GOG giveaway adapters;
- add another scheduler;
- manually seed giveaway artifacts;
- broaden into unrelated Steam collector cleanup.

## Done when

Either:

A. `complete`
- generic parser/validation fix is in place;
- regression passes;
- canonical workflow rerun gets past the former Steam blocker;
- giveaway stage runs and canonical giveaway snapshot is produced/validated;

or

B. `blocked`
- a new concrete unrelated blocker prevents completion and is captured exactly without scope creep.

## Report format

Save:
`reviews/worker_reports/steam-recommendation-count-fix-01.md`

### Task
What was fixed.

### Root cause
Why App_1328240 triggered the failure.

### Changes
Exact files/commits.

### Validation
Focused tests plus canonical workflow/run refs.

### Giveaway production result
If reached: source health, completeness, accepted count, artifact refs.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only; `none` is valid if complete.

Final response must include report path and exact refs.
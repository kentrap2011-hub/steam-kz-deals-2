# Steam discovery scope reduction implement 01

Status: `implementation_complete_deterministic_green_live_acceptance_pending_after_merge`

Task: `WORKER_TASK_STEAM_DISCOVERY_SCOPE_REDUCTION_IMPLEMENT_01.md`  
Worker slot: `ЧАТ 1`  
Implementation PR: #146  
Branch: `fix/steam-discovery-scope-reduction-implement-01`

## 1. Scope and result

Implemented the approved preservation-first reduction only in the existing GitHub-owned Steam KZ discovery path.

The implementation:
- replaces the production runner's broad combined content-category traversal with explicit paid partitions for `games`, `dlc`, and `bundles`;
- keeps exact App/Sub identity merge/deduplication deterministic;
- enforces the approved current paid gate `discount >= 50%` and `final price <= 4500 KZT` before expensive Reviews API enrichment;
- uses `hidef2p=1` only in paid partitions;
- keeps the existing free/giveaway pipeline separate;
- does not introduce a raw Steam top-N, second collector, scheduler, queue/retry owner, ChatGPT discovery loop, ranking change, Deep/Fast/Dossier change, or Mirror's Edge Catalyst special case;
- exposes source partitions and a deterministic filtering funnel for Statistics/read-only site use.

The completed broad diagnostic was reused and was not repeated.

## 2. Architecture preflight

Confirmed before implementation:

1. **Current owner:** `config/execution_ownership_contract.json` assigns exact discovery scope, completeness, validation, persistence and downstream orchestration to GitHub/GitHub Actions.
2. **Authorization:** the same ownership contract allows the interactive developer/operator chat to edit canonical configuration, scripts and workflows while GitHub retains production control-plane ownership; `config/daily_execution_contract.json` keeps this work inside the existing daily production cycle.
3. **No responsibility transfer:** no scope/queue/retry/completeness responsibility moved to ChatGPT, the browser, or a new component.
4. **No new recurring subsystem:** no scheduler, recurring stage, quota, queue, retry loop or backlog manager was created.

The existing owner remains `.github/workflows/steam-test.yml` -> `collect` -> `scripts/steam_partial_publish_runner.py`, with the existing 60-minute timeout.

## 3. Canonical policy changes

`config/mailing_policy.json` was advanced to v1.22 and now explicitly defines:

- `paid_discovery.source_scope_contract = preservation_first_bounded_paid_v1`;
- `minimum_discount_percent = 50`;
- `maximum_final_price_kzt = 4500`;
- `raw_source_top_n = null`;
- partitions:
  - `games` -> Steam `category1=998`;
  - `dlc` -> `category1=21`;
  - `bundles` -> `category1=996`;
- paid partition requirements: `specials=1`, `cc=kz`, `hidef2p=1`, validated KZ `maxprice=4500`;
- source-side minimum-discount semantics are **not** assumed;
- the parsed-row `>=50%` / `<=4500 KZT` gate is authoritative before Reviews API;
- free/giveaway remains a separate lane;
- completeness means the complete union of the explicit bounded paid partitions, never an arbitrary raw top-N.

`config/mailing_policy.md` was aligned with the same current rule and no longer describes the old broad full-specials feed as the authoritative paid discovery universe.

## 4. Exact source partitions and filters

The production runner traverses the three policy partitions independently in this deterministic order:

1. `games / category1=998`;
2. `dlc / category1=21`;
3. `bundles / category1=996`.

Each paid traversal uses:
- `specials=1`;
- `cc=kz`;
- `ignore_preferences=1`;
- `hidef2p=1`;
- `maxprice=4500`;
- full pagination of that bounded partition;
- no source top-N.

Rows are parsed, then rejected before review enrichment when:
- price is missing/non-paid;
- discount is below 50%;
- price is above 4500 KZT;
- the title matches the existing obvious-extra rules;
- software-only tags are present without game tags.

The exact identity key remains the existing `App_*` / `Sub_*` identity. Cross-partition duplicates are merged deterministically; the earlier partition wins only for the duplicate representation while provenance/counts are retained.

## 5. KZ maxprice trust boundary

The implementation does **not** trust `maxprice=4500` because the query string exists.

Before production partition traversal, `validate_kz_source_price_bound()` performs exactly three bounded live Steam requests on the games partition:

1. capped `Price_DESC` with `cc=kz`, `hidef2p=1`, `maxprice=4500` to obtain the capped total and prove returned capped rows are priced at or below 4500 KZT;
2. uncapped `Price_ASC` at the page containing that expected count boundary;
3. the immediately following uncapped `Price_ASC` page.

The run fails closed unless:
- the uncapped prices are monotonic across the checked boundary;
- the boundary actually crosses from `<=4500` to `>4500 KZT`;
- no `<=4500` row appears after the crossing in the bounded proof window;
- the count inferred from the uncapped KZT boundary equals Steam's capped `total_count`.

Only after that proof is the capped production traversal permitted.

PR regression includes a live-shaped deterministic fixture for a valid boundary and a mismatch fixture that must fail closed.

**Current acceptance state:** the proof logic is implemented and deterministically green, but a real KZ Steam response has not yet been accepted in production because PR runs intentionally have no canonical production-write authority. Therefore this report does not claim real-live `maxprice` acceptance before the post-merge main run.

## 6. 50% enforcement locations

The approved threshold is enforced in all current paid eligibility surfaces touched by this collector:

- canonical `config/mailing_policy.json`;
- `scripts/steam_production.py::paid_source_rejection_reason`;
- `base_item_info`;
- `needs_review_enrichment`;
- `broad_reasons`;
- `refined_reasons`;
- last-known-good preservation guard in `scripts/steam_partial_publish_runner.py`.

This last guard is important: a failed current item cannot re-enter the new shortlist only because an old preserved row existed with a now-ineligible discount below 50% or price above 4500 KZT.

No source-side minimum-discount query parameter was invented.

## 7. Free/giveaway semantics

Paid filtering does not own the free lane.

The existing workflow still runs the canonical Steam/Epic/GOG giveaway producer after the paid Steam collector:
`python scripts/giveaway_production.py`.

The policy retains `data/production/freebies.tsv` and explicitly states that paid filters do not remove the separate free/giveaway lane.

No giveaway scheduler, ownership or eligibility rules were changed.

## 8. Review-enrichment reduction

Previously, rows structurally compatible with thresholds as low as 20/25% and some prices up to 5000 KZT could reach review enrichment even though the newly approved paid product rule is stricter.

Now:
- rows below 50% are eliminated before Reviews API;
- rows above 4500 KZT are eliminated before Reviews API;
- obvious extras/software-only rows are eliminated before Reviews API;
- only surviving paid rows can enter the existing review-quality rule set.

Review-quality thresholds, global/Russian semantics, taste, family resolution and final ranking were not changed.

## 9. Filtering-funnel / Statistics producer fields

The collector now writes the following exact read-only observability fields into `data/production/manifest.json`:

- `search_query_shape = explicit_partitions`;
- `search_combined_category_query_used = false`;
- `search_partitions[]` with per-partition:
  - `reported_total`;
  - `rows_seen`;
  - `parsed_rows`;
  - `eligible_rows_after_local_gate`;
  - `unique_eligible_items`;
  - `rejection_counts`;
  - `duplicate_rows_seen`;
  - `requests_made`;
  - `reached_end`;
- `source_price_bound_validation`;
- `source_rows_seen`;
- `eligible_rows_before_partition_dedupe`;
- `cross_partition_duplicate_identities`;
- `multi_partition_identity_count`;
- `source_validation_requests`;
- `production_collection_requests`;
- `filtering_funnel`, including:
  - source reported/seen/parsed;
  - removed non-paid/missing-price;
  - removed discount below 50%;
  - removed price above 4500;
  - removed obvious extras;
  - removed software-only;
  - eligible before partition dedupe;
  - unique eligible after dedupe;
  - review candidate item/AppID counts;
  - broad shortlist;
  - paid shortlist;
  - old preserved rows dropped by the current paid gate.

The compact shortlist index also carries the scope contract, partition list, price-bound validation flag, 50%/4500 thresholds and `filtering_funnel`.

These fields preserve the data required for a later Statistics UI without moving filtering logic into the browser.

## 10. Site/current-task follow-up kept separate

The requested current-tasks / semantic-analysis-queue page is intentionally not mixed into this collector PR because its owner/state belongs to the semantic pipelines, which this task explicitly forbids inspecting or changing.

Bounded follow-ups already present in project state remain:
- `WORKER_TASK_SITE_CURRENT_TASKS_PAGE_01.md` for the read-only site task/queue view;
- `WORKER_TASK_STEAM_OWNED_LIBRARY_DLC_SUPPORT_01.md` for later owned-library-aware DLC support.

For the discovery/Statistics portion, the exact canonical producer fields needed by the site are listed in section 9. The browser must only present them; it must not filter, reorder or own the discovery queue.

## 11. Deterministic regression coverage

New regression: `scripts/test_steam_discovery_scope_reduction.py`.

It proves:
1. explicit `games/dlc/bundles` partitions and exact query parameters;
2. deterministic App/Sub merge/dedupe;
3. representative game, DLC and `Sub_*` bundle identities survive partition merge;
4. paid discount below 50% is rejected before Reviews API and cannot enter broad/refined shortlist;
5. paid price above 4500 KZT is rejected before Reviews API and cannot enter broad/refined shortlist;
6. exact 50% / 4500 KZT boundary remains eligible;
7. KZ maxprice is accepted only through the bounded boundary proof;
8. mismatched maxprice/count semantics fail closed;
9. free/giveaway remains separate and workflow-owned;
10. discovery scope remains GitHub-owned;
11. no raw source top-N / new schedule is introduced;
12. Mirror's Edge Catalyst/AppID 1233570 is not special-cased.

`.github/workflows/steam-test.yml` now compiles the touched collector modules and runs this regression in PR validation and before normal production collection.

## 12. Regression result

PR #146 initial deterministic validation:
- `Steam KZ production shortlist` run `37317412821`;
- job `regression` / `111787533863`: **success**;
- `collect`: **skipped as intended on pull_request**;
- compile step: success;
- fresh-discovery regression step, including the new bounded scope regression: success.
- `Validate backlog dispositions` run `37317412963`: **success**.

A later report/route-only commit may cause GitHub to attach a newer equivalent PR validation run; final PR head/check status must be read again before Director acceptance.

## 13. Before vs after measurable funnel

Confirmed pre-change baseline from the completed diagnostic:
- problematic current live broad Steam scope: about **100,307 rows** and timeout before persistence;
- last successful older raw scope: **12,977**;
- review-enrichment candidates: **9,923**;
- unique review AppIDs: **9,903**;
- logical Reviews API requests: **19,806**;
- broad shortlist: **1,615**;
- refined paid shortlist: **609**.

Post-change real source/funnel counts are intentionally **not invented**. They will be persisted by the first successful normal main production run in `manifest.search_partitions` and `manifest.filtering_funnel`.

Expected mechanical effect, not yet claimed as measured:
- substantially fewer Steam Search pages due to explicit partition + verified 4500 KZT source bound;
- fewer Reviews API candidates due to early 50%/4500/extras/software gate.

## 14. Live acceptance state and exact remaining action

A normal canonical live acceptance cannot be safely performed from the open PR:

- `steam-test.yml` correctly disables the production `collect` job on `pull_request`;
- the production job writes canonical artifacts and eventually pushes `HEAD:main`;
- running that mutating job from the feature branch would bypass the required PR/merge boundary.

Therefore live acceptance remains one bounded post-merge action after Director authorizes PR #146:

1. merge PR #146 to `main`;
2. observe the normal GitHub-owned `Steam KZ production shortlist` main run triggered by the changed collector/policy paths (manual `workflow_dispatch --ref main` only if the ordinary main trigger does not run);
3. require `collect` success within its existing 60-minute timeout;
4. verify the committed fresh `data/production/manifest.json` and shortlist index report:
   - `complete=true`;
   - validated KZ source price-bound evidence;
   - all three partitions reached end;
   - fresh source timestamp/universe;
   - funnel/source counts;
5. verify the normal downstream handoff starts from that fresh universe/commit.

Until those five checks pass, this report does **not** claim end-to-end production acceptance.

## 15. Runtime/API effect

Measured post-change runtime/API counts are pending the main live acceptance.

The implementation itself exposes exact counters needed to measure the effect:
- source validation requests;
- production collection requests;
- per-partition requests;
- review candidate AppIDs;
- logical review API requests;
- complete filtering funnel.

No timeout was increased and no rate-limit workaround was added; the task reduces work rather than expanding the execution budget.

## 16. PR / merge status

PR: #146 — `Bound Steam KZ discovery scope`.

At the time of this report:
- implementation branch is open against `main`;
- deterministic code validation is green on the initial implementation head;
- no merge has been performed;
- merge is intentionally left to Director authorization;
- real live production acceptance remains post-merge as described in section 14.

## 17. Remaining product choices

None are required to accept this preservation-first implementation.

This task deliberately does **not** decide or implement:
- arbitrary raw top-100 collection;
- a new hard source candidate budget;
- popularity-only pruning;
- Steam-library-aware DLC filtering;
- semantic queue ordering;
- final-site publication/ranking changes.

The current `delivery.fixed_top_n=null` remains unchanged; any downstream final visible ~100 behavior remains a separate canonical publication/ranking concern.

## 18. Final worker status

`implementation_complete_deterministic_green_live_acceptance_pending_after_merge`

Recommended Director action: review PR #146; if accepted, authorize merge and then require the single normal main production acceptance described in section 14 before declaring the production defect fully fixed.

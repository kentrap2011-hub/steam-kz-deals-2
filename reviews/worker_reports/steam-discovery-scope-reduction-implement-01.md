# Steam discovery scope reduction implement 01

Status: `live_validation_corrected_pr147_green_main_acceptance_pending`

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

PR #146 deterministic validation on validated head `9883761f4efbcab3d318c53c531f1130bf0ad39d`:
- `Steam KZ production shortlist` run `37317856886`: **success**;
- job `regression` / `111789040709`: **success**;
- `collect` / `111789042952`: **skipped as intended on pull_request**;
- compile step: success;
- fresh-discovery regression step, including the new bounded scope regression: success;
- `Validate backlog dispositions` run `37317857053`: **success**.

The report-finalization commit after this validated head changes documentation only; the implementation/test/workflow content validated above is unchanged.

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
- implementation branch is open and mergeable against `main`;
- validated implementation/task-finalization head: `9883761f4efbcab3d318c53c531f1130bf0ad39d`;
- deterministic validation on that head is green;
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


## 19. Post-merge live acceptance failure and correction — 2026-10-05

PR #146 was merged to `main` as `fb21b704ac36f56d40bdc6a00175864538dbcee7`.

The first normal GitHub-owned production acceptance ran automatically:

- workflow: `Steam KZ production shortlist`;
- run: `37319401442`;
- collect job: `111794299510`;
- all deterministic regressions passed;
- live collection failed before traversal/persistence with:
  `Steam KZ source price-bound validation failed: Cannot validate KZ maxprice: Price_ASC is not monotonic at cutoff`.

This established that the remaining blocker was the source-bound proof itself, not the deterministic 50%/4500 logic.

### Bounded live evidence

Follow-up PR: **#147 — `Fix Steam KZ live maxprice validation`**.

A temporary bounded probe was executed only in PR validation and then removed from the final branch. It did not run the production collector or write canonical production state.

The decisive probe was run `37334852442`, regression job `111846921732`.

Observed games-partition evidence with `cc=kz`, `hidef2p=1`:

- exact `maxprice=4500`:
  - `Price_ASC total_count=63681`, sampled prices all `150 KZT`;
  - `Price_DESC total_count=63681`, sampled maximum exactly `4500 KZT`;
  - `Name_ASC total_count=63681`, sampled maximum `3200 KZT`;
- arbitrary low values `maxprice=10/20/50/100/1000` behaved like an ignored/unbounded control:
  - `total_count=65097`;
  - sampled `Price_DESC` prices reached `74400 KZT`.

Therefore the live evidence supports **case 1** from the continuation task:

- the exact current Steam filter token `maxprice=4500` is materially active for the KZ query;
- the previous validation was invalid because it assumed globally monotonic `Price_ASC`;
- arbitrary numeric `maxprice` values must not be generalized as continuous KZT semantics.

### Correction

`scripts/steam_partial_publish_runner.py::validate_kz_source_price_bound` no longer uses a positional `Price_ASC` boundary or early-stop proof.

The corrected fail-closed proof uses only bounded direct controls:

1. for each supported paid partition (games/DLC/bundles), query capped `Price_DESC` with exact `maxprice=4500` and reject any sampled row above 4500 KZT;
2. query games with the same cap under `Name_ASC` and require the same capped `total_count`;
3. query an otherwise-identical **uncapped** games `Price_DESC` control and require:
   - a larger source total than the capped query; and
   - at least one sampled over-4500-KZT row.

This directly proves that the exact 4500 filter is active in the current KZ response without treating Steam's sort order as a completeness authority.

Local parsed-row `<=4500 KZT` validation remains authoritative on every production row, and the approved `discount >= 50%` gate is unchanged.

### Regression matching the real failure

`scripts/test_steam_discovery_scope_reduction.py` now explicitly proves:

- the validator succeeds without making any `Price_ASC` request;
- games/DLC/bundles capped samples are all checked;
- sort-invariant capped total is required;
- an uncapped larger/over-cap control is required;
- an over-cap row leaking from any capped partition fails closed;
- a non-material/ignored cap fails closed.

Temporary live-probe code and workflow changes were removed after evidence collection.

### PR #147 deterministic validation

Final implementation code head before documentation-only commits:
`c4930141ad5d604dfe681248fe6b6b283a58543c`.

Checks:

- `Steam KZ production shortlist` PR run `37335316576`: **success**;
- regression job `111848645135`: **success**;
- production `collect`: skipped as intended on pull_request;
- `Validate backlog dispositions` run `37335316556`: **success**.

No Scheduled Task, Dossier, Deep, Fast, ranking, site logic, source top-N, new scheduler/queue/retry owner, timeout, or Catalyst-specific rule was changed.

### Remaining live acceptance

After PR #147 is merged to `main`, one normal GitHub-owned production acceptance is still mandatory.

It must prove:

1. corrected live KZ source-bound validation passes;
2. all three bounded partitions complete;
3. collector completes inside the existing 60-minute timeout;
4. a fresh canonical discovery universe is committed;
5. actual partition/funnel/request/review counts are persisted;
6. downstream handoff starts from that fresh universe.

Until those checks pass, the overall production defect remains open even though the correction is deterministic-green.


## 19. PR #147 merge and second normal live acceptance

PR #147 was merged to `main` as:

`3ca7e6c12214756a847a5f5170d497dffb044c85`.

The resulting normal GitHub-owned production acceptance was:

- workflow run: `37335826933`;
- collect job: `111850233215`;
- all deterministic pre-collection regressions: **success**;
- collector step started: `2026-10-05T15:48:57.8182056Z`;
- job was cancelled at the existing ~60-minute owner timeout window:
  `2026-10-05T16:49:04.6268716Z`;
- no canonical production commit or downstream handoff occurred.

This run proves that the corrected `maxprice=4500` validation can start normal production, but the resulting source scope is still too large under the old 50-row pagination.

### Exact last live traversal progress

The completed job logs became available after cancellation and showed:

**games**
- first page: `start=0 rows=50 total=63683` at `15:52:44Z`;
- last page: `start=63650 rows=39 total=63689` at `16:40:20Z`;
- all **63,689** reported game rows were traversed;
- **41,654** rows had survived the local paid/discount/price/extras/software gate by the end of the partition;
- 1,274 successful 50-row page responses were logged;
- approximately **47.6 minutes** elapsed from the first games page to the final games page.

**DLC**
- began immediately after games at `16:40:20Z`;
- live total was approximately **34,354–34,356**;
- last observed page before timeout: `start=13700 rows=50`;
- **7,245** rows had survived the local gate at that point;
- only 275 successful DLC pages were reached before cancellation.

**bundles**
- did not start before the owner timeout.

The run logged **204 individual HTTP 429 responses**:
- 168 while in games traversal;
- 36 while in DLC traversal.

The repeated retry pattern was normally `3 + 6 + 12 + 24` seconds before a successful page, so the primary live bottleneck is confirmed as Steam Search pagination plus rate-limit backoff, not Reviews API enrichment.

This is a bounded continuation of the implementation acceptance, not a repeat of the earlier global diagnostic.

## 20. Mandatory live progress observability correction

The old collector emitted a line for every successful page, but Python buffering made those lines appear in large delayed batches in Actions. While a job was running, GitHub's job-log download endpoint also returned 404, so the Director could see only that the single collector step was still `in_progress`.

Follow-up PR **#148 — `Expose Steam collector progress and probe discount source filter`** adds permanent observability to the existing GitHub-owned collector only.

### Permanent progress output

`scripts/steam_partial_publish_runner.py` now emits flushed structured `[steam-progress]` JSON with:

- a 30-second heartbeat;
- explicit stage names:
  - `source_validation`;
  - `search_traversal`;
  - `local_merge_filter`;
  - `review_enrichment`;
  - `shortlist_selection`;
  - `persistence_preparation`;
  - `complete`;
- partition name / category;
- current page number and logical page-request count;
- current row offset;
- rows seen;
- Steam-reported partition total;
- progress percentage when total is known;
- cumulative eligible rows after the local gate;
- duplicate count;
- review candidate AppID total;
- completed review AppIDs / logical review components;
- fallback batch progress;
- elapsed time for the current stage and whole collector.

`scripts/steam_production.py` now exposes thread-safe live network counters for:

- Search HTTP requests;
- Search retry events;
- Search 429 events;
- Search backoff seconds;
- Reviews HTTP requests;
- Reviews retry events;
- Reviews 429 events;
- Reviews backoff seconds.

The workflow invokes the production collector as `python -u` so progress is not hidden by Python stdout buffering.

The successful manifest additionally carries:
- `stage_timings_seconds`;
- per-partition elapsed seconds;
- `network_stats`.

No timeout, scheduler, queue/retry owner, discovery ownership, product threshold, semantic stage or production writer was added or changed.

## 21. Bounded source-reduction probes after the timed-out run

The timed-out run demonstrated that exact KZ `maxprice=4500` is active but only reduces games from roughly 65k uncapped rows to roughly 63.7k capped rows. Therefore further semantics-preserving request reduction was investigated immediately with bounded read-only PR probes; no second production writer was started.

### Source-side 50% discount parameters are not available through tested query shapes

PR #148 bounded probe run `37344048116` showed that all tested candidate query parameters were ignored by the live Steam endpoint:

- `discounts=50`;
- `discounts=70`;
- `discounts=90`;
- `discount=50`;
- `min_discount=50`;
- `min_discount_pct=50`.

Every variant returned the same games `total_count=63691` as the baseline and first-page samples still contained discounts from **10% through 49%**.

Therefore no source-side minimum-discount filter was added. The authoritative `>=50%` parsed-row gate remains local and fail-closed.

### Steam Search supports complete 100-row pages

A second bounded PR probe, run `37344778557`, proved:

- `count=100,start=0` returned 100 rows / 100 unique identities;
- `count=100,start=100` returned the next 100 rows / 100 unique identities;
- both reported the same live `total_count=63692`;
- overlap between those two contiguous 100-row pages was **zero**;
- requests with `count=200` and `count=500` were capped by Steam at 100 returned rows.

This provides a semantics-preserving request reduction: the canonical collector page size is changed from **50 to 100**, the largest live-proven page size. Candidate completeness, source ordering and eligibility rules are unchanged.

For the observed run shape, this halves the number of successful Search pages required for the same source universe:
- games: roughly 1,274 -> roughly 637 pages;
- DLC: roughly 687 -> roughly 344 pages at the observed ~34.35k total;
- bundles remain separately complete.

No raw top-N or early stop is introduced.

## 22. PR #148 deterministic validation

Permanent PR #148 final code excludes all temporary live-probe scripts/steps.

Final implementation scope is limited to:
- `scripts/steam_production.py` — 100-row page size + network metrics;
- `scripts/steam_partial_publish_runner.py` — progress heartbeat/stage/timing/metrics;
- `scripts/test_steam_discovery_scope_reduction.py` — deterministic guards;
- `.github/workflows/steam-test.yml` — unbuffered collector invocation;
- task/report/route documentation.

Validated PR head before this report update:
`37c149b6a6ad3a8678edf8814e90b1db89c2775d`.

Checks:
- `Steam KZ production shortlist` PR run `37345208967`: **success**;
- regression job `111882026732`: **success**;
- PR production `collect`: skipped as intended;
- `Validate backlog dispositions` run `37345209009`: **success**.

Regression coverage now also checks:
- canonical page size is exactly 100;
- search params use that page size;
- progress snapshots carry stage/page/rows/total/eligible/duplicate/network fields;
- network retry/backoff counters expose the required metrics.

## 23. Current acceptance state after PR #148

The production defect is **not yet declared fixed**.

The next required action, after PR #148 is cleanly merged under the existing continuation authorization, is one normal `main` GitHub-owned production run.

It must prove all of the following:

1. live progress/heartbeat output is visible while the collector is running;
2. games, DLC and bundles all finish;
3. the same complete bounded discovery universe is preserved with 100-row pagination;
4. the collector finishes inside the existing 60-minute timeout;
5. a fresh canonical manifest/shortlist is persisted;
6. actual funnel, partition timing and network/review counters are present;
7. downstream handoff starts from that fresh universe.

If the 100-row change still cannot complete inside the existing owner timeout, the next investigation must use the newly visible stage metrics rather than another opaque wait or a lossy source truncation.


## 24. PR #148 merge and active main acceptance

PR #148 was merged to `main` as:

`28a94de86ba18dce37e5f944a81ce7c944e07d8c`.

The required normal GitHub-owned acceptance started automatically:

- workflow: `Steam KZ production shortlist`;
- run: `37345668260`;
- collect job: `111883491529`;
- event: `push`;
- source head: PR #148 merge commit above;
- all pre-collection deterministic steps completed successfully;
- `Collect Steam KZ catalog with partial publish failure isolation` is currently `in_progress`.

No competing production writer was started.

A later bounded diagnostic attempt, PR #149, was closed without merge because the existing `steam-kz-production` concurrency group correctly kept its PR validation pending behind the active production run. It contains no canonical changes and was not used as production evidence.

Current status remains:

`pr148_merged_normal_main_acceptance_in_progress`.

Do not claim the production defect fixed until run `37345668260` either:
- succeeds and persists the fresh complete universe + downstream handoff, or
- terminates with stage-level heartbeat/network/timing evidence that identifies the next bounded correction.

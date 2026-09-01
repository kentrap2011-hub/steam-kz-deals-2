# Steam recommendation count blocker fix 01

Task ID: `steam-recommendation-count-fix-01`  
Date: 2026-09-01

## Task

Resolve the bounded Steam blocker named in `WORKER_TASK_STEAM_RECOMMENDATION_COUNT_FIX_01.md` and repeat the canonical `Steam KZ production shortlist` run without re-investigating giveaway sources or broadening into unrelated Steam/ranking work.

The reported blocker `recommendation_count_for_appid_out_of_range_1328240` was checked against the actual owning code and the actual failed Actions run before making a code change. It was not reproducible and is not present in the current or failed-head collector implementation. A canonical rerun of the same production workflow then completed successfully end to end, including the cross-platform giveaway producer and artifact commit.

## Root cause

The blocker attribution inherited from `reviews/worker_reports/cross-platform-giveaway-production-fix-01.md` was incorrect.

Evidence:

- actual failed run: `Steam KZ production shortlist`, run ID `33539362872`, attempt 1, job `99961473887`, head `dc4edd9a72a522b080c1d168a05f239707214e37`;
- the actual job log did **not** contain `recommendation_count_for_appid_out_of_range_1328240` and did not call `update_search_reviews_from_search_html` / `parse_recommendation_count`;
- the real terminal failure in attempt 1 was:

```text
Full Steam traversal completeness check failed: unique=16439 reported=16441
Process completed with exit code 1.
```

- `scripts/steam_production.py` on current `main` and at the failed head contains neither `parse_recommendation_count` nor `update_search_reviews_from_search_html`;
- repository code search also returned no owning implementation for `recommendation_count_for_appid_out_of_range` or App `1328240`.

Therefore a parser change, larger numeric bound, special-case App ID, or synthetic regression around those nonexistent functions would have been an invented fix and would violate the task's hard boundaries.

The actual attempt-1 blocker was the existing fail-closed Steam traversal completeness guard while the storefront's reported total changed during the long crawl. On canonical rerun attempt 2 the traversal was stable and exact:

- `steam_total_reported = 16451`;
- `unique_items = 16451`;
- `rows_seen = 16451`;
- `duplicate_rows_seen = 0`;
- `coverage_ratio = 1.0`;
- `complete = true`;
- `recovery_pass_used = false`.

No Steam code change was necessary to obtain a valid complete production snapshot.

## Changes

No Steam collector/parser code was changed.

No App-specific special case was added.

No new recommendation-count regression was added because the alleged parsing path does not exist in the canonical collector and the alleged failure is not present in the actual run log. Existing behavioral production and giveaway regressions were used instead, followed by a real canonical run.

Production output created by the successful canonical rerun:

- production commit `50b763ba7ecb1b6e781be48ca2b17b0599d9d4ac` — `Update Steam KZ production and giveaways`;
- `data/production/giveaways/index.json` blob `4d3431540bdc669e1fd646da9d611f337cf22a87`;
- `data/production/giveaways/v1/current.json` blob `9a582fc18180807d44a514c2d1c1294655604574`;
- `data/production/giveaways/v1/audit.jsonl` blob `0942e19d292462ce1ec9aaa7cb716a390c308d76`.

The production commit rebased onto then-current `main` (`83e7150134af9cb7c25b0886235e11e7919a9e21`) and pushed successfully. Existing downstream GitHub-owned production jobs subsequently advanced `main`; giveaway artifacts remain present on current `main`.

## Validation

Canonical workflow rerun:

- workflow: `Steam KZ production shortlist`;
- run ID: `33539362872`;
- run number: `20`;
- attempt: `2`;
- head SHA: `dc4edd9a72a522b080c1d168a05f239707214e37`;
- job ID: `99989757334`;
- final conclusion: `success`.

Exact step results:

- `Regression test production output ownership` — `success`;
- `Regression test cross-platform giveaways` — `success` (`Ran 15 tests` / `OK`);
- `Collect full Steam KZ catalog and build production shortlist` — `success`;
- `Verify Steam collector touched only owned production paths` — `success`;
- `Build canonical Steam Epic GOG KZ giveaways` — `success`;
- `Validate canonical giveaway artifact contract` — `success`;
- `Verify production writers touched only owned paths` — `success`;
- `Commit production feed, giveaways and review cache` — `success`.

Steam collector result in attempt 2:

```text
collector_version: 7
steam_total_reported: 16451
unique_items: 16451
rows_seen: 16451
duplicate_rows_seen: 0
recovery_pass_used: false
coverage_ratio: 1.0
complete: true
review_candidate_appids: 12810
review_api_failed_requests: 0
free_items: 0
```

The successful production commit was created in-run, rebased, and pushed as `50b763ba7ecb1b6e781be48ca2b17b0599d9d4ac`.

## Giveaway production result

Canonical contract: `CROSS-PLATFORM-GIVEAWAY-V1`.

Generated at: `2026-09-01T19:30:40.405647Z`  
Fresh until: `2026-09-03T01:30:40.405647Z`  
Snapshot status: `complete`  
Accepted offer count: `2`  
Game group count: `2`  
Rejected offer count: `7`  
Unverified offer count: `0`

Tier-1 source health:

- **Steam:** `status=ok`, `complete=true`, candidates `0`, accepted `0`, rejected `0`, unverified `0`, `error_code=null`, targeted validation errors `0`;
- **Epic:** `status=ok`, `complete=true`, candidates `9`, accepted `2`, rejected `7`, unverified `0`, `error_code=null`;
- **GOG:** `status=ok`, `complete=true`, candidates `0`, accepted `0`, rejected `0`, unverified `0`, `error_code=null`, targeted validation errors `0`.

Accepted current KZ offers are the two Epic full-game claim-to-keep promotions present in the canonical artifact at generation time:

- `Breathedge` — promotion end `2026-09-03T15:00:00Z`;
- `Rival Stars Horse Racing : Desktop Edition` — promotion end `2026-09-03T15:00:00Z`.

The canonical `--validate-only` stage passed before commit, and all three versioned giveaway artifacts exist on `main`.

Efficiency / reusable lesson: candidate — verify the actual terminal Actions log and owning code before deriving a follow-up blocker task from a worker report; this is the same observable-behavior principle as `KNOWN_WORKER_PITFALLS.md` PITFALL-001.

## Status

`complete`

The named recommendation-count blocker was an incorrect prior attribution, not a reproducible defect in the canonical collector. The same canonical production workflow was rerun without weakening any guard and completed successfully through Steam collection, giveaway generation, validation, ownership checks, and production commit. No scoped blocker remains.

## Recommended next step

`none`

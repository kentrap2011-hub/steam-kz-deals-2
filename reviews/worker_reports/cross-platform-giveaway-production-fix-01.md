# Cross-platform giveaway PRODUCTION FIX 01

Task ID: `cross-platform-giveaway-production-fix-01`  
Date: 2026-09-01

## Task

Finished the repository-side production wiring that was missing after `cross-platform-giveaway-implement-01` without repeating source recon or redesigning the Steam/Epic/GOG adapters.

Implemented in this fix:

- aligned deterministic giveaway fixtures with the canonical first-party claim-URL guard;
- wired `scripts/test_giveaway_production.py` into the existing canonical GitHub-owned daily production workflow;
- wired `scripts/giveaway_production.py` into the same workflow after the existing full Steam KZ refresh;
- added canonical artifact validation for `CROSS-PLATFORM-GIVEAWAY-V1`;
- added production-path ownership verification covering the legacy Steam output family plus the separate giveaway output family;
- staged `data/production/giveaways/**` only from the canonical giveaway producer path;
- kept the existing single daily cron and `workflow_dispatch`; no new recurring schedule was added.

## Production wiring

Canonical workflow:

- `.github/workflows/steam-test.yml`
- workflow name: `Steam KZ production shortlist`
- existing daily cron remains `10 20 * * *`
- existing manual entry point remains `workflow_dispatch`

Relevant stage order after the fix:

1. `Regression test production output ownership`
2. `Regression test cross-platform giveaways`
3. `Collect full Steam KZ catalog and build production shortlist`
4. `Verify Steam collector touched only owned production paths`
5. `Build canonical Steam Epic GOG KZ giveaways`
6. `Validate canonical giveaway artifact contract`
7. `Verify production writers touched only owned paths`
8. `Commit production feed, giveaways and review cache`

Writer ownership remains separated:

- existing Steam collector owns `data/production/manifest.json`, `data/production/freebies.tsv`, `data/production/freebies_index.json`, `data/production/shortlist/**`;
- `scripts/giveaway_production.py` alone owns `data/production/giveaways/**`;
- no second writer for legacy `freebies*` was introduced.

## Production result

Canonical production run:

- workflow: `Steam KZ production shortlist`
- run number: `20`
- run ID: `33539362872`
- event: `push`
- head SHA: `dc4edd9a72a522b080c1d168a05f239707214e37`
- job ID: `99961473887`
- run URL: `https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/33539362872`
- final conclusion: `failure`

The run failed before the giveaway producer stage, inside the pre-existing full Steam KZ collector. Exact failure:

```text
scripts/steam_production_cached.py
  main -> crawl -> update_search_reviews_from_search_html -> parse_recommendation_count
OSError: recommendation_count_for_appid_out_of_range_1328240
Process completed with exit code 1
```

The log immediately before the failure showed the existing Steam snapshot context:

```text
Items: 15778; shortlist: 701; free: 1
Rate limit: total=9, cache=2, api=7, sleep=2.6s
```

### Tier-1 health for this run

Because the required upstream Steam collection failed before `scripts/giveaway_production.py` ran, no canonical `source_health` object was emitted. The only truthful per-source state for run `33539362872` is:

- **Steam:** prerequisite/full-catalog production stage `failed`; giveaway adapter/source-health stage was not reached;
- **Epic:** `not executed` / giveaway stage skipped after upstream failure;
- **GOG:** `not executed` / giveaway stage skipped after upstream failure.

These states must not be rewritten as successful source refreshes.

### Completeness

- canonical giveaway snapshot: **not produced**;
- `snapshot_status`: **not produced**, therefore not `complete`;
- Tier-1 completeness cannot be claimed;
- fail-closed behavior was preserved: no stale or manually seeded giveaway snapshot replaced the missing result.

### Accepted current offer count

- canonical `accepted_offer_count`: **not produced / unknown**;
- it is explicitly **not treated as `0`**, because Steam/Epic/GOG did not all refresh successfully and no complete `CROSS-PLATFORM-GIVEAWAY-V1` snapshot exists.

Verified current `main` state after the failed run:

- `data/production/giveaways/index.json` — absent;
- `data/production/giveaways/v1/current.json` — absent;
- `data/production/giveaways/v1/audit.jsonl` — absent;
- no `Update Steam KZ production and giveaways` production commit was created.

## Changes

Exact scoped commits from this production-fix task:

- `0ff8f8dae0942ab563035c1046f7249c80741cd1` — `scripts/test_giveaway_production.py`: align accepted fixtures with the first-party URL guard;
- `dc4edd9a72a522b080c1d168a05f239707214e37` — `.github/workflows/steam-test.yml`: wire giveaway tests, producer, artifact validation, ownership guard and staging into the existing canonical daily production path.

No Steam/Epic/GOG adapter redesign was performed in this fix.

## Validation

Canonical run `33539362872`, job `99961473887` produced these exact step results:

- `Regression test production output ownership` — `success`;
- `Regression test cross-platform giveaways` — `success`;
- deterministic giveaway suite result: `Ran 15 tests` / `OK`;
- `Collect full Steam KZ catalog and build production shortlist` — `failure`;
- `Build canonical Steam Epic GOG KZ giveaways` — `skipped`;
- `Validate canonical giveaway artifact contract` — `skipped`;
- `Verify production writers touched only owned paths` — `skipped`;
- `Commit production feed, giveaways and review cache` — `skipped`.

Therefore:

- deterministic giveaway validation is successfully wired and passes in the canonical route;
- single-writer integration is present in the workflow and the pre-run ownership regression passes;
- end-to-end giveaway artifact validation cannot pass or fail yet because the existing Steam collector aborts before the giveaway stage;
- no second scheduler or writer was introduced.

## Status

`blocked`

The production integration itself is wired, but the required canonical run cannot reach the giveaway producer because the existing upstream Steam production collector aborts on `recommendation_count_for_appid_out_of_range_1328240`. The task cannot truthfully be marked complete while the canonical giveaway artifacts do not exist.

## Recommended next step

Fix the bounded upstream Steam collector failure for `App_1328240` (`recommendation_count_for_appid_out_of_range_1328240`) in the owning Steam production path, then rerun the same canonical workflow and record the resulting Steam/Epic/GOG `source_health`, `snapshot_status` and `accepted_offer_count` from `data/production/giveaways/v1/current.json`.

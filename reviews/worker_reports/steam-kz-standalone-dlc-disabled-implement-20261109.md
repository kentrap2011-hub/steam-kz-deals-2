# Steam KZ: disable standalone DLC until owned Steam library — implementation

**Status:** IMPLEMENTED_ON_ISOLATED_PR; PR-only regression observed PASS; production rollout NOT DONE.  
**User authorization:** "Переделай" (2026-11-09), after successful complete offline replay of the same day's cached catalog without standalone DLC.  
**Repository:** only kentrap2011-hub/steam-kz-deals-2.  
**Base main SHA:** d99ce24fce32ecab076f02c6039353d3be1de343.  
**Source PR:** [#428](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/428) draft; no self-merge.  
**Snapshot QA:** [PR #427](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/427), [run 42678253183](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42678253183).

## Root decision / contract

Old current source contract was eligible_base_targeted_dlc_and_independent_sub_v3: verified parent appdetails of 365 games and 1385 distinct DLC-related AppIDs was mandatory even without owned-game data. Completed 2026-11-09 production collector took 3045.632 seconds (50m 45.632s); targeted DLC portion 2817.441s (~46m57s). That day's complete 907-item paid shortlist contains 365 non-targeted App_ offers, 14 independent Sub_ offers and 528 standalone targeted DLC offers. The exact 907→379 snapshot projection was tested using full stored source and mailing chunks; the real family resolver accepted all allowed 368 rows into 365 family groups.

The user chose to remove independent standalone DLC deals until a future owned-Steam-library discovery feature, rather than continue paying 47m each day for unowned-game DLC. This intentionally removes story DLC as well as non-story standalone offers. Package contents may still include DLC, so removing or suppressing Sub_ or package membership would be incorrect.

New canonical policy: source_scope_contract = game_and_independent_sub_without_standalone_dlc_v1, dlc_discovery.mode = disabled_until_owned_library, standalone_offers_enabled = false, requires_complete_verified_relations = false, global_category1_21_traversal = false, owned_base_expansion = separate_future_task. Complete source now refers to FULL KZ games/Sub search and matching local paid eligibility, NOT to a silently incomplete old DLC graph. The prior broad DLC product decision is superseded only in this specific source scope.

## Files and behavior

- config/mailing_policy.json / config/mailing_policy.md: update source scope, completeness and disabled DLC semantics; retain KZT>=50%, paid <=4500 KZT, no raw Top-N, independent on-sale Sub_ package lane and separate giveaway lane.
- scripts/steam_production.py: reject startup under an incompatible scope/mode that could accidentally re-enable unrelated DLC discovery.
- scripts/steam_targeted_paid_lanes.py: current_standalone_dlc_offers returns empty mapping plus honest zero appdetails request/relation metrics and scope_complete=true, relation_complete=null. The old discover_dlc_for_bases function remains available to deterministic historical tests/future approved owned-game feature, but never runs from current production collector.
- scripts/steam_partial_publish_runner.py: invoke zero-network disabled function while still selecting the base suitability set, processing independently discovered Sub_ packages, building the normal shortlist and source manifest. The prior paid outputs are unchanged on failure.
- scripts/validate_mailing_policy.py / scripts/test_steam_targeted_paid_lanes.py: policy guards, zero GET proof, no silent legacy fallback, rejection of accidental mode enablement, current games/Sub package admission test; original KZ DLC lineage and 429 guard tests remain.
- PROJECT_DECISIONS.md / PROJECT_ROUTES.md: durable product rationale and implementation route.

No new recurring workflow, queue/retry manager, source partition, networking, manual full collector run or production artifact writes. Historical semantic caches and legacy DLC tests are not removed.

## Verified tests and evidence

- Exact source PR code head 8a94837f3a7fdc52e254d3c28efca7cbc6e71b15: [GitHub Actions run 42681638405](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42681638405) completed SUCCESS, PR regression job SUCCESS, collect job SKIPPED. Log: "targeted Steam KZ DLC and independent package 19/19 PASS"; steam discovery scope regressions 20/20 PASS.
- Today's complete saved data (PR #427) proved 907 unique, 528 target DLC excluded, 365 non-target App_ preserved, 14 Sub_ preserved, all 379 KZT prices, discount percentages, names and IDs identical, 375 active Store, 368 eligible for family, 365 complete families.
- Source code policy+guard prohibits normal source from calling DLC appdetails. This is an isolated deterministic check, NOT a fresh live collector timing nor full downstream rebuild/deploy.

## Production rollout caution / blockers

1. **GitHub workflow trigger:** .github/workflows/steam-test.yml has main-push paths covering both config/mailing_policy.json and scripts/steam_partial_publish_runner.py. Merging source PR #428 into main will automatically dispatch a full collector, violating the explicit no-repeated-full-Steam-Action objective for the same day. Do not merge without accounting for this workflow trigger and the user's no-rerun constraint.
2. Existing data/production/shortlist, mailing, pre_ai and visual artifacts still bind to the OLD 907-item source generation and old source_scope_contract; do not mark them newly complete for 379 items by hand, falsify their timestamps, delete DLC caches or publish a mixed-generation visual. Full downstream rebind/new current source generation is required.
3. First accepted live no-DLC run and site publication have NOT happened. No actual "4-minute" runtime has been measured. Future accepted run must prove the games and packages remain complete under current KZ conditions, zero standalone DLC, acceptable complete snapshot, successful mailing/feed validation, intact package contents and past semantic histories, and visible site payload. Recheck actions/push gates and work coordination before any merge.

**Disposition:** SOURCE PR READY FOR EXACT-HEAD CI/independent acceptance; NOT PRODUCTION DEPLOYED; NO ADDITIONAL STEAM COLLECTOR RUN.
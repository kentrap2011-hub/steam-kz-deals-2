# Independent source QA — Steam listed-root alias PR #408

**Task:** `steam-listed-base-alias-pr408-independent-qa-01`  
**Date:** 2026-11-06 UTC  
**Repository:** `kentrap2011-hub/steam-kz-deals-2`  
**Mode:** independent source QA, read-only against source; this report is the only QA change  
**Source PR:** https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/408 (draft/unmerged)  
**Exact audited source HEAD:** `d3000e5cc66e1f2d1989232e97f0f55494068e04`  
**Report branch base:** `main` at `f08b0b476f1a794c9194527b17c0421e3d48d529`  
**Disposition: PASS — independent SOURCE/PR-only QA; NOT a live recovery acceptance.**  
**Substantive risk:** LOW for observed narrow source guard / MEDIUM L3 operational risk until a complete normal main collection succeeds.

## Scope, contracts, material delta

Read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, the exact QA task, relevant `PROJECT_ROUTES.md` route, `config/execution_ownership_contract.json`, and `config/mailing_policy.json#paid_discovery`. GitHub remains the collection/validation/publication owner; paid KZ discovery requires complete verified parent relations, `cc=kz`, discount >= 50% and final <= 4500 KZT. Inspected the complete five-file source PR delta: `scripts/steam_targeted_paid_lanes.py`, `scripts/test_steam_targeted_paid_lanes.py`, `PROJECT_DECISIONS.md` (STEAM-ALIAS-001), `CURRENT_TASK.md`, and `reviews/worker_reports/steam-listed-base-alias-1697640-implement-01.md`. Compared the source baseline `5e4fd5c` with current `main`: two subsequent commits only affect director task docs/config and the current QA task, not these source/runtime files.

Historical incident: 2026-11-05 normal collection run https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42033530995 observed HTTP 200 on request `1697640`, then an exact inner-ID contradiction, with 1223 HTTP 200 responses and no 429. Historical raw inner ID/root relation were not logged. Separately, the user's current 2026-11-06 official KZ API JSON for `1697640` shows `success=true`, `type=game`, integer `data.steam_appid=239140`, and `dlc` membership including `1697640`. This is current user-provided evidence, not a preserved historical response. RECON is in draft report-only PR #407.

## Independent source observations

1. **Exact identity and opt-in containment — PASS.** `scripts/steam_targeted_paid_lanes.py:211-302`: `get_appdetails` canonicalizes the requested ID, requests `appids=<requested>&cc=kz&l=english`, retains its original 4-attempt bounded 429/5xx/transport fail-closed behavior and invokes the existing strict mismatch guard unless `_is_verified_listed_base_alias` succeeds. Default `verified_base_aliases=()` grants no exception. No external ID mapping, title-only heuristic or root price inheritance.
2. **Sole proven root and reverse edge — PASS.** Lines 342-363, 375-426: only `type=game`, a canonical *different* `steam_appid`, `len(listed_bases)==1`, root-ID equality, absent/null `fullgame`, and exact requested member in the alias-returned `dlc` list qualify. `_dlc_ids` rejects malformed members, invalid list type and owner self-reference. `direct` is generated exclusively from previously fetched identity-checked `type=game` admitted parent responses, not from supplied arbitrary roots. Duplicated parent members collapse to exact set membership; two independent eligible roots listing one alias prevent exemption.
3. **Actual production caller / mock realism — PASS.** `scripts/steam_partial_publish_runner.py:1316-1339` calls `targeted.discover_dlc_for_bases(base_admitted_ids, core, reporter=reporter)` without overriding `fetch`. Thus the default `fetch=get_appdetails` is precisely the production function, and `if fetch is get_appdetails` at `steam_targeted_paid_lanes.py:412-420` is TRUE for the real call. Parent worker futures call `fetch(base)` without alias context. Exactly the first-hop child loop passes `verified_base_aliases=direct[appid]`. Nested lookups at lines 463-469 call `fetch(appid)` with no exemption. The test `check_verified_listed_base_alias_1697640` patches and explicitly passes the same callable; this represents the real branch rather than concealing a production wrapper.
4. **No paid alias / genuine siblings remain — PASS.** At lines 419-427 proven aliases enter `excluded_base_aliases` and are skipped before `fetched`, nested expansion, pricing and offer creation. At 431-460 an excluded alias cannot be used as a nested intermediate/child; any re-entry as a nested child raises. `all_ids` at 488-492 subtracts only proven aliases; separately-priced valid `type=dlc` children continue through the original parent/fullgame/KZT/discount path at 493-562. No `App_1697640` offer or borrowed `App_239140` price. The test fixture pairs alias 1697640->239140 and eligible genuine child 1700000 (250 KZT, 85%), expects only `App_1700000` and keeps exact parent chain.
5. **Counts and completeness — PASS within defined scope.** `related_dlc_unique_ids=len(all_ids)` excludes aliases, `dlc_price_lookups=len(fetched)+len(excluded_base_aliases)` includes actual unique child lookups, and `verified_base_game_alias_exclusions` discloses exclusions (`steam_targeted_paid_lanes.py:564-577`). The direct one-pass fetched set and nested overlap do not double-count distinct GETs. `relation_complete=len(relations)==len(bases)` is reached only after the parent/direct/nested loops return; any exception aborts before stats/publication. In `steam_partial_publish_runner.py:1325-1339`, relation failure stops the job before new publication, explicitly retaining prior paid data; the existing `preserve_last_known_good` flow is unchanged.
6. **Negative and price/HTTP guards — PASS for code review / existing deterministic coverage.** New test exercises foreign canonical ID, `type=dlc`, absent reverse membership, malformed alias `dlc`, foreign `fullgame`, multiple listed bases, malformed canonical inner IDs and nested alias overlap. Existing regression functions cover invalid/duplicate parent `dlc`, unrelated exact-ID contradictions, price missing/null versus partial KZT/foreign currency/wrong types, discount/4500 KZT gating, parent chains/cycles/third-hop, shared physical-start 180/rolling-300s across parent/child/retries, 120s own 429 and 900s full deadline guards, four attempts, 429 Retry-After/5xx/transport fail-closed. No source diff changed the existing pacing, pricing, retry, policy or publication code.

## Exact-HEAD GitHub CI

Checked actual GitHub Actions check-runs and workflow jobs for source HEAD `d3000e5cc66e1f2d1989232e97f0f55494068e04` (not earlier `f7b57fb`):

| Required gate | Check/run | Verified conclusion |
| --- | --- | --- |
| `steam-test.yml/regression` | https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42203298027 | **SUCCESS**, head matches; compile and fresh-discovery steps success; targeted 18/18 asserted by source PR/report |
| `validate` | https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42203297965 | **SUCCESS**, head matches |
| `backlog-disposition` | https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42203297842 | **SUCCESS**, head matches |
| `collect` | same `steam-test.yml` run | **SKIPPED** by existing pull-request event gate; no live recovery evidence |

No new offline test execution is claimed beyond independent source/test review and verified existing CI. The source HEAD remained exact `d3000e5cc66e1f2d1989232e97f0f55494068e04` at the final independent QA check.

## L2/L3 risk assessment and boundaries

- **L2 source/contract risk: LOW, no blocking counterexample identified.** Alias recognition is narrow and fail-closed, and the code path from the real production caller is proved. Existing `_check_fetched_identity` intentionally accepts an absent inner `steam_appid` (it checks mismatches only when present); this **pre-exists PR #408** and does not make an absent ID qualify for the new alias exception. It is not evidence of a regression and was not silently rewritten within this task.
- **L3 live/operational risk: MEDIUM, unverified.** No complete post-change KZ collection has run on this PR; the real current `239140` root's listing and uniqueness for `1697640` were not independently captured at runtime in this QA. The guard will block rather than silently skip if actual sole-root/reverse-edge conditions do not hold. Real Steam metadata can mutate; bounded 180/300s scheduling and 60-minute collector capacity can still fail. CI and offline 18/18 do NOT prove successful completion of the original 1223-request path, the absence of later failures or end-to-end publication.
- **Historical provenance:** the past failing run proved an inner-ID mismatch, not its historical exact numeric value. Current user-supplied API JSON must not be called a byte-exact 2026-11-05 artifact.
- **Not authorized/attempted:** source/test/workflow changes, production run or replay, scheduler/Dossier/Deep, source PR merge, or QA self-merge.

## Final disposition and ONE next step

**PASS** for independent PR-only source QA at exact `d3000e5cc66e1f2d1989232e97f0f55494068e04`, with the L3 live acceptance explicitly outstanding. **Next step:** Director reviews this report and independently decides whether to accept/merge source PR #408 under its existing authorization and merge gates; the already-defined *normal main* complete collector run remains the later separate live acceptance requirement.

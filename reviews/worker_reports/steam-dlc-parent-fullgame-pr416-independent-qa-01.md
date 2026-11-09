# Independent QA — Steam DLC fullgame parent, PR #416

**Task:** steam-dlc-parent-fullgame-pr416-independent-qa-01  
**Date:** 2026-11-08  
**Repository / base:** kentrap2011-hub/steam-kz-deals-2 / main  
**Mode:** independent source QA; source read-only, report-only draft PR  
**Source PR:** https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/416  
**Source exact HEAD verified (initial and before report):** 5b2d74aa4b750148bfd93ca847db93f60ba0ca59  
**Result:** **PASS** for the authorized bounded fix and exact source HEAD, **with documented unproven residual completeness risk**. This is not evidence of a successful full production cycle or a guarantee that every possible two-hop DLC lineage is discovered.

## Scope, authorization and contracts

Read current main CHAT_PROTOCOL.md, CHAT_CONTEXT.md, task, relevant Steam KZ discovery route, PROJECT_DECISIONS.md (including PR #416's proposed STEAM-DLC-PARENT-001), config/execution_ownership_contract.json, config/daily_execution_contract.json, config/mailing_policy.json#paid_discovery, affected collector/targeted implementation, full five-file PR patch and relevant regression tests. The source PR changes exactly CURRENT_TASK.md, PROJECT_DECISIONS.md, its worker report, scripts/steam_targeted_paid_lanes.py and scripts/test_steam_targeted_paid_lanes.py. No other repository was used.

Preflight: GitHub remains the deterministic discovery, completeness and production owner; paid_discovery explicitly requires complete verified relations, bounded eligible-base lookup, KZ paid filters, no global DLC crawl. The existing daily production cycle and failure-to-preserve-prior-publication rule remain authoritative. QA adds no new responsibility, schedule, queue, recurring stage or production execution.

## Confirmed positive evidence

1. In scripts/steam_partial_publish_runner.py:1316-1353, qualified eligible game roots are passed to targeted.discover_dlc_for_bases. An exception aborts before new paid publication (lines 1329-1339). The returned DLC entries are deduplicated by App_ key and enter existing review and selection stages.
2. Root appdetails are validated as type=game, and direct lists are canonicalized (scripts/steam_targeted_paid_lanes.py:396-432). The code expands first-hop fetched records once and loads the resulting nested records (lines 436-490). It constructs paid DLC paths in lines 492-568.
3. Incident: root 2820 lists both 201310 and 235960, while 201310.fullgame=2820, 201310.dlc does NOT list 235960, and 235960.fullgame=201310. The former code required the child's parent to be in the intermediate's reverse dlc list and raised an error rather than accepting valid child-side parent evidence. On PR #416, parent 201310 is already fetched from root 2820, and direct[201310] includes 2820; since 235960 is also directly listed by root 2820, line 527 accepts [2820,201310,235960]. This explains the removal of the incident's abort.
4. Verified GitHub Actions source-HEAD CI: steam-test.yml run 42400472154 regression=success, collect=skipped; validate run 42400472263 job validate=success; backlog-disposition run 42400472172 job backlog-disposition=success. Runs are linked from https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/416/checks and were associated with source commit 5b2d74a.
5. Independent *bounded live smoke*, not this source QA: diagnostic-only PR #417, run https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42453666183, job dlc235960_pr416_live_smoke=success. Its job log explicitly binds source_fix_commit to 5b2d74aa4b750148bfd93ca847db93f60ba0ca59, records 3 live KZ/English HTTP 200 GETs, production_discovery_on_live_values=NO_ABORT, real 235960 price_state=absent and no paid publication; the tested paid path is synthetic in-memory only.
6. Strong guards retained: exact appid identity where supplied and mandatory canonical IDs, verified game roots, strict first-hop root-alias exclusion, max two supported ancestry hops, observed third-hop/cycle checks, single App_ candidate deduplication, cc=kz/l=english, shared 180 starts/300s pacing, HTTP 429 max four attempts with finite waits, KZT price structure, >=50% discount and <=4500 KZT. No price from another AppID is substituted. The absent/null/empty child price remains omitted; an attributed malformed/non-KZT price raises. No source scheduling or workflow change.

## Residual risk 1 (synthetic, not reproduced live) — child discovered only in an unrelated root listing

**Location:** scripts/steam_targeted_paid_lanes.py:521-533, specifically lines 524 and 527; related incomplete success assertion lines 569-582.

**Minimal adversarial fixture (all AppIDs canonical; both roots admitted; price valid):**
- App_100: type=game, steam_appid=100, dlc=[200].
- App_900: type=game, steam_appid=900, dlc=[300].
- App_200: type=dlc, steam_appid=200, fullgame={appid:100}, no price, no child dlc listing.
- App_300: type=dlc, steam_appid=300, fullgame={appid:200}, price_overview={currency:'KZT', final:25000, discount_percent:85}.
- Call discover_dlc_for_bases(['100','900'], core, fetch=fixture_fetch).

**Expected by accepted parent-authority semantics:** App_300 is priced and belongs only to eligible root 100, with verified_base_appids=['100'] and verified_parent_chains=[['100','200','300']]. Root 900's reverse listing must not override the child's own fullgame lineage.

**Actual code-path walkthrough:** direct[200]={100}, direct[300]={900}, fetched contains both. For App_300, parent=200; middle_parent=100. The only candidate base is 100, but (100 in direct_bases={900}) and (100 in nested_bases={}) are both false at line 527. Thus paths stays empty; line 533 silently continues. No paid App_300, no exception, relation_complete=true. The code correctly avoids wrong root 900, but incorrectly loses the confirmed correct root 100. This is not a third-hop case: actual fullgame chain is 100->200->300 (two parent hops). The problem is that reverse-list origin is still treated as a veto, contrary to PR's main rationale.

## Residual risk 2 (synthetic, not reproduced live) — immediate parent absent from bounded fetched set

**Location:** scripts/steam_targeted_paid_lanes.py:521-533 and 569-582; tests scripts/test_steam_targeted_paid_lanes.py:490-495 intentionally assert the omission.

**Minimal fixture:**
- Admitted App_100: type=game, steam_appid=100, dlc=[300].
- App_300: type=dlc, steam_appid=300, fullgame={appid:200}, valid on-sale KZT price as above.
- App_200 is a real resolvable DLC with fullgame={appid:100}, but 200 is absent from root/intermediate reverse lists and therefore not in fetched.

**Actual:** middle_data=fetched.get('200') is None, so App_300 is silently skipped; relation_complete=true. The function never attempts to resolve the specific canonical immediate parent 200, even though that bounded lookup could prove ancestry to admitted root 100. It also emits no unresolved-parent warning/count or fail-closed incomplete result. A genuinely foreign parent's exclusion is safe for attribution, but this case is **not proven foreign**: the routine lacks evidence and falsely declares completeness. The test named missing_mid codifies silent exclusion, not a verified safe foreign-root negative case.

**Variant even without another network lookup:** App_100.dlc=[300,301]; App_301.fullgame=100 and App_301.dlc=[200]; App_200.fullgame=100 and has no dlc children; App_300.fullgame=200 with qualifying KZT price. App_200 is already fetched through nested discovery, but direct.get(200) is empty because root 100 did not list it directly. Lines 521-527 still skip App_300, although its genuine chain is 100->200->300. This proves that the defect is not only an absent-fetch issue.

## Limits of bounded discovery and telemetry

- Line 533 conflates known foreign roots with merely unresolved parentage, skips all those child records without raising or distinguishing the two cases. In some cases wrong-root ownership is correctly prevented; **absence of a false positive does not prove absence of a false negative**.
- relation_complete at line 581 is only len(successfully_fetched_root_responses)==len(admitted_roots); it does not cover unresolved, unvalidated, or silently discarded DLC lineage. Thus it can be true for the fixtures above despite incomplete candidate discovery.
- related_dlc_unique_ids=len(all_ids), dlc_rejected_after_paid_gate=len(all_ids)-len(candidates) and dlc_price_lookups=len(fetched)+len(excluded_aliases) mix unverified lineage with genuinely rejected/free/unpriced DLC. No actionable count of unknown ancestry. Nested/intermediate counters and paths are insufficient to detect this loss.
- Pricing validators at lines 535-568 execute only **after** nonempty paths; a discovered unknown-parent DLC with malformed price is silently dropped before the malformed price would raise. This avoids publishing unsafe prices, but does not establish complete/validated discovery.
- Direct root-only fallback for absent fullgame retains legacy listing-based attribution. If a nested listing exists and fullgame is absent, line 506 still raises; malformed fullgame type or invalid canonical parent identity still raises. No new priced misattribution was proved here, but no guarantee of general completeness is justified.
- Third-hop and cycle guards cover the observed list edges (lines 473-490); absent/foreign list edges can be skipped before this machinery. The supported two-parent-hop bound is not an excuse to silently drop a valid two-hop chain. Root type=game, first-hop alias 1697640→239140 safety, and same-AppID dedup were reviewed and do not remove the blocking issue.

## Regressions and risk

scripts/test_steam_targeted_paid_lanes.py:461-535 checks the specific 2820/201310/235960 absent-backlink case, a foreign parent exclusion, a no-longer-discovered intermediate (expected silent skip), and a second admitted root that also lists both the correct intermediate and child. It **does not** check the two failing cases above: source listing only from a different admitted root, or known/unknown intermediate absent from a root's direct list but with valid two-hop fullgame ancestry. The cross-root positive test has the *correct root also listing the child*, masking line 527's veto. Green regression is therefore insufficient.

Risk review: the hypothetical fixtures expose a real code-path limitation; they do not demonstrate that any real Steam DLC is lost. Neither a cross-base duplicate listing nor the missing-immediate-parent shape has been confirmed in live Steam data. The implemented discovery is deliberately bounded by existing root/intermediate `dlc` listings, so extending it into arbitrary parent GETs is a separate scope/architecture choice. `relation_complete=true` does not certify exhaustive traversal of all theoretical two-hop parent chains; it certifies completed admitted-root lookups. The strict contract's practical completeness boundary should remain explicit for future work, rather than be described as proven globally. Existing PR-only CI and #417's clipped smoke do not cover the remaining admitted roots, complete catalogue, real sale for 235960, or publication. Those limitations remain openly documented; they are **not presented as verified production correctness**.

**Why the verdict changed:** QA originally marked these synthetic-only cases as automatic `BLOCKED_SAFETY`. Following the user-requested reassessment (2026-11-09), they are treated as **documented residual risks rather than demonstrated blockers of the exact approved incident repair**. This is a scoped risk acceptance, not a finding that the counterexamples are impossible or that the algorithm is globally complete. All positive identity/price/region/pacing gates remain mandatory.

**Scope/permission:** QA is independently authorized as read-only assessment; no source IMPLEMENT authority is conferred by this QA task. No source code, test, production data, main, task board/registry, CURRENT_TASK, workflow, scheduling or source PR was changed.

## Single recommended next step

**Hand this scoped `PASS` and the two documented hypothetical gaps to the Director for PR #416 acceptance review** against its exact HEAD, approved bounded discovery scope and required CI. Any later goal to guarantee every possible two-hop `fullgame` ancestry (including parents absent from source lists) requires a separate canonical-contract/architecture decision and bounded verification; it is **not** silently added to this change. This QA does not authorize production, workflow dispatch or automatic merge.

**Final:** PASS — exact approved incident repair, with explicit unproven completeness limitations; no full-production acceptance claimed.
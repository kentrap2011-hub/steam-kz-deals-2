# Steam Search KZ maxprice sort-total drift guard 01 — worker report

- Task: `WORKER_TASK_STEAM_SEARCH_KZ_MAXPRICE_SORT_TOTAL_DRIFT_GUARD_01.md`.
- Scope: one source PR, developer self-check + existing `steam-test.yml` PR CI; no separate QA chat, no self-merge.
- Base: `main` at `85e306b728dc52dd058a4850f87083ea34b13711`.
- Branch: `fix/steam-search-kz-maxprice-sort-total-drift-guard-01`.
- Source files: `scripts/steam_partial_publish_runner.py`, `scripts/test_steam_discovery_scope_reduction.py`.
- Incident: main `Steam KZ production shortlist` run [41873904803](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41873904803), `aef253502e5828fe987c20f065e081cff4c9aeaa`, failed at source validation after two Search requests with capped `Price_DESC` total 9593 and capped `Name_ASC` total 9594. No full collector, targeted DLC, mailing or appdetails rolling-window acceptance occurred. Previous protected production snapshot remains.

## Mechanism proven vs unknown

**Proven code-level failure mechanism:** `validate_kz_source_price_bound` issued two `cc=kz`, `category1=998`, `hidef2p=1`, `maxprice=4500` first-page probes, differing only by `sort_by`. Any total inequality raised before the material uncapped control, irrespective of magnitude. This explains the exact fail-stop. **Unknown live cause:** Steam inventory/index fluctuation, sort-specific count semantics and upstream cache timing are hypotheses; neither a sort defect nor an ignored price filter was proven by 9593 versus 9594.

## Before / after and safety

- **Before:** 1 capped `Price_DESC` per supported partition, 1 capped `Name_ASC` games comparison, fail immediately for unequal totals, then 1 uncapped `Price_DESC` materiality control.
- **After, exact-match fast path:** unchanged three logical source probes for one `games` partition. The capped samples must all stay at or below 4500 KZT, totals must be valid and equal, and the identical no-`maxprice` games control must have a *larger* total and a price above 4500.
- **After, small initial drift:** initial difference up to 2 **only authorizes the diagnostic recheck; it is not an acceptance tolerance**. Two more complete pairs of capped `Price_DESC` / `Name_ASC` at start=0 must each report an *exact* equality **and the same total across both pairs**. All four extra capped samples must be safe. Then the uncapped control must be larger than **every** observed capped total and contain an over-cap row. Any missing price, malformed count, leaked price, insufficient stable evidence or query-binding change fails closed.
- **Bounded requests:** 3 logical probes on exact-match, max **7** for one games partition on small drift, max **6** before the final uncapped control on persistent contradiction, and 2 on a larger initial discrepancy. Up to two extra paired rounds, each separated by 1.8 s, with 180 s admission/deadline checks before and after each logical query; the existing `get_page` 8-attempt / HTTP 40-second timeout and finite backoff remain unchanged, so an individual in-flight HTTP retry sequence may exceed the outer 180-second elapsed gate (and then fails closed). No unbounded retry, full Search re-traversal, new scheduler or external data worker.
- **Boundaries unchanged:** original `cc=kz`, 998 games/Sub source, exact eligible traversal, parent-targeted DLC completeness, local <=4500 KZT price, >=50% sale, separate freebies, source freshness and publication isolation. Source validation is an admission gate, **not** the sole proof of complete eligible traversal. The existing subsequent traversal and DLC guards remain authoritative.
- **Counterexamples:** initial 9593/9594 followed by two exact 9594/9594 pairs is admissible only with a material uncapped control; repeated 9593/9594 mismatch, two individually equal pairs with different totals, an uncapped control that has the same total or lacks over-cap items, capped sample 4600 KZT, invalid/nonpositive row evidence, unknown/float/negative totals, and changed country/category/parameter binding all fail. No relative or +/-1 equivalence is permitted.

## Developer self-check / CI gate

- Deterministic offline tests added to `scripts/test_steam_discovery_scope_reduction.py` for transient PASS, persistent/unstable FAIL, big-drift FAIL, ignored cap FAIL, leaked price/invalid totals FAIL, cc/partition mismatches FAIL, timeout/no false success; previous exact-match test remains active.
- Source delta restricted to price-bound validation and its deterministic regression, no modifications to PR #397 appdetails rolling limiter, queue/index or daily production workflow.
- **Authoritative CI:** PR-only `.github/workflows/steam-test.yml`, `regression` (which invokes policy, ownership and backlog disposition validation). The workflow does not collect live Steam for PRs. Final exact-HEAD CI status and result are recorded on the source PR checks/conversation; do not treat this static report as evidence of a successful live main run.
- **L3 pending Director:** no worker merge, no live main production acceptance before Director's merge. After merge, the existing main push-triggered collect (if active) is the one live acceptance run; do not duplicate via manual dispatch. Confirm source validation -> full collector (including appdetails 180/300) -> mailing -> pre-AI -> exact Dossier binding; preserve failure isolation.

# WORKER TASK — Steam discovery maximal scope reduction diagnostic 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Do not search, read, modify, or use another repository for this task. If GitHub/tool opens another repository by default or the repository target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2`.

Task ID: `STEAM_DISCOVERY_MAXIMAL_SCOPE_REDUCTION_DIAGNOSTIC_01`
Worker slot: `ЧАТ 1`
Mode: `READ-ONLY / RECON`

## Goal

Perform a global but bounded diagnostic of the existing Steam KZ discovery path to determine how to reduce the amount of Steam catalog data fetched as much as safely possible while preserving the project's ability to surface the best deals.

Product target from the user:
- ideally the final site should contain about **100 best offers**;
- this does **not** automatically mean raw Steam discovery must contain exactly 100 rows;
- explicitly distinguish:
  1. raw Steam rows/pages fetched,
  2. canonical eligible candidate universe,
  3. shortlist/mailing scope,
  4. final visible site cards.

The previous Catalyst diagnostic already proved the current failure. Do **not** redo that investigation:
- report: `reviews/worker_reports/mirrors-edge-catalyst-post-refresh-absence-diagnostic-01.md`;
- current live search returned about 100,307 rows;
- the current `category1=998,21,996` attempt did not bound the live response;
- the collector timed out at 60 minutes before persistence.

This task asks a different question: **what are the strongest safe ways to shrink discovery now?**

## START / required reads

1. Read current `CHAT_PROTOCOL.md` and perform START gate.
2. Read current `CHAT_CONTEXT.md`.
3. Read this task fully before broad navigation.
4. Read only the Steam/discovery route in `PROJECT_ROUTES.md`.
5. Read the accepted Catalyst diagnostic report above.
6. Read the current ownership/execution contract required by the route.
7. Read only the relevant current business-selection rules/contracts needed to know which offers the product is supposed to preserve.
8. Inspect only the exact current Steam discovery workflow/script/API query path needed for this diagnostic.

Do not reconstruct project history, enumerate unrelated PRs/branches/workflows, or inspect semantic Dossier/Deep/Fast internals.

## Architecture boundary

GitHub remains the sole production control-plane and Steam discovery owner.

This task is diagnostic only:
- no implementation;
- no production-state mutation;
- no scheduler changes;
- no Scheduled Task changes;
- no new collector, queue, recurring stage, retry loop, or ChatGPT-owned discovery;
- no Catalyst special case.

Bounded live Steam/API probes are allowed only when necessary to verify actual query/filter semantics. Do not perform another full 100k-row crawl merely to reproduce the known timeout.

## Questions the diagnostic must answer

### A. Where can the universe be reduced before expensive pagination?

Test/establish which real Steam query/API constraints are actually honored live, independently and in combination.

Do not trust only locally constructed query strings. Verify real source behavior with bounded probes.

Consider all relevant source-side reduction opportunities supported by the actual Steam interfaces, including but not limited to:
- specials/active-sale constraints;
- app/content type;
- region/currency;
- paid/free distinctions;
- DLC/bundle/package distinctions;
- search/category/tag constraints where they are semantically safe;
- ordering/sorting parameters if Steam can return high-value deals first;
- price/discount-related constraints if available;
- alternative Steam endpoints already available to the existing owner;
- partitioning one broken broad query into several genuinely bounded queries;
- incremental/change-based discovery if it can remain GitHub-owned and correctness-preserving.

Do not assume any of these are valid; prove or reject them.

### B. What can be filtered cheaply after a small source response but before full downstream work?

Identify deterministic filters already implied by current product policy that can safely reduce candidates early.

For each possible early filter, state whether it:
- preserves current product semantics;
- changes product semantics;
- risks losing a genuinely strong offer;
- requires a user decision.

### C. How does the target of about 100 final offers change the design?

Determine whether the current system is discovering far more items than necessary for the final product goal.

Analyze whether it is safe to produce roughly the best 100 final cards by:
- source-side narrowing;
- deterministic pre-ranking/preselection;
- top-N after a sufficiently broad candidate pool;
- staged discovery;
- or another architecture.

Do not silently turn “about 100 visible best offers” into an arbitrary hard raw-fetch quota.

### D. Produce multiple viable options

Return at least **3 materially different viable approaches** if the source permits them.

For every option provide:
- how it works;
- which current owner/component changes;
- estimated/observed raw Steam scope;
- likely runtime/API pressure;
- probability/risk of missing a strong deal;
- whether current product rules change;
- what user choice, if any, is required;
- implementation complexity;
- recommended validation/acceptance test.

Rank the options:
1. safest / least product loss;
2. best balance;
3. most aggressive reduction.

If a combination is clearly superior, describe the combined design separately.

### E. User questions

If meaningful further reduction requires choosing what may be sacrificed — for example DLC, bundles, tiny discounts, certain price bands, low-confidence offers, particular content types, or other categories — **ask the user directly in this worker chat instead of choosing for them**.

Ask only questions that materially change the recommended architecture. Do not ask questions whose answer is already in current canonical rules.

## Required result

Save a compact but decision-useful report at:

`reviews/worker_reports/steam-discovery-maximal-scope-reduction-diagnostic-01.md`

The report must contain:
- confirmed current bottleneck, without redoing settled Catalyst tracing;
- verified Steam-side filtering/query findings;
- the current funnel sizes where measurable;
- at least 3 options with tradeoffs;
- the recommended option or combination;
- exact unresolved user choices/questions;
- smallest implementation task(s) that would follow **only after Director/user approval**.

Do not implement the recommendation.

## CURRENT_TASK.md

You may update only your own clearly delimited task entry. Re-read the file immediately before any write and do not overwrite another active worker's entry. If a safe merge is not possible because of concurrent movement, skip the write and state that in the report.

## Done when

The task is complete when the Director can choose an implementation strategy without another broad Steam investigation, and any genuine product tradeoff has been surfaced to the user rather than silently assumed.

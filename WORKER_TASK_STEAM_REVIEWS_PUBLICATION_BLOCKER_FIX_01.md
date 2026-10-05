# WORKER TASK — Steam Reviews / publication blocker fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `STEAM_REVIEWS_PUBLICATION_BLOCKER_FIX_01`
Worker slot: `ЧАТ 1`
Mode: `DIAGNOSE / IMPLEMENT / VALIDATE / LIVE ACCEPTANCE`

## Purpose

Fix the newly exposed production blocker after successful completion of the Steam discovery scope-reduction work.

The discovery problem itself is now accepted as fixed. Do **not** reopen the games/DLC source-scope correction, standalone `category1=996`, page-size 100, Search pacing 1.8s, or the completed PR #151 acceptance unless direct new evidence proves a regression.

This task starts **after** successful discovery.

## Accepted upstream production evidence

Normal main production run:

- workflow: `Steam KZ production shortlist`
- run: `37357943696`
- head: `8ecf017b7428bad3494f7d8f1a82bd581bd3d355`
- conclusion: **success**
- runtime: about 39 minutes
- canonical persistence step: success
- downstream visual-refresh dispatch step: success

Fresh canonical manifest proves:

- source status: `complete`
- coverage ratio: `1.0`
- games: 63,654 / complete
- DLC: 34,344 / complete
- total source rows: 97,998
- standalone 996 traversal: removed
- Search HTTP 429 events: 1
- Search backoff: 3 seconds

Treat that as settled acceptance of the previous task.

## Newly exposed blocker

The same fresh manifest shows review enrichment is unhealthy:

- review candidate items: **60,624**
- review candidate AppIDs: **60,477**
- items with review data: **33,959** (includes search-surface review data)
- `global_review_appids_ok = 147`
- `russian_review_appids_ok = 147`
- logical `review_api_requests = 120,954`
- `review_api_failed_requests = 120,654`
- `review_api_failure_rate = 0.99752`
- `review_rate_limit_circuit_open = true`
- actual network `review_http_requests = 310`
- network review 429 events: 10
- network review backoff: 3 seconds

This means the logical failure count is dominated by work that becomes unavailable/skipped after the review circuit opens, not by 120k physical HTTP calls.

Immediately after the fresh discovery production handoff, downstream publication did not become healthy:

- `Build daily visual payload` run `37362828015`: failure
- `Build mailing-optimized feed` run `37362840701`: failure
- later visual builds were repeatedly cancelled / superseded while Dossier activity also continued.

Do not assume all downstream failures have the same cause. Prove the exact causal chain.

## Required diagnosis

Inspect only the exact current review enrichment and downstream paths needed to answer:

1. Why does the review circuit open after roughly 310 physical requests?
2. What exact HTTP/status/error classes trigger it?
3. Are the 10 observed 429s the real trigger, or is another response/error counted into the circuit?
4. Is request pacing / retry behavior appropriate for the Steam Reviews endpoint specifically?
5. Is review enrichment unnecessarily attempted for all ~60k candidates before enough deterministic narrowing is available?
6. Which review fields are already available from the Steam Search surface and can safely satisfy existing deterministic gates without an AppReviews call?
7. Which downstream artifact(s) actually require AppReviews-derived data versus search-surface review data?
8. Why did the immediate mailing/visual builds fail after the fresh discovery commit?
9. Are those failures caused by review incompleteness, stale-state guards, Dossier/Deep freshness, or another exact downstream contract?

Do not make a broad architecture rewrite.

## Product / correctness constraints

Preserve:

- minimum paid discount = 50%
- max price = 4500 KZT
- complete approved games + DLC discovery universe
- package/bundle identities embedded in games
- no raw top-N truncation of discovery
- one problematic game must not block unrelated games
- GitHub owns production control plane, retries, persistence and canonical completion
- semantic Dossier/Deep workers remain independent
- Russian description absence remains nonblocking
- browser remains presentation-only

Do not change Dossier, Deep, ranking, translation, Scheduled Tasks, or the newly accepted discovery scope unless an exact dependency requires a bounded compatibility change.

## Preferred correction shape

Choose the smallest correction supported by evidence.

Potentially valid directions include, but are not limited to:

- endpoint-specific pacing/backoff that prevents the circuit from opening;
- correct handling of 429 / Retry-After if the endpoint exposes it;
- distinguishing permanent/temporary review failures;
- using existing search-surface review data where contractually sufficient;
- narrowing AppReviews enrichment to the items that actually require it **after** safe deterministic gates;
- cache-first behavior using the existing review cache;
- resumable review enrichment through the existing GitHub-owned producer if a single-run exhaustive enrichment is not necessary for publication;
- allowing partial review enrichment to publish when current product rules explicitly permit it.

Do **not** silently weaken review thresholds, invent ratings, or mark missing AppReviews data as successful.

Do not solve the issue by increasing workflow timeout as the primary fix.

## Publication acceptance

The task is not complete merely when review enrichment stops erroring.

After implementation:

1. deterministic tests for the exact review/circuit failure pass;
2. existing Steam discovery regressions stay green;
3. one normal main production run or the smallest canonical rerun proves the review path behaves as intended;
4. a fresh canonical mailing/pre-AI/visual downstream path must either:
   - complete successfully, or
   - expose a separate proven blocker with exact stage/error evidence;
5. if a separate downstream blocker is proven independent of Reviews, do not hide it inside this task—report it clearly for Director decision.

## Observability

Persist/report enough metrics to distinguish:

- physical review HTTP calls;
- logical review components requested;
- cache hits;
- search-surface review reuse;
- successful AppReviews components;
- temporary failures;
- permanent failures;
- 429 count;
- retry/backoff time;
- circuit-open reason and threshold;
- items skipped because the circuit is open;
- items still publishable despite missing AppReviews enrichment.

Do not report circuit-skipped logical requests as if they were physical HTTP failures without separate counters.

## Validation / ownership

Required before closeout:

- relevant Steam production tests;
- production-output ownership guard;
- fresh deal discovery lifecycle regression;
- backlog dispositions if affected;
- downstream publication tests touched by the fix.

No Scheduled Task creation/modification/run.

## Report

Create:

`reviews/worker_reports/steam-reviews-publication-blocker-fix-01.md`

Report:

- exact root cause of review circuit opening;
- exact relationship, if any, to downstream mailing/visual failures;
- files changed;
- before/after metrics;
- PR/checks;
- live acceptance;
- final publication state;
- any separate remaining blocker.

Allowed final statuses:

- `complete_publication_restored`
- `complete_reviews_fixed_separate_publication_blocker_found`
- `diagnosed_needs_director_decision`
- `blocked_external_rate_limit`

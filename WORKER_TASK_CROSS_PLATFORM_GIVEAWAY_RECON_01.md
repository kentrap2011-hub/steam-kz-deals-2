# WORKER TASK — NEXT FREE SLOT

Task ID: `cross-platform-giveaway-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/cross-platform-giveaway-recon-01.md`

## Goal

Determine the correct canonical source/production architecture for a separate **time-limited free-game giveaway** section across any reliably supportable storefronts, not only Steam.

The user requirement is storefront-neutral: if a game can be claimed permanently for free and is relevant, it should be surfaced separately from the monthly paid-purchase feed so the user does not miss a time-limited giveaway.

This is recon only. Do not implement collectors, workflows, UI, schedules or production data changes.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `PROJECT_RULES.md` — especially the main-goal rule that free giveaways are a separate scenario
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `CURRENT_TASK.md`
- `BACKLOG.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- current production source/collector contracts and workflows relevant to storefront/deal discovery

## Architecture preflight

Preserve ownership:
- GitHub/GitHub Actions must own storefront polling/discovery where technically and legally possible, exact scope, normalization, dedupe, expiry, persistence, completeness and UI payload construction.
- Scheduled ChatGPT may only be used for narrowly required external/semantic facts GitHub cannot obtain directly and only from GitHub-prepared exact work.
- Interactive worker must not manually compile the current giveaway list or become a production monitor.
- Do not create a new schedule in this task.

## Definition to audit

Target event = a time-limited offer where the user can **claim the game and retain access permanently** after the promotion ends.

Explicitly distinguish from:
- permanent free-to-play;
- demos/prologues;
- free weekends / temporary trials;
- subscription-catalog access that ends with subscription or removal;
- DLC-only giveaways unless the project later explicitly chooses to include them;
- coupons/discounts where final price is not actually zero.

If a storefront has a materially different ownership model, document it rather than forcing it into the same category.

## What to investigate

### 1. Current project route
- Does the current source/production pipeline already observe zero-price / giveaway-like offers?
- At what stage would a true claim-to-keep giveaway be filtered out or become indistinguishable from ordinary paid deals?
- Which current identity model is Steam-specific and which parts are reusable cross-store?

### 2. Storefront/source coverage
Evaluate practical, current, authorized access for at least the major relevant PC storefronts/sources that can plausibly expose time-limited claim-to-keep games, including:
- Steam;
- Epic Games Store;
- GOG;
- other serious candidate storefronts/aggregators discovered from official/current documentation.

Do not assume every platform needs a dedicated integration. A trustworthy aggregator may be preferable if its terms, provenance, latency and identity are acceptable; conversely do not choose an aggregator merely because it is convenient.

For each candidate source, record:
- exact signal proving `claim-to-keep` and zero price;
- promotion start/end timestamps if available;
- game/store identity and canonical URL;
- region/localization constraints relevant to the user-facing project;
- GitHub Actions accessibility/auth requirements/rate limits;
- current terms/licensing/attribution/caching/redistribution constraints for the project's current personal/non-commercial status;
- whether source can distinguish free weekend/F2P/subscription from permanent claim.

Use official documentation/terms where available. Tiny source-level sanity checks are allowed; no catalog crawl.

### 3. Cross-store canonical model
Recommend a minimal storefront-neutral record contract covering at least:
- storefront/provider;
- store offer/product identity;
- canonical game identity when safely known;
- title;
- claim URL;
- promotion start/end;
- `claim_to_keep` evidence/status;
- price/currency evidence where relevant;
- region eligibility/unknown;
- source/provenance/fetched_at;
- dedupe relationship when the same game is free on multiple stores.

Fail closed on ambiguous identity; no title-only merge.

### 4. User relevance semantics
The separate giveaway section should not be blocked by the ordinary monthly paid-deal cutoff.

Determine the cleanest existing Taste/relevance route to decide whether a giveaway is at least potentially relevant without making zero price artificially improve taste fit. Do not redesign ranking in this recon.

### 5. Freshness / urgency
Because giveaways expire, recommend a source refresh cadence based on actual provider behavior and project contracts. Do not invent a new ChatGPT schedule. If the existing nightly GitHub production cadence may miss short-lived offers, identify that as a product/architecture decision requiring a later contract change rather than silently changing scheduling here.

### 6. UI handoff requirements
Define only the producer fields/status needed for a future separate read-only UI section. Do not implement UI.

## Hard boundaries

Do NOT:
- implement source collectors or UI;
- manually list current free games as canonical data;
- add a recurring workflow/scheduled ChatGPT task;
- change Taste/ranking/paid-deal eligibility;
- treat a free weekend, subscription access or F2P as claim-to-keep;
- restrict the design to Steam;
- perform broad production catalog processing.

## Done when

- current pipeline loss point is identified;
- viable source strategy is compared across stores and any aggregator candidates;
- legal/access/provisioning concerns for current non-commercial use are recorded;
- recommended storefront-neutral record contract and identity/dedupe rules are clear;
- exact next bounded IMPLEMENT or contract task is recommended.

## Report format

Save:
`reviews/worker_reports/cross-platform-giveaway-recon-01.md`

### Task
Scope audited.

### Verified current project facts
Where giveaways would currently enter/be lost.

### Source comparison
Compact table by source/storefront.

### Recommended architecture
Provider strategy + canonical cross-store model + freshness/completeness ownership.

### Risks / terms / provisioning
Only current verified constraints.

### Unresolved
Real unknowns only.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only.

Final response must include report path and commit ref.
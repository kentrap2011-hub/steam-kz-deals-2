# WORKER TASK — CHAT 1

Task ID: `cross-platform-giveaway-ui-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/cross-platform-giveaway-ui-recon-01.md`

## Goal

Prepare the smallest correct implementation route for the remaining user-facing part of the cross-platform giveaway feature now that `CROSS-PLATFORM-GIVEAWAY-V1` production data is live and complete.

Current production fact from `steam-recommendation-count-fix-01`:
- canonical giveaway snapshot exists and is complete;
- Steam/Epic/GOG Tier-1 source health is all `ok` / complete;
- current accepted offers at that run: 2 Epic full-game claim-to-keep promotions;
- do not repeat source recon or data-plane implementation.

Remaining user requirement:
1. giveaways must appear as a **separate clearly visible block**, not disappear inside the paid-deal feed;
2. expired giveaways must disappear automatically from the visible block;
3. the block should avoid unconditional display of obviously irrelevant junk, but must not invent unsafe cross-store Taste identity or title-only mapping;
4. giveaways do not compete with the monthly paid-purchase choice and must not be hidden by the normal paid-deal ranking cutoff.

## Read first

- `reviews/worker_reports/steam-recommendation-count-fix-01.md`
- `config/cross_platform_giveaway_contract.json`
- current `data/production/giveaways/index.json`
- current `data/production/giveaways/v1/current.json`
- `config/execution_ownership_contract.json`
- current canonical read-only UI / visual payload route only as needed to answer this task
- relevant `PROJECT_ROUTES.md` entry if one exists
- relevant `KNOWN_WORKER_PITFALLS.md` entry only if the trigger matches

Do not perform broad history archaeology.

## Questions to answer

### 1. Exact current UI ownership

Identify the canonical path that currently builds and serves the read-only user UI / visual payload.

Determine the smallest place where a separate giveaway block should be added without creating a second UI writer or bypassing the canonical payload.

### 2. Artifact handoff

Determine how `data/production/giveaways/v1/current.json` should enter the existing visual/read-only payload:
- direct canonical read during visual build;
- versioned derived field in the visual payload;
- or another already-authorized route.

Do not invent a new scheduler or chat-owned cache.

### 3. Freshness / expiry

Confirm the exact fail-closed rule for visibility:
- only current complete snapshot;
- only offers whose claim window is active at build/render time;
- stale/incomplete giveaway snapshot must not be presented as current complete data.

State whether stale/incomplete data should hide the block or show a clear unavailable/incomplete state under the current UI contract.

### 4. Relevance semantics

Inspect what reliable identity/profile signals already exist for giveaway games.

Classify the smallest safe relevance policy into one of these routes:
- exact canonical game identity already maps to existing Taste/profile evidence;
- exact storefront/product identity can be safely mapped through an existing canonical cross-store identity table;
- no reliable cross-store personal relevance mapping exists yet.

If no reliable mapping exists:
- do **not** recommend title-only matching;
- do **not** invent a new semantic queue in this task;
- recommend the smallest honest fallback for the visible block (for example showing all verified Tier-1 claim-to-keep offers with clear separation from personalized paid recommendations, or another existing product rule) and explicitly explain the tradeoff against the user's wish to avoid irrelevant junk.

### 5. Current sample

Using the current canonical snapshot only, show how the current accepted giveaway rows would flow through the proposed UI policy. This is a bounded sample, not manual production curation.

### 6. Implementation boundary

Produce an exact bounded IMPLEMENT plan:
- files/components to change;
- payload fields if any;
- deterministic behavioral tests;
- generated-output checks;
- whether user/device acceptance is required after deploy.

## Hard boundaries

Do NOT:
- change product/runtime code in this task;
- repeat Steam/Epic/GOG source recon;
- redesign giveaway classification;
- add title-only cross-store dedup/Taste mapping;
- add a second writer/scheduler;
- manually curate current offers;
- alter paid ranking/Taste eligibility;
- claim personalized relevance where the repository cannot prove it.

## Status

Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Use `needs_user_decision` only if there are genuinely multiple product semantics that cannot be derived from existing rules/evidence.

## Report format

Save:
`reviews/worker_reports/cross-platform-giveaway-ui-recon-01.md`

### Task
What was inspected.

### Canonical UI route
Exact ownership/builder/serving path.

### Giveaway artifact handoff
Smallest authorized integration point.

### Freshness / expiry
Exact visibility semantics.

### Relevance policy
What can and cannot be proven with current identity/Taste data.

### Current sample
How current canonical accepted rows would render under the policy.

### Recommended IMPLEMENT
One bounded implementation task with exact files/tests/acceptance.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
One allowed status.

### Recommended next step
One bounded next step only.

Final response must include report path and exact refs.
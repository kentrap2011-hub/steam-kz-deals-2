# WORKER TASK — CHAT 1

Task ID: `giveaway-analysis-identity-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/giveaway-analysis-identity-recon-01.md`

## Context

The user has accepted the current giveaway navigation UX on real device:
- compact `🎁 Раздачи (N)` control is good;
- separate Wishlist-style giveaway view is good;
- compact list/detail navigation is good.

The only remaining user-facing defect is that giveaway detail cards do not yet contain real:
- description;
- pros;
- cons/minuses.

Previous giveaway UI work already proved that there is no currently established safe Epic/GOG -> Steam analysis binding, and correctly refused title-only/fuzzy reuse.

Do NOT repeat UI work or generic giveaway source recon.

## Goal

Find the smallest safe canonical identity/analysis route that lets a giveaway game reuse or obtain the same game-analysis facts (description, grounded positives, grounded negatives) without title-only matching and without a second semantic production system.

This task is RECON only.

## Required questions

### 1. Existing canonical identity assets

Inspect only the current identity-related artifacts/routes needed to answer this task.

Determine whether the repository already has any reliable cross-store identity bridge using one or more of:
- exact external game IDs;
- store product IDs bound to a canonical game identity;
- developer/publisher + release identity with another exact external identifier;
- already-ingested IGDB/other canonical game IDs;
- existing package/app family identity that can safely bridge storefronts.

Do not treat title normalization alone as proof.

### 2. Current active giveaway sample

For the current active giveaway games, determine whether an exact safe identity to an already-analyzed canonical game can be established using existing repository data.

Do not manually curate a mapping just for the current two titles.
Use the current titles only as a bounded proof sample for a generic rule.

For each sampled giveaway classify exactly one:
- `exact_existing_binding`
- `exact_binding_derivable_from_existing_canonical_data`
- `no_safe_binding_with_current_data`

Record the exact evidence/ref that supports the classification.

### 3. Reuse vs new analysis

If exact binding exists or can be deterministically derived:
- identify the exact canonical game-analysis source already used by normal cards;
- determine how description / positive evidence / grounded negative evidence can be reused without copying paid ranking/price state;
- preserve current provenance/readiness semantics.

If no safe binding exists:
- determine the smallest canonical identity enrichment needed;
- prefer an existing provider/route already authorized by the project;
- do not invent a new scheduled semantic worker if identity can be resolved deterministically or through an already-existing external provider/runtime.

### 4. IGDB constraint

A separate project track is currently blocked on user-provisioned IGDB secrets.

If IGDB would be the cleanest cross-store identity authority:
- state that clearly;
- reuse the existing blocked IGDB integration direction rather than creating a parallel provider contract;
- determine whether the already-required IGDB secrets would be sufficient for this identity task too;
- do not ask for any secret value in chat and do not commit secrets.

If a different already-available exact-ID source can solve identity without IGDB, explain why it is safer/smaller.

### 5. Analysis semantics

The eventual giveaway detail must expose only canonical analysis facts:
- concise Russian description;
- grounded positive explanation / pros;
- grounded negative / cons;
- explicit incomplete state when those analysis facts are not ready.

Do not copy:
- paid price/deal/rank state;
- wishlist-specific score effects;
- title-only Steam analysis;
- heuristic-only negatives as facts.

Grounded-negative readiness must respect the new V4 Taste contract where applicable.

### 6. Production ownership

Define the smallest authorized handoff through the existing GitHub-owned architecture.

Need exact answer for:
- where cross-store canonical identity is persisted;
- which existing producer owns it;
- how giveaway visual handoff consumes analysis by canonical identity;
- how stale/missing/unresolved identity is represented;
- how no second browser fetch / scheduler / chat-owned queue is introduced.

### 7. Recommended next step

Recommend exactly one bounded next task:
- `IMPLEMENT` if safe canonical identity authority already exists and wiring is clear;
- `IMPLEMENT after user secrets` if the correct route is the already-blocked IGDB provider and only missing prerequisite is the existing user-provisioned secrets;
- `CONTRACT/RECON` only if there is genuinely no canonical identity authority and multiple provider semantics remain unresolved.

Do not recommend manual mapping.

## Hard boundaries

Do NOT:
- change UI in this task;
- title/fuzzy-match games across stores;
- manually whitelist Breathedge/Rival Stars;
- create a second semantic Taste system;
- redesign giveaway source/classification;
- redesign paid ranking;
- invent pros/cons;
- expose secrets.

## Report format

Save:
`reviews/worker_reports/giveaway-analysis-identity-recon-01.md`

### Accepted UI state
Compact statement that navigation UX is already accepted and not under review.

### Existing identity authority
Exact current reusable identity assets/routes.

### Current sample
Classification/evidence for current active giveaways.

### Analysis reuse route
How description/pros/cons can safely attach by canonical identity.

### Missing prerequisite / identity gap
Exact blocker if any.

### Production ownership
Exact persisted identity + producer + visual handoff.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded step only.

Final response must include report path and exact refs.
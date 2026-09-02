# WORKER TASK — EXISTING CHAT 2

Task ID: `giveaway-identity-provider-alternatives-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/giveaway-identity-provider-alternatives-01.md`

## Context

Direct continuation of:
- `reviews/worker_reports/giveaway-analysis-identity-recon-01.md`
- `reviews/worker_reports/giveaway-igdb-implement-prep-01.md`
- `reviews/worker_reports/chat2-twitch-blocker-status-01.md`

Twitch/IGDB is currently blocked because the user cannot complete the Twitch 2FA prerequisite with the current Russian +7 phone flow. Twitch Support has been contacted. Treat IGDB as a fallback, not the primary route for now.

Do NOT repeat the Twitch troubleshooting.

## Goal

Find the smallest safe non-Twitch primary identity route for exact cross-store binding:

`Epic/GOG exact provider identity -> authoritative game identity -> exact Steam appid/family`

so giveaway detail cards can reuse the existing canonical description / pros / grounded cons.

## Required investigation

Evaluate only realistic provider/data routes that could produce durable exact identity. Prefer existing public/official/stable sources and routes that can be owned by GitHub Actions without a second semantic system.

For each serious candidate, determine:
- whether it can resolve from exact Epic and/or GOG product identity, not title alone;
- whether it can return or prove an exact Steam appid or another authoritative bridge to it;
- credential/account requirements;
- whether those requirements are realistically available to this project;
- API/data stability and automation suitability;
- relevant terms/licensing constraints for the current personal/non-commercial project;
- whether a second scheduler/queue/runtime would be required;
- failure behavior for missing/ambiguous mappings.

Candidates may be discovered by the worker; do not restrict the search to a preselected list. Do not recommend a provider merely because it has game metadata if it cannot establish exact cross-store identity.

## Proof standard

Use the current active giveaway sample only as a bounded proof sample when useful.

A route is acceptable only if the binding can be authorized by exact provider IDs / authoritative external IDs. Title, normalized title, publisher equality, fuzzy matching, web-search coincidence, or manual per-game mapping must never be sufficient proof.

Classify each serious route:
- `viable_primary`
- `viable_secondary`
- `blocked_by_credentials_or_terms`
- `insufficient_identity_precision`
- `not_automation_suitable`

## Existing architecture boundaries

- Do not redesign giveaway UI.
- Do not create a second Taste system.
- Do not create a browser-side provider fetch.
- Prefer the existing GitHub-owned production workflow and `scripts/giveaway_production.py` as the canonical writer.
- Keep unresolved identity fail-closed: description/pros/cons remain unavailable rather than guessed.
- IGDB remains a fallback option if Twitch Support later unblocks it.

## Required decision

Recommend exactly one next direction:
- `IMPLEMENT <named provider/route>`
- `CONTRACT/RECON <specific unresolved question>`
- `WAIT_FOR_IGDB` only if you prove there is no credible safer primary alternative
- `NEEDS_USER_DECISION` only if two genuinely viable routes have a meaningful product/tradeoff choice

Do not implement the new provider in this task.

## Report

Save `reviews/worker_reports/giveaway-identity-provider-alternatives-01.md`.

### Twitch/IGDB disposition
One sentence: fallback while support is pending.

### Candidate routes
Compact comparison with exact identity capability and blockers.

### Bounded proof
What could/could not be proven on the current giveaway sample.

### Recommended primary route
One route only, with why it beats the alternatives.

### Implementation ownership
Smallest canonical insertion point and what existing pipeline it reuses.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_user_decision`
- `needs_fix`

Efficiency / reusable lesson: `none | <short candidate/ref>`

Final response must include report path and exact refs.
# WORKER TASK — CHAT 1

Task ID: `cross-platform-giveaway-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/cross-platform-giveaway-implement-01.md`

## Goal

Implement the first production-ready **cross-platform claim-to-keep giveaway data plane** for the Tier-1 baseline established by `cross-platform-giveaway-recon-01`:

- Steam — keep current KZ discovery, but harden acceptance semantics;
- Epic Games Store — add first-party KZ giveaway discovery/validation;
- GOG — add first-party KZ giveaway discovery/validation.

This task is the direct continuation of the completed recon. Do not repeat source reconnaissance unless a concrete current integration fact has changed or an implementation blocker requires a bounded verification.

The user-facing UI/relevance presentation is NOT the primary scope of this task. First establish correct canonical data, ownership, completeness and current production output. Do not invent a new relevance policy merely to make the data visible.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md` only if relevant to worker operating constraints
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `PROJECT_RULES.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `config/freebies_upcoming_contract.json`
- `reviews/worker_reports/cross-platform-giveaway-recon-01.md`
- current Steam production/freebie producer and the exact workflows/routes that own its canonical outputs

## Architecture preflight — mandatory

Before changing workflow/collector/ownership:
1. identify current owner of Steam `freebies*` outputs;
2. preserve single-writer ownership;
3. do not make scheduled ChatGPT the control plane;
4. do not create parallel collectors writing the same canonical path;
5. explicitly version any ownership migration.

Preferred architecture from recon:
- source adapters -> one normalization/classification/dedup producer -> a separate versioned `data/production/giveaways/` artifact family;
- keep current Steam-owned `freebies*` outputs untouched unless there is an explicit tested ownership migration.

If current contracts prove a different single-writer arrangement is cleaner, document why and preserve the same invariants.

## Required implementation

### 1. Versioned canonical contract

Create a source-agnostic giveaway contract covering at minimum:
- schema/contract version;
- storefront/provider;
- stable store product/offer identity;
- canonical game identity only when safely known;
- title;
- first-party claim URL;
- promotion start/end timestamps;
- observed/fetched timestamp;
- `claim_to_keep` / permanent-after-claim evidence;
- final and original/base price evidence where applicable;
- KZ region state/evidence;
- content type;
- subscription requirement;
- access-expiry semantics;
- source provenance;
- classification status/reason codes;
- source completeness/health;
- non-destructive grouping of the same game across multiple stores.

Never title-only merge two store offers.

### 2. Steam hardening

Reuse the existing KZ Steam catalog scan only for candidate discovery.

The current shortcut:
`price_kzt == 0 && discount_percent > 0`
may produce a candidate but must no longer be sufficient proof for publication as a real giveaway.

For accepted Steam giveaways require enough first-party evidence to establish:
- active limited-time promotion;
- zero final price;
- paid/original product or explicit giveaway evidence;
- permanent claim semantics;
- eligible full-game/approved complete edition content type;
- KZ availability;
- known active promotion window.

Fail closed when permanent ownership or promotion-window semantics cannot be established.

Do not add a second full Steam crawl.

### 3. Epic Games Store adapter

Implement bounded first-party KZ discovery using the current storefront promotions route established by recon, with strict schema guards.

Requirements:
- explicit KZ country parameters;
- active promotion window only;
- full game / approved complete edition only;
- zero-price active offer;
- stable Epic namespace/offer identity;
- direct first-party claim/store route;
- reject mystery placeholders, DLC/extras, upcoming-only, permanent free products and unknown KZ applicability;
- fail closed if the undocumented schema changes materially.

Do not treat the endpoint as a guaranteed public API; source health must make schema failure visible.

### 4. GOG adapter

Implement bounded first-party KZ candidate discovery using the current GOG catalog route established by recon.

Requirements:
- explicit `countryCode=KZ` or current equivalent;
- stable GOG product identity;
- full-game content type;
- final zero price plus paid base or explicit giveaway evidence;
- active limited-time semantics and deadline where required by contract;
- direct first-party claim/store route;
- reject permanent-free/extras/unknown ownership semantics;
- fail closed if temporal giveaway semantics cannot be proven.

### 5. Classification / rejection reasons

Implement deterministic acceptance/rejection states such as the recon examples:
- accepted: active window + zero price + permanent grant + full game + KZ available;
- rejected: permanent F2P;
- rejected: free weekend / access only;
- rejected: non-game content;
- rejected: requires subscription;
- rejected: KZ unavailable;
- unverified: promotion window unknown;
- unverified: ownership semantics unknown.

Persist enough evidence so a later audit can explain why an offer was or was not published.

### 6. Dedup / grouping

- source offer identity is canonical at the raw normalized layer;
- never collapse by normalized title alone;
- if a trustworthy cross-store canonical mapping exists, group under one logical game while preserving each store offer/deadline/URL;
- low-confidence/fuzzy title similarity must remain separate.

### 7. Completeness / freshness

Tier-1 baseline for this task: Steam + Epic + GOG.

A canonical snapshot must explicitly record source health/completeness.
Do not publish a falsely `complete` snapshot when a required Tier-1 source failed to refresh.
Do not silently retain yesterday's active giveaway as current after its deadline or when freshness cannot be re-established.

Use current GitHub-owned production cadence unless the canonical contract already permits a different cadence. Do not create a new ChatGPT schedule.

If the existing nightly cadence is proven insufficient for time-limited giveaways, report that as an unresolved scheduling/product issue rather than silently adding a new recurring schedule in this task.

### 8. Production integration

Integrate the producer into the existing GitHub-owned production path at the correct stage, preserving single-writer ownership and failure semantics.

Produce current canonical artifacts under the selected versioned giveaway path and validate them against real current KZ source responses.

Do not manually seed production giveaway rows.

## Explicitly out of baseline

Do NOT add to the universal Tier-1 feed in this task:
- Amazon Luna / Prime subscription-gated PC entitlements;
- itch.io generic free downloads;
- Fanatical/Humble finite-key/event-specific giveaways;
- Ubisoft/EA/publisher-direct irregular campaigns;
- aggregator-only accepted offers;
- demos, prologues, trials, betas, playtests, free weekends;
- DLC/add-ons, soundtracks, artbooks, tools/assets;
- permanent F2P.

They may remain later adapters/classes.

## User relevance / UI boundary

Project rule remains: giveaways are a separate scenario from the monthly paid purchase and zero price must not improve Taste fit.

Do not invent a cross-store Taste mapping or title-based personal-relevance gate in this implementation.
If the current canonical architecture already has a safe reusable relevance route, preserve/expose the needed fields for the next UI/relevance task; otherwise report the exact missing handoff.

Do not redesign the paid-deal feed or ranking.

## Tests / validation

Add focused deterministic fixtures covering at least:
- true active claim-to-keep offer per Tier-1 source;
- permanent F2P false positive;
- free weekend/access-only false positive;
- DLC/non-game false positive;
- upcoming-not-yet-active offer;
- expired offer;
- unknown KZ region;
- source schema failure;
- unknown ownership semantics;
- duplicate/same logical game across stores without destructive offer loss;
- same/similar titles that must not merge;
- required-source failure marks overall snapshot incomplete;
- stale offer is not retained beyond deadline.

Run the smallest relevant existing regression suites plus the new giveaway tests.
Then run the canonical production path far enough to prove a real current cross-platform KZ giveaway artifact is generated or to identify one genuine external blocker.

## Hard boundaries

Do NOT:
- repeat the broad source recon;
- use Reddit/Telegram/deal sites as acceptance truth;
- manually populate current giveaway rows;
- add a second recurring ChatGPT worker;
- create a second writer for existing Steam canonical outputs;
- weaken fail-closed semantics to get a non-empty result;
- use title-only cross-store dedup;
- change paid ranking/Taste semantics;
- implement subscription entitlements in the universal giveaway baseline.

## Done when

- a versioned storefront-neutral contract exists;
- single-writer ownership is explicit and validated;
- Steam acceptance is hardened beyond `0 price + discount`;
- Epic KZ and GOG KZ adapters are implemented with strict source guards;
- one canonical normalized producer owns Tier-1 aggregation/classification/dedup;
- required-source completeness/freshness is explicit;
- deterministic tests pass;
- a real current production run proves the artifact path, even if the correct current result is an empty accepted-offer set;
- no manual production data or second scheduler was introduced.

## Report format

Save:
`reviews/worker_reports/cross-platform-giveaway-implement-01.md`

### Task
What was implemented.

### Architecture / ownership
Exact canonical writer and artifact paths.

### Sources implemented
Steam / Epic / GOG behavior and source-health state.

### Production result
Current KZ source completeness + accepted current offers count; do not paste large payloads.

### Changes
Exact files/commits.

### Validation
Tests + workflow/run refs.

### Unresolved
Only real remaining blockers, including UI/relevance/scheduling handoff if applicable.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only.

Final response must include report path and exact refs.
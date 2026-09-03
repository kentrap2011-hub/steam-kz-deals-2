# WORKER TASK — EPIC GIVEAWAY SCHEMA FIX 01

Task ID: `epic-giveaway-schema-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/epic-giveaway-schema-fix-01.md`

## Source decision

Direct continuation of:
`reviews/worker_reports/epic-giveaway-schema-recon-01.md`

Recon conclusion:
- the production failure is caused by requiring `element.price.totalPrice` for every Epic catalog element before deciding whether the element is a current giveaway candidate;
- `freeGamesPromotions` is heterogeneous and `price.totalPrice` is not guaranteed to be an object on irrelevant/non-current elements;
- one such element currently aborts the whole Epic source and marks the giveaway snapshot incomplete;
- the exact raw Sep 2 subtype (missing/null/other non-object) is unknown and must not be guessed;
- current giveaway promotion semantics remain valid and should stay authoritative;
- current active giveaway candidates must remain strict/fail-closed if their own required price data is missing or malformed.

## Goal

Implement the smallest safe parser-ordering fix so irrelevant/non-current Epic elements with variant price data no longer abort the whole source, while preserving strict validation for any current 100% giveaway that would actually be published.

## Required implementation

In the existing Epic adapter (`scripts/giveaway_epic.py` or exact current equivalent):

1. Parse only enough element structure to inspect `promotions` and determine whether the element has a **current 100% promotional offer** under the existing time-window and `discountSetting.discountPercentage == 0` semantics.
2. If an element is not a current giveaway candidate, skip it without requiring `price.totalPrice`.
3. Only after an element is confirmed as a current giveaway candidate, require the existing strict price contract:
   - `element.price` is an object;
   - `price.totalPrice` is an object;
   - `discountPrice` and `originalPrice` are integers;
   - `discountPrice == 0` for the current free promotion;
   - preserve existing `originalPrice` sanity checks and output mapping.
4. Keep current endpoint, KZ parameters, claim URL rules, output schema, source-health semantics and promotion discriminator unchanged.
5. Preserve source-level fail-closed behavior if an **actual current giveaway candidate** has missing/malformed required fields.

## Required focused regression coverage

Prove at minimum:
1. non-current/no-current-promo element with missing `price.totalPrice` -> skipped; Epic source continues;
2. non-current/no-current-promo element with `price.totalPrice = null` or another non-object -> skipped; Epic source continues;
3. upcoming-only promo with variant price -> does not abort current extraction;
4. current 100% promo + normal valid `price.totalPrice` -> maps exactly as before;
5. current 100% promo + missing/non-object `price.totalPrice` -> still fails closed;
6. malformed promotion structure that is required to determine current giveaway status remains strict according to existing contract;
7. no title/fuzzy/manual inference is introduced.

Use the smallest existing test file/fixture surface. Do not broaden into general Epic API compatibility work.

## Production verification

After focused tests pass:

1. Run/use the existing canonical giveaway production path.
2. Capture a fresh canonical giveaway snapshot/source-health result.
3. Prove that Epic no longer fails merely because an irrelevant/non-current element has variant `price.totalPrice`.
4. If current Epic data is reachable and valid:
   - Epic source should be `ok/complete` when all current giveaway candidates satisfy the strict contract;
   - any active current giveaway should be emitted through the existing canonical schema;
   - zero active giveaways is acceptable only if the source itself is complete.
5. If live Epic access is unavailable from the worker environment, use the canonical GitHub-owned production run/evidence if available. Do not invent live proof.
6. If an actual current giveaway candidate itself has malformed/missing required price data, stop with explicit fail-closed evidence rather than weakening the contract.

## Critical boundaries

Do NOT:
- make price parsing globally permissive;
- accept malformed price data for a current published giveaway;
- add fallback pricing or a second giveaway source;
- use title/fuzzy/manual matching as source authority;
- change ITAD/IGDB identity enrichment;
- redesign giveaway UI;
- change Steam/GOG behavior;
- change paid deal/ranking/Taste logic;
- create new scheduler/queue/writer/provider ownership;
- process the catalog manually item-by-item.

## Expected implementation surface

Prefer maximum 2–3 components:
- `scripts/giveaway_epic.py`;
- existing focused Epic giveaway test file/fixture;
- only one additional exact test fixture/component if genuinely necessary.

Do not change workflows unless the existing canonical production run cannot exercise the already-owned code path and a workflow change is strictly necessary; if so, stop and report rather than broadening silently.

## Required result

Report:
1. exact code change and why it matches the recon;
2. exact strictness preserved for current giveaways;
3. focused regression results;
4. production run/snapshot/source-health evidence;
5. whether Epic source is now complete;
6. current active accepted giveaway count, if live production evidence is available;
7. exact refs/commits/runs;
8. whether the original `SOURCE_SCHEMA_FAILURE` incident is closed.

Status exactly one:
- `complete`
- `needs_followup_fix`
- `blocked`

## Completion

Save:
`reviews/worker_reports/epic-giveaway-schema-fix-01.md`

Final answer must state exact report path, status and exact refs.
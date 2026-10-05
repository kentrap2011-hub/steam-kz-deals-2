# WORKER TASK — Steam discovery 50-percent discount and top-100 implementation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`

## Mode
IMPLEMENT / VALIDATE only after START gate and architecture preflight.

## Corrected user-approved product decisions
1. **50 means minimum discount 50%, not 50 visible offers.**
2. The live site keeps the previously approved **hard maximum of 100 best current offers**.
3. Current KZ paid price ceiling remains <=4500 KZT unless a bounded acceptance check proves a required exception.
4. Very obscure low-signal indie titles may be discarded early, but not by one blind review-count cutoff; preserve a deterministic exception path for unusually strong quality/value.
5. Temporary DLC rule: discover/consider DLC only for base games that pass the normal base-game suitability/eligibility path. The base game need not be visible in the final 100.
6. A later owned-library task extends DLC discovery to owned base games.
7. Bundles/packages are independent purchase opportunities and are evaluated before the visible top-100 cap.
8. Persist funnel counts for every major reduction step.

## Required staged flow

### Stage 1 — Base games: source narrowing
Use the existing GitHub-owned Steam collector. No second collector/scheduler/queue/retry owner.

Fetch the current discounted **base-game** partition for Kazakhstan with the strongest live-verified source-side bounds available.

Apply cheap deterministic gates as early as safely possible:
- current discount >=50%;
- current paid price <=4500 KZT;
- obvious non-game/extras/software rejection;
- validated obscure-low-signal rejection with an exceptional-value/quality escape path.

If Steam cannot safely express the 50% minimum discount in the source query, fetch only the bounded current-sale game partition and reject <50% immediately after parsing, before expensive enrichment.

### Stage 2 — Cheap quality and existing evidence
For surviving base games:
- reuse current cached personal/taste evidence whenever valid;
- use cheap current review/tag/release metadata before expensive semantic work;
- build the internal eligible base-game pool.

**Do not reduce this pool to 100 at this stage.** GitHub may remove only candidates that fail the approved deterministic eligibility gates.

Every candidate that survives those gates and can compete for publication must then receive the required **full detailed semantic analysis** under the existing Dossier/Deep architecture, reusing valid cached completed analysis where available.

The final top 100 may be chosen only after detailed analysis is complete for the entire current eligible comparison pool.

### Stage 3 — DLC discovery
Only after the eligible/suitable base-game set exists, discover DLC **for those base games**, rather than crawling all Steam DLC globally.

For each admitted base game:
- obtain the associated DLC identities through the safest existing/verified Steam relation path;
- consider only current KZ DLC offers meeting discount >=50%, price and ordinary quality/value rules;
- reject DLC unrelated to an admitted base game.

After the separate owned-library task, the base set becomes:
- suitable/eligible base games; OR
- base games owned by the user.

DLC discovery happens before final family resolution/ranking/top-100 publication.

### Stage 4 — Bundles/packages: independent lane
Do **not** crawl every historical Steam bundle/package.

Discover the current discounted KZ bundle/package offer partition with the strongest safe price/content bounds. Apply discount >=50% and price gates before resolving contents whenever the source data permits; otherwise apply them immediately after parsing.

Only surviving bundle/package offers get expensive content resolution.

For a surviving bundle:
- resolve the included games;
- assess relevant member games even when a member is not itself currently discounted and therefore did not enter the standalone-sale lane;
- member games do not need to be visible top-100 cards;
- count only genuinely suitable/eligible member games toward package value;
- compare package price against useful member value/current standalone alternatives through the canonical purchase-value rules;
- preserve one primary offer per purchase family;
- allow an exceptional bundle to enter the visible top 100 even when none of its members individually would.

A regression fixture must cover the case where five middling games are individually below the visible cutoff but their very cheap package becomes a top offer.

### Stage 5 — Detailed analysis, ranking and publication
Keep the existing canonical final ranking authority unless a specific contract conflict is proven.

Ranking inputs come from:
- completed detailed personal-suitability analysis, reusing valid completed cached results where possible;
- purchase value (current price, saving, price history, package value, and other canonical purchase factors).

**No candidate may be excluded merely because it is currently below a provisional top-100 line before detailed analysis is complete.**

The final visible cap is applied only after:
1. base-game/DLC/bundle eligibility;
2. package/family resolution;
3. required detailed analysis of the complete current eligible comparison pool;
4. canonical final ranking.

Only then publish **at most 100** best current offers. Never take the first 100 Steam rows and never use an intermediate GitHub score to shrink the semantic-analysis scope to 100.

### Stage 6 — Funnel visibility
Persist at least:
- raw rows per source partition;
- after price bound;
- rejected below 50% discount;
- extras/software rejected;
- obscure-low-signal rejected;
- base-game candidates entering lightweight suitability;
- eligible/suitable base games;
- DLC identities looked up from admitted bases;
- DLC accepted/rejected;
- bundle offers seen;
- bundles surviving cheap gates;
- bundle contents resolved;
- family-resolved offers;
- ranked internal offers;
- visible offers after top-100 cap.

Expose a useful subset in Statistics.

## Canonical alignment
The current policy text still says no artificial top-N. Update the relevant canonical policy/contract to the corrected decision:
- complete evaluation of the approved reduced eligible universe;
- minimum current discount 50%;
- no reduction to 100 during initial GitHub filtering or before required detailed semantic analysis is complete;
- hard visible maximum 100 only after eligibility/package/family resolution, complete required detailed analysis, and canonical ranking;
- no raw/source/intermediate top-100 truncation.

GitHub remains owner of source scope, queues, completeness, ranking inputs and persistence.

## Acceptance
- bounded KZ probes prove actual source behavior for base games, DLC relation path, and bundles before a normal full run;
- one ordinary GitHub production collection completes/persists within current runtime limits;
- no second scheduler/collector/backlog manager;
- no offer below 50% discount enters normal paid publication unless a separately approved explicit exception exists;
- visible current offer count <=100;
- bundle regression described above passes;
- DLC unrelated to an admitted base is not globally crawled/processed;
- no top-100 reduction occurs before required detailed analysis of the full eligible comparison pool;
- funnel counts reconcile;
- no ChatGPT Scheduled Task is created or changed.

## Durable report
`reviews/worker_reports/steam-discovery-50-percent-discount-top100-implementation-01.md`

# WORKER TASK — Steam discovery hard-50 selection implementation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`

## Mode
IMPLEMENT / VALIDATE, but only after START gate and architecture preflight.

## User-approved product decisions
1. The live site has a **hard maximum of 50 current offers**. Fewer than 50 is allowed if fewer offers are genuinely worthy; never fill the page with weak offers just to reach 50.
2. Current safe early paid gates remain: discount >=25% and current KZ price <=4500 KZT, unless a bounded live acceptance check proves an exact source-side representation is unsafe.
3. Very obscure low-signal indie titles may be discarded early. Do not use a blind review-count cutoff: preserve an exception path for unusually strong quality/value signals. The worker must propose and validate the exact deterministic rule on current data.
4. **Temporary DLC rule:** only consider DLC whose base game itself passes the normal game suitability/eligibility path. The base game does not need to be in the final visible 50. A separate queued task will later add DLC for games owned by the user.
5. Bundles/packages are independent purchase opportunities. A bundle must be able to reach the final 50 even when none of its member games would individually be in the final 50.
6. Show durable funnel counts for every major rejection step so the user can see where volume is removed.

## Required behavior

### A. Reduce Steam discovery before expensive work
Use the existing GitHub-owned collector. Do not create a second collector, scheduler, recurring stage, queue or retry owner.

Use explicit bounded source partitions where the current Steam endpoint supports them safely. Preserve KZ price/availability authority.

Push only proven necessary conditions early. At minimum:
- paid price ceiling;
- minimum discount;
- obvious non-game/extras/software rejection;
- validated obscure-low-signal rejection;
- DLC base-game eligibility gate.

Expensive review/taste/history work must run only after cheap deterministic gates.

### B. Bundle/package handling — critical
Do not make bundle discovery depend on a member game already being in the visible top 50.

Bundle/package evaluation must occur **before the final visible cap**.

For each candidate bundle/package:
- resolve the included game identities using the existing canonical Steam/family/package path or a bounded contract-authorized extension of that path;
- evaluate bundle value against the included **eligible** games, not only already-visible games;
- compute price/value using the canonical purchase-score rules;
- preserve the current rule that one purchase family produces one primary visible offer;
- allow the bundle route to beat the standalone route when it is the stronger purchase.

Example that must remain possible:
five individually middling eligible games may all rank outside the final 50, but a very cheap bundle containing them can still enter the final 50 because the bundle itself is an exceptional purchase.

The current `config/final_ranking_policy.json` fixed-package semantics may be reused, but any requirement that counts only already-visible games must be moved to pre-cap eligible-member coverage so the hard-50 cap cannot hide package value.

### C. Final visible cap — critical
Do **not** take the first 50 Steam rows and do not cap before eligibility/package/family resolution.

Required order:
1. source-side narrowing;
2. cheap deterministic rejection;
3. required review/taste/deal enrichment;
4. family/package resolution;
5. canonical final ranking;
6. take the first **at most 50** eligible current offers for publication.

The existing canonical final ranking contract remains the ranking authority unless this task proves a specific contract change is required. Do not invent a second ranking formula just for the cap.

If unresolved/progressive-analysis states can cause a lower-quality processed item to outrank a clearly stronger unprocessed candidate, surface that as a blocking product/contract issue rather than silently changing the ranking model.

### D. Observability
Persist counts at least for:
- raw Steam rows seen;
- rows after source-side price/content narrowing;
- rows rejected for discount;
- obvious extras/software rejection;
- obscure-low-signal rejection;
- DLC rejected because base game is not suitable;
- review/enrichment candidates;
- eligible games;
- eligible bundles/packages;
- family-resolved offers;
- ranked offers before cap;
- visible offers after hard cap (<=50).

Expose the useful user-facing subset in Statistics if that is consistent with the existing visual-data route.

## Canonical alignment
The current policy still says full snapshot/no artificial top-N. The user has now explicitly changed that product decision.

Before source/runtime implementation, update the relevant canonical policy/contract so it states:
- complete evaluation of the approved reduced eligible universe;
- hard **visible** maximum 50 only after family/package resolution and canonical ranking;
- no arbitrary raw/source top-50 truncation.

GitHub remains owner of source scope, queues, completeness, ranking inputs and persistence.

## Acceptance checks
- bounded KZ source probe proves the new narrowing semantics before a normal full run;
- one ordinary GitHub production run completes and persists within the existing runtime limit;
- no second scheduler/collector/backlog manager exists;
- visible current offer count is <=50;
- a regression fixture proves a strong cheap bundle can enter the final 50 even when all member standalone games are below position 50;
- a regression fixture proves DLC for an unsuitable/unqualified base game is excluded;
- funnel counts reconcile deterministically;
- no Fast/Dossier/Deep semantic execution is triggered merely as implementation validation;
- no ChatGPT Scheduled Task is created or changed.

## Durable report
Write:
`reviews/worker_reports/steam-discovery-hard-50-selection-implementation-01.md`

Report exact before/after funnel counts, contract changes, tests, production acceptance result, and any unresolved product risk.

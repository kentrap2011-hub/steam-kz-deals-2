# TASK — steam-server-side-prefilter-optimization-01

Status: `queued_later_do_not_start_now`
Mode when authorized: `MEASURE_FIRST_THEN_PROPOSE`

## Goal

Reduce the amount of Steam catalog data that must be fetched and enriched on each production refresh by pushing only **safe coarse filtering** into the Steam search request when possible, while preserving the current shortlist logic and recall.

Current real-production baseline from run `34643249267`:
- Steam catalog observed: `17,299` items;
- successfully processed: `17,287`;
- final production shortlist: `676` items;
- current request already uses `specials=1`;
- current local logic then filters by price, discount, tags, age/release date and review requirements.

The target is **not** to force Steam to return exactly ~600 items. The target is to reduce the input substantially (ideally to a few thousand or less if safe) without losing games that the current rules would keep.

## Core safety rule

Do not make the production catalog faster by silently reducing recall.

A proposed server-side filter is acceptable only if evidence shows it does not exclude items that can pass the current canonical shortlist rules.

If exact zero-loss cannot be proven for a proposed Steam-side filter, reject that filter or classify it as inconclusive. Do not trade correctness for speed without separate user approval.

## Required investigation when authorized

1. Identify which relevant filters the actual Steam search endpoint reliably supports for the Kazakhstan request used by this project.
   - Verify behavior; do not assume undocumented parameters work merely because they exist in Steam UI URLs.
   - Current `specials=1` behavior is the starting point.

2. Map the current canonical local eligibility rules to fields Steam can safely filter before download, including only where semantics match sufficiently:
   - discount;
   - price;
   - game/software/category exclusions;
   - tags/genres where safe;
   - release-age constraints where safe;
   - other coarse filters that cannot exclude a currently eligible path.

3. Use the existing successful production result as a control set.
   - Baseline final shortlist count: `676` from run `34643249267`.
   - Prefer replay/offline comparison from durable current data where possible.
   - For filters that require live Steam verification, use bounded queries/measurements rather than immediately running repeated full production crawls.
   - Account for normal catalog drift when comparing a later live sample to the historical baseline.

4. For every candidate filtering strategy, measure at minimum:
   - number of Steam catalog rows returned / expected pages;
   - reduction versus the ~17,299 baseline;
   - whether every baseline/current-canonical qualifying game remains reachable;
   - review-enrichment candidate count impact;
   - expected request-count/runtime reduction;
   - any correctness risk caused by Steam-side semantics.

5. Compare practical strategies rather than guessing. Examples may include:
   - one broader safe Steam query followed by canonical local filtering;
   - union of a small number of narrower safe Steam queries matching different canonical eligibility paths;
   - keeping full catalog discovery less frequently while using narrower commercial refreshes between discoveries, if evidence shows this is safer/faster.

6. Explicitly evaluate whether the ~14k review-candidate prefilter can also be reduced safely. The current structural review-enrichment gate is broad; identify which conditions can be checked earlier or served by durable known metadata without changing the canonical selection outcome.

## Important constraints

- Do not change the user's canonical price/discount/tag/review selection rules merely to improve speed.
- Do not use Steam popularity/order/ranking as a substitute for eligibility unless all qualifying games remain provably reachable.
- Do not drop packages/apps solely because their type is inconvenient; preserve existing identity/eligibility semantics.
- Do not weaken partial-publish failure isolation.
- Do not investigate the 12 current review-enrichment problem games as part of this task.
- Do not modify Taste or giveaway logic.
- Do not run repeated full Steam production refreshes just to benchmark alternatives.
- No production implementation until the Director/user separately authorizes IMPLEMENT after reviewing measurement results.

## Output when measurement phase is authorized

Write durable report:
`reviews/worker_reports/steam-server-side-prefilter-optimization-01.md`

Report must include:
- baseline;
- candidate Steam-side filter strategies tested;
- exact evidence/measurements;
- recall/correctness comparison;
- estimated request/runtime improvement;
- recommended strategy, if any;
- filters rejected and why;
- whether implementation is safe to authorize;
- smallest implementation plan.

Final status for measurement phase:
- `measurement_complete_safe_optimization_found`
- `measurement_complete_no_safe_material_reduction_found`
- `blocked_requires_followup`

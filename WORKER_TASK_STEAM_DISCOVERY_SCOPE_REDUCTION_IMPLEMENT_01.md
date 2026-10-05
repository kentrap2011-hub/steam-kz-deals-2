# WORKER TASK — Steam discovery scope reduction implement 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Do not search, read, modify, or use another repository. If the repository target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2`.

Task ID: `STEAM_DISCOVERY_SCOPE_REDUCTION_IMPLEMENT_01`
Worker slot: `ЧАТ 1`
Mode: `IMPLEMENT / VALIDATE`

## Goal

Implement the approved preservation-first Steam discovery reduction based on the completed diagnostic:

`reviews/worker_reports/steam-discovery-maximal-scope-reduction-diagnostic-01.md`

Do not repeat the broad diagnostic.

User-approved product decision:
- minimum paid-offer discount is **50%**;
- the site should aim to surface roughly the best ~100 offers, but this task must **not** implement an arbitrary raw-fetch top-N cutoff;
- keep current DLC and bundle/package semantics unless a change is strictly required for correctness;
- preserve a separate free/giveaway lane if current canonical product policy still requires it.

The implementation target is to make the existing GitHub-owned collector finish reliably within its existing production cycle by reducing source scope before expensive traversal/enrichment.

## START

1. Read current `CHAT_PROTOCOL.md` and perform START gate.
2. Read `CHAT_CONTEXT.md`.
3. Read this task fully.
4. Read only the Steam/discovery route in `PROJECT_ROUTES.md`.
5. Read the completed diagnostic report named above.
6. Read only the canonical ownership/business policy files required for Steam discovery and current shortlist eligibility.
7. Inspect only the exact existing collector/workflow/test files required for this implementation.

Do not reconstruct project history and do not inspect unrelated Dossier/Deep/Fast/ranking internals.

## Mandatory architecture preflight

GitHub remains sole control-plane owner for discovery scope, completeness, manifests, persistence and downstream orchestration.

Do not create:
- a second collector;
- a second scheduler;
- a ChatGPT-owned discovery loop;
- a new recurring queue/retry subsystem;
- any Scheduled Task;
- any Catalyst-specific special case.

If current canonical policy still encodes a lower minimum discount than 50%, update the canonical policy/contract first so implementation and policy agree.

## Required implementation

### 1. Explicit source partitions

Replace the ineffective broad combined content-category discovery shape with explicit bounded discovery partitions for the currently supported content types.

At minimum preserve the current supported game / DLC / bundle-or-package semantics unless canonical policy says otherwise.

Merge/deduplicate exact identities deterministically inside the existing GitHub collector.

### 2. Push current necessary paid-offer conditions as early as safely possible

For paid discovery:
- preserve Kazakhstan region/currency semantics;
- verify and use the current hard paid price ceiling of **4500 KZT** at the earliest safe source boundary;
- exclude free-to-play rows from paid partitions where the live Steam interface supports it safely;
- apply **discount >= 50%** as the current paid-offer gate as early as deterministically safe;
- keep price <= 4500 KZT;
- reject obvious extras/software-only rows using existing canonical rules before review enrichment.

Do not assume Steam-side query parameters are correct solely because a string is constructed. Add bounded live-shaped validation for the actual parameter semantics used.

If exact KZ `maxprice` semantics cannot be proven reliable, implement the diagnostic's approved fallback only if its price-order early-stop correctness can be proven. Do not silently choose an unsafe source cutoff.

### 3. Preserve free/giveaway semantics

If current canonical product policy still includes free/giveaway offers, keep them in a separate bounded lane. Do not let paid-only filtering silently remove them.

### 4. Review-enrichment reduction

Only rows that remain capable of satisfying current approved product rules should reach expensive review enrichment.

The 50% minimum discount is user-approved and must replace the earlier 25% preservation threshold wherever that threshold represented current paid eligibility.

Do not change unrelated review-quality/taste/family/ranking semantics in this task.

### 5. About ~100 visible offers

Do **not** implement a raw Steam top-100 or arbitrary source truncation.

This task may expose/measure the resulting candidate counts, but any separate hard final-site top-N publication rule is outside scope unless it is already canonical.



## Previously approved product and site rules

These decisions are already approved by the user and must be treated as requirements, not reopened questions:

### Final visible set
- The site should show **at most about 100 best offers**.
- Do **not** shrink the candidate universe to 100 before detailed/deep analysis.
- The intended flow is: apply deterministic Steam/commercial filtering first, then allow detailed/deep analysis of the remaining candidates, and only after that keep the best ~100 for final presentation.
- The site may show the current best ~100 while analysis is still progressing; that visible set is allowed to change as stronger Deep results arrive.

### Deep priority
- A game with a **positive completed Deep result always has priority over any game that has not yet completed Deep analysis**.
- Do **not** boost an item merely because its discount is ending soon.
- For items still awaiting Deep analysis, the analysis queue should prioritize the strongest commercial/reputation candidates first. The approved ordering intent is:
  1. deal/value attractiveness;
  2. higher positive-review rating;
  3. larger review count.
- Changes to Deep ordering must be made through the GitHub-owned instruction/config file that controls ordering. Do **not** rewrite the canonical Deep worker prompt merely to change queue priority.

### DLC and Steam library
- For now, keep discovering DLC broadly because Steam-library ownership is not yet available to this pipeline.
- The intended future refinement is to prioritize/show DLC for games the user owns once Steam-library data is available.
- Do not silently remove all DLC as a source-reduction shortcut.

### Bundles/packages
- Keep bundles/packages as a distinct opportunity class.
- A strong bundle may deserve a place in the final ~100 even when its component games individually would not.
- Do not reduce bundles to a simple by-product of already-selected games unless a later explicit user decision changes this rule.

### Low-value obscure content
- Extremely obscure / low-signal “indie among indie” content may be excluded when the existing quality/reputation evidence shows it is not competitive for the best-offer product.
- Do not implement a popularity-only shortcut that could remove a genuinely strong niche offer without evidence.

### Site / operational visibility
The site must expose operational progress clearly enough that the user can see what the system is currently doing.

Required direction:
- keep the existing Statistics observability;
- add/retain **filtering funnel statistics** so the user can see how many items were removed at the major deterministic stages;
- provide a **separate current-tasks / analysis-queue view** on the site showing the active/current semantic-analysis backlog and stage state, rather than forcing the user to infer it from GitHub;
- the queue view must be read-only presentation of GitHub-owned state; the browser must not own or reorder the queue;
- include the Steam-library/DLC ownership acquisition work as an explicit visible future/current task when that task exists in canonical GitHub state.

If these site changes are too large to implement safely inside the collector-scope PR without mixing unrelated concerns, do not drop them. Record them as a bounded follow-up implementation task in the report, with exact canonical producer fields needed. The Steam-scope implementation must preserve the data needed for those Statistics/queue views.


## Required validation

Add deterministic regressions proving at least:

1. explicit partitions cover the intended supported content types;
2. merge/dedupe is deterministic;
3. no paid row below 50% discount can enter the current approved paid shortlist;
4. no paid row above 4500 KZT can enter the current approved paid shortlist;
5. exact KZ source price-bound behavior is verified by bounded acceptance evidence before it is trusted;
6. free/giveaway handling is preserved if canonical policy requires it;
7. representative game/DLC/bundle identities are not lost solely due to the new query partitioning;
8. current discovery remains GitHub-owned;
9. no new scheduler/queue/retry owner is introduced;
10. Mirror's Edge Catalyst is not special-cased.

Then run one normal GitHub-owned production discovery acceptance if protocol permits and prove:
- the collector completes within the existing 60-minute owner timeout;
- a fresh canonical discovery universe is persisted;
- downstream handoff starts from that fresh universe;
- current source cardinality/funnel counts are reported.

If live acceptance cannot be executed by the worker under protocol, stop ready for Director acceptance with exact remaining live step.

## Branch / PR / report

Use a dedicated implementation branch and PR. Do not implement directly on `main`.

Report:
`reviews/worker_reports/steam-discovery-scope-reduction-implement-01.md`

The report must include:
- exact policy/contract changes;
- exact source partitions and live-proven filters;
- where 50% is enforced;
- measured source/funnel counts before vs after where available;
- runtime/API effect;
- regression results;
- live acceptance result or exact remaining acceptance action;
- PR number/head/checks;
- any remaining product choice that cannot be safely inferred.

Do not merge unless the current protocol plus explicit Director authorization permits it. For this task, implementation is authorized; merge still requires a clean PR and green required checks.

## CURRENT_TASK.md

You may update only your own clearly delimited task entry. Re-read immediately before every write and do not overwrite another active worker's entry.

## Done when

The existing GitHub-owned Steam discovery path is materially bounded using the approved 50%/4500-KZT/current-content semantics, no arbitrary raw top-N is introduced, required checks are green, and the result is ready for Director acceptance or safely merged if the protocol explicitly permits.


## Director continuation — live KZ acceptance failure after PR #146 merge

PR #146 has now been merged to `main` as:
`fb21b704ac36f56d40bdc6a00175864538dbcee7`.

The required first normal production acceptance ran automatically:

- workflow: `Steam KZ production shortlist`;
- run: `37319401442`;
- job: `collect / 111794299510`;
- deterministic regressions passed;
- live collection then failed immediately inside the new source-bound validation;
- exact error:
  `Steam KZ source price-bound validation failed: Cannot validate KZ maxprice: Price_ASC is not monotonic at cutoff`.

This is now the current task blocker.

### Required continuation

Do not repeat the global diagnostic and do not revert the approved 50% / 4500 KZT product policy.

Investigate only this exact live acceptance failure and complete the existing implementation safely.

Determine which is true:

1. Steam's `maxprice=4500` source bound is actually reliable for KZ, but the current `Price_ASC` monotonic-boundary proof is invalid/too strict because Steam Search sorting is not strictly monotonic; or
2. the source-side `maxprice` behavior itself cannot be trusted enough to serve as a canonical completeness boundary.

Use bounded live probes only. Do not perform a broad 100k crawl.

If case 1:
- replace the faulty proof with the smallest robust live validation that directly demonstrates the required KZ price-bound semantics without depending on globally monotonic `Price_ASC`;
- retain fail-closed behavior;
- keep the explicit games/DLC/bundles partitions and 50% local gate;
- add a regression matching the real non-monotonic behavior.

If case 2:
- do not weaken completeness or silently trust `maxprice`;
- evaluate the smallest safe alternative within the existing GitHub-owned collector that can still materially reduce traversal without losing current approved candidates;
- do not use the previously suggested Price_ASC early-stop fallback unless its correctness can now actually be proven;
- if no semantics-preserving source bound is possible, stop with exact measured evidence and a bounded set of product tradeoff choices for the Director/user rather than inventing a lossy rule.

After the fix:
1. update the same implementation branch/PR follow-up path according to current protocol;
2. run deterministic checks;
3. merge only if current protocol and existing Director authorization allow the continuation;
4. run one normal `main` production acceptance;
5. require the collector to complete/persist a fresh canonical discovery universe within the existing 60-minute owner timeout;
6. report actual partition/funnel counts and whether downstream publication unblocked.

Do not change Scheduled Tasks, Dossier, Deep, Fast, ranking, or unrelated site logic.

Update:
`reviews/worker_reports/steam-discovery-scope-reduction-implement-01.md`

with the live failure, root cause, correction, checks, new PR/commit references, and final live acceptance.


## Director continuation — do not wait for opaque long-running collection

The user explicitly does **not** want to wait passively for the current long-running production collection to hit the timeout.

Current observed live run:
- workflow: `Steam KZ production shortlist`;
- run: `37335826933`;
- collect job: `111850233215`;
- started from merged PR #147;
- all pre-collection regressions passed;
- for ~45+ minutes the workflow has remained on the single collection step with no useful external progress visibility;
- GitHub exposes the job as `in_progress`, but there is no actionable per-partition/page progress visible to the Director.

Treat this lack of observability as a task defect, not as an acceptable operating condition.

### Continue now

Do not wait for run `37335826933` to reach its 60-minute timeout before continuing investigation and implementation.

Immediately inspect the exact current collector path and current run evidence needed to answer:
- whether traversal is still advancing;
- which partition it is in;
- how many pages/rows have been processed;
- whether it is spending time on Steam Search pagination, Reviews API enrichment, retry/backoff, or another bounded substage;
- whether the new scope reduction is actually material in live execution.

If the current run is still executing while this continuation is performed, do not modify its canonical outputs in place. It may be allowed to finish or time out independently. Do not create a second production writer competing with it.

### Mandatory progress observability

Add explicit progress output to the existing GitHub-owned collector so future long runs are not opaque.

At minimum, logs must expose:

1. **partition start/end**
   - `games`
   - `dlc`
   - `bundles`

2. **search traversal progress**
   - current page/request number;
   - rows seen so far;
   - Steam-reported total for that partition when available;
   - percentage or `seen / total` where meaningful;
   - cumulative eligible rows after the local 50% / 4500 KZT / extras/software gate;
   - duplicate count where meaningful.

3. **review-enrichment progress**
   - candidate AppID count;
   - current completed / total candidate count;
   - logical Reviews API request count;
   - retry / 429 / backoff count;
   - periodic progress at a useful cadence, not only at the end.

4. **heartbeat**
   - when one network operation/retry loop can take long enough to make the job appear stalled, emit a periodic heartbeat with current stage and elapsed progress;
   - do not spam logs per single item if a coarser cadence such as every 10–20 pages or every bounded batch is sufficient.

5. **stage timing**
   - elapsed time for source validation;
   - each partition traversal;
   - local filtering/dedupe;
   - review enrichment;
   - shortlist/final persistence preparation.

The exact cadence may be chosen by the worker, but a Director looking at a live Actions job must be able to distinguish:
- progressing normally;
- slowed by rate limiting;
- stalled on one request;
- stuck in a large review-enrichment phase.

### Acceptance

Add deterministic tests where practical for the progress/metrics plumbing, but do not over-engineer tests for literal log strings.

The next normal `main` production acceptance must show enough live log/progress evidence to identify the active stage while it is running.

Do not increase the timeout merely to hide slow traversal.

Do not add another scheduler, collector, background worker, or competing production write path.

Update the existing report with:
- what the long run was actually doing;
- the last observable progress before completion/failure;
- the progress instrumentation added;
- whether the live runtime is now materially reduced;
- final production acceptance result.


## Director continuation — bundles + 429 bottleneck after PR #148 live timeout

The second normal `main` acceptance after PR #148 has now completed and timed out at the existing 60-minute owner limit.

Canonical live evidence:

- workflow run: `37345668260`;
- collect job: `111883491529`;
- result: cancelled at timeout;
- games completed:
  - reported total: **63,645**;
  - 637 pages at page size 100;
  - elapsed: **~1,573 s (~26.2 min)**;
- DLC completed:
  - reported total: **34,342**;
  - 344 pages;
  - elapsed: **~822 s (~13.7 min)**;
- bundles started but did not complete:
  - reported total: **~105,326**;
  - last observed: **48,000 rows / ~45.6%**;
- search 429 events by timeout: **192**;
- accumulated search backoff: **2,160 s (~36 min)**;
- review enrichment had not started yet;
- no fresh canonical production commit/persistence occurred.

This confirms the next blocker is no longer opaque:
1. the bundle partition is unexpectedly enormous;
2. Steam Search rate limiting/backoff dominates runtime.

### Required continuation

Do not re-open already solved items:
- page size 100 is already live-proven;
- progress observability is already implemented;
- games and DLC partitioning are working;
- 50% minimum discount and 4500 KZT maximum price remain fixed product requirements;
- no raw top-N truncation is allowed;
- do not increase the timeout as the primary fix.

Investigate only the smallest semantics-preserving ways to reduce **bundle traversal** and/or **429 exposure**.

### Bundle-specific validation

First determine what Steam's `category1=996` partition actually contains in the live KZ search surface.

Use bounded probes only and answer:
- are the ~105k rows genuinely distinct purchasable packages/bundles relevant to this product, or is this partition semantically broader/noisier than expected?
- what content types / purchase entities are returned?
- how much overlap exists with game/DLC AppIDs or duplicate package identities?
- are many rows software/soundtrack/video/demo/extras-like or otherwise outside the product's intended "valuable bundles/packages" class?
- is there a more precise Steam-supported query/filter for purchasable bundles/packages that preserves the intended bundle opportunity class?

Do not infer from parameter names alone; verify against bounded live samples.

### 429 / request strategy

Measure the current rate-limit pattern using bounded probes and existing logs.

Evaluate only safe options such as:
- request pacing that avoids the expensive repeated 3/6/12/24-second retry ladder;
- a conservative inter-request delay if it reduces total wall-clock time by preventing bursts/429s;
- use of Retry-After or other Steam response signals if actually present;
- bounded concurrency only if it is demonstrably safe and does not worsen rate limiting or violate current ownership assumptions;
- resuming/checkpointing within the existing GitHub-owned producer if canonical correctness can be preserved and the task architecture already permits it.

Do not add an unrelated scheduler/background collector.

### Preserve product intent

Bundles/packages remain a distinct valuable opportunity class. Do not solve the timeout by silently dropping bundles entirely or by keeping only famous bundles.

If the current `category1=996` source surface is proven to be far broader than the intended product concept, replace it only with a narrower source/query whose semantics are directly evidenced.

If no source-side semantics-preserving narrowing exists, report the exact tradeoff and propose the smallest architecture change that preserves completeness across runs rather than inventing a lossy cutoff.

### Acceptance

The next correction must:
1. be deterministic-green;
2. avoid a competing production writer while another run is active;
3. keep progress observability;
4. preserve completeness for the approved games/DLC/bundle product scope;
5. finish a normal `main` production collection within the existing 60-minute owner timeout, or provide exact evidence that a single-run 60-minute completion is impossible without a bounded architectural change;
6. persist a fresh canonical universe and start downstream handoff before declaring the defect fixed.

Update:
`reviews/worker_reports/steam-discovery-scope-reduction-implement-01.md`

with the bundle findings, 429 analysis, chosen correction, PR/checks, and final live acceptance evidence.

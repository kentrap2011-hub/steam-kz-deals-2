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

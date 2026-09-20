# WORKER TASK — PRODUCTION ARCHITECTURE SIMPLIFICATION REVIEW 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `production-architecture-simplification-review-01`
Mode: `READ-ONLY / ARCHITECTURE REVIEW`

## Why this task exists

The project has spent a prolonged period fixing production orchestration, Taste/Dossier evidence, binding, scheduled-worker, retrieval, validation and observability problems while the user-facing outcome has degraded: the user has not been reliably seeing current discounted games.

This review must challenge the architecture from first principles.

The goal is NOT to preserve every existing subsystem.
The goal is to recommend the simplest architecture that reliably delivers useful current game deals while retaining personalization where it adds value.

Do not optimize for elegance of the current design.
Optimize for:
1. visible useful deals every day;
2. failure isolation;
3. deterministic recovery;
4. low operator involvement;
5. bounded dependence on LLM/Scheduled Task compliance;
6. understandable production state;
7. incremental improvement without blocking the core product.

## START

First read current `CHAT_PROTOCOL.md` from `main` and complete START gate.

Then read this task fully.

After START read, in this order, only what is needed:

1. `CHAT_CONTEXT.md`;
2. `PROJECT_ROUTES.md`;
3. `PROJECT_RULES.md` — only sections that define the actual user-facing purpose and required deal-selection behavior;
4. `PROJECT_DECISIONS.md` — only decisions that materially constrain current production architecture;
5. `config/daily_execution_contract.json`;
6. `config/execution_ownership_contract.json`;
7. `config/mailing_policy.json` and/or `config/mailing_policy.md`;
8. `config/final_ranking_policy.json`;
9. current compact production/pre-AI/visual state needed to determine whether deals are flowing;
10. `DIRECTOR_TASK_BOARD.md`;
11. only the worker reports needed to understand the repeated failure classes.

Do NOT read every historical Taste/Dossier task or every implementation report.

## Architecture preflight

Before proposing any architecture, explicitly answer:

1. What does GitHub own today?
2. What does Scheduled ChatGPT own today?
3. Which user-facing outputs currently depend on Scheduled ChatGPT completing successfully?
4. Which failures block the entire daily product versus only optional enrichment?
5. Which current fail-closed gates protect correctness, and which may be over-scoped because they block unrelated useful output?

This task is READ-ONLY. Do not implement.

## Primary product question

Answer this directly:

> What is the smallest reliable production system that can resume showing useful current discounted games quickly, while advanced Taste/Dossier enrichment can fail, lag, or recover independently without taking the daily product down?

Do not assume the answer is the existing pipeline with more guards.

## Required current-state map

Build a compact critical-path map from:

`source data -> filtering -> deal facts -> history -> personalization -> ranking -> visual/current payload -> UI`

For every stage record:
- owner;
- whether deterministic or LLM-dependent;
- whether required for a basic deal to be shown;
- whether failure currently blocks downstream publication;
- whether cached/last-known-good data can legally be used;
- expected recovery behavior;
- known repeated failure class, if relevant.

The purpose is to identify unnecessary coupling.

## Required failure-class review

At minimum review these broad failure classes, without re-debugging each incident:

- Scheduled Task instruction/prompt non-compliance;
- stale binding/snapshot mismatch;
- semantic/Taste backlog or stale result;
- Taste Steam Review Dossier evidence/retrieval failure;
- external-site retrieval variability;
- fail-closed whole-group behavior;
- validator/generator mismatch;
- runtime artifact/persistence handoff;
- long repair cycles where the core daily product remains unavailable.

For each class answer:
- should this be able to stop **all deals**?
- should it stop only one game?
- should it stop only personalization/enrichment?
- should it merely lower confidence or mark data stale?

## Architectural principles to test

Do not assume they are all correct; evaluate them.

### P1 — Core deal availability must not depend on LLM completion

A basic current deal with deterministic facts should be publishable even if Taste/Dossier enrichment is unavailable.

### P2 — Personalization is enrichment, not availability

If fresh personalization is unavailable, consider:
- last-known-good taste;
- coarse cached taste;
- neutral ranking;
- visible `personalization_pending` / `personalization_stale`;
- exclusion only when a hard business rule truly requires it.

### P3 — One bad game must not block unrelated games

Evaluate per-item quarantine / partial publish versus current group-level fail-closed behavior.

### P4 — External evidence collection should be asynchronous to the daily deal path

Evaluate whether Taste Dossier can be maintained as a background knowledge cache whose freshness affects confidence, not basic daily availability.

### P5 — GitHub should own all deterministic state transitions

Scheduled ChatGPT should ideally receive a small immutable work item and return a bounded result; missing/invalid results should be quarantinable without blocking unrelated deterministic work.

### P6 — Last-known-good should be first-class

Evaluate explicit TTLs and fallback rules for:
- Taste verdicts;
- dossier facts;
- SteamDB/history;
- external review evidence;
- ranking inputs.

### P7 — User-visible output should have an availability SLA

Define a concrete target such as:
- daily payload exists by a fixed time;
- if enrichment is incomplete, publish degraded-but-valid payload;
- stale/degraded state is explicit.

Do not invent an SLA arbitrarily; recommend one with rationale.

## Required architecture alternatives

Compare at least four designs.

### DESIGN A — Current architecture, hardened

Keep current coupling and fail-closed philosophy, add observability/retries/guards.

Evaluate:
- reliability;
- complexity;
- operator burden;
- time-to-recovery;
- risk of another month-long repair cycle.

### DESIGN B — Split core deals from enrichment

Daily deterministic pipeline publishes eligible deals and ranking using available stable/cached data.
LLM-dependent Taste/Dossier enrichment updates independently.
Missing enrichment cannot block unrelated deals.

Evaluate exact boundary.

### DESIGN C — Cache-first personalization

Make long-lived per-game Taste/Dossier knowledge a background cache.
Daily deals never request large semantic work synchronously; they consume whatever valid cache exists and queue misses separately.

Evaluate freshness policy and how unknown games are handled.

### DESIGN D — Minimal product recovery architecture

Temporarily or permanently reduce the production system to the smallest useful feature set:
- current deal;
- basic eligibility;
- price/history;
- existing taste cache when available;
- deterministic ranking;
- UI output.

Everything else becomes optional background enrichment.

Evaluate what user-visible quality is lost versus reliability gained.

You may propose a fifth design only if it is materially different.

## Required recommendation

Choose exactly one target architecture.

It may be a staged migration, but there must be one clear target.

The recommendation must specify:

### 1. Core synchronous path
What must complete for today's deals to appear?

### 2. Non-blocking enrichment path
Which Taste/Dossier/external-evidence work moves off the critical path?

### 3. Failure isolation
What happens when:
- one game fails;
- one LLM result is invalid;
- Scheduled Task never runs;
- Steam/third-party pages cannot be retrieved;
- fresh Taste evidence is unavailable;
- a binding changes;
- an enrichment backlog grows?

### 4. Fallback hierarchy
For every important enrichment input define:
- fresh value;
- last-known-good value;
- stale-but-allowed value;
- unknown/default;
- hard-stop condition if any.

### 5. Publication semantics
Can partial daily output publish?
How is degraded/stale state surfaced?
What is the minimum valid daily payload?

### 6. Progress/completeness
Separate:
- completeness of daily user-facing deals;
- completeness of background enrichment.

Do not use one global completeness bit if those are different product concepts.

### 7. Retry/recovery
Which component retries what?
No conversational retry loops.

### 8. Observability
Name the small set of machine-visible states sufficient to answer:
- did today's deterministic build run?
- did a payload publish?
- how many games were omitted and why?
- how stale is enrichment?
- is Scheduled ChatGPT healthy?
- is background backlog growing?

Avoid verbose per-invocation LLM narration as the primary monitoring mechanism.

## Required simplification analysis

Identify current components/rules that could be:

- removed entirely;
- demoted from blocking to non-blocking;
- merged;
- cached;
- changed from group-level to item-level;
- replaced by deterministic validation;
- kept unchanged because they protect an essential invariant.

For every proposed removal/demotion explain the correctness risk.

## User-outcome recovery plan

Provide a staged plan prioritizing visible deals.

### Phase 0 — restore service
Smallest bounded change that could get useful deal output flowing again while preserving safety.

### Phase 1 — isolate enrichment
Remove LLM/Taste/Dossier failures from the core publication critical path.

### Phase 2 — simplify and delete obsolete machinery
Delete or retire duplicated guards/workflows/contracts only after the new path is proven.

### Phase 3 — improve personalization quality
Only after daily availability is reliable.

For each phase specify:
- objective;
- exact architecture change class;
- acceptance condition;
- rollback path;
- what the user sees.

Do NOT implement any phase.

## Quantitative comparison

Create a compact comparison table for Designs A-D with qualitative or bounded categorical values for:

- core daily availability;
- dependence on Scheduled ChatGPT;
- blast radius of one bad game;
- operational complexity;
- recovery difficulty;
- personalization quality;
- stale-data tolerance;
- migration effort.

Do not fabricate numeric reliability percentages unless supported by actual data.

## Explicit challenge to existing assumptions

Answer these questions even if the answer contradicts current design:

1. Does Taste Steam Review Dossier need to be on the daily critical path at all?
2. Does Russian-review retrieval need to block a deal from appearing?
3. Does exact fresh semantic evidence need to exist before every daily recommendation?
4. Should a group of three fail as one atomic unit for user-facing publication?
5. Is current content-complete binding protecting real correctness on the daily path, or is some of it only necessary for background knowledge updates?
6. Are we mixing “cannot prove enrichment is perfect” with “cannot safely show a discounted game”?
7. Which current invariants are essential user-safety/business invariants versus engineering-process invariants?

## No sunk-cost bias

Existing implementation effort is not a reason to preserve a subsystem.

If the best recommendation retires or sidelines major Taste/Dossier machinery, say so.

Likewise, do not recommend deleting it merely because it has caused problems; preserve it if it provides irreplaceable value and can be removed from the critical path.

## Scope exclusions

Do NOT:
- implement anything;
- edit contracts/source/workflows;
- run production;
- trigger Scheduled Tasks;
- manually rebuild today's deals;
- process backlog;
- change user preference/business rules;
- use another repository;
- optimize a single Hellish Quart/Cthulhu retrieval issue;
- create another observability patch as the primary answer.

Only the durable architecture review report may be written.

## Acceptance checks

REVIEW-01 — actual user-facing product goal identified from canonical rules.

REVIEW-02 — current critical path mapped end-to-end.

REVIEW-03 — blocking vs non-blocking dependencies identified.

REVIEW-04 — repeated failure classes reviewed by blast radius.

REVIEW-05 — Designs A-D compared.

REVIEW-06 — exactly one target architecture recommended.

REVIEW-07 — recommendation explicitly addresses whether Taste/Dossier remains on the daily critical path.

REVIEW-08 — per-item versus group-level failure semantics decided.

REVIEW-09 — fallback/last-known-good hierarchy defined.

REVIEW-10 — daily availability/completeness separated from enrichment completeness.

REVIEW-11 — machine-observable health model defined without depending primarily on LLM prose.

REVIEW-12 — Phase 0..3 migration/recovery plan defined.

REVIEW-13 — exact canonical contracts/components that would need later change are bounded.

REVIEW-14 — no implementation/production mutation occurred.

REVIEW-15 — exactly one next recommended step.

## Durable report

Write only:

`reviews/worker_reports/production-architecture-simplification-review-01.md`

Required sections:

1. Task / repo / mode.
2. User-facing product objective.
3. Current architecture / critical path.
4. Current blocking dependencies.
5. Failure-class blast-radius review.
6. Design A.
7. Design B.
8. Design C.
9. Design D.
10. Comparison table.
11. Explicit answers to the seven challenged assumptions.
12. Recommended target architecture — exactly one.
13. Core synchronous path.
14. Non-blocking enrichment path.
15. Fallback hierarchy.
16. Publication / partial-success semantics.
17. Availability vs enrichment completeness.
18. Retry / recovery ownership.
19. Minimal observability model.
20. Components to remove/demote/keep.
21. Phase 0 — restore service.
22. Phase 1 — isolate enrichment.
23. Phase 2 — simplify/delete.
24. Phase 3 — quality.
25. Required later canonical changes.
26. REVIEW-01..15.
27. Changes: report only.
28. Unresolved.
29. Status.
30. Exactly one recommended next step.
31. Exact refs.
32. Efficiency / reusable lesson.

Allowed statuses:
- `complete_architecture_recommendation`
- `needs_user_decision`
- `needs_more_recon`
- `blocked_external`

## Status rule

`complete_architecture_recommendation` requires:
- one clear target architecture;
- a Phase 0 capable of restoring useful output without relying on unfinished advanced enrichment;
- explicit ownership boundaries;
- explicit degradation/fallback behavior;
- no implementation.

## Exactly one next step

If complete:
- return to Director for comparison with the parallel observability preflight and user decision on the migration direction before any IMPLEMENT task.

Do not implement inside this task.

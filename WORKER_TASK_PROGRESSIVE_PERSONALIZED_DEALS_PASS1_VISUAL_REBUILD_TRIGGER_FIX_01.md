# WORKER TASK — Progressive Personalized Deals PASS 1 Visual Rebuild Trigger Fix 01

## Identity
- Task ID: `progressive-personalized-deals-pass1-visual-rebuild-trigger-fix-01`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Base branch / source of truth: `main`
- Mode: `IMPLEMENT / ACTIVATE / VALIDATE`
- Worker slot: `СУЩЕСТВУЮЩИЙ ЧАТ — ЧАТ 1`

## Confirmed defect
The first real Progressive PASS 1 invocation proved that Scheduled semantic execution, create-only result submission, GitHub ingest/validation, durable PASS 1 state, and queue progression work.

The remaining confirmed production defect is downstream publication:
accepted Progressive PASS 1 state does not trigger the existing GitHub-owned progressive visual/site rebuild path, so `data/production/visual/current.json` and the published site remain stale after accepted PASS 1 ingest.

Multiple consecutive PASS 1 items per Scheduled invocation are valid current production behavior and are NOT part of this fix.

## Goal
Make each successful accepted Progressive PASS 1 ingest cause the existing GitHub-owned progressive visual/site projection/publication path to refresh from current canonical state.

After the fix, accepted PASS 1 state must become visible without requiring a second manual semantic run.

## Required preflight
Before implementation:
1. Read `CHAT_PROTOCOL.md`, `DIRECTOR_PROTOCOL.md`, this task, and the current PASS 1 live-acceptance report.
2. Identify the current owner of:
   - PASS 1 ingest;
   - progressive visual rebuild;
   - site publication/deploy.
3. Reuse the existing GitHub-owned rebuild/publication path. Do not create a competing scheduler, semantic worker, queue, or state owner.
4. Determine the narrowest safe trigger/dispatch integration and record it in the report before changing implementation.

## Scope
Implement only the missing downstream edge from accepted PASS 1 ingest to progressive visual/site refresh.

The implementation must:
- trigger only after accepted PASS 1 state/work has been durably committed;
- use current canonical GitHub state as source of truth;
- preserve item-level independent ingest semantics;
- remain safe when several PASS 1 submissions arrive in one Scheduled invocation;
- tolerate overlapping/closely spaced ingest events without corrupting or rolling back newer state;
- preserve existing deterministic expiry/scope rules;
- preserve PASS 2 inactive state;
- avoid semantic retries or new semantic execution.

## Out of scope
Do not:
- change the Scheduled PASS 1 worker prompt merely to force one-item invocations;
- add a one-item production mode;
- run or implement PASS 2;
- retry `analysis_incomplete` items;
- change taste semantics/scoring;
- change Russian-review/Dossier behavior;
- introduce another control plane or scheduler;
- manually fabricate visual state.

## Validation
Validate at minimum:

### FIX-01 — ownership
The rebuild/publication remains GitHub-owned and reuses the existing canonical path.

### FIX-02 — trigger ordering
A visual rebuild cannot consume pre-ingest state for an accepted result because the downstream action occurs only after durable ingest commit.

### FIX-03 — multi-item safety
A normal multi-item Scheduled invocation can cause several accepted ingests without stale later projections overwriting newer canonical state.

### FIX-04 — canonical projection
The visual rebuild reads current canonical PASS 1 state/work rather than trusting event-local stale counters.

### FIX-05 — current accepted state reflected
Without performing another semantic `Run now`, rebuild/publish current state so the already accepted PASS 1 results are reflected in the progressive visual/site.

### FIX-06 — counts
Published processing counts reconcile with current canonical state, including current scope / attempted / remaining / expired semantics.

### FIX-07 — item statuses
Already accepted visible items no longer remain falsely `not_analyzed` / Tier 3 when their canonical PASS 1 state says otherwise.

### FIX-08 — no semantic side effects
No new PASS 1 semantic attempts, retries, or PASS 2 attempts are caused by this fix/validation.

### FIX-09 — deployment
The normal site publication/deploy path completes successfully and serves the refreshed projection.

### FIX-10 — regression
Existing relevant progressive visual/site and PASS 1 validation tests pass.

## Production boundary
This task MAY rebuild/publish the visual/site from already accepted canonical PASS 1 state as part of activation/validation.

This task MUST NOT invoke the Scheduled Progressive PASS 1 semantic worker, create new semantic result artifacts, retry incomplete items, or start PASS 2.

## Durable report
Create and commit:
`reviews/worker_reports/progressive-personalized-deals-pass1-visual-rebuild-trigger-fix-01.md`

The report must include:
- architecture/ownership preflight;
- exact defect cause;
- implementation/activation refs;
- FIX-01..10;
- before/after canonical counts and visual counts;
- proof that no new semantic PASS 1/PASS 2 execution occurred;
- final status;
- exactly one recommended next step.

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `blocked_external`
- `needs_user_decision`

Before presenting completion, reread the exact durable report from `main`.

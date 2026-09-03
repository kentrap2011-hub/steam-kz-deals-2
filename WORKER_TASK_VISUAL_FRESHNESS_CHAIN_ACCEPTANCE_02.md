# WORKER TASK — VISUAL FRESHNESS CHAIN ACCEPTANCE 02

Task ID: `visual-freshness-chain-acceptance-02`
Mode: `ACCEPTANCE`
Report: `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`

## Source decision

Follow-up acceptance for completed implementation:
- `reviews/worker_reports/visual-freshness-chain-fix-01.md`
- implementation branch `worker/visual-freshness-chain-fix-01`

Do not repeat the original diagnosis and do not redesign the implementation.

## Goal

Verify that the previously failed freshness controls now work on the implemented branch before production merge/release:

1. `Fresh-cycle build proof`
2. `Deploy-to-built-cycle binding`
3. `Stale-success visibility`

## Required checks

### A. Fresh path

Prove:
`current source/history cycle -> fresh visual build -> durable receipt -> exact canonical visual blob/commit -> deploy verification`

Confirm the receipt is tied to the intended source/history cycle and exact triggering workflow run, and that a fresh classification cannot be produced without those bindings.

### B. No-build/degraded path

Prove that an invocation with no fresh paid visual emits a durable explicit state equivalent to:
- `fresh_build=false`
- `outcome=degraded/no_fresh_build`

Confirm this path cannot be classified as a normal fresh publication merely because the workflow itself succeeds.

### C. Stale/mismatch path

Prove that if the canonical/staged visual no longer matches the receipt's produced visual blob/commit or intended history/source cycle, deploy verification fails closed before Pages publication can be classified as fresh.

### D. Ownership/regression

Confirm:
- no second build/deploy workflow or production data plane was introduced;
- existing ranking/Taste semantics and prerequisite gates were not changed;
- giveaway-only/non-workflow-run paths are explicitly non-fresh rather than silently fresh;
- receipt download/binding is from the exact triggering build run, not an arbitrary/latest artifact.

## Evidence boundary

Use the implementation report, exact branch refs, focused tests and the smallest exact workflow/config evidence needed.

Do not perform broad workflow-run or Git-history archaeology.

Do not manually regenerate/deploy production merely to force acceptance.

## Boundaries

Do NOT:
- modify implementation code/config/data except this report;
- redesign the pipeline;
- weaken history/Taste/readiness gates;
- change ranking semantics;
- create another deploy/build workflow;
- broaden into semantic-runtime or giveaway identity work.

## Required result

Report exactly:
1. `Fresh-cycle build proof`: `pass | fail | partial`
2. `Deploy-to-built-cycle binding`: `pass | fail | partial`
3. `Stale-success visibility`: `pass | fail | partial`
4. `Ownership/regression preserved`: `pass | fail`
5. exact evidence for each result;
6. maximum one remaining blocker/defect;
7. whether branch is ready for production merge/release;
8. one recommended next step only.

Status exactly one:
- `complete`
- `needs_fix`
- `blocked`

## Completion

Save:
`reviews/worker_reports/visual-freshness-chain-acceptance-02.md`

Final answer must state exact report path, status and exact refs.
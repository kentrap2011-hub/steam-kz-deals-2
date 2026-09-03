# WORKER TASK — VISUAL FRESHNESS CHAIN FIX 01

Task ID: `visual-freshness-chain-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`

## Source decision

Direct continuation of:
- `reviews/system_audits/baseline-01.md`
- `reviews/worker_reports/visual-freshness-chain-acceptance-01.md`

Acceptance result:
- `Fresh-cycle build proof`: `fail`
- `Deploy-to-built-cycle binding`: `fail`
- `Stale-success visibility`: `fail`
- status: `needs_fix`

Do not repeat the acceptance.

## Goal

Fix exactly the two missing mechanisms identified by acceptance so that a green publication cannot be indistinguishable from a fresh current-cycle publication when no fresh visual was built.

### A. Durable build freshness receipt

In the existing `Build daily visual payload` production workflow, emit one durable receipt for every ordinary invocation that records at minimum:
- `fresh_build: true|false`;
- explicit outcome when false, equivalent to `degraded/no_fresh_build` rather than implicit success;
- exact intended source/pre-AI cycle identity, including the canonical `history_snapshot.json` blob SHA plus the available source-cycle identity/timestamp;
- when `fresh_build=true`, exact produced `data/production/visual/current.json` blob SHA and canonical visual commit SHA;
- triggering workflow run identity sufficient for deploy binding.

A small JSON artifact/receipt is preferred. Do not introduce a second workflow or a new production data plane.

### B. Bind deploy to the exact triggering build receipt

Update the existing Pages deploy workflow so a `workflow_run` deployment consumes the receipt from that exact triggering build and verifies the staged canonical visual against it.

For a fresh build, require the staged payload to match the receipt's intended source cycle and produced visual blob/commit.

For `fresh_build=false`, the deploy path must expose an explicit degraded/no-fresh-build outcome and must not classify the publication as an ordinary fresh-cycle success.

A mismatched older `current.json` must never be accepted as fresh for the triggering cycle.

## Ownership and boundaries

Implementation ownership is limited to:
- `.github/workflows/build-daily-visual-payload.yml`
- `.github/workflows/deploy-visual.yml`
- one small freshness receipt/artifact contract and focused tests/helpers only if needed.

Do NOT:
- redesign the pipeline;
- create a second deploy workflow;
- weaken history/Taste/readiness gates;
- alter ranking or Taste semantics;
- manually regenerate production merely to force a pass;
- change unrelated UI;
- broaden into giveaway identity or semantic-runtime observability work.

Preserve existing canonical visual ownership and GitHub Pages deployment ownership.

## Required validation

Prove all three cases:
1. **Fresh path:** current source/history cycle -> fresh visual -> receipt -> exact deploy binding passes.
2. **No-build/degraded path:** prerequisite not ready / no fresh visual -> durable receipt says `fresh_build=false`; publication is explicitly degraded/no-fresh-build and cannot masquerade as fresh.
3. **Stale mismatch:** deploy sees an older/mismatched visual blob/commit than the triggering receipt -> fresh classification/deploy acceptance fails closed.

Also prove existing ordinary visual/deploy tests remain green where applicable.

Use bounded test/validation evidence. Do not perform broad workflow-run archaeology.

## Required result

Report:
1. exact implementation performed;
2. exact receipt schema/fields and ownership;
3. exact deploy binding behavior;
4. validation for fresh, degraded/no-build and stale-mismatch cases;
5. whether any production deployment was performed;
6. whether follow-up acceptance is ready now.

Status exactly one:
- `complete`
- `blocked`
- `needs_user_action`
- `needs_followup_fix`

## Completion

Save:
`reviews/worker_reports/visual-freshness-chain-fix-01.md`

Final answer must state exact report path, status and exact refs.
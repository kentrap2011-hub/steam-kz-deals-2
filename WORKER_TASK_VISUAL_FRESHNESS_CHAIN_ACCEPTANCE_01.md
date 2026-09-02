# WORKER TASK — VISUAL FRESHNESS CHAIN ACCEPTANCE 01

Task ID: `visual-freshness-chain-acceptance-01`
Mode: `ACCEPTANCE`
Report: `reviews/worker_reports/visual-freshness-chain-acceptance-01.md`

## Why this task exists

System Audit `reviews/system_audits/baseline-01.md` proved that a successful visual workflow/deploy chain does not necessarily prove that a fresh visual payload was rebuilt for the intended current production cycle. The build workflow can legitimately take a no-build path while remaining successful, and deploy may then publish the previously committed payload.

For a time-sensitive deal feed, a green deployment must not be indistinguishable from a fresh current-cycle publication if no fresh build happened.

## Read first

- `reviews/system_audits/baseline-01.md`
- `.github/workflows/build-daily-visual-payload.yml`
- `.github/workflows/deploy-visual.yml`
- `data/production/pre_ai/history_snapshot.json`
- `data/production/visual/current.json`
- the smallest exact run/artifact evidence needed to perform this acceptance

Do not perform broad Git-history archaeology.

## Goal

Determine whether the ordinary production chain can prove end to end:

`intended current source/pre-AI cycle -> fresh visual build -> canonical visual persistence -> Pages deployment of that same fresh cycle`

The acceptance must distinguish at minimum:
- fresh build and fresh deploy;
- intentional no-build/degraded path;
- deploy of an older canonical payload.

A successful workflow status alone is not sufficient proof of freshness.

## Required checks

1. Identify the current canonical cycle/freshness identifiers or timestamps available at each relevant stage.
2. Establish whether `build-daily-visual-payload.yml` explicitly records `fresh_build=true/false` or an equivalent durable signal when prerequisites are not ready.
3. Establish whether a successful `deploy-visual.yml` is cryptographically/semantically bound to the visual payload produced for the intended source cycle, or can deploy the prior committed payload without making that distinction explicit.
4. Determine whether current user-visible/operational acceptance can tell the difference between:
   - current fresh list;
   - successful deployment of stale/previous list.
5. Use a bounded current or recent run only if needed to prove the chain; do not perform broad run archaeology.

## Boundaries

Do NOT:
- redesign the production pipeline;
- alter ranking/Taste semantics;
- manually regenerate production just to force a pass;
- weaken prerequisite gates;
- create a second deploy workflow;
- make unrelated UI changes;
- implement a fix in this task unless an existing acceptance/freshness marker only needs a trivial activation explicitly already supported by canonical contracts. Otherwise localize the exact missing mechanism for a separate IMPLEMENT task.

## Required result

Report exactly:

1. `Fresh-cycle build proof`: `pass | fail | partial`
2. `Deploy-to-built-cycle binding`: `pass | fail | partial`
3. `Stale-success visibility`: `pass | fail | partial`
4. Exact evidence for each result.
5. If failed/partial, the smallest missing mechanism(s), no more than 2.
6. Whether an `IMPLEMENT` task is required.
7. One recommended next step only.

If implementation is required, specify the bounded implementation contract and exact ownership/files, but do not implement here.

## Completion

Save:
`reviews/worker_reports/visual-freshness-chain-acceptance-01.md`

Status exactly one:
- `complete`
- `needs_fix`
- `blocked`
- `needs_user_decision`

Final answer must state the exact report path and exact refs used.
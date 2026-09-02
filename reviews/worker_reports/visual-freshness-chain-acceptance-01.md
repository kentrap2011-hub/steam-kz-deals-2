# Visual Freshness Chain Acceptance 01

Task ID: `visual-freshness-chain-acceptance-01`  
Mode: `ACCEPTANCE`  
Status: `needs_fix`

## Required results

1. `Fresh-cycle build proof`: `fail`
2. `Deploy-to-built-cycle binding`: `fail`
3. `Stale-success visibility`: `fail`
4. `IMPLEMENT` task required: `yes`

This acceptance used bounded current canonical state plus the smallest recent commit evidence needed to identify the active source and visual cycles. No broad workflow-run or Git-history archaeology was required: the current canonical blob/commit relationships and the workflow control flow are sufficient to decide all three checks.

## Current cycle / freshness identifiers

| Stage | Identifier or timestamp currently available | Current evidence | Freshness limitation |
| --- | --- | --- | --- |
| Source / pre-AI cycle | source commit plus `source_mailing_updated_at_utc` in pre-AI state | commit `99ec326b27d06e2e8322729d0c3062b32c16c5ef` (`Refresh atomic pre-AI payload`) carries source mailing timestamp `2026-09-02T18:00:45.930255+00:00` | The visual/deploy workflows do not carry this exact source-cycle identity end to end. |
| History prerequisite | canonical file blob, readiness fields | `data/production/pre_ai/history_snapshot.json` blob `6aabd3e48b93e49ae0b71a3e5f33dc19347d1a23`; `status=complete`, `complete_coverage=true`, `primary_count=743`, `classified_count=743` | The snapshot has no durable publication receipt tying this exact blob to the later visual build/deploy. `persistent_cache_updated_at_utc` is a cache timestamp, not the source-cycle identifier. |
| Canonical visual | file blob plus producer provenance inside `production_contract` | current `data/production/visual/current.json` blob `4d71034840ca7bbf2133a0f7632b5c6180c52cf2`; its `production_contract.source_history_snapshot_blob_sha` is `f7120b05e6e92c25637e6b8c42fb593515940efc` | The declared source-history blob is not the current canonical history blob `6aabd3e...`; therefore the current visual cannot prove derivation from the current history/source cycle. |
| Canonical visual persistence | commit that last changed paid visual state | bounded visual-path history shows general visual commit `24b2890d0c85b14213fd0b91256afcfb306eb01e` at `2026-09-01T08:20:42Z`; later visual mutation `4e79f0efe951e86be4d05f791a585bbd44c917a3` at `2026-09-02T04:12:44Z` is `Refresh giveaway visual payload` | Giveaway-only refresh explicitly preserves the paid payload, so it is not proof that the paid list was rebuilt for the newer pre-AI cycle. |
| Pages deploy | successful triggering workflow plus whatever is on `main` at deploy checkout | `.github/workflows/deploy-visual.yml` checks out `ref: main` and copies `data/production/visual/current.json` to `web/data/current.json` | There is no source-cycle ID, triggering build receipt, produced visual blob SHA, or exact visual commit required by the deploy job. |

## 1. Fresh-cycle build proof — `fail`

### Exact evidence

- `.github/workflows/build-daily-visual-payload.yml` blob `2d56b81f822412c433852d55a749a4db8ce33b78` treats an unready/missing history prerequisite as a successful control-flow outcome. The `history` step writes `ready=false` and exits successfully (`SystemExit(0)`) rather than failing the job.
- The actual visual build step runs only when `steps.history.outputs.ready == 'true'`. If history is not ready, that step is skipped and there is no `built=true/false` value emitted by it for that run.
- Downstream visual validation, ranking review/lookup generation, and canonical visual commit are conditional on `steps.build.outputs.built == 'true'` (with the duration-cache exception on the commit step). Therefore the ordinary workflow can conclude successfully without creating a fresh visual payload.
- There is no durable, canonical `fresh_build=true|false` receipt (or equivalent) persisted for every ordinary production invocation. The existing `HISTORY_READY=false` text/output is run-local and does not become an end-to-end freshness contract.
- Current canonical state independently demonstrates why a source binding is necessary: current history blob is `6aabd3e48b93e49ae0b71a3e5f33dc19347d1a23`, while current visual declares `source_history_snapshot_blob_sha=f7120b05e6e92c25637e6b8c42fb593515940efc`.
- The bounded commit sequence is consistent with that mismatch: current pre-AI refresh commit `99ec326b27d06e2e8322729d0c3062b32c16c5ef` is from `2026-09-02T18:02:11Z`, while the last bounded general paid visual refresh is `24b2890d0c85b14213fd0b91256afcfb306eb01e` from `2026-09-01T08:20:42Z`; the later `4e79f0e...` visual mutation is giveaway-only and by contract preserves paid state.

### Acceptance conclusion

The chain cannot prove `intended current source/pre-AI cycle -> fresh visual build`. A green build workflow can mean either a fresh build or an intentional no-build path, and current canonical state has no durable receipt resolving that ambiguity.

## 2. Deploy-to-built-cycle binding — `fail`

### Exact evidence

- `.github/workflows/deploy-visual.yml` blob `625a22da18300795974ba6e3b46c6b92db1184d4` accepts a `workflow_run` trigger when `Build daily visual payload` concluded `success` on `main`.
- The deploy job then performs `actions/checkout@v4` with `ref: main`, not checkout of an exact visual commit identified by the triggering build.
- Its visual-scope classification finds the latest commit that touched `data/production/visual/current.json`, but that check only distinguishes `giveaway_only` from `general`; it does not prove that the visual commit was produced by the triggering run or from its intended source cycle.
- The Pages staging step simply copies the checked-out canonical file: `cp data/production/visual/current.json web/data/current.json`.
- The deploy job does not require or compare a triggering build `run_id` receipt, source/pre-AI cycle identifier, history blob SHA, produced `current.json` blob SHA, or exact canonical visual commit SHA.

### Acceptance conclusion

A successful deploy is not cryptographically or semantically bound to the visual payload produced for the triggering intended source cycle. After a successful no-build path, deploy can stage a previously committed `current.json` from `main` without distinguishing that from a fresh-cycle publication.

## 3. Stale-success visibility — `fail`

### Exact evidence

- The build log can contain `HISTORY_READY=false`, but the workflow can still conclude successfully; this is not a durable publication state and requires manual inspection of a particular run.
- The build workflow has no persisted ordinary-run classification equivalent to `fresh_build=true`, `fresh_build=false/degraded`, and `reused_previous_payload` that survives into deploy acceptance.
- The deploy workflow exposes `VISUAL_DEPLOY_SCOPE=general|giveaway_only`, which describes mutation scope, not freshness. A `general` deploy can still stage an older canonical payload when the triggering build produced none.
- The Pages artifact is assembled from the checked-out `current.json` and carries no deploy-time proof that its paid list belongs to the intended source cycle.
- Consequently, the operational green state and the user-visible feed do not reliably distinguish “current fresh list” from “successful deployment of previous list.” Current source/history-vs-visual provenance mismatch demonstrates that canonical timestamps/blobs alone do not currently close that gap.

### Acceptance conclusion

Stale-success is not explicitly visible as a first-class production outcome. Manual inference from separate logs/commits is possible, but ordinary acceptance cannot reliably distinguish it from a fresh publication.

## Smallest missing mechanisms

### 1. Durable build freshness receipt

**Owner:** `.github/workflows/build-daily-visual-payload.yml`

For every ordinary production invocation, emit one durable receipt tied to that workflow run containing at minimum:

- `fresh_build: true|false`;
- explicit outcome when false (`degraded/no_fresh_build` rather than implicit success);
- intended source/pre-AI cycle identity, at minimum the exact canonical `history_snapshot.json` blob SHA plus the available source-cycle identity/timestamp;
- when `fresh_build=true`, the exact produced `data/production/visual/current.json` blob SHA and canonical visual commit SHA.

A small run artifact (for example a single JSON freshness receipt) is sufficient; no ranking/Taste semantics or prerequisite gates need to change.

### 2. Deploy binding gate to the triggering build receipt

**Owner:** `.github/workflows/deploy-visual.yml`

For a `workflow_run` deployment, consume the exact receipt from the triggering `Build daily visual payload` run and verify that the staged canonical `current.json` matches the receipt's produced visual blob/commit and intended source cycle. If the receipt says `fresh_build=false`, the deploy path must classify that explicitly as degraded/no-fresh-build instead of treating it as indistinguishable from a fresh-cycle publication.

This is a bounded freshness/binding change only. It must not redesign the pipeline, weaken history/Taste gates, create a second deploy workflow, or alter ranking semantics.

## IMPLEMENT task required

`yes`

Bounded implementation contract is limited to the two mechanisms above and is owned by:

- `.github/workflows/build-daily-visual-payload.yml`
- `.github/workflows/deploy-visual.yml`
- one small generated build-run freshness receipt artifact/JSON contract if needed by those workflows

No production regeneration is required for implementation itself; the follow-up acceptance should exercise or inspect one normal fresh path and one explicit no-build/degraded path, and must reject a mismatched older visual blob as fresh.

## Recommended next step

Create one bounded `IMPLEMENT` task that adds the durable build freshness receipt and makes `deploy-visual.yml` verify that exact triggering-run receipt before classifying a Pages publication as fresh; then rerun this acceptance against the fresh, no-build/degraded, and stale-mismatch cases.

## Exact refs used

- `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_ACCEPTANCE_01.md` — blob `ef4a0d56d77efd0aa0015d03c87bd6b586f47947`
- `reviews/system_audits/baseline-01.md` — blob `5d3abfd95e84205b999329aa30bc806687d8b9cf`
- `.github/workflows/build-daily-visual-payload.yml` — blob `2d56b81f822412c433852d55a749a4db8ce33b78`
- `.github/workflows/deploy-visual.yml` — blob `625a22da18300795974ba6e3b46c6b92db1184d4`
- `data/production/pre_ai/history_snapshot.json` — blob `6aabd3e48b93e49ae0b71a3e5f33dc19347d1a23`
- `data/production/visual/current.json` — blob `4d71034840ca7bbf2133a0f7632b5c6180c52cf2`
- current bounded pre-AI/source commit — `99ec326b27d06e2e8322729d0c3062b32c16c5ef`
- bounded last general visual commit — `24b2890d0c85b14213fd0b91256afcfb306eb01e`
- bounded latest visual mutation (giveaway-only) — `4e79f0efe951e86be4d05f791a585bbd44c917a3`

No workflow-run archaeology was used because the current canonical provenance mismatch plus the encoded workflow control flow already prove the acceptance failures.

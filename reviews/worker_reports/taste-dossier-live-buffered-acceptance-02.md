# Taste Dossier Live Buffered Acceptance 02

- Task ID: `taste-dossier-live-buffered-acceptance-02`
- Mode: `ACCEPTANCE`
- Date: `2026-09-15`
- Verdict: **BLOCKED**

## Acceptance result

The PASS criterion was **not** reached.

The single user-started Scheduled Task invocation published **0 buffered groups**, created **0 dossier artifacts**, and claimed **0 canonical progress**. Therefore this invocation did not exercise, and cannot prove, the required live behavior of publishing at least two consecutive immutable buffered groups with group `N+1` published without waiting for canonical durable acceptance of group `N`.

This is recorded as **BLOCKED**, not PASS and not an architecture rejection: the activation contracts were aligned at start, but the live Scheduled Task invocation stopped before dossier publication because its available GitHub reader/runtime could not safely resolve the current immutable group descriptor from the large canonical manifest.

## Pre-run GitHub baseline

Baseline was captured before asking the user to run the Scheduled Task.

- Repository: `kentrap2011-hub/steam-kz-deals-2`
- `main` head: `170e5e916dbb5f2dcb7d1e330353acd9d8352c97`
- Snapshot ID: `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`
- Prepared required count: `594`
- Completed required count: `0`
- Remaining required count: `594`
- Immutable submission group count: `60`
- Canonical expected sequence: `1`

### Immutable group 1

- sequence: `1`
- start index: `0`
- end index: `9`
- group hash: `74000acf375f0f0647b09d3726e6e5b37c1953f21543527027b9d61ccf7d7d06`
- appids: `2378500, 1000360, 404680, 3353000, 2821400, 292030, 3017860, 2793760, 2577660, 2167580`
- expected deterministic artifact:
  `data/ai_inbox/taste_steam_review_dossiers/c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3--g000001--74000acf375f0f0647b09d3726e6e5b37c1953f21543527027b9d61ccf7d7d06.json`

### Immutable group 2

- sequence: `2`
- start index: `10`
- end index: `19`
- group hash: `f8646b55450b4b4fe988bdf1a8a3348be4f794461bdc30699be2393095ae5f8a`
- appids: `2124490, 3991810, 3590240, 3289400, 3365090, 1465360, 2456790, 3527290, 2670780, 2677070`
- expected deterministic artifact:
  `data/ai_inbox/taste_steam_review_dossiers/c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3--g000002--f8646b55450b4b4fe988bdf1a8a3348be4f794461bdc30699be2393095ae5f8a.json`

Both target artifacts were absent at baseline. The dossier inbox directory itself was absent.

Relevant pre-AI workflow evidence at baseline included GitHub Actions run `34936045981`, `Build pre-AI deterministic payload`, completed successfully for head SHA `fd3479266749f8b079fcfbc9fab981524706f252`.

## Contract / bridge / worker prompt alignment

Pre-run review found the three required layers aligned:

- `config/taste_steam_review_dossier_contract.json` marks buffered submission/drain as active.
- `config/taste_steam_review_dossier_persistence_bridge.json` selects `buffered_group_create_only_v1` as the active transport and activates state-based contiguous drain.
- `config/taste_steam_review_dossier_worker_prompt.md` allows the worker, after successfully publishing group `N`, to publish group `N+1` in the same invocation **without waiting for canonical acceptance of group `N`**.
- Legacy checkpoint behavior remains fallback only; it was not the active publication gate.

Therefore the acceptance start gate was safe from the contract-consistency perspective.

## Manual invocation

The user confirmed one manual `Run now` invocation. No second Scheduled Task run was requested or performed by this acceptance task.

The invocation returned a tool/runtime blocker before dossier work. Its reported sequence was:

1. It loaded the aligned active buffered contracts.
2. It loaded canonical snapshot `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`.
3. Its available GitHub reader truncated the large manifest before returning `submission_group_plan` and the GitHub-owned canonical expected sequence.
4. A repeated blob/raw read was also truncated in that runtime.
5. The contract forbids deriving or guessing an immutable group from `ordered_appids`, `current_checkpoint_items`, checkpoint size, or other reconstructed state.
6. It therefore stopped before publication rather than fabricating a group descriptor.

Reported invocation outcome:

- published buffered groups: `0`
- dossier artifacts created: `0`
- canonical progress claimed: `0`

The acceptance observer was later able to recover the baseline immutable descriptors through a different bounded read path. That does not retroactively make the Scheduled Task invocation successful: the live invocation had already stopped and no publication occurred.

## Post-run durable GitHub evidence

Bounded post-run checks confirmed:

- deterministic group-1 artifact: **absent**
- deterministic group-2 artifact: **absent**
- dossier inbox directory: **absent**
- snapshot ID: unchanged
- prepared / completed / remaining: unchanged at `594 / 0 / 594`
- no canonical dossier progress was produced by the invocation
- GitHub-owned contiguous ingestion was therefore not exercised by this invocation

A particularly strong ordering check came from the acceptance observer's first later repository write: its commit had parent exactly equal to the pre-run baseline `170e5e916dbb5f2dcb7d1e330353acd9d8352c97`. Thus there was no intervening repository commit from the Scheduled Task between the captured baseline and the observer's post-run reporting activity.

Because group 1 was never published, there is no live evidence for the required second-group property. In particular, this run cannot demonstrate that group 2 was published before canonical acceptance of group 1.

## Verdict rationale

**BLOCKED**.

The live invocation encountered a tool/runtime read limitation before it could safely resolve the authoritative immutable group descriptor. Stopping was contract-compliant because descriptor reconstruction or guessing is forbidden.

The acceptance therefore does **not** prove the buffered live path. The core PASS condition remains unvalidated in live runtime:

> one Scheduled Task invocation must publish at least two consecutive buffered groups, with the second published without waiting for canonical durable acceptance of the first.

This is not recorded as an architecture mismatch because the contract, persistence bridge, and worker prompt were aligned before the run.

## Constraints preserved

During the acceptance interval:

- Scheduled Task UI was not searched or inspected by the acceptance observer.
- The observer did not press `Run now`.
- No manual GitHub workflow dispatch was performed.
- No second Scheduled Task invocation was requested.
- No runtime/config/code change was made for acceptance.
- Taste Semantic Producer was not changed.

## Acceptance-observer tooling incident

After the Scheduled Task had already returned the BLOCKED result, while preparing this durable report, the acceptance observer made an accidental GitHub write to temporary path `x` and also created branch `noop-check`. The temporary file `x` was subsequently deleted. The required report path was also initially created with placeholder content and is replaced by this final report.

These observer-side writes occurred **after** the live acceptance interval. They did not alter the Scheduled Task result, canonical dossier progress, runtime/config/code, production limits, or Taste Semantic Producer. The accidental `noop-check` branch does not alter `main`; no safe branch-delete capability was available through the connected GitHub tool during this acceptance, so that branch is disclosed here rather than hidden or manipulated through an unapproved workaround.

Final `main` tree verification should therefore be evaluated against the baseline by content: the temporary `x` path is absent, and the intended durable acceptance report is the only acceptance artifact meant to remain on `main`.
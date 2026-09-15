# Taste Dossier Web Evidence Activation + Recovery 01

- Date: `2026-09-15`
- Mode: `IMPLEMENT`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Final status: `complete_ready_for_live_web_evidence_acceptance`

## Scope

Activate the already-reviewed web-evidence redesign in PR #30, verify the automatic post-merge production-preparation path, preserve canonical ownership boundaries, recover the legacy invalid deterministic blocker only through the existing GitHub-owned recovery interface, and leave the system ready for a new V2 group 1 without running the production Scheduled Task.

No separate task file was used; the chat instructions were the complete task.

## Architecture preflight

Preflight was performed against:

- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `PROJECT_DECISIONS.md`, especially TASTE-007
- `reviews/worker_reports/taste-dossier-web-evidence-redesign-01.md`
- `reviews/worker_reports/taste-dossier-non-review-defect-repair-01.md`
- `reviews/worker_reports/taste-dossier-full-defect-sweep-01.md`
- `config/taste_steam_review_dossier_recovery_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/execution_ownership_contract.json`
- current worker schema / worker prompt / compact worker-view files.

Verdict: activation and recovery are architecture-safe.

GitHub remains the control plane for exact scope, immutable group identity/order, validation, canonical progress, persistence, drain/reconciliation, stale cleanup and recovery. The Scheduled ChatGPT worker remains evidence-only. This task did not introduce a new queue, scheduler, retry loop, quota, alternate filename scheme or worker-owned progress mechanism.

The recovery contract permits quarantine only for the exact current expected deterministic artifact after canonical validator failure, preserves later pending groups and forbids canonical progress advancement. Those constraints were followed exactly.

## PR #30 verification and merge

PR #30 was re-verified before merge.

- PR: `#30`
- Head SHA: `a7ed4b239cf0a9c75f65bba19c96cead472ff0af`
- Scope: the same 14-file web-evidence redesign previously reviewed; no unrelated expansion was found.
- Required PR CI: `Validate buffered Steam review dossier runtime`
- PR CI run ID: `34996981923`
- PR CI result: `success`
- Mergeability was recalculated as clean before write.
- Merge method: normal GitHub merge.
- **PR #30 merge commit:** `4a3240cc2d2658ef1b4a6eb5e45aaae1560bd043`

No force merge or bypass was used.

## Automatic post-merge workflows

The merge triggered the expected automatic workflows. No manual production workflow dispatch was used.

| Run ID | Workflow | Trigger | Result |
|---|---|---|---|
| `35000250927` | `Build pre-AI deterministic payload` | automatic post-merge push | `success` |
| `35000250986` | `Validate execution ownership` | automatic post-merge push | `success` |

The automatic pre-AI writer produced bot commit:

- `5afe2e0d13e3cf95f53600dd0fab9a15275ee4f2`

The pre-AI logs explicitly reported same-day snapshot preservation plus `web_evidence_binding_added=true`.

Its reconciliation did not accept the old invalid group 1:

- `accepted_groups=0`
- `accepted_dossiers=0`
- blocked reason: `invalid_expected_group`

Therefore activation itself did not advance canonical progress through an invalid dossier.

## Active V2 bindings

After the post-merge writer completed, the current canonical work manifest binds:

- work manifest schema: `TASTE-STEAM-REVIEW-DOSSIER-WORK-V2`, version `2`
- evidence contract: `TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V1`, version `1`
- worker schema: `TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2`, version `2`
- dossier schema: `TASTE-STEAM-REVIEW-DOSSIER-V2`, version `2`
- worker prompt revision: `web-evidence-v1`

The current worker prompt makes the old Steam-only `sampling_policy` fields that remain in the compact index inactive compatibility metadata; they are not authority to perform the legacy Steam-lane/cursor workflow.

TASTE-007's web-evidence architecture is therefore active in the canonical GitHub bindings, not merely present as unreferenced files.

## Live Scheduled Task prompt binding

No Scheduled Task UI was searched or changed.

The already-prepared live buffered Scheduled Task wrapper is intentionally stable: at the start of every invocation it reads the latest `config/taste_steam_review_dossier_worker_prompt.md` from branch `main` and treats that repository file as authoritative. Because PR #30 changed that canonical repository worker prompt to revision `web-evidence-v1`, a second manual prompt replacement is **not required** for V2 activation.

This conclusion does not depend on inspecting the live UI and does not transfer any control-plane responsibility to the Scheduled Task.

## Snapshot / progress before and after

The same-day preservation rule correctly retained the existing daily snapshot while adding the V2 web-evidence binding.

### Before PR #30 merge

- snapshot ID: `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`
- prepared required: `594`
- completed required: `0`
- remaining required: `594`
- canonical expected sequence: `1`
- group count: `60`
- active inbox contained the legacy deterministic group 1 and group 2 artifacts.

### After V2 activation and canonical recovery

- snapshot ID: `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`
- prepared required: `594`
- completed required: `0`
- remaining required: `594`
- canonical expected sequence: `1`
- group count: `60`
- `full_backlog_complete=false`

Canonical progress is therefore unchanged at `594 / 0 / 594`. No invalid legacy dossier was counted as complete.

## Recovery of old invalid g1 / g2

### Why stale cleanup was not used

The active snapshot remained the same same-day snapshot. Legacy group 1 was still the exact current deterministic sequence-1 blocker, so it was not a stale/superseded artifact eligible for stale cleanup. The authorized invalid-expected recovery path was therefore the canonical mechanism.

### Legacy group 1

A single canonical recovery request was created at the contract-defined request path, targeting only:

`data/ai_inbox/taste_steam_review_dossiers/c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3--g000001--74000acf375f0f0647b09d3726e6e5b37c1953f21543527027b9d61ccf7d7d06.json`

Recovery request commit:

- `ee07128385a3868085c467ccf93d69deb45ba5ad`

That request automatically triggered the existing GitHub-owned checkpoint/recovery workflow:

- run ID: `35000521022`
- workflow: `Ingest Steam review dossier checkpoint`
- trigger: push of the canonical recovery request, not manual workflow dispatch
- result: `success`

The workflow's strict V2 validator rejected legacy g1 because it was missing required V2 fields:

- `game_identity`
- `evidence`

The workflow then quarantined that exact current expected artifact under the canonical `invalid_expected` quarantine path and removed the one-shot request through its normal recovery transaction.

Recovery bot commit:

- `13c9f799b70165f08c3ebd99422a9fe7d281b12f`

The durable recovery audit records:

- action: `quarantine_invalid_expected`
- sequence: `1`
- `canonical_progress_advanced=false`
- completed before: `0`
- remaining before: `594`
- validator error: `dossier is missing required fields: game_identity, evidence`

No alternate retry filename was created in the active inbox and the artifact was not manually deleted.

### Legacy group 2

Legacy group 2 remains in the active inbox at its original deterministic path:

`data/ai_inbox/taste_steam_review_dossiers/c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3--g000002--f8646b55450b4b4fe988bdf1a8a3348be4f794461bdc30699be2393095ae5f8a.json`

This is intentional canonical behavior. The recovery contract preserves later pending groups; sequence 2 was not the current expected artifact and therefore could not be quarantined through `quarantine_invalid_expected` at this state. It was not eligible for same-day stale cleanup either.

With canonical expected sequence still `1`, the old g2 is later-pending/inert for creation of the new V2 group 1. If it later becomes the current deterministic blocker, the same GitHub-owned recovery contract remains the only permitted recovery route.

## Proof that invalid dossiers did not advance progress

There are three independent durable checks:

1. The automatic post-merge reconciliation accepted `0` groups and `0` dossiers when it encountered invalid legacy g1.
2. The recovery audit explicitly records `canonical_progress_advanced=false`.
3. The current compact worker index remains `prepared/completed/remaining = 594 / 0 / 594` with `canonical_expected_sequence=1`.

Therefore neither invalid g1 nor legacy g2 advanced canonical progress.

## Readiness for live web-evidence acceptance

The system is unblocked for a **new V2 group 1**:

- V2 schema / web-evidence contract / prompt revision are active in the current work binding.
- canonical expected sequence is `1`.
- the deterministic active-inbox path for g1 is free because the invalid legacy g1 was canonically quarantined.
- progress remains at zero completed dossiers.
- the live Scheduled Task wrapper reads the current repository worker prompt at invocation start, so no prompt UI edit is required for `web-evidence-v1`.

This is readiness for live acceptance, not a claim that a live V2 dossier has already been produced or accepted.

## Negative confirmations

- Production Scheduled Task `Taste Steam Review Dossier` **Run now was not executed** in this task.
- Scheduled Task UI was **not searched, inspected or modified**.
- No manual production workflow dispatch was performed.
- Recovery was invoked only through the contract-defined GitHub recovery request interface and its automatic push-triggered workflow.
- No dossier was manually authored.
- No new raw review bodies were generated or added by this task. Canonical recovery only moved a pre-existing legacy invalid artifact to quarantine.
- No alternate retry artifact was created.
- Invalid dossiers did not advance canonical progress.
- `Taste Semantic Producer` was **not changed**: no producer prompt, schedule, limits, queue/state ownership, pin authority or behavior was modified.

## One next step

Run a dedicated **LIVE WEB EVIDENCE ACCEPTANCE** against the now-unblocked current sequence 1, with any production Scheduled Task invocation performed only under that separate acceptance step and not as part of this activation/recovery task.

## Final status

`complete_ready_for_live_web_evidence_acceptance`

# WORKER TASK — PIN TASTE PROFILE FOR FULL BATCH LIFECYCLE

## Task ID
`taste-pinned-profile-batch-lifecycle-fix-01`

## Mode
`IMPLEMENT / BOUNDED ARCHITECTURE FIX`

## Expected report
`reviews/worker_reports/taste-pinned-profile-batch-lifecycle-fix-01.md`

## User authorization
The user explicitly approved fixing the architecture so they may continue updating `gaming_taste_live.json` in parallel without invalidating a Taste batch that already started on an earlier correctly pinned profile.

## Goal
Make the immutable profile selected at the start of an authorized Taste work-unit remain authoritative for that exact work-unit through semantic evaluation, validation, ingest, post-ingest verification, and durable commit.

A later live-profile update must apply to the NEXT newly prepared Taste work-unit, not retroactively invalidate an already-started correctly pinned work-unit.

This must NOT become a way to accept arbitrary stale results. Acceptance must require proof that the exact profile revision was durably pinned to the exact authorized work-unit before semantic execution.

## Relevant predecessor evidence
Read only as needed:
- `reviews/worker_reports/taste-existing-batch-retry-01.md`
- `reviews/worker_reports/taste-manual-throughput-drain-01.md`
- `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`
- `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`

Known current failure pattern:
- batch generated/submitted against profile blob `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`;
- live profile later advanced to `08d569b56ea62f7ec1297320450db24073bbbd38`;
- ingest rejected solely because it compared the batch to the newer live profile;
- no row-level fingerprint/context identity mismatch was reported.

## Mandatory report-first rule
The FIRST repository mutation after reading this task must be creation of the expected report with:
- lifecycle: `in_progress`;
- current UTC;
- implementation_status: `not_started`;
- next_action: inspect exact work-unit/profile-binding and ingest validation paths.

Commit immediately. If report persistence fails, STOP.

## Required invariant
For every Taste semantic work-unit:

1. Producer resolves the current live profile at work-unit creation using the existing immutable live-profile freeze rules.
2. Producer durably records the exact authorized work-unit identity together with the exact pinned profile identity BEFORE semantic execution. At minimum preserve the existing canonical profile commit/blob/SHA256/byte identity and the exact ordered work-unit identities/hash plus existing model/semantics/context/fingerprint invariants.
3. Semantic results must bind exactly to that pinned work-unit/profile.
4. Ingest must validate against the durable pinned profile/work-unit authority, not against whatever newer live profile happens to exist at ingest time.
5. If live profile changes after work-unit pinning, the in-flight pinned work-unit remains valid if every other exact binding/invariant still matches.
6. After that work-unit is committed or abandoned under canonical recovery rules, any NEW work-unit must resolve/freeze the then-current live profile; it must not silently reuse the prior pinned profile.
7. A result that was never durably pinned before semantic execution, or whose work-unit/profile identity cannot be proven, must still fail closed.

## Scope of implementation
Inspect and change only the exact paths necessary to enforce the invariant, likely including:
- producer/work-unit preparation or checkpoint state that owns immutable profile pinning;
- `scripts/process_taste_inbox.py` / `ingest_taste_results.py` binding validation as directly required;
- `config/taste_checkpoint_contract.json`, `config/taste_result_contract.json`, `config/taste_validation_contract.json`, or execution ownership contract only where required to make authority explicit;
- focused tests/fixtures.

Reuse existing canonical work-unit/checkpoint machinery. Do not introduce a second queue, external database, local authority, or ChatGPT-maintained state.

## Critical safety distinction
The system must distinguish:

### Valid in-flight pinned batch
- exact work-unit was canonically prepared;
- exact profile revision was durably pinned BEFORE semantic execution;
- exact ordered subjects/fingerprints/context/model/semantics bindings match;
- live profile advanced only AFTER the pin.

This batch MAY remain acceptable through ingest under its pin.

### Unproven/arbitrary stale batch
- no durable pre-semantic work-unit/profile pin can be proven; or
- ordered work-unit identity differs; or
- profile/model/semantics/context/fingerprint binding differs; or
- canonical recovery/invalidation rules say the work-unit was superseded/abandoned.

This batch MUST fail closed even if its old profile can still be fetched from history.

Do not weaken this distinction.

## Existing 10-result package
The existing file:
`data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`

must NOT be edited, regenerated, or ingested in this implementation task.

However, determine from durable predecessor state whether its exact batch/profile was in fact pinned before semantic execution strongly enough to satisfy the new canonical invariant.

Report one of:
- `existing_batch_provably_grandfatherable_under_pinned_work_unit_rule`
- `existing_batch_not_provably_pinned_requires_regeneration`
- `existing_batch_status_uncertain`

Do not accept it during this task.

## Tests required
Add focused tests proving at least:
1. profile A pinned before semantic execution; live advances to profile B before ingest; exact A-bound result is accepted against durable A pin;
2. new work-unit created after live advances uses B, not A;
3. arbitrary old A-bound result with no matching durable active/pinned work-unit is rejected;
4. mismatched ordered work-unit identity/fingerprint/context/model/semantics remains rejected;
5. existing strict V5/result-count/order/duplicate/fail-closed protections remain active.

Run the narrowest relevant suite plus directly affected ingest/checkpoint tests.

## Preserve unchanged
- GitHub remains canonical authority;
- producer chooses candidates/order, never semantic ChatGPT;
- generation 2 and V5 contracts;
- exact fingerprint/context/model/semantics checks;
- normalized Taste factors/evidence rules;
- price-blind/no commercial evidence/no review sentiment as Taste evidence;
- atomic ingest and exact post-ingest verification;
- bounded retry for same exact work;
- one producer identity / one Scheduled Task;
- user does NOT need a quiet window or pause profile updates;
- no paid API/service/external scheduler.

## Not authorized
- do not run semantic Taste;
- do not ingest the existing 10 results;
- do not start next 10 games;
- do not modify Scheduled Task or cadence;
- do not change candidate-selection/business logic;
- do not weaken validation to `accept any historical profile`;
- do not manually mutate queue/cache/production data.

## Self-diagnosis
If implementation or tests cannot complete, obey `WORKER_REPORT_DURABILITY_PROTOCOL.md`: diagnose the first real failure/root cause in the same report before returning control, without unauthorized repair/retry expansion.

## Finish
Final status must be one of:
- `complete_pinned_profile_lifecycle_fix_ready_for_acceptance`
- `needs_followup`
- `blocked`

If complete, report:
- exact files changed;
- exact durable authority used for the pinned work-unit/profile;
- exact ingest validation change;
- tests and results;
- proof that a later live-profile update cannot invalidate a correctly pinned in-flight batch;
- proof that arbitrary stale historical results still fail closed;
- disposition of the existing 10-result package under the new invariant;
- confirmation no semantic run, ingest, next batch, queue mutation, or Scheduled Task mutation occurred.

Then STOP and return control to Director.

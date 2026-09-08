# taste-stale-inbox-repair-01

## Task
Confirm and minimally repair the stale Taste inbox blocker, preserve the historical generation-1 artifact, and re-ingest the already-produced Chernobylite generation-2 result through the canonical ingest path without semantic rerun, another game, another Scheduled Task, mass analysis, or weakened producer validation.

## Status
`needs_followup`

## Final outcome
The stale historical generation-1 file was confirmed as the original whole-inbox blocker and was repaired correctly without weakening safety. It is preserved as history outside the active inbox, its active copy is removed, and the canonical GitHub ingest workflow now passes the producer fence on the existing Chernobylite generation-2 file.

Chernobylite was **not accepted**, because after the stale-file blocker was cleared the normal later ingest validation detected an independent freshness failure: the current canonical taste-profile blob changed after the Chernobylite result had been produced. Accepting that result now would require bypassing or falsifying a mandatory binding check, which this task explicitly forbids.

Per `WORKER_TASK_TASTE_STALE_INBOX_REPAIR_01.md`, this is a required STOP condition: when the same existing Chernobylite result is stale/invalid for an unrelated reason, the worker must finish as `needs_followup` and must not rerun semantic ChatGPT analysis, choose another game, create another Scheduled Task, or widen production.

## Verified original root cause
- The active Taste producer contract is `TASTE-SEMANTIC-RESULT-V5` with producer `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`, generation `2`, and fail-closed mismatch policy.
- `.github/workflows/ingest-taste-batch.yml` executes the producer fence over `data/ai_inbox/taste` before transactional ingest.
- `scripts/taste_producer_fence.py::validate_taste_inbox()` scans every top-level `data/ai_inbox/taste/*.json` and rejects the run on an invalid producer envelope.
- Before repair the active inbox contained the historical generation-1 file `canary-App_10150-producer-g1.json` alongside `canary-app-1016800-gen2.json`.
- Prior canonical run `34260132159` failed on that historical generation-1 file before the Chernobylite ingest transaction.

Therefore the old generation-1 file was definitively the blocker of the earlier attempt.

## Architecture preflight
- Queue scope, validation, persistence, and inbox ingest remain owned by GitHub/GitHub Actions under `config/execution_ownership_contract.json`.
- Canonical authorization remains `config/taste_result_contract.json` plus the existing GitHub-owned ingest workflow.
- No control-plane work was moved to this interactive chat or to a new ChatGPT runtime path.
- No new recurring stage, queue, retry loop, quota, scheduler, producer identity, backlog manager, or Scheduled Task was introduced.

## Historical-artifact lifecycle repair
No pre-existing Taste archive/quarantine location existed in the current active inbox layout, so the smallest explicit lifecycle boundary was added outside the active inbox:

- archive policy: `data/ai_archive/taste/README.md`;
- preserved historical artifact: `data/ai_archive/taste/generation-1/canary-App_10150-producer-g1.json`;
- removed active copy: `data/ai_inbox/taste/canary-App_10150-producer-g1.json`.

The archive policy states that only `data/ai_inbox/taste/*.json` is active. Archived artifacts remain provenance only. Moving a stale artifact to the archive does not make that producer valid: if the same old/wrong producer artifact is placed back into the active inbox, the normal producer fence must reject it.

## Safety regression
Focused regression was added to `scripts/validate_taste_producer_fence.py` without changing the acceptance logic in `scripts/taste_producer_fence.py`.

Canonical workflow run `34267795151`, job `102201457478`, proved:
- correct current producer accepted: PASS;
- archived stale historical content excluded from active scan: PASS;
- active old-generation producer still rejected: PASS;
- active malformed JSON still rejected: PASS;
- normalized Taste factor contract: PASS;
- transactional proof regression: PASS;
- active inbox producer gate over only `canary-app-1016800-gen2.json`: PASS.

This proves the stale-file repair did not weaken current producer safety.

## Canonical re-ingest of the SAME Chernobylite result
Removing only the already-preserved historical active copy triggered the existing canonical workflow automatically. No new Chernobylite semantic analysis was run and no replacement game was selected.

Canonical attempt:
- workflow run: `34267795151`;
- job: `102201457478`;
- head SHA: `440efa3f0bc61d8b70cbda011d99dd5d16d67965`;
- input: existing `data/ai_inbox/taste/canary-app-1016800-gen2.json`.

The producer fence passed and explicitly validated only that Chernobylite file. The later normal ingest step then rebuilt current inputs and rejected the existing result with:

`Ingest binding mismatch for profile_blob_sha: input='c42a6a5dcf608e04bf86d24be9e1542f1b934456' current='b0d595c1699c70daa7c27c4b9fe0d9fdfd906ce2'`

The binding that changed is the canonical taste profile; model and semantic-contract bindings remained current in the same run. This is unrelated to the removed historical producer file.

## Post-attempt state
- Active Taste inbox now contains only `data/ai_inbox/taste/canary-app-1016800-gen2.json`; the generation-1 file is no longer active.
- Chernobylite `App_1016800` remains in `data/production/pre_ai/chatgpt_taste_queue.jsonl` with the same taste fingerprint and candidate-context digest; the queue therefore did **not** advance for this result.
- The failed workflow did not commit an acceptance transaction or remove the Chernobylite inbox file.
- `data/cache/taste_ingest_receipts/latest_runtime_status.json` still reports the previous accepted semantic batch from `2026-09-01`; no successful Chernobylite acceptance was written.

Chernobylite must therefore **not** be described as accepted.

## Containment verification
- ChatGPT semantic analysis rerun: **NO**.
- Different/replacement game selected: **NO**.
- New Scheduled Task created: **NO**.
- Existing Scheduled Task modified by this worker: **NO**.
- Mass analysis started: **NO**.
- Safety/binding checks weakened or bypassed: **NO**.
- System Audit started: **NO**.
- Next worker task started: **NO**.

## Changed paths
- `reviews/worker_reports/taste-stale-inbox-repair-01.md`
- `data/ai_archive/taste/README.md`
- `data/ai_archive/taste/generation-1/canary-App_10150-producer-g1.json`
- `scripts/validate_taste_producer_fence.py`
- removed active copy: `data/ai_inbox/taste/canary-App_10150-producer-g1.json`

## Implementation references
- report created before implementation: `6c65eedfb39ad3668b2153aae5e75a04498940fe`
- root-cause checkpoint: `cf25ea2bc2ffdad852e0fa7fbf36e1b6c91e2aa8`
- archive lifecycle README: `4de393be585f2e73cf0f89ec45c0f43a770d84b3`
- preserved historical file: `37b7fecb7de41b7be4e2432c0feb1744438db391`
- focused producer/archive regression: `ff3b80831459045eb9c403a5c85bc5904225abc7`
- active stale-file removal / canonical re-ingest trigger: `440efa3f0bc61d8b70cbda011d99dd5d16d67965`

## Validation summary
- Original stale generation-1 blocker confirmed: PASS.
- Historical artifact preserved before active removal: PASS.
- Historical artifact removed from working/active inbox: PASS.
- Active old-generation producer remains rejected: PASS.
- Malformed active input remains rejected: PASS.
- Existing Chernobylite result passed current producer fence: PASS.
- Same Chernobylite result sent through ordinary canonical acceptance mechanism: PASS.
- Chernobylite accepted: **FAIL — mandatory current-profile binding mismatch**.
- Queue advanced for Chernobylite: **NO**.
- Exact acceptance receipt created: **NO**.

## Follow-up required
A future task must obtain a Chernobylite result bound to the then-current canonical profile and submit it through the same existing canary/canonical path. That semantic rerun is intentionally **not** performed here because this task explicitly forbids rerunning ChatGPT analysis and requires `needs_followup` when the existing result is stale for an unrelated reason.

Do not use another game as a substitute and do not weaken the profile-binding guard.

## Efficiency / reusable lesson
Historical producer artifacts must never remain in an active whole-directory inbox. Preserve them outside the active glob and regression-test both sides of the lifecycle boundary: archived evidence is ignored as inactive, while identical stale/malformed evidence remains fail-closed if returned to the active inbox.

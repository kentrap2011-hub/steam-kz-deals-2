# WORKER TASK — TASTE CURRENT-LIVE PROFILE BINDING FIX 01

## Task ID
`taste-current-live-profile-binding-fix-01`

## Mode
`IMPLEMENT`

## Dispatch state
`PREPARED — DO NOT START WITHOUT EXPLICIT USER IMPLEMENT APPROVAL`

## Expected report
`reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`

## Goal
Fix only the proven blocker from the first real Chernobylite acceptance attempt: the lightweight current-main one-AppID preparation currently reuses a stale committed Taste profile binding instead of binding its exact prepared tuple to the then-current canonical live `gaming_taste_live.json`.

After this task, a read-only preparation for AppID `1016800` must be able to prove an exact current-live profile binding without semantic execution, canonical ingest, Scheduled Task mutation, manual SHA substitution, or broad production rebuild.

This task is NOT the real semantic canary.

## Immediate predecessor / proven blocker
Read first:
- `reviews/worker_reports/taste-chernobylite-real-canary-execute-01.md`
- `reviews/worker_reports/taste-current-main-canary-path-implement-01.md`

The first real acceptance attempt stopped correctly before semantic execution because:
- prepared profile blob SHA was `191b6d6c5dec2f9ef2976517f301528740f9bec2`;
- then-current live profile blob SHA was `9c9ef7cdf2d705b8dd10196cec654f16e04341e4`;
- exact equality failed;
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` was not mutated or triggered;
- semantic results and ingest attempts were both zero.

Do not repeat the same acceptance attempt until this binding route is fixed and independently validated.

## Required reading
1. Current `main`.
2. `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md`.
3. `WORKER_REPORT_DURABILITY_PROTOCOL.md`.
4. `WORKER_ANTI_STALL_PROTOCOL.md`.
5. `DIRECTOR_TASK_BOARD.md`.
6. `WORKER_TASK_TASTE_CURRENT_MAIN_CANARY_PATH_IMPLEMENT_01.md`.
7. `reviews/worker_reports/taste-current-main-canary-path-implement-01.md`.
8. `WORKER_TASK_TASTE_CHERNOBYLITE_REAL_CANARY_EXECUTE_01.md`.
9. `reviews/worker_reports/taste-chernobylite-real-canary-execute-01.md`.
10. Only the exact current one-AppID harness/workflow and canonical profile-binding contracts/routes needed for this fix.

Do not perform broad Git/Actions/history archaeology.

## Architecture preflight
Before changing code/workflow, prove from current canonical contracts:
- GitHub remains the control plane for deterministic preparation/binding validation;
- the existing scheduled ChatGPT task remains the only semantic producer;
- this fix does not create a second queue, scheduler, writer, retry loop, cache authority, or semantic runtime;
- the canonical live profile authority remains `kentrap2011-hub/stopgame-ratings-data:gaming_taste_live.json`.

If the current contracts do not permit a safe current-live binding route, stop `blocked` and explain the exact contract gap instead of inventing one.

## Required implementation
Make the smallest safe change to the existing lightweight one-AppID preparation so the exact tuple can be bound to the then-current canonical live Taste profile rather than an older source-aligned committed snapshot.

The implementation must:
1. Resolve/fetch the canonical live `gaming_taste_live.json` through a deterministic, auditable current route.
2. Capture and prove the exact immutable identity/blob/content binding actually used for preparation.
3. Ensure the prepared tuple's profile binding is derived from that exact fetched/proven live profile, not from manual SHA substitution or stale committed metadata.
4. Fail closed if the live profile cannot be fetched, identified unambiguously, parsed, or proven current enough for the exact preparation.
5. Preserve one-AppID bounding before Taste projection/payload/queue expansion.
6. Preserve existing Taste model/semantics/fingerprint/context binding validation and all V5/evidence/price-blind safety checks.
7. Keep all outputs temporary/artifact-only and outside canonical production paths.
8. Preserve clean repository proof before/after execution.
9. Avoid broad StoreBrowse/full production rebuild/historical rerun.

Prefer extending the existing `scripts/build_taste_current_main_canary.py` / `.github/workflows/taste-current-main-canary.yml` route rather than creating another canary system. A helper is acceptable only if it remains a bounded part of this same route and has no recurring ownership.

## Focused validation
Add/update the smallest focused tests that prove at least:
- exact current-live profile content/blob binding is used by the prepared tuple;
- stale committed profile binding cannot silently win over current live profile;
- unavailable/ambiguous/malformed live profile fails closed;
- exactly one AppID remains bounded;
- queue cardinality remains `0..1`;
- no other AppID leakage;
- no canonical write/ingest/semantic/Scheduled Task operation;
- repository remains clean.

Then perform one NON-SEMANTIC read-only validation for AppID `1016800` using the current-main one-game path.

Required validation proof:
- exactly one subject `App_1016800`;
- exact live profile blob/content identity observed for that validation;
- exact prepared profile binding;
- equality between the live profile actually used and prepared tuple binding;
- exact model/semantics/fingerprint/context tuple;
- queue cardinality `0..1` and, if `1`, only AppID `1016800`;
- semantic execution `false`;
- canonical ingest `false`;
- Scheduled Task mutation/trigger `false`;
- production write `false`;
- repository clean before/after.

If the live profile changes during validation such that exact equality cannot be proven for one frozen tuple, fail closed and report the race precisely. Do not chase it with unbounded retries.

## Hard boundaries
Do NOT:
- execute any semantic Taste result;
- modify or trigger Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`;
- create another Scheduled Task;
- use old generation 1;
- manually substitute a profile SHA;
- hand-edit canonical queue/payload/cache/receipt/inbox;
- run canonical Taste ingest;
- take a second game;
- widen backlog/daily production;
- weaken producer fence/binding/V5/evidence/price-blind guards;
- use paid OpenAI API, Copilot, paid external service, or external scheduler;
- start System Audit;
- start Giveaway/ITAD or other backlog work.

## Anti-stall
Follow `WORKER_ANTI_STALL_PROTOCOL.md` exactly. Record external run/job/artifact IDs immediately. Bound polling. If an external process remains active beyond the allowed response cycle, checkpoint `waiting_external` in the durable report and return control rather than waiting indefinitely.

## Done when
Save:
`reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`

Report must contain:
1. Task
2. Verified predecessor/blocker
3. Architecture preflight
4. Changes
5. Focused tests
6. Non-semantic Chernobylite preparation validation
7. Exact current-live profile proof and prepared binding proof
8. Safety/containment proof
9. Unresolved
10. Status
11. Recommended next step
12. Exact commit/run/job/artifact/file refs
13. Efficiency / reusable lesson

Final Status exactly one:
- `complete_ready_for_real_canary_acceptance`
- `needs_followup`
- `blocked`

If status is `complete_ready_for_real_canary_acceptance`, stop. Do not execute the semantic canary. The Director will issue a separate ACCEPTANCE task using the already-recorded user authorization for exactly one Chernobylite canary.

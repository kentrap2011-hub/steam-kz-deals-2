# WORKER TASK — TASTE CURRENT-LIVE PROFILE BINDING FIX 01

## Task ID
`taste-current-live-profile-binding-fix-01`

## Mode
`IMPLEMENT`

## Dispatch state
`APPROVED — READY FOR NEW WORKER CHAT`

## Expected report
`reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`

## Goal
Fix the proven stale-profile blocker in the lightweight current-main one-AppID Taste path.

Important operating requirement from the user: `gaming_taste_live.json` will continue to be updated in parallel while Taste is running. That is normal operation, not an exceptional condition.

The solution must therefore safely support profile changes without mixing profile versions, without relying on a long quiet window, and without requiring the user to stop updating the profile.

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

Do not repeat the same acceptance attempt until this route is fixed and validated.

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
- this fix does not create a second queue, scheduler, writer, retry daemon, cache authority, or semantic runtime;
- the canonical live profile authority remains `kentrap2011-hub/stopgame-ratings-data:gaming_taste_live.json`;
- the chosen solution is safe when the live profile changes before, during, or after one game is processed.

If current contracts do not permit a safe concurrency-aware route, stop `blocked` and explain the exact contract gap instead of weakening guards or inventing a second system.

## Required behavior
The implementation must establish an immutable, auditable profile version for each prepared semantic tuple.

Required semantics:
1. If the profile changes BEFORE the tuple is frozen, preparation must use the newer proven live version.
2. Once one exact tuple is frozen, every later step for that tuple must refer to that same exact profile version. Never mix old tuple fields with a newer profile.
3. A profile update that happens AFTER the tuple is frozen must not silently rewrite or corrupt that tuple.
4. If canonical contracts allow the frozen tuple to remain valid against its immutable profile snapshot, use that safe versioned binding and prove it.
5. If canonical contracts require the profile still to be current at ingest/commit time, then a later profile change must make that old result fail closed cleanly and automatically, with no manual repair; the next normal attempt must pick up the new profile. Do not create an unbounded retry loop.
6. Normal profile updates must not leave Taste permanently stuck on an old profile or require the user to stop editing tastes.

Do not weaken existing producer-fence, binding, V5, evidence, or price-blind checks to achieve this.

## Required implementation
Make the smallest safe change to the existing lightweight one-AppID path.

The implementation must:
1. Resolve/fetch canonical live `gaming_taste_live.json` through a deterministic, auditable route.
2. Capture the exact immutable identity/blob/content binding actually used for preparation.
3. Derive the prepared tuple's profile binding from that exact fetched/proven profile, not manual SHA substitution or stale committed metadata.
4. Carry that exact immutable profile binding through all relevant preparation data needed by the later semantic step.
5. Fail closed if the profile cannot be fetched, identified unambiguously, parsed, or bound exactly.
6. Preserve one-AppID bounding before Taste projection/payload/queue expansion.
7. Preserve existing Taste model/semantics/fingerprint/context validation and all V5/evidence/price-blind safety checks.
8. Keep outputs temporary/artifact-only and outside canonical production paths.
9. Preserve clean repository proof before/after execution.
10. Avoid broad StoreBrowse/full production rebuild/historical rerun.
11. Avoid any design that assumes the user will pause profile updates.

Prefer extending the existing `scripts/build_taste_current_main_canary.py` / `.github/workflows/taste-current-main-canary.yml` route rather than creating another canary system. A helper is acceptable only as a bounded part of this route with no recurring ownership.

## Focused validation
Add/update the smallest focused tests that prove at least:
- exact current-live profile content/blob binding is used by the prepared tuple;
- stale committed profile binding cannot silently win;
- unavailable/ambiguous/malformed live profile fails closed;
- profile changes before freeze select the new version;
- profile changes after freeze cannot create a mixed-version tuple;
- if a later change invalidates an old result under canonical contracts, that result is rejected cleanly and the route is able to use the newer profile on the next bounded attempt without manual repair;
- exactly one AppID remains bounded;
- queue cardinality remains `0..1`;
- no other AppID leakage;
- no canonical write/ingest/semantic/Scheduled Task operation;
- repository remains clean.

Then perform one NON-SEMANTIC read-only validation for AppID `1016800` using the current-main one-game path.

Required validation proof:
- exactly one subject `App_1016800`;
- exact live profile identity selected for that validation;
- exact prepared profile binding;
- equality between the profile actually used and prepared tuple binding;
- exact model/semantics/fingerprint/context tuple;
- queue cardinality `0..1` and, if `1`, only AppID `1016800`;
- semantic execution `false`;
- canonical ingest `false`;
- Scheduled Task mutation/trigger `false`;
- production write `false`;
- repository clean before/after.

Also prove the concurrency rule with focused tests or a bounded deterministic simulation: a profile version change around the freeze boundary must never produce a mixed-version result and must not require a user-controlled quiet window.

Do not chase a changing profile with unbounded retries.

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
- require the user to stop or pause profile updates;
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
6. Concurrency/profile-update behavior proof
7. Non-semantic Chernobylite preparation validation
8. Exact profile proof and prepared binding proof
9. Safety/containment proof
10. Unresolved
11. Status
12. Recommended next step
13. Exact commit/run/job/artifact/file refs
14. Efficiency / reusable lesson

Final Status exactly one:
- `complete_ready_for_real_canary_acceptance`
- `needs_followup`
- `blocked`

If status is `complete_ready_for_real_canary_acceptance`, stop. Do not execute the semantic canary. The Director will issue a separate ACCEPTANCE task using the already-recorded user authorization for exactly one Chernobylite canary.

# Worker Report — Taste Canary Execute Now 01

## Task
`taste-canary-execute-now-01`

Run the already-armed one-game Taste canary immediately using the same recurring Scheduled Task, verify the exact one-game GitHub ingest outcome, and restore the permanent DAILY 01:00 Europe/Samara schedule without widening production.

## Status
`complete_canary_rejected_needs_diagnosis`

## Final outcome
The existing generation-2 `Taste Semantic Producer` was successfully triggered immediately by temporarily moving the schedule of that SAME recurring task. It produced exactly one semantic result for the authorized canary `Chernobylite Complete Edition` / `App_1016800` and submitted it through the canonical GitHub Taste inbox route.

The result was NOT canonically accepted. The GitHub ingest workflow failed before ingest because the shared inbox still contains a pre-existing generation-1 Prototype canary file whose old producer identity is now correctly rejected by the generation-2 producer fence.

No retry, repair, second game, second task, backlog widening, paid API, Copilot, or external scheduler was used.

## Fixed identities
- Scheduled Task title: `Taste Semantic Producer`
- Scheduled Task id: `6aa032f37e688191a5c9a1a83f91c5d9`
- producer id: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`
- producer generation: `2`
- canary title: `Chernobylite Complete Edition`
- canary AppID: `1016800`
- canary key: `App_1016800`
- permanent schedule: DAILY 01:00 Europe/Samara

Old completed generation-1 task `6a9d6fdddc00819193ed670d782045c4` was not modified, deleted, re-enabled, or reused.

## Exact canary pre-trigger revalidation
Immediately before triggering, current `main` still contained the exact bound canary and it remained eligible:
- `taste_fingerprint = b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`
- `candidate_context_sha256 = 2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`
- `profile_blob_sha = c42a6a5dcf608e04bf86d24be9e1542f1b934456`
- `taste_model_version = taste-v3`
- `taste_semantics_sha256 = 0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- `source_mailing_updated_at_utc = 2026-09-07T20:45:43.377890+00:00`
- `ai_required_reason = taste_cache_key_missing`
- `work_required` still included `evaluate_taste_fit`, `evaluate_normalized_taste_factors`, and `resolve_grounded_negative_analysis`.

Canonical producer fence before execution remained:
- active producer id `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`
- active producer generation `2`
- semantic contract `TASTE-SEMANTIC-RESULT-V5`
- mismatch policy `reject_before_ingest`.

## Trigger method used
No direct/manual run-now action is exposed for an existing Scheduled Task in this execution, so the task-authorized schedule-only fallback was used.

Temporary mutation on the SAME task only:
- task id remained `6aa032f37e688191a5c9a1a83f91c5d9`;
- title/prompt/canary binding/producer identity remained unchanged;
- temporary exact recurring schedule: `2026-09-08 21:54 Europe/Samara`;
- no one-time task conversion;
- no second task created.

Current time used for staging was `2026-09-08 21:51:39 +04:00`.

## Actual dispatch / run proof
The existing task did run.

Scheduler readback after execution reports:
- `id = 6aa032f37e688191a5c9a1a83f91c5d9`
- `last_run_time = 2026-09-08T17:57:42.661880+00:00`
- exact Samara local run time = `2026-09-08 21:57:42.661880 Europe/Samara`.

GitHub received a new commit from the canary execution:
- commit: `1ca45ad415ddb79f8ad276a1a92c79856b79ff04`
- message: `Submit generation-2 Taste canary for App 1016800`
- GitHub timestamp: `2026-09-08T17:57:00Z`
- submitted path: `data/ai_inbox/taste/canary-app-1016800-gen2.json`.

The commit added exactly one result in the `results` array:
- `key = App_1016800`
- `appid = 1016800`
- `producer_id = chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`
- `producer_generation = 2`
- exact fingerprint/context/profile/model/semantics/source bindings matched the frozen canary tuple.

No second canary/result was produced by this Scheduled Task run.

## Semantic result produced
The one submitted result itself was structurally generation-2 and canary-bound:
- verdict: `INCLUDE`
- fit level: `moderate`
- reason code: `include_moderate`
- normalized Taste factors were present;
- grounded negative analysis was present;
- evidence-state fields were present.

This report does NOT treat those semantics as canonical accepted data because the ingest transaction failed before acceptance.

## Canonical GitHub ingest outcome
The push triggered canonical workflow:
- workflow: `Ingest context-bound taste batch`
- workflow run id: `34260132159`
- head SHA: `1ca45ad415ddb79f8ad276a1a92c79856b79ff04`
- status: `completed`
- conclusion: `failure`
- ingest job id: `102175717841`.

Important validation detail from the job log:
1. `python scripts/validate_taste_producer_fence.py` PASSED under generation 2.
2. It reported `correct_active_producer_accepted: true` and the wrong/missing producer identity regression cases rejected as expected.
3. The next whole-inbox gate `python scripts/taste_producer_fence.py data/ai_inbox/taste` scanned the existing shared inbox.
4. It stopped on the pre-existing file:
   `data/ai_inbox/taste/canary-App_10150-producer-g1.json`
5. Exact rejection reason:
   old `producer_id = chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4` does not match the active generation-2 producer.
6. The gate exited with code `1`, so `process_taste_inbox.py` did not perform the canonical ingest transaction for the new App 1016800 result.

Therefore the concrete rejection is an inbox cleanliness / old-generation artifact blocker, not a demonstrated rejection of the new generation-2 canary envelope itself.

## Post-failure acceptance proof
Current `main` confirms non-acceptance:
- `data/ai_inbox/taste/` still contains both the old `canary-App_10150-producer-g1.json` and the new `canary-app-1016800-gen2.json`;
- `App_1016800` remains in `data/production/pre_ai/chatgpt_taste_queue.jsonl` with `ai_required_reason = taste_cache_key_missing` and its full Taste work still required;
- `data/cache/taste_ingest_receipts/latest_runtime_status.json` still points to the prior successful semantic execution on `2026-09-01T21:03:08+00:00`, not this canary.

Accepted AppID for this execute-now task: `none`.
Rejected/not-accepted canary AppID requiring diagnosis: `1016800`.

No canonical receipt for this canary was created because the workflow failed before `process_taste_inbox.py` could complete its transaction.

## Failure containment
No attempt was made to bypass the producer fence, delete/move the historical generation-1 inbox file, alter ingestion semantics, or manually force acceptance. Those would be repair actions outside this task.

No second semantic submission was made and the failed workflow was not blindly retried, because the same pre-existing gen1 inbox artifact would deterministically hit the same whole-inbox fence.

No second game was selected. No fallback logic was exercised. No backlog analysis was started.

## Permanent schedule restoration
After the immediate dispatch was observed, the SAME task was restored to the permanent schedule.

Final explicit scheduler readback after restoration/containment:
- task id: `6aa032f37e688191a5c9a1a83f91c5d9`
- title: `Taste Semantic Producer`
- schedule:
  `DTSTART;TZID=Europe/Samara:20260909T010000`
  `RRULE:FREQ=DAILY;BYHOUR=1;BYMINUTE=0;BYSECOND=0`
- timing mode: `exact_schedule`
- default timezone: `Europe/Samara`
- `is_enabled = true`
- `last_run_time = 2026-09-08T17:57:42.661880+00:00`.

During final readback, a schedule-only update initially showed the task with the correct 01:00 recurrence but `is_enabled = false`. This was immediately corrected on the SAME task by explicitly setting `is_enabled = true` while preserving the same 01:00 schedule, prompt, immutable id, and canary binding. The subsequent tool response returned `status = SUCCESS` and `is_enabled = true`.

Thus the permanent recurring schedule is restored and enabled on the original generation-2 task. The task remains canary-only; it has NOT been widened to backlog processing.

## Proof no second game / no widening
- Scheduled Task submission commit contains exactly one `results` entry.
- That entry is only `App_1016800`.
- No fallback result was created.
- No second Scheduled Task was created.
- Existing task prompt remains the exact canary-bound prompt from the prior implementation.
- Old completed task was untouched.
- Backlog/full-production instructions were not installed.

The old Prototype file observed by the GitHub workflow is historical pre-existing inbox content; it was not a second game selected or analyzed by this run.

## Cost / hard-boundary confirmation
- paid OpenAI API: not used;
- Copilot: not used;
- external scheduler/service: not used;
- second Scheduled Task: not created;
- new immutable task identity: not created;
- producer fence weakening: none;
- semantic V5 weakening: none;
- backlog/mass analysis: not started.

## Independent System Audit readiness
`not_ready_until_ingest_blocker_is_diagnosed_and_repaired`

The canary execution path itself reached GitHub correctly and the new generation-2 producer fence regression passed, but the canary was not canonically accepted. Therefore this task must not claim `complete_canary_accepted_ready_for_system_audit`.

A diagnosis/repair task is required for the stale generation-1 inbox artifact / whole-inbox fencing interaction. After a separately authorized repair and successful canonical acceptance of this same canary, independent System Audit can evaluate the full transition before any backlog widening.

This worker does not start that repair, System Audit, or any other task.

## Final validation summary
- durable report existed in `main` before Scheduled Task mutation: PASS;
- exact canary revalidated before trigger: PASS;
- same immutable task used: PASS;
- second task created: NO;
- immediate dispatch achieved: PASS;
- exact actual run time observed: PASS — `2026-09-08 21:57:42.661880 Europe/Samara`;
- semantic results produced by this run: exactly `1`;
- produced AppID: exactly `1016800`;
- producer identity/generation in submission: correct gen2;
- canonical GitHub inbox reached: PASS;
- generation-2 producer regression validator: PASS;
- canonical ingest transaction: FAIL before ingest due pre-existing gen1 inbox file;
- App 1016800 canonically accepted: NO;
- second game processed by this run: NO;
- permanent DAILY 01:00 Europe/Samara schedule restored: PASS;
- final task enabled/recurring: PASS (`is_enabled = true`);
- canary-only prompt preserved: PASS;
- backlog widening: NO;
- old completed task mutation: NO;
- paid API/Copilot/external scheduler: NO;
- System Audit can start immediately: NO — diagnosis/repair required first.

## Changed GitHub paths in this task
1. `reviews/worker_reports/taste-canary-execute-now-01.md` — durable report/checkpoints/final state.
2. `data/ai_inbox/taste/canary-app-1016800-gen2.json` — exactly one canary result created by the existing Scheduled Task run.

No canonical cache/result/receipt was accepted for App 1016800.

## Exact next-state containment
- existing generation-2 Scheduled Task remains the same immutable task;
- task remains enabled and recurring DAILY 01:00 Europe/Samara;
- prompt remains restricted to App 1016800 only;
- App 1016800 remains unaccepted/current in queue;
- gen2 result remains in canonical inbox;
- stale generation-1 Prototype inbox file remains untouched;
- no backlog/full-production authorization exists;
- do not create another producer or select another game;
- diagnose the stale-inbox/whole-inbox fence blocker in a separately authorized task.

## Refs
- Task: `WORKER_TASK_TASTE_CANARY_EXECUTE_NOW_01.md`
- Prior implementation report: `reviews/worker_reports/taste-active-producer-restore-implement-01.md`
- Producer fence: `config/taste_result_contract.json`
- Canary submission commit: `1ca45ad415ddb79f8ad276a1a92c79856b79ff04`
- Canary inbox file: `data/ai_inbox/taste/canary-app-1016800-gen2.json`
- Blocking old inbox file: `data/ai_inbox/taste/canary-App_10150-producer-g1.json`
- Ingest workflow run: `34260132159`
- Ingest job: `102175717841`
- Queue: `data/production/pre_ai/chatgpt_taste_queue.jsonl`
- Runtime receipt status: `data/cache/taste_ingest_receipts/latest_runtime_status.json`

## Efficiency / reusable lesson
A producer-generation fence applied to an entire shared inbox makes stale historical inbox files part of every future ingest transaction. A successful new-producer submission can therefore be blocked before its own canonical validation/ingest even when the new producer identity itself is correct. The safe response is to stop without bypassing the fence or retrying blindly, preserve the exact failed input, and repair inbox lifecycle/archival behavior under a separate task.

# Worker Report — Taste Active Producer Restore Design 01

## Task
Design only: determine the narrowest safe restoration path for exactly one ACTIVE recurring ChatGPT Scheduled Taste producer, without creating or mutating any Scheduled Task or processing any game.

## Final decision

Restore by creating **exactly one NEW recurring daily ChatGPT Scheduled Task** and keep the old completed task untouched for provenance.

The new task receives a new immutable Scheduled Task / jawbone id. That new external producer identity must be cut over in GitHub from producer generation `1` to producer generation `2`. The same new recurring task must first run in a one-game canary mode and, only after an independent System Audit passes, have its instructions widened to normal daily Taste production. Do not create a disposable one-off canary task.

The normal cycle remains the canonical **01:00 Europe/Samara** cycle. The future implementation should set the first occurrence to the next 01:00 Europe/Samara that leaves enough staging time to complete task configuration, GitHub identity migration, and validation before execution; if the next 01:00 is too close, start on the following day's 01:00 rather than risk a pre-migration run.

## Verified facts

- Required task/protocol/context set was read: `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `DIRECTOR_PROTOCOL.md`, `WORKER_REPORT_DURABILITY_PROTOCOL.md`, and `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`.
- Old completed Scheduled Task supplied by the task/user UI evidence:
  - jawbone id: `6a9d6fdddc00819193ed670d782045c4`
  - canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`
  - producer generation: `1`
  - UI state: `Completed`
  - Date/Time non-editable
  - Scheduled `Active` filter empty.
- `config/taste_result_contract.json` is the canonical concrete repository producer fence. Exact current fields are:
  - `producer_fence.active_producer_id = "chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4"`
  - `producer_fence.active_producer_generation = 1`
  - `producer_fence.missing_legacy_or_mismatch_policy = "reject_before_ingest"`.
- `scripts/taste_producer_fence.py` reads the active id/generation dynamically from `config/taste_result_contract.json`; it does not need a new hard-coded producer id.
- `scripts/validate_taste_producer_fence.py` also derives the accepted identity dynamically and already proves current identity acceptance plus wrong/missing id/generation rejection.
- `.github/workflows/ingest-taste-batch.yml` runs the producer fence before semantic validation and persistence.
- `scripts/ingest_taste_results.py` binds every accepted result to the current queue row using `key`, `appid`, `taste_fingerprint`, and `candidate_context_sha256`, and also validates the current payload bindings `profile_blob_sha`, `taste_model_version`, `taste_semantics_sha256`, and `source_mailing_updated_at_utc`.
- The current queue does **not** expose one literal field named `run_key`. Therefore this design does not invent one. For canary safety, the effective current-run identity is the exact existing queue/binding tuple described above.
- `config/execution_ownership_contract.json` keeps GitHub as control plane and Scheduled ChatGPT as constrained semantic data plane.
- `config/daily_execution_contract.json` is canonical for cadence: timezone `Europe/Samara`, `night_preparation.local_time = "01:00"`, external semantic worker `ChatGPT scheduled task`.
- Historical automatic success corroborates that cycle: the last proven accepted automatic batch was named `chatgpt-20260902-0100-001.json` and was accepted at approximately 01:03 Europe/Samara.
- Current official OpenAI Scheduled Tasks documentation supports recurring tasks and lets users review/edit/pause/resume tasks. It does not provide evidence sufficient to override the user's concrete observation that this specific old task is terminal `Completed` with non-editable Date/Time.

## Required design answers

### 1. Can the old completed task be safely reactivated?

**No, not under the currently verified evidence.**

Strongest evidence:

1. The user's direct UI inspection of this exact task shows `Completed`.
2. Date/Time is non-editable for this exact task.
3. The Scheduled `Active` filter is empty.
4. Prior repository recon did not establish an authoritative reusable/reactivation path for this terminal instance.
5. Official OpenAI documentation describes generic recurring-task management, including pause/resume/edit, but does not prove that this exact terminal/non-editable `Completed` instance can be converted back into a durable recurring active producer.

Therefore a future implementation must **not** depend on reactivating id `6a9d6fdddc00819193ed670d782045c4`. Preserve it unchanged as historical provenance.

### 2. Is a new recurring Scheduled Task required?

**Yes.** Create exactly one new **recurring daily** Scheduled Task named/serving the `Taste Semantic Producer` role.

Do not create a one-time canary task. The same new recurring task must be used for:

- the first one-game canary;
- the hold/no-op period before audit;
- normal daily production after the independent audit gate passes.

### 3. Exact producer id and generation if the new task has a new immutable id

After creation returns new immutable id `<NEW_TASK_ID>`:

```text
producer_id = chatgpt_scheduled_task:<NEW_TASK_ID>
producer_generation = 2
```

Generation must advance from `1` to `2` because the external producer instance changed. Reusing generation `1` for a different immutable Scheduled Task id would erase the replacement boundary and make provenance/fencing ambiguous.

Generation is monotonic. If this new generation-2 task later must be abandoned and replaced by another immutable task id, the next replacement must use generation `3`; do not roll a different producer id back into generation `1` or reuse `2` for a second producer instance.

### 4. Exact GitHub identity migration in the future IMPLEMENT

The narrowest production identity migration changes **one canonical runtime contract file**:

`config/taste_result_contract.json`

Change exactly:

```text
producer_fence.active_producer_id
  FROM chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4
  TO   chatgpt_scheduled_task:<NEW_TASK_ID>

producer_fence.active_producer_generation
  FROM 1
  TO   2
```

Keep unchanged:

```text
producer_fence.transport_fields = ["producer_id", "producer_generation"]
producer_fence.missing_legacy_or_mismatch_policy = "reject_before_ingest"
contract = TASTE-SEMANTIC-RESULT-V5
```

No identity edit is required in:

- `config/execution_ownership_contract.json`;
- `scripts/taste_producer_fence.py`;
- `scripts/validate_taste_producer_fence.py`;
- `.github/workflows/ingest-taste-batch.yml`.

Those files must be revalidated, not rewritten merely because the id changed. Historical reports/task records must remain historical and must not be rewritten to claim generation `2` for the old id.

Future validation must prove:

- new id + generation `2` accepted by the producer fence;
- old id + generation `1` rejected before ingest;
- wrong/missing id or generation rejected;
- `TASTE-SEMANTIC-RESULT-V5` unchanged;
- normal current queue/binding validation still passes.

### 5. How to prevent overlap and guarantee one active analyzer

Future IMPLEMENT sequence:

1. Preflight Scheduled UI/control plane and prove **zero active Taste producer tasks**; retain the old id in `Completed` state.
2. Select the one exact fresh canary candidate/binding from current GitHub-prepared data; do not process it in the worker chat.
3. Create **one and only one** new recurring task with first execution at a safe future 01:00 Europe/Samara slot.
4. Capture the returned immutable task id. If creation outcome is ambiguous, **do not retry creation blindly**. Re-read Scheduled/Active first. Ambiguity is a stop condition.
5. Configure that same task with its exact canonical producer id, generation `2`, and singleton canary authorization.
6. Migrate the GitHub producer fence to that id/generation and run repository validations before its first scheduled execution.
7. Final pre-run proof: old id remains Completed; exactly one Taste task is Active; its id equals `<NEW_TASK_ID>`; GitHub accepts only `<NEW_TASK_ID>` generation `2`.

At no point is a second active analyzer needed.

### 6. Exact first-run canary containment

Do **not** hard-code today's AppID in this design report because the requirement is a **fresh current** game at the future real run.

Immediately before future implementation, rebuild/read the current completed GitHub-prepared Taste scope and select exactly one row satisfying all of the following:

- it is in the current canonical `data/production/pre_ai/chatgpt_taste_queue.jsonl`;
- it is current under the current manifest/projection bindings;
- it requires a fresh full Taste evaluation (`evaluate_taste_fit`), rather than selecting a historical already-evaluated row merely for convenience;
- record its exact `taste_subject_key`, `appid`, `taste_fingerprint`, `candidate_context_sha256` and current batch bindings.

The new recurring Scheduled Task's initial instructions must authorize **only that exact tuple**, with maximum one result and no fallback candidate:

```text
(taste_subject_key,
 appid,
 taste_fingerprint,
 candidate_context_sha256,
 profile_blob_sha,
 taste_model_version,
 taste_semantics_sha256,
 source_mailing_updated_at_utc)
```

This tuple is the effective existing run identity. The repository currently has no literal `run_key` field, so adding a fake parallel run-key contract is unnecessary.

The task must submit only through the existing canonical Taste inbox with:

```text
producer_id = chatgpt_scheduled_task:<NEW_TASK_ID>
producer_generation = 2
```

GitHub then independently rejects a different/stale AppID, key, fingerprint, candidate context, producer identity, generation, or global binding.

### 7. How immediate later scheduled runs remain no-op before widening

The new task stays **recurring and Active**, but its prompt remains locked to the same singleton canary tuple until audit.

Its canary rule must be:

- analyze only the authorized exact tuple;
- if that exact tuple is no longer current, no-op;
- if an accepted cache/overlay entry for that exact current fingerprint/context now exists as a result of the canary, no-op;
- never choose the next queue row;
- never treat a changed fingerprint/context as permission to analyze a refreshed version;
- never widen from one item automatically.

Choosing a row that requires fresh `evaluate_taste_fit` makes the post-success state observable: after successful canonical ingest, the exact current evaluation is now persisted. Therefore the next recurring run can deterministically stop rather than process a second game, even if other backlog remains.

The task must remain active; it must **not** use an end condition that marks itself Completed after the canary.

### 8. Independent System Audit gate after successful canary

After one successful scheduled canary and before any widening, run a **separate System Audit task/chat**. The audit must not edit the Scheduled Task or widen throughput.

Audit PASS requires all of these:

- old id `6a9d6fdddc00819193ed670d782045c4` still exists only as Completed historical provenance;
- exactly one active Taste Scheduled Task exists and its id is `<NEW_TASK_ID>`;
- `config/taste_result_contract.json` points to `chatgpt_scheduled_task:<NEW_TASK_ID>` generation `2`;
- old id/generation `1` fails the producer fence;
- exactly one fresh authorized AppID/current binding was semantically processed;
- exactly one canonical result for that canary was accepted/persisted, with no duplicate receipt or unintended second candidate;
- result matched current `key/appid/taste_fingerprint/candidate_context_sha256` and current global bindings;
- producer fence, V5 semantic validation, transactional proof, queue rebuild and receipts all remain valid;
- at least the next scheduled invocation under still-canary-bound instructions performs no semantic work on another game;
- the new task remains recurring/Active after the canary rather than becoming Completed.

Any failure => audit `FAIL`, no widening.

Suggested later audit filename after canary success (design only; do not create now):

`WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_SYSTEM_AUDIT_01.md`

Suggested audit report path:

`reviews/worker_reports/taste-active-producer-restore-system-audit-01.md`

### 9. How the SAME task becomes normal daily production after audit

Only after independent System Audit PASS, use a later authorized implementation to edit the **same task id `<NEW_TASK_ID>`**.

Keep unchanged:

- immutable task id;
- canonical producer id;
- producer generation `2`;
- daily 01:00 Europe/Samara schedule;
- GitHub ownership of scope/queue/bindings/validation/persistence;
- `TASTE-SEMANTIC-RESULT-V5`;
- canonical inbox/ingest path.

Change only its instructions from the fixed singleton canary tuple to the canonical normal bounded daily Taste-consumer instructions. Remove the one-candidate canary lock; do not create another task. Normal throughput/completeness remains whatever the canonical GitHub daily contract requires; the Scheduled Task must not invent a per-day quota or redefine the queue.

### 10. Rollback / fail-closed behavior

The restoration must be staged so a failure produces **zero accepted unauthorized semantic writes**, not a second producer.

Before first run:

- choose a first recurring 01:00 slot sufficiently in the future;
- if possible, keep the new task paused during configuration/migration and resume only after all checks pass;
- if a pause-at-creation workflow is unavailable, the safe future first-run time is the protection window.

If task creation succeeds but GitHub migration/configuration fails:

- pause the new task before its first run;
- do not create a replacement immediately;
- old task stays Completed;
- system is allowed to have zero active Taste producers while failed closed.

If the new task somehow emits before GitHub migration finishes:

- current GitHub producer fence still expects the old id/generation and therefore rejects the new producer before ingest/persistence;
- investigate/pause; do not weaken the fence to accept the output.

If canary fails after GitHub has moved to generation `2`:

- do not widen;
- pause or leave the new task canary-locked/no-op as appropriate;
- keep generation monotonic; do **not** roll the repository identity backward to generation `1` merely to make the old completed task usable;
- if the same task can be repaired safely, keep generation `2`;
- if a different new immutable task is ultimately required, use generation `3` after ensuring the failed generation-2 task is not active.

### 11. Exact normal daily cadence

Canonical cadence remains:

```text
DAILY
01:00
Europe/Samara
```

This is not a new secondary recurring stage. It is the existing `config/daily_execution_contract.json` nightly production cycle in which GitHub owns preparation/control and the Scheduled ChatGPT producer consumes only completed GitHub-prepared semantic inputs.

For the restoration rollout, do not shift normal production to an invented 01:15/02:00 schedule merely to make migration easier. Instead finish migration before the first chosen 01:00 execution. If the next 01:00 does not leave a safe staging window, explicitly start the same daily recurrence on the following day's 01:00.

### 12. One concrete next IMPLEMENT task design

Proposed next task filename:

`WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_IMPLEMENT_01.md`

Proposed required report path:

`reviews/worker_reports/taste-active-producer-restore-implement-01.md`

That future IMPLEMENT should be narrowly scoped to:

1. prove zero active Taste producers and preserve the old Completed task;
2. select/record one fresh current full-evaluation canary tuple without analyzing it in the worker chat;
3. create exactly one new recurring daily Scheduled Task for 01:00 Europe/Samara using that singleton canary contract;
4. capture its immutable id and configure the same task with canonical producer id + generation `2`;
5. migrate only `config/taste_result_contract.json` producer-fence identity fields to the new id/generation;
6. run the existing producer-fence/semantic/transactional validations and explicit old-generation rejection checks;
7. prove exactly one active task exists and is the new id;
8. leave the task singleton-canary-bound and recurring/Active for its first real scheduled run;
9. do not widen throughput in that IMPLEMENT;
10. after the canary is actually accepted, require the separate System Audit described above before any widening.

This design intentionally separates restoring a durable producer from approving normal production. A successful task creation/migration is not itself permission to process the backlog.

## Migration sequence summary

```text
OLD completed task retained (id ...045c4, generation 1)
        |
        | preflight: Active Taste count == 0
        v
select one fresh exact current canary tuple
        |
        v
create ONE recurring daily task, safe future 01:00 Europe/Samara
        |
        v
capture <NEW_TASK_ID> and bind task prompt to singleton canary
        |
        v
GitHub producer fence -> chatgpt_scheduled_task:<NEW_TASK_ID>, generation 2
        |
        v
validate new accepted / old gen1 rejected / V5 + bindings unchanged
        |
        v
resume/leave exactly ONE task Active
        |
        v
first scheduled run: exactly one fresh current game
        |
        v
same recurring task remains canary-locked; later invocations no-op
        |
        v
SEPARATE SYSTEM AUDIT
        |
        +-- FAIL -> no widening; pause/repair fail-closed
        |
        +-- PASS -> later edit SAME task instructions for normal daily scope
```

## Changes made by this DESIGN task

- Created and updated only this report:
  - `reviews/worker_reports/taste-active-producer-restore-design-01.md`
- No Scheduled Task was created, updated, resumed, paused, or deleted.
- No game was analyzed.
- No Taste queue/result/cache/receipt/production artifact was changed.
- Old completed task was not deleted or modified.
- No paid OpenAI API or Copilot was used.
- No next worker task was created or started.

## Validation

Repository design checks completed:

- current producer fence fields verified exactly in `config/taste_result_contract.json`;
- dynamic fence behavior reviewed in `scripts/taste_producer_fence.py` and `scripts/validate_taste_producer_fence.py`;
- pre-ingest fence ordering reviewed in `.github/workflows/ingest-taste-batch.yml`;
- current candidate/binding checks reviewed in `scripts/ingest_taste_results.py` and `scripts/process_taste_inbox.py`;
- canonical cadence and ownership reviewed in `config/daily_execution_contract.json` and `config/execution_ownership_contract.json`;
- prior singleton/canary and failure-forensic reports reviewed;
- current official OpenAI Scheduled Tasks documentation reviewed for recurring/manage/pause/resume behavior.

## Status

`complete_restore_plan_ready`

## Exact refs

- Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`
- Report: `reviews/worker_reports/taste-active-producer-restore-design-01.md`
- Current producer contract: `config/taste_result_contract.json`
- Ownership: `config/execution_ownership_contract.json`
- Daily cadence: `config/daily_execution_contract.json`
- Producer fence: `scripts/taste_producer_fence.py`
- Fence regression: `scripts/validate_taste_producer_fence.py`
- Candidate/binding ingest: `scripts/ingest_taste_results.py`
- Transactional processor: `scripts/process_taste_inbox.py`
- Ingest workflow: `.github/workflows/ingest-taste-batch.yml`
- Prior singleton implementation: `reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`
- Prior current-state evidence: `reviews/worker_reports/taste-singleton-disabled-state-confirm-01.md`
- Prior completed-task reuse recon: `reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`
- Failure forensic: `reviews/worker_reports/taste-daily-automation-failure-forensic-recon-01.md`
- Official OpenAI Scheduled Tasks Help: `https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt`

## Efficiency / reusable lesson

Keep external immutable producer identity in one canonical GitHub fence and keep validators dynamic. Then replacing a terminal Scheduled Task requires a narrow, reviewable generation cutover rather than weakening semantic validation or duplicating the producer path.

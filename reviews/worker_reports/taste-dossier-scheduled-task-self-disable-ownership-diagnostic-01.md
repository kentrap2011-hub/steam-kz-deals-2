# Taste Dossier Scheduled Task Self-Disable Ownership Diagnostic 01

## Final status

`needs_user_evidence`

The root-cause class is established from current canonical sources and the operator-reported live prompt: the worker had a valid instruction to **stop the current invocation** under full-block/fail-closed conditions, but no authoritative instruction was found that converts that invocation stop into authority to disable the recurring Scheduled Task. The `STOP -> disable recurring task` step is therefore an unsupported worker interpretation and conflicts with the explicit scheduler-ownership fence.

The current external Scheduled Task state itself was not directly exposed by usable read-only scheduler evidence in this diagnostic session, so enabled/disabled state, exact current cadence, exact live task configuration, and last-run/status/error are not asserted.

## Scope and provenance

- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Source of truth: `main`
- Pre-report inspected `main` head: `c35a51599b567f12a9115ac970daf04655b6e04a`
- Task: `WORKER_TASK_TASTE_DOSSIER_SCHEDULED_TASK_SELF_DISABLE_OWNERSHIP_DIAGNOSTIC_01.md`
- Diagnostic mode: read-only except this report.
- START gate was completed from current `CHAT_PROTOCOL.md`, then `CHAT_CONTEXT.md`, the task, routes/decisions, and the required current canonical files were read before targeted history/search.

Current blob evidence used:

| File | Blob SHA | Controlling evidence |
|---|---|---|
| `config/taste_steam_review_dossier_runtime_prompt.md` | `3ab7946cc5cc9241d8433155b85559a68226a4c9` | “current invocation”; worker must never enable/disable/pause/delete/reschedule/edit its own task; invocation-level STOP is never authority to change recurring schedule |
| `config/execution_ownership_contract.json` | `76f1132bf8dceda9792e303d70e64cabd49b1a0e` | Scheduled ChatGPT forbidden capability: `enable_disable_pause_delete_reschedule_or_edit_its_own_scheduled_task` |
| `config/taste_steam_review_dossier_contract.json` | `c9765f9a3330f90aa00899309949e5348e6bcb21` | forbidden: `enable_disable_or_edit_the_scheduled_dossier_task_from_the_semantic_worker` |
| `config/taste_steam_review_dossier_persistence_bridge.json` | `4d53faade7de382d63539bdb5e4ed2797c601400` | GitHub control plane owns validation/persistence/progress; `schedule_edit_by_worker: forbidden`; semantic failure is `...no_schedule_edit` |
| `config/taste_steam_review_dossier_worker_prompt.md` | `1ba4a390923e6bfbc655c7f0094db70ba395b9a6` | multiple stop/fail-closed rules, including full backlog complete/no dossier work and existing deterministic artifact/canonical lag; none grants scheduler mutation |
| `PROJECT_DECISIONS.md` | `605163831cefa7a4a796476552fb7652be4d458c` | Scheduled worker never owns schedule mutation; explicit prohibition on enabling/disabling/pausing/deleting/rescheduling/editing own task |
| `PROJECT_ROUTES.md` | `81d288d17f281f35de389387b75a3e8e8cd3c8ba` | scheduler ownership route and explicit “cannot ... enable/disable/edit its own schedule” invariant |
| `WORKER_TASK_TASTE_DOSSIER_SCHEDULED_TASK_SELF_DISABLE_OWNERSHIP_DIAGNOSTIC_01.md` | `5298979dbc653efc4587dd8d1e090cb4ccd82d48` | operator-reported live prompt evidence and explicit statement that live prompt does not say `STOP` means disabling the recurring task |

## A. Canonical STOP semantics

The controlling current runtime clause is unambiguous:

> “A true runtime/transport failure ... may stop the **current invocation** when safe forward progress is impossible.”

Immediately after that, the runtime prompt says the Scheduled Dossier worker must never enable, disable, pause, delete, reschedule, or edit its own Scheduled Task, and that group failure, invalid candidate, an existing deterministic artifact, recovery-pending state, empty current work, or invocation-level STOP is **never authority to change the recurring schedule**.

The worker prompt independently contains the conditions that produce a stop. Examples include:

- `full_backlog_complete=true` -> “stop with no dossier work”;
- missing/unreadable/inconsistent worker projection -> “stop fail-closed”;
- changed snapshot/plan/binding or transport failure -> stop current work;
- deterministic artifact already exists while canonical progress has not advanced -> stop and leave GitHub recovery/validation state to the control plane.

Therefore current canonical meaning is:

`full block / fail-closed condition -> stop or return from this invocation`

It is not:

`full block / fail-closed condition -> disable future scheduled invocations`.

## B. Scheduler mutation ownership

The ownership sources agree:

1. `execution_ownership_contract.json` explicitly forbids Scheduled ChatGPT from enabling/disabling/pausing/deleting/rescheduling/editing its own task.
2. `taste_steam_review_dossier_contract.json` explicitly forbids the semantic worker from enabling/disabling/editing the Scheduled Dossier task.
3. `taste_steam_review_dossier_persistence_bridge.json` gives canonical validation/persistence/progress ownership to the GitHub control plane and separately states `schedule_edit_by_worker: forbidden`.
4. `taste_steam_review_dossier_runtime_prompt.md` says the hourly cadence is external orchestration and the worker must not mutate it.
5. `PROJECT_DECISIONS.md` records the same ownership boundary as an intentional architecture decision.

Scheduler configuration/state is therefore an **external operator concern**, not worker semantic authority. GitHub owns repository control-plane state; this does not give GitHub or the semantic worker authority to mutate the external ChatGPT Scheduled Task unless a separate operator action explicitly does so.

### Non-causal documentation note

`PROJECT_ROUTES.md` describes `config/taste_steam_review_dossier_worker_prompt.md` as containing an explicit prohibition on editing/disabling its own Scheduled Task. In the current worker-prompt blob inspected here, the stop rules are present but that scheduler-prohibition wording is not literal. The prohibition is nevertheless explicit in the runtime prompt and machine contracts above. This location mismatch is not the source of the self-disable behavior and does not create authority to self-disable.

## C. Operator-reported live Scheduled Task prompt

The diagnostic task records the operator-supplied current live prompt as runtime evidence. The relevant reported clauses are:

- canonical repository files win on conflict and the worker must fail closed where required;
- create/write failure: `STOP immediately`;
- deterministic artifact already exists while canonical progress has not advanced: `STOP`;
- “Do not modify or reinterpret the existing Scheduled Task title, schedule/cadence or production limits. Do not create another scheduler or recurring producer.”

The task explicitly records that the live prompt does **not** say `STOP` means disabling the recurring Scheduled Task.

Thus the reported live prompt is aligned with the canonical ownership fence. It supplies current-invocation STOP conditions; it does not supply the missing `STOP -> disable` mapping.

## D. Exact origin of the self-disable requirement

### Attribution result

| Candidate source | Result |
|---|---|
| Current canonical repository rule | **Not source.** Current canonical rules explicitly prohibit self-disable. |
| Operator-reported live Scheduled Task prompt | **Not source.** It says STOP in specific current-run conditions and says not to modify/reinterpret schedule/cadence. |
| Generic Scheduled Task / automation runtime semantics visible in this diagnostic | **No supporting rule exposed.** No read-only runtime evidence surfaced a semantic rule that an invocation-level STOP automatically or obligatorily disables recurrence. |
| Worker interpretation | **Source of the unsupported mapping.** The worker conflated invocation lifecycle control with scheduler lifecycle control. |
| Persistence bridge / GitHub control plane | **Not source.** It owns repository validation/persistence/recovery and explicitly forbids worker schedule edit. |

The precise causal chain is therefore two different rules that were incorrectly fused:

1. **Sourced rule:** a full block/fail-closed condition can require `STOP` of the current invocation.
2. **Unsourced inference:** `STOP` of the current invocation means the recurring task must be disabled.

Only step 1 is authoritative. Step 2 is contradicted by current canonical rules and the operator-reported live prompt.

### Targeted history check

A task-scoped read-only history check was used to distinguish an inherited old rule from a newly invented interpretation.

- `33eb191bbabb1e7cc5f0269107b574c2c89a7ac4` — “Add Taste Steam review dossier scheduler task”: initial scheduler-oriented instructions said to “stop cleanly if there is no work”; no self-disable rule was found.
- `79f1c38c218d0d2ea89d7722e4ff5b1c9840d508` — “Implement non-blocking Taste dossier group progress”: added/recorded schedule-mutation prohibition.
- `f0ffb166f37b0ba2da363f8908359373d8b17939` — “Finish Taste dossier non-blocking runtime activation”: explicitly added the current clause that invocation-level STOP is never authority to change recurring schedule.

No `full block -> disable own Scheduled Task` requirement was found in the relevant authoritative history returned by the task-targeted search. This history check is supporting evidence; the current `main` contracts remain controlling.

## E. External Scheduled Task evidence boundary

Read-only external task inspection was attempted. No usable task record/state was exposed into this diagnostic context, so this report does **not** claim to have directly verified:

- whether exactly one `Taste Steam Review Dossier` recurring task currently exists;
- whether it is enabled or disabled;
- the exact current cadence;
- the exact current live prompt beyond the operator-reported prompt captured in the task file;
- the last-run/status/error record.

No inference is made from the reported worker behavior to the current scheduler state.

Minimum operator evidence needed to close only this external-state gap: the task details/state for `Taste Steam Review Dossier` showing (1) title/identity, (2) enabled vs disabled, (3) cadence, (4) full current prompt, and (5) latest run/status/error. Nothing else is required for this diagnostic.

Because direct external state was unavailable, the task-prescribed final status is `needs_user_evidence`, even though the source of the invalid self-disable rule is already classified.

## F. Root cause and conflict conclusion

### Root cause

**Worker interpretation error / ownership-layer conflation.** The worker promoted a current-invocation fail-closed `STOP` into an external scheduler mutation requirement. That transition has no authority in the current repository contracts, no authority in the operator-reported live prompt, and no supporting generic runtime rule exposed during this diagnostic.

### Conflict conclusion

There is **no canonical-vs-live-prompt conflict** in the evidence available here. Both support stopping the current invocation while preserving the external recurring schedule.

The actual conflict is:

`worker's inferred self-disable requirement` **vs** `canonical + reported live scheduler ownership boundary`.

## G. Minimal next step — not executed

Do **not** change GitHub runtime/state/workflows/contracts based on this diagnosis.

Smallest next-step class:

1. **Operator-only external-state verification:** inspect the existing `Taste Steam Review Dossier` task and provide only the five fields listed in section E so its actual enabled state/cadence/prompt/last-run can be reconciled with the proven ownership boundary.
2. If the task is externally disabled or its live prompt differs materially, any enable/repair/prompt action is an **operator action**, not a worker action.
3. If external task state already matches the expected prompt/cadence, no scheduler mutation is indicated by this diagnostic; the behavioral correction class is simply “do not reinterpret invocation STOP as schedule disable.”

No fix was applied.

## Validation gates

| Gate | Status | Evidence |
|---|---|---|
| DIAG-01 | **PASS** | Current runtime prompt explicitly distinguishes current-invocation STOP from recurring schedule authority; worker prompt stop cases were inspected. |
| DIAG-02 | **PASS** | Execution ownership, Dossier contract, persistence bridge, runtime prompt, and project decision all assign/limit scheduler mutation consistently. |
| DIAG-03 | **PASS** | Direct external state was not exposed; the evidence boundary is explicitly recorded without guessing, with minimum required operator evidence specified. |
| DIAG-04 | **PASS** | All task-required authoritative current sources plus runtime prompt/routes/decisions and targeted relevant history were checked; no self-disable requirement exists there, while the opposite rule is explicit. |
| DIAG-05 | **PASS** | Root cause classified as unsupported worker interpretation: invocation STOP was conflated with scheduler disable. |
| DIAG-06 | **PASS** | No Scheduled Task mutation was performed. |
| DIAG-07 | **PASS** | No Run now, workflow dispatch, scheduler creation, or production semantic processing was performed. |
| DIAG-08 | **PASS** | Minimal next-step class is stated above and was not applied. |
| DIAG-09 | **PASS** | This durable report is the only repository write authorized by the task; completion is claimed only after this exact committed report is reread from `main` before the final response. |

## Mutation ledger

Repository / external mutations performed by this diagnostic:

- **Allowed:** create this single durable report at `reviews/worker_reports/taste-dossier-scheduled-task-self-disable-ownership-diagnostic-01.md` on `main`.
- **Not performed:** Scheduled Task enable/disable/edit/delete/rename/recreate.
- **Not performed:** Scheduled Task prompt/cadence edit.
- **Not performed:** `Run now`.
- **Not performed:** scheduler creation.
- **Not performed:** GitHub workflow dispatch.
- **Not performed:** GitHub runtime/workflow/contract/state/work-manifest/inbox/cache changes.
- **Not performed:** Dossier semantic production work.
- **Not performed:** Progressive Fast/Deep mutation.
- **Not performed:** Chat 1 coalescing-liveness implementation/report changes.
- **Not performed:** historical `g000012` recovery/special-casing.

No repair is included in this report.

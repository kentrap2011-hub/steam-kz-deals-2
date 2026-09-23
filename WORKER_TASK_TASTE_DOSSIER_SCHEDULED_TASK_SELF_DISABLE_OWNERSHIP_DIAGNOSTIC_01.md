# WORKER TASK — TASTE DOSSIER SCHEDULED TASK SELF-DISABLE OWNERSHIP DIAGNOSTIC 01

## Assignment

- Worker slot: **NEW physical ЧАТ 2**
- Mode: **DIAGNOSTIC / READ-ONLY**
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Source of truth: `main`
- Expected durable report:
  `reviews/worker_reports/taste-dossier-scheduled-task-self-disable-ownership-diagnostic-01.md`

This is a separate diagnostic task. Do not use or modify another repository.

## START gate

Before investigating:

1. Read the current `CHAT_PROTOCOL.md` from `main` and execute its START gate.
2. Read this task fully.
3. Read the current canonical versions on `main` of:
   - `config/taste_steam_review_dossier_worker_prompt.md`
   - `config/taste_steam_review_dossier_contract.json`
   - `config/taste_steam_review_dossier_persistence_bridge.json`
   - `config/execution_ownership_contract.json`
4. Read only the additional current repository files/workflow definitions needed to trace scheduler/runtime ownership.
5. Do not begin any write, dispatch, scheduler mutation, production semantic work, or repair.

## Operator-observed problem

The existing scheduled production worker `Taste Steam Review Dossier` stopped with an ownership conflict: its runtime reasoning required the task to be disabled on a full block, while the current canonical Dossier ownership boundary appears to forbid the worker from enabling, disabling, or editing its own Scheduled Task.

The operator supplied the current live Scheduled Task prompt. Relevant clauses include:

- `If this live prompt ever conflicts with those current canonical repository files, ... follow the canonical repository contract and fail closed where required.`
- on create/write failure: `STOP immediately.`
- if the deterministic artifact for the current canonical expected group already exists while canonical progress has not advanced: `STOP.`
- scheduler ownership: `Do not modify or reinterpret the existing Scheduled Task title, schedule/cadence or production limits. Do not create another scheduler or recurring producer.`

The live prompt does **not** explicitly say that `STOP` means disabling the recurring Scheduled Task.

Treat the operator-supplied prompt as reported runtime evidence. If the exact live task configuration is directly inspectable, verify it; otherwise state that boundary explicitly and do not pretend to have verified it.

## Diagnostic objective

Determine exactly why the Dossier invocation concluded that a full block required disabling `Taste Steam Review Dossier`, and whether that requirement comes from:

1. a current canonical repository rule;
2. the live Scheduled Task prompt;
3. generic Scheduled Task / automation runtime semantics visible to the worker;
4. worker interpretation or an invented rule;
5. another identifiable external control layer.

Also determine the actual external Scheduled Task state **only if directly observable**: enabled/disabled, cadence unchanged or changed, and relevant last-run/status/error evidence. If the task/UI state is not accessible, report that as an evidence boundary and do not guess.

## Required investigation

### A. Canonical STOP semantics

Establish from current `main` whether Dossier `STOP` means:

- stop only the current invocation; or
- disable/suspend the recurring Scheduled Task.

Quote the exact controlling clauses and identify their files / current commit or blob evidence.

### B. Scheduler mutation ownership

Establish which actor, if any, is authorized to:

- enable the Dossier Scheduled Task;
- disable it;
- edit its title/prompt/cadence;
- create/delete/reconfigure recurring production scheduling.

Distinguish repository-owned control plane from external ChatGPT Scheduled Task operator actions.

### C. Exact origin of the conflicting self-disable requirement

Trace the exact rule/evidence that caused or could cause:

> full block => disable the Dossier Scheduled Task

Do not infer a source merely because such behavior would be convenient. Identify the clause/runtime instruction if it exists. If no such instruction exists in accessible authoritative sources, say so and classify the unsupported conclusion precisely.

### D. External task state

If directly accessible, record:

- whether exactly one relevant `Taste Steam Review Dossier` recurring task exists;
- whether it is enabled or disabled;
- configured cadence;
- whether title/prompt/cadence differ from the operator-supplied prompt expectations;
- relevant last-run/status/error evidence.

If direct access is unavailable, use status `needs_user_evidence` or `blocked_external_operator_state` as appropriate and specify the minimum exact UI evidence the operator must provide. Do not ask for unrelated screenshots or data.

### E. Minimal next-step classification

Recommend the smallest **class of fix** only, without applying it. Examples:

- no repo change; correct worker/runtime interpretation;
- canonical ownership wording needs clarification;
- live Scheduled Task prompt needs correction;
- external operator must re-enable/repair task;
- other specifically evidenced action.

Do not implement that fix in this task.

## Hard prohibitions

This task is read-only except for its own durable diagnostic report.

Do **not**:

- click or invoke `Run now`;
- enable, disable, edit, delete, rename, recreate, or otherwise mutate `Taste Steam Review Dossier`;
- edit its live Scheduled Task prompt/cadence;
- create another scheduler or recurring producer;
- dispatch GitHub workflows;
- alter GitHub runtime/workflows/contracts/state/work manifests/inbox/cache;
- alter Dossier candidate paths, identities, validators, recovery semantics, or production data;
- perform Dossier semantic evidence work;
- alter Progressive Fast or Deep behavior/state;
- touch the active ЧАТ 1 coalescing-liveness task, its report, branch, or implementation;
- recover or special-case historical `g000012`;
- perform any repair merely because the likely fix seems obvious.

## Validation gates

The report must explicitly mark each gate PASS / FAIL / BLOCKED with evidence:

- **DIAG-01** — current canonical/live meaning of `STOP` established: invocation stop vs scheduler disable.
- **DIAG-02** — current scheduler mutation ownership/authority established from canonical sources.
- **DIAG-03** — actual Scheduled Task state directly verified, or the external evidence boundary is explicitly proven.
- **DIAG-04** — exact origin of the self-disable requirement identified, or authoritative accessible sources exhaustively show no such requirement.
- **DIAG-05** — root cause classified as canonical rule / live prompt / runtime-system rule / worker interpretation / other evidenced layer.
- **DIAG-06** — no Scheduled Task mutation occurred.
- **DIAG-07** — no `Run now`, workflow dispatch, scheduler creation, or production semantic processing occurred.
- **DIAG-08** — minimal next-step fix class stated without applying it.
- **DIAG-09** — durable report committed to `main` and then reread exactly from `main`.

## Durable report requirements

Create:

`reviews/worker_reports/taste-dossier-scheduled-task-self-disable-ownership-diagnostic-01.md`

The report must include:

- final status;
- exact files/clauses and current commit/blob refs used;
- any directly observed external Scheduled Task evidence, clearly separated from assumptions;
- root-cause classification;
- conflict/no-conflict conclusion;
- DIAG-01..09 table;
- explicit mutation ledger proving read-only behavior;
- smallest recommended next step, not executed.

Allowed final statuses:

- `complete_root_cause_proven`
- `needs_user_evidence`
- `needs_fix`
- `blocked_external_operator_state`

Before claiming completion, commit the report to `main` and reread that exact report from `main`.

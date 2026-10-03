# WORKER TASK — Dossier frozen invocation rollover safety fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `dossier-frozen-invocation-rollover-safety-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `ЧАТ 2`

Durable report:
`reviews/worker_reports/dossier-frozen-invocation-rollover-safety-fix-01.md`

## Incident

A recent Dossier semantic invocation started from exact canonical snapshot:

`448f12da0193d4b5d43b65042e6e6826f39f571d1ae260055913ef11a3125f18`

sequence 1, group SHA:

`50ee28265629b1fd51275e9c27ddf34510a5443c65a875dd96b2b18a640e561e`.

It completed substantial exact-product and player-feedback research for the three bound games. Immediately before publication it re-read the current worker index and observed that GitHub had replaced the active daily snapshot with:

`a9a1390c7821fcc69c06f83e57c0297df0016e0d90e637ddccd7185d53bd8b19`.

Under the current runtime rule it stopped with:
- `stop_gate = snapshot_plan_or_binding_changed`;
- `publication_state = not_attempted`;
- zero canonical completion.

The semantic work was discarded solely because the daily snapshot changed during the invocation.

## User-approved architecture correction

Long-running ChatGPT semantic workers must be able to operate in parallel with GitHub canonical progress.

Once a Dossier invocation has frozen an exact legitimate GitHub-prepared work authority, unrelated later `main` movement or normal daily snapshot rollover must not by itself invalidate the already-started semantic computation.

This is analogous in principle to the already accepted Deep frozen-start authority architecture, but Dossier ownership/group semantics are different and must be designed explicitly rather than copied blindly.

## Important sequencing gate

A separate task `WORKER_TASK_PR_PRODUCTION_TRIGGER_ISOLATION_FIX_01.md` is being handled by ЧАТ 1.

The current repository has an unsafe PR -> production `workflow_run` edge until that fix is merged.

You MAY:
- diagnose;
- design;
- implement on a dedicated branch;
- run local/non-PR deterministic tests;
- commit/push the branch.

You MUST NOT open a pull request or intentionally trigger PR CI until current `main` contains the accepted PR-production-trigger isolation fix.

Immediately before opening the PR, re-read current `main` and prove that the unsafe trigger is fixed. If not, stop with implementation prepared but PR intentionally deferred.

## START gate

1. Read current `CHAT_PROTOCOL.md` and execute START gate fully.
2. Read current `DIRECTOR_TASK_BOARD.md`.
3. Read this task fully.
4. Read the current:
   - `config/taste_steam_review_dossier_runtime_prompt.md`;
   - `config/taste_steam_review_dossier_worker_prompt.md`;
   - `config/taste_steam_review_dossier_contract.json`;
   - persistence bridge;
   - execution ownership contract;
   - current Dossier work/index/descriptor machinery;
   - relevant TASTE-005 / later Dossier decisions;
   - accepted Deep frozen-start authority decision/report only as an architectural comparison.
5. Verify the incident and current stop rule from repository truth.
6. Reconcile with current `main` before any write.

Do not start another task.

## Problem to solve

Current Dossier supports non-blocking per-group progress, but the worker still requires the latest active daily snapshot/plan to remain the same through publication.

The daily rollover rule currently makes already-started work disposable.

That is too broad for the desired parallel architecture.

## Required architecture preflight

Before implementation, prove and record:

1. What exact GitHub-prepared identities make one Dossier group legitimate work?
2. What minimum immutable authority must be frozen at invocation/group start?
3. Which later changes are non-material and must NOT invalidate the frozen group?
4. Which later changes are material and must still fail closed?
5. How GitHub can prove an old frozen authority was genuinely prepared, rather than trusting a worker-supplied arbitrary historical snapshot.
6. How a result completed after daily rollover can be persisted without falsely claiming progress for an unrelated new snapshot/group.
7. How current/future snapshots can safely reuse the resulting dossier cache when exact semantic/evidence compatibility permits.
8. Why the design does not create a second queue, retry owner, scheduler, or ChatGPT-owned authority.

If this cannot be proven safely, stop with `needs_user_decision` rather than weakening stale-work protection.

## Required behavior

Implement the smallest GitHub-owned frozen-authority model satisfying all of the following:

### A. Freeze exact work authority

Before material semantic research for a group, establish/freeze an exact GitHub-prepared authority for that group.

The worker must not choose arbitrary historical work.

The authority must bind all fields material to semantic validity, including as applicable:
- snapshot/prepared scope identity;
- exact group descriptor identity;
- ordered items/appids;
- evidence/schema/worker bindings;
- exact product/work bindings;
- transport identity;
- trusted start/authority provenance.

### B. Later repository movement is not automatically invalidating

After the authority is frozen:
- unrelated `main` movement does not invalidate it;
- daily preparation of a new snapshot does not by itself invalidate it;
- new current queue ordering/group partitioning does not retroactively change the frozen group;
- the worker does not substitute new snapshot data into the in-flight group.

### C. Preserve material stale-work protection

Still fail closed when:
- the claimed authority was never genuinely GitHub-prepared;
- descriptor/binding identity is forged or mismatched;
- evidence/semantic contract compatibility materially changed in a way that makes the result invalid for current reuse;
- exact product identity is wrong;
- the frozen authority was already consumed/retired under a rule that forbids another submission;
- another exact transport already exists;
- the worker tries to rebind old semantic output to a new snapshot/group.

### D. Rollover-safe persistence

A valid result completed after snapshot A has been replaced by snapshot B must not be discarded solely due to rollover.

GitHub must be able to:
- validate the result against its genuine frozen A authority;
- persist valid neutral dossier content safely;
- keep A progress/history truthful;
- keep B progress truthful;
- reuse the persisted dossier in B/current/future work only when deterministic current compatibility permits;
- avoid repeating semantic research merely because the daily snapshot changed, when the produced dossier is still current and compatible.

Do not simply mark an arbitrary B group accepted based on an A group hash.

### E. No semantic attempt loss from rollover

A changed current snapshot after frozen authority establishment must not force:
- publication_state=not_attempted;
- discarded semantic work;
- a duplicate semantic attempt

unless a genuinely material compatibility condition makes the frozen result unsafe.

## Required regressions

Prove at minimum:

1. **Exact incident reproduction**
   - freeze snapshot A / group 1;
   - replace active projection with snapshot B before publication;
   - A result remains publishable/ingestible under frozen authority.

2. **Unrelated main movement**
   - unrelated canonical commit after freeze does not invalidate.

3. **Current snapshot partition changed**
   - B may have different group_count/order/group SHA;
   - A result is not naively rebound to B;
   - valid dossier content is preserved and reusable where exact compatibility permits.

4. **Evidence binding change**
   - old result is not treated as current-compatible when semantic/evidence binding changed materially.

5. **Forged historical snapshot/group**
   - worker cannot invent/select arbitrary old authority.

6. **Duplicate transport**
   - create-only/idempotent behavior remains safe.

7. **No false current progress**
   - accepting frozen A result cannot falsely mark unrelated B work accepted.

8. **No repeated research when compatible**
   - compatible current projection can consume/reuse the newly persisted dossier without another semantic web-research run.

9. Existing failed-group recovery/nonblocking traversal remains correct.

10. Deep/Fast independence and GitHub ownership remain unchanged.

## Production safety

Do not run the real Dossier backlog as implementation validation.

Do not create/modify/run ChatGPT Scheduled Tasks.

Use deterministic tests and existing GitHub validation workflows after the PR-trigger isolation task is confirmed on `main`.

## PR / merge

Dedicated branch and PR.

Do not open PR before the sequencing gate above is satisfied.

Before merge:
- sync with latest `main`;
- run affected Dossier contract/runtime/persistence/backlog/ownership validations;
- verify no current PR can trigger production unexpectedly;
- merge only with required checks green.

## Durable report

Write `reviews/worker_reports/dossier-frozen-invocation-rollover-safety-fix-01.md`.

Required sections:
1. Task
2. Incident reproduction
3. Architecture preflight
4. Root cause
5. Frozen authority model
6. Rollover-safe persistence semantics
7. Current-snapshot reuse semantics
8. Changes
9. Regression coverage
10. Validation
11. Production safety
12. Exact PR/commit/run refs
13. Unresolved
14. Status
15. Recommended next step — exactly one bounded action

Allowed statuses:
- `implementation_complete_ready_for_director_acceptance`
- `implementation_prepared_waiting_for_trigger_isolation`
- `needs_user_decision`
- `blocked`

## Hard boundaries

Do NOT:
- accept arbitrary old snapshots;
- rebind an old group hash to a new group;
- weaken exact-product/evidence/schema validation;
- make ChatGPT own current scope/order/retry/completeness;
- create another scheduler/queue/retry daemon;
- modify Fast/Deep semantics;
- modify canonical Taste profile/scoring;
- run production Dossier;
- create or modify ChatGPT Scheduled Tasks;
- open PR before the trigger-isolation sequencing gate is satisfied;
- start another task.

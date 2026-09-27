# WORKER TASK — PROGRESSIVE DEEP PARALLEL FROZEN START AUTHORITY FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2` for this task;
- do not search, read, modify, or use another repository;
- if GitHub/tool opens another repository by default or the target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `progressive-deep-parallel-frozen-start-authority-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/progressive-deep-parallel-frozen-start-authority-fix-01.md`

## User-approved architecture correction

The user has explicitly corrected the intended runtime behavior:

- Dossier and Deep are independent stages and must be able to run in parallel.
- When a Deep invocation starts, it freezes the exact GitHub-prepared Deep work and all exact inputs/bindings needed for that invocation.
- That invocation must continue against that frozen immutable view.
- Canonical Dossier/profile/work/progress changes written after the invocation has frozen its start view belong to the next invocation.
- Such later concurrent GitHub writes must not retroactively invalidate or cancel an already-started Deep invocation merely because `main` advanced.
- The anti-race protection must remain, but it must protect the exact frozen Deep authority, not require the entire repository head to remain unchanged during startup.

Observed production symptom:
- Deep read/froze an `observed_main_commit`;
- Dossier was running concurrently and `main` advanced before the run-start marker became durable;
- GitHub rejected the marker as superseded;
- Deep published nothing and consumed no attempt.
- This behavior is now considered architecturally incorrect when the intervening change does not invalidate the exact frozen Deep work authority.

## Canonical architecture that must be preserved

Current repository decisions already state:
- Fast / Dossier / Deep are independent stages.
- Deep uses one frozen invocation view.
- Dossier/profile/recovery/work changes after the established invocation boundary belong to the next invocation and must not trigger retroactive invalidation.
- GitHub remains the control-plane owner of Deep scope/order/authorization/attempts/recovery/completeness/persistence.
- Scheduled ChatGPT remains only the bounded semantic worker.
- No second scheduler, queue, retry daemon or backlog manager may be created.

The current `PPD-006` / `PPD-007` run-start mechanism still rejects a marker when the marker commit's actual parent is no longer the exact previously observed `main` commit. This task must reconcile that mechanism with the user-approved parallel independence rule rather than weakening all stale-work protection.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully and make the required task checklist.

Read minimally:
1. `CHAT_CONTEXT.md`;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. `PROJECT_ROUTES.md` Progressive Fast / Dossier / Deep route;
4. `PROJECT_DECISIONS.md#PPD-004`, `#PPD-006`, `#PPD-007`;
5. `config/execution_ownership_contract.json`;
6. `config/progressive_pass2_contract.json`;
7. `config/progressive_pass2_worker_prompt.md`;
8. only the exact run-start / ingest / validation files needed to prove and implement the correction.

Do not reconstruct unrelated project history.

## Architecture preflight — mandatory before writes

Prove and record:
1. which exact component owns Deep start authority;
2. which exact immutable identities already define one prepared Deep invocation;
3. why whole-`main` equality is stronger than the business requirement for independent parallel stages;
4. how the replacement rule proves that a worker cannot arbitrarily revive stale/unprepared historical work;
5. why concurrent unrelated or later canonical writes cannot invalidate an already-frozen valid Deep invocation;
6. why the proposed design does not move control-plane authority to ChatGPT.

If any of these cannot be proven from current canonical contracts/state, stop and report `needs_user_decision` rather than inventing authority.

## Required behavior

Implement the smallest canonical correction satisfying all of these:

### A. Frozen start view

At invocation start, Deep must freeze one exact GitHub-prepared view including all inputs material to that invocation, including as applicable:
- Deep work identity/order;
- immutable profile pin;
- exact accepted Dossier identity/content/binding used by each authorized item;
- recovery authorization identity/reason when applicable;
- exact result/receipt paths and other immutable bindings required by the current contract.

The worker must not choose or rebuild scope.

### B. Parallel repository movement

After that exact invocation view has been frozen, later `main` movement alone must not reject the invocation.

Explicit regression case:
1. Deep freezes valid prepared authority A.
2. Before its start marker/confirmation becomes durable, Dossier or another canonical writer advances `main` to B.
3. The frozen Deep authority A is still a legitimate invocation authority under the corrected contract.
4. Deep may continue/publish results bound to A after GitHub confirms the exact frozen authority.
5. The new Dossier/work state from B is visible only to a later Deep invocation.

### C. Preserve stale-work protection

Do NOT replace the current rule with "accept any old commit".

GitHub must still fail closed when the claimed frozen authority:
- was never a valid GitHub-prepared Deep authority;
- does not exactly match its frozen work/profile/Dossier/recovery bindings;
- has malformed/forged identity or lineage;
- is already canonically consumed/retired in a way that current contracts forbid;
- attempts to use a different work unit than the one actually frozen for the invocation;
- otherwise violates canonical eligibility/authorization rules that are material to the start authority.

The exact replacement proof may use a more specific immutable prepared-work/authorization identity rather than whole-repository head equality. Choose the smallest design consistent with current architecture.

### D. One invocation remains immutable

Once GitHub has confirmed the corrected frozen start authority:
- later Dossier/profile/work/recovery changes do not invalidate that invocation;
- no per-item mutable reread is added;
- no sibling-ingest wait is restored;
- results remain bound to the exact frozen authority;
- changes become input only to the next invocation.

### E. Publication guard remains real

Do not remove the GitHub-owned publication guard.

Before the first Deep result or terminal execution receipt becomes publishable, GitHub must have durably confirmed the exact frozen invocation authority under the corrected rule.

A missing/rejected/mismatched confirmation still publishes nothing and consumes no attempt.

## Implementation requirements

If current canonical decisions explicitly encode the incorrect whole-`main` equality as architecture, amend the canonical decision/contract first, then align implementation and worker prompt.

Expected areas may include, but are not prescribed:
- `PROJECT_DECISIONS.md`;
- `PROJECT_ROUTES.md`;
- `config/progressive_pass2_contract.json`;
- `config/execution_ownership_contract.json`;
- `config/progressive_pass2_worker_prompt.md`;
- exact PASS 2 run-start/ingest logic;
- focused regressions.

Do not change unrelated Dossier semantics or Fast semantics.

## Required regressions

Prove at minimum:

1. **Concurrent Dossier success**
   - freeze exact valid Deep invocation A;
   - advance `main` with a canonical Dossier-related change before marker confirmation;
   - confirmation succeeds for A;
   - result bound to A is accepted;
   - newer Dossier state is not silently substituted into A.

2. **Unrelated GitHub write success**
   - same as above with an unrelated canonical repository change;
   - whole-head movement alone does not reject valid A.

3. **Material binding mismatch rejection**
   - change or forge an exact bound input/identity;
   - confirmation/result fails closed.

4. **Arbitrary historical authority rejection**
   - worker cannot select an old valid-looking Deep work unit that was not the invocation's current prepared/frozen authority.

5. **No retroactive substitution**
   - after A is confirmed, newer Dossier/profile/work state cannot be mixed into A's results.

6. **Missing/rejected confirmation**
   - still no result/terminal publication and zero attempt.

7. Existing asynchronous sibling traversal remains non-blocking.

8. Fast/Dossier/Deep independence tests remain green.

9. No new scheduler/queue/retry/backlog owner is introduced.

## Production acceptance

Do not manually process the Deep backlog as validation.

Use focused tests and existing GitHub validation workflows. If safe and naturally available, observe a subsequent normal Deep invocation, but do not trigger or modify any ChatGPT Scheduled Task unless separately authorized by the user.

A fix is not complete merely because the superseded rejection is suppressed. It is complete only if GitHub can prove the exact frozen authority while allowing legitimate parallel repository progress.

## Hard prohibitions

Do not:
- disable or bypass Deep run-start confirmation entirely;
- accept arbitrary stale commits;
- make ChatGPT the authority for freshness/eligibility/scope;
- reread mutable current Dossier/profile/work between Deep items;
- serialize Dossier and Deep as a workaround;
- pause Dossier to make Deep start;
- add a second queue/scheduler/retry loop;
- change any ChatGPT Scheduled Task;
- manually process production Deep backlog;
- change Dossier evidence semantics or recovery policy;
- change Fast prerequisites.

## Report

Write:
`reviews/worker_reports/progressive-deep-parallel-frozen-start-authority-fix-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Verified root cause`
4. `Corrected authority model`
5. `Changes`
6. `Validation`
7. `Production observations`
8. `Unresolved`
9. `Status`
10. `Recommended next step` — exactly one bounded next step
11. exact PR/commit/run refs
12. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another project task after this one.

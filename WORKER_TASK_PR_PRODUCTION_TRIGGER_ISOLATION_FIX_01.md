# WORKER TASK — PR production trigger isolation fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `pr-production-trigger-isolation-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `ЧАТ 1`

Durable report:
`reviews/worker_reports/pr-production-trigger-isolation-fix-01.md`

## Incident

On 2026-10-03 a pull-request validation run of `Steam KZ production shortlist` completed successfully for PR #140.

That PR-only validation unexpectedly triggered the production chain:

- PR `Steam KZ production shortlist` success;
- `Build mailing-optimized feed` via `workflow_run`;
- `Build pre-AI deterministic payload`;
- a new canonical Dossier snapshot was committed to `main`.

Observed run chain:
- PR shortlist run: `37119438688`, completed 2026-10-03T11:23:15Z;
- mailing run: `37119485890`, created 2026-10-03T11:23:17Z;
- pre-AI run: `37119499934`, created 2026-10-03T11:23:30Z;
- pre-AI commit: `7361a45644055276305347eb621ff8a5a8d1c9e3` at 2026-10-03T11:24:09Z.

The current `.github/workflows/build-mailing-feed.yml` listens to successful `Steam KZ production shortlist` workflow runs but does not require the triggering run to belong to `main`.

This allowed a PR validation to mutate production.

## Goal

Ensure pull-request validation can never start a production-mutating workflow chain.

Production downstream `workflow_run` consumers must only run from explicitly authorized production-source runs, normally successful runs on `main`.

Do not disable PR validation itself.

## START gate

1. Read current `CHAT_PROTOCOL.md` and fully execute START gate.
2. Read current `DIRECTOR_TASK_BOARD.md`.
3. Read this task fully.
4. Inspect the current workflow trigger graph starting from:
   - `Steam KZ production shortlist`;
   - `Build mailing-optimized feed`;
   - `Build compact feed ingest validation`;
   - `Build pre-AI deterministic payload`;
   - downstream visual/publication workflows.
5. Verify the incident from current workflow configuration and GitHub run metadata before implementation.
6. Reconcile with current `main` immediately before writing.

Do not start another task.

## Required diagnosis

Answer explicitly:

1. Which exact `workflow_run` edge allowed PR #140 validation to enter production?
2. Why did its downstream workflow check out and mutate `main`?
3. Which other production-mutating `workflow_run` consumers have the same or an equivalent missing source-branch/source-event guard?
4. Which consumers already correctly require `head_branch == main` or an equivalent production authority?
5. What exact condition should define an authorized upstream production run?

Do not patch only the observed file if an equivalent unsafe edge exists elsewhere.

## Required behavior

After the fix:

- pull-request runs remain available for validation;
- a successful PR run must not trigger any workflow that writes canonical production state to `main`;
- a successful authorized production run on `main` must continue to trigger the intended downstream chain;
- manually authorized production `workflow_dispatch` behavior must remain as currently designed;
- existing scheduled production behavior must remain as currently designed;
- no production workflow may infer authority merely from the upstream workflow name plus `conclusion == success`;
- downstream jobs must fail closed / skip when the triggering run is from a PR branch or otherwise not an authorized production source.

Prefer the smallest explicit guard consistent with existing architecture. Do not create a second scheduler or duplicate workflow chain.

## Required audit

Audit all `workflow_run`-based production-mutating workflows in the repository.

For each relevant edge classify:
- safe and why;
- unsafe and fixed;
- non-production/read-only and therefore out of scope.

Avoid unrelated workflow cleanup.

## Required regression

Add deterministic validation proving at minimum:

1. successful upstream run with `head_branch=main` follows the production path;
2. successful upstream PR branch run is skipped;
3. failed/cancelled upstream run is skipped;
4. direct allowed production triggers remain functional;
5. the PR #140 incident shape cannot recur;
6. no PR-only validation can cause a canonical `main` write through the audited downstream chain.

If repository workflow-test conventions exist, use them rather than inventing a new framework.

## Safety while this task itself is being implemented

The current unsafe trigger still exists until this fix reaches `main`.

Therefore:
- do not run Dossier/Deep or other semantic production workers as validation;
- do not manually dispatch production workflows;
- expect that opening/rerunning this PR may itself produce one final unwanted downstream production trigger under the pre-fix default-branch workflow;
- minimize unnecessary PR reruns before the guard lands;
- never manually edit production data to compensate.

## PR / merge

Use a dedicated branch and PR.

Immediately before merge:
- synchronize with current `main`;
- rerun all directly affected workflow/ownership validations;
- verify the production-source guard is present on current PR head;
- merge only with required checks green.

## Durable report

Write `reviews/worker_reports/pr-production-trigger-isolation-fix-01.md` with:

1. Task
2. Incident reconstruction
3. Unsafe edge
4. Workflow-run audit
5. Fix
6. Regression coverage
7. PR self-trigger safety note
8. Validation
9. Exact PR/commit/run refs
10. Status
11. Recommended next step — exactly one bounded action

Allowed final statuses:
- `implementation_complete_ready_for_director_acceptance`
- `blocked`
- `diagnosed_needs_different_fix`

## Hard boundaries

Do NOT:
- disable PR validation;
- remove legitimate production scheduling;
- create a second production chain;
- modify ChatGPT Scheduled Tasks;
- run semantic workers;
- manually mutate production data;
- implement the Dossier rollover/frozen-authority fix in this task;
- start another task.

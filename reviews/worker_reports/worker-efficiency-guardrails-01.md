# Worker efficiency guardrails 01

### Task

Implemented only the minimal durable process mechanism from `reviews/worker_reports/worker-efficiency-audit-01.md`; the audit was not repeated.

Changes are operational documentation only:
- created `KNOWN_WORKER_PITFALLS.md` with exactly the three audit-proven reusable recipes;
- added minimal conditional START/PRE-SEND hooks and Recommended-next-step architecture preflight to `CHAT_PROTOCOL.md`;
- added the one-line conditional efficiency field to worker reports in `DIRECTOR_PROTOCOL.md`.

### Changes

- `KNOWN_WORKER_PITFALLS.md`
  - commit `7844d32a9728047f676b5085c9b297616d0cb464`;
  - exactly three seeds: behavioral outcome vs source-shape proxy; GitHub Pages concurrency/already-uploaded artifact rerun; architecture/source authority before recommending IMPLEMENT.
- `CHAT_PROTOCOL.md`
  - commit `7f5b239183e3fb3f8e5e02a35e1901b59d17042f`;
  - START reads only a relevant pitfall entry when a known trigger matches and explicitly avoids broad pitfall/history reading for unrelated work;
  - PRE-SEND persists reusable lessons to routes/decisions/pitfalls, or names an exact candidate in a read-only report;
  - architecture preflight now explicitly covers `Recommended next step` for source/runtime/workflow/schedule/queue/retry/checkpoint/ownership changes and requires `RECON`/`CONTRACT` instead of `IMPLEMENT` when canonical authority/route is unproven.
- `DIRECTOR_PROTOCOL.md`
  - commit `c04e3d73e3d827115a1abfea9526211dc0b711da`;
  - added `Efficiency / reusable lesson` as one compact report line: `none` for normal tasks, otherwise only a short candidate/ref; explicitly not a narrative section or essay.
- `reviews/worker_reports/worker-efficiency-guardrails-01.md`
  - this report only.

### Validation

- Current `KNOWN_WORKER_PITFALLS.md` clearly separates responsibilities:
  - `PROJECT_ROUTES.md` = where/how to navigate;
  - `PROJECT_DECISIONS.md` = why a non-obvious product/architecture decision exists;
  - `KNOWN_WORKER_PITFALLS.md` = reusable cross-cutting operational failure recipe.
- Current pitfalls file contains exactly three `## PITFALL-*` entries and explicitly says not to use the file as a generic troubleshooting diary.
- Current `CHAT_PROTOCOL.md` START says to check only the relevant pitfall entry for a matching trigger and explicitly says unrelated tasks must not read the entire file or perform broad pitfall/history search.
- Current PRE-SEND explicitly covers a worker's `Recommended next step`: if it would add/change source/runtime/workflow/schedule/queue/retry/checkpoint/ownership, architecture preflight must already be complete; unproven authority/route leads to bounded `RECON`/`CONTRACT`, not `IMPLEMENT`.
- Current `DIRECTOR_PROTOCOL.md` contains exactly the requested compact conditional report field and keeps it one line.
- `PROJECT_ROUTES.md` and `PROJECT_DECISIONS.md` were re-read only for boundary consistency; neither was changed.
- Exact implementation-commit file lists prove no product/runtime behavior changed:
  - `7844d32...` changed only `KNOWN_WORKER_PITFALLS.md`;
  - `7f5b239...` changed only `CHAT_PROTOCOL.md`;
  - `c04e3d73...` changed only `DIRECTOR_PROTOCOL.md`.
- No product code, production workflow/schedule, telemetry, time tracking, quota, dashboard, performance score, report-path automation, new CI workflow, or acceptance weakening was added.
- `main` advanced concurrently with unrelated Chat 1 work between these commits; those unrelated commits are not part of this worker's implementation. The exact per-commit file lists above isolate this task's changes.

Efficiency / reusable lesson: none

### Status

complete

### Recommended next step

none

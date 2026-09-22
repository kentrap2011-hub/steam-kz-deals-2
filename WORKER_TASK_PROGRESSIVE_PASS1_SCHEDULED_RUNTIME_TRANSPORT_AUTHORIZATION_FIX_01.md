# WORKER TASK — Progressive PASS 1 Scheduled Runtime Transport Authorization Fix 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: progressive-pass1-scheduled-runtime-transport-authorization-fix-01
Mode: IMPLEMENT / ACTIVATE / VALIDATE
Worker slot: СУЩЕСТВУЮЩИЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2

## START

First open the current CHAT_PROTOCOL.md from main and complete its START gate.
Then open this task from main.
Use current canonical contracts/prompts/ownership files as source of truth.

Direct continuation of:
- WORKER_TASK_PROGRESSIVE_PASS1_CREATE_ONLY_ENVIRONMENT_REJECTION_DIAGNOSTIC_01.md
- reviews/worker_reports/progressive-pass1-create-only-environment-rejection-diagnostic-01.md

Do not repeat the broad diagnosis.

## Accepted diagnosis

The Bear and Breakfast create-only operation is repository-contract-valid and has no current GitHub-side collision/blocker.
The narrowest proven failure boundary is the Scheduled-runtime/platform/tool write-authorization layer before GitHub mutation.
The prior self-disable of the PASS 1 Scheduled Task was unauthorized.

## Goal

Restore the existing Progressive PASS 1 Scheduled worker's legal create-only GitHub transport and harden the live entrypoint so a failed invocation stops only that invocation and never disables/edits its own schedule.

Do not change PASS 1 semantic rules, work ordering, attempt policy, retry policy, state ownership, result schema, or GitHub control-plane ownership.

## Required work

1. Inspect the current existing Progressive PASS 1 Scheduled Task/live entrypoint configuration and the effective connected GitHub write path/permission surface available to that Scheduled runtime.
2. Compare the current failing transport authorization/binding to the previously successful PASS 1 create-only path.
3. Restore only the missing/incorrect runtime/tool authorization or binding needed for the canonical create-file action to the exact GitHub-prepared submission path on main.
4. Do not replace the canonical GitHub create-only transport with shell, workflow dispatch, alternate files, update/overwrite, manual state edits, or another scheduler.
5. Harden the live Scheduled Task entrypoint/loader so it explicitly forbids enabling/disabling/editing its own schedule. On any blocked write it must stop the current invocation only.
6. Preserve the user's hourly cadence. Do not change the cadence to another interval.
7. After the transport fix is in place, perform exactly one bounded manual acceptance run against the current canonical PASS 1 head.
8. The acceptance run must follow the current manifest. If Bear and Breakfast is still head, use it; if canonical state legitimately advanced before validation, use the then-current head without inventing work.
9. Validate:
   - create-only artifact reaches GitHub;
   - canonical ingest/validation consumes it normally;
   - accepted PASS 1 state/progress advances;
   - no skip/reorder/extra retry/PASS 2 occurs;
   - Scheduled Task remains enabled after the run;
   - hourly cadence remains configured.
10. If the platform permission/binding cannot be inspected or changed with available authorized tooling, fail closed. Do not invent a repository workaround. Record the exact remaining operator action/evidence needed.

## Boundaries

- Do not change PASS 1 contract semantics.
- Do not change PASS 2.
- Do not change Dossier.
- Do not change queue ordering or attempt budgets.
- Do not create alternate result paths.
- Do not manually edit canonical PASS 1 state.
- Do not process more than the single bounded acceptance run.
- Do not create another Scheduled Task.

## Acceptance checks

- FIX-01: exact live Scheduled Task/entrypoint identified.
- FIX-02: write-authorization/binding cause fixed or precisely proven externally blocked.
- FIX-03: canonical create-only GitHub transport preserved.
- FIX-04: self-disable/edit-schedule behavior explicitly forbidden in live entrypoint.
- FIX-05: hourly cadence preserved.
- FIX-06: one bounded acceptance run only.
- FIX-07: accepted PASS 1 progress advances if runtime fix succeeds.
- FIX-08: no PASS 2 or unrelated production mutation.
- FIX-09: Scheduled Task remains enabled after successful acceptance.
- FIX-10: no repository-side workaround masks an unresolved platform authorization failure.

## Durable report

Create and commit:
reviews/worker_reports/progressive-pass1-scheduled-runtime-transport-authorization-fix-01.md

Keep it compact. Include:
- exact runtime/entrypoint configuration changed;
- exact transport authorization/binding fix;
- self-disable hardening;
- one acceptance run result;
- resulting current PASS 1 head/counts if available;
- enabled/hourly state after validation;
- FIX-01..10;
- exact refs;
- unresolved;
- final status;
- exactly one recommended next step.

Allowed statuses:
- complete_ready_for_director_acceptance
- blocked_external_operator_action
- needs_fix
- needs_user_decision

Before final response, commit the report and reread the exact report from main.

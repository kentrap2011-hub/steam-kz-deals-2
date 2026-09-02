# SYSTEM AUDITOR ROLE

Independent periodic review role for project `kentrap2011-hub/steam-kz-deals-2`.

## Purpose

The auditor looks at the system from the outside and asks whether the project actually delivers the intended user result, not merely whether individual components satisfy their local contracts.

Core question:

> Does the whole production system reliably produce the right user-visible result, and what important failure modes are currently invisible?

## Scope

The auditor may inspect bounded current production evidence, compact reports, current workflows/contracts and a small representative sample.

The auditor should actively look for:
- user-visible omissions despite locally passing stages;
- automations that are queued but not actually running;
- missing completion monitoring;
- stale/incomplete data that silently degrades results;
- duplicated mechanisms or ownership confusion;
- fail-open or overly broad fail-closed behavior;
- tests that validate source shape instead of behavioral outcome;
- pipelines that succeed technically but fail the real user goal;
- unnecessary complexity that increases operational risk;
- assumptions that were once true but are no longer verified.

## Hard boundaries

The auditor does NOT:
- implement fixes;
- redesign the whole architecture;
- perform broad Git-history archaeology;
- produce dozens of speculative improvements;
- replace the Director;
- replace the Taste Reviewer;
- judge personal game taste except where a system mechanism claims to represent it.

## Output discipline

Maximum 5 significant findings per audit.

Each finding must include:
- concrete user impact;
- evidence;
- severity;
- whether it is proven or only a risk hypothesis;
- one bounded verification or fix candidate.

At the end, recommend at most 2 tasks to the Director.

Reports:
`reviews/system_audits/<audit-id>.md`

## Mandatory trigger rules

A System Audit becomes due when ANY of the following is true:

1. **First scheduled checkpoint:** both currently active September 2 tracks reach a stable boundary:
   - Trine 4 runtime/start/completion-control investigation has a saved report and Director decision;
   - giveaway IGDB continuation is either implemented or explicitly blocked on the user's secret-provisioning step.
   Before starting another ordinary backlog implementation after that point, run the first System Audit.

2. **Production-change cadence:** 3 material production IMPLEMENT/ACCEPTANCE changes have been closed since the previous System Audit. A material change is one that affects selection, ranking, identity, semantic analysis, external-data readiness, queue/runtime ownership, or user-visible feed behavior.

3. **Incident trigger:** the user finds an unexpected missing/incorrect game, giveaway, ranking result, or apparently automatic process whose actual execution/completion was not being observed. Run an audit after the immediate incident is stabilized, unless the last audit already covered that exact failure class.

4. **Architecture trigger:** a new queue, scheduler, external provider, identity authority, ranking gate, semantic runtime or canonical ownership boundary is introduced. Audit it after acceptance before treating the architecture as settled.

## Forget-prevention rule

The Director must check `DIRECTOR_REVIEW_CHECKPOINTS.md` before choosing a new ordinary backlog task whenever a worker slot becomes free.

If `system_audit_due: true`, the audit takes priority over normal backlog unless the user explicitly gives a more urgent time-sensitive task.

Completing an audit must update the checkpoint file with the report ref and reset the material-change counter.
# WORKER TASK — DIRECTOR ORCHESTRATION PHASE 2B LIVE READ-ONLY PILOT 01

Task ID: `director-orchestration-phase2b-live-readonly-pilot-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`
Priority: `VERY_HIGH_INFRASTRUCTURE_PRIORITY`

## Gate

DO NOT START until the user has confirmed that repository Actions secret `OPENAI_API_KEY` exists in `kentrap2011-hub/steam-kz-deals-2`.

Never ask for or inspect the secret value.

## Context

Phase 1 shadow orchestration: independently accepted.

Phase 2A security/state/cloud-worker boundary:
- implementation: `reviews/worker_reports/director-orchestration-phase2a-security-boundary-implement-01.md`
- independent audit: `reviews/system_audits/director-orchestration-phase2a-audit-01.md`
- closure: accepted.

The audit authorizes one separately enabled bounded live READ-ONLY cloud-worker pilot only. Autonomous IMPLEMENT remains forbidden.

## Goal

Enable and execute exactly one real cloud `READ_ONLY_RECON` pilot through GitHub-hosted Actions + pinned official Codex Action, while preserving all accepted Phase 2A invariants.

The pilot task is exactly:
`WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`

Expected worker report:
`reviews/worker_reports/epic-ru-availability-source-probe-01.md`

The pilot is chosen because it is already queued, READ-ONLY, independent of current Taste implementation, and was the exact Phase 2A staging candidate.

## Required current-state reconciliation before enabling

Before any live dispatch:

1. Reconcile `orchestration/state.json` with current Director truth.
2. Current manual Chat 1 task must be represented as external/manual occupancy if still active:
   `reconsideration-commercial-bridge-and-wishlist-implement-01`.
3. Do not treat the old `play-role-and-start-priority-implement-01` occupancy as current if it has completed.
4. Preserve exactly two logical slots.
5. Bind the pilot to current exact task revision, task-file blob SHA, current/base SHA, expected report path and attempt identity.
6. Use the single authoritative controller/state-writer path only.

If current state cannot be reconciled unambiguously, fail closed and do not dispatch.

## Critical Phase 2B stale/concurrency barrier

Implement the audit-required optimistic-concurrency/current-state barrier before publication.

A report may be published only if, immediately before commit/push:
- current authoritative state still contains the same task revision/attempt/lease;
- lease is still active and unexpired;
- exact task file/blob/base/report bindings still match;
- no newer state revision invalidates the result;
- expected report path is still the only allowed repository mutation;
- compare-and-swap / expected-head or equivalent fail-closed protection prevents a concurrent state advance from accepting stale output.

If the repository/state advances concurrently, reject the result and leave the pilot unaccepted rather than publishing stale output.

## Live worker security boundary

The real LLM/Codex job must preserve accepted Phase 2A constraints:

- GitHub-hosted runner;
- only `READ_ONLY_RECON` / `AUDIT` cloud modes are valid;
- this pilot is `READ_ONLY_RECON` only;
- official immutable action pin exactly:
  `openai/codex-action@86365089eb2b84e0a8fb0717b304f8bdcb13b20e`;
- checkout exact bound base SHA;
- `persist-credentials: false` in worker job;
- worker permissions `contents: read` only;
- only `OPENAI_API_KEY` exposed to Codex worker step;
- no Steam/provider secrets;
- no GitHub write credential in the LLM job;
- permission profile read-only;
- drop-sudo safety strategy;
- no state/product/repository mutation authority;
- worker cannot choose next task;
- structured result only.

Trusted publisher remains a separate deterministic job/path and may write exactly the expected worker report path only after all bindings/stale checks pass.

## Dispatch scope

Enable live dispatch narrowly enough that this task can execute exactly one pilot attempt.

Do NOT create a general always-on autonomous dispatcher in this task.
Do NOT automatically fill another slot after the pilot completes.
Do NOT dispatch more than the exact Epic RU source-probe task.

After the one pilot attempt, leave the system in a safe state where further automatic dispatch requires Director review/next bounded phase.

## Required live evidence

Run the real pilot and capture exact:
- controller/state transition commit/ref;
- dispatch workflow run/job;
- Codex worker job conclusion;
- trusted publisher job conclusion;
- resulting report commit/path if published;
- attempt ID and lease ID;
- base SHA/task-file blob SHA/report binding;
- proof the LLM job had no GitHub write authority;
- proof no product/state file was mutated by the worker/publisher other than controller-authorized orchestration state transitions and the exact report publication path;
- API/Codex errors if any, without leaking secret material.

## Pilot success criteria

A successful pilot means:
1. one real Codex READ_ONLY_RECON worker ran;
2. exact expected durable report was produced and trusted-published;
3. stale/current-state barrier passed;
4. no unauthorized mutation occurred;
5. max-two-slot/manual occupancy invariant held;
6. report can be read later by Director without the user manually relaying worker output;
7. no second worker or IMPLEMENT task was auto-dispatched.

If the Codex/API call fails because of billing/quota/key/model availability, report `blocked` with exact non-secret failure evidence. Do not weaken security to make it pass.

## Required tests

Before live dispatch, deterministic tests must prove at minimum:
- current manual occupancy migration/reconciliation;
- stale report rejected after concurrent state revision change;
- stale report rejected after lease expiry;
- expected-head/CAS conflict fails closed;
- wrong report path rejected;
- worker has no write credentials;
- exact pilot only can dispatch;
- second automatic dispatch is disabled;
- IMPLEMENT remains structurally excluded.

## Boundaries

Do NOT:
- expose/log/commit `OPENAI_API_KEY`;
- automate IMPLEMENT;
- alter Taste/product logic;
- enable general autonomous queue draining;
- dispatch a second task;
- broaden worker permissions;
- expose additional secrets;
- bypass stale/current-state checks;
- let Codex commit/push directly;
- let the publisher write state/product files;
- create more than two slots.

## Done when

Save:
`reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`

Include:
1. Status
2. Secret-presence gate result (presence only, never value)
3. Files/contracts/workflows changed
4. Current-state/manual occupancy reconciliation
5. Optimistic-concurrency/stale barrier
6. Exact pilot task binding
7. Tests
8. Live dispatch run/job refs
9. Codex worker result
10. Trusted publisher result
11. Attempt/lease/base/blob/report refs
12. Exact resulting worker report path/commit if published
13. Proof no unauthorized write or second dispatch occurred
14. Whether Phase 2B pilot succeeded
15. One bounded next step only

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`

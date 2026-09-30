# WORKER TASK — Deep invalid not-fit contract loop fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `deep-invalid-not-fit-contract-loop-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Planned worker slot: `ЧАТ 1 after DEEP_SCORE_EVIDENCE_EXPLAINABILITY_ALIGNMENT_01 is accepted`

Durable report:
`reviews/worker_reports/deep-invalid-not-fit-contract-loop-fix-01.md`

## Dependency / start condition

DO NOT START implementation while PR #128 / `WORKER_TASK_DEEP_SCORE_EVIDENCE_EXPLAINABILITY_ALIGNMENT_01.md` is still active.

This task touches the same Deep prompt/schema/contract/ingest surfaces.

At task start:
1. read current `CHAT_PROTOCOL.md` and fully execute START gate;
2. verify PR #128 is merged/closed and refresh from current `main`;
3. read the accepted worker report for the Deep score-evidence alignment;
4. reconcile this task against the new canonical Deep contract before editing.

If PR #128 is still active, stop cleanly without implementation.

## User-reported production defect

Repeated Progressive Deep invocations processed the same games again:

- Five Dates / AppID 1353270 / work_id `1379906886119f0bcd8b2d764fa7ce663140ada66a7da03ec1dd08176679773b`
- Her New Memory - Hentai Simulator / AppID 1296770 / work_id `a349c27f3663446a76886e22218455525bc43a2428278ca450257ad916f6239a`
- Blazing Sails / AppID 1158940 / work_id `ddb33cb3665250557120ce1deaa1af3f23fe213fd96119e7335f5d17a9c01fe9`

Latest repeated invocation:
- run-start anchor: `4d1a1c573289358713897559e79b754907ff91c8`
- frozen authority: `ab9f5f1c841b9c6d40ace1932c7d32437763eb8a`
- submitted result commits ended at `911e1b1e00fdc5dbed1bff3d9e3f0148a18c58ac`

All three submitted:
- `outcome = analyzed_not_fit`
- `not_fit_basis = confirmed_personal_negative`
- `confidence = medium`

GitHub ingest rejected all three with:
`confirmed personal negative requires high confidence`

Rejection disposition:
`rejected_invalid_result_no_attempt`

Because invalid results consume no first-pass attempt and current work remains ordinary eligible work, the same exact work IDs reappear in the next frozen manifest and are semantically reprocessed again.

Historical commit evidence shows this happened across multiple invocations, not just the latest two.

## Root contract mismatch already verified

Current canonical layers are inconsistent:

1. Worker prompt requires for `analyzed_not_fit + confirmed_personal_negative`:
   - completed negative assessment;
   - at least one `confirmed_personal_risk`;
   but does NOT explicitly require `confidence=high`.

2. Current JSON result schema permits both `medium` and `high` confidence for `analyzed_not_fit` and does not structurally encode the special high-confidence requirement.

3. GitHub ingest applies an additional semantic validation:
   `confirmed_personal_negative requires high confidence`.

Therefore the worker can produce a result that appears valid under its prompt/schema but is rejected only after semantic work and transport.

## User requirement

Do not solve this by telling the model “always set high”.

The invariant must be structurally and operationally enforced:

> A result with `analyzed_not_fit + confirmed_personal_negative` is valid only when the semantic evidence genuinely supports `confidence=high`. If confidence is only medium, that exact outcome/basis combination is unavailable; the worker must choose the truthful alternative allowed by the evidence.

The system must also make it impossible for an exact contract-invalid semantic result to cause an endless normal-first-pass loop.

## Required behavior

### A. One canonical rule in prompt + schema + contract + ingest

After this task, all four layers must state/enforce the same invariant:

`outcome=analyzed_not_fit AND not_fit_basis=confirmed_personal_negative => confidence=high`

Implement this as a real conditional in the canonical result schema, not merely prose.

The worker prompt must explain the semantic choice:
- use `confirmed_personal_negative/high` only when evidence truly warrants high confidence;
- if the worker's confidence remains medium, do NOT promote it mechanically;
- use another valid completed basis only when that basis is genuinely supported;
- otherwise return `analysis_incomplete` with the appropriate issue code.

The contract and ingest must match the same invariant exactly.

Do not create divergent duplicate business rules with different semantics.

### B. Pre-publication contract self-check

The canonical Deep worker instructions must require a final result-object contract check before create-only submission.

At minimum the worker must verify:
- outcome/basis/confidence compatibility;
- required fields for that outcome;
- negative assessment consistency;
- exact immutable bindings/paths.

This is an additional worker-side safeguard, not a replacement for GitHub ingest validation.

Do not claim LLM self-check is a hard security boundary; GitHub validation remains authoritative.

### C. Semantic-contract-invalid result must not loop as fresh normal work

Distinguish:

1. **transport/stale/unbound garbage** where GitHub cannot prove a valid semantic execution against the exact current work identity:
   - remains non-attempting rejection as appropriate.

2. **exact-bound semantic execution that produced a parseable result but violates a semantic result invariant after work was actually executed**, such as the pinned `confirmed_personal_negative + medium` case:
   - must not return immediately to ordinary normal-first-pass eligibility;
   - GitHub must record this through the EXISTING attempt/recovery architecture, not a new queue.

Preferred architecture:
- GitHub persists/derives an existing GitHub-owned terminal execution failure for the exact work identity when exact run-start/work binding and semantic execution are sufficiently proven;
- this consumes the normal first-pass attempt under the existing attempt-budget model;
- the exact identity moves to existing `recovery_owned`;
- any later retry requires a fresh GitHub-owned recovery authorization;
- after this implementation, the appropriate existing recovery reason is `corrected_runtime_or_validation_defect_material_to_the_prior_failure`.

If current architecture provides a safer equivalent using an already-existing terminal receipt/disposition, use it. Do not invent a second failure queue or retry owner.

### D. Never auto-upgrade confidence

Absolutely forbid deterministic rewriting:
`medium -> high`

GitHub must reject inconsistent semantic truth; it must not “repair” confidence.

The semantic worker may choose high only from the evidence.

### E. Current affected-work reconciliation

After the generic fix is implemented, reconcile current affected exact identities deterministically.

Pinned cases:
- Five Dates;
- Her New Memory - Hentai Simulator;
- Blazing Sails.

Do not manually fabricate successful Deep results.

For each exact current identity, use existing durable run-start/result/rejection evidence to determine whether a semantic execution was sufficiently proven to transition it out of ordinary first-pass looping.

If yes:
- move it through the existing terminal-failure/recovery-owned semantics;
- authorize one bounded recovery only after the runtime/validation defect is corrected, using the existing reason `corrected_runtime_or_validation_defect_material_to_the_prior_failure`.

If exact proof is insufficient for any item, fail closed and report it; do not invent attempt history.

Do not execute the semantic recovery from this developer chat.

### F. Worker final report wording

The Progressive Deep worker must stop presenting create-only submission as canonical acceptance.

Final invocation report must clearly distinguish:
- create-only artifacts submitted;
- canonical GitHub acceptance confirmed, if actually known;
- rejected, if actually known;
- acceptance pending/unverified.

If the worker does not wait for asynchronous ingest, it must say that acceptance is not confirmed.

Do not add unbounded polling or waiting between games.

### G. Preserve asynchronous traversal

Keep the current rule:
- submit item A;
- do not wait for ingest before processing frozen sibling B.

The fix must not reintroduce the old per-item GitHub-receipt blocking that reduced throughput.

Any bounded final status observation must not control semantic traversal or retry items in the same invocation.

## Required regressions

At minimum:

1. Schema rejects:
   `analyzed_not_fit + confirmed_personal_negative + medium`.

2. Schema accepts:
   `analyzed_not_fit + confirmed_personal_negative + high`
   when all other required evidence fields are valid.

3. Medium-confidence negative evidence does not get auto-promoted; truthful incomplete path remains available.

4. Ingest and schema agree on the same outcome/basis/confidence invariant.

5. Exact-bound semantic-contract-invalid result transitions out of ordinary first-pass repetition through the existing terminal/recovery state.

6. Malformed/stale/wrong-work/wrong-run-start transport does NOT falsely consume a semantic attempt.

7. The same exact work_id cannot be emitted again as normal first-pass merely because GitHub rejected a proven semantic execution for this contract violation.

8. Recovery requires a new explicit GitHub authorization and correct reason.

9. The three pinned current games are reconciled without fabricated accepted results and do not remain in an automatic repeated ordinary-work loop after reconciliation.

10. Sibling traversal remains nonblocking/asynchronous.

11. Worker final summary cannot label submitted artifacts as accepted unless acceptance is actually confirmed.

12. No new scheduler, queue, retry daemon, semantic worker or Scheduled Task.

13. Existing Progressive PASS2 core, recovery, frozen-start, parallel Dossier, backlog disposition and execution ownership suites stay green.

14. Preserve changes from the accepted PR #128 Deep score-evidence/explainability contract.

## Hard boundaries

Do not:
- mechanically force `confidence=high`;
- weaken the high-confidence requirement;
- accept invalid results merely to advance the queue;
- delete rejection evidence;
- fabricate successful results for the three games;
- manually perform semantic Deep recovery;
- create a second queue or retry mechanism;
- add a new scheduler;
- block each frozen sibling on ingest of the previous one;
- change Fast/PASS1 or Dossier semantics;
- change RANK-013;
- change Scheduled Tasks.

## Production acceptance

Implementation PR must be rebased/reconciled with fresh main after PR #128.

Before merge prove:
- canonical result schema, worker prompt, contract and ingest agree;
- exact invalid-result loop regression passes;
- existing Deep tests pass;
- current affected identities have a deterministic post-fix disposition.

After merge:
- verify ordinary `progressive_pass2_work.json` no longer exposes proven failed exact identities as fresh normal-first-pass work;
- if recovery authorization is prepared, report exact recovery items and do not execute them in this chat;
- the user may then run the existing Deep semantic worker normally.

## Delivery

Use a dedicated branch/PR under current worker protocol.

Write:
`reviews/worker_reports/deep-invalid-not-fit-contract-loop-fix-01.md`

Required report sections:
1. `Task`
2. `Dependency reconciliation with PR #128`
3. `Root cause`
4. `Canonical confidence invariant`
5. `Schema / prompt / contract / ingest alignment`
6. `Invalid semantic execution disposition`
7. `Attempt / recovery semantics`
8. `Pinned repeated games reconciliation`
9. `Worker final-report semantics`
10. `Validation`
11. `Production acceptance`
12. `Unresolved`
13. `Status`
14. exact PR/commit/run references
15. `Recommended next step` — exactly one bounded next action
16. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `recovery_prepared_needs_semantic_execution`
- `needs_fix`
- `needs_user_decision`
- `blocked`

Do not start another task after this one.

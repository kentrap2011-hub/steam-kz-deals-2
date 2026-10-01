# WORKER TASK — Dossier exhausted fail-closed loop fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `dossier-exhausted-fail-closed-loop-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/dossier-exhausted-fail-closed-loop-fix-01.md`

## User problem

The Dossier semantic worker can honestly exhaust every required Russian-feedback retrieval route and stop fail-closed, but GitHub still leaves the exact group as ordinary `pending`.

That causes the next invocation to select the same group again and repeat the same exhausted research indefinitely.

This has now been observed on more than one snapshot for the same product:

- current snapshot `f26a7466dfe1a534a4c7ab506df29725d4ed5fe4fdef1633af6c1fc751771d1b`;
- group sequence `5`;
- group sha `04fa628954e081c590b4de0f907599f64b51504bd353be17a4e84434029652c7`;
- blocked game `To Be or Not to Be`, appid `2190290`;
- stop gate `russian_evidence.existence_established_access_unresolved`;
- all required Russian/source-diversification routes exhausted;
- publication not attempted;
- GitHub still projects `next_pending_sequence=5`, failed/recovery count 0.

Earlier snapshot showed the same structural problem with the same game under a different group sequence and `existence_established_retrieval_unresolved`.

## Mandatory START gate

1. Read current `CHAT_PROTOCOL.md` from `main` fully and execute START gate.
2. Read this task fully.
3. Read current `DIRECTOR_TASK_BOARD.md` current-state section.
4. Read current Dossier runtime prompt, semantic worker prompt, schema, web-evidence contract, persistence bridge, execution ownership contract, worker index, work manifest and validation status.
5. Inspect current buffer/drain/recovery code and tests.
6. Refresh current `main` immediately before any writes.

Do not start another task.

## Required invariant

A normal-first-pass Dossier group must never remain ordinary `pending` forever after the semantic worker has:

- proven exact work identity;
- genuinely exhausted every required materially distinct route;
- reached a contract-defined incomplete/fail-closed semantic outcome such as
  `existence_established_retrieval_unresolved` or
  `existence_established_access_unresolved`;
- and has no further required semantic step left in that invocation.

The worker must still NOT fabricate a valid dossier.

Instead GitHub must durably learn that this exact normal-first-pass group consumed its semantic attempt and must leave ordinary first-pass traversal.

The exact group should become existing GitHub-owned failed/recovery state (or an equivalent already-canonical terminal state) so later unrelated groups can continue.

## Architecture constraints

GitHub remains sole owner of:
- normal-first-pass accounting;
- terminal classification;
- failed/recovery projection;
- next-work projection;
- persistence;
- idempotency;
- recovery authorization.

The semantic worker may only submit an exact-bound terminal/fail-closed execution artifact allowed by the canonical contract.

Do not make the semantic worker mutate canonical state directly.

Do not add:
- a second queue;
- a retry daemon;
- a new scheduler;
- arbitrary retry counters;
- AppID-specific exceptions;
- browser logic;
- manual state edits.

## Required implementation behavior

Design and implement a generic terminal path for exact-bound semantic fail-closed exhaustion.

It must distinguish at least:

### A. Semantic exhaustion that consumes normal first pass

Examples:
- exact-product Russian existence established;
- all required materially distinct retrieval routes exhausted;
- no concrete usable Russian/mixed player feedback observed;
- canonical contract says incomplete dossier;
- no remaining semantic route exists.

These outcomes must:
- be represented by a durable exact-bound artifact/receipt;
- consume the exact normal-first-pass semantic attempt;
- classify the exact group out of ordinary pending;
- project it through the existing failed/recovery mechanism;
- allow later pending groups to continue.

### B. Transport/runtime failures that do NOT consume the semantic attempt

Examples:
- stale snapshot/binding;
- wrong group identity;
- malformed artifact;
- missing descriptor;
- write failure before durable submission;
- ordinary invocation/runtime cutoff before required routes are exhausted;
- tool failure while materially distinct required routes still remain.

These must remain retryable normal work and must not be falsely classified as semantic exhaustion.

## Terminal artifact requirements

Prefer extending an existing canonical receipt/artifact mechanism if one exists.

If a new Dossier terminal receipt is required, it must be:
- exact snapshot/group bound;
- deterministic/create-only;
- idempotent;
- impossible to replay onto another snapshot/group;
- explicit about semantic stop class;
- explicit that no valid dossier was produced;
- explicit about attempt consumption;
- validated by GitHub before canonical state transition.

The receipt must not persist raw review text, usernames, snippets, or other evidence forbidden by the current Dossier privacy/provenance contract.

## Recovery semantics

Use the existing GitHub-owned failed/recovery architecture.

Do not let the worker decide when/how to retry.

A later recovery may only occur when GitHub explicitly projects/authorizes it under the canonical contract.

Normal first-pass traversal must skip such classified groups.

## Current regression

Add a generic regression reproducing the current failure:

1. group is ordinary pending;
2. worker reaches exact-bound `existence_established_access_unresolved` or `existence_established_retrieval_unresolved` after required route exhaustion;
3. no valid dossier candidate is emitted;
4. terminal artifact is accepted;
5. group becomes failed/recovery, not pending;
6. next pending sequence advances to the next unrelated group;
7. later invocation does not repeat the same normal-first-pass identity.

Also prove snapshot rollover does not erase the invariant by turning the same exhausted historical attempt into a fresh retry under the same exact snapshot/work identity. New daily snapshot semantics may create genuinely new work only according to existing canonical daily preparation rules.

## Safety regressions

At minimum prove:

1. unresolved semantic exhaustion consumes one normal first pass;
2. valid dossier candidate path remains unchanged;
3. malformed terminal receipt does not consume;
4. stale snapshot receipt does not consume;
5. wrong group sha does not consume;
6. unexhausted runtime/tool stop does not consume;
7. deterministic receipt replay is idempotent;
8. accepted/failed groups never re-enter normal traversal;
9. later groups continue despite one failed/recovery group;
10. recovery requires GitHub authorization;
11. Dossier evidence strict validator remains fail-closed;
12. current Russian evidence contract is not weakened;
13. current privacy/provenance rules remain unchanged;
14. canonical writer serialization remains correct;
15. no Scheduled Task changes.

## Current production handling

Do not fabricate a receipt for the user's pasted ledger.

Do not manually edit current group 5 canonical state merely from chat text.

After implementation is merged, the normal Dossier semantic worker must be able to reread current GitHub work and, if the exact same semantic exhaustion is still true, submit the new canonical terminal artifact itself.

If the current snapshot legitimately changes before then, obey the then-current GitHub projection.

## Delivery

Use a dedicated implementation branch and PR.

Write:
`reviews/worker_reports/dossier-exhausted-fail-closed-loop-fix-01.md`

Required report sections:
1. Task
2. START / fresh-main reconciliation
3. Root cause
4. Attempt-consumption boundary
5. Terminal artifact/receipt design
6. GitHub ingest/classification
7. Recovery semantics
8. Regression coverage
9. Current production state after merge
10. Boundaries preserved
11. Exact PR/commit/run refs
12. Status
13. Recommended next step — exactly one bounded next action
14. Efficiency / reusable lesson

Allowed statuses:
- `complete_ready_for_director_acceptance`
- `implementation_complete_needs_next_semantic_invocation`
- `needs_fix`
- `blocked`

Do not run Dossier or Deep semantic work yourself.
Do not modify Scheduled Tasks.
Do not start another task.

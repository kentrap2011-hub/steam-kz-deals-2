# WORKER TASK — PROGRESSIVE ASYNC TRAVERSAL + DEEP INVALID TRANSPORT FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `progressive-async-traversal-and-deep-invalid-transport-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/progressive-async-traversal-and-deep-invalid-transport-fix-01.md`

## User-approved decision

Implement the accepted findings from:
`reviews/worker_reports/progressive-runtime-rule-rationale-consistency-audit-01.md`

The user explicitly approved:

1. Fast/PASS 1 must not wait for GitHub ingest or manifest advancement between already-predeclared independent items.
2. Deep/PASS 2 must not wait for prior sibling ingest before later independently authorized items.
3. Deep invalid technical transport must NOT consume the semantic attempt.
4. For an invalid Deep result/terminal-receipt candidate:
   - keep the existing durable error/ingest receipt with the reason;
   - do NOT keep a separate raw copy of the bad candidate;
   - remove the bad candidate from the active inbox after the rejection receipt is durably recorded;
   - keep the semantic attempt unconsumed;
   - allow the exact current item to become submit-able again through GitHub-owned current work/authorization if it is still otherwise live/current.
5. Do NOT add a new rejected-payload fingerprint/hash field or a new raw rejected-payload archive merely for this fix.
   - Existing internal hashing already used by current receipt-file naming may remain unchanged; do not redesign it unless technically required by an unrelated existing invariant.
6. Do not change any Scheduled Task configuration/settings.
7. Do not weaken exact profile pin, Dossier liveness, one-attempt semantics for valid execution, recovery authorization, identity validation, privacy/evidence rules or GitHub canonical acceptance ownership.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Read current:
- `DIRECTOR_TASK_BOARD.md`
- `CHAT_CONTEXT.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `scripts/ingest_progressive_pass1.py`
- `scripts/ingest_progressive_pass2.py`
- `scripts/progressive_pass1.py`
- `scripts/progressive_pass2.py`
- `scripts/progressive_work_authority.py`
- the current Fast/Deep result/receipt schemas and relevant validation tests
- the accepted audit report above
- the accepted pinned-profile handoff report only as needed for regression provenance.

## Architecture preflight — fixed decisions

Before editing, verify these remain true:

1. GitHub remains the only owner of scope, order, canonical acceptance, attempt state, retry/recovery authorization, completeness and persistence.
2. Scheduled ChatGPT remains semantic execution + create-only candidate transport only.
3. This task does not add a new scheduler, queue owner, retry daemon, polling loop or canonical state owner.
4. A worker may traverse only work already prepared/authorized by GitHub.
5. Transport existence may mean only “already submitted / do not recreate”; it never means “accepted”.
6. Exact immutable profile pin and Git-history pre-semantic work authority remain unchanged.
7. Deep Dossier current binding/content/expiry and recovery authorization remain live checks before each new Deep execution.
8. No Scheduled Task create/update/enable/disable/pause/delete/reschedule/rename/recreate/run action is authorized.

If implementation would violate any fixed decision, stop and report the exact conflict instead of inventing a broader architecture.

# IMPLEMENT

## FIX-01 — Fast asynchronous traversal

Repair the PASS 1 worker semantics so GitHub ingest latency cannot serialize semantic execution one item at a time.

Required behavior:

- At invocation start read the current exact PASS 1 manifest and its exact profile pin.
- Traverse only the ordered items already prepared in that manifest / current authorized projection.
- After successfully creating result A, do NOT require GitHub to ingest A, increment attempted count, remove A, or rebuild the manifest before starting B.
- Continue A -> B -> C -> ... while runtime/tool budget safely permits.
- Preserve exact GitHub order.
- Never invent work outside the prepared manifest.
- Never submit one item twice in the same invocation.
- One bad/incomplete item must not block unrelated later items.

### Later invocation with already-submitted Fast item

If the current GitHub-prepared item still appears in the current manifest but its exact deterministic `submission_path` already exists:

- interpret this only as `already submitted; do not recreate`;
- do NOT infer acceptance, attempt consumption, fit/not-fit or canonical progress;
- continue to the next later predeclared current item whose exact submission path is absent;
- the exact existing path must match the current manifest item; a similarly named/stale/wrong-generation artifact must never count as a marker.

Fast exact malformed current submissions keep their existing one-shot terminal-incomplete semantics. Do not change that policy in this task.

## FIX-02 — Deep asynchronous sibling traversal

Clarify/repair PASS 2 worker semantics:

- before each new Deep item, retain current GitHub authorization/liveness checks;
- retain exact profile pin verification;
- retain exact Dossier content SHA/binding/expiry check;
- retain exact recovery authorization for recovery work;
- BUT prior sibling canonical ingest/attempt advancement is never a prerequisite for the next independent authorized sibling.

If exact result or terminal-receipt transport for Deep item A already exists:
- do not rerun A;
- do not treat it as canonically accepted;
- later currently authorized siblings may still proceed.

Do not freeze an old Deep plan blindly: each new item must still pass current item-specific authorization/Dossier liveness checks.

## FIX-03 — Deep invalid transport leaves no active-file deadlock

Current problem:
`rejected_invalid_result_no_attempt` / `rejected_invalid_execution_receipt_no_attempt` can leave the invalid candidate occupying the active deterministic inbox path while consuming zero attempts.

Implement the user-approved policy:

1. GitHub validates the candidate as today.
2. If it is an invalid current Deep result or invalid current Deep terminal receipt and policy says zero attempt:
   - persist the existing ingest/error receipt with the exact reason and identifying fields already required;
   - do NOT create a separate raw rejected-payload archive;
   - do NOT add a new fingerprint/hash field for this rejected payload;
   - once that rejection receipt is durably represented in the same canonical GitHub-owned persistence transaction, remove the invalid candidate from the active inbox.
3. The semantic attempt remains unconsumed.
4. If the item is still current, live and otherwise authorized, GitHub's normal work projection must be able to make it submit-able again; ChatGPT must not invent this eligibility itself.
5. Preserve the old rejected receipt for diagnosis even after the bad active file is removed.
6. Never overwrite or mutate the bad candidate before classification.
7. Never silently turn invalid transport into accepted/incomplete semantic state.
8. Do not create a tight same-invocation retry loop. A candidate rejected by GitHub is not rerun by the same semantic invocation merely because cleanup later frees the path.

### Reusing the deterministic path

Prefer the smallest mechanism compatible with existing Git-history authority and create-only semantics.

If recreating the same exact deterministic submission path after GitHub-owned rejection cleanup is already safe under the current work-authority model, prove it with tests and use it.

If current historical-authority logic makes same-path recreation unsafe/ambiguous, add only the minimal GitHub-owned correction authorization/path identity necessary to preserve:
- zero semantic-attempt consumption;
- immutable audit history;
- no worker-owned retry decision;
- no raw rejected-payload archive;
- no new rejected-payload fingerprint field.

Do not invent a broader retry subsystem.

## FIX-04 — Preserve GitHub ownership and no-wait semantics explicitly in contracts

Update the smallest necessary canonical contract/prompt text so future maintenance cannot reintroduce:

- “previous sibling must disappear from manifest before next item”;
- “submitted means accepted”;
- “worker owns retry because path became free”.

Make explicit:
- semantic worker can traverse already-authorized independent work asynchronously;
- GitHub acceptance can lag transport;
- GitHub alone decides canonical result/attempt/recovery state.

## FIX-05 — Do not touch Dossier behavior

The audit found current Dossier normal buffered/nonblocking behavior correct.

Do NOT modify:
- Dossier worker progression;
- Dossier pending-collision ownership rule;
- Dossier group state/recovery;
- Dossier semantic/evidence contracts.

## FIX-06 — Do not change stage independence

Preserve:
- Deep does not require Fast attempt/completion/incomplete;
- Fast does not wait for Deep except existing same-identity authoritative Deep suppression;
- Dossier remains independent neutral evidence preparation.

# VALIDATION

Add focused regression coverage proving at least:

### Fast
- F-01: A result created while manifest is unchanged -> B still executes.
- F-02: A exact path already exists on a later invocation -> A is not recreated, B can execute.
- F-03: exact existing transport never counts as canonical acceptance/attempt.
- F-04: stale/wrong-generation/wrong-path file does not mark current item submitted.
- F-05: malformed exact current Fast transport retains existing terminal-incomplete one-shot semantics.
- F-06: profile pin/latest-main advancement behavior remains correct.

### Deep traversal
- D-01: valid A transport awaiting ingest does not block B.
- D-02: B still requires its own current Dossier content/binding/expiry and current authorization.
- D-03: expired/rebound Dossier blocks only the affected item without consuming its attempt.
- D-04: recovery authorization cannot be bypassed by old/prepared local state.
- D-05: no Fast prerequisite is introduced.

### Deep invalid transport
- D-06: malformed exact current result -> rejection receipt persists, active bad file removed, attempt count unchanged.
- D-07: malformed exact current execution receipt -> same.
- D-08: after cleanup, if exact work is still current/live, it can be submitted again through GitHub-owned current work; no worker-created retry scope.
- D-09: a later valid resubmission is accepted exactly once and only then consumes the normal attempt.
- D-10: old rejection receipt remains available after successful later submission.
- D-11: no separate raw rejected-payload archive is created.
- D-12: no new rejected-payload fingerprint/hash field is added for this policy.
- D-13: invalid Deep A does not block unrelated Deep B.
- D-14: stale/mismatched Deep artifact keeps existing stale policy and is not confused with current-invalid transport.

### Cross-stage / ownership
- O-01: GitHub remains sole canonical acceptance/attempt/recovery owner.
- O-02: no new scheduler/queue/retry daemon/polling owner.
- O-03: no Dossier behavior change.
- O-04: no Scheduled Task mutation/run.
- O-05: no manual semantic production backlog processing.

Run the relevant current validation workflows/tests. Do not weaken tests merely to make them green.

## Live production boundary

Do not manually run Fast/Dossier/Deep semantic workers for acceptance.

Normal external scheduled production may continue independently. If a natural result appears while validating, it may be observed but must not be required for task completion.

GitHub CI/workflow validation triggered by implementation commits is allowed.

## Durable report

Commit:
`reviews/worker_reports/progressive-async-traversal-and-deep-invalid-transport-fix-01.md`

Required report sections:
1. Final status.
2. Architecture preflight.
3. Exact root causes repaired.
4. Fast traversal behavior before/after.
5. Deep traversal behavior before/after.
6. Deep invalid transport behavior before/after.
7. Exact rejected-error persistence behavior and proof that no raw rejected-payload archive/new fingerprint field was added.
8. Work-authority/path-reuse design actually implemented.
9. Files changed.
10. Tests/workflows and exact refs.
11. Validation F-01..F-06, D-01..D-14, O-01..O-05.
12. Any natural concurrent production observations, clearly separated from validation.
13. Unresolved items.
14. Final Director recommendation.

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_user_decision`

Before completion:
- commit the final durable report to `main`;
- reread that exact committed report from fresh `main`;
- do not modify the report after that reread unless you repeat the final commit+reread closeout.

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
2. Deep/PASS 2 must use one fixed run-start view: at the start of each Scheduled invocation, read/freeze the then-current GitHub-prepared Deep work, exact Dossier bindings/expiry state and recovery authorizations once; later changes are for the next invocation and must not force per-item rereads or invalidate work already authorized for the current invocation.
3. GitHub ingest must validate Deep submissions against that exact run-start authority, not against mutable changes that happened after the invocation began.
4. Deep invalid technical transport must NOT consume the semantic attempt.
5. For an invalid Deep result/terminal-receipt candidate:
   - keep the existing durable error/ingest receipt with the reason;
   - do NOT keep a separate raw copy of the bad candidate;
   - remove the bad candidate from the active inbox after the rejection receipt is durably recorded;
   - keep the semantic attempt unconsumed;
   - allow the exact current item to become submit-able again through GitHub-owned current work/authorization if it is still otherwise live/current.
6. Do NOT add a new rejected-payload fingerprint/hash field or a new raw rejected-payload archive merely for this fix.
   - Existing internal hashing already used by current receipt-file naming may remain unchanged; do not redesign it unless technically required by an unrelated existing invariant.
7. Do not change any Scheduled Task configuration/settings.
8. Do not weaken exact profile pin, one-attempt semantics for valid execution, recovery authorization identity, privacy/evidence rules or GitHub canonical acceptance ownership. Dossier/recovery freshness is checked at the invocation boundary instead of before every item; this timing change is explicitly user-approved.

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
7. Deep uses one invocation-start authority boundary: the exact current Deep manifest/work, Dossier bindings/expiry state and recovery authorizations visible at invocation start are fixed for that invocation. They are not reread/revalidated before each later item.
8. A live-profile/Dossier/authorization change after invocation start applies only to a later invocation and must not retroactively invalidate an item authorized in the current run-start view.
9. GitHub acceptance must be able to prove the submission belongs to that exact run-start authorized view; ChatGPT still never chooses scope/order/recovery itself.
10. No Scheduled Task create/update/enable/disable/pause/delete/reschedule/rename/recreate/run action is authorized.

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

## FIX-02 — Deep fixed run-start snapshot + asynchronous traversal

Replace per-item mutable-currentness checks with one invocation boundary.

Required behavior:

- At the start of each Deep Scheduled invocation, read the then-current GitHub-prepared Deep manifest/work from one exact `main` revision and establish that as the immutable run-start view for this invocation.
- The run-start view must include or exactly bind:
  - ordered Deep items/work IDs;
  - work mode;
  - exact profile pin;
  - exact Dossier path/content SHA/compatibility binding and the expiry state applicable at run start;
  - exact recovery authorization identity/reason/binding for recovery items.
- Verify the exact profile pin once for the invocation and use those exact pinned profile bytes throughout that invocation.
- Establish that each item in the run-start view is authorized/live at the invocation boundary using the smallest GitHub-owned mechanism compatible with current architecture.
- After that boundary is established, do NOT reread/revalidate mutable Dossier state, expiry, recovery authorization, manifest order or GitHub progress before every later item.
- A Dossier/profile/authorization/work change that occurs after invocation start is intentionally deferred to the next invocation.
- Do NOT require prior sibling canonical ingest/attempt advancement before the next item.
- Traverse only the immutable ordered items in the run-start view and only while runtime/tool budget safely permits.
- Never add work that was not present in the run-start view.

If exact result or terminal-receipt transport for Deep item A already exists:
- do not rerun A;
- do not treat it as canonically accepted;
- continue to later items from the same run-start view.

### GitHub acceptance boundary

Current ingest logic revalidates Deep against mutable current Dossier state. That must be reconciled with the new user-approved invocation snapshot rule.

A result created under an exact valid run-start view must remain eligible for canonical validation even if, after invocation start:
- Dossier content/binding changes;
- Dossier wall-clock expiry passes;
- recovery authorization projection changes;
- a newer Deep manifest is prepared;
- the live profile advances.

GitHub must validate the result against the exact run-start authority used by the worker, while still rejecting:
- work that was already stale/unauthorized at invocation start;
- wrong item/work/profile/Dossier/recovery binding;
- arbitrary historical/unprepared work;
- malformed/invalid result transport;
- duplicate/replayed consumed work.

Prefer reusing existing immutable manifest/work authority. If current result/receipt identity cannot unambiguously prove the exact run-start view, add only the minimal durable run-start binding needed (for example an exact manifest authority commit/id). Do not introduce a new queue, scheduler or mutable worker-owned state.

This change intentionally supersedes the old rule that Dossier expiry/current authorization must be rechecked immediately before each individual item and again against mutable-latest state at ingest. Freshness is now defined at the invocation boundary; later changes belong to the next invocation.

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
3. The semantic attempt remains unconsumed. On a later invocation, GitHub's then-current run-start view decides whether the item is submit-able again; ChatGPT must not invent this eligibility itself.
4. Preserve the old rejected receipt for diagnosis even after the bad active file is removed.
5. Never overwrite or mutate the bad candidate before classification.
6. Never silently turn invalid transport into accepted/incomplete semantic state.
7. Do not create a tight same-invocation retry loop. A candidate rejected by GitHub is not rerun by the same semantic invocation merely because cleanup later frees the path.

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
- Deep freezes its authorized Dossier/recovery/work view once at invocation start rather than rechecking between games;
- changes after invocation start belong to the next invocation;
- GitHub acceptance can lag transport and validates Deep against the exact run-start authority;
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

### Deep run-start snapshot / traversal
- D-01: invocation reads one exact current Deep run-start view and later A transport awaiting ingest does not block B.
- D-02: the run-start view exactly binds every processed item's Dossier identity/content, work mode and any recovery authorization.
- D-03: Dossier/profile/authorization changes after invocation start do not stop or invalidate later items from that same authorized run-start view.
- D-04: the next invocation sees the newer GitHub state and does not silently reuse the older run-start view.
- D-05: work already stale/expired/unauthorized before the invocation boundary is not admitted to that run-start view.
- D-06: GitHub ingest accepts a valid result against its exact run-start authority even if mutable current state changed after invocation start.
- D-07: wrong/unprepared/arbitrary historical work is still rejected.
- D-08: no Fast prerequisite is introduced.

### Deep invalid transport
- D-09: malformed exact authorized result -> rejection receipt persists, active bad file removed, attempt count unchanged.
- D-10: malformed exact authorized execution receipt -> same.
- D-11: after cleanup, a later invocation may resubmit only if its then-current GitHub run-start view authorizes the item; no worker-created retry scope.
- D-12: a later valid resubmission is accepted exactly once and only then consumes the normal attempt.
- D-13: old rejection receipt remains available after successful later submission.
- D-14: no separate raw rejected-payload archive is created.
- D-15: no new rejected-payload fingerprint/hash field is added for this policy.
- D-16: invalid Deep A does not block unrelated Deep B.
- D-17: stale/mismatched/unprepared Deep artifact keeps fail-closed behavior and is not confused with current-invalid transport.

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
11. Validation F-01..F-06, D-01..D-17, O-01..O-05.
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

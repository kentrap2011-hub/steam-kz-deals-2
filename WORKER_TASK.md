# WORKER TASK — PROGRESSIVE DEEP DEFERRED RUN-START CONFIRMATION 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`

Task ID: `progressive-deep-deferred-run-start-confirmation-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/progressive-deep-deferred-run-start-confirmation-01.md`

## User-approved decision

The user explicitly approved changing PASS 2 so GitHub run-start confirmation no longer blocks semantic work.

Target behavior:

1. Deep reads one exact `observed_main_commit`, reads contract/work from that exact commit, and creates the existing create-only run-start marker.
2. Deep MAY begin semantic analysis immediately against that exact observed immutable view while GitHub processes the marker.
3. Before Deep publishes the FIRST result or terminal execution receipt from that invocation, it MUST obtain the GitHub-owned run-start receipt for the marker anchor.
4. Publication is allowed only if that receipt is exact, durable and `status:"confirmed"`, and its `run_start_authority_commit` equals the exact `observed_main_commit` used for the provisional semantic work.
5. If the receipt is `rejected`, inconsistent, unsafe, or confirms a different authority, discard all provisional semantic work from that invocation and publish no result/terminal receipt.
6. If the receipt is merely not present yet when the first semantic result becomes ready, bounded rechecks/waiting are allowed while runtime/tool budget safely permits. Absence never authorizes publication.
7. After confirmation, continue through the already frozen ordered invocation items without waiting for sibling ingest, exactly as today.
8. Do not change Scheduled Task settings or create another scheduler/queue/retry owner.

## Proven incident motivating the change

Real production run:
- observed main: `c2d2789658036739f18d2dfd241aac7d9a481cf7`
- run-start anchor: `202a0517b61d3462049afad503e57f2610c1eb05`
- marker commit time: `2026-09-24T16:36:49Z`
- GitHub receipt commit: `d6723e9f75efccd648eb0958ca3d88b98c6b180c`
- receipt became `confirmed` at about 13 seconds after marker creation
- Scheduled worker had already stopped before semantic execution because receipt was absent on its immediate check
- frozen manifest contained 40 items

This is a liveness defect: a valid start can produce a zero-work invocation solely because GitHub confirmation is asynchronous.

A separate earlier production case proves the confirmation guard itself is still required:
- anchor `90e8f5cc93c19950d5a4f4f016ce262f854c4eeb`
- GitHub later created a `rejected` receipt
- reason: `Progressive observed main was superseded before the actual run-start marker`

Therefore this task moves the confirmation gate later; it does NOT remove it.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Read current, minimally:
- `CHAT_CONTEXT.md`
- `DIRECTOR_TASK_BOARD.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `scripts/ingest_progressive_pass2.py`
- `scripts/test_progressive_pass2.py`
- the current PASS 2 result/execution-receipt schemas
- the accepted report `reviews/worker_reports/progressive-async-traversal-and-deep-invalid-transport-fix-01.md` only as needed for run-start authority rationale/regressions.

Do not perform broad repository archaeology.

## Architecture preflight — fixed decisions

Before editing, verify and preserve:

1. GitHub remains the sole owner of Deep scope/order, run-start confirmation truth, canonical acceptance, attempts, recovery authorization, completeness and persistence.
2. Scheduled ChatGPT remains only the bounded semantic data plane plus create-only transport.
3. No new scheduler, recurring stage, queue, retry daemon, backlog manager or canonical state owner is introduced.
4. The existing GitHub-owned marker receipt remains mandatory before ANY Deep semantic artifact is published.
5. The marker commit's actual first parent and Git committer time remain the trusted authority/time source; worker-supplied time never becomes authority.
6. No per-item mutable-current reread is reintroduced after the invocation authority is confirmed.
7. No Fast prerequisite is introduced.
8. Dossier acceptance/evidence semantics are unchanged.
9. No Scheduled Task create/update/enable/disable/pause/delete/reschedule/rename/recreate/run action is authorized.

Important: the current canonical contract explicitly says confirmation must happen before semantic execution. The new user-approved design conflicts with that exact rule. Therefore implementation must update the canonical contract/ownership rationale FIRST in the same bounded change, then align prompt/tests. Do not silently violate the old contract.

## IMPLEMENT

### FIX-01 — split provisional semantic execution from publication authority

Change the Deep runtime contract so:

- marker creation remains before semantic execution;
- semantic analysis may start immediately using ONLY the exact `observed_main_commit` view already read before marker creation;
- no result or terminal execution receipt may be serialized/published until the GitHub run-start receipt is confirmed;
- once receipt is confirmed, verify:
  - exact anchor;
  - exact marker path/nonce lineage;
  - `status:"confirmed"`;
  - `run_start_authority_commit == observed_main_commit`;
  - trusted `run_started_at_utc` comes only from the receipt;
- only then may the already computed first semantic outcome be transported using the confirmed authority/time fields;
- later frozen siblings continue asynchronously without waiting for ingest.

Do not permit semantic execution from a mutable/latest re-read after marker creation.

### FIX-02 — rejected/superseded start behavior

If the receipt is rejected or proves the marker was not anchored on the observed authority:
- publish no Deep result;
- publish no Deep execution receipt;
- consume no semantic attempt;
- discard provisional semantic work;
- stop the invocation;
- do not create a second marker in the same invocation.

Preserve the real superseded-main failure protection demonstrated by anchor `90e8f5...`.

### FIX-03 — absent receipt behavior

If the first semantic outcome is ready but receipt is still absent:
- bounded repeat read/wait is permitted while runtime/tool budget safely permits;
- do not introduce an unbounded polling loop;
- do not invent a fixed semantic quota;
- do not terminate immediately merely because the first receipt read missed the GitHub asynchronous writer;
- if the invocation must stop before confirmation arrives, publish nothing and consume no attempt.

Choose the smallest bounded behavior that can tolerate ordinary GitHub receipt latency such as the observed ~13 seconds. Do not turn ChatGPT into a queue manager.

### FIX-04 — canonical documentation/ownership alignment

Update the smallest necessary canonical sources so they agree:
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `config/execution_ownership_contract.json`
- relevant `PROJECT_DECISIONS.md` rationale
- `PROJECT_ROUTES.md` only if the operational route text would otherwise be stale.

The durable rationale must say:
- confirmation remains an anti-race publication guard;
- semantic computation before confirmation is speculative/provisional only;
- GitHub confirmation remains authoritative;
- rejected confirmation invalidates all provisional work;
- no semantic artifact can cross the GitHub boundary before confirmation.

### FIX-05 — ingest authority remains strict

Do not weaken `scripts/ingest_progressive_pass2.py` acceptance proof.

A published result must still:
- reference an existing confirmed receipt;
- be bound to the exact confirmed authority;
- have transport Git history after the durable confirmation;
- fail closed for rejected/missing/wrong authority receipts.

If current ingest already enforces this, preserve it and prove it with regression rather than changing it unnecessarily.

## VALIDATION

Add focused regression coverage proving at least:

- C-01: marker -> receipt delayed/absent initially -> semantic work may begin, but no artifact is published before confirmation.
- C-02: receipt appears confirmed after a realistic delayed check -> already computed first result may then be published and accepted.
- C-03: receipt rejected because observed main was superseded -> provisional semantic result is discarded; no artifact and no attempt.
- C-04: forged/worker-chosen timestamp cannot substitute for GitHub receipt.
- C-05: confirmed authority must equal the exact observed authority used for provisional semantics.
- C-06: missing receipt never permits publication.
- C-07: bounded waiting/rechecks cannot become an unbounded polling/retry loop.
- C-08: after one confirmation, sibling B/C traversal still does not wait for sibling ingest or mutable manifest advancement.
- C-09: later mutable Dossier/profile/recovery changes remain deferred to next invocation as already accepted.
- C-10: ingest still rejects result transport that predates confirmation or references rejected/wrong receipt.
- O-01: GitHub remains control-plane owner.
- O-02: no new scheduler/queue/retry owner.
- O-03: no Dossier behavior change.
- O-04: no Scheduled Task action.
- O-05: no manual semantic production backlog processing.

Run relevant current PASS 2 and execution-ownership regressions/workflows. Do not weaken tests to make them green.

## Production boundary

Do NOT manually process real Deep backlog in this worker task.
Do NOT run or edit the Scheduled Task.
Natural concurrent production may be observed but is not required for implementation acceptance.

## Durable report

Commit:
`reviews/worker_reports/progressive-deep-deferred-run-start-confirmation-01.md`

Required sections:
1. Final status
2. Architecture preflight
3. Proven production incident
4. Before/after contract
5. Exact implementation
6. Rejected/superseded behavior
7. Delayed-confirmation behavior
8. Files changed
9. Tests/workflows with exact refs
10. Validation C-01..C-10 and O-01..O-05
11. Natural production observations, if any
12. Unresolved
13. Director recommendation

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_user_decision`

Before completion:
- commit the report to `main`;
- reread the exact committed report from fresh `main`;
- do not modify it after that reread unless you repeat the final commit+reread closeout.

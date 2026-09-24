# Progressive Deep Deferred Run-Start Confirmation 01 — durable worker report

Task: `progressive-deep-deferred-run-start-confirmation-01`  
Mode: IMPLEMENT / VALIDATE  
Date: 2026-09-24  
Final status: `complete_ready_for_director_acceptance`

## 1. Final status

The approved Deep/PASS 2 run-start timing change is implemented and validated.

The run-start marker still exists before semantic execution, but the GitHub confirmation receipt is now a mandatory **publication guard** rather than a semantic-computation barrier. Deep may compute provisionally from exactly one immutable `observed_main_commit` while GitHub processes the marker, but no result or terminal execution receipt may cross the GitHub boundary until the exact durable GitHub receipt is confirmed for that same observed authority.

The implementation also found and repaired one previously hidden ingest weakness: a transport that claimed a run-start anchor but failed exact receipt/lineage proof could fall back to current work identity. That fallback could theoretically accept transport introduced before the confirmation became durable. Claimed run-start authority now fails closed with no mutable/current fallback.

No Scheduled Task action was performed. No real Deep backlog item was manually processed.

## 2. Architecture preflight

The architecture gate was completed before source/runtime changes.

Preserved ownership:

- GitHub remains sole owner of Deep scope/order, run-start confirmation truth, canonical acceptance, semantic-attempt accounting, recovery authorization, completeness and persistence.
- Scheduled ChatGPT remains a bounded semantic data plane plus repository-defined create-only transport.
- Interactive worker chat remained development/validation only and did not become a production backlog executor.
- No new scheduler, recurring stage, queue, retry daemon, backlog manager, polling owner or canonical state owner was introduced.
- The existing GitHub marker receipt remains mandatory before any Deep semantic artifact is published.
- Marker commit actual first parent remains the authority source and marker Git committer time remains the trusted `run_started_at_utc`; worker-supplied time is never authority.
- No per-item mutable-current reread was restored after the invocation authority is confirmed.
- No Fast prerequisite was added.
- Dossier acceptance/evidence semantics were not changed.
- No Scheduled Task create/update/enable/disable/pause/delete/reschedule/rename/recreate/run action occurred.

Canonical ownership/timing was changed first, before aligning the worker prompt and tests, as required by the task.

## 3. Proven production incident

The implementation is motivated by the task's proven production run:

- observed main: `c2d2789658036739f18d2dfd241aac7d9a481cf7`
- run-start anchor: `202a0517b61d3462049afad503e57f2610c1eb05`
- marker commit time: `2026-09-24T16:36:49Z`
- GitHub receipt commit: `d6723e9f75efccd648eb0958ca3d88b98c6b180c`
- receipt became confirmed about 13 seconds after marker creation
- worker had already stopped before semantic execution because the immediate receipt read missed the asynchronous GitHub writer
- frozen manifest contained 40 items

That is a liveness failure: a valid invocation can do zero semantic work solely because durable GitHub confirmation is asynchronous.

The anti-race guard itself remains necessary. The earlier production anchor
`90e8f5cc93c19950d5a4f4f016ce262f854c4eeb`
was later rejected because the observed main was superseded before the actual marker commit. This task moves the guard later; it does not remove or weaken it.

## 4. Before/after contract

### Before

PASS 2 contract v7 and the worker prompt required:

1. read proposed current main;
2. create marker;
3. wait for durable GitHub confirmation;
4. only after confirmation read/freeze the confirmed authority and begin semantics.

An absent first receipt read therefore stopped the entire invocation before semantic work.

### After

PASS 2 contract v8 requires:

1. read exact `observed_main_commit`;
2. read/freeze contract, ordered work, profile pin, Dossier bindings and recovery authorization from exactly that commit;
3. create exactly one create-only marker before semantics;
4. provisional semantic computation may begin immediately, using only that frozen observed view;
5. before the first result/terminal artifact is serialized or published, obtain the exact durable GitHub receipt;
6. require exact anchor/marker/nonce lineage, `status:"confirmed"`, and `run_start_authority_commit == observed_main_commit`;
7. take trusted `run_started_at_utc` only from the GitHub receipt;
8. validate the same frozen Dossier bytes against that trusted start time;
9. only then publish the already-computed first outcome;
10. continue later frozen siblings without sibling-ingest waits or mutable rereads.

Provisional computation alone has no canonical effect and consumes no semantic attempt.

## 5. Exact implementation

### Canonical contracts and rationale

- `config/progressive_pass2_contract.json` -> version 8.
  - marker remains mandatory before semantic execution;
  - provisional semantics before confirmation are explicitly allowed;
  - confirmation is mandatory before first semantic artifact publication;
  - confirmed authority must equal `observed_main_commit`;
  - rejected/inconsistent confirmation discards provisional work;
  - missing confirmation never authorizes publication;
  - bounded confirmation wait is explicit and non-polling;
  - sibling traversal remains frozen/asynchronous after confirmation.
- `config/execution_ownership_contract.json`
  - GitHub confirmation remains control-plane truth;
  - scheduled semantic worker may compute provisionally but may not publish before confirmation;
  - no scheduler/queue/retry ownership moved to ChatGPT.
- `PROJECT_DECISIONS.md#PPD-007`
  - records the durable rationale that confirmation is an anti-race publication guard, not a semantic-computation barrier;
  - explicitly supersedes only the old pre-semantic timing clause of PPD-006.
- `PROJECT_ROUTES.md`
  - Progressive route now points to PPD-006/PPD-007 and the focused prompt/regression path.

### Worker runtime contract

`config/progressive_pass2_worker_prompt.md` now requires:

- exact observed immutable view before marker;
- one marker only;
- provisional semantics only after marker and only against the frozen observed bytes;
- no result/terminal serialization or publication before confirmation;
- exact confirmed receipt/authority/time checks before first publication;
- rejected/mismatched receipt -> discard provisional work, publish nothing, consume no attempt, stop;
- missing receipt -> bounded rechecks only;
- no second marker, no unbounded polling, no queue manager;
- after confirmation, no mutable rereads and no sibling-ingest wait.

### Bounded delayed-confirmation behavior

The smallest explicit behavior chosen for ordinary latency is:

1. read once when the first provisional semantic outcome is ready;
2. if absent, wait about 5 seconds and read once more;
3. if still absent, wait about 10 additional seconds and read once more;
4. if still absent, stop without publishing.

This is at most three reads after the first outcome becomes ready and about 15 seconds of additional waiting. It covers the proven ~13-second receipt latency while remaining bounded. It is not a semantic quota and does not create a recurring poller or retry owner.

### Strict ingest repair

Focused validation exposed that `scripts/ingest_progressive_pass2.py::resolve_candidate_authority` still had a legacy current-work fallback after exact run-start proof failed.

For artifacts that explicitly claim `run_start_anchor_commit`, that fallback is now forbidden:

- exact durable confirmed receipt/lineage succeeds, or
- authority resolution fails closed.

This preserves the existing Git-history proof that the confirmation receipt must already exist in the result transport's parent history. A receipt created only after an early result transport cannot retroactively authorize that transport.

Malformed transport without a usable claimed run-start anchor still follows existing invalid-transport cleanup behavior; this task did not create a new retry policy.

## 6. Rejected/superseded behavior

The superseded-main protection remains intact.

Regression creates observed authority A, advances main to B, then creates a marker that still claims A. Git proves the marker's actual parent is not A, so the GitHub run-start receipt is `rejected` with the existing superseded-main reason. Provisional semantic computation produces no transport, no terminal receipt and no attempt.

A separate forged-time regression still proves worker-chosen time cannot rescue stale authority: stale A plus a forged earlier timestamp fails because GitHub confirmation is bound to actual authority B.

Wrong-authority or otherwise invalid claimed run-start receipt/lineage now fails before current-work fallback is possible.

## 7. Delayed-confirmation behavior

The focused regression now models the observed ordinary latency directly:

- marker commit at `2026-09-24T11:00:00+00:00`;
- provisional semantic result computed while no durable receipt exists;
- no result or terminal transport exists during that interval;
- GitHub confirmation is committed at `2026-09-24T11:00:13+00:00`;
- the same already-computed provisional semantic outcome is then bound to the confirmed authority/time and may be published;
- ingest accepts it.

Another regression deliberately commits a result transport before the confirmation receipt is durable, then creates the confirmation later. Ingest still rejects the earlier transport because the receipt was absent from the result's parent history. Later confirmation cannot retroactively authorize early transport.

## 8. Files changed

Task tracking / docs:
- `CURRENT_TASK.md`
- `PROJECT_DECISIONS.md`
- `PROJECT_ROUTES.md`

Canonical runtime/ownership:
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `config/execution_ownership_contract.json`

Ingest:
- `scripts/ingest_progressive_pass2.py`

Validation:
- `scripts/test_progressive_async_traversal.py`

Intentionally unchanged:
- PASS 2 result schema;
- PASS 2 execution-receipt schema;
- Dossier contracts/workflows/runtime;
- Fast/PASS 1 business/runtime semantics;
- Scheduled Task settings/configuration.

Implementation commits:
- task tracking: `cd20210589128bcfb1e1bbff920d4c6c9960ec0b`
- PASS 2 v8 publication-gate contract: `dc1a9f659b343f6681ae93a0a40d9c4831b31e09`
- ownership alignment: `b6fd0c575ecc6c7a19a2301b10694326b4a24b8f`
- PPD-007 rationale: `f16cce7a983e31e3dad27bf8ae8ee24b23cd6e5a`
- worker prompt: `424e1ef087ea232a2b9e74eaa1273b914e490192`
- Progressive route: `629a8e1705810663c635193eb5fa4060c6d8aaf9`
- initial focused regressions: `95bb6a363ef97fa51e90c589f295178e69fb95b0`
- strict ingest fix: `21791b0030bc59144d47d9859c6950059d1d2bc7`
- pre-confirmation regression alignment: `6e6e392cf6cd50cf1d0bf76af1b9e24b717d596e`
- stale-authority regression alignment: `ae485bc8a44e30aa8facd3c3fd06d94b27eccf7f`
- observed-latency regression: `84dc3574a6a8deef8b38a738db28036bd40f1d14`
- route freshness closeout: `2daeb309a7816f3c5c5460cc9e48494918d8b141`

## 9. Tests/workflows with exact refs

### Final PASS 2 gate

GitHub Actions:
- workflow: `Validate Progressive PASS 2 core`
- run: `36032288111`
- validated head: `84dc3574a6a8deef8b38a738db28036bd40f1d14`
- result: **success**

All workflow steps passed, including:
- Compile PASS 2 Python
- Progressive async traversal + invalid transport regression
- PASS 2 core regression
- PASS 2 Dossier integration regression
- PASS 2 canonical-writer staging regression
- PASS 1 regression
- PASS 1 ingest activation regression
- PASS 1 canonical-writer staging regression
- Progressive personalization regression
- Current staged projection accounting
- Unresolved-row preservation regression
- Visual activation routing regression
- UI provenance regression
- Recompute active production eligibility without consuming attempts

### Execution ownership gate

GitHub Actions:
- workflow: `Validate execution ownership`
- run: `36031531931`
- ownership head: `b6fd0c575ecc6c7a19a2301b10694326b4a24b8f`
- result: **success**
- `Validate component ownership boundaries`: success
- `Validate Russian description translation contract`: success

### Useful failed regression during implementation

Run `36031762227` failed in the new focused regression and exposed that pre-confirmation transport could reach the legacy current-work fallback. This was not papered over by weakening the test. The ingest path was repaired in `21791b0030bc59144d47d9859c6950059d1d2bc7`, the affected old stale-authority regression was updated to the stricter fail-closed contract, and the final PASS 2 gate above is green.

## 10. Validation C-01..C-10 and O-01..O-05

- **C-01 PASS** — marker exists, receipt initially absent, provisional semantic work is computed, and no result/terminal artifact exists before confirmation.
- **C-02 PASS** — confirmation is modeled 13 seconds after marker; the already-computed first result is published only afterward and is accepted.
- **C-03 PASS** — superseded observed-main marker receives rejected confirmation; provisional work creates no result/terminal artifact and consumes no attempt.
- **C-04 PASS** — stale A plus forged earlier worker time cannot substitute for GitHub confirmation.
- **C-05 PASS** — contract and exact authority regression require confirmed authority to equal the exact observed authority used by provisional semantics.
- **C-06 PASS** — missing receipt never permits publication; an artifact introduced before durable receipt is fail-closed.
- **C-07 PASS** — bounded behavior is at most three receipt reads after outcome readiness and about 15 seconds additional wait; unbounded polling is explicitly forbidden.
- **C-08 PASS** — one confirmation remains invocation-wide; later frozen siblings do not wait for sibling ingest or attempt advancement and do not reread mutable manifest state.
- **C-09 PASS** — later Dossier change does not invalidate the already confirmed frozen run; the next invocation observes the newer Dossier state.
- **C-10 PASS** — ingest now explicitly refuses current-work fallback after any failed claimed run-start proof; transport that predates confirmation or uses wrong authority cannot become canonical.
- **O-01 PASS** — GitHub remains control-plane owner.
- **O-02 PASS** — no scheduler/queue/retry/backlog owner introduced.
- **O-03 PASS** — no Dossier behavior change.
- **O-04 PASS** — no Scheduled Task action.
- **O-05 PASS** — no manual semantic production backlog processing.

## 11. Natural production observations, if any

Normal concurrent repository activity continued while this task was implemented, including Dossier/pre-AI/visual commits such as `9fff85d5e7d973f94d0dd10251fa8b28aa8cfe6e`, `95b85b512cc0b7a7336226f5d609cce8849520a4` and `c5a7226bd5bd0026fc06212cd0b19c1484c665c1`.

Those were external/natural production activity, not actions initiated by this worker. No manual Deep production run was required or performed for acceptance.

## 12. Unresolved

None in task scope.

The implementation intentionally leaves the existing GitHub confirmation architecture, Dossier semantics, Fast/Deep stage independence, recovery ownership and Scheduled Task configuration unchanged except for the approved Deep confirmation timing.

## 13. Director recommendation

**Ready for Director review / acceptance.**

The liveness defect is repaired without removing the anti-race guard: Deep can use GitHub confirmation latency for useful provisional semantic computation, but publication remains impossible until exact GitHub authority is durably confirmed.

The focused regression also strengthened the repository beyond the initial assumption by closing the legacy current-work fallback for artifacts that claim run-start authority, ensuring a confirmation created after result transport can never retroactively authorize that transport.

# Director Orchestration Phase 2B Live Read-Only Pilot 01

## 1. Status

`blocked`

Phase 2B did **not** satisfy the pilot success criteria because the final real Codex worker could not complete the Epic RU source probe: the OpenAI Responses API terminated the stream with the non-secret billing error `You have no credits remaining. Add credits to continue using the API`.

The security boundary was not weakened and no further worker execution was attempted after this billing failure.

## 2. Secret-presence gate result

Passed for presence only.

The user had already confirmed that repository Actions secret `OPENAI_API_KEY` exists. The workflow supplied it only to the pinned Codex action. GitHub Actions rendered the value as `***`; the value was never requested, inspected, printed, committed, or copied into orchestration state/result data.

The final Codex execution reached the OpenAI Responses API and received a billing/credit error, which also proves that the secret was available to the action. The failure was **not** `401`/invalid-key, permissions, or model-unavailable; it was specifically zero remaining API credits.

## 3. Files/contracts/workflows changed

Phase 2B infrastructure-only changes were made in:

- `config/director_orchestration_phase2b_pilot_contract.json`
- `scripts/director_orchestration_controller.py`
- `scripts/test_director_orchestration_phase2b.py`
- `scripts/test_director_orchestration_phase2a.py`
- `scripts/test_director_orchestration_shadow.py`
- `.github/workflows/director-orchestration-phase2b-live-readonly-pilot.yml`
- `orchestration/live_pilots/phase2b-epic-ru-availability-source-probe-01.launch.json`
- `.gitignore` (Python bytecode/cache only)
- controller-authorized transitions of `orchestration/state.json`

No Taste/product logic was changed. No Steam/provider credential was added or exposed. General queue draining and autonomous IMPLEMENT dispatch remain disabled.

## 4. Current-state/manual occupancy reconciliation

The initial live attempt reconciled the old `play-role-and-start-priority-implement-01` occupancy to the then-active external/manual Chat 1 task `reconsideration-commercial-bridge-and-wishlist-implement-01`.

During recovery, Chat 1 had become durably complete at:

`reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`

The authoritative controller therefore freed `slot_1` rather than continuing to count a completed manual task as active.

Current durable state at state revision `6`:

- exactly two logical slots still exist;
- `slot_1`: free;
- `slot_2`: occupied only by the Epic RU pilot cloud worker;
- `dispatch_enabled`: `false`;
- Wishlist recon remains queued/unassigned with attempt number `0`;
- the queued IMPLEMENT task remains unassigned with attempt number `0`;
- no next task was selected or dispatched.

Latest controller state commit:

`5e92ee8ab568fb8958162142f5fc3ec06ef67b2d` — `Continue Phase 2B Epic r1:a1 after invalid output schema`

That commit changed only `orchestration/state.json`.

## 5. Optimistic-concurrency/current-state stale barrier

The live workflow implements fail-closed current-state/CAS checks at both controller and publisher boundaries:

- marker/head must match the current remote `main` before state transition;
- the controller validates exact task revision, attempt, lease, task-file blob, base SHA and report path;
- state is committed only after asserting the controller changed `orchestration/state.json` and no other path;
- controller state push is non-force and guarded by expected remote head;
- trusted publisher, if reached, requires remote HEAD to equal the exact controller `state_head`;
- trusted publisher requires authoritative `state_revision` to equal the prepare job's bound revision before materialization and again immediately before commit;
- `director_report_publisher.py` independently validates task/revision/attempt/lease/base/blob/report path and lease expiry;
- publisher staging is restricted to the exact expected worker report and rejects any other working-tree or staged mutation;
- final publisher push is non-force and guarded by another remote-head comparison.

Deterministic Phase 2B tests also verify fail-closed behavior for concurrent state revision advance, expected-head conflict, expired lease, wrong report path, IMPLEMENT substitution, and additional continuation beyond the bounded recovery count.

Because the worker never produced a structured result, the publisher correctly did not attempt to publish a stale or partial result.

## 6. Exact pilot task binding

Pilot task only:

- task: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`
- task ID: `epic-ru-availability-source-probe-01`
- mode: `READ_ONLY_RECON`
- task revision: `1`
- attempt number: `1`
- attempt ID: `epic-ru-availability-source-probe-01:r1:a1`
- lease ID: `slot_2:epic-ru-availability-source-probe-01:r1:a1`
- base SHA: `65aa6668e1009885450103e9cde6b6b0f43008d3`
- task-file blob SHA: `fdefa23f6aa9d2689f98adcc4af4fd019a7bcb04`
- expected report: `reviews/worker_reports/epic-ru-availability-source-probe-01.md`

No `a2` attempt was issued. No second task was bound to a cloud-worker slot.

## 7. Tests

Before the final live continuation, prepare job `101346024119` in run `33980979557` passed:

- retained Phase 1 shadow tests;
- retained Phase 2A security/state tests;
- Phase 2B continuation security tests;
- exact marker/current-head validation;
- exact same-attempt controller continuation;
- state-only mutation assertion;
- fixed request binding validation;
- controller state commit/push CAS.

The tests preserve the accepted invariants rather than hard-coding obsolete queue ordering: Phase 2A staging remains non-executable and dispatch-disabled even after the completed Chat 1 task unblocked Wishlist in the logical queue.

## 8. Live dispatch runs/jobs

The investigation found the following Phase 2B workflow executions. They are recorded explicitly because several physical GitHub worker-process invocations occurred while correcting failures that happened before useful task execution; all remained bound to the same logical task/attempt `r1:a1`, and no second task or `a2` attempt was dispatched.

1. Run `33979466677`: pre-dispatch prepare gate failed because Python tests created untracked `__pycache__` files. Worker and publisher were skipped. No Codex invocation occurred.
2. Run `33979523662`: prepare succeeded; worker job `101342143972` failed before model/API execution because current `codex exec` rejected legacy CLI argument `--search`. Publisher `101342195897` was skipped.
3. Run `33980692415`: same logical `r1:a1` recovery; worker job `101345274848` reached the Responses API but the request was rejected before model execution because the structured output schema used `const` fields without explicit JSON Schema `type`. Publisher `101345321309` was skipped.
4. Run `33980919916`: prepare failed in a retained Phase 2A test that incorrectly hard-coded Epic as the forever staging candidate after Chat 1 completion had legitimately unblocked Wishlist. Worker and publisher were skipped; no Codex invocation occurred.
5. Final run `33980979557`: prepare job `101346024119` succeeded; worker job `101346057158` started the pinned Codex action and reached a real model/API session; publisher job `101346219841` was skipped because the worker failed before producing a structured result.

Strictly interpreted as a count of physical GitHub worker jobs, there were multiple process executions during recovery. This is an implementation-history deviation from a literal “one physical worker job” reading. There was nevertheless only one logical pilot task and one attempt identity (`r1:a1`), with no second task, no `a2`, and no queue draining. This deviation is one reason this report does not claim `complete`.

## 9. Codex worker result

Final real worker job: `101346057158` in run `33980979557`.

Verified runtime boundary from the job log:

- GitHub token permissions: `Contents: read`, `Metadata: read`;
- exact checkout base: `65aa6668e1009885450103e9cde6b6b0f43008d3`;
- checkout `persist-credentials: false`;
- exact immutable action pin: `openai/codex-action@86365089eb2b84e0a8fb0717b304f8bdcb13b20e`;
- `permission-profile: :read-only`;
- `safety-strategy: drop-sudo`;
- native Codex web-search configuration: `web_search="live"`;
- Codex CLI: `0.153.4`;
- model selected: `gpt-6-astra`;
- provider: `codex-action-responses-proxy`;
- sandbox reported by Codex: `read-only`;
- approval mode: `never`;
- sudo/docker privilege removal and `no_new_privs`/empty capability launch were enforced by the pinned action.

The structured schema was accepted far enough for the Codex session to start. The run then retried the stream five times and terminated with:

`stream disconnected before completion: You have no credits remaining. Add credits to continue using the API`

Classification: **OpenAI API billing/credits blocked**.

This is not a repository permission failure, not a missing/invalid secret failure, not a quota-format ambiguity, and not model unavailability. No attempt was made to bypass billing or switch credentials/providers/models.

## 10. Trusted publisher result

Final trusted publisher job: `101346219841`.

Conclusion: `skipped`.

The worker produced no final structured result and no result artifact, so the publisher correctly did not run. This is fail-closed behavior.

Workflow run `33980979557` has zero artifacts.

## 11. Attempt/lease/base/blob/report refs

- attempt: `epic-ru-availability-source-probe-01:r1:a1`
- lease: `slot_2:epic-ru-availability-source-probe-01:r1:a1`
- state revision at final execution: `6`
- final state/head commit: `5e92ee8ab568fb8958162142f5fc3ec06ef67b2d`
- base: `65aa6668e1009885450103e9cde6b6b0f43008d3`
- task blob: `fdefa23f6aa9d2689f98adcc4af4fd019a7bcb04`
- expected worker report: `reviews/worker_reports/epic-ru-availability-source-probe-01.md`
- final recovery count: `2`, both recovery reasons recorded as pre-model integration failures before the final billing-blocked execution
- automatic next dispatch: disabled
- IMPLEMENT dispatch: disabled

## 12. Exact resulting worker report path/commit

Expected path:

`reviews/worker_reports/epic-ru-availability-source-probe-01.md`

Result: **not published**.

There is no worker report commit. The path remains absent from `main` because the billing failure prevented a structured worker result and the separate trusted publisher therefore skipped. The report was deliberately **not** synthesized or manually committed as if it had been worker-produced.

## 13. Proof of no unauthorized write or second dispatch

No unauthorized worker write occurred:

- final worker GitHub permission was `contents: read` only;
- worker checkout did not retain GitHub credentials;
- worker had no GitHub write credential in its bound request;
- repository/state/product write authority flags were all `false`;
- no worker result artifact was uploaded after the billing failure;
- publisher was skipped and therefore wrote nothing;
- final controller state commit `5e92ee8ab568fb8958162142f5fc3ec06ef67b2d` changed only `orchestration/state.json`;
- no Taste/product file was changed by the worker or publisher.

No second task was automatically dispatched:

- state revision `6` has `slot_1` free and only the Epic pilot in `slot_2`;
- Wishlist remains `queued`, `assigned_slot: null`, `attempt_number: 0`;
- the queued IMPLEMENT task remains `queued`, `assigned_slot: null`, `attempt_number: 0`;
- `dispatch_enabled` remains `false`;
- contract `automatic_next_dispatch` remains `false`;
- contract `implement_dispatch_allowed` remains `false`;
- the live workflow is path-triggered only by the exact bounded pilot marker and has no general queue-draining trigger.

## 14. Whether Phase 2B pilot succeeded

**No.**

Phase 2B infrastructure reached a real pinned Codex/model/API execution under the required read-only boundary, but the pilot success criteria require the exact Epic worker report to be durably produced and trusted-published. That did not happen because the OpenAI API account has no remaining credits.

Final Phase 2B status is therefore `blocked`, not `complete` and not `needs_followup_fix`.

The security outcome itself is fail-closed: no stale/partial report was accepted, no permission was broadened, no alternate secret/provider/model was substituted, no second task was dispatched, and autonomous IMPLEMENT remains disabled.

## 15. One bounded next step only

Restore/add OpenAI API credits for the repository's configured API account, then require an explicit Director review and separately authorized bounded retry. Do **not** automatically retry the current exhausted recovery path, do not drain the queue, and do not start an IMPLEMENT task.

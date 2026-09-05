# Director Orchestration Phase 2B Live Read-Only Pilot 01

## 1. Final status

`blocked`

Phase 2B is durably closed, but the pilot did **not** succeed. The final real Codex execution reached an OpenAI Responses API model session and was blocked by the exact non-secret billing error:

`You have no credits remaining. Add credits to continue using the API`

No further Codex execution was attempted after that billing failure. No alternate key/provider/model was substituted and no security boundary was relaxed.

Both mandatory durable paths now exist:

- `reviews/worker_reports/epic-ru-availability-source-probe-01.md`
- `reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`

The Epic path is explicitly a **trusted blocked-closeout evidence report**, not a fabricated or substituted Epic research result. Billing prevented the worker from completing the requested source probe, so no Epic RU availability conclusion is claimed.

## 2. Secret availability and failure classification

Repository Actions secret `OPENAI_API_KEY` was available to the pinned Codex action. Its value was never requested, inspected, printed, committed, copied into state, or exposed in this report. GitHub Actions rendered it only as masked `***`.

The final worker reached the OpenAI Responses API and started a Codex session, therefore this was not a missing-secret path. The final failure was not `401`/invalid key, repository permission failure, sandbox failure, or model-unavailable failure.

Final classification: `openai_api_billing_no_credits`.

## 3. Exact logical pilot binding

Only this logical pilot was dispatched:

- task file: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`
- task ID: `epic-ru-availability-source-probe-01`
- worker mode: `READ_ONLY_RECON`
- task revision: `1`
- attempt number: `1`
- attempt ID: `epic-ru-availability-source-probe-01:r1:a1`
- lease ID: `slot_2:epic-ru-availability-source-probe-01:r1:a1`
- base SHA: `65aa6668e1009885450103e9cde6b6b0f43008d3`
- task-file blob SHA: `fdefa23f6aa9d2689f98adcc4af4fd019a7bcb04`
- exact report path: `reviews/worker_reports/epic-ru-availability-source-probe-01.md`

No `a2` attempt was issued. Wishlist remained attempt `0`. The queued IMPLEMENT task remained attempt `0`. No second task was cloud-dispatched.

## 4. Current-state synchronization and slot accounting

At the initial live pilot, the stale `play-role-and-start-priority-implement-01` occupancy was replaced by the then-active external/manual Chat 1 task `reconsideration-commercial-bridge-and-wishlist-implement-01`.

Chat 1 later became durably complete at:

`reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`

The authoritative recovery controller therefore freed `slot_1` instead of retaining obsolete manual occupancy.

Final durable orchestration state is revision `7` with phase:

`phase_2b_live_readonly_pilot_blocked_billing`

Final slot state:

- `slot_1`: free
- `slot_2`: free
- `dispatch_enabled`: `false`
- `automatic_next_dispatch`: `false`

Epic is `blocked`, unassigned, still bound to attempt `r1:a1`, with billing failure evidence recorded. Wishlist is still queued/unassigned at attempt `0`. The queued IMPLEMENT task is still queued/unassigned at attempt `0`.

Final controller state commit:

`670c22f1859889fa365da1de0d797368b0b1d605` — `Finalize Phase 2B blocked on OpenAI API credits`

That commit changed only `orchestration/state.json`.

## 5. Worker security boundary

The real Codex worker retained the required boundary:

- exact immutable action pin `openai/codex-action@86365089eb2b84e0a8fb0717b304f8bdcb13b20e`;
- GitHub job permission `contents: read` only, plus GitHub metadata read;
- checkout `persist-credentials: false`;
- no worker GitHub write credential;
- no Steam/provider secret;
- `permission-profile: :read-only`;
- `safety-strategy: drop-sudo`;
- repository/state/product write authority all `false`;
- worker could not select the next task;
- native Codex hosted web-search config `web_search="live"` without granting direct repository write authority;
- Codex sandbox reported `read-only` and approval mode `never`;
- pinned action removed sudo/docker privilege paths and launched with `no_new_privs`/empty capabilities.

No worker-owned repository write occurred.

## 6. Optimistic-concurrency/current-state stale barrier

Phase 2B implemented fail-closed CAS/current-state checks around state transitions and publication:

- launch/closeout marker HEAD had to equal current remote `main`;
- controller validated task revision, attempt ID, lease ID, base SHA, task blob and report path;
- state commits were restricted to `orchestration/state.json` and pushed non-force only after remote-head comparison;
- normal publisher required exact state revision and remote HEAD before materialization and again before commit;
- wrong report path, expired lease, stale revision/attempt, concurrent state advance and IMPLEMENT substitution were covered by deterministic tests;
- normal worker result publication was skipped when no valid structured result existed;
- blocked-closeout publisher independently verified the completed failed source run/job and exact billing text before creating the exact Epic path;
- blocked-closeout publication staged only the exact Epic report path and used a non-force CAS push;
- controller finalization then used the published-report head as its expected current HEAD and changed only state.

Any stale/concurrent mismatch remained fail-closed.

## 7. Phase 2B execution history

Several physical GitHub workflow/worker-process executions occurred while repairing pre-model integration failures. They all remained the same logical task and same logical attempt `r1:a1`; no second task and no `a2` were dispatched.

1. Run `33979466677`: prepare failed before state commit because Python tests produced untracked `__pycache__`. Worker and publisher skipped; no Codex invocation.
2. Run `33979523662`: prepare succeeded; worker `101342143972` failed before model/API execution because the installed `codex exec` rejected legacy `--search`. Publisher `101342195897` skipped.
3. Run `33980692415`: same `r1:a1` recovery; worker `101345274848` reached Responses API request validation, but the structured output schema was rejected before model execution because `const` fields lacked explicit JSON Schema `type`. Publisher `101345321309` skipped.
4. Run `33980919916`: prepare failed before worker because a retained Phase 2A test incorrectly hard-coded Epic as the forever staging candidate after Chat 1 completion. Worker/publisher skipped; no Codex invocation.
5. Final live execution run `33980979557`: prepare `101346024119` succeeded; real Codex worker `101346057158` started a model/API session; normal trusted publisher `101346219841` skipped because billing terminated the worker before a structured result was produced.

The two same-attempt continuations were bounded explicitly in state as pre-model integration recovery. Recovery count ended at `2`. No continuation was permitted after the final model/API billing failure.

## 8. Final real Codex worker result

Final real worker:

- workflow run: `33980979557`
- prepare job: `101346024119` — `success`
- Codex worker job: `101346057158` — `failure`
- normal trusted publisher: `101346219841` — `skipped`

Runtime evidence showed:

- Codex CLI `0.153.4`;
- model `gpt-6-astra`;
- provider `codex-action-responses-proxy`;
- read-only sandbox;
- corrected structured schema accepted far enough for the Codex session to start;
- stream reconnect attempted five times;
- terminal failure: `You have no credits remaining. Add credits to continue using the API`.

Run `33980979557` produced no worker-result artifact, so the normal result publisher correctly failed closed.

## 9. Trusted publisher results

### Normal worker-result publisher

Job `101346219841`: `skipped`.

Reason: the billing failure prevented a final structured worker result/artifact. It did not publish partial/stale output.

### Trusted billing-blocked closeout publisher

A separate Phase 2B closeout workflow was introduced only after the recovery budget was exhausted and the billing failure was proven. It contains no Codex invocation and cannot dispatch another task.

First closeout run `33981388632` failed closed before publication because GitHub CLI refused ANSI-bearing job logs without `--allow-escape-sequences`. No report or state change occurred in that failed closeout.

After fixing only that trusted log reader, closeout run `33981465053` completed `success`:

- trusted blocked publisher job `101347325055` — `success`;
- controller finalizer job `101347357372` — `success`;
- read-only verifier job `101347383484` — `success`.

The trusted blocked publisher automatically created exactly:

`reviews/worker_reports/epic-ru-availability-source-probe-01.md`

Publisher commit:

`916946a24787ef9754f9d72e525d11613c7516a0` — `Publish billing-blocked Epic RU pilot report`

That commit changed only the exact Epic report path.

The report is deliberately labeled a trusted blocked-closeout report. It records the real worker/billing evidence and explicitly says that no Epic RU research conclusion was produced.

## 10. Final state finalization

Controller finalizer in closeout run `33981465053` validated:

- recovery count `2`;
- exact attempt/lease identity;
- exact base/blob/report bindings;
- exact blocked report contents and source run/job;
- current state before mutation;
- no second dispatch.

It then:

- changed Epic status from `assigned` to `blocked`;
- cleared Epic `assigned_slot`;
- freed `slot_2`;
- recorded `last_failure.class = openai_api_billing_no_credits` with source run/job;
- added the exact Epic report path to evidence refs;
- incremented authoritative state revision from `6` to `7`;
- left `dispatch_enabled` false;
- recorded `phase2b_closeout.status = blocked` and `automatic_next_dispatch = false`.

The final verifier confirmed both mandatory report files exist and both slots are free.

## 11. Proof of no unauthorized writes

Worker-side:

- worker had `contents: read` only;
- checkout did not retain credentials;
- bound request had `github_write_credential: false`;
- repository/state/product write authority were false;
- no worker result artifact was produced after billing failure;
- worker made no repository commit.

Trusted writes were narrowly separated:

- `916946a24787ef9754f9d72e525d11613c7516a0`: only `reviews/worker_reports/epic-ru-availability-source-probe-01.md`;
- `670c22f1859889fa365da1de0d797368b0b1d605`: only `orchestration/state.json`;
- this Director report update: only `reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`.

No Taste/product logic was changed by the worker or publishers. No Steam/provider secret was introduced.

## 12. Proof no second task was automatically launched

Final state revision `7` proves:

- both logical slots are free;
- Wishlist recon: `queued`, `assigned_slot: null`, `attempt_number: 0`;
- Epic: `blocked`, `assigned_slot: null`, `attempt_number: 1`, still `r1:a1`;
- queued IMPLEMENT task: `queued`, `assigned_slot: null`, `attempt_number: 0`;
- `dispatch_enabled: false`;
- Phase 2B closeout `automatic_next_dispatch: false`.

No queue draining and no automated IMPLEMENT occurred.

## 13. Did Phase 2B pilot succeed?

**No.**

The infrastructure successfully reached a real pinned Codex/model/API session under the required read-only boundary, but the worker could not complete `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md` because the configured OpenAI API account had no remaining credits.

Therefore final Phase 2B status is **`blocked`**, not `complete`.

The blocked state is now durable and internally consistent: both mandatory paths exist, the exact Epic path truthfully records blocked evidence rather than fabricated research, the lease is closed, state is revision `7`, both slots are free, no next task was dispatched, and the security boundary stayed fail-closed.

## 14. Only permissible future prerequisite

Restore/add OpenAI API credits for the configured API account. Any future worker retry requires a new explicit Director authorization; it must not be automatic, must not reuse this exhausted closeout as queue draining, and must not start an IMPLEMENT task implicitly.

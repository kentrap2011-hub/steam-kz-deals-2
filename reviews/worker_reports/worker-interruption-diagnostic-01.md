# Worker interruption diagnostic 01

Status: `classified_platform_unobservable`

## Task and boundaries

Authoritative task: `WORKER_TASK_WORKER_INTERRUPTION_DIAGNOSTIC_01.md`.

This was a read-only/recon diagnostic except for this report, required `CURRENT_TASK.md` bookkeeping, and isolated disposable replay branches. `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PERSISTENCE_BRIDGE_01.md` was not resumed. Production `Run now` was not invoked and the real dossier backlog was not processed.

The diagnostic follows `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, and `KNOWN_WORKER_PITFALLS.md -> PITFALL-004`: do not label an interruption as context exhaustion, timeout, runtime budget, or a tool limit without an explicit surfaced signal.

## Incident 1 — dossier control-plane refresh interruption

Task: `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01.md`.

### Last evidenced checklist state

The retained session evidence places the stop after START/task reading and architecture-preflight work, before a worker implementation write was durably established. No pre-interruption worker commit attributable to that attempt is preserved. The later corrected continuation used `e1de0ab3a7629c04dfa7251cc2642e8082233a77` as its immutable baseline and its first worker write was `5db9b8726f6b3ac8804494aad04a3bb3297ee084` (`Define fixed daily dossier snapshot contract`). Therefore `e1de0ab...` is a safe replay reference, not claimed as the interrupted worker's own last write.

Exact historical final tool/action before the stop is **not exposed by the retained trace**. The earlier assistant explanation that the run had exhausted context was later retracted because no platform/system signal supported it.

Required incident fields:

- last completed mandatory checklist item: START plus architecture-preflight reads were completed; implementation write was not yet durably evidenced;
- last durable worker checkpoint: none preserved from the interrupted attempt;
- exact final action/tool: not recoverable from retained trace;
- system/tool error before interruption: **none exposed**;
- branch/commit state at the exact stop: exact worker ref is not recoverable; no worker write from the interrupted attempt is preserved;
- same chat accepted subsequent user input: **yes**;
- interruption phase: between preflight/reasoning and implementation/response continuation, not during a proven canonical persistence operation;
- network/API failures immediately before the stop: no failure is proven to be the terminating event. Separate historical container errors such as `Could not resolve host: github.com` did return explicit responses and the work continued, so they cannot be promoted to the interruption cause.

### Controlled replay recipe

Using immutable ref `e1de0ab3a7629c04dfa7251cc2642e8082233a77`, the diagnostic replayed the proven preflight class with the same GitHub read primitive and the same files/contracts:

1. `CHAT_PROTOCOL.md`;
2. `CHAT_CONTEXT.md`;
3. `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01.md` (historical blob `7c3d45de89dab01554da6c552c3bdb0576060c05`);
4. `config/execution_ownership_contract.json`;
5. `config/daily_execution_contract.json`;
6. `config/taste_steam_review_dossier_contract.json` (historical V1 state);
7. relevant `PROJECT_DECISIONS.md -> TASTE-004` lookup.

The responses ranged from small contract JSON to large protocol/context/decision documents; connector output was sometimes truncated for display, but every request returned successfully and the same chat continued to subsequent calls.

Replay result: **not reproduced**.

Known difference: the historical trace does not preserve the exact final action immediately preceding the original stop, so replay is maximally equivalent to the last proven stage rather than a claim of byte-for-byte identity at an unknown final action.

## Incident 2 — dossier persistence bridge interruption

Task: `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PERSISTENCE_BRIDGE_01.md`.

### Last evidenced checklist state

The last durable branch chain before the reported stop is reconstructable:

- `59598e8fb06473dda7c6132cea3feb0bd11f488c` — `Add dossier persistence bridge regressions`;
- `347d26ef42ce0c7fc4838945e319eed4e0477c0b` — `worker: validate dossier persistence bridge`, adding the 35-line branch-only validation workflow `.github/workflows/_worker_validate_dossier_persistence_bridge.yml`.

The corresponding GitHub Actions run was created at `2026-09-14T02:59:46Z` and later verified as successful:

- run `34801046463`;
- job `103843634734`;
- head SHA `347d26ef42ce0c7fc4838945e319eed4e0477c0b`;
- conclusion `success`.

The interrupted session stopped before it had durably closed the task's mandatory acceptance/merge/report checklist. A later continuation first inspected that already-existing validation result and then continued acceptance.

Required incident fields:

- last completed mandatory checklist item: implementation and focused deterministic regression code were durably committed; the GitHub-hosted validation stage had been initiated by commit `347d26...`, but acceptance/merge/durable report were not completed by that session;
- last durable checkpoint: `347d26ef42ce0c7fc4838945e319eed4e0477c0b`;
- exact last durable write: creation of `.github/workflows/_worker_validate_dossier_persistence_bridge.yml`, blob `c0b78a7d96783a0d049c9ed4df2e9dbae2b25713`;
- whether the exact connector response to that historical write was delivered to the chat: retained telemetry is insufficient to prove it; repository state proves the GitHub operation itself completed;
- system/tool error before interruption: **none exposed**;
- same chat accepted subsequent user input: **yes**;
- interruption phase: after a successful durable write / before validation observation and task closeout;
- nearby network/API failures: none is proven as the terminating event. Other historical container/download/Python reset errors returned explicit error responses and later work continued.

### Controlled replay recipe

A disposable branch was created from the exact parent `59598e8fb06473dda7c6132cea3feb0bd11f488c`. The diagnostic then used the connected GitHub `create-file` action with:

- the same repository;
- the same target path `.github/workflows/_worker_validate_dossier_persistence_bridge.yml`;
- the same 35-line workflow payload;
- the same workflow branch filter pointing at `worker/taste-steam-review-dossier-persistence-bridge-01`, ensuring the disposable replay branch could not execute the workflow;
- the exact original trailing newline.

Exact replay write result:

- replay commit `f79420a8e79d6de4ad675cd909bffcf8442381e5`;
- fetched replay blob SHA `c0b78a7d96783a0d049c9ed4df2e9dbae2b25713`, exactly equal to the historical blob.

A second create-file replay with a tiny payload also succeeded (`73859c1a993f493cb1c87b330c5bf385bb638ea5`), so no size sensitivity was observed between a minimal create-file and the exact historical workflow payload. The first near-exact replay also succeeded (`f39a3fd1deb4bd3542116295731da9b71ae179cb`) and differed only by the final newline before the byte-exact replay removed that difference.

Replay result: **not reproduced**.

After recording the replay refs, both disposable diagnostic branch refs were reset back to the original parent `59598e8...`; no replay workflow or diagnostic payload remains as an active branch change and nothing was merged to production.

## Cross-incident diagnostic answers

1. **Was a system/platform error visible at either actual interruption?** No. `system/tool error before interruption: none exposed` for both interruption endpoints.
2. **Can either interruption be reproduced in the same chat/session class?** No. The proven control-plane read/preflight stage and the byte-exact persistence-bridge create-file operation both completed normally during controlled replay.
3. **Smallest reproducible case?** None found because the interruption itself did not reproduce.
4. **Common exact tool/stage?** None established. Incident 1 is only provably localized to preflight/reasoning before implementation write; incident 2 occurred after a durable GitHub write and before validation/closeout observation.
5. **Payload/range/batch size effect?** Not observed. Large and small GitHub reads succeeded; tiny create-file and the exact historical 35-line create-file payload both succeeded.
6. **Did the last tool fail, succeed, or return no response?** Incident 1: exact final tool is not retained. Incident 2: the GitHub write itself succeeded durably; whether its connector response reached the interrupted chat is not exposed.
7. **GitHub/network failure near interruption?** No terminating GitHub/network error is proven. Known DNS/download/runtime-reset errors elsewhere returned explicit responses and were followed by continued work.
8. **Could the same chat continue after a new user message?** Yes for both incidents.
9. **What platform telemetry is missing?** Session/generation termination reason; server-side stop reason; explicit context-window/budget state; orchestration cancellation reason; wall-clock runtime budget; client/UI disconnect state; and an authoritative last-dispatched/last-delivered tool-response marker are not exposed to this worker.
10. **What trace should future workers persist proactively?** Use the existing PITFALL-004 reproducibility trace at every durable boundary: checklist step/stage; exact action/tool; nonsecret arguments/ref/path; payload/range/batch size; whether a response was received; exact result/error plus commit/run/job refs; next intended step. On an unexplained stop record the exact phrase `system/tool error before interruption: none exposed` when true, plus last durable checkpoint and branch SHA before retrying.

## Classification

Narrowest supported class for both incidents:

`platform-level interruption with no exposed telemetry`

This classification does **not** assert context exhaustion, context-window overflow, timeout, model runtime budget, or a specific tool failure. Controlled replay did not reproduce the interruption, and the available telemetry cannot distinguish among platform/session/UI/orchestration causes.

The earlier `context exhausted` explanation is therefore unsupported and must not be reused as a diagnosis absent a future explicit platform signal.

## Resume safety and mitigation

No persistence-bridge implementation continuation is performed by this diagnostic. That task has since reached `main`, so there is no implementation branch that needs blind replay.

For any future worker continuation or the later user production validation boundary, continuation is safe under these mitigations:

- preserve PITFALL-004 trace fields continuously rather than reconstructing them after a stop;
- take durable repository checkpoints before long validation/merge sequences;
- after an unexplained interruption, inspect branch/commit/run state first and perform one bounded equivalent replay before repeating writes;
- never infer a context/timeout/runtime cause without an explicit error;
- if the same operation begins reproducing the interruption, stop normal work and minimize that reproducible case instead of repeatedly retrying production work.

`KNOWN_WORKER_PITFALLS.md -> PITFALL-004` already contains the reusable operating rule, so no duplicate pitfall/route change is needed from this recon.

## Exact refs

Diagnostic authority:
- `WORKER_TASK_WORKER_INTERRUPTION_DIAGNOSTIC_01.md` blob `0a8347cabf1ebddffec36dd293b31e80cd783b0c`;
- `KNOWN_WORKER_PITFALLS.md` blob `b83a9eb3dc6fe996748b398a5a5e66939543fddd`.

Incident 1 / control-plane:
- historical replay baseline `e1de0ab3a7629c04dfa7251cc2642e8082233a77`;
- task blob `7c3d45de89dab01554da6c552c3bdb0576060c05`;
- first subsequent worker write after restart `5db9b8726f6b3ac8804494aad04a3bb3297ee084`;
- eventual implementation PR #18, merge `efc754a094199a8c41ae686494c8f2a5e4741cef`;
- eventual validation run `34763260187`, job `103739651104`.

Incident 2 / persistence bridge:
- regression parent `59598e8fb06473dda7c6132cea3feb0bd11f488c`;
- last durable pre-stop commit `347d26ef42ce0c7fc4838945e319eed4e0477c0b`;
- historical validation workflow blob `c0b78a7d96783a0d049c9ed4df2e9dbae2b25713`;
- historical validation run `34801046463`, job `103843634734`, success;
- exact replay commit `f79420a8e79d6de4ad675cd909bffcf8442381e5`, exact replay blob `c0b78a7d96783a0d049c9ed4df2e9dbae2b25713`;
- small-payload replay commit `73859c1a993f493cb1c87b330c5bf385bb638ea5`;
- eventual production implementation PR #21, merge `8916348d651afbdeaa13ba71e517bd2a967ce777`.

## Recommended next step

Director reads this report and uses the `classified_platform_unobservable` procedure for future worker interruptions. Do not resume or rerun persistence-bridge implementation from this diagnostic. The later production `Run now` validation remains a separate explicit user action after Director review.

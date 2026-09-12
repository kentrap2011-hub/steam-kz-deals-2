# WORKER TASK — Taste Steam review dossier full backlog 01

Task ID: `taste-steam-review-dossier-full-backlog-01`

Status: `authorized_ready_for_worker`

Mode: `IMPLEMENT`

## Goal

Correct the Steam review dossier production control-plane so one invocation of the existing `Taste Steam Review Dossier` Scheduled Task can continue through the **entire current eligible dossier backlog**, rather than treating the current Taste active pin/checkpoint of 10 games as the complete dossier scope.

`10` may remain an internal durable checkpoint size, but it must never be interpreted as a per-run quota or as the total dossier backlog.

Do not perform the real production backlog after implementation. The user will validate the finished path by pressing **Run now / Выполнить сейчас** on the already existing Scheduled Task.

## Background / proven production symptom

The first real `Run now` of `Taste Steam Review Dossier` completed successfully but reported:

- required at start: `10`;
- reused fresh: `0`;
- generated/persisted: `10`;
- remaining: `0`;
- final state: `ready_from_fresh_cache`;
- durable checkpoint commit: `0e3a1e425a03466ee841d19e0d9446a04157b4da`.

Those 10 dossiers are valid and must be preserved/reused.

The problem is not dossier synthesis itself. The problem is scope/completeness: the current implementation derives dossier work from the current Taste active pin, so after those 10 are fresh it concludes that no dossier work remains even though additional Taste-eligible games can exist in the current canonical backlog.

Relevant prior artifacts:

- implementation task: `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PREPARER_01.md`;
- implementation report: `reviews/worker_reports/taste-steam-review-dossier-preparer-01.md`;
- scheduler task: `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_SCHEDULER_01.md`.

The scheduler task already requires every run to request the entire currently required dossier work scope, continue through it until exhausted or a real runtime/tool limit occurs, and preserve durable progress for the next run. Do not weaken that behavior.

## Mandatory architecture preflight result

This task changes scope/queue/checkpoint behavior, so the ownership gate is binding.

Canonical ownership from `config/execution_ownership_contract.json`:

- GitHub/control-plane owns production scope selection, queue construction, retry/unresolved state, checkpoint merge logic and completeness accounting;
- scheduled ChatGPT is only the constrained semantic data-plane and must not invent or independently choose the backlog;
- checkpoint size must not become a quota;
- no interactive chat may become the production backlog manager.

A canonical conflict is already known and must be resolved **before** implementation proceeds:

`config/taste_steam_review_dossier_contract.json` currently states that GitHub selects the `exact_pinned_game_scope`, and its cleanup rules refer to the current Taste scope. That was correct for the original bounded preparer but is now too narrow for the separately authorized recurring dossier scheduler, whose explicit contract requires the complete current required dossier scope rather than only the next Taste batch.

Therefore this task must first reconcile the dossier contract, then implement the control-plane behavior. Do not patch around the contract while leaving it contradictory.

## Required semantic model

There are two different scopes and they must remain separate:

1. **Dossier preparation backlog** — the full current GitHub-owned set of games that are presently eligible to need Taste semantic evaluation and therefore may need a fresh Steam review dossier.
2. **Taste active pin/work unit** — the bounded exact set currently handed to the Taste semantic producer, with its existing immutable pin/profile binding.

The dossier preparation backlog is intentionally broader than one active Taste pin.

The active pin remains authoritative for downstream Taste semantic execution and must not be redefined by this task.

### How the full dossier backlog must be derived

GitHub must derive the full dossier backlog deterministically from the current canonical Taste queue/backlog and the same eligibility semantics that determine whether an item can enter Taste semantic evaluation, but **across the whole current eligible queue**, not only the current active pin.

Requirements:

- preserve canonical queue/order semantics unless a dossier-specific deterministic appid dedupe is required;
- do not include rows that are only non-Taste/base-support work;
- deduplicate reusable Steam dossiers by canonical Steam `appid` where multiple Taste subjects can reuse the same dossier;
- fresh valid dossiers are reusable and are not emitted as semantic work;
- missing dossiers are required work;
- stale/expired dossiers that are still in the full eligible backlog are required refresh work;
- stale dossiers outside the full eligible backlog remain subject to deterministic GitHub-owned cleanup according to the reconciled contract;
- invalid dossiers remain fail-closed and must not be silently treated as fresh.

If the current canonical files do not provide an unambiguous deterministic way to derive this full eligible Taste backlog, do not invent a new source. Stop with a precise contract gap in the report.

## Phase A — reconcile canonical contract first

Before changing runtime/control-plane behavior:

1. Update `config/taste_steam_review_dossier_contract.json` so it explicitly distinguishes:
   - full dossier preparation backlog;
   - bounded Taste active pin used downstream.
2. Keep GitHub as the sole scope/backlog/checkpoint/completeness owner.
3. Keep scheduled ChatGPT forbidden from inventing scope or managing its own independent queue/retry policy.
4. Preserve TTL default `20` days and existing compact dossier schema/sampling/neutrality rules.
5. Preserve the downstream rule that `build_taste_semantic_dossier_input.py` joins only the current active Taste pin and fails closed if a dossier required by that pin is missing/stale/invalid.
6. Reconcile cleanup terminology so `in scope` for dossier freshness/cleanup means the full eligible dossier backlog where appropriate, not merely the current active pin.
7. Record the rationale for this non-obvious architecture correction in `PROJECT_DECISIONS.md` unless an already-canonical rationale entry exists and can be updated instead.

Do not proceed to Phase B until the resulting contract and ownership model are internally consistent.

## Phase B — implement full-backlog preparation

Change only the minimum dossier control-plane/runtime integration needed to honor the reconciled contract.

Expected likely touchpoints include the existing dossier work builder, dossier lifecycle helper/tests, and only the minimal canonical queue/eligibility dependency required to derive the full backlog. Do not perform a broad refactor.

Required behavior:

1. The GitHub-owned control-plane determines the full eligible dossier backlog independently of the current active Taste pin.
2. It determines total current required work after fresh-cache reuse.
3. One Scheduled Task invocation can process that work in durable checkpoints and continue to the next checkpoint in the **same invocation** until:
   - the full required backlog reaches zero; or
   - a real platform/tool/runtime limit prevents further work.
4. A checkpoint of 10 is allowed and is preferred for compatibility with the existing working pattern, but it is only a durability boundary. It is not a daily quota, per-run quota, or total scope limit.
5. The exact semantic submission/ingest contract must remain safe. If submissions are currently required to exactly cover a prepared manifest, keep each prepared checkpoint exact and let GitHub produce the next checkpoint after successful ingest rather than weakening validation to accept arbitrary partial submissions.
6. After each successful checkpoint, completed dossiers remain durable and fresh; rebuilding work must exclude them and expose the next remaining checkpoint automatically.
7. If one item/checkpoint fails, already accepted earlier checkpoints remain durable. The next run continues from canonical unresolved work rather than repeating completed work.
8. The final no-work state is allowed only when the **full eligible dossier backlog** has no missing/stale required dossiers, not merely when the current active pin is fully covered.
9. The existing 10 production dossiers must be reused and must not be regenerated solely because this task changes scope derivation.

## Scheduled Task boundary

Do **not** create, duplicate, replace or delete Scheduled Tasks in this task.

Existing tasks must remain in place:

- `Taste Steam Review Dossier` — existing dossier task; user will run it manually after this implementation is accepted;
- `Taste Semantic Producer` — existing task id `6aa032f37e688191a5c9a1a83f91c5d9`; do not modify it.

Do not run `Run now` or perform the real mass dossier backlog from the worker chat after implementation.

## Explicitly out of scope

Do not:

- continue the old Taste throughput benchmark;
- change the Taste production limit;
- implement age-priority ordering;
- modify Taste personal-fit semantics;
- solve the separate `complete_no_negative` / negative-contract question;
- change dossier TTL/sampling/neutrality except where terminology is strictly required by the scope correction;
- redesign Steam catalog collection;
- create another scheduler, queue owner or retry manager;
- manually process the production backlog item by item in the worker chat.

## Required validation

Add focused deterministic regression coverage. At minimum prove all of the following:

1. **Backlog > 10:** construct at least 25 currently Taste-eligible games needing dossiers.
2. The full backlog/completeness layer sees all 25; it must not conclude `ready_from_fresh_cache` after only the first 10.
3. First checkpoint processes/persists 10.
4. Rebuild after checkpoint 1 exposes the next 10 and reports 15 still required overall (or equivalent unambiguous completeness evidence).
5. Second checkpoint processes/persists the next 10.
6. Rebuild exposes the final 5.
7. Final checkpoint processes/persists 5.
8. Only then does full-backlog remaining become 0 / ready.
9. Fresh existing dossiers are reused and excluded from work.
10. Stale in-backlog dossier is refresh-required; stale out-of-backlog dossier follows GitHub-owned cleanup policy.
11. Non-Taste/base-support-only rows do not enter the dossier backlog.
12. Duplicate Taste subjects that resolve to the same Steam appid do not force duplicate dossier synthesis.
13. Exact checkpoint submission validation remains fail-closed; arbitrary partial/out-of-scope submission is not silently accepted.
14. Existing active Taste pin semantics/binding remain unchanged.
15. `Taste Semantic Producer` configuration remains unchanged.

Use bounded fixtures/tests. Do not validate by manually creating dozens of real production dossiers.

## Context-budget rule

This task exists partly because the previous worker session exhausted its context before making a safe change.

After START gate and this task file:

- use `PROJECT_ROUTES.md` before any broad search;
- inspect only the minimal relevant dossier/queue files;
- do not reconstruct the whole project or reread unrelated historical reports;
- if a referenced path moved, use one bounded lookup and return to this checklist;
- if navigation requires meaningful rediscovery, update `PROJECT_ROUTES.md` with the verified route before finishing;
- if context pressure appears, prioritize a safe committed implementation + tests + exact checkpoint/report over additional exploratory reading.

## CURRENT_TASK.md rule

The worker may update `CURRENT_TASK.md` only as required by `CHAT_PROTOCOL.md` for this active subtask and its handoff/closeout.

Do not delete or overwrite unrelated active work already recorded there. On completion, leave `CURRENT_TASK.md` truthful and compact.

## Durable report

Write:

`reviews/worker_reports/taste-steam-review-dossier-full-backlog-01.md`

The report must stay compact and include:

1. `Task`.
2. `Verified facts`.
3. `Changes`.
4. `Validation`.
5. `Unresolved`.
6. `Status`.
7. `Recommended next step` — exactly one next step.
8. Exact commit/test/file refs sufficient for Director verification.
9. `Efficiency / reusable lesson` — `none` unless a real reusable route/pitfall was discovered.

Also explicitly state:

- what exact old dependency restricted dossier scope to the active 10-item Taste pin;
- what canonical source/eligibility rule now defines the full backlog;
- whether checkpoint size is 10 or another value and confirmation that it is not a quota;
- the `>10` regression result and checkpoint sequence;
- confirmation that the existing 10 production dossiers were preserved;
- confirmation that neither Scheduled Task was modified/run by this worker.

## Allowed final statuses

- `complete_ready_for_user_run_now_full_backlog_validation`
- `blocked_contract_or_scope_ambiguity`
- `needs_fix`

Do not invent another success status.

## Expected next step after successful completion

Exactly one next step:

The Director reviews this durable report. If accepted, the user manually presses **Run now / Выполнить сейчас** on the existing `Taste Steam Review Dossier` Scheduled Task and we evaluate whether that single invocation now proceeds through the full current eligible backlog (or stops only on a genuine runtime/tool limit with durable progress preserved).

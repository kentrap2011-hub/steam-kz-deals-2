# WORKER TASK — TASTE DOSSIER SCHEDULED ENTRYPOINT LEDGER DIAGNOSTIC 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-scheduled-entrypoint-ledger-diagnostic-01`
Mode: `READ-ONLY / RECON`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай только минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md` только для конфликта активной работы, не как источник более свежей Taste-истины;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- релевантный operational pitfall, только если trigger реально совпадает;
- `DIRECTOR_TASK_BOARD.md`, раздел `LIVE ACCEPTANCE FAILED — fail-closed ledger not emitted`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_persistence_bridge.json`;
- `config/execution_ownership_contract.json`;
- accepted implementation report:
  `reviews/worker_reports/taste-dossier-fail-closed-execution-ledger-implement-01.md`.

Не делай broad history search и не исследуй unrelated Taste defects.

## Accepted live symptom

Live production acceptance against active snapshot
`ad93a4484f1c6ceba4ba3d4ef0de681f65fe670ec1ee600e2abc0822b0eec54a`
stopped fail-closed before publication of expected `g000001`.

Observed response correctly stated:
- snapshot changed;
- active binding is `web-evidence-v2-fail-closed-execution-ledger-v1`;
- prior invocation evidence cannot be rebound/reused;
- no deterministic artifact was created;
- canonical progress did not change.

But the same final response omitted the mandatory marker:
`FAIL_CLOSED_EXECUTION_LEDGER_V1`

and omitted the required structured ledger object.

Canonical `main` has already been independently checked by Director: the mandatory ledger section is present in the active worker prompt.

Therefore this task is NOT to redesign the ledger. It is to localize why the Scheduled Task final response did not follow the already active requirement.

## Goal

Establish, with the narrowest available evidence, where the compliance chain broke:

`Scheduled Task entrypoint/configuration -> canonical prompt load -> active binding interpretation -> early fail-closed path -> final response rendering`.

Distinguish confirmed fact from inference.

The preferred result is one exact first divergence/root cause. If the platform does not expose enough state, narrow the failure to the smallest unresolved boundary and say exactly what cannot be observed.

## Hard boundaries

READ-ONLY / RECON only.

Do NOT:
- edit the scheduled task;
- edit worker prompt/contracts/schema/validator;
- create or modify production candidates;
- trigger production `Run now`;
- run retrieval for Crown Trick / Hellish Quart / Tetris as a substitute for diagnosis;
- change snapshot/progress/recovery state;
- add logging, queue, retry, scheduler, checkpoint or watchdog architecture;
- weaken fail-closed behavior;
- invent a platform/runtime cause;
- treat the omission itself as proof of timeout, context truncation, model forgetfulness, tool failure, or prompt conflict.

Only the final worker-report may be written to `main`.

## Diagnostic questions — answer all

### ENTRY-01 — actual Scheduled Task instruction

Inspect the actual current Scheduled Task definition/entrypoint for `Taste Steam Review Dossier` if the product tooling exposes it.

Record:
- exact task title/identity sufficient to disambiguate it;
- whether the entrypoint explicitly requires reading the latest canonical
  `config/taste_steam_review_dossier_worker_prompt.md` from `main` at every invocation;
- whether it says to read it fully;
- whether it declares canonical repository files authoritative over the live task prompt;
- any duplicated fail-closed/final-response instructions in the task entrypoint that could conflict with or supersede the canonical prompt.

Do not reproduce secrets or irrelevant full prompt text in the report; quote only short decisive clauses or identify them structurally.

If Scheduled Task definition is not inspectable through available product tooling, mark exactly:
`ENTRY-01 blocked: task definition not exposed by available tool`
and continue with repository-side diagnosis.

### ENTRY-02 — canonical prompt activation

Verify on current `main`:
- active worker prompt contains exact marker requirement;
- fail-closed ledger applies to every stop before successful connected GitHub create-file action;
- binding revision is `web-evidence-v2-fail-closed-execution-ledger-v1`;
- no later section of the canonical prompt cancels, weakens or narrows this requirement for binding/snapshot-change stops.

Classify:
- `aligned`;
- or exact internal contradiction with refs.

### ENTRY-03 — early binding-change path

Trace only the contract/prompt instructions relevant to the observed early stop:
- invocation loads current canonical state;
- old snapshot evidence is rejected as stale/incompatible;
- current group was not fully researched;
- publication is not attempted;
- final response is fail-closed.

Determine whether a binding/snapshot-change stop before evidence retrieval is explicitly inside the ledger requirement.

The key question:
Would the observed live stop, if following the canonical prompt, have been required to emit the ledger even with zero/partial new web retrieval?

Answer yes/no with exact canonical support.

### ENTRY-04 — final-response instruction conflicts

Search the current Scheduled Task entrypoint (if exposed) and canonical worker prompt for competing final-response instructions, including:
- success-only concise response rules;
- generic fail-closed wording;
- “stop immediately” wording;
- stale/binding-change wording;
- any instruction that could reasonably be interpreted as returning before the ledger section is applied.

Report only actual conflicts/ordering hazards. Do not manufacture a conflict merely because two sections exist.

### ENTRY-05 — prompt-load evidence from the failed response

Use only observable content of the failed production response and durable current state.

Determine what it proves, and what it does NOT prove, about prompt loading.

At minimum distinguish:
- knowing the new binding revision;
- knowing stale evidence cannot be rebound;
- having actually read the full canonical worker prompt including the ledger section.

Do not equate the first two with proof of the third unless there is direct evidence.

### ENTRY-06 — task/runtime observability

Inspect whatever product/task metadata is legitimately exposed for that invocation, without triggering another run.

Look for directly observable:
- task configuration/version;
- invocation prompt/input snapshot if exposed;
- tool/runtime error;
- truncation/length warning;
- cancellation/timeout marker;
- model/tool failure;
- partial-response indicator.

If none is exposed, state `none exposed`. Do not infer hidden runtime behavior.

### ENTRY-07 — root-cause classification

Choose exactly one of:

1. `scheduled_entrypoint_mismatch`
   - actual Scheduled Task instruction is stale/incorrect and does not reliably require the canonical full prompt.

2. `canonical_prompt_internal_conflict`
   - current canonical prompt contains a real competing instruction causing the ledger requirement not to apply on this path.

3. `observable_runtime_or_tool_blocker`
   - a directly exposed runtime/tool condition prevented compliant completion.

4. `live_worker_noncompliance_without_exposed_cause`
   - entrypoint and canonical prompt are aligned, no runtime/tool blocker is exposed, but final output violated the active prompt.

5. `insufficient_observability_to_classify`
   - a required layer cannot be inspected, so more than one materially different cause remains live.

Do not create a sixth speculative category.

## Controlled proof

No production run.

If available, use only non-production/static proof to demonstrate expected behavior:
- a synthetic stop shaped like `binding_changed before publication`;
- show the canonical expected final-response obligation at contract level;
- do not ask another model/task to perform live retrieval;
- do not publish any dossier candidate.

This proof is optional if canonical text is already unambiguous.

## Acceptance checks

DIAG-01 — actual Scheduled Task entrypoint inspected, or exact tooling limitation recorded.

DIAG-02 — active canonical prompt marker and scope verified.

DIAG-03 — binding/snapshot-change early stop classified as ledger-covered or not, with refs.

DIAG-04 — competing final-response instructions checked.

DIAG-05 — failed response separated into what it proves vs does not prove.

DIAG-06 — available invocation/runtime metadata checked without another run.

DIAG-07 — one root-cause classification selected from ENTRY-07.

DIAG-08 — no production `Run now`.

DIAG-09 — no source/runtime/task/config changes except the report.

DIAG-10 — recommended next step is bounded to the confirmed divergence; if cause is not exposed, recommend the smallest observability/acceptance step rather than speculative implementation.

## Durable report

Write only:
`reviews/worker_reports/taste-dossier-scheduled-entrypoint-ledger-diagnostic-01.md`

Required sections:
1. Task / repo / mode.
2. Live symptom restatement.
3. ENTRY-01 actual Scheduled Task entrypoint.
4. ENTRY-02 canonical activation.
5. ENTRY-03 early binding-change path.
6. ENTRY-04 final-response conflicts.
7. ENTRY-05 what the failed response proves / does not prove.
8. ENTRY-06 runtime/tool observability.
9. ENTRY-07 root-cause classification.
10. DIAG-01..10 results.
11. Changes: report only.
12. Unresolved.
13. Status.
14. Exactly one recommended next step.
15. Exact refs sufficient for Director review.
16. Efficiency / reusable lesson.

Allowed statuses:
- `complete_root_cause_confirmed`
- `complete_narrowed_no_exposed_cause`
- `blocked_external`
- `needs_user_decision`

## Next-step rule

If `scheduled_entrypoint_mismatch`:
- recommend one bounded fix to the Scheduled Task entrypoint only.

If `canonical_prompt_internal_conflict`:
- recommend one bounded canonical prompt fix only.

If `observable_runtime_or_tool_blocker`:
- recommend the smallest action addressing that exact exposed blocker.

If `live_worker_noncompliance_without_exposed_cause`:
- do NOT blindly rewrite the prompt again; recommend the smallest deterministic acceptance/observability mechanism that can distinguish prompt application on the next invocation while preserving ownership boundaries.

If `insufficient_observability_to_classify`:
- recommend exactly one bounded method to expose the missing layer.

Do not run or implement that next step inside this task.

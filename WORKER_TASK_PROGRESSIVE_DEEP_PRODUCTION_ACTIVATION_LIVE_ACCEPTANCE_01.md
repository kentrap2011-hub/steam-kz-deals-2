# WORKER TASK — Progressive Deep Production Activation + Live Acceptance 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: progressive-deep-production-activation-live-acceptance-01
Mode: IMPLEMENT / ACTIVATE / VALIDATE
Worker slot: НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2

This is one task with two phases:
A. GitHub activation and operator handoff.
B. After the user performs the exact Scheduled Task action, continue in THIS SAME physical worker chat and complete live acceptance.

Do not create a second worker chat for phase B; it is a direct continuation of the same task.

## START

First open the current `CHAT_PROTOCOL.md` from main and complete its START gate.

Then read and obey:
- `config/progressive_personalization_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `reviews/worker_reports/progressive-fast-dossier-deep-architecture-amendment-01.md`
- `reviews/worker_reports/progressive-deep-runtime-adaptation-01.md`
- `DIRECTOR_TASK_BOARD.md`

Accepted production model: `FAST-DOSSIER-DEEP-V1`.

## Confirmed starting state

- Fast/PASS 1 is active provisional analysis.
- Dossier is active independent neutral evidence preparation.
- Deep/technical PASS 2 runtime is fully adapted but inactive.
- Deep normal work covers every current eligible item once an exact-compatible accepted current Dossier is ready; Fast state is not a prerequisite.
- Deep state is V2 with separate normal-first-pass and explicit GitHub-owned recovery accounting.
- Producer-owned per-game Fast/Dossier/Deep stage fields and independent statistics fields already exist.
- Current Deep attempts are zero.
- At the latest accepted runtime-adaptation snapshot, Deep projection had 22 ready/pending and 518 waiting for Dossier, but current live counts must be reread from fresh main and may legitimately differ.
- No Deep Scheduled Task has been accepted yet.

## Architecture preflight

Before any write, explicitly verify:
1. GitHub remains control-plane owner for Deep scope/order/attempts/recovery/persistence.
2. The canonical contracts authorize exactly one recurring bounded Scheduled ChatGPT Deep semantic worker.
3. Activation does not move queue/retry/recovery/completeness logic into ChatGPT.
4. No second queue, scheduler, recurring producer, hidden quota or retry loop is created.

If any of these are false or ambiguous, stop and report `needs_fix`.

# PHASE A — GitHub production activation

## 1. Fresh-main activation audit

From current `main`, identify every canonical activation mirror/guard that must change for Deep production to be authorized.

At minimum reconcile the currently canonical equivalents of:
- `config/progressive_pass2_contract.json#active`
- its `activation_guard.pass2_active`
- its `activation_guard.deep_active`
- its `activation_guard.production_execution_authorized`
- its `activation_guard.real_backlog_processing_allowed`
- runtime/status fields that currently describe Deep as inactive;
- `config/progressive_personalization_contract.json` Deep/PASS2 active mirrors;
- `config/progressive_pass1_contract.json#pass2.active`;
- `config/execution_ownership_contract.json#progressive_personalization_phase_c_pass2_core.pass2_active` and status;
- `config/daily_execution_contract.json` PASS2/Deep mirrors in progressive sections;
- any current work-manifest activation field derived from those contracts.

Do not blindly copy the old recovery-only activation plan. Use current `FAST-DOSSIER-DEEP-V1` contracts only.

## 2. Canonical scheduler identity

Canonicalize the production worker identity as:

- user-facing/internal scheduler title: `Progressive Deep Worker`
- technical implementation remains the existing Progressive PASS 2/Deep paths.
- one recurring task only.

If current contracts need a compact scheduler metadata field to make this unambiguous, add only the minimum canonical metadata. Do not create the Scheduled Task from this worker.

## 3. Activate repository truth

Make the smallest reviewed GitHub change that sets every required Deep activation mirror consistently to active/authorized.

Requirements:
- preserve `FAST-DOSSIER-DEEP-V1`;
- preserve all exact binding/liveness/recovery rules;
- preserve one normal first-pass attempt per current Deep identity;
- preserve explicit recovery authorization;
- do not alter Fast/Dossier semantic rules;
- do not alter ranking weights;
- do not consume an attempt just by activation/recompute.

After merge/commit to `main`, require relevant validation workflows to pass.

Then reread fresh main and prove:
- all activation mirrors agree;
- `progressive_pass2_work.json` is regenerated with active=true/current equivalent;
- current Deep projection is exact/current;
- durable Deep attempt count is still zero immediately after activation;
- no result/receipt was fabricated.

## 4. Scheduled Task operator handoff

After repository activation is proven, STOP before semantic execution and provide the user the exact Scheduled Task configuration below, updated only if current canonical contracts require a stronger exact equivalent.

### Duplicate guard

The user must inspect Scheduled Tasks and count BOTH legacy/current possible titles:
- `Progressive PASS 2 Worker`
- `Progressive Deep Worker`

Rules:
- if total matching count = 0: create exactly one new `Progressive Deep Worker`;
- if total matching count = 1: do not create another; verify/update that single task to the canonical Deep configuration;
- if total matching count > 1: do not enable or run any; report duplicates and wait for separately explicit dedup action.

Do not assume historical count 0 is still current.

### Scheduled Task exact configuration

Title:
`Progressive Deep Worker`

Initial state:
disabled while being configured; enable only after repository activation validation has passed.

Timing:
- exact schedule;
- once per hour at local minute 30;
- canonical operational timezone: `Europe/Samara`.

Schedule:
```text
BEGIN:VEVENT
RRULE:FREQ=HOURLY;BYMINUTE=30;BYSECOND=0
END:VEVENT
```

Exact compact loader prompt:
```text
Operate only as the bounded Progressive Deep semantic worker for repository kentrap2011-hub/steam-kz-deals-2, branch main. At the start of every invocation, first read the latest config/progressive_pass2_worker_prompt.md from main fully, then read and obey config/progressive_pass2_contract.json. If implemented != true or active != true, stop cleanly without creating any artifact. Use only the current GitHub-owned data/production/pre_ai/progressive_pass2_work.json and its exact order, work_mode values, work IDs, immutable bindings, dossier paths, result paths and terminal-receipt paths. Immediately before semantic execution of each item, apply every liveness check required by the canonical worker prompt. Deep eligibility is independent from Fast/PASS 1; never require or invent a Fast result. Never choose, rebuild, reorder, expand, retry or reinterpret scope. For recovery work, copy only the exact GitHub-provided recovery authorization/reason/binding and never invent recovery eligibility. Never modify Fast state, Dossier state, Deep eligibility/order/accounting/recovery, visual state or scheduler settings. Create only the exact create-only Deep result or terminal execution receipt authorized by the current manifest and canonical prompt. Stop cleanly when no current items remain or when runtime/tool budget no longer safely permits another item. GitHub remains the control plane for eligibility, order, validation, persistence, normal-first-pass attempts, recovery authorization, recomputation, completeness and visual projection.
```

Operator order after Phase A:
1. ensure exactly one matching Deep/PASS2 task after duplicate guard;
2. configure it exactly as above while disabled;
3. enable it;
4. press `Run now` exactly once;
5. do not press `Run now` a second time;
6. return the Scheduled Task result/output to THIS SAME worker chat.

At this point the worker should use status:
`blocked_external_operator_action`

Commit an interim durable report before waiting, so the handoff survives context loss.

# PHASE B — one-run live acceptance

After the user returns with the one `Run now` result, do not trust the chat text alone. Verify fresh GitHub canonical state.

## Required live checks

- confirm exactly current Deep work identity/authorization was consumed;
- confirm any result/receipt was accepted through canonical GitHub ingest;
- confirm attempt consumption happened only for items whose authorized semantic execution actually occurred;
- confirm normal-first-pass vs recovery accounting is correct;
- confirm no sibling item was blocked by an unrelated result/failure;
- confirm Fast and Dossier histories were not mutated by Deep;
- confirm effective-result precedence:
  - authoritative Deep fit/not-fit becomes effective source `deep`;
  - Deep incomplete/recovery preserves a still-valid Fast provisional result if one exists;
- confirm producer-owned stage fields update correctly for processed items;
- confirm Deep statistics reconcile;
- confirm work recomputes after ingest;
- confirm scheduler cardinality is one by user/operator evidence if platform inventory is not available to the worker.

### Acceptance threshold

If current active manifest had at least one executable normal/recovery Deep item when the run began:
- require at least one canonically accepted Deep semantic result for full live acceptance;
- a terminal execution receipt alone proves execution/accounting but is NOT sufficient by itself for final `complete_live_accepted`; diagnose/fix within this same task before asking for another manual run.

If the current manifest had zero executable items:
- a clean no-op is acceptable only if GitHub proves zero current executable work; never fabricate work.

If a defect is found:
- fix only the owning repository/runtime defect within this same task if it is within scope;
- preserve GitHub ownership and current architecture;
- after a fix, do NOT ask the user for another Run now until the fix is committed, validated and a new exact operator retry instruction is explicitly given.

## Validation gates

- ACT-01: all canonical Deep activation mirrors are consistent and true.
- ACT-02: activation/recompute alone consumes zero attempts.
- ACT-03: active work manifest uses current `FAST-DOSSIER-DEEP-V1` predicate.
- ACT-04: exactly one canonical scheduler identity/config is defined.
- ACT-05: one manual Run now uses only GitHub-prepared exact work.
- ACT-06: at least one exact Deep result is canonically accepted when executable work existed.
- ACT-07: normal first-pass/recovery attempt accounting is exact.
- ACT-08: one item failure/unresolved cannot block siblings.
- ACT-09: Fast/Dossier histories are unchanged by Deep ingest.
- ACT-10: Deep-over-Fast effective precedence works; unresolved Deep preserves valid Fast fallback.
- ACT-11: per-game Fast/Dossier/Deep stage fields update producer-side.
- ACT-12: stage statistics reconcile independently.
- ACT-13: active work is recomputed after acceptance.
- ACT-14: no browser-side semantic inference is introduced.
- ACT-15: no second scheduler/queue/retry loop is created.
- ACT-16: relevant focused/canonical regressions pass.
- ACT-17: durable final report is committed and reread from main.

## Durable report

Use:
`reviews/worker_reports/progressive-deep-production-activation-live-acceptance-01.md`

The same report may first be committed with interim status `blocked_external_operator_action`, then updated after Phase B.

Final report must include:
- activation files/refs;
- exact current active Deep counts before first run;
- Scheduled Task canonical config;
- user/operator action evidence;
- exact first-run artifacts/receipts and ingest refs;
- before/after Deep state/statistics;
- processed item identities and outcomes at a bounded summary level;
- proof Fast/Dossier were not mutated;
- validation ACT-01..17;
- exact refs;
- final status;
- exactly one recommended next step.

Allowed statuses:
- blocked_external_operator_action
- complete_live_accepted
- needs_fix
- needs_user_decision

Before every completion/final response, commit and reread the exact report from `main`.

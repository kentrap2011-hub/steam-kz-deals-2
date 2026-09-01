# WORKER TASK — CHAT 2

Task ID: `worker-efficiency-guardrails-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/worker-efficiency-guardrails-01.md`

## Goal

Implement only the minimal durable process mechanism recommended by `worker-efficiency-audit-01`.

Do not repeat the audit and do not inspect more historical tasks unless a concrete wording conflict requires a bounded check.

## Read first

- `reviews/worker_reports/worker-efficiency-audit-01.md`
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`

## Required changes

### 1. Create `KNOWN_WORKER_PITFALLS.md`

Purpose: compact canonical home for reusable cross-cutting operational failure recipes that do not belong in:
- `PROJECT_ROUTES.md` (`where/how`), or
- `PROJECT_DECISIONS.md` (`why an architecture/product decision exists`).

Keep each entry compact:
- Trigger / symptom
- Do not repeat
- Correct move
- Evidence refs

Seed only the three patterns proven by the audit:
1. behavioral contract/outcome vs source-shape/static-proxy validation;
2. GitHub Pages concurrency + already-uploaded artifact rerun trap;
3. architecture/source preflight before recommending IMPLEMENT that would add/change source/runtime/workflow/schedule/queue/retry/checkpoint/ownership.

Do not turn the file into a generic troubleshooting diary.

### 2. Update `CHAT_PROTOCOL.md`

Add only the minimal hooks recommended by the audit:

- START: after checking `PROJECT_ROUTES.md`, check relevant `KNOWN_WORKER_PITFALLS.md` entries when the task matches a known trigger. Do not require broad pitfall/history reading for unrelated tasks.

- PRE-SEND: if the task encountered a reusable avoidable detour or a user/CI correction exposed one, persist it in the correct durable home:
  - `PROJECT_ROUTES.md`,
  - `PROJECT_DECISIONS.md`, or
  - `KNOWN_WORKER_PITFALLS.md`.
  If task boundaries are read-only and prohibit that edit, the report must name the exact route/pitfall candidate for one bounded follow-up.

- Extend architecture preflight wording so it applies not only to immediate implementation but also to a worker's **Recommended next step**. If the proposed next step would add/change source/runtime/workflow/schedule/queue/retry/checkpoint/ownership and the canonical authority/route is not proven, recommend RECON/CONTRACT rather than IMPLEMENT.

### 3. Update `DIRECTOR_PROTOCOL.md`

Add one conditional compact worker-report field:

`Efficiency / reusable lesson: none | <short candidate/ref>`

It must remain `none` for normal tasks and must not become a narrative section or a mandatory essay.

## Hard boundaries

Do NOT:
- change product code;
- change production workflows or schedules;
- add telemetry, time tracking, quotas, dashboards, performance scores or arbitrary duration targets;
- add report-path automation;
- create a new CI workflow solely for these docs;
- add more pitfall entries beyond the three audit-proven seeds;
- weaken validation/acceptance for speed.

## Validation

- confirm all referenced files remain internally consistent;
- confirm `KNOWN_WORKER_PITFALLS.md` clearly distinguishes itself from routes and decisions;
- confirm START does not require reading the entire pitfalls file for unrelated tasks;
- confirm PRE-SEND architecture wording explicitly covers `Recommended next step`;
- confirm no product/runtime files changed.

## Done when

- `KNOWN_WORKER_PITFALLS.md` exists with exactly the three seeded high-value recipes;
- `CHAT_PROTOCOL.md` has the minimal START/PRE-SEND hooks and expanded next-step architecture preflight;
- `DIRECTOR_PROTOCOL.md` has the one-line conditional efficiency field;
- no product/runtime behavior changed.

## Report format

Save:
`reviews/worker_reports/worker-efficiency-guardrails-01.md`

### Task
What was changed.

### Changes
Exact files/commit.

### Validation
Compact consistency checks.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only; `none` is acceptable if no follow-up is needed.

Final response must include report path and exact commit ref.
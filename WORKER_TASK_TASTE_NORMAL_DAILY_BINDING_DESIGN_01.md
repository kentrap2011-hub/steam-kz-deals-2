# WORKER TASK — DESIGN NORMAL DAILY TASTE BINDING

## Task ID
`taste-normal-daily-binding-design-01`

## Mode
`DESIGN ONLY / NO PRODUCTION MUTATION`

## Expected report
`reviews/worker_reports/taste-normal-daily-binding-design-01.md`

## Goal
Define the exact canonical normal-daily Scheduled Task consumer rule that is currently missing, so Taste can later be enabled safely without ChatGPT inventing queue/quota policy at runtime.

## Context
The transition report `reviews/worker_reports/taste-normal-daily-operation-enable-01.md` stopped safely with `blocked_missing_production_definition` because current contracts do not unambiguously define:
- the exact subset of the GitHub-prepared Taste queue authorized per Scheduled Task invocation;
- the bounded per-run work limit or equivalent bound;
- the deterministic stop/resume rule;
- how this interacts with the rule that checkpoint/chunk size must not silently become a daily quota.

Current unresolved semantic queue count in that report: 566.

## Mandatory execution order

### Step 1 — create report first
The FIRST repository mutation after reading this task must be creation of the expected report with:
- lifecycle: `in_progress`;
- current UTC;
- decision: `pending`;
- next action: inspect only the exact current ownership/daily-execution/producer contracts referenced by the blocking report.

Commit immediately. If report creation fails, STOP.

### Step 2 — use existing architecture, do not redesign the system
Read once:
- `reviews/worker_reports/taste-normal-daily-operation-enable-01.md`

Then inspect only the exact current contracts/configs it names plus any directly referenced producer-binding definition needed to resolve the missing rule.

Do NOT broaden into a general architecture review.

### Step 3 — produce one concrete production binding design
The report must answer, concretely and unambiguously:

1. **Selection authority** — which component chooses the work items for one daily run. Preserve GitHub as owner of scope/queue selection; ChatGPT must consume only explicitly prepared work.
2. **Per-run bound** — define the exact bounded amount of semantic work a single Scheduled Task invocation may consume, or define an equivalent bounded prepared-batch mechanism. It must prevent draining all 566 items accidentally.
3. **Stop rule** — define exactly when that invocation stops.
4. **Resume rule** — define how remaining work stays pending for the next normal run without manual repair.
5. **Profile concurrency** — preserve immutable current-live-profile freeze/binding and bounded retry behavior; no user quiet window.
6. **Safety contracts** — preserve generation 2, V5, exact binding/fingerprint/context checks, evidence sufficiency, normalized factors, price-blind/no-commercial/no-review-sentiment-as-fit protections.
7. **Cost/infra** — no paid OpenAI API, Copilot runtime, new paid service, new external scheduler, or second Scheduled Task.
8. **No quota confusion** — explain why the chosen per-run bound is an execution safety bound and not a business/daily-completeness quota. GitHub remains free to prepare future bounded work according to its canonical control-plane logic.

### Design preference
Prefer the smallest change consistent with current contracts. If the existing system already has a natural prepared-batch/chunk mechanism, reuse it rather than inventing a new parallel queue.

If more than one safe design is possible, choose one recommended design and briefly state why it is safer/simpler than the alternatives.

## Boundaries
- DESIGN ONLY.
- Do not modify Scheduled Tasks.
- Do not run semantic evaluation.
- Do not ingest.
- Do not change queue, cache, production state, code, or config.
- Only the durable report may be created/updated.

## Finish
Finalize the report with one of:
- `complete_design_ready_for_implementation`
- `blocked_missing_architecture_fact`
- `needs_followup`

If complete, include a paste-ready exact specification for the later implementation task, including the recommended bound/selection/stop/resume semantics.

Then STOP.

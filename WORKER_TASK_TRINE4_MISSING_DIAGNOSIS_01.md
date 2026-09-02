# WORKER TASK — NEW CHAT 1

Task ID: `trine4-missing-diagnosis-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/trine4-missing-diagnosis-01.md`

## Priority context

The user explicitly promoted this task ahead of giveaway-analysis enrichment because `Trine 4` is currently discounted. Diagnose it while the live sale state still exists so the canonical route can be observed under the condition in which the game is expected to be eligible.

Do not delay the trace until after the discount disappears if the task can be completed now.

## Goal

Find the exact first canonical point where `Trine 4` disappears from the current production path and explain why it is absent from the final user-visible game list.

Do not assume the cause is Taste, price, ranking, ownership, package identity, or region until the route proves it.

This is diagnosis only. Do not force-add the game and do not broaden into a general feed redesign.

## Read first

- `CHAT_PROTOCOL.md`
- relevant `PROJECT_ROUTES.md` entries
- relevant `KNOWN_WORKER_PITFALLS.md` entry only if a known trigger matches
- `config/execution_ownership_contract.json`
- the smallest current canonical source -> shortlist -> visual route needed to trace one exact Steam game

Do not perform broad history archaeology.

## Required trace

### 1. Canonical identity

Resolve `Trine 4` to the exact canonical Steam/app/product identity used by current production.

Do not trace by title alone after identity is established.

### 2. Capture the live sale state first

Before deeper tracing, record the current canonical facts that prove the live sale context for the exact Trine 4 identity:
- KZ availability;
- current price;
- discount percent / deal state;
- relevant source timestamp.

Use canonical project data first. If canonical data is stale/incomplete, report that as part of the diagnosis rather than substituting an unrelated source silently.

### 3. First disappearance point

Trace that exact identity through the current canonical path and stop at the **first stage where it is present before and absent after**.

Check only as needed:
- Steam KZ source/catalog presence and current region availability;
- current price/discount/deal facts;
- ownership / played / wishlist state used by production;
- package/bundle identity or constituent handling;
- eligibility / Taste gate;
- deal/history quality gate;
- ranking / cutoff;
- final visual payload/card assembly.

For every stage inspected, record:
- exact artifact/path;
- whether Trine 4 is present;
- relevant canonical reason/status fields;
- first exclusion reason.

### 4. Correctness classification

Classify the result as exactly one of:

A. `expected_exclusion`
- current rules intentionally exclude the game and the exclusion is consistent with product rules;

B. `systemic_defect`
- a generic rule/data/identity bug wrongly removes Trine 4 and could affect other games;

C. `stale_or_incomplete_data`
- canonical data needed for the decision is missing/stale/incomplete;

D. `needs_user_decision`
- repository evidence shows multiple legitimate product semantics and existing rules do not determine which one is intended.

Do not use `expected_exclusion` merely because the code currently behaves that way; compare against canonical product rules.

### 5. Scope of impact

If the cause is systemic, use only a bounded sample or existing counts to determine whether it likely affects other games.

Do not manually scan the whole catalog item-by-item.

### 6. Next step

If `systemic_defect`, recommend one bounded IMPLEMENT fixing the generic rule plus a regression for Trine 4's failure shape.

If `expected_exclusion`, explain plainly why the game should not be in the current list and recommend `none` unless a separate product-rule change is desired.

If `stale_or_incomplete_data`, identify the owning existing GitHub/runtime route that must refresh it; do not create a second queue/scheduler.

## Hard boundaries

Do NOT:
- add Trine 4 manually or special-case its app ID;
- change ranking/Taste rules in this RECON;
- use title-only identity after canonical ID is known;
- perform broad code/history archaeology;
- create a new external runtime, queue or scheduler;
- infer a failure reason from absence alone;
- treat price/rank as personal Taste evidence.

## Report format

Save:
`reviews/worker_reports/trine4-missing-diagnosis-01.md`

### Task
What was traced.

### Canonical identity
Exact Steam/app/product identity.

### Live sale state
Current canonical KZ price/discount/source timestamp captured while the discount is active.

### Trace
Compact stage-by-stage presence/exclusion evidence.

### First disappearance point
Exact first stage and canonical reason.

### Classification
Exactly one:
- `expected_exclusion`
- `systemic_defect`
- `stale_or_incomplete_data`
- `needs_user_decision`

### Scope of impact
Bounded evidence only.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded step only; `none` is acceptable.

Final response must include report path and exact refs.
# WORKER TASK — CHAT 2

Task ID: `card-explanation-audit-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/card-explanation-audit-01.md`

## Goal

Audit the current user-facing card explanations — especially the text equivalent to “почему подходит” / “почему может не подойти” — and determine whether they are specific, evidence-based, useful, and aligned with the canonical Taste/profile evidence.

This is diagnosis only. Do not change ranking, Taste, prompts, UI, producer code, workflows, or production data.

## Why this can run in parallel

This task is intentionally read-only except for its report and is independent of the current Chat 1 package/UI blocker fix. Do not edit shared runtime/visual/UI files.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- current canonical final visual payload/schema/producer route identified from `PROJECT_ROUTES.md`
- current canonical Taste profile/blob and any result contract actually referenced by the current production payload

## Scope

Use one bounded diagnostic sample only:
- current top 30 visible/ranked cards, or the smallest equivalent bounded sample already used by the canonical visual audit route;
- do not inspect/process the whole catalog;
- do not write any sampled judgments back into production data.

## What to assess

For each sampled card, identify the actual fields rendered or intended as positive/negative fit explanation and classify their quality.

Evaluate at least:

1. **Specificity**
   - Does the explanation say something concrete about this game and this user?
   - Or is it generic filler that could fit almost any game?

2. **Evidence alignment**
   - Is each claim supported by canonical game metadata/Taste evidence/current card facts?
   - Flag invented, overstated, contradictory, or unsupported claims.

3. **Taste usefulness**
   - Does “why fits” connect to meaningful positive user preferences?
   - Does “why may not fit” surface a real risk/tradeoff rather than boilerplate caution?

4. **Non-duplication**
   - Are positive/negative explanations merely restating genre/title/description/rating?
   - Are multiple cards receiving near-identical wording without game-specific reason?

5. **Calibration**
   - Strong claims should require strong evidence.
   - Weak/unknown evidence should be expressed cautiously rather than as certainty.

6. **Contradictions with score/rank**
   - Identify cards where explanation materially conflicts with displayed detailed score, Taste result, or ranking reason.
   - Do not change scoring in this task.

7. **User-facing clarity**
   - Russian should be natural, concise, and understandable without internal project jargon.

## Required output metrics

Give compact counts for the bounded sample, for example:
- `good_specific`
- `generic_but_not_wrong`
- `unsupported_or_invented`
- `contradictory`
- `missing_or_unhelpful`

Also identify recurring failure patterns and 3–8 representative examples with appid/title/rank and the exact problem category. Quote only short fragments when needed.

## Root-cause tracing

For each major recurring failure pattern, trace only far enough to say which layer most likely owns the problem:
- scheduled ChatGPT Taste/result generation;
- deterministic final producer/formatter;
- source data insufficiency;
- UI presentation only;
- unclear/other.

Do not implement the fix.

## Hard boundaries

Do NOT:
- rewrite any live explanation text;
- manually improve sampled cards;
- change ranking weights or ranks;
- change Taste profile/results/contracts;
- alter ChatGPT schedules/queues;
- touch Russian-description translation work;
- touch duration/IGDB;
- touch package UI;
- inspect more than the bounded sample unless a tiny additional record is strictly required to prove a root cause.

## Done when

- bounded current sample audited;
- quality counts and recurring patterns recorded;
- representative bad/good examples identified;
- likely owning layer identified for each recurring problem;
- one bounded next implementation/recon step recommended.

## Report format

Save:
`reviews/worker_reports/card-explanation-audit-01.md`

### Task
Sample and fields audited.

### Verified facts
Where explanations originate and what evidence they use.

### Quality counts
Compact table/counts.

### Representative examples
3–8 concise examples.

### Failure patterns
Recurring issues, severity, likely owner.

### Validation
Canonical files/artifacts inspected; no production writes.

### Unresolved
Real uncertainties only.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only.

Final response must include report path and commit ref.
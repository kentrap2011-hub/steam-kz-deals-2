# WORKER TASK — PROGRESSIVE FAST INSUFFICIENT EVIDENCE REVIEW 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `progressive-fast-insufficient-evidence-review-01`
Mode: `READ-ONLY / RECON / SEMANTIC QUALITY REVIEW`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/progressive-fast-insufficient-evidence-review-01.md`

## User intent

Independently review the four real Fast/PASS 1 results from the latest post-fix invocation that ended as:

`analysis_incomplete / insufficient_evidence`

Games:
- `RV There Yet?` — App_3949040
- `Uncanny Tales: Cold Road` — App_3534240
- `Nimbatus - The Space Drone Constructor` — App_383840
- `Borderlands 3` — App_397540

The user wants to know whether Fast genuinely lacked enough evidence for a trustworthy fit/not-fit conclusion, or whether adequate lightweight evidence was available and the worker stopped too early.

This is a review only.

Do not modify any Fast/Deep/Dossier state.
Do not create replacement Fast results.
Do not run production Fast/Deep/Dossier.
Do not change prompts/contracts/Scheduled Tasks.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

## Mandatory canonical inputs

Read current:
- `DIRECTOR_TASK_BOARD.md`
- `PROJECT_DECISIONS.md`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- `config/execution_ownership_contract.json`
- current pinned profile identity from `data/production/pre_ai/progressive_pass1_work.json`

For each of the four games, recover the exact historical Fast work item and exact submitted result from the real invocation around:
`2026-09-24T10:02:37Z..10:02:53Z`

Use exact work authority commit:
`3aec5050283ec006fefa66f70d7473a499ced2f9`

Use the exact pinned Taste profile referenced by that invocation. Do not substitute remembered user preferences or a newer mutable profile.

## Review standard

Judge the original Fast result against the actual Fast contract, not against Deep standards.

Fast is allowed to:
- use the exact candidate semantic input;
- use the pinned Taste profile;
- use lightweight public evidence sufficient for a trustworthy decision;
- stop early once fit/not-fit is trustworthy.

Fast is NOT required to:
- build a full Dossier;
- find Russian Steam reviews universally;
- exhaustively research every source;
- perform Deep-level evidence recovery.

Therefore the key question is:

**Was there reasonably accessible lightweight evidence at the time that should have been enough for Fast to reach a trustworthy fit/not-fit decision?**

## Web evidence

Use current public web evidence carefully.

For each game:
- identify exact-product official/store/reputable descriptive sources;
- prefer sources that describe gameplay loop, structure, genre, co-op/single-player requirements, combat/puzzle/exploration emphasis, progression and other Taste-relevant traits;
- do not use price/discount/popularity as Taste evidence;
- do not treat current evidence as proof that the exact same page was indexed identically at 10:02Z; separate “evidence exists and is readily discoverable now” from claims about exact historical retrieval availability.

Use the minimum evidence needed to judge Fast sufficiency.

## Required per-game analysis

For each game produce:

1. Exact Fast semantic input available at invocation.
2. Exact Fast result: `analysis_incomplete / insufficient_evidence`.
3. Relevant pinned-profile preferences that actually matter.
4. Lightweight public evidence found.
5. Whether that evidence is sufficient under Fast standards for:
   - `analyzed_fit`
   - `analyzed_not_fit`
   - or still legitimately `analysis_incomplete`
6. Whether the original Fast decision was:
   - `JUSTIFIED_INSUFFICIENT_EVIDENCE`
   - `TOO_CONSERVATIVE_EVIDENCE_WAS_AVAILABLE`
   - `UNPROVABLE_HISTORICAL_RETRIEVAL_LIMITATION`
7. Short explanation.

Do NOT convert this review into a replacement canonical Fast result.

## Special caution

A game may have obvious general genre information but still lack enough personalized evidence for the user's pinned profile.

Conversely, a familiar/major game such as Borderlands 3 must not be left as “insufficient” merely because the worker failed to use readily available exact-product gameplay evidence, if that evidence plus the pinned profile would have supported a trustworthy Fast conclusion.

Do not assume either outcome in advance.

## Cross-game diagnosis

After reviewing all four, determine whether there is a common Fast-quality issue such as:
- worker relying too heavily on only the prepared short description/tags;
- failure to perform even light web retrieval;
- overly high confidence threshold;
- evidence strategy not being followed;
- or no common issue.

Do not recommend implementation unless the evidence demonstrates a repeatable defect.

## Required final classification

For each game, one of:
- `JUSTIFIED_INSUFFICIENT_EVIDENCE`
- `TOO_CONSERVATIVE_EVIDENCE_WAS_AVAILABLE`
- `UNPROVABLE_HISTORICAL_RETRIEVAL_LIMITATION`

And one overall:
- `FAST_BEHAVIOR_ACCEPTABLE`
- `FAST_TOO_CONSERVATIVE_PATTERN_CONFIRMED`
- `MIXED_RESULTS`
- `INSUFFICIENT_EVIDENCE_TO_JUDGE_WORKER`

## No implementation

Do not:
- edit source/contracts/prompts;
- replace the four Fast results;
- reset attempts;
- authorize retry/recovery;
- modify Scheduled Tasks;
- manually run semantic production;
- create Fast/Deep transport artifacts.

Only the durable report may be committed.

## Durable report

Commit:
`reviews/worker_reports/progressive-fast-insufficient-evidence-review-01.md`

Required sections:
1. Final status.
2. Exact invocation/profile/work authority used.
3. Per-game review table.
4. Detailed evidence for each game.
5. Historical retrieval limitations.
6. Cross-game diagnosis.
7. Whether any repeatable Fast-quality defect is confirmed.
8. Recommended next Director step, diagnostic only.
9. Confirmation that no production/state/scheduler mutation occurred.

Allowed final statuses:
- `complete_ready_for_director_review`
- `needs_more_recon`
- `blocked`

Before completion:
- commit the report to `main`;
- reread the exact committed report from fresh `main`.

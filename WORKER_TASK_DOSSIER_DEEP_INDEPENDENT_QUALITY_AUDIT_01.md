# WORKER TASK — Independent Dossier + Deep quality audit 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `DOSSIER_DEEP_INDEPENDENT_QUALITY_AUDIT_01`
Worker slot: `ЧАТ 2`
Mode: `READ-ONLY / INDEPENDENT AUDIT`

## Purpose

Independently audit how complete, accurate, well-grounded, and useful the current Taste Steam Review Dossier and Progressive Deep analysis actually are.

This is **not** a Dossier semantic-worker invocation and **not** a Progressive Deep semantic-worker invocation.

Do not execute their worker prompts as operational instructions. Read their prompts/contracts/schemas only as artifacts that define what the system claims it should do, then independently test whether real outputs actually meet that standard and whether that standard itself is sufficient for the product goal.

The audit must be willing to conclude that current rules, evidence gathering, scoring, or outputs are insufficient even when they technically satisfy the existing contracts.

## START

1. Read current `CHAT_PROTOCOL.md` and perform the normal repository START gate.
2. Read only the minimum project context needed to understand the product goal and the two semantic stages.
3. Read the current canonical Dossier and Deep prompts/contracts/schemas required to understand expected behavior.
4. Read current canonical Dossier and Deep status/manifests.
5. Do not modify production state, queues, prompts, contracts, schedules, results, or UI.

## Independent-audit principle

Do not assume:
- a result is correct because GitHub accepted it;
- a Dossier is complete because it is schema-valid;
- a Deep result is correct because it is marked fit/not_fit;
- a score is justified because fields are populated;
- more citations automatically mean better analysis.

Judge the semantic quality from the actual evidence and reasoning.

You may use current public web evidence where needed to verify factual claims, review themes, game mechanics, recurring negatives, and whether the Dossier captured the important player-feedback picture.

## Product questions the audit must answer

1. Does Dossier capture the **important recurring positive and negative player feedback**, or does it miss material themes?
2. Are the cited/referenced review claims actually supported by the underlying evidence?
3. Does Dossier distinguish recurring patterns from anecdotes strongly enough?
4. Is source coverage broad enough across languages/recency/positive-negative perspectives?
5. Does Deep actually use the Dossier faithfully, or does it ignore/distort material evidence?
6. Are Deep `fit` / `not_fit` outcomes believable given the user's taste profile and the evidence?
7. Is the 0–100 taste score meaningfully calibrated, or are scores compressed/arbitrary/inconsistent?
8. Are the stated pluses/minuses the real reasons for the score/outcome, rather than generic filler?
9. Do similar games receive reasonably consistent treatment?
10. Are there cases where a game is scored confidently despite weak or incomplete evidence?
11. Does the current analysis provide enough information for the final site ranking and purchasing decision?
12. What important information is systematically missing from either stage?
13. Are there current rules that technically improve validation but accidentally reduce semantic usefulness?

## Sampling

Do not audit only convenient recent successes.

Build a **stratified sample** from current canonical data.

Minimum:
- at least **12 accepted Dossiers**;
- at least **20 authoritative Deep results**.

The Deep sample must include:
- both `fit` and `not_fit`;
- high, middle, and low taste-score ranges where available;
- recent results and older still-current results;
- different genres;
- games with strong review volume and weaker review volume;
- at least several cases where the final outcome is potentially debatable or close.

Whenever possible, pair a sampled Deep result with its exact accepted Dossier and inspect the full chain.

If a systematic issue is found, expand the sample enough to determine whether it is isolated or recurring.

Do not claim a percentage for the whole corpus from a small sample unless clearly labelled as sample-only.

## Audit dimensions and scoring

Give separate 0–100 audit scores for:

1. **Dossier evidence completeness**
2. **Dossier factual/evidence correctness**
3. **Dossier balance and recurrence quality**
4. **Deep use of Dossier evidence**
5. **Deep fit/not_fit correctness**
6. **Taste-score calibration**
7. **Deep explanation quality / transparency**
8. **Cross-game consistency**
9. **Overall usefulness for purchase ranking**

Then give one overall system-quality score 0–100.

For every score:
- explain what would be required for 100;
- explain the main reasons points were lost;
- distinguish confirmed defects from judgement calls.

## Required spot checks

For sampled items, explicitly verify:
- title/AppID identity;
- Dossier evidence belongs to the correct game/release;
- cited review themes are not invented or overstated;
- negative evidence is not omitted when it is materially recurring;
- positive evidence is not omitted when it materially matters;
- recurrence labels match the actual number/diversity of supporting records;
- time-sensitive claims are not presented as current when evidence is old;
- Deep does not contradict the Dossier without explaining why;
- Deep score/outcome is compatible with the stated reasons;
- a high taste score does not coexist with unexplained major negatives;
- a low score is not based only on absence of evidence;
- `not_fit` is not being used merely because evidence is incomplete.

## Calibration / comparative checks

Select several pairs or small groups of broadly comparable games and ask:
- would a reasonable reviewer using the same user taste profile rank them in the same relative order?
- do score differences correspond to meaningful evidence differences?
- are review-count/popularity differences being over- or under-weighted?
- are genre/taste preferences applied consistently?

Call out concrete contradictions.

## Completeness audit of Dossier source strategy

Independently assess whether the current evidence strategy is sufficient:
- Steam reviews only vs broader useful sources;
- Russian vs non-Russian coverage;
- recent vs lifetime review balance;
- handling of small samples;
- handling of patches/major updates;
- handling of multiplayer population/technical health when relevant;
- handling of DLC/bundle-specific concerns when relevant.

Do not propose broadening sources unless it materially improves decision quality.

## What not to do

Do not:
- modify any Dossier or Deep result;
- create or ingest semantic result files;
- change prompts/contracts/schemas;
- change queues/order/recovery;
- change ranking/site/publication;
- create or modify Scheduled Tasks;
- implement fixes;
- restart Dossier or Deep;
- treat this audit as production semantic work.

This is read-only diagnosis only.

## Report

Create:
`reviews/worker_reports/dossier-deep-independent-quality-audit-01.md`

The report must contain:

1. Executive verdict in plain language.
2. Overall 0–100 score.
3. The nine component scores.
4. Sample methodology and exact sampled AppIDs/titles.
5. At least 5 examples of analysis that was done well.
6. At least 5 concrete weaknesses/errors if present.
7. For every serious issue, show the exact Dossier/Deep artifact involved and the evidence for the criticism.
8. Separate:
   - isolated mistakes;
   - recurring systematic weaknesses;
   - limitations caused by the current rules themselves.
9. Estimate whether the current system is:
   - trustworthy enough for rough ranking;
   - trustworthy enough for top-100 ordering;
   - trustworthy enough for a confident purchase recommendation.
10. Rank the most valuable improvements by expected impact.
11. Clearly mark which improvements require changing Dossier, which require changing Deep, and which require no semantic-worker change.
12. No implementation in this task.

## Final status

End with one of:
- `audit_complete_quality_acceptable`
- `audit_complete_quality_acceptable_with_material_weaknesses`
- `audit_complete_systematic_quality_problems_found`
- `audit_blocked_insufficient_evidence`

Do not soften the conclusion to match existing project assumptions.

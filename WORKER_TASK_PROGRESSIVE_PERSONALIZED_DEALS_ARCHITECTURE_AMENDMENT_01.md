# WORKER TASK — PROGRESSIVE PERSONALIZED DEALS ARCHITECTURE AMENDMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `progressive-personalized-deals-architecture-amendment-01`
Mode: `READ-ONLY / ARCHITECTURE AMENDMENT`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.

Затем открой этот task-файл из `main`.

Это прямое продолжение:
- `WORKER_TASK_PRODUCTION_ARCHITECTURE_SIMPLIFICATION_REVIEW_01.md`
- `reviews/worker_reports/production-architecture-simplification-review-01.md`

Не начинай общий аудит заново.

## User correction — authoritative product direction for this amendment

The user rejected the idea that unresolved/unanalysed games should compete on equal footing with personalized games.

The product remains PERSONALIZED DEAL DISCOVERY.

Required visible ordering concept:

1. Successfully analysed games that fit the user — FIRST.
2. Games whose analysis was attempted but could not be completed — AFTER successful fit results.
3. Games not yet analysed at all — LAST.
4. Successfully analysed games that do NOT fit the user — excluded from the normal visible list.

All current deterministic-eligible deal candidates must be visible before analysis finishes, unless they are excluded by an existing hard deterministic business/source/identity rule.

A game must NOT disappear merely because analysis has not yet run.

If later analysis concludes the game does not fit the user, it is then removed from the normal list.

## Required progressive-state model

Design a minimal explicit per-item state machine.

At minimum cover:

- `not_analyzed`
- `analysis_in_progress` if a durable state is actually necessary; otherwise explain why it should remain ephemeral
- `analyzed_fit`
- `analyzed_not_fit`
- `analysis_incomplete` / `analysis_error`

Do not proliferate states without need.

For every state define:
- whether the game is visible on the site;
- its sort tier;
- whether personalized score/text may be shown;
- whether it counts as successfully processed;
- whether it enters retry/second-pass work;
- what transition can move it out of that state.

## Required two-pass architecture

### PASS 1 — coverage first

The first pass must attempt every current unresolved candidate once.

Critical rule:
- one game's failure must not block the next game;
- group/batch transport may remain an efficiency detail, but outcome and forward progress must be item-level.

Each candidate must finish PASS 1 in exactly one durable outcome class:
- analysed fit;
- analysed not fit;
- incomplete/error.

Games not yet reached by PASS 1 remain `not_analyzed` and must still appear at the bottom of the site.

PASS 1 must prioritize broad catalogue coverage over deep recovery on a single difficult item.

### PASS 2 — recovery only

After or independently behind PASS 1 coverage, only items in incomplete/error state receive deeper recovery work.

Assess and define:
- whether PASS 2 starts only after PASS 1 has covered the full current candidate set, or may run opportunistically without starving first-pass coverage;
- how GitHub owns the retry/recovery set;
- how many retry classes/states are actually necessary;
- how to prevent one permanently difficult item from creating an infinite retry loop;
- how a recovered item becomes `analyzed_fit` or `analyzed_not_fit`;
- how a still-unresolved item remains visible and explicitly marked without blocking publication.

Do NOT introduce conversational retries.

## Required sorting contract

Design an exact tiered ordering that implements the user's intended product behavior.

Tier 1:
- `analyzed_fit`
- sorted by the existing personalized ranking authority / current personalized score semantics, unless a canonical conflict is proven.

Tier 2:
- `analysis_incomplete` / error
- no fake personal score;
- define deterministic secondary ordering, likely deal quality / urgency using existing producer-owned signals.

Tier 3:
- `not_analyzed`
- no fake personal score;
- define deterministic secondary ordering using existing producer-owned deal signals.

`analyzed_not_fit`:
- excluded from normal list.

Important:
- do not compare a partial purchase score against a full personalized score as though they were the same scale;
- sort by tier first, then tier-specific ordering;
- preserve existing user-controlled urgency behavior if compatible, or explain the smallest required adjustment.

## Required site visibility / control model

The website must clearly show analysis status per game.

At minimum define user-facing labels for:
- analysed / personalized;
- analysis incomplete/error;
- not analysed yet.

The website must also expose an aggregate processing status that lets the user monitor the pipeline directly from the site.

At minimum:
- total current deterministic-eligible candidates;
- successfully processed/analyzed count;
- processing error/incomplete count.

Also assess whether to expose:
- fit count;
- not-fit count;
- not-analyzed count;
- second-pass/retry count;
- last successful analysis/update timestamp.

Do not add metrics merely because they are available. Recommend the smallest useful set.

Counts must be GitHub-owned machine data, not calculated from hidden ChatGPT prose.

Define exact arithmetic invariants, e.g. how totals reconcile:
`total = analyzed_fit + analyzed_not_fit + analysis_error + not_analyzed (+ in_progress if durable)`

If in-progress is ephemeral, define how the site avoids inconsistent totals.

## Required publication behavior

A fresh current deterministic candidate set should be publishable immediately even if zero items are analysed.

Example acceptable beginning state:
- total = 734;
- analysed fit = 0;
- analysed not fit = 0;
- errors = 0;
- not analysed = 734.

As PASS 1 advances, the same current catalogue progressively changes state without requiring global completion.

Publication must never wait for:
- all Taste results;
- all Dossiers;
- all Russian review retrieval;
- all PASS 1 outcomes;
- all PASS 2 recovery.

But hard source-integrity/current-offer/business exclusions remain authoritative.

## Required analysis of existing group/checkpoint semantics

Explicitly determine what happens to the current dossier group-of-three / maximal-contiguous-prefix model.

The user requirement is:
- a failure for one game must not discard or block valid analysis of unrelated games.

Therefore assess:
- whether groups can remain transport-only;
- what must change so acceptance/progress becomes item-level;
- whether existing exact binding/provenance validation can be preserved per item;
- what existing group-level invariants become background implementation details or should be retired.

Do not weaken evidence correctness for an item merely to gain throughput.

## Required interaction with Dossier / Taste

Decide the minimum semantic pipeline needed for PASS 1.

Question to answer:
- Does PASS 1 truly require the full current Dossier process for every game, or can it make the fit/not-fit decision from lighter existing semantic inputs while Dossier becomes PASS 2/background enrichment?

Do not assume either answer.

Compare:
A. full Dossier required before fit verdict;
B. lightweight fit verdict first, Dossier only for richer explanation/risk/current-state evidence;
C. hybrid based on availability of cached compatible evidence.

Recommend exactly one.

The chosen design must preserve honesty:
- no `analyzed_fit` if the semantic evidence is insufficient under the chosen contract;
- no fabricated why-fit or risk text.

## Required failure semantics

For each, state what the user sees and what continues:
- Scheduled ChatGPT does not run;
- one item errors;
- batch/group contains one bad item;
- Russian review unavailable;
- Dossier incomplete;
- binding changes;
- accepted cached Taste exists;
- analysis result is invalid;
- PASS 2 repeatedly cannot resolve an item.

No single item-level enrichment failure may block unrelated items or site publication.

## Required implementation staging

Do NOT implement.

Propose a staged IMPLEMENT plan that minimizes time until user-visible improvement.

At minimum:

### Phase A — progressive display + state/count model
Get all deterministic eligible games onto the site with correct tiers/status/counts without pretending they are personalized.

### Phase B — item-level PASS 1
Make semantic analysis advance one item at a time without global blocking.

### Phase C — PASS 2 recovery
Deep retry/retrieval for incomplete items only.

### Phase D — cleanup
Retire old global/group blocking machinery after new path is proven.

For each phase define:
- smallest canonical/source/UI surfaces likely to change;
- acceptance criteria;
- rollback;
- whether production can already provide useful personalized ordering after that phase.

## Architecture preflight

Explicitly answer:
1. Which component owns the item analysis state?
2. Which component owns PASS 1 and PASS 2 queue/order?
3. Which component owns canonical retry decisions?
4. Which component owns site counts?
5. Does the design add a new recurring stage, queue, retry loop, or checkpoint owner?
6. If yes, what exact canonical contract change is required before implementation?
7. Does any responsibility improperly move into interactive ChatGPT or Scheduled ChatGPT?

GitHub must remain control-plane owner.

## Scope exclusions

Do NOT:
- implement;
- edit source/contracts/workflows/UI;
- run production;
- trigger Scheduled Tasks;
- process games manually;
- rebuild current payload;
- change taste thresholds;
- change hard business eligibility rules;
- weaken source identity/price correctness;
- create another prompt-only observability mechanism as the main solution.

Only the durable architecture amendment report may be written.

## Acceptance checks

AMEND-01 — user product correction is represented exactly: fit first, errors second, never-analysed last, not-fit excluded.

AMEND-02 — all deterministic-eligible games are visible before analysis unless hard-excluded.

AMEND-03 — exact minimal per-item state machine defined.

AMEND-04 — PASS 1 coverage-first semantics defined.

AMEND-05 — PASS 2 recovery-only semantics defined.

AMEND-06 — one item failure cannot block unrelated items.

AMEND-07 — tiered sorting contract defined without comparing incompatible score scales.

AMEND-08 — site aggregate counts and arithmetic invariants defined.

AMEND-09 — item labels/status visibility defined.

AMEND-10 — exact relation to current Taste/Dossier pipeline decided.

AMEND-11 — current group/checkpoint semantics explicitly retained, demoted or retired.

AMEND-12 — GitHub ownership of state/order/retry/counts preserved.

AMEND-13 — implementation staged A-D with user-visible recovery prioritized.

AMEND-14 — no implementation/production mutation.

AMEND-15 — exactly one target architecture and exactly one next recommended step.

## Durable report

Write only:
`reviews/worker_reports/progressive-personalized-deals-architecture-amendment-01.md`

Required sections:
1. Task / repo / mode.
2. Accepted user correction.
3. Architecture ownership preflight.
4. Per-item state machine.
5. PASS 1.
6. PASS 2.
7. Sorting contract.
8. Site per-item labels.
9. Site aggregate counters + invariants.
10. Publication semantics.
11. Existing group/checkpoint treatment.
12. Taste/Dossier relationship comparison A-C.
13. Exactly one chosen semantic path.
14. Failure scenarios.
15. Target architecture.
16. Phase A.
17. Phase B.
18. Phase C.
19. Phase D.
20. Required later canonical changes.
21. AMEND-01..15.
22. Changes: report only.
23. Unresolved.
24. Status.
25. Exactly one recommended next step.
26. Exact refs.
27. Efficiency / reusable lesson.

Allowed statuses:
- `complete_architecture_amendment`
- `needs_user_decision`
- `needs_more_recon`
- `blocked_external`

## Exactly one next step

If complete:
- return to Director for acceptance;
- after Director acceptance, request/consume explicit user approval for the first bounded IMPLEMENT phase only.

Do not implement inside this task.

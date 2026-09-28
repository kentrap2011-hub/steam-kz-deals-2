# WORKER TASK — DEEP-FIRST FINAL-SCORE ORDER FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `deep-first-final-score-order-fix-01`
Mode: `CONTRACT-FIRST IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/deep-first-final-score-order-fix-01.md`

## Explicit user decision

The user has explicitly corrected the intended ranking semantics.

Required automatic stage precedence:

1. current authoritative completed Deep / PASS 2 fit;
2. otherwise current completed Fast / PASS 1 fit;
3. unresolved / incomplete;
4. not analyzed.

Within the same completed-analysis stage, sort by the final transparent game score:
`total_score DESC`.

A Fast game MUST NOT appear above a completed Deep-fit game merely because the Fast game has a higher `total_score`.

A Deep-fit game with a lower `total_score` MUST still remain above every Fast-only fit game.

`analyzed_not_fit` visibility/exclusion semantics remain unchanged.

## User-observed motivating case

Accepted diagnostic:
`reviews/worker_reports/kof-xv-high-priority-without-deep-diagnostic-01.md`

Matching published snapshot had:

1. Severed Steel — Deep — 71.8
2. THE KING OF FIGHTERS XV — Fast — 68.0
3. MY HERO ONE'S JUSTICE 2 — Deep — 67.1

Under the corrected rule this is wrong because a Fast-only game appears above a completed Deep-fit game.

KOF XV is not itself a scoring bug:
- Fast result is valid;
- score 68.0 is valid;
- the defect is cross-stage ordering.

## Current known contract conflict

Current canonical files include:
- `config/progressive_personalization_contract.json` grouping Fast-fit and Deep-fit into the same `analyzed_fit` tier;
- `config/final_ranking_policy.json` with `tier_1_uses_existing_personalized_order=true`;
- existing RANK decisions where sale urgency may precede score.

The user's correction supersedes any rule that allows Fast to cross above Deep or urgency to cross the Deep/Fast boundary.

Do not patch only the KOF card.

## Goal

Create one canonical, producer-owned ordering model with stage precedence before final score:

### Main/default order

For visible eligible cards:

1. `deep_fit`
2. `fast_fit`
3. `analysis_incomplete`
4. `not_analyzed`

Inside `deep_fit`:
- `total_score DESC`
- deterministic title/id tiebreak only after equal score unless another already-canonical non-semantic tie-break is required.

Inside `fast_fit`:
- `total_score DESC`
- same deterministic tiebreak.

For unresolved/not-analyzed states that are not allowed a personalized `total_score`, preserve the existing deterministic purchase-only ordering unless the current canonical contract provides a stricter compatible rule.

### Urgency

The Deep/Fast stage boundary is absolute.

Sale expiry urgency MUST NOT:
- move a Fast-only card above a completed Deep-fit card;
- move unresolved/not-analyzed above completed Fast/Deep.

If an explicit user-selected `Срочные` view is retained:
- it may reorder only *inside the same analysis stage*;
- within that selected view the exact order may be `stage -> urgency -> total_score -> title`.

The default feed must remain:
`stage -> total_score -> deterministic tiebreak`.

Do not preserve an independent producer `priority_rank` whose semantics contradict the visible default order. There must be one clearly named canonical automatic ranking meaning, with any explicit urgency view represented as a separate view mode rather than a second ambiguous "priority".

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. accepted KOF XV diagnostic;
4. current ranking routes in `PROJECT_ROUTES.md`;
5. `PROJECT_RULES.md`;
6. RANK-001 through current latest RANK decision;
7. PPD-004 and current Progressive stage/effective-source rules;
8. `config/final_ranking_policy.json`;
9. `config/progressive_personalization_contract.json`;
10. `config/execution_ownership_contract.json`;
11. only the smallest producer/UI/ranking validation files necessary.

## Mandatory architecture preflight

Before writes, prove:

- GitHub remains sole owner of production scoring/ranking/order fields;
- browser remains presentation/local-view only and does not invent semantic analysis order;
- Fast/Dossier/Deep semantic ownership is unchanged;
- ranking change does not trigger semantic re-analysis;
- no queue/scheduler/retry/backlog ownership is moved to ChatGPT;
- no Scheduled Task setting changes;
- manual `В конец очереди` remains the absolute explicit user override;
- this task changes ordering semantics only, not taste weights, risk weights, purchase weights, Deep/Fast result contents or Dossier state.

If current RANK rules conflict, add the smallest new canonical ranking decision (for example RANK-014) before runtime changes and explicitly supersede only the conflicting ordering clauses.

## Required canonical stage key

Do not infer Deep-vs-Fast in the browser from decorative UI.

Producer must expose/use a deterministic canonical ranking-stage key derived from current producer-owned semantic authority, for example conceptually:

- `deep_fit`
- `fast_fit`
- `analysis_incomplete`
- `not_analyzed`

Exact field/schema naming is worker-owned, but semantics must be explicit and testable.

Historical/stale Deep must not qualify as current Deep.
PPD-012 semantic-equivalent current Deep does qualify.
Deep incomplete/error does not erase a valid Fast fit result; such a card remains in the Fast-fit stage if Fast is the effective current result.

## Score semantics

Do NOT change how `total_score` is calculated.

Preserve existing:
- personal score;
- purchase score;
- risk penalties;
- wishlist contribution;
- achievements;
- price/history/savings;
- package-route logic;
- eligibility/budget gates.

This task changes ordering precedence only.

A Fast 90/100 remains 90/100. It simply cannot outrank a Deep 50/100 because Deep authority comes first.

## Required regressions

At minimum prove:

1. Deep 60 ranks above Fast 99.
2. Deep 70 ranks above Deep 60.
3. Fast 90 ranks above Fast 80.
4. Fast fit ranks above analysis_incomplete even if unresolved purchase-only score is higher.
5. analysis_incomplete ranks above not_analyzed according to current stage precedence.
6. Deep not-fit remains excluded according to existing visibility rules.
7. stale/non-current Deep does NOT grant Deep stage precedence.
8. PPD-012 semantically reconciled current Deep DOES grant Deep precedence.
9. Deep incomplete + valid Fast fit remains Fast stage.
10. missing Deep with valid Fast fit is Fast stage.
11. urgency cannot move Fast above Deep.
12. urgency cannot move unresolved above Fast/Deep.
13. explicit urgency mode, if retained, reorders only inside a stage.
14. manual `В конец очереди` remains absolute after automatic ordering.
15. score calculation values are byte-for-byte/field-for-field unchanged for bounded fixtures except ordering/rank metadata.
16. KOF XV / MY HERO regression proves MY HERO Deep is above KOF Fast despite 67.1 < 68.0, assuming the same pinned semantic states.
17. two Deep cards are ordered by `total_score DESC`.
18. two Fast cards are ordered by `total_score DESC`.

## UI semantics

Fix misleading naming discovered by the KOF diagnostic.

The user-visible main queue header must describe what it actually displays.

Preferred semantics:
- `Позиция в ленте: N из M`

Do not label local cursor position as `Приоритет` if it is not a canonical rank field.

If an explicit urgency view remains, label it as a view/mode, not as a second hidden global rating.

Do not add "world rating" or imply external/global review score. This ranking is the user's internal recommendation order.

## Current production reconciliation

Before merge:
- reread fresh `main`;
- preserve current Dossier progress and current Fast/Deep results;
- preserve active ЧАТ 2 diagnostic work;
- do not overwrite production state from stale branch snapshots.

After merge use only normal GitHub-owned deterministic rebuild/publication.

Required proof from fresh output:
- every visible current Deep-fit card precedes every visible Fast-fit card;
- within current Deep-fit cards, order follows `total_score DESC`;
- within current Fast-fit cards, order follows `total_score DESC`;
- KOF XV cannot appear above a completed Deep-fit card solely because 68 > that Deep card's lower score;
- report exact current first several cards and their stage/score after publication.

If current catalogue membership changes concurrently, test the invariant rather than requiring exact historical positions.

## Interaction with active ЧАТ 2

ЧАТ 2 is running:
`WORKER_TASK_ATELIER_ESCHA_LOGY_DEEP_WITHOUT_POSITIVE_REASON_DIAGNOSTIC_01.md`

Do not modify or interfere with its diagnostic scope/report.

If ЧАТ 2 finishes while this task is active, reconcile fresh `main` normally.

## Hard prohibitions

Do not:
- run Deep/Fast/Dossier semantic workers;
- change semantic results;
- change Dossier data;
- change total-score weights;
- change risk policy;
- change purchase eligibility;
- create a second ranking formula;
- retain ambiguous competing "priority" orders without explicit view semantics;
- add scheduler/queue/retry logic;
- change Scheduled Tasks.

## Validation

Required:
- focused stage-order regression;
- existing final ranking validation;
- Progressive personalization/ranking integration;
- PPD-012 current-authority regression;
- package/ranking regression;
- UI queue regression;
- manual-end override regression;
- full deterministic visual build;
- Pages deploy validation if canonical workflow triggers it.

## Report

Write:
`reviews/worker_reports/deep-first-final-score-order-fix-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Canonical ranking decision`
4. `Previous conflicting rules`
5. `Changes`
6. `Stage precedence regression`
7. `Final-score ordering regression`
8. `Urgency behavior`
9. `UI wording`
10. `KOF / MY HERO regression`
11. `Production reconciliation`
12. `Validation`
13. `Published first positions`
14. `Changes not made`
15. `Unresolved`
16. `Status`
17. `Recommended next step` — exactly one bounded next step or `none`
18. exact PR/commit/run/artifact refs
19. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `blocked`
- `needs_user_decision`

Do not start another task after this one.

# WORKER TASK — TASTE DOSSIER 60 SECONDS TEMPORAL SEMANTIC RISK DIAGNOSTIC 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-60-seconds-temporal-semantic-risk-diagnostic-01`
Mode: `READ-ONLY DIAGNOSTIC`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- current canonical dossier worker index/work manifest for snapshot/group binding;
- exact immutable candidate artifact for current `g000002`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- relevant strict/prepublication/semantic-consistency validation paths;
- `reviews/worker_reports/taste-dossier-early-multi-source-diversification-implement-01.md`;
- recent relevant TASTE decisions in `PROJECT_DECISIONS.md`.

Do not read unrelated product areas or unrelated repositories.

## Authoritative live context

Treat the user-provided Scheduled Task result as authoritative:

- active snapshot: `593378be74141105830ebe7f1fb94d8942f7427bc1abb7f05430b6bfccc69a26`;
- active prompt binding: `web-evidence-v2-early-multi-source-diversification-v1`;
- `g000001` candidate was published and has been canonically accepted;
- current canonical state:
  - `completed_required_count: 3`;
  - `remaining_required_count: 731`;
  - `canonical_expected_sequence: 2`;
  - `full_backlog_complete: false`;
- `g000002` immutable candidate was published at commit prefix `8f42fa1b…`;
- after publication, a semantic risk was identified in the dossier for `60 Seconds! Reatomized`;
- the risky observation is marked `historical`, but the candidate lacks the mandatory recent current-state source that appears required for the claim shape;
- because candidate publication is create-only/immutable, the worker correctly did not overwrite `g000002`, create an alternate candidate, or continue to `g000003`;
- `g000002` is buffered only and is not canonical acceptance.

## Purpose

Determine the **first actual defect** behind the 60 Seconds! Reatomized temporal/evidence inconsistency.

Choose exactly one primary classification:

1. `observation_temporal_classification_error`
   - the worker framed/classified the observation incorrectly;
   - the underlying evidence may be valid for a durable/historical trait, but the observation wording/temporal tag causes it to require current-state support or otherwise violates active rules.

2. `recent_source_retrieval_miss`
   - the observation legitimately makes a current-state claim;
   - a suitable recent source was reasonably reachable within the active retrieval strategy/budget;
   - the worker failed to retrieve/bind it.

3. `validator_gap`
   - the published candidate violates an active temporal/current-state evidence rule;
   - the defect should have been rejected before candidate publication by existing prepublication/strict validation;
   - current validator coverage is incomplete or late.

4. `contract_or_prompt_contradiction`
   - active prompt/schema/evidence contract/validator disagree about whether this observation requires recent support or how `historical` should behave.

5. `mixed_blocker`
   - more than one defect exists; identify which one occurs first in the pipeline and should be fixed first.

Do not assume the user's semantic-risk description proves a validator defect. Inspect the exact candidate and active rules first.

## Scope

Diagnose ONLY:
- current snapshot `593378be…69a26`;
- current immutable `g000002`;
- `60 Seconds! Reatomized`;
- the exact risky observation(s), bound source(s), dates, temporal labels and validation path involved.

Do NOT diagnose the other games in g000002 unless necessary to understand group validation mechanics.

Do NOT implement any fix.
Do NOT mutate or republish the candidate.
Do NOT run Scheduled Task.

## Required candidate inspection

From the immutable g000002 candidate, establish precisely:

1. exact appid/title descriptor for 60 Seconds! Reatomized;
2. exact observation text/meaning at issue;
3. observation temporal classification/tag;
4. bound player-feedback/source IDs;
5. source publication dates if available;
6. whether any source is <=365 days old as of 2026-09-19;
7. whether the observation is:
   - durable trait;
   - explicitly historical statement;
   - current-state technical/localization/service/content claim;
   - mixed temporal claim;
8. whether wording itself implies current state even if the field says `historical`.

Do not reproduce long raw review text or personal identity.

## Active-rule reconstruction

Read the current canonical prompt/contract/schema/validator and answer:

- What exactly requires a recent source?
- Does `historical` permit only old support, or is it simply a label that cannot override current-state wording?
- Are current technical/localization/service claims required to have recent evidence?
- Are durable gameplay/story/art/music traits allowed to rely on old evidence?
- Is there an explicit mixed/historical-current rule?
- At what layer should a mismatch be rejected:
  - worker prompt;
  - prepublication validator;
  - strict canonical validator;
  - semantic consistency test only?

Cite exact repo paths/sections in the durable report.

## Retrieval check

Only if the observation legitimately requires recent current-state support:

Perform a bounded check for whether suitable recent evidence was reasonably retrievable.

Diagnostic ceiling:
- <=8 web/search queries;
- <=16 opened/read pages.

Use the active production-style strategy.
Do not search merely to patch the candidate; this is diagnosis only.

Classify:
- `recent_source_reachable`;
- `recent_source_not_found_within_bound`;
- `not_applicable_durable_or_historical_trait`.

If recent evidence is found, record source class/date/what current-state fact it can support, without changing the candidate.

## Validator-path check

Determine whether the immutable g000002 candidate:

- passed a repo-local prepublication validator before publish;
- would pass/fail the current strict validator if evaluated now;
- was published before the semantic-risk check could run;
- contains a shape not covered by machine validation and only detectable semantically.

Important distinction:

A semantic-risk that requires human/LLM interpretation is not automatically a validator gap if the active machine contract never claimed to infer claim temporality from prose.

Conversely, if the candidate contains explicit structured fields that mechanically prove a missing required recent source and current validator still accepts it, that is a real validator gap.

## Required plain-language answers

The report must answer clearly:

1. Что именно не так в dossier 60 Seconds! Reatomized?
2. Утверждение действительно говорит о текущем состоянии игры или это долговечная/историческая характеристика?
3. Почему tag `historical` не решает проблему (если не решает)?
4. Нужен ли на самом деле recent source?
5. Если нужен — можно ли было его получить в рамках текущего retrieval budget?
6. Должен ли validator был остановить candidate до публикации?
7. Это ошибка worker synthesis, retrieval, validator или противоречие правил?
8. Какой один минимальный следующий фикс нужен?

## No implementation / immutability

READ-ONLY.

Allowed repository write:
- durable report only.

Do NOT:
- change candidate;
- delete candidate;
- create replacement/alternate g000002;
- advance g000003;
- edit prompt/schema/contract/validator/tests;
- create PR;
- merge;
- activate;
- change snapshot/progress;
- run Scheduled Task.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-60-seconds-temporal-semantic-risk-diagnostic-01.md`

Required sections:
1. Task / repo / mode.
2. Current snapshot / canonical state / exact g000002 artifact.
3. Exact 60 Seconds! Reatomized descriptor.
4. Exact risky observation and structured temporal fields.
5. Bound evidence/source dates.
6. Active temporal/recency rules.
7. Durable-vs-current-state semantic analysis.
8. Whether recent support is actually required.
9. Bounded recent-source retrieval result, if applicable.
10. Prepublication/strict validator path.
11. Whether this is mechanically detectable or semantic-only.
12. Primary defect classification.
13. Whether current contract/prompt/validator are internally consistent.
14. Impact on immutable g000002.
15. Minimal next-step design direction.
16. Unresolved.
17. Status.
18. Exactly one recommended next step.
19. Efficiency / reusable lesson.

Allowed statuses:
- `complete_observation_temporal_classification_error`
- `complete_recent_source_retrieval_miss`
- `complete_validator_gap`
- `complete_contract_or_prompt_contradiction`
- `complete_mixed_blocker`
- `blocked`

## Exactly one next step

If observation_temporal_classification_error:
- recommend one narrow synthesis/prompt/semantic-validation fix that prevents current-state wording from being mislabeled as historical/durable.

If recent_source_retrieval_miss:
- recommend one bounded retrieval fix for recent evidence.

If validator_gap:
- recommend one bounded validator/prepublication fix that rejects the structurally detectable bad shape before candidate publication.

If contract_or_prompt_contradiction:
- recommend one narrow rule-alignment task.

If mixed_blocker:
- fix only the first defect in pipeline order.

Do not implement in this task.

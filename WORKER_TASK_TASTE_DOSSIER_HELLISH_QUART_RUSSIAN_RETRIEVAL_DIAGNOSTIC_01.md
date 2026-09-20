# WORKER TASK — TASTE DOSSIER HELLISH QUART RUSSIAN RETRIEVAL DIAGNOSTIC 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-hellish-quart-russian-retrieval-diagnostic-01`
Mode: `READ-ONLY / RECON`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный Taste Steam review dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `reviews/worker_reports/taste-dossier-steam-russian-review-retrieval-improvement-01.md`;
- `reviews/worker_reports/taste-dossier-validator-generator-parity-fix-01.md`;
- current worker index/group descriptor only as needed to confirm the active snapshot/group binding.

Do not begin with broad history/search. Use the accepted prior retrieval implementation report as the baseline.

## Accepted live production facts

Treat these as accepted unless current canonical state has already advanced:

- production Scheduled Task `Taste Steam Review Dossier` was run once after the accepted validator-generator parity fix;
- active snapshot:
  `3bd2085e4a4a157aa0edadfeabbdcc36786228787016f373189d71d12da8d99b`;
- `canonical_expected_sequence = 1`;
- current `g000001` contains:
  - Crown Trick — appid `1000010`;
  - Hellish Quart — appid `1000360`;
  - Tetris® Effect: Connected — appid `1003590`;
- current validator-generator parity binding matched across canonical contract/index/descriptor;
- invocation stopped fail-closed before publishing `g000001`;
- no `g000001` candidate was created;
- worker did not advance to `g000002`;
- Hellish Quart exact-product Russian review existence was established from Steam aggregate UI/state, showing 566 Russian reviews at the time of the run;
- worker could not retrieve a concrete Russian review card/item that could legally become a `player_feedback_record`;
- aggregate Russian review count is existence/discovery metadata only and correctly was not treated as a mention or feedback record.

This is currently classified as an evidence/retrieval stop, not canonical completion and not a validator/parity defect.

## Prior accepted retrieval behavior to compare against

The prior generic Steam Russian retrieval improvement for Cthulhu Saves the World implemented:

- neutral stable review/recommendation locator first;
- if direct language-filter family is aggregate-only/inaccessible, use bounded search-indexed exact-app Store/Community recovery;
- a profile-scoped Russian hit may be discovery-only, never persisted/rebound;
- if no safe stable item locator exists, transient-author fallback is legal only when a concrete Russian/mixed card is actually visible on a returned non-profile exact-app collection parent;
- localized URL parameters are retrieval/routing hints only, not language evidence;
- exact appid remains fail-closed;
- materially equivalent inaccessible endpoint variants should not be repeated;
- source-agnostic diversification remains available;
- existing 8 search / 16 opened-page ceilings remain unchanged.

The Cthulhu proof succeeded through a concrete Russian card visible on a non-profile exact-product Steam Store representation.

## Goal

Determine, with current ordinary web/search/open capabilities, **why the already-implemented generic Cthulhu recovery route did not yield a legal concrete Russian feedback item for Hellish Quart**.

Find the first confirmed divergence between:

`expected recovery path from current prompt`

and

`what is actually reachable/retrievable for Hellish Quart`.

Do not implement a fix in this task.

## Required diagnostic questions

Answer all of these with evidence:

### HQ-01 — Was the current prompt route actually applicable?
Confirm that the active prompt binding still contains the generic search-indexed exact-app Steam recovery route and that Hellish Quart met its trigger condition:
- exact product;
- Russian existence established;
- direct/ordinary retrieval did not yield a legal Russian item.

### HQ-02 — Can exact-app non-profile Steam representations be reached?
Using ordinary current web/search/open tooling, test bounded exact-product Hellish Quart retrieval:
- exact title;
- exact appid `1000360`;
- Russian player-review terms;
- Steam Store/Community representations where materially distinct.

Record only route class and outcome; do not persist usernames/profile identity/raw review bodies.

### HQ-03 — Does any returned non-profile exact-app parent expose a concrete Russian review card?
Classify each material route as:
- aggregate-only;
- concrete non-Russian cards only;
- concrete Russian/mixed card visible;
- profile-scoped only;
- inaccessible/dynamic/no usable card;
- exact-product mismatch.

### HQ-04 — Stable locator availability
If a Russian card is visible, determine whether it exposes:
- neutral stable item/recommendation/public locator;
- or only transient-author identity sufficient for the already-legal fallback;
- or neither.

Do not persist author/profile identity in the report.

### HQ-05 — Compare directly with the Cthulhu proof shape
Identify the earliest concrete point where Hellish Quart differs from the successful Cthulhu path:
- search result shape;
- Store representation;
- Community representation;
- language-filter representation;
- card rendering;
- item locator visibility;
- non-profile parent containment;
- or another observed transport/retrieval difference.

Do not attribute cause to Steam/web tooling unless directly observed.

### HQ-06 — Did the production worker likely stop too early?
Using only the current canonical prompt plus the observed Hellish Quart retrieval path, classify:

- `prompt_route_not_executed` — current instructions required a route that the live worker appears not to have attempted;
- `prompt_route_executed_but_transport_returned_aggregate_only`;
- `prompt_route_executed_but_no_legal_item_identity`;
- `prompt_route_executed_but_exact_product_binding_failed`;
- `external_transport_limitation_other`;
- `insufficient_evidence_to_classify`.

Do not infer tool calls from absence alone. If the live Scheduled Task trace is not durable/visible enough to prove execution, say so and distinguish:
- production execution unknown;
- diagnostic reproduction result known.

### HQ-07 — Is this a generic repeatable retrieval gap?
Determine whether the confirmed issue is:
- Hellish-Quart-specific current representation;
- generic class affecting exact-app Steam pages with aggregate Russian counts but no rendered card;
- generic class where current prompt fails to force search-indexed recovery;
- or not enough evidence to generalize.

No speculation.

## Bounded live diagnostic

A bounded live proof is required because this is a retrieval diagnosis.

Target:
- Hellish Quart;
- appid `1000360`.

Use only ordinary web/search/open behavior available to the Scheduled worker.

Hard ceiling for this diagnostic:
- no more than the existing production ceiling of 8 search queries;
- no more than 16 opened/read source pages/representations.

Stop earlier when the first divergence is proven.

Do not publish any production dossier candidate.

## Privacy / evidence boundaries

Preserve all current rules:

- do not reproduce raw review bodies;
- do not reproduce usernames/display names;
- do not reproduce SteamID/account/profile identifiers;
- do not persist profile URLs;
- profile-scoped hits remain discovery-only;
- aggregate review/language counts are not feedback records;
- locale URL params are not language evidence;
- exact appid is mandatory;
- no base/DLC/sequel/edition substitution;
- no invented review-card locator.

The report may say that a concrete Russian card was visibly inspected without reproducing its identity/content.

## Diagnostic classification

End with exactly one primary classification:

- `worker_execution_gap`
- `retrieval_strategy_gap`
- `current_web_transport_limitation`
- `exact_product_representation_limitation`
- `no_repro_currently_retrieval_succeeds`
- `insufficient_evidence`

If `no_repro_currently_retrieval_succeeds`:
- prove a legal current route exists;
- do not assume the prior production worker executed it;
- distinguish current reproducibility from production trace evidence.

## What is NOT allowed

Do NOT:
- edit prompt/schema/evidence contract;
- edit validator;
- add source types;
- weaken Russian gate;
- weaken privacy/provenance rules;
- create a special-case Hellish Quart rule;
- add browser automation/proxy/external service;
- add retry/queue/scheduler machinery;
- run the production Scheduled Task;
- create/quarantine/edit inbox candidates;
- manually alter canonical progress.

This task is diagnosis only.

## Required report

Write only the compact durable report:
`reviews/worker_reports/taste-dossier-hellish-quart-russian-retrieval-diagnostic-01.md`

Required sections:

1. Task / repo / mode.
2. Accepted production facts.
3. Active prompt/retrieval route confirmation.
4. Bounded diagnostic ledger.
5. Exact-app Steam route outcomes.
6. Concrete Russian-card result.
7. Stable locator vs transient fallback result.
8. Cthulhu-vs-Hellish first divergence.
9. Production execution known vs unknown.
10. Primary classification.
11. Genericity / scope of the problem.
12. Changes: `none` except report.
13. Validation of diagnosis.
14. Unresolved.
15. Status.
16. Exactly one recommended next step.
17. Efficiency / reusable lesson.

Allowed statuses:
- `complete_diagnosis_fix_candidate_ready`
- `complete_no_repro_current_route_available`
- `needs_bounded_followup`
- `blocked_external`

## Exactly one next step

If `complete_diagnosis_fix_candidate_ready`:
- recommend one bounded IMPLEMENT only for the confirmed retrieval gap; do not implement it.

If `complete_no_repro_current_route_available`:
- recommend one clean production acceptance retry only if the report proves current prompt already requires the successful route and there is no contract/runtime change needed.

If `needs_bounded_followup`:
- identify exactly one missing evidence item.

If `blocked_external`:
- identify the exact inaccessible retrieval capability.

Do not start the next task automatically.

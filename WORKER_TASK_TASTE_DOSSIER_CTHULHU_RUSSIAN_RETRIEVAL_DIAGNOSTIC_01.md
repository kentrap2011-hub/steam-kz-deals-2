# WORKER TASK — TASTE DOSSIER CTHULHU RUSSIAN RETRIEVAL DIAGNOSTIC 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-cthulhu-russian-retrieval-diagnostic-01`
Mode: `READ-ONLY DIAGNOSTIC`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- current canonical dossier work manifest / worker index sufficient to resolve current snapshot, expected group and exact Cthulhu appid;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `reviews/worker_reports/taste-dossier-contract-contradictions-fix-01.md`;
- `reviews/worker_reports/taste-dossier-steam-store-review-card-parent-fix-01.md`;
- `reviews/worker_reports/taste-dossier-transient-author-dedupe-fallback-implement-01.md`.

Do not read unrelated product areas.

## Authoritative live context

User-provided Scheduled Task result is authoritative:

Current snapshot:
`d253b195…f2bbb`

Published buffered candidate groups:
- g000001
- g000002
- g000003
- g000004
- g000005
- g000006

Those publications are buffered transport progress, not automatically canonical acceptance.

The last liveness check showed the same snapshot/plan/binding and canonical acceptance had reached the first 15 dossiers, with g000006 next expected at that moment.

The Scheduled worker then continued to:

`g000007`
- Cthulhu Saves the World
- Banners of Ruin
- Dry Drowning

Cthulhu Saves the World has a clear exact-product Russian existence signal: Steam shows approximately 284 Russian-language user reviews.

After diversified bounded retrieval across Steam Community, Russian-language web search and other player-feedback surfaces, the worker did not obtain a contract-usable Russian/mixed item-level record.

Result:
`existence_established_retrieval_unresolved`

Therefore:
- g000007 was not published;
- g000008 was not attempted.

Treat that live result as authoritative. Do not rerun production.

## Diagnostic question

Determine which of these is true for Cthulhu Saves the World:

### A — retrieval limitation
Concrete Russian player-feedback items exist publicly, but the current web/retrieval tooling cannot expose/inspect enough item-level structure to serialize a valid stable or transient-author fallback record.

### B — contract contradiction / overrestriction
Concrete Russian player-feedback items are visibly inspectable and sufficiently attributable under the current retrieval environment, but one or more active schema/contract/prompt/validator/provenance rules still reject a case that should be legal under the accepted evidence model.

### C — source-access limitation
Russian existence is proven, but item-level content is behind a surface/tool access barrier such that neither retrieval quality nor contract semantics can be fairly diagnosed from the available environment.

Do not assume A, B or C in advance.

## Scope

Audit ONLY Cthulhu Saves the World.

Do not diagnose Banners of Ruin or Dry Drowning in this task.

Do not implement any fix.

Do not broaden the task into a general Russian-source audit.

## Retrieval approach

Use a bounded diagnostic budget wider than normal production only enough to classify the blocker.

Maximum per Cthulhu diagnostic:
- 16 web/search queries;
- 32 opened pages/documents.

This wider diagnostic budget does NOT change production's canonical search/page ceilings.

Search adaptively across materially different public player-feedback surface classes when reasonably discoverable, including:
- exact-product Steam Store review cards;
- Steam Community/recommendation/discussion surfaces;
- public mirrors/indexes that expose concrete player review cards;
- Russian-language forums/community posts;
- other public player-feedback surfaces.

Do not waste the budget repeatedly hitting the same blocked endpoint family.

## Candidate ledger requirement

For every concrete Russian/mixed player-feedback lead that is actually found, record a compact diagnostic row with:

- diagnostic local ID;
- surface/source class;
- exact-product identity status;
- whether concrete player-generated content was actually visible/inspected;
- language;
- whether a stable neutral item locator exists;
- whether transient author identity is visible enough for dedupe;
- whether the parent surface is valid under current accepted rules;
- whether the item is recent/old if date is known;
- contract usability verdict;
- FIRST rejection reason;
- classification:
  - retrieval limitation;
  - source-access limitation;
  - contract-caused rejection;
  - semantically insufficient;
  - usable under current contract.

Do NOT persist:
- usernames;
- display names;
- SteamIDs;
- profile URLs;
- raw review bodies;
- long quotations.

Short semantic paraphrase is enough.

## Explicit checks

### CHECK-01 — Steam Store exact-app review cards
Determine whether concrete Russian review cards are actually visible/inspectable on the exact-product Steam Store page.

If yes:
- test whether they now fit the accepted Steam Store parent + transient-author fallback path;
- if they still fail, identify the exact remaining rule.

If no:
- distinguish “aggregate existence visible” from “concrete cards not retrievable.”

### CHECK-02 — transient-author fallback
If a concrete Russian review is visible without neutral review ID:
- can the author be transiently distinguished?
- is there a valid exact-product parent collection surface?
- would current contract allow a privacy-safe fallback record?

### CHECK-03 — stable locator
If a neutral stable review/recommendation ID or direct safe item URL is available:
- would it validate under current exact-app/parent rules?

### CHECK-04 — non-Steam source
Try at least one materially different public player-feedback surface class if reasonably discoverable and useful.

Do not require non-Steam if none is discoverable within budget.

### CHECK-05 — exact product identity
No base-game/DLC/edition confusion.
Use exact canonical Cthulhu dossier appid from current g000007 descriptor.

### CHECK-06 — language
Concrete item language must come from the item, not locale/store UI.

### CHECK-07 — current vs durable claim
Old reviews may still support durable gameplay/story observations but not current technical/localization claims alone.

## What counts as contract contradiction

Report a contract contradiction only if:

1. concrete player-feedback content is actually visible/inspectable;
2. exact product identity is established;
3. the accepted evidence model conceptually allows this class of item;
4. a specific active rule/component still rejects it inconsistently.

Do not call ordinary inability to retrieve a stable ID a contradiction if transient-author fallback should already solve it and the concrete item itself is not visible enough to use.

## Required conclusions

The report must select exactly one primary blocker classification:

- `retrieval_limitation`
- `source_access_limitation`
- `contract_contradiction`
- `mixed_blocker`

If `mixed_blocker`, quantify which blocker actually prevents publication first.

Also answer plainly:

1. Are concrete Russian Cthulhu player reviews actually visible to the diagnostic worker?
2. If yes, why exactly can/cannot they be serialized today?
3. Does the accepted Steam Store review-card fallback solve this case?
4. Is a new contract change justified?
5. If not, what specific retrieval improvement is needed?
6. If yes, what is the narrowest design change?

## No implementation

READ-ONLY.

Allowed repo write:
- durable report only.

Do NOT:
- edit schema/contract/prompt/validator/scripts/tests;
- create PR;
- trigger activation;
- modify production progress;
- publish dossier candidate;
- run Scheduled Task;
- advance g000007/g000008.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-cthulhu-russian-retrieval-diagnostic-01.md`

Required sections:
1. Task / repo / mode.
2. Current canonical snapshot/group/appid.
3. Diagnostic budget actually used.
4. Russian existence evidence.
5. Candidate ledger.
6. Steam Store review-card result.
7. Stable locator result.
8. Transient-author fallback result.
9. Non-Steam/public alternative result.
10. Exact-product/language/recency checks.
11. Primary blocker classification.
12. Whether current contract is internally consistent for this case.
13. Whether a contract change is justified.
14. Minimal next-step design direction.
15. Unresolved.
16. Status.
17. Exactly one recommended next step.
18. Efficiency / reusable lesson.

Allowed statuses:
- `complete_retrieval_limitation`
- `complete_source_access_limitation`
- `complete_contract_contradiction`
- `complete_mixed_blocker`
- `blocked`

## Exactly one next step

If contract contradiction:
- recommend one bounded implementation task for the exact contradiction.

If retrieval/source-access limitation:
- recommend one bounded retrieval-improvement task, not a contract weakening.

If mixed:
- recommend fixing the first actual blocker only.

Do not implement it in this task.

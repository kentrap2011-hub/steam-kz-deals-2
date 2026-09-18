# WORKER TASK — TASTE DOSSIER MO:ASTRAY NON-STEAM RUSSIAN SOURCE DIAGNOSTIC 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-mo-astray-non-steam-russian-source-diagnostic-01`
Mode: `READ-ONLY DIAGNOSTIC`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- current canonical dossier worker index/work manifest sufficient to resolve current snapshot and exact g000011 descriptor;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `reviews/worker_reports/taste-dossier-mo-astray-retrieval-diagnostic-01.md`;
- `reviews/worker_reports/taste-dossier-steam-community-child-retrieval-implement-01.md`;
- `reviews/worker_reports/taste-dossier-russian-multi-source-retrieval-implement-01.md` if present;
- recent relevant TASTE decisions in `PROJECT_DECISIONS.md`.

Do not read unrelated product areas.

## Authoritative live context

Treat the user-provided Scheduled Task result and accepted Director conclusions as authoritative:

- current snapshot: `ec6ff4015ad01a9dcaaa2be845230cf04790c1444b99d5a1c31dad39047de872`;
- create-only candidate groups g000001–g000010 were published in a prior Scheduled invocation;
- that publication is buffered transport progress only, not canonical acceptance;
- canonical status last reported:
  - `canonical_expected_sequence: 7`
  - `completed_required_count: 18`
  - `remaining_required_count: 684`
  - `full_backlog_complete: false`;
- g000011 contains:
  - Monster Train
  - The Room VR: A Dark Matter
  - MO:Astray;
- exact canonical MO:Astray appid: `1104660`;
- Steam proves 144 Russian-language reviews exist;
- Steam retrieval currently fails to expose a contract-usable Russian/mixed concrete item;
- latest Steam Community child-retrieval implementation task ended `blocked_external_transport`;
- no implementation from that blocked task was merged or activated.

## Purpose

Determine whether MO:Astray's Russian gate can be satisfied through the **already-approved multi-source player-feedback model without relying on Steam as the retrieval source**.

This task exists specifically to avoid overfitting the pipeline to Steam.

Primary question:

> Is there at least one contract-usable Russian/mixed concrete player-feedback item for MO:Astray on a public non-Steam surface reachable by the current web tooling?

If yes, determine whether the existing Scheduled worker strategy should already find it or needs a bounded generic source-diversification refinement.

If no, determine whether the available evidence supports source scarcity/indexing limitations strongly enough to justify returning to the external-transport architecture question.

## Scope

Audit ONLY MO:Astray.

Steam may be used only for:
- exact product identity;
- the already-established Russian existence signal;
- comparison/context.

Do NOT spend the diagnostic budget trying to solve Steam child retrieval again.

Do NOT diagnose Monster Train or The Room VR.

Do NOT implement fixes.

Do NOT publish candidates.

## What counts as a useful non-Steam source

The source must expose actual player/community feedback about exact MO:Astray, not merely professional editorial content.

Potential source classes include, when publicly reachable:
- Russian gaming/community forums;
- DTF or similar user/community posts and comments;
- VK/public community discussions only if public-web reachable and usable without identity persistence;
- StopGame user/community reviews/comments;
- iXBT/community/forum discussions;
- 4PDA/forum discussions if exact game player feedback is public and safe;
- Reddit Russian-language comments/posts if any;
- Metacritic user reviews;
- GOG/community/user reviews if product exists there;
- itch/other storefront user reviews if exact product exists there;
- public game databases with individual user reviews;
- public video/community comments only if current contract accepts that source class as player feedback;
- other public exact-product player-feedback surfaces discovered during search.

Professional reviews, news, wiki/game descriptions, storefront descriptions, guides, localization resources, screenshots and aggregate scores do NOT satisfy the Russian player-feedback gate.

## Required source diversification

Use a materially diverse search.

At minimum, if discoverable within budget, test several different source classes rather than many query variants against one site.

Do not impose a fixed per-site quota.

Prefer:
1. exact product title + Russian feedback/review/discussion wording;
2. exact title plus likely Russian community domains;
3. exact app/product identity checks where ambiguity exists;
4. direct opening of promising concrete results.

## Exact-product requirement

MO:Astray only.

Reject:
- similarly named products;
- soundtrack/DLC where not the exact game;
- unrelated “Astray” titles;
- localization/resources that do not represent player feedback.

Use appid 1104660 and developer/publisher/release metadata when necessary to disambiguate.

## Language requirement

Russian/mixed must be determined from the concrete player-feedback item itself.

Russian UI/site locale/title alone is not enough.

## Recency

Follow the current canonical recency rules.

Old feedback may support durable gameplay/story/art/music traits.

Do not use old feedback as evidence for current technical/localization/service state unless current contract permits it.

## Candidate ledger

For every promising Russian/mixed lead record:

- local diagnostic ID;
- source/platform;
- exact product identity: yes/no;
- actual player-feedback item: yes/no;
- concrete content visible: yes/no;
- language;
- stable safe locator: yes/no;
- safe parent/container: yes/no;
- date / recent-old-undated;
- current contract usability;
- FIRST rejection reason if unusable;
- classification.

Do NOT persist unnecessary personal identity:
- usernames/display names;
- account IDs;
- profile URLs;
- author hashes;
- raw long review bodies.

Short paraphrases are enough.

## Diagnostic budget

Maximum:
- 20 web/search queries;
- 40 opened/read source representations.

This is a one-off diagnostic budget only.
It does NOT change production limits.

Use the larger diagnostic budget to test source diversity, not to brute-force one site.

## Required result classifications

Choose exactly one primary result:

### `non_steam_usable_found`
At least one contract-usable Russian/mixed concrete MO:Astray player-feedback item is reachable outside Steam.

### `strategy_diversification_gap`
Usable non-Steam item(s) exist, but current Scheduled worker retrieval strategy would predictably miss them because source-diversification/query guidance is insufficient.

Use this instead of `non_steam_usable_found` only if an actual generic strategy gap is demonstrated.

### `non_steam_source_scarcity`
Materially diverse public non-Steam search was performed, but no contract-usable Russian/mixed item was found; results suggest genuine scarcity or poor public indexing.

### `external_transport_limitation`
Promising non-Steam concrete Russian player feedback is visibly indicated, but current web transport cannot open/read the concrete item safely.

### `contract_contradiction`
A concrete exact-product Russian/mixed non-Steam player-feedback item is safely inspectable and conceptually allowed, but an active contract rule rejects it inconsistently.

### `mixed_blocker`
More than one blocker exists; identify the first blocker that prevents publication.

## Explicit questions to answer

1. What exact canonical MO:Astray target is being diagnosed?
2. Which materially different non-Steam player-feedback source classes were searched?
3. Was any concrete Russian/mixed MO:Astray player-feedback item actually opened/read outside Steam?
4. If yes, is it contract-usable as-is?
5. If usable, would the current production worker likely find it within the existing 8/16 production budget?
6. If current production would miss it, what exact generic diversification/query gap caused that?
7. If no usable item exists, is the evidence better described as public-source scarcity or web-transport limitation?
8. Does any result justify changing evidence/privacy contract?
9. Is a new external retrieval provider still necessary, or is a simpler multi-source strategy fix sufficient?
10. What is exactly one next step?

## No implementation

READ-ONLY.

Allowed repository write:
- durable report only.

Do NOT:
- edit prompt/schema/contract/validator/tests;
- create PR;
- merge;
- activate;
- modify progress;
- publish g000011;
- run Scheduled Task.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-mo-astray-non-steam-russian-source-diagnostic-01.md`

Required sections:
1. Task / repo / mode.
2. Current snapshot / g000011 / exact target.
3. Diagnostic budget used.
4. Source-diversification plan actually executed.
5. Source-class results.
6. Candidate ledger.
7. Concrete usable non-Steam item(s), if any.
8. Production-strategy reachability assessment under current 8/16 budget.
9. Primary blocker/result classification.
10. Whether current contract is internally consistent.
11. Whether any contract change is justified.
12. Whether external retrieval capability is still needed.
13. Minimal next-step direction.
14. Unresolved.
15. Status.
16. Exactly one recommended next step.
17. Efficiency / reusable lesson.

Allowed statuses:
- `complete_non_steam_usable_found`
- `complete_strategy_diversification_gap`
- `complete_non_steam_source_scarcity`
- `complete_external_transport_limitation`
- `complete_contract_contradiction`
- `complete_mixed_blocker`
- `blocked`

## Next-step rules

If `non_steam_usable_found`:
- recommend one clean production live acceptance only if current worker strategy already covers the source adequately;
- otherwise classify as `strategy_diversification_gap`.

If `strategy_diversification_gap`:
- recommend one bounded generic multi-source retrieval-strategy implementation task.

If `non_steam_source_scarcity`:
- recommend returning to one bounded architecture decision about external retrieval capability.

If `external_transport_limitation`:
- identify the exact missing capability and recommend one bounded architecture decision.

If `contract_contradiction`:
- recommend one narrow contract-fix task.

If `mixed_blocker`:
- recommend fixing only the first actual blocker.

Do not implement the next step in this task.

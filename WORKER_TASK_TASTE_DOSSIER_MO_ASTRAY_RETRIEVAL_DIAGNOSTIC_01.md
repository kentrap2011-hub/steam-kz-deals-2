# WORKER TASK — TASTE DOSSIER MO:ASTRAY RETRIEVAL DIAGNOSTIC 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-mo-astray-retrieval-diagnostic-01`
Mode: `READ-ONLY DIAGNOSTIC`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- current canonical dossier work manifest / worker index sufficient to resolve current snapshot, expected group and exact MO:Astray appid;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `reviews/worker_reports/taste-dossier-steam-russian-review-retrieval-improvement-01.md`;
- `reviews/worker_reports/taste-dossier-cthulhu-russian-retrieval-diagnostic-01.md`;
- `reviews/worker_reports/taste-dossier-contract-contradictions-fix-01.md`.

Do not read unrelated product areas.

## Authoritative live context

User-provided Scheduled Task result is authoritative.

Current snapshot:
`ec6ff401…de872`

Create-only buffered candidate groups published in the invocation:
- g000001
- g000002
- g000003
- g000004
- g000005
- g000006
- g000007
- g000008
- g000009
- g000010

This is buffered transport progress only, not automatic canonical acceptance.

Latest canonical status at the time of the live report:
- `canonical_expected_sequence: 7`
- `completed_required_count: 18`
- `remaining_required_count: 684`
- `full_backlog_complete: false`

So GitHub canonical ingest was still behind buffered publications g000007–g000010.

The Scheduled worker stopped on:

`g000011`
- Monster Train
- The Room VR: A Dark Matter
- MO:Astray

For MO:Astray:
- exact appid Russian Steam existence signal: 144 Russian-language reviews;
- bounded retrieval did not yield a contract-usable Russian/mixed concrete item;
- one concrete Russian review card was found only through a profile-scoped Steam surface;
- current privacy/provenance contract correctly forbids persisting that profile-scoped provenance;
- result remained `existence_established_retrieval_unresolved`;
- g000011 was not published.

Treat this as authoritative live evidence.

## Purpose

Compare the already-working Cthulhu retrieval route with MO:Astray and determine **why the generic retrieval improvement succeeded for Cthulhu but failed for MO:Astray**.

Do not re-open the contract-design question unless concrete evidence proves a new contradiction.

Primary question:

> Is MO:Astray failing because the improved search-indexed exact-app recovery strategy was not applied effectively, because Steam/search indexing exposes this product differently, or because the current transport simply cannot expose safe concrete Russian cards for this app?

## Scope

Audit ONLY MO:Astray, with Cthulhu used as the control/comparison case.

Do not diagnose Monster Train or The Room VR in this task.

Do not implement any fix.

Do not publish candidates.

## Exact comparison axes

Compare Cthulhu appid 107310 against the exact canonical MO:Astray appid from current g000011 on:

1. Exact-app Steam Store result visibility.
2. Exact-app Steam Community result visibility.
3. Search-indexed Store/Community recovery.
4. Russian query forms.
5. Appid-constrained query forms.
6. Whether concrete Russian cards appear in returned indexed representations.
7. Whether returned cards expose:
   - safe non-profile parent;
   - neutral stable item locator;
   - transient author distinguishability.
8. Whether only profile-scoped Russian hits are exposed.
9. Whether locale / country / query parameter variants materially change the returned representation.
10. Whether search engine indexing differs by title punctuation/colon/Unicode/tokenization.

Do not assume title punctuation is the cause; test it only if evidence supports it.

## Diagnostic budget

Maximum:
- 16 search/web queries;
- 32 opened/read source representations.

This diagnostic ceiling does NOT change production limits.

Use the budget to compare materially different route forms, not to repeat equivalent blocked endpoint variants.

## Required route replay

Replay the successful Cthulhu strategy as faithfully as possible against MO:Astray.

Specifically test:
- exact title + exact appid + Russian review terms constrained to Steam Store;
- exact title + exact appid + Russian review terms constrained to Steam Community;
- search-indexed exact-app Store result forms;
- search-indexed exact-app Community result forms;
- at least one materially different public player-feedback surface if useful.

Record whether each route yields:
- aggregate-only;
- concrete non-Russian cards;
- concrete Russian cards;
- profile-only Russian item;
- no usable representation.

## Candidate ledger

For every concrete Russian/mixed lead actually found, record:

- local diagnostic ID;
- surface/source class;
- exact product identity;
- concrete player content visible: yes/no;
- language;
- stable neutral locator: yes/no;
- transient author distinguishable: yes/no;
- safe non-profile exact-product parent: yes/no;
- contract usability;
- FIRST rejection reason;
- blocker classification.

Do NOT persist:
- username/display name;
- SteamID;
- profile URL;
- raw review body.

## Required blocker classification

Choose exactly one primary result:

- `strategy_application_gap`
  - current generic strategy should have found a legal item, but production query ordering/route selection failed to exercise it effectively;

- `indexing_surface_difference`
  - Cthulhu and MO:Astray are exposed differently by public search/Steam indexing; generic strategy needs another legal route pattern;

- `external_transport_limitation`
  - current accessible web/search/open environment cannot expose a safe concrete Russian card for MO:Astray even with the improved strategy;

- `contract_contradiction`
  - a concrete Russian item is safely inspectable under an accepted evidence shape but an active rule still rejects it inconsistently;

- `mixed_blocker`
  - more than one blocker is present; identify which one blocks publication first.

## Explicit questions to answer

1. What exact canonical MO:Astray appid is in current g000011?
2. Does the exact Cthulhu recovery query pattern produce any concrete Russian MO:Astray card?
3. If not, what is different in the returned representation?
4. Is there another generic search-indexed exact-app route that does produce a legal card?
5. If yes, why did production miss it?
6. If no, is the limitation clearly external transport/indexing?
7. Is any new contract change justified?
8. What is the narrowest next step:
   - prompt/query-strategy refinement;
   - retrieval-route implementation;
   - external-transport architecture decision;
   - no change.

## No implementation

READ-ONLY.

Allowed repository write:
- durable report only.

Do NOT:
- edit prompt/schema/contract/validator/scripts/tests;
- create PR;
- trigger activation;
- publish candidate;
- modify progress;
- run Scheduled Task.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-mo-astray-retrieval-diagnostic-01.md`

Required sections:
1. Task / repo / mode.
2. Current snapshot / canonical status / g000011 / exact MO:Astray appid.
3. Diagnostic budget used.
4. Cthulhu control route replay.
5. MO:Astray route-by-route comparison.
6. Candidate ledger.
7. Search-index / Store / Community differences.
8. Stable locator result.
9. Transient-author fallback result.
10. Non-Steam/public alternative result.
11. Primary blocker classification.
12. Whether current contract is internally consistent.
13. Whether a new contract change is justified.
14. Minimal next-step design direction.
15. Unresolved.
16. Status.
17. Exactly one recommended next step.
18. Efficiency / reusable lesson.

Allowed statuses:
- `complete_strategy_application_gap`
- `complete_indexing_surface_difference`
- `complete_external_transport_limitation`
- `complete_contract_contradiction`
- `complete_mixed_blocker`
- `blocked`

## Exactly one next step

If strategy_application_gap:
- recommend one bounded prompt/query-strategy fix.

If indexing_surface_difference:
- recommend one bounded generic retrieval-route improvement.

If external_transport_limitation:
- recommend one bounded architecture decision with the exact missing capability.

If contract_contradiction:
- recommend one bounded contract fix.

If mixed:
- recommend fixing only the first actual blocker.

Do not implement it in this task.

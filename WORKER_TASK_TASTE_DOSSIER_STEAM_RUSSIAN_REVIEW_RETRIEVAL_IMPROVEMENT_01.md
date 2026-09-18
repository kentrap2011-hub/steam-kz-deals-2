# WORKER TASK — TASTE DOSSIER STEAM RUSSIAN REVIEW RETRIEVAL IMPROVEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-steam-russian-review-retrieval-improvement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- current canonical dossier work manifest / worker index sufficient to resolve current snapshot and current expected group;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- relevant strict/prepublication/buffered paths only as needed;
- `reviews/worker_reports/taste-dossier-cthulhu-russian-retrieval-diagnostic-01.md`;
- `reviews/worker_reports/taste-dossier-contract-contradictions-fix-01.md`;
- `reviews/worker_reports/taste-dossier-steam-store-review-card-parent-fix-01.md`;
- `reviews/worker_reports/taste-dossier-transient-author-dedupe-fallback-implement-01.md`;
- relevant recent TASTE decisions in `PROJECT_DECISIONS.md`.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Accepted diagnosis

The read-only diagnostic for `Cthulhu Saves the World` established:

- exact target: appid `107310`;
- exact-product Russian review existence is proven (~282–284 Russian reviews depending on crawl snapshot);
- at least one concrete Russian Steam review is actually readable through current web tooling;
- that readable Russian review was exposed only in profile-scoped context;
- no neutral stable recommendation/item locator was exposed;
- exact-app Steam Store/Community retrieval did not expose that same Russian card at concrete-card level;
- current contract is internally consistent;
- primary blocker is `retrieval_limitation`, not contract contradiction;
- no contract weakening is justified.

Treat that diagnosis as accepted baseline.

## Goal

Improve the **existing Scheduled ChatGPT web-retrieval strategy/path** so that, for exact-app Steam Russian review existence cases like Cthulhu Saves the World, the worker can obtain at least one contract-usable Russian/mixed player-feedback record by one of the already-legal paths:

### Preferred path
A concrete exact-product Russian review with a neutral stable item locator:
- Steam recommendation/review ID;
- safe non-profile direct item URL;
- accepted neutral public_ref.

### Fallback path
A concrete exact-product Russian review visibly inspected on a non-profile exact-product collection parent, with transient author identity available for same-product dedupe and no author identity persisted.

No new evidence semantics are requested.

## Critical ownership constraint

Do NOT pretend repository code can modify the capabilities of the external ChatGPT/web transport.

Before implementation, identify the actual repo-owned lever:

Possible acceptable levers include:
- worker prompt/search strategy;
- deterministic query/URL construction guidance;
- explicit ordered Steam retrieval routes that are already reachable by Scheduled ChatGPT web tooling;
- GitHub-prepared non-semantic hints/metadata if current ownership contract already permits them and they do not perform semantic review analysis;
- an existing repo-owned retrieval helper/path that Scheduled ChatGPT can actually consume without requiring local shell/runtime.

If the only apparent solution requires:
- changing the external web tool itself;
- browser automation unavailable to Scheduled ChatGPT;
- an unsupported Steam API transport;
- repository-local Python/shell execution as a Scheduled worker prerequisite;
- a new server/proxy/service;
- a new recurring fetch stage not authorized by canonical ownership;

then do NOT fake an implementation. Return `blocked` or `needs_user_decision` with the exact architectural reason.

## Architecture preflight questions

Before writing, answer explicitly:

1. Which component owns Russian player-feedback web retrieval today?
2. Which repo-owned artifact actually influences that retrieval at Scheduled runtime?
3. Can the proposed improvement be exercised by the Scheduled worker with its existing tools?
4. Does it preserve GitHub as control plane and avoid moving semantic research into an unauthorized component?
5. Does it avoid creating a new recurring stage/service/queue?

If any answer is unclear, stop implementation and resolve architecture first.

## Retrieval strategy requirements

The improvement must be **adaptive**, not a hardcoded Cthulhu-only special case.

For exact-app Steam products with positive Russian existence signal:

1. Try the exact-app Store/Community review collection with Russian/language-targeted forms that are demonstrably reachable by current web tooling.
2. Prefer routes that expose a neutral recommendation/item ID.
3. If neutral ID is unavailable, seek a concrete card on a non-profile exact-app collection that can use the accepted transient-author fallback.
4. If search discovers a profile-scoped concrete Russian review:
   - do not persist/rebind that profile URL;
   - use it as a signal to search for the same item or equivalent Russian concrete cards on safe exact-app collection/item surfaces;
   - do not weaken privacy.
5. Try materially different public mirrors/indexes only when useful and within the existing production budget.
6. Do not repeatedly hit an endpoint family already proven inaccessible.
7. Preserve current production hard ceilings unless the canonical contract already says otherwise.

Do not introduce a website quota. The strategy must remain adaptive.

## Candidate route investigation

Within this task, test feasible public routes using the same class of web tooling available to the Scheduled worker.

Investigate only as needed, examples:
- exact-app Steam Store review collection/filter forms;
- exact-app Steam Community review collection/filter/pagination forms;
- search-engine indexed Steam review/recommendation surfaces;
- publicly readable Steam review endpoints only if they are actually reachable by current Scheduled-style tooling;
- public mirrors/indexes that retain exact product identity and concrete review-card structure.

Do not rely on a route merely because a normal browser could hypothetically execute JavaScript.

## Required proof-of-retrieval

This task is NOT complete merely because prompt text was improved.

For `Cthulhu Saves the World` appid `107310`, using the improved strategy and the same available web/search/open environment, obtain at least one **concrete Russian/mixed item that is contract-usable under the already active evidence model**, proving either:

### PROOF-A — stable
- exact product;
- Russian/mixed from concrete item content;
- neutral stable locator/public_ref;
- non-profile persisted provenance;
- passes current conceptual strict rules.

or

### PROOF-B — transient-author fallback
- exact product;
- concrete Russian/mixed review card actually inspected on a non-profile exact-product collection parent;
- transient author distinguishable for dedupe;
- no author/profile identity persisted;
- valid current parent surface;
- would serialize under current fallback rules.

Do NOT publish a production candidate or alter canonical progress as part of this proof.

If no such proof can be obtained after bounded implementation testing, status cannot be `complete_ready_for_live_acceptance`.

## No evidence-contract weakening

Do NOT:
- allow profile-scoped persisted URLs;
- turn aggregate counts into mentions;
- re-parent a profile-surfaced item to a collection where it was not actually inspected;
- treat collection URL as stable item identity;
- use author hash as persistent identity;
- weaken exact appid/physical-parent binding;
- weaken language projection;
- weaken recurrence caps;
- change Russian existence semantics.

If evidence contract/schema changes are unnecessary, leave them unchanged.

If only prompt/retrieval instructions change, content-complete binding should change only through the canonical prompt revision mechanism.

## Generalization requirement

Although Cthulhu is the acceptance proof, do not hardcode appid 107310 into production logic.

The improvement must apply generically to exact-app Steam products where:
- Russian existence is proven;
- normal retrieval initially exposes only aggregate population, non-Russian cards, or unsafe profile-scoped Russian items.

## Production budget

Do not raise the existing production web query/page ceilings unless explicitly required by canonical contract and separately justified.

The purpose is to make the worker use its bounded budget better, not to solve retrieval by unlimited searching.

## Required regressions / validation

Implement the smallest relevant validation suite for repo-owned behavior.

### RETRIEVE-RU-01 — stable route preferred
Worker instructions prefer neutral stable recommendation/item identity when reachable.

### RETRIEVE-RU-02 — safe collection fallback
If neutral ID is unavailable but concrete Russian card is inspectable on exact-app non-profile collection, worker uses transient-author fallback.

### RETRIEVE-RU-03 — profile result not persisted
Profile-scoped Russian review hit cannot be serialized or rebound merely by host/title similarity.

### RETRIEVE-RU-04 — aggregate remains non-evidence
Russian count alone remains existence signal only.

### RETRIEVE-RU-05 — exact appid preserved
Retrieval route must remain bound to exact dossier appid.

### RETRIEVE-RU-06 — bounded adaptive search
Prompt/strategy does not introduce unlimited retries or fixed website quotas and avoids repeated inaccessible endpoint families.

### RETRIEVE-RU-07 — current evidence guards remain green
Existing Store-card, transient-author, contradiction, language, Russian gate, semantic consistency and buffered suites remain green.

### RETRIEVE-RU-08 — Cthulhu live proof
The report must include a bounded live proof under the current web environment satisfying PROOF-A or PROOF-B.

If RETRIEVE-RU-08 fails, do not claim success.

## Current group / progress

At task start, read current canonical state.

Do not assume transport publications imply canonical acceptance.

Do not modify:
- candidate inbox;
- canonical progress;
- current expected group;
- buffered artifacts.

No production dossier candidate may be created by this task.

## Activation

If implementation changes canonical worker prompt/retrieval instructions:
- bounded branch/PR;
- focused validation + existing dossier suites + ownership validation;
- merge only green;
- normal GitHub-owned activation/rebuild;
- fresh compatible prompt binding/snapshot if required;
- no manual rebind/progress repair.

If no repo-owned implementation is possible, do not create an empty/artificial PR.

## Scheduled Task

Do NOT run Scheduled Task `Run now`.
Do not change Scheduled Task settings.

The bounded Cthulhu proof must be performed inside this implementation/validation chat using ordinary web retrieval, without publishing production state.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-steam-russian-review-retrieval-improvement-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture preflight and actual retrieval owner.
3. Accepted Cthulhu diagnosis.
4. Repo-owned lever selected.
5. Routes tested and why.
6. Exact implementation.
7. Cthulhu proof-of-retrieval ledger.
8. PROOF-A or PROOF-B result.
9. Confirmation no profile/author identity persists.
10. Confirmation evidence contract was not weakened.
11. Generalization beyond Cthulhu.
12. Production budget behavior.
13. RETRIEVE-RU-01..08 results.
14. Existing guard suite results.
15. PR / CI / merge refs, if implementation occurred.
16. Activation/binding/snapshot state, if activation occurred:
   - snapshot id;
   - prepared/completed/remaining;
   - expected sequence;
   - group count;
   - group size;
   - exact current expected group;
   - scope delta and reason if changed.
17. Scheduled Task Run now/settings confirmation.
18. Unresolved.
19. Status.
20. Exactly one recommended next step.
21. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_live_acceptance`
- `blocked_external_transport`
- `needs_user_decision`
- `needs_fix`

## Status rule

`complete_ready_for_live_acceptance` is allowed ONLY if:
- repo-owned improvement is implemented/activated as required;
- RETRIEVE-RU-01..07 pass;
- RETRIEVE-RU-08 proves at least one contract-usable Russian/mixed Cthulhu item with current web tooling;
- no evidence/privacy/provenance rule was weakened.

Otherwise report the truthful blocked/fix status.

## Exactly one next step

If complete:
- return to Director for one clean production live acceptance.

If blocked_external_transport:
- return to Director with the exact unavailable capability and one bounded architecture option; do not invent a workaround.

If needs_user_decision:
- present the smallest architectural choice requiring user approval.

Do not run production in this task.

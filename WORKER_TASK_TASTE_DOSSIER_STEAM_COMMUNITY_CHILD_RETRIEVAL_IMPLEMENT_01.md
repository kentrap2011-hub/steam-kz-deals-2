# WORKER TASK — TASTE DOSSIER STEAM COMMUNITY CHILD RETRIEVAL IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-steam-community-child-retrieval-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- current canonical dossier worker index/work manifest sufficient to resolve snapshot, expected group and current binding;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- relevant strict/provenance/prepublication/buffered paths only as needed;
- `reviews/worker_reports/taste-dossier-mo-astray-retrieval-diagnostic-01.md`;
- `reviews/worker_reports/taste-dossier-steam-russian-review-retrieval-improvement-01.md`;
- `reviews/worker_reports/taste-dossier-contract-contradictions-fix-01.md`;
- recent relevant TASTE decisions in `PROJECT_DECISIONS.md`.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Accepted diagnosis

The accepted MO:Astray diagnostic established:

- exact target: `MO:Astray`, appid `1104660`;
- exact-product Russian existence signal: 144 Steam reviews;
- one concrete Russian review was discoverable only through profile-scoped Steam context;
- Store exact-app retrieval remained aggregate-only;
- Community exact-app review collection exposed concrete cards, but inspected cards were non-Russian;
- Community exact-app discussions exposed Russian exact-product activity as a safe collection/index row;
- the returned collection/index representation did not expose a usable child thread/post locator/body;
- Cthulhu-style indexed Store recovery is volatile and did not solve MO:Astray;
- primary classification: `indexing_surface_difference`;
- current evidence/privacy contract is internally consistent;
- no contract weakening is justified.

Treat that diagnosis as accepted baseline.

## Goal

Improve the generic Scheduled-worker retrieval strategy so that a safe exact-app Steam Community collection/index result can be followed to a **neutral non-profile child thread/review locator and concrete item representation** when such a child is actually exposed by the available web/search/open/click environment.

Target route:

`exact-app Steam Community collection/index -> concrete Russian row/card -> safe child locator -> child open/read -> existing stable/fallback evidence path`

This must be generic, not MO:Astray-specific.

## Critical ownership / capability constraint

Do NOT pretend repository code can add link extraction/click capabilities to the external web tool.

Before implementation, prove the repo-owned lever:

1. Which component owns public-web retrieval?
2. Which canonical repo artifact influences route selection at Scheduled runtime?
3. Can existing Scheduled web tooling actually follow a returned safe Steam Community child target when one is exposed?
4. Is the desired route achievable by prompt/query/open/click strategy alone?
5. Does the change preserve GitHub as control plane and avoid local-shell/browser-automation dependencies?

If the current web environment cannot expose or follow the child target even with correct route selection, do not fake success. Report `blocked_external_transport` or `needs_user_decision`.

## Generic route requirements

When:
- exact Steam appid is established;
- Russian existence is established;
- Store indexed recovery is aggregate-only or fails;
- exact-app Community exposes a Russian row/card/index lead;

the worker should:

1. Inspect the exact-app Community collection/index representation for actual child targets.
2. Prefer a neutral, non-profile child URL/ref that identifies:
   - a discussion thread;
   - review/recommendation;
   - post/comment item;
   - other contract-accepted concrete player-feedback child.
3. If the parent page exposes numbered/clickable links, follow the child target rather than issuing many new broad searches.
4. Verify the opened child remains bound to exact appid/product and physical parent/container.
5. Determine language from the concrete child content, not row locale/UI.
6. Use the ordinary stable-locator path when the safe child locator is item-level.
7. If the opened child is a safe collection/container with a concrete card but no stable item id, use the already accepted transient-author fallback only if all current prerequisites are satisfied.
8. If the row has no exposed child target, do not invent/guess thread ids or URLs.
9. Do not re-parent profile-scoped evidence to a Community collection where that concrete item was not inspected.
10. After a genuine child-target extraction failure, diversify rather than repeating equivalent index queries.

## Search/open efficiency

This task should improve route traversal, not increase budgets.

Production ceilings stay unchanged:
- max 8 web/search queries per game;
- max 16 opened/read pages per game.

A discovered safe collection row should preferentially consume an open/click step rather than another broad search query when the current tool exposes a child link.

Do not create a fixed Steam-only quota.

## Candidate route forms

Investigate only routes actually reachable by Scheduled-style web tooling, including as appropriate:

- exact-app Steam Community discussions collection;
- exact-app Steam Community reviews collection;
- search-indexed exact-app Community rows;
- numbered links exposed in opened Community pages;
- safe thread/review child URLs returned by search results;
- search-engine follow-up constrained by exact parent row/title when direct child link extraction is unavailable.

Do not rely on hypothetical DOM/JavaScript behavior unavailable to the current environment.

## Required MO:Astray live proof

Task cannot be successful based only on prompt text/regressions.

Using current web tooling after the repo-owned route improvement, prove at least one contract-usable Russian/mixed MO:Astray item via one of:

### PROOF-C — safe stable Community child

- exact appid 1104660;
- Russian/mixed concrete player-feedback child content is opened/read;
- neutral non-profile child locator is exposed;
- locator physically belongs to the exact-app Community parent/container;
- current strict conceptual rules would accept it.

### PROOF-D — safe Community fallback

- exact appid 1104660;
- safe non-profile Community parent/container;
- concrete Russian/mixed player-feedback card/item actually inspected there;
- transient author distinguishable if required;
- no profile/author identity persists;
- existing fallback rules would accept it.

The proof may use an actual discussion/post if it is genuine player feedback relevant to the dossier. A localization resource, screenshot, guide, announcement or mere discussion index row is not enough.

Do not publish a production candidate during proof.

## Cthulhu regression

Because the previous search-indexed Store route was useful but volatile:

- preserve it as an earlier recovery route when it yields a concrete safe card;
- do not replace it with Community-only logic;
- the new Community-child route should be the next generic recovery step when Store recovery is aggregate-only/unusable.

No requirement to reproduce the old Cthulhu card during this task if the current index no longer exposes it; regression should validate route ordering/semantics, not brittle search-result contents.

## No contract weakening

Do NOT change evidence semantics to make the proof pass.

Do not:
- persist profile-scoped URL;
- count aggregate review/language totals as mentions;
- treat index row alone as player feedback;
- guess a thread id;
- re-parent an item by title/host only;
- weaken exact appid/physical parent binding;
- persist author identity/hash;
- weaken language binding or recurrence caps.

Evidence contract/schema/strict validator should remain unchanged unless implementation uncovers a genuine separate contradiction. If that happens, stop and report `needs_user_decision` rather than quietly broadening scope.

## Repo-owned implementation

Prefer the smallest repo-owned change that Scheduled runtime actually consumes.

Likely owner:
- `config/taste_steam_review_dossier_worker_prompt.md`
plus prompt revision metadata/content-complete binding.

If a current canonical route/hint artifact already exists and is genuinely consumed by Scheduled ChatGPT, it may be updated instead/in addition.

Do not add a local Python/browser helper that Scheduled ChatGPT cannot execute.

## Required regressions

### COMMUNITY-CHILD-01 — Store recovery remains earlier route
Concrete safe exact-app Store card remains usable before Community child recovery.

### COMMUNITY-CHILD-02 — exact-app Community row traversal
Prompt/strategy explicitly moves from a safe exact-app collection/index row to exposed child locator/open before issuing repeated equivalent broad searches.

### COMMUNITY-CHILD-03 — neutral child stable path
Safe exact-app Community child URL/ref is handled through stable-locator path when item-level.

### COMMUNITY-CHILD-04 — safe fallback path
Concrete card/item on safe Community parent without neutral item id may use current transient-author fallback.

### COMMUNITY-CHILD-05 — row alone invalid
Index/list row without opened concrete child remains non-evidence.

### COMMUNITY-CHILD-06 — no guessed ids
Strategy explicitly forbids synthesizing/guessing thread/review ids.

### COMMUNITY-CHILD-07 — profile hit remains discovery-only
Profile-scoped Russian item cannot be persisted/re-parented.

### COMMUNITY-CHILD-08 — exact appid/container preserved
Child must remain physically bound to exact dossier appid and parent/container.

### COMMUNITY-CHILD-09 — bounded adaptive route
No new production budget, website quota or repeated equivalent endpoint loop.

### COMMUNITY-CHILD-10 — prior guards green
Store-card, transient-author, contradiction, language, Russian gate, semantic consistency, package/story-DLC, buffered/compatibility suites remain green.

### COMMUNITY-CHILD-11 — MO:Astray live proof
PROOF-C or PROOF-D succeeds in the current web environment.

If COMMUNITY-CHILD-11 fails, status cannot be `complete_ready_for_live_acceptance`.

## Architecture / activation

If implementation is possible:
- bounded branch/PR;
- focused regressions;
- existing dossier/ownership suites;
- merge only green;
- normal GitHub-owned activation;
- fresh compatible prompt binding/snapshot if required;
- no manual rebind/progress repair.

If the current web tool does not expose/follow any usable child target and no repo-owned strategy can change that, do not create an artificial implementation PR.

## Current production state

At task start, read current canonical state.

Do not assume buffered create-only publications are canonical acceptance.

Do not:
- alter candidate inbox;
- alter canonical progress;
- publish g000011;
- advance g000012;
- manually replay prior groups.

## Scheduled Task

Do NOT run Scheduled Task `Run now`.
Do not modify Scheduled Task settings.

Live proof is diagnostic/validation only and must not publish production state.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-steam-community-child-retrieval-implement-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture preflight / actual retrieval owner.
3. Accepted MO:Astray diagnosis.
4. Repo-owned lever and capability proof.
5. Generic Community-child route implemented.
6. Route ordering relative to Store recovery/source diversification.
7. MO:Astray proof ledger.
8. PROOF-C / PROOF-D result.
9. Exact parent/child/appid verification.
10. Privacy/provenance confirmation.
11. Confirmation contract/schema/strict semantics not weakened.
12. Cthulhu route preservation.
13. Production budget behavior.
14. COMMUNITY-CHILD-01..11 results.
15. Existing guard suites.
16. PR / CI / merge refs if implementation occurred.
17. Activation/binding/snapshot if activation occurred:
   - snapshot id;
   - prepared/completed/remaining;
   - expected sequence;
   - group count;
   - group size;
   - exact expected group;
   - scope delta and reason if changed.
18. Scheduled Task confirmation.
19. Unresolved.
20. Status.
21. Exactly one recommended next step.
22. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_live_acceptance`
- `blocked_external_transport`
- `needs_user_decision`
- `needs_fix`

## Status rule

`complete_ready_for_live_acceptance` is allowed ONLY if:
- a real repo-owned Scheduled-runtime route improvement was implemented/activated;
- COMMUNITY-CHILD-01..10 pass;
- COMMUNITY-CHILD-11 proves PROOF-C or PROOF-D on MO:Astray using current web tooling;
- no evidence/privacy/provenance guard was weakened.

Otherwise return the truthful blocked/decision/fix status.

## Exactly one next step

If complete:
- return to Director for one clean production live acceptance.

If blocked_external_transport:
- identify the exact missing child-link/open capability and recommend one bounded architecture decision only.

If needs_user_decision:
- state the smallest architectural choice requiring approval.

Do not run production inside this task.

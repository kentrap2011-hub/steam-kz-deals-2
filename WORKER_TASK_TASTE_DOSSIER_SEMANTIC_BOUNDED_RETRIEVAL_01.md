# WORKER TASK — TASTE DOSSIER SEMANTIC BOUNDED RETRIEVAL 01

Repository: `kentrap2011-hub/steam-kz-deals-2`

Base branch / source of truth: `main`

Repository scope guard: do not search, read, change, or use any other repository. If a tool opens another repository or the repository is ambiguous, stop and return to `kentrap2011-hub/steam-kz-deals-2` before doing task work.

Task ID: `taste-dossier-semantic-bounded-retrieval-01`

Mode: `IMPLEMENT`

## User decision

The user explicitly approved replacing **both** small hard per-game numeric web-retrieval ceilings with semantic/adaptive bounded stopping:

- remove the hard web-search query-count ceiling;
- remove the hard opened/read source-page count ceiling;
- do **not** replace either with another arbitrary numeric ceiling such as 12, 16, 20, 40, etc.

The accepted intent is:

- the Dossier worker should stop because evidence is sufficient, required materially distinct routes are exhausted, a real blocker is exposed, binding/liveness changes, or ordinary invocation runtime ends;
- it should not stop merely because an arbitrary count of searches or opened pages was reached;
- repeated materially equivalent searches/retries remain forbidden;
- source diversification and exact-product/Russian/identity requirements remain mandatory;
- this change is **not** permission for unbounded retry loops, arbitrary site crawling, or endless searching;
- ordinary invocation runtime remains the outer technical safety boundary for one invocation.

## START / authority

First execute the START gate from the current `CHAT_PROTOCOL.md`.

Then read the minimum current canonical surfaces needed for this runtime-contract change, including at least:

- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_runtime_prompt.md`
- `config/taste_steam_review_dossier_scheduled_task_regulation.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/execution_ownership_contract.json`
- the current semantic schema / web-evidence contract referenced by the worker prompt
- focused Dossier regressions/tests that bind retrieval and fail-closed ledger behavior
- `reviews/worker_reports/taste-dossier-steam-russian-review-retrieval-improvement-01.md`
- `reviews/worker_reports/taste-dossier-fail-closed-execution-ledger-implement-01.md`

Use current `main` as authority.

## Observed trigger

A clean Scheduled Dossier invocation produced a valid `FAIL_CLOSED_EXECUTION_LEDGER_V1` for `DEEEER Simulator: Your Average Everyday Deer Game` with:

- `search_queries_used: 11`
- `search_query_limit: 8`
- `opened_pages_used: 2`
- `opened_page_limit: 16`

The invocation performed Steam exact-app, Steam Community, generic cross-source, and Russian user-review diversification before stopping.

Do not assume from the ledger alone whether all 11 searches were correctly counted. The implementation target is the user-approved contract change: numeric search/page counts must no longer be semantic stop gates. Semantic/adaptive boundedness and observability remain required.

## Required architecture preflight

Before editing runtime/worker behavior, establish and record:

1. current owner of Dossier retrieval/stopping semantics;
2. why this change stays inside the existing Scheduled Dossier worker rather than adding a new retry/scheduler/queue/checkpoint owner;
3. which existing guards prevent materially equivalent retry loops after both numeric ceilings are removed;
4. how semantic route exhaustion plus ordinary invocation runtime/binding/liveness bound worst-case execution;
5. whether any machine contract/schema/test currently requires numeric search/page limit fields and, if so, the smallest compatible migration.

Fail closed if removing both numeric ceilings would silently create a second retry/control plane or make stopping semantics ambiguous.

## Required implementation

Implement the smallest canonical change that makes semantic/adaptive stopping primary and removes both hard per-game numeric web-retrieval ceilings.

At minimum:

1. Remove canonical statements that impose `at most 8 web-search queries` or equivalent hard query-count stopping semantics.
2. Remove canonical statements that impose `at most 16 opened/read source pages` or equivalent hard page-count stopping semantics.
3. Do not introduce replacement arbitrary numeric ceilings for search queries, opened pages, sites, endpoint variants, or source classes.
4. Preserve the existing rule to stop early as soon as evidence is sufficient.
5. Preserve/strengthen the rule that materially equivalent routes are not retried once their unusable stop-shape is established.
6. Preserve early source diversification after unusable Steam shapes.
7. Preserve fail-closed when mandatory evidence/identity requirements remain unresolved after all reasonably discoverable required materially distinct routes are exhausted, or a directly observed blocker/runtime/liveness condition prevents safe continuation.
8. Search/page counting may remain only if useful for diagnostics/ledger observability; counts must no longer act as semantic stop gates. Represent absence of a numeric limit unambiguously and consistently with the current schema rather than fabricating a finite limit.
9. Update `FAIL_CLOSED_EXECUTION_LEDGER_V1` so it cannot claim `search budget exhausted` or `page/open budget exhausted` solely from numeric counts after this change.
10. Update `next_required_step`, `next_required_step_status`, `why_not_executed`, and required-route accounting consistently with semantic stopping.
11. Keep exact-product, Russian existence/item-level, source-diversification, temporal, identity/privacy, create-only publication, V2 traversal, and GitHub-control-plane semantics unchanged.
12. Do not duplicate these details into the Scheduled Task bootstrap unless that file has an actual stale numeric-ceiling statement. Its canonical indirection should continue to follow the worker/runtime prompt automatically.

## Semantic boundedness / anti-loop requirement

Removing both numeric ceilings must not create an unlimited-retry or crawler interpretation.

The active prompt/regressions must make clear that:

- materially equivalent query/locale/endpoint variants after an already-proven unusable shape are not a new route;
- a route may be revisited only when a materially new factual lead changes what is being queried, not merely because another wording or another equivalent page is available;
- discovery should choose the most promising materially distinct public player-feedback surface, not enumerate arbitrary websites;
- once all reasonably discoverable mandatory materially distinct routes are exhausted, the worker must stop fail-closed rather than continue searching for arbitrary new sites/pages;
- once evidence is sufficient, the worker must stop even if more sources could theoretically be searched;
- ordinary invocation runtime, changed binding/liveness, tool/transport failure, or another directly exposed runtime blocker may still stop the current invocation safely;
- no semantic requirement may be relaxed merely because numeric ceilings were removed.

Do not introduce a fixed site quota, replacement numeric budget, background crawler, or retry daemon.

## Validation

Add/update focused regressions proving at least:

- SEMBOUND-01: no active canonical Dossier prompt/runtime/test requires an 8-search hard ceiling;
- SEMBOUND-02: no active canonical Dossier prompt/runtime/test requires a 16-opened-page hard ceiling;
- SEMBOUND-03: a hypothetical 9th/11th search is not invalid solely because its ordinal exceeds 8;
- SEMBOUND-04: a hypothetical 17th opened/read page is not invalid solely because its ordinal exceeds 16;
- SEMBOUND-05: evidence-sufficient state still stops early;
- SEMBOUND-06: equivalent-route repetition remains prohibited;
- SEMBOUND-07: mandatory distinct recovery/source-diversification routes must execute while reasonably discoverable and safe;
- SEMBOUND-08: when required materially distinct routes are exhausted with insufficient critical evidence, fail-closed remains valid;
- SEMBOUND-09: ledger cannot emit `search budget exhausted` or `page/open budget exhausted` from numeric counts alone;
- SEMBOUND-10: no scheduler/queue/retry/checkpoint/persistence owner was added;
- SEMBOUND-11: relevant existing Dossier V2, retrieval, privacy/exact-product, ledger and ownership regressions remain green.

Run the smallest relevant existing validation workflow/suite plus the new focused regression. Do not run production Dossier semantics as part of implementation.

## Explicit prohibitions

Do not:

- create, edit, enable, disable, pause, delete, reschedule, rename, recreate, or run any ChatGPT Scheduled Task;
- press or simulate `Run now`;
- run Dossier semantic production;
- publish/recover a Dossier group;
- change Dossier group ordering, snapshot binding, V2 traversal, create-only artifact identity, canonical persistence, progress, recovery ownership, or completeness;
- change Fast/PASS 1 or Deep/PASS 2;
- replace either removed ceiling with another arbitrary numeric ceiling;
- add an unlimited retry loop, fixed website quota, background crawler, queue, checkpoint, or second scheduler.

## Durable report

Write and commit:

`reviews/worker_reports/taste-dossier-semantic-bounded-retrieval-01.md`

Allowed final statuses:

- `complete_ready_for_director_acceptance`
- `needs_user_decision`
- `blocked`

The report must include:

- exact files changed;
- architecture/ownership conclusion;
- before/after stopping semantics;
- treatment of ledger search/page counters and limit representation;
- proof that neither search count nor opened-page count remains a semantic stop gate;
- validation runs/results;
- SEMBOUND-01..11 status;
- confirmation that no external Scheduled Task action or production Dossier run occurred.

Before claiming completion, reread the committed report from fresh `main`.

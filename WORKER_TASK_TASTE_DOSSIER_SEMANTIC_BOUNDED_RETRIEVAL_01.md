# WORKER TASK — TASTE DOSSIER SEMANTIC BOUNDED RETRIEVAL 01

Repository: `kentrap2011-hub/steam-kz-deals-2`

Base branch / source of truth: `main`

Repository scope guard: do not search, read, change, or use any other repository. If a tool opens another repository or the repository is ambiguous, stop and return to `kentrap2011-hub/steam-kz-deals-2` before doing task work.

Task ID: `taste-dossier-semantic-bounded-retrieval-01`

Mode: `IMPLEMENT`

## User decision

The user explicitly approved replacing the small hard **per-game web-search query-count ceiling** with semantic/adaptive bounded stopping.

The accepted intent is:

- the Dossier worker should stop because evidence is sufficient, required materially distinct routes are exhausted, a real blocker is exposed, binding/liveness changes, or ordinary invocation runtime ends;
- it should not stop merely because an arbitrary small number of search queries was reached;
- repeated materially equivalent searches/retries remain forbidden;
- source diversification and exact-product/Russian/identity requirements remain mandatory;
- this change is **not** permission for unbounded retry loops or endless searching.

The current 16 opened/read source-page ceiling is **not authorized for removal by this task** unless an unavoidable contract inconsistency is proven. Preserve it by default.

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

Do not assume from the ledger alone whether all 11 were correctly counted. The implementation target is the user-approved contract change: eliminate the small numeric search-query ceiling as a semantic stop gate, while preserving adaptive semantic boundedness and observability.

## Required architecture preflight

Before editing runtime/worker behavior, establish and record:

1. current owner of Dossier retrieval/stopping semantics;
2. why this change stays inside the existing Scheduled Dossier worker rather than adding a new retry/scheduler/queue/checkpoint owner;
3. which existing guards prevent materially equivalent retry loops after the numeric query ceiling is removed;
4. how ordinary invocation runtime/binding/liveness and the existing page-read ceiling bound worst-case execution;
5. whether any machine contract/schema/test currently requires a numeric search-query limit field.

Fail closed if removing the query ceiling would silently create a second retry/control plane or make stopping semantics ambiguous.

## Required implementation

Implement the smallest canonical change that makes semantic/adaptive stopping primary and removes the hard per-game **web-search query-count ceiling**.

At minimum:

1. Remove canonical statements that impose `at most 8 web-search queries` or equivalent hard query-count stopping semantics.
2. Preserve the existing rule to stop early as soon as evidence is sufficient.
3. Preserve/strengthen the rule that materially equivalent routes are not retried once their unusable stop-shape is established.
4. Preserve early source diversification after unusable Steam shapes.
5. Preserve fail-closed when mandatory evidence/identity requirements remain unresolved after all reasonably discoverable required materially distinct routes are exhausted, or a directly observed blocker/runtime/liveness condition prevents safe continuation.
6. Preserve the current hard opened/read source-page ceiling of 16 unless a proven contradiction requires a separate user decision.
7. Keep search-query counting only if useful for diagnostics/ledger observability; it must no longer act as a semantic stop gate. If retained, represent the absence of a numeric query ceiling unambiguously rather than fabricating a finite limit.
8. Update `FAIL_CLOSED_EXECUTION_LEDGER_V1` requirements so a retrieval stop cannot claim `search budget exhausted` solely from query count after this change.
9. Update `next_required_step`, `next_required_step_status`, `why_not_executed`, and required-route accounting consistently with semantic stopping.
10. Keep exact-product, Russian existence/item-level, source-diversification, temporal, identity/privacy, create-only publication, V2 traversal, and GitHub-control-plane semantics unchanged.
11. Do not duplicate these details into the Scheduled Task bootstrap unless that file has an actual stale numeric-ceiling statement. Its canonical indirection should continue to follow the worker/runtime prompt automatically.

## Anti-loop requirement

Removing the numeric query ceiling must not create an unlimited retry interpretation.

The active prompt/regressions must make clear that:

- materially equivalent query/locale/endpoint variants after an already-proven unusable shape are not a new route;
- a route may be revisited only when a materially new factual lead changes what is being queried, not merely because another wording is available;
- once all reasonably discoverable mandatory materially distinct routes are exhausted, the worker must stop fail-closed rather than continue searching for arbitrary new sites;
- ordinary invocation runtime/binding/liveness may still stop the current invocation safely.

Do not introduce a new fixed site quota or a replacement arbitrary numeric search ceiling.

## Validation

Add/update focused regressions proving at least:

- SEMBOUND-01: no active canonical Dossier prompt/runtime/test requires an 8-search hard ceiling;
- SEMBOUND-02: a hypothetical 9th/11th search is not invalid solely because its ordinal exceeds 8;
- SEMBOUND-03: evidence-sufficient state still stops early;
- SEMBOUND-04: equivalent-route repetition remains prohibited;
- SEMBOUND-05: mandatory distinct recovery/source-diversification routes must execute while reasonably discoverable and safe;
- SEMBOUND-06: when required materially distinct routes are exhausted with insufficient critical evidence, fail-closed remains valid;
- SEMBOUND-07: 16-page opened/read ceiling remains active unless separately authorized;
- SEMBOUND-08: ledger cannot emit `search budget exhausted` from query count alone;
- SEMBOUND-09: no scheduler/queue/retry/checkpoint/persistence owner was added;
- SEMBOUND-10: relevant existing Dossier V2, retrieval, privacy/exact-product, ledger and ownership regressions remain green.

Run the smallest relevant existing validation workflow/suite plus the new focused regression. Do not run production Dossier semantics as part of implementation.

## Explicit prohibitions

Do not:

- create, edit, enable, disable, pause, delete, reschedule, rename, recreate, or run any ChatGPT Scheduled Task;
- press or simulate `Run now`;
- run Dossier semantic production;
- publish/recover a Dossier group;
- change Dossier group ordering, snapshot binding, V2 traversal, create-only artifact identity, canonical persistence, progress, recovery ownership, or completeness;
- change Fast/PASS 1 or Deep/PASS 2;
- replace the removed 8-search ceiling with another arbitrary small numeric query ceiling such as 12/20/40;
- remove the 16-page ceiling without a proven need and explicit scope decision;
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
- treatment of ledger query counters/limit representation;
- confirmation that the 16-page ceiling was preserved or exact reason it could not be;
- validation runs/results;
- SEMBOUND-01..10 status;
- confirmation that no external Scheduled Task action or production Dossier run occurred.

Before claiming completion, reread the committed report from fresh `main`.

# WORKER TASK — TASTE DOSSIER TEMPORAL PRE-STOP RETRIEVAL GATE IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-temporal-prestop-retrieval-gate-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- current canonical dossier worker index/work manifest sufficient to resolve active snapshot/binding;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- relevant strict/prepublication/buffered/semantic-consistency validation paths;
- `reviews/worker_reports/taste-dossier-60-seconds-temporal-semantic-risk-diagnostic-01.md`;
- `reviews/worker_reports/taste-dossier-early-multi-source-diversification-implement-01.md`;
- recent relevant TASTE decisions in `PROJECT_DECISIONS.md`.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Accepted diagnosis

Treat the following as accepted:

- active snapshot at diagnosis time:
  `593378be74141105830ebe7f1fb94d8942f7427bc1abb7f05430b6bfccc69a26`;
- canonical had accepted `g000001`;
- current expected sequence was `2`;
- immutable `g000002` candidate exists and is invalid;
- exact affected game:
  - `60 Seconds! Reatomized`
  - appid `1012880`;
- risky observation was a technical-state claim based on a 2019 Russian feedback item and serialized with `evidence_status:"historical"`;
- active V2 semantics require a historical technical/current-state observation to have:
  - historical evidence; and
  - a <=365-day `current_state` source;
- the candidate lacked the required recent current-state source;
- GitHub strict validation correctly rejected `g000002`;
- this was NOT a validator gap;
- this was NOT a contract/prompt contradiction;
- bounded diagnostic retrieval found suitable recent exact-product technical feedback in the current environment within the active 8/16 ceiling;
- primary defect: `recent_source_retrieval_miss`;
- first pipeline error: worker stopped research prematurely with `research_state:"sufficient"` / `stop_reason:"evidence_stable"` before satisfying the already-existing recent-check obligation.

The old immutable `g000002` must remain untouched.

## Goal

Strengthen the Scheduled-worker retrieval/stopping behavior so that **a current-state-sensitive observation cannot be finalized as `historical` while its bound evidence lacks a recent `current_state` source**.

This is a retrieval/stopping fix only.

Do not change the meaning of `historical`, `current`, `uncertain`, `durable`, recency, source admissibility, or strict validation.

## Required behavior

Before the worker may emit:

- `research_state:"sufficient"`; or
- `stop_reason:"evidence_stable"`;

it must perform a structured temporal completeness check over the observations it intends to serialize.

For every proposed observation:

### Current-state-sensitive topics

This includes at minimum the current canonical contract topics such as:
- bugs;
- performance;
- compatibility;
- technical state;
- localization;
- regional/service state.

### If proposed status is `historical`

The worker must verify that the observation already has BOTH:

1. historical evidence; and
2. at least one bound source with:
   - `evidence_role:"current_state"`; and
   - `freshness:"recent"` under the active <=365-day rule.

If the recent current-state source is missing and retrieval budget remains:
- continue bounded exact-product recent retrieval;
- do NOT declare research sufficient;
- do NOT use `evidence_stable`.

After bounded retrieval:

- if recent evidence supports a historical/fixed/materially-reduced interpretation, `historical` may be used;
- if recent evidence supports a still-current issue, synthesize under the existing current-state semantics;
- if the temporal state remains unresolved, use the already-defined `uncertain` path instead of forcing `historical`.

Do not invent a new evidence status.

### If proposed status is `current`

Preserve the existing rule that current-state observations require recent current-state support.

### Durable traits

Do not over-tighten durable gameplay/story/art/music/structure observations. Old evidence may remain valid under existing durable-trait rules.

## Important semantic boundary

The worker does NOT need to infer temporality from arbitrary prose through machine code.

This task only strengthens the Scheduled semantic worker's own pre-stop checklist and retrieval order before serialization.

The strict validator remains the post-publication authority and should remain unchanged unless a separate contradiction is discovered.

Do not duplicate strict validation logic into a new runtime service.

## Retrieval behavior

If a recent check is required:

1. prefer exact-product recent player-feedback sources;
2. apply the active early multi-source diversification strategy;
3. do not over-focus on Steam;
4. recent current-state support may come from any already-legal player-feedback source class;
5. language of the recent current-state source does not need to be Russian unless another active rule independently requires that;
6. preserve exact product identity;
7. preserve 8 search / 16 page ceilings;
8. do not create fixed site quotas.

## Stop-gate ordering

The worker's intended order should be:

`collect evidence -> draft/plan observations -> temporal completeness check -> targeted recent retrieval if required -> re-evaluate temporal status -> only then decide sufficient/evidence_stable -> serialize candidate`

NOT:

`collect old issue evidence -> mark historical -> evidence_stable -> publish -> let strict validator catch it`.

## No repair of old immutable artifact

Do NOT:
- edit/delete old g000002;
- create an alternate replacement for old g000002;
- manually advance old snapshot progress;
- manually rebind old buffered candidates;
- start g000003 on the old snapshot.

If prompt binding changes and normal activation creates a fresh compatible snapshot, report that as expected compatibility behavior.

## Repo-owned lever / architecture

Expected primary lever:
- `config/taste_steam_review_dossier_worker_prompt.md`;
- worker prompt revision/content-complete binding metadata.

Update durable route/decision notes only if required by current project protocol.

Do not add:
- local shell/Python prerequisite to Scheduled runtime;
- new queue;
- new scheduler;
- new recurring stage;
- retry daemon;
- browser automation service.

## Required live proof — 60 Seconds! Reatomized

A prompt edit alone is NOT sufficient.

Using the improved strategy in the current ordinary web environment, perform a bounded proof for:

- title: `60 Seconds! Reatomized`;
- appid: `1012880`.

The proof must show:

1. old historical technical evidence alone is recognized as insufficient for `historical`;
2. before declaring research sufficient, the worker performs a recent current-state retrieval step;
3. at least one <=365-day exact-product current-state player-feedback source is obtained within the existing 8/16 ceiling;
4. the proof does not claim that one recent anecdote resolves every historical sub-issue;
5. synthesis demonstrates the correct decision logic:
   - `historical` only if recent evidence supports it;
   - otherwise `current` or `uncertain` under existing rules;
6. no production candidate is published.

Known recent Steam Community support evidence from the diagnostic may be rediscovered, but the production prompt must not hardcode its URL or 60 Seconds specifically.

## Generic proof

The implementation must apply generically to future games where:

- an old bug/performance/compatibility/localization/service complaint is found;
- the worker is tempted to classify it as historical;
- current-state evidence has not yet been bound.

Do not hardcode:
- appid 1012880;
- 60 Seconds! Reatomized;
- Steam Community;
- a specific source URL.

## Required regressions

### TEMPORAL-PRESTOP-01 — historical technical requires recent check before stop
Worker instructions prohibit `evidence_stable` while a historical current-state-sensitive observation lacks recent current-state support.

### TEMPORAL-PRESTOP-02 — retrieval continues while budget remains
Missing required recent support triggers bounded retrieval rather than premature stop.

### TEMPORAL-PRESTOP-03 — historical remains existing semantic state
No definition change: historical still requires old evidence plus recent current-state check.

### TEMPORAL-PRESTOP-04 — unresolved uses existing uncertain path
If recent evidence does not resolve old-vs-current state, worker uses existing unresolved/uncertain semantics rather than fabricating historical.

### TEMPORAL-PRESTOP-05 — current still requires recent support
Existing current-state rule remains unchanged.

### TEMPORAL-PRESTOP-06 — durable traits not over-tightened
Old durable gameplay/story/art/music/structure evidence remains legal under existing rules.

### TEMPORAL-PRESTOP-07 — early multi-source diversification preserved
Required recent retrieval remains source-agnostic and does not regress into Steam-only searching.

### TEMPORAL-PRESTOP-08 — production ceilings unchanged
8/16 ceilings remain unchanged; no new quota/loop.

### TEMPORAL-PRESTOP-09 — strict validator unchanged and still green
Existing machine validator semantics remain authoritative and unchanged.

### TEMPORAL-PRESTOP-10 — privacy/provenance/language guards unchanged
All prior identity/source/language rules remain green.

### TEMPORAL-PRESTOP-11 — prior suites green
Russian gate, multi-source, early diversification, Store-card, transient-author, contradictions, language, package/story-DLC, buffering/compatibility/ownership suites remain green.

### TEMPORAL-PRESTOP-12 — 60 Seconds live proof
Live proof for appid 1012880 demonstrates recent current-state retrieval occurs before `evidence_stable` and within current 8/16 budget.

If TEMPORAL-PRESTOP-12 fails, status cannot be `complete_ready_for_live_acceptance`.

## Validator boundary

Do NOT change strict validator semantics merely because it rejected the old candidate.

The old candidate proves the validator already works.

Only change validator/tests if necessary to keep existing semantics aligned with prompt revision metadata; do not add new evidence rules.

If implementation uncovers an actual contradiction between prompt/contract/schema/validator, stop scope expansion and report `needs_user_decision`.

## Activation

If implementation succeeds:

- bounded branch/PR;
- focused regressions;
- existing relevant dossier suites;
- ownership validation;
- merge only green;
- normal GitHub-owned activation;
- fresh compatible prompt binding/snapshot if required;
- no manual old-progress repair/rebind.

Report compatibility effects clearly.

## Scheduled Task

Do NOT run Scheduled Task `Run now`.
Do not change Scheduled Task settings.

The live proof is validation-only and must not publish production state.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-temporal-prestop-retrieval-gate-implement-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture preflight / actual retrieval owner.
3. Accepted 60 Seconds diagnosis.
4. Exact pre-change stopping defect.
5. Repo-owned implementation.
6. Before/after temporal retrieval flow in plain language.
7. Temporal pre-stop gate semantics.
8. 60 Seconds live proof ledger.
9. Recent current-state source proof.
10. Synthesis outcome logic without overclaiming.
11. Generic behavior beyond 60 Seconds.
12. Confirmation no product/site hardcoding.
13. Confirmation contract/schema/strict semantics unchanged.
14. TEMPORAL-PRESTOP-01..12 results.
15. Existing guard suites.
16. PR / CI / merge refs.
17. Activation/binding/snapshot state:
   - snapshot id;
   - prepared/completed/remaining;
   - expected sequence;
   - group count;
   - group size;
   - exact expected group;
   - scope delta and reason;
   - compatibility effect on old `593378be…` buffered/canonical progress.
18. Confirmation old immutable g000002 was not changed/replaced.
19. Scheduled Task confirmation.
20. Unresolved.
21. Status.
22. Exactly one recommended next step.
23. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_live_acceptance`
- `needs_fix`
- `needs_user_decision`
- `blocked_external_transport`

## Status rule

`complete_ready_for_live_acceptance` is allowed ONLY if:

- real repo-owned Scheduled retrieval/stopping change is implemented and activated;
- TEMPORAL-PRESTOP-01..11 pass;
- TEMPORAL-PRESTOP-12 proves the behavior on 60 Seconds within the current 8/16 budget;
- old immutable g000002 remains untouched;
- evidence/privacy/provenance/temporal semantics are not weakened.

## Exactly one next step

If complete:
- return to Director for one clean production live acceptance on the newly activated compatible snapshot.

If needs_fix:
- identify one exact implementation defect.

If needs_user_decision:
- identify one bounded architectural/contract choice only.

If blocked_external_transport:
- identify the exact missing recent-retrieval capability.

Do not run production inside this task.

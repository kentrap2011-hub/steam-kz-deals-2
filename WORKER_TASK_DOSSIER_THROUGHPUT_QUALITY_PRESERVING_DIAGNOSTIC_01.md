# WORKER TASK — Dossier throughput / quality-preserving diagnostic 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Mode: `DIAGNOSTIC / MEASURE / NO IMPLEMENTATION`

## Goal

Find how to make Taste Steam Review Dossier processing materially faster **without reducing semantic quality, evidence quality, provenance strictness, or GitHub validation guarantees**.

The user is willing to change workflow/architecture if the same or better result quality can be proven, but does not authorize lower-quality dossiers, weaker validators, skipped evidence, or silent fallback.

## Required starting point

Read the current canonical Dossier runtime/worker contracts and exact current production state, including:
- `config/taste_steam_review_dossier_runtime_prompt.md`
- `config/taste_steam_review_dossier_worker_prompt.md`
- all schema / web-evidence / terminal-receipt contracts required by them
- current worker index/work manifest/state
- current validation/ingest path
- recent accepted and rejected Dossier execution evidence
- current Dossier -> Deep handoff behavior

Do not rely on old chat assumptions when current GitHub evidence differs.

## Questions to answer

### 1. Where time is actually spent
Measure or bound, from durable evidence where possible:
- semantic/web research time;
- source collection and provenance construction;
- validation and ingest latency;
- retry/rejection waste;
- group sizing / number of games per invocation;
- GitHub write / workflow overhead;
- duplicated work across nearby games or retries;
- any serial dependency that prevents safe parallelism.

Separate:
- unavoidable semantic work;
- avoidable orchestration overhead;
- avoidable retry work;
- avoidable repeated web/source work.

### 2. Current rejection/retry tax
Analyze recent retryable transport/validation failures and quantify:
- rejection rate;
- common failure classes;
- whether failures are semantic-quality failures or mechanical/schema/provenance mistakes;
- how much throughput would improve if mechanical failures were prevented before submission.

Do not propose weakening validation. Prefer earlier deterministic validation or better worker guidance.

### 3. Safe acceleration options
Evaluate, with concrete expected benefit and risk, at least:
- deterministic pre-validation before GitHub submission;
- prompt/contract simplification without semantic weakening;
- moving mechanical/provenance construction from ChatGPT to GitHub-owned deterministic code where safe;
- reusing already-fetched/source-normalized evidence without reusing stale semantic conclusions;
- group-size changes;
- safe independent-group parallelism, only if compatible with current order/binding/ownership rules;
- splitting research from final dossier assembly if that reduces repeated work without adding another authority;
- bounded caching of web evidence/source metadata;
- reducing redundant terminal-receipt / transport round trips;
- automatic retry only for purely mechanical failures, if exact authority can remain GitHub-owned;
- any other architecture that preserves the same semantic and evidence acceptance bar.

### 4. Quality invariants
For every recommendation, explicitly state which invariants remain unchanged:
- evidence completeness;
- provenance traceability;
- no fabricated reviews/sources;
- same canonical schema;
- same or stronger fail-closed validation;
- exact immutable bindings;
- no silent acceptance of incomplete dossiers;
- no reduction in required semantic coverage;
- no lowering of the quality bar merely to increase accepted count.

### 5. Throughput model
Produce a practical comparison:
- current approximate dossiers/hour (or groups/hour, if that is the only defensible unit);
- expected throughput after each proposed change;
- combined conservative / realistic / optimistic improvement;
- which changes are low-risk/high-return versus architectural.

If precise numbers cannot be proven, give bounded ranges and explain the evidence/assumptions.

### 6. Recommended implementation sequence
End with a ranked plan:
- **Quick wins** — low-risk, can be implemented independently;
- **Medium changes** — require code/contract work;
- **Architectural changes** — only if clearly worth it.

Identify which changes can be implemented without touching the semantic worker prompt, which require prompt/schema changes, and which require migration/compatibility work.

## Important boundaries

- Diagnostic only. Do not implement any acceleration.
- Do not create, change, enable, disable, or delete Scheduled Tasks / automations.
- Do not weaken validators or relax accepted evidence/provenance requirements.
- Do not change Dossier scope/eligibility to make throughput look better.
- Do not skip difficult games.
- Do not change Deep ranking, Stage 1/Stage 2 semantics, site UI, or Steam discovery.
- Do not create a second independent queue/control-plane owner.
- Do not use synthetic production data.
- Do not submit semantic Dossier results as part of this task.

## Deliverable

Create:
`reviews/worker_reports/dossier-throughput-quality-preserving-diagnostic-01.md`

The report must include:
1. measured current bottlenecks;
2. rejection/retry taxonomy;
3. candidate acceleration methods;
4. estimated speedup;
5. quality/safety risks;
6. recommended implementation order;
7. explicit answer: **how much faster can Dossier realistically become without lowering quality?**

Create a PR containing only the diagnostic report and minimal protocol-required worker closeout metadata.

Stop after report/PR. Do not implement the proposed changes.

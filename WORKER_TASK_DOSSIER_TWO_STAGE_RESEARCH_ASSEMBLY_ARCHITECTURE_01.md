# WORKER TASK — Dossier two-stage research / assembly architecture 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Mode: `ARCHITECTURE / CONTRACT RECON / NO IMPLEMENTATION`

## User-approved product direction

Split the current Dossier semantic work into two distinct semantic roles:

### Stage A — Research
A research worker focuses on **completeness and quality of game evidence**:
- find the strongest available exact-product evidence;
- cover strengths, weaknesses, current/historical issues, Russian-language evidence where required, dates and source identity;
- do not spend semantic attention on producing the final strict Dossier transport structure;
- output a bounded intermediate evidence package.

### Stage B — Assembly
A separate assembly worker focuses on **technical correctness and canonical Dossier construction**:
- consume the Stage-A evidence package;
- map already-found evidence into the exact canonical Dossier schema;
- verify required fields, provenance links, source identity, dates/languages/categories and deduplication;
- if a specific field is missing or ambiguous, first reopen the exact Stage-A source and fill only that gap;
- only if the required fact truly is absent from the supplied sources may it perform a narrow targeted lookup for that specific missing fact;
- it must not redo the whole game research by default.

Then the existing strict GitHub validator remains the final authority.

Conceptual flow:

`GitHub work authority -> Research worker -> immutable evidence package -> Assembly worker -> canonical validator/ingest -> accepted Dossier -> Deep`

The two semantic stages should be capable of operating as a pipeline: while Assembly handles already-researched work N, Research may work on later GitHub-assigned work N+1, subject to exact GitHub-owned scope/order/bindings.

## Goal of this task

Design the exact architecture and contracts needed to implement this safely.

Do **not** implement the two-stage worker yet.

## Required analysis

### 1. Current contract fit
Read the current canonical Dossier runtime/worker/schema/evidence/terminal contracts and current ingest/buffer/frozen-authority code.

Identify precisely:
- which current responsibilities belong to semantic research;
- which are mechanical/assembly responsibilities;
- which must remain solely GitHub-owned;
- which current invariants cannot move to either semantic worker.

### 2. Intermediate evidence package
Design a versioned Stage-A output contract.

It must preserve enough information that Stage B can assemble a complete canonical Dossier without redoing full research.

At minimum evaluate fields for:
- exact AppID/title/work/release binding;
- source URL / normalized locator;
- source type / surface;
- publication/observation date where actually known;
- language;
- acquisition mode and parent/child source relationship;
- exact-product identity evidence;
- safe summarized observed findings;
- which findings support which Dossier dimensions;
- strengths / weaknesses / nuances / temporal relevance;
- whether the source is current, historical or durable;
- source dedupe identity;
- research completeness / unresolved gaps.

Do not persist raw personal identifiers, usernames, profile URLs, or prohibited raw review text merely to make Stage B easier.

Clearly separate:
- facts Stage A actually observed;
- deterministic fields GitHub can derive;
- semantic classifications Stage B may make;
- fields that must never be inferred when absent.

### 3. Stage-B authority and bounded supplemental research
Define exactly what Stage B may do.

Default:
1. consume Stage-A package;
2. assemble canonical Dossier;
3. detect missing/invalid fields;
4. reopen exact supplied source for a missing field;
5. only then do narrow additional research for that explicit gap.

Define what counts as a narrow gap lookup and how to prevent Stage B from silently becoming a second full researcher.

Define what happens when:
- supplied source is unavailable later;
- date/language/product identity cannot be recovered;
- Stage-A evidence is contradictory;
- required coverage is genuinely missing;
- Stage B finds that Stage A used an invalid/duplicate source.

### 4. GitHub ownership / queue model
There must remain **one GitHub control-plane owner**.

Design:
- GitHub-prepared Research assignments;
- immutable research package identity/hash/bindings;
- GitHub acceptance or validation of Stage-A package before Assembly sees it, if needed;
- GitHub-prepared Assembly assignments;
- exact relationship between Research sequence and Assembly sequence;
- retry/recovery authority;
- stale package handling;
- snapshot rollover;
- canonical writer/serialization;
- terminal receipts.

Neither semantic chat may choose arbitrary games, skip failed groups, reorder canonical work, or become a second queue owner.

### 5. Pipeline / concurrency
Design how Research and Assembly can overlap safely.

Example target:
- Research works on package N+1;
- Assembly works on accepted/authorized package N.

Determine:
- whether current group-of-3 atomicity should remain, change, or move to per-game evidence packages;
- maximum safe in-flight packages;
- how to prevent two workers from receiving the same work;
- whether acceptance must remain ordered even if research finishes out of order;
- failure isolation so one bad game does not unnecessarily block unrelated researched evidence.

Do not create or authorize a new Scheduled Task in this task.

### 6. Validator role
The existing canonical Dossier validator must remain final authority and must not be weakened.

Determine whether an additional deterministic validator is needed for:
- Stage-A evidence package;
- Stage-B pre-submit structure;
- immutable bindings.

The goal is that semantic workers handle semantic judgment, while deterministic checks handle referential/schema correctness.

### 7. Throughput model
Using the already accepted Dossier throughput diagnostic, estimate:
- expected throughput of the two-stage pipeline;
- where latency is hidden by overlap;
- additional cost of Stage B;
- when the design is faster than one-worker Dossier;
- worst case where it becomes slower;
- conservative / realistic / optimistic expected improvement.

Do not promise an unmeasured production number.

### 8. Quality proof
Define acceptance tests proving no quality loss:
- same or stronger evidence coverage;
- same Russian/temporal/product-identity requirements;
- same strict provenance;
- no fabricated source or inferred missing fact;
- same canonical final Dossier schema;
- same fail-closed validator;
- no semantic dimension removed;
- compare representative real accepted/rejected historical inputs;
- downstream Deep receives equivalent or better usable evidence.

### 9. Migration plan
Define a bounded implementation sequence, preferably:
1. contracts/schema for Stage-A package;
2. deterministic validators/helpers;
3. Research worker;
4. Assembly worker;
5. offline real-artifact parity test;
6. non-active dual-stage shadow run;
7. controlled activation;
8. retire old one-stage path only after proof.

Explain compatibility with existing accepted Dossier cache and current Deep handoff.

## Important boundaries

- Architecture/recon only; no implementation.
- No Scheduled Task / automation changes.
- No production Dossier writes.
- No semantic backlog execution.
- No weakening of current Dossier evidence/provenance requirements.
- No second control-plane queue owner.
- No Deep scoring/ranking/UI changes.
- No Steam discovery changes.
- No synthetic production data.

## Deliverable

Create:
`reviews/worker_reports/dossier-two-stage-research-assembly-architecture-01.md`

The report must end with:
1. exact proposed Stage-A package;
2. exact Stage-B rules;
3. GitHub queue/ownership design;
4. pipeline/concurrency model;
5. expected speedup range;
6. quality-preservation proof plan;
7. implementation task split recommended for Director.

Create a PR containing only the architecture report and minimal protocol-required closeout metadata.

Stop after report/PR. Do not implement.

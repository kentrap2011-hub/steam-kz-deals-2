# WORKER TASK — Dossier two-stage contract/schema implementation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Mode: `IMPLEMENT / CONTRACTS / SCHEMAS / INACTIVE`

## Accepted architecture

The Director accepted:
- PR #171 — two-stage Dossier Research + Assembly architecture;
- report: `reviews/worker_reports/dossier-two-stage-research-assembly-architecture-01.md`.

Treat that report as the approved design baseline for this task.

Do not redesign the architecture from scratch.

## Goal

Implement **only P1** from the accepted architecture:

1. versioned Stage-A Research evidence-package schema/contract;
2. versioned Stage-B Assembly assignment/result/receipt schema/contract;
3. exact immutable bindings between GitHub-prepared work, Research package and Assembly work;
4. lifecycle/status vocabulary needed for future GitHub-owned staging;
5. compatibility/versioning rules with the current one-stage Dossier path;
6. inactive feature-gating so the current production one-stage Dossier remains authoritative.

This task prepares interfaces only. It must not activate Research or Assembly workers.

## Required contract surfaces

### A. Research package

Implement a strict, versioned contract equivalent to the accepted
`DOSSIER-RESEARCH-PACKAGE-V1` design.

It must define, at minimum:
- exact immutable assignment identity;
- current snapshot/group/item bindings;
- exact AppID/title/work/release binding;
- source locator and safe normalized source identity;
- source type / evidence role;
- date/language/acquisition mode;
- exact-product binding evidence;
- parent/child source relationship;
- physical-source dedupe identity;
- observed feedback records;
- safe neutral findings;
- strength/weakness/nuance/conflict support;
- 12-dimension coverage/gap audit;
- current/historical/durable/uncertain relevance;
- unresolved gaps;
- package hash / contract version binding;
- privacy restrictions.

Unknown/unobserved facts must remain explicit unknowns.
No schema default may manufacture evidence.

### B. Assembly assignment and output contract

Implement the inactive contract for Assembly so that future Assembly work can consume only a GitHub-validated Research package.

Define:
- exact accepted Research package hash;
- exact original assignment/snapshot/group/item bindings;
- Stage-B contract/prompt revision binding;
- permitted output path/namespace;
- exact current canonical Dossier V2 target schema binding;
- typed outcomes for:
  - assembled candidate ready;
  - exact-source revisit required/resolved;
  - narrow gap lookup required/resolved;
  - unresolved semantic gap;
  - source unavailable;
  - invalid/duplicate Research evidence;
  - binding mismatch / stale package;
  - runtime/tool failure;
- create-only semantics;
- no direct canonical cache/progress acceptance.

### C. Exact-source-first supplemental research rule

Encode clearly in machine-readable contract/config where practical:

Assembly must:
1. use the accepted Research package;
2. when a required field is missing, first revisit the exact supplied source;
3. only when that exact source genuinely lacks the needed fact may Assembly perform a narrow lookup for that named gap;
4. never silently restart broad game research;
5. never invent a missing date, language, product identity, source relationship or evidence statement.

Define what qualifies as a narrow lookup and what requires fail-closed return to GitHub.

### D. Ownership / lifecycle

GitHub remains the single control-plane owner.

Contracts must make clear:
- neither Research nor Assembly chooses games;
- neither stage reorders work;
- neither stage authorizes retries/recovery;
- neither stage marks canonical Dossier accepted;
- neither stage writes Deep state;
- package/assignment state is GitHub-owned;
- only the existing final strict Dossier validator/ingest may authorize canonical acceptance after future integration.

Define state names for future inactive staging, but do not implement the staging engine in this task.

### E. Compatibility and inactive gate

The existing one-stage Dossier must remain fully live and authoritative.

Implement:
- version separation;
- distinct inactive namespaces;
- no collision with current `data/ai_inbox/taste_steam_review_dossiers` transport;
- explicit compatibility behavior for already accepted Dossiers/cache;
- no rewriting of existing accepted Dossier artifacts;
- no automatic migration of old prompt/contract hashes;
- explicit inactive / implemented-but-not-authoritative flags.

A later task must be required to activate any two-stage execution.

## Validation

Add bounded deterministic validation/tests for the new contracts/schemas only.

At minimum prove:
- valid Research package shape passes;
- unknown fields fail when contract says strict;
- broken refs fail;
- duplicate local ids fail;
- invalid source/feedback parent relation fails;
- missing immutable bindings fail;
- unsafe/private locator classes fail;
- invented/default semantic evidence is not auto-filled;
- Assembly cannot reference an unaccepted/unbound Research hash;
- stale/binding mismatch fails;
- typed outcomes are exhaustive and unambiguous;
- existing current one-stage Dossier tests remain green.

Use fixtures only for schema/unit validation; do not write synthetic production data.

## Boundaries

- Do not implement Research semantic worker prompt.
- Do not implement Assembly semantic worker prompt.
- Do not implement the GitHub staging/claim/assignment engine beyond the contracts/schema helpers strictly required to validate these interfaces.
- Do not change current Dossier queue/order/retry behavior.
- Do not change current Dossier canonical validator acceptance rules.
- Do not change Deep, ranking, site UI, Steam discovery, translations or publication.
- Do not modify or create Scheduled Tasks / automations.
- Do not activate the two-stage path.
- Do not write production Research/Assembly artifacts.
- Do not migrate existing accepted Dossiers.
- Do not weaken evidence/provenance/Russian/temporal/privacy requirements.

## Deliverable

Create:
`reviews/worker_reports/dossier-two-stage-contract-schema-implement-01.md`

Report must include:
1. exact files added/changed;
2. Research package schema;
3. Assembly assignment/result/receipt contracts;
4. version/binding model;
5. inactive feature gate;
6. compatibility with current one-stage Dossier;
7. validation evidence;
8. explicit confirmation that production authority is unchanged;
9. recommended next task = P2 GitHub deterministic helpers/validators, but do not start it.

Create a PR and stop.

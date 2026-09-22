# WORKER TASK — Progressive PASS 2 Phase C Core Implement 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: progressive-pass2-phase-c-core-implement-01
Mode: IMPLEMENT / VALIDATE
Worker slot: НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2

## START

First open the current CHAT_PROTOCOL.md from main and complete its START gate.
Then open this task from main and use the current canonical contracts/routes/prompts as source of truth.

Canonical inputs include:
- config/progressive_personalization_contract.json
- config/progressive_pass1_contract.json
- reviews/worker_reports/progressive-pass2-dossier-ready-gate-amendment-01.md
- current Dossier acceptance/persistence contracts as read-only dependencies

## Why this task is split from final activation

ЧАТ 1 is concurrently implementing the Dossier non-blocking progress redesign. That work may change Dossier progress/ingest orchestration.

Therefore this task must implement the PASS 2 core on Progressive-owned surfaces only and must NOT modify Dossier contracts, Dossier worker prompt, Dossier recovery logic, or Dossier ingest/workflow files.

The later Dossier-persistence -> PASS 2 re-evaluation wiring is intentionally deferred until ЧАТ 1 is accepted, so two workers do not modify the same runtime surface concurrently.

## Goal

Implement the inactive GitHub-owned PASS 2 Phase C core exactly from the accepted canonical design, without starting production PASS 2.

At the end, PASS 2 core mechanics must exist and be validated, but:
- PASS 2 remains inactive;
- no PASS 2 Scheduled Task is created or run;
- no Dossier workflow integration is activated yet;
- no production PASS 2 attempt is consumed.

## Required core semantics

1. PASS 2 considers only current `analysis_incomplete` items.
2. Eligibility requires the exact current PASS 1 `semantic_generation_id + work_id`.
3. Eligibility requires a canonically accepted, exact-compatible, fresh Dossier for the same app/work identity.
4. Buffered/unaccepted, stale, expired, wrong-app, wrong-work, ambiguous, cross-release, or compatibility-mismatched Dossier never unlocks PASS 2.
5. Waiting for Dossier consumes zero attempts.
6. Queue projection alone consumes zero attempts.
7. Maximum automatic PASS 2 attempts is exactly one per current `semantic_generation_id + work_id`.
8. The attempt is consumed only by:
   - an exact-bound accepted PASS 2 result; or
   - a GitHub-owned terminal execution receipt proving the authorized attempt actually ran.
9. A failed/unresolved PASS 2 result remains `analysis_incomplete` and becomes ineligible for another automatic PASS 2 attempt for that same generation/work_id.
10. PASS 1 and PASS 2 remain independent; neither waits for the other globally.
11. One PASS 2 item failure cannot block unrelated PASS 2 items.
12. GitHub owns eligibility, order, immutable binding, validation, persistence, state, attempt accounting, and visual projection.
13. Scheduled ChatGPT, when later activated, will only execute GitHub-prepared bounded work; it must never choose/rebuild/reorder scope.

## Core implementation surfaces

Implement the minimum canonical PASS 2 core, including:

- PASS 2 durable state;
- deterministic PASS 2 work projection/manifest;
- immutable create-only per-item result transport;
- result schema/validator;
- exact binding to:
  - semantic_generation_id;
  - work_id;
  - appid;
  - accepted Dossier content sha256;
  - current Dossier compatibility binding;
- GitHub-owned ingest/persistence;
- GitHub-owned terminal execution receipt path/accounting for a real authorized attempt that ran but produced no accepted semantic result;
- independent item-level processing; no batch all-or-none/maximal-prefix semantics;
- a bounded PASS 2 worker prompt/contract for future Scheduled execution;
- focused regression tests for eligibility, stale binding rejection, one-attempt accounting, sibling independence, and PASS1/PASS2 parallelism;
- a reusable PASS 2 eligibility recomputation entrypoint/function that can later be wired to canonical Dossier persistence without changing Dossier semantics.

Do not wire that recomputation into Dossier workflows in this task.

## Progressive state projection

PASS 2 must be able to replace the current unresolved projection for the exact current item only:

- trustworthy fit -> `analyzed_fit`;
- trustworthy completed negative -> `analyzed_not_fit`;
- unresolved/insufficient/worker terminal failure -> remain `analysis_incomplete`.

Do not mutate the original PASS 1 historical attempt record to pretend PASS 1 produced the PASS 2 result.

Preserve clear provenance between PASS 1 and PASS 2.

## User-visible provenance requirement

The site must be able to distinguish an item whose current resolution came from PASS 2.

Add a GitHub-produced machine provenance field sufficient for the browser to render this without inference from DOM/history.

Required visible behavior:
- PASS 1 fit may keep the existing label `Разобрана · подходит вам`;
- PASS 2 fit must visibly identify PASS 2, e.g. `Разобрана · PASS 2`;
- PASS 2 unresolved after its one attempt must visibly identify that the additional pass ran, e.g. `Разбор не завершён · PASS 2`;
- `not_analyzed` remains unchanged;
- analyzed_not_fit remains excluded from the normal list under existing rules.

Browser remains read-only presentation and must not derive PASS provenance itself.

## Activation guards

During this task:
- keep runtime `pass2_active=false`;
- no production PASS 2 result artifact;
- no automatic attempt consumption in current production state;
- no Scheduled Task create/edit/enable/run;
- no user/operator Run now;
- do not process any real backlog item through PASS 2.

It is allowed to mark the repository implementation as implemented-but-inactive only after all core tests pass and the contract clearly distinguishes `implemented=true` from `active=false`.

## Concurrency / scope exclusions

Do not modify:
- Dossier non-blocking progress state;
- Dossier worker prompt;
- Dossier recovery/quarantine behavior;
- Dossier ingest/workflow wiring;
- PASS 1 behavior or attempt state;
- Taste Semantic Producer;
- Scheduled Task cadence.

If the core cannot be completed without changing a Dossier-owned file currently in ЧАТ 1 scope, stop that part, record the exact dependency, and continue only independent PASS 2 work.

## Validation

Prove at minimum:

- P2CORE-01: no accepted exact-compatible Dossier -> no eligible work, zero attempts consumed.
- P2CORE-02: exact accepted compatible Dossier + current incomplete PASS 1 -> exactly one eligible work unit.
- P2CORE-03: stale/wrong-app/wrong-work/wrong-binding Dossier -> no eligibility.
- P2CORE-04: work/result identity is immutable and exact-bound to dossier SHA/binding.
- P2CORE-05: queue presence alone consumes zero attempts.
- P2CORE-06: accepted result consumes exactly one attempt.
- P2CORE-07: terminal execution receipt consumes exactly one attempt only when it proves the authorized run actually executed.
- P2CORE-08: second automatic attempt for same generation/work_id is impossible.
- P2CORE-09: changed semantic generation/work_id may establish a new budget under canonical rules.
- P2CORE-10: one invalid/stale PASS 2 artifact cannot block valid siblings/later work.
- P2CORE-11: PASS 1 may continue not_analyzed work while PASS 2 has eligible/recovered incomplete items.
- P2CORE-12: PASS 2 state projection preserves PASS 1 historical provenance.
- P2CORE-13: site projection visibly distinguishes PASS 2-resolved and PASS 2-still-incomplete cards.
- P2CORE-14: PASS 2 remains inactive and no production attempt/run occurred.
- P2CORE-15: no Dossier-owned runtime file modified while ЧАТ 1 task is active.
- P2CORE-16: durable report committed and reread from main before completion.

## Durable report

Create and commit:
reviews/worker_reports/progressive-pass2-phase-c-core-implement-01.md

Keep it compact and include:
- architecture preflight;
- exact files changed;
- state/work/result/receipt model;
- provenance/UI behavior;
- validation results P2CORE-01..16;
- unresolved Dossier integration dependency;
- exact refs;
- final status;
- exactly one recommended next step.

Allowed statuses:
- complete_core_ready_for_director_acceptance
- needs_fix
- blocked_external_operator_action
- needs_user_decision

Before final response, commit the report and reread the exact report from main.

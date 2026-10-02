# WORKER TASK — fresh deal discovery refresh fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `fresh-deal-discovery-refresh-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/fresh-deal-discovery-refresh-fix-01.md`

## User-visible defect

A currently excellent offer for **Mirror's Edge Catalyst** (Steam AppID `1233570`) was absent from the recommendation list entirely.

Director investigation on current main found:

- canonical production manifest discovery was last rebuilt from Steam on 2026-09-23;
- that discovery produced 609 shortlist/mailing candidates;
- `data/production/pre_ai/store_snapshot.json` was refreshed on 2026-10-01, but its discovery source was still `data/production/mailing/index.json` from 2026-09-23;
- the store refresh rechecked price/discount state only for those already-known 609 candidates;
- AppID 1233570 was absent from mailing, store snapshot, progressive candidate context and PASS work;
- therefore the game never reached taste evaluation, ranking or visual publication.

The implementation must verify this root cause from current main before changing code. If current evidence contradicts it, stop and report the actual root cause instead of forcing the proposed fix.

## Goal

Make the normal production refresh discover **newly discounted games that were not present in the previous shortlist/candidate set**.

A fresh production cycle must not be limited to refreshing commercial fields on the previous candidate universe.

The fix must be generic. Do not add any AppID/title-specific exception for Mirror's Edge Catalyst.

## Architecture requirement

There must remain one GitHub-owned production discovery/control path.

Do not add:
- a second catalog owner;
- a parallel shortlist;
- a retry daemon;
- a browser-side discovery path;
- a ChatGPT Scheduled Task;
- a second recurring scheduler.

Reuse the existing canonical Steam discovery/production pipeline and repair its freshness handoff.

The browser remains read-only.

## Mandatory START gate

1. Read current `CHAT_PROTOCOL.md` fully and execute START gate.
2. Read current `DIRECTOR_TASK_BOARD.md` current-state section.
3. Read this task fully.
4. Inspect current canonical architecture/contracts/workflows for:
   - Steam discovery/catalog collection;
   - shortlist generation;
   - mailing/index generation;
   - pre-AI store snapshot;
   - progressive candidate materialization;
   - final visual publication.
5. Inspect current source timestamps/bindings before implementation.
6. Reconcile with latest main immediately before writing.

Do not start another task.

## Required diagnosis

Establish the exact current chain that allows this stale-universe behavior.

At minimum answer:

1. Which workflow/script owns fresh Steam catalog discovery?
2. Why did later production refreshes update current prices but not rebuild the candidate universe?
3. Is the old 2026-09-23 discovery source intentionally pinned, accidentally skipped, or blocked by another freshness gate?
4. Which downstream artifacts inherit the stale universe?
5. What normal event/workflow should own refreshing discovery going forward?
6. Can discovery be refreshed without forcing semantic Deep/Dossier execution?

Do not patch downstream symptoms before answering these.

## Required implementation behavior

After the fix, a normal fresh production refresh must:

1. obtain a fresh authoritative Steam catalog/deal discovery input;
2. evaluate newly appearing discounted games under the existing deterministic shortlist eligibility rules;
3. add newly eligible games to the canonical candidate universe;
4. remove or exclude games whose offers are no longer active according to existing commercial-freshness rules;
5. regenerate all deterministic downstream candidate/pre-AI bindings that depend on the candidate universe;
6. preserve existing semantic results only where their immutable/current bindings remain valid;
7. mark genuinely new candidates as needing the appropriate existing semantic work rather than fabricating results;
8. allow later visual publication to include a newly discovered candidate once it satisfies the existing publication requirements.

Do not weaken existing shortlist quality gates merely to make Catalyst appear.

## Mirror's Edge Catalyst as regression probe, not special case

Use AppID `1233570` only as a concrete regression probe.

Prove both:

### Historical/stale-source reproduction
Given an old candidate universe that does not contain a game, refreshing only its prices cannot discover it.

### Fixed behavior
Given a fresh catalog in which that same game has an active qualifying discount, the normal discovery path can introduce it into the candidate universe if it passes the ordinary existing rules.

No code/config branch may special-case:
- AppID 1233570;
- title Mirror's Edge Catalyst;
- EA;
- -95%;
- this exact sale.

If live Steam state changes before validation, use deterministic fixtures to prove the generic behavior and report the current live status separately.

## Freshness contract

Introduce or strengthen an explicit fail-closed freshness contract so downstream production cannot silently claim a fresh recommendation set when:

- current price snapshot is fresh;
- but the candidate discovery universe is materially older/stale.

At minimum the relevant production metadata should expose:
- discovery observed/generated timestamp;
- commercial refresh timestamp;
- their source/binding relationship;
- whether the candidate universe was rebuilt for this production cycle.

A downstream build must not label the candidate list current if only prices were refreshed over a stale discovery universe.

Choose the simplest existing-owner-compatible mechanism; do not invent another control plane.

## Scheduling / execution ownership

If an existing GitHub Actions nightly/production workflow is supposed to perform fresh discovery, fix its dependency/order so that fresh discovery happens before downstream refresh.

Do not create an additional recurring schedule if an existing one can own the job.

Do not create, modify, enable, disable, pause, resume or run any ChatGPT Scheduled Task.

A GitHub Actions workflow may be updated/run only as part of the existing production architecture and task validation.

## Preservation requirements

Do not reopen or alter without necessity:
- RANK-013 ordering policy;
- current 60/40 score geometry;
- Deep/Dossier semantic contracts;
- Russian translation behavior;
- expired-sale filtering logic already accepted;
- giveaway pipeline;
- browser/UI architecture.

Do not use this task to implement the new taste-scoring architecture or questionnaire profile delta.

## Required tests

Add deterministic regressions proving at least:

1. newly discounted game absent from prior candidate universe becomes discoverable after fresh catalog rebuild;
2. price-only refresh cannot masquerade as candidate-universe refresh;
3. stale discovery + fresh price snapshot is detected/fails closed or is explicitly degraded according to the canonical contract;
4. ordinary eligibility gates still apply to newly discovered games;
5. expired/inactive games remain excluded under existing rules;
6. unchanged candidates preserve valid deterministic/semantic state where bindings permit;
7. genuinely new candidates receive existing pending semantic state, not fabricated fit;
8. no duplicate candidate identity is introduced;
9. downstream pre-AI candidate context/work manifests bind to the new discovery universe;
10. no AppID-specific logic exists.

## Live acceptance

After implementation and regression validation, if the existing production workflow can safely be run without invoking ChatGPT semantic workers:

1. run the normal GitHub-owned discovery/production refresh;
2. verify the canonical discovery timestamp advanced;
3. verify the candidate universe is rebuilt from fresh source data rather than the old 2026-09-23 mailing universe;
4. check whether AppID 1233570 is currently active and qualifies under ordinary gates;
5. if it qualifies, show the exact stage it reaches;
6. if it does not qualify, report the deterministic reason;
7. verify later existing semantic queues/work identify new candidates normally.

Do not fabricate a Catalyst row if the live offer has changed or fails ordinary gates.

If a safe live refresh cannot be run, provide exact evidence and stop at implementation-ready validation rather than manually editing production data.

## PR / validation

Use a dedicated branch and PR.

Before merge:
- reconcile branch with latest main;
- run all directly affected tests;
- run existing ownership/backlog/visual/pre-AI validations required by touched contracts;
- ensure no unrelated production/semantic state is overwritten.

Do not merge with failing required checks.

## Durable report

Write:
`reviews/worker_reports/fresh-deal-discovery-refresh-fix-01.md`

Required sections:

1. Task
2. START / current-main reconciliation
3. Reproduction
4. Root cause
5. Existing ownership chain
6. Why Catalyst was absent
7. Chosen fix
8. Freshness contract
9. New-candidate lifecycle after fix
10. Regression coverage
11. Live acceptance
12. Catalyst current outcome
13. Boundaries preserved
14. Exact PR/commit/run refs
15. Status
16. Recommended next step — exactly one bounded next action

Allowed final statuses:
- `implementation_complete_ready_for_director_acceptance`
- `implementation_complete_live_refresh_pending`
- `diagnosed_needs_different_fix`
- `blocked`

## Hard boundaries

Do NOT:
- add an AppID-specific exception;
- manually insert Catalyst into canonical candidate/visual files;
- weaken shortlist/review/taste gates;
- create another scheduler/control plane;
- run semantic Deep/Dossier workers;
- modify canonical Taste profile;
- implement new taste scoring;
- create or modify ChatGPT Scheduled Tasks;
- start another task.

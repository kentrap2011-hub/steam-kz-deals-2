# WORKER TASK — DOSSIER / DEEP RELEASE-YEAR IDENTITY COMPATIBILITY FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `dossier-deep-release-year-identity-compatibility-fix-01`
Mode: `CONTRACT-FIRST IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/dossier-deep-release-year-identity-compatibility-fix-01.md`

## Accepted diagnosis

The accepted diagnostic report is:

`reviews/worker_reports/dossier-deep-ready-count-gap-diagnostic-01.md`

Accepted root cause:

- Dossier current/fresh count = 46;
- ordinary Deep ready/pending = 38;
- exactly 8 current/fresh exact-AppID/exact-title dossiers are rejected only as `dossier_wrong_release_year`;
- Dossier stores a resolved original/work release year;
- Deep derives a year from the current queue/store release date and currently requires exact equality;
- the eight exact products are therefore falsely incompatible even though AppID, title, evidence binding, resolved identity and freshness are otherwise correct;
- this is a cross-stage contract-boundary defect, not missing Dossier work and not the separate legacy Deep migration.

Exact known regression AppIDs:
- 1170760 — XIII - Classic
- 1237950 — STAR WARS™ Battlefront™ II
- 1237970 — Titanfall® 2
- 1237980 — STAR WARS™ Battlefront
- 1238040 — Dragon Age II: Ultimate Edition
- 1238060 — Dead Space™ 3
- 1238820 — Battlefield 3™
- 13500 — Prince of Persia: Warrior Within™

Do not re-diagnose the root cause from scratch unless current `main` materially contradicts the accepted report.

## Goal

Define and implement one shared, explicit identity-compatibility rule for Dossier -> Deep so that:

1. exact-product protection remains fail-closed;
2. the eight accepted exact-product dossiers are no longer falsely rejected merely because original/work release year differs from Steam/store release year;
3. truly wrong product/edition/identity evidence remains rejected;
4. GitHub remains the sole control plane;
5. no Dossier/Deep/Fast semantic backlog is manually replayed as part of this fix;
6. the independent legacy Deep migration remains intact and may continue concurrently.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. accepted diagnostic report;
4. relevant Dossier/Deep routes in `PROJECT_ROUTES.md`;
5. relevant identity/exact-product decisions in `PROJECT_DECISIONS.md`;
6. current Dossier contract/schema/evidence contract;
7. current PASS 2 contract;
8. `config/execution_ownership_contract.json`;
9. only the smallest compatibility/recompute/tests/workflow files needed.

## Mandatory architecture preflight

Before writes, prove:

- GitHub remains owner of Dossier acceptance/freshness, Deep eligibility, exact Dossier binding, recomputation, persistence, attempts, recovery, completeness and publication;
- Scheduled ChatGPT remains only the bounded semantic data plane;
- this fix changes no scheduler, recurrence, queue ownership, retry loop, recovery ownership or Scheduled Task configuration;
- Dossier and Deep may continue independently and in parallel;
- the one-off legacy Deep migration is separate and must not be invalidated/rebuilt/restarted merely by this compatibility repair;
- no whole-`main` stability requirement is introduced.

If current decisions do not define the corrected cross-stage identity semantics precisely enough, add the smallest new canonical decision (for example PPD-011) BEFORE changing runtime behavior.

## Required contract decision

Do not simply delete the release-year check.

Define one explicit shared semantic rule that distinguishes, at minimum:

- exact Steam product identity / AppID;
- exact intended title/work identity;
- original/work release year;
- Steam/storefront release-date year when different.

The rule must make clear when a year is:
- identity evidence/corroboration;
- a hard compatibility key;
- informational only.

### Required safety property

A Dossier MUST NOT be rejected solely because:

- Dossier resolved original/work year != current Steam/store release-date year,

when all required exact-product identity evidence proves it is the same intended current AppID/product.

But the repair MUST NOT weaken protection against:
- wrong AppID;
- wrong title/product;
- wrong edition/remaster when identity truly differs;
- unresolved identity;
- stale/expired/incompatible Dossier binding;
- cross-product or DLC/base-game contamination;
- forged or missing exact-product evidence.

If a year equality remains anywhere as a hard gate, both compared fields must have the same canonical semantic meaning and source class. Do not compare original/work year to storefront/re-release year as if they were the same field.

## Implementation boundary

Implement the smallest coherent contract/runtime change.

Likely affected areas may include:
- Dossier identity contract/schema terminology if semantics are currently ambiguous;
- PASS 2 Dossier compatibility/eligibility rule;
- deterministic eligibility recomputation;
- regression tests;
- route/decision documentation.

Do not manually rewrite accepted Dossier files just to make the eight pass.

Historical accepted dossiers should remain immutable unless the canonical contract versioning model genuinely requires a migration. Prefer compatibility logic that correctly understands already-valid exact-product dossiers.

Do not manually edit current Deep state to mark the eight ready. The normal GitHub-owned recomputation path must derive the corrected eligibility.

## Exact regression requirements

Add positive regressions for all eight known AppIDs or a fixture set that explicitly enumerates them and proves their real year pairs:

- 1170760: queue/store 2020 vs Dossier work 2003
- 1237950: 2020 vs 2017
- 1237970: 2020 vs 2016
- 1237980: 2020 vs 2015
- 1238040: 2020 vs 2011
- 1238060: 2020 vs 2013
- 1238820: 2020 vs 2011
- 13500: 2009 vs 2004

For each, prove that exact current product identity remains accepted despite the year-kind difference.

Add negative regressions proving fail-closed behavior for:
- wrong AppID;
- wrong product/title;
- unresolved identity;
- stale/expired Dossier;
- incompatible evidence-contract binding;
- actual wrong edition/remaster/cross-product case where exact identity does not match.

Regression must prove the fix does not mean “ignore year and trust any dossier”.

## Current production reconciliation

Immediately before merge:

- reread fresh `main`;
- preserve any concurrent Dossier progress;
- preserve any concurrent legacy migration progress/results;
- do not overwrite migration state, Deep receipts, Dossier state or visual state.

After merge, use only normal deterministic GitHub recomputation/build paths.

Required current-state proof:

- the eight known identities no longer have `dossier_wrong_release_year` solely due to the original-vs-store year mismatch;
- if the surrounding 399-game scope and Dossier freshness counts are unchanged, ordinary Deep compatibility should reconcile 46 current/fresh Dossiers -> 46 ordinary Deep-ready/compatible identities;
- if concurrent production changed counts, do not force 46/46 numerically: instead provide exact current arithmetic and prove all eight are no longer in the false-rejection set.

The finite legacy migration may still pause ordinary Deep emission. That is acceptable. Distinguish:
- ordinary Deep eligibility/readiness;
- actual worker-emitted migration work.

## Legacy migration constraint

Current one-off migration:
`deep-legacy-full-reanalysis-with-preserved-positives-01`

Requirements:
- do not rebuild its frozen 30-target scope;
- do not invalidate accepted migration results;
- do not re-run completed migration items;
- do not mix the eight release-year compatibility items into that frozen migration;
- do not change PPD-010 semantics;
- ordinary Deep items unlocked by this fix may wait until migration priority naturally releases them.

If the migration completes concurrently, simply reconcile fresh `main` and continue.

## Dossier constraint

Dossier may continue normally throughout this task.

Do not:
- pause Dossier;
- change Dossier Scheduled Task settings;
- manually process Dossier backlog;
- regenerate the eight dossiers merely to bypass the bug;
- add a second Dossier compatibility queue.

## Validation

Required:
- focused identity compatibility regression;
- existing Dossier strict/exact-product regressions;
- PASS 2 core;
- Dossier/PASS 2 integration;
- backlog disposition validation;
- migration regression if shared PASS 2 compatibility code is touched;
- current production eligibility recomputation with zero semantic attempts consumed;
- visual/UI counter validation if published counters change;
- post-merge normal build/deploy validation when applicable.

Prove:
1. all eight false rejects are repaired;
2. wrong-product cases remain fail-closed;
3. no ordinary Deep attempt is consumed merely by recomputation;
4. no migration attempt/result is changed by recomputation;
5. no Dossier canonical history is rewritten;
6. no Scheduled Task is changed;
7. Dossier can continue concurrently.

## Hard prohibitions

Do not:
- manually author Deep semantic results;
- manually process the eight through Deep;
- manually rebuild their Dossiers as a workaround;
- weaken exact-product identity globally;
- remove all year semantics without a replacement contract;
- change ranking weights/risk policy;
- change migration scope/history;
- create a second scheduler/queue/retry loop;
- change Scheduled Tasks.

## Report

Write:
`reviews/worker_reports/dossier-deep-release-year-identity-compatibility-fix-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Canonical identity decision`
4. `Accepted root cause`
5. `Changes`
6. `Eight-AppID regression`
7. `Negative identity regressions`
8. `Legacy migration reconciliation`
9. `Dossier parallelism`
10. `Validation`
11. `Current production counters`
12. `Published result`
13. `Unresolved`
14. `Status`
15. `Recommended next step` — exactly one bounded next step
16. exact PR/commit/run/artifact refs
17. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another task after this one.

# WORKER TASK — VISUAL STALE SNAPSHOT REBASE RACE FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- do not search, read, modify, or use another repository;
- if GitHub/tool opens another repository or the target is ambiguous, stop and switch to this repository before continuing.

Task ID: `visual-stale-snapshot-rebase-race-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/visual-stale-snapshot-rebase-race-fix-01.md`

## User authorization

The user explicitly authorizes fixing the already diagnosed visual-publication freshness defect.

Do not broaden this task into unrelated browser, ranking, translation, Fast, Dossier, Deep, sale-expiry, scheduler, queue, or retry redesign.

## Accepted diagnosis

The accepted read-only diagnostic is:

`reviews/worker_reports/stale-deep-statistics-publication-diagnostic-01.md`

That report proved a stale-snapshot persistence race in the GitHub-owned full visual publication path:

1. a visual payload was generated from an older checkout / older semantic source blobs;
2. `main` advanced while the build was running;
3. the first push failed;
4. the workflow rebased the already-generated visual commit onto the newer parent;
5. the visual JSON was not rebuilt against that newer parent;
6. the final visual commit therefore had a newer parent while still carrying older Deep/PASS2 source binding/statistics.

Pinned historical proof from the accepted diagnostic:
- build checkout: `53767218c890c9bdb5698d039a5651fa416c4963`;
- old PASS2 state blob: `4435430a967f94474c41aa77ea97374f7d276cf1`;
- newer parent: `dede9ea264b834819642b6e23f778cabd85a4fdd`;
- newer PASS2 state blob: `b1967e420ef55cc3c2368f25f71ef99df8041aec`;
- stale persisted visual commit: `2202a668cad11f67f0659aa6bcfe5e6cf34bb9ab`.

Current project state also includes PR #125 / merge `070f30807acceffed36a342e1d442f5dcd1c99c7`, which made missing Russian translations nonblocking and added translation observability. Preserve all of that current behavior.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully and make the required task checklist.

Read minimally:
1. `CHAT_CONTEXT.md`;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. the accepted stale Statistics diagnostic report named above;
4. visual build / publication routes in `PROJECT_ROUTES.md`;
5. current visual/freshness decisions and contracts in `PROJECT_DECISIONS.md` / relevant config;
6. `config/execution_ownership_contract.json`;
7. current `.github/workflows/build-daily-visual-payload.yml`;
8. current `.github/workflows/deploy-visual.yml`;
9. the exact scripts that build, bind, validate, persist, or classify freshness for `data/production/visual/current.json`;
10. only focused tests needed for this fix.

Do not reconstruct unrelated project history.

## Architecture preflight — mandatory before writes

Prove and record:

1. GitHub/GitHub Actions remains sole owner of deterministic visual rebuild, freshness validation, canonical persistence and Pages publication.
2. Browser remains read-only and is not part of the fix.
3. Which exact source artifacts/blobs materially define one generated full visual payload.
4. Which current step can move/rebase a generated payload onto a newer `main`.
5. Why whole-repository head movement alone is not necessarily a semantic change, but material source-blob drift is.
6. How the replacement design prevents a generated payload from being persisted under a parent whose material inputs differ from those used to build it.
7. Why the design adds no second scheduler, queue, retry daemon, backlog manager, or ChatGPT control-plane authority.

If ownership or source-binding authority cannot be proven from current canonical state, stop with `needs_user_decision` rather than inventing it.

## Required behavior

### A. Bind every full visual build to exact material source state

The generated full visual must carry or otherwise be validated against exact immutable identities for the material source inputs used to compute it.

At minimum include the current authoritative Progressive/PASS2 state identity and every other source identity already required by the current visual production contract to prove the visual was computed from the same semantic/control-plane state that will become its persisted parent.

Do not invent a broad whole-repository equality requirement if only specific material inputs matter.

### B. No stale generated JSON may survive material drift

If `main` advances before persistence/push:

- compare the exact material source identities used by the generated visual with the identities in the candidate fresh parent;
- if none of those material identities changed, the existing generated payload may proceed only if current contracts allow it;
- if any material source identity changed, the already-generated JSON must NOT be rebased/persisted unchanged onto that new parent.

On material drift, choose the smallest correct canonical behavior:
- rebuild the full visual from fresh `main` and revalidate before persistence; or
- fail closed without modifying `data/production/visual/current.json`.

Do not silently reuse stale generated bytes.

### C. Publication must stay honest

A successful workflow/deploy must not imply freshness by itself.

Preserve or improve explicit freshness receipts so they distinguish:
- a genuinely fresh build bound to the exact current source state;
- an intentionally degraded publication using an older canonical visual;
- a build aborted because source state changed during persistence;
- any current legitimate `deterministic_refresh_preserved_semantic_history` case.

Do NOT simply relabel a degraded state as fresh.

If the current reason `deterministic_refresh_preserved_semantic_history` is still legitimately required after the race is fixed, keep it and explain why.

If a full rebuild is provably computed from the exact current material source state and current contracts consider that fresh, the receipt should reflect that exact fact.

### D. Preserve current translation behavior

PR #125 behavior must remain intact:

- unresolved Russian translations alone do not block visual build/deploy;
- invalid/stale/wrong-AppID/non-Russian masquerading still fails closed;
- translation Statistics block remains;
- translation attempt/success timestamps remain producer-owned;
- manual semantic-worker prompt remains available;
- no production translations are executed in this task.

### E. Preserve current semantic state

Do not:
- rerun or rewrite Fast results;
- rerun or rewrite Dossier results;
- rerun or rewrite Deep results;
- change Deep eligibility/order/attempt/recovery semantics;
- change ranking;
- change expired-sale logic;
- change Taste profile semantics;
- change any Scheduled Task.

Concurrent Dossier/Deep/translation production writes may continue. The fix must tolerate them correctly rather than serializing them.

## Required regressions

At minimum prove:

1. **Historical stale-race reproduction**
   - build from a fixture equivalent to old source state `53767218...` / PASS2 blob `4435430...`;
   - move candidate parent to state equivalent to `dede9ea...` / PASS2 blob `b1967e42...`;
   - assert that a final visual cannot have the newer parent while retaining the old PASS2/source binding and old derived Statistics.

2. **No material drift**
   - `main` moves for an unrelated file/write while all material visual source identities remain equal;
   - valid generated payload is not rejected merely because repository HEAD changed.

3. **Material drift**
   - one relevant semantic/control-plane source blob changes;
   - stale generated payload is rebuilt or rejected before canonical persistence.

4. **Concurrent Dossier/Deep write**
   - a legitimate semantic-state advance during visual build cannot produce a mixed-parent/mixed-source visual.

5. **Freshness receipt**
   - the receipt accurately classifies fresh, degraded/no-fresh-build, or aborted-on-drift outcomes;
   - green workflow status alone is never the only freshness proof.

6. **Canonical visual preservation on failure**
   - if a drift-triggered rebuild cannot complete, the prior good `data/production/visual/current.json` remains unchanged.

7. **Translation regression**
   - unresolved translation remains publication-nonblocking exactly as PR #125 defines;
   - invalid masquerading Russian remains blocking/fail-closed.

8. Existing Progressive/Dossier/Deep/ranking/expiry/translation validation suites remain green.

9. No new scheduler/queue/retry owner is introduced.

## Production acceptance

After merge, use the normal GitHub-owned visual build/deploy path.

Acceptance requires:

- a post-merge full visual run exercising the corrected persistence path;
- exact source-binding proof for the persisted canonical visual;
- no mixed-parent/mixed-source condition;
- if Pages deploy occurs, the deployed `web/data/current.json` must equal the accepted canonical `data/production/visual/current.json`;
- the freshness receipt must truthfully describe the outcome.

If live production state changes concurrently, preserve newer Dossier/Deep/translation/production truth. Never reset or overwrite it with task fixtures or stale generated state.

Do not manually trigger or modify any ChatGPT Scheduled Task.

## Hard prohibitions

Do not:
- rebase an already-generated visual onto changed material source state without rebuilding;
- weaken source/provenance validation;
- use browser-side recounting as a workaround;
- freeze Dossier or Deep to make visual build easier;
- add a new queue/scheduler/retry loop;
- change semantic worker prompts unrelated to visual persistence;
- rewrite accepted semantic history;
- mark stale/degraded data fresh merely to make the UI look healthy;
- reopen PR #121 expiry logic or PR #125 translation semantics unless a regression proves this task broke them.

## Delivery

Implement on a dedicated branch/PR according to current worker protocol.

Before merge:
- reconcile with fresh `main`;
- preserve all concurrent production/Dossier/Deep/translation writes;
- run required focused and existing validations;
- merge only if clean and current worker protocol permits it.

Write:
`reviews/worker_reports/visual-stale-snapshot-rebase-race-fix-01.md`

Required report sections:
1. `Task`
2. `Architecture preflight`
3. `Verified current persistence path`
4. `Source binding model`
5. `Changes`
6. `Race regression`
7. `Freshness classification`
8. `Validation`
9. `Production acceptance`
10. `Unresolved`
11. `Status`
12. exact PR/commit/run/artifact refs
13. `Recommended next step` — exactly one bounded next step
14. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another project task after this one.

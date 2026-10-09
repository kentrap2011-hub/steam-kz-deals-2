# WORKER TASK — Inactive fully-async Dossier Research semantic worker 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Task ID: `dossier-async-research-semantic-worker-implement-01`
Physical developer slot: **ЧАТ 1 — NEW conversation**
Mode: **IMPLEMENT INACTIVE / OFFLINE VALIDATE**

## Goal

Implement the **inactive** Research semantic-worker entry prompt and the minimal bounded implementation/validation needed to produce exactly one immutable Research package for each GitHub-preauthorized item, in frozen manifest order. This is an implementation task, **not** authorization to run research on real current games or activate the two-stage production path.

Previous authority: PR #179, report `reviews/worker_reports/dossier-fully-async-pipeline-01.md`, and the current fully-async V2 contracts.

## START / ownership / interfaces

1. Read current `CHAT_PROTOCOL.md` and complete START gate, then read current `CHAT_CONTEXT.md` and this task file **fully** from `main`.
2. Work in this repository only; if any GitHub tool opens another repository, stop and switch back. Do not touch the `stopgame-ratings-data` repository.
3. Architecture preflight before changing any responsibilities. GitHub alone owns finite work authorization, ordering, immutable frozen bindings, validation, final acceptance, retry/recovery, and current canonical one-stage Dossier.
4. Read the **relevant sections only** of `PROJECT_ROUTES.md`, `config/execution_ownership_contract.json`, `config/dossier_two_stage_interfaces_contract.json`, `config/dossier_two_stage_staging_contract.json`, `config/dossier_two_stage_async_buffer_contract.json`; then exact Research package schema `config/dossier_research_package_v1.schema.json`, canonical privacy/evidence rules, and applicable P2/offline helpers. No repository-wide discovery.

## Required implementation

- Deliver a versioned **inactive Research semantic-worker prompt** (suggested path `config/dossier_two_stage_research_semantic_worker_prompt.md`) with strict immutable-authority entry checks and exact result-path construction. Implement only the small Research-specific supporting code/contracts required by that prompt; reuse existing P2 GitHub validation and frozen-manifest helpers where possible.
- Accept only **GitHub-prepared frozen Research manifest** and its actual single-parent start marker. Bind every item to exact original assignment, manifest/blob, snapshot, group, item index, AppID/title, web-evidence/Research schema and prompt hashes; fail closed on any mismatch. Never self-issue a marker, lease or new authorization.
- Traverse the entire finite manifest **in exact original order**, without requiring GitHub acknowledgement, prior-item Research acceptance, sibling completion, unresolved-slot release or fixed buffer capacity. No self-chosen items, retries, reordering, manifest extension, polling for acceptance, or daily quota.
- One exact-product, profile-blind Research package per item; use `DOSSIER-RESEARCH-PACKAGE-V1` and existing strict source/provenance/privacy rules. Cover the twelve dimensions without inventing evidence, source dates, author identity, quotations or source independence. Prefer evidence completeness to speed.
- Immutable **create-only** Research transport at the GitHub-authorized path `data/ai_inbox/dossier_research/{snapshot_id}/g{sequence:06d}/{appid}--{assignment_id}.json`. Preserve exact original byte/blob/hash and first-parent marker provenance for later Assembly and GitHub verification. Existing identical transport means submitted, **not** GitHub accepted; never overwrite/rename/rebind it. Collisions, stale authority, missing scope, and tool failure must fail closed with accurate item diagnostics and no fabricated success.
- One invalid or incomplete game must not prevent the next independently preauthorized game. Do not turn an unresolved sibling into a global wait gate. Only GitHub may later accept/reject or authorize recovery.
- Keep stage gates `active=false`, `authorized_for_semantic_execution=false`, `executable_in_production=false`; don't set `semantic_workers_implemented=true` globally based on Research alone. Offline/inert implementation may exist behind these gates.

## Concurrent work boundary

ЧАТ 2 independently implements the **inactive Assembly** worker. Do not edit its prompt, candidate schema, Assembly-owned helpers or its task/report. Avoid shared ownership/contract rewrites; if a genuinely necessary shared interface change is discovered, report the exact conflict rather than silently racing a parallel PR. Do not perform Assembly semantic execution.

## Verification / deliverables

- Add isolated offline tests (use disposable Git history and local fixtures **only**, never test production data): 12+ frozen items exceeding old eight-slot barrier; no prior-item acknowledgements; exact ordering; valid identity/source schema; duplicate and tampered transport; stale/mismatched marker/blob/prompt; local item failure without sibling blocking; no invented retry/lease; inactive guards.
- Validate tests relevant to Research plus existing P1/P2/async regressions and execution ownership where applicable. CI must not run real semantic processing or mutate canonical production.
- Produce report `reviews/worker_reports/dossier-async-research-semantic-worker-implement-01.md`: changed paths, exact checks/results, remaining integration blockers, invariant proof and PR link.
- Use a new focused implementation branch and PR against latest `main`; **do not merge your own PR**. Handle `CURRENT_TASK.md` non-destructively; no other workstream may be erased.

## Hard prohibitions

No real research run, no test records in production, no current one-stage worker/cache/queue/strict final validator changes; no Dossier or Deep cutover, ranking, website/Steam/translation changes, unrelated repos, secrets or `manual-shell-write.yml`. Do **not** create, change, run, disable or reconfigure Scheduled Tasks or automations.

## Finish

Stop at inactive, PR-tested implementation. GitHub remains the only eventual strict final canonical acceptance authority (including atomic original three-game group). Next step belongs to Director: review this PR and integrate with independently developed Assembly only after separate authorization.

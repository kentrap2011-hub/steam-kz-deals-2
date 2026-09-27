# WORKER TASK — DEEP VISUAL AUTHORITATIVE BINDING FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or the target is ambiguous, stop and switch first;
- do not use another repository.

Task ID: `deep-visual-authoritative-binding-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/deep-visual-authoritative-binding-fix-01.md`

## Goal

Repair the already-proven visual publication defect so current authoritative Deep/PASS 2 results are accepted by the GitHub-owned visual producer and current Deep statistics can be persisted and deployed.

Accepted diagnostic:
`reviews/worker_reports/deep-visual-statistics-staleness-diagnostic-01.md`

The accepted diagnosis proved:
- canonical Deep is advancing and accepted Deep results exist;
- PASS 2 ingest correctly triggers the existing visual rebuild;
- PASS 2 provenance mismatch correctly requires a fresh build;
- the full visual builder reads/projects current Deep correctly;
- publication fails in `scripts/grounded_negative_visual.py::apply_to_document()` because its current personalized-binding guard recognizes compatible cache/Fast but omits trustworthy authoritative `progressive_pass2`;
- builds then fail with `personalized card binding is not current/INCLUDE`, leaving canonical visual and Pages stale.

Do not re-diagnose the whole pipeline unless fresh `main` contradicts this accepted report.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current `CHAT_CONTEXT.md`;
3. current top of `DIRECTOR_TASK_BOARD.md`;
4. relevant Progressive/visual route in `PROJECT_ROUTES.md`;
5. accepted diagnostic report above;
6. `config/execution_ownership_contract.json`;
7. `config/progressive_personalization_contract.json`;
8. only the exact producer/test files needed for the bounded fix.

## Architecture preflight

Before writes, confirm:
- GitHub owns Progressive projection, validation, persistence and publication;
- current completed Deep is authoritative under the canonical Progressive contract;
- browser remains read-only;
- the fix changes no scheduler, queue, retry loop, semantic scope, Dossier evidence semantics, Deep recovery semantics or Scheduled Task configuration.

## Required implementation

Implement the smallest correct change in the GitHub-owned visual producer guard so a trustworthy current authoritative PASS 2 result using `analysis_semantic_source='progressive_pass2'` satisfies the current personalized-binding requirement where appropriate.

Do not disable the guard.

Preserve rejection of stale, unbound, incomplete, incompatible or otherwise non-current personalized state.

Add focused regression coverage for at least:
1. `projection_status=ai_required` + current authoritative Deep `analyzed_fit` => valid current personalized binding and no erroneous RuntimeError;
2. authoritative Deep `analyzed_not_fit` remains handled consistently with current contract;
3. stale/non-current Deep does not bypass the guard;
4. existing Fast/cache behavior remains unchanged.

## End-to-end validation

After implementation:
- run the existing focused validation gates;
- merge only if clean/green;
- verify one successful full visual build on `main`;
- verify the following Pages deploy succeeds;
- inspect the deployed artifact and confirm Deep counters are no longer the old zero values and correspond to the then-current canonical Deep state/provenance.

Do not manually trigger or process Deep/Dossier/Fast semantic backlog for validation.

## Hard prohibitions

Do not:
- modify or diagnose Dossier production; user explicitly said Dossier does not need investigation;
- change Dossier state, Dossier semantics, Dossier recovery or Dossier Scheduled Task;
- change Deep semantic conclusions or recovery rules;
- move logic into the browser;
- add a scheduler, queue, retry loop or recurring stage;
- change any ChatGPT Scheduled Task;
- manually process production semantic backlog.

## Report

Write:
`reviews/worker_reports/deep-visual-authoritative-binding-fix-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Accepted root cause`
4. `Changes`
5. `Validation`
6. `Published result`
7. `Unresolved`
8. `Status`
9. `Recommended next step` — exactly one bounded next step
10. exact PR/commit/run/artifact refs
11. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another task after this one.

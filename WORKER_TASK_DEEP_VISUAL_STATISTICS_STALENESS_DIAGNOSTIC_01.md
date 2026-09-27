# WORKER TASK — DEEP VISUAL STATISTICS STALENESS DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or the target is ambiguous, stop and switch first;
- do not use another repository.

Task ID: `deep-visual-statistics-staleness-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/deep-visual-statistics-staleness-diagnostic-01.md`

## User-observed symptom

The site statistics still showed zero completed Deep analyses, while fresh canonical GitHub state already showed accepted Deep results.

Latest Director spot-check before this task observed:
- current Deep work scope around `410`;
- `deep_first_pass_attempted_count = 11`;
- `deep_authoritative_completed_count = 11`;
- `deep_completed_fit_count = 11`;
- `deep_completed_not_fit_count = 0`;
- `deep_incomplete_or_recovery_count = 0`;
- `deep_ready_or_pending_count = 19`;
- `deep_waiting_for_dossier_count = 380`.

The user's page at approximately the same period showed:
- total Deep scope `397`;
- completed `0`;
- fit `0`;
- not fit `0`;
- incomplete/recovery `0`;
- waiting for dossier `367`;
- ready/pending `30`;
- remaining `397`.

Treat both sets as observations to verify, not assumptions.

## Goal

Prove exactly where the Deep statistics become stale between canonical accepted Deep state and the browser-visible statistics.

This task is diagnosis only. Do not implement a fix.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully and create the required checklist.

Read minimally:
1. `CHAT_CONTEXT.md`;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. relevant Progressive/visual routes in `PROJECT_ROUTES.md`;
4. accepted report `reviews/worker_reports/dossier-visual-progress-refresh-fix-01.md` to reuse the already-proven visual publication route rather than rediscovering it;
5. current Deep canonical state/work;
6. current canonical visual artifact;
7. latest relevant visual-build/deploy run and deployed Pages artifact;
8. only the smallest additional workflow/producer files needed to prove the exact broken boundary.

Do not reconstruct unrelated history.

## Questions that must be answered

1. What are the current canonical Deep counts on fresh `main`?
2. What Deep counts are currently stamped into `data/production/visual/current.json`?
3. What Deep counts are present in the latest actually deployed `web/data/current.json` / Pages artifact?
4. Is the user's zero state explained by:
   - an old browser cache only;
   - a stale canonical visual artifact;
   - a visual artifact that is fresh but not deployed;
   - a missing visual rebuild trigger after accepted Deep results;
   - a provenance/freshness check that ignores Deep state;
   - another proven cause?
5. Does accepted Deep ingest currently trigger the same existing visual rebuild path automatically?
6. If the visual builder runs after Deep acceptance, does it read the latest canonical Deep state or preserve stale counters?
7. Is the site now already correct and the screenshot simply older than the latest deploy? If so, prove the deployment time/artifact and state this clearly.
8. If a repository defect exists, identify the smallest exact component that must change. Do not change it in this task.

## Important comparison

The earlier accepted Dossier statistics fix (PR #100) repaired:
- Dossier ingest -> visual rebuild activation;
- exact Dossier-work provenance binding.

Check whether Deep already has an equivalent correct path or whether its path differs.

Do not assume the Dossier fix should be copied. Prove the actual Deep path first.

## Hard prohibitions

Do not:
- modify source, workflow, runtime, contracts, visual data, Deep state, Dossier state or cache;
- run or modify any ChatGPT Scheduled Task;
- manually trigger Deep/Dossier/Fast semantic work;
- manually process backlog;
- alter browser/frontend code;
- merge/create an implementation PR.

The only allowed repository write is the report.

## Acceptance

The report must contain:
1. `Task`
2. `Verified facts`
3. `Exact stale boundary`
4. `Current canonical vs visual vs deployed counts`
5. `Cause`
6. `Changes` — report only
7. `Validation`
8. `Unresolved`
9. `Status`
10. `Recommended next step` — exactly one bounded next step
11. exact file/commit/run/artifact refs
12. `Efficiency / reusable lesson`

Allowed conclusion labels:
- `BROWSER_CACHE_ONLY`
- `CANONICAL_VISUAL_STALE`
- `DEPLOYED_VISUAL_STALE`
- `DEEP_VISUAL_REBUILD_TRIGGER_DEFECT`
- `DEEP_VISUAL_PROVENANCE_DEFECT`
- `OTHER_PROVEN_CAUSE`
- `UNDETERMINED`

Allowed final statuses:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another task after this one.

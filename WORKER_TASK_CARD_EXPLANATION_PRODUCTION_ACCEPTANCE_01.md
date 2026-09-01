# WORKER TASK — CHAT 2

Task ID: `card-explanation-production-acceptance-01`
Mode: `ACCEPTANCE / BOUNDED IMPLEMENT IF REQUIRED`
Report: `reviews/worker_reports/card-explanation-production-acceptance-01.md`

## Goal

Close the gap between the already-passing card-explanation code/runner sample and the **actual canonical production payload + deployed Pages UI**.

This task exists because `card-explanation-fix-01` passed its generated runner sample but the workflow later failed at an independent Russian-description gate, so the corrected visual payload was not proven to reach production/deploy.

Director evidence before this task:
- current `data/production/visual/current.json` latest commit is `24b2890d0c85b14213fd0b91256afcfb306eb01e` at `2026-09-01T08:20:42Z`, before the final card-explanation fix;
- therefore code/runner acceptance is not sufficient user-facing acceptance.

## Read first

- `reviews/worker_reports/card-explanation-fix-01.md`
- `reviews/worker_reports/ru-translation-runtime-acceptance-01.md`
- `CHAT_PROTOCOL.md`
- current `data/production/visual/current.json` metadata / latest commit
- `.github/workflows/build-daily-visual-payload.yml`
- `.github/workflows/deploy-visual.yml`
- relevant execution ownership contract
- relevant pitfall only if trigger matches

Do not repeat the explanation audit or redesign explanation policy.

## Required work

1. Confirm current production `data/production/visual/current.json` does or does not contain the fixed explanation behavior.
2. Identify the exact existing blocker preventing the fixed payload from being committed/deployed.
3. If the existing canonical Russian-description/runtime prerequisites are now satisfied, run the smallest supported existing build/deploy route and verify:
   - card explanation gates pass;
   - visual payload commit occurs;
   - Pages deploy succeeds;
   - deployed payload version is newer than the fix commits.
4. If the Russian-description gate is still blocked by existing scheduled-runtime work, stop and report `blocked`; do **not** weaken/bypass the gate and do not create a second scheduler.
5. Once production/deploy succeeds, inspect the deployed/generated payload for at least:
   - no old generic fallback `Игра прошла строгий вкусовой отбор...` in visible explanation output;
   - the previous personal-link violation remains closed;
   - no false visible risk filler reintroduced.
6. Mark the final result as `needs_user_verification` until the user checks the actual site/device.

## Hard boundaries

Do NOT:
- weaken the Russian-description quality gate;
- hand-edit production visual JSON;
- create a second scheduler/runtime/queue;
- redo card explanation design/audit;
- treat runner workspace output as production acceptance;
- claim completion before actual deploy and user-visible verification.

## Done when

Technical acceptance:
- canonical visual payload containing the fix is committed;
- Pages deployment containing that payload succeeds;
- deployed/generated output passes the explanation assertions.

Then status must be `needs_user_verification` until the user confirms the actual UI.

If canonical prerequisites still prevent production, status `blocked` with the exact existing blocker.

## Report format

Save:
`reviews/worker_reports/card-explanation-production-acceptance-01.md`

### Production state before
Current visual payload commit/time and whether it predates the fix.

### Canonical route
Exact build/deploy workflow refs.

### Validation
Exact runs/commits/deploy refs and generated/deployed output checks.

### User verification
What exact visible behavior the user should check on the site.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_verification`

### Recommended next step
One bounded next step only.
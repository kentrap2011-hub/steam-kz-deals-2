# ЧАТ 1 — ВОССТАНОВЛЕНИЕ АКТУАЛЬНОГО САЙТА И БЕСПЛАТНОЙ ИГРЫ

Task ID: `site-current-games-and-free-game-recovery-01`
Mode: `IMPLEMENT / END-TO-END PRODUCTION RECOVERY`

## User goal

The immediate priority is NOT Taste queue ordering.

Restore the real published site so it reflects the current canonical publishable game state, and ensure the current free-game item is present when canonical source/business rules say it should be present.

The user specifically reports that the free game is currently missing from the site.

## Known trigger/evidence

Taste ingest itself completed successfully:
- acceptance commit: `ddb1a51b8321997bbbb83505d69cfe4031758619`
- Taste receipt: `data/cache/taste_ingest_receipts/ba86bfdcf8365dfa0195.json`

Immediately afterward the downstream visual chain did not publish:
- `Build daily visual payload` run `34484781975` — `failure`
- `Deploy visual mailing` run `34484824317` — `skipped`

This downstream failure does not invalidate the accepted Taste results, but it is now the primary production problem.

## End-to-end objective

Do not stop after merely diagnosing the failed workflow if the repair is clearly within this authorized site/publication goal.

Complete the smallest safe end-to-end recovery needed to prove:
1. the visual/site build succeeds on current canonical state;
2. the published site is refreshed from that state;
3. all games that CURRENT canonical business/visibility rules require to be visible are actually represented on the published site;
4. the current free-game entry is included if it is currently active/eligible according to canonical source/business truth;
5. if any user-mentioned game is legitimately excluded by current canonical rules, identify that exact reason rather than forcing it onto the site;
6. no stale pre-fix visual payload is being served as if current.

Do not equate "10 Taste results were accepted historically" with "all 10 must necessarily be shown". Visibility must follow current canonical site/business rules. However, no eligible game may be missing merely because the visual/deploy pipeline is stale or broken.

## First action — REPORT FIRST

Create/update immediately:
`reviews/worker_reports/site-current-games-and-free-game-recovery-01.md`

Initial checkpoint must include:
- lifecycle `in_progress`;
- UTC;
- current live/site publication state if cheaply resolvable;
- known failed run IDs above;
- exact first investigation action.

## Required diagnosis

Start with run `34484781975`.

Find the first real failing job/step/invariant and record it before repair.
Classify root cause as:
- `root_cause_proven`,
- `likely_root_cause`, or
- `root_cause_unknown`.

Inspect only the directly involved workflow/config/code/data path needed to repair the current publication path.

Also determine the canonical source/status of the current free-game item and trace its route into the visual/site payload. Do not invent the free game from user wording; establish its exact canonical identity from project state.

## Authorized changes

You may make the smallest code/config/workflow/data-generation repair necessary for the current site/publication path, including directly involved visual/giveaway integration surfaces.

You may run focused tests and allow/trigger the normal production build/deploy route needed to verify the repair.

If a normal production workflow must be manually dispatched and the connected tool cannot create `workflow_dispatch`, do NOT fake it or rewrite unrelated files solely to trigger it. Record the exact required user action and stop at `waiting_user_dispatch` only if there is no safe automatic path from the authorized repair commit.

## Prohibited

Do NOT:
- alter Taste semantic results;
- manually edit Taste queue/cache/overlay;
- start new Taste game analysis;
- implement Taste age-ordering in this task;
- implement selective profile reevaluation;
- change the ChatGPT Scheduled Task;
- weaken business eligibility/visibility rules just to make items appear;
- manually hardcode a free game into the published site if the canonical pipeline is supposed to supply it;
- hide/ignore a failing invariant by bypassing validation.

## Validation required

At minimum prove:
1. root cause of run `34484781975` is recorded;
2. focused tests/checks for the repair pass;
3. current visual payload builds successfully from canonical state;
4. deployment/publication succeeds or, if external manual dispatch is the only blocker, exact safe dispatch step is documented;
5. published/live artifact is current, not stale;
6. current eligible free-game identity is present in the canonical visual payload and published site;
7. current eligible paid/other game entries expected by canonical publication rules are present;
8. no unrelated Taste/business semantics were changed;
9. no next Taste semantic batch was started.

If checking the real live site is technically possible, verify the actual published output rather than only repository files.

## Failure handling

If recovery fails, do not blindly retry production.
Self-diagnose in the same report:
- exact failed step;
- first real error;
- proven/likely/unknown root cause;
- what changed and what did not;
- whether the site is still stale;
- status of the free-game route;
- smallest next action;
- what was deliberately not attempted because unauthorized/impossible.

## Final statuses

Use one of:
- `complete_site_current_and_free_game_visible`
- `complete_site_current_free_game_legitimately_not_eligible`
- `waiting_user_dispatch`
- `failed_closed_root_cause_proven`
- `failed_closed_root_cause_unknown`
- `blocked_external`

## Final report

Final report path:
`reviews/worker_reports/site-current-games-and-free-game-recovery-01.md`

Include exact repair commit(s), build/deploy run IDs, published artifact/site proof, exact free-game identity/status, and whether Taste backlog work may resume.

Stop only after the end-to-end objective is either verified or a genuine external/authorization blocker is recorded. Do not start queue-ordering or new Taste analysis afterward.

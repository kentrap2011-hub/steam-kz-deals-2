# WORKER TASK — VISUAL FRESHNESS RELEASE 01

Task ID: `visual-freshness-release-01`
Mode: `IMPLEMENT / RELEASE`
Report: `reviews/worker_reports/visual-freshness-release-01.md`

## Source decision

This is a direct production continuation of the already accepted visual-freshness fix.

Accepted implementation:
- `reviews/worker_reports/visual-freshness-chain-fix-01.md`
- blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`

Final acceptance:
- `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`
- blob `6a691fb29d88b1785accf717752149e027265a2c`

Accepted branch:
`worker/visual-freshness-chain-fix-01`

Accepted branch head at acceptance:
`4080030e686d6b04fcc666069819aa46df18da7a`

Accepted workflow blobs:
- build: `b497093eef1f5dac0bfd5efd9d3ef69bb272cb67`
- deploy: `7479a56ac7ee363e6a212952e58f36558b371877`

System Audit 02 and Mobile Post-Incident Audit 01 both confirm:
- the fix is accepted and release-ready;
- production `main` still runs the old freshness behavior;
- the previous mobile incident blocker is gone;
- release priority is **now**.

## Goal

Release the already accepted visual-freshness branch to production `main` through the normal bounded path and capture one ordinary production build/deploy proving the accepted freshness receipt and exact triggering-run binding are actually active.

Do not redesign or extend the accepted fix.

## Required release procedure

1. Reconfirm only the minimum safe merge/release state:
   - accepted branch still exists;
   - no unresolved conflict with current `main` in the exact files being released;
   - no mobile-cache/Epic work is accidentally included.
2. Merge/rebase/cherry-pick only as needed to place the accepted visual-freshness implementation onto current `main` without altering its accepted semantics.
3. Run/use the canonical production build/deploy path.
4. Capture exact evidence that production now exercises:
   - build freshness receipt creation;
   - `fresh_build=true` only for a real fresh canonical build;
   - explicit `degraded/no_fresh_build` when no fresh build occurs;
   - deploy bound to the exact triggering workflow run/receipt;
   - stale/mismatched payload cannot silently pass as a fresh deploy.
5. Capture exact production refs/run IDs/conclusions.

## Critical boundaries

Do NOT:
- change mobile feed/cache behavior;
- add `tests/feed-bootstrap.test.js` to deploy in this task;
- fix Epic giveaways;
- change Taste/ranking/semantic policy;
- redesign workflows beyond what is required to land the already accepted branch;
- add another build/deploy workflow or ownership path;
- combine ITAD/IGDB work;
- claim success if the accepted receipt/binding mechanism is not actually active on `main`.

## Acceptance

The release is complete only if:
- accepted freshness implementation is on production `main`;
- canonical production build/deploy runs successfully or explicitly produces the accepted degraded classification where applicable;
- exact triggering-run/receipt binding is observable in the production run;
- no unrelated mobile/Epic/Taste changes are mixed into the release.

If current `main` drift makes the accepted branch unsafe to land without redesign, stop and report `blocked` rather than improvising.

## Required result

Report:
1. exact merge/release method;
2. exact production commit/ref;
3. exact workflow run IDs and conclusions;
4. exact freshness receipt classification/evidence;
5. exact deploy-to-triggering-run binding evidence;
6. confirmation that no unrelated task was mixed in;
7. whether production stale-success risk is now closed.

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`

## Completion

Save:
`reviews/worker_reports/visual-freshness-release-01.md`

Final answer must state exact report path, status and exact refs.
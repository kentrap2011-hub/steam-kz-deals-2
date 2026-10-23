# ЧАТ 4 — безопасное исправление управления проектом (этап А)

Task ID: `director-governance-safe-fixes-chat4-01`
Status: `implementation_draft_PR241_pending_independent_QA`
Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: main `44b7c4ac29dc088efb963c3133fdd92d16bd3a64` at branch creation
Implementation branch: `fix/director-governance-safe-fixes-chat4-01`
Implementation pre-report HEAD: `89d3e53ba67babcca6f0015fba3e38a066274ca3`
Final review HEAD: take unchanged SHA from PR #241 after this report commit; independent QA must pin exact SHA and successful CI.
Draft PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/241
Report: `reviews/worker_reports/director-governance-safe-fixes-chat4-01.md`

## Verified facts

1. START gate: current CHAT_PROTOCOL, DIRECTOR_PROTOCOL, CHAT_CONTEXT read. Existing `WORKER_TASK_DIRECTOR_GOVERNANCE_SAFE_FIXES_CHAT4_01.md` is registered in Board and `config/director_task_plan.json`, `status=active`, slot ЧАТ 4, current main after PR #240. Exact task scope: independent IMPLEMENT, draft PR and tests, no merge, Deploy, Research/Assembly, Scheduled Tasks or edits in PR #238/#239.
2. Deploy visual mailing https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39647198011 : push to `71d3bbca7c333f4fccd802f6127232f87f5e0a08`, job `119385778440`, conclusion failure. Receipt validator succeeded, visual mutation classification succeeded, Russian description diagnostic succeeded, giveaway validation succeeded and independent current-site status succeeded. `Run UI regressions` failed, so payload staging, task-page generation, upload and Pages Deploy were all skipped.
3. Error is proved against the **historical exact commit**, not guessed: `config/director_task_plan.json` at `71d3bbca7` had two completed records without `recent_completion` (`dossier-shadow-assembly-github-python-handoff-fix-01` and `dossier-shadow-assembly-pr230-security-review-01`) and one record `dossier-shadow-research-stage1-technical-boundary-audit-01` with `recent_completion: null`. The log shows `Unexpected/omitted task registry fields`, `KeyError: 'recent_completion'`, 4 test failures and 5 errors. This explains the first failed deploy step; it does not prove the freshness of the live Pages site.
4. **Already repaired before this work:** current main's 86 registry items have all 16 required keys, supported four statuses, boolean `recent_completion`, string `updated_at_utc` and string `blocker`. PR #240 HEAD `3f932898e3d2b861c03c7f5373ae96dd27b3ba23` has passing `Validate site task registry and page` run `39757762490`; no repeat data repair is necessary. This report does not claim that rerunning the old `71d3bbca7` action would succeed.
5. `main` GitHub branch metadata reports `protected=false`, `protection.enabled=false`, no required checks, and repository rulesets API returned empty list. Branch-protection details returned 403 (`Resource not accessible by integration`); the connected GitHub tool cannot configure protection through the available read/write endpoints.

## Changes (stage A only)

- `scripts/build_site_tasks.py`: keep exact same strict required-field contract; now include offending Task ID and sorted missing/extra fields in `ValueError`. No unsafe fallback/default supplied.
- `scripts/test_site_tasks.py`: five negative registration regressions: absent/null `recent_completion`, absent `updated_at_utc`, null `blocker`, unsupported status. No tests skipped or weakened.
- `.github/workflows/validate-site-tasks-page.yml`: all pull requests run the existing registry and task UI validation. Removed `paths` condition because a skipped conditional status is unsuitable as an always-required branch check. Additional PR CI use is the deliberate limited cost.
- `DIRECTOR_PROTOCOL.md`: current JSON registration + current PR/CI evidence, no duplicate assignment without an unresolved useful goal, coordinated Board/registry update, explicit success for exact-HEAD required checks, and `CURRENT_TASK.md` demoted to handoff (consistent with CHAT_CONTEXT).
- `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`: deleted obsolete global two-worker cap, use uniquely numbered free `ЧАТ N` under canonical Director protocol.
- `DIRECTOR_BOOTSTRAP.md`, `DIRECTOR_HANDOFF_CURRENT.md`: explicit historical-only notices and replacement of obsolete two-worker operating caps; no rewriting historical PR/report evidence.

## Validation and security boundaries

- Existing production control plane and canonical writer unchanged. No live workflow dispatch, Deploy, Research/Assembly, production or Scheduled Task.
- Prior main PR #240 registry/UI checks passed. The PR #241 **final HEAD** must pass `Validate site task registry and page / validate` and `Validate backlog dispositions` and any additional relevant PR CI. At report authoring, do not claim unfinished CI as success: use GitHub Actions exact-head results and independent reviewer.
- DO NOT bypass a red required check. Workflow YAML does not enforce merge protection on its own. Protected branch and required status checks need separate admin settings.
- Scope isolation: PR #238 and PR #239 branches and their code are unchanged. This PR does not take ownership of their QA or merge.

## Administrative GitHub setting required (NOT performed)

Repository **Settings → Rules → Rulesets → New branch ruleset** targeting `main` (or **Settings → Branches → Add branch protection rule**, if that UI is available):
1. Require a pull request before merging and at least one independent review; avoid self-approval. Require a fresh approval when the reviewed head changes if available.
2. Require status checks to pass before merging. Choose the existing GitHub Actions check produced by workflow `Validate site task registry and page`, job `validate` (UI may display `Validate site task registry and page / validate`). After the workflow has run on a PR, select the exact advertised check. Add other checks as required by affected code contracts rather than pretending these two are exhaustive.
3. Protect against direct pushes, force-push and deletions; apply to administrators and avoid unrestricted bypass. Verify ruleset actually shows as active and test blocked merge on a deliberately failing **synthetic PR** only with separate authorization; do not run live Deploy.
4. Check that each required CI name appears on **every PR**, not only path-filtered ones. If ruleset/branch protection unavailable on the GitHub plan or connection, do not claim enforcement; enforce procedural no-merge until settings can be activated.

## Proposed stage B — design only (no implementation or new registry)

**Single current task identity remains `config/director_task_plan.json`.** Each active task has immutable ID and task file. Use GitHub PR metadata / exact HEAD / CI / worker-report for verified execution status; Board holds only human decisions not inferable from GitHub (physical `ЧАТ N` correspondence, NEW/EXISTING/retired, explicit permission, conditional user verification). Avoid duplicating current execution status in a second JSON file.

A future bounded implementation can produce **derived**, never manually maintained, compact Director status/handoff and site task view from plan + scoped PR metadata + a short Board section with human-only assertions. Archived Board sections, `CURRENT_TASK.md` and dated bootstrap remain searchable evidence but not live status. Current canonical contract and GitHub exact artifacts override prose. Ensure generation failure is isolated from verified paid-game publication per separate PR #238; do not take over that PR here.

Proposed small current view: (1) task ID and goal; (2) `ЧАТ N` and physical NEW/EXISTING/retired only where proven; (3) status from registry plus PR number/HEAD/CI from GitHub; (4) dependencies, blocker, next user decision; (5) last verified UTC and provenance. Produce one compact current table on demand instead of appending unbounded historical sections. No new scheduler, retry owner, semantic stage, production coupling or writable second registry.

Transition only after #238/#239 proceed independently and after separate user-approved next-stage task with a migration/compatibility check. Keep old UI/Task ID URLs stable; test derived view against existing 86 records and existing dependency gates. Do not silently mark physical chats active based merely on a planned JSON slot.

## Unresolved / recommended next step

1. Independent QA of PR #241 at its exact final HEAD, with CI, no self-merge. Record any uncovered issues in PR.
2. Director/user administrator configures mandatory GitHub protection for `main`. Until then green CI is procedural, not technically enforced.
3. Later, if needed and separately authorized, implement the limited stage-B derived compact view; do not create another ledger.
4. No live Pages freshness proof was performed; it belongs to the dedicated site publication PR #238 scope.

Efficiency/reusable lesson: The old #39647198011 log named no offending Task ID; precise validator errors and existing PR-wide CI reduce repeated GitHub history and manual troubleshooting. Preserve strict failure rather than silently normalizing records.

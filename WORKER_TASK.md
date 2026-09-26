# WORKER TASK — TASTE DOSSIER PRODUCTION FAILURE DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2` for this task;
- do not search, read, modify, or use another repository;
- if GitHub/tool opens another repository by default or the target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-production-failure-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/taste-dossier-production-failure-diagnostic-01.md`

CURRENT_TASK.md:
- do not modify.

## Goal

Establish the exact root causes of two production failures exposed by the first Dossier group under the newly accepted pragmatic evidence model.

Do not implement a fix in this task. Diagnose, prove, and recommend the smallest safe fix for a later separately authorized IMPLEMENT task.

## Production case

Snapshot:
`b98f8691529d9c4d1bdf66227f08537fbb5dd385ba8798280da05aa98f4054d5`

Group:
- sequence: `1`
- group SHA-256: `9299039791406b032d652da85c685c8868e4dcaba808168f67c68b6fe5b709b0`
- games: Crown Trick / appid 1000010; Tiny Snow / appid 1002560; EARTH DEFENSE FORCE 5 / appid 1007040
- candidate create commit: `2a3a2e2dbd99faf784f22878f0b7ec2252d1f5fa`
- candidate path:
  `data/ai_inbox/taste_steam_review_dossiers/b98f8691529d9c4d1bdf66227f08537fbb5dd385ba8798280da05aa98f4054d5--g000001--9299039791406b032d652da85c685c8868e4dcaba808168f67c68b6fe5b709b0.json`

GitHub ingest workflow:
- workflow: `Ingest Steam review dossier checkpoint`
- run id: `36241650284`
- job id observed by Director: `108403182115`

Observed facts from the run:
- group 1 was locally classified failed;
- `accepted_group_count_this_run: 0`;
- `failed_group_count_this_run: 1`;
- `failed_dossier_count: 3`;
- local commit `Drain and validate Steam review dossier buffer` was created;
- publication to main then failed with:
  `error: cannot rebase: You have unstaged changes.`
- because the workflow failed before pushing, current main may still show stale pending/validation state. Treat current GitHub truth and the failed run log separately and explicitly.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Read current, minimally:
- `CHAT_CONTEXT.md`
- `DIRECTOR_TASK_BOARD.md`
- `DIRECTOR_PROTOCOL.md` only if required by CHAT_PROTOCOL
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- current Dossier contract, worker prompt, web-evidence contract and schema
- current strict/prepublication/buffered/ingest/worker-projection code relevant to the two failures
- `reviews/worker_reports/taste-dossier-pragmatic-evidence-model-fix-01.md`
- the exact candidate artifact and exact failed workflow run/logs above.

Do not perform broad repository archaeology.

## Architecture / ownership boundary

This is diagnosis only.

Preserve and verify:
- GitHub remains Dossier control plane;
- Scheduled ChatGPT remains bounded semantic/data producer;
- no Scheduled Task action;
- no manual Dossier recovery;
- no manual Tiny Snow rerun;
- no Deep recovery;
- no manual backlog processing;
- no source/runtime/workflow/contract changes;
- no production artifact rewrite;
- only the durable report may be committed by this task.

If the recommended future fix would change source/runtime/workflow/checkpoint/ownership behavior, include the required architecture preflight analysis in the report, but do not implement it.

## Investigation A — freshness contradiction

Observed candidate problem:

At least one Tiny Snow player-feedback source was serialized with `freshness:"recent"` while one or more concrete bound feedback records under that source had known publication dates older than the canonical 365-day boundary relative to `generated_at_utc`.

The strict validator already contains the rule that an old dated feedback record cannot inherit a recent parent-source freshness classification.

Determine exactly:

1. Which exact source/feedback record(s) caused the strict failure.
2. The exact validator error text and code path.
3. Why the worker was able to construct and publish the contradictory candidate despite the rule already existing.
4. Whether the gap is in:
   - worker prompt compliance only;
   - prepublication validation coverage;
   - candidate-generation path;
   - validator invocation/order;
   - or a combination.
5. Whether the worker performed any machine validation before create-file and, if so, why that validation did not stop this candidate.
6. The smallest machine-enforced future barrier that would make this class of contradiction impossible to publish:
   - it must not rely on "remembering" the rule;
   - it must evaluate known child feedback dates against parent freshness/current-state classification before create-file;
   - it must preserve the allowed undated path without inventing dates.
7. Exact focused regression(s) needed for a future implementation.

Do not weaken the 365-day rule.

## Investigation B — uncommitted changes before rebase

The ingest workflow created its local canonical-state commit and then failed because Git reported unstaged changes before rebase.

Do not guess which file caused it.

Reproduce the workflow path safely from the exact relevant repository state in an isolated/local test environment, without pushing production state.

Run the same material steps in order and record `git status --porcelain` and relevant `git diff` after each step, especially:
- after recovery step;
- after buffered drain/classification;
- after validation-status generation;
- after PASS 2 eligibility regeneration;
- after the workflow's current `git add`;
- immediately after the local commit;
- immediately before the attempted rebase.

Prove:

1. Exact unstaged path(s).
2. Exact step/function that creates or modifies each path.
3. Why the workflow's current staging list does not include it.
4. Whether the file is intended canonical output, temporary output, or accidental side effect.
5. Why existing tests failed to catch this.
6. Whether the failure requires concurrent movement of `main` to surface, or can occur deterministically on a clean isolated reproduction.
7. The smallest safe future fix:
   - stage the missing intended path;
   - stop generating it there;
   - move its generation before/after the commit;
   - or another proven correction.
8. Focused regression needed to guarantee a clean worktree before rebase/push.

The report must include the exact observed `git status --porcelain` evidence. Do not conclude the root cause until the concrete path is proven.

## Cross-check

Determine whether Investigation A and Investigation B are independent defects or causally linked.

Also state clearly:
- whether the substantive Dossier candidate was rejected for a real semantic/temporal reason;
- whether the later Git failure merely prevented that already-determined state from reaching main;
- whether any current main state is stale because of the failed publication.

Do not repair or recover the group.

## Done criteria

The task is complete only when:

- exact freshness failure is reproduced/proven;
- exact reason it escaped prepublication is proven;
- a machine-enforced prevention point is identified;
- exact unstaged file(s) are reproduced/proven;
- exact creator step and staging omission are proven;
- the relationship between the two defects is classified;
- minimal future fixes and focused regressions are specified without implementing them;
- no Scheduled Task, recovery, backlog, production state, source, workflow, contract, or runtime is modified.

## Durable report

Commit only:
`reviews/worker_reports/taste-dossier-production-failure-diagnostic-01.md`

Required sections:
1. Final status
2. Sources / exact production refs
3. Freshness failure — reproduced facts
4. Freshness escape path — exact root cause
5. Machine-enforced prevention point
6. Rebase failure — exact reproduction
7. Exact unstaged paths and creator step
8. Why staging/tests missed it
9. Relationship between the two defects
10. Minimal future fixes
11. Required regression tests
12. Architecture/ownership preflight for the proposed future fix
13. Production state / stale-state implications
14. Unresolved
15. Director recommendation

Allowed final statuses:
- `complete_root_cause_proven`
- `blocked`
- `needs_user_decision`

Before completion:
- commit the durable report to `main`;
- reread that exact committed report from fresh `main`;
- make no further task-owned changes after that reread.

Expected next step after this task:
- Director reviews the diagnostic report and asks the user for separate authorization before any IMPLEMENT task.

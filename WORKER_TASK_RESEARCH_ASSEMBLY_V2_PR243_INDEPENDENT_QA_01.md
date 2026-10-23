# ЧАТ 2 — independent exact-HEAD QA of inactive V2 PR #243

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: research-assembly-v2-pr243-independent-qa-01
Worker slot: ЧАТ 2 (НОВЫЙ физический чат, independent of ЧАТ 1)
Mode: READ-ONLY / INDEPENDENT QA of PR #243, except own report-only draft PR and review comment on target PR
Report: reviews/worker_reports/research-assembly-v2-pr243-independent-qa-01.md

## START and registration authority

Before all task-specific work, fully read current `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md` from main and execute START gate and architecture preflight. Read `DIRECTOR_PROTOCOL.md`, relevant `PROJECT_ROUTES.md`, this registered task from main, matching Task ID/slot in `config/director_task_plan.json` and `DIRECTOR_TASK_BOARD.md`, and verify the director registration PR is merged and its required CI successful in main. Restrict ALL tools and source inspection to `kentrap2011-hub/steam-kz-deals-2`; stop if another repository opens. This message alone is not authority unless task, registry, Board and merge/CI agree.

## Exact review target and boundary

Developer: ЧАТ 1. Target: draft [PR #243](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/243), preliminary known HEAD `7765083edfff0802026f1f16b663cef3518c7ed7` (re-read live HEAD and re-evaluate if it changed). Base: merged main `e9d9fd64986ada2e26a5ea1dea95298f98b1ae3e`. Original task: `WORKER_TASK_RESEARCH_ASSEMBLY_V2_SAFE_USE_READINESS_01.md`; worker report: `reviews/worker_reports/research-assembly-v2-safe-use-readiness-01.md` in the PR branch. The observed three exact-HEAD workflows `Validate inactive Research Notes V2 and autonomous Assembly`, `Validate site task registry and page`, `Validate backlog dispositions` were successful on this preliminary head, but must be checked again on final review HEAD; previous red CI for 34/35 tests is historical.

Review only the actual PR changes and their immediate relevant contracts, including `scripts/dossier_research_notes_v2.py`, `scripts/test_dossier_research_notes_v2.py`, and the dedicated worker report. Independently assess claims, don't merely summarize developer report. PR #232 historical V1 remains CHANGES_REQUIRED and out of scope.

## Required independent checks

1. Compare exact PR #243 final HEAD diff/file list to main and original task, and evidence that the four inactive V2 activation flags remain false; no execution, real trial marker, semantic Research/Assembly, production, live publication, workflow dispatch, scheduler, original trial or PR #232 modification.
2. Check immutable Git proof against disposable repository changes: original manifest, run marker and Research/Assembly single-add-introduction commits; first-parent path history catches byte-perfect revert; no bypass via path ancestry/commit selection/HEAD races; frozen binding and exact original 18/six fixed triples remain untouched.
3. Check independently the new Assembly transport revalidation on stale/forged work/Research, distinction of missing vs invalid and no fabricated attempts, original ordered typed publication with two sequential candidate submissions, previous candidate state after ready list shrinks, and no order-skipping. Check precisely whether the new V2 helper actually protects a real runtime path; do not misrepresent offline test-only guards as integrated.
4. Verify reviewer A/B/C independence and honest absence of authenticated real GitHub appointment verification. Check item receipt phase/disposition consistency, safety, correctness for absent source/zero-source Notes, SULFUR substantive role conflict, Sifu hostname and original-work-year conflict, four historical missing packages, strict final Dossier V2 and 3-item atomic gate.
5. Check exact-head GitHub CI and test coverage (prefer independent disposable Git reproduction where possible); look for a real bypass/false-positive case, not only green-check counts. Separate `code acceptable for inactive merge` from `ready to start live trial`. If an evidence gap requires a new source patch or canonical architecture authority, report it as a bounded blocker.

## Output / verdict

Write one independent concise report at `reviews/worker_reports/research-assembly-v2-pr243-independent-qa-01.md` in a separate report-only DRAFT PR, if GitHub reporting is available; never edit code or PR #243 branch. Post precise review verdict and report link in PR #243 Conversation, using one of: `PASS_FOR_DIRECTOR_MERGE_REVIEW`, `CHANGES_REQUIRED`, `BLOCKED_EVIDENCE`. Include target exact HEAD, checked CI runs, confirmed facts vs unknown, adversarial test gaps, no-live-authority conclusion, recommended one next step. If target HEAD moves before report, re-run exact-HEAD review or mark prior verdict invalid; if no ability to comment, disclose this and still save report.

No QA self-merge, no unrelated source/runtime edits, no source acceptance claims without independent proof, no real Research/Assembly or production/Deploy, no Scheduled Tasks, no human reviewer appointments. Director alone decides whether PR #243 can merge after a PASS verdict; a merge would still leave V2 inactive.

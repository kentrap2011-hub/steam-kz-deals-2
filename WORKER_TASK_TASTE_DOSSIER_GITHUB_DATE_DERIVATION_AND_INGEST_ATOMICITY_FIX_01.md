# WORKER TASK — TASTE DOSSIER GITHUB DATE DERIVATION AND INGEST ATOMICITY FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2` for this task;
- do not search, read, modify, or use another repository;
- if GitHub/tool opens another repository by default or the target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-github-date-derivation-and-ingest-atomicity-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/taste-dossier-github-date-derivation-and-ingest-atomicity-fix-01.md`

## User-approved decisions

The user explicitly approved both changes below.

### Decision A — ChatGPT no longer decides "fresh / old"

Do not add another prompt-memory rule or another semantic self-check to make ChatGPT remember the one-year rule.

Instead simplify the responsibility split:

- the semantic worker records concrete publication dates when known;
- if a date is genuinely unknown, it records `null`;
- the semantic worker must not be responsible for deciding whether a dated review/source is `recent` or `older`;
- GitHub deterministically derives temporal classification from the dates under the canonical 365-day rule;
- unknown date must remain unknown and must never be promoted to recent merely because the page is accessible now;
- unknown temporal evidence cannot satisfy a rule that specifically requires recent evidence;
- do not weaken current-state / temporal completeness semantics.

The implementation should remove redundant worker judgment rather than add a second "remember to check age" layer.

### Decision B — failed-group audit/quarantine remain correct, saving them must be reliable

The failed-group audit record and quarantine copy are intentional canonical outputs and must remain.

Fix the GitHub workflow so:
- absence of one optional path cannot prevent other intended changed paths from being staged;
- staging errors are not silently hidden;
- after the local canonical commit, the worktree must be proven clean before rebase/push;
- if anything remains modified/untracked, the workflow must stop and print the exact paths rather than continue;
- no intended audit/quarantine output may be silently omitted from the canonical commit.

## Triggering diagnostic

Read:
`reviews/worker_reports/taste-dossier-production-failure-diagnostic-01.md`

Accepted root causes:

1. Tiny Snow / appid 1002560 candidate contained temporal contradictions even though the strict 365-day validator rule was correct.
2. The Scheduled worker was the component choosing/persisting `freshness`, while canonical validation happened only after create-only publication.
3. The user does NOT want to solve that by adding another pre-create validation layer to ChatGPT.
4. In ingest run `36241650284`, failed-group classification correctly created:
   - modified `data/audit/taste_steam_review_dossier_group_failures.jsonl`;
   - a new deterministic failed-group quarantine artifact under `data/quarantine/taste_steam_review_dossier_inbox/failed_group/...`.
5. The workflow then ran:
   `git add -A -- data/control data/quarantine data/audit 2>/dev/null || true`
6. Because optional `data/control` did not exist, that command failed as a whole; the failure was suppressed; audit/quarantine remained unstaged; rebase then failed on a dirty worktree.

Production refs:
- snapshot: `b98f8691529d9c4d1bdf66227f08537fbb5dd385ba8798280da05aa98f4054d5`
- sequence: `1`
- group SHA-256: `9299039791406b032d652da85c685c8868e4dcaba808168f67c68b6fe5b709b0`
- candidate create commit: `2a3a2e2dbd99faf784f22878f0b7ec2252d1f5fa`
- failed ingest run: `36241650284`

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Read current, minimally:
- `CHAT_CONTEXT.md`
- `DIRECTOR_TASK_BOARD.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- current Dossier contract/schema/worker prompt/web-evidence contract
- current strict / buffered / ingest / worker-projection / prepublication code needed for this task
- ingest workflow
- focused Dossier temporal and canonical-writer tests
- `reviews/worker_reports/taste-dossier-production-failure-diagnostic-01.md`
- `reviews/worker_reports/taste-dossier-pragmatic-evidence-model-fix-01.md`

Do not perform broad repository archaeology.

## Architecture preflight

Before source/workflow writes prove and preserve:

1. GitHub remains control plane for deterministic transformations, temporal classification, strict validation, canonical persistence, failed-group quarantine, audit, recovery eligibility and completeness.
2. Scheduled ChatGPT remains only bounded semantic/evidence collection and create-only candidate transport.
3. Moving "recent/older" derivation from ChatGPT to GitHub is a move toward the existing ownership contract, not away from it.
4. Do not create a new scheduler, queue, retry loop, crawler, backlog manager, or second canonical validator.
5. Do not add a new semantic prepublication gate owned by ChatGPT.
6. Do not alter the 365-day rule.
7. Do not alter TASTE-012 temporal completeness semantics except where needed to make temporal classification GitHub-derived.
8. Do not weaken exact-product identity, TASTE-014 bounded retrieval, TASTE-015 coverage sufficiency, privacy, or pragmatic evidence modes.
9. No Scheduled Task action is authorized.
10. No manual Dossier recovery / Tiny Snow rerun / Deep recovery / backlog processing is authorized.

If the canonical contracts currently assign derived freshness to ChatGPT, update those contracts first/with the implementation so ownership is unambiguous.

## IMPLEMENT A — GitHub-derived temporal classification

### A1. Remove worker-owned freshness judgment

The active worker instructions and candidate contract must no longer require ChatGPT to decide whether dated evidence is `recent` or `older`.

The semantic worker should provide factual temporal inputs only:
- `publication_date: YYYY-MM-DD` when actually known;
- `publication_date: null` when genuinely unknown.

Do not tell ChatGPT to calculate age in days or choose the final freshness classification.

### A2. GitHub derives the classification deterministically

Use the canonical generated-at/reference date and the existing threshold:
- age <= 365 days => recent;
- age > 365 days => older;
- unknown date => unknown/undated; never infer recent merely from current page accessibility.

Choose the smallest coherent representation.

Preferred design:
- transport/candidate carries factual dates;
- GitHub normalization/validation derives effective temporal state before canonical persistence/use.

It is acceptable for the canonical persisted Dossier to retain a derived freshness field for downstream compatibility, but if retained it must be GitHub-computed, not worker-authored.

Do not duplicate the 365-day calculation in multiple independent implementations. Centralize the deterministic calculation in one canonical helper and reuse it.

### A3. Parent/child temporal coherence

The model must handle the case that caused Tiny Snow:

- a collection/page itself may be undated;
- individual bound feedback records may have known dates;
- known old feedback cannot become recent because the parent page is undated or currently reachable;
- if different feedback records under one source have different dates, temporal qualification of an observation must be based on the actual supporting dated records, not a guessed page-wide "recent" label.

If this requires reducing or removing source-level `freshness` as an authoritative field, do so cleanly rather than preserve a misleading field.

### A4. Current-state evidence

Preserve fail-closed semantics:

- current bugs/performance/compatibility/localization/regional state that requires recent support must be backed by evidence whose date GitHub can deterministically classify as recent;
- an unknown date does not count as recent;
- old evidence may still support durable/historical observations where allowed;
- historical/recent conflict behavior remains as currently intended.

### A5. Candidate compatibility / migration

Handle schema/binding revision explicitly if required.

Do not rewrite historical accepted Dossiers manually.

Do not silently reinterpret an old candidate under a new incompatible binding.

Normal GitHub-owned rebuild/refresh semantics remain authoritative.

### A6. Regressions

At minimum prove:

- DATE-01 known date exactly 365 days old => recent;
- DATE-02 known date 366 days old => older;
- DATE-03 unknown date => unknown/undated, never recent;
- DATE-04 undated parent + old dated child => child remains old;
- DATE-05 undated parent + recent dated child => child may satisfy recent support;
- DATE-06 mixed old/recent children under one source are classified per supporting record and do not inherit one guessed parent freshness;
- DATE-07 unknown child cannot satisfy current-state recent-support requirement;
- DATE-08 worker candidate no longer has to choose/compute recent-vs-older;
- DATE-09 GitHub canonical output/downstream semantics receive the deterministic derived state they require;
- DATE-10 existing TASTE-012 temporal behavior remains strict.

Use the existing Tiny Snow shape as a focused regression, but do not rerun production Tiny Snow.

## IMPLEMENT B — reliable canonical staging of failed-group outputs

### B1. Fix optional-path staging

Replace the current failure-prone pattern:

`git add -A -- data/control data/quarantine data/audit 2>/dev/null || true`

with a form where:
- each optional path is handled independently;
- absence of `data/control` does not prevent `data/quarantine` and `data/audit` from being staged;
- unexpected staging errors are visible and fail the workflow;
- do not broadly suppress stderr or return status for the whole staging operation.

Prefer the simplest shell that is easy to reason about.

### B2. Clean-worktree proof before rebase/push

After the local canonical commit and before rebase:

- run a deterministic clean-worktree check including untracked files;
- if dirty, print the exact `git status --porcelain --untracked-files=all` output;
- fail before rebase;
- do not stash, discard, auto-add unknown paths, or hide the error.

This is a safety assertion, not a retry mechanism.

### B3. Focused Git regression

Add a regression that executes the real staging logic in a temporary Git repository where:

- `data/control` is absent;
- `data/audit/taste_steam_review_dossier_group_failures.jsonl` is modified;
- a quarantine artifact exists under the real quarantine path class;
- normal manifest/index/candidate changes are present.

Prove:
- intended audit/quarantine changes are staged;
- optional absent control path does not fail the operation;
- local commit includes all intended outputs;
- worktree is clean immediately afterward;
- the regression would fail under the old combined `git add ... || true` command.

Also preserve canonical-writer serialization/concurrency behavior.

## Durable decision

Update `PROJECT_DECISIONS.md` with a new durable Dossier decision that records:

- worker supplies dates/facts, not freshness judgment;
- GitHub derives recent/older/unknown deterministically under the canonical threshold;
- unknown dates never become recent by assumption;
- temporal current-state qualification is based on actual supporting evidence dates;
- failed-group audit/quarantine outputs remain canonical and must be committed atomically with progress state;
- optional-path absence must not suppress staging of other canonical outputs;
- a clean-worktree assertion is required before canonical rebase/push.

Update `config/execution_ownership_contract.json` only if needed to make the deterministic temporal ownership explicit; do not change the broader control-plane model.

Update `PROJECT_ROUTES.md` only if routing materially changes.

## Validation

Run all focused tests plus the relevant current Dossier validation suite.

Required checks include:
- all DATE regressions above;
- the real staging/clean-worktree regression;
- existing TASTE-012 temporal tests;
- existing pragmatic evidence tests;
- existing TASTE-014/TASTE-015 tests;
- buffered group validation/nonblocking traversal;
- canonical writer/coalescing tests;
- execution ownership validation.

Do not weaken unrelated tests to make the suite pass.

## Production boundaries

Do NOT:
- run or modify Scheduled Tasks;
- manually rerun Tiny Snow;
- manually recover g000001;
- manually edit current group progress;
- manually process Dossier backlog;
- authorize Deep recovery;
- rewrite existing production candidate/cache files by hand.

Natural GitHub-owned deterministic rebuilds caused by merged source changes are allowed.

The stale production g000001 state is NOT part of this implementation task. After this fix is independently accepted, Director will decide the normal canonical reconciliation/recovery step separately.

## Durable report

Commit:
`reviews/worker_reports/taste-dossier-github-date-derivation-and-ingest-atomicity-fix-01.md`

Required sections:
1. Final status
2. Architecture preflight
3. User-approved simplification
4. Previous temporal responsibility model
5. New GitHub-derived date model
6. Candidate/schema/binding changes
7. Current-state temporal semantics
8. Tiny Snow regression
9. Old staging failure
10. New staging behavior
11. Clean-worktree proof
12. DATE regressions
13. Full validation results
14. Files changed
15. Durable decisions/contracts changed
16. Production actions explicitly not performed
17. Unresolved
18. Director recommendation

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_user_decision`

Before completion:
- commit the final durable report to `main`;
- reread that exact committed report from fresh `main`;
- do not modify it after that reread unless repeating the final commit+reread closeout.

Expected next step after this task:
- Director independently verifies the implementation/report;
- only after acceptance decide whether/how to reconcile the already-stale production g000001 state through the normal GitHub-owned mechanism.

# WORKER TASK — stale live Statistics publication diagnostic 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `stale-live-statistics-publication-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/stale-live-statistics-publication-diagnostic-01.md`

## User-visible defect

On 2026-09-30 around 15:59 user-local time (+04:00), live site Statistics showed:

### Dossier
- total: 266
- last record: `30.09.2026, 10:25`
- ready: 60
- waiting: 200
- recovery required: 6

### Deep
- total: 262
- last record: `30.09.2026, 06:07`
- authoritative completed: 41
- completed fit: 37
- completed not fit: 4
- incomplete/recovery: 7
- waiting dossier: 206
- ready/pending: 8
- remaining until authoritative: 221

### Top page freshness
- `Скидки: обновлено 24 сент., 03:12`

Current GitHub truth is newer.

Verified before this task:
- canonical Dossier store received new accepted dossiers in commit
  `6e84248d60b27d80dfb2bbbe677b9a076798c868`
  at `2026-09-30T09:48:55Z`;
- those dossiers include `generated_at_utc = 2026-09-30T09:44:48Z`;
- current Dossier validation status has accepted group count 9, failed group count 5, pending group count 56;
- current Dossier work group progress reports accepted dossier count 27, failed dossier count 15, pending dossier count 167;
- current PASS 2 work scope reports:
  - total current coverage target: 266
  - first-pass attempted: 58
  - authoritative completed: 48
  - completed fit: 42
  - completed not-fit: 6
  - incomplete/recovery: 10
  - waiting for dossier: 182
  - ready/pending: 27
  - remaining authoritative: 218;
- score-explainability migration is complete 43/43;
- its last accepted semantic result is `2026-09-30T07:34:20Z`;
- therefore the live Deep block is not merely displaying a different timestamp: its counts are materially stale too.

The user wants the exact reason why Statistics and page freshness lag GitHub truth.

## Mandatory START gate

Before diagnosis:

1. Read current `CHAT_PROTOCOL.md` from `main` fully and execute its START gate.
2. Read this task fully.
3. Re-read current `DIRECTOR_TASK_BOARD.md` current-state section.
4. Verify current `main` and do not rely on old chat conclusions as authority.

Do not IMPLEMENT anything.

## Diagnostic objective

Find the **first stale boundary** in the publication chain.

Trace current values and bindings through, at minimum:

1. canonical Dossier truth;
2. canonical Deep/PASS 2 truth;
3. statistics/visual producer inputs;
4. generated canonical visual payload;
5. any freshness/material-binding receipt;
6. staged Pages input such as `web/data/current.json`;
7. latest Pages/deploy artifact and workflow run;
8. browser-side caching / service worker only if GitHub/Pages artifact is current but the live browser still serves older bytes.

Do not jump directly to browser caching. Prove each upstream boundary first.

## Questions the report must answer

### A. Dossier timestamp semantics

Determine exactly what the UI field `Последняя запись` for Dossier is intended to mean.

Possible sources include, but are not limited to:
- latest dossier `generated_at_utc`;
- latest canonical acceptance/persistence time;
- latest group drain time;
- latest statistics snapshot time.

Identify the exact producer field/function and current canonical value.

State whether the displayed `30.09.2026, 10:25` was correct for any older canonical snapshot, or is computed incorrectly.

### B. Deep timestamp semantics

Determine exactly what `Последняя запись` for Deep is intended to mean.

Distinguish:
- semantic worker run start;
- create-only submission;
- canonical GitHub acceptance;
- technical state reconciliation;
- migration acceptance.

Identify the exact producer field/function and current canonical value.

Do not count developer-only state reconciliation as a new semantic result unless the UI contract explicitly does so.

### C. Count provenance

For every visible Deep count on the screenshot, map:
UI label -> producer field -> canonical current source.

Do the same for Dossier ready/waiting/recovery counts.

Prove where the screenshot values `41/37/4/7/206/8/221` and `60/200/6` came from, if an older payload containing them still exists.

### D. Publication chain

Establish exact SHAs/timestamps for:
- latest canonical visual payload generation;
- the input material SHA/binding used by that payload;
- latest staged `web/data/current.json`;
- latest deploy/Pages artifact;
- currently deployed/public artifact if determinable.

Compare those against the newest canonical Dossier/Deep truth.

Identify the first boundary where newer truth stopped propagating.

### E. Existing stale-snapshot protection

PR #126 / stale-snapshot rebase-race work is historical context, not assumed root cause.

Verify whether the current defect:
- bypassed that protection;
- is a different trigger/publication problem;
- is a Pages deploy problem;
- is a browser cache/service-worker problem;
- or is a statistics producer bug.

Do not reopen or modify PR #126 in this diagnostic.

### F. Top-page date

Explain why the live page still shows:
`Скидки: обновлено 24 сент., 03:12`

Determine whether this comes from:
- the same stale visual payload as Statistics;
- a separate stale field;
- a browser/service-worker cache;
- or a deliberate source-update timestamp with different semantics.

### G. Scope of defect

Determine whether stale publication affects:
- only Statistics;
- the entire visual payload;
- card ordering/content;
- expired-sale hiding;
- translations;
- or some subset.

Use exact evidence, not assumptions.

## Required evidence

Prefer GitHub-owned metadata and exact artifact bindings.

Inspect only what is necessary:
- relevant workflow runs;
- relevant commits;
- current/older visual payload metadata;
- freshness receipts;
- deploy artifacts;
- specific producer/staging scripts;
- browser cache/service-worker code only if needed.

If a workflow/action artifact must be downloaded or inspected, do so only as needed for diagnosis.

Do not perform broad unrelated code review.

## Hard boundaries

Do NOT:
- modify production code;
- modify workflows;
- rebuild/redeploy;
- trigger manual workflows;
- alter Pages;
- alter Service Worker state;
- change Scheduled Tasks;
- run Deep or Dossier semantic workers;
- repair counters;
- edit canonical data;
- create an implementation PR;
- conflate current GitHub truth with old screenshots.

This task is diagnostic only.

## Output

Write:
`reviews/worker_reports/stale-live-statistics-publication-diagnostic-01.md`

Required sections:

1. Task
2. User-visible evidence
3. Current canonical Dossier truth
4. Current canonical Deep truth
5. Dossier last-record semantics
6. Deep last-record semantics
7. Statistics count provenance
8. Visual payload provenance
9. Pages/deploy provenance
10. Browser/service-worker provenance, if relevant
11. First stale boundary
12. Root cause
13. Scope of stale publication
14. Relation to prior stale-snapshot fix
15. Exact evidence / commits / runs / artifacts
16. Recommended fix
17. Status
18. Recommended next step — exactly one bounded next action

Allowed statuses:
- `diagnosed_needs_fix`
- `diagnosed_external_cache_only`
- `diagnosed_no_current_defect`
- `needs_user_decision`
- `blocked`

Do not implement the recommended fix in this task.
Do not start another task after this one.

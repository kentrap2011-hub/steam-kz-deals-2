# WORKER TASK — ANALYSIS LAST WRITE TIMESTAMPS UI 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or the target is ambiguous, stop and switch first;
- do not use another repository.

Task ID: `analysis-last-write-timestamps-ui-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/analysis-last-write-timestamps-ui-01.md`

## User goal

On the Statistics page, add a visible `Последняя запись` timestamp for each independent analysis stage so the user can tell when a stage has stopped making durable progress:

1. `Быстрый разбор` / Fast / PASS 1
2. `Досье отзывов Steam` / Dossier
3. `Глубокий разбор` / Deep / PASS 2

The timestamp must represent the latest **durably persisted canonical progress record for that stage**, not:
- page load time;
- visual build time;
- deployment time;
- Scheduled Task start time;
- an unaccepted/inbox-only candidate;
- an inferred heartbeat.

This feature is observability only. It must not change analysis eligibility, ordering, retries, completeness or execution.

## Parallel-work constraint

ЧАТ 1 is concurrently working on:
`WORKER_TASK_RUSSIAN_DESCRIPTION_PUBLICATION_BLOCKER_FIX_01.md`.

Parallel development is authorized.

Before final merge:
- refresh/re-read current `main`;
- inspect whether ЧАТ 1 landed changes touching any files modified by this task;
- reconcile normally and rerun relevant validation;
- do not overwrite or revert ЧАТ 1 changes;
- if an actual semantic conflict exists, stop with `blocked` rather than guessing.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current `CHAT_CONTEXT.md`;
3. current top of `DIRECTOR_TASK_BOARD.md`;
4. the Fast/Dossier/Deep route in `PROJECT_ROUTES.md`;
5. `config/progressive_personalization_contract.json`;
6. `config/execution_ownership_contract.json`;
7. only the smallest state/producer/frontend files needed to implement this feature.

## Architecture preflight

Before writes, prove:
- GitHub remains owner of canonical Fast/Dossier/Deep state and persistence;
- browser remains read-only and only formats timestamps already prepared by GitHub;
- no new heartbeat, scheduler, queue, retry loop, polling daemon or semantic stage is introduced;
- the timestamp definition for each stage comes from existing durable canonical records.

## Canonical timestamp semantics

Determine the exact existing durable timestamp source for each stage and document it.

Required meaning:

### Fast
`Последняя запись` = latest durable canonical PASS 1/Fast progress record accepted/persisted by GitHub for the current production state.

### Dossier
`Последняя запись` = latest durable canonical Dossier group progress transition persisted by GitHub for the current snapshot, including either accepted or failed group classification if that is the canonical progress record.

Do not use merely buffered/unaccepted candidate creation time.

### Deep
`Последняя запись` = latest durable canonical PASS 2/Deep progress record accepted/persisted by GitHub for the current production state.

If the current canonical structures do not expose a trustworthy timestamp directly, derive it deterministically in the GitHub-owned visual producer from existing canonical persisted records. Do not invent a browser-side inference.

If a stage genuinely has no durable record yet, publish `null` and display `Ещё не было записей`.

## Visual payload

Add explicit machine-readable fields to the existing GitHub-produced statistics/processing-status payload for the three stage timestamps.

Use clear names and ISO-8601 UTC values in the payload.

The exact schema location may follow the existing statistics contract, but keep all three timestamps together with the corresponding stage metrics.

Do not overload visual generation time or provenance hashes as substitutes for stage progress time.

## UI

On the existing Statistics page, show under/next to each stage:

`Последняя запись: <date and time>`

Requirements:
- format the canonical timestamp for the viewer's local timezone using normal browser date/time formatting;
- do not alter the underlying timestamp;
- if null, display `Последняя запись: ещё не было записей`;
- keep layout usable on phone and desktop;
- no continuously polling frontend is required;
- do not infer whether a stage is "завис" or show an alarm threshold in this task. The user will judge that from the timestamp.

## Validation

Add focused regressions proving:
1. Fast timestamp chooses the latest durable canonical Fast record, not build time;
2. Dossier timestamp chooses the latest accepted/failed canonical group transition for the current snapshot and ignores buffer-only candidates;
3. Deep timestamp chooses the latest durable canonical Deep record;
4. no-record state produces null and safe UI text;
5. timestamps survive the normal final visual payload path;
6. browser only formats the provided values;
7. existing stage counts/provenance remain unchanged.

Run the relevant existing visual/Progressive validation gates.

Before merge, update against fresh `main` because ЧАТ 1 is operating in parallel.

After merge:
- validate a normal full visual build if the publication pipeline is available;
- if publication is still temporarily blocked by the independent Russian-description task, do not alter/bypass that gate; report the implementation as validated but publication-blocked and cite the exact blocker.
- if ЧАТ 1 has already repaired the blocker, verify a successful Pages deploy and inspect the deployed payload/UI fields.

## Scope exclusions

Do not:
- diagnose or modify Dossier worker execution itself;
- alter Dossier evidence semantics/recovery;
- alter Fast or Deep semantic conclusions, work queues, eligibility or recovery;
- change any Scheduled Task;
- manually process Fast/Dossier/Deep backlog;
- add a watchdog, automatic "stuck" detector or timeout policy;
- change the Russian-description subsystem owned by ЧАТ 1.

## Report

Write:
`reviews/worker_reports/analysis-last-write-timestamps-ui-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Timestamp definitions`
4. `Changes`
5. `Parallel reconciliation`
6. `Validation`
7. `Published result`
8. `Unresolved`
9. `Status`
10. `Recommended next step` — exactly one bounded next step
11. exact PR/commit/run/artifact refs
12. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another task after this one.

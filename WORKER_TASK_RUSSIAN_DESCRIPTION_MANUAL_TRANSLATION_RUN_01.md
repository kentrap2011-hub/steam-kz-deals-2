# WORKER TASK — RUSSIAN DESCRIPTION MANUAL TRANSLATION RUN 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- do not search, read, modify, or use another repository;
- if GitHub/tool opens another repository or the target is ambiguous, stop and switch to this repository before continuing.

Task ID: `russian-description-manual-translation-run-01`
Mode: `SEMANTIC / MANUAL ONE-SHOT`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/russian-description-manual-translation-run-01.md`

## User authorization

The user explicitly authorizes one immediate manual worker invocation to process the current Russian-description translation work.

This is NOT authorization to create, edit, enable, disable, pause, resume, rename, delete, or otherwise modify any ChatGPT Scheduled Task or automation.

Do not interpret this task as recurring work.

## Goal

Process the current GitHub-authorized Russian-description translation workload using the current canonical translation contract and persistence path.

Translate only the exact current work prepared/authorized by GitHub. Do not invent scope, rebuild the queue, or directly patch canonical cache/data outside the repository-defined translation transport/persistence mechanism.

The purpose is to complete as much of the current pending translation workload as the canonical worker contract permits in this one-shot invocation.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully and make the required task checklist.

Read minimally:
1. `CHAT_CONTEXT.md`;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. the Russian-description / translation route in `PROJECT_ROUTES.md`;
4. the current canonical Russian translation worker prompt/contract/schema named by that route;
5. the exact current GitHub-prepared translation work/index/queue named by the canonical prompt;
6. only the exact persistence/transport files required by the canonical translation worker.

Do not reconstruct unrelated project history.

## Required behavior

1. Use only current `main` and current GitHub-prepared translation work.
2. Translate only items explicitly authorized by the current canonical translation scope.
3. Preserve exact AppID/item/source/binding identity required by the current contract.
4. Follow the canonical semantic requirements for meaningful Russian text.
5. Do not treat English or other non-Russian source text as if it were already Russian.
6. Do not fabricate content where source meaning is unavailable.
7. Persist results only through the current repository-defined create-only / canonical ingest path.
8. If the current worker contract groups or batches work, continue through the current authorized pending work according to that contract; do not invent an arbitrary quota.
9. If no current items require translation, treat that as a valid no-work completion and report it accurately.
10. If an exact item cannot be translated under the canonical rules, record/report the unresolved condition through the allowed path; do not weaken validation.

## Scope boundaries

Do not:
- change translation code, validation logic, workflow behavior, publication gates, UI, Statistics, ranking, Fast, Dossier, Deep, expiry handling, or visual build logic;
- directly edit canonical translation cache/state unless the canonical worker contract explicitly identifies that exact write as the normal worker output path;
- create replacement work items;
- change retry/completeness ownership;
- modify any Scheduled Task;
- process unrelated semantic queues.

## Concurrency

Another worker may concurrently implement changes to the translation/publication/statistics pipeline.

Therefore:
- preserve all concurrent `main` changes;
- never reset/revert unrelated commits or production data;
- before each write, obey current canonical liveness/binding checks;
- if a concurrent implementation changes the translation contract in a way that invalidates this frozen/current work, fail closed and report the exact contradiction rather than guessing.

## Acceptance

The task is successful when:
- all translation outputs created in this invocation are valid under the current canonical contract;
- they are persisted through the normal GitHub-owned path;
- exact current scope/bindings are preserved;
- no unrelated project state is changed;
- the report states counts for attempted, successfully persisted, unresolved/failed, and remaining current translation work when those values are available from canonical state.

Do not claim the live site is fresh merely because translations were produced.

## Report

Write:
`reviews/worker_reports/russian-description-manual-translation-run-01.md`

Required sections:
1. `Task`
2. `Canonical translation authority used`
3. `Current scope`
4. `Translations attempted`
5. `Translations successfully persisted`
6. `Unresolved / failed`
7. `Remaining work`
8. `Validation`
9. `Unresolved`
10. `Status`
11. exact commit/run/artifact refs used or created
12. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another project task after this one.

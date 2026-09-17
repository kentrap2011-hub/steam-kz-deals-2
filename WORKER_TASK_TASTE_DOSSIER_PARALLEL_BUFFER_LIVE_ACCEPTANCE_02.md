# WORKER TASK — Taste Dossier Parallel Buffer Live Acceptance 02

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If GitHub/tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-parallel-buffer-live-acceptance-02`
Mode: `READ / VALIDATE`

## Goal

Independently validate the second real Scheduled ChatGPT run under the active parallel-buffer contract, with special focus on proving same-invocation multi-group buffering while canonical acceptance lags.

Do not implement or fix anything in this task.

## Authoritative manual UI result supplied by the user

Treat the following verbatim Scheduled Task result as authoritative UI evidence. Do not try to rediscover the Scheduled Task UI or ask the worker to inspect unavailable ChatGPT UI state:

> В этой инвокации create-only опубликованы candidate-группы g000002 и g000003. Snapshot/plan/binding оставались неизменными; это только buffered transport progress, не canonical acceptance. На последней проверке GitHub ещё показывал canonical_expected_sequence=2, completed_required_count=3, remaining_required_count=630, full_backlog_complete=false.
>
> Следующая строго предобъявленная локальная группа — g000004: GRANDIA HD Remaster, Shadow Warrior 3: Definitive Edition, Digimon Story Cyber Sleuth: Complete Edition.

## Read first / START gate

Follow `CHAT_PROTOCOL.md` START gate fully, then read the minimum relevant canonical material, including:

- `CHAT_CONTEXT.md`;
- `DIRECTOR_PROTOCOL.md` as applicable;
- `WORKER_TASK_TASTE_DOSSIER_PARALLEL_BUFFER_VALIDATION_IMPLEMENT_01.md`;
- `reviews/worker_reports/taste-dossier-parallel-buffer-validation-implement-01.md`;
- `reviews/worker_reports/taste-dossier-parallel-buffer-live-acceptance-01.md`;
- active worker prompt/contract/index/descriptor state needed for validation;
- GitHub-owned candidate ingest / validation status / canonical progress state relevant to this second live run.

Run architecture preflight before conclusions.

## Questions to answer

Validate, from current canonical GitHub state and the user-supplied live result:

1. Did the Scheduled Task publish exactly the expected immutable candidates for `g000002` and `g000003` under the same active snapshot and binding?
2. Were both candidate paths create-only additions, not overwrites or alternate filenames?
3. Were `g000002` and `g000003` published in exact descriptor order during the same invocation?
4. At the time they were published, did canonical `expected_sequence` still lag at 2 as the UI states, thereby proving the worker did not wait for GitHub acceptance of g2 before publishing g3?
5. Did GitHub strict validation run for both candidates?
6. What durable validation result/state did each group receive: accepted, valid-but-buffered, invalid, pending, or other?
7. What is the canonical progress after GitHub processing? Report exact completed/remaining/expected sequence.
8. If `g000002` is valid and accepted, did `g000003` also advance canonically once the contiguous prefix permitted it?
9. If either group is invalid, did canonical progress stop exactly at the first invalid group while later work stayed buffered?
10. Was any invalid marker/status produced? If yes, report the exact strict validation failure without implementing a fix.
11. Did `g000004` actually get published, or was it only named as the next local group? Do not infer publication without GitHub evidence.
12. Does this run now prove the defining live property: same-invocation publication of multiple consecutive groups while canonical validation/acceptance lags?
13. Confirm no per-game split/retry/healing behavior appeared and no canonical data crossed an invalid/unvalidated gap.

## Acceptance standard

Classify the live acceptance as exactly one of:

- `accepted_live_parallel_buffering`
- `partial_live_acceptance_more_runtime_evidence_needed`
- `rejected_live_parallel_buffering`
- `blocked`

The intended success condition is now narrow and concrete: real live evidence must prove that at least two consecutive predeclared groups were published in the same Scheduled invocation without waiting for canonical advancement, while GitHub retained exclusive canonical acceptance control and processed them safely in contiguous order.

If that is proven and no semantic/validation defect is found, classify `accepted_live_parallel_buffering`.

## Prohibitions

Do not:

- implement fixes;
- edit runtime/contract/prompt/schema;
- run Scheduled Task `Run now`;
- create test dossier artifacts;
- inspect other repositories;
- infer UI-only facts not present in the supplied text;
- treat candidate publication as canonical acceptance.

## Durable report

Publish to `main`:

`reviews/worker_reports/taste-dossier-parallel-buffer-live-acceptance-02.md`

The report must include:

- architecture preflight;
- the authoritative user-supplied live result;
- active snapshot/binding identity;
- exact g2/g3 descriptor and candidate identities;
- publication commit/order evidence proving whether both came from the same live invocation;
- canonical state visible at publication time if reconstructable from GitHub history plus the authoritative UI result;
- exact GitHub validation result for g2 and g3;
- canonical progress before/after;
- whether g4 was actually published or only named as next;
- property-by-property live proof matrix;
- confirmation whether same-invocation multi-group buffering is finally proven live;
- any strict validation defect found;
- final acceptance classification;
- exactly one next step.

If accepted, the one next step should be to return control to the Director for the next production-readiness decision, not to run another Scheduled Task automatically.

Ensure the durable report is in `main` before completion. Stop after report publication.
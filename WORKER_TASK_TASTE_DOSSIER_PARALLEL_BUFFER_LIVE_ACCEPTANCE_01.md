# WORKER TASK — Taste Dossier Parallel Buffer Live Acceptance 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If GitHub/tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-parallel-buffer-live-acceptance-01`
Mode: `READ / VALIDATE`

## Goal

Independently validate the first real Scheduled ChatGPT run after `taste-dossier-parallel-buffer-validation-implement-01`.

Do not implement or fix anything in this task.

## Authoritative manual UI result supplied by the user

Treat the following verbatim Scheduled Task result as authoritative UI evidence. Do not try to rediscover the Scheduled Task UI or ask the worker to inspect unavailable ChatGPT UI state:

> Опубликован immutable candidate-buffer для группы 1 из 211. Это только transport/persistence progress, не canonical acceptance и не завершение snapshot. Canonical control plane на момент последней проверки всё ещё показывал canonical_expected_sequence=1, remaining_required_count=633.
>
> Следующая локальная группа по неизменившемуся плану — g000002 (Blacksad: Under the Skin, Prototype™, Welcome to Elk).

## Read first / START gate

Follow `CHAT_PROTOCOL.md` START gate fully, then read the minimum relevant canonical material, including:

- `CHAT_CONTEXT.md`;
- `DIRECTOR_PROTOCOL.md` as applicable;
- `WORKER_TASK_TASTE_DOSSIER_PARALLEL_BUFFER_VALIDATION_IMPLEMENT_01.md`;
- `reviews/worker_reports/taste-dossier-parallel-buffer-validation-implement-01.md`;
- active worker prompt/contract/index/descriptor state needed for validation;
- GitHub-owned candidate ingest / validation status / canonical progress state relevant to this one live run.

Run architecture preflight before conclusions.

## Questions to answer

Validate, from current canonical GitHub state and the user-supplied live result:

1. Did the Scheduled Task successfully publish exactly the expected immutable candidate for `g000001` under the active snapshot and binding?
2. Did GitHub strict validation run on that candidate?
3. What is the durable validation status of `g000001` — pending, valid, invalid, accepted, or other canonical state?
4. Did canonical progress advance from sequence 1? If yes, to exactly what counts/sequence? If not, why not?
5. Was any invalid marker/status produced? If yes, identify the exact strict validation failure without attempting a fix.
6. Did any later group (`g000002+`) get buffered during this same invocation? The user-visible result mentions `g000002` only as the next local group; do not infer publication without GitHub evidence.
7. Does this live run prove the new asynchronous architecture actually works end to end, or only partially?
8. Specifically distinguish these properties:
   - local Python/prepublication requirement removed in live runtime;
   - create-only candidate publication works;
   - GitHub validation of candidate works;
   - canonical contiguous-prefix acceptance works;
   - same-invocation publication of multiple groups while canonical validation lags works.
9. If only one candidate exists, determine whether that is merely insufficient evidence for multi-group parallel buffering or whether canonical prompt/runtime state proves the worker incorrectly stopped after one group. Do not speculate beyond evidence.
10. Confirm no canonical data crossed an invalid/unvalidated gap and no per-game split/retry behavior appeared.

## Acceptance standard

Classify the live acceptance as exactly one of:

- `accepted_live_parallel_buffering`
- `partial_live_acceptance_more_runtime_evidence_needed`
- `rejected_live_parallel_buffering`
- `blocked`

Do not call it accepted unless the real run proves the intended live properties, not just deterministic tests.

If `g000001` is invalid, this is not a request to repair it. Record the defect and reject/partial-accept as appropriate.

If `g000001` is valid and accepted but only one group was ever published, do not claim multi-group parallel buffering was proven. State exactly what is and is not proven.

## Prohibitions

Do not:

- implement fixes;
- edit runtime/contract/prompt/schema;
- run Scheduled Task `Run now`;
- create test dossier artifacts;
- inspect other repositories;
- infer UI-only facts not present in the user's supplied text;
- treat candidate publication as canonical acceptance.

## Durable report

Publish to `main`:

`reviews/worker_reports/taste-dossier-parallel-buffer-live-acceptance-01.md`

The report must include:

- architecture preflight;
- the authoritative user-supplied live result;
- active snapshot/binding/expected group identity;
- exact candidate artifact identity and whether only g1 exists;
- exact GitHub validation status/result for g1;
- canonical progress before/after;
- property-by-property live proof matrix for the five properties listed above;
- whether same-invocation multi-group buffering is proven, disproven, or still unproven;
- any strict validation defect found;
- final acceptance classification;
- exactly one next step.

If the result is partial solely because only one group was published and there is no defect, the next step should be a narrowly targeted second live run or prompt/runtime investigation sufficient to prove multi-group same-invocation buffering — whichever the evidence supports.

Ensure the durable report is in `main` before completion. Stop after report publication.
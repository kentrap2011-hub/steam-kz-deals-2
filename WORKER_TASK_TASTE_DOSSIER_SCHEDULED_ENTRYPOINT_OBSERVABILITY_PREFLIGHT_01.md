# WORKER TASK — TASTE DOSSIER SCHEDULED ENTRYPOINT OBSERVABILITY PREFLIGHT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-scheduled-entrypoint-observability-preflight-01`
Mode: `READ-ONLY / ARCHITECTURE PREFLIGHT`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`, включая обязательный architecture preflight;
- `DIRECTOR_PROTOCOL.md` только если чат работает как Director (обычный worker не становится Director);
- `CURRENT_TASK.md` только для конфликта активной работы;
- релевантный Taste dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_persistence_bridge.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `data/production/pre_ai/taste_steam_review_dossier_work.json` только в объёме, нужном для понимания binding/control-plane handoff;
- accepted reports:
  - `reviews/worker_reports/taste-dossier-fail-closed-execution-ledger-implement-01.md`;
  - `reviews/worker_reports/taste-dossier-scheduled-entrypoint-ledger-diagnostic-01.md`.

Do not broad-search unrelated history.

## Accepted problem

Two facts are already accepted:

1. The canonical prompt in `main` unambiguously requires
   `FAIL_CLOSED_EXECUTION_LEDGER_V1`
   on every fail-closed stop before successful candidate publication.

2. A live Scheduled Task invocation stopped fail-closed on the current binding but omitted that mandatory ledger.

The follow-up diagnostic could not inspect the actual live Scheduled Task entrypoint/invocation prompt and therefore classified the failure as:

`insufficient_observability_to_classify`

The missing boundary is:

`Scheduled Task entrypoint/config -> canonical prompt load/application -> early fail-closed -> output`.

Repeatedly strengthening wording inside the same prompt is NOT an accepted solution.

## Goal

Design the smallest deterministic observability / acceptance mechanism that lets GitHub distinguish at least:

A. the Scheduled worker never established the current canonical prompt/binding handshake;

B. it established the handshake, then failed later while executing the current prompt contract;

C. it established the handshake and produced the required success/failure runtime artifact correctly.

The design must NOT pretend that an LLM self-assertion alone proves full prompt compliance.

The result of this task is architecture only. Do not implement.

## Architecture preflight questions — answer explicitly

Before recommending any design, answer:

1. Which component currently owns:
   - canonical work binding;
   - runtime external/semantic work;
   - validation/persistence/progress;
   - retry/recovery/completeness?

2. Which existing canonical contract permits the proposed observability mechanism?

3. Does any option move GitHub control-plane responsibility into Scheduled ChatGPT or interactive chat?

4. Does any option create a new recurring stage, queue, retry loop, backlog manager, checkpoint owner, or scheduler?

If an option violates ownership, reject it rather than trying to make it convenient.

## Required design comparison

Evaluate at least the following mechanisms.

### OPTION A — final-response attestation only

Example shape:
- final response echoes current snapshot/binding/prompt revision/prompt hash and says canonical prompt was loaded.

Assess honestly:
- what this proves;
- what it does NOT prove;
- whether it is materially stronger than the failed ledger requirement.

Do not recommend A as sufficient if it remains pure prompt compliance.

### OPTION B — candidate-only binding proof

Require successful candidate artifacts to echo a GitHub-issued immutable binding tuple such as:
- snapshot id;
- sequence/group sha;
- prompt revision/hash;
- schema/contract hashes or existing equivalent fields.

Assess:
- whether this already exists partly or fully;
- whether it proves success-path binding;
- why it does or does not solve fail-closed/no-candidate invocations.

### OPTION C — GitHub-validated create-only invocation receipt

Assess a minimal create-only runtime receipt written by Scheduled ChatGPT through the existing repository-defined runtime artifact interface, before external evidence work or before a terminal fail-closed return.

The receipt must be designed only if ownership allows it.

Candidate fields to assess:
- snapshot id;
- canonical expected sequence;
- group sha;
- worker prompt revision;
- worker prompt sha256;
- relevant contract/schema binding hashes;
- receipt phase/state;
- deterministic invocation/work-unit identity derived from GitHub-owned input, not model-chosen scope.

Key questions:
- Can this be made create-only and non-authoritative?
- Can GitHub validate it without treating it as progress?
- Can it avoid becoming a new queue/checkpoint/retry owner?
- What exact event would require it: invocation start, before first web retrieval, before any terminal fail-closed response, or another bounded point?
- How are duplicate/replayed/stale receipts handled?
- Does the current persistence bridge permit this artifact class, or would a contract change be required?

### OPTION D — fail-closed durable execution receipt

Assess a create-only fail-closed sidecar/receipt containing only observable execution facts:
- exact stop gate;
- material route classes attempted;
- observable result;
- budget used;
- next required step;
- factual blocker or explicit unknown.

This is a durable analogue of the user-visible ledger.

Assess:
- whether it should be the same artifact as C with phases, or separate;
- whether GitHub can validate it while preserving no-progress semantics;
- privacy constraints;
- stale quarantine/replay behavior;
- whether it duplicates or simplifies the final-response ledger.

### OPTION E — GitHub-issued challenge/nonce or manifest-bound token

Assess whether GitHub should place a deterministic or opaque per-work-unit challenge in the prepared canonical work input and require the Scheduled worker to echo it in any candidate/failure receipt.

Determine:
- what this proves (e.g. current manifest read);
- what it does not prove (e.g. full prompt comprehension);
- whether it materially improves binding assurance without creating secret handling or unnecessary complexity.

Do not recommend a nonce merely because it sounds stronger; compare against existing content-complete hashes.

## Required adversarial test

For every serious candidate design, test these scenarios conceptually:

1. Worker knows the new binding revision but did not read/apply the full canonical prompt.
2. Worker read the current work manifest but not the full worker prompt.
3. Worker read both, starts correctly, then stops before retrieval.
4. Worker performs retrieval and fail-closes without candidate.
5. Worker publishes a candidate.
6. Snapshot/binding changes between invocations.
7. Duplicate/replayed receipt appears.
8. Receipt is missing.
9. Receipt has stale/mismatched hashes.
10. Runtime ends abruptly before a terminal receipt can be written.

For scenario 10, do not claim observability that the mechanism cannot provide. State the residual ambiguity explicitly.

## Required decision

Choose exactly one recommended architecture.

The recommendation must specify:

- minimal artifact/interface;
- exact owner that writes it;
- exact owner that validates it;
- whether it is authoritative for progress (expected answer likely no, but prove it);
- deterministic path/naming rule at design level;
- lifecycle:
  `prepared -> runtime receipt -> candidate/fail-closed receipt -> GitHub validation`
  or the minimal equivalent;
- stale/duplicate handling;
- privacy rules;
- how success and fail-closed differ;
- how Director diagnoses A/B/C from durable state;
- what remains fundamentally unobservable if the runtime disappears before writing anything.

Prefer reusing the current runtime artifact boundary over inventing a parallel subsystem, but do not force reuse if the canonical contracts prohibit it.

## Critical design constraint

The mechanism must NOT depend solely on a model remembering to print text in its final answer.

At least one recommended acceptance signal must be externally machine-verifiable by GitHub.

However, do not overclaim:
- a machine-verifiable receipt can prove that the worker possessed/echoed the current binding;
- it may not prove semantic comprehension of every prompt clause.

State the strongest claim the mechanism can honestly support.

## Scope exclusions

Do NOT:
- implement any option;
- edit Scheduled Task;
- edit prompt/contracts/schema/validator;
- add workflow files;
- create runtime receipts;
- run production;
- run Hellish/Crown/Tetris retrieval;
- mutate canonical progress;
- perform recovery/quarantine;
- add a scheduler/queue/retry daemon/logging service;
- redesign dossier evidence semantics.

Only the durable architecture report may be written.

## Acceptance checks

PREFLIGHT-01 — four architecture-preflight ownership questions answered.

PREFLIGHT-02 — OPTIONS A-E compared, including what each proves and does not prove.

PREFLIGHT-03 — current canonical contracts checked for whether a receipt artifact is already permitted or requires explicit contract change.

PREFLIGHT-04 — no option relies on final-response self-attestation alone as a sufficient guarantee.

PREFLIGHT-05 — success path and fail-closed/no-candidate path are both covered.

PREFLIGHT-06 — stale/binding-change and duplicate/replay behavior defined.

PREFLIGHT-07 — abrupt-runtime-loss residual ambiguity stated honestly.

PREFLIGHT-08 — no control-plane ownership moved from GitHub.

PREFLIGHT-09 — no new recurring stage/queue/retry/checkpoint owner introduced without canonical authorization.

PREFLIGHT-10 — exactly one recommended architecture selected.

PREFLIGHT-11 — implementation impact bounded to exact canonical files/components that would need change, but no implementation performed.

PREFLIGHT-12 — no production run; report only.

## Durable report

Write only:
`reviews/worker_reports/taste-dossier-scheduled-entrypoint-observability-preflight-01.md`

Required sections:
1. Task / repo / mode.
2. Accepted problem.
3. Architecture ownership preflight.
4. Current binding/persistence surfaces.
5. OPTION A.
6. OPTION B.
7. OPTION C.
8. OPTION D.
9. OPTION E.
10. Adversarial scenarios 1-10.
11. Recommended architecture — exactly one.
12. Strongest guarantee / explicit non-guarantees.
13. Required canonical changes if later implemented.
14. PREFLIGHT-01..12.
15. Changes: report only.
16. Unresolved.
17. Status.
18. Exactly one recommended next step.
19. Exact refs.
20. Efficiency / reusable lesson.

Allowed statuses:
- `complete_architecture_recommendation`
- `needs_user_decision`
- `blocked_external`
- `needs_more_recon`

## Status rule

`complete_architecture_recommendation` is allowed only if:
- one minimal GitHub-verifiable design is selected;
- ownership remains valid;
- the design covers both candidate and fail-closed/no-candidate paths;
- residual unobservable cases are explicit;
- exact implementation surfaces are bounded;
- no implementation/production run occurred.

## Exactly one next step

If complete:
- return to Director for architecture acceptance and explicit user approval before IMPLEMENT.

If needs_user_decision:
- present one bounded architecture choice only.

If blocked_external:
- identify the exact platform/contract limitation.

If needs_more_recon:
- identify the exact missing canonical fact.

Do not implement inside this task.

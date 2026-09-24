# WORKER TASK — PROGRESSIVE FAST FIVE-ITEM STOP DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `progressive-fast-five-item-stop-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/progressive-fast-five-item-stop-diagnostic-01.md`

## User intent

The user wants a separate worker chat to investigate why the latest real Fast/PASS 1 regulatory invocation stopped after exactly five games even though the current canonical Fast contract has no fixed five-item quota.

This task is diagnostic only.

Do not fix anything.
Do not change the Scheduled Task.
Do not manually run Fast.
Do not infer a platform/runtime cause without evidence.

## Confirmed production observation to explain

A real post-fix Fast invocation submitted these five results consecutively:

1. `BOKURA` — submission commit `c3c7b5506ad62689c6d861d75ce21f03fa06a55f` at `2026-09-24T10:02:37Z`
2. `RV There Yet?` — `d6614b52239b9a84857b8ef8142256ebb95274ac` at `10:02:41Z`
3. `Uncanny Tales: Cold Road` — `9dcb2e70377ad25b2dd552a9f0421fae5e5a38c1` at `10:02:45Z`
4. `Nimbatus - The Space Drone Constructor` — `85e4075348564251f239d7e5dedb2e4a808278dd` at `10:02:50Z`
5. `Borderlands 3` — `01528e104fae5689a8f7399e49eb3a7738ed0218` at `10:02:53Z`

The first GitHub ingest commit was only afterwards:
- `f9c8fdcbd2f6af0eb0e126d66a0c4b13ee793654` at `10:02:57Z`

Therefore the no-wait fix itself is already proven in production: all five submissions existed before first ingest.

The unresolved question is why the semantic invocation stopped after item 5 instead of continuing through later frozen items.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Read current:
- `DIRECTOR_TASK_BOARD.md`
- `CHAT_CONTEXT.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- `config/execution_ownership_contract.json`
- current `data/production/pre_ai/progressive_pass1_work.json`
- current `data/cache/progressive_pass1_state.json`
- PASS 1 ingest/build/runtime tests only as needed.

Use Git history around the five exact submission commits and nearby commits.

## Diagnostic questions

Answer each explicitly.

### STOP-01 — fixed quota

Is there any current canonical code/contract/prompt/bootstrap rule that caps Fast at exactly five items per invocation?

Search for:
- literal 5-item batch/quota/limit;
- implicit list slicing or batch size;
- tool-call/item counters;
- a five-item transport grouping;
- a five-item stop condition.

If none exists, state that clearly.

### STOP-02 — canonical stop condition

What canonical conditions are allowed to stop Fast before exhausting the frozen invocation-start item list?

Distinguish:
- no more frozen work;
- unsafe/no remaining runtime/tool budget;
- profile fetch/verification failure;
- unrecoverable invocation-level error;
- per-item caught failure that should NOT stop siblings;
- exact-path collision that should now skip and continue.

### STOP-03 — actual fifth-item boundary

Using Git history and production state, prove:
- which exact invocation-start work generation/pin was active;
- what item followed Borderlands 3 in the frozen/prepared order at that invocation;
- whether that next item remained valid and unsubmitted immediately after Borderlands 3;
- whether any repository-side change at/after item 5 would have forced the worker to stop under the current contract.

### STOP-04 — GitHub did not block item 6

Prove whether:
- ingest had begun before item 6 would have started;
- any manifest/state update removed or invalidated item 6 before it could run;
- any create-only collision existed for item 6;
- any profile generation/pin changed during the five submissions.

### STOP-05 — runtime/platform evidence

Determine whether there is actual evidence for:
- tool/runtime budget exhaustion;
- tool/API error;
- model/platform interruption;
- context/token exhaustion;
- scheduled invocation timeout;
- explicit clean stop chosen by the worker.

Do NOT label any of these as the cause unless there is direct evidence in accessible records.

If repository/GitHub evidence cannot prove which one happened, say exactly:
`root cause not provable from repository evidence alone`

Then identify the smallest missing evidence required to distinguish the possibilities, e.g. the final visible message/error from the actual Scheduled Task invocation. Do not invent it.

### STOP-06 — hidden stale bootstrap

Check whether any current external/bootstrap text represented in repository-owned canonical files can still impose a five-item limit or old traversal rule despite the canonical PASS 1 worker prompt.

If the actual external Scheduled Task bootstrap is not repository-visible, state that limitation rather than assuming it is correct or stale.

### STOP-07 — semantic outcomes are not stop reasons

Verify whether the mix of:
- fit;
- insufficient evidence;
- per-item incomplete

could legitimately stop the whole invocation. Current design says one incomplete item must not block later siblings; prove whether that remains true.

## Required classification

Choose exactly one final classification:

- `CONFIRMED_FIXED_QUOTA`
- `CONFIRMED_CANONICAL_STOP_RULE`
- `CONFIRMED_RUNTIME_OR_TOOL_INTERRUPTION`
- `CONFIRMED_WORKER_EARLY_STOP_BUG`
- `NOT_PROVABLE_FROM_REPOSITORY_EVIDENCE`

Do not choose a stronger classification than evidence supports.

## No implementation

Do not:
- edit Fast/Deep/Dossier code, contracts or prompts;
- change any Scheduled Task;
- run production Fast/Dossier/Deep;
- reset attempts;
- dispatch workflows;
- create semantic transport;
- “fix” a suspected five-item limit.

Only the required durable report may be committed.

## Durable report

Commit:
`reviews/worker_reports/progressive-fast-five-item-stop-diagnostic-01.md`

Required sections:
1. Final classification.
2. Timeline of the five submissions and first ingest.
3. Canonical stop rules.
4. Evidence for/against a five-item quota.
5. Item 6 state immediately after item 5.
6. Repository-side blockers checked.
7. Runtime/platform evidence checked.
8. External Scheduled Task/bootstrap visibility limitation, if any.
9. STOP-01..STOP-07.
10. Exact missing evidence if root cause cannot be proven.
11. Recommended next step — diagnostic only; do not implement.

Allowed final statuses:
- `complete_ready_for_director_review`
- `needs_external_invocation_evidence`
- `blocked`

Before finishing:
- commit the report to `main`;
- reread the exact committed report from fresh `main`.

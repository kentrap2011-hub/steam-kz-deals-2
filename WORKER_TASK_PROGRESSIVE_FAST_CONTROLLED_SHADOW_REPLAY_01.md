# WORKER TASK — PROGRESSIVE FAST CONTROLLED SHADOW REPLAY 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `progressive-fast-controlled-shadow-replay-01`
Mode: `CONTROLLED SHADOW REPLAY / OBSERVE / NO PRODUCTION MUTATION`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable summary report:
`reviews/worker_reports/progressive-fast-controlled-shadow-replay-01.md`

Per-item diagnostic artifacts:
`reviews/reproductions/progressive-fast-controlled-shadow-replay-01/items/{sequence:03d}--{work_id_prefix}.json`

## User intent

Reproduce the problematic real Fast/PASS 1 invocation as closely as safely possible and record the observable behavior in enough detail to diagnose BOTH:

1. why the real invocation stopped after exactly five items even though item 6 remained available; and
2. why items 2-5 returned `analysis_incomplete / insufficient_evidence` even though later independent review found Fast-level evidence was sufficient.

This is a controlled shadow replay. It must not alter canonical Fast/Deep/Dossier state and must not create real semantic transport.

## Important limitation

This replay can reproduce exact repository inputs, exact historical worker rules, exact order, exact pinned Taste profile, and approximately the same one-GitHub-write-per-item pattern.

It CANNOT guarantee that:
- public web search/index results are byte-for-byte identical to the historical 10:02Z run;
- the platform runtime/tool budget is identical to the historical Scheduled Task environment.

Therefore distinguish:
- what the replay directly reproduces;
- what it only tests behaviorally;
- what remains historically unprovable.

Do not claim “exact historical cause” unless evidence truly supports it.

## No hidden chain-of-thought logging

Do NOT record private chain-of-thought, hidden reasoning, or internal token-level deliberation.

For diagnosis, record only observable/communicable facts:
- exact input used;
- exact action taken;
- exact web query or source requested;
- tool success/failure;
- source facts used;
- concise rule-based rationale for the outcome;
- whether another item was safe to start;
- any explicit observable runtime/tool/platform limit or error.

Never invent token counts, runtime counters, hidden budgets, or platform stop reasons.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Read current:
- `DIRECTOR_TASK_BOARD.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`

Do not read the accepted Fast semantic-quality review report until Phase B below.

## Exact historical replay authority

Use immutable Git state from immediately before the first real submission:

`a1fe53af3e77c21e8fd4de61da6324c11c9c575a`

At that exact commit read:
- `config/progressive_pass1_worker_prompt.md`
- `config/progressive_pass1_contract.json`
- `data/production/pre_ai/progressive_pass1_work.json`

Verified immutable identities that must match before replay begins:

- historical PASS 1 work blob:
  `f3dd4b1d756becc77eb0770c580afcd3aa63a775`
- historical PASS 1 worker-prompt blob:
  `03b0cba057f7b8205e5b2232f578b32369151700`
- semantic generation:
  `b33cc4416860bd15a37f530c9daef8fb7755ae440929f93aa915d5363e31c490`
- pinned Taste profile repository:
  `kentrap2011-hub/stopgame-ratings-data`
- path:
  `gaming_taste_live.json`
- resolved profile commit:
  `5e06acad2a3dc410d4d74177efc69752ade45865`
- profile blob:
  `9b9926031889dbd98ba6585c57836d52c739a0bb`
- profile content SHA256:
  `e2d5f363778d83ec9fdd269f29744356c1b777201fb3dc0c56e898dbd99a44b4`
- profile bytes:
  `269906`
- profile pin SHA256:
  `cf4a4ecf03e72d0d77c85c5e101ce4e37ab36b8547d1bcc1deada780a8df2a6c`

The same historical work blob is also reachable at work-authority commit:
`3aec5050283ec006fefa66f70d7473a499ced2f9`

If any previous report conflicts with the immutable contents above, immutable Git contents win.

## Exact replay order

Start from sequence 1 and follow the exact historical frozen order.

The first eight verified items are:

1. BOKURA — App_1801110 — work_id `60dd08d1cbecfb0f5be325fca5666226fe9487402a014e56bf68a27d29f6838d`
2. RV There Yet? — App_3949040 — `ef1df1ac1f72ac88225dcf5165291e919fbb6647652435618a3b6d252501d908`
3. Uncanny Tales: Cold Road — App_3534240 — `f8782b96421df6c0e30d7c322f51e6071dd20c36689ccf675769af063aaf2d4e`
4. Nimbatus - The Space Drone Constructor — App_383840 — `39001aea6700a19148fefaec098a0373ddb2dc630e43f429e49eb286a08acdc7`
5. Borderlands 3 — App_397540 — `16a60518ece2265eb4ceb8d58d6a2e0ed9de09bddca914ad32e1a9a988494789`
6. The Bureau: XCOM Declassified — App_65930 — `43c59fcb26f1a23774b2547e2d3a3720618a043d5ae47795b4c619d7ed3a6eab`
7. Borderlands 2 — App_49520 — `1898637572e67db463a36df18af194b9277495bfc1ab6d08aeab9cc461c4c241`
8. Shadow Warrior — App_233130 — `38c53a8647384f2bec8c47a94983c881a638af3163fa570e3a35803999329b84`

Do not impose a replay quota of 5 or 8. Continue through the historical frozen list while runtime/tool budget safely permits, exactly as the historical worker contract requires.

Items 1-8 are named only to make the critical boundary observable.

## PHASE A — blind shadow replay

Before making the shadow decision for a given item:

- do NOT read that item's historical submitted Fast result;
- do NOT read the accepted report `reviews/worker_reports/progressive-fast-insufficient-evidence-review-01.md`;
- do NOT use remembered conclusions from that report;
- use only the exact historical Fast work item, exact pinned profile, exact historical Fast worker contract and lightweight public evidence allowed by that contract.

This is intended to reduce outcome anchoring.

### Evidence behavior

For each item, behave according to the historical Fast standard:
- use exact candidate semantic input;
- use pinned Taste profile;
- use the lightest public evidence needed for a trustworthy fit/not-fit decision;
- do not require a Dossier;
- do not require Russian Steam reviews universally;
- do not perform Deep-level exhaustive research;
- stop semantic depth once Fast-level confidence is sufficient.

If prepared semantic input alone is enough, record that no web retrieval was needed.

If it is not enough, perform the lightest reasonable web retrieval.

### Required observable trace per item

Create exactly ONE diagnostic JSON artifact for each completed replayed item at:

`reviews/reproductions/progressive-fast-controlled-shadow-replay-01/items/{sequence:03d}--{first_16_chars_of_work_id}.json`

Create-only. Never overwrite.

The artifact must contain at least:

- `sequence`
- `appid`
- `title`
- `work_id`
- `historical_authority_commit`
- `historical_prompt_blob`
- `profile_pin_sha256`
- `prepared_input_summary`
- `relevant_profile_signals` — concise, only signals actually used
- `retrieval_needed` — boolean
- `retrieval_actions` — ordered list:
  - exact query/request;
  - source/page identity;
  - success/failure;
  - short factual evidence obtained;
- `observable_tool_errors` — empty list if none
- `shadow_outcome` — one of `analyzed_fit`, `analyzed_not_fit`, `analysis_incomplete`
- `fit_level` / `confidence` when applicable
- `issue_code` when incomplete
- `decision_basis` — concise communicable rationale, NOT chain-of-thought
- `fast_standard_satisfied` — boolean
- `continuation_decision` — one of:
  - `continue_next_item`
  - `stop_frozen_work_exhausted`
  - `stop_observable_runtime_or_tool_limit`
  - `stop_invocation_level_error`
- `continuation_reason`
- `next_sequence_expected` if continuing

Do not write a second auxiliary trace commit for the same item. One item = one diagnostic GitHub write, to keep GitHub-write cadence closer to the real invocation.

### Critical item-5 boundary

For sequence 5 / Borderlands 3, the diagnostic artifact MUST explicitly state:
- whether item 6 is safe to start;
- whether any observable runtime/tool/platform limit exists at that moment;
- whether the worker chooses `continue_next_item` or a permitted stop;
- expected next item identity.

If sequence 5 says `continue_next_item` but no sequence-6 artifact is ever created, that is itself important evidence of an interruption outside the explicit worker decision.

### Do not voluntarily stop after five

There is no five-item quota.

If no permitted stop condition is observable after item 5, proceed to item 6.

If item 6 completes and no permitted stop exists, continue to item 7, etc.

Do not stop merely because the diagnostic focus was the first five.

## PHASE B — comparison after replay crosses the critical boundary

Only after:
- sequence 6 has been completed, OR
- an explicit observable permitted stop has occurred,

read:
- the historical real result commits for the replayed items;
- `reviews/worker_reports/progressive-fast-insufficient-evidence-review-01.md`;
- `reviews/worker_reports/progressive-fast-five-item-stop-diagnostic-01.md`.

Then compare.

### Quality diagnosis for original items 2-5

For each of:
- RV There Yet?
- Uncanny Tales: Cold Road
- Nimbatus
- Borderlands 3

classify the most supported mechanism:

- `REPLAY_SUPPORTS_NORMAL_FAST_DECISION` — replay reaches fit/not-fit with normal light evidence;
- `REPLAY_REPRODUCES_INSUFFICIENT_EVIDENCE`;
- `REPLAY_HIT_RETRIEVAL_OR_TOOL_FAILURE`;
- `REPLAY_AMBIGUOUS`.

If replay reaches fit/not-fit, say whether this points toward:
- original retrieval not attempted;
- original retrieval failed;
- original evidence not used;
- original decision threshold too conservative;
- mechanism still cannot be distinguished.

Do not overclaim beyond observable replay evidence.

### Five-item stop diagnosis

Classify:

- `STOP_AT_FIVE_REPRODUCED_WITH_EXPLICIT_REASON`
- `STOP_AT_FIVE_REPRODUCED_WITHOUT_EXPLICIT_REASON`
- `STOP_AT_FIVE_NOT_REPRODUCED`
- `REPLAY_INTERRUPTED_BEFORE_BOUNDARY`

If item 6 and later items are successfully processed, explicitly state that the manual controlled replay does not reproduce the historical five-item stop.

If a platform hard-stop prevents Phase B/final report, the already committed per-item diagnostic artifacts are intended to preserve the last observable state.

## Production safety

STRICTLY FORBIDDEN:
- writing to `data/ai_inbox/progressive_pass1/`;
- writing to PASS 1 state/receipts/work;
- creating replacement historical Fast results;
- resetting attempts;
- changing Fast/Deep/Dossier prompts/contracts/code;
- changing or running Scheduled Tasks;
- manually running production Fast/Deep/Dossier;
- triggering production ingest workflows.

Allowed repository writes:
1. one diagnostic artifact per replayed item under the dedicated `reviews/reproductions/.../items/` path;
2. the final durable summary report.

These diagnostic commits are not semantic transport and must not be interpreted as canonical Fast attempts.

## Final durable report

If execution reaches a safe closeout, commit:

`reviews/worker_reports/progressive-fast-controlled-shadow-replay-01.md`

Required sections:
1. Final status.
2. Exact historical authority/prompt/profile verified.
3. Replay limitations.
4. Item-by-item observable trace summary.
5. Sequence 5 -> 6 boundary.
6. Whether stop-at-five reproduced.
7. Per-game comparison for original items 2-5.
8. What the replay says about retrieval behavior.
9. What the replay says about decision threshold.
10. Observable tool/runtime errors, if any.
11. Root-cause conclusions separated into CONFIRMED / SUPPORTED / STILL UNKNOWN.
12. No-production-mutation confirmation.
13. Recommended Director next step.

Allowed final statuses:
- `complete_ready_for_director_review`
- `replay_stopped_with_observable_reason`
- `replay_interrupted_incompletely`
- `blocked_before_replay`

Before completion:
- commit the report;
- reread the exact committed report from fresh `main`.

Do not implement any fix in this task.

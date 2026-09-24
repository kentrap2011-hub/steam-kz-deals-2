# Progressive Fast Controlled Shadow Replay 01

## 1. Final status

`complete_ready_for_director_review`

Five-item stop classification:

`STOP_AT_FIVE_NOT_REPRODUCED`

Semantic-quality classification for original items 2-5:

- RV There Yet?: `REPLAY_SUPPORTS_NORMAL_FAST_DECISION`
- Uncanny Tales: Cold Road: `REPLAY_SUPPORTS_NORMAL_FAST_DECISION`
- Nimbatus - The Space Drone Constructor: `REPLAY_SUPPORTS_NORMAL_FAST_DECISION`
- Borderlands 3: `REPLAY_SUPPORTS_NORMAL_FAST_DECISION`

The controlled replay processed sequence 1 through sequence 12 in frozen historical order. Sequence 5 explicitly chose `continue_next_item`; sequence 6 was then successfully executed and persisted as a diagnostic artifact. No observable runtime/tool/platform stop occurred at the historical five-item boundary.

This task did not alter production Fast, Deep, Dossier, state, attempts, scheduler configuration, contracts, prompts, code, workflows or canonical semantic results.

## 2. Exact historical authority / prompt / profile verified

Historical invocation-side authority used for the replay:

- repository: `kentrap2011-hub/steam-kz-deals-2`
- exact authority commit: `a1fe53af3e77c21e8fd4de61da6324c11c9c575a`
- historical worker prompt blob: `03b0cba057f7b8205e5b2232f578b32369151700`
- historical PASS 1 work blob: `f3dd4b1d756becc77eb0770c580afcd3aa63a775`
- semantic generation: `b33cc4416860bd15a37f530c9daef8fb7755ae440929f93aa915d5363e31c490`
- historical contract blob read at authority: `21d51e74543ab8c6153a65224897f267d8151855`

Pinned Taste profile:

- repository: `kentrap2011-hub/stopgame-ratings-data`
- path: `gaming_taste_live.json`
- resolved commit: `5e06acad2a3dc410d4d74177efc69752ade45865`
- Git blob: `9b9926031889dbd98ba6585c57836d52c739a0bb`
- byte count: `269906`
- content SHA256: `e2d5f363778d83ec9fdd269f29744356c1b777201fb3dc0c56e898dbd99a44b4`
- profile pin SHA256: `cf4a4ecf03e72d0d77c85c5e101ce4e37ab36b8547d1bcc1deada780a8df2a6c`

The replay independently fetched the exact pinned profile and verified blob SHA, byte count and content SHA256 before Phase A semantic work.

### Immutable-authority conflict found in an older accepted report

The current file `reviews/worker_reports/progressive-fast-five-item-stop-diagnostic-01.md` contains historical identity statements in sections 3 and 5 that conflict with the immutable authority above, including a different prompt blob, work blob, semantic-generation form, profile commit and profile pin.

Per this task contract, immutable Git contents at `a1fe53af...` win. The five actual result commits also bind to the `b33cc...` generation and `cf4a...` profile pin, corroborating the immutable replay authority.

This controlled replay does not edit the older report. Its high-level conclusion that no repository-owned five-item quota was proven remains separately compatible with the replay.

## 3. Replay limitations

Directly reproduced:

- exact historical Git authority commit;
- exact historical Fast prompt and contract;
- exact historical work blob and item order;
- exact pinned Taste profile bytes and identity;
- approximately the same one-GitHub-write-per-item cadence, using isolated diagnostic artifacts only;
- the historical Fast standard: lightweight, coverage-first, no Dossier requirement, no universal Russian-review requirement, no Deep-level exhaustive recovery.

Not exactly reproducible:

- public search/index results byte-for-byte at the historical 2026-09-24 10:02Z invocation;
- Scheduled Task platform runtime/tool-budget state;
- the historical per-item tool trace, because production results did not persist query/source/tool-error telemetry.

Blindness limitation:

- `CHAT_PROTOCOL.md` START gate required reading current `DIRECTOR_TASK_BOARD.md` before replay.
- The Board currently includes an accepted summary of the earlier Chat 2 semantic review, including the fact that items 2-5 were judged overly conservative.
- The accepted semantic-quality report itself and historical result payloads were not opened until Phase B, but absolute outcome blindness was therefore not possible.
- This contamination is treated as a replay limitation and no stronger historical-causation claim is made from it.

Closeout limitation:

- The diagnostic replay traversed 12 frozen items, well beyond the critical 5->6 boundary and beyond the first eight named items.
- The frozen historical manifest contains many later items. Sequence 12 itself recorded `continue_next_item`; this task then reserved the remaining interactive execution for the mandatory Phase B comparison and durable report.
- This manual closeout is not classified as a reproduced worker stop and is not evidence about the historical Scheduled Task termination mechanism.

## 4. Item-by-item observable trace summary

Full machine-readable traces are stored under:

`reviews/reproductions/progressive-fast-controlled-shadow-replay-01/items/`

| Seq | Game | Retrieval | Replay outcome | Continuation |
|---:|---|---|---|---|
| 1 | BOKURA | not needed | `analyzed_fit / moderate / medium` | continue |
| 2 | RV There Yet? | one Steam exact-product query/page | `analyzed_fit / moderate / high` | continue |
| 3 | Uncanny Tales: Cold Road | one Steam exact-product query/page | `analyzed_fit / moderate / medium` | continue |
| 4 | Nimbatus - The Space Drone Constructor | one Steam exact-product query/page | `analyzed_fit / moderate / medium` | continue |
| 5 | Borderlands 3 | one official 2K exact-product query/page | `analyzed_not_fit / medium` | continue to item 6 |
| 6 | The Bureau: XCOM Declassified | one Steam exact-product query/page | `analyzed_fit / moderate / medium` | continue |
| 7 | Borderlands 2 | initial search no usable hit; Steam age gate; then official 2K evidence | `analyzed_not_fit / medium` | continue |
| 8 | Shadow Warrior | one Steam exact-product query/page | `analyzed_fit / strong / high` | continue |
| 9 | Shadow Warrior 2 | one Steam exact-product query/page | `analyzed_fit / strong / medium` | continue |
| 10 | Neon Abyss | not needed | `analyzed_fit / moderate / medium` | continue |
| 11 | Maneater | one developer/PlayStation exact-product page | `analyzed_fit / strong / high` | continue |
| 12 | Bloodstained: Ritual of the Night | one Steam exact-product query/page | `analyzed_fit / moderate / medium` | continue |

No item-level replay artifact records hidden chain-of-thought. They contain only prepared input, profile signals actually used, observable retrieval actions, source facts, tool status, concise outcome rationale and continuation decision.

## 5. Sequence 5 -> 6 boundary

Sequence 5 / Borderlands 3 diagnostic explicitly records:

- item 6 safe to start: `true`;
- observable runtime/tool/platform limit at that boundary: `false`;
- continuation decision: `continue_next_item`;
- expected next item: The Bureau: XCOM Declassified / App_65930 / work_id `43c59fcb26f1a23774b2547e2d3a3720618a043d5ae47795b4c619d7ed3a6eab`.

Sequence 6 diagnostic was then successfully created.

Therefore the controlled replay crosses the exact historical boundary that the real invocation did not cross.

## 6. Whether stop-at-five reproduced

Classification:

`STOP_AT_FIVE_NOT_REPRODUCED`

Observed replay facts:

1. Historical Fast rules at immutable authority `a1fe53af...` contain no five-item quota.
2. Sequence 5 completed without an item-level error.
3. The replay explicitly selected continuation to item 6.
4. Item 6 completed successfully.
5. Items 7-12 also completed under the same frozen historical manifest/profile.
6. No observable platform/tool/runtime error occurred at item 5.

This proves only that the controlled manual replay can continue past five under the historical rules and available tools. It does not prove the exact reason the real Scheduled Task stopped.

The historical stop mechanism therefore remains invocation-specific and historically unresolved without the actual Scheduled Task run trace.

## 7. Per-game comparison for original items 2-5

### RV There Yet?

Original real result:
`analysis_incomplete / insufficient_evidence` at commit `d6614b52239b9a84857b8ef8142256ebb95274ac`.

Replay:
`analyzed_fit / moderate / high`.

Replay evidence:
Steam exact-product page states that up to four players drive one RV together, use front/rear physics winches, maintain the vehicle and help each other.

Pinned-profile match:
meaningful shared play, role-like coordination and helping each other are strong positives.

Classification:
`REPLAY_SUPPORTS_NORMAL_FAST_DECISION`.

Mechanism inference:
the replay shows that a single lightweight exact-product retrieval is enough. It does not distinguish whether the original run skipped retrieval, failed retrieval, ignored retrieved evidence, or applied an overly conservative threshold.

### Uncanny Tales: Cold Road

Original real result:
`analysis_incomplete / insufficient_evidence` at commit `9dcb2e70377ad25b2dd552a9f0421fae5e5a38c1`.

Replay:
`analyzed_fit / moderate / medium`.

Replay evidence:
Steam exact-product page supplies a concrete linear first-person psychological-horror structure built around tense atmosphere, detailed surroundings, realistic human danger, exploration and a specific mystery.

Earlier accepted review:
the later independent review reached provisional `not_fit` using additional lightweight evidence about walking-simulator/low-interaction structure.

Classification:
`REPLAY_SUPPORTS_NORMAL_FAST_DECISION`.

Important nuance:
the replay and accepted review disagree on direction, but both independently show that `insufficient_evidence` was not required. This game is evidence that source selection can affect the provisional verdict direction, while the original Fast outcome was still more conservative than necessary.

Mechanism inference:
retrieval/evidence-selection/decision-threshold behavior remains unresolved. The replay does not support genuine Fast-level evidence absence.

### Nimbatus - The Space Drone Constructor

Original real result:
`analysis_incomplete / insufficient_evidence` at commit `85e4075348564251f239d7e5dedb2e4a808278dd`.

Replay:
`analyzed_fit / moderate / medium`.

Replay evidence:
Steam exact-product page gives 75+ simulated parts, survival campaign, six captains, destructible procedural planets, automation with sensors/logic, tech tree, custom weapons and mothership upgrades.

Pinned-profile match:
mastery, visible progression, development/variety and exploration with understandable effects are strong positives; technical complexity is a caution but not a blanket rejection.

Classification:
`REPLAY_SUPPORTS_NORMAL_FAST_DECISION`.

Mechanism inference:
one lightweight exact-product source was sufficient. The original mechanism still cannot be distinguished among skipped/failed/not-used retrieval and an overly high threshold.

### Borderlands 3

Original real result:
`analysis_incomplete / insufficient_evidence` at commit `01528e104fae5689a8f7399e49eb3a7738ed0218`.

Replay:
`analyzed_not_fit / medium`.

Replay evidence:
2K official exact-product page describes the original shooter-looter returning, centered on blasting enemies, collecting loot, four Vault Hunters, skill trees, abilities and customization.

Pinned-profile match:
the original Borderlands is a high-confidence 2.5/5 negative benchmark specifically because its core gameplay felt boring and visual novelty could not sustain interest.

Classification:
`REPLAY_SUPPORTS_NORMAL_FAST_DECISION`.

Mechanism inference:
this is the strongest replay case against genuine insufficiency because exact personal franchise evidence already exists and official exact-product evidence confirms continuity of the core shooter-looter loop. Exact original retrieval behavior still remains unknown.

## 8. What the replay says about retrieval behavior

For original items 2-5:

- all four had usable lightweight exact-product evidence available in the replay;
- all four searches succeeded without tool errors;
- RV, Uncanny and Nimbatus were resolved from Steam exact-product pages;
- Borderlands 3 was resolved from an official 2K exact-product page;
- no Dossier, Russian-review requirement, exhaustive multi-source research or Deep recovery was necessary.

The replay therefore does **not** reproduce a retrieval/tool failure for those four items.

It also cannot prove that the historical Scheduled Task saw the same search index or that it attempted the same queries.

Most supported conclusion:
`genuine Fast-level evidence absence is not supported by the replay`.

Historical mechanism still cannot be distinguished among:

1. original retrieval not attempted;
2. original retrieval attempted but failed or returned weaker results;
3. usable evidence retrieved but not used;
4. usable evidence used but judged under an excessively conservative threshold.

## 9. What the replay says about decision threshold

The historical Fast contract is coverage-first and lightweight. It requires trustworthy provisional moderate/strong fit or completed not-fit; it does not require Deep-level certainty.

Replay behavior shows:

- BOKURA can be decided from prepared input/profile alone;
- RV, Nimbatus and Borderlands 3 can be decided after one lightweight exact-product source;
- Uncanny can also reach a Fast decision with light evidence, although exact direction is more evidence-selection-sensitive.

This supports the conclusion that the original four consecutive `insufficient_evidence` outcomes applied a more conservative effective threshold and/or failed to use accessible light evidence.

The replay cannot isolate threshold conservatism from retrieval/evidence-use behavior because the real invocation did not persist its per-item retrieval trace.

## 10. Observable tool/runtime errors

At the critical original items 2-5:

- no replay web/tool errors occurred;
- each required retrieval returned usable exact-product evidence.

Later replay item 7 / Borderlands 2 had two non-fatal retrieval dead ends:

- an initial exact-title search returned no usable source;
- direct Steam app access returned an age-check page.

A subsequent official 2K query produced usable evidence, and the replay continued. These were not invocation-level failures and demonstrate the historical contract's intended behavior: a recoverable per-item retrieval detour does not stop later siblings.

No observable tool/runtime/platform error occurred at sequence 5 or sequence 6.

## 11. Root-cause conclusions

### CONFIRMED

- The exact historical authority for this task is commit `a1fe53af...`, worker prompt blob `03b0cba0...`, work blob `f3dd4b1d...`, semantic generation `b33cc441...`, and profile pin `cf4a4ecf...`.
- The real invocation submitted BOKURA as fit and then RV, Uncanny, Nimbatus and Borderlands 3 as `analysis_incomplete / insufficient_evidence`.
- The historical Fast rules contain no five-item quota.
- The controlled replay successfully processed item 6 and later items under the historical frozen order/profile.
- Therefore the historical stop at exactly five is **not reproduced**.
- For all four original insufficient-evidence items, the controlled replay found lightweight evidence sufficient to reach a normal Fast fit/not-fit outcome.
- Therefore the replay does **not** reproduce `insufficient_evidence` for any of the four.
- The old accepted five-item stop report contains historical identity fields that conflict with the immutable Git authority used here; immutable Git wins.

### SUPPORTED

- The four original insufficient results represent overly conservative Fast behavior relative to the intended lightweight standard.
- Genuine lack of Fast-level evidence is unlikely to explain those four outcomes.
- The historical five-item stop was not caused by a canonical five-item quota or a requirement to wait for sibling ingest.
- The historical stop is more consistent with an invocation-specific external interruption/limit or an unjustified early worker termination than with repository control-plane rules, but the replay cannot choose between those possibilities.

### STILL UNKNOWN

- Whether the historical run attempted web retrieval for RV, Uncanny, Nimbatus or Borderlands 3.
- Which exact pages/results the historical Scheduled Task saw.
- Whether a historical retrieval/tool call failed transiently.
- Whether usable evidence was retrieved but not used.
- Whether the decisive semantic defect was an overly high confidence threshold.
- The exact platform/worker stop reason immediately after Borderlands 3.
- Whether the historical run ended because of runtime/tool budget, timeout, cancellation, model/context limit, another platform interruption, or a voluntary early stop without a permitted reason.

## 12. No-production-mutation confirmation

Writes made by this task are limited to:

- one create-only diagnostic JSON per replayed item under
  `reviews/reproductions/progressive-fast-controlled-shadow-replay-01/items/`;
- this durable report.

Not performed:

- no write to `data/ai_inbox/progressive_pass1/`;
- no Fast/Deep/Dossier state/result replacement;
- no attempt reset or recovery authorization;
- no production worker run;
- no production ingest trigger;
- no workflow/contract/prompt/code modification;
- no Scheduled Task modification;
- no scheduler action.

`CURRENT_TASK.md` was not edited because this task's stricter production-safety boundary permits only the isolated replay diagnostics and final report.

## 13. Recommended Director next step

1. Treat `STOP_AT_FIVE_NOT_REPRODUCED` as the controlled-replay result. Do not implement a five-item-limit fix; no such canonical limit was reproduced or found.
2. If the exact historical stop cause is still required, inspect the actual Scheduled Task execution record immediately after Borderlands 3. The controlled replay cannot substitute for that external run record.
3. Treat the original four `insufficient_evidence` outcomes as a real Fast quality defect at the outcome/retrieval-use threshold level. The controlled replay strengthens the earlier semantic review because all four reached normal Fast decisions with lightweight evidence.
4. Do not infer one exact mechanism until historical tool telemetry is available. If that telemetry is unavailable, the next bounded design task should focus on future observability and a precise `insufficient_evidence` gate, rather than retrying consumed historical attempts.
5. Consider a separate docs-only correction of the stale immutable-authority fields inside `progressive-fast-five-item-stop-diagnostic-01.md`; do not mix that documentation correction with any semantic/runtime implementation.

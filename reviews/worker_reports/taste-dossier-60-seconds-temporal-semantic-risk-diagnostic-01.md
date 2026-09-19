# Taste dossier 60 Seconds temporal semantic risk diagnostic 01 — durable report

## 1. Task / repo / mode

- Task: `taste-dossier-60-seconds-temporal-semantic-risk-diagnostic-01`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Base/source of truth: `main`.
- Mode: `READ-ONLY DIAGNOSTIC`.
- Scope was limited to the current immutable `g000002` and the dossier for `60 Seconds! Reatomized`.
- No other repository was read, searched, changed, or used.
- No candidate, snapshot, progress, prompt, schema, contract, validator, Scheduled Task, PR, or `g000003` was changed/started.
- The only repository write in this task is this durable report.

## 2. Current snapshot / canonical state / exact g000002 artifact

Current worker index and work manifest agree on the active binding:

- snapshot: `593378be74141105830ebe7f1fb94d8942f7427bc1abb7f05430b6bfccc69a26`;
- prepared date: `2026-09-19`;
- prepared / completed / remaining: `734 / 3 / 731`;
- `full_backlog_complete: false`;
- current canonical expected sequence: `2` (worker index / current validation state);
- active prompt revision: `web-evidence-v2-early-multi-source-diversification-v1`;
- evidence contract revision: `contract-contradictions-fix-2026-09-18`;
- group size for `g000002`: 3.

Canonical files:

- `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`;
- `data/production/pre_ai/taste_steam_review_dossier_work.json`;
- `data/production/pre_ai/taste_steam_review_dossier_worker_groups/593378be74141105830ebe7f1fb94d8942f7427bc1abb7f05430b6bfccc69a26/g000002.json`.

Exact group identity:

- sequence: `2`;
- appids: `1003890, 1012880, 1018800`;
- group SHA: `bc1342223f730d0b4991f3e8d04e496cb8171fb6345db90938e946e7d6cbed89`.

Exact immutable buffered artifact:

`data/ai_inbox/taste_steam_review_dossiers/593378be74141105830ebe7f1fb94d8942f7427bc1abb7f05430b6bfccc69a26--g000002--bc1342223f730d0b4991f3e8d04e496cb8171fb6345db90938e946e7d6cbed89.json`

It was created by commit `8f42fa1bffc9634bc7498e22ad8f15b4fc5bd0af` (`buffer taste steam review dossiers g000002`).

Current `data/production/pre_ai/taste_steam_review_dossier_validation_status.json` marks this candidate `invalid`, with:

`observation 0 historical/fixed claim lacks recent current-state check`.

Therefore `g000002` is buffered transport only and has not advanced canonical progress.

## 3. Exact 60 Seconds! Reatomized descriptor

Descriptor:

- key: `App_1012880`;
- appid: `1012880`;
- title: `60 Seconds! Reatomized`;
- dossier path: `data/cache/taste_steam_review_dossiers/App_1012880.json`;
- reason: `missing_dossier`.

Candidate dossier:

- generated: `2026-09-19T08:35:00Z`;
- expires: `2026-10-09T08:35:00Z`;
- release year: `2019`;
- resolved developer corroborator: `Robot Gentleman`.

## 4. Exact risky observation and structured temporal fields

Exact observation statement:

> Russian PC player feedback reports launch-era technical problems including broken movement, display issues, and settings that did not persist.

Structured fields:

- category: `friction`;
- sentiment: `negative`;
- recurrence: `anecdotal`;
- mention count: `1`;
- evidence languages: `["russian"]`;
- evidence status: `historical`;
- source ids: `["source-002"]`;
- player-feedback ids: `["fallback-001"]`.

The wording itself is explicitly past-scoped by `launch-era`. It does not literally say those defects are current in 2026.

However, under the active V2 semantics, `historical` is not a free-form label meaning merely “an old complaint existed.” For a technical/current-state topic it is an adjudicated temporal state: the old issue is retained as historical only after a recent current-state check. That structured status therefore creates a present-state evidence obligation even though the prose sentence is past-scoped.

## 5. Bound evidence / source dates

Bound evidence for the risky observation:

### `source-002`

- type: `forum`;
- domain: `tapochek.net`;
- URL: `https://tapochek.net/viewtopic.php?t=222170`;
- source publication date: null;
- language: `russian`;
- freshness: `older`;
- evidence role: `historical`;
- player feedback: true;
- surface mode: `concrete_item_collection`.

### `fallback-001`

- source id: `source-002`;
- publication date: `2019-07-30`;
- language: `russian`;
- identity mode: `transient_author_deduped`.

The 2019-07-30 feedback record is far older than the active 365-day boundary on 2026-09-19.

No source bound to this observation has:

- `freshness:"recent"`, and
- `evidence_role:"current_state"`.

So the candidate contains valid evidence that launch-era complaints existed, but it contains no evidence resolving their current state.

## 6. Active temporal / recency rules

The active rules are internally aligned.

### Worker prompt

`config/taste_steam_review_dossier_worker_prompt.md`, section **Recency and temporal truth**:

- search recent feedback first;
- dated evidence is `recent` at age <=365 days and `older` beyond 365 days;
- for bugs, performance, compatibility, technical state, localization, and regional/service issues, recent evidence dominates launch-era evidence;
- an issue may be represented as `historical` when recent evidence shows it fixed or materially reduced;
- unresolved old-vs-current temporal state is `uncertain`;
- current observations need recent current-state support;
- historical observations need historical evidence **plus a recent current-state check**;
- durable observations need durable-trait evidence.

The same prompt's **Adaptive bounded stopping** says research should expand for temporally conflicted/sparse evidence and stop only when further research is unlikely to materially change the dossier.

### Web evidence contract

`config/taste_steam_review_dossier_web_evidence_contract.json`, `recency`:

- `recent_max_age_days: 365`;
- current-state topics explicitly include `bugs`, `performance`, `compatibility`, `technical_state`, `localization`, and `regional_service_state`;
- `current_state_requires_recent_support: true`;
- recent evidence dominates old evidence for current-state topics;
- launch-only issue with recent fix/material reduction -> `historical`;
- old evidence remains valid for durable traits such as gameplay/story/structure/repetition/difficulty/durable friction;
- unresolved temporal evidence -> `uncertain`.

### Dossier schema

`config/taste_steam_review_dossier_schema.json`:

- `current_requires_recent_current_state_source: true`;
- `historical_requires_historical_and_recent_current_state_sources: true`;
- `durable_requires_durable_trait_source: true`.

### Strict validator

`scripts/taste_steam_review_dossier_strict.py`, observation validation:

- `current` requires a referenced `current_state + recent` source;
- `historical` requires a referenced historical source **and** a referenced `current_state + recent` source;
- `durable` requires a referenced `durable_trait` source.

For this exact candidate, the strict failure is therefore mechanically derivable from structured fields; no prose interpretation is needed to reject it.

## 7. Durable-vs-current-state semantic analysis

This observation is **not a durable trait**.

“Broken movement”, display/startup behavior, and settings persistence are technical-state topics. The old 2019 report can remain evidence of launch-era history, but those facts cannot be treated like durable gameplay/story/art/music traits whose old evidence remains sufficient by itself.

The sentence is explicitly historical in wording. The problem is not that the sentence secretly says “the game is broken now.” The problem is that the worker promoted an old technical complaint to the structured V2 state `historical` without performing the recent comparison that gives that status its meaning under the active contract.

In other words:

- 2019 evidence proves **then**;
- `historical` under V2 also requires evidence about **now**;
- the candidate only proves the first half.

## 8. Whether recent support is actually required

Yes.

Recent support is required because this is a technical/current-state topic and the worker emitted `evidence_status:"historical"`.

The active contract does not permit `historical` to mean “old source only.” It specifically requires a recent current-state check.

If no usable recent evidence can be obtained, the active rules already provide `uncertain` for unresolved temporal state; the worker cannot declare the old technical issue resolved into `historical` merely from its age.

The cutoff for a dated source on 2026-09-19 is mechanically <=365 days, i.e. approximately 2025-09-19 or newer.

## 9. Bounded recent-source retrieval result

Classification: **`recent_source_reachable`**.

Diagnostic budget used:

- 7 / 8 web/search queries;
- 5 page-open/read operations, below the 16-page ceiling;
- no candidate was patched and no production write was made.

Production-style exact-product retrieval found the current Steam Community Support surface for appid `1012880`:

`https://steamcommunity.com/app/1012880/discussions/1/`

The current support index exposes multiple 2026 technical topics in the same issue families, including mouse/input problems, startup/display problems, settings resetting, and frame drops. The listing explicitly transitions from current-year month/day rows to `28 Nov, 2025`, so the preceding Jan-Aug rows are current-year 2026.

More importantly, a concrete exact-app child topic was directly reachable:

`https://steamcommunity.com/app/1012880/discussions/1/573795560006462989/`

It is dated 16 July in the current 2026 support listing and describes a black-screen-on-start condition. That is recent, exact-product, PC player-feedback evidence in a technical/display/startup issue family.

This diagnostic does **not** claim that one recent anecdotal topic proves every 2019 sub-issue is still current or recurrent. It proves the narrower fact required for diagnosis: suitable recent exact-product current-state player-feedback was reasonably reachable inside the active bounded retrieval strategy, so stopping after the 2019 source was premature.

A current Russian-language item was not required to establish this retrieval miss: the dossier already satisfied the separate Russian-attempt requirement with bound Russian historical feedback, while the temporal current-state check may use valid exact-product player feedback in another language under the active contract.

## 10. Prepublication / strict validator path

### Scheduled-worker publication path

The active worker prompt explicitly states that GitHub, not Scheduled ChatGPT, runs canonical strict/buffered validation **after candidate publication**.

It also states that `scripts/taste_steam_review_dossier_prepublication.py` is CI/developer parity tooling only and is **not** a Scheduled-runtime gate; the worker must not execute or emulate repository-local Python before create-only publication.

Therefore this candidate did **not** “pass” a mandatory repo-local prepublication gate. That gate is intentionally not part of Scheduled publication.

### What the optional parity utility would do

`scripts/taste_steam_review_dossier_prepublication.py::validate_prepublication_artifact` calls:

`taste_steam_review_dossier_buffered.validate_buffer_artifact`

and that in turn calls:

`taste_steam_review_dossier_strict.validate_dossiers_against_expected_items`.

So if the same artifact were evaluated by the optional parity utility, it would fail on the same missing recent-current-state condition.

### Authoritative post-publication validation

`scripts/taste_steam_review_dossier_buffered.py::validate_buffer_artifact` invokes the strict dossier validator before a group can enter the accepted contiguous prefix.

Current `taste_steam_review_dossier_validation_status.json` confirms the actual result:

- sequence 2;
- validation: `invalid`;
- canonical position: `expected`;
- validator error: `observation 0 historical/fixed claim lacks recent current-state check`.

Canonical progress remains at expected sequence 2.

## 11. Mechanically detectable vs semantic-only

Two different questions must be separated.

### Mechanically detectable

The published candidate has:

- `evidence_status:"historical"`;
- a historical source;
- no referenced `current_state + recent` source.

That violates an explicit structured invariant and **is mechanically detectable**. The strict validator correctly detects it.

### Semantic judgment

Whether the correct repaired classification should ultimately be `current`, `historical`, or `uncertain` requires semantic reading of recent evidence and comparison with the old technical complaints.

That deeper classification is not something the strict validator claims to infer from arbitrary prose, and this diagnostic does not attempt to repair it.

## 12. Primary defect classification

**Primary classification: `recent_source_retrieval_miss`.**

Pipeline order:

1. Worker found a 2019 Russian technical complaint.
2. Active rules required a recent current-state check before a technical observation could be finalized as `historical`.
3. The candidate nevertheless recorded `research_state:"sufficient"` and `stop_reason:"evidence_stable"`.
4. Bounded diagnostic retrieval later found suitable recent exact-product technical evidence well inside the same 8/16 ceiling.
5. The worker then serialized the unsupported `historical` state.
6. GitHub strict validation correctly rejected the candidate after publication.

The first defect is therefore the worker's premature retrieval/stop decision, not GitHub validation.

The `historical` classification is unproven as serialized, but that is downstream of the missing recent check rather than a separate independent blocker: after the required recent retrieval, synthesis can choose the correct existing status based on the evidence.

## 13. Contract / prompt / validator internal consistency

No `contract_or_prompt_contradiction` was found.

The relevant layers agree:

- prompt: historical technical claims need a recent check;
- evidence contract: technical state is current-state-sensitive and historical requires temporal resolution;
- schema: historical requires historical + recent current-state sources;
- strict validator: enforces exactly that shape;
- current validation status: rejects this candidate for exactly that reason.

The prior early-multi-source-diversification implementation also explicitly preserved the 365-day recency/current-state semantics. It changed retrieval ordering, not evidence admissibility or temporal rules:

`reviews/worker_reports/taste-dossier-early-multi-source-diversification-implement-01.md`.

Relevant decision rationale is also aligned:

- `PROJECT_DECISIONS.md` — TASTE-006 buffered transport;
- TASTE-007 multi-source web evidence and temporal semantics;
- TASTE-008 Russian retrieval/diversification.

## 14. Impact on immutable g000002

`g000002` must remain unchanged.

Current impact:

- immutable candidate exists;
- it is buffered only;
- strict validation marks it invalid;
- it cannot enter the canonical contiguous accepted prefix;
- canonical expected sequence remains 2;
- no overwrite, alternate `g000002`, manual progress repair, or `g000003` work is appropriate in this task.

This is the designed fail-closed behavior of the buffered architecture.

## 15. Minimal next-step design direction

The smallest design direction is to make the existing temporal retrieval obligation an explicit **pre-stop retrieval gate** for the Scheduled worker:

before `research_state:"sufficient"` / `stop_reason:"evidence_stable"` is allowed, any proposed `historical` observation in a current-state-sensitive topic (bugs/performance/compatibility/technical/localization/regional service) must already have at least one bound recent `current_state` source; if it does not and budget remains, the worker must continue bounded exact-product current-state retrieval rather than stop.

This does not change evidence semantics, validation authority, source admissibility, or the 8/16 ceilings.

Architecture preflight for this direction:

1. bounded public-web retrieval remains owned by Scheduled ChatGPT;
2. GitHub remains owner of the canonical prompt/contract and post-publication strict validation;
3. no control-plane responsibility moves into interactive chat;
4. no new queue, retry loop, recurring stage, quota, or scheduler is introduced.

## 16. Unresolved

Not required to resolve the primary defect:

- whether all three 2019 sub-issues still occur in 2026;
- whether current evidence is strong enough to classify the issue family as `current` rather than `uncertain`;
- whether a recent Russian-language concrete item can also be found.

Those are repair/synthesis questions for a future authorized task. This diagnostic only establishes that the required recent check was missing and reasonably retrievable.

## 17. Status

`complete_recent_source_retrieval_miss`

## 18. Exactly one recommended next step

Create one narrow follow-up task that strengthens the existing worker retrieval/stopping behavior so that a current-state-sensitive observation cannot be finalized as `historical` while its bound evidence lacks a <=365-day `current_state` source: while the existing 8/16 budget remains, continue bounded exact-product recent retrieval; only after that evidence is obtained may synthesis choose `historical`, otherwise use the already-defined unresolved temporal path instead of `evidence_stable`.

Do not change validator semantics or create a new runtime stage as part of that fix.

## 19. Efficiency / reusable lesson

The fastest reliable diagnostic route for this class of failure is:

1. worker index + exact group descriptor;
2. `taste_steam_review_dossier_validation_status.json`;
3. exact immutable buffered artifact;
4. only the recency sections of prompt/evidence/schema;
5. strict observation validation;
6. bounded external retrieval only if the structured rule proves a recent check is required.

That route immediately separated transport publication from canonical acceptance and avoided falsely blaming the validator.

The main time cost in this diagnostic was reconstructing the exact artifact/rule chain and verifying recent-source reachability without exceeding the 8/16 budget. A reusable improvement is to keep using the current validation-status artifact as the first post-publication pointer to the exact invalid group and validator error; no new route file change is necessary for this case.

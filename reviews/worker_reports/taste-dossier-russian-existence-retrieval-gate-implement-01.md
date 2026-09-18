# Taste dossier Russian existence/retrieval gate implement 01

## Task / repository / mode

- Task: `TASTE_DOSSIER_RUSSIAN_EXISTENCE_RETRIEVAL_GATE_IMPLEMENT_01`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Base/source of truth: `main`
- Mode completed: IMPLEMENT / ACTIVATE / VALIDATE
- Scheduled Task `Run now`: **not launched**
- Other repositories: **not read, searched, changed, or used**

## START / architecture preflight

`CHAT_PROTOCOL.md` was read first and its START gate was followed before implementation. The bounded route and ownership contracts confirmed:

- GitHub/GitHub Actions remains the control plane for schema/contract binding, immutable group plan, strict validation, canonical persistence, snapshot rebuild, recovery and completeness;
- Scheduled ChatGPT remains only the bounded semantic/evidence retrieval worker;
- no control-plane responsibility moved to ChatGPT;
- no new recurring stage, queue, retry/healing loop, backlog manager, checkpoint model or production quota was introduced;
- group/checkpoint size remains `3`;
- buffered canonical acceptance remains maximal-valid-contiguous-prefix from the GitHub-owned expected sequence.

## Canonical rule implemented

The old ambiguous Russian attempt model was replaced with one machine-readable field, `evidence.russian_attempt`, with exactly four active states:

1. `found_and_used` — at least one attributable item-level Russian/mixed player-feedback record is bound to an observation/conflict.
2. `searched_no_existence_signal` — bounded good-faith search did not establish a reliable exact-product/exact-appid Russian **player-activity** existence signal.
3. `existence_established_retrieval_unresolved` — exact-product Russian player-feedback existence is proven, but no contract-usable attributable item-level Russian/mixed record was obtained within hard bounds.
4. `existence_established_access_unresolved` — exact-product Russian player-feedback existence is proven, but source access prevents item-level resolution.

Only states 1 and 2 are complete-dossier states. States 3 and 4 are explicit retrieval/access failures and the strict validator rejects a complete dossier carrying either one. Therefore a three-game group cannot be published when one planned game is in a proven-existence unresolved state.

This directly enforces the task rule: **proven existence + no usable item-level record is not ordinary absence**.

## Existence signal versus usable evidence

The active evidence contract now states mechanically that an exact-product existence signal:

- may be a reliable exact-product/exact-appid player-activity signal such as a nonzero Russian-language review population or exact-product community player activity;
- is discovery state only;
- is not a `player_feedback_record`;
- cannot support an observation or conflict;
- cannot create `mention_count` or recurrence;
- cannot satisfy `found_and_used`.

A Russian-rendered UI/page by itself does not prove Russian player activity. Professional/journalistic Russian material may be context/relevance evidence but is not player feedback and does not satisfy the retrieval gate.

## Discovery behavior

Within the unchanged hard bounds of <=8 web-search queries and <=16 opened/read source pages per game, the worker prompt/contract now requires the bounded Russian path to use:

- exact descriptor title plus release year and/or exact appid;
- Russian-language query variants;
- when unresolved and budget remains, a relevant site-specific player-feedback/community search;
- exact-product Steam Community/discussion/review surfaces as a natural option where available, without making Steam mandatory or creating a fixed website quota;
- after a reliable existence signal, remaining bounded search is directed to attributable item-level retrieval instead of repeated aggregate/list lookups.

The bounds remain safety ceilings, not targets.

## Exact-product identity hardening

The strict validator now rejects a Steam player-feedback source when its URL explicitly exposes `/app/{appid}/` and that appid differs from the exact dossier appid.

This prevents base-game Steam Community/review evidence from satisfying an exact DLC/edition retrieval gate. The existing title + release year + appid identity rules remain in force; no fuzzy substitution was added.

## Files changed by implementation PR

Implementation PR #47 changed only task-scoped files:

- `CURRENT_TASK.md`
- `PROJECT_DECISIONS.md`
- `PROJECT_ROUTES.md`
- `config/taste_steam_review_dossier_schema.json`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/taste_steam_review_dossier_strict.py`
- `scripts/test_taste_steam_review_dossier_contract_gaps.py`
- `scripts/test_taste_steam_review_dossier_language_binding.py`
- `scripts/test_taste_steam_review_dossier_semantic_consistency.py`
- `scripts/test_taste_steam_review_dossier_strict_recovery.py`

Canonical rationale was recorded as `TASTE-008 — Russian existence proof creates an item-level retrieval gate`.

## Deterministic regression matrix

The existing semantic-consistency suite now includes:

- **RUS-GATE-01** — audited Tetris® Effect: Connected exact-appid discovery shape and contract guidance: exact appid/title + Russian term + site-specific Steam Community/discussion path, while preserving <=8 / <=16 and no fixed source quota.
- **RUS-GATE-02** — BG3 Digital Deluxe DLC and Hellish Quart otherwise-sufficient dossiers are rejected when exact-product existence is represented as `existence_established_retrieval_unresolved`.
- **RUS-GATE-03** — a synthetic otherwise-sufficient dossier with genuine `searched_no_existence_signal` validates successfully.
- **RUS-GATE-04** — an aggregate/context existence signal remains non-player-feedback and cannot be promoted into attributable feedback; a Steam Store app page marked as player feedback is rejected.
- **RUS-GATE-05** — base-game Steam appid feedback is rejected for the exact BG3 Digital Deluxe DLC appid.
- **RUS-GATE-06** — proven existence plus source-access failure is rejected as `existence_established_access_unresolved`, not ordinary absence.

## PR validation

Implementation PR: **#47**

- merge commit on `main`: `e50f0f93e73ea7c17fadf8684dfce27d4b2052c1`
- focused workflow: `Validate buffered Steam review dossier runtime`
- final successful PR run: **35340626056** / run #68
- result: **success**
- compile: success
- execution ownership validation: success
- daily snapshot regression: success
- buffered submission regression: success
- same-day preservation regression: success
- strict recovery regression: success
- prepublication parity regression: success
- contract-gap regression: success
- language binding regression: success
- semantic consistency regression including RUS-GATE-01..06: success
- package identity regression: success
- parallel candidate validation / contiguous-prefix regression: success

An earlier PR run #67 failed only because one existing test still hard-coded the previous `worker_prompt_revision`. The assertion was updated to the new content-complete binding; no validator rule was weakened. The full focused suite was then rerun successfully.

## Activation

Merging the changed dossier contract/schema/prompt paths triggered the existing GitHub-owned `Build pre-AI deterministic payload` push workflow automatically.

- activation run: **35340697550** / run #132
- trigger: normal push to `main`, not manual dispatch
- result: **success**
- dossier steps `Prepare fixed daily full Steam review dossier backlog`, `Reconcile already-present dossier inbox state`, and `Regression test fixed daily dossier snapshot control plane`: all success
- atomic pre-AI commit: `2c5da1ecfd53268e340edc91f47c199d4ddd6018`

No Scheduled Task `Run now` was used.

## Fresh snapshot / binding validation

After activation, canonical work/index were rebuilt under the new content-complete compatibility binding:

- snapshot: `093952f414cc1020388559e4f390593d921df2b96fd64df831450feec3258296`
- previous snapshot: `00072072b0b382e6b973f448ce00b4aaaeccb2dbe355ca323de1785ccc0bd34c`
- canonical expected sequence: `1`
- prepared / remaining: `732 / 732`
- completed: `0`
- group size: `3`
- group count: `244`
- full backlog complete: `false`
- evidence contract revision: `russian-existence-retrieval-gate-2026-09-18`
- worker schema revision: `russian-existence-retrieval-gate-2026-09-18`
- worker prompt revision: `web-evidence-v2-russian-retrieval-gate-v1`
- index and exact `g000001` descriptor bindings: exact match

Current `g000001` is now:

1. `2378500` — Baldur's Gate 3 - Digital Deluxe Edition DLC
2. `1000010` — Crown Trick
3. `1000360` — Hellish Quart

The normal fresh rebuild therefore did not preserve the previous stale group projection by hand.

The old live run had published no candidate artifact. The current repository tree has no `data/ai_inbox/taste_steam_review_dossiers` directory, so there was no old-snapshot buffer artifact requiring quarantine.

## Validation conclusion

Status: **implemented_activated_validated**

The requested production rule is active in machine contract, worker prompt and canonical strict validation:

> if exact-product Russian player feedback existence is proven but the worker cannot obtain at least one contract-usable attributable item-level Russian/mixed record, the result is a retrieval/access failure and cannot be serialized as ordinary `searched_no_existence_signal` or accepted as a complete dossier.

No Scheduled Task live run was launched, as required.

## Unresolved

None within this IMPLEMENT / ACTIVATE / VALIDATE task. A future live Scheduled-worker acceptance, if desired, is a separate task and was intentionally not started here.

## Efficiency / reusable lesson

The existing route, strict validator and semantic-consistency suite were reused instead of creating a new validator or recurring stage. The only CI failure came from an obsolete hard-coded prompt revision; keeping content-binding assertions centralized or derived from the active evidence contract would make future same-class binding migrations faster and reduce maintenance-only reruns.

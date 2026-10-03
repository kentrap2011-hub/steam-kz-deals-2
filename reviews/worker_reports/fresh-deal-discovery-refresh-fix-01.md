# Fresh deal discovery refresh fix 01

## 1. Task

Task: `WORKER_TASK_FRESH_DEAL_DISCOVERY_REFRESH_FIX_01.md`.

Goal: repair the existing GitHub-owned Steam discovery -> shortlist -> mailing -> pre-AI -> Progressive -> visual handoff so a newly discounted game that was absent from the prior candidate universe can enter the normal pipeline without adding another scheduler/control plane or fabricating semantic output.

## 2. START / current-main reconciliation

START gate was executed from current `main`: `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, current-state `DIRECTOR_TASK_BOARD.md`, `PROJECT_ROUTES.md`, relevant `PROJECT_DECISIONS.md` / `KNOWN_WORKER_PITFALLS.md`, the task file, and the canonical production workflows/scripts were inspected before implementation.

Initial diagnosis base: `b4f23d27901ea64beb8792f9786ff8fa7322d140`.

Before merge validation the branch was reconciled again onto current `main` `9fb07c7cd1b93bd9a23649a35c8e7385de3f8f77`. The five commits added to `main` since the prior synchronization did not overlap any PR-touched file. The validated implementation head before this report-only finalization was `2de1a4b66c96908b1b80a238903dd14289004c59`; comparison at validation time: ahead 1, behind 0.

## 3. Reproduction

Current-main evidence before implementation:

- `data/production/manifest.json.updated_at_utc = 2026-09-23T23:12:47.031485+00:00`;
- `data/production/shortlist/index.json.source_updated_at_utc = 2026-09-23T23:12:47.031485+00:00`, 609 candidates;
- `data/production/mailing/index.json.source_updated_at_utc = 2026-09-23T23:12:47.031485+00:00`, 609 candidates;
- `data/production/pre_ai/store_snapshot.json.observed_at_utc = 2026-10-01T18:15:33.903961+00:00`, but `discovery_source_updated_at_utc = 2026-09-23T23:12:47.031485+00:00`;
- AppID `1233570` was absent from mailing, Store snapshot, Progressive candidate context, PASS 1 work and PASS 2 work.

The historical defect is therefore reproducible: refreshing current Store price/discount state for the existing mailing identities cannot discover an identity that is not already in that mailing universe.

## 4. Root cause

Fresh catalog discovery is owned by the existing `Steam KZ production shortlist` GitHub Actions workflow and `scripts/steam_partial_publish_runner.py` / `scripts/steam_production.py`.

The discovery workflow already had the intended nightly schedule. The stale 2026-09-23 universe was not an intentional pin. Later deterministic/pre-AI executions were able to refresh Store commercial state against the old mailing set without an explicit contract proving that discovery had been rebuilt for the same production cycle. That allowed a fresh price observation to look operationally current while the identity universe remained old.

The fix therefore repairs the freshness handoff and fail-closed semantics; it does not introduce another catalog owner or scheduler.

## 5. Existing ownership chain

Canonical ownership remains:

1. `.github/workflows/steam-test.yml` / `scripts/steam_partial_publish_runner.py` — fresh Steam KZ catalog discovery and deterministic shortlist.
2. `.github/workflows/build-mailing-feed.yml` — canonical compact mailing projection of the shortlist.
3. `.github/workflows/build-pre-ai-store-snapshot.yml` / `scripts/build_pre_ai_store_snapshot.py` — current Store offer classification for the freshly discovered identities.
4. Existing pre-AI builders — family/content/taste/history/deal projections.
5. Existing Progressive work builders — current candidate context and PASS work.
6. Existing `build-daily-visual-payload.yml` / final visual producer — publication.

No ChatGPT Scheduled Task, browser discovery path, retry daemon, second recurring schedule, second shortlist or second catalog authority was added.

## 6. Why Catalyst was absent

AppID `1233570` was absent before Store refresh. Store refresh requests only identities supplied by `data/production/mailing/index.json`; therefore it could update or remove already-known offers but could not invent/discover Catalyst. Because the identity was missing before pre-AI materialization, it never reached Taste, Progressive, ranking or visual publication.

Catalyst is only a regression probe in tests; no production code branches on AppID `1233570`, title, EA, or this exact sale.

## 7. Chosen fix

Implemented within the existing owner path:

- added `scripts/discovery_freshness.py` as a deterministic freshness/binding guard;
- `build_pre_ai_store_snapshot.py` now requires authoritative discovery chain alignment before making a current Store snapshot;
- Store snapshot exposes the discovery/commercial relationship and refuses a stale candidate universe;
- commercial visual refresh validates the exact fresh discovery binding instead of treating a newer Store observation alone as sufficient;
- final visual metadata carries the relevant discovery freshness provenance;
- the existing collector search remains the source of new identities and still applies the ordinary shortlist rules;
- current exact semantic cache reuse remains binding-driven; a genuinely new candidate has no reusable exact cache entry and enters the existing `ai_required` path rather than receiving fabricated fit.

Existing expired/inactive offer classification remains in force.

## 8. Freshness contract

The new contract records/checks:

- discovery generated timestamp;
- commercial Store observation timestamp;
- manifest -> shortlist -> mailing timestamp alignment;
- candidate-count alignment across that chain;
- source completeness / known catalog gaps;
- discovery age at commercial observation;
- production-cycle date in the existing Samara production timezone;
- `candidate_universe_rebuilt_for_current_cycle`;
- explicit `price_refresh_can_substitute_for_discovery_refresh = false`.

A stale or mismatched discovery universe now fails closed before a Store-price refresh can be treated as current recommendation-set freshness.

## 9. New-candidate lifecycle after fix

For a newly appearing discounted game:

1. existing Steam catalog discovery sees the identity;
2. existing broad/refined shortlist rules decide eligibility;
3. eligible identity enters canonical shortlist and mailing;
4. pre-AI Store snapshot classifies the current active offer;
5. deterministic family/context artifacts are rebuilt on the new mailing source timestamp;
6. exact reusable semantic state is preserved only when immutable/current bindings match;
7. a genuinely new identity receives existing pending semantic work (`ai_required`), never fabricated Taste;
8. existing Progressive/Dossier/Deep workers remain the only semantic paths;
9. later visual publication can include it once existing semantic/publication requirements are satisfied.

## 10. Regression coverage

Deterministic task regressions:

- `scripts/test_discovery_freshness.py`: 9/9 PASS;
- `scripts/test_fresh_deal_discovery_refresh.py`: 11/11 PASS;
- `scripts/test_steam_review_fallback.py`: 6/6 PASS;
- expired-offer guard: PASS;
- commercial refresh tests: PASS;
- Steam partial publish regressions: PASS;
- production output ownership: PASS;
- pre-AI deal contract guard: PASS;
- visual freshness receipt: PASS;
- visual material freshness guard: PASS after CI checkout wiring fix;
- backlog disposition validator regression: PASS;
- canonical backlog validation: PASS after PR base/head wiring fix;
- execution ownership validation, Progressive personalization and PASS 1 are included in the green regression job.

PR-head CI on the latest-main-synchronized implementation head `2de1a4b66c96908b1b80a238903dd14289004c59`:

- `Steam KZ production shortlist` run `37120329209`: SUCCESS;
- `Validate backlog dispositions` run `37120329195`: SUCCESS;
- `Validate package purchase value` run `37120329193`: SUCCESS;
- `Validate buffered Steam review dossier runtime` run `37120329203`: SUCCESS;
- `Validate Progressive PASS 2 core` run `37120329194`: SUCCESS.

Two CI wiring defects were diagnosed while finishing PR #140:
- original run `37038405284` failed because the PR regression checkout was shallow while `test_visual_material_freshness_guard.py` requires historical git objects; fixed with `fetch-depth: 0`;
- subsequent run `37119392277` reached that historical test successfully, then failed because `validate_backlog_dispositions.py` was called without its required `--base/--head`; fixed by passing the PR refs explicitly.

Neither failure was a discovery implementation failure.

## 11. Live acceptance

A safe live production refresh was not manually dispatched from this worker chat because the available GitHub connector exposes read/PR/file operations and reruns, but no `workflow_dispatch` mutation. The task explicitly forbids manually editing production data as a substitute.

Implementation-level acceptance is complete and green. The existing production workflow remains the sole owner of live discovery. Merging this PR changes the existing workflow/script paths on `main`, so the existing push architecture can own the next production discovery run; no new scheduler is needed.

## 12. Catalyst current outcome

Public Steam currently shows Mirror's Edge Catalyst AppID `1233570` in an active 95% sale ending October 8, 2026. Exact Kazakhstan canonical qualification was not fabricated here because the GitHub-owned KZ production collector was not manually dispatched from this chat.

Therefore the current canonical stage remains: **live KZ discovery acceptance pending**. The deterministic fixture proves that if the fresh KZ catalog contains Catalyst with an active offer satisfying the ordinary existing quality/price/discount gates, it can now enter the canonical candidate universe and then receive normal pending semantic work.

## 13. Boundaries preserved

Not changed:

- RANK-013 ordering policy;
- 60/40 score geometry;
- Deep/Dossier semantic contracts;
- Russian translation behavior;
- accepted expired-sale filtering semantics;
- giveaway ownership;
- browser/UI read-only architecture;
- canonical Taste profile;
- taste-scoring/questionnaire work;
- ChatGPT Scheduled Tasks.

No second catalog owner, scheduler, queue or semantic execution path was added.

## 14. Exact PR/commit/run refs

- PR: #140 — `Fix stale deal discovery freshness handoff`.
- original pre-sync PR head: `681591b1b8d1d757573acfa4d1e6916ecc59f440`;
- first synchronization base: `7a53dc8a3ca6f247711df38733e403271872825d`;
- latest synchronization base: `9fb07c7cd1b93bd9a23649a35c8e7385de3f8f77`;
- latest validated implementation head: `2de1a4b66c96908b1b80a238903dd14289004c59`;
- historical regression checkout fix: `d29c8afe55dbf8559b3a5b99d12f3b04a82004d9`;
- backlog-validator invocation fix: `b738677364086feeba35d863006464b08efb056b`;
- failed run proving shallow-history wiring defect: `37038405284`, job `110942196175`;
- failed run proving missing backlog args after first fix: `37119392277`, job `111192397915`;
- green latest task regression run: `37120329209`;
- green latest backlog validation run: `37120329195`;
- green latest companion validation runs: `37120329193`, `37120329203`, `37120329194`.

## 15. Status

`implementation_complete_live_refresh_pending`

Implementation and all required PR-level deterministic/ownership/backlog/Progressive validations are green on a branch synchronized with current `main`. Only the task's live KZ production refresh acceptance remains pending because this worker surface cannot dispatch the existing workflow and production data was not edited manually.

## 16. Recommended next step — exactly one bounded next action

After PR #140 is merged, verify the task's live-acceptance criteria on the resulting existing GitHub-owned production refresh: discovery timestamp advance, rebuilt candidate universe, Catalyst ordinary-gate outcome, and normal semantic-work materialization.

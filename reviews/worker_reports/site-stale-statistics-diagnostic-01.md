# Site stale statistics diagnostic 01

## Task / scope

- Task: `SITE-STALE-STATISTICS-DIAGNOSTIC-01`.
- Repository/source of truth: `kentrap2011-hub/steam-kz-deals-2@main`.
- Mode: READ-ONLY diagnostic. No production/state/workflow/UI/Scheduled Task fix was made.
- Pinned final diagnostic source anchor: `a6d864e9e2ccdae192f47c8880ee2b3e9e272c36` (2026-10-07T09:49:13Z).
- Production moved while diagnosis was running, so observed UI, final Pages artifact, and pinned canonical state are recorded separately instead of mixing moving-`main` reads.

## Current canonical values

At pinned anchor `a6d864e...`:

Canonical Deep work: `data/production/pre_ai/progressive_pass2_work.json`, blob `9857db95df9114809e61b1f0d08a9b2fc3a6a237`.

- coverage target: 2301
- first-pass attempted: 166
- authoritative completed: 147
- fit: 133
- not-fit: 14
- incomplete/recovery: 19
- waiting for Dossier: 2132
- ready/pending: 3
- normal first-pass remaining: 2135
- remaining until all authoritative: 2154
- work items: 3

At diagnostic start, before a concurrent Dossier drain, the same authoritative totals were `147 / 133 / 14 / 19`, but waiting/ready were `2135 / 0` and `items=[]`. The later `2132 / 3` change is normal live queue movement and is not the stale-site defect.

Canonical translation status: `data/production/pre_ai/chatgpt_ru_description_status.json`, blob `a941f93b6b4189c5e0a44dbe27dc084355f1fae2`.

- untranslated games: 813
- translation diagnostics: 1
- last successful translation: `2026-10-05T12:48:19.220279+00:00`
- last translation attempt: `2026-10-05T12:48:19.220279+00:00`
- status generated: `2026-10-06T02:02:58.782061+00:00`

## Exact UI / published source

The Statistics page does not read Deep or translation canonical files directly.

- `web/app.js`: `DATA_URL='data/current.json'`; it fetches with `cache:'no-store'`.
- `renderStatisticsView()` passes only `data.processing_status` to the statistics UI.
- `web/progressive-personalization-ui.js::statisticsSections()` maps the visible Deep and translation labels directly from `processing_status`.
- `.github/workflows/deploy-visual.yml` stages the site with:
  `cp data/production/visual/current.json web/data/current.json`.

Therefore the exact path is:

`canonical Deep/translation state`
→ `scripts/progressive_personalization.py::build_processing_status()/stamp_processing_status()`
→ `scripts/build_final_visual_payload.py`
→ `data/production/visual/current.json`
→ deploy copies it to `web/data/current.json`
→ Pages artifact
→ browser Statistics rendering.

### Artifact matching the user-observed Deep values

Deploy run `37506878989` / #1307, Pages artifact `11432311542`, contains `data/current.json` blob `bba35bbc838bd3f9e6337cdbcacab4e91956460a`, generated `2026-10-06T17:51:49.479968+00:00`.

It contains exactly the reported Deep block:

- total: 2293
- authoritative completed: 117
- fit: 104
- not-fit: 13
- incomplete/recovery: 18
- waiting Dossier: 2135
- ready/pending: 23
- remaining authoritative: 2176
- Deep last write: `2026-10-05T16:29:10+00:00` = 05.10 20:29 at +04.

The same artifact contains exactly the reported translation block:

- untranslated: 813
- diagnostics: 1
- success/attempt: `2026-10-05T12:48:19+00:00` = 05.10 16:48 at +04.
- bound Russian status blob: `a941f93b6b4189c5e0a44dbe27dc084355f1fae2`.

So the user's original screen was not inventing those values: they were real published Pages bytes.

### Latest Pages artifact during diagnosis

Deploy run `37601972850` / #1351 succeeded at 2026-10-07T09:38Z and published Pages artifact `11472514317`.

Its `data/current.json` is blob `5232ecd694ce8d87999601125bcd2052db6f7763`, generated `2026-10-06T18:14:04.340724+00:00`, from canonical visual commit `d5193b17a684856e82fb7266e68103f0290fb270`.

It is newer than the user's observed artifact, but still behind canonical Deep:

- total: 2291
- first-pass attempted: 147
- authoritative completed: 128
- fit: 114
- not-fit: 14
- incomplete/recovery: 19
- waiting Dossier: 2135
- ready/pending: 9
- remaining authoritative: 2163
- Deep last write: `2026-10-06T18:12:59+00:00`.

Translation in this latest artifact is still exactly canonical: `813 / 1 / 2026-10-05T12:48:19Z / 2026-10-05T12:48:19Z`, with the exact current translation-status blob `a941f93...`.

## First stale stage / root cause

The first causal stale boundary for current Deep truth is **after fresh full-visual candidate generation and before canonical visual persistence**, at `Validate generated card explanations`.

Latest directly relevant Deep-driven full visual build inspected:

- Deep ingest run `37569270632` / #466: success.
- Downstream `Build daily visual payload` run `37569298594` / #1390: failure.
- Scope detection correctly saw stale Deep provenance and required a full build:
  `PROGRESSIVE_SCOPE ... compatible=false ... reason=progressive_pass2_state_provenance_mismatch`.
- The producer successfully built a fresh candidate:
  `visual progressive items=2282 total=2296 fit=150 incomplete=29 not_analyzed=2103`
  and `VISUAL_FINAL_BUILD=BUILT`.
- The next gate failed:
  `CARD_EXPLANATION_VIOLATION=Tetris® Effect: Connected: positive contains commercial/ranking-only language`
  followed by `CARD_EXPLANATION_VALIDATION=FAIL count=1`.
- Freshness receipt:
  `degraded/no_fresh_build reason=canonical_persistence_failed`.

Thus current Deep truth reaches routing and the visual producer, but the candidate is rejected before `data/production/visual/current.json` can be committed. That is earlier than Pages/browser and is the primary root cause of the continuing 128→147 Deep lag.

The code-level incompatibility is bounded:
- `scripts/card_explanation_policy.py::deep_score_reasons()` copies accepted linked Deep score-finding `text_ru` into player-facing `why_fit`;
- `scripts/validate_card_explanations.py` rejects any positive `why_fit` containing commercial/ranking tokens such as `рейтинг`, `score`, `rank`, `цена`, or `скидк`.

The current accepted Deep data can therefore be valid for scoring/provenance yet fail the stricter player-facing explanation policy.

## Secondary publication lag

There was also a downstream lag that explains why the user saw 117 even after the canonical visual later reached 128.

After deploy #1307, several visual builds/persists advanced `data/production/visual/current.json` through commit `d5193b17...`, but the corresponding deploy workflow-run invocations were cancelled/skipped/failed during the busy update sequence. No newer Pages artifact replaced #1307 until deploy #1351 on 7 October.

Latest overall build/deploy is also important:

- `Build daily visual payload` run `37601910773` / #1392: workflow conclusion success, but the real build job was skipped.
- Its receipt explicitly says:
  `fresh_build=false ... reason=upstream_prerequisite_not_ready`.
- Deploy #1351 still succeeded and copied the existing canonical visual; its publication outcome is:
  `degraded/no_fresh_build`.

So “deploy succeeded” does not mean the Deep snapshot is fresh. This is downstream amplification, not the first causal Deep boundary.

## Translation classification

**Separate / no current translation stale defect.**

The translation values seen by the user exactly match the canonical translation-status blob, and the latest Pages artifact still binds that same current blob and values.

Translation shares the same `processing_status → visual → Pages` publication channel, so a future translation-state change could be delayed by a blocked full visual publication. But for the observed task values, there is no translation discrepancy to repair.

## Cache / refresh role

Browser cache is not the root cause:

- `web/app.js` fetches `data/current.json` with `cache:'no-store'`;
- no current `web/sw.js` / `web/service-worker.js` canonical path is present;
- the user-observed values exactly matched a real Pages artifact.

Because Pages changed during this diagnostic, a browser refresh can now move the page from the old 117-authoritative snapshot to the newer 128-authoritative snapshot. It **cannot** reach canonical 147 while the published artifact itself is still stale.

## Smallest bounded implementation direction

Create one bounded IMPLEMENT task for **Deep positive card-explanation producer/validator parity**, without changing Deep/Dossier/translation semantics, scheduling, queue ownership, or browser authority.

Preferred narrow direction:
- keep the accepted Deep score finding and score/provenance intact;
- prevent commercial/ranking-only Deep finding text from being projected verbatim as player-facing positive `why_fit` (fail closed by omitting that positive explanation rather than weakening the validator);
- add a regression reproducing the current Tetris case.

Primary files/owner:
- producer policy: `scripts/card_explanation_policy.py`;
- regression: `scripts/test_card_explanation_policy.py` and/or focused validation regression;
- validator `scripts/validate_card_explanations.py` should normally remain strict; only change it if the contract is deliberately revised, not as a bypass.
- publication workflow remains GitHub-owned; no new scheduler/retry/control-plane owner is needed.

Architecture preflight: this direction preserves the existing GitHub control plane, existing visual producer/deploy route, and read-only browser.

## Acceptance after fix

A bounded implementation is complete only if one current-state full cycle proves:

1. fresh full visual candidate generation succeeds;
2. `Validate generated card explanations` passes on the Tetris regression/current payload;
3. exact material binding/freshness validation passes;
4. a new `data/production/visual/current.json` is canonically persisted with current PASS 2 provenance;
5. the downstream deploy publishes that exact new visual blob as `web/data/current.json`;
6. freshness receipt is a fresh full-visual success, not `degraded/no_fresh_build`;
7. Pages Deep counters reflect the same current accounting snapshot used by the build;
8. translation values remain bound to the current canonical Russian status and are not regressed.

## Status

`diagnosed_needs_fix`.

## Recommended next step

One bounded IMPLEMENT worker task for the producer/validator parity above; do not start it from this diagnostic worker.

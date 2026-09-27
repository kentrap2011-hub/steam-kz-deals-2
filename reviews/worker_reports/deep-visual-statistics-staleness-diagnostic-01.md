# Deep visual statistics staleness diagnostic 01

## Task

- Task ID: `deep-visual-statistics-staleness-diagnostic-01`
- Repository/source of truth: `kentrap2011-hub/steam-kz-deals-2@main`
- Mode: `READ-ONLY / RECON`
- Worker slot: new physical `ЧАТ 1`
- Diagnostic conclusion label: `OTHER_PROVEN_CAUSE`
- Final status: `needs_fix`
- Final coherent repository snapshot used for canonical-vs-visual comparison: commit `fcbae73bbc45d740211a9ed36de5c86758f947fe` (`Submit Deep result for FINAL FANTASY IV`, 2026-09-27T17:35:23Z).
- The only repository mutation made by this worker is this report, as required by the task. No `CURRENT_TASK.md`, source, workflow, contract, runtime, visual, Deep, Dossier, cache, frontend or Scheduled Task state was changed.

## Verified facts

1. Canonical Deep/PASS 2 has advanced materially beyond the values visible on the site.
   - At the final pinned diagnostic snapshot `fcbae73bbc45d740211a9ed36de5c86758f947fe`, `data/production/pre_ai/progressive_pass2_work.json` has blob `af0b46793ab268712e58d5fd63f8ac2d2ab38449`.
   - Its GitHub-owned current scope reports:
     - total current Deep coverage target: `410`;
     - first-pass attempted: `27`;
     - authoritative completed: `27`;
     - completed fit: `23`;
     - completed not-fit: `4`;
     - incomplete/recovery: `0`;
     - waiting for Dossier: `380`;
     - ready/pending: `3`;
     - remaining until authoritative completion: `383`.
   - The corresponding canonical state blob is `data/cache/progressive_pass2_state.json@7a274633d4941729d3fd9aa0e811af8f359133b9`.
   - Production was advancing during diagnosis: an earlier read showed 19 authoritative completions; the final pinned read showed 27. The report therefore uses the one pinned commit above rather than mixing moving-`main` reads.

2. The current canonical visual artifact is stale with respect to Deep.
   - `data/production/visual/current.json` at the same pinned commit has blob `c0d351655280b84db0d65eb41e8c1488c65e1938`, generated at `2026-09-27T17:11:35.486920+00:00`.
   - Its Deep statistics are:
     - total: `397`;
     - attempted: `0`;
     - authoritative completed: `0`;
     - fit: `0`;
     - not-fit: `0`;
     - incomplete/recovery: `0`;
     - waiting for Dossier: `367`;
     - ready/pending: `30`;
     - remaining: `397`.
   - These are exactly the values reported by the user from the Statistics page.
   - Its production contract still binds `progressive_pass2_state_blob_sha=2de5bf4ca43eec4b3bdf27cfcb753422c815ec51`, while the current canonical PASS 2 state blob at the pinned snapshot is `7a274633d4941729d3fd9aa0e811af8f359133b9`.

3. The actually deployed Pages payload is also stale and matches the canonical visual artifact rather than current Deep.
   - Last successful relevant deploy observed: `Deploy visual mailing` run `36336022032` / run #810, success, head `76bd1e6fa7bcdc530e278be53df2b251fac9c9b6`.
   - Pages artifact: `10937510781`, digest `sha256:166d3080b0ec051e241005beb1c03b473ebbb3c90d2174139dff9565068d7178`.
   - The artifact's `data/current.json` has the same generation time and the same Deep values `397 / 0 attempted / 0 authoritative / 0 fit / 0 not-fit / 0 incomplete / 367 waiting / 30 ready / 397 remaining`, and the same old PASS 2 state provenance blob `2de5bf4ca43eec4b3bdf27cfcb753422c815ec51`.
   - Therefore the user's browser is not merely displaying a locally cached older value while Pages already contains corrected Deep statistics.

4. Deep ingest does automatically activate the existing visual rebuild workflow.
   - `.github/workflows/build-daily-visual-payload.yml` explicitly lists `Ingest Progressive PASS 2 item` under its `workflow_run` triggers.
   - The first observed post-baseline Deep acceptance demonstrates the route end-to-end up to the failing build:
     - `Ingest Progressive PASS 2 item` run `36336174143` / #118 succeeded after submission of the Deep result for Black Skylands;
     - canonical `game:1143810` was accepted as authoritative `analyzed_fit` at `2026-09-27T17:14:20+00:00`;
     - `Build daily visual payload` run `36336192364` / #773 then started automatically and failed.
   - Subsequent successful PASS 2 ingests continued to create visual build invocations. The trigger is therefore present and live.

5. Deep provenance/freshness binding is also present.
   - `scripts/progressive_visual_activation_routing.py` compares the visual's `progressive_pass2_state_blob_sha` with the current Git blob of `data/cache/progressive_pass2_state.json`.
   - A mismatch returns `progressive_pass2_state_provenance_mismatch` and requires a full Progressive visual build.
   - Thus the stale visual is not being incorrectly accepted as fresh because PASS 2 provenance is absent.

6. The full visual builder reads current canonical Deep rather than intentionally preserving the old zero counters.
   - `scripts/progressive_personalization.py` loads the current PASS 2 state, resolves matching/current authoritative Deep entries, sets `analysis_semantic_source='progressive_pass2'`, and recomputes Deep stage/count fields.
   - `scripts/build_final_visual_payload.py` stamps the current Git blob of `data/cache/progressive_pass2_state.json` into `production_contract.progressive_pass2_state_blob_sha`.
   - Failed build logs prove the builder had already seen current Deep before failing: run #773 logged `visual progressive items=410 total=410 fit=1 incomplete=0 not_analyzed=409`; later run #799 logged `visual progressive items=405 total=409 fit=22 incomplete=0 not_analyzed=383`.

7. The exact failure is downstream of correct Deep projection and is caused by a stale Fast/cache-only binding guard in `scripts/grounded_negative_visual.py`.
   - In `apply_to_document()`, the current code defines:
     - current-bound if `projection.status == 'cache_hit'`; or
     - `game.analysis_semantic_source == 'progressive_pass1'`.
   - It does not recognize `analysis_semantic_source == 'progressive_pass2'`, even though `scripts/progressive_pass2.py::project_state()` explicitly marks authoritative Deep output as `progressive_pass2` and the canonical Progressive contract says trustworthy current completed Deep is authoritative effective personalized truth.
   - Consequently an authoritative Deep `analyzed_fit` card whose old reusable Taste projection remains `ai_required` is added to the `unresolved` list and the build raises `RuntimeError: personalized card binding is not current/INCLUDE`.
   - This is directly proven by the first failing build #773: it had exactly one current fit item and failed on exactly one family, `game:1143810`. That family is canonically authoritative `analyzed_fit` in PASS 2 state, accepted at `17:14:20Z`.
   - The same defect persists later. Build run `36337395471` / #799 failed at `2026-09-27T17:34:03Z` after logging 22 fit items, again with the same `personalized card binding is not current/INCLUDE` failure. Its sample contains multiple families independently confirmed in current PASS 2 state as `authoritative_completed=true`, `outcome=analyzed_fit`.

8. The architecture preflight for a future repair is unambiguous.
   - `config/execution_ownership_contract.json` assigns Progressive state projection, aggregate counts, validation, persistence and publication to the GitHub control plane.
   - `config/progressive_personalization_contract.json` defines current completed Deep as authoritative and browser presentation as read-only.
   - Correcting this GitHub-owned visual producer guard would not transfer control-plane responsibility to ChatGPT, would not add a scheduler/queue/retry loop, and would not change Deep/Dossier semantics.

## Exact stale boundary

The stale boundary is:

`canonical PASS 2 state/work (fresh)`
→ `PASS 2 ingest completion trigger (works)`
→ `progressive visual provenance mismatch detection (works)`
→ `full visual build reads/projects current Deep (works)`
→ **`scripts/grounded_negative_visual.py::apply_to_document()` rejects authoritative PASS 2 fit cards because its current-bound check recognizes cache/Fast but not Deep**
→ full visual build exits non-zero before persisting a new `data/production/visual/current.json`
→ deploy is skipped
→ `web/data/current.json` / Pages stays on the last pre-Deep successful visual
→ browser correctly renders those stale deployed counters.

So the defect is not at the browser, Deep ingest trigger, Deep state accounting, or PASS 2 provenance check. The write/publish chain is stranded inside the full visual producer after correct Deep projection but before visual persistence.

## Current canonical vs visual vs deployed counts

Pinned canonical repository comparison: `fcbae73bbc45d740211a9ed36de5c86758f947fe`.

| Deep metric | Canonical PASS 2 work/state | `data/production/visual/current.json` | deployed Pages `data/current.json` |
| --- | ---: | ---: | ---: |
| Total current coverage | 410 | 397 | 397 |
| First-pass attempted | 27 | 0 | 0 |
| Authoritative completed | 27 | 0 | 0 |
| Completed fit | 23 | 0 | 0 |
| Completed not-fit | 4 | 0 | 0 |
| Incomplete / recovery | 0 | 0 | 0 |
| Waiting for Dossier | 380 | 367 | 367 |
| Ready / pending | 3 | 30 | 30 |
| Remaining until all authoritative | 383 | 397 | 397 |
| PASS 2 state provenance | current state blob `7a274633...` | old blob `2de5bf4c...` | old blob `2de5bf4c...` |

The denominators differ as well because the visual is an older generation, which reinforces that the published file is genuinely old rather than merely mis-rendering a single counter.

## Cause

Primary allowed conclusion: `OTHER_PROVEN_CAUSE`.

The proven cause is a Deep-incompatible downstream visual-producer guard in `scripts/grounded_negative_visual.py`, not a missing visual rebuild trigger and not a missing Deep provenance binding.

Observable consequences are both canonical and deployed visual staleness:
- `data/production/visual/current.json` is stale;
- the latest successful Pages artifact is stale;
- the browser-visible zero Deep completions match that stale published payload.

The exact faulty predicate is the `current_bound` check in `grounded_negative_visual.apply_to_document()`: it admits compatible cache and `progressive_pass1`, but omits current authoritative `progressive_pass2`.

## Changes — report only

Created only:
- `reviews/worker_reports/deep-visual-statistics-staleness-diagnostic-01.md`.

No implementation, workflow, runtime, contract, visual payload, Deep state, Dossier state, cache, frontend, Scheduled Task or production backlog change was performed.

The normal CHAT_PROTOCOL durable-state update to `CURRENT_TASK.md` was intentionally not made because this worker task explicitly authorizes only one repository write: the report.

## Validation

Repository/state:
- pinned diagnostic main commit: `fcbae73bbc45d740211a9ed36de5c86758f947fe`;
- current Deep work blob at that commit: `af0b46793ab268712e58d5fd63f8ac2d2ab38449`;
- current PASS 2 state blob at that commit: `7a274633d4941729d3fd9aa0e811af8f359133b9`;
- stale canonical visual blob: `c0d351655280b84db0d65eb41e8c1488c65e1938`;
- stale visual PASS 2 provenance: `2de5bf4ca43eec4b3bdf27cfcb753422c815ec51`.

Last good pre-Deep publication:
- full visual build run `36335990742` / #772 — success;
- build log: `visual progressive items=410 total=410 fit=0 incomplete=0 not_analyzed=410`;
- visual commit produced: `76bd1e6fa7bcdc530e278be53df2b251fac9c9b6`;
- deploy run `36336022032` / #810 — success;
- Pages artifact `10937510781`;
- artifact digest `sha256:166d3080b0ec051e241005beb1c03b473ebbb3c90d2174139dff9565068d7178`;
- deployed `data/current.json` independently inspected and confirmed to carry the stale zero-Deep counters.

First direct failure after Deep became visible to the builder:
- PASS 2 ingest run `36336174143` / #118 — success;
- `game:1143810` accepted authoritative Deep fit at `2026-09-27T17:14:20+00:00`;
- visual build run `36336192364` / #773 — failure;
- build log: `visual progressive items=410 total=410 fit=1 incomplete=0 not_analyzed=409`;
- failure: `personalized card binding is not current/INCLUDE` for exactly `game:1143810`.

Latest failed build inspected:
- visual build run `36337395471` / #799 — failure;
- log at `2026-09-27T17:34:03Z`: `visual progressive items=405 total=409 fit=22 incomplete=0 not_analyzed=383`;
- same `personalized card binding is not current/INCLUDE` RuntimeError;
- corresponding deploy run `36337426447` / #837 — skipped.

Code/contract proof:
- `.github/workflows/build-daily-visual-payload.yml` — PASS 2 ingest is an upstream `workflow_run` trigger.
- `scripts/progressive_visual_activation_routing.py` — exact PASS 2 state provenance mismatch forces full Progressive rebuild.
- `scripts/progressive_personalization.py` — current Deep state is loaded and Deep statistics are producer-computed.
- `scripts/progressive_pass2.py::project_state()` — authoritative Deep sets `analysis_semantic_source='progressive_pass2'`.
- `scripts/grounded_negative_visual.py::apply_to_document()` — current-bound guard admits cache/Fast but omits Deep and raises the observed RuntimeError.
- `config/progressive_personalization_contract.json` — current completed Deep is authoritative.
- `config/execution_ownership_contract.json` — GitHub owns projection/publication and browser is read-only.

## Unresolved

The implementation defect is not repaired by this READ-ONLY task, so the site remains dependent on the last successful pre-Deep visual until the GitHub-owned producer guard is corrected and a full visual build/deploy succeeds.

Production Deep was still advancing during the diagnostic window. Counts after the pinned commit may therefore be higher than 27; that does not change the proven stale boundary or root cause.

No evidence supports `BROWSER_CACHE_ONLY`, `DEEP_VISUAL_REBUILD_TRIGGER_DEFECT` or `DEEP_VISUAL_PROVENANCE_DEFECT`.

## Status

`needs_fix`

## Recommended next step

Create exactly one bounded IMPLEMENT worker task that updates the current-bound logic in `scripts/grounded_negative_visual.py::apply_to_document()` to recognize trustworthy current authoritative PASS 2 / `progressive_pass2` fit as a valid personalized binding, adds a focused regression reproducing the `projection_status=ai_required + authoritative Deep analyzed_fit` case, and validates one successful full visual build followed by Pages deploy. Preserve the existing PASS 2 trigger, provenance checks, GitHub ownership and scheduler architecture unchanged.

## Exact refs

- Task: `WORKER_TASK_DEEP_VISUAL_STATISTICS_STALENESS_DIAGNOSTIC_01.md`
- Report: `reviews/worker_reports/deep-visual-statistics-staleness-diagnostic-01.md`
- Pinned diagnostic commit: `fcbae73bbc45d740211a9ed36de5c86758f947fe`
- Canonical Deep work: `data/production/pre_ai/progressive_pass2_work.json`
- Canonical Deep state: `data/cache/progressive_pass2_state.json`
- Canonical visual: `data/production/visual/current.json`
- Deep projection: `scripts/progressive_pass2.py`
- Progressive visual producer: `scripts/progressive_personalization.py`
- Failing downstream guard: `scripts/grounded_negative_visual.py`
- Activation/provenance routing: `scripts/progressive_visual_activation_routing.py`
- Visual workflow: `.github/workflows/build-daily-visual-payload.yml`
- Successful baseline visual build: `36335990742` / #772
- Successful baseline deploy: `36336022032` / #810
- Pages artifact: `10937510781`
- First failing post-Deep visual build: `36336192364` / #773
- Latest failed visual build inspected: `36337395471` / #799
- Latest skipped deploy inspected: `36337426447` / #837

## Efficiency / reusable lesson

The existing `PROJECT_ROUTES.md` route was sufficient to avoid a repository-wide rediscovery of Deep → visual → deploy. The important new reusable pitfall is narrower: after an architecture adds a new authoritative semantic source, downstream presentation/enrichment guards must recognize that source wherever they gate “current personalized binding”; otherwise the producer can correctly compute new stage state and still fail before publication.

Because this task allowed only the report write, that pitfall was not added to `PROJECT_ROUTES.md` or a regression file here. The recommended implementation task should preserve it as a focused regression alongside the code fix.

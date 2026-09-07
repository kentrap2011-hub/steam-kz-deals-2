# Worker Report — Publication Freshness Pre-Fix Forensic Recon 01

## Task
`publication-freshness-pre-fix-forensic-recon-01`

Mode: `READ-ONLY / RECON / FORENSIC`

Goal: freeze and explain the current paid-list publication freshness failure before any repair, and assess the prepared repair task without mutating production state.

## Verified facts
- Investigation started from current `main`.
- Required forensic report was created before expensive investigation, per `WORKER_REPORT_DURABILITY_PROTOCOL.md`.
- No repair, manual refresh, scheduler, writer, workflow, contract, Taste, or production-state mutation has been performed.
- The only repository mutation made by this recon is this report.
- Fresh Steam-derived deterministic state is reaching the canonical commercial pipeline above visual publication:
  - `data/production/shortlist/index.json`: `updated_at_utc=2026-09-06 21:00:38 UTC`, `app_count=4671`, `source_snapshot_id=steam_kz_daily::2026-09-06T21:00:38Z::raw`, integrity SHA-256 `5b9789ec59aecfd14376b35272196435d2f94f202d62dc35ef758421741652e1`.
  - `data/production/mailing/index.json`: same source timestamp/snapshot/integrity identity, `app_count=4671`, content digest `7fcf0973d116dab3c88bc3311dcff798c402052cdc59359757c30402da527df0`.
  - `data/production/pre_ai/store_snapshot.json`: generated `2026-09-07 03:20:25 UTC`, bound to mailing source `2026-09-06 21:00:38 UTC`, source item count `4671`, selected entry count `45`, selected-appids SHA-256 `cb119223166edf2355004ea664feb93839939c3f8fdd2572b5d027229e502483`.
  - `data/production/pre_ai/family_graph.json`: same current mailing source binding, generated `2026-09-07 03:20:25 UTC`, entry count `45`.
  - `data/production/pre_ai/chatgpt_payload.json`: generated `2026-09-07 03:20:41 UTC`, same current mailing source binding, but `status=DEGRADED`, `failure_reason=chatgpt_completion_missing`, `semantic_status.complete=false`, `semantic_status.awaiting_chatgpt_completion=true`, `provenance_only=true`.
- Therefore the active break is not Steam ingest, shortlist publication, shortlist→mailing, or deterministic pre-AI source construction.
- `scripts/build_daily_visual_payload.py` deliberately fails closed unless ChatGPT payload status is `COMPLETE`; current `DEGRADED/chatgpt_completion_missing` therefore blocks the full visual rebuild path by design.
- A deterministic scoped helper already exists: `scripts/refresh_visual_commercial_fields.py`. It refreshes commercial/worthiness fields from current deterministic pre-AI truth while preserving already-published semantic labels and enforcing strict provenance/coverage checks. The helper itself is not the missing implementation.
- `.github/workflows/build-daily-visual-payload.yml` currently has a production `giveaway_only` branch but no analogous `commercial_only` classifier/job/receipt branch. `refresh_visual_commercial_fields.py` is covered by workflow change/test logic but is not production-invoked by the workflow.
- Thus the current inactive edge is the deterministic commercial handoff into canonical visual paid publication: the full route is stopped by the intended semantic fail-closed guard, while the already-existing scoped commercial refresh route is not wired into production orchestration.

## Current canonical chain
The current intended data/publication topology is:

`Steam ingest → data/production/shortlist → data/production/mailing → data/production/pre_ai/{store_snapshot,family_graph,chatgpt_payload} → visual publication orchestration → canonical visual writer/publication helper → data/production/visual/current.json + snapshot/latest aliases + data/published/visual_current.json + visual_current.js → frontend/site`.

There are two conceptually valid visual refresh modes:
1. full semantic visual rebuild, which correctly requires a semantically complete ChatGPT production payload;
2. scoped deterministic subdomain refresh, which may update independently refreshable deterministic fields while preserving unrelated/semantic state and proving preservation by receipt.

The giveaway incident already established mode (2) for giveaway data. The paid/commercial helper for mode (2) exists, but production orchestration does not expose a `commercial_only` route.

## Exact cause classification
### Primary cause
`missing / inactive production-orchestration handoff` at deterministic commercial state → canonical visual paid publication.

Specifically, the existing visual workflow has no `commercial_only` classification/job/receipt path that invokes `scripts.refresh_visual_commercial_fields` when commercial provenance becomes newer than the paid lineage in the current visual artifact.

### Contributing blocking condition
The full visual route is intentionally fail-closed on semantic incompleteness. Current `chatgpt_payload` is `DEGRADED` with `chatgpt_completion_missing`, so a full rebuild cannot legally absorb the fresh commercial state.

### Causes not supported by current evidence
- source scheduler gap: disproven by fresh shortlist/mailing/pre-AI artifacts;
- shortlist→mailing trigger failure: disproven by identical current source identity in shortlist and mailing, plus successful retained mailing workflow runs;
- contract/version incompatibility as the active root cause: not observed;
- provenance/freshness guard incorrectly rejecting otherwise legal commercial-only refresh: not the root, because no production commercial-only invocation exists to reach that guard;
- missing commercial refresh implementation: disproven by existing `scripts/refresh_visual_commercial_fields.py`;
- need for a new scheduler or writer: contradicted by existing ownership/routing architecture.

## Why the system looked partially healthy
- Steam/source collection continued normally.
- Shortlist and mailing continued updating with a fresh shared source identity.
- Deterministic pre-AI store/family state continued updating from fresh mailing.
- Giveaway scoped publication was separately repaired and continued to mutate the visual artifact without changing paid rows.
- Therefore repository/workflow activity, fresh upstream timestamps, and even successful visual commits could coexist with a paid section whose commercial lineage remained stale.
- The latest frozen workflow evidence demonstrates this directly: the current source cycle had a successful mailing run, a pre-AI run that failed on the full semantic path, followed by a successful `giveaway_only` visual run and receipt. The repository therefore looked active and partially healthy while the paid commercial lineage did not advance.
- The frontend is correctly rendering the stale canonical paid facts it receives; entries whose retained sale window ended are therefore shown as `скидка закончилась` rather than being silently hidden or fabricated.

## Why freshness / receipt / fail-closed checks did not raise a clear stale-paid alarm
- Existing fail-closed checks are primarily integrity/safety gates: they prevent invalid full publication when semantic completion/provenance is missing.
- `scripts/visual_freshness_receipt.py` currently supports `full` and `giveaway_only`, not `commercial_only`.
- A successful `giveaway_only` receipt proves paid hash/order preservation and giveaway freshness, and explicitly has `full_visual_freshness=false`; it does not assert that paid commercial lineage matches the newest deterministic commercial source.
- A failed full refresh proves that full semantic publication is unsafe; it does not by itself enforce a paid-list liveness SLA or compare paid source timestamp/hash to newest mailing/store provenance and escalate prolonged lag.
- Net result: safety/fail-closed behavior worked, but no scoped paid-commercial freshness receipt/invariant converted the growing upstream→paid lineage lag into a dedicated alert/failure state.

## Comparison with previous giveaway incident
### Different
- Giveaway now has an explicit wired `giveaway_only` production path, classifier, preservation checks, and scoped receipt.
- Paid commercial refresh already has a strict helper but no corresponding production orchestration branch or receipt scope.
- Giveaway source is a separately refreshable subdomain; commercial refresh derives from current deterministic mailing/pre-AI truth and must preserve semantic labels/coverage while updating prices/discount windows/ranking-related deterministic commerce.

### Common systemic problem
Both incidents expose the same architectural coupling: multiple independently refreshable deterministic subdomains ultimately feed one canonical visual artifact, while the full visual path is coupled to a semantic-completion gate. If a deterministic subdomain has no independently wired scoped handoff, correct fail-closed behavior preserves old visual state indefinitely. Integrity protection therefore needs a paired liveness/freshness invariant for each independently refreshable publication subdomain.

## Frozen pre-fix evidence
### Current upstream/commercial identities
- shortlist source commit: `8086a61c6bed323ad39f77c45631524eaa0d7330` at `2026-09-06T21:00:40Z`
- shortlist blob SHA: `724d4914167e58615bc1b89193cebfdd8dcc5639`
- shortlist source timestamp: `2026-09-06 21:00:38 UTC`
- shortlist source integrity SHA-256: `5b9789ec59aecfd14376b35272196435d2f94f202d62dc35ef758421741652e1`
- mailing source commit: `d9f3d36c364c06af72888b4b81ca69c42c4e04b7` at `2026-09-06T21:00:54Z`
- mailing blob SHA: `029413ab406371948235f58f652f754dd9720fc2`
- mailing content digest: `7fcf0973d116dab3c88bc3311dcff798c402052cdc59359757c30402da527df0`
- store snapshot blob SHA: `1da3bf26fbb0a08a103698e23656141e85bc5426`
- family graph blob SHA: `6b1692bea0e33380b50016a1597654678212f28e`
- ChatGPT payload blob SHA: `db17224af3793744149e8e58ac10ef29e7177b46`
- ChatGPT payload state: `DEGRADED / chatgpt_completion_missing`
- current visual blob SHA before repair: `242275cf24368062f0c76535f305ba4688784ac0`

### Current pre-fix workflow/run/receipt identities
- Latest frozen shortlist→mailing handoff:
  - workflow: `Build mailing-optimized feed`
  - run ID: `34059728770`
  - run number: `30`
  - event: `workflow_run`
  - head SHA: `8086a61c6bed323ad39f77c45631524eaa0d7330`
  - created: `2026-09-06T21:00:47Z`
  - conclusion: `success`
  - resulting mailing commit: `d9f3d36c364c06af72888b4b81ca69c42c4e04b7`
- Corresponding full pre-AI workflow:
  - workflow: `Build pre-AI deterministic payload`
  - run ID: `34059742637`
  - run number: `93`
  - event: `workflow_run`
  - head SHA: `d9f3d36c364c06af72888b4b81ca69c42c4e04b7`
  - created: `2026-09-06T21:01:00Z`
  - conclusion: `failure`
  - current persisted semantic state identifies the blocking condition as `DEGRADED / chatgpt_completion_missing`.
- Corresponding visual workflow that still succeeded for the independent giveaway domain:
  - workflow: `Build daily visual payload`
  - run ID: `34059763292`
  - run number: `200`
  - event: `workflow_run`
  - head SHA: `06c9ac33ceb2f3fc244c5d889d798fb81cb2f6f5`
  - upstream workflow run ID recorded by receipt: `34059742637`
  - upstream head SHA recorded by receipt: `d9f3d36c364c06af72888b4b81ca69c42c4e04b7`
  - created: `2026-09-06T21:01:26Z`
  - conclusion: `success`
- Frozen `visual-freshness-receipt` artifact for that visual run:
  - artifact ID: `9997090112`
  - artifact name: `visual-freshness-receipt`
  - artifact digest: `sha256:e78e48b29a7c529aeeed9efa3f771eded7aa92862b381e23226f07fdf1549725`
  - created: `2026-09-06T21:01:45Z`
  - receipt contract: `visual-freshness-receipt-v1`
  - `fresh_build=true`
  - `freshness_scope=giveaway_only`
  - `full_visual_freshness=false`
  - `outcome=fresh_build`
  - produced visual commit: `df4a96ac9f3b57e4c679b196f99504f0a50342fb`
  - produced visual blob: `242275cf24368062f0c76535f305ba4688784ac0`
  - receipt workflow run ID: `34059763292`
  - receipt attempt: `1`
- This receipt is important negative evidence: it proves a fresh scoped giveaway build and successful visual mutation, but by contract does **not** prove or claim paid-list freshness.

### Historical visual evidence
- Commit `d3d268a57b49b89f58867f88cfd1800f2398c06b` refreshed daily visual at `2026-08-31T20:37:59Z`.
- Subsequent visual commits on `2026-09-01` include `19472a7f...`, `f928af44...`, `0c6db0ea...`, `15db361d...`, `8a778db3...`, `9aa0aef0...`.
- Later visual mutations include giveaway-only refresh commits, including `a05aec8d...` on `2026-09-04`, `1d7fb4d1...` on `2026-09-06T17:14:23Z`, and `df4a96ac9f3b57e4c679b196f99504f0a50342fb` on `2026-09-06T21:01:43Z`.
- Prior freshness recon proved the paid section retained the `31 Aug 2026 00:37` commercial snapshot semantics/lineage while later visual activity preserved/reused those paid rows.
- Current retained evidence proves that fresh deterministic source cycles after that paid snapshot, through the current `2026-09-06T21:00:38Z` source, did not reach canonical paid commercial publication.

## Historical break boundary — final
The exact first failed/missed internal commercial-publication invocation cannot be proven from retained evidence and is **not inferred**.

The narrowest proven boundary is:

### Last proven synchronized commercial cycle
- shortlist commit `714cd4d57170eac8ba65272fe5a26a100918dbec` at `2026-08-31T20:36:53Z` (`Update Steam KZ production shortlist`);
- mailing commit `2bdef90c3e2855b16d211dbe8c0570d6109e611b` at `2026-08-31T20:37:08Z` (`Rebuild mailing feed and Store state cache`);
- paid visual refresh commit `d3d268a57b49b89f58867f88cfd1800f2398c06b` at `2026-08-31T20:37:59Z`.

This is the last retained cycle for which source→mailing→published paid lineage is proven to be caught up.

### First proven newer commercial source not represented by paid visual lineage
- shortlist commit `50b763ba7ecb1b6e781be48ca2b17b0599d9d4ac` at `2026-09-01T19:30:42Z`;
- successful `Build mailing-optimized feed` run ID `33549933036`, run number `20`, created `2026-09-01T19:30:50Z`, conclusion `success`;
- resulting mailing commit `1be38324ca68e0ec3613331709840b9f383d27eb` at `2026-09-01T19:30:57Z`;
- successful downstream `Build pre-AI deterministic payload` run ID `33549958109`, run number `78`, created `2026-09-01T19:31:05Z`, conclusion `success`.

The paid visual lineage nevertheless remained anchored to the August 31 commercial snapshot. A later visual commit `43b7d8f47bfda036741e3d6e03fd276f9c4bf5b4` at `2026-09-01T20:20:29Z` was explicitly `Refresh giveaway visual payload`, so it is not evidence of paid catch-up.

Therefore:
- **last proven caught-up point:** `2026-08-31T20:37:59Z`;
- **first proven divergent fresh commercial source:** mailing commit at `2026-09-01T19:30:57Z` (with successful upstream/downstream deterministic workflow evidence);
- the transition from healthy paid catch-up to stale paid publication occurred somewhere after the last synchronized August 31 cycle and was already observable on the first retained September 1 commercial cycle;
- retained evidence does **not** identify an exact trigger-removal commit, exact failed visual invocation, or exact second within that interval. Claiming one would be speculation.

This boundary is stronger than merely saying “sometime after August 31”: it proves the first retained September 1 commercial source progressed through mailing and deterministic pre-AI while paid publication did not advance.

## Architecture / reliability invariants
- GitHub Actions owns deterministic transforms, orchestration, canonical persistence, and fail-closed behavior per `config/execution_ownership_contract.json`.
- ChatGPT semantic incompleteness must continue to block full semantic publication.
- A scoped commercial refresh must never invent semantic truth; it may only preserve previously canonical semantic labels when coverage/provenance checks prove that preservation safe.
- Scoped commercial refresh must preserve giveaway state exactly.
- No second canonical writer, scheduler, or parallel publication chain is warranted.

## Repair task assessment — final
Verdict for `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`:

`requires_one_bounded_correction`

The task is directionally correct and its hard boundaries are good, but **it is not sufficiently safe as-is** because its accepted predecessor wording says the blocker is “between fresh daily shortlist and the existing canonical commercial mailing/visual publication path” and Required implementation item 3 asks to repair the link “between successful daily shortlist refresh and the existing canonical commercial mailing/visual build.” The forensic evidence now proves shortlist→mailing is healthy and the missing edge is narrower and later. Leaving the wording as-is creates avoidable scope ambiguity and could lead an implementer to modify a healthy upstream handoff or attempt to make the full semantic path permissive.

### The one bounded correction required before repair execution
Correct the repair task's **repair-target scope** so that Required implementation explicitly states, as one bounded change:

> Repair only the missing deterministic **commercial-only visual handoff** inside the existing canonical visual orchestration: reuse `scripts/refresh_visual_commercial_fields.py` from the current deterministic commercial/pre-AI source, wire it through the existing `.github/workflows/build-daily-visual-payload.yml` as a scoped `commercial_only` path with a truthful scoped freshness receipt, preserve giveaway state, and leave the full semantic `ChatGPT production payload is not complete` fail-closed guard unchanged. Do not modify the already-working Steam→shortlist→mailing handoff and do not add a scheduler, writer, or parallel pipeline.

This is one scope correction, not a redesign. It resolves all material ambiguity exposed by the forensic recon. The rest of the prepared task can remain unchanged, including its acceptance requirement that fresh paid source identity/timestamp be tied to actually published paid items and not giveaway/artifact time.

After that bounded correction, the task is suitable to enter repair/acceptance work in a separate authorized step.

## Validation
- Initial durability checkpoint persisted before investigation.
- Mid-investigation checkpoint recorded the reconstructed path, current source identities, primary break classification, guard blind spot, giveaway comparison, and provisional repair-task direction.
- Final bounded continuation re-read this saved report from `main` before finalization.
- Historical boundary was narrowed using retained shortlist/mailing/visual commit history plus first-divergent workflow run identities.
- Current pre-fix visual receipt was frozen by exact run ID, artifact ID, artifact digest, scope, lineage, output commit/blob, and upstream run identity.
- Prepared repair task was re-read and assessed against the final forensic root cause.
- No repair action has been invoked.
- No workflow, production data, Taste, scheduler, writer, contract, or repair-task file was changed.

## Unresolved / forensic limitation
No unresolved item blocks repair preparation.

The exact first internal failed/missed visual commercial invocation is not reconstructible from retained evidence. This is a recorded forensic limitation, not an open guess: the report preserves the narrowest proven healthy→divergent boundary instead.

## Status
`complete_ready_for_repair`

## Recommended next step
None is executed by this recon. The prepared repair task requires the single bounded repair-target correction described above before it is run.

## Exact refs
- Task: `WORKER_TASK_PUBLICATION_FRESHNESS_PRE_FIX_FORENSIC_RECON_01.md`
- Prepared repair task assessed: `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
- Report: `reviews/worker_reports/publication-freshness-pre-fix-forensic-recon-01.md`
- Current visual: `data/production/visual/current.json`
- Commercial scoped helper: `scripts/refresh_visual_commercial_fields.py`
- Visual workflow: `.github/workflows/build-daily-visual-payload.yml`
- Freshness receipt implementation: `scripts/visual_freshness_receipt.py`
- First divergent mailing run: `33549933036`
- First divergent deterministic pre-AI run: `33549958109`
- Latest frozen mailing run: `34059728770`
- Latest frozen full pre-AI run: `34059742637`
- Latest frozen scoped visual run: `34059763292`
- Latest frozen visual freshness receipt artifact: `9997090112`

## Efficiency / reusable lesson
When a canonical aggregate artifact contains independently refreshable subdomains, fail-closed correctness and freshness liveness must be modeled separately. A healthy upstream plus a successful scoped refresh for one subdomain is not evidence that another preserved subdomain is fresh.

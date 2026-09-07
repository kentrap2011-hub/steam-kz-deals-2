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
- `scripts/build_daily_visual_payload.py` deliberately fails closed unless ChatGPT payload status is `COMPLETE`; current `DEGRADED/chatgpt_completion_missing` blocks the full visual rebuild path by design.
- A deterministic scoped helper already exists: `scripts/refresh_visual_commercial_fields.py`. It refreshes commercial/worthiness fields from current deterministic pre-AI truth while preserving already-published semantic labels and enforcing strict provenance/coverage checks. The helper itself is not the missing implementation.
- `.github/workflows/build-daily-visual-payload.yml` currently has a production `giveaway_only` branch but no analogous `commercial_only` classifier/job/receipt branch. The commercial helper is not production-invoked by that workflow.
- Thus the current inactive edge is the deterministic commercial handoff into canonical visual paid publication: the full route is stopped by the intended semantic fail-closed guard, while the already-existing scoped commercial refresh route is not wired into production orchestration.

## Current canonical chain
The intended topology is:

`Steam ingest → data/production/shortlist → data/production/mailing → data/production/pre_ai/{store_snapshot,family_graph,chatgpt_payload} → visual publication orchestration → canonical visual writer/publication helper → data/production/visual/current.json + snapshot/latest aliases + data/published/visual_current.json + visual_current.js → frontend/site`.

Two refresh modes are architecturally valid:
1. full semantic visual rebuild, which correctly requires a semantically complete ChatGPT production payload;
2. scoped deterministic subdomain refresh, which may update independently refreshable deterministic facts while preserving unrelated/semantic state and proving preservation by receipt.

The giveaway incident already established mode (2) for giveaway data. The paid/commercial helper for mode (2) exists, but production orchestration does not expose a `commercial_only` route.

## Exact cause classification
### Primary cause
`missing / inactive production-orchestration handoff` at deterministic commercial state → canonical visual paid publication.

Specifically, the existing visual workflow has no `commercial_only` classification/job/receipt path that invokes `scripts/refresh_visual_commercial_fields.py` when commercial provenance becomes newer than the paid lineage in the current visual artifact.

### Contributing blocking condition
The full visual route is intentionally fail-closed on semantic incompleteness. Current `chatgpt_payload` is `DEGRADED` with `chatgpt_completion_missing`, so a full rebuild cannot legally absorb the fresh commercial state.

### Causes not supported by evidence
- source scheduler gap: disproven by fresh shortlist/mailing/pre-AI artifacts;
- shortlist→mailing trigger failure: disproven by identical current source identity in shortlist and mailing plus successful retained mailing workflow runs;
- contract/version incompatibility as the active root cause: not observed;
- provenance/freshness guard incorrectly rejecting an otherwise invoked commercial-only refresh: not the root, because no production commercial-only invocation exists to reach that guard;
- missing commercial refresh implementation: disproven by existing `scripts/refresh_visual_commercial_fields.py`;
- need for a new scheduler or writer: contradicted by existing ownership/routing architecture.

## Why the system looked partially healthy
- Steam/source collection continued normally.
- Shortlist and mailing continued updating with a fresh shared source identity.
- Deterministic pre-AI store/family state continued updating from fresh mailing.
- Giveaway scoped publication was separately repaired and continued to mutate the visual artifact without changing paid rows.
- The latest frozen cycle demonstrates this directly: mailing succeeded, the full semantic pre-AI path remained blocked by semantic incompleteness, and a `giveaway_only` visual run still succeeded with its own receipt.
- Therefore repository/workflow activity, fresh upstream timestamps, and successful visual commits could coexist with stale paid commercial lineage.
- The frontend is correctly rendering the stale canonical paid facts it receives; rows whose retained sale window ended are consequently shown as `скидка закончилась` rather than silently fabricated as current.

## Why freshness / receipt / fail-closed checks did not raise a clear stale-paid alarm
- Existing fail-closed checks are primarily integrity/safety gates: they prevent invalid full publication when semantic completion/provenance is missing.
- `scripts/visual_freshness_receipt.py` currently supports `full` and `giveaway_only`, not `commercial_only`.
- A successful `giveaway_only` receipt proves paid preservation and giveaway freshness, and explicitly has `full_visual_freshness=false`; it does not assert that paid commercial lineage matches newest deterministic commercial truth.
- A failed full refresh proves that full semantic publication is unsafe; it does not itself enforce a paid-list liveness SLA or compare paid source timestamp/hash with newest mailing/store provenance and escalate prolonged lag.
- Net result: safety/fail-closed behavior worked, but no scoped paid-commercial freshness receipt/invariant converted growing upstream→paid lineage lag into a dedicated failure/alert state.

## Comparison with previous giveaway incident
### Different
- Giveaway now has an explicit wired `giveaway_only` production path, classifier, preservation checks, and scoped receipt.
- Paid commercial refresh already has a strict helper but no corresponding production orchestration branch or receipt scope.
- Giveaway source is a separately refreshable subdomain; commercial refresh derives from deterministic mailing/pre-AI truth and must preserve semantic labels/coverage while updating deterministic commercial facts.

### Common systemic problem
Both incidents expose the same architectural coupling: multiple independently refreshable deterministic subdomains feed one canonical visual artifact, while the full visual route is coupled to a semantic-completion gate. If a deterministic subdomain has no independently wired scoped handoff, correct fail-closed behavior can preserve old visual state indefinitely. Integrity protection therefore needs a paired liveness/freshness invariant for each independently refreshable publication subdomain.

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

### Current pre-fix workflow/run identities
Latest frozen shortlist→mailing handoff:
- workflow: `Build mailing-optimized feed`
- run ID: `34059728770`
- run number: `30`
- event: `workflow_run`
- head SHA: `8086a61c6bed323ad39f77c45631524eaa0d7330`
- created: `2026-09-06T21:00:47Z`
- conclusion: `success`
- resulting mailing commit: `d9f3d36c364c06af72888b4b81ca69c42c4e04b7`

Corresponding full pre-AI workflow:
- workflow: `Build pre-AI deterministic payload`
- run ID: `34059742637`
- run number: `93`
- event: `workflow_run`
- head SHA: `d9f3d36c364c06af72888b4b81ca69c42c4e04b7`
- created: `2026-09-06T21:01:00Z`
- conclusion: `failure`
- persisted semantic state identifies the blocking condition as `DEGRADED / chatgpt_completion_missing`.

Corresponding scoped visual workflow:
- workflow: `Build daily visual payload`
- run ID: `34059763292`
- run number: `200`
- event: `workflow_run`
- head SHA: `06c9ac33ceb2f3fc244c5d889d798fb81cb2f6f5`
- created: `2026-09-06T21:01:26Z`
- conclusion: `success`
- receipt upstream workflow run ID: `34059742637`
- receipt upstream head SHA: `d9f3d36c364c06af72888b4b81ca69c42c4e04b7`

### Frozen visual freshness receipt
For visual run `34059763292`:
- artifact ID: `9997090112`
- artifact name: `visual-freshness-receipt`
- artifact digest: `sha256:e78e48b29a7c529aeeed9efa3f771eded7aa92862b381e23226f07fdf1549725`
- created: `2026-09-06T21:01:45Z`
- expires: `2026-10-06T21:01:45Z`
- contract: `visual-freshness-receipt-v1`
- `fresh_build=true`
- `freshness_scope=giveaway_only`
- `full_visual_freshness=false`
- `outcome=fresh_build`
- produced visual commit: `df4a96ac9f3b57e4c679b196f99504f0a50342fb`
- produced visual blob: `242275cf24368062f0c76535f305ba4688784ac0`
- produced giveaway state: `active`
- receipt workflow run ID: `34059763292`, attempt `1`

This is important negative evidence: it proves a fresh scoped giveaway build and successful visual mutation, but by contract does **not** prove or claim paid-list freshness.

## Historical break boundary — final, evidence-conservative
The exact first failed/missed internal commercial-publication invocation cannot be proven from retained evidence and is **not inferred**.

### Last proven paid commercial lineage
The prior paid-list freshness recon proves that the published paid `items` remain tied to the commercial snapshot rendered by the site as:

`31 Aug 2026, 00:37`

Previously captured payload provenance for that retained paid lineage was:
- `source_mailing_updated_at_utc = 2026-08-30 20:37:11 UTC`
- `source_mailing_sha256 = f00636de30ab19ee99cfd7fca78bd8ed91a8bd9bb0e45ccbc4a9c98ef8dda97e`
- visual generation for that lineage: `2026-08-30 20:37:50 UTC`

This is the last **proven published paid lineage**, not merely the last file-write timestamp.

### First proven newer commercial source
A newer mailing source definitely existed on the next daily cycle:
- shortlist commit: `714cd4d57170eac8ba65272fe5a26a100918dbec`
- mailing commit: `2bdef90c3e2855b16d211dbe8c0570d6109e611b` at `2026-08-31T20:37:08Z`
- historical `data/production/mailing/index.json` at that commit: `updated_at_utc=2026-08-31 20:36:53 UTC`, `app_count=4664`
- canonical visual refresh commit after that mailing write: `d3d268a57b49b89f58867f88cfd1800f2398c06b` at `2026-08-31T20:37:59Z`

The retained connector evidence exposes the `d3d268a...` visual commit and its large one-line `current.json` blob identity, but does not expose enough of that historical JSON body/patch to prove its internal `source_mailing_*` binding. Therefore this recon does **not** claim that `d3d268a...` was either the first failed invocation or a successful catch-up. Treating it as either would be speculation.

### First later divergent cycle with retained workflow proof
By the first retained September 1 commercial cycle, fresh commercial data again progressed successfully above visual publication:
- shortlist/head commit: `50b763ba7ecb1b6e781be48ca2b17b0599d9d4ac` at `2026-09-01T19:30:42Z`
- `Build mailing-optimized feed` run ID `33549933036`, run number `20`, created `2026-09-01T19:30:50Z`, conclusion `success`
- resulting mailing commit: `1be38324ca68e0ec3613331709840b9f383d27eb` at `2026-09-01T19:30:57Z`
- `Build pre-AI deterministic payload` run ID `33549958109`, run number `78`, created `2026-09-01T19:31:05Z`, conclusion `success`

The published paid lineage later remained anchored to the old `31 Aug 2026, 00:37` commercial snapshot, while subsequent giveaway-only visual commits explicitly preserved paid rows.

### Narrowest defensible historical statement
- **last proven published paid lineage:** source timestamp `2026-08-30 20:37:11 UTC` (rendered locally as `31 Aug 2026, 00:37`);
- **first proven newer mailing source:** `2026-08-31 20:36:53 UTC`, persisted by commit `2bdef90c...`;
- **first visual write opportunity after that newer source:** commit `d3d268a...` at `2026-08-31T20:37:59Z`, but its internal source binding is not reconstructible from retained accessible evidence;
- **later fresh commercial path definitely still active above visual:** September 1 mailing run `33549933036` and pre-AI run `33549958109` both succeeded;
- **exact first missed visual commercial invocation / exact trigger-removal moment:** not proven and deliberately not guessed.

This is the maximum historical precision supported by retained evidence.

## Architecture / reliability invariants
- GitHub Actions owns deterministic transforms, orchestration, canonical persistence, and fail-closed behavior per `config/execution_ownership_contract.json`.
- ChatGPT semantic incompleteness must continue to block full semantic publication.
- A scoped commercial refresh must never invent semantic truth; it may preserve previously canonical semantic labels only when coverage/provenance checks prove preservation safe.
- Scoped commercial refresh must preserve giveaway state exactly.
- No second canonical writer, scheduler, or parallel publication chain is warranted.

## Repair task assessment — final
Verdict for `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`:

`requires_one_bounded_correction`

The task is directionally correct and its hard boundaries are good, but it is **not sufficiently safe as-is** because its repair-target wording is broad enough to include the already-healthy shortlist→mailing handoff. The forensic evidence proves the missing edge is narrower and later. Leaving that ambiguity could cause an implementer to touch a healthy upstream edge or weaken the full semantic path unnecessarily.

### The one bounded correction required before repair execution
Correct only the task's **repair-target scope** so it explicitly requires:

> Repair only the missing deterministic **commercial-only visual handoff** inside the existing canonical visual orchestration: reuse `scripts/refresh_visual_commercial_fields.py` from the current deterministic commercial/pre-AI source, wire it through the existing `.github/workflows/build-daily-visual-payload.yml` as a scoped `commercial_only` path with a truthful scoped freshness receipt, preserve giveaway state, and leave the full semantic `ChatGPT production payload is not complete` fail-closed guard unchanged. Do not modify the already-working Steam→shortlist→mailing handoff and do not add a scheduler, writer, or parallel pipeline.

This is one bounded scope correction, not a redesign. The rest of the prepared task can remain unchanged, including acceptance that fresh paid source identity/timestamp must be tied to actually published paid items rather than giveaway/artifact time.

After that bounded correction, the task is suitable to enter repair/acceptance work in a separate authorized step.

## Validation
- Initial durability checkpoint persisted before investigation.
- Mid-investigation checkpoint persisted the reconstructed chain/root cause.
- Final continuation re-read this saved report from `main` before finalization.
- Historical boundary was narrowed without assigning an unsupported first-failure timestamp.
- Current pre-fix workflow/run identities were frozen.
- The scoped visual freshness receipt was frozen by exact run ID, artifact ID, artifact digest, contract, scope, output commit/blob, and upstream run identity.
- Prepared repair task was assessed against the final forensic root cause.
- No repair action was invoked.
- No workflow, production data, Taste, scheduler, writer, contract, or repair-task file was changed.

## Unresolved / forensic limitation
No unresolved item blocks repair preparation.

The exact first internal failed/missed visual commercial invocation is not reconstructible from retained evidence. This is a recorded forensic limitation, not an open guess.

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
- First retained September 1 mailing run: `33549933036`
- First retained September 1 deterministic pre-AI run: `33549958109`
- Latest frozen mailing run: `34059728770`
- Latest frozen full pre-AI run: `34059742637`
- Latest frozen scoped visual run: `34059763292`
- Latest frozen visual freshness receipt artifact: `9997090112`

## Efficiency / reusable lesson
When a canonical aggregate artifact contains independently refreshable subdomains, fail-closed correctness and freshness liveness must be modeled separately. A healthy upstream plus a successful scoped refresh for one subdomain is not evidence that another preserved subdomain is fresh.

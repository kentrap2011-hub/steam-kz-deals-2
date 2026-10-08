# Dossier throughput without quality regression — diagnostic 01

**Task:** `WORKER_TASK_DOSSIER_THROUGHPUT_QUALITY_PRESERVING_DIAGNOSTIC_01.md`  
**Mode:** DIAGNOSTIC ONLY; no implementation, no semantic Dossier publication, no scheduler changes.  
**Repository / baseline:** `kentrap2011-hub/steam-kz-deals-2`, `main`, inspected 2026-10-08 approximately 12:41 UTC.  
**State is moving:** numbers below describe that bounded observation, not a permanently frozen production snapshot.  
**Decision status:** recommendation for Director review; *not* approval to change contracts or production.

## Executive conclusion

**A defensible conditional goal is ~1.4–1.8× more *accepted* Dossier output per unit of active worker effort from preventing mechanical/referential rejection and preserving already-researched, independently valid evidence.** A wider ~1.8–2.4× scenario requires contract-governed deterministic assembly/preflight plus bounded source reuse; >2.5× is speculative and should not be a delivery commitment. No measured experiment yet establishes any actual post-change speedup or unchanged semantic quality. The lower bound of a guaranteed improvement is **zero** until a real-data, strict-validator A/B measurement is performed.

This is primarily a **failed-candidate/rework problem**, not proof that GitHub ingest itself is slow. For the current snapshot's first 10 eventually accepted groups, GitHub recorded **27 rejected transports and 10 accepted results**: **27/37 = 73.0%** of recorded outcome events were rejections, meaning 3.7 submission outcomes per accepted group. Several retries occurred for the same immutable group. A rejection is not necessarily a complete repeat of semantic research: do not turn 3.7× submission amplification into an asserted 3.7× wall-clock speedup.

The report does **not** recommend reducing Russian retrieval, neutral game-experience coverage, product/year identity, physical-source deduplication, dated evidence, privacy, provenance, or fail-closed strict validation.

## 1. Sources and reproducibility

Actual canonical sources inspected from `main`:

- `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `PROJECT_ROUTES.md`, `PROJECT_DECISIONS.md` (especially TASTE-014/015/016/017 and PPD-008/011), `config/execution_ownership_contract.json`.
- `config/taste_steam_review_dossier_runtime_prompt.md` (blob `5743c85120db2b7f50cb4230c3ba1d44e7950017`); `config/taste_steam_review_dossier_worker_prompt.md`; `config/taste_steam_review_dossier_contract.json` (blob `1335d3df358e9ec38064e026b48169f7d9ab69ee`).
- `config/taste_steam_review_dossier_schema.json`, `config/taste_steam_review_dossier_web_evidence_contract.json`, `config/taste_steam_review_dossier_terminal_receipt_schema.json`.
- `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`, current `data/production/pre_ai/taste_steam_review_dossier_validation_status.json`, and the canonical `data/production/pre_ai/taste_steam_review_dossier_work.json` route. The huge full manifest was deliberately **not used for aggregate counting**: a full contents read was truncated; the validated compact index was used instead.
- `data/audit/taste_steam_review_dossier_transport_rejections.jsonl`, `data/audit/taste_steam_review_dossier_group_failures.jsonl`, `data/audit/taste_steam_review_dossier_frozen_invocations.jsonl` (parsed line-by-line).
- `scripts/taste_steam_review_dossier_buffered.py` (strict candidate validation, rejection/quarantine, frozen acceptance), `scripts/taste_steam_review_dossier_prepublication.py`, `scripts/taste_steam_review_dossier_parallel_validation.py`, `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`.
- Ten current-snapshot GitHub `result_introduction_commit` timestamps, matched to trusted marker `run_started_at_utc` and canonical audit `recorded_at_utc`.

**Reproduction recipe:** count JSONL records by exact `snapshot_id` (rejections) or `authority_snapshot_id` (frozen accepted); never combine snapshots or the two kinds of failure ledger into one denominator. For the current first 10 accepted sequences, count rejections with `sequence <= 10` and divide by that rejection count plus 10 accepted groups. Compute GitHub ingest lag as `audit.recorded_at_utc - result_introduction_commit.created_at`. This is a *commit-to-audit* span, not isolated runner CPU time.

## 2. Measured production state and throughput

| Metric (bounded observation) | Value | Interpretation |
| --- | ---: | --- |
| Prepared snapshot date | 2026-10-06 | Still the current **GitHub** projection at measurement time; do not invent a refresh or repair in this task. |
| Required dossiers | **2,134** | Fixed prepared daily Dossier scope, not the Deep queue. |
| Group count / checkpoint size | **712 / 3 games** | Last group has fewer than three; size 3 is transport/atomic validation boundary, **not** throughput quota. |
| Accepted / failed / pending groups | **10 / 0 / 702** | `next_pending_sequence=11`. |
| Accepted / pending dossiers | **30 / 2,104** | Current snapshot, not all historical neutral-cache dossiers. |
| Frozen-authority accepted audit records | **34** | 24 preceding-snapshot, 10 current; **22 distinct successful markers** across this bounded audited population. Excludes unsuccessful invocations. |
| Retryable transport rejections, all audited | **54** | Distinct rejection events, not unique games or executions; may include older-snapshot/frozen events. |
| Retryable rejections attributed to current snapshot | **31** | 27 for eventually accepted sequences 1–10; 4 for still-pending sequences 11–14 at cutoff. |
| Historical legacy group-failure audit records | **45** | Different earlier classification/recovery semantics. **Not added** to the 54 retryable rejections or treated as current pending-state failures. |
| Current-snapshot recorded outcomes, inclusive | **31 rejects / 10 accepts** | 75.6% recorded rejection fraction (31/41), biased by censored pending work. |
| Completed-group outcome subset | **27 rejects / 10 accepts** | 73.0% rejected events, 27.0% successful events; 3.7 outcomes/accepted group. |
| Groups with ≥1 rejected transport among current 1–10 | **6/10** | 1, 3, 5, 6, 7, 8. Groups 5–8 alone account for 24 rejected submissions. |

**Observed timing:**

- For current groups 1–10: frozen run-start marker → accepted create-only result commit was **5.7–18.3 minutes**, mean **12.4**, median approximately **11.5**. It contains worker setup, research and/or reuse, synthesis, retries/assembly and GitHub create-file latency; when one marker spans multiple groups the time is cumulative, **not** an independent per-game runtime.
- Result Git commit → frozen acceptance audit was **0.22–0.87 minutes (13–52 seconds)**, mean **~21 seconds**, across those ten outcomes. This includes workflow wake-up, GitHub validation/commit visibility; it does not measure every Actions runner stage in isolation and may reflect coalesced processing.
- The earliest current accepted group was audited on **2026-10-06 14:38:48 UTC**, the tenth on **2026-10-08 12:19:42 UTC**. Thus **~10/45.7 = 0.22 accepted groups/hour**, or **~0.66 dossiers/hour**, over this *calendar* interval. **This is not sustainable scheduled-worker capacity**: the observation contains idle time, manually launched episodes and rejected/censored work.
- Across six successful current marker windows, the summed marker-to-last-accepted spans are roughly 90 minutes for ten groups (illustrative **~6.7 accepted groups/hour** inside selected successful windows). Some windows overlap and the sample excludes wholly unsuccessful attempts. This is **not** a second trustworthy baseline; it only demonstrates that long calendar gaps and failed transports dominate the comparison if ignored.
- Group 5 had six rejections; group 6 seven; group 7 five; group 8 six before acceptance. The first recorded rejection → eventual acceptance gaps were about **25 hours** for each. These are *elapsed* delays including inactivity, **not** 25 hours of proven wasted active work.

**What cannot be measured from these artifacts:** per-search and per-open timings, exact time spent collecting source metadata, separately isolatable semantic research vs JSON assembly, per-failed-submission worker active minutes, which page content was already inspected when a retry began, live tool overhead per source, and the fraction of scheduled hourly invocations that actually execute material work. Existing audit records are result/authority/progress facts, not start/finish traces for each material research route. Any such precise breakdown without new instrumentation would be fabricated.

## 3. Rejection and retry taxonomy (31 current-snapshot retryable events)

| Failure class | Count | Status and safe prevention |
| --- | ---: | --- |
| Acquisition mode ↔ parent feedback-surface mismatch | **11** | Often mechanical serialization: `inspected_collection_item` requires concrete-item collection; `search_result_observation` requires representation provenance. Do not change acquisition mode to hide an unobserved item. |
| Schema/enum/field/locator mistakes | **5** | Missing `evidence`, unsupported category, non-HTTPS child locator, invalid product-binding basis. Easily **detectable**; correcting an exact-product basis needs factual support. |
| Bound support ↔ source join / language projection mismatch | **5** | Deterministic relationship projection is a strong candidate for generation from the already-fixed evidence graph. Never invent missing source records. |
| Physical-source duplicates / aliases | **3** | Not always merely mechanical. Removing a duplicate can change recurrence/coverage; re-evaluate claims rather than silently merging independent-looking evidence. |
| Temporal, recurrence, historical/durable or coverage consistency | **5** | Often substantive: a current claim without dated support or recurrence inflation cannot be made valid by a different label. Re-research or retain uncertain/failed state. |
| Privacy/prohibited profile URL | **1** | Fail closed. Replace only if a genuinely observed safe non-profile locator exists; never hash an author ID or launder raw text into `public_ref`. |
| Exact product/title/release binding mismatch | **1** | Substantive wrong-product risk. Cannot auto-correct an identity assertion from query wording. |
| **Total** | **31** | Each is one rejected candidate event, not a distinct game or an independent newly discovered semantic defect. |

At least **16 mode/join failures (11+5)** are strong *deterministic-assembly* targets, conditional on the supporting facts already being truthful. Some of the five schema failures (unsupported enum and missing structural field) are similarly preventable; **~16–19 of 31 (52–61%)** is a **candidate preventable subset**, **not** a proven safe auto-repair count. All 31 are *detectable* by current strict validation; detecting is different from truth-preserving repair. Remaining dedupe, current-state dates, exact identity, privacy, recurrence and coverage must retain semantic inspection.

The 45 historical `group_failures` show the same families (duplicates, unsupported categories, acquisition-parent mismatch, dates and author/profile URLs), but reflect earlier handling in which invalid groups were moved to a different failed/recovery path; combining them as 99 contemporary retries would be methodologically false. There is no evidence that simply loosening the validator would improve *valid* throughput.

## 4. Time-cost model and independent bottlenecks

Use the following nonoverlapping buckets:

1. **Required semantic work (cannot be removed):** exact title/work identity + release year and identity-role corroboration; multiple credible physical player-feedback surfaces where available; Russian/mixed player-feedback attempt with the strict `found_and_used` gate; material dated current-state evidence; 12-dimension neutral coverage and balanced strengths/weaknesses; concise attributable observations/conflicts. The TASTE-014 adaptive distinct-route rule already avoids equivalent-route loops; search/page ceilings are **not active** and must not be reintroduced.
2. **Avoidable deterministic construction:** local `source-NNN`/`feedback-NNN`, source/feedback joins, canonical ordered language projection, category enum choice, domain normalization, summary count sentence, provenance parent/mode compatibility and copying exact immutable descriptor fields. Mechanical assembly consumes context/tool/output budget and creates the dominant logged rejection categories.
3. **Avoidable repeated submission/rework:** candidate is immutable create-only, rejected transport is GitHub-quarantined with zero semantic attempts consumed; same group can legitimately be resubmitted only as authorized by a later exact GitHub frozen view. Every failed group submission risks repeating serialization and some research. The audit proves frequency, **not duration**.
4. **GitHub ingest/validation:** measured ~13–52 seconds between accepted candidate commit and acceptance audit, short relative to 5.7–18.3-minute successful marker-to-commit spans. Shared serialized writer is necessary for correctness, and already processes present independent groups without waiting for earlier gaps.
5. **Grouping/round trips:** three games are atomic; failure in one submitted Dossier rejects the complete candidate. Frozen same-invocation traversal **already removes** per-sibling ingest waiting. A proposal to “stop waiting for each group” would duplicate an implemented optimization.
6. **Source repetition and schedule gaps:** source reuse between similar games or failed attempts has no instrumentation proving its magnitude. The hourly orchestration is externally owned; idle time/manual starts cannot be attributed to GitHub validation.

**Conditional retry tax:** for the 10 completed groups, 27 rejected submissions precede 10 accepted submissions (2.7 rejected events per accepted). If correcting/repeating a rejected submission consumes **2–5 active minutes** (explicit *assumption*, not logged), that corresponds to **54–135 hypothetical active minutes** across these ten groups. It is incorrect to present the ~25-hour rejection-to-acceptance gap as active computation. Candidate GitHub validation itself takes seconds in the accepted sample; reducing GitHub wake-up overhead alone cannot account for the largest plausible gain.

## 5. Quality and authority invariants (all recommendations must satisfy)

**Q1** Exact immutable GitHub-prepared snapshot, marker-parent frozen index, descriptor, plan order, group hash, AppID/title and work/source/contract bindings.  
**Q2** Unchanged V2 Dossier schema/enum semantics, Russian gates, TASTE-014 distinct-route boundedness and TASTE-015 coverage closure, including current/historical/durable distinctions and both strengths and trade-offs.  
**Q3** Only *directly observed*, exact-product player-feedback material; no fabricated sources, dates, feedback records or claims; no aggregate-only counts treated as player feedback.  
**Q4** Strict physical-source/feedback dedupe, exact parent-child surface identity, concrete acquisition-mode truth, local record joins, and date/language derivation.  
**Q5** Privacy: no raw reviews/snippets/quotes, profile locators, usernames or author-derived identity; safe neutral provenance only, no author fingerprint caching.  
**Q6** Identical or stronger GitHub-owned strict/fail-closed validation, quarantine and independent group state; no auto-accept on a worker-side check, no fake “success” from a buffered candidate.  
**Q7** GitHub exclusively owns scope, order, retry/recovery eligibility, liveness, cache compatibility, current group classification and Deep recomputation; worker executes only bounded authorized semantics.  
**Q8** Deep consumes only canonically accepted, current-compatible Dossiers; no Fast prerequisite and no change to Deep ranking, stage semantics, UI or Steam discovery.

**Quality-proof procedure before any production rollout:** replay real, historically recorded accepted/rejected immutable inputs in an isolated CI/test environment under the *unchanged* canonical validator; assert no formerly rejected payload is newly accepted merely by lossy conversion, no duplicate source becomes independent, no fabricated/renamed provenance, no weakened 12-dimension gate or dated Russian support. For a representative real-data set of easy, obscure, Russian-sparse, DLC, temporal-conflict and repeated-source games, independently compare semantic coverage, evidence attribution, downstream Deep usability and rejection reason accuracy before/after. **No synthetic production data** and no production result writes. Proof of equivalent *semantic quality* requires this review, not only a JSON-schema pass.

## 6. Acceleration candidates (independent estimates, NOT additive)

All ranges below are planning hypotheses in **accepted output per unit of active effort**, holding identical scope/semantic requirements. They cannot be multiplied naively; approaches overlap. `Q1–Q8` always remain mandatory.

| ID, option | Expected independent gain | Quality invariant / specific risk | Authority and change surface |
| --- | --- | --- | --- |
| **A. Read-only failure dashboard, stage timing** | ~1.00× immediate; enables reliable later bounds | Q1–Q8 unchanged; telemetry must exclude raw review/user data; counters cannot become stop quotas. | GitHub-owned read-only diagnostics/CI; **no worker-prompt change** if added without semantic input changes. |
| **B. Canonical descriptor/JSON assembly from already-authorized data** | ~1.10–1.40× if mode/join errors fall | Q1/Q3/Q4/Q6: derive sequential IDs, language unions, exact descriptor echo and summary from existing **real** records; never create evidence. | GitHub-owned deterministic helper/bridge requires architecture and transport contract review; worker prompt/compatibility if serialization responsibilities change. |
| **C. Deterministic pre-submission fail-closed check** | ~1.20–1.65× in rejection-heavy conditions | Q2–Q6: same canonical validator, earlier *reject* only; repairs cannot auto-supply missing dates, identity or sources. | **Contract change required.** Existing `scripts/taste_steam_review_dossier_prepublication.py` is explicitly **CI/developer parity utility only**, not a Scheduled-worker Python/manual gate. Need a GitHub-owned or explicitly contract-authorized validation handoff; **do not just tell Scheduled ChatGPT to run/emulate this script**. |
| **D. Remove redundant prompt prose, auto-supply exact enums/templates** | ~1.03–1.12×, uncertain | Q2/Q3/Q6: preserve full semantics and strict validator. Runtime prompt outranks conflicting traversal prose in worker prompt; remove ambiguity only, not research gates. | Worker-prompt change modifies worker binding/hash, needs version/compatibility review and cache impact assessment. No silent in-place rebind. |
| **E. Move mechanical provenance normalization to GitHub** | ~1.10–1.35×, overlaps B | Q3–Q5: safe normalization of observed URL/domain, joining, source IDs; **never** fabricate physical sources, suppress duplication, infer Russian/date/identity from query. | GitHub control-plane code + contract/provenance bridge, machine validation and compatibility migration. |
| **F. Reuse already observed exact-product normalized source metadata** | ~1.05–1.20× if real overlap is proven | Q1/Q3–Q5: content/safe locator and observed factual date only, scoped by appid/work/release and allowed freshness; never reuse stale semantic **conclusions**, raw text or identities. Re-verify when source/current-state changes. | Bounded GitHub-owned ephemeral or TTL cache, contract/data lineage changes; audit cache hits and misses. Existing strict per-item *Dossier* cache reuse already exists; do not duplicate it. |
| **G. Research/assembly split inside same invocation** | ~1.05–1.15× if fewer rewrites | Q2–Q4: keep complete balanced research before “sufficient”; assembly from frozen observed evidence graph, no persistent second semantic queue. | Can start as worker guidance/contract design; persistent cross-invocation split requires durable schema, ownership and compatibility work. |
| **H. Group size 2 / 3 / 4 comparison** | Indeterminate (plausible 0.8–1.2×, may regress) | Q1/Q6: larger groups magnify atomic failure blast radius; smaller groups increase transport overhead. No throughput quota and no skipping difficult games. | Current **3 is not a confirmed bottleneck**. Changing group size changes GitHub plan/groups/hashes and migration; only evaluate with real-artefact offline benchmark after A–C. |
| **I. Independent group concurrency** | Potential 1.2–2.0× *capacity* only if research is truly parallel | Q1/Q6/Q7: existing frozen ordered pending list cannot simply be processed by multiple duplicate workers; no worker-chosen shards, skipped sequences, competing artifact collisions, race in canonical writer or second scheduler. | **Architectural / contract-first**, GitHub-owned exact lease/shard authority and serialized acceptance; no Scheduled Task change in this task. |
| **J. Avoid redundant terminal/transport round trips** | ~1.00–1.08× expected | Q1/Q6: one marker per invocation and one create-only candidate **or** true semantic-exhaustion receipt per exact group; never misclassify tool failure as semantic exhaustion. Buffered siblings already do not wait for ingest. | First instrument. Changes to marker/receipt semantics require explicit frozen-authority/terminal schema migration; likely low return. |
| **K. GitHub-owned mechanical retry on validation failure** | ~1.05–1.25× *only* for provably deterministic reversible transforms | Q3–Q7: auto retry is forbidden for wrong product, dated evidence gap, source alias, unsupported semantics, incomplete coverage or privacy leak. No silent auto-accept or unbounded loop; same exact authority/attempt accounting. | **Do not implement under current contract.** Explicit GitHub retry authorization + retry state/versioned transport contract needed. Prefer prevention at C/B over after-the-fact retries. |

**Low-risk/no worker-prompt changes:** A (measurement) and offline developer parity/regression tests. The already-existing strict per-item Dossier cache reuse and no-ingest-wait frozen traversal require **no** new work. A bounded improvement to GitHub's assembly code (B/E) is mechanically plausible, but is **not** contract-free if it changes what the worker submits.

**High-risk/incompatible:** automatic category relabeling, inventing a safe URL or publication date, folding genuinely distinct views into one “source,” silently dropping duplicate supports while preserving recurrence, changing `research_state` to sufficient for sparse coverage, lowering Russian/dated evidence bar, adding an independent queue/sharded scheduler, changing group size in the current immutable snapshot.

## 7. Practical throughput model / assumptions

Let `S` be the active effort for one ultimately accepted group (including its correct research/assembly/one submission); `r*S` the incremental effort for **one rejected** submission plus related correction, with `r` unknown. For the 10 groups with 27 rejected events, observed normalized effort per accepted group is `S × (1 + 2.7r)`. If a fraction `p` of those rejections can be prevented *without losing evidence*, predicted relative speedup is:

`G = (1 + 2.7r) / (1 + 2.7(1-p)r)`.

Scenarios using expressly **unmeasured** `r` and `p`:

| Case | Assumptions | Modeled gain |
| --- | --- | ---: |
| Conservative | `r=0.20`, `p=0.50` | **1.21×** |
| Realistic candidate | `r=0.35`, `p=0.65` | **1.46×** |
| High-value rejection prevention | `r=0.50`, `p=0.80` | **1.85×** |
| Pure illustrative ceiling | `r=1.00`, `p=1.00` | **3.70×** — *not* defensible for total runtime |

The 16–19 strongest mechanical candidates are 52–61% of *all* current rejection events; `p=0.65–0.80` additionally assumes more failures become safely **preventable before write** through feedback to semantic assembly, not automatically fixable. `r=0.2–0.5` says a rejected transport consumes 20–50% of a successful group's active effort; no existing journal measures that. If `r` is near zero, preventing rejections yields little active-time gain even though it strongly improves accepted-output reliability and operator experience.

**Practical conditional throughput illustration** (hold the *same* invocation opportunities/idle pattern; not a forecast): the measured 0.66 accepted dossiers/calendar-hour would become ~0.80 with 1.21×, ~0.96 with 1.46× and ~1.22 with 1.85×. Because this historic interval contains manual sessions and backlog stalls, **do not use these absolute rates as the future scheduled hourly SLA**. In successfully running windows, marker/result evidence suggests multi-group output can already be much faster; A should first measure a representative week of real scheduled invocations before a capacity promise.

Combined planning envelope, avoiding naive product of overlapping options:

- **Conservative: 1.15–1.35×**, structured preflight catches a minority of repeatable mechanical faults, no risk to semantic gates.
- **Realistic target: 1.4–1.8×**, deterministic assembly + same strict preflight + truthful reuse, after compatibility and quality A/B checks. This is the recommended evaluation target, **not yet measured improvement**.
- **Optimistic: 1.8–2.4×**, adds proven source-metadata caching and less reassembly under comparable work mix; only after instrumentation shows semantic research is not the dominant irreducible cost.
- **Speculative architectural ceiling: up to ~3×** on certain parallelizable workloads; no claim of overall x3, no proof that independent group parallelism is legal/safe or would respect current cadence.

Do **not** claim an exact percentage of total time used for web research, provenance, retry or GitHub writes: only the timestamp bounds and categorical failure counts are durable today.

## 8. Prioritized follow-up implementation sequence (not executed)

### Quick wins — diagnostic/offline, no production semantics altered

1. **A / instrumentation contract design**: specify privacy-safe timestamps for marker seen, per-group research start/stop, source-metadata construction, candidate create, GitHub ingest, failure-class reassembly and number of safe exact-product source routes; ensure no raw user/player content and no numeric research cap. GitHub publishes a concise aggregate report, not a new queue. Can begin without changing semantic worker prompt if counters come from GitHub observable facts; worker-side research phase timings need explicit prompt/transport privacy and ownership review.
2. Build offline, **read-only** fail-closed regression fixtures from actual 54 transport rejection reasons, 45 distinct older failure ledger records and 34 accepted frozen outcomes. Classify *detection* versus *truth-preserving repair*; canonical validator must remain unchanged. Existing developer prepublication parity utility is useful **only in CI/offline mode**.
3. Ask Director to authorize a **contract/recon task** defining when immutable evidence can be assembled/checked before the one allowed create-only publication. No prompt edits yet. Quantify source-reuse duplication using safe identifiers; do not persist raw review evidence.

### Medium — after architecture preflight, bounded PRs and mandatory gates

4. **B/E first:** GitHub-owned deterministic assembly of local join IDs, record-derived language unions, descriptor echo and safe URL/domain normalization from explicitly observed semantic facts; prevent mismatched mode/parent serialization where both facts were actually observed. Add real-data positive/negative parity regressions. May require a versioned intermediate evidence graph; never infer omitted semantic facts.
5. **C:** design/implement an explicitly authorized GitHub-owned pre-submit strict validation path using the canonical validator and same immutable authority/binding. Quarantine or return fail-closed detail *before* final create-only candidate, without a second progress owner or silent group acceptance; choose transport contract carefully to avoid adding more write round trips than it saves. Explicitly update `prepublication_validation` policy first; current worker forbids mandatory local Python/manual checking.
6. **D/G/F** only if measured: simplify conflicting traversals without changing semantic coverage, split in-invocation research from machine serialization, and TTL-bound safe exact-product source metadata. Any worker prompt/hash/contract change requires binding compatibility and old-snapshot/cache behavior review.

### Architectural — defer unless the medium changes fail to meet target

7. **H/I**: offline compare strict complete-group outcomes on real games under alternative size/sharding. Preserve exact GitHub group plan, descriptor binding, single canonical writer and nonblocking independent ingest. If parallel work is genuinely profitable, specify a **GitHub-owned** lease/assignment and recovery contract before implementation; ordinary interactive chat / Scheduled Task must never choose scope or operate a second scheduler.
8. **J/K**: only if aggregate instrumentation proves significant remaining transport overhead; automatic retry strictly for provable mechanical and exact-authority-safe transformations, never for semantically incomplete or provenance-invalid evidence.

**Recommended acceptance gates for each later PR:** zero loosening of the strict validator; identical required evidence and Russian/temporal/neutral coverage rules; no new fabricated sources or identity; unchanged exact source/binding and fail-closed outcomes on known negative fixtures; atomic state and read-only Deep handoff regressions; measured reduction in rejections **and** equal or better independent downstream evidence usefulness on comparable real work. An increased acceptance count alone is not evidence of equal quality.

## 9. Dossier → Deep and scheduler safety

- Dossier accepted state is GitHub-owned in the canonical manifest/neutral cache; `scripts/build_progressive_pass2_work.py` recomputes Deep eligibility **from strict accepted Dossiers** after Dossier ingest. Mere create-only buffer presence or a failed/invalid candidate never satisfies Deep. The current workflow shares the `taste-steam-review-dossier-canonical-writer` noncanceling serialization boundary and commits progress/projection atomically.
- Deep eligibility does not require prior Fast/PASS 1. Dossier frozen-authority late rollover may populate compatible neutral cache, but must not rebind old group identity or partially advance a new snapshot.
- Existing canonical group-size 3, frozen marker-parent liveness, per-item strict compatible dossier cache reuse, independent group validation, and forward sibling traversal are already active. Avoid claiming these are novel speedups.
- Current external hourly Scheduled Dossier cadence is **not changed**. No new recurring task, worker-selected shard, retry manager, recovery loop, backlog manager, dataset sample or semantic Dossier result has been created.

## 10. Worker closeout and limitations

**Diagnostic status:** evidence analysis completed; implementation deliberately **not** started.  
**Deliverable:** `reviews/worker_reports/dossier-throughput-quality-preserving-diagnostic-01.md` in a report-only PR.  
**Recommended Director action:** review the ~1.4–1.8× conditional target, then commission a bounded contract/instrumentation/real-data parity task **before** asking another worker to implement prepublication validation. Do not approve a new scheduler or a weaker evidence contract.  
**Unproven:** actual current Scheduled Task utilization, active minutes per rejected attempt, exact research vs provenance time share, cached-source opportunity size, and real post-change throughput/quality. These unknowns cap confidence in the estimates.

### Architecture preflight for the recommendations

1. **Owner:** GitHub remains the only control-plane owner, `config/execution_ownership_contract.json` and `config/taste_steam_review_dossier_contract.json`. Worker remains semantic data plane.
2. **Permission:** this task grants *diagnosis only*. Any runtime/prepublication/retry/group-size/concurrency write requires a *separate* explicit canonical contract authorization first.
3. **No migration of ownership:** proposed assembly/preflight/retry/caching authority must remain GitHub-owned; worker cannot select work, classify accepted state, or substitute its self-check.
4. **No hidden recurring stage/queue/quota:** proposals must preserve one existing Dossier semantic stage and the explicit external scheduler; unapproved new queue, retry loop, shard/scheduler or daily quota remains forbidden.

**Final answer:** Based on 27 observable retryable rejections preceding ten successful groups, there is a credible, **conditional** opportunity to make Dossier **approximately 40–80% faster per active unit of work** by preventing mechanical rejection and avoiding truthful evidence reassembly. There is **not enough phase-timing evidence to promise** that result yet; all stronger numbers require instrumentation and unchanged-validator/semantic-quality proof on real data.

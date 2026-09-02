# System Audit — Baseline 01

Date: 2026-09-02
Role: `SYSTEM AUDITOR`
Mode: `READ-ONLY / AUDIT`
Status: `complete`

## Scope

This audit checked the current production system as an end-to-end user-result pipeline, not as a collection of locally correct components. It used bounded current evidence only and did not modify production code, configuration, contracts, ranking policy, Taste policy, queues, providers, or production items.

Primary evidence reviewed:

- `SYSTEM_AUDITOR_ROLE.md`
- `DIRECTOR_REVIEW_CHECKPOINTS.md`
- `DIRECTOR_TASK_BOARD.md`
- `reviews/worker_reports/trine4-missing-diagnosis-01.md` (blob `28be8b531be3918f0981076ebbf0b08d50dbc16c`)
- `reviews/worker_reports/taste-runtime-trigger-status-01.md` (blob `0bc7ed57b5a288413882cb7d94a88e60e0cc9663`)
- `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md` (blob `85ad9d5cdd26d066dc1996773d4f35bd5de3b9cd`)
- `data/production/pre_ai/chatgpt_payload.json` (blob `4e6b1f793a094241c86f0039c2b746f00c005c3d`)
- `data/production/pre_ai/history_snapshot.json`
- `config/execution_ownership_contract.json` (blob `f0b5f48756489965ec223a42f3b234f62ac4bae1`)
- `.github/workflows/ingest-taste-batch.yml` (blob `3242fbe96fba9ab6a2165176a852a0fedbead759`)
- `.github/workflows/build-daily-visual-payload.yml` (blob `2d56b81f822412c433852d55a749a4db8ce33b78`)
- `.github/workflows/deploy-visual.yml` (blob `625a22da18300795974ba6e3b46c6b92db1184d4`)
- `reviews/worker_reports/giveaway-igdb-implement-prep-01.md` (blob `1a53652e5c4a6c3fc19f735c2e2a226b4e5c9026`)
- `reviews/worker_reports/itad-terms-permission-prep-01.md` (blob `5d2d7f7be0104484e80fed9e787deebd993e2d05`)
- `.github/workflows/persist-ai-pilot-25.yml` (blob `ccfbcd2f703d6cf40fd2277985fdc0ee6e823bbb`)
- `.github/workflows/test-one-real-taste-persistence.yml` (blob `6c023ef5c7f91ef4f2ff183707cd69d595e10a50`)

## Executive conclusion

The deterministic GitHub side has strong ownership contracts and several fail-closed checks, but the whole system is **not yet self-proving end to end**. The largest gap is that a large semantic workload can be correctly queued while the actual scheduled semantic runtime remains operationally unobserved. Because unresolved semantic readiness is fail-closed at visual admission, that runtime blind spot becomes silent user-visible omissions rather than an explicit degraded state.

A second independent gap exists after data preparation: a successful visual workflow/deploy chain does not necessarily prove that a fresh visual payload was rebuilt for the current source cycle. The current workflow can legitimately skip the build when a prerequisite is not ready and still conclude successfully, after which deployment may publish the previously committed payload.

The audit therefore finds two high-impact completion/observability defects, one high-impact stale-success control-flow defect, one current provider-operability limitation, and one bounded ownership-complexity risk.

## Finding 1 — Semantic work can be queued without a verified execution heartbeat

**User impact**

A valid live-sale game can remain absent while its sale window continues to run because queue presence does not prove that the scheduled semantic worker is enabled, running, or going to run soon. There is also no verified standard immediate trigger from the currently inspected execution surface.

**Evidence**

- Current `data/production/pre_ai/chatgpt_payload.json` is internally `status=complete`, but at `source_mailing_updated_at_utc=2026-09-02T18:00:45.930255+00:00` it has `source_family_count=743`, `ai_queue_count=644`, and `ready_without_ai_count=0`.
- `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md` explicitly states that no trustworthy live value was captured for the scheduled automation's `enabled` state, exact schedule/RRULE, or `next_run`, and that no separate supported `Run now` operation was confirmed.
- `reviews/worker_reports/taste-runtime-trigger-status-01.md` confirms `App_690640` was queued but active processing was not confirmed.
- The Trine 4 incident proves this is user-visible, not merely theoretical: the game had a valid KZ sale and remained blocked on unresolved semantic work.

**Severity:** `high`

**Certainty:** `proven`

**Bounded verification/fix candidate**

Run one acceptance task for the **existing** scheduled semantic runtime that records a canonical operational signal sufficient to answer: enabled/disabled, expected cadence or next execution, last successful execution, and whether the current GitHub-prepared queue is making progress. If the platform cannot expose all fields, require an equivalent bounded heartbeat/progress proof tied to the current queue. Do not create a second scheduler or a parallel semantic path.

## Finding 2 — Fail-closed semantic readiness silently removes valid candidates from the user-visible choice set

**User impact**

When semantic readiness is missing, the system does not present an explicit “analysis incomplete / feed degraded” result for the affected paid candidate; it simply omits the candidate from the final list. This can make an incomplete recommendation set look authoritative and can materially squeeze the user's available choices during time-limited sales.

**Evidence**

- `reviews/worker_reports/trine4-missing-diagnosis-01.md` traces `App_690640` as present in the live KZ source, shortlist, purchase/deal context, and Taste queue, then first absent at `scripts/build_visual_feed_v2.py::get_fit()` because there is no usable current `resolved_taste_fit` / cache verdict. Ranking never receives the game.
- The same report confirms the UI consumes the canonical visual payload and cannot rediscover a game skipped before visual assembly.
- Current `chatgpt_payload.json` has `644` AI queue rows out of `743` source families and `ready_without_ai_count=0`; `complete_family_partition=true` proves accounting completeness, not user-result semantic completeness.
- The ownership contract intentionally requires fail-closed behavior when required inputs are incomplete. The local safety rule is therefore working as designed, while the system-level user result is still partial.

**Severity:** `high`

**Certainty:** `proven`

**Bounded verification/fix candidate**

Add an end-to-end publication/readiness acceptance that distinguishes “scope successfully partitioned” from “user-visible recommendation result sufficiently complete.” At minimum it should surface current unresolved semantic counts/age and prove that a published feed cannot silently look fully current while a materially large required semantic scope is unresolved. This is a completion/observability task, not a Taste-policy change.

## Finding 3 — A green visual workflow/deploy does not prove that the published feed was freshly rebuilt

**User impact**

The automation can appear healthy while users continue seeing an older sales payload. For a time-sensitive deal feed, a green workflow that only republishes stale `current.json` is a false operational success signal.

**Evidence**

- In `.github/workflows/build-daily-visual-payload.yml`, the history-readiness step deliberately exits successfully when `history_snapshot.json` is missing or not ready and writes `ready=false` rather than failing the job.
- The actual visual build step runs only when `steps.history.outputs.ready == 'true'`.
- Validation, ranking export, lookup build, and canonical visual commit are conditional on `steps.build.outputs.built == 'true'`; therefore a no-build path can finish without producing a fresh visual commit.
- `.github/workflows/deploy-visual.yml` triggers from successful completion of `Build daily visual payload`, checks out current `main`, and stages the already committed `data/production/visual/current.json` into `web/data/current.json` before Pages deployment.
- Current `history_snapshot.json` is ready now (`status=complete`, `complete_coverage=true`), so this audit is not claiming that today's current payload was produced through the stale branch. The hidden failure mode itself is nevertheless directly encoded in the workflow control flow.

**Severity:** `high`

**Certainty:** `proven`

**Bounded verification/fix candidate**

Create one end-to-end freshness acceptance for `source/pre-AI cycle -> visual build -> canonical visual commit -> Pages deploy`. It should prove that a successful ordinary daily deploy is bound to the intended current source cycle, or explicitly classify the run as degraded/no-fresh-build instead of treating both outcomes as equivalent success. Do not redesign the pipeline.

## Finding 4 — Cross-store giveaway identity currently has no accepted operational primary route

**User impact**

Epic/GOG giveaways can be discovered and shown while exact binding into the canonical Steam family / description / Taste analysis path remains incomplete. That limits the quality and consistency of giveaway analysis compared with Steam-native items and makes this feature dependent on an unresolved provider decision.

**Evidence**

- `reviews/worker_reports/giveaway-igdb-implement-prep-01.md` says the IGDB production continuation is blocked on Twitch/IGDB credentials and requires live provider/source semantics before any production identity binding is authorized.
- `DIRECTOR_TASK_BOARD.md` records Twitch/IGDB as fallback because Twitch 2FA/support is blocked/pending.
- `reviews/worker_reports/itad-terms-permission-prep-01.md` records ITAD as a technically promising exact-ID route, but implementation is forbidden until explicit permission is received.
- The board records the permission request as sent and sets a fallback-decision SLA; ITAD is not an accepted production dependency today.

**Severity:** `medium`

**Certainty:** `proven`

**Bounded verification/fix candidate**

Keep the existing provider SLA. If ITAD permission is not operationally available by the recorded threshold, run the already-planned bounded fallback decision/acceptance rather than leaving cross-store identity in indefinite external wait. Whatever route is chosen must preserve exact provider IDs, unique Steam appid binding, and explicit unresolved status for incomplete coverage.

## Finding 5 — Legacy one-shot Taste mutation workflows remain as alternate dispatchable write paths

**User impact**

Multiple manual workflows capable of writing the canonical Taste overlay increase operator/ownership ambiguity. An accidental or later-repurposed dispatch could bypass the current transactional inbox workflow and make it harder to reason about which mechanism is authoritative for production semantic persistence.

**Evidence**

- The current production ingest workflow, `.github/workflows/ingest-taste-batch.yml`, is triggered by `data/ai_inbox/taste/*.json`, runs transactional proof validation, calls `scripts/process_taste_inbox.py`, and commits synchronized overlay/index/receipts/pre-AI consumer state.
- `.github/workflows/persist-ai-pilot-25.yml` still has `workflow_dispatch`, `contents: write`, calls `scripts/ingest_taste_results.py`, and commits `data/cache/taste_fit.entry_overlay.json` directly to `main`.
- `.github/workflows/test-one-real-taste-persistence.yml` also still has `workflow_dispatch`, `contents: write`, calls `scripts/ingest_taste_results.py`, and commits the overlay directly.
- Both legacy workflows contain strict historical preconditions, so this audit does **not** prove that either can successfully mutate today's current state. The risk is the continued existence of alternate production-capable write mechanisms and the ambiguity they create.

**Severity:** `medium`

**Certainty:** `risk_hypothesis`

**Bounded verification/fix candidate**

Run a small ownership inventory limited to dispatchable workflows that can write Taste canonical state. Prove whether each is still needed and production-safe; retire/disable or explicitly constrain obsolete one-shot paths so that the current transactional inbox path is the only normal production semantic write route.

## Director recommendations

1. **Highest impact:** create and run `WORKER_TASK_SEMANTIC_RUNTIME_COMPLETION_ACCEPTANCE_01.md` as a bounded acceptance/recon task covering Findings 1–2. Exact starting refs: `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md`, `reviews/worker_reports/trine4-missing-diagnosis-01.md`, `data/production/pre_ai/chatgpt_payload.json`, `config/execution_ownership_contract.json`, and `scripts/build_visual_feed_v2.py`. Goal: prove the existing scheduled semantic worker is operationally observable and prove the user-visible feed has an explicit completeness/degraded-state signal when required semantic work is unresolved.

2. **Second:** create and run `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_ACCEPTANCE_01.md`. Exact starting refs: `.github/workflows/build-daily-visual-payload.yml`, `.github/workflows/deploy-visual.yml`, `data/production/pre_ai/history_snapshot.json`, and `data/production/visual/current.json`. Goal: prove that ordinary successful deployment is bound to a fresh intended production cycle, or explicitly reports a no-fresh-build/degraded outcome rather than silently redeploying the previous payload.

The existing ITAD/Twitch provider track should continue under the already recorded Director SLA; it does not need a third audit-created task at this checkpoint.

## Completion

Status: `complete`

Report: `reviews/system_audits/baseline-01.md`

# Dossier V2 reusable batches + exact fresh6 — IMPLEMENT report

Task: `dossier-v2-reusable-batches-fresh6-launch-ready-implement-01`  
Repository: `kentrap2011-hub/steam-kz-deals-2`; source of truth: `main`  
Author/role: developer implementation only — no semantic run, independent QA or owner-issued grant  
Final consolidated source: [PR #440](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/440), **retargeted to main**; leave draft/NO MERGE until independent physical-chat L3 PASS.  
Reviewed code commit before this report: `e6f58f24c3aa346f04d468f456d5751dceecc03a`; final PR HEAD is this report's descendant (verify directly on GitHub).

## START and architecture / relevant source

Completed the full current `CHAT_PROTOCOL.md` START gate, read `CHAT_CONTEXT.md`, this task, relevant `CURRENT_TASK.md`, `PROJECT_ROUTES.md`, `PROJECT_DECISIONS.md`, `config/execution_ownership_contract.json`, `config/dossier_research_notes_v2_contract.json`, the final strict/writer contracts and source PR #438/#439/#440.

Ownership unchanged: **GitHub** prepares exact finite source/work identity, immutable index/group descriptor/blob evidence, one-use trial grant, manifest, marker, separate owner authorization and GitHub run proof, per-item status, strict writer and sandbox. **Separate ChatGPT semantic workers** only collect independent evidence and return per-item exact prepared Research/Assembly JSON. Developer/operator cannot select a queue, self-grant semantics, dispatch an owner's Actions, schedule, retry or claim canonical acceptance.

`config/dossier_research_notes_v2_contract.json` global `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false` and `production_enabled=false` remain unchanged. Original18 fixed 18-game identity and earlier one-use SHA/authorities are untouched. No V1, Deep, production or site change; no new scheduler or automatic retry.

## Source consolidation and exact write set

- **Reused PR #439:** the original six-game GitHub-prepared `config/dossier_notes_v2_fresh6_preparation_contract.json` and its **read-only** immutable source guard/tests (PR #438 readiness and approved edition identity). These are historical pinned provenance, **not** issuer or execution authority.
- **Reused/generalized PR #440:** the real V2 `scripts/dossier_research_notes_v2.py` frozen manifest validation, `scripts/dossier_notes_v2_per_item_receipts.py` per-item Git-bound Research/Assembly transport and run proof, `scripts/taste_steam_review_dossier_buffered.py` strict per-item writer, shared serialized `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`, and the existing PR CI `.github/workflows/validate-dossier-research-notes-v2.yml`.
- **New reusable contract files:** `config/dossier_notes_v2_batch_policy.json`, `config/dossier_notes_v2_batches/dossier-notes-v2-fresh6-20261111-first.json`, `scripts/dossier_notes_v2_batch_preflight.py`. A future batch adds one *separately GitHub-reviewed* finite cohort data contract with unique `trial_id` and pinned GitHub source descriptor, but requires no new runtime/worker prompt/workflow/allowlist. Contract cardinality 1–24 items, maximum 24 groups; no scheduling and no runtime queue selection.
- **New reusable source:** `scripts/dossier_notes_v2_batch_route.py` (immutable grant/manifest/marker/authenticated Actions chain and SHA checks), `scripts/dossier_notes_v2_batch_issuer.py` (manual owner one-use freeze and separate authorize), `scripts/dossier_notes_v2_batch_pilot.py` (one-item bounded Research or Assembly transport), and `scripts/test_dossier_notes_v2_batch_route.py`.
- **New reusable GitHub owner-only Actions:** `.github/workflows/issue-dossier-notes-v2-batch.yml` and `.github/workflows/authorize-dossier-notes-v2-batch.yml`. The latter authenticates **exact trial ID + marker SHA** via GitHub-verified workflow `run-name`, first attempt, actor ID, run ID, successful completion and workflow/ref.
- **Reusable semantic launchers:** `config/dossier_notes_v2_batch_research_manual_one_shot_prompt.md` and `config/dossier_notes_v2_batch_assembly_manual_one_shot_prompt.md`; owner steps `config/dossier_notes_v2_batch_operator.md`.
- **Superseded, deleted from final PR:** hard-coded fresh6 issuer/route/pilot/test, fresh6-specific manual Research/Assembly prompts, and fresh6-only issue/authorize workflows. Historical worker reports are retained as source audit, not executable mechanisms.
- PR #440 now directly targets **main** and includes what PR #439 had prepared; PR #439 remains open and **must not be merged separately** before independent reviewer resolves its replacement status. No new PR #441 or one-off mechanism was created.

## Exactly frozen first cohort

`trial_id=dossier-notes-v2-fresh6-20261111-first`  
`snapshot_id=25c227d782188699f56b5702b3f0cfa63b101d890f09620b7b59893fab93c1af`  
Source group descriptor sequences: **1 and 70**; exact descriptor Git blobs and candidate AppID/title/edition/source item indices pinned inside cohort data.

1. `1000010` — Crown Trick
2. `102600` — Orcs Must Die!
3. `1029690` — Sniper Elite 5
4. `49520` — Borderlands 2
5. `499180` — Braid, Anniversary Edition
6. `501590` — Bulletstorm: Full Clip Edition

No replacement of these six with changed edition/title/source. Candidate status is `source_verified_not_authorized`; this source identity never serves as semantic approval. For new batches, data contract is reviewed and frozen again by GitHub, with unique SHA and one-use grant.

## Isolation, typed outcomes and fail-closed behavior

Per-cohort sandbox `sandbox/{trial_id}`; only `data/control/dossier_notes_v2/batch_pilot_store/{trial_id}` and `data/control/dossier_notes_v2/batch_pilot_accepted/{trial_id}` receive strict output. Canonical `data/cache/taste_steam_review_dossiers`, production, Deep and V1 cannot be selected in batch mode. The existing `taste-steam-review-dossier-canonical-writer` lock serializes the manual isolated writer against canonical work but does not grant canonical writes.

Each issuer commit is a **one-add exact Git parent**: reviewed main source → separate owner grant → frozen manifest → unique nonce marker → distinct later authorization. Code, policy and cohort source cannot change on sandbox first-parent history. Authenticated successful first-attempt owner Actions run must bind the *same* marker and cohort, not merely be any prior successful run. Direct transport is Git create-only and receipt-bound; strict-ready items persist independently of insufficient/invalid/missing siblings, then same binding replay produces no duplicate. No silent automatic retry or batch-wide abort because one game's evidence was insufficient.

## Executed verification (real GitHub Actions, synthetic evidence only)

First successful consolidated source-code test head: `0062f5311d5c77c9de5d783df49b8f2ca9d2a6e6`; **7/7 GitHub PR CI workflows succeeded**, including:
- Validate inactive Research Notes V2 and autonomous Assembly — run `43279473423`;
- Validate inactive Dossier final GitHub acceptance integration — `43279474006`;
- Validate inactive Dossier GitHub eventual chain acceptance QA — `43279473586`;
- Validate buffered Steam review dossier runtime — `43279473524`;
- Validate Progressive PASS 2 core — `43279473449`;
- Validate site task registry and page — `43279473818`;
- Validate backlog dispositions — `43279473434`.

The V2 CI executes existing legacy/adversarial and fresh6 immutable source tests, then **real reusable synthetic route** tests (two independent future-cohort fixtures including 1/2-item selected group, immutable owner grant/manifest/marker/authorization, authentic owner run mock and wrong event/actor/attempt/trial, wrong branch/production path, malformed Assembly terminal, strict-ready + typed-insufficient sibling + four missing, no duplicate receipt, bare Git remote issuer one-use). Additional stale main, wrong descriptor blob, original18 overlap and maximum-cardinality adversarial cases were added in code head `e6f58f24`; their exact-HEAD CI must be checked **before** merge and independent QA, regardless of earlier successful runs.

This was **offline, synthetic Git fixture testing in GitHub CI**, not actual live semantic Research/Assembly, not GitHub owner Actions dispatch and not evidence QA. An independent physical-chat L3 reviewer must verify actual final PR HEAD and CI status; the author of the implementation cannot self-approve.

## Owner GitHub Actions procedure, then immediate pilot — no new RECON

Only **after code is accepted in main and independent L3 PASS**:

1. Authenticated repository owner opens **GitHub Actions → Issue reusable Dossier Notes V2 immutable batch sandbox**, selects main; supplies `trial_id=dossier-notes-v2-fresh6-20261111-first`, `expected_main_sha=<exact SHA of merged current main>`, `confirmation=FREEZE_DOSSIER_NOTES_V2_BATCH_ONCE:dossier-notes-v2-fresh6-20261111-first`. Verify first successful owner event on main, frozen grant/manifest/marker commit and branch SHA readback. This step does **not** approve semantic execution.
2. Separately authenticated owner opens **GitHub Actions → Authorize one batch Dossier Notes V2 sandbox semantic pilot**, selects main; supplies same `trial_id`, exact latest `expected_main_sha`, exact `marker_commit` from freeze and `confirmation=AUTHORIZE_DOSSIER_NOTES_V2_BATCH_ONCE:dossier-notes-v2-fresh6-20261111-first`. Verify owner actor `315790060`, first run attempt, success event/ref/path, **run-name binding to trial+marker**, exact authorization child and remote SHA readback. A chat, PR CI or user statement alone cannot substitute for this.
3. **Only after real owner authorization:** separate actual one-shot semantic Research using `config/dossier_notes_v2_batch_research_manual_one_shot_prompt.md` on these six exact immutable assignments; then independently run Assembly using `config/dossier_notes_v2_batch_assembly_manual_one_shot_prompt.md` against confirmed original Research Git commits. No new source audit/RECON or selection, no automatic retries/schedules.
4. **Only after separate owner approval of isolated write:** manual `ingest-taste-steam-review-dossier-checkpoint.yml` dispatch on main with `notes_v2_batch_pilot_writer=true`, other manual writer flags false, exact trial/marker and Git-bound per-item commit map. Verify Git sandbox strict receipts, no canonical/Deep effects; then independent evidence quality QA against PR #438 and quality guards.

**Explicit STOP blockers:** PR #440 still unmerged and has no independent physical-chat L3 PASS; `main` has not installed the new owner Actions; no authenticated real GitHub owner freeze run or distinct authorize run exists for fresh6; no live semantic worker/Research or Assembly has been launched, and no sandbox pilot writer has been authorized. The developer chat must not manufacture actor/run IDs, run the owner workflows, bypass token/tool requirements or claim six completed games.

## Actual activity metrics / timestamp semantics

Prepared games: **6**; synthetic second-cohort tests are not real source queue intake.  
New real fresh6 Research: **0**; Assembly: **0**; sandbox strictly accepted six: **0**; canonical/production accepted six: **0**.  
New owner Actions freeze: **0**; authorization: **0**; changes to scheduled tasks: **0**.  
Known calendar date of implementation/review: **2026-11-12**. Do not infer Research, Assembly or owner run timestamps, durations, acceptance percentages or user grant from source PR timestamps. Next operator records real start/end UTC and immutable GitHub run IDs only on actual dispatch.

**Director handoff:** run independent physical-chat L3 on *one* source PR #440 against latest main and its exact HEAD. If PASS and accepted, perform the already-approved real fresh6 sequence after separately authenticated owner GitHub Actions. No repeated readiness research.

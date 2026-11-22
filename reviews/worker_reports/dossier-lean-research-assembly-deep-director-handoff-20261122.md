# Director handoff — Lean Dossier Research → Assembly → Deep compatibility

**Report date:** 2026-11-22  
**Repository:** `kentrap2011-hub/steam-kz-deals-2`  
**Canonical source of truth:** `main`  
**Source PR:** [#471](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/471)  
**Source branch:** `fix/dossier-assembly-no-routine-discovery-20261119`  
**Verified code HEAD before this report:** `a6428a73350345031e1b7c49427196b2c15e83fa`  
**Verified `main` HEAD at handoff:** `c720bf22b8202cf7822f79be930b2214d16aa38d`  
**Final status:** **PARTIALLY IMPLEMENTED / NOT PRODUCTION-READY / NOT MERGED**. PR remains **OPEN, DRAFT, mergeable=clean** at this check. This report is handoff evidence, not independent QA or a merge authorization.

## 1. User intent / governing decision

The user instructed: simplify evidence handling; Assembly should **trust Research by default** and must not repeat broad independent player-review research just to fill formal schema fields. Reverification requires a *specific actual material contradiction*, wrong game/edition, or consequential unsupported temporal assertion. Do not mistake GitHub structural failures for evidence that collecting detailed per-review records improves final personalized recommendation quality.

Retain actual semantic quality: game mechanics, strengths, weaknesses, dissent/tradeoffs, uncertainty, exact AppID/title/edition, links for material claims, and cautious dates for patch-sensitive technical issues. No invented review counts, fake per-review identities, or artificial twelve-dimension “completeness.” Profile-specific Deep analysis should still weigh both favorable and unfavorable candidate evidence.

## 2. What has been implemented in source PR #471

- New `config/dossier_notes_v2_lean_final.schema.json`: `DOSSIER-NOTES-V2-LEAN-FINAL-V1` with exact product, observations (with sentiment), conflicts, small sources list, unknowns, limited/moderate confidence and timestamps. No mandatory `provenance.player_feedback_records`, per-feedback identifiers/mention counts, or 12-dimension coverage matrix.
- `scripts/dossier_notes_v2_lean_final.py`: standalone validator for identity, balance, source URL safety, source indices, date plausibility, bounded temporal claims, privacy and expiry. Sources used for `current`/`historical` must carry compatible explicitly supplied date and item-level player-feedback URL where required. **This does not independently verify that a public source actually supports the semantic claim.**
- `config/dossier_research_notes_v2_contract.json` + Assembly prompts: `independent_source_discovery=false`; Research findings as default; targeted checks only for named observed contradictions. Lean option is deliberately restricted to **separately owner-authorized inactive Notes V2 sandbox trials**, never automatically production.
- `scripts/dossier_research_notes_v2.py`: Assembly accepts lean candidate with exact binding and dedicated validation; existing legacy strict V2 path preserved.
- `scripts/taste_steam_review_dossier_buffered.py`: lean validation/storage possible only when **`trial_sandbox=true`**. Canonical / non-sandbox path still uses original strict validator and compact provenance checks.
- `scripts/dossier_notes_v2_deep_compat.py`: versioned `DOSSIER-NOTES-V2-LEAN-DEEP-PREVIEW-V1` binding; **read-only sandbox-only** Deep eligibility and ephemeral preview work item.
- `scripts/progressive_pass2.py`: explicit `lean_sandbox_preview=True` check path. Ordinary Deep **intentionally rejects** lean with `lean_dossier_is_not_canonical_deep_evidence`. Deep score finding and balanced negative assessment normalizers work with lean `observations`/`conflicts` in preview tests.
- Tests added/updated for the lean schema, identity/temporal/privacy, Research→Assembly handoff, Deep fit/negative handlers, normal-Deep denial and non-sandbox writer denial; relevant PR CI wired.
- `PROJECT_DECISIONS.md` includes `DOSSIER-LEAN-001` rationale.
- Flaky unrelated `test_dossier_two_stage_staging.py::test_03_invalid_json_produces_safe_typed_rejection` fixed: no longer matches an accidental `bad` substring inside a random SHA digest.

**Scope:** 17 files changed in PR #471 at inspected HEAD. No `main` merge, live Deep run, owner sandbox launch, deployed production source, backlog processing, scheduled task edit, or old create-only trial retry.

## 3. Verified tests

**GitHub Actions checked at exact code HEAD `a6428a73350345031e1b7c49427196b2c15e83fa`: 11/11 workflow runs `completed/success`.** Includes:
- `Validate inactive Research Notes V2 and autonomous Assembly`
- `Validate Progressive PASS 2 core`
- `Validate buffered Steam review dossier runtime`
- `Validate inactive Dossier final GitHub acceptance integration`
- `Validate Dossier async postmerge joint integration (offline)`
- `Validate inactive Dossier two-stage interfaces`
- `Validate inactive Dossier GitHub eventual chain acceptance QA`
- `Validate Deep Stage 1 migration preparation`
- Three other affected repository checks (backlog dispositions, commercial lexical boundaries, site task registry).

New report commit will change PR HEAD: **recheck CI on the final code/merge HEAD**, and distinguish report-only change from code delta. This 11/11 claim applies to the **pre-report code SHA**, not necessarily a future head.

All green checks are **synthetic/offline code safety**, not evidence of live compatibility or of better recommendation quality.

## 4. Blockers — not yet done

1. **Canonical Dossier writer/store:** `scripts/taste_steam_review_dossier_strict.py`, canonical worker schema, and production writer require strict `TASTE-STEAM-REVIEW-DOSSIER-V2` and legacy `provenance` fields. Lean Dossier is not canonically accepted.
2. **Canonical semantic input:** `scripts/taste_steam_review_dossier_web.py::build_semantic_input_strict` calls `dossier_state_strict`, which rejects lean. Existing canonical cache/manifest compatibility and freshness bindings are legacy-specific.
3. **Deep normal eligibility/issuer:** `scripts/progressive_pass2.py::dossier_is_eligible` deliberately rejects lean in normal mode. Existing `game_identity.resolution_status`, `corroborators`, `identity_source_ids`, `provenance.sources` and `web_evidence_contract_binding` gates cannot simply be bypassed or faked.
4. **Positive end-to-end proof:** No confirmed owner-authorized `Research → lean Assembly → sandbox writer → version-aware Deep projection/eligibility → score/negative assessment ingest` chain. Current preview test uses an ephemeral stand-in Dossier record and exercises normalizers, **not a real accepted Deep run**.
5. **Semantic quality limitations:** Compact source date and URL remain self-reported; schema checks can detect inconsistencies but cannot authenticate actual review content or guarantee useful game coverage. A small representative same-game comparison is needed, not broad re-research by Assembly.
6. **Integration/authorization:** Dual-format canonical adoption would change production acceptance/Deep bindings and historical compatibility. Needs a separately versioned canonical contract, user approval for actual production activation, risk-appropriate independent L3 QA and rollback plan. Main has advanced from PR's base; check actual merge delta and any collisions before merge.

## 5. Recommended single next director action

**REGISTER one bounded worker IMPLEMENT task for a _versioned canonical lean dual-reader + Deep integration, OFF by default_.** First pin exact `main`/PR HEAD and reconcile the current contracts. Have the worker:
- Define a distinct versioned canonical lean evidence binding (never borrow the strict V2 binding) and explicit GitHub-owned authorization/activation gate; old strict V2 bytes and accepted Deep results stay untouched.
- Add explicit dual-format validation in the canonical writer, cache freshness reader, semantic-input builder and Deep eligibility/work projection. Reuse lean `observations`/`conflicts` as Deep score/risk semantic interface; preserve product/edition identity, SHA/content binding, release-year compatibility, expiry, privacy and source temporal uncertainty. No synthetic per-review objects.
- Add tests for correct lean/legacy routing; legacy accepted Dossiers/Deep remaining stable; wrong edition, wrong AppID, bad SHA, expired/stale technical claim, spoofed evidence binding, missing meaningful pros/cons; strict no-activation behavior.
- Demonstrate a bounded isolated positive end-to-end test (including actual writer boundary, Deep projection/normalization); compare a few fixed games for real semantic adequacy. Do not auto-run production/backlog or reauthorize old immutable trial paths.
- Produce one worker report with exact code HEAD/CI, remaining deployment boundaries and independent L3 QA request. Keep draft PR open until gates are proven.

**Director decision required:** do not label #471 complete, do not merge solely because CI passed. Current user explicitly requested to continue the work in another chat, which is permission for a handoff/report, not automatic authority to run production semantics/deploy.

## 6. Continuation / sources

- [Source PR #471](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/471) — source code, full diff, CI.
- [Compatibility QA comment](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/471#issuecomment-7009303647) — initial diagnosed canonical/Deep blockers.
- [Compatibility implementation comment](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/471#issuecomment-7014524185) — sandbox preview, temporal guard, and prior flaky CI explanation.
- [Live current `main` contract](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/execution_ownership_contract.json) — GitHub owns scope, validation, binding, persistence and Deep projection; chat edits are development only.
- Read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `DIRECTOR_PROTOCOL.md`, `PROJECT_ROUTES.md` and relevant current Board/registry **before** registering another worker. Do not blindly use historical `CURRENT_TASK.md` as live task truth.

### Ready-to-forward director message

> Проверь отчёт `reviews/worker_reports/dossier-lean-research-assembly-deep-director-handoff-20261122.md` в PR #471 репозитория `kentrap2011-hub/steam-kz-deals-2`. На 22 ноября реализация lean Research→Assembly и тестовый Deep preview готовы; 11/11 CI на кодовом HEAD были зелёными. Но канонический writer, semantic-input и обычный Deep lean не принимают; PR draft и не merged. Выбери и зарегистрируй одно bounded IMPLEMENT-поручение для versioned dual-format integration с independent L3 QA, без автоматической активации production. Проверь актуальные HEAD/main/Board/registry и не начинай Research/Assembly заново.

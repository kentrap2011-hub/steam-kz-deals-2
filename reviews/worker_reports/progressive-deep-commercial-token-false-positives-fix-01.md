# Worker report — Progressive Deep commercial lexical false positives 01

- Task: `WORKER_TASK_PROGRESSIVE_DEEP_COMMERCIAL_TOKEN_FALSE_POSITIVES_FIX_01.md`
- Original worker: ЧАТ 8; targeted repair worker: **ЧАТ 2**, authorized by `WORKER_TASK_PROGRESSIVE_DEEP_PR323_COMMERCIAL_GUARD_TARGETED_REPAIR_01.md`; bounded IMPLEMENT in same PR, **no self-merge**
- Branch: `fix/progressive-deep-commercial-token-false-positives-01`
- Base/source of truth: `main`
- Status: **READY_FOR_NARROW_INDEPENDENT_DELTA_QA**; Director acceptance and merge still pending.
- Initial independent QA reviewed `7c60297d2936ee28c234dc5029efa2fe9e21f101`; tested final source/test HEAD **`d3fd16415434f05e9f91cd235db7b1051e71fad0`**. This report update is documentation-only after that source/test HEAD.

## ЧАТ 2 — targeted correction of PR #323 (2026-10-28)

**Source/test HEAD:** `d3fd16415434f05e9f91cd235db7b1051e71fad0`; preceding implementation code commit `8d0a0c53a0c9e777fe6a4fe423b5b1550ecdbd82`. Same original PR #323 and branch; no third workflow, new PR or production execution.

- **Currency adjacent after code:** `USD100`, `RUB100`, `EUR100`, `KZT100` now match, as do earlier `100RUB`/`100руб`. End-of-numeric-token constraint avoids interpreting `USD100foo` as a standalone currency amount. Existing valid-word boundaries (`грубую`, `труба`, `рубеж`, `сцена`, `scrub`, `Salem`) remain safe.
- **Mixed scripts:** limited visual confusable maps are applied only to complete *individual tokens that contain both Latin and Cyrillic letters*, and a folded token must fully match the pre-existing commercial regex inventory. Examples `цeна`, `cкидка`, `prіce`, `diѕcount`, `ѕale`, `Рrice` reject. Anti-overblocking inputs `Сцeна`, `Sаlem`, `Diѕcountenance`, `Prіceless`, `Груbую` remain accepted. No global transliteration, broad semantic substitutions or new synonyms.
- **Explicit lexical boundaries:** support `рубл.` as an unambiguous conventional abbreviation (with/without adjacent numeric amount). A bare currency glyph such as `₽` remains **accepted**, while glyph+amount is **rejected**. Spaced letter codes such as `R U B 500` remain accepted: arbitrary whitespace spelling is outside this candidate-token policy. Standalone contextual English homonyms (`The rub feels abrasive`, `Sale is a character surname`) remain conservatively **rejected** as ambiguous commercial tokens; semantic disambiguation would require a different owned contract. All four choices are pinned by executable Fast/Deep/inventory tests, not just documentation.
- **Canonical paths exercised:** Fast `positive_evidence` and `not_fit_evidence`, Deep evidence and `score_findings[].text_ru`, plus real `process_result_documents` synthetic receipt acceptance/rejection in isolated in-memory state. No historical receipt, queue or production write.
- **Scope hygiene:** removed `workflow_dispatch` from *existing new* read-only PR validator; removed PR-only ЧАТ 8 entry from `CURRENT_TASK.md` without modifying other task entries, leaving `CURRENT_TASK.md` absent from PR changed-file list. Original AppID **1261040** rejected/consumed/recovery-owned event stays canonical, no rerun, retry, migration, Dossier, ranking, marker, scheduled-task or production action.

**Exact-code-HEAD GitHub Actions evidence:**

- [Focused Progressive lexical Fast/Deep/ingest CI **40673325919**](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40673325919): **SUCCESS**, `d3fd1641`, includes `test_progressive_commercial_language.py`, `test_progressive_pass1.py`, `test_progressive_pass2.py` and compilation.
- [Existing PASS 2 core CI **40673325866**](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40673325866): **SUCCESS**, `d3fd1641`, existing broad Deep and negative/score/history regressions.
- Site registry CI `40673326009` and backlog dispositions CI `40673325953`: **SUCCESS** at `d3fd1641`.
- [Deep Stage 1 migration preparation CI **40673325796**](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40673325796): **FAILURE** at separate `test_deep_stage1_migration_pr_preview.py:61`, assertion `len(fresh["items"]) == scope["normal_pass2_eligible_count"] > 0`. Its scripts and state/migration logic are untouched by PR #323; an equivalent failure also occurred on source commit `8d0a0c53`. **Do not characterize the entire PR check suite as green**; independent owner/Director must handle this check without broadening commercial lexical repair.

Next: independent narrow material-delta QA against exact latest PR HEAD, then Director disposition. **Not merged/deployed.** Reporter note: local GitHub checkout DNS failed, so real Python regression execution was attested by GitHub Actions, not claimed as a local run.

## Confirmed incident and root cause

`data/cache/progressive_pass2_ingest_receipts/4a461de403abec199df0def7d3b659ca20cdbb3af71f577b44021b1d7af169f8.json` records AppID **1261040** (Streamer Life Simulator), `rejected_semantic_contract_result_attempt_consumed`, reason `not_fit_evidence[2] contains forbidden commercial evidence fragment: 'руб'`; `attempt_consumed=true`, `recovery_owned=true`.

Active Deep `scripts/progressive_pass2.py::normalize_result` calls `scripts/progressive_pass1.py::_validate_text_list` for both `positive_evidence` and `not_fit_evidence`. That shared function performed `fragment in text.casefold()` against a commercial-fragment list. Thus ordinary `грубую` contains the sequence `руб` without any currency meaning. The same check also affected Fast/PASS 1.

A second adjacent family check in `scripts/progressive_pass2.py::normalize_score_findings` independently used `term in lowered` to reject commercial/ranking-only text from `score_findings[].text_ru`. It could reject e.g. `сцена` for `цена`, `Salem` for `sale`, and other embedded words. This check is Deep-only; it was not the exact AppID 1261040 receipt path.

## Inspected inventory and analogous findings

- Shared Fast/Deep evidence: English `price`, `discount`, `wishlist`, `steamdb`, `sale price`, `historical price`, `rub`, `kzt`; Russian `цена`, `скидк`, `вишлист`, `руб`, `тенге`. The previously independent Deep score list adds `sale`, `распродаж`, score/ranking phrases.
- Verified structural false-positive classes: `руб` within `грубую`, `труба`, `рубеж`; `цена` within `сцена`; `rub` within `scrub` / `Rubicon`; `sale` within `Salem`; `discount` within `discountenance`. These all matched the prior substring strategy despite noncommercial usage.
- Currency words/codes, Russian grammatical inflections, Latin casefold, wide Unicode (NFKC), optional Cyrillic stress accents, Unicode whitespace, punctuation, numeric-adjacent currency code/name and symbol+amount were inspected and covered in focused tests.
- Related readers: only the canonical `progressive_pass1._validate_text_list` is shared by Fast and Deep evidence. The Deep `normalize_score_findings` path is separately checked. No Dossier, ranking, purchase scoring or unrelated search/filters are changed.

## Bounded implementation

- Added `scripts/progressive_commercial_language.py`: shared word-boundary checks for commercial terms, grammatical currency variants, supported major currency names/codes, amount+currency glyphs; and an additional bounded Deep ranking-phrase matcher. No whole-word substring-in-interior matches. Preserve original rejection taxonomy/text through unchanged callers.
- Changed `scripts/progressive_pass1.py` to call the shared lexical guard on `positive_evidence`/`not_fit_evidence`.
- Changed `scripts/progressive_pass2.py` to call the guard on scored finding text. The other Deep evidence paths continue calling the shared Fast validator.
- Added `scripts/test_progressive_commercial_language.py`: harmless-word positives, commercial-language negatives, mixed-script/Unicode typography, currency and store/discount terms, Fast full result normalization, Deep full result normalization, Deep score findings and real `process_result_documents` receipt status with isolated in-memory fixtures.
- Added read-only PR validation workflow `.github/workflows/validate-progressive-commercial-language.yml` running compilation, new focused tests and existing Fast/Deep contract regressions. No deployment, ingest job or scheduler action is added.

## Validation and remaining risk

Focused commands: `python scripts/test_progressive_commercial_language.py`, `python scripts/test_progressive_pass1.py`, `python scripts/test_progressive_pass2.py`; all three are part of PR-only CI. Confirm **exact PR head CI** before Director acceptance; a successful file write is not a validation result.

Regex intentionally remains lexical, not semantic: a standalone English `rub` can mean an ordinary verb; such ambiguous isolated words cannot be reliably disambiguated without new semantic interpretation. Rare commercial expressions outside the listed token family (e.g. a standalone synonym without price/currency token) may not be caught. The fix removes confirmed *word-interior* false positives without disabling genuine standalone commercial evidence rejection.

## Explicit exclusions and handoff

No changes to historical receipts, consumed attempts, recovery authorization, work manifests, queue, state, retry/completeness, Deep semantic execution, Dossier, Fast/Deep scoring, production payload, deployment or Scheduled Tasks. AppID 1261040 remains **recovery-owned**; only the separate GitHub-authorized recovery path can resubmit it, and this worker does **not** run that path.

Director to review diff, exact-head PR CI, and the narrow token tradeoffs; no self-merge by worker.

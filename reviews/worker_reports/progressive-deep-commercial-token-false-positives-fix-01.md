# Worker report — Progressive Deep commercial lexical false positives 01

- Task: `WORKER_TASK_PROGRESSIVE_DEEP_COMMERCIAL_TOKEN_FALSE_POSITIVES_FIX_01.md`
- Worker: ЧАТ 8; mode: bounded IMPLEMENT, one PR, **no self-merge**
- Branch: `fix/progressive-deep-commercial-token-false-positives-01`
- Base/source of truth: `main`
- Status: **READY_FOR_DIRECTOR_REVIEW** (subject to exact-head PR CI result)

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

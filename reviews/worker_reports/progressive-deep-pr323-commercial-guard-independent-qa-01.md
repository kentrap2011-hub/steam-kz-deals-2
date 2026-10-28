# Independent L3 QA — Progressive commercial lexical guard, PR #323

- Task: `WORKER_TASK_PROGRESSIVE_DEEP_PR323_COMMERCIAL_GUARD_INDEPENDENT_QA_01.md`
- Worker: independent **ЧАТ 3**, separate from implementation ЧАТ 8.
- Verdict: **CHANGES_REQUIRED**.
- Target: [PR #323](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/323), exact reviewed HEAD `7c60297d2936ee28c234dc5029efa2fe9e21f101` (checked twice; unchanged during QA); base `main`.
- Report-only QA: no source code, source PR, production, queue, state, historical receipts, Scheduled Tasks or manual semantic/recovery execution modified.

## Checked evidence and boundaries

1. Read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, task, Progressive route, relevant Fast/Deep and execution-ownership contracts; reviewed all seven PR changed paths, source patch, implementation report and exact live historical rejection receipt.
2. Canonical receipt `data/cache/progressive_pass2_ingest_receipts/4a461de403abec199df0def7d3b659ca20cdbb3af71f577b44021b1d7af169f8.json` proves Streamer Life Simulator AppID **1261040**: `not_fit_evidence[2] contains forbidden commercial evidence fragment: 'руб'`; `rejected_semantic_contract_result_attempt_consumed`; `attempt_consumed=true`; `recovery_owned=true`; `authoritative_completed=false`. This is not an authorization to retry. No PR #323 diff changes canonical history or this receipt.
3. Old Fast `progressive_pass1._validate_text_list` used `fragment in text.casefold()`. Deep `normalize_result` routes evidence through that Fast validator; old Deep `normalize_score_findings` also used raw substring search. New Fast evidence is routed to `commercial_evidence_hit`, Deep evidence still routes through Fast, and score findings now route to `score_explanation_hit` in `scripts/progressive_commercial_language.py`. The original error taxonomy and score-only rejection error message remain intact.
4. Verified word-boundary / Unicode mechanics: `NFKC().casefold()`, drop combining U+0300/U+0301, `(?<!\\w)...(?!\\w)` for terms; `(?<!\\w)|(?<=\\d)` prefix for currency codes/names; `currency_symbol` requires currency glyph adjacent to a number. These are lexical heuristics, not full semantic language analysis.

## Independent result matrix

The independent Python lexical reproducer copied the inspected pattern definitions from the immutable PR HEAD into a disposable local process. A checkout of the repository could **not** be obtained in the isolated runtime (GitHub hostname DNS resolution failed). Thus independent execution of the entire canonical ingest was **not** claimed; separately, exact-head GitHub Actions executed real Fast/Deep ingest regressions successfully.

| Input / mechanism | Actual new lexical result | QA |
| --- | --- | --- |
| `грубую`, `сцена`, `труба`, `рубеж`, `scrub`, `Salem` | no commercial hit | **PASS** — original word-interior false positives removed |
| `Цена 499 руб.`, `Стоит 100 рублей`, `100руб`, `100RUB`, `USD 100`, `₽100`, `100 €`, `скидки`, `price`, `SteamDB` | commercial hit | **PASS** — representative actual terms protected |
| `USD100`, `EUR100`, `RUB100`, `KZT100` | **no hit** | **FAIL** — currency-before-amount without space bypass |
| `цeна 100` (Latin `e`), `cкидка 20%` (Latin `c`), `prіce 100` (Cyrillic `і`), `diѕcount 20%` (Cyrillic `ѕ`) | **no hit** | **FAIL** — commonplace mixed-script confusables bypass NFKC |
| `рубл. 500`, `Стоит ₽` (bare currency symbol), `R U B 500` | no hit | **RESIDUAL** — abbreviation, bare symbol and spaced letters are uncovered; assess explicit scope before expanding |
| `The rub feels abrasive`, `Sale is a character's surname` | commercial hit | **RESIDUAL FALSE POSITIVE** — legitimate standalone homonyms require semantic context |

**Defect mechanism A:** `_currency` deliberately permits digits *before* the token (`(?<=\\d)`), but `(?!\\w)` rejects digits *after* the token. So the common `USD100` form escapes, while `100USD` is detected.

**Defect mechanism B:** NFKC/casefold normalize width/case, **not Latin/Cyrillic confusable letters**; the word-boundary guard will not detect a visually equivalent commercial term with a single different-script glyph. This directly fails the task's mixed-script requirement; distinguish this from arbitrary newly invented synonyms.

The remaining standalone `rub` / `Sale` false positives are lexical ambiguity, not evidence that word-boundary repair failed. They should be documented and weighed against taste-purity risk; do not make the entire word family permissive just to silence them. Fixed consumer-facing source-labels are not changed: existing `цена`, `скидк`, `руб`, `price` etc. return stable token labels when matched. Newly introduced labels (`usd`, `eur`, `currency_symbol`) do not affect the existing error field taxonomy.

## Exact-head CI and ingestion scope

- [New targeted lexical CI run 40642265309](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40642265309): **SUCCESS** at reviewed HEAD; compiled modules, ran `test_progressive_commercial_language.py`, `test_progressive_pass1.py`, `test_progressive_pass2.py`; inspected job 122662873819, including `Progressive commercial lexical boundaries / Fast / Deep ingest: OK`.
- [Existing PASS 2 core CI run 40642265375](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40642265375): **SUCCESS**; inspected job 122662874069, Fast/Deep/negative-score/invalid-not-fit/versioned-history/authority/queue regressions completed. Other exact-head Actions runs 40642265316, 40642265304, 40642265297 also succeeded.
- Implementation test covers full synthetic `normalize_submission` Fast fit/not-fit, `normalize_result` Deep, score finding, and `process_result_documents` accepted vs consumed rejection status. Its inventory omits the two reproduced bypass families above. **Green CI therefore does not override the concrete lexical findings.**
- Changed-file list contains only `scripts/progressive_commercial_language.py`, Fast/Deep entrypoints, focused regression, read-only workflow, implementation worker report and `CURRENT_TASK.md`. It does **not** modify frozen queue, recovery authorizer, run-start marker, scoring, ingest writer, production state, historical receipts or workflow scheduler settings. No claim is made about visibility of external Scheduled Task settings, which are outside this diff.
- The existing recovery contract makes a consumed invalid semantic attempt GitHub-recovery-owned. **Do not** re-run Deep or repair AppID 1261040 from this QA or PR #323.

## Scope/handoff assessment

- `.github/workflows/validate-progressive-commercial-language.yml` is read-only with `contents: read`, `pull_request` and existing Python tests; no production or recurring scheduler behavior. However `workflow_dispatch` creates a **new manual trigger** that the targeted regression does not require. Remove `workflow_dispatch` unless explicitly justified; keep automatic PR CI, or use existing PASS 2 CI with a focused-test step if avoiding another workflow is preferred. Do not add another validator.
- The new `CURRENT_TASK.md` handoff entry is not needed to execute the lexical fix, and its broad shared-file footprint risks stale/multi-worker merge conflicts. Prefer the immutable worker report + PR description as handoff; remove the unrelated shared-handoff diff from source PR #323, or confirm Director explicitly wants that transient entry. Preserve all other concurrently active tasks in `main`.
- PR #323 remains draft; no deployment/production validation or recovery test is claimed by green CI.

## Required minimal corrections before Director acceptance

1. Add a bounded currency-prefix amount case (`USD100`, `RUB100`, `EUR100`, `KZT100`) **without** reintroducing word-interior matches (`scrub`, `рубеж`). Include Fast evidence, Deep evidence, Deep scored findings and actual synthetic ingest receipt checks.
2. Add narrowly scoped mixed-script/confusable detection for commercial *candidate tokens*, with strict safe-word counterexamples to avoid overblocking ordinary prose; include both Latin-with-Cyrillic and Cyrillic-with-Latin substitutions and NFKC/Unicode punctuation cases. Do not use unbounded global text transliteration or weaken the genuine-token guard.
3. Decide explicitly whether `рубл.` abbreviation, currency glyph alone and common commercial derivatives warrant coverage; document any intentionally unsupported ambiguous forms.
4. Keep read-only automatic CI; remove unnecessary manual `workflow_dispatch`. Prefer removing the shared `CURRENT_TASK.md` change from the implementation PR unless specifically Director-authorized.
5. After changes, independent QA of the **new exact PR head** plus existing Fast/Deep and negative-score regressions. No historic replay, manual Deep run or recovery.

**Final QA status: CHANGES_REQUIRED**, not `BLOCKED_EVIDENCE` and not `PASS`. Source PR #323 was not edited by this worker. Director owns disposition and any future authorization.

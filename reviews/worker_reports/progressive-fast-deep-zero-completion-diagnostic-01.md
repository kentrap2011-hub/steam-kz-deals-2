# Progressive Fast + Deep zero-completion diagnostic 01

## 1. Task

READ-ONLY / RECON for `WORKER_TASK_PROGRESSIVE_FAST_DEEP_ZERO_COMPLETION_DIAGNOSTIC_01.md`.

Question answered: why current Fast and Deep have zero completed fit/not-fit results; whether this is semantic/evidence failure, identity drift, runtime failure, or Statistics projection error.

No production worker, Scheduled Task, recovery, replay, source/config/prompt/workflow/state/work/result mutation was executed. The only authorized write is this report.

## 2. Architecture preflight

- GitHub remains the control-plane owner of Fast/Deep scope, exact identity, attempt accounting, persistence, recovery authorization, Dossier acceptance and Statistics projection.
- Scheduled ChatGPT workers are bounded semantic data-plane only.
- Canonical route inspected: `Fast -> Dossier -> Deep`.
- Fast authority: `config/progressive_pass1_contract.json`, `config/progressive_pass1_worker_prompt.md`, `scripts/progressive_pass1.py`, `scripts/build_progressive_pass1_work.py`.
- Dossier authority: `config/taste_steam_review_dossier_contract.json`, current worker index and accepted Dossier artifacts.
- Deep authority: `config/progressive_pass2_contract.json`, `config/progressive_pass2_worker_prompt.md`, `scripts/progressive_pass2.py`, `scripts/build_progressive_pass2_work.py`.
- Statistics producer: `scripts/progressive_personalization.py::build_processing_status`; browser consumer: `web/progressive-personalization-ui.js::statisticsSections`.
- No other repository was inspected.

## 3. Fresh current counts

Fresh `main` snapshot immediately before report creation:

| Stage | Current canonical count |
|---|---:|
| Fast total current scope | 511 |
| Fast attempted / processed | 91 |
| Fast completed fit | 0 |
| Fast completed not-fit | 0 |
| Fast incomplete | 87 |
| Fast error | 4 |
| Fast skipped due to authoritative Deep | 0 |
| Fast remaining | 420 |
| Dossier total current scope | 511 |
| Dossier accepted | 12 |
| Dossier pending | 499 |
| Dossier failed/recovery | 0 |
| Deep total current coverage target | 511 |
| Deep first-pass attempted | 2 |
| Deep authoritative completed | 0 |
| Deep completed fit | 0 |
| Deep completed not-fit | 0 |
| Deep incomplete/recovery | 2 |
| Deep waiting for Dossier | 499 |
| Deep ready/pending | 10 |
| Deep normal first-pass remaining | 509 |
| Deep remaining until all authoritative | 511 |

Arithmetic is internally consistent:

- Fast: `91 = 0 + 0 + 87 + 4`; `511 = 91 + 0 + 420`.
- Dossier: `511 = 12 + 499 + 0`.
- Deep: 12 accepted Dossiers split into 2 current attempted + 10 ready/pending; the other 499 wait for Dossier. With zero authoritative completions, all 511 remain until final authoritative coverage.

The trigger snapshot in the task was older (`86 attempted / 82 incomplete / 4 error`). The increase to `91 / 87 / 4` proves Fast continues to execute while useful completion remains zero.

## 4. Fast findings

### 4.1 Current exact outcome distribution

`data/cache/progressive_pass1_state.json` contains 159 physical entries, but exact current binding against the 511 current candidate-context rows yields only 91 current entries:

- `analyzed_fit = 0`
- `analyzed_not_fit = 0`
- `analysis_incomplete / insufficient_evidence = 87`
- `analysis_incomplete / worker_failure = 3`
- `analysis_incomplete / invalid_semantic_result = 1`

`scripts/build_progressive_pass1_work.py` intentionally projects `worker_failure` and `invalid_semantic_result` into the Fast error bucket; all other valid `analysis_incomplete` outcomes are Fast incomplete.

### 4.2 Representative current incomplete samples

All three examples below have exact current identity, valid result transport, accepted ingest receipt/state, and remain current `analysis_incomplete / insufficient_evidence`:

1. `App_1220140` / Cartel Tycoon — work `c79ff57ee983bd48248825c09434803bc07ad541f1debd764391bde6ac2ac0be`. Current semantic input: survival business sim description, no `fit_tags`, `core_fit_count=0`. Worker result commit `b6462b968affd42baf19bb3a5c19a246c120a569`; canonical ingest commit `e357ba478f6f57561c87a3d3e1a34942d720406e`.
2. `App_1135690` / Unpacking — work `062be5c04af8ceaa9b66c32fb3a5e0e68a6750341220557a54c949a62ea82c87`. Current input has `Story Rich` and a description about puzzle/home decoration/story clues. Result commit `0c688a6bf9c321e9388b27c9fc1898925cbce8fd`; ingest `73230a70331235d4f59b9a4fdcd0dc35e2fccb39`.
3. `App_445980` / Wizard of Legend — work `2dc646e726dddcbd5ae2644a1f0e7b574a01c61c74f922ffa69fa8f0f5dcd7e8`. Current input describes precise movement, spell comboing and roguelike action; result commit `fabbf7b02645d9782d69cce52a9c8b4d7b58d71b`; ingest `be4bb81afb3f671b924aa1de789dca71c7837d6a`.

The PASS 1 incomplete result schema persists only the issue code; it does not persist searched sources or evidence-rejection reasoning. Therefore the durable repository proves that the worker judged evidence insufficient, but cannot reconstruct which individual pages were considered for these three items.

### 4.3 Dominant Fast root cause: canonical personalized semantic input is not actually handed to the worker

This is a systemic handoff defect, not merely “Fast is intentionally lightweight”.

The Fast contract binds the semantic generation to `profile_blob_sha`, `taste_model_version` and `taste_semantics_sha256`, but current work items expose only an opaque binding plus candidate fields such as title, description, `fit_tags`, `core_fit_count`, release data and semantic-condition metadata. The current Fast worker prompt explicitly tells the worker to read the PASS 1 contract + current PASS 1 work and use the exact candidate-specific semantic input plus light public evidence. It does **not** instruct the worker to read a canonical taste-profile payload.

`data/production/pre_ai/taste_projection.json` proves the actual current profile content lives behind a separate profile reference while the current work carries hashes/bindings, not that content. A hash proves identity; it does not communicate preferences or the five personalized factor semantics required for a trustworthy `analyzed_fit`.

This mismatch is especially material because a completed fit requires all five personalized `taste_factors`, and a completed not-fit requires a trustworthy personalized below-threshold or confirmed-negative basis. The worker cannot reproducibly derive those personalized judgments from the current canonical work payload alone without relying on non-canonical remembered context.

The Fast prompt has not changed since commit `13496145bd39f6472c6208abde7bcb28baa8da97`, so the zero-completion pattern is not explained by a later Fast prompt regression.

## 5. Fast error breakdown

Current exact error projection is 4 = 3 `worker_failure` + 1 `invalid_semantic_result`.

### worker_failure — 3

- `App_233130` / Shadow Warrior — work `3cbe9a92e418a9c6c036310c19421bf7d82d9ef704ee9abaf40a041814b4c7ae`; result commit `74a28b7f66a0259924b7a88b6897d79601aa4d1b`; accepted ingest `ab3a2570c3cd05d509aaab0cc4b5bbc8578f202c`.
- `App_629820` / Maneater — work `74eb145b7ed4e773dafe34ef411ecad146bffbd3725babb4b1322fe087c392a7`; result `867990e08500038eff098b138b465c11c0db47f6`; ingest `1fac7b635627d748043860bfb57e9ff7bd8e4c0a`.
- `App_1571440` / Lunch Lady — work `935b22d46668fa48917730972f4056d24db2a60f55c5608140f2e7bd5267c5cb`; result `f5b12b6ecd0c094c0a14fb89ce3b84d757561b63`; ingest `414933d6b217e1d54efe9bbf2db4e6a32ba9594d`.

Each artifact is a structurally valid worker-declared `analysis_incomplete / worker_failure`, and each receipt is `status=accepted`. Under the prompt this category is specifically for a caught per-item tool/runtime failure. No more specific exception/tool detail is persisted in the result or receipt, so the immediate sub-cause is not recoverable from durable repository evidence. These are current accounting outcomes of historical per-item runtime/tool events; repository evidence does not prove that one shared runtime defect is still live.

### invalid_semantic_result — 1

`App_335000` / Tormentum - Dark Sorrow — work `68a6a025796a5065ccfd729e58d970608aa3cb1011d9f2189dbd10e9b0d92e8d`.

Exact cause is proven. Prepared/current `candidate_context_sha256` is:

`9c2de31795bda81bc59a191da0a39203366ab0512c3027b2d5eef1681e089042`

but worker result commit `e208953a0bd06629e4d061a016c39b786a86c188` submitted:

`9c2de31795b59a191da0a39203366ab0512c3027b2d5eef1681e089042`

The ingest receipt in commit `41c052232af0072138b6e536bf64a2f5f95af2d0` records `validation_error="submission identity does not exactly match prepared PASS 1 work"` and `status=accepted_as_incomplete_invalid_result`. This is invalid worker output / exact-identity failure, not semantic insufficiency and not a validator mismatch.

The four errors are therefore secondary; they cannot explain the dominant 87/91 valid incomplete outcomes.

## 6. Historical-vs-current Fast reconciliation

Physical Fast state has 68 non-current entries:

- 59 `analysis_incomplete`
- 9 `analyzed_fit`
- 0 `analyzed_not_fit`

All 9 historical fits use the same global semantic-generation ID as current work, so “generation mismatch” is **not** the reason they are excluded. Their `family_id` values are absent from the current 511-row `progressive_candidate_context.jsonl`; exact reason: **no longer a current candidate**.

Two exact examples:

- `App_815370` / Green Hell — historical fit work `9196dc298c77af612add1811a72716345966f73e066f0124cb711ef125ab58f9`; result commit `c225cd5b75dd114fdd7f385e58a000331ea8749a`; moderate/medium with non-empty positive evidence and five factors; ingest `7d0df846eb9254546a23ffe7c360e33be9b91a00`. Family is absent from current candidate scope, therefore not current.
- `App_2492120` / SAEKO: Giantess Dating Sim — historical fit work `68e89a218bcd461a10339951ccf3291d032f2192e3b3c225fa8b3a5a64d1f61c`; result `875a4fc34c06aae750568fd468c1a81385f2e6ef`; moderate/medium with positive evidence/factors; ingest `02fe33ec87fb27222865274dafed370faa17f1ab`. Family is also absent from current candidate scope.

Thus current zero completed Fast is not a Statistics omission of valid current fits. Historical completion exists, but those games are outside current scope.

## 7. Deep findings — every current attempted item

Physical Deep state contains three entries, but only two are current exact-compatible attempts. `App_1102190` is bound to old Dossier evidence revision `validator-generator-parity-fix-2026-09-20` / SHA `be470f...`; current Dossier binding is `semantic-bounded-retrieval-2026-09-23` / SHA `5ad29bc1...`, so that older state entry is correctly excluded from current Deep attempted accounting.

### App_1036890 — Shadow Warrior 3: Definitive Edition

- work: `e7fa6fa96ab0a7ea01528df4ce0e634eed0877d0e0c320efefb8454f8b9bf987`
- authorization: `6c421679773f4d3fd0d533469e5b2e90c153bcf8b7041302e68cdf28ba77e160`
- Dossier: `data/cache/taste_steam_review_dossiers/App_1036890.json`
- Dossier SHA: `4385da1dbbbbd3c6c9dd97c2a6829779dd4436fff441ade9c2b9ce7f0d1c1378`
- evidence binding: `semantic-bounded-retrieval-2026-09-23`, SHA `5ad29bc1e4df614191d380bf832f4865f9ee73bab406e314f8d5687b0daa7ec7`
- Dossier evidence: exactly 1 durable Russian anecdotal mechanics observation; `source_mix_status=single_source_only`; `overall_strength=limited`.
- Deep result: `analysis_incomplete / insufficient_evidence`; result was submitted in commit `f082952fe52aca1de69c516e02e3257dc29fb203`; accepted/reconciled in `053a1260d2306b77a15fe546e06343fb92efe500`.
- Canonical result receipt: accepted, `authoritative_completed=false`, `recovery_owned=true`.

### App_1072150 — Hedon Bloodrite

- work: `9759f2fbc9c65e75657627fb306d45bc2c1ac284d8c24c77d600336379e1dca0`
- authorization: `ea2a82981be1b67cba0cfffef58b5a3fa8a8348eea4f7d22c3be923870077071`
- Dossier: `data/cache/taste_steam_review_dossiers/App_1072150.json`
- Dossier SHA: `95b61cefc396d29ec253e9236b4a198813c1861c72288795eb065b78dae96c5d`
- same current evidence binding `semantic-bounded-retrieval-2026-09-23` / `5ad29bc1...`
- Dossier evidence: exactly 1 durable non-Russian anecdotal structure observation; `source_mix_status=single_source_only`; `overall_strength=limited`; Russian attempt found no usable existence signal.
- Deep result: `analysis_incomplete / insufficient_evidence`; result commit `2086d3e05753587fb4d145aee2f7c7b042c0bcc8`; accepted/reconciled in `7b84a5307aa400a7636a2014384a7b8e4fd409e5`.
- Canonical receipt again records accepted incomplete, not authoritative, recovery-owned.

For incomplete Deep results the schema persists the issue code but not a source-by-source “evidence actually used” explanation. Therefore repository evidence cannot prove whether the worker actively reasoned from the single Dossier observation before declaring insufficiency. It does prove that the exact Dossiers were current/eligible and that the accepted outcome was semantic insufficiency, not binding/freshness failure or runtime failure.

## 8. Dossier -> Deep evidence assessment

The intended route is clear:

- Fast receives candidate-specific metadata and may use lightweight public evidence.
- Dossier independently gathers neutral player-feedback evidence.
- Deep receives the prepared candidate semantic input + exact accepted Dossier and must return a trustworthy personalized fit/not-fit to become authoritative.
- Deep may not invent/rebuild scope and the current prompt says to read only the prepared semantic input and exact Dossier.

The actual handoff has two constraints:

1. **Personal taste semantics are bound but not supplied as semantic data.** Both Fast and Deep can verify hashes but do not receive the canonical personalized preference/factor model needed to reproducibly map candidate evidence into the required five factors / personalized verdict.
2. **Dossier acceptance is not equivalent to Deep-decision sufficiency.** Both current accepted Dossiers declare their Dossier research state “sufficient”, but each has only one anecdotal observation and `overall_strength=limited`. The Dossier contract validates a neutral dossier; it does not certify that enough evidence exists for a Deep personalized verdict. Deep is then prohibited from broadening the prepared evidence route itself.

This creates a real semantic handoff gap: Dossier can be valid and accepted while still not giving Deep enough decision material, and the worker still lacks canonical taste semantics to interpret even the evidence it has.

The first constraint is independently fatal to reproducible personalized completion and affects both Fast and Deep. The second is proven as a contributing Deep evidence weakness, but this recon cannot prove that those same two games would remain incomplete after canonical taste semantics are supplied.

## 9. Root-cause classification

**Primary root cause — systemic semantic-input handoff defect.**

Current GitHub work binds the personalized model by hashes, but the bounded worker contracts do not hand the worker the canonical taste-semantic payload. The required personalized result fields cannot be reproducibly derived from hashes alone. This explains why execution can advance while useful current completion remains zero.

**Contributing Deep cause — accepted-but-limited Dossier evidence.**

Both current Deep Dossiers are exact/current/valid but semantically thin: one anecdotal observation, limited strength, single-source only. Deep reports `insufficient_evidence`, not a runtime or identity failure.

**Secondary Fast causes — four exact error outcomes.**

Three are valid `worker_failure` outcomes with no persisted sub-cause; one is a proven malformed identity field from the worker. These affect 4/91 current attempts and are not the main zero-completion mechanism.

**Identity/projection behavior is working as designed.**

Historical completed Fast and old-binding Deep state are excluded for exact, proven non-current reasons.

Final Statistics/system classification:

`mixed_root_causes` — with **no Statistics projection bug**. The page is accurately exposing real current semantic/evidence failures plus four Fast error outcomes.

## 10. Why Statistics is correct

`scripts/progressive_personalization.py` independently builds current exact state, maps Fast `analyzed_fit/not_fit -> completed`, maps `worker_failure/invalid_semantic_result -> error`, derives Dossier state, derives current exact Deep state, recomputes all counters, and enforces arithmetic invariants before stamping `visual.processing_status`.

`web/progressive-personalization-ui.js` reads those producer-owned fields directly:
- Fast completed rows: `fast_completed_fit_count`, `fast_completed_not_fit_count`;
- Dossier: accepted/pending/recovery;
- Deep final: `deep_authoritative_completed_count`, fit/not-fit, incomplete/recovery, waiting and ready/pending.

No browser-side inference was found that could turn a current completed result into zero. Current state independently reproduces the same zero-completed result.

## 11. Recommended bounded repair task — do not implement here

Primary bounded implementation task should be a **Progressive canonical taste-semantic input handoff fix**, owned by the GitHub control plane.

Required authorization boundary:
- `config/progressive_pass1_contract.json`
- `config/progressive_pass2_contract.json`
- their canonical worker prompts
- the GitHub work builders / semantic-input projection that create exact work identity.

Smallest correct behavior:
- project a compact deterministic canonical taste-decision context into each Fast/Deep work item, or an exact same-repository immutable path+hash that both workers are explicitly required to read;
- make that payload part of semantic identity/work-id generation, rather than exposing only `profile_blob_sha` / `taste_semantics_sha256`;
- preserve existing fit/not-fit business thresholds; this repairs implementation/data handoff, not the intended Taste policy;
- retain exact GitHub-owned validation/persistence/attempt accounting;
- after the handoff changes identity, let GitHub regenerate new exact work identity. Do not manually rewrite existing incomplete state.

Existing consumed attempts cannot simply be rerun under the current one-attempt contracts. Any reprocessing must arise from the new GitHub-owned semantic identity or separately authorized GitHub recovery; this report authorizes neither.

Acceptance for that task should also retest the two current Deep examples. If they remain incomplete with canonical taste semantics present, then create a separate Dossier-to-Deep evidence-readiness alignment task; do not weaken Deep verdict thresholds merely to force nonzero counts.

## 12. DIAG-01..13

- **DIAG-01 PASS** — fresh Fast/Dossier/Deep counts independently reproduced from canonical work/state/index plus producer logic.
- **DIAG-02 PASS** — current Fast exact distribution proven: 87 insufficient + 3 worker_failure + 1 invalid semantic; zero fit/not-fit.
- **DIAG-03 PASS** — 9 historical Fast fits proven non-current because their families are absent from current candidate scope, not because of generation mismatch.
- **DIAG-04 PASS** — all current Fast error classes and all 4 exact items identified; invalid-output cause proven exactly; worker_failure durable evidence bounded to typed runtime/tool outcome.
- **DIAG-05 PASS** — 3 representative current insufficient Fast attempts traced result -> ingest -> current binding.
- **DIAG-06 PASS** — both currently counted Deep attempts traced end-to-end.
- **DIAG-07 PASS** — current Deep zero final is semantic insufficiency with current/valid but limited evidence, not freshness/binding/runtime failure.
- **DIAG-08 PASS** — Fast input, Dossier evidence and Deep completion requirements compared; canonical taste-semantic handoff gap proven.
- **DIAG-09 PASS** — classification: `mixed_root_causes`, Statistics correct, system semantic/evidence handoff defective.
- **DIAG-10 PASS** — workers demonstrably execute: Fast advanced from task snapshot 86 -> 91 attempts; Deep has accepted first-pass results; zero means zero useful completion, not zero execution.
- **DIAG-11 PASS** — no production/scheduler/recovery/source/config/state/work/result mutation performed; only this report is written.
- **DIAG-12 PASS** — repair owner/contract boundary named; GitHub remains control-plane owner.
- **DIAG-13 PASS** — report was committed to `main` as `cae00fb479e6dc4380ffa74cdf9ed8e011cc3861` and reread from fresh `main`; final closeout revision is reread again after this marker is persisted.

## 13. Key exact refs

- semantic generation: `334bee04617cc4a43fe300a26d62a3ef3af4e1469eb313c352e37fb39fc0213d`
- current Dossier evidence revision: `semantic-bounded-retrieval-2026-09-23`
- current Dossier evidence SHA: `5ad29bc1e4df614191d380bf832f4865f9ee73bab406e314f8d5687b0daa7ec7`
- current Fast work: `data/production/pre_ai/progressive_pass1_work.json`
- current Fast state: `data/cache/progressive_pass1_state.json`
- candidate scope: `data/production/pre_ai/progressive_candidate_context.jsonl`
- candidate semantic queue: `data/production/pre_ai/chatgpt_taste_queue.jsonl`
- Dossier index: `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- current Deep work: `data/production/pre_ai/progressive_pass2_work.json`
- current Deep state: `data/cache/progressive_pass2_state.json`
- Statistics producer: `scripts/progressive_personalization.py`
- Statistics browser surface: `web/progressive-personalization-ui.js`

## 14. Final status

`complete_multiple_root_causes_proven`

Primary zero-completion cause is the missing canonical personalized semantic payload at the worker boundary; Deep additionally receives Dossiers that are structurally accepted but limited in decision evidence. Statistics accurately exposes these outcomes.

## 15. Recommended next Director step

Assign one bounded implementation task for the **Progressive canonical taste-semantic input handoff fix** under the PASS 1 + PASS 2 contracts, with semantic identity regeneration and no manual retry/recovery; require its acceptance to retest Fast completion and the two traced Deep cases before deciding whether a separate Dossier-to-Deep evidence-readiness repair is necessary.

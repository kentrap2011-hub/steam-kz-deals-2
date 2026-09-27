# Jedi Deep missing negative evidence diagnostic 01

## 1. Task

Task ID: `jedi-deep-missing-negative-evidence-diagnostic-01`

Mode: `READ-ONLY / RECON`

Target: `game:1172380` / `STAR WARS Jedi: Fallen Order™`.

Question: determine why the authoritative Deep fit result ultimately produces no negative/risk findings on the published card, without rerunning Fast/Dossier/Deep, processing backlog, changing Scheduled Tasks, or changing runtime/contracts.

Diagnostic baseline: `main@9525a3e402e5d33ba61285bb789ae19251f914cf`.

## 2. Verified chain

The exact current chain is:

1. **Accepted Dossier** — `data/cache/taste_steam_review_dossiers/App_1172380.json` contains both positive evidence and concrete mixed/negative observations.
2. **Deep input requirements** — current worker prompt tells Deep to use the frozen Dossier evidence, but the semantic-outcome section only defines `analyzed_fit`, `analyzed_not_fit`, and `analysis_incomplete`. The result schema/normalizer for an `analyzed_fit` has fields for `positive_evidence` and `taste_factors`, but no field for a balanced negative analysis.
3. **Exact submitted Deep result** — the accepted transport for Jedi was `analyzed_fit / strong / high`, with three `positive_evidence` strings and five taste factors. It contained no negative/risk field.
4. **Accepted PASS 2 state** — ingest accepted that result and persisted the same fit/positive/factor data. No negative evidence was present in the submitted result, so there was nothing for persistence to drop.
5. **Deep semantic projection** — `progressive_pass2.semantic_taste_entry()` turns any authoritative `analyzed_fit` into a Taste entry with `negative_analysis_status: "incomplete_no_confirmed_negative"`, `negative_findings: []`, and `negative_evidence: []`.
6. **Visual/risk projection** — the current evidence-readiness compatibility path interprets an INCLUDE entry with empty `negative_evidence` and no current evidence-contract binding as `legacy_include_without_negative`; personal grounded risk mapping therefore returns no risk.
7. **Current visual item** — Jedi has no described risk, risk component `0`, no counted risk codes, and `risk_status.code = "no_confirmed_risk"`.
8. **Published card** — `priority_ranking.build_risk_status()` supplies the label `Подтверждённых персональных рисков не найдено`; `web/app.js::renderRisk()` shows `Риск пока не подготовлен.` when the card has no risk text.

Negative information therefore disappears **before ingest/state persistence**: it is never representable in the current successful Deep result shape.

## 3. Dossier negative evidence

The Dossier bound to the accepted result has canonical content SHA-256:

`e06c17a567e1f9a249d2ece40eadad045933262562b8ff35aad74c42bf33b144`

and current Git blob:

`bb15bfe5c5a39493cb6479b3ed3ca10aebc10153`.

Relevant accepted observations include:

- **Structure / mixed / moderate recurrence / 3 mentions:** revisiting planets after new abilities is part of the metroidvania loop; the lack of fast travel is rewarding for some players and tedious for others.
- **Conflict / moderate recurrence / 3 mentions:** backtracking is divisive; some players value revisiting areas while others find repeated routes, map layout, and absence of fast travel unnecessarily time-consuming.
- **Friction / negative / current / anecdotal / 1 mention:** a current Russian player-feedback record reports EA application launch/access friction, including mandatory installation, account sign-in, and failure to start the single-player game without it.

The Dossier explicitly records `weaknesses_tradeoffs_investigated: true`, and its coverage marks recurring complaints/trade-offs and technical/performance/localization/regional friction as covered.

These observations are **negative candidates that require personalized semantic evaluation**. This report does not assert that each one must become a confirmed personal risk or ranking penalty. In particular, the existing grounded-risk contract deliberately does not penalize plain backtracking by itself; a confirmed personal relevance/contract code is still required.

Conclusion at this boundary: **relevant negative material exists in the accepted Dossier**. Therefore `NO_RELEVANT_NEGATIVE_EVIDENCE_IN_ACCEPTED_DOSSIER` is excluded.

## 4. Deep prompt/result behavior

Current worker prompt, lines 91–93, defines semantic outcomes as:

- trustworthy fit → `analyzed_fit`;
- trustworthy completed negative → `analyzed_not_fit`;
- unresolved evidence → `analysis_incomplete`.

It does not require an `analyzed_fit` to return a balanced negative assessment.

More importantly, the current result schema makes that omission structural:

- `positive_evidence` is an allowed field;
- `taste_factors` is an allowed field;
- `not_fit_evidence` exists only for the completed `analyzed_not_fit` path;
- there is no generic `negative_analysis_status`, `negative_findings`, `negative_evidence`, `risks`, or equivalent field for `analyzed_fit`;
- `additionalProperties: false` prevents a worker from safely inventing such a field.

The Python normalizer confirms the same contract. For `analyzed_fit`, it persists only `fit_level`, `confidence`, `positive_evidence`, `taste_factors`, and `base_support_compatible`. The negative evidence path is only normalized for `analyzed_not_fit`.

The exact Jedi transport removed during accepted ingest had:

- `outcome: "analyzed_fit"`;
- `fit_level: "strong"`;
- `confidence: "high"`;
- three positive evidence strings;
- taste factors 88 / 81 / 71 / 87 / 86;
- no negative/risk fields.

Thus the concrete Deep result did omit the Dossier's negative candidates, but it did so in a result contract that provides no successful-fit channel in which to return them.

## 5. State persistence

Acceptance commit:

`4a2c09061a018d4723ba17a4fddbf6546f49444e` — `Reconcile Dossier and PASS 2 state`.

At that commit:

- the exact incoming result transport was removed from the inbox after processing;
- ingest receipt `dd6c419c24fbf91d7d62b12f16a025da709321f6887a7ea86d6bbbc34b6338e1.json` was added with `status: accepted`, `outcome: analyzed_fit`, and `authoritative_completed: true`;
- `data/cache/progressive_pass2_state.json` was updated with the same three positive evidence strings and taste factors.

The submitted transport itself had no negative field. The persisted state likewise has no negative field.

Therefore there is **no evidence of an ingest or state-persistence loss**. `INGEST_OR_STATE_DROPS_NEGATIVE_EVIDENCE` is excluded.

## 6. Visual/risk projection

The first explicit negative projection after Deep state is in `scripts/progressive_pass2.py::semantic_taste_entry()`. For every authoritative `analyzed_fit` it emits:

- `negative_analysis_status: "incomplete_no_confirmed_negative"`;
- `negative_findings: []`;
- `negative_evidence: []`.

This is not a mapper dropping a populated negative field; it is the downstream representation of a Deep state that never contained one.

The current Taste evidence compatibility logic then sees:

- `verdict: INCLUDE`;
- empty `negative_evidence`;
- no current `evidence_contract_sha` binding in the Deep-generated semantic entry;

and classifies it as:

`fit_evidence_source: "legacy_include_without_negative"`.

The current canonical visual item for Jedi confirms the result:

- `analysis_state: analyzed_fit`;
- `analysis_semantic_source: progressive_pass2`;
- `deep_stage_state: completed`;
- `deep_stage_outcome: fit`;
- `fit: strong`;
- `fit_evidence_state_source: legacy_include_without_negative`;
- `fit_evidence_bound: false`;
- risk score component: `points: 0`, `value: "штрафа нет"`, `risk_codes_counted: []`;
- `risk_status.code: "no_confirmed_risk"`;
- `risk_status.label: "Подтверждённых персональных рисков не найдено"`;
- `risk_status.has_described_risk: false`.

The final card policy only exposes risks grounded in `taste_negative_evidence` or `confirmed_practical`. Because Deep supplies neither, nothing grounded is available to show. The frontend itself does not compute semantics; it renders the prepared label and uses `Риск пока не подготовлен.` as the empty-list fallback.

Therefore `VISUAL_RISK_PROJECTION_DROPS_NEGATIVE_EVIDENCE` is also excluded as the primary cause: no populated Deep negative evidence reaches that boundary.

### Textual caution versus ranking penalty

The current path should not be read as “no risk penalty” proving “no drawback exists.” They are separate questions.

For Jedi, both happen to be empty because the Deep semantic result carries no negative result at all. The ranking layer counts grounded `risk_codes` (subject to its explicit ignored-code policy), so the current data model does not provide a separate Deep `analyzed_fit` display-only caution channel. A future correction must explicitly distinguish **personal confirmed/scoring risk** from **grounded non-scoring caution** if both are desired; this report does not choose that product rule.

## 7. Control sample

Two additional current authoritative Deep `analyzed_fit` games were checked, within the task's bounded limit.

### `game:1179080` — FAITH: The Unholy Trinity

Accepted Dossier contains:

- mixed simple/old-school mechanics;
- negative friction: slow movement can make exploration, backtracking, and repeated ending attempts laborious;
- mixed difficulty with reported late spikes;
- a conflict about challenge level.

Current Deep state fields still contain only `fit_level`, `confidence`, `positive_evidence`, and `taste_factors`; no negative result field exists.

### `game:1227280` — Despot's Game: Dystopian Battle Simulator

Accepted Dossier contains:

- negative later-stage difficulty swings;
- mixed repetition/run-variety trade-offs;
- negative Steam Deck interface-navigation friction.

Current Deep state again contains only `fit_level`, `confidence`, `positive_evidence`, and `taste_factors`.

The control sample corroborates the code-level finding: this is **systematic behavior of the current Deep `analyzed_fit` path**, not an isolated Jedi evidence case.

## 8. Root cause

**Conclusion label: `DEEP_PROMPT_OR_CONTRACT_OMISSION`.**

The decisive boundary is the Deep successful-fit contract:

- accepted Dossier truth contains negative/mixed candidate evidence;
- current Deep prompt does not require a balanced positive + negative output for a successful fit;
- current Deep result schema does not permit a general negative assessment on `analyzed_fit`;
- the exact Jedi result therefore returns only positives/factors;
- ingest faithfully persists that result;
- downstream Deep projection explicitly creates empty negative arrays;
- visual/ranking/UI then behave consistently with those empty arrays.

`DEEP_SEMANTIC_OMISSION_DESPITE_EVIDENCE` describes the observed Jedi result symptom, but the proven underlying reason is the missing result/prompt contract for balanced negatives on `analyzed_fit`.

## 9. User-visible interpretation

The current card text must **not** be interpreted as “Jedi: Fallen Order has no drawbacks” or “Deep checked all possible negatives and confirmed none.”

What repository truth supports is narrower:

- Deep confirmed a strong fit from positive evidence;
- the accepted Dossier also contained concrete mixed/negative observations;
- the current successful-fit Deep contract had no structured place to return a negative assessment;
- the card consequently has no grounded personal-risk payload to display.

So `Подтверждённых персональных рисков не найдено` currently means “none reached the grounded risk payload,” not “the Dossier contained no negative signal.”

## 10. Changes — report only

Only this report was added:

`reviews/worker_reports/jedi-deep-missing-negative-evidence-diagnostic-01.md`

No contract, prompt, runtime, Dossier, Deep state, Fast state, backlog, visual producer, frontend, workflow, or Scheduled Task was changed.

`CURRENT_TASK.md` was intentionally not edited because this task explicitly permits only the required report to be written.

## 11. Unresolved

The diagnostic does **not** decide which accepted Jedi Dossier observations should ultimately become:

- a confirmed personal risk;
- a low-confidence/neutral caution;
- a scoring penalty;
- display-only context;
- or no personalized warning after evaluation.

That is a contract/product decision that must be made before implementation. The existing negative catalog includes categories such as repetition, difficulty friction, felt technical burden, and `other_grounded_taste_risk`, but Dossier criticism is not automatically a confirmed personal risk.

No production rerun is required to establish the root cause.

## 12. Status

`needs_fix`

The diagnostic is complete; the current Deep successful-fit result contract is insufficient for preserving a balanced negative assessment.

## 13. Recommended next step

Create **one bounded contract-first implementation task** that extends the canonical Deep `analyzed_fit` result contract/schema and its semantic projection to carry an explicit grounded negative-analysis result (including an explicit distinction between scoring risk and any allowed display-only caution), with a bounded Jedi fixture/test proving that accepted Dossier negative candidates are evaluated and survive into visual risk preparation. Do not use a frontend fallback and do not rerun the backlog as part of that task.

Architecture preflight for this recommendation:

- GitHub remains control-plane owner of the Deep result contract, validation, persistence, projection, and visual rebuild.
- Scheduled ChatGPT remains only the bounded semantic worker returning fields explicitly required by the canonical contract.
- No scope/order/retry/scheduler responsibility moves to ChatGPT.
- No new recurring stage, queue, quota, retry loop, or backlog manager is introduced.

## 14. Exact file/result/commit refs

Diagnostic baseline:
- `main@9525a3e402e5d33ba61285bb789ae19251f914cf`

Protocol/task/ownership:
- `CHAT_PROTOCOL.md` blob `38e4891059d71fd16da39bae8e7bbeec684fc56a`
- `config/execution_ownership_contract.json` blob `6975c45a5207c8fae31bc1bb2f7174e4982d02ea`
- `WORKER_TASK_JEDI_DEEP_MISSING_NEGATIVE_EVIDENCE_DIAGNOSTIC_01.md` from the diagnostic baseline

Deep contract/runtime:
- `config/progressive_pass2_contract.json` blob `19d3a443bdd8f0557b214b30241389ded6317aa6`
- `config/progressive_pass2_worker_prompt.md` blob `6b5b5406614c5610b9e9b65fb08ccd674a445917`
- `config/progressive_pass2_result_schema.json` blob `73dd96d4368f2becf40947a50f34505b9057c1f2`
- `scripts/progressive_pass2.py` blob `7fa8b39ccd8936de14a8a859903f6617a8acaa74`
- `scripts/ingest_progressive_pass2.py` inspected at the diagnostic baseline
- `scripts/progressive_personalization.py` blob `8408a66c84df965fe287642b8d9bb2d0baf956bf`

Jedi accepted evidence/result/state:
- Dossier path: `data/cache/taste_steam_review_dossiers/App_1172380.json`
- Dossier Git blob: `bb15bfe5c5a39493cb6479b3ed3ca10aebc10153`
- Dossier canonical content SHA-256 bound to Deep: `e06c17a567e1f9a249d2ece40eadad045933262562b8ff35aad74c42bf33b144`
- Deep work ID: `9ae7b3ff76e8f91f25d6f66285c2c4f47e8b9d97fd343eb4d23798276b9658e2`
- Deep authorization ID: `a54bba18a1bacab918c0de4022b6192f1eb9a3c6a667369edc712801a5082ee6`
- run-start anchor: `850fd0ab32ce67271497ae9bfafe80a8ab83fdce`
- run-start authority: `f8f8370bf647edf05db79eeb4ec82caeee3d5148`
- accepted result transport path: `data/ai_inbox/progressive_pass2/results/4596b03979956f78--9ae7b3ff76e8f91f25d6f66285c2c4f47e8b9d97fd343eb4d23798276b9658e2--a54bba18a1bacab918c0de4022b6192f1eb9a3c6a667369edc712801a5082ee6.json`
- accepted result transport Git blob before ingest removal: `e1fec4cb5a77e8002bd5c6d107032f09546faf35`
- acceptance/ingest commit: `4a2c09061a018d4723ba17a4fddbf6546f49444e`
- ingest receipt: `data/cache/progressive_pass2_ingest_receipts/dd6c419c24fbf91d7d62b12f16a025da709321f6887a7ea86d6bbbc34b6338e1.json`
- ingest receipt blob at acceptance: `f06cdaba19a4aff71fc85ca101c127282b25963f`
- current PASS 2 state path: `data/cache/progressive_pass2_state.json`
- current PASS 2 state blob at diagnostic baseline: `dd0bbb5150fad574a1ef17bbe0eaab440de050d6`

Risk/visual path:
- `scripts/taste_evidence_contract.py` blob `03fa56867e4fcadc873626bbd99cd458c2add050`
- `scripts/taste_negative_contract.py` blob `712a8d457ee8568e8c4345a2120b81a31a1b1173`
- `scripts/refine_visual_ranking.py` blob `90859b55cb033725182eb7866b59ba6c43f7ea3a`
- `scripts/card_explanation_policy.py` blob `96105545d3e3d724f2828e2d34313e18e5a7c833`
- `scripts/build_final_visual_payload.py` blob `48024e190f6256e51d3587cbb413c8007f176701`
- `scripts/priority_ranking.py` blob `ffd85aa2925d65e54cb542fde9994181a41b0e37`
- `data/production/visual/current.json` blob `56c72e5fe7ae7661190706f91287d0106c5b6c1b`
- `data/production/visual/ranking_lookup/s.json` blob `ed9f4db886abe617ece613fe702f81eda34e1d1a`
- `web/app.js` blob `c367c4247d8505b93353f33e857efa36be725e92`

Bounded controls:
- `data/cache/taste_steam_review_dossiers/App_1179080.json` blob `1ef56dbd5d5a74b773b2f86e4492926895f34cb5`
- `data/cache/taste_steam_review_dossiers/App_1227280.json` blob `f910f42c4a9d3435d178fbd5c9683a0aa7b603b0`

## 15. Efficiency / reusable lesson

The most reusable diagnostic route for “Deep says fit but card has no risks” is now:

`accepted Dossier → exact removed/accepted transport from ingest commit → PASS 2 state → progressive_pass2.semantic_taste_entry → taste evidence readiness / grounded-risk mapper → current visual item → priority risk label → frontend fallback`.

The decisive shortcut is to inspect the **exact accepted transport before debugging visual code**. If negative data is already absent there and the schema does not permit it, persistence/UI investigation becomes a bounded confirmation rather than a broad search.

Route/pitfall candidate for a later documentation-only follow-up, if desired: add this exact chain to `PROJECT_ROUTES.md` or `KNOWN_WORKER_PITFALLS.md`. This task did not do so because its write boundary permits only the required report.

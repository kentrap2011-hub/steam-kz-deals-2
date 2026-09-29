# KOF XV missing positive reasons diagnostic 01

## Task

Task: `kof-xv-missing-positive-reasons-diagnostic-01`

Mode: `READ-ONLY / RECON`

Pinned product:
- `THE KING OF FIGHTERS XV`
- AppID `1498570`
- family `game:1498570`

This diagnostic traced the current canonical record from accepted Progressive semantics through the card-explanation producer, canonical visual payload, deploy staging and browser fallback. No Fast, Dossier or Deep semantic run was started. No ranking, publication, UI, contract, workflow, automation or scheduler state was changed.

The only write made by this task is this required diagnostic report.

## Pinned symptom

The current canonical card is:
- `analysis_state = analyzed_fit`;
- `effective_analysis_source = deep`;
- `fit = strong`;
- `priority_rank = 3`;
- `why_fit = []`;
- `why_fit_status = {"has_described_fit": false, "grounding": "insufficient_evidence"}`;
- `why_fit_provenance = []`.

The browser therefore renders the neutral fallback:

`Персональная причина пока не подготовлена.`

The symptom is reproduced in the canonical producer output itself. It is not first introduced by browser rendering.

## Current semantic authority for KOF XV

The current visual authority for `game:1498570` is **authoritative Deep / Progressive PASS 2**, not Fast and not reusable Taste cache.

Current Deep entry:
- `authoritative_completed = true`;
- `outcome = analyzed_fit`;
- `fit_level = strong`;
- `confidence = high`;
- `semantic_generation_id = d21e7d0b38be9d16dbd931900610ff8603715150eec3d0e666f5c84a93e52408`;
- `work_id = 30958cc0d3bf530f846dfcea23f7b382cd60659cf525fc4550b2f863ccf7a3a5`;
- `dossier_content_sha256 = 69061fd36eea80763e61c1fb2eec9886b6e242248f9966335a0e45eb90aa2123`;
- `authorization_id = 14dbe354ac94de42af2204527b3733f41ea9a1d5a856b79383673da18eaba117`;
- accepted at `2026-09-29T11:32:43+00:00`;
- authority commit `21b1d01477d15a9f87c1e0231afbf768f5d42b59`.

`scripts/progressive_personalization.py::build_state_index()` gives an authoritative completed Deep result precedence over Fast and then materializes it through `scripts/progressive_pass2.py::semantic_taste_entry()`.

The older accepted Fast result remains healthy and present, but it is no longer the selected authority for this current card.

## Positive evidence before projection

### Current Deep positive evidence

The authoritative Deep entry contains three non-empty positive rows:

1. `The 3-on-3 system combines fast movement, hops, meter management, cancels and chained supers into a deep mastery-focused fighting loop.`
2. `The large roster and team combinations create substantial long-term experimentation across characters and lineups.`
3. `Character endings and the extensive music collection add identity and variety around the core competitive mechanics.`

Its current `taste_factors` are:
- `gameplay_mastery = 96`;
- `development_variety = 83`;
- `structure_pacing_direction = 70`;
- `identity_hooks = 78`;
- `breadth_of_match = 89`.

### Current Dossier positive evidence

The current Dossier is valid, exact-AppID and current. It contains, among other observations:
- positive mechanics evidence for fast combo-focused 3-on-3 combat with hops, meter, cancels and chained supers;
- positive structure evidence for large roster, team combinations, character endings, music and long-tail variety.

The Dossier therefore does not lack the favorable game facts that Deep used.

### Older Fast positive evidence

The accepted Fast result also contains non-empty grounded positives, including:
- the pinned profile's strong enjoyment of fighting games with distinctive fighters and mastery;
- KOF XV's fast 3-on-3 structure, varied roster and character/team mastery.

Fast is not current visual authority, but its presence independently confirms that this is not a missing-positive-semantic-work problem.

### Exact Deep provenance before card policy

`scripts/progressive_pass2.py::semantic_taste_entry()` copies the Deep `positive_evidence` and creates `positive_evidence_binding` containing the accepted-state identity:
- semantic source/generation;
- profile pin;
- work id;
- family id;
- taste subject;
- appid;
- taste fingerprint;
- candidate-context hash;
- dossier content hash;
- authorization id;
- accepted timestamp;
- work authority commit.

So the required proof exists before card explanation generation.

## Exact projection chain

Current chain for KOF XV:

1. `data/cache/progressive_pass2_state.json`  
   Contains the authoritative completed Deep result, its three `positive_evidence` rows, taste factors and accepted-state identity.

2. `scripts/progressive_pass2.py::semantic_taste_entry()`  
   Produces the selected semantic Taste entry. It preserves all three positives and adds `positive_evidence_binding`.

3. `scripts/progressive_personalization.py::build_state_index()` / `effective_taste_entries()`  
   Selects current semantic authority with Deep precedence. KOF is projected as `effective_analysis_source = deep`.

4. `scripts/card_explanation_policy.py::positive_reasons()` -> `_positive_reason()`  
   Each raw positive is passed through a small deterministic lexical/template recognizer.

5. `scripts/build_visual_feed_v2.py`  
   Calls the shared policy and writes `why_fit`, `why_fit_status` and `why_fit_provenance` into the base visual structure.

6. `scripts/build_final_visual_payload.py::apply_card_explanation_policy()`  
   Re-runs the same shared policy from current semantic inputs. It therefore does not preserve a stale explanation: it deterministically produces the same empty KOF result.

7. `data/production/visual/current.json`  
   Current canonical result has `why_fit=[]`, false described-fit status and no positive provenance.

8. `.github/workflows/deploy-visual.yml`  
   Stages publication with a direct copy:
   `cp data/production/visual/current.json web/data/current.json`.
   `web/data/current.json` is deploy staging output, not a separately tracked semantic authority in current `main`.

9. `web/app.js`  
   Reads `data/current.json`. For an analyzed/personalized card it calls the list renderer with `g.why_fit`; when that array is empty, it displays `Персональная причина пока не подготовлена.`.

## First divergence / root cause

The **first causal divergence is `scripts/card_explanation_policy.py::_positive_reason()`**.

The current KOF Deep positive evidence arrives at this function intact and with valid accepted-state binding. The function then recognizes only a bounded hard-coded set of textual shapes, including:
- 2.5D + first-person;
- a combat-mastery pattern requiring at least two recognized details such as parry, dodge or enemy-reading;
- formation / army composition / unit types;
- multiple-solution phrases;
- a small traversal vocabulary;
- ability/skill progression phrases;
- clue/interrogation;
- choice-consequence phrases;
- clear objective/goal/escape phrases.

None of KOF's three current grounded Deep positives matches those patterns:
- its mastery evidence is about fast movement, hops, meter, cancels and chained supers, not the recognized parry+dodge/enemy-reading combination;
- roster/team experimentation is not recognized by the tactical `formation/army composition/unit types` matcher;
- character endings/music/identity/variety has no supported positive matcher.

Therefore `_positive_reason()` returns `(None, None)` for all three rows. `positive_reasons()` consequently returns empty reasons and empty provenance.

This is a **positive-explanation coverage false negative**, not a provenance/binding failure.

The fail-closed principle itself is healthy: unsupported or generic claims must not be turned into fabricated praise. The defect is that the deterministic recognizer is too narrow to project already-grounded, sufficiently specific favorable evidence that the semantic layer has accepted.

## Why the placeholder appears

The placeholder is a downstream consequence of the producer's empty result:

- card policy returns no recognized positive reason;
- base visual gets `why_fit=[]`;
- final producer re-applies the same policy and keeps it empty;
- canonical visual persists the empty array;
- deploy copies that payload without semantic transformation;
- browser sees an analyzed card with an empty `why_fit` list and correctly renders its neutral placeholder.

There is no later overwrite that removes a previously generated KOF positive.

## Affected scope

The defect is not KOF-only.

Fresh current canonical visual checked at `2026-09-29T18:50:26.476858+00:00`:
- visible items: `257`;
- current `analyzed_fit` cards: `34`;
- all 34 currently use Deep as effective authority;
- cards with non-empty `why_fit`: `7`;
- cards with empty `why_fit`: `27`.

Deterministic comparisons:

### Healthy comparison — Thymesia / `game:1343240`

Current authoritative Deep has grounded positive evidence containing `parry` and `dodge`. That happens to match the existing `combat_mastery` template, so the card receives a grounded personalized reason and full Deep semantic provenance.

### Same-class omission — MY HERO ONE'S JUSTICE 2 / `game:1058450`

Current authoritative Deep is `analyzed_fit` and contains specific positive evidence about:
- expanded roster and differentiated Quirk-driven matchups;
- story/villain/mission routes and offline structures.

Its visual also has `why_fit=[]` because those specific positives do not match the current lexical templates.

### Scope conclusion

Empirically, this is a **broader current Deep positive-explanation projection coverage defect**.

Structurally, the same shared `card_explanation_policy.positive_reasons()` is used for Deep, Fast and reusable semantic entries, so the narrow recognizer is not Deep-specific. The current visible sample contains no Fast-authority analyzed-fit cards, so the live incidence for Fast cannot be quantified from this snapshot. KOF's older Fast positives also do not match the current whitelist, so selecting Fast instead would not solve this KOF symptom.

No evidence supports a special dependency on “Dossier arrived after Fast”.

## Ranking impact

The missing positive text does **not** change KOF's current score or order.

Current KOF visual:
- `total_score = 68.9`;
- `personal_score = 45.9`;
- `purchase_score = 23.0`;
- `priority_rank = 3`;
- ranking stage `deep_fit`.

The personal Taste score uses normalized `taste_factors`, which remain present. `card_explanation_policy.py` explicitly separates explanation visibility from ranking/scoring, and the final producer's canonical rule states:

`positive requires specific Taste evidence; visible negative requires grounded provenance; scoring/ranking semantics unchanged`

The current KOF cautions are display-only cautions and do not create a separate risk penalty here.

This task therefore diagnoses a presentation/projection defect, not a ranking defect.

## What is healthy / do not reopen

Do not reopen or weaken these components for this bug:

- **Fast/PASS 1 state**: current accepted Fast result is healthy and contains positives.
- **Dossier research**: current KOF Dossier is valid and contains useful positive observations.
- **Deep/PASS 2 semantics**: current authoritative Deep result is complete, analyzed-fit, strongly scored and contains three positives.
- **Deep accepted-state binding**: `semantic_taste_entry()` creates the exact positive binding. KOF's current caution provenance also reaches canonical visual with the same accepted Deep identity, independently proving that the binding path is available downstream.
- **Deep-over-Fast authority selection**: current selection is intentional and correct.
- **Provenance validator strictness**: keep fail-closed accepted-state checks. The KOF positives are lost before that validator can evaluate them.
- **Final visual mapping**: it is correctly reapplying the shared policy rather than carrying stale explanation text.
- **Deploy staging**: it copies canonical visual to `web/data/current.json` without reinterpreting semantics.
- **Browser fallback**: the browser is correctly representing the producer-owned empty state.
- **Ranking/scoring**: current score/order uses the accepted Taste factors and is independent of positive explanation visibility.
- **Scheduled workers / manual translator**: unrelated to this defect.

## Unresolved

1. The current visible payload has no Fast-authority `analyzed_fit` cards, so this diagnostic cannot produce a current empirical Fast-only failure percentage. Code structure proves the positive renderer is shared, but current live Fast incidence is not measurable from this snapshot.
2. A live-browser fetch was unnecessary to establish causality: the canonical visual already contains the empty array, deploy stages a byte-equivalent copy, and `web/app.js` has an explicit empty-list placeholder. This diagnostic therefore does not make a separate claim about which exact Pages artifact a user's browser cache may currently hold.
3. This diagnostic does not decide the complete future taxonomy of positive-reason templates. That design belongs to the bounded implementation task; provenance and no-generic-praise requirements remain fixed.

These unresolved items do not block the root-cause diagnosis.

## Status

`diagnosed_needs_fix`

Root cause: grounded current positive evidence is rejected by the overly narrow deterministic positive-reason lexical/template projection in `scripts/card_explanation_policy.py::_positive_reason()`.

## Exact file / blob / commit references

Diagnostic authority before this report write:
- `main`: `1d6dc179b185b78720a0af0d89e26d3ce3af0b0b`

Task/procedure:
- `WORKER_TASK_KOF_XV_MISSING_POSITIVE_REASONS_DIAGNOSTIC_01.md` blob `69cac3fd91eb6f9b0973209236eb1e8baef971ba`

Current semantic/data inputs:
- `data/cache/progressive_pass1_state.json` blob `7ada757c14f44ee62001b04a6f05d62d306913dd`
- `data/cache/progressive_pass2_state.json` blob `7a6ada9642ec74b35782679b30e34b3b0a600d23`
- `data/cache/taste_steam_review_dossiers/App_1498570.json` blob `ddba9994987d64805a2ecdd6743b9bc9945b8546`
- `data/production/visual/current.json` blob `d2c14d020a453c2f18115b0a7995c70baaa03507`

Current producer/policy:
- `scripts/progressive_pass2.py` blob `22fdd60d2f736af3c09cad6d486651fd36484a6e`
- `scripts/progressive_personalization.py` blob `3ec14658bb5db85e2c4089a1e0c05f508c32f611`
- `scripts/card_explanation_policy.py` blob `692668375df10ba311e31223de231896a3b87830`
- `scripts/build_visual_feed_v2.py` blob `6f26a81fe7057990019dc1f1f620f7abf6c0269b`
- `scripts/build_final_visual_payload.py` blob `9ead3d704a5a127be98a3f2b6be04232a8bd416f`
- `scripts/validate_card_explanations.py` blob `c97f2727d8195fb07f5f22d7ad2768f158f0f900`

Current browser/publication:
- `web/app.js` blob `397cfe560f20876bb39f922809d4264e16f8a58c`
- `.github/workflows/deploy-visual.yml` blob `cc308f2fccaeb9db330fa7443e8b9d3fa93f0432`

Relevant existing explanation implementation refs retained as background, not reopened:
- `353bc86d0814c0a1921689f9ab3f23c55d565fce` — shared grounded card explanation policy introduced.
- `df67452288a1c37ab56e74bdff797c9760bdfd2b` — final producer explanation enforcement.
- `77a53d6585e58d84d84b20648571196f4788c5d5` — personal-link wording alignment.
- `d2aa975ed71d2f1ec17626266f025b4268c1b1b5` — focused positive explanation regressions.

## Recommended next step

Create exactly one bounded **IMPLEMENT** task for the GitHub-owned card explanation producer:

**Extend the shared positive-explanation projection in `scripts/card_explanation_policy.py` so already-grounded specific fighting/mastery and roster/team-variety evidence such as the current KOF XV Deep positives can produce a personalized reason, while preserving the existing fail-closed behavior for generic/commercial/rank-only text and preserving exact Deep provenance. Add focused regressions using KOF XV as the pinned case plus one existing healthy card and one same-class omitted card, then validate only a bounded generated canonical sample.**

Boundaries for that one implementation:
- do not rerun Fast, Dossier or Deep;
- do not add per-AppID special cases;
- do not weaken Deep provenance validation;
- do not change ranking/scoring;
- do not move semantic logic into browser/UI;
- do not change publication ownership;
- do not create/change scheduler, queue, retry or Scheduled Tasks.

Architecture preflight for that next step is already clear:
- owner: GitHub visual/explanation producer;
- canonical route: existing shared card-explanation policy and final producer;
- no control-plane responsibility moves to ChatGPT/browser;
- no new recurring stage, queue, retry loop or scheduler is required.

## Efficiency / reusable lesson

The diagnosis was slower mainly because both `progressive_pass2_state.json` and `data/production/visual/current.json` are larger than the normal GitHub Contents response path used by this connector. A direct large-file fetch produced an empty body and a raw-file attempt was rejected. The bounded recovery was to read their already-known exact Git blob objects and extract only the pinned AppID/current comparison records.

Reusable route lesson:
- for large Progressive state/visual files, prefer exact blob identity + bounded Git blob retrieval instead of repeated Contents/raw retries;
- for “missing positive text” diagnostics, inspect `semantic_taste_entry -> card_explanation_policy._positive_reason -> final visual` before investigating UI;
- an empty `why_fit` with intact Deep cautions/provenance is a strong early signal that accepted-state identity is healthy and positive template coverage should be checked.

Because this task permits only the diagnostic report as a durable write, `PROJECT_ROUTES.md` / `KNOWN_WORKER_PITFALLS.md` were intentionally not edited. A later bounded maintenance change may add the large-blob retrieval note to the existing Progressive visual/card-explanation route if desired.

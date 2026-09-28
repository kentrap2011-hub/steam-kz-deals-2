# Atelier Escha & Logy Deep without positive reason — diagnostic 01

## 1. Task

Task ID: `atelier-escha-logy-deep-without-positive-reason-diagnostic-01`.

Mode: READ-ONLY DIAGNOSTIC. The only repository write performed by this task is this durable report.

Target:
- family: `game:1152310`
- Taste subject: `App_1152310`
- AppID: `1152310`
- title: `Atelier Escha & Logy: Alchemists of the Dusk Sky DX`

Question: explain why the published card is already Deep-authoritative and can say `МОЖНО БРАТЬ`, and can show the display-only warning `Есть подтверждённые нюансы — без отдельного штрафа`, while `Почему может зайти` is still empty and the UI falls back to `Персональная причина пока не подготовлена.`

No Deep, Fast, or Dossier worker was run. No card, score, rank, risk, queue, scheduler, or Scheduled Task setting was changed.

## 2. Pinned current truth

Inspection baseline immediately before this report write:
- repository: `kentrap2011-hub/steam-kz-deals-2`
- branch/source of truth: `main`
- inspected `main` head: `b09b179010cfaafdd740f2b773d05b3193cd78f8`

Current production semantics observed on that baseline:
- current global semantic generation in `data/production/pre_ai/progressive_pass2_work.json`: `d21e7d0b38be9d16dbd931900610ff8603715150eec3d0e666f5c84a93e52408`
- Atelier's immutable accepted Deep revision keeps its historical generation `4596b03979956f78c308551a75fdbe9f432ed3f80925c29b0835bdb052222033`
- the old generation is still current through the fail-closed PPD-012 historical semantic-equivalence rule; it was not rewritten to the new generation.

The PPD-010 legacy reanalysis migration is currently complete: 30/30 accepted completed revisions. Atelier is one of those migrated revisions.

## 3. Exact product identity

The exact current product identity is:
- `family_id=game:1152310`
- `taste_subject_key=App_1152310`
- `appid=1152310`
- `work_id=beebff3f680904998a25cfad4ee14a509681f97ab48ececa8894e7a178b73ea0`
- `taste_fingerprint=3ebb6a7d9452c0f7f3f356a4c48895af9476287bf06b99dfb5c864b1fc8851df`
- `candidate_context_sha256=dd825ea7d7d004d0700fac51f942eba39d3d0d321c3c934d509567f3060dc0f7`
- Dossier path: `data/cache/taste_steam_review_dossiers/App_1152310.json`
- Dossier content SHA-256: `41dce0c3148d3b113bc5071b10fe060fe312c8b49861bbf9e84ec71f53930f84`

The current purchase context for the same family has:
- strong-fit branch: `disposition=INCLUDE`, `purchase_decision=МОЖНО БРАТЬ`, `priority_bucket=2`
- moderate-fit branch: also `INCLUDE` / `МОЖНО БРАТЬ`, with bucket 5
- current displayed price 357 RUB, original 893 RUB, discount 60%.

There is no current PASS 1/Fast state entry for `game:1152310` in `data/cache/progressive_pass1_state.json`. Deep authority does not depend on Fast completion.

## 4. Current semantic authority

The current accepted Deep state in `data/cache/progressive_pass2_state.json` is authoritative:
- `authoritative_completed=true`
- `outcome=analyzed_fit`
- `fit_level=strong`
- `confidence=medium`
- `analysis_issue_code=null`
- current accepted migration revision: `2026-09-28T10:21:47+00:00`
- `work_mode=legacy_full_reanalysis`
- work authority: `637b5e9cdda16f73e31aac05b09b99c88f9f5ce9`
- current authorization: `3f0f9e898604a3feb152fa516d2d2d481254f66ab789bcf36d3268980d8b4fa3`

Its normalized Taste factors are:
- gameplay mastery: 82
- development variety: 84
- structure/pacing/direction: 83
- identity hooks: 72
- breadth of match: 82

PPD-012 is relevant because the current global generation has moved on while this accepted result retains historical exact provenance. `scripts/progressive_pass1.py::state_entry_semantically_matches()` accepts an old state only by exact identity, direct new semantic identity, or `historical_semantic_equivalence()`. The historical path reopens the exact work-authority manifest and proves the same profile content, model/semantics/context bindings, and item identity. It does not rewrite the result. `scripts/progressive_pass2.py::authoritative_completion_entry()` then exposes the accepted Deep result as current.

Therefore Atelier is not accidentally using a stale Deep row. Its current Deep authority is deliberate PPD-012 reconciliation.

## 5. Accepted Deep positive evidence

The accepted Deep result contains **three non-empty positive-evidence rows**. They were already present in the prior normal first pass and PPD-010 required the migration to preserve them exactly:

1. `The synthesis system starts approachable and becomes substantially more flexible through elemental values, skills, trait transfer and protagonist-specific specialties, directly matching the preference for visible mechanical development.`

2. `Six-character front/back parties and support attacks make combat more dynamic and add tactical planning rather than leaving progression concentrated only in crafting.`

3. `Four-month assignments provide clear short-term goals while usually leaving substantial discretionary time, fitting the preference for direction without excessive lostness or deadline pressure.`

They correspond directly to the accepted Dossier:
- positive `observation[0]`, category `mechanics`: synthesis grows from approachable to flexible; elemental values, skills, trait transfer, protagonist specialties;
- positive `observation[1]`, category `mechanics`: six-character front/back party, support attacks, more dynamic turn-based combat;
- positive `observation[2]`, category `pacing`: four-month assignments provide clear short-term goals and generally lenient time pressure.

The Deep result schema stores positive evidence as non-empty strings, not as per-row structured `evidence_refs`. Therefore the accepted positive rows do **not** contain explicit `observation[index]` pointers in the way PPD-009 negative findings do. Their exact accepted-state provenance is instead bound to the Deep item/Dossier identity, including the Dossier content SHA-256. The one-to-one observation mapping above is verified from the exact bound Dossier content; it is not a separate stored per-row reference field.

This is not an accepted-fit-with-zero-positives case. In fact, `scripts/progressive_pass2.py::normalize_result()` calls the shared text-list validator with `require_nonempty=True` for `analyzed_fit`. A newly accepted Deep `analyzed_fit` result with zero positive rows is invalid. PPD-010 is stricter still: a legacy fit migration must have preserved prior positives and the submitted list must equal the preserved list exactly.

## 6. Why personal reason is missing

The positive evidence is not lost in Deep persistence and is not stale/unbound.

Current transport is:
`accepted PASS 2 state -> progressive_pass2.semantic_taste_entry() -> effective_taste_entries() -> card_explanation_policy.positive_reasons() -> visual why_fit`.

`semantic_taste_entry()` explicitly copies all three `positive_evidence` strings and supplies a `positive_evidence_binding` containing the exact Deep identity, Dossier SHA, authorization, accepted time, and work authority. Thus the already-fixed provenance handoff is present.

The loss happens in `scripts/card_explanation_policy.py::_positive_reason()`. That policy is deliberately fail-closed: it emits a Russian `why_fit` reason only when the English accepted evidence matches one of a bounded set of recognized semantic phrase patterns.

None of Atelier's three valid rows currently matches a supported policy code:

- synthesis row: it contains `skills`, but the `ability_progression` mapper additionally requires one of `new`, `unlock`, `upgrade`, `expand`, or `progress`; the accepted sentence says `visible mechanical development`, so it does not match;
- party/combat row: it says `front/back parties`, `support attacks`, and `tactical planning`, but the current tactical mapper looks for `formation`, `army composition`, or `unit types`; the combat-mastery mapper instead looks for at least two of parry/dodge/enemy-reading signals; neither condition matches;
- assignment row: it says `clear short-term goals`, but the current clear-objective mapper looks for the literal patterns `clear objective`, `clear goal`, or `escape premise`; `clear short-term goals` does not contain the required literal `clear goal` sequence.

The policy therefore returns `why_fit=[]` and empty positive provenance for display even though the upstream Deep evidence and binding are valid.

The UI then does exactly what it is coded to do: for an `analyzed_fit` card it calls `textList(..., g.why_fit, 'Персональная причина пока не подготовлена.')`. The fallback text is therefore a **rendering consequence of an empty mapped list**, not evidence that Deep found no positive arguments.

Classification: **shared positive-explanation policy coverage defect** at the Deep-positive -> player-facing Russian explanation boundary. It is not a Deep-result defect, Dossier defect, PPD-012 currentness defect, frontend data-loss defect, or missing-positive-provenance defect.

## 7. Why caution is visible

The negative/caution channel is structurally different because PPD-009 stores an already classified, already user-facing Russian finding with exact Dossier references.

Atelier's current migrated Deep negative assessment is:
- `status=completed`
- evaluated candidates: `observation[3]` and `observation[4]`
- one surfaced finding:
  - `disposition=caution`
  - `risk_code=null`
  - text: `У английской локализации отмечают опечатки и местами неточные или расплывчатые описания механик; это может мешать осознанному сравнению и настройке систем, хотя не отменяет их глубину.`
  - exact evidence reference: `observation[4]`

Dossier `observation[4]` is a negative translation/localization observation about typos, liberal translations, and vague or misleading mechanic descriptions.

`semantic_taste_entry()` projects this through `deep_negative_findings` plus an exact Deep binding. `card_explanation_policy.deep_cautions()` does not need to infer a new Russian reason from arbitrary English prose: it accepts a current Deep `caution` only when the assessment status/binding is valid and then passes the already prepared `text_ru` and `evidence_refs` through.

PPD-009 explicitly defines such a caution as display-only: it has no `risk_code`, creates no ranking penalty by itself, and may be shown to the user. This explains the visible asymmetry: the negative side already arrives in display-ready structured form, while the positive side still requires a bounded phrase-to-Russian mapper.

## 8. Why game can still be buyable

The buyability label and the positive prose explanation are separate outputs.

Current ranking review for Atelier proves:
- rank: 2
- `source_fit=strong`
- `fit=strong`
- `decision=МОЖНО БРАТЬ`
- `priority_bucket=2`
- total score: 66.2/100
- purchase score: 23
- current risk status: `caution_only`
- `affects_score=false`
- `score_penalty=0`
- no scored risk code.

The exact candidate context says the strong-fit commercial branch is `INCLUDE` and its `purchase_decision` is `МОЖНО БРАТЬ`. `scripts/refine_visual_ranking.py::apply_commercial_branch()` selects the branch from the already resolved fit and copies that purchase decision. The final score/ranking is calculated separately.

Therefore an empty `why_fit` display list does not invalidate the accepted Deep fit, does not change the Taste factor vector, and does not make an otherwise eligible commercial branch ineligible. The current caution also intentionally carries no separate penalty. The card can consistently be:
- Deep-authoritative strong fit;
- commercially eligible / `МОЖНО БРАТЬ`;
- caution visible without score penalty;
- positive prose missing because the renderer failed to recognize the accepted positive sentence shapes.

## 9. Relation to prior positive-projection fix

This is directly related to the previously accepted Deep-positive card-projection defect, but it is **not** evidence that the provenance fix regressed.

Accepted prior fix:
- task/report: `deep-positive-evidence-card-projection-fix-01`
- implementation PR #105
- merge commit: `21c3331eec471a18889de0264776216490bee7bf`
- target at that time: Jedi Fallen Order.

That diagnosis proved the same broad boundary: accepted Deep positives survived state persistence but the shared fail-closed explanation mapper could not turn them into card reasons. The implementation then:
1. added exact `positive_evidence_binding` provenance for Deep;
2. added bounded mapper coverage for combat-mastery and ability-progression evidence;
3. validated the resulting `why_fit_provenance.semantic_binding`.

Atelier demonstrates a remaining coverage hole. The current Deep provenance path is working: its accepted positives reach `semantic_taste_entry()` with an exact binding. What is missing is a recognized mapping for these three specific semantic shapes (crafting/synthesis development, party/support tactical depth, and clear short-term assignment goals).

So the relationship is:
- **same defect class / same shared rendering boundary**;
- **different still-uncovered evidence shapes**;
- **not a reappearance of the fixed missing-binding problem**;
- **not proof that the Jedi repair was undone**.

## 10. User-facing explanation

Простыми словами:

У Atelier Deep-разбор действительно нашёл три причины, почему игра тебе может подойти: развитие алхимии и крафта, более тактические бои с шестью персонажами и понятные короткие цели по заданиям.

Эти плюсы сохранены и используются в итоговой оценке игры. Но карточка не показывает английский текст Deep напрямую. Она пропускает его через ограниченный набор правил, которые должны превратить доказательство в нормальную русскую персональную причину. Формулировки Atelier пока не попадают ни под одно из этих правил, поэтому блок остаётся пустым и интерфейс пишет «Персональная причина пока не подготовлена».

Предупреждение про локализацию устроено иначе: Deep уже сохранил его готовым русским текстом и привязал к конкретному отрицательному наблюдению Dossier, поэтому оно отображается без дополнительного распознавания.

`МОЖНО БРАТЬ` не означает, что положительная причина на карточке обязательно заполнена. Этот статус берётся из отдельной ветки: у игры подтверждён сильный Deep-fit, цена проходит коммерческий фильтр, а найденный нюанс является предупреждением без отдельного штрафа.

## 11. Changes — report only

Created this diagnostic report only.

Not changed:
- Deep state/result;
- Fast state/result;
- Dossier state/result;
- card content;
- positive mapper;
- ranking;
- score weights;
- risks/cautions;
- candidate context;
- visual payload;
- Scheduled Tasks / scheduler settings.

No semantic worker was invoked.

## 12. Unresolved

The positive card renderer still has no accepted mapping for Atelier's three positive-evidence sentence shapes. Therefore a normal deterministic visual refresh with the current code will continue to produce an empty `why_fit` for this game even though its authoritative Deep positives remain present and current.

This is not normal semantic-contract behavior in the sense of “Deep fit may contain no positive evidence”: current Deep acceptance requires non-empty positive evidence. It is normal **fail-closed renderer mechanics** to leave the card explanation empty when no allowed mapper rule matches. Given the product intent established by the prior Deep-positive projection repair, the uncovered valid Deep evidence is a **remaining implementation defect / coverage gap**, not a reason to treat the Deep result as invalid.

## 13. Status

`needs_fix`

## 14. Recommended next step

Create one bounded implementation task to extend the shared fail-closed positive explanation policy with grounded mappings/regressions that cover Atelier's accepted synthesis-development, party/support tactical-depth, and clear-short-term-goal evidence shapes while preserving exact Deep provenance and leaving Deep/Dossier/Fast/ranking semantics unchanged.

## 15. Exact commit/artifact refs

Inspection/current truth:
- inspected pre-report `main`: `b09b179010cfaafdd740f2b773d05b3193cd78f8`
- current Deep state blob observed: `642a5d64971aac81998fa59801d41ecd36cf18ed`
- current Fast state blob observed: `7ada757c14f44ee62001b04a6f05d62d306913dd`
- current Dossier blob for App 1152310: `f73ce6f739d8626bc68dbdb0df0ec4f308f2212a`
- Dossier content SHA-256: `41dce0c3148d3b113bc5071b10fe060fe312c8b49861bbf9e84ec71f53930f84`
- current ranking review blob observed: `8b35f1472eaed18fbb70fe7b6b8304b1bf73365b`
- current candidate-context blob observed: `2b09a4d945d497387e160ab5e574d2627ade3297`
- current card explanation policy blob observed: `692668375df10ba311e31223de231896a3b87830`
- prior positive-projection report blob: `723338559b31e407e6d76ae157122b7c51385628`

Atelier accepted Deep:
- historical semantic generation: `4596b03979956f78c308551a75fdbe9f432ed3f80925c29b0835bdb052222033`
- work ID: `beebff3f680904998a25cfad4ee14a509681f97ab48ececa8894e7a178b73ea0`
- prior normal-first-pass authorization: `b7702416dff6ba8343efd85867d15a8095fdc395d3e23e86cac21d1af2197213`
- prior accepted at: `2026-09-27T17:21:20+00:00`
- prior work authority: `f8f8370bf647edf05db79eeb4ec82caeee3d5148`
- PPD-010 migration authority: `97d7798dfbf113ff0c3c4e71a75c7d50b39f3b3a`
- migration frozen at: `2026-09-28T04:01:33Z`
- current migrated authorization: `3f0f9e898604a3feb152fa516d2d2d481254f66ab789bcf36d3268980d8b4fa3`
- current migrated accepted at: `2026-09-28T10:21:47+00:00`
- current migrated work authority: `637b5e9cdda16f73e31aac05b09b99c88f9f5ce9`

Relevant accepted fixes/decisions:
- PPD-010: legacy Deep full reanalysis with preserved positives
- PPD-012 primary implementation PR #113 merge: `bf4061d3` (full repository history retains the canonical full SHA)
- PPD-012 production-history regression PR #114 merge: `32f3354d`
- PPD-012 downstream exact Deep-risk projection PR #115 merge: `e864f882d74d26512d1430ab1632d7c93654f058`
- Deep-positive projection PR #105 merge: `21c3331eec471a18889de0264776216490bee7bf`

Current PPD-012 profile semantic identity:
- `profile_semantic_sha256=f0852fd520755bedafb764da25d3aa391fd0706eae4878d6f89ef10894fd915e`
- current global semantic generation: `d21e7d0b38be9d16dbd931900610ff8603715150eec3d0e666f5c84a93e52408`

## 16. Efficiency / reusable lesson

For future cases where a current authoritative Deep-fit card says `Персональная причина пока не подготовлена`, do not start by rerunning Deep or inspecting the frontend broadly.

Use this bounded route:
1. prove the exact current Deep entry and `positive_evidence`;
2. prove currentness with exact identity / PPD-012 historical equivalence if generations differ;
3. inspect `semantic_taste_entry()` to confirm the evidence and binding survive;
4. test each accepted sentence against `card_explanation_policy._positive_reason()`;
5. only if the mapper emits a reason should investigation continue into visual handoff/frontend.

For Atelier, step 4 is the terminal diagnostic boundary: all three valid accepted positive rows fail the current bounded mapper, while the separate structured PPD-009 caution path succeeds.

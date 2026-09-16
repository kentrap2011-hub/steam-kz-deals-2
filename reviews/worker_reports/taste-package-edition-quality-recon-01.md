# Taste Package / Edition Quality RECON 01

Task: `taste-package-edition-quality-recon-01`  
Mode: `READ-ONLY / RECON`  
Status: `complete`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`  
Recon baseline: `969ba7837dd725326055a3a315a3cdb1e6bbd142`

## Executive conclusion

Specific package/remaster/edition quality should remain a **separate offer/version-quality dimension**, not part of member-game Taste and not a second ranking system.

The canonical durable owner should be GitHub control-plane state in a new compact **offer-scoped edition-quality evidence object**, keyed to the exact Steam offer/version identity. It should reuse the existing multi-source player-feedback evidence semantics (identity binding, recent-first current-state handling, Russian-evidence attempt, compact provenance, no raw review bodies), but it should **not be stored inside the member-game Taste dossier**. A package or collection can have several member-game dossiers, while its edition/offer quality is one different concern with a different identity and lifecycle.

The final effect should enter the existing `FINAL-PRIORITY-RANKING-V2` through its existing visible **personal `risk` component**, whose current maximum penalty is 12 and whose combine rule is `strongest_only`. No new final score, package-quality score, ranker, sorter, or hidden tie-break is needed.

A critical integration constraint is that edition quality is **offer-scoped**. For an `App_...` whose exact app is the remaster/edition being ranked, the risk can apply directly to that candidate. For a `Sub_...` package attached as an alternative purchase route to a game, the package risk must apply only to that package route. Applying it globally to the game card would incorrectly penalize the standalone route too. Therefore the existing route comparison eventually needs to compare the same transparent final-score formula with the correct route-scoped risk attached to each route, while still producing one `total_score` and one final `priority_rank`.

## Architecture preflight

Result: **PASS for RECON/report publication; implementation requires a later contract-first task.**

1. **Current owner:** `config/execution_ownership_contract.json` assigns exact scope/identity, deterministic transformations, validation, persistence, completeness, and final downstream calculation to GitHub. Scheduled ChatGPT is only a constrained external/semantic data-plane worker.
2. **Current authority:** `config/final_ranking_policy.json` is the sole final ranking authority. No canonical offer-edition-quality contract exists on the recon baseline, so this task does not invent runtime behavior or modify ranking.
3. **Control-plane transfer:** the proposal does not move scope, identity, retry, cache merge, route selection, or scoring authority into Scheduled ChatGPT or the interactive chat.
4. **No new recurring architecture:** the proposal requires no second scheduler, second ranker, independent retry loop, or ChatGPT-owned backlog. Future evidence acquisition should reuse the existing bounded semantic/web-research execution architecture under GitHub-prepared work, with a distinct offer-quality data object/contract.

No source, schema, workflow, ranking policy, prompt, production data, Scheduled Task, Taste Semantic Producer, PR #31, or `CURRENT_TASK.md` was changed by this task.

## Verified current architecture

- `config/final_ranking_policy.json` defines the only canonical automatic order: `sale_expiry_urgency_asc -> total_score_desc -> title_asc`.
- `total_score = personal_score + purchase_score`; personal is max 60, purchase max 40.
- Existing personal `risk` is already visible and can subtract up to 12 points. Current configured magnitudes are `0`, `-1`, `-3`, `-10`, `-12`, with `strongest_only` combination.
- `scripts/priority_ranking.py` exposes that risk in `score_breakdown.personal_components[id=risk]`, `risk_status`, and `risk_status.score_penalty`.
- `web/app.js` already has a prominent `risk_status` surface plus the visible `risks` list.
- `scripts/card_explanation_policy.py` already separates score calculation from visible grounded warnings; visible negatives require grounded provenance.
- Fixed `Sub` package economics already live as a purchase route in `scripts/apply_fixed_package_purchase_options.py` and `scripts/priority_ranking.py`; current route selection compares standalone vs fixed-package purchase score.
- Current Taste dossier V2 is a neutral **game/release** evidence object keyed by exact game app identity. Its web-evidence contract already supplies the useful evidence rules: exact identity, multi-source player feedback, recent-first technical-state evidence, Russian-language attempt, `current/historical/durable/uncertain` temporal status, and no raw review bodies.
- The dossier schema does not currently model an offer/package quality subject or edition-specific categories such as port quality, remaster changes, missing content, launcher/DRM, or edition technical state. This confirms that simply putting package-quality findings into a member-game dossier would conflate identities.
- `WORKER_TASK_TASTE_PACKAGE_MEMBER_DOSSIER_AGGREGATION_01.md` establishes the required separation: package member games are evaluated independently for Taste; at least one qualifying member can keep the package alive; edition/package quality is a separate later signal and must not hard-exclude at Taste.

## Findings for the 10 required questions

### 1. Canonical location

Use a dedicated GitHub-owned compact evidence cache/object for **offer edition quality**, separate from `data/cache/taste_fit.json` and separate from member-game dossiers. Proposed canonical names for a future implementation:

- contract: `config/offer_edition_quality_contract.json`;
- evidence schema: `config/offer_edition_quality_schema.json`;
- canonical cache: `data/cache/offer_edition_quality.json`.

Those names are proposals, not files created by this RECON.

The final visual producer should only attach the already validated deterministic result to the exact offer/route before the one canonical `priority_ranking` pass.

### 2. Reuse existing dossier evidence model or distinct object?

**Reuse the evidence policy, not the storage identity.**

The existing dossier web model is suitable for how to research evidence: bounded multi-source player feedback, recent-first technical claims, durable-vs-current separation, Russian evidence, compact provenance, no raw bodies. It is not a safe canonical home for package/edition quality because:

- member dossiers are game-release/app scoped;
- a package can map to multiple member dossiers;
- a `Sub` package is an offer identity, not a single game build;
- an app-backed collection/remaster needs exact version identity distinct from the underlying original games;
- current dossier categories do not explicitly distinguish edition-specific defects.

Therefore use a distinct bounded evidence object linked to the exact offer/version, while sharing the existing research semantics and, if implemented, preferably the existing Scheduled ChatGPT web-research runtime rather than creating another recurring producer.

### 3. Exact research identity

Research must bind to the **quality subject actually sold**, not to an arbitrary member game.

Proposed identity model:

- `offer_key`: exact canonical `App_<appid>` or `Sub_<packageid>`;
- `entity_kind`: `app` or `sub`;
- `exact_offer_title`;
- `edition_or_version_label` when present (`Definitive`, `Remastered`, `Anniversary`, collection name, etc.);
- `edition_release_year` when reliably resolvable;
- exact `appid` for app subjects or exact `packageid` for Sub subjects;
- `member_appids[]` and a composition hash for packages/collections where membership is material;
- `identity_status`: `resolved` or `ambiguous`;
- a deterministic `identity_fingerprint` so title/version/member-composition changes invalidate stale evidence.

For an app-backed remaster/collection, the exact current App/version is the research identity; original/member titles are only corroborating context. For a Sub, the package ID/title is the offer identity, but technical claims must identify the affected included app/version where the Sub itself is only an entitlement container. Never treat a member appid as the package's software identity.

### 4. Distinguishing intrinsic game criticism from edition-specific criticism

Every finding needs an explicit `claim_scope`:

- `edition_specific` — applies to the exact remaster/port/collection/package version;
- `member_game_intrinsic` — gameplay/story/pacing/design criticism of the underlying game itself;
- `ambiguous` — scope cannot be reliably separated.

Only `edition_specific` findings may drive edition-quality risk. `member_game_intrinsic` belongs in the member-game Taste dossier and must not be duplicated as an edition penalty. `ambiguous` cannot cause a material edition penalty.

Edition-specific finding codes should cover at least:

- `technical_bugs`;
- `performance`;
- `port_quality`;
- `missing_or_removed_content`;
- `remastering_quality`;
- `graphics_audio_changes`;
- `launcher_or_drm`;
- `localization_or_font`;
- `regional_service`.

A finding should qualify as edition-specific only when the evidence is tied to the exact version/port/package identity or clearly describes a difference introduced by that edition. Generic dislike of GTA III gameplay, for example, is not evidence that GTA Trilogy Definitive Edition is a bad edition.

### 5. Freshness and fixed launch issues

Reuse the current dossier temporal model:

- `current`: recent evidence supports that the problem still exists;
- `historical`: older launch problem is shown by newer evidence to be fixed or materially reduced;
- `durable`: a version-specific change remains intrinsic to the edition, e.g. removed content or persistent remastering/graphics/audio changes;
- `uncertain`: temporal conflict or insufficient evidence prevents a current-state conclusion.

For bugs, performance, compatibility, launcher/DRM, localization, and regional-service state, recent evidence must dominate old evidence. Search recent-first and prefer evidence from the last 12 months when available, matching the active web-evidence contract. A launch-only problem marked `historical` must not retain a current severe score penalty.

For cache freshness, a future contract should use a shorter refresh window for active technical state than for durable changes; a practical starting proposal is 14 days for severe/current technical findings, 30 days for ordinary current-state evidence, and up to 60 days for durable edition changes, always invalidated earlier by identity/version fingerprint changes. These TTL values are proposal-level and are not current policy.

### 6. Existing score/risk component for the penalty

Use **only** `score_model.personal.risk` in `FINAL-PRIORITY-RANKING-V2`.

Do not reduce Taste factors, do not alter commercial price/value points, and do not create `edition_quality_score` as another final score. A future policy mapping can reuse the existing risk penalty magnitudes without expanding the current risk budget:

| Edition evidence state | Proposed existing-risk effect |
|---|---:|
| severe + `confirmed` + current/durable | `-12` |
| severe + `supported` + current/durable | `-10` |
| moderate + confirmed/supported + current/durable | `-3` |
| low + confirmed current/durable | `-1` |
| limited/anecdotal, historical-only, uncertain/conflicted, unavailable | `0` material penalty |

Keep the current `max_penalty=12` and `combine_rule=strongest_only`, so edition quality cannot stack with another risk into an unbounded hidden punishment.

Do **not** misuse `modern_windows_friction` merely to obtain the `-12` branch. Edition quality needs its own explicit structured risk provenance under the same canonical risk component.

### 7. Existing warning/explanation surface

Reuse the current card surfaces:

- `risk_status` for the prominent severity banner;
- `risks[]` for one concise grounded explanation;
- `risk_provenance` for deterministic provenance binding.

For severe confirmed/supported edition problems, the visible warning should explicitly scope itself, e.g. `Проблема конкретного издания: ...`, and the banner should state that the edition problem affects ranking. It must not read as though the member games themselves are bad Taste matches.

For a fixed-package route, the same canonical warning should also be echoed beside that package offer in the existing package-offer presentation so the user can see which purchase option is affected. That echo is display-only; it must not create a second warning state or second scoring path.

`scripts/card_explanation_policy.py` currently allows only `taste_negative_evidence` and `confirmed_practical` as visible grounded sources. A future implementation should add an explicit grounded edition-quality provenance class instead of laundering web evidence through an unrelated source type.

### 8. Severity / confirmation states

Use orthogonal dimensions rather than one opaque quality score:

- severity: `none | low | moderate | severe`;
- confirmation: `confirmed | supported | limited | conflicted | unavailable`;
- temporal status: `current | historical | durable | uncertain`;
- recurrence: reuse `strong | moderate | limited | anecdotal` where useful.

Suggested confirmation rules:

- `confirmed`: exact identity resolved, multiple independent player-feedback sources when practical, materially consistent evidence, and recent support for current-state claims;
- `supported`: exact identity resolved and evidence is substantial but source diversity or recurrence is weaker than confirmed;
- `limited`: sparse evidence; cannot cause a strong penalty;
- `conflicted`: meaningful sources disagree or temporal state cannot be reconciled; no strong penalty;
- `unavailable`: research/access/evidence insufficient; neutral score effect.

A single anecdotal complaint must never produce a serious penalty.

### 9. Strong member Taste + severe edition quality

The package remains alive at the Taste stage because member aggregation and edition quality are separate dimensions. One qualifying member is still sufficient under the product rule; weak members are not averaged against it.

After that, severe confirmed edition quality enters the existing final risk component. Outcomes:

- if the exact edition itself is the candidate App, its total score is reduced by the risk penalty;
- if the problematic object is a fixed `Sub` purchase option, only that package route receives the edition risk;
- the standalone route for the same member game remains unpenalized unless it has its own exact edition-quality evidence;
- if the package route no longer produces the better transparent total after its risk is applied, the existing recommendation should fall back to the standalone route while keeping the package visible with its warning;
- if the problematic edition is the only relevant route, its one canonical `total_score` falls normally and therefore its final rank falls.

The current main policy does not expose a separate post-score inclusion cutoff. Therefore this RECON does not invent one. If a future/current canonical policy contains a general score inclusion threshold, the already-penalized `total_score` may naturally cross it; edition quality itself still must not hard-exclude at Taste.

### 10. Missing or ambiguous evidence

Use **fail-closed attribution, fail-neutral scoring**.

- If exact offer/version identity cannot be resolved, do not publish a negative edition-quality finding against that offer.
- If evidence is unavailable, insufficient, limited, or temporally conflicted, do not assume the edition is bad and do not apply a material penalty.
- If old negative evidence is contradicted by newer evidence showing a fix, mark the old issue historical and remove the current technical penalty.
- Preserve an explicit evidence state (`unavailable`, `conflicted`, etc.) so neutral scoring is not mistaken for proof that the edition is good.

This is the correct asymmetry because edition-quality evidence is a negative modifier after Taste eligibility: absence of evidence is not evidence of poor quality, while attaching criticism to the wrong edition would be materially harmful.

## Proposed compact evidence schema

Illustrative shape only; no schema was created by this RECON:

```json
{
  "offer_key": "App_... or Sub_...",
  "identity": {
    "entity_kind": "app|sub",
    "steam_id": "...",
    "exact_offer_title": "...",
    "edition_or_version_label": "...",
    "edition_release_year": null,
    "member_appids": [],
    "identity_status": "resolved|ambiguous",
    "identity_fingerprint": "sha256:..."
  },
  "generated_at_utc": "...",
  "expires_at_utc": "...",
  "overall": {
    "severity": "none|low|moderate|severe",
    "confirmation": "confirmed|supported|limited|conflicted|unavailable",
    "temporal_status": "current|historical|durable|uncertain"
  },
  "findings": [
    {
      "code": "performance",
      "claim_scope": "edition_specific|member_game_intrinsic|ambiguous",
      "severity": "moderate",
      "confirmation": "supported",
      "evidence_status": "current",
      "recurrence": "moderate",
      "statement": "compact synthesis, no raw review body",
      "affected_appids": [],
      "source_ids": []
    }
  ],
  "russian_attempt": "found_and_used|searched_not_found_or_insufficient|source_access_unavailable",
  "provenance": {"sources": []}
}
```

Do not persist `score_penalty` as semantic evidence. GitHub should deterministically map the structured evidence state to the existing risk component using canonical ranking policy, so score tuning does not require re-researching evidence.

## Route-scoped scoring integration

This is the main implementation-sensitive result of the RECON.

Current fixed-package ranking computes personal score once, then compares standalone vs package **purchase** score. That is insufficient for offer-specific quality because a bad package must not poison the standalone route.

Future integration should preserve one formula by evaluating the existing transparent components per available purchase route:

`route_total = common_personal_components + route_scoped_risk + route_purchase_score`

where `common_personal_components` remain Taste/wishlist/achievements/duration and `route_scoped_risk` is the same canonical risk component, with edition evidence for the exact offer added only to the affected route. The selected route is the higher result under the same formula; ties remain standalone. The selected route then exposes the one `personal_score`, one `purchase_score`, one `total_score`, and one `priority_rank` already used by the system.

This is not a second ranking system. It is the existing route-selection problem made quality-aware before the existing one final ranking pass.

## Control / regression examples

### A. GTA: The Trilogy – Definitive Edition-style App collection

- Member Taste: Vice City = strong, San Andreas = strong, GTA III = weak/moderate.
- Taste aggregation: package survives because at least one member qualifies; no averaging down.
- Edition evidence: exact Definitive Edition identity has severe, confirmed, current/durable edition-specific problems.
- Result: no Taste exclusion. Existing risk component receives up to `-12`, warning is prominent and explicitly edition-scoped, total score/rank falls materially.
- If newer evidence shows launch bugs fixed, those bug findings become historical and stop contributing a current technical penalty; separate durable remaster changes may still contribute if independently confirmed.

### B. Fixed `Sub` package with strong member but package-specific bad route

- Strong member game remains eligible.
- Standalone App route has no edition-quality problem.
- Fixed Sub route has severe supported package/edition problem.
- Package route gets `-10`; standalone does not.
- If standalone now has the higher transparent route total, it becomes the ranking-driving route. The package remains visible with the warning and is not erased from commercial data.

### C. Launch-bad, later-fixed remaster

- Old player reports describe severe crashes/performance issues.
- Recent evidence consistently says the technical issue was fixed/materially reduced.
- Old defect is `historical`; current technical penalty = 0.
- This prevents launch reputation from permanently suppressing a repaired edition.

### D. Anecdotal complaint

- One isolated complaint tied to the exact edition, no independent recurrence.
- Confirmation = `limited`, recurrence = `anecdotal`.
- No material score penalty; no `serious_risk` banner.

### E. Ambiguous release identity

- Current listing title contains `Anniversary/Definitive/Remastered`, but available evidence cannot reliably distinguish the original release from the current Steam edition.
- Identity = `ambiguous`.
- No negative edition finding is attached; score remains neutral until identity is resolved.

## Implementation boundaries / likely affected areas

Evidence-acquisition phase would likely affect only a new offer-quality contract/schema/cache plus bounded GitHub-prepared work/validation/persistence wiring. It should reuse the existing web-evidence principles and constrained semantic runtime rather than creating a second recurring scheduler. It must not change member Taste semantics or Taste Semantic Producer.

Ranking/UI integration phase would likely touch:

- `config/final_ranking_policy.json` — edition-quality-to-existing-risk mapping, still within `risk.max_penalty=12` and `strongest_only`;
- `scripts/priority_ranking.py` — route-scoped risk and same-formula route selection;
- `scripts/build_final_visual_payload.py` — attach validated offer-quality evidence before the single final ranking pass;
- `scripts/card_explanation_policy.py` — explicit grounded edition-quality provenance;
- `scripts/apply_fixed_package_purchase_options.py` — carry exact offer identity/evidence binding on package routes, without changing package economics;
- `web/app.js` — display the same canonical warning on the existing risk/package-offer surfaces only;
- focused deterministic validators/regressions.

Do not put edition quality into `taste_fit`, member-game dossier fit, commercial savings/price/history points, or a new hidden score.

## Task breakdown decision

**Split implementation into two bounded tasks.**

1. Evidence contract/acquisition/persistence first: exact offer/version identity, compact evidence schema, freshness, confirmation, deterministic validation, no ranking changes.
2. Ranking/warning integration only after evidence is canonical and testable: route-scoped existing risk component, one final score, visible warning, regression controls.

This split prevents scoring code from being designed around an unproven evidence shape and allows evidence identity/freshness to be validated independently.

## Validation / unresolved

Validated by bounded read-only inspection of the current canonical ranking policy, ownership contract, Taste dossier evidence/schema contracts, package commercial model, final scorer, refinement/risk flow, final visual producer, card explanation policy, UI warning/package surfaces, required prior reports, package-member task contract, routes and decisions.

No broad live research over products was required to establish the architecture. The GTA-style cases above are regression controls, not claims about the current live state of a particular store listing.

The package-member aggregation worker report was not present on `main` at the expected path during this recon; the required package-member behavior is taken from the explicit current task contract `WORKER_TASK_TASTE_PACKAGE_MEMBER_DOSSIER_AGGREGATION_01.md`. This does not block the edition-quality architecture because the separation rule itself is explicit and this task performs no integration.

Current main also does not expose a general post-`total_score` inclusion threshold in `FINAL-PRIORITY-RANKING-V2`; no such threshold is invented here.

## Recommended next step

Dispatch one bounded **CONTRACT / evidence-acquisition implementation task** for `offer_edition_quality`: define the exact offer/version identity and compact evidence contract/cache, reuse the existing bounded web-research semantics/runtime ownership, and prove GTA-style / fixed-Sub / fixed-after-launch / anecdotal / ambiguous-identity controls **without changing ranking yet**.

Final status: `complete`

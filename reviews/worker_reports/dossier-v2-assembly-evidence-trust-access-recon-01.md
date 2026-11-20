# Dossier V2 Assembly — evidence trust / external access RECON

**Task:** dossier-v2-assembly-evidence-trust-access-recon-01  
**Mode/outcome:** READ-ONLY diagnostic; one report-only DRAFT PR; no semantic retries, no source/config/contract changes, no writer/Actions, no canonical acceptance.  
**Checked:** 2026-11-17; repository: kentrap2011-hub/steam-kz-deals-2 only.  
**Source main HEAD at report branch creation:** `9f81a86876e657eda5091f8f981f052950f77a1b`.  
**Evidence sandbox branch:** `sandbox/dossier-notes-v2-fresh6-20261114-rerun1`, live HEAD read from GitHub ref: `c4232fb579fa88c4ed01afd5c45c57792c309984`.  
**Trial:** `dossier-notes-v2-fresh6-20261114-rerun1`; manifest: `data/control/dossier_notes_v2/manifests/dossier-notes-v2-fresh6-20261114-rerun1.json` (sandbox, not present on main; original manifest blob in assignment `752d5689c3f7d055c94c1844877337eea13ebd79`).  
**Authority:** an Assembly candidate and its receipt are *not* canonical accepted Dossier. Both groups remain subject to the existing atomic three-game GitHub writer.

## 1. Scope, exact artifact inventory and epistemic bounds

All six original Research candidate JSON files, Assembly JSON files and corresponding typed Research/Assembly receipts were retrieved from the **live exact sandbox ref**; source state was not inferred from an old QA document. Paths are deterministic:

- Research: `data/ai_inbox/dossier_notes_v2/{trial_id}/g{group_sequence:06d}/{appid}--{assignment_id}.json`
- Assembly: `data/ai_inbox/dossier_assembly_v2/{trial_id}/g{group_sequence:06d}/{appid}--{assignment_id}.json`
- Receipts: `data/control/dossier_notes_v2/receipts/{trial_id}/g{group_sequence:06d}/{appid}--{assignment_id}--{phase}.json` for `phase` = `research` or `assembly`.

The following table identifies exact group/item stems and full Git **blob SHAs** of (R) Research candidate, (A) Assembly candidate, (RR) Research receipt, (AR) Assembly receipt; prefix the stem with the trial path above. All receipts say `canonical_acceptance=false`.

| Game / exact artifact stem | R blob SHA | A blob SHA |
|---|---|---|
| Crown Trick — `g000001/1000010--batch-bdda4764cb82820cc71565e1` | `1737afbff09b18dfd5f7fefb4a0d6e2fd9d7f32d` | `3efefd646ca3c278e5d6ec2ea3bde40bb58602e9` |
| Orcs Must Die! — `g000001/102600--batch-c2cc7fa24858133403a944a3` | `2ed0600870442c76272b655688696add1fad19b2` | `27a412471ee8d200854656bf9a54c0eac55168b2` |
| Sniper Elite 5 — `g000001/1029690--batch-bcc93e385d885f2c6046d2ec` | `7cddb91dff2d5aa8f4ca0ebb75cf701006030c14` | `62d7ec644e7e11a419a4aa5d54baf3bf7698a852` |
| Borderlands 2 — `g000070/49520--batch-4701e24f9a6e0e539d40de24` | `3872ebebdb41c233a410f87a3cb0d2f70e717f46` | `1bb3c22ca7ad6d4316de1c0e186ff2d7b31be336` |
| Braid, Anniversary Edition — `g000070/499180--batch-cb814fef210f7aed5dede611` | `6a41e6405cf5e5e60dd4c7739e60ecba628f41ff` | `17de60189d0a88e8e677ed49b1ab40e770e42911` |
| Bulletstorm: Full Clip Edition — `g000070/501590--batch-26a14ae3e2cdab2a3dfe369a` | `1f66c942d21c7506b9b79ee22a1f7c4dc5540342` | `3b9688a44f9b05775076fe48bdf31b019410f14b` |

| AppID | RR blob SHA | AR blob SHA |
|---|---|---|
| 1000010 | `75d7937d36a54138dcd5d573ef69acb96feca65e` | `e355bf23aa0e740dc339e1ab13d0033285013656` |
| 102600 | `28e53f7686af16adcfc349066187c4458a232f64` | `f232b72126166f25f85036ee92a65f67529fe510` |
| 1029690 | `e7375b885139b9259930e4d80609008a833687f7` | `8e815ee98d68c251bdbc29eb3e71cf4f2695ddcb` |
| 49520 | `55dea0f04a6c228726e8280049fba086ef38f594` | `cb936b21011ba0dd99d10ba45cd3e0bc23f362dc` |
| 499180 | `5d477a691e0631161a46ed66d6be9349fe20153e` | `84af463b6842771b7768275cc28edf75006ee6ce` |
| 501590 | `bcd0f89f0a17778ea562dc2f8512a04553eaf682` | `1d80d1979618d5d189f05ed565bd0b84d8df4194` |

All six RR receipts show `safe_incomplete_research` with `transport_technically_verified=true`; **that is transport verification, not an independent semantic quality grade**. Four AR receipts show `assembly_missing_evidence` and `final_dossier=null`, while 49520/499180 show `strict_item_valid_pending_existing_atomic_group_ingest` for `assembled_candidate_ready`. Two successes in group 70 cannot overcome a different unresolved sibling in the existing atomic group. Old PR #456 QA originally calling 4 GOOD / 2 WEAK was disavowed (`KNOWN_WORKER_PITFALLS.md#PITFALL-009`), and is **not** used as evidence of Research quality or defects. Whether all reported Research sources really displayed their claimed content when the first worker visited them is outside this RECON; no new Research quality certification is being issued.

## 2. Four failures: what Research said vs what Assembly actually did

### 2.1 Crown Trick (1000010; group 1)

**Research:** described step-triggered combat, positioning/teleports, elemental/familiar combos and attractive presentation; reported player trade-offs about imbalance, randomness, repeated rooms, UI/curse clarity. Explicitly called save corruption **one individual report**, with occurrence and present-day state *unknown*; it did not claim a widespread current save defect or confirmed fix. Research source log lists a Steam review collection as `opened` and a third-party review as `search_result_only`, but this log is not independent browse proof.

**Assembly operations actually recorded:** `opened` exact Steam store product `https://store.steampowered.com/app/1000010/Crown_Trick/` for identity; `inspected_collection` English review collection `https://steamcommunity.com/app/1000010/reviews/?filterLanguage=english`; `search_result_only` Steam top-rated collection for an attributed 2024 save issue `https://steamcommunity.com/app/1000010/reviews/?browsefilter=toprated`; `unknown` direct Russian filter `https://steamcommunity.com/app/1000010/reviews/?filterLanguage=russian` (failure, **not** inspected).

**Refusal:** insufficient independently attributed neutral player coverage / Russian feedback retrieval; cannot state 2024 save defect as fixed, historical or currently widespread without dated later feedback. **Research contradiction found? None identified.** Research itself confined the defect to an unverified anecdote. The recent-dated-current check is mandatory **only if** a final `current`/`historical` technical assertion is made. It is not a reason to re-prove or resolve a hypothetical current save issue absent such an assertion. A narrowly described uncertain anecdote, or not promoting it into a material observation, avoids that invented claim. Russian search status and bound feedback still must satisfy the strict Russian gate, if the exact-product existence signal is established.

**Targeted resolution without full redo:** confirm exact-product player-authored Russian material through usable `search_result_observation` or inspected collection; bind source/feedback for durable gameplay strengths and weaknesses; leave save state explicitly uncertain or unasserted; assess actual coverage rather than inventing a current post-fix state.

### 2.2 Orcs Must Die! (102600; group 1)

**Research:** identified the **original 2011, single-player** action/tower-defense hybrid, praised personal fighting and trap combinations, noted different enemy pressure and limited trap variety/repetition. Its unknowns concern difficulty subjectivity and comparisons to sequels; **no affirmative Windows 11 compatibility or resolved-bug assertion**.

**Assembly operations:** `opened` exact original Steam storefront `https://store.steampowered.com/app/102600/Orcs_Must_Die`; `opened` player discussion `https://www.reddit.com/r/OrcsMustDie/comments/1qt3f62/my_feelings_about_orcs_must_die_1/`; `inspected_collection` English Steam reviews `https://steamcommunity.com/app/102600/reviews/`; `search_result_only` Russian-language store `https://store.steampowered.com/app/102600/Orcs_Must_Die?l=russian` showing Russian activity and Windows workaround fragments, **not** concrete Russian review read; `unknown` filtered Russian community `https://steamcommunity.com/app/102600/reviews/?filterLanguage=russian`.

**Refusal:** established Russian activity but no actually consumed Russian player record; could not classify modern Windows compatibility as already fixed/current from a verified dated post-change player. **Research contradiction? None.** No need for a positive Windows 11 resolution claim; uncertainty/omission protects validity. The Russian existence→usable-item gate **is real**, but not Steam-only: a separate Russian player-feedback surface is valid.

**New independent retrieval in this RECON:** `https://stopgame.ru/game/orcs_must_die/reviews` opened and displayed individual Russian-language first-person reviews about original game combat/traps, solo feel, repetition and tone. This is a materially different **player review** surface rather than professional context or aggregate metadata. Exact 2011-game identity must be bound when used; publication year may be null where page only says day/month. This concrete workaround was not attempted in the original Assembly operations.

### 2.3 Sniper Elite 5 (1029690; group 1)

**Research:** praised sniping, level approach choices, weapon customization, coop and Axis Invasion; acknowledged **opposed opinions** versus Sniper Elite 4 about corridor restrictions, mobility, repetitive missions and AI. Its unknowns explicitly do not universalize individual AI/control complaints into a current technical failure.

**Assembly operations:** `opened` exact Steam product `https://store.steampowered.com/app/1029690/`; `opened` exact player discussion `https://steamcommunity.com/app/1029690/discussions/0/594024287509165179/`; `inspected_collection` English review cards `https://steamcommunity.com/app/1029690/reviews/` with contested AI and occasional PC stutter; `search_result_only` Russian store aggregate `https://store.steampowered.com/app/1029690/Sniper_Elite_5?l=russian`; `unknown` Russian filter `https://steamcommunity.com/app/1029690/reviews/?filterLanguage=russian`.

**Refusal:** no usable Russian player record although population exists; no recent dated feedback validating whether individual stutter/technical problem is an actual **current** technical state. **Research contradiction?** Conflicting player preferences existed *inside Research already*, not contradiction between Research and Assembly. The required response is neutral competing feedback with appropriate scope, not wholesale Research reassessment. Do not label AI criticism universal current technical bug without date.

**New independent retrieval:** `https://stopgame.ru/game/sniper_elite_5/reviews` opened, revealing multiple Russian-language first-person game reviews about levels, secondary objectives, AI and coop/invasion; one explicitly states a PS5 playthrough, therefore **not proof of Windows/PC performance**. This is usable for durable cross-platform game-experience observations if bound appropriately, not proof of a PC stutter fix. Precise publication year null when not rendered. Steam Russian store **search results** for exact AppID also exposed concrete player-authored Russian snippets (search-result observation, not inspected Steam item).

### 2.4 Bulletstorm: Full Clip Edition (501590; group 70)

**Research:** described 2017 **Full Clip re-release**, Skillshots, whip/kicks/environment combos, speedy linear campaign and polarizing humor; mixed response to repetition and anecdotal crashes/collisions/skillshot recognition. Research explicitly said bug frequency, platform and patch/current status **unknown**.

**Assembly operations:** Steam store identity on `https://store.steampowered.com/app/501590/Bulletstorm/?l=russian` was `search_result_only`; direct store access led to `https://store.steampowered.com/agecheck/app/501590/?l=russian`, which was **opened as an age verification page only**, not reviewed game product text; English Steam reviews `https://steamcommunity.com/app/501590/reviews/` `inspected_collection`; top-rated reviews `https://steamcommunity.com/app/501590/reviews/?browsefilter=toprated` `search_result_only`; localized store Russian **aggregate** activity `search_result_only`; `https://steamcommunity.com/app/501590/reviews/?filterLanguage=russian` `unknown`/blocked.

**Refusal:** credible Russian player-review population, no usable Russian review; age-gated official product route, no established current localization/technical state. **Research contradiction? None identified.** Technical anecdotes were already labeled uncertain by Research; a dated fix is unnecessary unless specifically asserted. Exact *Full Clip Edition* identity is crucial: original 2011 Bulletstorm review pages alone cannot be rebound to this edition.

**New independent retrieval:** localized exact AppID Steam store **search-result representations** revealed concrete player-authored Russian Full Clip sentiments (the opened storefront is not equivalent to reading those search snippets). `https://steamcommunity.com/sharedfiles/filedetails/?id=3402192357` genuinely **opened** and contains Russian comments about a *fan-dub guide* and launch/friction experience for the Full Clip edition. Caution: the fan translation's existence and comments do **not** prove default game's Russian localization, general crash prevalence, nor a recent fixed state. Steam store may display accessible indexed product metadata on one normalized URL while `agecheck` remains age only; these are distinct representations, not a general reliable age-gate bypass.

### Cross-case classification

- **(i) Source-level:** `filterLanguage=russian` fails for four exact apps in the tested web reader; one exact store route is age gated. Not a verified proof Steam has no reviews or that *all tools* have identical restrictions.
- **(ii) Overbroad re-evaluation:** Assembly's repeated demand to independently establish post-change/current state for **unasserted** technical anecdotes exceeds the minimum needed if they remain uncertain or omitted. No item has a documented factual Research-vs-Assembly content contradiction. Disputed game opinions are not a contradiction of Research if Research already reported both.
- **(iii) Actual strict fields:** exact AppID/edition/year, bounded individual player-feedback records and source bindings, Russian `attempt`, correct languages, 12-dimension coverage classification, source mix, dates where known, status for any current/fixed technical claim.
- **(iv) Real critical gap:** where Russian exact-game player-review activity exists but no concrete Russian item has been observed and bound, strict final completion is impossible under current contract. This is independent of whether Research's neutral semantic conclusions are sensible.

No claim is made that retrospectively discovered material is sufficient to validate a complete immutable final dossier; the earlier typed terminal outcomes are not altered.

## 3. Current contract and validator: required vs nonrequired work

**Too-broad instructions (precise points):**

1. `config/dossier_notes_v2_batch_assembly_manual_one_shot_prompt.md`: “Research Notes are unverified leads. Independently investigate exact product/edition, current dated state versus historical role, player experiences, source/access conflicts and feedback evidence.” The all-domain “independently investigate” wording induces re-assessment even absent a concrete contradiction.
2. `config/dossier_two_stage_autonomous_assembly_v2_worker_prompt.md`: “Research Notes are leads, not accepted facts. Independently search public sources and verify ... positive/negative/technical/temporal findings, including sources not named by Research”; `mandatory pre-submit` “Independently revisit attributable ... player feedback”, and “Search snippets are not observed reviews”. The last sentence is correct only insofar as a snippet is **not an opened page**; it conflicts with a blanket refusal to use genuinely player-authored **search-result-observed** content. This prompt is original18 guidance only for batch launcher, so its future instruction clarification must preserve its authority/scope boundary.
3. `config/dossier_research_notes_v2_contract.json#assembly` already grants `independent_source_discovery=true` and `can_correct_research_facts=true`, but explicitly `mandatory_exact_source_revisit=false`. Thus there is **no machine contract forcing a fresh re-read of every Research source**; broad prompt semantics should be narrowed rather than rewriting strict validation.
4. `config/taste_steam_review_dossier_web_evidence_contract.json` expressly allows `inspected_collection_item` and `search_result_observation` with concrete player-authored content and exact-product source binding. Target-page open success, individual item URLs, author identities and counts of evidence URLs are **not** mandatory; search query or aggregate sentiment alone are not evidence.
5. `config/taste_steam_review_dossier_web_evidence_contract.json#recency` and `scripts/taste_steam_review_dossier_strict.py` `_validate_observations`: **`current`** requires actual supporting recent dated `current_state` feedback; **`historical`** additionally requires historical evidence and recent dated current-state check; **`uncertain`** remains an acceptable status for unresolved anecdotes, **`durable`** for stable gameplay traits with durable-trait support. `publication_date=null` is allowed, but **not** treated as current.
6. `scripts/taste_steam_review_dossier_strict.py` ``_validate_feedback_record`/`_validate_observations`/`_validate_coverage_sufficiency`/`validate_dossier_strict` validate: source/feedback join identities, allowed acquisition modes, exact AppID/title/edition binding, observed record counts and language projection, source mix, Russian gate, and 12 classified (not necessarily 12 covered) dimensions. ``1060–1112` reject both Russian `existence_established_*_unresolved` states for a final dossier. The validator does **not** ingest an epistemic verdict saying every neutral Research observation must be independently reinvestigated.
7. `config/dossier_research_notes_v2_contract.json#research_handoff` permits sparse notes, zero research sources, no Research semantic acceptance, and optional `source_log`. Research notes/receipts are therefore **neither guaranteed quality nor browse proof**. Requiring Research to archive screenshots, browse logs, usernames, review copies or a URL quota would be an unauthorized additional task and contradict compact privacy/transport design.

**Why each minimal necessary check exists:**

- Exact edition/AppID/source check prevents accidentally attributing original Bulletstorm/Orcs 2, base Braid, or Sniper Elite 4's reviews to the target product.
- Real individually observed feedback + safe provenance is required **for the final strict schema** so the dossier does not invent number of independent experiences, language, recurrence, source identity or the factual basis of an observation. It does **not** imply challenging every neutral Research summary.
- Russian good-faith attempt is independently required when player activity exists and can be satisfied off Steam, or by concrete search-result observation, with exact edition binding.
- Recent dated **current-state** check is mandatory **only to assert current/fixed/historical technical status**; it is not mandatory to demonstrate a fix to a defect Research only named as a past/uncertain anecdote.
- Actual substantive contradiction (wrong product, conflicting factual evidence, unsupported source, material technical claim, or other established risk) triggers **only** specific targeted Research re-review, not complete replay.

## 4. Controlled successes: what sufficed (not accepted by writer)

**Borderlands 2 (49520):** Assembly confirmed exact base product/2012 identity; inspected actual dated Russian Steam review cards at `https://steamcommunity.com/app/49520/reviews/?browsefilter=toprated&l=russian&p=1`, separately inspected English cards and read first-person Reddit UVHM/slag discussion. Its final dossier uses `russian_attempt=found_and_used` with bound Russian `inspected_collection_item` records, gameplay `durable` claims and an anecdotal network issue `uncertain` with undated publication `null`. It did **not** require proof that every co-op connection issue was fixed or every Research source was separately proven again. Assembly outcome `assembled_candidate_ready`, receipt `strict_item_valid_pending_existing_atomic_group_ingest`, **not canonical acceptance**.

**Braid, Anniversary Edition (499180):** Assembly verified exact remaster AppID 499180 (not original 26800), inspected exact-AppID English Steam user cards, and used concrete first-person Reddit discovery snippets with `search_result_only` as **search-result observations**, not falsely “opened” target pages. No reliable Russian **2024 edition** review population signal established by its scoped attempt: `russian_attempt=searched_no_existence_signal`. Claims concern durable puzzle content and differing perceptions of edition value; multiplayer, progression and technical categories may be classified `not_material_or_not_applicable`. No invented current technical claims or arbitrary evidence counts. Outcome is item-ready **pending atomic writer only**.

Together the two controls prove practical **compact supported coverage** can be enough; they do not prove all four failures could have passed without new Russian item evidence. Group 70 still includes failed Bulletstorm; separate successful items do not become accepted canon automatically.

## 5. Independent external web-route access RECON (2026-11-17)

Access categories below describe **this diagnostic reader's actual retrieval**, not original Research worker access and not universal Steam behavior. A page now returned from an indexed/cached representation is an inspected **representation**, not proof of up-to-date game state.

| Exact URL / route | Observed access | What it establishes / limitation |
|---|---|---|
| `https://steamcommunity.com/app/1000010/reviews/?filterLanguage=russian` | **inaccessible in this web reader** (URL not accessible) | No inspected filtered Crown card |
| `https://steamcommunity.com/app/102600/reviews/?filterLanguage=russian` | **inaccessible** | No inspected Orcs filtered card |
| `https://steamcommunity.com/app/1029690/reviews/?filterLanguage=russian` | **inaccessible** | No inspected Sniper filtered card |
| `https://steamcommunity.com/app/501590/reviews/?filterLanguage=russian` | **inaccessible** | No inspected Bulletstorm filtered card |
| Same four exact-app routes with `?browsefilter=toprated&l=russian&p=1` | **inaccessible** | Parameter substitution alone not a demonstrated universal fix |
| `https://steamcommunity.com/app/49520/reviews/?browsefilter=toprated&l=russian&p=1` | **opened/inspected concrete Russian player cards** | Control: Steam Community review read works for at least one different AppID; cannot globalize failure |
| `https://stopgame.ru/game/orcs_must_die/reviews` | **opened/inspected concrete Russian user reviews** | Confirmed independent off-Steam player-feedback route for the original 2011 product; not editorial alone |
| `https://stopgame.ru/game/sniper_elite_5/reviews` | **opened/inspected concrete Russian user reviews** | Confirmed alternative player opinions, some explicitly PS5, not a PC performance test |
| `https://stopgame.ru/game/crown_trick/reviews` | **inaccessible** | Does not establish absence of Russian reviews |
| `https://stopgame.ru/game/bulletstorm_full_clip_edition/reviews` | **inaccessible** | Does not establish absence or justify substituting original 2011 game |
| `https://store.steampowered.com/app/1000010/Crown_Trick/?cc=us&l=russian` and exact AppID indexed curator variant | **search-result representation with concrete player-authored Russian review content**, target opened page only metadata | Potential `search_result_observation`, **not** `opened` review, exact AppID must be checked; dates null unless actually shown |
| `https://store.steampowered.com/app/1029690/Sniper_Elite_5?l=russian` | **search-result representation with concrete first-person Russian snippets**, opened metadata **aggregate only** | Candidate `search_result_observation`; source page open is not equal to card read |
| `https://store.steampowered.com/app/501590/Bulletstorm/?l=russian` and indexed exact AppID store variants | **search-result concrete Russian reviews**, opened store variant **aggregate metadata only** | Potential actual player authored search evidence on exact edition; Russian-language review counts alone NOT feedback |
| `https://store.steampowered.com/agecheck/app/501590/?l=russian` | **opened agecheck only** | No game page feedback viewed; no claim to bypass age check |
| `https://steamcommunity.com/sharedfiles/filedetails/?id=3402192357` | **opened guide plus Russian discussion comments** | Full Clip-specific fan voice pack and individual commentary/launch observations; not proof of built-in dub, fixed patch or general crash incidence |
| `https://store.steampowered.com/appreviews/501590?json=1&filter=all&language=russian&num_per_page=20` | **inaccessible in this web reader** | No direct appreviews JSON evidence; do not attribute to absent Steam reviews |

**Reproducible workaround:** after a blocked Steam Community language-filter page, do **not** retry a family of equivalent parameters indefinitely. Search exact AppID plus exact edition title and Russian player-review phrasing; inspect a concrete player-review collection on a materially distinct community (confirmed StopGame examples), and/or a search result with actually displayed original player-authored opinion and exact-product binding. Serialize `inspected_collection_item` or `search_result_observation` **truthfully**, with safe parent source, acquisition mode, language and factual date/null; no fabricated item URL or browse-proof from Research. Metadata-only `?l=russian` remains merely an existence signal, not `found_and_used`. Some real access failures remain source/tool specific, not resolved by a universal Steam age-filter patch.

## 6. Trust-by-default model and single bounded next recommendation

**Model (future prompt wording, not a policy change applied by this report):**

1. **Default:** accept neutral Research's meaningful qualitative observations, already-declared uncertainties and balanced differences of opinion as the **semantic working base**. A technical receipt attests transport only; this is a procedure for avoiding unjustified suspicion, not a certification of correctness.
2. **Challenge threshold:** reopen just the implicated Research fact when there is a **specific observed** contradiction, wrong AppID/edition/source, explicit claim contradicting accessible first-hand feedback, material unsupported temporal assertion, or applicable contract/schema/identity obstacle. State that reason, the contested claim and a small targeted lookup. “Could theoretically be stale” is **not** a reason.
3. **Final artifact gate independent of Research semantic trust:** identify actual usable individual player feedback to support final `provenance.sources` / `player_feedback_records` / `observations` / `conflicts` with exact identity, source language and date/null, Russian attempt and coverage. This supports schema and auditability without evaluating Research from scratch or requiring Research's web log. Use `inspected_collection_item` / `search_result_observation` when warranted.
4. **Technical scope:** do **not** promote an old/isolated complaint into `current` or `historical/fixed` without a recent dated supporting current-state record. If no such record is available, retain truthful `uncertain` with bound anecdotal evidence, or omit a nonmaterial technical conclusion and mark coverage appropriately. Do not invent a resolved or universal failure.
5. **Source access:** react to a failed Steam language/age route with a materially distinct player-feedback surface or a genuinely content-bearing search-result representation. Stop on a real unresolved critical Russian item gate, not on an assertion that one URL's filter failed everywhere.

**One bounded proposal to the Director (requires separate approval):** **CONTRACT/wording reconciliation followed by IMPLEMENT of only the two Assembly prompt files** named in `3, replacing blanket “independently investigate/revisit all Research” language with the five-step trust/strict-evidence distinction above; explicitly document supported search-result/collection acquisition modes and alternative off-Steam Russian retrieval. Keep `config/dossier_research_notes_v2_contract.json` `mandatory_exact_source_revisit=false` unchanged unless Director finds a *concrete* conflicting canonical clause during approval. Keep **all** final strict evidence, Russian gate, source language, current/fixed dating, identities, existing writer/schema/validator and group atomicity unchanged. No new worker, scheduler, retry, queue, quota, or acceptance privilege.

**Expected effect:** fewer semantic dead ends and unnecessary attempts to “prove a fix” for uncertain anecdotes, lower full Research duplication, earlier use of real Russian off-Steam/search-result player feedback, better alignment between prompt and already-permissive strict evidence modes. **Risks:** insufficient first-hand provenance can still correctly block strict final; spurious/snippet-only non-player content can be misclassified unless the concrete player-authored + exact product check is explicit; blind trust could hide an actual Research mistake if specific contradictions are overlooked. Mitigate by preserving contradiction triggers and final validation, and by testing future prompt wording offline with these six frozen fixtures **only after separate permission**, not by rerunning them here.

**Preflight:** GitHub remains owner of manifest/assignment/order/retry/strict validation/atomic writer under `config/execution_ownership_contract.json`. Assembly remains bounded semantic evidence producer under the inactive V2 contracts. The proposal changes only guidance inside that role, not GitHub/ChatGPT ownership or a new recurring stage. No actual contract/implementation change, semantic rerun, writer invocation, sandbox write, production or merge has been authorized by this RECON.

**Follow-up route candidate (not modified due to task read-only scope):** add this exact sandbox paired-artifact lookup and Russian retrieval surface distinction to the relevant Dossier section in `PROJECT_ROUTES.md` only as part of a separately authorized bounded documentation change.

## 7. Termination and acceptance

- **Diagnostic result:** Complete six-item comparison against live immutable sandbox plus bounded independent external web access testing. Four failures split into real source-level Russian evidence/provenance constraints **and** unnecessary full independent Research reassessment for unasserted current technical facts; all four Research conclusions were treated as ungraded, not proven flawed or GOOD.
- **Actual writes:** this **one report file in one report-only DRAFT PR** to main. No project runtime, prompt, contract, source, Board, registry, queue, manifest, receipt or historical candidate changed.
- **No hidden claim:** nothing in this report converts `assembly_missing_evidence` to `assembled_candidate_ready` or establishes accepted Dossier; neither successful control equals group or canonical acceptance.

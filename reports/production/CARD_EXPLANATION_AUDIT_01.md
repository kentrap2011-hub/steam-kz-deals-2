# CARD_EXPLANATION_AUDIT_01

Status: **AUDIT COMPLETE — CURRENT EXPLANATIONS FAIL THE CONTENT QUALITY GATE**  
Mode: **report-only / read-only reconnaissance**  
Runtime, schemas, UI, Taste data, queues, `CURRENT_TASK.md` and production artifacts were **not modified**.

## 1. Scope and source snapshot

The bounded audit covers the current visible explanation fields for the first 30 ranked entries from the canonical visual review route.

Primary audit source:

- repository: `kentrap2011-hub/steam-kz-deals-2`
- branch: `main`
- fixed audit source commit: `9a7d398622c666bc612979f51e264f10977588c3`
- canonical visible payload: `data/production/visual/current.json`
- canonical review sample: `data/production/visual/ranking_review.jsonl`
- sample: ranks 1–30 from that review artifact

`main` moved while the audit was running. Before report write the findings were revalidated against:

- `main` write-base commit: `e3db8ac796f3b39f2c17ac282ba7419d23d5d9a3`

The current payload at the write base still carries the same bound producer contract and the same two failure modes: generic/fallback positive text and non-empty `risks[]` for `risk_status.has_described_risk=false`.

Important artifact versions observed in the canonical payload:

- top-level visual artifact `schema_version`: `3`
- embedded `production_contract.schema_version`: `7`
- current payload final producer blob: `9f20022072772c839c2656c1e5846cf58edaf833`
- current payload visual builder blob: `7c31e8f756e775857a0cce7817b09ce1eee9592d`
- current payload refinement helper blob: `757caca50fcfd167bd4eeded97f69b1b4d391eaa`
- canonical Taste profile blob: `c478cda9bb7a9b024a30ca188dce4b98a2de24ea`
- Taste model: `taste-v3`

A standalone `config/visual_payload.schema.json` was not present on the fixed audit source. Therefore this report treats the actual canonical artifact shape plus its embedded production contract as authoritative for the current output. Any documentation still pointing at removed/renamed schema or audit paths should be treated as route/schema drift, not as a reason to audit stale artifacts.

## 2. Hard-gate result

The current explanation layer fails the requested quality gate.

1. **`Игра прошла строгий вкусовой отбор...` is a placeholder, not an explanation.** It appears in 11 of the sampled 30 cards.
2. **Absence of a confirmed risk is currently rendered as if it were a negative bullet.** In 13 of 30 cards, `risk_codes=[]` and `risk_status.has_described_risk=false`, yet `risks[]` still contains a sentence. With the currently accepted evidence those 13 cards must render **no negative block**.
3. **The remaining positive text is still template-level, not game-specific.** Under a strict rubric requiring a concrete fact/system/situation from the particular game plus the relevant personal taste link, 0 of 30 cards currently has a fully game-specific positive rationale.
4. **Price, discount and rank are not being used as the positive taste explanation in this sample.** This hard gate currently passes.
5. **A score/rank can corroborate fit but cannot substitute for the rationale.** The current explanations are not literal score restatements, but the fallback effectively says only that upstream filtering liked the game; that is still insufficient.
6. **Risks must not be invented.** A non-empty heuristic `risk_code` is useful support, but by itself is not proof that a player-facing complaint is justified. The future producer needs source provenance/grounding before wording a specific minus.

## 3. Exact implementation map

### 3.1 Positive explanation

Visible canonical field:

- `data/production/visual/current.json -> games[].why_fit[]`

Audit mirror:

- `data/production/visual/ranking_review.jsonl -> strengths[]`

Current bound producer path:

1. bound visual builder `7c31e8f756e775857a0cce7817b09ce1eee9592d`
2. `scripts/build_visual_feed_v2.py::build_feed()` gathers positive evidence / tags / Taste factors and builds the reasons list
3. `scripts/build_visual_feed_v2.py::reason_ru()` maps evidence by keyword to a small set of fixed Russian templates
4. `reason_ru()` falls back to the exact placeholder:

> Игра прошла строгий вкусовой отбор, но конкретное русское объяснение этого совпадения ещё нужно доработать после утверждения оформления.

This is the primary positive-text defect. `reason_ru()` is translating/classifying broad evidence into generic prose instead of composing a concrete `game fact -> personal preference -> relevance` explanation.

### 3.2 Negative explanation

Visible canonical fields:

- `games[].risks[]`
- support: `games[].risk_codes[]`
- support: `games[].risk_status`

Audit mirror:

- `weaknesses_risks[]`
- `risk_codes[]`

There are two risk-generation stages, and the final stage wins:

1. bound visual builder `7c31e8f...` has `derive_risks()` and can already emit a no-risk sentence;
2. bound final producer `9f200220... -> scripts/build_final_visual_payload.py::refine_games_from_signals()` overwrites the visible risks;
3. it calls bound refinement helper `757caca... -> scripts/refine_visual_ranking.py::structural_risks()`;
4. it then calls `scripts/refine_visual_ranking.py::risk_summary()`;
5. when no risk codes exist, `risk_summary()` returns the exact final filler currently shown:

> По доступным подтверждённым данным конкретный персональный минус не выявлен; отсутствие найденного риска не считается доказательством идеального совпадения.

The canonical artifact simultaneously says:

- `risk_codes=[]`
- `risk_status.code="no_confirmed_risk"`
- `risk_status.has_described_risk=false`
- but `risks[]` is non-empty

That is an internal semantic inconsistency. `has_described_risk=false` should lead to an empty player-facing risk list, not a synthetic negative bullet.

### 3.3 Current producer drift

The payload embeds exact producer blob SHAs. Those bound SHAs must be used to explain the current artifact. During the audit, HEAD versions of at least the visual/final producer had already moved relative to the blobs bound into the current payload. Therefore a later implementation task must first decide whether it is changing:

- the producer version actually bound into the current production artifact, or
- a newer HEAD producer that has not yet produced the canonical artifact.

Do not infer current behavior solely from HEAD source when the payload contract provides exact producer blobs.

## 4. Classification rubric

Positive classes:

- **P-A — game-specific grounded:** concrete title-specific system/fact/situation + explicit personal preference link. Desired class.
- **P-B — typed generic:** broadly supported mechanic/category, but wording could describe many games.
- **P-C — placeholder/fallback:** states that the game passed Taste selection without explaining why.
- **P-D — redundant:** two bullets on the same card communicate substantially the same idea.

Negative classes:

- **N-0 — no accepted negative:** no current accepted risk evidence; negative block must be omitted.
- **N-H — heuristic risk:** a structural risk code exists, but player-facing text remains heuristic until grounded to a concrete source/evidence clause.
- **N-G — grounded negative:** desired state: a concrete game fact/risk plus the relevant personal sensitivity and provenance.

Current top-30 contains **0 P-A**. It contains P-B, P-C and several P-D cases. Current negative text contains N-0 filler and N-H templates; the current card output does not expose enough provenance to certify those N-H sentences as N-G.

## 5. Template dictionary used by the sample

The table in section 6 uses IDs below so every sampled card can be mapped to its exact current visible text without duplicating dozens of long sentences.

### Positive templates

- `P-FALLBACK` — `Игра прошла строгий вкусовой отбор, но конкретное русское объяснение этого совпадения ещё нужно доработать после утверждения оформления.`
- `P-CHOICE` — `Решения заметно влияют на происходящее, а тебе обычно интереснее игры, где действия меняют ситуацию, а не служат только декорацией.`
- `P-CHOICE2` — `Здесь важны решения и их последствия, поэтому ситуации могут развиваться по-разному, а не идти по полностью однообразному сценарию.`
- `P-PROGRESS` — `Есть заметное развитие возможностей персонажа с понятным игровым эффектом — это совпадает с твоей любовью к ясному и полезному прогрессу.`
- `P-MOVE` — `Передвижение здесь — важная часть самого удовольствия от игры, а тебе особенно нравятся игры, где движение и контроль персонажа интересны сами по себе.`
- `P-MOVE2` — `Заметная часть игры построена вокруг активного передвижения, а выразительное движение для тебя само по себе является плюсом.`
- `P-ACTIVE` — `В игре заметную роль играет непосредственное управление и действие, а не только чтение или наблюдение — это соответствует твоему предпочтению активного геймплея.`
- `P-TACTICAL` — `Игра регулярно ставит понятные тактические задачи, где можно выбирать подход и улучшать исполнение — это хорошо совпадает с твоей любовью к анализу ситуации и освоению игровых систем.`
- `P-VARIETY` — `Игра регулярно меняет ситуации или способ взаимодействия, поэтому меньше риска застрять в одном повторяющемся цикле — это сильный плюс для твоего профиля.`
- `P-INVEST` — `В центре есть конкретное расследование и понятный вопрос, на который нужно найти ответ — тебе такие загадки лучше заходят, когда направление поиска остаётся ясным.`
- `P-INVEST2` — `Основной игровой интерес связан с расследованием и поиском ответов — это хорошо совпадает с твоей любовью к направленным загадкам.`
- `P-MYSTERY` — `В игре есть конкретная тайна, которая даёт исследованию и продвижению понятный смысл — это хорошо совпадает с твоей любовью к направленным загадкам.`
- `P-EXPLORE` — `Исследование здесь связано с открытиями и продвижением, а тебе важнее плотность причин исследовать, чем просто большой мир.`
- `P-PUZZLE` — `Головоломки дают конкретные задачи и понятные точки прогресса, что обычно лучше соответствует твоему вкусу, чем бесцельное исследование.`
- `P-GOAL` — `У игровых задач есть понятная общая цель, поэтому исследование и отдельные механики не ощущаются бесцельными.`

### Negative templates

- `R-NONE` — `По доступным подтверждённым данным конкретный персональный минус не выявлен; отсутствие найденного риска не считается доказательством идеального совпадения.`
- `R-REPEAT` — `Есть риск повторения одних и тех же действий без достаточного изменения условий или развития — именно такой повтор для тебя быстро становится утомительным.`
- `R-DIR-OPEN` — `Открытая структура может давать слишком мало направления; тебе такие миры лучше заходят, когда постоянно понятно, зачем исследовать следующую точку.`
- `R-DIR` — `Есть риск недостатка ясного направления: тебе заметно хуже заходят игры, когда непонятно, куда идти, что делать и ради чего развиваться.`
- `R-PLAT` — `Если сложные участки платформинга начнут требовать слишком много одинаковых повторов, это может утомлять.`
- `R-MANAGE` — `Есть риск, что управление ресурсами или повторяющаяся хозяйственная рутина займут слишком большую часть игры.`
- `R-DIFF` — `Сложность может требовать много повторных попыток; для тебя это хорошо работает только когда ошибки понятны, а освоение ощущается содержательным.`
- `R-PUZZLE` — `Если головоломки станут однотипными или надолго остановят темп, сильная сторона игры может превратиться в минус.`
- `R-READ` — `Расследование может включать много чтения и сопоставления улик; важно, чтобы это не вытесняло активное взаимодействие с игрой.`
- `R-EXPLORE` — `Исследование может оказаться слишком самоцельным; тебе оно лучше подходит, когда есть ясный вектор и плотные открытия.`
- `R-OLD` — `Возраст игры может ощущаться в управлении или интерфейсе, хотя сам по себе старый год выпуска не делает игру плохой.`

## 6. Bounded top-30 audit

Input shorthand for the final column:

- `I+`: current deterministic positive source families — `positive_evidence`, `tags`, `short_description`, `summary`, `taste_factors`, profile evidence if explicitly available.
- `I-`: current deterministic negative source families — `negative_evidence`, `summary`/tags, `risk_codes`, practical facts only when they are actually relevant to the personal preference.
- `omit -`: current accepted risk evidence is empty; do not manufacture a negative bullet.

All 30 sampled review rows expose `direct_user_evidence_level="none"`; therefore current personalization here is profile-level rather than direct same-title user feedback.

| # | Game | Current `why_fit` | + class | Current risk | - class | Real inputs for a better explanation |
|---:|---|---|---|---|---|---|
| 1 | Fable Anniversary | P-CHOICE; P-PROGRESS | P-B | R-DIR-OPEN (`directionlessness`) | N-H | I+; I- + concrete directionality evidence |
| 2 | Psychonauts 2 | P-MOVE; P-MOVE2 | P-B + P-D | R-PLAT (`platform_repetition`) | N-H | I+ summary can name platforming/psychic traversal; I- must ground repetition |
| 3 | Uncle Chop's Rocket Shop | P-FALLBACK | P-C | R-NONE, `risk_codes=[]` | N-0 | I+ has a concrete repair/roguelite-loop summary; current `-` must be omitted unless a real loop-risk is explicitly derived |
| 4 | Terminator: Resistance | P-CHOICE2 | P-B | R-REPEAT; R-DIR-OPEN | N-H | I+; I- needs concrete source clauses for repetition/open structure |
| 5 | Darkest Dungeon® | P-FALLBACK; P-CHOICE | P-C + P-B | R-REPEAT | N-H | I+ has detailed stress/party/turn-based summary; I- should cite the actual repeated-loop evidence |
| 6 | Project Hospital | P-VARIETY; P-FALLBACK | P-B + P-C | R-MANAGE; R-DIFF | N-H | I+ has hospital design/doctor/manager facts; I- can be tied to management load only if profile sensitivity is explicit |
| 7 | Teenage Mutant Ninja Turtles: Splintered Fate | P-ACTIVE | P-B | R-REPEAT | N-H | I+ can name roguelike combat/techniques/co-op; I- must ground run repetition |
| 8 | Suit for Hire | P-TACTICAL; P-ACTIVE | P-B | R-NONE, `risk_codes=[]` | N-0 | I+ can name gunplay + martial-arts combination; omit - |
| 9 | Journey to Incrementalia | P-FALLBACK; P-PROGRESS | P-C + P-B | R-REPEAT | N-H | I+ from Taste evidence/short description needed because visible summary is placeholder; I- needs real loop evidence |
| 10 | The Last Soldier of the Ming Dynasty | P-ACTIVE | P-B | R-NONE, `risk_codes=[]` | N-0 | I+ from Taste evidence/short description; omit - |
| 11 | Plague Inc: Evolved | P-FALLBACK | P-C | R-NONE, `risk_codes=[]` | N-0 | I+ has concrete pathogen-evolution/adaptation summary; omit current - unless a specific evidence-backed risk is derived |
| 12 | Decarnation | P-PUZZLE | P-B | R-PUZZLE (`puzzle_pacing`) | N-H | I+ / I- from upstream evidence because visible summary is placeholder |
| 13 | The Black Grimoire: Cursebreaker | P-VARIETY; P-GOAL | P-B | R-NONE, `risk_codes=[]` | N-0 | I+ from Taste evidence/short description; omit - |
| 14 | Orbo's Odyssey | P-MOVE | P-B | R-PLAT (`platform_repetition`) | N-H | I+ from Taste evidence/short description; I- needs concrete platforming repetition evidence |
| 15 | Doors: Paradox | P-INVEST; P-MYSTERY | P-B + overlap | R-PUZZLE; R-READ | N-H | I+ can name room-escape dioramas/items/clues; I- must distinguish puzzle pacing from reading instead of generic speculation |
| 16 | ENDLESS Space™ - Definitive Edition | P-FALLBACK; P-CHOICE | P-C + P-B | R-NONE, `risk_codes=[]` | N-0 | I+ has concrete civilization/colonization/control summary; omit - |
| 17 | The Chrono Jotter | P-INVEST; P-INVEST2 | P-B + P-D | R-READ (`reading_investigation`) | N-H | I+ from Taste evidence/short description; I- needs actual reading/dialogue evidence |
| 18 | ENDLESS Space™ 2 | P-PROGRESS; P-FALLBACK | P-B + P-C | R-DIR (`directionlessness`) | N-H | I+ has concrete civilization/4X summary; I- needs a real lack-of-direction basis, not genre alone |
| 19 | RUNNING WITH RIFLES | P-TACTICAL; P-PROGRESS | P-B | R-DIR-OPEN (`directionlessness`) | N-H | I+ can name top-down tactical shooter/open world/RPG mechanics; I- must ground directionality |
| 20 | 港詭實錄ParanormalHK | P-FALLBACK | P-C | R-NONE, `risk_codes=[]` | N-0 | I+ from Taste evidence/short description; omit - |
| 21 | Anodyne | P-EXPLORE | P-B | R-EXPLORE (`exploration_direction`) | N-H | I+ / I- from upstream evidence because visible summary is placeholder |
| 22 | The Escape: Together | P-EXPLORE | P-B | R-NONE, `risk_codes=[]` | N-0 | I+ from upstream evidence; omit - |
| 23 | Marfusha:Sentinel Girls | P-FALLBACK; P-PROGRESS | P-C + P-B | R-REPEAT | N-H | I+ from upstream evidence; I- requires concrete repetitive-loop evidence |
| 24 | CONTROL Ultimate Edition | P-MOVE; P-MYSTERY | P-B | R-NONE, `risk_codes=[]` | N-0 | I+ should use game/system evidence rather than package-oriented visible summary; omit - |
| 25 | SCARLET NEXUS | P-TACTICAL; P-VARIETY | P-B | R-NONE, `risk_codes=[]` | N-0 | I+ can name telekinesis/two protagonists/combat structure; omit - |
| 26 | Mega Man 11 | P-MOVE2; P-MOVE | P-B + P-D | R-PLAT (`platform_repetition`) | N-H | I+ can name 2D platforming and Double Gear; I- needs concrete retry pressure evidence |
| 27 | Shadow Gambit: The Cursed Crew | P-TACTICAL; P-PROGRESS | P-B | R-NONE, `risk_codes=[]` | N-0 | I+ can name nonlinear stealth strategy/crew abilities/tactical approach; omit - |
| 28 | THE KING OF FIGHTERS XIV STEAM EDITION | P-ACTIVE; P-CHOICE | P-B | R-NONE, `risk_codes=[]` | N-0 | I+ from Taste evidence/short description; omit - |
| 29 | Roguebook | P-FALLBACK; P-CHOICE | P-C + P-B | R-NONE, `risk_codes=[]` | N-0 | I+ has concrete two-hero deckbuilding/combo facts; omit - |
| 30 | FlatOut 2 | P-FALLBACK | P-C | R-OLD (`old_design_friction`) | N-H / weak | I+ from upstream evidence; R-OLD must not be shown merely because the title is old — require concrete control/UI friction evidence |

## 7. Repetition and placeholder counts

Top-30 totals:

- cards audited: **30**
- positive sentences: **49**
- cards containing P-FALLBACK: **11/30 = 36.7%**
- fallback sentences: **11/49 = 22.4%**
- cards with `risk_codes=[]` but visible R-NONE filler: **13/30 = 43.3%**
- cards containing both P-FALLBACK and fake no-risk negative: **5/30 = 16.7%** — ranks 3, 11, 16, 20, 29
- cards with strict game-specific positive rationale (P-A): **0/30**
- cards with an obvious within-card duplicate/near-duplicate positive pair: **at least 4/30** — ranks 2, 15, 17, 26
- visible Russian `summary` is still a placeholder for **14/30** sampled cards
- importantly, **7 of the 11 P-FALLBACK cards already have a concrete non-placeholder summary** (ranks 3, 5, 6, 11, 16, 18, 29), so missing summaries are not the root cause of the fallback problem

Positive-template frequency:

- P-FALLBACK — 11
- P-PROGRESS — 6
- P-CHOICE — 5
- P-MOVE — 4
- P-ACTIVE — 4
- P-TACTICAL — 4
- P-VARIETY — 3
- P-MOVE2 — 2
- P-INVEST — 2
- P-MYSTERY — 2
- P-EXPLORE — 2
- P-CHOICE2 — 1
- P-INVEST2 — 1
- P-PUZZLE — 1
- P-GOAL — 1

Negative-template frequency:

- R-NONE filler — 13
- R-REPEAT — 5
- R-DIR-OPEN — 3
- R-PLAT — 3
- R-PUZZLE — 2
- R-READ — 2
- R-DIR — 1
- R-MANAGE — 1
- R-DIFF — 1
- R-EXPLORE — 1
- R-OLD — 1

This is not just stylistic repetition. The template system removes the title-specific fact that would let the user verify whether the recommendation actually understands the game.

## 8. Evidence inventory

### 8.1 Deterministic evidence already available

The existing Taste/result and scoring contracts already provide enough structure to attempt better grounded text without inventing new external lookup scope:

- `positive_evidence`
- `negative_evidence`
- `tags`
- `short_description`
- current item `summary`
- `taste_factors`
- `fit`, confidence and score breakdown as supporting context only
- `direct_user_evidence` / explicit user rating when present
- `developer` / `publisher` when an explicit profile relationship exists
- `risk_codes` and `risk_status`
- practical facts such as Windows/achievements/duration only when they map to a real stated preference

Relevant contracts checked:

- `config/taste_result_contract.json` — `taste_result.v2`, model `taste-v3`; includes `short_description`, `tags`, `positive_evidence`, `negative_evidence`, fit/decision/score metadata
- `config/taste_scoring_cache_contract.json` — carries fit/verdict/confidence/score, positive/negative evidence, hard signals, gates/signals, tags, short description, developer/publisher and related scoring context
- canonical Taste profile: `kentrap2011-hub/stopgame-ratings-data/gaming_taste_live.json`, payload-bound blob `c478cda9bb7a9b024a30ca188dce4b98a2de24ea`

### 8.2 What must remain deterministic

A future deterministic explanation builder should first try to produce:

`concrete game fact -> explicit profile/taste evidence -> why that matters`

Examples of valid source pairing, without inventing new facts:

- a summary says the game combines guns and martial arts + profile evidence values active/tactical execution;
- a summary says the game uses two heroes/deckbuilding combos + profile evidence values meaningful choices/build interaction;
- a summary says the game is a 2D platformer with a named movement/system mechanic + profile evidence values expressive movement;
- negative evidence says repeated runs/actions are central + profile evidence says unchanged repetition is tiring.

If that bridge cannot be made from accepted evidence, the deterministic producer should output fewer bullets or no bullet — never the current fallback.

### 8.3 What would require Taste/personality inference

These are not safe to silently synthesize as deterministic facts:

- analogies to previously rated games when no explicit analog relation is stored;
- extrapolating developer affinity merely from a developer name;
- interpreting a broad store description as a likely personal experience when the evidence contract did not assert it;
- turning genre membership into a complaint (for example, “old game => bad controls”, “investigation => too much reading”, “platformer => frustrating retries”) without supporting evidence;
- creating a personal risk from a missing/unknown field.

If a later workflow intentionally asks Taste/personality inference to synthesize such a bridge, the result should carry provenance/confidence and still obey the no-invented-complaints gate.

## 9. Required future behavior

### Positive block

1. Allow `why_fit` to contain **0–2** bullets.
2. Delete/disable P-FALLBACK as a player-facing output.
3. Every shown bullet must contain at least one concrete game-specific fact/system/situation, not only a category label.
4. Link that fact to an explicit Taste/profile signal.
5. Deduplicate semantic siblings before keeping two bullets.
6. `price`, `discount`, purchase score, rank, sale urgency and package value must stay outside the “why fits your taste” rationale.
7. If no grounded positive explanation can be produced, prefer an empty/insufficient-evidence state over a placeholder.

### Negative block

1. Allow `risks` to contain **0–2** bullets.
2. If `risk_status.has_described_risk=false`, the player-facing `risks[]` should be empty.
3. If `risk_codes=[]`, do not generate R-NONE or any substitute negative sentence.
4. A `risk_code` is a candidate label, not sufficient provenance by itself. The final sentence must be tied to an actual `negative_evidence`, summary/tag fact, or other accepted source.
5. Do not turn age, genre, missing data, unknown compatibility, missing achievement assessment, or broad category membership into a personal complaint unless the contract/profile provides an explicit relevant signal.
6. For the current sample, **13 cards must show no negative block with the currently accepted risk evidence**. A future improved producer may later discover a real grounded risk for some of them, but until then omission is correct.

## 10. Exact later change points

No code change is authorized by this audit. A separate implementation task should target these exact areas:

1. `data/production/visual/current.json -> games[].why_fit[]`
2. `data/production/visual/current.json -> games[].risks[]`
3. `games[].risk_codes[]` / `games[].risk_status.has_described_risk` consistency
4. `scripts/build_visual_feed_v2.py::reason_ru()` — remove the player-facing generic fallback and stop mapping broad keywords directly to final generic prose
5. `scripts/build_visual_feed_v2.py::build_feed()` — compose/deduplicate concrete positive rationale from accepted source evidence
6. `scripts/build_visual_feed_v2.py::derive_risks()` — align base-stage empty-risk behavior with final semantics even though the final refinement currently overwrites it
7. `scripts/refine_visual_ranking.py::structural_risks()` — preserve provenance for each risk code and avoid genre/age-only speculative risks
8. `scripts/refine_visual_ranking.py::risk_summary()` — return no player-facing sentence when no real risk exists; require grounded source for a described risk
9. `scripts/build_final_visual_payload.py::refine_games_from_signals()` — do not repopulate `risks[]` when `has_described_risk=false`; carry provenance through the final payload
10. schema/UI contract in the later implementation must explicitly allow an absent/empty negative block and an empty positive explanation when evidence is insufficient

Recommended future structured shape, if a schema revision is approved, is provenance-bearing rather than free text only, for example an explanation item containing `text`, `source_field`, `source_excerpt`/source key, `personalization_basis`, and `confidence`. This is a recommendation only; no schema change is made here.

## 11. Acceptance criteria for a later implementation

A later implementation should not be accepted until a regenerated bounded sample passes all of the following:

- 0 occurrences of P-FALLBACK or equivalent “passed Taste filter” placeholder
- 0 visible negative bullets when `has_described_risk=false`
- 0 R-NONE filler bullets
- no price/discount/rank used as a taste rationale
- every visible positive bullet names a concrete fact/system/situation from that game and connects it to accepted personal evidence
- every visible negative bullet has explicit accepted provenance and a relevant personal sensitivity
- no duplicate pair like P-MOVE + P-MOVE2 on one card unless the two bullets genuinely refer to distinct concrete systems
- no invented complaint from age/genre/missing data alone
- the audit review artifact mirrors the same semantics as the canonical UI payload

## 12. Risks / open items

1. **Producer drift:** current canonical payload is bound to explicit producer blob SHAs that differ from newer HEAD source in at least some producer files. Implementation must choose the intended producer line deliberately.
2. **Schema/route drift:** a standalone schema/audit path expected by older documentation was not present on the fixed source. Do not resurrect stale artifacts without an explicit task.
3. **Some visible summaries are placeholders:** 14/30 in this sample. Better deterministic text should use `short_description` / positive evidence / tags when valid, rather than fall back to generic prose.
4. **Some no-code cards may still contain a potentially meaningful risk clue in their description.** That does not justify R-NONE. The future producer may derive a real risk only if it can attach accepted evidence and provenance.
5. **Heuristic risk codes are not self-validating.** The sample contains plausible risk templates, but this audit does not certify each one as a factual complaint about the game.

## 13. Completion record

- audit source branch: `main`
- exact fixed audit source SHA: `9a7d398622c666bc612979f51e264f10977588c3`
- exact report write-base SHA: `e3db8ac796f3b39f2c17ac282ba7419d23d5d9a3`
- report status: **COMPLETE / FAIL CURRENT CONTENT QUALITY GATE / READY FOR A SEPARATE IMPLEMENTATION TASK**
- files modified by this task: **only** `reports/production/CARD_EXPLANATION_AUDIT_01.md`
- runtime/schema/UI/Taste/project-state modifications: **none**
- bounded sample checked: **top 30 current ranked review cards**
- current user-facing negative omission requirement: **13/30 cards with current accepted evidence**
- exact report commit SHA: returned by the GitHub write operation and should be recorded in the worker handoff/final response; embedding a commit's own SHA inside its contents is self-referential and therefore intentionally not attempted

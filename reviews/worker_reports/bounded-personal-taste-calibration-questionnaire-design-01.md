# Bounded personal taste calibration questionnaire design 01

## 1. Task

Task: WORKER_TASK_BOUNDED_PERSONAL_TASTE_CALIBRATION_QUESTIONNAIRE_DESIGN_01.md.

Mode: READ-ONLY / RESEARCH / DESIGN.

Goal: design a finite, auditable calibration questionnaire that extracts high-value missing preference information from the user's existing historical game evidence, without new games, new playthroughs, an open-ended interview, production scoring changes, or profile writes.

Hard boundary: the questionnaire must start with an exact frozen total before question 1. No dynamic extension is allowed.

## 2. Current evidence reviewed

Current main was reviewed on 2026-10-02.

Repository/process evidence:
- CHAT_PROTOCOL.md;
- CHAT_CONTEXT.md;
- current-state section of DIRECTOR_TASK_BOARD.md;
- relevant Taste/profile route material in PROJECT_ROUTES.md;
- reviews/worker_reports/personal-taste-scoring-architecture-research-01.md;
- reviews/worker_reports/personal-taste-scoring-offline-backtest-01.md;
- reviews/worker_reports/personal-taste-scoring-targeted-offline-backtest-02.md;
- experiments/personal_taste_scoring/backtest_02/heldout_truth.json;
- experiments/personal_taste_scoring/backtest_02/truth_classifications.json.

Canonical profile evidence:
- kentrap2011-hub/stopgame-ratings-data/gaming_taste_live.json, blob 9b9926031889dbd98ba6585c57836d52c739a0bb;
- kentrap2011-hub/stopgame-ratings-data/ratings.json, blob 1317bf7add5d279c95992f97c3970b29ccaa3056.

The live profile contains 120 StopGame rating/reason cards. It already encodes many high-confidence broad preferences: gameplay/control feel, sustained development, progression clarity, story/character context, dense open worlds, mystery-with-direction, mastery, art direction, conditional repetition tolerance, social/shared-play value, sequel development, slow-start risk, nostalgia, and the risk of games that are competent but leave no strong personal trace.

Therefore the calibration should not spend slots on generic questions such as whether the user likes story, difficulty, open worlds, or repetition. The missing information is mainly conditional: when a known factor becomes decisive, how strongly context changes it, and when one exceptional positive outweighs several ordinary flaws.

Hard cases reviewed:
- Mass Effect: severe false-high because first-hours friction, information overload, slow-feeling control/combat and weak early hook dominated.
- Castlevania: Lords of Shadow: similarity to DMC caused an unfavourable benchmark comparison rather than positive transfer.
- GTA III: first-contact novelty was incorrectly assumed; truth was the reverse because Vice City came first.
- RDR: shared RDR2 strengths were overgeneralized; playing RDR after RDR2 made it feel weaker and emptier.
- Cyberpunk 2077: generic open-world/system risk missed weak story hook plus stalled discovery/development.
- Perfect World: conventional MMO grind was overweighted; social role, group dungeons and flight were the personal hook.
- Sanitarium: conventional interaction friction was overweighted; atmosphere, puzzles and emotionally affecting stories dominated.
- Banner Saga 2: the formula still worked, but novelty/development relative to the first game disappeared.

Backtest-02 error taxonomy reviewed:
- missed decisive negative;
- overweighted generic richness;
- missed social/contextual hook;
- overweighted conventional friction;
- missed franchise-relative novelty expectation;
- superficial similarity to a favourite/formula;
- invented importance when direct truth was weak;
- correct decisive factor but wrong magnitude;
- correct reasoning and score band.

## 3. Missing information map

High-value gaps:
1. Entry-friction threshold: why a slow start is recoverable in one game but terminal in another.
2. Information-density threshold: whether text/system overload is independently decisive or mainly harmful in combination.
3. Control/combat feel as a gate: when poor moment-to-moment feel overrides story/world strengths.
4. Sustained-development threshold: when an initially strong game becomes boring because development stops.
5. Play-order effect size: how strongly playing a refined/later game first changes the earlier one.
6. First-contact novelty / expectation baseline: positive first-contact bonus versus negative sequel expectation.
7. Sequel novelty-decay threshold: what minimum development a sequel needs.
8. Dominant-positive compensation: when one exceptional strength can carry several ordinary flaws.
9. Conventional quality weight: whether polish/friction is a floor, a multiplier, or merely nice to have.
10. Social/contextual multiplier.
11. Nostalgia/context multiplier.
12. Conditional repetition tolerance.
13. Emotional/story-hook compensation.
14. Favourite-formula comparison direction: similarity as affinity versus similarity as a harsher benchmark.

Lower-value/already covered:
- camera perspective;
- raw genre preference;
- difficulty/mastery;
- generic open-world preference;
- generic art-direction importance;
- game length as quality rather than a practical risk.

## 4. External practices

Bounded current review supports five design principles.

1. Active preference elicitation should select questions for expected uncertainty reduction rather than ask everything uniformly. Guo & Sanner frame query choice using value of information. Maystre & Grossglauser show adaptively selected pairwise comparisons can be more sample-efficient than indiscriminate comparison collection.

2. Adaptive content does not require adaptive length. Adaptive choice-based conjoint work selects later comparisons from earlier answers to reduce uncertainty. This supports changing later wording/references while keeping the total fixed.

3. Pairwise comparisons are useful evidence, not infallible scalar truth. Recent pairwise-preference work emphasizes assumptions about the latent model and data structure.

4. Low cognitive load matters. Preference-elicitation work explicitly treats low cognitive load as a practical requirement, while respondent-burden literature warns about irrelevant, repetitive and cognitively demanding questionnaires.

5. Stopping should follow marginal value. For this task, the value-of-information decision is made before the questionnaire: freeze the smallest N that covers the high-value uncertainty map. During execution, only slot content may adapt.

Practical implications:
- prefer concrete comparisons/counterfactuals over essays;
- one independent target per primary slot;
- use ranked choices or bounded tradeoffs where possible;
- clarifications resolve only the current answer;
- unresolved uncertainty remains unresolved after the frozen total.

## 5. Definition of a primary question

A primary question is one independently selected information target whose answer can establish or materially update one reusable preference fact.

It consumes exactly one frozen slot when first presented.

A primary question may reference multiple games only when all references isolate the same uncertainty target. It may not bundle separate targets merely to save counter slots.

## 6. Definition of a clarification

A clarification is a follow-up needed only to understand the current primary answer.

Allowed:
- choose between two interpretations of the same answer;
- clarify wording;
- request one concrete example of the same factor;
- distinguish two reasons already raised in that answer;
- ask confidence in the same recollection.

Not allowed:
- introduce a new independent preference dimension;
- introduce a new game pair for unrelated evidence;
- ask a second tradeoff that establishes another reusable fact;
- fill a later target while pretending to clarify the current one.

## 7. Clarification counting rule

- Present primary X -> Question X of 14.
- Any allowed clarification -> still X / 14.
- Resolve or mark X unresolved -> next independently selected target is X+1.
- If memory is insufficient, store unresolved/low-confidence and continue; no hidden replacement questions.
- A fallback reference for the same target remains the same primary slot.
- Any new independent target consumes the next primary slot.

## 8. Candidate uncertainty targets

Ordinal heuristic: I = importance, U = current uncertainty, R = redundancy, IG = expected information gain; 1–5, higher R means more overlap.

| Target | I | U | R | IG | Decision |
|---|---:|---:|---:|---:|---|
| Entry-friction threshold | 5 | 5 | 1 | 5 | include |
| Information-density / reading threshold | 5 | 4 | 2 | 5 | include |
| Control/combat feel as gate | 5 | 4 | 2 | 4 | include |
| Sustained-development threshold | 5 | 5 | 1 | 5 | include |
| Play-order effect size | 5 | 5 | 1 | 5 | include |
| First-contact novelty / expectation baseline | 5 | 4 | 2 | 5 | include |
| Sequel novelty-decay threshold | 5 | 5 | 2 | 5 | include |
| Dominant-positive compensation | 5 | 5 | 1 | 5 | include |
| Conventional quality vs personal hook | 5 | 5 | 2 | 5 | include |
| Social/contextual multiplier | 5 | 5 | 1 | 5 | include |
| Nostalgia/context multiplier | 4 | 4 | 2 | 4 | include |
| Conditional repetition tolerance | 5 | 4 | 2 | 4 | include |
| Emotional/story-hook compensation | 5 | 4 | 2 | 4 | include |
| Favourite-formula comparison direction | 5 | 5 | 1 | 5 | include |
| Separate pure slow-start question | 4 | 3 | 4 | 2 | merge into entry friction |
| Good-but-forgettable threshold | 4 | 3 | 4 | 3 | covered by conventional-quality slot |
| Game-length tolerance | 3 | 3 | 3 | 2 | reserve only |
| Difficulty/mastery | 3 | 1 | 5 | 1 | exclude |
| Camera/genre preference | 2 | 1 | 5 | 1 | exclude |

This is a prioritization heuristic, not a statistical estimate.

## 9. Information-gain prioritization

Tier A, directly tied to serious known errors:
1. entry-friction threshold;
2. sustained-development threshold;
3. play-order effect;
4. franchise/novelty expectations;
5. dominant-positive compensation;
6. social/contextual multiplier;
7. conventional-quality versus personal-hook weighting;
8. favourite-formula comparison direction.

Tier B, required to make Tier A reusable rather than game-specific:
9. information-density threshold;
10. control/combat feel;
11. sequel novelty-decay threshold;
12. repetition tolerance;
13. emotional/story-hook compensation;
14. nostalgia/context multiplier.

A 15th or 16th question would mostly subdivide interactions already represented or chase cards that the user has explicitly said are poorly remembered.

## 10. Chosen total N

Chosen total: N = 14 primary questions.

The questionnaire must begin with:

0 / 14 primary questions

Then: Question 1 of 14.

N=14 is the smallest fixed budget that covers all high-value independent uncertainty targets without using forgotten games as evidence and without hiding multiple independent targets inside one question.

Expected completion time: about 18–25 minutes including occasional clarifications.

## 11. Why not fewer

Fewer than 14 would either leave a backtest-proven failure channel unmeasured or force independent effects into compound questions.

Unsafe merges include:
- onboarding friction versus information overload;
- play order versus sequel novelty decay;
- social context versus nostalgia;
- repetition tolerance versus sustained development;
- emotional hook versus conventional-quality tolerance.

These interactions can move scores in opposite directions, so merging them would reproduce the same ambiguity that caused the hard-case failures.

## 12. Why not more

Beyond 14, marginal value drops sharply because:
- broad preferences are already well represented in the 120-card profile;
- roughly 40 cards have some medium/low-confidence or explicit memory-gap marker, but many say the user no longer remembers enough detail;
- extra questions would increasingly repeat the same compensation rules with another title;
- remaining topics such as very long playtime are more practical-risk questions than central taste-scoring gaps;
- fatigue/burden literature supports removing irrelevant/repetitive items.

Thus 14 is a bounded calibration set, not an attempt to exhaust every possible preference.

## 13. Early-finish rule

No early finish for the first calibration run.

Rationale:
- the first run is an auditable experiment;
- 14 is already the smallest set of independent high-value targets;
- if an earlier answer fully resolves a later target, that slot is reassigned to the highest-value unresolved reserve target;
- fixed completion improves comparability and directly respects the user's desire to know the endpoint in advance.

The run ends at exactly 14 / 14 complete.

Reserve target order if a planned slot becomes redundant:
1. good-but-forgettable threshold if not already resolved;
2. game-length fatigue as taste-versus-practical distinction;
3. expectation/hype penalty if Q06 did not isolate it.

## 14. Progress UX

Before start:
- 0 / 14 primary questions
- 14 primary questions remaining
- Clarifications do not increase the total.

During:
- Question X of 14
- X / 14
- after resolution: 14 - X primary questions remaining
- clarification label: Clarification for question X — still X / 14

If unresolved:
- Question X marked unresolved — X / 14 complete
- continue to X+1 without hidden extra questions

Completion:
- 14 / 14 complete
- show resolved versus unresolved targets separately
- never offer an automatic extra round

The counter never resets or disappears.

## 15. Question-type distribution

Planned 14 slots:
- 6 contrastive/pairwise;
- 4 counterfactual;
- 2 forced-priority/threshold;
- 2 single-case context-isolation.

Most answers should fit in 1–3 sentences or a ranked choice plus a short reason.

## 16. Proposed questionnaire plan

### Q01
- question_id: cal01_entry_friction_threshold
- primary_index: 1
- uncertainty_target: entry-friction threshold
- question_text_ru: У Mass Effect тяжёлый вход оказался почти непреодолимым, а у RDR2 нудный старт в итоге был полностью перекрыт дальнейшей игрой. Что было решающим различием именно в первые часы: перегрузка информацией/системами, управление и бои, отсутствие сюжетного крючка, неясность цели — или другое? Выбери максимум два главных пункта и скажи, какой был важнее.
- games/references used: Mass Effect; Red Dead Redemption II
- expected answer type: ranked top-2 + short reason
- allowed clarification scope: only distinguish the named first-hours factors
- what new profile fact it can establish: threshold for terminal onboarding friction versus recoverable slow start
- what scoring failure it is intended to reduce: Mass Effect false-high
- fallback if the user cannot remember enough: choose among currently recorded reasons; otherwise unresolved

### Q02
- question_id: cal02_information_density
- primary_index: 2
- uncertainty_target: information overload / reading-dialogue tolerance
- question_text_ru: Если представить Mass Effect с приятным управлением и интересными боями, но оставить тот же объём текста, терминов и сразу выданных систем: этого одного всё ещё хватило бы, чтобы ты, скорее всего, бросил игру в первые часы, или тогда перегрузка стала бы терпимой?
- games/references used: Mass Effect
- expected answer type: forced counterfactual + confidence
- allowed clarification scope: distinguish too much reading from too many systems only if raised by the answer
- new fact: whether information density is an independent veto or mainly an interaction effect
- scoring failure reduced: missed decisive negative / generic RPG richness
- fallback: answer from recorded reasons as a hypothetical; otherwise unresolved

### Q03
- question_id: cal03_control_vs_story_tradeoff
- primary_index: 3
- uncertainty_target: control/combat feel as a gate
- question_text_ru: Что для тебя обычно опаснее: игра с интересным миром/сюжетом, но вялым или неудобным управлением и боями, или игра со слабым сюжетом, но очень приятным непосредственным геймплеем? Ориентир: Mass Effect против Dark Messiah.
- games/references used: Mass Effect; Dark Messiah of Might and Magic
- expected answer type: pairwise tradeoff + condition
- allowed clarification scope: clarify what pleasant gameplay means in this comparison
- new fact: relative veto power of moment-to-moment feel versus narrative/world strength
- failure reduced: overrating rich games with poor personal control feel
- fallback: use recorded summaries only

### Q04
- question_id: cal04_sustained_development
- primary_index: 4
- uncertainty_target: sustained development versus strong opening followed by stagnation
- question_text_ru: Cyberpunk 2077 и Hogwarts Legacy оба сначала нравились заметно сильнее, чем в итоге. Что сильнее разделило их итоговые оценки: насколько долго продолжали появляться новые возможности, сила сюжета после середины, качество самого игрового цикла или что-то другое?
- games/references used: Cyberpunk 2077; Hogwarts Legacy
- expected answer type: contrastive ranking
- clarification: distinguish no new mechanics from same mechanics becoming repetitive
- new fact: threshold where stalled development becomes rating-dominant and what can compensate
- failure reduced: Cyberpunk missed decisive negative
- fallback: choose between recorded causes only

### Q05
- question_id: cal05_play_order_effect
- primary_index: 5
- uncertainty_target: order in which related games were experienced
- question_text_ru: Если мысленно поменять порядок знакомства: ты сначала сыграл бы в GTA III до Vice City и в Red Dead Redemption до RDR2. У какой из этих двух игр оценка, по твоему ощущению, изменилась бы сильнее — и примерно в какую сторону?
- games/references used: GTA III; Vice City; Red Dead Redemption; Red Dead Redemption II
- expected answer type: pairwise counterfactual + direction/magnitude
- clarification: direction or whether order would matter at all
- new fact: magnitude/generalizability of reverse-order penalty
- failure reduced: GTA III and RDR history-relative false-highs
- fallback: strongly / slightly / almost not at all

### Q06
- question_id: cal06_first_contact_expectations
- primary_index: 6
- uncertainty_target: first-contact novelty and expectation baseline
- question_text_ru: Сравни эффект первого знакомства с серией Assassin's Creed и разочарование от GTA V после предыдущих GTA. Что сильнее влияет на твою оценку: сам вау-эффект «я такого раньше не видел» или несоответствие ожиданию, что новая часть должна заметно развить уже знакомую формулу?
- games/references used: Assassin's Creed; GTA V; earlier GTA entries
- expected answer type: forced comparison + depends-when condition
- clarification: distinguish novelty bonus from expectation penalty within this target
- new fact: whether history acts mainly as first-contact bonus, expectation penalty, or both
- failure reduced: GTA V novelty-relative-to-history miss
- fallback: identify which mechanism better describes each recorded case

### Q07
- question_id: cal07_sequel_novelty_decay
- primary_index: 7
- uncertainty_target: novelty decay across sequels
- question_text_ru: Почему «знакомая формула» сработала в плюс у Devil May Cry 4, но стала минусом у Banner Saga 2 и частично у Devil May Cry 5? Что продолжение должно изменить минимум, чтобы ощущение «то же самое» не снижало твою оценку?
- games/references used: DMC4; DMC5; The Banner Saga 2
- expected answer type: contrastive rule / minimum-change threshold
- clarification: mechanical versus story/character evolution if both are mentioned
- new fact: minimum sufficient sequel evolution and whether types of novelty substitute for each other
- failure reduced: Banner Saga 2 novelty miss
- fallback: use recorded summaries and answer at rule level

### Q08
- question_id: cal08_dominant_positive
- primary_index: 8
- uncertainty_target: one dominant positive outweighing conventional flaws
- question_text_ru: Mirror's Edge и Prince of Persia (2008) показывают, что один очень сильный личный плюс может перекрыть заметные минусы. Что должно быть правдой, чтобы один такой плюс реально «тащил» игру: он должен быть центральной механикой, постоянно присутствовать, быть уникальным для тебя, или достаточно просто очень сильного впечатления?
- games/references used: Mirror's Edge; Prince of Persia (2008)
- expected answer type: rank conditions
- clarification: necessary versus merely helpful condition
- new fact: non-additive compensation rule for dominant positives
- failure reduced: false-lows from conventional flaws
- fallback: identify the carrying strength in the two recorded cases

### Q09
- question_id: cal09_conventional_quality_weight
- primary_index: 9
- uncertainty_target: conventional quality importance
- question_text_ru: Что для твоей оценки обычно важнее: неровная/устаревшая игра с одним сильным личным крючком или качественно сделанная игра без яркого личного следа? Ориентиры: Sanitarium против «хорошо сделано, но почти нечего вспомнить» вроде Mafia II / среднего впечатления от Resident Evil 4.
- games/references used: Sanitarium; Mafia II; Resident Evil 4
- expected answer type: pairwise principle + exception
- clarification: meaning of roughness or personal hook
- new fact: whether polish is floor, multiplier or secondary
- failure reduced: Sanitarium false-low / generic quality halo
- fallback: answer abstract tradeoff only

### Q10
- question_id: cal10_social_context_multiplier
- primary_index: 10
- uncertainty_target: social/contextual value
- question_text_ru: Если убрать из Perfect World помощь новичкам, данжи с людьми и ощущение своей роли в сообществе, оставив тот же MMO-геймплей и полёты, насколько заметно упала бы твоя оценка: почти не изменилась / немного / сильно?
- games/references used: Perfect World
- expected answer type: categorical magnitude + reason
- clarification: social role versus group activity
- new fact: magnitude of social-role/context bonus
- failure reduced: Perfect World decisive-positive miss
- fallback: necessary / helpful / incidental

### Q11
- question_id: cal11_nostalgia_context
- primary_index: 11
- uncertainty_target: nostalgia/context versus intrinsic properties
- question_text_ru: Если бы ты впервые познакомился с Postal 2 сегодня, без детского вау-эффекта и воспоминаний, но с теми же необычными возможностями, оценка была бы примерно такой же, немного ниже или намного ниже?
- games/references used: Postal 2
- expected answer type: counterfactual magnitude + reason
- clarification: nostalgia/memory versus novelty of mechanics
- new fact: temporal-context multiplier independent of underlying novelty
- failure reduced: Postal 2 false-low
- fallback: mark nostalgia share uncertain

### Q12
- question_id: cal12_repetition_tolerance
- primary_index: 12
- uncertainty_target: repetition tolerance
- question_text_ru: Повторяемость не помешала высоко оценить Assassin's Creed и Prince of Persia (2008), но сильно ударила по Banner Saga 2 и Rayman Legends. Что чаще всего решает, простишь ли ты повторение: удовольствие от базового действия, сильная атмосфера/фантазия, появление новых деталей, короткая длительность — или другое?
- games/references used: Assassin's Creed; Prince of Persia (2008); The Banner Saga 2; Rayman Legends
- expected answer type: rank top-2 compensators
- clarification: one selected compensator only
- new fact: conditional repetition-compensation rule
- failure reduced: treating repetition as globally negative/positive
- fallback: use any two remembered anchors in the same target

### Q13
- question_id: cal13_emotional_story_hook
- primary_index: 13
- uncertainty_target: emotional/story hook as compensation
- question_text_ru: Sanitarium запомнился атмосферой, загадками и эмоциональными историями, а у Mass Effect сюжет в первые часы не помог преодолеть трение. Какой сюжетный/эмоциональный крючок для тебя достаточно сильный, чтобы терпеть неудобства игры, и есть ли предел, после которого даже сильная история уже не спасает?
- games/references used: Sanitarium; Mass Effect
- expected answer type: threshold rule
- clarification: strong story versus emotional attachment/atmosphere
- new fact: compensation relationship between emotional hook and gameplay friction
- failure reduced: Sanitarium false-low plus Mass Effect false-high
- fallback: identify the strongest recorded Sanitarium factor

### Q14
- question_id: cal14_similarity_benchmark_direction
- primary_index: 14
- uncertainty_target: why superficially similar games receive different ratings
- question_text_ru: Castlevania: Lords of Shadow похожестью на Devil May Cry не получила бонус — наоборот, сравнение сделало её слабее. Когда сходство с любимой игрой для тебя работает в плюс, а когда превращается в более строгий эталон? Назови 1–2 признака, которые должны быть не хуже оригинала, чтобы сходство помогало.
- games/references used: Castlevania: Lords of Shadow; Devil May Cry
- expected answer type: contrastive rule + required dimensions
- clarification: clarify a named dimension only
- new fact: guardrail against positive transfer from superficial similarity
- failure reduced: Castlevania false-high / superficial-similarity taxonomy
- fallback: similarity usually plus / neutral / raises requirements

## 17. Adaptive branching rules

1. Total remains 14.
2. Each slot has one uncertainty target; wording may adapt only within that target.
3. If an answer fully resolves a future slot before it is reached, that slot is reassigned to the highest-value unresolved reserve target.
4. Reassignment must be recorded before presentation: original target, reason it became redundant, replacement target.
5. Reassignment occupies the same primary index; it cannot create question 15.
6. If the user cannot remember a named game, first use the stored direct reason as a scaffold; if still insufficient, switch to another already-known reference for the same target.
7. If no adequate reference exists, mark unresolved rather than inventing evidence.
8. Avoid why-chain interviews. Once a follow-up seeks another reusable fact, it is a new primary target and cannot be hidden as clarification.
9. Prefer high-confidence cards; do not mine explicitly forgotten games merely to fill space.
10. Answers must produce reusable conditional evidence, not AppID-specific scoring rules.

## 18. Profile-update schema proposal

No profile write is authorized here.

A later questionnaire-run should preserve:
- source_type: bounded_calibration_questionnaire;
- questionnaire_id;
- question_id;
- primary_index;
- direct_user_statement;
- clarification_statements attached to the same source question;
- inferred_preference;
- inference_confidence: high / medium / low;
- related_games;
- temporal_context_qualifier;
- franchise_context_qualifier;
- reusability: global / conditional_global / franchise_specific / game_specific;
- scope_guardrail;
- unresolved boolean.

Rules:
- direct statement and inference remain separate;
- confidence applies to the inference;
- clarifications never become separate source questions;
- unresolved remains explicit and is not negative evidence;
- contextual facts such as childhood, first contact, play order, family/friend context are stored as qualifiers;
- a later profile update should be a bounded delta through the canonical profile-update path, not a whole-profile rewrite.

## 19. Validation against known failure cases

| Case | Planned question(s) | Missing signal | Generalizes? |
|---|---|---|---|
| Mass Effect | Q01, Q02, Q03, Q13 | first-hours vetoes; info density; control/combat; hook versus friction | yes, system-heavy/onboarding cases |
| Castlevania: Lords of Shadow | Q14 | favourite similarity can raise the benchmark | yes |
| GTA V | Q06 | novelty-relative-to-history / expectation baseline | yes, franchises |
| GTA III | Q05 | reverse-order penalty after Vice City | yes |
| RDR / RDR2 | Q01, Q05 | recoverable slow start plus play-order/reference-quality effect | yes |
| Cyberpunk 2077 | Q04 | stalled discovery/development plus weak hook | yes, long-form games |
| Perfect World | Q10 | social role/group value separate from MMO grind | yes, social context |
| Sanitarium | Q09, Q13 | personal atmosphere/emotional hook outweighing friction | yes, rough/older narrative games |
| Postal 2 | Q11 | nostalgia/childhood context versus intrinsic novelty | yes, with qualifier |
| Assassin's Creed | Q06, Q12 | first-contact novelty and tolerated repetition | yes |
| Banner Saga 2 | Q07, Q12 | sequel novelty decay despite working base loop | yes |

Additional anchors:
- Mirror's Edge -> Q08 tests one dominant positive.
- Hogwarts Legacy -> Q04 tests strong-opening/stagnation decay.
- DMC4/DMC5 -> Q07 tests successful versus insufficient sequel evolution.

The plan targets causes of known errors instead of asking for more ratings of the same kind.

## 20. Expected user time

Estimated primary-question time:
- six pairwise/contrastive: about 60–90 sec each;
- four counterfactuals: about 45–75 sec each;
- two threshold/ranking: about 45–60 sec each;
- two context-isolation: about 45–60 sec each.

Primary answers: about 15–20 minutes.
With occasional clarifications: about 18–25 minutes total.

The user should see both the exact count and approximate time before question 1.

## 21. Risks / fatigue / ambiguity

Recall risk:
- many weakly remembered games exist.
- mitigation: high-confidence anchors, stored reasons as scaffolds, unresolved rather than reconstruction.

Counterfactual uncertainty:
- play-order hypotheticals are not historical facts.
- mitigation: store as counterfactual evidence with confidence/qualifier.

Compound-question risk:
- factors interact.
- mitigation: one uncertainty target per slot; clarification cannot spawn another target.

Respondent fatigue:
- 14 is meaningful but bounded.
- mitigation: visible remaining count, bounded answer types, no essays, no dynamic extension, no generic repeats.

Anchoring:
- named reasons can bias.
- mitigation: always allow another reason and use named options only to isolate a known ambiguity.

Overgeneralization:
- Postal 2, Perfect World and RDR are context-heavy.
- mitigation: explicit reusability and temporal/franchise/social qualifiers.

False precision:
- answers do not automatically justify exact scalar weights.
- mitigation: questionnaire produces evidence/conditional rules first; later scoring requires a separate experiment.

Clarification abuse:
- unlimited hidden questions would violate the boundary.
- mitigation: per-question clarification scope is part of the record.

## 22. Exact external sources

Bounded web review performed 2026-10-02.

1. Shengbo Guo, Scott Sanner. Real-time Multiattribute Bayesian Preference Elicitation with Pairwise Comparison Queries. AISTATS / PMLR 9, 2010.
https://proceedings.mlr.press/v9/guo10b.html

2. Adish Singla, Sebastian Tschiatschek, Andreas Krause. Actively Learning Hemimetrics with Applications to Eliciting User Preferences. ICML / PMLR 48, 2016.
https://proceedings.mlr.press/v48/singla16.html

3. Lucas Maystre, Matthias Grossglauser. Just Sort It! A Simple and Effective Approach to Active Preference Learning. ICML / PMLR 70, 2017.
https://proceedings.mlr.press/v70/maystre17a.html

4. Denis Sauré, Juan Pablo Vielma. Ellipsoidal Methods for Adaptive Choice-Based Conjoint Analysis. Operations Research, 2019.
https://pubsonline.informs.org/doi/10.1287/opre.2018.1790

5. William Muldrew, Peter Hayes, Mingtian Zhang, David Barber. Active Preference Learning for Large Language Models. ICML / PMLR 235, 2024.
https://proceedings.mlr.press/v235/muldrew24a.html

6. Rattana Pukdee, Maria Florina Balcan, Pradeep Ravikumar. What Does Preference Learning Recover from Pairwise Comparison Data? ICML / PMLR 306, 2026.
https://proceedings.mlr.press/v306/pukdee26a.html

7. Olalekan Lee Aiyegbusi et al. Key considerations to reduce or address respondent burden in patient-reported outcome (PRO) data collection. Nature Communications 13, 6026, 2022.
https://pmc.ncbi.nlm.nih.gov/articles/PMC9556436/

External-method conclusion: literature supports targeted, adaptive, information-rich comparisons and respondent-burden control. It does not provide a universal magic question count; N must come from this profile's uncertainty map.

## 23. Status

design_complete_ready_for_director_review

No questionnaire was asked.
No canonical profile was modified.
No production scoring/ranking was modified.
No Deep/Dossier contract or state was modified.
No semantic production worker was run.
No site change was published.
No Scheduled Task was created or changed.
No implementation PR was created.

## 24. Recommended next step — exactly one bounded next action

Director reviews this design against the task hard boundaries and either accepts it or returns one bounded correction; do not start the questionnaire before that review.

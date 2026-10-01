# Personal taste scoring architecture research 01

## 1. Task and research method

Task ID: personal-taste-scoring-architecture-research-01

Mode: READ-ONLY / RESEARCH / DESIGN.

Цель исследования — спроектировать личную вкусовую оценку игры, которая одновременно:
- лучше отражает фактический вкус пользователя;
- не зависит от заранее выдуманных потолков вроде 18/12/8/8/4;
- объяснима через конкретные свойства игры и подтверждённые предпочтения;
- не позволяет semantic worker просто назначить число «по ощущению»;
- остаётся воспроизводимой и проверяемой в GitHub;
- допускает будущие пользовательские исправления без скрытой перенастройки всей системы.

Метод:
1. Сначала независимо рассмотрены альтернативы fixed-weight архитектуре.
2. Затем изучены внешние практики: pairwise preference learning, Bradley–Terry/Thurstone/Plackett–Luce, active preference learning, explainable recommendation, calibration, multi-attribute utility, LLM-as-judge, content/embedding recommenders и крупные production recommender patterns.
3. Только после этого рекомендованные варианты сопоставлены с текущим репозиторием и миграционными ограничениями.
4. Production execution не выполнялся. Deep, Dossier, ranking, visual payload, Scheduled Tasks и runtime state не изменялись.

Внешние источники перечислены в разделе 24. В тексте ниже явно различаются:
- **Established practice** — подходы, непосредственно поддержанные литературой/production practice.
- **Promising research idea** — направление с хорошими основаниями, но требующее проверки именно на этом проекте.
- **Worker proposal** — архитектурное предложение для этого репозитория.

## 2. User problem restated

Проблема не в том, что текущие пять факторов плохо названы. Проблема глубже: fixed-weight модель заранее решает, сколько максимум может значить конкретный тип опыта, ещё до того как увидена конкретная игра.

Это создаёт несколько рисков:
- действительно доминирующая для пользователя особенность искусственно упирается в потолок своей категории;
- слабая или поверхностная похожесть получает баллы только потому, что попала в «правильную» категорию;
- пять независимых чисел создают иллюзию точности даже там, где вкус целостный и контекстный;
- итоговый балл становится математически воспроизводимым, но не обязательно психологически верным;
- семантическая модель всё равно выбирает исходные 0–100 значения факторов, поэтому произвольность не исчезает — она лишь прячется перед детерминированной формулой.

Требуемая система должна отвечать на вопрос не «сколько баллов набрали заранее заданные категории», а:

> Какова ожидаемая личная оценка этой игры пользователем после достаточного знакомства с ней, почему именно, относительно какого уже известного опыта и насколько этот вывод надёжен?

Цена, скидка, вишлист, срочность акции и коммерческая выгодность — другие вопросы и не должны менять смысл этого личного fit.

## 3. Current architecture — only as baseline

Текущая архитектура полезна как источник доказательств и provenance, но не должна определять новый дизайн.

Подтверждённый baseline:
- config/final_ranking_policy.json задаёт общий 0–100 score: personal максимум 60 + purchase максимум 40.
- Внутри personal текущий taste максимум 50.
- Эти 50 баллов распределены по пяти фиксированным факторам:
  - gameplay_mastery — 18;
  - development_variety — 12;
  - structure_pacing_direction — 8;
  - identity_hooks — 8;
  - breadth_of_match — 4.
- scripts/priority_ranking.py детерминированно умножает каждый Deep normalized factor 0–100 на его max_points и суммирует.
- Текущий personal score дополнительно включает wishlist, achievements, duration и risk. Поэтому название «Подходит тебе» сейчас означает смесь чистого taste fit и других сигналов.
- config/progressive_pass2_result_schema.json и DEEP-SCORE-EVIDENCE-V1 уже требуют evidence-backed score_findings, но factor_impacts жёстко привязаны к тем же пяти factor_id.
- config/progressive_pass2_worker_prompt.md требует покрыть score findings всеми пятью факторами; если один фактор нельзя честно обосновать, completed fit не должен быть выдуман.
- web/score-details-ui.js уже поддерживает collapsed/expanded score display и explicit legacy/coarse labelling.
- GitHub-owned provenance, exact Dossier refs, exact pinned profile refs и fail-closed acceptance — сильные части текущей архитектуры, которые следует сохранить.

Особенно важное наблюдение из канонического профиля вкуса:
- gaming_taste_live.json содержит 120 StopGame cards;
- у всех 120 есть numeric rating и why_this_rating;
- профиль прямо содержит contextual_preferences/holistic_non_additive_evaluation: пользователь оценивает игры целостно, влияние плюса/минуса зависит от силы и сочетания с другими элементами; профиль отдельно запрещает механически выводить итог из независимых весов;
- профиль также разделяет taste fit, текущий start priority и play role.

Следовательно, текущая fixed-weight формула находится в напряжении с уже зафиксированной семантикой самого профиля. При этом 120 реальных rating+reason примеров дают хороший материал для anchor-based calibration.

## 4. External practices researched

### 4.1 Pairwise preference learning — established practice

Bradley–Terry и Thurstone представляют предпочтение через сравнения пар, а не через независимую абсолютную оценку каждого объекта. Plackett–Luce расширяет похожую идею на ранжирование нескольких объектов.

Практическая ценность для этого проекта: человеку и semantic judge часто легче ответить «эта игра по ожидаемому удовольствию выше или ниже конкретной знакомой игры?» чем независимо назначить «87/100».

BPR показывает более современную recommender-формулировку: оптимизировать именно персональный порядок, а не косвенную pointwise цель. Human-preference работы Christiano et al. и InstructGPT также демонстрируют практическую ценность сравнительных предпочтений как сигнала сложной человеческой цели.

Но pairwise модель не является магией. Pukdee, Balcan, Ravikumar (ICML 2026) показывают, что Bradley–Terry корректно восстанавливает желаемую preference structure только при определённых условиях; важны model fit, margin и connectivity. Поэтому BT нельзя объявлять «истиной» без backtest.

### 4.2 Active preference elicitation — established/promising

Maystre & Grossglauser показывают, что адаптивный выбор сравнений может резко уменьшить число нужных pairwise labels. Singla et al. аналогично исследуют активное извлечение пользовательских предпочтений. Muldrew et al. (2024) показывают value of information / uncertainty-aware selection pairwise preference examples в контексте LLM preference learning.

Для проекта это не причина немедленно строить active-learning subsystem. Но это сильное основание для будущего feedback UX: спрашивать пользователя не случайные вопросы, а сравнения, которые сильнее всего уменьшают неопределённость.

### 4.3 Explainable recommendation — established practice

Обзор Zhang & Chen подчёркивает несколько ролей explanations: прозрачность, доверие, convincingness, effectiveness, debugging. Для данного проекта особенно важен debugging: объяснение должно быть связано с теми же основаниями, которые реально повлияли на score, а не быть пост-hoc текстом.

Текущий DEEP-SCORE-EVIDENCE-V1 уже движется в правильную сторону, связывая visible findings с candidate/profile evidence. Новая архитектура должна сохранить этот принцип, но отвязать evidence от пяти глобальных factor buckets.

### 4.4 Calibration — established practice, но термин нужно использовать аккуратно

Guo et al. исследуют probability calibration: confidence 0.8 должна соответствовать примерно 80% correctness. Это полезный принцип для отдельной confidence/uncertainty оценки, но personal-fit score не должен притворяться вероятностью, если он ей не является.

Steck использует calibration в другом смысле: рекомендованный набор должен отражать распределение интересов пользователя и не вытеснять второстепенные интересы одним доминирующим кластером. Это важно как предупреждение против монотонного «ещё больше похожего на главный любимый паттерн», но не является прямым методом калибровки 0–100 personal score.

Вывод: score и confidence должны быть двумя разными величинами.

### 4.5 Multi-attribute utility — established theory with a warning

Keeney показывает: additive/multiplicative multi-attribute utility допустима при определённых independence/trade-off assumptions. Это как раз причина не считать fixed weighted sum универсальной истиной. Если пользовательский профиль прямо говорит, что влияние свойств зависит от сочетания и целостного впечатления, assumptions простой additive utility нельзя молча считать выполненными.

Dynamic contributions остаются возможной архитектурой, но должны признавать interactions и не маскировать предположение об аддитивности.

### 4.6 LLM-as-judge — promising with known failure modes

Zheng et al. показали, что сильные LLM judges могут достаточно хорошо совпадать с human preferences, но также документировали position, verbosity и self-enhancement bias и ограничения reasoning.

Для проекта это означает:
- Deep можно использовать как semantic comparison engine;
- нельзя делать голый LLM number финальной властью;
- нужны fixed anchors, exact evidence, stable prompt/model/version, consistency checks и deterministic acceptance.

### 4.7 Embeddings / nearest-neighbour / collaborative filtering — useful but not score authority

Google production work показывает ценность candidate generation + separate ranking и embeddings для semantic retrieval/cold start. Wide & Deep отдельно предупреждает, что dense embeddings при sparse interactions могут over-generalize.

Для одного пользователя:
- embedding similarity может хорошо находить релевантные reference games;
- similarity не равна preference;
- collaborative filtering требует поведения многих пользователей и легко импортирует «средний массовый вкус», которого здесь нет;
- superficial similarity к любимой игре особенно опасна.

**Worker proposal:** embeddings допустимы как retrieval aid для выбора возможных anchors, но не как самостоятельный personal-fit score.

## 5. What a 0–100 score should mean

### Recommended semantic definition

**0–100 = нормализованный прогноз личной пользовательской оценки игры после достаточного знакомства с ней, на той же шкале удовольствия/общего впечатления, что и фактические пользовательские рейтинги.**

Это:
- не вероятность покупки;
- не confidence;
- не percentile среди текущих скидок;
- не «насколько похожа на любимые игры»;
- не current desire to start;
- не play role;
- не commercial value.

Практически 0–100 можно сделать rating-equivalent шкалой, где пользовательская 1–5 шкала нормализована линейно:

score = 25 × (predicted_rating_1_to_5 − 1)

Тогда:
- 0 ≈ 1/5;
- 25 ≈ 2/5;
- 50 ≈ 3/5;
- 75 ≈ 4/5;
- 100 ≈ 5/5;
- 87 ≈ прогноз 4.48/5.

Это не требует верить, что модель умеет психологически различать «86 от 87» напрямую. Число выводится из сравнений/калибровки относительно реального rating history.

### Stable interpretation of ranges

Предлагаемые пользовательские bands:
- 0–19: очень сильное несовпадение;
- 20–39: скорее выраженно не зайдёт;
- 40–59: смешанное / около нейтрального;
- 60–79: вероятно положительное впечатление;
- 80–94: сильное попадание;
- 95–100: исключительное попадание, уровень лучших личных оценок.

Это bands expected enjoyment, а не bands confidence. Игра может иметь predicted fit 88 при low confidence; UI должен показывать оба факта отдельно.

### Cross-genre and cross-time comparability

Сравнимость достигается не общими genre weights, а общей пользовательской rating-equivalent шкалой:
- 4/5 в тактике и 4/5 в экшене означают одинаковый уровень общего личного впечатления;
- underlying reasons могут быть полностью разными;
- anchors привязываются к пользовательскому опыту, а не к жанровой норме;
- новая версия profile/calibration получает explicit version, поэтому изменение вкуса во времени не притворяется той же шкалой без provenance.

## 6. Architecture A — holistic calibrated semantic score

### Model

Deep читает:
- exact accepted Dossier;
- exact pinned taste profile;
- deterministic calibration anchor deck из реально оценённых игр.

Deep выдаёт:
- holistic personal_fit_score_0_100;
- score_band;
- confidence отдельно;
- 2–5 material positive/negative findings;
- exact candidate evidence refs;
- exact profile preference refs;
- explicit anchor comparisons: «выше/примерно равно/ниже anchor X по ожидаемому общему впечатлению»;
- uncertainty/conflict notes.

Нет fixed categories и caps. Deep оценивает игру целостно.

### One strong factor

Может фактически определить почти весь verdict, если:
- профиль доказывает, что эта характеристика для пользователя действительно доминирующая;
- candidate evidence показывает её содержательно, а не по тегу;
- сравнение с anchors остаётся согласованным;
- нет более сильного подтверждённого deal-breaker.

Никакого формального «максимум 18» нет.

### Negatives

Negatives входят в holistic judgment. Explicit user-confirmed deal-breaker может перевести outcome в not-fit; обычная friction снижает holistic score пропорционально её фактической роли в опыте.

### Anti-arbitrary safeguards

- обязательные anchor comparisons;
- score обязан лежать в диапазоне, совместимом с заявленными anchor comparisons;
- exact evidence refs;
- no generic praise;
- counterfactual: worker должен назвать, какое найденное свойство сильнее всего изменило бы verdict при его отсутствии;
- same exact inputs не переоцениваются беспричинно;
- model/prompt/profile/dossier/anchor version pinned;
- disagreement/weak evidence понижает confidence, а не автоматически score.

### Strengths

- максимально соответствует holistic_non_additive_evaluation;
- поддерживает неожиданные cross-genre matches;
- простой semantic contract;
- strong single factor может быть действительно strong.

### Failure modes

- финальное число всё ещё назначает LLM;
- anchor reasoning может рационализировать уже выбранное число;
- повторные judges могут расходиться;
- deterministic GitHub validation способна проверить evidence/bounds, но не истинность самого 87.

### Migration

Большой refactor, но current Dossier/profile evidence reusable. Five taste_factors и factor_impacts можно удалить. Existing score_findings можно частично переиспользовать как evidence rows, но старые numbers несопоставимы и требуют finite reanalysis.

## 7. Architecture B — dynamic evidence contribution model

### Model

Deep сам обнаруживает candidate-specific preference effects. Например:
- «тактические задачи постоянно требуют менять план»;
- «после сильных эпизодов есть длинные рутинные отрезки»;
- «важный персонажный конфликт совпадает с тем, что нравилось в reference game».

У каждого effect:
- polarity: positive / negative / contextual;
- exact candidate evidence refs;
- exact profile refs;
- materiality;
- optional signed score-point contribution.

GitHub детерминированно складывает contributions и interactions по прозрачному contract.

Нет постоянных global buckets.

### One strong factor

Да. Один effect может иметь очень крупный contribution, если evidence и profile support сильны. Нет category cap.

### Negatives

Варианты:
- additive negative contribution;
- multiplicative interaction;
- explicit gate для user-confirmed hard deal-breaker;
- uncertainty отдельно, без штрафа за само отсутствие знания.

### Strengths

- лучшая арифметическая auditability;
- карта может показать «+22 / −17»;
- легко объяснить, что двигает score;
- нет фиксированного набора факторов.

### Failure modes

Главный: numeric contribution почти так же может быть выдуман моделью, как финальный 87.

Дополнительно:
- double counting близких findings;
- interaction effects раздувают schema;
- additive presentation может противоречить holistic profile;
- пользователь может ошибочно считать +18 объективной физической величиной.

### Safeguards

- contribution clusters / deduplication;
- explicit interaction IDs;
- сумма должна точно воспроизводить score;
- each contribution bound to evidence;
- large contribution требует stronger profile evidence and counterfactual;
- contribution magnitudes калибруются на held-out rated games, а не выбираются только prompt-ом.

### Migration

Five fixed factors retire. Existing findings can seed candidate-specific effects, but historical contribution values должны быть recomputed. Moderate-to-high implementation complexity.

## 8. Architecture C — pairwise / preference-learning model

### Model

Абсолютное число не генерируется напрямую.

Шаг 1. GitHub держит calibration set из реально оценённых игр пользователя.

Шаг 2. Для candidate собираются pairwise judgments:
- candidate лучше anchor A по ожидаемому общему впечатлению;
- примерно на уровне anchor B;
- ниже anchor C.

Часть pairwise labels может быть:
- прямой пользовательской;
- выведенной из различающихся direct ratings;
- semantic Deep comparison для новых candidates, обязательно с evidence-backed rationale.

Шаг 3. GitHub детерминированно оценивает latent utility через Bradley–Terry/Thurstone-подобную модель либо другую заранее выбранную ordinal модель.

Шаг 4. Latent utility монотонно отображается на rating-equivalent 0–100 шкалу по known rated anchors.

### Bradley–Terry vs Thurstone vs Plackett–Luce vs Elo-like

- **Bradley–Terry**: хороший простой baseline для вероятности A > B как функции difference in latent utilities; детерминированный fit и понятная математика.
- **Thurstone**: похожая latent-comparison идея с Gaussian noise; полезный alternative model check.
- **Plackett–Luce**: полезен, если пользователь ранжирует сразу несколько games, а не только пары.
- **Elo-like update**: операционно простой online update, но порядок поступления feedback и learning rate могут создавать лишнюю path dependence; для audit-first GitHub проекта batch refit предпочтительнее.
- **BPR**: важен как ranking objective, но рассчитан прежде всего на implicit-feedback recommender setting; current project имеет более богатые explicit ratings/reasons, поэтому чистый BPR не оптимален.

### One strong factor

Pairwise модель не знает «факторных потолков». Если одна особенность настолько важна, что candidate consistently выигрывает у high-rated anchors, latent utility растёт сильно.

Но pure pairwise architecture сама по себе не объясняет, почему. Rationale layer всё равно нужен.

### Negatives

Deal-breaker проявляется как сильные losses against anchors. Explicit hard negative может дополнительно стать deterministic eligibility constraint, но только если профиль хранит его как user-confirmed hard rule.

### Strengths

- финальное absolute number не назначается LLM напрямую;
- strong protection against arbitrary 87;
- естественно использует 120 current rated examples;
- concrete game comparisons хорошо совпадают с profile testing_rule;
- future user corrections очень естественны.

### Failure modes

- transitivity/BT assumptions могут быть нарушены;
- sparse/poorly connected comparison graph;
- context changes;
- одинаковая 4/5 оценка не задаёт строгий порядок двух 4/5 games;
- pure pairwise может быть менее объяснимым без semantic evidence;
- если все pairwise labels на новых games делает один LLM judge, judge bias всё ещё присутствует, просто в другой форме.

### Required safeguards

- model-fit diagnostics;
- minimum anchor coverage across low/mid/high rating regions;
- no claim of fine-grained 0–100 precision when comparison interval broad;
- explicit ties/near-equality handling;
- held-out backtest;
- exact comparison provenance;
- direct user comparison overrides model-inferred comparison.

### Migration

Current direct ratings and reasons are highly reusable. Old five factor scores are not needed. Existing Deep evidence/Dossier remains useful for semantic comparison rationale. A finite reanalysis of current unseen candidates is needed, but historical rated games themselves are training/calibration anchors rather than migration liabilities.

## 9. Architecture D — anchor-calibrated evidence-grounded hybrid

### Summary

Это объединяет лучшие стороны C и текущего evidence/provenance layer.

**Deep не имеет права назначать финальный 0–100.**
Deep отвечает на семантические вопросы:
1. Какие candidate-specific свойства реально важны этому profile?
2. Какие из них positive / negative / contextual?
3. Какие exact candidate/profile evidence это доказывают?
4. Как candidate сравнивается по ожидаемому целостному впечатлению с exact GitHub-selected calibration anchors?
5. Есть ли explicit user-confirmed deal-breaker match?
6. Что остаётся uncertain/conflicted?

**GitHub детерминированно:**
- валидирует exact refs;
- проверяет anchor identity/version;
- собирает pairwise constraints;
- вычисляет latent utility;
- переводит её в rating-equivalent 0–100;
- вычисляет uncertainty/interval из структуры сравнения;
- сохраняет model/calibration version;
- формирует read-only visual payload.

### Why this is different from current five-factor system

Нет:
- fixed factor names;
- fixed factor maxima;
- требования «обязательно покрыть все пять»;
- hidden normalized values по заранее заданным buckets;
- direct LLM final number.

Есть:
- candidate-specific semantic findings;
- concrete known-game comparisons;
- deterministic numeric assembly;
- explicit uncertainty;
- exact audit chain.

### One very strong factor

Может фактически привести candidate в верхнюю часть шкалы, даже если других positives мало.

Но для этого он должен пережить три проверки:
1. **Preference proof** — profile показывает, что underlying experience действительно очень важен, желательно через direct statement и/или несколько rated examples.
2. **Candidate proof** — Dossier показывает actual sustained property, а не поверхностный genre/tag/art similarity.
3. **Anchor consistency** — holistic pairwise comparisons с high-rated anchors не противоречат тезису о высоком fit.

Это позволяет одному фактору иметь огромную фактическую роль без arbitrary global cap.

### Negatives

Три разных типа:
- **soft friction** — отражается в holistic pairwise comparisons;
- **material negative** — отдельный negative finding, который заметно двигает comparisons вниз;
- **hard deal-breaker** — только explicit user-confirmed profile rule; может детерминированно запрещать high-fit outcome или переводить в not-fit state.

Uncertainty не является negative. Она расширяет interval / снижает confidence.

### Safeguards against arbitrary scoring

- Deep не возвращает score points.
- Every comparison cites exact candidate + profile evidence.
- GitHub selects/prepares anchor IDs; worker не выбирает удобные references.
- Anchor set covers multiple rating regions.
- Pairwise graph/model-fit checked.
- Same exact semantic input + same accepted comparisons produces exact same score.
- Direct user pairwise correction dominates inferred comparison.
- Superficial similarity itself is never a positive finding.
- A large score change requires changed canonical evidence/profile/comparison/calibration version; otherwise previous accepted result remains authoritative.
- Model judge bias is monitored by held-out comparison accuracy and optional bounded repeated-judge experiment, not hidden retries.
- Score precision shown to user depends on uncertainty; 87 may display as «87, ориентир 82–91» instead of fake exactness.

### Strengths

- strongest fit to current profile’s holistic rule;
- much less arbitrary final number;
- excellent auditability;
- no global category cap;
- natural future correction loop;
- reuses current provenance and Dossier architecture;
- score remains comparable across genres through same personal anchor scale.

### Failure modes

- more complex than A;
- anchor selection policy matters;
- semantic judge still influences pairwise labels;
- BT/Thurstone model misspecification possible;
- more semantic comparisons per candidate increase runtime cost;
- calibration requires a real offline experiment before contract freeze.

### Migration

Substantial but clean rewrite of score semantics. Current five factor vector should be retired rather than adapted.

## 10. Additional variants worth noting

### 10.1 Bayesian latent utility + active questions

Promising later extension: maintain posterior uncertainty over anchor/candidate utilities and ask user only the comparison with highest expected information gain.

Not recommended for first implementation because it adds state/model complexity before the simpler hybrid is validated.

### 10.2 Learned nonlinear preference model over semantic primitives

With enough future corrections, a learned nonlinear model could consume semantic findings/interactions and predict personal rating. This could capture non-additivity better than a weighted sum.

Current dataset is only one user and 120 explicit rated examples, so a flexible learned model risks overfit. Better as later experiment.

### 10.3 Embedding nearest-neighbour

Use embeddings to retrieve possible reference games whose underlying descriptions/reasons may be relevant. Do not map cosine similarity directly to score.

A superficially similar game can be a bad fit; a very different genre can reproduce the same valued experience.

### 10.4 Collaborative filtering

Not recommended as core architecture. The project optimizes one user’s individual taste. Collaborative filtering becomes useful only if a trustworthy multi-user dataset is intentionally introduced, which would be a separate product/privacy/architecture decision.

## 11. Common safeguards against arbitrary scoring

Regardless of architecture:

1. **Separate score from confidence.** Low evidence must not automatically mean low fit.
2. **Exact evidence binding.** Every material reason points to candidate evidence and personal preference evidence.
3. **Calibration anchors.** Never interpret a naked 87 without known reference experiences.
4. **Score-band criteria.** User-visible meaning of bands is fixed and versioned.
5. **Counterfactual check.** For top positive/negative reason, state whether removing it would materially change the conclusion.
6. **No superficial similarity credit.** Shared genre, camera, art, setting or franchise is evidence only if linked to the actual liked experience.
7. **Conflict accounting.** Contradictory Dossier evidence lowers certainty and must remain visible.
8. **Input identity.** Persist model/prompt/profile/Dossier/anchor/calibration versions.
9. **No silent recomputation.** Browser never recalculates; same canonical accepted data stays stable.
10. **Change provenance.** Reanalysis must say what changed. Identical inputs are not a license to replace 82 with 91.
11. **Held-out backtest.** Before production, hide known ratings and test whether architecture recovers them.
12. **Pairwise consistency checks.** Detect strong cycles or anchor contradictions.
13. **Direct user feedback precedence.** Explicit correction outranks inferred preference.
14. **Precision honesty.** Wide uncertainty means coarse display; do not expose decimals merely because the formula can produce them.

Repeated judge agreement can be useful as a bounded experiment, but should not become a hidden retry loop. The production contract should not rerun semantics until a convenient answer appears.

## 12. Worked examples

All examples below are hypothetical. They are not claims about the user’s actual preferences.

### Example 1 — one dominant factor legitimately drives very high score

Hypothesis:
- a user has repeatedly shown that deep tactical problem-solving is the main reason several 5/5 games were loved;
- candidate X has unusually rich encounter-to-encounter tactical adaptation;
- story, art and exploration are merely adequate;
- no major negative is present.

**Architecture A — holistic semantic**
Deep can return a very high fit because the one dominant property is sufficient in this context. It might place X around the 90s, but must cite the candidate evidence, the repeated preference evidence and high-rated anchors. There is no gameplay cap.

**Architecture B — dynamic contributions**
One discovered effect could account for most positive movement. For example, the tactical finding could be the largest positive contribution, while several minor findings add little. Auditability is clear, but the exact size of that contribution remains a calibration problem.

**Architecture C — pairwise**
X consistently beats 4/5 anchors and is near 5/5 tactical anchors. The latent utility becomes high without ever assigning «tactics = 35 points». The strong property matters because it changes whole-game pairwise preference.

**Architecture D — hybrid**
Semantic evidence proves why tactical depth is personally dominant; pairwise anchors determine how high the overall outcome belongs. This is the desired behaviour: one factor can dominate, but only after preference proof + candidate proof + anchor consistency.

### Example 2 — superficial similarity to a favourite must NOT create a high score

Hypothesis:
- user loved a hypothetical Last-of-Us-like reference primarily for character relationships, tense encounter pacing and emotional continuity;
- candidate Y is also third-person, post-apocalyptic and visually similar;
- but its characters are thin, encounters repetitive and crafting/filler dominates.

**Architecture A**
Shared setting/camera cannot be used as a material positive unless profile evidence says those were the liked reasons. Holistic comparison should land far below the favourite reference.

**Architecture B**
No contribution for «same setting» unless linked to an actual preference. Character/pacing misses become negative contributions. Superficial similarity may be shown only as neutral context.

**Architecture C**
Y loses pairwise against the favourite and potentially against other 4/5 anchors because pairwise prompt asks about expected total enjoyment, not visual resemblance. Embedding proximity does not enter score.

**Architecture D**
Evidence layer explicitly identifies why the reference was liked and checks those underlying properties in Y. The candidate can receive a middling or low score despite high surface similarity. This directly prevents the failure mode the user is concerned about.

### Example 3 — many moderate positives vs one meaningful deal-breaker

Hypothesis:
- candidate Z has good combat, exploration, progression, art and story;
- but requires a form of opaque mandatory micromanagement that the user has explicitly and repeatedly marked as a deal-breaker.

**Architecture A**
Holistic verdict may be low/not-fit despite many positives. The deal-breaker is not averaged away.

**Architecture B**
A simple additive model is dangerous here: five +8 positives and one −20 negative would still look good. A separate hard-constraint/gating semantic is required.

**Architecture C**
If historical anchors with the same deal-breaker are disliked, pairwise losses should pull Z down sharply. But with sparse relevant anchors, the model may understate the hard constraint.

**Architecture D**
Exact profile evidence marks the issue as user-confirmed hard constraint; Deep proves candidate match; GitHub applies the contracted not-fit/high-score prohibition while preserving all positives as explanation. This is safer than both a flat penalty and an average of positives.

## 13. User-facing audit UI

### Collapsed card

Default card should stay compact:

**Личный прогноз: 87/100 · высокая уверенность**
- Главный плюс: «...»
- Главный риск: «...»
- «Почему 87?» expandable control
- badge when relevant: «новая модель», «приближённая legacy», «низкая уверенность», «мигрировано»

Do not show a long matrix by default.

### Expanded audit view

1. **Meaning**
   - «87 ≈ ожидаемая личная оценка ~4.5/5»
   - confidence and interval separate: e.g. «ориентир 82–91».

2. **Anchor comparisons**
   - выше known 4/5 anchor A;
   - примерно на уровне 4.5-equivalent anchor B;
   - ниже known 5/5 anchor C.

3. **What moved the conclusion**
   - positive findings ordered by materiality;
   - negative findings ordered by materiality;
   - no fake numeric point contribution unless architecture B is chosen.

4. **Evidence chain for each finding**
   - property of candidate;
   - source/Dossier observation;
   - linked personal preference / known game reason;
   - effect: supports / lowers / contextual / hard constraint.

5. **Uncertainty**
   - missing/contradictory evidence;
   - sparse anchor coverage;
   - semantic comparison disagreement.

6. **Provenance**
   - personal-fit model version;
   - profile version;
   - Dossier binding;
   - calibration version;
   - legacy/migration status.

Current collapsed score-details pattern can be reused conceptually, but the contents should change from fixed components to this audit model.

## 14. Correction/feedback loop

Future user corrections should update the smallest correct source of truth.

### “Этот фактор для меня гораздо важнее / менее важен”

Update:
- Taste profile preference strength/context;
- linked evidence/examples.

Do not directly edit a global bucket weight, because there should be no permanent bucket.

### “Ты неправильно понял, почему мне понравилась эта игра”

Update:
- why-this-rating / preference rationale for that anchor/reference;
- invalidate semantic comparisons that depended on the wrong reason.

Do not change the historical rating unless user changes the rating.

### “Этот минус для меня не проблема”

Update:
- negative preference rule / contextual guardrail;
- pairwise evidence derived from that rule becomes stale.

### “87 слишком высоко; сравни с A и B”

Store:
- explicit pairwise preferences against A/B;
- this becomes stronger calibration evidence than model-inferred comparisons.

### “Сейчас эта игра мне подходит, но не хочу начинать её первой”

Do **not** lower personal fit. Update separate start-priority / role state if that feature exists later.

### Future active-learning idea

If uncertainty is high, ask the comparison that would most reduce uncertainty, not a random preference question. This is a later feature, not part of this task.

## 15. GitHub/Deep ownership model

### Architecture A

Deep:
- holistic score;
- findings;
- anchor comparisons;
- uncertainty explanation.

GitHub:
- exact inputs/anchors;
- schema validation;
- score-band/anchor consistency;
- persistence/versioning;
- publication.

Weakness: GitHub cannot deterministically prove that semantic 87 is the right number.

### Architecture B

Deep:
- discovers evidence effects and semantic materiality;
- proposes signed contributions/interactions.

GitHub:
- validates refs/dedup structure;
- deterministic composition;
- bounds/rounding/versioning.

Weakness: Deep still chooses contribution magnitudes.

### Architecture C

Deep:
- only evidence-backed candidate-vs-anchor preference judgments for new games.

GitHub:
- anchor graph;
- user/direct-rating pairwise constraints;
- latent utility fitting;
- 0–100 mapping;
- uncertainty/model-fit checks;
- versioned persistence.

Stronger deterministic boundary.

### Architecture D

Deep:
- candidate-specific findings;
- exact evidence links;
- candidate-vs-anchor holistic comparisons;
- explicit hard-negative match only when profile authority exists;
- semantic conflict/uncertainty facts.

GitHub:
- all C responsibilities;
- deterministic validation of hard-rule authority;
- final fit computation;
- migration state;
- audit payload;
- no silent recalculation in browser.

### Browser

For every architecture:
- read-only rendering only;
- may expand/collapse sections and preserve local UI state;
- never selects anchors;
- never applies weights;
- never recomputes personal fit;
- never reinterprets missing evidence.

This stays consistent with PRODUCTION-EXECUTION-OWNERSHIP-V1.

## 16. Comparative analysis

| Criterion | A. Holistic semantic | B. Dynamic contributions | C. Pairwise latent | D. Hybrid anchor-calibrated |
|---|---|---|---|---|
| Faithfulness to real taste | Very high potential; fully non-additive | Medium-high if interactions modeled | High for relative preference | Very high: holistic evidence + pairwise calibration |
| Freedom from fixed caps | Excellent | Excellent | Excellent | Excellent |
| Explainability | High | Very high | Medium without rationale layer | Very high |
| Auditability | Medium | High | High | Very high |
| Resistance to arbitrary final number | Medium-low | Medium | High | Very high |
| Learns from liked/disliked examples | High via anchors | High via evidence/profile | Excellent | Excellent |
| Strong single factor | Natural | Natural | Natural | Natural + evidence safeguards |
| Negatives/deal-breakers | Semantic | Needs explicit gate semantics | Indirect unless constraints added | Explicit soft/material/hard separation |
| Uncertainty handling | Possible but judge-owned | Possible | Natural from comparison graph | Natural + semantic conflicts |
| Cross-genre comparability | Good if anchors strong | Risk of contribution drift | Strong if common anchor scale | Strong |
| Stability over time | Medium | Medium | High with versioned graph | High |
| User correction support | Good | Good | Excellent | Excellent |
| Implementation complexity | Lowest of new options | Medium-high | High | Highest |
| Migration cost | High | High | High | High |
| Runtime semantic cost | Low-medium | Medium | Medium-high | High |
| Deterministic validation strength | Medium | High on arithmetic, not magnitudes | High | Highest |

No numeric scorecard is assigned to these architectures because there is no defensible common quantitative utility for these trade-offs yet.

## 17. Two strongest candidates

### Strongest: D — anchor-calibrated evidence-grounded hybrid

Почему:
- matches holistic_non_additive_evaluation;
- final number not directly chosen by LLM;
- preserves exact evidence chain;
- uses 120 existing rating+reason examples as real calibration assets;
- strong single factor can dominate without a global cap;
- superficial similarity has no direct scoring route;
- future user corrections map naturally to profile/pairwise evidence;
- GitHub can own the numeric transformation and versioning.

### Second: C — pure pairwise latent preference model

Почему:
- simplest principled way to eliminate direct arbitrary 0–100 assignment;
- strong theory and extensive preference-learning practice;
- excellent use of existing rated games;
- highly compatible with direct future “A or B?” corrections.

Why it is second rather than first:
- explanations and deal-breaker semantics are weaker unless evidence layer is added;
- pairwise structure alone may compress contextual reasons into a one-dimensional utility;
- model assumptions need explicit diagnostics.

## 18. Recommended architecture

**Recommend Architecture D: anchor-calibrated evidence-grounded hybrid.**

### Proposed canonical output concept

Instead of current taste_factors:

personal_fit:
- model_version
- score_0_100
- rating_equivalent_1_to_5
- score_band
- confidence
- interval_low / interval_high when defensible
- calibration_version
- anchor_comparisons[]
- findings[]
- hard_constraints[]
- uncertainty[]
- provenance

Each finding:
- finding_id
- polarity / role
- materiality
- text_ru
- candidate_evidence_refs
- profile_evidence_refs
- optional related_anchor_refs
- counterfactual_materiality

Each anchor comparison:
- anchor_game_id
- anchor_user_rating
- relation: candidate_better / roughly_equal / anchor_better
- exact rationale refs
- origin: direct_user / derived_from_rating / semantic_deep
- accepted semantic binding

Deep does **not** write score_0_100. GitHub derives it.

### Recommended scoring pipeline

1. GitHub prepares exact candidate + profile + accepted Dossier.
2. GitHub selects versioned calibration anchors.
3. Deep produces grounded findings + holistic pairwise comparisons.
4. GitHub validates all refs and comparison completeness.
5. GitHub fits/evaluates candidate latent utility with a chosen pairwise model.
6. GitHub maps latent utility to the user’s rating-equivalent 0–100 scale.
7. GitHub computes/labels uncertainty and stores exact provenance.
8. Visual producer publishes only prepared audit fields.
9. Browser renders; it does not infer.

### Why not keep five factors just with dynamic weights?

Because the profile itself says the final judgement is non-additive/contextual. Dynamic global weights would make the current architecture less rigid, but would still assume stable separable dimensions and would still force every candidate through the same ontology.

The better reusable object is the **evidence-backed preference finding**, not the global factor bucket.

## 19. Serious runner-up

**Architecture C: pure pairwise latent preference model.**

A simpler initial implementation could:
- derive a graph from 120 ratings;
- select fixed rating-stratified anchors;
- ask Deep only candidate-vs-anchor holistic comparisons with rationale;
- fit BT and map to 0–100;
- expose pairwise rationale without the richer finding taxonomy.

Reasons to choose C instead of D:
- if D’s semantic findings materially increase runtime/cost without improving held-out accuracy;
- if pairwise-only explanations are sufficient for the user;
- if hard negatives can be represented well through explicit pairwise/user constraints;
- if a simpler migration is materially safer.

## 20. What would change the recommendation

Recommend C over D if a bounded offline experiment shows all of the following:
- pairwise-only model predicts held-out known ratings/rankings at least as well as D;
- user can understand why scores differ from pairwise rationale alone;
- explicit deal-breaker cases are not systematically over-scored;
- D’s additional semantic findings add little correction value or materially hurt runtime stability.

Recommend A over both if:
- pairwise consistency is poor because the user’s preferences are strongly context-dependent/non-transitive;
- BT/Thurstone diagnostics show unacceptable misfit even after contextual anchors;
- holistic semantic scoring with fixed anchors demonstrates much better held-out calibration and low rerun variance.

Recommend B only if:
- the user strongly prefers exact visible +/− point accounting;
- a held-out experiment demonstrates that contribution magnitudes are stable and interactions/double-counting can be controlled;
- additive/interacting contribution explanations predict user corrections better than anchor comparisons.

## 21. Migration impact

### Current data reusable

Strongly reusable:
- accepted Dossier observations/conflicts and provenance;
- exact profile pinning;
- gaming_taste_live.json rating history;
- all 120 rating + why_this_rating examples;
- contextual preferences and guardrails;
- current score_findings candidate/profile refs where still semantically valid;
- negative_assessment evidence;
- run-start authority / work identity / acceptance history;
- current collapsed/expanded score UI pattern;
- GitHub-owned deterministic validation/persistence architecture.

### Fields/concepts to retire from personal fit

Recommended retirement:
- five mandatory taste_factors;
- fixed factor enum in factor_impacts;
- 18/12/8/8/4 max points;
- current 50-point taste subscore semantics;
- current 60-point «personal» semantics as the definition of pure taste;
- requirement that every completed Deep fit explain all five buckets;
- legacy coarse fit as a value comparable to new personal-fit score.

Legacy data can remain immutable historical provenance, but must be visibly labelled legacy and never numerically mixed with the new model.

### Fields/concepts to separate

Move out of personal fit semantics:
- purchase price/savings/history — remain commercial purchase value;
- sale urgency — remains outside score;
- current wishlist — interest/context, not proof of enjoyment;
- current start priority / play role — separate future dimensions;
- platform/Windows friction — practical suitability, not necessarily taste.

Personal negatives like repetitive filler or opaque mandatory routine can remain inside personal fit when linked to profile evidence.

### Likely files/contracts affected by a future implementation

Not changed in this task, but likely future scope:
- config/final_ranking_policy.json
- scripts/priority_ranking.py
- config/progressive_pass2_result_schema.json
- config/progressive_pass2_worker_prompt.md
- config/progressive_pass2_contract.json
- scripts/progressive_pass2.py
- scripts/progressive_personalization.py
- scripts/card_explanation_policy.py
- scripts/build_final_visual_payload.py
- web/score-details-ui.js
- related score/Deep/card validation tests
- potentially a new dedicated personal-fit calibration contract/data artifact
- cross-repo usage of kentrap2011-hub/stopgame-ratings-data/gaming_taste_live.json remains read-only canonical input; changes to actual profile evidence continue through its canonical update path.

### Finite migration

Yes: current Deep results that are shown with a new 0–100 personal-fit score need finite reanalysis/recalibration.

Do not:
- reinterpret old 18/12/8/8/4 totals as new fit;
- linearly rescale old 50/60 score;
- mix old/new scores in one comparable sort.

Safe rollout:
1. build and validate new model offline;
2. freeze model/calibration version;
3. prepare finite GitHub-owned migration manifest for currently relevant Deep results;
4. reuse exact current Dossier/profile evidence where compatible;
5. accept new results only through existing bounded semantic worker + GitHub ingest principles;
6. mark unmigrated cards legacy/coarse;
7. switch ranking/display only after enough new comparable coverage exists.

Rollback:
- keep old accepted revisions immutable;
- new model has explicit version and separate fields;
- rollback selects previous contract/revision, not hand-edited numbers.

### RANK-013

Keep RANK-013’s **stage precedence** concept separate initially:
Deep fit > Fast fit > incomplete > not analyzed remains an orthogonal analysis-completeness/provenance decision.

Eventually RANK-013 may consume new personal_fit_score as one prepared input within completed stages, but this should be a separate ranking design decision.

Do not define personal fit by what helps the final sale ranking.

### Commercial purchase scoring

Keep separate.

Recommended long-term UI:
- Personal fit: 0–100 rating-equivalent.
- Purchase value: separate deterministic 0–100 or current transparent commercial scale.
- Final priority: separate policy combining/staging them only if the user wants one automatic order.

A 95/100 personal fit at a bad price remains 95 personal fit; the purchase recommendation can still be weak.

## 22. Proposed validation/experiment before implementation

Run a bounded offline backtest before changing any production contract.

### Dataset

Use a fixed, versioned subset of historical rated games from gaming_taste_live.json, stratified by:
- low/mid/high user rating;
- multiple genres/experience types;
- cases with strong positives;
- cases with strong negatives;
- cases whose why_this_rating shows mixed trade-offs.

Never reveal the held-out rating to the semantic evaluator for the prediction step.

### Compare

At minimum:
- Architecture A prototype;
- Architecture C prototype;
- Architecture D prototype;
- current five-factor baseline.

### Measures

Do not optimize only one number.

Evaluate:
- rank correlation with held-out user ratings;
- pairwise accuracy on higher-vs-lower rated games;
- calibration of predicted rating-equivalent bands;
- error magnitude;
- stability across repeated bounded semantic judgments;
- rate of unsupported findings;
- explanation correctness by manual audit;
- ability to catch known negative/deal-breaker examples;
- cross-genre calibration;
- score drift with unchanged evidence;
- semantic/runtime cost per candidate.

For pairwise models:
- graph connectivity;
- cyclic inconsistency;
- BT vs Thurstone model fit;
- sensitivity to anchor selection.

### User evaluation

Present a small blinded sample:
- candidate score;
- reasons;
- anchor comparisons;
- no architecture label.

Ask which explanation/relative placement feels correct. This directly tests controllability and trust, not only predictive error.

## 23. Unresolved questions

These should be answered by the experiment/user review, not guessed into the production contract:

1. Should direct historical 1–5 ratings be treated as interval-like anchors or only ordinal constraints?
2. How many anchors per new candidate give enough stability without excessive semantic cost?
3. Should anchor set have a fixed core plus candidate-specific contrast anchors?
4. Which pairwise model fits the user better: Bradley–Terry, Thurstone, tie-aware extension, or another ordinal model?
5. How should ties / “примерно одинаково” be encoded?
6. Should hard deal-breakers cap numeric score, force not-fit state, or both?
7. What uncertainty representation is easiest for the user: confidence label, interval, or both?
8. How large must a score change be before UI explicitly calls out «оценка изменилась»? No arbitrary threshold should be frozen before observing real variance.
9. Should Fast eventually produce only a coarse band while Deep produces calibrated score?
10. How should temporal taste change re-anchor older ratings without silently rewriting history?

## 24. Exact external sources

### Explainable recommendation
1. Yongfeng Zhang, Xu Chen. **Explainable Recommendation: A Survey and New Perspectives**. Foundations and Trends in Information Retrieval, 2020. DOI: https://doi.org/10.1561/1500000066

### Pairwise / ranking foundations
2. R. A. Bradley, M. E. Terry. **Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons**. Biometrika, 1952. https://www.jstor.org/stable/2334029
3. L. L. Thurstone. **A Law of Comparative Judgment**. Psychological Review, 1927. DOI: https://doi.org/10.1037/h0070288
4. R. L. Plackett. **The Analysis of Permutations**. Applied Statistics, 1975. DOI: https://doi.org/10.2307/2346567
5. Steffen Rendle et al. **BPR: Bayesian Personalized Ranking from Implicit Feedback**. https://arxiv.org/abs/1205.2618

### Human preference learning
6. Paul F. Christiano et al. **Deep Reinforcement Learning from Human Preferences**. NeurIPS 2017. https://proceedings.neurips.cc/paper/2017/hash/d5e2c0adad503c91f91df240d0cd4e49-Abstract.html
7. Long Ouyang et al. **Training language models to follow instructions with human feedback**. 2022. https://arxiv.org/abs/2203.02155
8. Lucas Maystre, Matthias Grossglauser. **Just Sort It! A Simple and Effective Approach to Active Preference Learning**. ICML 2017. https://proceedings.mlr.press/v70/maystre17a.html
9. Adish Singla, Sebastian Tschiatschek, Andreas Krause. **Actively Learning Hemimetrics with Applications to Eliciting User Preferences**. ICML 2016. https://proceedings.mlr.press/v48/singla16.html
10. William Muldrew et al. **Active Preference Learning for Large Language Models**. ICML 2024. https://proceedings.mlr.press/v235/muldrew24a.html
11. Rattana Pukdee, Maria Florina Balcan, Pradeep Ravikumar. **What Does Preference Learning Recover from Pairwise Comparison Data?** ICML 2026. https://proceedings.mlr.press/v306/pukdee26a.html

### Calibration / uncertainty
12. Chuan Guo et al. **On Calibration of Modern Neural Networks**. ICML 2017. https://proceedings.mlr.press/v70/guo17a.html
13. Harald Steck. **Calibrated Recommendations**. RecSys 2018. DOI: https://doi.org/10.1145/3240323.3240372

### Multi-attribute utility
14. Ralph L. Keeney. **Multiplicative Utility Functions**. Operations Research, 1974. DOI: https://doi.org/10.1287/opre.22.1.22

### LLM judge reliability
15. Lianmin Zheng et al. **Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena**. 2023. https://arxiv.org/abs/2306.05685

### Industrial recommender / embeddings
16. Paul Covington, Jay Adams, Emre Sargin. **Deep Neural Networks for YouTube Recommendations**. RecSys 2016. https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/
17. Heng-Tze Cheng et al. **Wide & Deep Learning for Recommender Systems**. 2016. https://research.google/pubs/wide-deep-learning-for-recommender-systems/
18. Joonseok Lee, Nisarg Kothari, Paul Natsev. **Content-based Related Video Recommendations**. 2016. https://research.google/pubs/content-based-related-video-recommendations/

### Source interpretation notes

- Bradley–Terry/Thurstone/Plackett–Luce and preference-learning papers support comparative preference modelling; they do not prove that one specific model will fit this user.
- Guo et al. support keeping confidence calibration explicit; their classification probability calibration should not be copied as if personal-fit score were a probability.
- Steck supports interest-distribution calibration, not scalar score calibration.
- Google embedding/industrial papers support retrieval/generalization patterns, not the claim that similarity equals personal preference.
- Architecture D is the worker’s proposal synthesizing these practices with the repository’s current evidence/provenance constraints.

## 25. Status

research_complete_ready_for_director_review

Research requirement is satisfied:
- four materially different architectures analyzed;
- external primary/first-party research included;
- 0–100 semantics defined;
- strong-factor, superficial-similarity, negatives/deal-breakers, uncertainty, anti-arbitrary safeguards, UI, feedback, ownership and migration addressed;
- three worked hypothetical examples included;
- current repository mapped only after independent design;
- no production implementation performed.

## 26. Recommended next step — exactly one bounded next action

Create one separate **READ-ONLY / OFFLINE EXPERIMENT** task that freezes a representative held-out subset of the existing 120 rating+reason examples and backtests Architecture D against Architecture C, Architecture A and the current five-factor baseline, measuring prediction quality, pairwise consistency, explanation auditability, rerun stability and runtime cost before any production contract is changed.

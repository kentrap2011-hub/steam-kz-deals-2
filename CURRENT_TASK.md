# CURRENT TASK

Последнее обновление: 2026-09-13

## Завершено

### Cross-platform claim-to-keep giveaway RECON 01
Статус: `complete`.
- worker task: `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_RECON_01.md`;
- выполнен только RECON: collector/UI/scheduling/production pipeline не изменялись;
- рекомендованный первый IMPLEMENT baseline: hardened Steam + Epic Games Store + GOG;
- Amazon Luna / Prime PC-game grants оставлены отдельным `subscription_entitlement` классом и не входят в universal claim-to-keep baseline;
- зафиксированы KZ fail-closed region policy, anti-false-positive predicates, store identity/dedup, normalized schema, single-writer ownership boundary и failure modes;
- текущий Steam `price_kzt == 0 && discount_percent > 0` трактуется как candidate discovery, а не достаточное доказательство temporary permanent-ownership giveaway;
- report: `reviews/worker_reports/cross-platform-giveaway-recon-01.md`;
- report commit: `1e6184d2235618336a5af402d76712f95b761adb`.

### Taste V3 migration
Статус: `complete`.
- исходная миграция Taste V3 была завершена и production-validated;
- model binding: `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`.

Текущий source snapshot также прошёл отдельный canonical Taste ingest recovery:
- 9 submission-файлов / 147 уже полученных Taste results ingested и receipted GitHub-owned workflow;
- ingestion commit: `cfadfd094c7a86ffbd4f43370a1bf42f47a79025`;
- receipt: `data/cache/taste_ingest_receipts/970f899a5219e41aa7d7.json`;
- safe cache hits: `492 -> 639` (+147), поэтому повторная Taste semantic оценка этих 147 результатов не требуется;
- после rebuild AI queue содержит ровно 3 строки (`App_1017030`, `App_1019930`, `App_1022850`) и каждая требует только `resolve_base_support_condition`; это штатная отдельная downstream semantic work, а не незавершённый Taste ingest.

### Steam fixed-package purchase options — verified complete-content valuation
Статус: `complete`.

Финальная acceptance:
- feature implementation: `80789541b1d3384324beb64ba1fa067f08149eab`;
- double-count regression: `b2680f5740d2a45ea23287c33b2263aafded9b9f`;
- regression run `33486496289`, job `99787681615`: fixed package tests `19 passed`, complete-content tests `6 passed`;
- refreshed pre-AI commit: `e6ba0081d74970338aefa82a25fb68b3b5a09b63`;
- refreshed visual commit: `24b2890d0c85b14213fd0b91256afcfb306eb01e`;
- visual build run `33486538903`, job `99787819857`: success;
- deploy run `33486561472`, job `99787892867`: success; Pages artifact `9791985882`;
- latest deployed BioShock control case keeps all 6 verified included items and shows `256 ₽` visible games + `173 ₽` verified incremental content = `429 ₽` comparable value vs `265 ₽` package, savings `164 ₽` (`38.2%`);
- Season Pass / constituent overlap regression proves one entitlement is counted once; no production-code fix was required;
- final acceptance report: `reviews/worker_reports/package-acceptance-02.md`.

Все пункты Definition of Done для этой fixed-package задачи подтверждены. Следующая planned-задача здесь не начата.

### Fix stale/wrong game image when swiping cards
Статус: `complete`.
- причина была в том, что старая картинка могла оставаться видимой, пока новый кадр ещё загружался;
- добавлен guard: старый foreground/blur очищается сразу, поздняя загрузка от предыдущей карточки игнорируется;
- regression моделирует быстрые переходы `A -> B -> C` и обратный переход с загрузками не по порядку;
- merge: `d10cfe40aed926f488e02e93d19c6c43037d8e93`; усиление regression: `8067c105ae6c2d7c3b9f7316d22ff17b475b20e2`;
- deploy run `33487711192`: success;
- worker report: `reviews/worker_reports/image-swipe-01.md`;
- финальная пользовательская проверка на реальном телефоне 2026-09-01: картинка больше не залипает при перелистывании.

### Compact purchase options — best option first, full list on demand
Статус: `complete`.
- worker task: `compact-purchase-options-01`;
- при нескольких вариантах покупки в свернутом состоянии показывается ровно один producer-selected primary route;
- `score_breakdown.purchase_route = fixed_package` показывает пакет первым, иначе primary остаётся standalone; UI не пересчитывает ranking/цены и не переигрывает producer choice;
- `Показать ещё N вариант/варианта/вариантов` раскрывает полный список, включая все regular offers и полный подтверждённый состав fixed package;
- длинный package composition/economics скрыт в compact mobile state;
- technical score/ranking phrasing заменён практическим объяснением того, какой способ покупки рекомендован и почему;
- deterministic mobile regression проверяет collapsed/expanded states, полноту expanded package content, отсутствие score/rank terminology и producer-route invariance;
- renderer: `fe8d99f2d202403f092cd072bb598c6f3fd969b4`; regression: `78ee55bc08a8833aac3a40cd768e836f88c96393`; styles: `fa83828df7db15afc7953a23c5821989038cd082`; asset wiring: `526107bf431cb7c861c11d868b12bf2555d33196`; deploy gate: `368224ca162f83b48cad32651fe42dde6d013c8a`;
- deploy run `33489817719`, rerun job `99798942975`: success; `Run UI regressions` success; GitHub Pages deploy success; Pages artifact `9793337134`;
- worker report: `reviews/worker_reports/compact-purchase-options-01.md`.

### Current Taste source ingestion
Статус: `complete_ingested_base_support_pending`.
- authoritative prepared Taste batch: 147;
- canonical workflow run `33440037739`, rerun job `99800543286`: success;
- proof fix разрешает ingest key оставаться после Taste ingest только как доказанный safe cache hit с `work_required=["resolve_base_support_condition"]` и canonical `requires_ai_base_support=true`;
- canonical receipt: `data/cache/taste_ingest_receipts/970f899a5219e41aa7d7.json`;
- все 147 Taste results persisted как safe cache hits; 9 inbox submissions canonical workflow удалил после receipt;
- оставшиеся 3 queue rows — только отдельная downstream base-support работа, не Taste re-evaluation и не ingest blocker;
- повторную semantic Taste evaluation 147 игр не запускать.

### Package/UI pre-AI blocker fix
Статус: `complete`.
- worker task: `package-ui-blocker-fix-01`;
- canonical pre-AI workflow был заблокирован stale static regression, который всё ещё ожидал старую форму `window.renderPackageDeal=function(g)`, старую score/rank-фразу и старый asset version, хотя compact purchase UI уже намеренно перешёл на IIFE + `root` exports и practical copy;
- исправлен только owning regression check, без изменения UI implementation, package economics, purchase-route semantics, ranking, Taste, duration или translation logic;
- fix commit: `c243dfe498abec27923bc7f229f34fc82b5c26f0`;
- canonical pre-AI run `33518894933`, job `99892817550`: success; fixed-package tests `19 passed`, complete-content tests `6 passed`;
- тот же run успешно прошёл translation contract/runtime validation (`9 tests`) и canonical Russian translation scope build;
- production scope опубликован автоматически commit `529795ca74db15508e5178c29090b113f9cda23d`: `translation_queue_count=155`, `resolved_direct_ru_count=389`, `nontranslatable_blocker_count=26`;
- report: `reviews/worker_reports/package-ui-blocker-fix-01.md`.

### Taste evidence state and confidence implementation 01
Статус: `complete` (internal Taste step 1; final Taste acceptance pending combined review).
- implementation: `2a1708ad598ea9baf7095478b646da689eb8f890`;
- report: `reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`;
- semantic states: `sufficient / insufficient / reconsiderable / confirmed_negative`;
- existing fit-cache semantic digest preserved; V5 evidence has separate exact contract binding;
- legacy ambiguous evidence backfills through existing `resolve_grounded_negative_analysis`; no new scheduler;
- HighFleet/Haven Moon/BioShock deterministic controls passed;
- Step 2 role/start and Step 3 commercial bridge are now implemented separately; final material acceptance remains pending the combined independent review.

### Play role and start priority implementation 01
Статус: `complete` (internal Taste step 2; combined final Taste Review remains pending after step 3).
- implementation: `19ff08128b09b9acb6cbe81f1789e0a5bba294ec`;
- report: `reviews/worker_reports/play-role-and-start-priority-implement-01.md`;
- roles: `main_full / secondary_palate_cleanser / family_coop / unresolved`;
- start priority: `high / ordinary / low / unresolved`;
- role/start remain separate from fit, wishlist and commercial sale urgency;
- `confirmed_negative` cannot receive high start priority;
- `priority_ranking.py` / final ranking policy unchanged; no second sorter/scheduler;
- Step 3 wishlist-good-deal/reconsideration bridge is now implemented and technically closed; combined final Taste Review remains pending.

### Reconsideration commercial bridge and wishlist implementation 01
Статус: `complete` (internal Taste step 3; final material Taste acceptance pending combined independent review).
- worker task: `WORKER_TASK_RECONSIDERATION_COMMERCIAL_BRIDGE_AND_WISHLIST_IMPLEMENT_01.md`;
- primary implementation: `0fddfd3fc58373645bb648348dd5dc013b347eea`;
- final downstream/contract closeout fix: `69baa039c30c7cbc1f266f2a4395656a2b71fad8`;
- final self-check: run `33979912267`, job `101343174589`: success;
- canonical wishlist route: exact ready V5 `insufficient` + Steam wishlist + moderate scenario `INCLUDE` + purchase decision `БРАТЬ СЕЙЧАС`;
- exact ready V5 `reconsiderable` may use existing strict fixed-`Sub_` package savings while Taste remains `EXCLUDE / below_moderate`;
- exact V5 `confirmed_negative` / direct confirmed conflict remains non-rescuable; legacy `exclude_direct_conflict` reason alone is not V5 confirmation;
- role/start, warnings/risks, ranking weights, giveaway and package-equivalence semantics remain unchanged;
- current production payload is still degraded on existing V5 backfill (`379`) with `0` current reconsiderable package candidates; canonical final producer fail-closes as expected and no semantic queue was fabricated;
- report: `reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`, report commit `1f843dd55edb3811820cf7b616889a7e17fcd84f`;
- all temporary Step-3 helpers/workflows were removed after validation.

## Завершённые package-инварианты, которые сохраняются

- только fixed Steam Store Package (`Sub_`);
- dynamic/personalized Complete-the-Set `/bundle/` исключён fail-closed;
- exact included appid + explicit verified directional purchase equivalence; title/fuzzy remaster guessing запрещён;
- package info может быть visible без ranking boost;
- Taste не меняется от цены;
- fresh commercial refresh обновляет standalone commercial fields независимо от semantic queue;
- scorer сравнивает standalone и eligible package routes без stacking одного и того же commercial value;
- verified top-level DLC/content может добавлять commercial value только при детерминированном current KZ acquisition route;
- unknown/unpriced и nonpersonalized content не получают выдуманную персональную стоимость;
- Season Pass / edition constituent content не считается рекурсивно второй раз.

## Не активная основная работа

### SteamDB tail
Статус: `blocked_low_priority`.
- `App_901735` remains blocked/retryable;
- exact Kazakhstan historical minimum remains unproven and must not be fabricated.

## Запланировано / выполняется

### Taste pre-AI deal contract guard fix implement 01
Статус: `in_progress`.
- worker task: `WORKER_TASK_TASTE_PRE_AI_DEAL_CONTRACT_GUARD_FIX_IMPLEMENT_01.md`;
- scope: только exact-version guard для canonical deal-quality contract, focused regression и штатный pre-AI refresh/acceptance;
- canonical contract version: `1.5`; stale expected version в builder: `1.3`;
- fail-closed для wrong/missing/malformed contract должен сохраниться;
- Taste canary в этой задаче не запускать; Prototype output не использовать;
- существующий Taste Semantic Producer `6a9d6fdddc00819193ed670d782045c4` должен остаться выключенным;
- запрещены второй Scheduled Task/producer, новая generation и ручная правка queue/cache/receipt.

### Taste Steps 1–3 production materialization acceptance 01
Статус: `blocked_semantic_runtime`.
- worker task: `WORKER_TASK_TASTE_STEPS_1_3_PRODUCTION_MATERIALIZATION_ACCEPTANCE_01.md`;
- priority: `VERY_HIGH_USER_PRIORITY`; не переключаться на giveaway/ITAD или другой backlog до снятия production gate;
- reviewer recommendations A1/A2 implemented and regression-covered: Batman/RDR2 positive-exception guards + fail-closed static role/start profile provenance revalidation;
- current canonical V5 semantic scope: `701`, resolved `0`, unresolved `701`, `sufficiently_complete_for_publication=false`;
- runtime owner remains the existing `scheduled ChatGPT production task`; repository observability says `no_current_scope_progress_observed` after current source update `2026-09-03T18:53:27.390807+00:00`;
- no second semantic scheduler/queue was created and interactive chat did not manually process the 701-row backlog;
- deterministic acceptance snapshot: `data/cache/taste_steps123_production_acceptance.json`;
- validation run `34010651477`: success; execution ownership run `34010651478`: success;
- all 10 required controls are recorded in the acceptance snapshot; HighFleet is `semantic_pending_current_scope` and its confirmed-negative guard forces `unresolved / low`, while the current visual HighFleet row is explicitly not accepted as new Taste evidence;
- downstream final regeneration/deploy intentionally not run while semantic completeness is false;
- report: `reviews/worker_reports/taste-steps-1-3-production-materialization-acceptance-01.md`;
- exact unblock: resume/repair the same existing scheduled semantic producer so current V5 results arrive through the canonical inbox/ingest path; only after legitimate completeness may GitHub-owned downstream regeneration/deploy and user-site verification proceed.

### A. Ranking and card explanation quality audit
Статус: `planned`.
- audit минимум top-30 + boundary cases;
- trace `evidence -> Taste factors -> personal/purchase score -> rank -> card explanation`;
- высокий rank не должен необъяснимо получаться из одного слабого generic factor;
- служебная фраза вроде `Игра прошла строгий вкусовой отбор` не считается плюсом;
- каждая visible recommendation должна иметь минимум один конкретный содержательный плюс и минимум один доказуемый минус/ограничение/trade-off;
- `Подтверждённых персональных рисков не найдено` не считается минусом;
- если evidence недостаточно для содержательных плюса/минуса, карточка считается incomplete и требует enrichment, а не placeholder;
- добавить score/explanation regression guards.

### A1. Card explanation implementation 01
Статус: `in_progress`.
- worker task: `WORKER_TASK_CARD_EXPLANATION_IMPLEMENT_01.md`;
- цель: исправить подтверждённые audit-дефекты positive `why_fit` и consistency negative `risks[]` в текущем canonical producer path;
- ranking weights, giveaway, duration, translation, package и unrelated UI не меняются;
- другая параллельная работа F сохраняется без изменений.

### Normal Taste semantic producer 01
Статус: `blocked_requires_followup`.
- worker task: `WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md`;
- START gate из актуального `CHAT_PROTOCOL.md` выполнен до task-specific реализации;
- linked age-priority worker: `WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`;
- canonical age authority доказан: `data/cache/taste_fit.json` → accepted entry `evaluated_at_utc`;
- implementation gate не пройден: текущий active exact-10 pin `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20` ещё не имеет terminal verified receipt;
- latest terminal receipt `ba86bfdcf8365dfa0195` относится к предыдущему grandfathered batch и сам зафиксировал этот SHA как `next_work_unit_sha256`;
- active pin не переупорядочен и не изменён; source/runtime artifacts не менялись;
- существующий Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` не изменялся, второй producer/scheduler не создавался;
- age report-first: `reviews/worker_reports/taste-queue-age-priority-order-01.md`, commit `6da7f006497fc6a3d849e14c9b2ed20644d47c44`;
- parent report: `reviews/worker_reports/taste-normal-semantic-producer-01.md`, initial commit `8fb4eb40b03ec8841013f49af2b7b0d2d301466e`;
- exact unblock: existing producer must finish and canonically ingest the current exact-10 pin; after terminal receipt, rerun this worker to implement age-ordering for newly constructed pins and prove `complete_ready_for_normal_scheduled_producer` before changing prompt/cadence.

### Steam review dossier preparer 01
Статус: `complete_ready_for_separate_scheduler_and_clean_throughput_measurement`.
- worker task: `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PREPARER_01.md`;
- mode: `IMPLEMENT_AND_VALIDATE` completed;
- implemented separate GitHub-owned scope/freshness/validation/persistence + fail-closed Taste dossier handoff;
- default TTL 20 days, adaptive Russian/non-Russian Steam review sampling contract and compact neutral schema implemented;
- validation: 11/11 regressions + end-to-end CLI smoke passed;
- current active pin and `scripts/taste_pinned_work_unit.py` remained unchanged;
- existing Taste Semantic Producer unchanged; no Scheduled Task created; old throughput measurement not continued;
- report: `reviews/worker_reports/taste-steam-review-dossier-preparer-01.md`.

### Full Steam review dossier backlog continue 01
Статус: `in_progress`.
- worker task: `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_FULL_BACKLOG_CONTINUE_01.md`;
- branch: `worker/taste-dossier-full-backlog-01`;
- START gate и architecture preflight выполнены; GitHub остаётся владельцем full backlog scope, checkpoint progression, durable persistence и completeness;
- подтверждены все 6 handoff-коммитов; активный Taste pin остаётся downstream-only и не используется как total dossier scope;
- реальный production dossier backlog и Scheduled Tasks в этой работе не запускаются и не изменяются;
- next gate: закрыть Phase A item 7 в `PROJECT_DECISIONS.md`, затем исправить checkpoint progression/eligibility и пройти regression matrix до безопасной интеграции в `main`.

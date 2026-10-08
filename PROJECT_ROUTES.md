# PROJECT_ROUTES

Практическая карта маршрутов проекта. Это быстрый индекс уже исследованных участков, чтобы будущий чат не восстанавливал структуру проекта заново.

## Как вести карту

- Не описывать весь проект заранее. Добавлять маршрут только тогда, когда он реально понадобился в текущей работе и был найден/проверен.
- Перед широким поиском по репозиторию сначала проверить, есть ли нужная тема здесь.
- Если маршрут есть, начинать с указанных точек входа, state/validation-файлов и workflow, а не перечитывать дерево репозитория и историю коммитов.
- Если во время задачи пришлось заметно разбираться, где находится нужная логика или кто ею владеет, найденный путь нужно сохранить или уточнить здесь до завершения подзадачи.
- Не дублировать здесь канонические business rules: при конфликте contract/policy имеет приоритет.

---

## Исторический минимум SteamDB (KZ / KZT)

**Что ищем:** точный исторический минимум цены SteamDB для текущих primary offer keys.

**Последняя проверка:** 2026-08-31

**Канонический контракт:**
- `config/steamdb_lookup_contract.json`
- `config/steamdb_checkpoint_contract.json`
- ownership: `config/execution_ownership_contract.json`

**Быстрая точка входа:**
1. `data/cache/steamdb_runtime_work.json` — текущая GitHub-derived незакрытая работа.
2. При unresolved/retry проверять GitHub → external runtime → GitHub handoff; не искать исторические минимумы вручную в interactive chat.
3. После runtime submissions проверить ingest/completeness, validation/checkpoint и downstream.

**Маршрут данных:**
1. GitHub определяет true misses → `data/cache/steamdb_miss_manifest.json`.
2. Runtime state → `data/cache/steamdb_runtime_state.json`.
3. Незакрытая работа → `data/cache/steamdb_runtime_work.json`.
4. Внешний runtime-worker возвращает факты в `data/inbox/steamdb_runtime/*.json`.
5. GitHub ingest → `.github/workflows/ingest-steamdb-runtime-submissions.yml` + `scripts/ingest_steamdb_runtime_submissions.py`.
6. После полного resolution → `data/cache/steamdb_web_resolutions.json`.
7. Validation → `scripts/validate_steamdb_runtime_resolutions.py` → `data/cache/steamdb_lookup.validation.json`.
8. Checkpoint → `data/cache/steamdb_history.json`.
9. Downstream → `scripts/build_pre_ai_history_snapshot.py` → `data/production/pre_ai/history_snapshot.json`.

**Текущее состояние:** 9 ожидаемых ключей, 8 resolved, 1 unresolved retry — `App_901735`. Для него сохранены две transient ошибки `steamdb_runtime_disabled_error`; interactive chat не должен подменять runtime ручным lookup.

---

## Taste V3 / normalized factors

**Что ищем:** текущий semantic scope Taste V3, exact bindings, inbox submissions, canonical ingest и downstream propagation пяти нормализованных price-blind факторов.

**Последняя проверка:** 2026-08-31
**Проверенный recovery ref:** после commit `31a3f3e2b84185ab32cf0a4e5bbdf1776681331b`.

**Канонические контракты:**
- `config/taste_result_contract.json` — допустимый semantic result и exact binding requirements;
- `config/taste_cache_entry_contract.json` — canonical cache entry;
- `config/execution_ownership_contract.json` — GitHub владеет scope/queue/validation/persistence, scheduled ChatGPT только semantic data-plane;
- `config/daily_execution_contract.json` — один nightly production cycle, batch не является суточной квотой.

**Быстрая точка входа — читать в таком порядке:**
1. `data/production/pre_ai/chatgpt_payload.json` — количество текущей AI queue и canonical model/profile binding.
2. `data/production/pre_ai/taste_projection.json` — exact global binding, с которым обязан совпасть submission.
3. `data/production/pre_ai/chatgpt_taste_queue.jsonl` — открывать только конкретный key/строку, а не весь файл без необходимости.
4. `data/ai_inbox/taste/` — только список submission-файлов; полный большой JSON не читать, если достаточно metadata или точечного key.
5. `.github/workflows/ingest-taste-batch.yml` → `scripts/process_taste_inbox.py` → `scripts/ingest_taste_results.py` — единственный штатный ingest path.
6. После ingest проверять компактные `data/cache/taste_fit.entry_index.json`, `data/cache/taste_ingest_receipts/`, новый `chatgpt_payload.json` и только bounded downstream diagnostics.

**Критический recovery-инвариант:**
- submission с несовпадающим top-level `profile_blob_sha` / `taste_model_version` / `taste_semantics_sha256` / source binding нельзя «починить» простым переименованием полей;
- сначала доказать, что semantic worker действительно выполнил **тот же** канонический semantic contract. Без такого доказательства exact binding validator должен остаться fail-closed;
- механическое совпадение отдельных key/fingerprint/context не доказывает semantic equivalence всей оценки;
- не обходить `ingest_taste_results.py` и не писать результаты напрямую в canonical cache.

**Anti-stall / экономия контекста:**
- для состояния очереди не считать строки вручную: брать `ai_queue_count` из `chatgpt_payload.json`;
- для provenance сначала сравнить bindings одного submission с `taste_projection.json`, а не читать все 500 результатов;
- при failed ingest открыть один конкретный run → job → log; не polling и не repository-wide search;
- если требуется простая визуальная проверка существующей scheduled-задачи ChatGPT, сначала попросить пользователя открыть её настройки/текст prompt и прислать нужный фрагмент; не тратить контекст на обходные поиски, если пользователь может проверить это напрямую.

**Текущее recovery-состояние:**
- canonical pre-AI snapshot перед ingest: `ai_queue_count=634`;
- опубликовано пять файлов `data/ai_inbox/taste/2026-08-31T0630Z-001..005.json`, по 100 результатов каждый;
- все пять имеют одинаковую stale/noncanonical global binding: model `price_blind_taste_v3`, semantic digest `fc0e4846…`, source timestamp `2026-08-30T14:27:39Z`, тогда как текущая canonical projection использует `taste-v3` и другой semantic digest/source snapshot;
- в `001` дополнительно подтверждён typo `App_1261040.taste_fingerprint`: лишняя завершающая `a`;
- one-shot repair run `33372236792` корректно остановился fail-closed на global binding mismatch до commit/persistence; ошибочный helper затем удалён commit `31a3f3e2b84185ab32cf0a4e5bbdf1776681331b`;
- эти 500 результатов **не считать ingested/canonical** и не relabel-ить без проверки provenance существующего scheduled semantic worker;
- следующий шаг — проверить конфигурацию/инструкцию именно существующего scheduled worker и установить, почему он записал старую binding-метку. Если semantic contract реально был старым — результаты нужно переоценить штатным worker-ом; если contract был текущим, а ошибочна только serialization/binding metadata, эквивалентность нужно доказать до bounded migration.

---

## Финальная сортировка / прозрачный рейтинг 0–100

**Что ищем:** где формируется production ranking, из каких баллов он складывается и как локальная мобильная очередь может его отображать.

**Последняя проверка:** 2026-08-30
**Последний успешный production build:** GitHub Actions run `33325344781` (`Build daily visual payload`, run 64) — success.
**Последний успешный deploy:** run `33325360599` (`Deploy visual mailing`, run 100) — success.
**Production payload commit:** `491b1660dcca7a4b069978c29e9ff46e071252e2`.

**Сначала открыть:**
1. `config/final_ranking_policy.json` — канонический источник весов и production ranking contract.
2. `PROJECT_DECISIONS.md` → `RANK-001..RANK-011`, `UI-001`.
3. `scripts/priority_ranking.py` — config-driven scorer.
4. `scripts/validate_priority_ranking.py` — regression guard production ranking.
5. `web/app.js` — local queue/view overrides поверх готового payload.
6. ownership: `config/execution_ownership_contract.json`.

### Production ranking

**Канонический контракт:** `FINAL-PRIORITY-RANKING-V2`.

Production `priority_rank` строится только GitHub producer-ом и означает позицию в обычной Deep-first ленте:
1. `ranking_stage_asc` — `deep_fit → fast_fit → analysis_incomplete → not_analyzed`;
2. `stage_score_desc` — для Deep/Fast это видимый `total_score` 0–100, для unresolved/not-analyzed — существующий deterministic purchase-only score;
3. `title_asc` / ID — deterministic fallback.

Срочность находится вне 100 баллов, не меняет сам score и не входит в default production `priority_rank`. В явно выбранном режиме «Срочные» она применяется браузером только внутри опубликованного producer-owned `ranking_stage`.

`total_score = personal_score + purchase_score`:
- personal: максимум 60;
- purchase: максимум 40.

Personal:
- taste до 50;
- wishlist до +4;
- achievements до +3;
- duration до +3;
- risk до −12.

Purchase:
- `savings` до 20 — `max(0, original_price_rub - current_price_rub)`;
- current price до 12;
- history до 8.

`discount_percent` остаётся отображением/context и не даёт V2 score сам по себе.

### Локальные режимы очереди в UI

Production ranking **не меняется**. В `web/app.js` есть отдельный локальный view-mode:

- кнопка **`⏱ Срочные` выключена (default)** → локальная очередь следует готовому production `priority_rank`: `stage → stage score → title/id`;
- кнопка **`✓ Срочные` включена** → локальный view-mode: `stage → urgency → stage score → title/id`; срочность никогда не пересекает границу Deep/Fast/unresolved;
- выбранный режим хранится в localStorage как `state.settings.urgency_first`;
- `QUEUE_VERSION=5` заставляет старое состояние один раз пересобрать очередь по новому default;
- при переключении `buildQueue()` сохраняет текущую открытую игру, если она остаётся активной;
- UI не выводит semantic stage из истории или значков: default использует producer-owned `priority_rank`, а explicit urgency view — опубликованные `ranking_stage_rank`, `sale_expiry_urgency_rank` и stage score.

**Критически:** `manual_end_at` («В конец очереди») остаётся абсолютным локальным override в обоих режимах. `canonicalQueueIds()` сначала формирует automatic order, затем всегда отделяет manual items и ставит их после automatic items; manual items сохраняют порядок по времени отправки в конец.

`renderPriority()` учитывает локальный режим:
- без срочности показывает позицию в текущей очереди и явно пишет, что срочность сейчас не влияет на порядок;
- со срочностью может показывать canonical production comparison;
- у вручную отправленной в конец игры явно пишет про manual override.

### Taste precision

Большинство старых taste-cache записей пока имеют только `strong/moderate`, поэтому V2 использует явный fallback:
- strong → 42/50;
- moderate → 34/50;
- `score_precision=legacy_coarse_fit`.

Следующая отдельная ranking-задача в `BACKLOG.md` — детальные normalized price-blind taste factors 0..100.

### Production-путь

1. `.github/workflows/build-daily-visual-payload.yml` → `scripts/validate_priority_ranking.py`.
2. `scripts/build_final_visual_payload.py` — единственный final producer.
3. `scripts/priority_ranking.py::apply_final_priority_order()` считает score и production rank.
4. Итог → `data/production/visual/current.json`.
5. Full audit → `ranking_review.jsonl`.
6. Bounded diagnostics → `data/production/visual/ranking_lookup/<bucket>.json`.
7. `web/app.js` читает готовые поля и применяет только local queue/view overrides.

### Проверенный пример

**High On Life:** 62.5/100, production rank 220.
**Seraph's Last Stand:** 44.5/100, production rank 348.

High On Life выше по score благодаря wishlist, отсутствию серьёзного риска и большей реальной экономии. Seraph получает +12/12 за низкую текущую цену, но её экономия 17 ₽ даёт 0/20 и серьёзный риск даёт −10.

### Regression / invariants

Production validator проверяет:
- canonical Deep-first stage → stage score → title/id;
- explicit urgency view не пересекает ranking-stage boundary;
- 60 + 40 = 100;
- ruble savings вместо discount percentage;
- risk/wishlist/achievements/duration weights;
- `manual_end_at` UI invariant.

Для local UI режима обязательные implementation-инварианты:
- default `urgency_first=false`;
- off-mode следует готовому canonical `priority_rank`;
- on-mode применяет urgency только внутри producer-owned `ranking_stage`;
- mode входит в queue signature, поэтому переключение реально пересобирает очередь;
- manual items всегда добавляются после automatic items;
- `sendCurrentToEnd()` остаётся без изменения семантики.

**Открытые отдельные задачи:**
- детальный taste-factor migration;
- automatic Windows compatibility evidence-source;
- оставшиеся SteamDB retry (пользователь отложил).

---

## Taste Steam review dossier: non-blocking per-group progress and immutable recovery

**Что ищем:** как Scheduled ChatGPT публикует immutable predeclared 3-game candidates, а GitHub независимо классифицирует каждую группу как `pending`, `accepted` или `failed_or_invalid_pending_recovery` без head-of-line blocking.

**Последняя проверка:** 2026-09-27.

**Быстрая точка входа:**
1. `config/taste_steam_review_dossier_contract.json` — canonical GitHub-owned per-group progress/completeness contract; `checkpoint_size=3` остаётся transport/group boundary, не quota.
2. `scripts/taste_steam_review_dossier_group_progress.py` — canonical state transitions, counts, `next_pending_sequence`, normal-first-pass vs all-accepted semantics.
3. `scripts/taste_steam_review_dossier_buffered.py` + `scripts/taste_steam_review_dossier_strict.py` — strict independent validation/persistence; invalid transport quarantine affects only its exact group.
4. `scripts/taste_steam_review_dossier_worker_projection.py` — V2 compact index; worker resumes from GitHub-owned next pending group, not first historical failure.
5. `scripts/taste_steam_review_dossier_parallel_validation.py` — validation/recovery observability; not queue/progress authority.
6. `scripts/taste_steam_review_dossier_recovery.py` — separate GitHub-owned failed-group recovery after normal first pass; no automatic semantic retry.
7. Exact shared-writer inventory: `.github/workflows/build-pre-ai-store-snapshot.yml`, `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`, `.github/workflows/ingest-progressive-pass1.yml`, `.github/workflows/ingest-progressive-pass2.yml`, `.github/workflows/authorize-progressive-pass2-recovery.yml`; all use the single `taste-steam-review-dossier-canonical-writer` boundary and state-reconcile current Dossier inbox before dependent Deep projection/write.
8. `scripts/test_taste_dossier_canonical_writer_coalescing_liveness.py` — regression for cancelled/coalesced zero-job Dossier wake-up, exactly-once classification, idempotence and post-reconcile Deep visibility.
9. `scripts/stage_taste_dossier_canonical_writer.sh` — real ingest staging helper: mandatory canonical paths fail closed, optional `data/control` / `data/quarantine` / `data/audit` are staged independently, and `assert-clean` proves no tracked/untracked leftovers before rebase/push.
10. `scripts/test_taste_dossier_github_date_derivation.py` + `scripts/test_taste_dossier_ingest_atomic_staging.py` — focused DATE-01..10 and real Git staging/clean-worktree regressions.
11. `config/taste_steam_review_dossier_worker_prompt.md` — create-only semantic data-plane rules; worker supplies factual publication dates/null only, while GitHub derives temporal state.

**Runtime / recovery-инварианты:**
- create-only deterministic transport remains immutable and is not canonical acceptance;
- every present pending group is strict-validated independently; valid later groups may persist even when an earlier different group failed;
- invalid group is recorded `failed_or_invalid_pending_recovery`, moved out of normal forward progress and remains separately recoverable;
- missing pending group remains pending but does not prevent processing another present pending group;
- accepted and failed groups are excluded from normal first-pass traversal; future worker invocations start from `next_pending_sequence`;
- `normal_first_pass_complete=true` means no pending groups remain; `full_backlog_complete` retains the stricter legacy/all-accepted meaning and failures never count as accepted evidence;
- Scheduled ChatGPT cannot overwrite/rename/delete transport, own retry/completeness, or enable/disable/edit its own schedule;
- snapshot/plan/binding exactness, strict dossier semantics, story-DLC scope, Russian retrieval/provenance and stale-snapshot isolation remain fail-closed;
- current/historical temporal qualification uses GitHub-derived state from actual bound feedback-record publication dates; unknown date never qualifies as recent;
- failed-group audit/quarantine are canonical outputs and must be staged atomically with progress; no optional-path failure may hide another path, and the local canonical commit must leave a clean worktree before rebase/push;
- old snapshot artifacts never rebind to a new snapshot; same-snapshot descriptors stay immutable.
- Dossier wake-up events are advisory only: durable repository state is authoritative, so cancellation/coalescing of the original zero-job wake-up cannot strand a current candidate while another shared writer survives.


---

## Progressive Fast / Dossier / Deep: stage architecture and Deep recomputation boundary

**Что ищем:** canonical Fast/Dossier/Deep semantics, effective-result precedence, Deep first-pass/recovery ownership and the reusable GitHub recomputation hooks.

**Последняя проверка:** 2026-09-27.

**Быстрая точка входа:**
1. `config/progressive_personalization_contract.json` — canonical three-stage model, effective-result precedence, explicit UI stage states and statistics-page metric contract.
2. `config/progressive_pass1_contract.json` — PASS 1 as provisional user-facing `Быстрый разбор`; no Dossier requirement and no Fast prerequisite for Deep.
3. `config/progressive_pass2_contract.json` — technical PASS 2 as eventual authoritative `Глубокий разбор`, all-current-game coverage target, one normal first pass plus separate GitHub-owned recovery authorization model; production-active under current `FAST-DOSSIER-DEEP-V1` contracts.
4. `config/taste_steam_review_dossier_contract.json` — independent neutral Dossier acceptance/recovery truth; buffered/failed candidates never count as accepted Deep evidence.
5. `config/execution_ownership_contract.json` — GitHub owns Deep scope/order/first-pass/recovery/completeness; under the current production-active architecture Scheduled ChatGPT is only the bounded Deep semantic data plane, while scheduler configuration remains outside repository-owned execution.
6. `scripts/progressive_pass2.py::recompute_eligibility` + `scripts/build_progressive_pass2_work.py` — runtime-adapted `FAST-DOSSIER-DEEP-V1` recomputation: all-current Deep first-pass scope, no Fast prerequisite, explicit authoritative-completion exclusion and separate GitHub-authorized recovery.
7. Recompute hooks exist after canonical Dossier persistence, Fast/PASS 1 persistence, daily/current generation-work-binding-freshness preparation, Deep/PASS 2 persistence, and explicit Deep recovery authorization.
8. Those writers remain inside `taste-steam-review-dossier-canonical-writer` with `cancel-in-progress:false`; do not split them into unsynchronized authority domains.
9. `PROJECT_DECISIONS.md#PPD-004` — rationale for Fast/Dossier/Deep independence, Deep precedence, all-game coverage and non-blocking recovery.
10. `PROJECT_DECISIONS.md#PPD-006` + `#PPD-007` + `#PPD-008` — V2 creates one nonce-only marker first; the marker commit's actual Git parent is the GitHub-selected immutable Deep authority, then the worker freezes the exact PASS 2 contract/work/profile/Dossier/recovery view from that parent; a durable confirmed GitHub receipt remains mandatory before first semantic transport.
11. `config/progressive_pass2_worker_prompt.md` + `scripts/test_progressive_async_traversal.py` — bounded worker timing and regressions for delayed/missing/rejected confirmation, authority equality, no pre-confirmation publication and continued sibling traversal.
12. Dossier statistics source: `data/production/pre_ai/taste_steam_review_dossier_work.json` → `scripts/progressive_personalization.py::_dossier_processing_metrics()` → `processing_status` in `data/production/visual/current.json`; browser only renders that prepared block.
13. Dossier progress activation: successful `Ingest Steam review dossier checkpoint` completion is an upstream `workflow_run` trigger for `.github/workflows/build-daily-visual-payload.yml`, parallel to Fast/Deep ingest triggers; no second scheduler is used.
14. Visual freshness binds the published statistics to `source_taste_steam_review_dossier_work_blob_sha`; `scripts/progressive_visual_activation_routing.py` forces a full Progressive rebuild on Dossier-manifest drift instead of allowing a bounded commercial/giveaway refresh to preserve stale counts.
15. Publication remains `.github/workflows/build-daily-visual-payload.yml` → `scripts/build_final_visual_payload.py` → `data/production/visual/current.json` → `.github/workflows/deploy-visual.yml` → `web/data/current.json`.
   - full-build persistence is guarded by `scripts/visual_material_freshness_guard.py`: rejected push compares exact material blobs rather than whole `HEAD`; material drift forces one fresh-main rebuild, a second drift fails closed, and `scripts/visual_freshness_receipt.py` verifies the same bindings before deploy.
16. Positive card explanation path: current exact-compatible semantic entry (`Deep > Fast > reusable cache`) is selected in `scripts/progressive_personalization.py`; authoritative Deep entries are materialized by `scripts/progressive_pass2.py::semantic_taste_entry()` with accepted-state identity and `positive_evidence`.
17. User-facing `Почему может зайти` is rendered only through `scripts/card_explanation_policy.py::positive_reasons()`; both `scripts/build_visual_feed_v2.py` and the final canonical `scripts/build_final_visual_payload.py` use that shared fail-closed policy. Deep positives carry `positive_evidence_binding` into `why_fit_provenance.semantic_binding`; stale/unbound Deep is excluded earlier by exact binding matching.
18. Explanation acceptance guard: `scripts/test_card_explanation_policy.py` is exercised from the PASS 2 core regression, and `scripts/validate_card_explanations.py` rejects ungrounded visible positives and, for Deep cards, missing/mismatched accepted-state provenance.
19. Balanced Deep negative path: `PROJECT_DECISIONS.md#PPD-009` + `config/progressive_pass2_result_schema.json` require every new completed Deep result to evaluate the exact accepted Dossier negative/mixed observations and conflicts. `scripts/progressive_pass2.py` validates exact Dossier refs and preserves historical missing fields as `legacy_not_evaluated`; `scripts/refine_visual_ranking.py` sends only explicit `confirmed_personal_risk` findings through existing risk codes/policy, while `scripts/card_explanation_policy.py::deep_cautions()` and `scripts/build_final_visual_payload.py` expose grounded display-only cautions without a new penalty. `scripts/test_deep_balanced_negative_assessment.py` is the bounded Jedi transport/projection regression; it is not production semantic truth for any specific Jedi finding.
20. Dossier/Deep year-kind compatibility: `PROJECT_DECISIONS.md#PPD-011` + `config/dossier_deep_identity_compatibility_contract.json` define Dossier `game_identity.release_year` as original/work identity evidence and Progressive semantic-input year as Steam/storefront context. `scripts/progressive_pass2.py::dossier_is_eligible` keeps exact AppID/title/resolved/current-binding/freshness fail-closed while forbidding cross-kind year equality as a hard gate; `scripts/test_dossier_deep_release_year_identity_compatibility.py` enumerates the eight historical false rejects and wrong-product regressions.
21. Profile semantic identity stability: `PROJECT_DECISIONS.md#PPD-012` separates content-based `profile_semantic_sha256` from exact immutable `PROGRESSIVE-PROFILE-PIN-V1` execution provenance. `scripts/progressive_pass1.py` derives global/item semantic identity from profile blob/content plus model/semantics/context, while `historical_semantic_equivalence()` may keep an immutable accepted Fast/Deep result current only after its exact `work_authority_commit` manifest proves identical profile content and semantic/item bindings. Exact worker transport still echoes the current prepared provenance pin; missing or inconsistent historical proof fails closed. `scripts/test_progressive_profile_semantic_identity_stability.py` covers commit-only churn, real invalidators, exact transport provenance, PPD-010 reconciliation and no re-emission.


**Bundle / 429 continuation after PR #148:**
- normal main run `37345668260` completed games (`63,645`, 637 pages, ~1573s) and DLC (`34,342`, 344 pages, ~822s), then timed out inside standalone `category1=996` at `48,000 / ~105,326` rows; Reviews had not started;
- by timeout Search logged 192 HTTP 429 responses and 2160s accumulated backoff; the stable pattern was four 429s (`3/6/12/24s`) about every 30 successful 100-row pages;
- bounded PR #151 evidence proved standalone `category1=996` is not bundle-only: it matched the no-category broad scope at ~105.3k rows and sampled overwhelmingly ordinary `App_` rows, including DLC/soundtracks/extras;
- a representative purchasable package, `Sub_76471` / “Daedalic - Gigantic Bundle”, was returned under `category1=998` as well as `996`; therefore package opportunity semantics are preserved inside the games traversal and the redundant standalone 996 crawl is removed;
- `category1=998,996` had the same total as games-only and `21,996` the same total as DLC-only in bounded controls, reinforcing that 996 is additive rather than an exclusive bundle class;
- live pacing probe: 0.5s cadence produced 14×429 in 35 requests (first at request 22 in that shared rate window); after cooldown, 1.8s produced 35/35 HTTP 200 with no 429; `Retry-After` was absent. Production Search pacing is therefore 1.8s while the existing explicit retry ladder remains unchanged.

**Инварианты:** Deep eligibility never requires prior Fast/PASS 1 attempt or Fast `analysis_incomplete`; the V2 marker contains no worker-chosen authority and its actual Git parent is the frozen invocation authority; the worker reads/fixes all PASS 2 work/profile/Dossier/recovery inputs only from that parent; a write before the marker is part of that view, while later parallel `main` movement belongs to the next invocation and does not invalidate the current one; no Deep result/terminal receipt may be published until GitHub durably confirms the same marker-parent authority and lineage; missing/rejected/mismatched confirmation consumes no attempt and publishes nothing; exact-compatible canonically accepted Dossier remains the evidence gate; completed authoritative Deep suppresses future Fast for the same current identity while Fast success never suppresses Deep; Deep incomplete/error does not erase a valid Fast provisional result; unresolved consumed Deep becomes recovery-owned and can return only through a fresh concrete GitHub-owned recovery authorization; normal Deep first-pass completeness and eventual all-authoritative completeness are separate; no blind retry loop or hidden recovery quota; Deep semantic execution remains forbidden while active flags are false.


## Russian game descriptions — direct Steam source to publication

Use this route for Russian-description resolution, translation observability, or publication diagnostics.

1. GitHub-owned pre-AI scope: `scripts/build_russian_description_translation_queue.py` calls `scripts/russian_description_translation_runtime.py`.
2. Direct Russian precedence inside that runtime:
   - exact-app `IStoreBrowseService/GetItems(language=russian)`;
   - if that is not `good_ru`, exact-app official Steam `/api/appdetails?cc=kz&l=russian`;
   - a `good_ru` appdetails description remains a direct Russian source;
   - if StoreBrowse has no already-translatable source and exact-app appdetails contains meaningful `non_ru` / `weak_ru` text, preserve that exact text and app provenance only as the existing translation/rewrite source; it is not publishable Russian;
   - only an exact-bound accepted translation/cache entry can then turn that unresolved source into `ready_ru`.
3. Canonical unresolved/observability state: `data/production/pre_ai/chatgpt_ru_description_queue.jsonl` and `chatgpt_ru_description_status.json`; accepted semantic translations persist only through `data/cache/russian_description_translations.json`; exact current item-level translation-quality failures persist separately in `data/cache/russian_description_translation_diagnostics.json`.
   - submission/container corruption, duplicate identities and stale/wrong AppID/hash/source-version bindings remain fail-closed before persistence;
   - after those exact-safety checks pass, a translated item that fails `good_ru` is not cached: only that exact request enters GitHub-owned translation diagnostics while safe valid siblings remain persistable;
   - an active exact diagnostic request is excluded from the normal translation queue and is never an automatic translation retry; a source-binding/request-id change cannot inherit the stale diagnostic, direct `ready_ru` makes it non-current, and only explicit GitHub-owned resolution may return the exact unchanged request to normal work;
   - `untranslated_game_count` is the current producer-owned count of scope records without valid `ready_ru`;
   - `translation_diagnostic_count` is the current producer-owned count of unresolved exact requests isolated from normal translation work for diagnosis;
   - `last_translation_attempt_at_utc` advances on a current exact-bound attempt/check, including a zero-queue check;
   - `last_successful_translation_at_utc` advances on at least one accepted exact-bound sibling translation or a zero-queue successful check; quarantining an item alone never manufactures translation success;
   - a valid exact-bound worker error advances attempt only; invalid/stale/wrong-AppID transport remains rejected and does not create success.
4. Visual producer: `scripts/build_visual_feed_v2.py` resolves card descriptions; `scripts/progressive_personalization.py::_translation_processing_metrics` projects translation observability into `processing_status`; `scripts/build_final_visual_payload.py` binds the final payload to the translation-status/contract blobs.
5. `scripts/validate_russian_descriptions.py` remains strict by default, but the normal build/deploy workflows call its explicit `--allow-untranslated` diagnostic mode. Missing translations therefore remain visible/unresolved facts but do not alone block replacing or deploying the visual payload.
6. Statistics route: producer-owned `processing_status` -> `web/progressive-personalization-ui.js::statisticsSections` -> dedicated `Переводы описаний` block, including `На диагностике перевода`. The browser formats only the prepared counts/timestamps and does not infer them.
7. Explicit manual one-shot semantic worker: a fresh user-launched chat reads `config/russian_description_manual_semantic_worker_prompt.md`. It may consume only the exact current normal GitHub queue in order and create only result transport under `data/ai_inbox/russian_descriptions/*.json`; diagnostic items are intentionally absent and must never be reconstructed/retried by the worker. GitHub ingest remains the sole validator/cache/diagnostic/timestamp/completeness owner. Empty normal queue is recorded by a zero-result submission that GitHub validates against the current queue. No Scheduled Task is created or modified.
8. Publication chain remains `.github/workflows/build-daily-visual-payload.yml` -> `data/production/visual/current.json` -> `.github/workflows/deploy-visual.yml` -> `web/data/current.json`.

The browser does not fetch or repair descriptions. Ordinary interactive developer/operator chat does not translate production rows or populate the translation cache manually. Only the explicitly user-launched canonical one-shot semantic-worker role may translate current prepared requests, and it still cannot write canonical cache/state directly. Translation acceptance remains fail-closed even though publication is nonblocking for unresolved descriptions.

## Legacy Deep full reanalysis migration

Use this route only for the finite PPD-010 migration `deep-legacy-full-reanalysis-with-preserved-positives-01`.

- Decision: `PROJECT_DECISIONS.md#PPD-010`.
- Frozen finite scope/evidence authority: `data/control/progressive_pass2_legacy_full_reanalysis_manifest.json`.
- Runtime contract: `config/progressive_pass2_contract.json#legacy_full_reanalysis`.
- Semantic worker: existing `config/progressive_pass2_worker_prompt.md`; there is no migration-specific worker or Scheduled Task.
- Prepared work projection: `scripts/build_progressive_pass2_work.py` -> `data/production/pre_ai/progressive_pass2_work.json`, work mode `legacy_full_reanalysis`.
- Exact evidence gate: `scripts/progressive_pass2.py::validate_run_start_authority` uses the migration authority Dossier bytes and frozen time while preserving the ordinary V2 run-start publication guard.
- Result validation/history: `scripts/progressive_pass2.py::normalize_result`, `_attempt_authorization_status`, `_apply_attempt`; prior authoritative Deep revision is archived under `revision_history`, incomplete migration leaves it current.
- Ingest: `scripts/ingest_progressive_pass2.py::resolve_candidate_authority`; migration requires exact confirmed run-start authority and never falls back to mutable current Dossier bytes.
- Observability: `scripts/progressive_pass2.py::legacy_reanalysis_work_and_metrics` -> PASS 2 work scope -> `scripts/progressive_personalization.py` producer status.
- Regression: `scripts/test_deep_legacy_full_reanalysis.py`.
- Dossier remains in the existing shared canonical-writer domain and continues independently. Scheduled Task configuration is unchanged.

Rediscovery invariant: never regenerate migration membership from later legacy state. The committed manifest is the complete one-off target set.

Currentness invariant after PPD-012:
- the finite PPD-010 manifest is immutable historical membership, not permanent membership in today's commercial/Progressive scope;
- first determine whether a target exists in the current GitHub-owned Progressive scope;
- only a target that is currently in scope must have a current binding; a missing binding for such an in-scope target remains a regression;
- an out-of-scope target keeps its immutable accepted Deep history but has no current binding/result selection until it re-enters current scope;
- when it re-enters, PPD-012 historical semantic-equivalence must prove the current semantic identity before the old revision can be selected current; a real profile/model/semantics/item-context change remains stale and may establish ordinary new work rather than replaying PPD-010;
- regression coverage: `scripts/test_progressive_profile_semantic_identity_stability.py` classifies every frozen migration target individually as current+equivalent, current+stale, or outside current scope.

## Production workflow_run authority / PR isolation

**Что ищем:** почему validation-run или другой upstream GitHub Actions run может/не может запустить downstream, который пишет canonical production state в `main`.

**Последняя проверка:** 2026-10-03.

**Быстрая точка входа:**
1. `.github/workflows/steam-test.yml` — `Steam KZ production shortlist`: PR запускает только `regression`; production `collect` исключает `pull_request`.
2. `.github/workflows/build-mailing-feed.yml` — первый production-mutating downstream после shortlist.
3. `.github/workflows/build-feed-ingest-validation.yml` и `.github/workflows/build-pre-ai-store-snapshot.yml` — mailing successors.
4. `.github/workflows/build-daily-visual-payload.yml` — visual producer; все jobs, которые могут push в `main`, обязаны применять production-source guard.
5. `.github/workflows/deploy-visual.yml` — read-only checkout / Pages publication; workflow-run trigger уже требует successful `main`.
6. SteamDB workflow-run chain: `checkpoint-steamdb-history.yml` → `build-steamdb-cache-classification.yml` → `export-steamdb-miss-manifest.yml` → `ingest-steamdb-runtime-submissions.yml`.
7. `scripts/test_workflow_run_production_authority.py` — каноническая regression/audit поверхность для mutating `workflow_run` jobs; вызывается из `validate-execution-ownership.yml`.

**Инвариант:** имя upstream workflow и `conclusion == success` сами по себе не дают production authority. Для `workflow_run` job, способного записать canonical repository state, текущая минимальная authority — successful run с `head_branch == main`; direct `workflow_dispatch` / `push` / schedule поведение остаётся отдельным существующим entrypoint. PR-only run с feature head branch обязан skip mutating job.


## Steam KZ discovery — bounded paid source scope

**Что ищем:** где задаётся и выполняется current paid Steam KZ discovery scope до Reviews API, как доказать KZ price bound и где смотреть funnel.

**Последняя проверка:** 2026-10-05.  
**Implementation refs:** PR #146 (base implementation) + PR #147 (live maxprice validation correction) + PR #148 (runtime observability / 100-row pagination continuation) + PR #151 (bundle-scope / rate-limit correction).

**Канонические правила:**
1. `config/mailing_policy.json#paid_discovery` — explicit `games / dlc` traversals, `discount >= 50%`, `price <= 4500 KZT`, no raw top-N, separate free/giveaway lane. Purchasable package/bundle `Sub_` identities are preserved from the games partition; standalone `category1=996` traversal is forbidden because live Steam proves it is broad `Include Bundles`/untyped scope, not bundle-only.
2. `config/execution_ownership_contract.json` — GitHub owns discovery scope, completeness, persistence and orchestration.
3. `config/daily_execution_contract.json` — discovery remains inside the existing GitHub-owned daily production cycle.

**Быстрая точка входа:**
1. `scripts/steam_partial_publish_runner.py` — production collector owner; validates the exact live KZ `maxprice=4500` filter with capped-vs-uncapped controls, traverses explicit partitions, deterministic App/Sub dedupe, early paid gate, review enrichment and funnel publication.
2. `scripts/steam_production.py` — shared Steam Search parsing/rules and policy-derived paid gate.
3. `.github/workflows/steam-test.yml` — PR runs deterministic regression only; normal `main` push/schedule runs the 60-minute production `collect`.
4. `scripts/test_steam_discovery_scope_reduction.py` — deterministic regression for partitions, dedupe, 50%/4500, non-monotonic Steam price ordering, fail-closed source-bound validation, giveaway separation, ownership and no Catalyst special case.
5. `data/production/manifest.json` and `data/production/shortlist/index.json` — after a successful main production run, read `search_partitions`, `source_price_bound_validation`, `filtering_funnel`, request/review counts and source completeness.

**Live evidence / correction:**
- PR #146 merged as `fb21b704ac36f56d40bdc6a00175864538dbcee7`; first normal acceptance run `37319401442` failed only because the old proof required strict `Price_ASC` monotonicity.
- bounded PR #147 probe run `37334852442` showed exact `cc=kz&maxprice=4500` is active: games `total_count=63681` under `Price_ASC`, `Price_DESC` and `Name_ASC`; capped `Price_DESC` sampled maximum exactly `4500 KZT`.
- the same bounded probe showed arbitrary low `maxprice` values are not safe substitutes: values 10/20/50/100/1000 behaved as ignored/unbounded controls (`total_count=65097`, sampled prices up to `74400 KZT`). Therefore production trusts only the exact current policy value after live control validation; it does not infer general numeric semantics.
- the corrected proof does **not** use `Price_ASC` positional early stop. It checks every paid partition's capped `Price_DESC` sample for no over-cap row, requires the games capped total to be sort-invariant, and requires an otherwise-identical uncapped games control to have both a larger total and an over-cap KZT row.

**Live runtime continuation after PR #147:**
- normal main run `37335826933` completed games traversal at ~63,689 rows / 41,654 locally eligible rows, then reached only `13,700 / ~34,356` DLC rows before the existing 60-minute job timeout; bundles never started;
- the same run logged 204 HTTP 429 responses, with repeated `3/6/12/24s` backoff; Search traversal, not Reviews enrichment, consumed the acceptance window;
- bounded PR #148 probes proved tested minimum-discount query parameters are ignored, so the local `>=50%` gate remains authoritative;
- bounded live pagination proved Steam returns complete non-overlapping 100-row pages for `start=0` and `start=100`, while larger requested counts are capped at 100; canonical `PAGE_SIZE=100` is therefore the largest live-proven semantics-preserving request reduction;
- PR #148 adds unbuffered `[steam-progress]` heartbeats/stages plus Search/Reviews request, retry, 429, backoff and stage-timing metrics so the next main run is diagnosable while it is running.

**Инварианты:**
- production never trusts `maxprice=4500` only because the query string exists; the bounded capped-vs-uncapped KZ control must pass first;
- `Price_ASC` global monotonicity is explicitly **not** required and is not a completeness authority;
- source-side minimum-discount parameter is not assumed; parsed-row gate `>=50%` remains authoritative before Reviews API;
- paid traversals use `hidef2p`, but free/giveaway remains a separate existing lane;
- standalone `category1=996` must not be reintroduced as a bundle partition unless new bounded live evidence proves exclusive bundle semantics;
- no raw top-N, second collector/scheduler, ChatGPT-owned loop or Catalyst special case;
- live acceptance is an ordinary GitHub-owned `Steam KZ production shortlist` run on `main`; PR `collect` remains intentionally disabled.

## Deep two-stage frozen architecture: Stage 1 -> Stage 2 -> ranking

**Что ищем:** target architecture and exact parallel implementation interfaces for replacing Fast/current monolithic Deep with independent Deep analysis and comparative calibration.

**Последняя проверка:** 2026-10-06.  
**Проверенный ref:** branch `feature/deep-two-stage-architecture-freeze-01` before production cutover.

**Быстрая точка входа:**
1. `config/deep_two_stage_architecture_contract.json` — pipeline, 56+4+40 scoring split, ownership, precision and activation gates.
2. `config/deep_stage1_contract.json` + `config/deep_stage1_result_schema.json` — independent per-game analysis interface and dynamic point-breakdown semantics.
3. `config/deep_stage2_contract.json` + `config/deep_stage2_result_schema.json` — GitHub-selected anchor-window comparative calibration interface and strict-order output.
4. `config/deep_two_stage_site_projection_contract.json` — compact card/detail/Statistics producer fields and section order.
5. `config/deep_two_stage_migration_contract.json` — legacy Dossier/Deep reuse classification, old arithmetic retirement and no-mixed-authority boundary.
6. `config/deep_two_stage_dependency_map.json` — which four implementation tasks may proceed in parallel and which shared files they may not redefine.
7. `PROJECT_DECISIONS.md#PPD-013` — rationale and activation boundary.
8. `scripts/test_deep_two_stage_architecture_freeze.py` — bounded invariant regression proving the frozen target is non-active and current production remains unchanged.

**Критические инварианты:**
- Stage 1 and Stage 2 are different semantic workers with different manifests/results/state.
- Stage 1 never sees ranking neighbors; Stage 2 never researches or invents facts.
- Stage-2 semantic comparison is not itself canonical numeric placement; GitHub inserts/re-spaces locally.
- active calibrated fit scores are strictly monotonic/unique and displayed to two decimals.
- Wishlist remains deterministic +4; purchase remains deterministic /40.
- old achievements/duration/risk arithmetic cannot survive as independent post-Deep adjustments after cutover.
- current `FAST-DOSSIER-DEEP-V1` remains production authority until the integration task performs coherent cutover.
- no Scheduled Task change is part of the freeze.

**Stage-2 implementation path (non-active, 2026-10-07):**
- `scripts/deep_stage2.py` — frozen Stage-1/Stage-2 binding validation, exact neighbor-comparison validation, GitHub-owned unique two-decimal placement and smallest local one-cent re-spacing;
- `scripts/build_deep_stage2_work.py` — consumes only explicit accepted Stage-1 result references/profile pins and current calibrated Stage-2 state; never infers acceptance from inbox artifacts and never auto-retries diagnostics;
- `scripts/ingest_deep_stage2.py` — strict exact-path ingest, create-only accepted-result/receipt persistence and idempotent replay;
- `config/deep_stage2_manual_worker_prompt.md` — manual semantic data-plane prompt; implementation presence is not launch authority;
- `data/production/pre_ai/deep_stage2_work.json` + `data/cache/deep_stage2_state.json` — non-active manifest/state surfaces;
- `.github/workflows/validate-deep-stage2-calibration.yml` + `scripts/test_deep_stage2_calibration.py` — bounded compile/frozen-interface/runtime regression.
- Stage-2 bootstrap anchors are intentionally not invented: the frozen contract requires already-calibrated anchors, so seed/migration activation remains an integration/cutover responsibility.
- No mutating production ingest workflow is activated by this implementation task; the ingest script exists for later canonical integration wiring.




---

## Site publication resilience / current Statistics / local quarantine

**Что ищем:** почему один presentation-дефект больше не должен удерживать свежие Statistics/остальной сайт и где проходит global fail-closed boundary.

**Последняя проверка:** 2026-10-07, branch `fix/site-nonblocking-freshness-quarantine-01`.

**Быстрая точка входа:**
1. `config/site_publication_resilience_contract.json` — canonical local-vs-global classification, quarantine/status/publication rules.
2. `scripts/isolate_site_publication_defects.py` — per-item isolation for card explanations/descriptions plus giveaway diagnostics; semantic score/ranking is not rewritten.
3. `scripts/site_publication_resilience.py` + `data/production/site/publication_quarantine.json` — stable defect identity, pending/resolved reconciliation and category counts.
4. `scripts/build_site_status.py` — independent current Fast/Dossier/Deep/translation + quarantine projection with exact source bindings.
5. `.github/workflows/build-site-current-status.yml` — GitHub-owned status persistence independent of full visual card success.
6. `.github/workflows/build-daily-visual-payload.yml` — full visual build → local isolation → strict post-isolation validators → exact material binding/persistence.
7. `.github/workflows/deploy-visual.yml` — stage visual plus optional `web/data/status.json`; status-only publication preserves existing visual and validates exact status bindings.
8. `web/app.js` + `web/progressive-personalization-ui.js` — Statistics prefers `data/status.json`, fallback is legacy `data.current.processing_status`; browser never reconstructs canonical state.
9. `scripts/test_site_publication_resilience.py` + `web/progressive-personalization-ui.test.js` — Tetris/local-defect, quarantine dedupe/resolution, global identity guard, status/UI regressions.

**Global guards that remain intentionally blocking:** canonical source/schema/authority contradictions, Progressive scope/accounting invariants, full visual exact material binding, persistent material drift, missing mandatory global identity. Do not route those through local quarantine.

---


## Site tasks page / canonical Director forward plan

**Проверено:** 2026-10-08, branch `implement/site-current-tasks-page-01` (использовать main после merge).

1. `config/director_task_plan.json` — один структурированный реестр известных текущих и будущих задач, включая неназначенные, статусы, причины трудоёмкости/срочности, порядок, зависимости и дату проверки.
2. `DIRECTOR_TASK_BOARD.md` — human-readable состояние директора; текущие forward-секции и `config/deep_two_stage_dependency_map.json` сверяются при публикации, а исторические sections не превращаются в очередь.
3. `scripts/build_site_tasks.py` — проверка полноты, связности и безопасности, статический `web/data/tasks.json` в существующем GitHub Pages deploy.
4. `.github/workflows/deploy-visual.yml` — read-only построение task-payload перед Pages artifact, без API-запросов из браузера и без нового scheduler.
5. `web/tasks.html`, `web/tasks.js`, `web/tasks.css` — адаптивная страница; `web/index.html` — вход.
6. `scripts/test_site_tasks.py`, `web/tasks.test.js`, `.github/workflows/validate-site-tasks-page.yml` — обязательные PR checks.

При назначении/изменении/закрытии задачи директор меняет Board current planning + JSON в одном update. CI запрещает новые task-file ссылки в forward-секциях Board и Deep map без registry entry. Старые исторические sections не являются live state. После приёмки этого PR необходимо закрыть `site-tasks` в реестре.

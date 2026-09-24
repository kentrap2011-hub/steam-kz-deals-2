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

Production `priority_rank` по-прежнему строится только GitHub producer-ом:
1. `sale_expiry_urgency_asc` — сегодня → завтра → позже/неизвестно;
2. `total_score_desc` — видимый score 0–100;
3. `title_asc` — deterministic fallback.

Срочность находится вне 100 баллов и не меняет сам score.

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

- кнопка **`⏱ Срочные` выключена (default)** → локальная очередь: `total_score DESC → title`;
- кнопка **`✓ Срочные` включена** → локальная очередь использует готовый production `priority_rank`, то есть `urgency → score → title`;
- выбранный режим хранится в localStorage как `state.settings.urgency_first`;
- `QUEUE_VERSION=5` заставляет старое состояние один раз пересобрать очередь по новому default;
- при переключении `buildQueue()` сохраняет текущую открытую игру, если она остаётся активной;
- UI не пересчитывает semantic score, urgency или ranking factors: он только меняет порядок уже готовых producer-owned полей `total_score` / `priority_rank`.

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
- canonical urgency → score → title;
- 60 + 40 = 100;
- ruble savings вместо discount percentage;
- risk/wishlist/achievements/duration weights;
- `manual_end_at` UI invariant.

Для local UI режима обязательные implementation-инварианты:
- default `urgency_first=false`;
- off-mode сортирует automatic items по `total_score`;
- on-mode использует готовый `priority_rank`;
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

**Последняя проверка:** 2026-09-24.

**Быстрая точка входа:**
1. `config/taste_steam_review_dossier_contract.json` — canonical GitHub-owned per-group progress/completeness contract; `checkpoint_size=3` остаётся transport/group boundary, не quota.
2. `scripts/taste_steam_review_dossier_group_progress.py` — canonical state transitions, counts, `next_pending_sequence`, normal-first-pass vs all-accepted semantics.
3. `scripts/taste_steam_review_dossier_buffered.py` + `scripts/taste_steam_review_dossier_strict.py` — strict independent validation/persistence; invalid transport quarantine affects only its exact group.
4. `scripts/taste_steam_review_dossier_worker_projection.py` — V2 compact index; worker resumes from GitHub-owned next pending group, not first historical failure.
5. `scripts/taste_steam_review_dossier_parallel_validation.py` — validation/recovery observability; not queue/progress authority.
6. `scripts/taste_steam_review_dossier_recovery.py` — separate GitHub-owned failed-group recovery after normal first pass; no automatic semantic retry.
7. Exact shared-writer inventory: `.github/workflows/build-pre-ai-store-snapshot.yml`, `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`, `.github/workflows/ingest-progressive-pass1.yml`, `.github/workflows/ingest-progressive-pass2.yml`, `.github/workflows/authorize-progressive-pass2-recovery.yml`; all use the single `taste-steam-review-dossier-canonical-writer` boundary and state-reconcile current Dossier inbox before dependent Deep projection/write.
8. `scripts/test_taste_dossier_canonical_writer_coalescing_liveness.py` — regression for cancelled/coalesced zero-job Dossier wake-up, exactly-once classification, idempotence and post-reconcile Deep visibility.
9. `config/taste_steam_review_dossier_worker_prompt.md` — create-only semantic data-plane rules and explicit prohibition on editing/disabling its own Scheduled Task.

**Runtime / recovery-инварианты:**
- create-only deterministic transport remains immutable and is not canonical acceptance;
- every present pending group is strict-validated independently; valid later groups may persist even when an earlier different group failed;
- invalid group is recorded `failed_or_invalid_pending_recovery`, moved out of normal forward progress and remains separately recoverable;
- missing pending group remains pending but does not prevent processing another present pending group;
- accepted and failed groups are excluded from normal first-pass traversal; future worker invocations start from `next_pending_sequence`;
- `normal_first_pass_complete=true` means no pending groups remain; `full_backlog_complete` retains the stricter legacy/all-accepted meaning and failures never count as accepted evidence;
- Scheduled ChatGPT cannot overwrite/rename/delete transport, own retry/completeness, or enable/disable/edit its own schedule;
- snapshot/plan/binding exactness, strict dossier semantics, story-DLC scope, Russian retrieval/provenance and stale-snapshot isolation remain fail-closed;
- old snapshot artifacts never rebind to a new snapshot; same-snapshot descriptors stay immutable.
- Dossier wake-up events are advisory only: durable repository state is authoritative, so cancellation/coalescing of the original zero-job wake-up cannot strand a current candidate while another shared writer survives.


---

## Progressive Fast / Dossier / Deep: stage architecture and Deep recomputation boundary

**Что ищем:** canonical Fast/Dossier/Deep semantics, effective-result precedence, Deep first-pass/recovery ownership and the reusable GitHub recomputation hooks.

**Последняя проверка:** 2026-09-23.

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
10. `PROJECT_DECISIONS.md#PPD-006` + `#PPD-007` — one immutable Deep run-start authority plus deferred confirmation: marker before semantics, provisional computation on the exact observed commit, mandatory confirmed GitHub receipt before first semantic transport.
11. `config/progressive_pass2_worker_prompt.md` + `scripts/test_progressive_async_traversal.py` — bounded worker timing and regressions for delayed/missing/rejected confirmation, authority equality, no pre-confirmation publication and continued sibling traversal.

**Инварианты:** Deep eligibility never requires prior Fast/PASS 1 attempt or Fast `analysis_incomplete`; the run-start marker is created before semantics, provisional semantics may use only the exact observed immutable authority, and no Deep result/terminal receipt may be published until GitHub durably confirms the same authority; missing/rejected/mismatched confirmation consumes no attempt and publishes nothing; exact-compatible canonically accepted Dossier remains the evidence gate; completed authoritative Deep suppresses future Fast for the same current identity while Fast success never suppresses Deep; Deep incomplete/error does not erase a valid Fast provisional result; unresolved consumed Deep becomes recovery-owned and can return only through a fresh concrete GitHub-owned recovery authorization; normal Deep first-pass completeness and eventual all-authoritative completeness are separate; no blind retry loop or hidden recovery quota; Deep semantic execution remains forbidden while active flags are false.
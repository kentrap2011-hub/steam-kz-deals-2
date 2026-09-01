### Task

Системно проверен существующий canonical source/path для normalized game duration без проверки игр поштучно. Проверены ownership/execution contracts, ranking route, current duration producer, Steam-native pre-AI store path, существующие cache/pre-AI/inbox artifacts и уже разрешённые external-runtime patterns.

Цель проверки: установить, существует ли уже источник/кэш/contract, который final ranking должен читать, либо реализация требует сначала отдельного canonical architecture contract.

### Verified facts

- **Готового canonical structured duration source/path в репозитории сейчас нет.** В полном дереве `main` отсутствуют duration-specific contract, cache, pre-AI artifact, inbox/runtime input и workflow/stage для collection/normalization/persistence duration. Существующие `estimated_duration_hours`, `duration_estimate_source` и `duration_preference_band` появляются только на final visual/ranking стороне.
- `scripts/build_final_visual_payload.py` сейчас является точкой потребления duration для ranking: он вызывает `refine_visual_ranking.extract_duration_hours(projection, game)`, передаёт результат в ranking и публикует `estimated_duration_hours`, `duration_estimate_source`, `duration_preference_band`.
- `scripts/refine_visual_ranking.py::extract_duration_hours()` не читает structured duration cache. Он opportunistically ищет явную числовую длительность только в `projection.short_description` и `game.summary`; при отсутствии распознаваемого текста возвращает `(None, None)`.
- `config/final_ranking_policy.json` определяет scoring/fallback, но не источник данных. `unknown = 2/3` — intentional fail-safe и не должен меняться в этой задаче или в source-contract fix.
- Текущий Steam-native pre-AI path не предоставляет normalized completion-duration fact. `scripts/build_pre_ai_store_snapshot.py` сохраняет store/app metadata, включая `short_description`, но не сохраняет structured duration/playtime estimate. Поэтому **существующие Steam-native данные, уже собираемые проектом, не являются надёжным canonical источником `estimated_duration_hours`**. Индивидуальный player playtime также не был бы семантически эквивалентен оценке длительности прохождения.
- **Существующего GitHub-accessible API/source, уже разрешённого контрактами именно для duration, не найдено.** Ни `PROJECT_ROUTES.md`, ни execution/daily contracts, ни pre-AI builders не называют duration provider/API или GitHub-owned direct collection path.
- **Существующего GitHub-prepared external/semantic runtime path, которому уже разрешено получать duration, тоже нет.** `config/execution_ownership_contract.json` разрешает scheduled ChatGPT получать external/semantic facts только когда canonical production contract явно назначает ему эту работу и GitHub заранее задаёт точный scope. Duration такого назначения не имеет.
- SteamDB runtime route нельзя считать готовым duration route. `config/steamdb_lookup_contract.json` жёстко ограничен stage-15 SteamDB price-history true misses, конкретным provider/source и конкретными artifacts. Его архитектурный шаблон полезен, но его scope нельзя молча расширить на duration.
- Следовательно, следующий IMPLEMENT **нельзя корректно сделать только patch-ом `extract_duration_hours()` или `build_final_visual_payload.py`**: это создало бы новый фактический source/ownership без canonical authorization, что прямо запрещено architecture-change gate.

**Canonical ownership, который уже следует из общих contracts:**

| Responsibility | Current state | Required owner if duration source is introduced |
|---|---|---|
| Source collection | duration-specific stage отсутствует | GitHub, если источник доступен GitHub напрямую; иначе только явно назначенный contract-ом scheduled ChatGPT data-plane для GitHub-prepared exact keys |
| Scope / ordering / retry / completeness | duration-specific scope отсутствует | GitHub control-plane |
| Normalization / validation | structured duration normalization отсутствует | GitHub-owned deterministic stage |
| Persistence/cache | duration cache отсутствует | GitHub-owned canonical cache/artifact |
| Final ranking handoff | существует только text extraction в final visual builder | `build_final_visual_payload.py` должен читать validated structured duration до text fallback |
| Fallback | существует | при отсутствии validated duration сохранять `unknown`, а scoring оставлять `2/3` |

**Точный contract gap:** перед IMPLEMENT отсутствует canonical duration-source/enrichment contract. Он должен как минимум определить:

1. authoritative duration source class/provider и trust precedence;
2. кто имеет право получать source facts: GitHub direct collection либо scheduled ChatGPT data-plane;
3. если нужен внешний runtime — GitHub-owned exact work input/scope и repository-defined submission interface, без ChatGPT-owned queue/backlog;
4. normalized record/schema для `estimated_duration_hours` + provenance/source + validation/confidence state;
5. GitHub-owned persistence/cache path и conflict/invalid handling;
6. freshness/staleness/refresh semantics;
7. точку deterministic ingestion в final visual builder и сохранение существующего text extraction только как явно определённого fallback, если contract это разрешит;
8. окончательный fail-safe: no validated duration => `unknown` => canonical `2/3`.

### Changes

`none` кроме этого report.

### Validation

Вывод подтверждён текущими файлами/маршрутами `main`:

- `WORKER_TASK_DURATION_SOURCE_RECON_01.md`
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `PROJECT_RULES.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `config/final_ranking_policy.json`
- `config/mailing_policy.json`
- `config/steamdb_lookup_contract.json`
- `scripts/build_pre_ai_store_snapshot.py`
- `scripts/build_pre_ai_chatgpt_payload.py`
- `scripts/refine_visual_ranking.py`
- `scripts/build_final_visual_payload.py`
- `reviews/worker_reports/duration-data-diagnosis-01.md`
- полное recursive tree `main` (`truncated=false`) для проверки отсутствия duration-specific contract/cache/runtime/workflow artifacts.

Проверка не включала top-N, per-game lookup или ручной поиск HowLongToBeat/SteamDB/Google/web duration values, в соответствии с hard boundaries текущего задания.

### Unresolved

- Не выбран authoritative external duration provider/source. Текущие canonical contracts его не называют, поэтому выбирать конкретного провайдера в RECON было бы самовольным architecture decision.
- Не определено, сможет ли выбранный в будущем источник стабильно читаться напрямую из GitHub Actions или потребует scheduled ChatGPT data-plane. Это можно решить только после выбора/утверждения source в duration contract.
- Поэтому точные имена будущих cache/work-input/submission artifacts пока не canonical и не должны изобретаться реализацией до contract change.

### Status

`complete`

### Recommended next step

Один bounded **CONTRACT** step до любого IMPLEMENT: добавить и утвердить canonical duration-source/enrichment contract, который выбирает authoritative source и executor class (GitHub-direct либо GitHub-prepared scheduled ChatGPT external fact worker), закрепляет GitHub-owned normalization/validation/cache/freshness semantics и final-builder ingestion precedence. Только после этого отдельный IMPLEMENT должен подключить этот утверждённый path к `build_final_visual_payload.py`, не меняя scoring и сохраняя `unknown = 2/3` как fail-safe.
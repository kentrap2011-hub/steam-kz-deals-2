# Duration data diagnosis 01

### Task

Проверена canonical цепочка, из которой в published recommendation payload попадают `estimated_duration_hours` / `duration_preference_band`, и локализовано происхождение состояния `duration_preference_band = unknown` с fallback-оценкой `2/3`.

Проверка была read-only по системе: scoring math, fallback `unknown = 2/3`, UI, Taste/package/descriptions, `CURRENT_TASK.md` и данные отдельных игр не изменялись. После диагностического прохода по прямому указанию пользователя дополнительный ручной пересчёт top-30 и поиск длительности по отдельным играм не выполнялся.

### Verified facts

- `unknown` формируется не UI. Он уже присутствует в canonical `data/production/visual/current.json`; UI показывает готовое precomputed состояние.
- В ранее проверенном current payload как минимум `Fable Anniversary` (priority rank 1) и `Psychonauts 2` (priority rank 2) были опубликованы с `duration_preference_band = "unknown"`. Это уже показывает, что состояние не является единичным UI-артефактом.
- Текущая producer-цепочка длительности проходит через `scripts/build_final_visual_payload.py`, который использует `extract_duration_hours()` из `scripts/refine_visual_ranking.py`.
- `extract_duration_hours()` не обращается к отдельному canonical duration field/source. Он пытается извлечь число часов из текстов `projection.short_description` и `game.summary` по ограниченным текстовым шаблонам. Если явная длительность в подходящей форме в этих текстах отсутствует или не распознана, функция возвращает `None`.
- После этого `scripts/priority_ranking.py` штатно применяет canonical fallback для `duration_preference_band = unknown`: duration component получает neutral/default `2/3`. Сам этот fallback не является причиной дефекта.
- Следовательно, корневая причина находится до UI/scoring: существующий final visual producer зависит от opportunistic text extraction вместо гарантированного normalized duration enrichment/persistence. При отсутствии распознаваемой фразы данные о длительности до scoring не доходят.
- Canonical ownership текущего поля находится в GitHub-owned final visual build/ranking chain: `scripts/build_final_visual_payload.py` + `scripts/refine_visual_ranking.py`; именно здесь сейчас определяется, удалось ли получить duration или будет `unknown`.

#### Top-30 audit state

Надёжный итоговый счётчик `confirmed` vs `unknown` для всех top-30 в предыдущем диагностическом проходе завершён не был. После него пользователь отдельно запретил дополнительный ручной пересчёт и поиск длительности по отдельным играм. Поэтому числа ниже намеренно не выдумываются:

- confirmed: `unresolved`
- unknown: `unresolved`

#### Known unknown cases from the completed source-path diagnosis

| key/title | expected source/path | actual state | cause |
|---|---|---|---|
| Fable Anniversary | existing final visual duration extraction from `projection.short_description` / `game.summary` | `duration_preference_band = unknown` in current published payload | current extractor did not obtain a normalized duration; exact per-game source availability was not re-searched after the user's no-manual-recount instruction |
| Psychonauts 2 | existing final visual duration extraction from `projection.short_description` / `game.summary` | `duration_preference_band = unknown` in current published payload | same systemic extraction/enrichment gap; exact per-game source availability was not re-searched after the user's no-manual-recount instruction |

### Changes

`none` кроме этого report.

### Validation

Вывод подтверждён проверкой следующих canonical материалов в `main`:

- `WORKER_TASK_DURATION_DATA_DIAG_01.md`
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `config/final_ranking_policy.json`
- `data/production/visual/current.json`
- `scripts/build_final_visual_payload.py`
- `scripts/refine_visual_ranking.py`
- `scripts/priority_ranking.py`
- `reviews/worker_reports/detailed-score-user-fixes-01.md`

Ключевая цепочка валидации: current payload уже содержит `unknown` -> final visual builder вызывает duration extractor -> extractor ищет длительность только в текстовых полях -> отсутствие/нераспознавание явной фразы даёт `None` -> ranking policy превращает это в штатный `unknown = 2/3`.

### Unresolved

- Полный top-30 confirmed/unknown count не был надёжно завершён до отдельного указания пользователя не выполнять дополнительный ручной пересчёт.
- Для каждого отдельного unknown из top-30 не установлено, существует ли надёжная duration source data вне двух текстовых полей, потому что дополнительный per-game source search теперь явно запрещён пользователем.
- Поэтому нельзя честно разделить все top-30 unknown на `source absence` и `data exists but pipeline misses it` без отдельного автоматизированного/producer-level аудита.

### Status

`blocked`

### Recommended next step

Один bounded IMPLEMENT scope: в существующей GitHub-owned final visual duration chain добавить/подключить normalized duration enrichment из уже разрешённого canonical source path и передавать его в scoring как структурированное поле, оставив текущий text extractor только как совместимый fallback и сохранив `unknown = 2/3` для действительно неподтверждённых случаев. Добавить producer-level test, который проверяет, что доступная canonical duration не теряется до `current.json`. Не добавлять ручные per-game overrides, новую recurring queue или внешний semantic backlog.
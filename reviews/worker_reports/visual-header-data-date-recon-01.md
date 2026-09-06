# Visual Header Data Date Recon 01

## Summary

`Данные: 31 авг., 00:37` берётся не из времени последней публикации сайта и не из времени последнего обновления giveaway. Текущий frontend выводит поле `source_mailing_updated_at_utc` из опубликованного `data/current.json` и форматирует его в локальном часовом поясе браузера/Android-устройства.

По смыслу это timestamp исходной mailing-выгрузки, на которой основан базовый принятый visual snapshot. Это отдельная семантика от времени генерации visual artifact (`generated_at_utc`) и от свежести giveaway.

Поэтому свежая бесплатная раздача и старая дата в header одновременно возможны: giveaway имеет section-level refresh path и может обновляться без полного пересбора базового visual snapshot. История `main` прямо содержит giveaway-only обновления `data/production/visual/current.json`, включая коммит 2026-09-06 `Refresh giveaway visual payload`.

Технически текущее значение поля используется согласованно с его семантикой. Но подпись `Данные:` вводит в заблуждение, потому что визуально читается как «все данные этой страницы актуальны на указанное время», чего система при независимом обновлении giveaway не гарантирует.

Один минимальный fix, если будет отдельная implementation-задача: заменить только label `Данные:` на `Рассылка:` в `web/app.js`, сохранив источник `data.source_mailing_updated_at_utc`. Не заменять timestamp на `generated_at_utc`.

В рамках этого RECON код, production data и workflows не изменялись.

## Evidence/files

### `web/app.js`

Текущий frontend задаёт:

```js
const DATA_URL='data/current.json';
```

Форматирование:

```js
function formatDate(iso){
  if(!iso)return'—';
  const d=new Date(iso);
  return new Intl.DateTimeFormat('ru-RU',{
    day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'
  }).format(d)
}
```

Header строится так:

```js
function sourceLabel(data){return`Данные: ${formatDate(data.source_mailing_updated_at_utc)}`}
```

Следовательно, точный source field для видимой строки `Данные: ...` — root field:

`source_mailing_updated_at_utc`

Frontend не вычисляет этот timestamp самостоятельно и не подменяет его временем загрузки страницы.

Также `formatDate()` не задаёт `timeZone`, поэтому ISO timestamp отображается в timezone браузера/Android-устройства. Наблюдаемое пользователем `31 авг., 00:37` — локально отформатированное значение embedded ISO timestamp.

Загрузка payload выполняется через:

```js
fetch(DATA_URL,{cache:'no-store'})
```

То есть сама старая дата не объясняется frontend cache: UI читает текущий опубликованный `data/current.json`, а label показывает содержащийся внутри него source timestamp.

### `.github/workflows/deploy-visual.yml`

Pages deployment готовит runtime payload так:

```sh
mkdir -p web/data
cp data/production/visual/current.json web/data/current.json
test -s web/data/current.json
```

После этого публикуется `./web`.

Следовательно, browser flow:

`data/production/visual/current.json`
→ deployment copy
→ `web/data/current.json`
→ browser `data/current.json`
→ `web/app.js`
→ `source_mailing_updated_at_utc`
→ header `Данные: ...`

### `scripts/build_visual_feed_v2.py`

Base visual-feed builder читает:

`data/production/pre_ai/chatgpt_payload.json`

и формирует отдельные поля:

```py
"source_mailing_updated_at_utc": payload.get("source_mailing_updated_at_utc"),
"generated_at_utc": datetime.now(timezone.utc).isoformat(),
```

Это прямое подтверждение, что source timestamp наследуется из mailing payload, а generation timestamp означает другое событие.

### `scripts/build_daily_visual_payload.py`

Production visual builder аналогично сохраняет provenance:

```py
"generated_at_utc": datetime.now(timezone.utc).isoformat(),
"source_mailing_updated_at_utc": pre_ai_payload.get("source_mailing_updated_at_utc"),
```

То есть production visual содержит как минимум два разных freshness clocks:

- `source_mailing_updated_at_utc` — время source mailing snapshot;
- `generated_at_utc` — время генерации visual artifact.

Также payload содержит отдельный freshness status, включая `full_visual_freshness`; это ещё раз показывает, что один header timestamp не является универсальным timestamp свежести всех секций.

### `scripts/build_final_visual_payload.py`

Finalization path загружает base visual и giveaway visual отдельно и начинает output с:

```py
output = dict(base)
output["giveaway"] = giveaway
```

При этом отдельно фиксируются:

- `base_visual_generated_at_utc`;
- `giveaway_visual_generated_at_utc`.

Это архитектурное подтверждение section-level независимости: giveaway может быть более свежим, а поля базового visual snapshot сохраняться без изменения.

Важно: текущий Pages workflow публикует `data/production/visual/current.json`, а не `final_current.json`; `build_final_visual_payload.py` здесь используется как evidence архитектурной модели независимого giveaway. Прямое доказательство того, что giveaway-only refresh дошёл именно до production `current.json`, даёт git history ниже.

### `data/production/pre_ai/chatgpt_payload.json`

На момент RECON текущий `main` содержит:

```json
"source_mailing_updated_at_utc":"2026-09-03T18:53:27.390807+00:00"
```

Это уже новее наблюдаемого header `31 авг., 00:37`.

Следовательно, header не live-bound к текущему pre-AI source. Он отображает source timestamp, уже embedded в принятом/deployed production visual snapshot. Наличие более нового upstream payload само по себе не переписывает header без соответствующего полного production visual refresh.

### Git history: `data/production/visual/current.json`

История `main` содержит отдельные commits с сообщением `Refresh giveaway visual payload`, в том числе:

- 2026-09-06, commit `1d7fb4d172d6d36dec4e78a5db2cdf51fa26b6ab` — `Refresh giveaway visual payload`.

До этого в истории есть отдельные `Build daily visual payload (manual)` commits 2026-08-31 / 2026-09-01.

Это прямое operational evidence требуемого сценария:

1. базовый visual snapshot был построен раньше;
2. позднее giveaway обновлялся отдельными production commits;
3. свежая giveaway-секция не обязана менять source mailing timestamp базового snapshot.

### `reviews/worker_reports/giveaway-visual-publication-recovery-implement-01.md`

Предыдущий recovery report также фиксирует восстановление giveaway при отсутствии полного global visual freshness. Это согласуется с текущим recon и с фактической историей giveaway-only publication.

## Exact field + flow

Точный field:

`source_mailing_updated_at_utc`

Точный full/base provenance flow:

`data/production/pre_ai/chatgpt_payload.json`
→ `scripts/build_visual_feed_v2.py`
→ visual feed
→ `scripts/build_daily_visual_payload.py`
→ `data/production/visual/current.json`
→ `.github/workflows/deploy-visual.yml`
→ copied `web/data/current.json`
→ runtime `data/current.json`
→ `web/app.js`
→ `sourceLabel(data)`
→ `formatDate(data.source_mailing_updated_at_utc)`
→ `Данные: ...`

Frontend не recompute-ит и не обновляет поле по текущему времени.

Timezone behavior:

`Intl.DateTimeFormat` вызывается без явного `timeZone`, поэтому точные wall-clock дата и время зависят от локального timezone браузера/Android-устройства. Поэтому в RECON нельзя корректно выводить конкретный UTC instant только из строки `31 авг., 00:37`, не зная timezone самого устройства; однако источник строки и field установлены однозначно.

## Semantics

### `source_mailing_updated_at_utc`

Означает timestamp исходного mailing snapshot, из которого берётся базовый visual data set.

Это не:

- время последнего открытия страницы;
- время последнего Pages deploy;
- время последнего изменения любой секции страницы;
- время последнего giveaway refresh;
- универсальное время свежести всего сайта.

### `generated_at_utc`

Означает время генерации соответствующего visual artifact.

Это тоже нельзя использовать как замену source freshness: новый rebuild может иметь свежий `generated_at_utc`, продолжая опираться на старый source snapshot.

### Giveaway freshness

Giveaway имеет собственный section-level artifact/refresh lifecycle и может обновляться независимо от source mailing timestamp базового visual snapshot.

## Why stale header / fresh giveaway is possible

Это не противоречие данных, а следствие нескольких freshness domains.

Базовый visual payload сохраняет `source_mailing_updated_at_utc` своего source snapshot. Giveaway может быть вставлен/обновлён отдельно. При section-level giveaway refresh нет требования переписать source timestamp базового mailing snapshot, потому что это было бы семантически неверно: giveaway refresh не превращает старую mailing-выгрузку в новую.

Именно поэтому возможна наблюдаемая комбинация:

- бесплатная раздача на Android снова свежая/видимая;
- header продолжает показывать `31 авг., 00:37`.

Git history `Refresh giveaway visual payload` 2026-09-06 подтверждает, что это не теоретическая возможность, а фактически использованный publication path.

## Correct/misleading assessment

### Data behavior

**Technically correct.**

Frontend показывает именно то поле, которое выбрано: `source_mailing_updated_at_utc`. Giveaway-only refresh не обязан менять этот timestamp.

### UX label

**Misleading.**

`Данные:` для обычного пользователя означает примерно «данные страницы актуальны на это время». Но система гарантирует только «source mailing snapshot имеет это время», а отдельные секции — прежде всего giveaway — могут быть новее.

То есть проблема не в самом timestamp и не в независимом refresh giveaway. Проблема в слишком широком label для более узкой семантики.

## One minimal fix recommendation

**RECOMMENDATION ONLY — NOT IMPLEMENTED IN THIS RECON.**

В `web/app.js` заменить только текст label:

```js
`Данные: ${formatDate(data.source_mailing_updated_at_utc)}`
```

на:

```js
`Рассылка: ${formatDate(data.source_mailing_updated_at_utc)}`
```

Оставить source field тем же:

`data.source_mailing_updated_at_utc`

Почему это минимальный корректный fix:

- одна строковая UX-правка;
- не меняет schema;
- не меняет provenance;
- не меняет freshness logic;
- не требует синхронизировать независимые секции;
- точно объясняет, к чему относится timestamp.

Не рекомендуется заменять header source на `generated_at_utc`: это покажет время сборки artifact, а не свежесть source data, и создаст другую ложную семантику.

## Risk/Regression

Риск предложенного future fix низкий: label-only change.

Не затрагиваются:

- production JSON;
- source timestamps;
- giveaway payload;
- visual builders;
- deploy workflow;
- freshness gates;
- schema contracts.

Validation для отдельной implementation-задачи:

1. На Android header показывает `Рассылка: <та же дата/время>`.
2. Giveaway остаётся видимой.
3. `data.source_mailing_updated_at_utc` не меняется.
4. Network/runtime payload не меняется.
5. Deploy/build outputs кроме frontend text не меняются.

## Validation notes

- `CHAT_PROTOCOL.md` прочитан.
- `CHAT_CONTEXT.md` прочитан.
- `DIRECTOR_PROTOCOL.md` прочитан.
- `WORKER_TASK_VISUAL_HEADER_DATA_DATE_RECON_01.md` прочитан и выполнен как `READ-ONLY / RECON`.
- Header source field traced in current frontend: confirmed.
- Runtime fetch path traced: confirmed.
- Browser-local timezone behavior: confirmed.
- Source-field provenance through visual builders: confirmed.
- Pages copy/deploy path: confirmed.
- Independent giveaway refresh architecture: confirmed.
- Direct giveaway-only production commit history: confirmed.
- Current upstream source newer than visible header: confirmed.
- Код, data и workflow не изменялись.
- Единственная repository mutation в рамках задачи — этот обязательный worker report.
- Следующая задача не начиналась.

## Status

**SUCCESS**

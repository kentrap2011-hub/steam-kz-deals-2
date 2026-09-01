# Worker report — detailed-score-user-fixes-01

### Task
Исправлена детальная оценка по результатам первой пользовательской проверки на телефоне: реальное сворачивание/раскрытие, повторные переключения на той же карточке, непонятная терминология Taste и объяснение положительного балла при неподтверждённой длительности.

Scoring/ranking math, Taste semantics, purchase route, package economics, цены/evidence и production queue/schedule не менялись.

### Verified facts
- Причина несворачивающегося блока была в UI: `score-details.css` задавал `.score-details-compact { display:flex }`, а regression проверял только JS-свойство `panel.hidden`. Поэтому тест мог быть зелёным, не защищая фактическую браузерную видимость закрытой панели.
- Canonical `FINAL-PRIORITY-RANKING-V2` явно задаёт для `duration_preference_band = unknown` значение `2` из максимума `3`. `scripts/priority_ranking.py::_duration_component()` действительно использует именно этот fallback. Следовательно, `+2/3` при отсутствии подтверждённой длительности — текущая каноническая нейтральная/default-политика, а не обнаруженный scoring bug.
- Producer по-прежнему отдаёт внутренние источники/значения Taste (`normalized_taste_factors`, `детальная нормализованная оценка` и т.п.); менять producer/Taste semantics для этой задачи не требуется. Проблема была в том, что UI показывал слишком близкую к внутренней терминологию.
- Числовые total/personal/purchase и component scores этой задачей не пересчитываются и отображаются из готового `score_breakdown`.

### Changes
- `web/score-details-ui.js`
  - добавлен единый `toggleScoreDetails()` для повторного `collapsed -> expanded -> collapsed -> ...`;
  - Taste переименован в понятное `Совпадение с твоими вкусами`;
  - `детальная нормализованная оценка` / `normalized_taste_factors` преобразуются в `оценка по твоим игровым предпочтениям`;
  - precision copy преобразован в пользовательские формулировки (`подробная оценка по твоим предпочтениям`, `твоя прямая оценка`, `приближённая оценка по старым данным`);
  - для unknown duration показывается: `нет подтверждённых данных; применяется стандартный балл для неизвестной длительности`, что точно соответствует canonical `unknown = 2/3` и не маскирует отсутствие данных.
- `web/score-details.css`
  - добавлено `.score-details-compact[hidden]{display:none!important}`, чтобы HTML `hidden` гарантированно побеждал собственный `display:flex` renderer-а.
- `web/score-details-ui.test.js`
  - добавлен repeated-toggle guard с пятью последовательными переключениями;
  - добавлена проверка CSS hidden-state, а не только JS property;
  - добавлен normalized Taste fixture и запрет старой внутренней терминологии;
  - добавлен exact unknown-duration fixture `+2/3` с проверкой объяснения и неизменности total/personal score;
  - сохранены проверки компактности, всех score components и producer-owned значений.
- `web/index.html`
  - cache-busting обновлён до `detailed-score-ui-fix-1` для JS и CSS.

Коммиты: UI/copy `da76249bc56e3694ff217ea5127482d39092bce5`; hidden CSS `29c47508b824c38dd0d2be60c8a8f7e77cd92348`; regression `0a1352d432fed0c3f033cc749891837947bc9594`; финальный cache-bust `a52daabc95983a8e991187210b92bb45e4211a33`.

### Validation
- Deploy run `33495533284` после core fix: `success`; новый `detailed score mobile regression` прошёл вместе с существующими image-swipe и compact-purchase regressions.
- Финальный cache-bust попал в существующую Pages concurrency race: push-run был отменён соседним workflow event. Попытка rerun уже загрузившего artifact run закономерно получила duplicate `github-pages` artifact и не использовалась как acceptance.
- Для чистой финальной публикации rerun был выполнен на старом deploy-run, который ранее остановился до artifact upload. Job `99817807119` checkout’нул текущий `main` commit `a52daabc95983a8e991187210b92bb45e4211a33` и завершился `success`.
- В job `99817807119`: `image swipe regression: PASS`; `compact purchase options mobile regression: PASS`; `detailed score mobile regression: PASS`; staging precomputed payload — success; Pages artifact upload — success; GitHub Pages deployment — success.
- Финальный Pages artifact: `9795675163`, digest `sha256:690678e23dc3b136d3e701baa5d0bd582c5c1c71f0e3aeea202064c0401cde11`.
- Ranking/scoring contracts и `scripts/priority_ranking.py` не изменялись.

### Unresolved
Автоматические проверки и deploy закрыты. По условиям текущего поручения задача F не считается окончательно принятой до повторной проверки пользователем на реальном телефоне. Нужно подтвердить именно фактическое многократное сворачивание/раскрытие и понятность новых формулировок в реальном мобильном браузере.

### Status
`complete`

### Recommended next step
На телефоне на одной карточке нажать `Детальная оценка` минимум четыре раза подряд (`раскрыть -> свернуть -> раскрыть -> свернуть`) и одновременно проверить новые формулировки Taste/длительности; после успешного подтверждения закрыть F окончательно.

# Image swipe worker report

### Task
Локализован и исправлен stale/wrong image при быстрых перелистываниях карточек. Исправление ограничено UI-слоем; package valuation, Taste, ranking, production payload/contracts и `CURRENT_TASK.md` не менялись.

### Verified facts
Причина — разрыв во времени между синхронным переключением текущей игры/текста/цены и фактической загрузкой/отрисовкой нового изображения. Старый декодированный кадр мог оставаться видимым, пока новый `src` ещё загружался. При нескольких быстрых переходах нужен явный контроль того, какой запрос на изображение всё ещё относится к текущей игре.

### Changes
- `web/image-swipe-sync.js`: старое изображение и blur-background очищаются сразу; новый кадр грузится отдельно и коммитится только если generation + game id + shot index + URL всё ещё соответствуют текущей карточке. Поздний stale load игнорируется.
- `web/image-swipe-sync.test.js`: моделирует быстрые `A -> B -> C` и обратный переход, намеренно завершает загрузки не по порядку и проверяет связку `title + price + image` одной текущей игры.
- `web/index.html`: подключает guard после `app.js` с cache-busting token.
- Основной merge: PR #9, merge commit `d10cfe40aed926f488e02e93d19c6c43037d8e93`.
- Усиление regression-проверки `title + price + image`: commit `8067c105ae6c2d7c3b9f7316d22ff17b475b20e2`.

### Validation
- `node --check web/image-swipe-sync.js` — PASS.
- `node --check web/image-swipe-sync.test.js` — PASS.
- `node web/image-swipe-sync.test.js` — PASS (`image swipe regression: PASS`).
- `A -> B -> C`, загрузки завершаются `B, A, C`: stale `B/A` не коммитятся; на финале `Game C + 300 ₽ + C.jpg`.
- Быстрый обратный переход `C -> B`: поздний `C` не коммитится; на финале `Game B + 200 ₽ + B.jpg`.
- Старый foreground/blur очищаются до готовности нового текущего кадра.
- Существующие направления свайпа не менялись.
- GitHub PR check `validate` — success.
- Pages deploy run `33487513565` для merge commit — success.
- После усиления regression-проверки Pages deploy run `33487711192` для commit `8067c105ae6c2d7c3b9f7316d22ff17b475b20e2` — success.

### Unresolved
Физический stress-test на реальном телефоне из worker-среды недоступен; race покрыт исполняемой DOM/Image simulation с production guard-кодом.

### Status
complete

### Recommended next step
Один раз быстро пролистать карточки влево/вправо на реальном телефоне (лучше при медленной сети) как финальную пользовательскую smoke-проверку.

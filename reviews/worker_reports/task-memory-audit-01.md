# Worker report — task-memory-audit-01

### Root cause

У потери задач было не одно событие, а два последовательных lifecycle-разрыва.

1. **Неполная миграция при создании backlog.** `BACKLOG.md` появился commit `79e81b67b03b37c4705315c6f5f0a50c8c1920d6` (`Add project backlog and defer SteamDB retries`, 2026-08-30) как новый файл с одной SteamDB-задачей. Это не была миграция всех уже существовавших пользовательских договорённостей. Его parent `989ccab679a34de38bd9a6a708329fdc4e01a92f` уже содержал в `PROJECT_RULES.md`, среди прочего, отдельное правило для релевантных временных `claim-to-keep` раздач, требования к реальным screenshots, purchase-family/better-edition логике, Windows-compatibility и achievements. Значит отсутствие старого требования в первоначальном backlog не доказывало его отмену или выполнение.

2. **Удаление проверяло отсутствие записи, но не её durable destination.** Несколько implementation/cleanup commits удаляли backlog-секции сразу после технического изменения. Особенно показательные случаи:
   - `5573f6fe2d841133de9b85dd09a8af54d0f9eb96` одновременно реализовал compact/collapsible score UI и бинарное отображение wishlist и удалил обе backlog-секции до пользовательской проверки;
   - `7bcff5c3fc656836a173e0d40f23f32f554c4206` реализовал media alias/coverage fix и одновременно удалил `Media: устранить карточки без скриншотов`, хотя требуемый production/user acceptance ещё не был сохранён;
   - `874891eb47ee0aa9905f7e9119e62739bad1f864` вынужден был восстановить score/wishlist/Chrome/media хвосты как `needs_user_verification` и явно записал, что такие задачи нельзя считать закрытыми до реальной пользовательской проверки;
   - `b38393819f912864364d1772518698811db54637` затем провёл массовую чистку и снова удалил эти `needs_user_verification` записи вместе с рядом плановых пунктов. Политика этого commit требовала убирать активные/завершённые хвосты из backlog, но тогда ещё не требовала атомарного доказательства назначения/acceptance/cancellation для **каждой** удаляемой записи.

Дополнительный слабый случай — `6088c1153bbc5e3832a59e8de3c14b09ab49f48a` (`Move package purchase options into active work`): backlog-пункт packages был удалён, но сам commit менял только `BACKLOG.md`; durable active state появился позднее. Задача в итоге полностью закрыта, но transfer не был атомарным.

Третья, более узкая проблема — **user/device acceptance мог оставаться только в живом чате**. Для Chrome shortcut implementation есть хороший durable trace (`db3241bb4008410194b040d844abcca8bf8aefaf`), а текущий директорский task-file `WORKER_TASK_TASK_MEMORY_AUDIT_01.md` отдельно фиксирует, что позже была положительная пользовательская проверка и задачу восстанавливать не надо. Однако отдельный исторический contemporaneous acceptance marker поиском не найден. Это не основание снова спрашивать пользователя сейчас, но это пример того, почему acceptance надо сохранять в durable state в момент подтверждения.

Текущий commit `e05c3f796d39e15933da82d0dc7e263fdefbddf4` уже исправил большую часть process gap текстовым инвариантом: explicit defer должен сразу получить durable запись; удаление из backlog допустимо только при явном active/completed/cancelled destination; `needs_user_verification` нельзя удалять без user check или точного переноса. Текущий `DIRECTOR_TASK_BOARD.md` дополнительно содержит rule 15: backlog removal requires destination/completion/cancellation evidence.

### Historical task ledger

| Task | Historical evidence | Current destination/status | Classification |
|---|---|---|---|
| Временные бесплатные `claim-to-keep` раздачи | Правило уже есть в `PROJECT_RULES.md@989ccab679a34de38bd9a6a708329fdc4e01a92f`; при создании backlog `79e81b6...` не мигрировано. Восстановлено и расширено до cross-platform в `e05c3f796d39e15933da82d0dc7e263fdefbddf4`. RECON report: `reviews/worker_reports/cross-platform-giveaway-recon-01.md`, report commit `1e6184d2235618336a5af402d76712f95b761adb`. | Есть в текущем `BACKLOG.md`; `DIRECTOR_TASK_BOARD.md` держит `ЧАТ 1` с Tier-1 implementation Steam + Epic KZ + GOG KZ. | `backlog_current` |
| Media/screenshots, включая `The Stronghold Collection` | Первое небезопасное удаление `7bcff5c3fc656836a173e0d40f23f32f554c4206`; восстановление как `needs_user_verification` `874891e...`; повторное удаление в `b383938...` без положительного user acceptance. `e05c3f...` фиксирует последующий отрицательный пользовательский результат и восстанавливает только reconciliation, не утверждая, что дефект всё ещё существует. | Текущий `BACKLOG.md`: `recovered_needs_reconciliation`. | `backlog_current` |
| SteamDB history tail | С 2026-08-30 был durable deferred state; количество unresolved постепенно уменьшалось. | Текущий `BACKLOG.md`/`CURRENT_TASK.md`: один `App_901735`, `blocked_low_priority`, exact KZ minimum не фабриковать. | `backlog_current` |
| Wishlist: хорошая скидка должна преодолевать слабое Taste | Добавлено в backlog 2026-08-30; cleanup его не удалил. | Представлено в текущем `BACKLOG.md`. | `backlog_current` |
| YouTube: выбранный релевантный русскоязычный обзор | Добавлено в backlog 2026-08-30; `CURRENT_TASK.md` также держит это как planned C. | Представлено в текущем `BACKLOG.md` и `CURRENT_TASK.md`. | `backlog_current` |
| Windows compatibility: automatic evidence source | Добавлено в backlog 2026-08-30; старые правила уже требовали учитывать практическую Windows-совместимость. | Представлено в текущем `BACKLOG.md`. | `backlog_current` |
| UI: возврат к началу исходной ленты | Backlog removal `d450bee55c2fa3713f5a8957747057570b3b9fe7`; ему предшествует implementation/styling chain, включая `b204db5ec96c1010c222e53906486c4993fc15af`. В entry не было отдельного real-device acceptance gate. | Реализация закрыта; повторного незакрытого хвоста не найдено. | `completed_with_evidence` |
| UI: Wishlist tab + `Показать в ленте` | Removal `6145c0a5eb312548c9c26c3cdc3c2aa2b7da2398`; перед ним implementation/mobile-tab chain, включая `7bf052711e69f0a3b02f921e0c0293f3b36632f2`. | Реализация закрыта; отдельного user-verification gate в исторической записи не было. | `completed_with_evidence` |
| UI: объяснять позицию ranking factors | Removal `ebff7017bfa90432c76b9f26048d1f1f2d9e0d80`. `PROJECT_ROUTES.md` update `ed4f7e2c30b05b4f51875493695676a578954d0e` фиксирует producer-owned `priority_factors`/`priority_vs_next`, успешный CI `33312895688` и production artifact commit `9e064fd65358de5dabf53f1c4879613020207ef7`. | Реализовано и задокументировано в canonical ranking route. | `completed_with_evidence` |
| Risk: явный status/fallback на каждой карточке | Removal `05a2a1a45f0ab7850cb41c507fde6454e8eb01da`; preceding production refresh `99907d34442c2470b12a2e318cc4a579ec5fcddb` добавляет structured `risk_status`, `risk_codes`, `no_confirmed_risk`/`descriptive_risk`/`serious_risk` в production artifacts. | Реализовано в production route. | `completed_with_evidence` |
| Независимый Taste review текущей сортировки | `50f25099859e0fe62ecd7b23e774975916009fed` меняет статус на `cancelled_unavailable` и прямо фиксирует решение пользователя не ждать недоступный review-чат; `321551ddacf9bbb59de7fdafce54b5a2d9756a37` затем убирает cancelled запись. | Намеренно не является зависимостью проекта. | `explicitly_cancelled_or_superseded` |
| Прозрачный числовой рейтинг 0–100 | Был отдельным backlog design item; `321551ddacf9bbb59de7fdafce54b5a2d9756a37` удаляет его после production V2 и создаёт более узкий follow-up на детализацию Taste. Текущие score contracts/UI/reports используют producer-owned `score_breakdown`. | Базовая 0–100 модель реализована; последующий Taste follow-up закрыт отдельно. | `completed_with_evidence` |
| Compact/collapsible score UI | `5573f6fe2d841133de9b85dd09a8af54d0f9eb96` реализовал и слишком рано удалил; `874891e...` восстановил `needs_user_verification`; `b383938...` снова удалил до durable acceptance. Позднее `reviews/worker_reports/detailed-score-ui-01.md` + `reviews/worker_reports/detailed-score-user-fixes-01.md`; commit `59ed5e1f3f493b81a1135a01047ad03b441819d4` фиксирует успешную повторную проверку на телефоне 2026-09-01. | Завершено после реального phone follow-up. | `completed_with_evidence` |
| Убрать вводящее в заблуждение `Вишлист 0/4` | Реализовано вместе с compact score в `5573f6...` (wishlist отображается бинарно), затем пережило тот же unsafe remove/restore/remove цикл. Текущий `web/score-details-ui.js` показывает `есть в желаемом` / `не в желаемом`; phone acceptance score UI сохранён в `59ed5e1...`. | Завершено и user-verified как часть score UI. | `completed_with_evidence` |
| Красивый Chrome shortcut icon | `db3241bb4008410194b040d844abcca8bf8aefaf` добавил manifest + normal/maskable icons и правильно оставил `implemented_pending_real_chrome_check`; `874891e...` усилил это до `needs_user_verification`; `b383938...` затем удалил хвост. Текущий `WORKER_TASK_TASK_MEMORY_AUDIT_01.md` содержит директорский checkpoint о более поздней положительной пользовательской проверке и прямо запрещает восстанавливать задачу только из-за исчезновения из backlog. | Не восстанавливать; acceptance checkpoint теперь durable в текущем audit input. | `completed_with_evidence` |
| Achievements: усилить значение для confirmed played/completed | Плановый пункт удалён `b383938...`. Implementation `729bba5e54db8980b8ad04d79b2c09c998bfa2b3` различает played и new/unconfirmed; regression `f19fa1339d8a8325e3627aaa344bccf094b039b6` проверяет played achievements bonus и сильный played/no-achievements penalty. | Реализовано и regression-protected. | `completed_with_evidence` |
| Taste: заменить coarse strong/moderate нормализованными факторами | Пункт удалён `b383938...`, когда Taste migration уже переходила в отдельный active flow. Cutover/production chain завершён; текущий `CURRENT_TASK.md` фиксирует `Taste V3 migration: complete`, binding `taste-v3`, а canonical ingest recovery сохранил 147 safe cache hits без re-evaluation. | Реализовано/cut over; отдельные 3 base-support rows не являются незавершённой Taste re-evaluation. | `completed_with_evidence` |
| Bundles/packages: более выгодный набор вместо отдельных игр | Backlog removal `6088c1153bbc5e3832a59e8de3c14b09ab49f48a` был неатомарным transfer, но задача позднее получила active durable state. Финальный report `reviews/worker_reports/package-acceptance-02.md`; close commit `d6b99014628c1912b0cfbf3deab4eb0bd1596bfb`; regressions/build/deploy success, включая double-count regression `b2680f5740d2a45ea23287c33b2263aafded9b9f`. | Полностью закрыто с acceptance evidence. | `completed_with_evidence` |
| Ranking/card explanation quality audit | Более поздний директорский план, не потерян при cleanup. | `CURRENT_TASK.md` section A: `planned`; текущий board также оставляет explanation-quality implementation deferred. | `active_or_blocked_durable` |
| Russian language availability как ranking factor | Отдельный будущий пункт виден в исторической director board и мог выглядеть как кандидат на потерю; targeted check показал, что он не исчез. | `CURRENT_TASK.md` section B: `planned`, минимум `yes/no/unknown + evidence`, сильный practical/final-ranking penalty при отсутствии русского. | `active_or_blocked_durable` |
| Guarantee Russian descriptions / translation runtime | Отдельная chain task-files/contracts/reports; не смешивается с language-availability ranking factor. | `CURRENT_TASK.md` section E: `runtime_acceptance_blocked_on_existing_scheduled_execution`; report `reviews/worker_reports/ru-translation-runtime-acceptance-01.md`, commit `8b9e6598f2b1233defc7b4e1262e97da0fdb46df`. | `active_or_blocked_durable` |
| Duration coverage/provider connectivity | Поздняя data-quality задача после score phone follow-up. | Текущий `DIRECTOR_TASK_BOARD.md`: duration connectivity blocked on user-provisioned IGDB secrets; task-files `WORKER_TASK_DURATION_*` остаются durable. | `active_or_blocked_durable` |

**Pre-backlog gap check.** Сверка `PROJECT_RULES.md@989ccab...` и соседних pre-2026-08-30 durable requirements с текущим `BACKLOG.md` + `CURRENT_TASK.md` + reports не выявила ещё одного незаписанного unfinished product requirement. Старые требования разложились так: giveaways -> восстановленный backlog/Chat 1; screenshots/media -> восстановленный reconciliation; packages -> completed; played achievements -> completed; Windows evidence -> current backlog; Russian description/language work -> current planned/blocked durable state. Бизнес-правила, уже полностью реализованные в producer/UI, не превращались искусственно в новые backlog items.

### Orphaned / ambiguous candidates

**Новых unrecovered `orphaned_probable` или `ambiguous_user_decision_needed` кандидатов не найдено.**

Два реально найденных разрыва уже были восстановлены до этого аудита и потому сейчас классифицируются по их текущему durable destination, а не как orphan:
- cross-platform claim-to-keep giveaways — pre-backlog migration orphan, восстановлен `e05c3f...`, сейчас есть и backlog entry, и активный Tier-1 worker route;
- media/screenshots user-verification tail — дважды удалялся без требуемого положительного acceptance; `e05c3f...` восстановил его как **reconciliation**, не как утверждение, что старый дефект точно сохраняется.

Chrome shortcut не требует нового user decision: текущий audit task уже содержит директорский checkpoint о положительной пользовательской проверке. Недостаток здесь только в качестве старого durable acceptance trace, а не в состоянии продукта.

### Confirmed safe removals

- `d450bee55c2fa3713f5a8957747057570b3b9fe7` — feed jump-to-start: закрывающая implementation chain существует.
- `6145c0a5eb312548c9c26c3cdc3c2aa2b7da2398` — Wishlist navigation: implementation/mobile UI chain существует.
- `ebff7017bfa90432c76b9f26048d1f1f2d9e0d80` — ranking explanation: producer-owned diagnostics + CI/production evidence.
- `05a2a1a45f0ab7850cb41c507fde6454e8eb01da` — risk status: structured production risk status/fallback доказан.
- `321551ddacf9bbb59de7fdafce54b5a2d9756a37` — cancelled independent Taste review удалён после explicit user cancellation; числовой V2 ranking удалён после production implementation и заменён более узким Taste-detail follow-up.
- `b38393819f912864364d1772518698811db54637` — **mixed, не считать целиком safe commit**. Из удалённых им пунктов compact score/wishlist позднее получили real-phone acceptance; Chrome имеет поздний positive user checkpoint; achievements и normalized Taste позднее получили implementation/validation. Но media removal в этом commit не имел требуемого acceptance и потому был правильно восстановлен `e05c3f...`.
- `6088c1153bbc5e3832a59e8de3c14b09ab49f48a` — packages transfer был неатомарным, но дальнейший active state и финальный `package-acceptance-02.md` полностью закрывают продуктовую задачу.

Небезопасные historical removals, которые нельзя использовать как хороший образец процесса: `5573f6...` (score/wishlist до user check), `7bcff5...` (media до published/user check) и media-часть `b383938...`.

### Prevention gap

Текстовый инвариант теперь достаточный по смыслу (`e05c3f...` + current board rule 15), но он всё ещё зависит от дисциплины редактора. Минимальный недостающий предохранитель — **один маленький same-diff validator для удалений из `BACKLOG.md`**.

Он должен fail-closed отклонять удаление task heading/ID, если тот же operational change не содержит ровно одного допустимого durable disposition:
1. exact active task/task-file + expected report;
2. completion/acceptance evidence, включая user/device acceptance, если оно было частью Definition of Done;
3. explicit cancelled/superseded evidence.

Для `needs_user_verification` validator должен отдельно запрещать “code exists => delete”. Никакой тяжёлой PM-системы не требуется: достаточно стабильного task key/heading и проверки deletion -> disposition. Creation-side gap уже закрыт текущим правилом “сделаем потом -> durable entry в том же директорском шаге”.

### Validation

Проверено выборочно и по lifecycle, без crawl production data и без product changes:
- текущие `DIRECTOR_PROTOCOL.md`, `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `DIRECTOR_TASK_BOARD.md`, `BACKLOG.md`, `CURRENT_TASK.md`, `PROJECT_RULES.md`, `PROJECT_DECISIONS.md`, `PROJECT_ROUTES.md`;
- `WORKER_TASK_TASK_MEMORY_AUDIT_01.md`;
- вся история `BACKLOG.md` от создания `79e81b67b03b37c4705315c6f5f0a50c8c1920d6` до текущего восстановления, с адресной проверкой removal commits;
- pre-backlog `PROJECT_RULES.md` на parent `989ccab679a34de38bd9a6a708329fdc4e01a92f`;
- исторические `CURRENT_TASK.md`/director transitions по Taste/packages/UI;
- relevant worker reports, включая `package-acceptance-02.md`, `detailed-score-ui-01.md`, `detailed-score-user-fixes-01.md`, translation/giveaway durable refs;
- targeted implementation/production evidence для jump-to-start, Wishlist navigation, ranking diagnostics, risk status, played-achievement weighting, Taste V3 и packages.

Изменён только этот report. `BACKLOG.md`, board, rules, contracts и product code в рамках worker task не менялись.

### Status

`complete`

### Recommended next step

Создать один bounded implementation task на маленький CI/diff validator `BACKLOG deletion -> durable disposition`; до его появления не делать массовые backlog cleanup commits без ручной проверки того же инварианта директором.

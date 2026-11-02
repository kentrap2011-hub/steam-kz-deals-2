# НОВЫЙ ЧАТ 4 — независимая проверка резервного хранения задач

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: director-recovery-fallback-existing-backup-independent-qa-01
Worker slot: НОВЫЙ физический ЧАТ 4
Mode: independent READ-ONLY QA of existing fallback, one report-only DRAFT PR
Report: reviews/worker_reports/director-recovery-fallback-existing-backup-independent-qa-01.md

## START / доказательства
Полностью прочитай CHAT_PROTOCOL.md и выполни START gate, затем этот task, адресные CHAT_CONTEXT.md и PROJECT_ROUTES.md. Работай исключительно в репозитории kentrap2011-hub/steam-kz-deals-2. Никаких других GitHub repositories; при неверном GitHub target STOP.

Пользователь поручил независимо проверить резерв, который директор уже создал для сохранения незарегистрированных задач при отказе GitHub. Это QA СУЩЕСТВУЮЩЕГО резервного состояния, не будущего кода из параллельного ЧАТА 1, который может проектировать долговечное восстановление. Не смешивать их результаты, не заявлять о наличии автоматики без кода и исполняемого теста.

Точки входа:
- GitHub issue https://github.com/kentrap2011-hub/steam-kz-deals-2/issues/375 (temporary recovery outbox), открытый и обновлённый директором; issue сам зависит от GitHub.
- ChatGPT Library: `/Director Recovery/director-recovery-handoff-2026-11-02.md`, stable file library id `libfile_f00828e9b7c08191b7faba8b0be16846`. Это отдельный от GitHub snapshot. Для независимой проверки пользоваться доступными Files/Library средствами ChatGPT; если новая беседа не имеет доступа — прямо указывать UNVERIFIED, не делать вывод по одному имени.
- Точные PR: #368/#374 merged; #376/#377 merged; #371 и #372 открыты при исходной проверке. Проверить фактическое текущее состояние и ограничить сравнение этими refs.
- Важный исходный факт: Library snapshot заявляет старое состояние #368/#374 как open, хотя сейчас они merged; это потенциально stale, проверять самостоятельно.
- Отказ REGISTER в одном предыдущем tools call был tool safety rejection ДО записи; другие GitHub reads и issue create успешны. Не путать со всеобщим GitHub outage. Отдельная prewrite schema error с недопустимым публичным `PR #` дала 0 writes.

## Проверить независимо
1. Существует ли *физически* независимое от GitHub хранилище Library и можно ли прочитать сохранённый текст; содержатся ли точные ids/source/owner/status и достаточно ли сведений для восстановления при недоступном GitHub. Отличить файл в библиотеке от отсутствующего пути, чатового текста и GitHub issue.
2. Сверить содержимое Library snapshot, Issue #375, последнего Board и адресных registry IDs со свежими GitHub фактами. Отметить устаревшие сведения, ошибки статусов, пропущенные задачи, риск двойного запуска и отсутствие автообновления; не исправлять их молча.
3. Строго оценить сбои по отдельности: (a) невалидный prewrite input, (b) блокировка OpenAI tool safety, (c) отказ GitHub writes при доступных reads, (d) полный GitHub outage, (e) недоступность Files/Library, (f) разрыв беседы ChatGPT, (g) восстановление после сбоя с одновременным изменением main. Для каждого: где можно записать, где реально хранится, кто вручную переносит, как обнаруживается ошибка, предотвращается дубль и проверяется восстановленный canonical main.
4. Построить 3-6 проверяемых safe сценариев на существующих фактах/контрактах, без фактического отключения GitHub, уничтожения резервов, опасных writes и обхода политик инструментов. Если симуляции нет, явно static-only. Проверь, что fallback не является альтернативной авторизацией на merge/semantic/production и не обещает automatic replay/monitoring.
5. Дать один точный verdict `PASS_CONFIRMED_RECOVERY` / `PARTIAL_BACKUP_ONLY` / `FAIL_NO_INDEPENDENT_BACKUP` / `BLOCKED_EVIDENCE`. В отчёте отделить наличие резервной записи от работоспособного восстановления и от будущего исправления ЧАТА 1. Если FAIL/PARTIAL, дать только адресные изменения/тесты для последующего использования ЧАТОМ 1 без нового широкого аудита.

## Строгие границы и результат
READ-ONLY: ничего не менять в GitHub Issue #375, Library, source PR, Board, registry, Director protocols, scripts, production или V1/V2/Deep. Никакого real semantic run, retry/recovery trigger, workflow dispatch, разрешения на source MERGE или Scheduled Task. Разрешено сохранить ОДИН отчёт `reviews/worker_reports/director-recovery-fallback-existing-backup-independent-qa-01.md` в отдельном report-only DRAFT PR, если GitHub доступен. При полном отказе GitHub вернуть полный копируемый текст отчёта пользователю/директору без ложного утверждения о PR — это не означает успешной публикации. Итог: проверенные links/refs, конкретные найденные gaps, ограничения доступа, verdict и один следующий bounded actor/step. Сам worker не объединяет PR.

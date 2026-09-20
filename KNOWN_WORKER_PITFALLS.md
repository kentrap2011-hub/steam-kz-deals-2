# KNOWN WORKER PITFALLS

Компактный канонический список **повторяемых cross-cutting operational failure recipes** для worker-чатов.

Граница с другими файлами:
- `PROJECT_ROUTES.md` отвечает **где/как быстро найти** уже исследованный участок проекта;
- `PROJECT_DECISIONS.md` отвечает **почему** принято неочевидное продуктовое/архитектурное решение;
- этот файл отвечает **какую уже доказанную операционную ошибку не повторять и какой bounded recovery применять**.

Не использовать как общий troubleshooting diary. Добавлять только повторяемые, доказанные и переносимые между задачами ошибки; одноразовые дефекты остаются в своих worker-report/run refs. Перед задачей читать только релевантную запись по известному trigger, а не весь файл «на всякий случай».

---

## PITFALL-001 — Проверка proxy/source shape вместо фактического поведения

**Trigger / symptom:** regression/acceptance проверяет JS property, конкретную форму присваивания, строку copy, asset token или другой implementation marker, хотя Definition of Done относится к реальному поведению/выходу.

**Do not repeat:** не считать зелёным доказательством тест, который может пройти при нарушенном пользовательском/семантическом результате; не сохранять stale static assertions после осознанного refactor формы реализации.

**Correct move:** проверять observable behavior/output и явно сопоставлять каждый обязательный DoD-пункт с исполняемой проверкой либо помечать его как непроверенный. При refactor implementation/copy/asset wiring обновлять зависящие static guards атомарно. Real-device/user judgment сохранять отдельным acceptance-слоем, если он действительно требуется.

**Evidence refs:** `reviews/worker_reports/detailed-score-user-fixes-01.md`; `reviews/worker_reports/package-ui-blocker-fix-01.md`; `reviews/worker_reports/package-acceptance-01.md`; `reviews/worker_reports/package-acceptance-02.md`; package/UI blocker fix commit `c243dfe498abec27923bc7f229f34fc82b5c26f0`.

---

## PITFALL-002 — GitHub Pages concurrency и повторный upload того же artifact

**Trigger / symptom:** Pages deploy отменён `concurrency: pages`, либо rerun падает на duplicate `github-pages` artifact после того, как исходный run уже успел выполнить artifact upload.

**Do not repeat:** не rerun-ить вслепую любой cancelled/failed Pages run и особенно не повторять run, который уже загрузил Pages artifact.

**Correct move:** сначала определить, на каком step остановился run. Если artifact уже был uploaded, выбрать безопасный pre-upload cancelled run, новый поддерживаемый trigger/run или более новый успешный deploy, который доказанно содержит нужный commit. Concurrency cancellation сама по себе не является продуктовым дефектом.

**Evidence refs:** `reviews/worker_reports/detailed-score-ui-01.md`; `reviews/worker_reports/compact-purchase-options-01.md`; `reviews/worker_reports/detailed-score-user-fixes-01.md`; successful recovery job `99817807119`.

---

## PITFALL-003 — IMPLEMENT рекомендуется до доказательства canonical authority/source route

**Trigger / symptom:** worker собирается рекомендовать следующий `IMPLEMENT`, который добавит/изменит source, runtime, workflow, schedule, queue, retry/checkpoint или ownership, но ещё не доказано, какой canonical contract это разрешает и какой component владеет ответственностью.

**Do not repeat:** не переносить architecture preflight на следующего worker-а и не рекомендовать IMPLEMENT на основании предполагаемого «уже разрешённого» source/path без проверки canonical authority.

**Correct move:** до формулировки `Recommended next step` пройти тот же architecture preflight, что и перед непосредственной реализацией. Если authorizing contract/route/owner не доказан — рекомендовать bounded `RECON` или `CONTRACT`, а не `IMPLEMENT`.

**Evidence refs:** `reviews/worker_reports/duration-data-diagnosis-01.md`; `reviews/worker_reports/duration-source-recon-01.md`; `reviews/worker_reports/duration-provider-recon-01.md`; `reviews/worker_reports/duration-contract-01.md`.

---

## PITFALL-004 — Неподтверждённая причина внезапного прерывания worker-сессии

**Trigger / symptom:** worker не завершил обязательный task-checklist, а следующий доступный turn начинается уже после прерывания предыдущего выполнения; при этом нет явного system/tool error, подтверждающего причину остановки. Особенно важно при повторных случаях, когда возникает соблазн назвать причиной `context limit`, `timeout`, `tool limit` или другую платформенную границу без фактического сигнала.

**Do not repeat:** не угадывать тип лимита и не писать, что «исчерпан контекст», «закончился runtime», «сработал timeout» и т.п., если такого сообщения/кода ошибки worker реально не видел. Не считать `причина неизвестна` достаточным recovery-решением. Не переходить в цикл `неизвестно -> просто попробовать ещё раз` без воспроизводимой диагностики.

**Mandatory reproducibility trace:** worker должен вести достаточно точный след выполнения, чтобы после неизвестного прерывания можно было воспроизвести участок работы от последнего durable checkpoint до точки остановки. След должен сохраняться на естественных task-checkpoint'ах, а не только пытаться восстанавливаться задним числом после падения. Для каждого шага фиксировать, насколько это доступно без секретов:
1. последовательный номер шага;
2. task-checklist item / стадия;
3. конкретное действие;
4. tool/action/command;
5. существенные аргументы или их безопасную точную форму: repository/path/ref/query/operation type, размер batch/range/payload и другие параметры, влияющие на поведение; секреты не записывать;
6. началось ли действие и был ли получен ответ;
7. краткий observable result: success/error/no response, returned ref/commit/run/job при наличии;
8. следующий запланированный шаг.

Если задача делает GitHub writes, trace можно держать в task-specific draft report/handoff на worker-ветке и обновлять на естественных стадиях; финальный шум можно свернуть перед merge, но при прерывании trace должен остаться доступен. Цель — не подробный дневник рассуждений, а **reproduction recipe** действий.

**Mandatory interruption record:** после прерывания зафиксировать:
- последний завершённый обязательный checklist item;
- последний durable checkpoint;
- точную последовательность trace-шагов после него вплоть до остановки;
- последний вызванный tool/action и был ли получен его ответ;
- exact visible system/tool error, если он был;
- иначе дословно `system/tool error before interruption: none exposed`;
- текущую branch/commit/write state;
- мог ли тот же чат принять следующее пользовательское сообщение;
- подтверждённую причину, если известна; иначе `причина неизвестна`.

**Controlled reproduction before blind retry:** если причина не видна, задача не просто продолжается с места остановки. Сначала воспроизводится сохранённый recipe в максимально эквивалентных условиях:
- тот же порядок действий;
- те же tool/action types;
- те же существенные параметры и сопоставимый объём данных;
- тот же тип стадии (`read`, `write`, `validation`, `merge`, response composition и т.п.).

Если точное повторение могло бы сделать опасный/необратимый production write, воспроизводить на disposable branch, synthetic fixture или другом безопасном эквиваленте, сохраняя форму операций и размер нагрузки. Production состояние не повреждать ради диагностики.

**If interruption reproduces:** считать это диагностическим сигналом и переходить к локализации. Повторять не всю задачу, а уменьшать воспроизводимую последовательность: разбивать recipe на части, проверять меньшие диапазоны/одиночные действия и сравнивать, при каком минимальном наборе шагов обрыв возвращается. Цель — получить минимальный воспроизводимый участок и определить, связан ли он с конкретным tool, operation type, payload size, стадией, длительностью или иной наблюдаемой переменной.

**If interruption does not reproduce:** не объявлять проблему решённой. Зафиксировать `not reproduced`, условия повтора и отличия от исходного инцидента, затем разрешается controlled resume с продолжением trace. Следующее неизвестное прерывание сравнивается с уже сохранённым recipe.

**Diagnostic escalation:**
- После первого неизвестного прерывания допускается один controlled reproduction + resume по правилам выше.
- Если обрыв воспроизводится или неизвестное прерывание повторилось, обычный blind retry запрещён; выполняется bounded diagnostic pass с минимизацией reproduction recipe.
- Если доступна дополнительная platform/system telemetry, использовать её. Если внутренние telemetry/error codes не предоставляются worker-у, фиксировать `platform interruption telemetry: not exposed`.
- Финальная классификация должна быть максимально узкой: например `confirmed tool/network error`, `confirmed repository/action failure`, `repeatable tool-specific interruption`, `repeatable payload/size-sensitive interruption`, `repeatable stage-specific interruption`, `platform-level interruption with no exposed telemetry`, либо другой доказанный класс.
- Формулировка просто `причина неизвестна` после воспроизводимого повторного случая недостаточна.

**Recovery after diagnostic:** если выявлена техническая причина — исправить или обойти именно её в отдельном разрешённом scope. Если остался класс `platform-level interruption with no exposed telemetry`, продолжение допускается только с сохранённым reproduction recipe и более частыми durable checkpoints, чтобы следующий инцидент можно было сравнить и воспроизвести. Это mitigation, а не утверждение, что root cause известен.

**Evidence refs:** повторные прерывания `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01.md` и `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PERSISTENCE_BRIDGE_01.md`, где платформа не предоставила worker-у подтверждённый код причины; прежняя формулировка про «исчерпанный контекст» была впоследствии признана неподтверждённой.

---

## PITFALL-005 — Regression test hardcodes yesterday's canonical live group

**Trigger / symptom:** a regression intended to prove a generic dossier invariant reads the current production work manifest but also asserts exact historical appids/titles for `g000001`. A legitimate GitHub-owned snapshot refresh changes the canonical expected group, so CI fails even though the semantic invariant under test is still correct.

**Do not repeat:** do not bind generic runtime/contract regressions to one historical snapshot id, group sequence payload, appid set, title set or specific current game unless the task is explicitly a regression for that immutable production incident.

**Correct move:** when a test deliberately exercises the current canonical descriptor, derive appid/title/order from that descriptor and assert the invariant against those immutable descriptor values. Keep incident-specific appids/snapshots only in dedicated incident fixtures/reports. This preserves fail-closed semantic checks without turning normal daily snapshot rotation into a false failure.

**Evidence refs:** `WORKER_TASK_TASTE_DOSSIER_IDENTITY_PROVENANCE_GENERATION_FIX_01.md`; `reviews/worker_reports/taste-dossier-identity-provenance-generation-fix-01.md`; fixes to `scripts/test_taste_dossier_transient_author_fallback.py` and `scripts/test_taste_dossier_contract_contradictions_fix.py`.

---

## PITFALL-006 — Content-binding revision change leaves stale exact-string regression assertions

**Trigger / symptom:** a legitimate content-complete contract/schema/prompt change intentionally advances `contract_revision`, `schema_revision` or `worker_prompt_revision`, while focused regression suites still assert the previous exact revision string. CI then fails on a stale binding expectation even though the semantic guard itself is still valid.

**Do not repeat:** do not wait for CI to discover old exact revision literals one test at a time, and do not weaken semantic assertions merely to make the revision update pass.

**Correct move:** before the final PR run for any intentional dossier binding revision, perform one bounded scan of the focused dossier regression files for exact `contract_revision`, `schema_revision` and `worker_prompt_revision` expectations. Update only stale expected binding literals to the new canonical values; keep behavioral/semantic assertions unchanged. Then run the normal focused dossier gate once. When useful, pin unchanged semantic authorities separately (for example the strict-validator Git blob SHA) so a binding-only update cannot hide a semantic change.

**Evidence refs:** `WORKER_TASK_TASTE_DOSSIER_VALIDATOR_GENERATOR_PARITY_FIX_01.md`; `reviews/worker_reports/taste-dossier-validator-generator-parity-fix-01.md`; PR #70, where the first dossier CI pass exposed a stale strict-recovery `worker_prompt_revision` assertion after the intentional parity binding update.


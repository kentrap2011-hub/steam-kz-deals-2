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

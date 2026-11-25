# НОВЫЙ ЧАТ 1 — независимая L3 QA исправления путей Lean Writer

Task ID: dossier-lean-auto-path-layout-pr490-l3-independent-qa-01
Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Worker: NEW PHYSICAL ЧАТ 1
Mode: independent source-only L3 QA of PR #490. Report-only PR; NO source modification, no live run.

## START
1. Работай ТОЛЬКО в `kentrap2011-hub/steam-kz-deals-2`; `main` — source of truth. Не ищи, читай, используй или меняй другие репозитории. Если GitHub/tool указал другой target — STOP и исправь target.
2. Сначала ПОЛНОСТЬЮ прочитай актуальный `CHAT_PROTOCOL.md` из main и выполни START gate; далее `CHAT_CONTEXT.md`, этот task, релевантные `PROJECT_ROUTES.md`, `PROJECT_DECISIONS.md`, `KNOWN_WORKER_PITFALLS.md`, `config/execution_ownership_contract.json`, `config/dossier_lean_writer_auto_ready_v1.json` и только адресные writer/claim contracts. Не проводи широкий аудит всего репозитория.
3. Source PR #490: source-only path fix от ЧАТА 3, branch `fix/dossier-lean-auto-writer-sandbox-path-layout-20261125`, на входе HEAD `89939b27f3f5c2a5c17a029c6b37110318cfc52e`, base `main@2a98a3d57b2a97e2c1239804ec0285a55220b513`. Перечитай live HEAD и actual CI на этом HEAD. В момент регистрации CI checks synthetic-v2, backlog-disposition, validate = 3/3 PASS. Не считай self-tests полноценной независимой L3 QA.
4. Реальное GitHub Actions #45628656098, job #139255581611, исполнилось на main `4ccf23005166a1ae3c35800e1b38e0c295e29d8e`: `V2 single-item paths must be separate writer-owned subdirectories`. Сверь точный log/state при необходимости, не повторяй старый GitHub event bug.
5. КРИТИЧНО: историческая автоматическая попытка уже СОЗДАЛА immutable one-use claim `refs/heads/dossier-lean-auto-attempts/cdcdb4951e2fc98336729af75b954da4` SHA `6df354d024b0e3104ee408e815a1e5d141fb8e84`; frozen sandbox SHA `d1b9a9e78dcde879a03370682ade4969763fd9d1`, 0/6 accepted docs и 0/6 receipts. Это POSTCLAIM терминальная ошибка, в отличие от предыдущих preclaim. Claim подтверждён live GitHub и не подлежит перезаписи; без нового явного отдельного разрешения не бывает новой реальной попытки.

## Independent substantive QA
A. На текущей реальной дельте проследи `scripts/dossier_lean_writer_auto_ready.py::sandbox_writer_destinations()` → `batch.paths(trial_id)` → `drain_buffered_groups()` → `_drain_notes_v2_individual()`, включая cwd, temp sandbox checkout, effective absolute `store_dir` и `accepted_dir`. Подтверди обе writer-owned directories находятся строго внутри нужного sandbox Git worktree, разделены, соответствуют прежнему V2 namespace/contract, нет path traversal/symlink/foreign-trial пересечения и запись в `main`/canonical невозможна.
B. Адресно проверь протестированные real temporary Git six-input positive/readback и негативные cases старых relative/out-of-root путей, overlap store/receipt, strict/manual mode, 12-file transaction. Повтори лишь нужные безопасные offline tests, если инструмент позволяет, без GitHub live runner. Цитируй exact source lines/test cases, не только слова автора отчёта.
C. Независимо убедись, что изменены только path binding и целевые regressions; owner/auth/event/claim/no_retry/shared lock/SHA/year/edition/TTL/canonical/Deep/production и immutable receipts не ослаблены. Сравни exact final source HEAD и обязательный GitHub CI. При конкретном material failure → CHANGES_REQUIRED с минимальным reproduction. Не превращай это в неограниченную проверку прошлого Research/Assembly.
D. Source PR acceptance НЕ равно live owner recovery permission. Подтверди claim уже израсходован; не делай rerun старых Actions (#45540222575, #45591943959, #45603534459, #45628656098), не меняй claim, не создавай новый grant/nonce, не запускай workflow, writer, semantic Research/Assembly, Deep или production. Дай директору ровно один минимальный дальнейший approval boundary по отдельной новой авторизации (без её выдачи).
E. Финальный verdict: `PASS_FOR_DIRECTOR_MERGE_REVIEW`, `CHANGES_REQUIRED` или `BLOCKED_EVIDENCE`; отсутствующую проверку не объявляй PASS.

## Deliverable
Сохрани **report-only** PR с единственным новым файлом `reviews/worker_reports/dossier-lean-auto-path-layout-pr490-l3-independent-qa-01.md` (или при технической необходимости доказанный scoped report-only diff). В отчёте: проверенный exact HEAD, перечисление actual checks и негативных случаев, risks, CI, proof of postclaim spent, один verdict, next Director action. Не self-merge source PR или QA PR, не делать live acceptance. Сдать отчёт директору; после финального отчёта слот ЧАТ 1 свободен.

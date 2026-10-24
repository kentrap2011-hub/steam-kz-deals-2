# ЧАТ 3 — завершение удалённого сохранения Research Notes V2 (PR #270)

**Task:** `dossier-v2-research-github-persistence-finish-01`  
**Status:** `BLOCKED_GITHUB_WRITE_AUTHORITY` — реализация предложена, но настоящий GitHub Research Notes V2 НЕ публиковался, исполнение тестов PR #270 не подтверждено. **Не объединять.**  
**Base:** `main`, изначальная база существующего draft PR #270 `09cc60b91965cb6dd054c26b69ca9792da604274`; продолжена прежняя ветка `implement/dossier-v2-research-per-item-receipts-01` с исходного HEAD `676d7473e5fda85e8e07bfdbb206859d69e3be69`.  
**Remote-writer code SHA:** `017fa213b9c7d09f9051915ac6f13d9eec908cb8` (после исправлений helper + тестов); служебная запись в `CURRENT_TASK.md` — `07b6b80fb2c11e303481e163224f78a8827ee079`. Финальный PR HEAD после добавления этого отчёта следует брать из GitHub PR #270.

## Architecture preflight

1. `config/execution_ownership_contract.json`: GitHub управляет scope, строгими проверками и долговременной записью. Интерактивный чат меняет лишь неактивный исходный код.
2. `config/dossier_research_notes_v2_contract.json`: `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, V1 и строгое трёхигровое принятие не заменяются. PR #266/issuer/grant/marker остаются отдельными.
3. Ни очереди, выбора игр, повторных попыток, Scheduled Task, нового GitHub Actions или второго механизма окончательной публикации не добавлено.

## Реализовано в существующем адаптере

- `scripts/dossier_notes_v2_per_item_receipts.py`: `publish_candidate_remote`, `publish_receipt_remote` и `publish_one_research_item_remote` передают **одну конкретную игру**. Используется прежний `prepare_candidate / inspect_candidate / prepare_receipt / inspect_receipt_commit`, существующий `dossier_research_notes_v2` и `dossier_two_stage_staging`; новых семантических валидаторов нет.
- Фиксированная явная ветка `sandbox/…`, ожидаемый parent SHA, fresh `ls-remote` + `fetch`, чистое одноразовое Git worktree, один create-only файл на коммит, проверка single-parent/diff/blob/binary bytes и обычный **non-force fast-forward** Git push. Конфликт, несоответствие parent, дубликат, пустые bytes или отказ push означают отказ без retry.
- После каждого push заново проверяются remote ref, Git commit, parent, файл и bytes. Для `github_receipt_confirmed=true` дополнительно необходимы токен, точный GitHub repo/remote и **подтверждение ref и blob через аутентифицированное чтение GitHub REST**. Перед push также проверяется authenticated ref. Локальный `bare`-репозиторий даёт лишь `remote_git_confirmed=true`, **никогда** `github_receipt_confirmed=true`.
- Первый подтверждённый candidate и отдельный подтверждённый receipt показываются отдельно; семантическая и каноническая приёмка всегда false. Если кандидат попал в GitHub, а запись receipt впоследствии оборвалась, helper не подделывает успех и запрещает слепое повторное создание: требуется отдельная проверка удалённого состояния.
- Ничего не обходит отсутствующий реальный issuer/семантическое разрешение. Даже структурно корректный issuer не подтверждает, что Research был разрешён. Вызов реальной записи возможен только из позднее разрешённого владельцем GitHub процесса, не из этого developer-чата.

## Новые проверки и их фактический статус

`scripts/test_dossier_notes_v2_per_item_receipts.py`: сохранены прежние 10 disposable-Git тестов и дописаны **4** проверки на отдельный remote candidate→receipt, независимый успех B при ошибке A, полную функцию одной игры и remote collision/stale head/ложную GitHub идентичность.

**Не выполнены:** `python scripts/test_dossier_notes_v2_per_item_receipts.py -v` и старые V2/V1 регрессии. Контейнер не содержит checkout (`/mnt/data/scripts/test_dossier_notes_v2_per_item_receipts.py` отсутствует); `git ls-remote https://github.com/kentrap2011-hub/steam-kz-deals-2.git HEAD` даёт `Could not resolve host: github.com`. При этом доступны Python 3.13.5, Git 2.47.3, jsonschema 4.26.0. Чтение тестового кода **не** считается их запуском. Не запускался ни один workflow dispatch; новых CI/workflow не создано. На кодовом commit `017fa213...` GitHub combined statuses пусты; прошлые unrelated checks #270 не проверяют этот remote-writer. Новый final HEAD требует отдельного запуска тестов и независимой проверки.

## Изменённые пути PR #270

1. `scripts/dossier_notes_v2_per_item_receipts.py` — дополнен remote create-only Git transport и GitHub authenticated read-back.
2. `scripts/test_dossier_notes_v2_per_item_receipts.py` — сохранён исходный набор, добавлены 4 регрессии на remote путь.
3. `CURRENT_TASK.md` — минимальная временная запись BLOCKED, без удаления других активных задач.
4. `reviews/worker_reports/dossier-v2-research-github-persistence-finish-01.md` — этот отчёт.
5. Уже существующий `reviews/worker_reports/dossier-v2-research-per-item-receipts-implement-01.md` из прежнего PR — не изменён.

Нет изменения семи файлов PR #266, PR #274, production, V1, старого Dossier, исходных 18, Actions/CI или scheduler.

## Одно конкретное внешнее условие

Нужен **разрешённый GitHub-owned writer-контекст** с подтверждённым владельцем issuer/семантическим разрешением и полномочиями записи/чтения строго выбранной sandbox-ветки (`origin` и GitHub API token). **Сейчас такой разрешённый контекст не выдан.** Реальную публикацию не проводили. Функция технически описывает сохранение одной игры с проверкой удалённого GitHub; её работоспособность именно на GitHub, а не на disposable fixtures, до разрешённого испытания остаётся неподтверждённой.

**Следующее действие:** исполнить написанные регрессии в checkout точного финального PR HEAD, провести независимый review; отдельно разрешать любые реальные испытания V2. Ни один QA/CI или local-Git результат не должен объявляться публикацией семантического исследования.

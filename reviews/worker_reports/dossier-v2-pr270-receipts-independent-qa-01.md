# ЧАТ 2 — независимая QA PR #270: поштучные Research Notes V2 receipts

**Task:** `dossier-v2-pr270-receipts-independent-qa-01`  
**Verdict:** `BLOCKED_TEST_EXECUTION` — **не принимать PR #270 в main до фактического запуска новых и уместных старых тестов**. Это не установленный дефект исходного кода и не `PASS_FOR_DIRECTOR_MERGE_REVIEW`.  
**Exact implementation HEAD:** `676d7473e5fda85e8e07bfdbb206859d69e3be69` (live PR HEAD подтверждено).  
**Source of truth:** `main`; QA inspection is read-only, no Research/Assembly/production.

## Проверено чтением текущего кода

- В PR #270 **ровно три** пути: `scripts/dossier_notes_v2_per_item_receipts.py`, `scripts/test_dossier_notes_v2_per_item_receipts.py`, отчёт ЧАТА 3. Ни один из семи файлов PR #266, код V1, production, workflows/CI не изменён.
- Адаптер опирается на уже существующие `dossier_research_notes_v2.py` и `dossier_two_stage_staging.py`, не вводит самостоятельный GitHub writer, запуск семантики, retry/scheduler или новую очередь.
- `issuer_structure` связывает отдельный marker, его nonce/parent, manifest с точными исходными 18, одно-add authorization, scoped grant и frozen исходные blob SHA. Поля actor/run — **только структурные локальные утверждения**, не проверенная подлинность GitHub Actions или одобрение Research.
- `prepare_candidate`/ `inspect_candidate` предназначены для одной игры: неизменяемые AppID/группа/assignment/выпуск, проверка строгой Notes schema, приватности/ссылок, первичного единственного добавления файла, Git blob/raw и запрет переписывания, включая восстановление старых bytes. Неуспешные проверки не обозначаются принятием.
- `prepare_receipt` строит фиксированный create-only путь `<trial>/g<group>/<appid>--<assignment>--research.json` для одной игры и одной фазы; существующий путь блокирует повторную выдачу. `inspect_receipt_commit` проверяет single-add commit, исходного родителя, идентичность содержимого и отсутствие последующих перезаписей.
- `github_receipt_confirmed=false`, `semantic_quality_accepted=false` и `canonical_acceptance=false` сохраняются и при успешном локальном доказательстве. `attempt_state=unknown`. Локальное присутствие файла не выдается за подтверждённую удалённую публикацию или качественную приёмку.
- В тестовом модуле заявлены 10 одноразовых Git tests: корректная отдельная игра, повторная запись и подмена, переписывание receipt с восстановлением, неправильная группа/AppID, поддельные issuer/grant/nonce, плохой Git parent, повреждённый JSON, отсутствие результата, лишний файл и две параллельные локальные ветки. **Сценарии прочитаны, но их прохождение не доказано.**

## Тесты и CI — фактическая граница

- Выполнена попытка **точной команды** `python scripts/test_dossier_notes_v2_per_item_receipts.py -v` из `/mnt/data`. **Exit code 2**: `can't open file '/mnt/data/scripts/test_dossier_notes_v2_per_item_receipts.py': [Errno 2] No such file or directory`. Файлы репозитория в среде локально не смонтированы.
- `git ls-remote https://github.com/kentrap2011-hub/steam-kz-deals-2.git HEAD` → `Could not resolve host: github.com`: checkout не удалось получить. Наличие `git`, Python и `jsonschema` подтверждено, но этого недостаточно без полного checkout и зависимостей.
- Старые `scripts/test_dossier_research_notes_v2.py` и V1 two-stage тесты **не запускались** по той же причине. Ни одна серия тестов не объявляется пройденной.
- GitHub по **этому exact HEAD** сообщил только два успешных check-runs: `backlog-disposition` (Actions run `40095389749`) и `validate` (run `40095389760`, site tasks). Они **не исполняли** тесты данного адаптера. Combined commit statuses — пусто. Это не доказательство работы нового кода.
- Реальная одновременная запись нескольких writers с удалённой compare-and-swap, достоверная идентичность GitHub Actions, семантическая/каноническая приёмка и подтверждённая удалённая receipt **не реализованы и не разрешены** в этой ограниченной offline задаче. PR #266 отдельно draft/unmerged; это не полномочие запускать Research.

## Действие директора

**Не объединять PR #270 при данном вердикте.** Чтобы снять именно блокер, требуется исполнить уже написанные новые тесты на авторизованном checkout **этого же HEAD**, плюс релевантные существующие V2/V1 тесты, и предъявить полные результаты. При изменении HEAD назначить новое exact-SHA QA; **не создавать CI, новые тесты, Actions или автоматизации**. Затем директор решает о принятии только **неактивного offline компонента**, без разрешения настоящего Research/Assembly или записи в GitHub.

Дополнительная осторожность: `introduction_commit=None` классифицируется как `missing_research_transport` по отсутствию переданной ссылки на коммит, а не по доказанному отсутствию пути в удалённом GitHub; будущий writer обязан отдельно проверять действительное удалённое состояние перед выдачей необратимого receipt. Это не свидетельство настоящего удаления и не разрешение «принять как успешное».

# WORKER TASK — TASTE DOSSIER POST-SCG LIVE ACCEPTANCE 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-post-scg-live-acceptance-01`
Mode: `READ / VALIDATE`

## START gate

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate.
Затем открой этот task-файл из `main` и зафиксируй checklist.

## Goal

Оценить первый live Scheduled Task run после:
- принятого language-binding fix;
- принятого SCG-01..SCG-06 implementation;
- activation fresh snapshot `00072072b0b382e6b973f448ce00b4aaaeccb2dbe355ca323de1785ccc0bd34c`.

Это **READ / VALIDATE**, не IMPLEMENT.
Не исправляй prompt/contract/validator/runtime в этой задаче.
Не запускай Scheduled Task повторно.

## Authoritative manual UI result

Scheduled Task UI worker надёжно читать не умеет.
Следующий дословный результат предоставлен пользователем вручную и считается authoritative confirmed source для live behavior:

> Текущая canonical-проекция обновилась на snapshot `00072072…bd34c` от 18 сентября: ожидается `g000001`, 564 элемента остаются, backlog не завершён.
>
> Для `g000001` выполнена обязательная проверка контрактов и начато evidence-исследование трёх точных элементов: `Baldur's Gate 3 - Digital Deluxe Edition DLC`, `Hellish Quart`, `Tetris® Effect: Connected`. Группа не опубликована: в пределах этой инвокации не удалось получить достаточно надёжных attributable item-level русскоязычных feedback records для полного трёхигрового V2-кандидата. По контракту неполную группу публиковать нельзя, поэтому create-only write не выполнялся.

Не пытайся получить Scheduled Task UI самостоятельно и не ставь под сомнение этот дословный UI-result как источник observed live behavior.

## Critical contract question

Проверь на fresh `main`, действительно ли отсутствие достаточного attributable Russian-language player feedback само по себе делает dossier/game/group неполным.

Обязательно reconcile active:
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- canonical strict validator только в объёме, нужном для этого exact вопроса;
- current snapshot/index/descriptor metadata только если нужно подтвердить binding/identity, без broad artifact mining.

Особенно проверь canonical Russian attempt states:
- `found_and_used`;
- `searched_not_found_or_insufficient`;
- `source_access_unavailable`.

Установи, допускает ли contract complete V2 dossier при добросовестной Russian-language попытке, когда Russian player feedback не найден или недостаточен, при условии что остальной required evidence достаточен.

## Required classification

Классифицируй live outcome ровно в одну из категорий:

1. `accepted_live_behavior`
   - только если contract действительно требует достаточный Russian attributable feedback для complete dossier/group и observed stop был правильным;

2. `rejected_worker_contract_misread`
   - если active contract допускает `searched_not_found_or_insufficient` / `source_access_unavailable`, а worker ошибочно сделал отсутствие Russian feedback самостоятельным blocker-ом;

3. `rejected_general_evidence_insufficient`
   - если UI формулировка про Russian feedback неполна, но canonical evidence proves хотя бы один из трёх dossiers объективно не мог быть complete по более общей evidence/identity причине;

4. `blocked_insufficient_evidence_to_classify`
   - если по canonical files + authoritative UI-result нельзя честно различить причины без запрещённого глубокого расследования.

Не смешивай категории.

## Acceptance questions

Report обязан ответить обычным человеческим языком и технически:

1. Что именно произошло в live run?
2. Было ли правильным не публиковать partial 3-game group?
3. Было ли правильным считать отсутствие достаточного Russian feedback причиной, по которой full dossier/group нельзя завершить?
4. Что canonical contract требует при `searched_not_found_or_insufficient`?
5. Есть ли доказательство отдельной общей insufficiency по BG3 DLC, Hellish Quart или Tetris, или UI-result указывает только на Russian-evidence blocker?
6. Является ли этот run clean live acceptance?
7. Если нет — какой **один** bounded follow-up нужен: contract/prompt fix, runtime/prompt-interpretation fix, либо иной narrow recon?

## Architecture constraints

- GitHub остаётся control plane.
- Group size = 3.
- Не split-ить группу по играм.
- Не добавлять retry/healing.
- Не ослаблять strict validator.
- Не менять parallel buffer / maximal contiguous prefix.
- Не создавать candidate manually.
- Не чинить queue/cache/progress/receipt/artifacts.
- Не запускать Scheduled Task `Run now`.
- Не запускать Proactive Project Auditor.
- Не делать IMPLEMENT в этом task.

## Durable report

Required path:

`reviews/worker_reports/taste-dossier-post-scg-live-acceptance-01.md`

Report должен попасть в `main` до завершения worker task.

Содержимое:
- Task / repository / mode.
- Authoritative observed UI result.
- Canonical contract interpretation.
- Exact live classification из четырёх разрешённых выше.
- Human-readable explanation.
- Minimal supporting canonical refs.
- What was correct in runtime behavior.
- What was wrong or unproved.
- Unresolved.
- Status.
- Exactly one recommended next step.
- Efficiency / reusable lesson per `DIRECTOR_PROTOCOL.md`.

Allowed final statuses:
- `accepted_live_behavior`
- `rejected_worker_contract_misread`
- `rejected_general_evidence_insufficient`
- `blocked_insufficient_evidence_to_classify`

## CURRENT_TASK.md

Можно обновить только в рамках требований `CHAT_PROTOCOL.md` для реально выполняемой acceptance-задачи; unrelated concurrent work не удалять и не переписывать.

## Next-step boundary

Если live outcome rejected, worker НЕ начинает fix.
Он только формулирует один bounded follow-up для отдельного Director-authorized task.

# НОВЫЙ ЧАТ 1 — одноразовый Assembly Dossier V2 на шести Research items

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: dossier-v2-fresh6-rerun1-assembly-one-shot-01
Assigned: НОВЫЙ физический ЧАТ 1, не старый Research ЧАТ 1.
Mode: EXPLICIT USER-LAUNCHED CANONICAL SEMANTIC ONE-SHOT / ASSEMBLY (не developer, не QA и не Scheduled Task).

## Область авторизации и START
Пользователь 2026-11-16 явно распорядился ПРОПУСТИТЬ отдельный независимый аудит качества Research и перейти к следующему этапу Assembly. Это разрешение относится только к одному изолированному Assembly этой уже выданной GitHub-партии, без повторного Research, Production, V1, Deep, canonical ingest или самостоятельного запуска sandbox writer. Прежний audit task приостановлен в registry/Board по решению пользователя; не ждать его QA verdict и не считать прежний недостоверный PR #456 доказательством качества.

Сначала открой CHAT_PROTOCOL.md из текущего main и выполни START gate. Затем прочитай CHAT_CONTEXT.md, config/execution_ownership_contract.json, этот task и полностью канонический launcher:
config/dossier_notes_v2_batch_assembly_manual_one_shot_prompt.md.
Прочитай все перечисленные в launcher contracts, strict schema, presubmit checklist и инструкции GitHub Connector. Канонический launcher имеет приоритет над кратким task, кроме явно закреплённого здесь scope. Работай ТОЛЬКО в kentrap2011-hub/steam-kz-deals-2; не открывай, не используй и не изменяй никакие другие репозитории. При неоднозначном GitHub target остановись, не пиши в другой repo.

## Exact immutable sandbox cohort
- trial_id: dossier-notes-v2-fresh6-20261114-rerun1
- branch: sandbox/dossier-notes-v2-fresh6-20261114-rerun1
- manifest: data/control/dossier_notes_v2/manifests/dossier-notes-v2-fresh6-20261114-rerun1.json
- manifest_blob_sha (предварительно подтверждённый): 752d5689c3f7d055c94c1844877337eea13ebd79
- marker_commit: cdc8bcf79cef6d6e7c3c97ab91b5fb9416ab96d1
- authorization_commit (issued sandbox auth introduction): 3c33d1baeed5d9fef1f10c9add21ea28cd142a32
- exact owner authorizer run: 43697110508, completed/success/first attempt, main source SHA bc317ae4d7cc8aaf52ad13fac2a98a3ae3261377
- observed current sandbox head before new task: cc36202c8e257a59a2bd463b0be821e572894ec7
- frozen manifest order: 1000010 Crown Trick; 102600 Orcs Must Die!; 1029690 Sniper Elite 5; 49520 Borderlands 2; 499180 Braid, Anniversary Edition; 501590 Bulletstorm: Full Clip Edition.
Эти данные — подсказки для проверки, а не замена реального свежего connector preflight; проверять динамический текущий branch HEAD и настоящие GitHub authority/commit links. Запрет на пользовательский пересчёт/самовольную подмену source pins, выбор игр или изданий.

## Что сделать
1. В рамках канонического Assembly launcher выполни полноценный owner-authenticated GitHub preflight (phase=assembly) на актуальном sandbox HEAD. Требуются точные immutable Research candidates **и отдельные typed Research receipts** для каждого AppID; Research receipt safe_incomplete_research — техническое состояние передачи заметок, не итоговый semantic acceptance и само по себе не препятствует независимому Assembly. Если реальные authority/provenance проверки не проходят — остановись без семантической публикации.
2. Для каждой игры, независимо от качества прежнего QA, самостоятельно изучай надёжные доступные публичные свидетельства и отзывы игроков о ТОЧНО этой игре/издании, проверяй идентичность, доступность режимов, разницу современных и исторических проблем, даты и платформы. Research notes — неподтверждённые подсказки, а не доказательства. Не объявляй search snippets прочитанными отзывами.
3. Формируй строго `DOSSIER-AUTONOMOUS-ASSEMBLY-RESULT-V2` с итоговым strict final Dossier либо честным `assembly_missing_evidence`/другим terminal и `final_dossier=null`. Две предварительные механические коррекции максимум. Не публикуй фиктивное `assembled_candidate_ready` ради полноты 6/6.
4. Используй ТОЧНО tokenless connector handoff route из launcher: initial preflight+handoff, затем отдельный Code Mode вызов на один item, далее только немедленный подтверждённый next_handoff. Только create-only GitHub CAS candidate+typed Assembly receipt. Каждая неоднозначная запись = STOP для этого item без самовольного retry.
5. Заверши объективным итогом в чате по каждому AppID: research binding, Assembly candidate/receipt Git SHAs, semantic outcome и независимые блокеры/неопределённости. Транспортный commit не является strict acceptance. Не выполняй последующий isolated writer без отдельного разрешения.

## Запреты / выходной артефакт
Допустимые записи: только one-shot exact `data/ai_inbox/dossier_assembly_v2/dossier-notes-v2-fresh6-20261114-rerun1/g<group_sequence:06d>/<appid>--<assignment_id>.json` и GitHub-owned/connector typed receipt `data/control/dossier_notes_v2/receipts/dossier-notes-v2-fresh6-20261114-rerun1/g<group_sequence:06d>/<appid>--<assignment_id>--assembly.json` на существующей sandbox/dossier-notes-v2-fresh6-20261114-rerun1, строго по каноническому launcher и strict writer. Без изменений main, source, workflow, task/Board/registry, Research candidates, старого PR #456, QA-протокола или других cohort.

Итоговые report-файлы этого канонического one-shot — именно шесть create-only Assembly JSON плюс шесть typed receipts в указанных GitHub sandbox paths при полном успешном прохождении. Дополнительный developer worker-report в `reviews/worker_reports/` не создавать: для изолированной one-shot роли разрешён только sandbox transport, а итоговый отчёт дать пользователю текстом в текущем чате с GitHub refs.

Готово, когда все шесть frozen items независимо проверены, либо честно зафиксирована их индивидуальная недоступность, результат кандидата/receipt подтверждён, и нет неподтверждённого acceptance или дополнительного writer run. Один следующий шаг: директор проверяет фактические Assembly receipts и отдельно решает, разрешать ли sandbox writer; никакого production/Deep автоматически.
